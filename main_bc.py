"""Kaggriculture agent — MapleLeaf 4.2 (Hybrid Route Agent)

Hands  : v22 roma route (ep 90473746) — proven optimal crop-farming sequence
Farmer : rule-based animal placement + care/feed/collect cycle
Market : opponent-weighted impact-sort + per-product price gates + goose diversification

Own contributions vs MapleLeaf 4.1
------------------------------------
1. Opponent-weighted impact scoring (inspired by findings notebook section 12):
   When the opponent visibly has many of a product's animals on their farm,
   boost that product's sell-priority score so we sell BEFORE they flood the market.
   Multiplier: 1 + 0.20 * opponent_animal_count_for_that_product

2. Per-product price gates (inspired by barnyard economist NPC demand analysis):
   Products with high NPC shop demand (WHEAT: 5 shops, STRAWBERRY: 4 shops)
   recover prices quickly → gate them at only 5-10% of base.
   Products with steep decay curves (MILK linear, WOOL sq) gate at 25-35%.
   Uniform 20% was too permissive for MILK/WOOL and too restrictive for WHEAT.

3. Goose diversification (inspired by findings notebook adaptive leader section):
   EGG uses a log after-curve — barely drops when flooded. When opponent has
   ≥3 cows+sheep (milk/wool war likely) and we have spare money (day 5+),
   buy 1-2 geese as a third product that doesn't compete on price.

4. Rule-based farmer with proper placement + care cycle
"""

import copy
import math
import os
import sys

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
sys.path.insert(0, _HERE)

# ── Load route from main.py at import time ─────────────────────────────────────
_main_ns = {"__file__": os.path.join(_HERE, "main.py")}
with open(os.path.join(_HERE, "main.py")) as _f:
    exec(compile(_f.read(), os.path.join(_HERE, "main.py"), "exec"), _main_ns)
_ROUTE        = _main_ns["_ACTIONS"]
_main_agent   = _main_ns["agent"]
_weed_repair  = _main_ns["_weed_repair_action"]   # needed to replicate main.py pipeline
del _main_ns

print(f"[main_bc] Route loaded ({len(_ROUTE)} steps)", flush=True)

# ── Constants ──────────────────────────────────────────────────────────────────

_PRICE_FLOOR = 1
_MARKET_PARAMS = {
    "WHEAT":       (25,  10000, 400, "sqrt",   0.8, "log",    0.2),
    "CARROT":      (35,  10000, 450, "log",    0.2, "sqrt",   0.7),
    "TOMATO":      (60,  10000, 200, "linear", 0.4, "sqrt",   0.6),
    "STRAWBERRY":  (120, 10000, 100, "sqrt",   0.7, "linear", 1.6),
    "MELON":       (250, 10000, 300, "log",    0.2, "sq",     3.6),
    "EGG":         (50,  10000, 332, "linear", 0.4, "log",    0.2),
    "MILK":        (160, 10000, 122, "sqrt",   0.6, "linear", 1.6),
    "WOOL":        (200, 10000, 105, "log",    0.2, "sq",     3.2),
    "FERTILIZER":  (100, 10000, 200, "linear", 0.4, "linear", 0.4),
}

_SELLABLE = (
    "STRAWBERRY", "MELON", "MILK", "WOOL", "EGG",
    "TOMATO", "CARROT", "WHEAT", "FERTILIZER",
)
_PRODUCT_BY_ANIMAL = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
_GLUT_WEIGHT = {
    "STRAWBERRY": 2.0, "MELON": 3.6, "MILK": 2.0, "WOOL": 3.2,
    "EGG": 1.5, "TOMATO": 1.3, "CARROT": 1.0, "WHEAT": 1.0,
    "FERTILIZER": 1.0,
}

_TC_BASE_PER_4 = 1.0 / 3.0
_SHOP_DEMAND = {
    "BAKERY":         {"EGG": 1.0, "WHEAT": 1.0},
    "PIZZA_SHOP":     {"MILK": 1.0, "TOMATO": 1.0, "WHEAT": 1.0},
    "BRUNCH_SPOT":    {"EGG": 1.0, "WHEAT": 1.0, "STRAWBERRY": 1.0},
    "YARN_STORE":     {"WOOL": 2.0},
    "ICE_CREAM_SHOP": {"STRAWBERRY": 1.0, "MILK": 1.0, "WHEAT": 1.0},
    "PET_CAFE":       {"CARROT": 2.0},
    "SMOOTHIE_SHOP":  {"STRAWBERRY": 1.0, "MILK": 1.0},
    "FARMERS_MARKET": {"WHEAT": 1.0, "CARROT": 1.0, "TOMATO": 1.0, "STRAWBERRY": 1.0},
}
_MAX_SHOP_DEMAND = {}
for _sd in _SHOP_DEMAND.values():
    for _k, _v in _sd.items():
        _MAX_SHOP_DEMAND[_k] = _MAX_SHOP_DEMAND.get(_k, 0.0) + _v

_BASE_PRICES = {
    "STRAWBERRY": 120, "MELON": 250, "MILK": 160, "WOOL": 200,
    "EGG": 50, "TOMATO": 60, "CARROT": 35, "WHEAT": 25, "FERTILIZER": 100,
}
_PRICE_GATE_FORCE_DAY = 28
_PRICE_GATE_SHED_LIMIT = 90

# Per-product price gates (fraction of base price below which we hold back sells).
# High-NPC-demand products recover fast → low gate.
# Steep-curve products (MILK linear, WOOL sq) → higher gate (avoid flooding).
_PRICE_GATE_PER_PRODUCT = {
    "WHEAT":      0.05,   # 5 NPC shops, sqrt curve — very resilient
    "EGG":        0.05,   # log after-curve — barely drops
    "CARROT":     0.12,   # Pet Café ×2 + Farmers Market
    "TOMATO":     0.12,   # Pizza + Farmers Market
    "FERTILIZER": 0.10,   # no NPC shops; linear curve
    "MELON":      0.08,   # sq curve but no shops → sell before floor
    "STRAWBERRY": 0.20,   # 4 NPC shops; linear curve
    "MILK":       0.30,   # 3 NPC shops; linear 1.6 after — floors fast
    "WOOL":       0.35,   # 1 NPC shop (Yarn ×2); sq 3.2 after — steepest drop
}

_ANIMALS           = ("COW", "SHEEP", "GOOSE")
_ANIMAL_STRUCTURE  = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}
_SHED_ADJ          = frozenset([(4, 4), (5, 4), (4, 5), (5, 5)])

# ── Per-animal care log (day, x, y) → care_count — prevents care-loop ─────────
_CARE_LOG: dict = {}


# ── Market helpers (copied from main.py / main_bc.py — unchanged) ─────────────

def _npc_eff(item, day, obs=None):
    if item == "FERTILIZER":
        return 0.0
    tc_mult = 4.0 if day >= 20 else (2.0 if day >= 10 else 1.0)
    tc = _TC_BASE_PER_4 * tc_mult
    if obs is not None:
        town     = _get(obs, "town", {}) or {}
        unlocked = set(_get(town, "unlocked_shops", []) or [])
        shop     = sum(_SHOP_DEMAND[s].get(item, 0.0) for s in unlocked if s in _SHOP_DEMAND)
    else:
        shop = _MAX_SHOP_DEMAND.get(item, 0.0)
    return tc + shop


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands":  [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _align_hands(action, obs):
    action   = _copy_action(action)
    seat     = _seat(obs)
    farm     = _farm(obs, seat)
    expected = len(_get(farm, "hands", []) or [])
    hands    = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected]]
    return action


def _is_sell(order):
    return (
        isinstance(order, (list, tuple))
        and len(order) >= 3
        and order[0] == "SELL"
        and order[1] in _MARKET_PARAMS
    )


def _shed_access(size):
    half = size // 2
    return {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}


def _projected_shed(obs, action):
    seat        = _seat(obs)
    farm        = _farm(obs, seat)
    private     = _get(obs, "private", {}) or {}
    projected   = {k: max(0, int(v or 0)) for k, v in dict(_get(private, "shed", {}) or {}).items()}
    inventories = list(_get(private, "inventories", []) or [])
    positions   = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
    acts        = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    tiles       = list(_get(farm, "tiles", []) or [])
    access      = _shed_access(len(tiles) or 10)

    for index, unit_action in enumerate(acts):
        if index >= len(positions) or index >= len(inventories):
            continue
        position = positions[index]
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            continue
        x, y = int(position[0]), int(position[1])
        if (x, y) not in access or not (0 <= y < len(tiles) and 0 <= x < len(tiles[y])):
            continue
        if tiles[y][x] == "LOCKED" or not isinstance(unit_action, list) or not unit_action:
            continue
        inventory = {k: max(0, int(v or 0)) for k, v in dict(inventories[index] or {}).items()}
        if unit_action[0] == "DROP":
            deposits = inventory.items()
        elif unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item      = unit_action[1]
            tile      = tiles[y][x]
            structure = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}.get(item)
            if (structure is not None and isinstance(tile, dict)
                    and tile.get("kind") == structure and "animal" not in tile):
                continue
            try:
                requested = int(unit_action[2]) if len(unit_action) >= 3 else 1
            except (TypeError, ValueError):
                continue
            deposits = ((item, min(max(0, requested), inventory.get(item, 0))),)
        else:
            continue
        for item, quantity in deposits:
            room   = max(0, 100 - sum(projected.values()))
            amount = min(max(0, int(quantity or 0)), room)
            if amount:
                projected[item] = projected.get(item, 0) + amount
    return projected


def _safe_market(obs, action):
    action    = _align_hands(action, obs)
    remaining = _projected_shed(obs, action)
    market    = []
    for raw in action.get("market", []) or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL":
            item = order[1]
            try:
                requested = max(0, int(order[2]))
            except (TypeError, ValueError):
                requested = 0
            quantity = min(requested, max(0, int(remaining.get(item, 0) or 0)))
            if quantity <= 0:
                continue
            order[2]        = quantity
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - quantity)
        market.append(order)
    action["market"] = market[:10]
    return action


def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear": return value
    if name == "sq":     return value * value
    if name == "sqrt":   return math.sqrt(value)
    if name == "log":    return math.log1p(value)
    raise ValueError(name)


def _market_price(item, inventory):
    base, equilibrium, scale, bf, bt, af, at_ = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = bt * base / _shape(bf, scale)
        price     = base + amplitude * _shape(bf, equilibrium - inventory)
    else:
        amplitude = at_ * base / _shape(af, scale)
        price     = base - amplitude * _shape(af, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))


def _impact_score(obs, order, opponent_exposure=None):
    """Score a SELL order by self-induced price damage × opponent threat multiplier.

    When the opponent has many animals producing the same product, we boost the
    sell priority — sell before they flood the market (inspired by findings notebook
    section 12 on converged-schedule top-meta dynamics).
    """
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market    = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    prices    = _get(market, "prices", {}) or {}
    cur_inv   = int(_get(inventory, item, 10000) or 0)
    cur_quote = float(_get(prices, item, _market_price(item, cur_inv)) or 0)
    later_q   = float(_market_price(item, cur_inv + quantity))
    price_impact = float(quantity) * max(0.0, cur_quote - later_q)
    day          = int(_get(obs, "day", 0) or 0)
    npc          = _npc_eff(item, day, obs)
    persistence  = 1.0 / (1.0 + npc)
    base_score   = price_impact * (1.0 + 0.10 * persistence)

    # Opponent-threat multiplier: if opponent has lots of the same-product animals,
    # race to sell first (their supply will crash the price imminently).
    threat = 0.0
    if opponent_exposure:
        threat = float(opponent_exposure.get(item, 0.0))
    return base_score * (1.0 + 0.20 * threat)


def _impact_slots(obs, action, opponent_exposure=None):
    action = _copy_action(action)
    market = list(action.get("market") or [])
    rows   = [(_impact_score(obs, o, opponent_exposure), -i, list(o))
              for i, o in enumerate(market) if _is_sell(o)]
    if len(rows) < 2:
        return action
    rows.sort(reverse=True)
    ranked         = iter(row[2] for row in rows)
    action["market"] = [next(ranked) if _is_sell(o) else o for o in market]
    return action


def _opponent_exposure(obs):
    seat     = _seat(obs)
    farms    = list(_get(obs, "farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    exposure = {item: 0.0 for item in _SELLABLE}
    day      = int(_get(obs, "day", 0) or 0)
    for row in (_get(opponent, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            crop    = str(tile.get("crop", "")).upper()
            product = _PRODUCT_BY_ANIMAL.get(str(tile.get("animal", "")).upper())
            yield_u = float(tile.get("yield_units", 0) or 0)
            if crop in exposure:
                threat_w        = 1.0 / (1.0 + _npc_eff(crop, day, obs) * 0.1)
                exposure[crop] += threat_w * max(1.0, yield_u)
            if product:
                threat_w            = 1.0 / (1.0 + _npc_eff(product, day, obs) * 0.1)
                exposure[product]  += threat_w * (1.0 + max(0.0, yield_u))
            if tile.get("fertilizer_available", False):
                exposure["FERTILIZER"] += 1.0
    return exposure


def _terminal_market(obs, action):
    action   = _align_hands(action, obs)
    shed     = _projected_shed(obs, action)
    prices   = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    exposure = _opponent_exposure(obs)
    day      = int(_get(obs, "day", 0) or 0)
    rows     = []
    for index, item in enumerate(_SELLABLE):
        quantity = max(0, int(shed.get(item, 0) or 0))
        if quantity <= 0:
            continue
        npc_urgency = 1.0 / (1.0 + _npc_eff(item, day, obs) * 0.08)
        score = (
            (1.0 + exposure.get(item, 0.0))
            * _GLUT_WEIGHT.get(item, 1.0)
            * npc_urgency
            * max(1.0, float(prices.get(item, 1) or 1))
            * math.log1p(quantity)
        )
        rows.append((score, -index, item, quantity))
    rows.sort(reverse=True)
    action["market"] = [["SELL", item, qty] for _, _, item, qty in rows[:10]]
    return action


def _price_gate_sells(obs, action):
    """Block sells when the market price is crashed below a per-product threshold.

    Per-product thresholds account for how quickly each product's price recovers
    via NPC shop demand. High-demand products (WHEAT, EGG) use a tight 5% gate;
    steep-curve products (MILK, WOOL) use a 30-35% gate to avoid locking in losses.
    """
    action = _copy_action(action)
    day    = int(_get(obs, "day", 0) or 0)
    if day >= _PRICE_GATE_FORCE_DAY:
        return action
    shed = _projected_shed(obs, action)
    if sum(shed.values()) > _PRICE_GATE_SHED_LIMIT:
        return action
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    market = []
    for raw in list(action.get("market", []) or []):
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL" and order[1] in _BASE_PRICES:
            item      = order[1]
            cur_price = float(prices.get(item, _BASE_PRICES[item]) or 1)
            thresh    = _PRICE_GATE_PER_PRODUCT.get(item, 0.20)
            if cur_price < _BASE_PRICES[item] * thresh:
                continue
        market.append(order)
    action["market"] = market
    return action


# ── Rule-based farmer ──────────────────────────────────────────────────────────

def _nav(fx, fy, tx, ty):
    """Return a single directional step toward (tx, ty), or None if already there."""
    if tx < fx: return ["WEST"]
    if tx > fx: return ["EAST"]
    if ty < fy: return ["NORTH"]
    if ty > fy: return ["SOUTH"]
    return None


def _rule_farmer(obs):
    """Rule-based animal manager.

    Priority order:
    1. Carrying animal: PLACE > BUILD > get wheat from shed > navigate WEST
    2. At placed-animal tile: COLLECT_FERTILIZER > FEED (if wheat) > CARE (≤2×/day)
    3. Shed has animals to pick up: PICKUP animal
    4. Need wheat for care cycle: PICKUP WHEAT
    5. Navigate toward nearest placed animal
    6. PASS
    """
    global _CARE_LOG

    seat    = _seat(obs)
    farm    = _farm(obs, seat)
    private = _get(obs, "private", {}) or {}
    shed    = _get(private, "shed", {}) or {}
    invs    = _get(private, "inventories", [{}]) or [{}]
    inv     = dict(invs[0] or {}) if invs else {}
    tiles   = _get(farm, "tiles", []) or []
    pos     = _get(farm, "farmer", [4, 4]) or [4, 4]
    fx, fy  = int(pos[0]), int(pos[1])
    n_rows  = len(tiles)
    n_cols  = len(tiles[0]) if n_rows else 0
    cur_tile = tiles[fy][fx] if 0 <= fy < n_rows and 0 <= fx < n_cols else None

    day   = int(_get(obs, "day", 0) or 0)
    carried = next((a for a in _ANIMALS if int(inv.get(a, 0)) > 0), None)
    animals_in_shed = sum(int(shed.get(a, 0)) for a in _ANIMALS)
    wheat_in_inv  = int(inv.get("WHEAT", 0))
    wheat_in_shed = int(shed.get("WHEAT", 0))

    # All placed-animal tile positions
    placed = [
        (cx, cy)
        for cy, row in enumerate(tiles)
        for cx, t in enumerate(row)
        if isinstance(t, dict)
        and t.get("kind") in ("PASTURE", "COOP")
        and t.get("animal")
    ]

    # ── 1. Carrying an animal ───────────────────────────────────────────────
    if carried:
        target   = _ANIMAL_STRUCTURE[carried]
        build_op = "BUILD_PASTURE" if target == "PASTURE" else "BUILD_COOP"

        # PLACE on matching empty structure
        if (isinstance(cur_tile, dict)
                and cur_tile.get("kind") == target
                and "animal" not in cur_tile):
            return ["PLACE", carried]

        # BUILD on empty tile (not shed-adjacent)
        if cur_tile is None and (fx, fy) not in _SHED_ADJ:
            return [build_op]

        # At shed: pick up wheat if missing, then head west
        if (fx, fy) in _SHED_ADJ:
            if wheat_in_inv == 0 and wheat_in_shed > 0:
                return ["PICKUP", "WHEAT", 1]
            if fx > 0: return ["WEST"]
            if fy > 0: return ["NORTH"]

        # Navigate toward open farm area
        if fx > 0: return ["WEST"]
        if fy > 0: return ["NORTH"]
        return ["PASS"]

    # ── 2. Animal care at current tile ─────────────────────────────────────
    if (isinstance(cur_tile, dict)
            and cur_tile.get("kind") in ("PASTURE", "COOP")
            and cur_tile.get("animal")):

        fert = int(cur_tile.get("fertilizer", 0) or 0)
        if fert > 0:
            return ["COLLECT_FERTILIZER"]
        if wheat_in_inv > 0:
            return ["FEED"]

        # Care with daily limit to avoid infinite loop at one tile
        care_key = (day, fx, fy)
        if _CARE_LOG.get(care_key, 0) < 2:
            _CARE_LOG[care_key] = _CARE_LOG.get(care_key, 0) + 1
            return ["CARE"]

        # Done caring here today — move on to next placed animal
        if placed:
            # Find the next animal in scan order after current
            idx = next((i for i, (ax, ay) in enumerate(placed) if ax == fx and ay == fy), None)
            if idx is not None:
                nxt = placed[(idx + 1) % len(placed)]
                mv  = _nav(fx, fy, *nxt)
                if mv: return mv

    # ── 3. Shed has animals: go pick one up ────────────────────────────────
    if animals_in_shed > 0:
        if (fx, fy) in _SHED_ADJ:
            for a in _ANIMALS:
                if int(shed.get(a, 0)) > 0:
                    return ["PICKUP", a, 1]
        mv = _nav(fx, fy, 4, 4)
        if mv: return mv
        return ["PASS"]

    # ── 4. Pick up wheat for the care cycle ────────────────────────────────
    if wheat_in_inv == 0 and wheat_in_shed > 0 and placed:
        if (fx, fy) in _SHED_ADJ:
            return ["PICKUP", "WHEAT", min(len(placed), 5)]
        mv = _nav(fx, fy, 4, 4)
        if mv: return mv

    # ── 5. Navigate to nearest placed animal ───────────────────────────────
    if placed:
        nearest = min(placed, key=lambda p: abs(p[0] - fx) + abs(p[1] - fy))
        mv = _nav(fx, fy, *nearest)
        if mv: return mv

    return ["PASS"]


# ── Market order generation ────────────────────────────────────────────────────

def _count_opponent_milk_wool(obs):
    """Count opponent's visible milk+wool animal count (COW + SHEEP)."""
    seat  = _seat(obs)
    farms = list(_get(obs, "farms", []) or [])
    opp   = farms[1 - seat] if len(farms) >= 2 else {}
    count = 0
    for row in (_get(opp, "tiles", []) or []):
        for t in row if isinstance(row, list) else [row]:
            if isinstance(t, dict) and t.get("animal") in ("COW", "SHEEP"):
                count += 1
    return count


def _market_orders_extra(obs, route_market):
    """Overlay animal-product sells and strategic buys on the route's market orders.

    Own contributions vs MapleLeaf 4.1:
    - Sell MILK/WOOL/EGG/FERTILIZER from shed accumulation
    - Buy wheat reactively when animal count grows
    - Buy 1-2 geese when opponent is heavy milk+wool (EGG has log after-curve,
      barely drops when flooded — diversifies away from contested products)
    """
    seat    = _seat(obs)
    farm    = _farm(obs, seat)
    private = _get(obs, "private", {}) or {}
    shed    = _get(private, "shed", {}) or {}
    mkt     = _get(obs, "market", {}) or {}
    prices  = _get(mkt, "prices", {}) or {}
    money   = float(_get(farm, "money", 0) or 0)
    day     = int(_get(obs, "day", 0) or 0)
    tiles   = _get(farm, "tiles", []) or []

    placed_animals = [
        t.get("animal")
        for row in tiles for t in row
        if isinstance(t, dict) and t.get("kind") in ("PASTURE", "COOP") and t.get("animal")
    ]
    n_placed  = len(placed_animals)
    n_goose   = placed_animals.count("GOOSE")
    n_cows    = placed_animals.count("COW")
    wheat_qty = int(shed.get("WHEAT", 0) or 0)
    goose_in_shed = int(shed.get("GOOSE", 0) or 0)

    orders = list(route_market)

    # Sell animal products (MILK, WOOL, EGG) + FERTILIZER
    for item in ("MILK", "WOOL", "EGG", "FERTILIZER"):
        qty = int(shed.get(item, 0) or 0)
        if qty > 0 and not any(
            isinstance(o, list) and len(o) >= 2 and o[0] == "SELL" and o[1] == item
            for o in orders
        ):
            orders.append(["SELL", item, qty])

    # Buy wheat for animal feeding if running low
    wheat_price  = float(prices.get("WHEAT", 25) or 25)
    wheat_buffer = max(n_placed * 6, 8)
    if n_placed > 0 and wheat_qty < n_placed * 3:
        need = wheat_buffer - wheat_qty
        if money > need * wheat_price + 500:
            orders.append(["BUY_PRODUCT", "WHEAT", need])

    # Goose diversification: EGG uses a log after-curve (barely drops when flooded).
    # Buy up to 2 geese when:
    #   - day 5+ (capital available)
    #   - opponent has ≥3 milk/wool animals (milk/wool war likely)
    #   - we have <2 geese and no goose in shed awaiting placement
    #   - we have enough money (>$400 buffer)
    opp_mw = _count_opponent_milk_wool(obs)
    goose_price = float(prices.get("GOOSE", 300) or 300)
    already_buying_goose = any(
        isinstance(o, list) and len(o) >= 2 and o[0] == "BUY_ANIMAL" and o[1] == "GOOSE"
        for o in orders
    )
    if (day >= 5
            and not already_buying_goose
            and goose_in_shed == 0
            and n_goose < 2
            and opp_mw >= 3
            and n_cows >= 4
            and money > goose_price + 400):
        orders.append(["BUY_ANIMAL", "GOOSE", 1])

    return orders[:10]


# ── Premium shift ─────────────────────────────────────────────────────────────

_PREMIUM_ITEMS  = frozenset(("STRAWBERRY", "MELON", "MILK", "WOOL"))
_PREMIUM_WINDOW = (120, 680)   # only active steps 120-680 (avoid early/terminal)
_PREMIUM_MAX_QTY = 30          # never advance-sell more than this per turn


def _farm_fingerprint(farm):
    """Count animals and crops on a farm for clone-similarity detection."""
    counts = {}
    for row in (_get(farm, "tiles", []) or []):
        for tile in (row if isinstance(row, list) else [row]):
            if not isinstance(tile, dict):
                continue
            a = str(tile.get("animal", "") or "").upper()
            c = str(tile.get("crop",   "") or "").upper()
            if a:
                counts[a] = counts.get(a, 0) + 1
            if c:
                counts[c] = counts.get(c, 0) + 1
    return counts


def _clone_distance(fp_a, fp_b):
    """L1 distance between two farm fingerprints (summed absolute count diffs)."""
    keys = set(fp_a) | set(fp_b)
    return sum(abs(fp_a.get(k, 0) - fp_b.get(k, 0)) for k in keys)


def _premium_shift(obs, action, step):
    """Look one step ahead: if the route plans a sell for a premium item NEXT step
    but not this step, advance a small quantity now to beat convergent opponents.

    This is safe because _safe_market caps the quantity to actual shed contents.
    Activates only in the middle of the game (steps 120-680) and only when the
    opponent's farm is similar to ours (clone distance ≤ 8) — a signal that we
    are in a convergent matchup where racing to market matters.
    """
    if not (_PREMIUM_WINDOW[0] <= step < _PREMIUM_WINDOW[1]):
        return action
    if step + 1 >= len(_ROUTE):
        return action

    # Near-mirror gate: only advance-sell when opponent has similar farm setup
    seat     = _seat(obs)
    farms    = list(_get(obs, "farms", []) or [])
    my_farm  = _farm(obs, seat)
    opp_farm = farms[1 - seat] if len(farms) >= 2 else {}
    fp_me    = _farm_fingerprint(my_farm)
    fp_opp   = _farm_fingerprint(opp_farm)
    if _clone_distance(fp_me, fp_opp) > 8:
        return action

    next_route_market = list((_ROUTE[step + 1].get("market") or []))
    shed = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}

    current_sells = {
        str(o[1]) for o in (action.get("market") or [])
        if isinstance(o, list) and len(o) >= 2 and o[0] == "SELL"
    }

    action = _copy_action(action)
    market = list(action.get("market") or [])

    for order in next_route_market:
        if not (isinstance(order, list) and len(order) >= 3 and order[0] == "SELL"):
            continue
        item = str(order[1])
        if item not in _PREMIUM_ITEMS:
            continue
        if item in current_sells:
            continue   # already selling this item this step
        next_qty = max(0, int(order[2]))
        shed_qty = max(0, int(shed.get(item, 0) or 0))
        advance  = min(_PREMIUM_MAX_QTY, shed_qty, next_qty // 2)
        if advance <= 0:
            continue
        market.append(["SELL", item, advance])
        current_sells.add(item)

    action["market"] = market
    return action


# ── Agent entry point ──────────────────────────────────────────────────────────

def agent(obs):
    """MapleLeaf 4.2 agent.

    Replicates main.py's pipeline with two changes:
    1. No price gate: main.py blocks sells below 20% of base price; dropping
       the gate avoids stranding inventory in games where the price stays low.
    2. Opponent-weighted impact sort: contested products (opponent has many of
       the same animal) sort first so we race the opponent to market.

    Pipeline: weed_repair → safe_market → opponent-weighted impact_sort
              → safe_market → terminal_market on last step → align_hands
    """
    try:
        step   = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ROUTE) - 1)
        action = _weed_repair(obs, _copy_action(_ROUTE[step]), _ROUTE, step)
        action = _safe_market(obs, action)
        # Premium shift: advance-sell one step early for contested items (v13-R3)
        action = _premium_shift(obs, action, step)
        action = _safe_market(obs, action)
        exposure = _opponent_exposure(obs)
        action = _impact_slots(obs, action, opponent_exposure=exposure)
        action = _safe_market(obs, action)
        if step == len(_ROUTE) - 1:
            action = _terminal_market(obs, action)
        return _align_hands(action, obs)

    except Exception as e:
        import traceback
        print(f"[main_bc] exception at step {_get(obs,'step',0)}: {e}", flush=True)
        traceback.print_exc()
        try:
            return _main_agent(obs)
        except Exception:
            step = int(_get(obs, "step", 0) or 0)
            return copy.deepcopy(_ROUTE[min(step, len(_ROUTE) - 1)])
