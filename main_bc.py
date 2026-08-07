"""Kaggriculture agent — MapleLeaf 4.2 (Behavioral Cloning)
Navigation : PolicyNet from train_bc.py (102 replays, 95.4% action accuracy)
Market     : rule-based sell/buy + price-gate + impact-sort + terminal liquidation
Weights    : weights_bc.npz  (copy to project root after training)

For Kaggle submission, run embed_weights.py to produce a self-contained file.
"""

import copy
import math
import os
import sys

import numpy as np

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _HERE = os.getcwd()
sys.path.insert(0, _HERE)
from model import encode_obs, ACTIONS, PolicyNet

# ── Load weights at import time so failures are immediately visible ────────────
_WEIGHTS_PATH = os.path.join(_HERE, "weights_bc.npz")

if not os.path.exists(_WEIGHTS_PATH):
    raise FileNotFoundError(
        f"\n\nweights_bc.npz not found at:\n  {_WEIGHTS_PATH}\n\n"
        "Copy weights_bc.npz from the machine where you ran train_bc.py "
        "into the same folder as main_bc.py."
    )

_NET = PolicyNet().load(_WEIGHTS_PATH)
print(f"[main_bc] Loaded weights from {_WEIGHTS_PATH}", flush=True)

_LOGGED_ERROR = False


def _get_net():
    return _NET


# ── Pipeline helpers (exact copies from main.py — no changes) ─────────────────

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
_PRICE_GATE_THRESH = 0.20
_PRICE_GATE_FORCE_DAY = 28
_PRICE_GATE_SHED_LIMIT = 90


def _npc_eff(item, day, obs=None):
    if item == "FERTILIZER":
        return 0.0
    tc_mult = 4.0 if day >= 20 else (2.0 if day >= 10 else 1.0)
    tc = _TC_BASE_PER_4 * tc_mult
    if obs is not None:
        town = _get(obs, "town", {}) or {}
        unlocked = set(_get(town, "unlocked_shops", []) or [])
        shop = sum(
            _SHOP_DEMAND[s].get(item, 0.0)
            for s in unlocked if s in _SHOP_DEMAND
        )
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
    projected   = {
        k: max(0, int(v or 0))
        for k, v in dict(_get(private, "shed", {}) or {}).items()
    }
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
        inventory = {
            k: max(0, int(v or 0))
            for k, v in dict(inventories[index] or {}).items()
        }
        if unit_action[0] == "DROP":
            deposits = inventory.items()
        elif unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item = unit_action[1]
            tile = tiles[y][x]
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


def _impact_score(obs, order):
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
    day         = int(_get(obs, "day", 0) or 0)
    npc         = _npc_eff(item, day, obs)
    persistence = 1.0 / (1.0 + npc)
    return price_impact * (1.0 + 0.10 * persistence)


def _impact_slots(obs, action):
    action = _copy_action(action)
    market = list(action.get("market") or [])
    rows   = [
        (_impact_score(obs, o), -i, list(o))
        for i, o in enumerate(market)
        if _is_sell(o)
    ]
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
            crop    = str(tile.get("crop",   "")).upper()
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
    action = _copy_action(action)
    day = int(_get(obs, "day", 0) or 0)
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
            item = order[1]
            cur_price = float(prices.get(item, _BASE_PRICES[item]) or 1)
            if cur_price < _BASE_PRICES[item] * _PRICE_GATE_THRESH:
                continue
        market.append(order)
    action["market"] = market
    return action


# ── Market order generation ────────────────────────────────────────────────────

def _market_orders(obs):
    """Generate sell/buy orders from current shed state."""
    seat     = _seat(obs)
    farm     = _farm(obs, seat)
    private  = _get(obs, "private", {}) or {}
    mkt      = _get(obs, "market", {}) or {}
    shed     = _get(private, "shed", {}) or {}
    seeds    = _get(private, "seeds", {}) or {}
    prices   = _get(mkt, "prices", {}) or {}
    money    = float(_get(farm, "money", 0) or 0)
    day      = int(_get(obs, "day", 0) or 0)
    hour     = int(_get(obs, "hour", 0) or 0)
    tiles    = _get(farm, "tiles", []) or []

    num_animals = sum(
        1 for row in tiles for t in row
        if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and t.get("animal")
    )
    n_empty = sum(1 for row in tiles for t in row if t is None)
    num_workers = 1 + len(_get(farm, "hands", []) or [])

    orders = []

    # Sell all non-wheat items
    for item in ["EGG", "MILK", "WOOL", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "FERTILIZER"]:
        qty = int(shed.get(item, 0) or 0)
        if qty > 0:
            orders.append(["SELL", item, qty])

    # Sell wheat surplus above animal buffer
    wheat_buffer = max(num_animals * 6, 10)
    wheat_qty    = int(shed.get("WHEAT", 0) or 0)
    if wheat_qty - wheat_buffer > 0:
        orders.append(["SELL", "WHEAT", wheat_qty - wheat_buffer])

    # Buy wheat for animals if running low
    if num_animals > 0 and wheat_qty < num_animals * 3:
        need = num_animals * 4 - wheat_qty
        wheat_price = float(prices.get("WHEAT", 25) or 25)
        if money > need * wheat_price + 200:
            orders.append(["BUY_PRODUCT", "WHEAT", need])
            money -= need * wheat_price

    # Hire at hour 0 (cost 1 → huge ROI)
    hires = int(_get(farm, "hires_today", 0) or 0)
    fib   = [1, 1, 2, 3, 5, 8, 13, 21, 34]
    hire_cost = fib[hires] if hires < len(fib) else 9999
    if hour == 0 and hires < 2 and money >= hire_cost + 100:
        orders.append(["HIRE"])
        money -= hire_cost

    # Buy wheat seeds
    wheat_seeds = int(seeds.get("WHEAT", 0) or 0)
    seed_want   = min(n_empty, num_workers * 8) - wheat_seeds
    if seed_want > 0 and money > seed_want * 10 + 300:
        orders.append(["BUY_SEED", "WHEAT", seed_want])
        money -= seed_want * 10

    # Buy land when profitable
    unlocked  = _get(farm, "unlocked_quadrants", ["NW"]) or ["NW"]
    num_quad  = len(unlocked)
    land_cost = {1: 1000, 2: 2000, 3: 4000}.get(num_quad, 99999)
    if (day >= 8 and num_quad < 4 and money > land_cost + 500
            and n_empty < 5 and num_workers >= 2):
        orders.append(["BUY_LAND"])

    return orders[:10]


# ── Agent entry point ──────────────────────────────────────────────────────────

def agent(obs):
    try:
        net = _get_net()

        # 1. BC model → farmer action
        enc    = encode_obs(obs)
        idx    = net.act_greedy(enc)
        farmer = list(ACTIONS[idx])

        # 2. Generate market orders from shed inventory
        action = {"farmer": farmer, "hands": [], "market": _market_orders(obs)}

        # 3. Clamp SELL quantities to actual shed inventory
        action = _safe_market(obs, action)

        # 4. Skip sells where price has crashed >80% below base
        action = _price_gate_sells(obs, action)

        # 5. Sort SELLs: highest self-damage goes first
        action = _impact_slots(obs, action)

        # 6. Final clamp after sort
        action = _safe_market(obs, action)

        # 7. Terminal: liquidate everything on last step
        step = int(_get(obs, "step", 0) or 0)
        if step >= 719:
            action = _terminal_market(obs, action)

        return _align_hands(action, obs)

    except Exception:
        global _LOGGED_ERROR
        if not _LOGGED_ERROR:
            import traceback
            print("\n[main_bc] ERROR on first agent() call:", flush=True)
            traceback.print_exc()
            _LOGGED_ERROR = True
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands":  [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }
