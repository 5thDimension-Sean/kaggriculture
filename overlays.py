"""overlays.py -- Market-intelligence overlays revived from MapleLeaf 6.3
(git commit 5f69c92), ported to run on top of whatever backbone route 6.6
adopts. Deleted wholesale in the 6.4 rewrite on the assumption the new route
didn't need them; never re-tested against the new route until now.

Ported near-verbatim (same state-machine/checkpoint-lock structure as the
original -- these are intricate, already-validated mechanisms, and the
lowest-risk way to make them tunable is to keep their logic exactly as
written and only externalize the ALL-CAPS constants). Every tunable knob
lives in DEFAULT_PARAMS; call configure(params) once per process/game-batch
before use to patch them in (see tuning_spec.py / evolve.py). A "params"
value that reproduces DEFAULT_PARAMS reproduces 6.3's original behavior
exactly (modulo running on a different backbone route).

Each overlay function is independently disable-able by driving its gate
constant to a sentinel (e.g. distance-max to 9999, enabled flag to False) --
matching the existing sentinel pattern already used for
_PREEMPT_MAX_CLONE_DISTANCE / _RELAY_DISTANCE_MAX in this project's history.
"""

import math

# ===========================================================================
# Tunable parameters -- single source of truth, consumed by tuning_spec.py.
# ===========================================================================

DEFAULT_PARAMS = {
    # premium market-lead preemption
    "premium_shift_enabled":        1.0,
    "premium_shift_start":          120,
    "premium_shift_stop":           680,
    "premium_shift_fraction":       2.0,
    "premium_shift_max_batch":      30,
    "premium_shift_min_future_qty": 2,
    "premium_shift_opp_ready_threshold": 4,
    "mirror_max_distance":          20,

    # fertilizer relay
    "fert_relay_enabled":     1.0,
    "fert_relay_distance_max": 9999,   # sentinel = unconditional (matches project history)
    "fert_relay_lead":        3,
    "fert_relay_lead_heavy_animal": 6,
    "fert_relay_start":       278,
    "fert_relay_stop":        662,

    # price floor guard
    "price_floor_enabled": 1.0,

    # opportunistic surplus sell
    "opp_sell_enabled":         1.0,
    "opp_sell_start":           50,
    "opp_sell_stop":            705,
    "opp_sell_batch_cap":       8,
    "opp_sell_base_fraction":   0.5,
    "opp_sell_floor_fraction":  0.15,
    "opp_sell_ramp_start":      600,
    "opp_sell_min_supply_fraction": 0.5,

    # terminal liquidation
    "terminal_soft_start": 706,
    "terminal_hard_start": 708,

    # sell-slot ranking (impact-score) / demand-urgency weight
    "rank_sell_slots_enabled": 1.0,
    "demand_alpha": 0.25,
}

_PRICE_FLOOR = 1
_I0 = 10000

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
_SHOP_PRODUCTS = {
    "BAKERY":         ("EGG", "WHEAT"),
    "PIZZA_SHOP":     ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT":    ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE":     ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE":       ("CARROT",),
    "SMOOTHIE_SHOP":  ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
_SELLABLE = tuple(_MARKET_PARAMS)
_PREMIUM = ("STRAWBERRY", "MELON", "MILK", "WOOL")
_PRODUCT_BY_ANIMAL = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
_GLUT_WEIGHT = {
    "STRAWBERRY": 2.0, "MELON": 3.6, "MILK": 2.0, "WOOL": 3.2,
    "EGG": 1.5, "TOMATO": 1.3, "CARROT": 1.0, "WHEAT": 1.0,
    "FERTILIZER": 1.0,
}
_CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
_ANIMALS = ("COW", "SHEEP", "GOOSE")
_STRUCTURE_KINDS = ("PASTURE", "COOP")
_QUADRANTS = ("NW", "NE", "SW", "SE")
_MAX_ACTORS = 13
_DEFAULT_CONFIGURATION = {"turnsPerDay": 24, "townShopSellInterval": 4, "townCenterSellInterval": 24}

# Live params (patched by configure()); starts as a copy of the defaults.
_P = dict(DEFAULT_PARAMS)


def configure(params):
    """Patch in a candidate parameter set (see tuning_spec.py for the spec
    these are drawn from). Call once per process before running games for
    that candidate -- cheap, and the per-episode STATE dicts below already
    self-reset on step==0 so this is safe to call between games too."""
    global _P
    _P = dict(DEFAULT_PARAMS)
    _P.update(params or {})
    _reset_all_state()


def _reset_all_state():
    for seat in (0, 1):
        _MIRROR_STATE[seat] = {"last_step": -1, "checks": {}, "locked": None}
        _SHIFT_STATE[seat]  = {"last_step": -1, "due_step": -1, "due": {}}
        _RELAY_STATE[seat]  = {"last_step": -1, "checks": {}, "locked": False, "due_step": -1, "due": 0}
        _OPPONENT_TYPE[seat] = "unknown"


# ===========================================================================
# Core obs helpers (mirrors main.py's own -- kept local so this module has
# no import-order dependency on main.py).
# ===========================================================================

def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _copy_action(action):
    action = dict(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands":  [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _shed_access(size):
    half = size // 2
    return {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}


def _projected_shed(obs, action):
    farm = _farm(obs, _seat(obs))
    private = _get(obs, "private", {}) or {}
    projected = {k: max(0, int(v or 0)) for k, v in dict(_get(private, "shed", {}) or {}).items()}
    inventories = list(_get(private, "inventories", []) or [])
    positions = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    tiles = list(_get(farm, "tiles", []) or [])
    access = _shed_access(len(tiles) or 10)
    for index, unit_action in enumerate(unit_actions):
        if index >= len(positions) or index >= len(inventories):
            continue
        position = positions[index]
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            continue
        x, y = int(position[0]), int(position[1])
        if (x, y) not in access or not (0 <= y < len(tiles) and 0 <= x < len(tiles[y])):
            continue
        inventory = {k: max(0, int(v or 0)) for k, v in dict(inventories[index] or {}).items()}
        if unit_action and unit_action[0] == "DROP":
            deposits = inventory.items()
        elif unit_action and unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item = unit_action[1]
            tile = tiles[y][x]
            structure = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}.get(item)
            if structure and isinstance(tile, dict) and tile.get("kind") == structure and not tile.get("animal"):
                continue
            try:
                requested = int(unit_action[2]) if len(unit_action) >= 3 else 1
            except (TypeError, ValueError):
                continue
            deposits = ((item, min(max(0, requested), inventory.get(item, 0))),)
        else:
            continue
        for item, quantity in deposits:
            room = max(0, 100 - sum(projected.values()))
            amount = min(max(0, int(quantity or 0)), room)
            if amount:
                projected[item] = projected.get(item, 0) + amount
    return projected


# ===========================================================================
# Opponent similarity / exposure.
# ===========================================================================

def _position(value):
    try:
        return (int(value[0]), int(value[1]))
    except (IndexError, TypeError, ValueError):
        return (-1, -1)


def _public_route_signature(farm):
    hands = list(_get(farm, "hands", []) or [])
    unlocks = set(_get(farm, "unlocked_quadrants", []) or [])
    positions = [_position(_get(farm, "farmer", (-1, -1)))]
    positions.extend(_position(item) for item in hands)
    positions = (positions + [(-1, -1)] * _MAX_ACTORS)[:_MAX_ACTORS]
    counts = {key: 0 for key in (*_CROPS, *_ANIMALS, *_STRUCTURE_KINDS, "WEED")}
    yields = {key: 0 for key in (*_CROPS, *_ANIMALS)}
    for row in (_get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            crop = str(tile.get("crop", "")).upper()
            animal = str(tile.get("animal", "")).upper()
            kind = str(tile.get("kind", "")).upper()
            if crop in counts:
                counts[crop] += 1
                yields[crop] += max(0, int(tile.get("yield_units", 0) or 0))
            if animal in counts:
                counts[animal] += 1
                yields[animal] += max(0, int(tile.get("yield_units", 0) or 0))
            if kind in _STRUCTURE_KINDS:
                counts[kind] += 1
            if kind == "WEED":
                counts["WEED"] += 1
    return {
        "workers": len(hands),
        "unlocks": sum(1 << i for i, name in enumerate(_QUADRANTS) if name in unlocks),
        "positions": [c for point in positions for c in point],
        "counts": [counts[k] for k in (*_CROPS, *_ANIMALS, *_STRUCTURE_KINDS, "WEED")],
        "yields": [yields[k] for k in (*_CROPS, *_ANIMALS)],
    }


def _signature_distance(left, right):
    total = 12.0 * abs(int(left["workers"]) - int(right["workers"]))
    total += 7.0 * (int(left["unlocks"]) ^ int(right["unlocks"])).bit_count()
    lp, rp = list(left["positions"]), list(right["positions"])
    for actor in range(_MAX_ACTORS):
        o = 2 * actor
        lpt, rpt = lp[o:o + 2], rp[o:o + 2]
        if lpt == [-1, -1] and rpt == [-1, -1]:
            continue
        weight = 0.8 if actor == 0 else 0.25
        total += weight * sum(abs(a - b) for a, b in zip(lpt, rpt))
    lc, rc = list(left["counts"]), list(right["counts"])
    for i, (a, b) in enumerate(zip(lc, rc)):
        total += (0.25 if i == len(lc) - 1 else 3.0) * abs(a - b)
    total += 0.15 * sum(abs(a - b) for a, b in zip(left["yields"], right["yields"]))
    return total


def _clone_distance(obs):
    farms = list(_get(obs, "farms", []) or [])
    if len(farms) < 2:
        return 10 ** 9
    return _signature_distance(_public_route_signature(farms[0]), _public_route_signature(farms[1]))


def _opponent_exposure(obs):
    seat = _seat(obs)
    farm = _farm(obs, 1 - seat)
    exposure = {item: 0.0 for item in _SELLABLE}
    for row in (_get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            yield_units = max(0.0, float(tile.get("yield_units", 0) or 0))
            crop = str(tile.get("crop", "")).upper()
            if crop in exposure and yield_units > 0:
                exposure[crop] += yield_units
            product = _PRODUCT_BY_ANIMAL.get(str(tile.get("animal", "")).upper())
            if product in exposure and yield_units > 0:
                exposure[product] += yield_units
    return exposure


def _count_driver(farm, kind, name):
    total = 0
    for row in (_get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            if kind == "animal":
                if str(tile.get("animal", "")).upper() == name:
                    total += 1
            elif tile.get("kind") == "PLANT" and str(tile.get("crop", "")).upper() == name:
                total += 1
    return total


_SUPPLY_DRIVER = {
    "MILK": ("animal", "COW"), "WOOL": ("animal", "SHEEP"),
    "STRAWBERRY": ("crop", "STRAWBERRY"), "MELON": ("crop", "MELON"),
}


def _opponent_supply_scale(obs, item):
    driver = _SUPPLY_DRIVER.get(item)
    if driver is None:
        return 1.0
    seat = _seat(obs)
    mine = _count_driver(_farm(obs, seat), *driver)
    theirs = _count_driver(_farm(obs, 1 - seat), *driver)
    if mine <= 0:
        return 2.0 if theirs > 0 else 1.0
    return max(0.0, min(2.0, theirs / float(mine)))


def _detect_opponent_type(obs, step):
    if step != 2:
        return
    seat = _seat(obs)
    opp_hands = len(_get(_farm(obs, 1 - seat), "hands", []) or [])
    if opp_hands <= 2:
        _OPPONENT_TYPE[seat] = "heavy_animal"
    elif opp_hands >= 4:
        _OPPONENT_TYPE[seat] = "high_worker"
    else:
        _OPPONENT_TYPE[seat] = "standard"


_OPPONENT_TYPE = {0: "unknown", 1: "unknown"}


# ===========================================================================
# Repay ledger helper + episode-reset helper.
# ===========================================================================

def _consume_due(market, item, remaining):
    out = []
    for raw in market:
        order = list(raw)
        if remaining > 0 and len(order) >= 3 and order[0] == "SELL" and order[1] == item:
            requested = max(0, int(order[2]))
            reduction = min(requested, remaining)
            requested -= reduction
            remaining -= reduction
            if requested <= 0:
                continue
            order[2] = requested
        out.append(order)
    return out


def _reset_if_new_episode(state, step, empty_factory):
    if step == 0 or step < int(state.get("last_step", -1)):
        state = empty_factory()
    state["last_step"] = step
    return state


# ===========================================================================
# Mirror-locked premium market lead.
# ===========================================================================

_MIRROR_CHECKPOINTS = (40, 70, 100)
_MIRROR_STATE = {0: {"last_step": -1, "checks": {}, "locked": None},
                  1: {"last_step": -1, "checks": {}, "locked": None}}
_SHIFT_STATE = {0: {"last_step": -1, "due_step": -1, "due": {}},
                 1: {"last_step": -1, "due_step": -1, "due": {}}}


def _mirror_state(obs, step):
    seat = _seat(obs)
    state = _reset_if_new_episode(_MIRROR_STATE[seat], step,
                                   lambda: {"last_step": step, "checks": {}, "locked": None})
    _MIRROR_STATE[seat] = state
    if step in _MIRROR_CHECKPOINTS and step not in state["checks"]:
        state["checks"][step] = _clone_distance(obs) <= float(_P["mirror_max_distance"])
        if all(cp in state["checks"] for cp in _MIRROR_CHECKPOINTS):
            state["locked"] = all(state["checks"].values())
    return state


def _shift_state(obs, step):
    seat = _seat(obs)
    _SHIFT_STATE[seat] = _reset_if_new_episode(_SHIFT_STATE[seat], step,
                                                lambda: {"last_step": step, "due_step": -1, "due": {}})
    return _SHIFT_STATE[seat]


def repay_premium_shift(obs, action, step):
    if not _P["premium_shift_enabled"]:
        return action
    state = _shift_state(obs, step)
    if int(state.get("due_step", -1)) != step:
        if int(state.get("due_step", -1)) < step:
            state["due_step"], state["due"] = -1, {}
        return action
    action = _copy_action(action)
    market = list(action.get("market") or [])
    for item, quantity in dict(state.get("due") or {}).items():
        market = _consume_due(market, item, max(0, int(quantity)))
    action["market"] = market
    state["due_step"], state["due"] = -1, {}
    return action


def _future_sells_at(backbone_route, step, horizon, items):
    idx = step + horizon
    if idx >= len(backbone_route):
        return {}
    result = {}
    for raw in (backbone_route[idx].get("market") or []):
        if len(raw) >= 3 and raw[0] == "SELL" and raw[1] in items:
            result[raw[1]] = result.get(raw[1], 0) + max(0, int(raw[2]))
    return result


def premium_shift(obs, action, step, backbone_route):
    if not _P["premium_shift_enabled"] or not (_P["premium_shift_start"] <= step < _P["premium_shift_stop"]):
        return action
    mirror = _mirror_state(obs, step)
    seat = _seat(obs)
    state = _shift_state(obs, step)
    if state.get("due"):
        return action
    if mirror["locked"]:
        eligible_items = _PREMIUM
    else:
        opponent_ready = _opponent_exposure(obs)
        eligible_items = tuple(i for i in _PREMIUM
                                if opponent_ready.get(i, 0) >= _P["premium_shift_opp_ready_threshold"])
    if not eligible_items:
        return action
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
    remaining = _projected_shed(obs, action)
    for raw in market:
        if len(raw) >= 3 and raw[0] == "SELL":
            remaining[raw[1]] = max(0, int(remaining.get(raw[1], 0) or 0) - max(0, int(raw[2])))
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}

    for horizon in (3, 2, 1):
        future = _future_sells_at(backbone_route, step, horizon, _PREMIUM)
        if not future:
            continue
        shifted = {}
        trial_market = list(market)
        trial_remaining = dict(remaining)
        for item in eligible_items:
            future_qty = max(0, int(future.get(item, 0) or 0))
            if future_qty < _P["premium_shift_min_future_qty"]:
                continue
            base_price = float(_MARKET_PARAMS[item][0])
            current_price = float(_get(prices, item, 0) or 0)
            if current_price <= _PRICE_FLOOR:
                continue
            target = min(
                max(0, int(trial_remaining.get(item, 0) or 0)),
                future_qty,
                int(_P["premium_shift_max_batch"]),
                max(1, int(round(future_qty * _P["premium_shift_fraction"]))),
            )
            if target <= 0 or len(trial_market) >= 10:
                continue
            trial_market.append(["SELL", item, target])
            trial_remaining[item] = max(0, int(trial_remaining.get(item, 0) or 0) - target)
            shifted[item] = target
        if shifted:
            action = _copy_action(action)
            action["market"] = trial_market[:10]
            state["due_step"], state["due"] = step + horizon, shifted
            return action
    return action


# ===========================================================================
# Fertilizer relay.
# ===========================================================================

_RELAY_CHECKPOINTS = (216, 240, 264)
_RELAY_STATE = {0: {"last_step": -1, "checks": {}, "locked": False, "due_step": -1, "due": 0},
                 1: {"last_step": -1, "checks": {}, "locked": False, "due_step": -1, "due": 0}}


def _relay_state(obs, step):
    seat = _seat(obs)
    state = _reset_if_new_episode(
        _RELAY_STATE[seat], step,
        lambda: {"last_step": step, "checks": {}, "locked": False, "due_step": -1, "due": 0})
    _RELAY_STATE[seat] = state
    if step in _RELAY_CHECKPOINTS and step not in state["checks"]:
        state["checks"][step] = _clone_distance(obs) <= float(_P["fert_relay_distance_max"])
        if all(cp in state["checks"] for cp in _RELAY_CHECKPOINTS):
            state["locked"] = all(state["checks"].values())
    return state


def _effective_relay_lead(seat):
    if _OPPONENT_TYPE.get(seat) == "heavy_animal":
        return int(_P["fert_relay_lead_heavy_animal"])
    return int(_P["fert_relay_lead"])


def repay_fertilizer_relay(obs, action, step):
    state = _relay_state(obs, step)
    due_step = int(state.get("due_step", -1))
    if due_step != step:
        if 0 <= due_step < step:
            state["due_step"], state["due"] = -1, 0
        return action
    action = _copy_action(action)
    action["market"] = _consume_due(list(action.get("market") or []), "FERTILIZER", max(0, int(state.get("due", 0))))
    state["due_step"], state["due"] = -1, 0
    return action


def fertilizer_relay(obs, action, step, backbone_route):
    if not _P["fert_relay_enabled"]:
        return action
    seat = _seat(obs)
    state = _relay_state(obs, step)
    if not state.get("locked") or state.get("due") or not (_P["fert_relay_start"] <= step <= _P["fert_relay_stop"]):
        return action
    lead = _effective_relay_lead(seat)
    future_step = step + lead
    if future_step >= len(backbone_route):
        return action
    target = sum(
        max(0, int(order[2]))
        for order in (backbone_route[future_step].get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == "FERTILIZER"
    )
    if target <= 0:
        return action
    market = [list(o) for o in (action.get("market") or [])]
    if len(market) >= 10:
        return action
    shed = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    available = max(0, int(_get(shed, "FERTILIZER", 0) or 0))
    for o in market:
        if len(o) >= 3 and o[0] == "SELL" and o[1] == "FERTILIZER":
            available = max(0, available - max(0, int(o[2])))
    quantity = min(target, available)
    if quantity <= 0:
        return action
    action = _copy_action(action)
    market.append(["SELL", "FERTILIZER", quantity])
    action["market"] = market[:10]
    state["due_step"], state["due"] = step + lead, quantity
    return action


# ===========================================================================
# Sell-slot ranking by price impact + demand urgency, and the price-floor
# guard.
# ===========================================================================

def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear": return value
    if name == "sq":     return value * value
    if name == "sqrt":   return math.sqrt(value)
    if name == "log":    return math.log1p(value)
    raise ValueError(name)


def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory)
    else:
        amplitude = above_target * base / _shape(above_func, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))


def _is_sell(order):
    return isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL" and order[1] in _MARKET_PARAMS


def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    prices = _get(market, "prices", {}) or {}
    current_inventory = int(_get(inventory, item, _I0) or 0)
    current_quote = float(_get(prices, item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)


def _demand_per_day(obs, configuration, item):
    town = _get(obs, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    turns_per_day = int(_get(configuration, "turnsPerDay", 24) or 24)
    shop_interval = max(1, int(_get(configuration, "townShopSellInterval", 4) or 4))
    demand = 0.0
    for shop in shops:
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += (turns_per_day / shop_interval) * (2 if len(products) == 1 else 1)
    if item != "FERTILIZER":
        center_interval = max(1, int(_get(configuration, "townCenterSellInterval", 24) or 24))
        demand += turns_per_day / center_interval
    return demand


def _order_score(obs, configuration, order):
    score = _impact_score(obs, order)
    if score <= 0 or not _is_sell(order):
        return score
    item = str(order[1])
    quantity = max(0, int(order[2]))
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    current_inventory = int(_get(inventory, item, _I0) or 0)
    demand = max(0.25, _demand_per_day(obs, configuration, item))
    excess = max(0.0, current_inventory + quantity - _I0)
    urgency = min(1.0, (excess / demand) / 10.0)
    return score * (1.0 + float(_P["demand_alpha"]) * urgency)


def rank_sell_slots(obs, action, configuration=None):
    if not _P["rank_sell_slots_enabled"]:
        return action
    configuration = configuration or _DEFAULT_CONFIGURATION
    action = _copy_action(action)
    market = list(action.get("market") or [])
    rows = [(_order_score(obs, configuration, order), -i, list(order))
            for i, order in enumerate(market) if _is_sell(order)]
    if len(rows) < 2:
        return action
    rows.sort(reverse=True)
    ranked = iter(row[2] for row in rows)
    action["market"] = [next(ranked) if _is_sell(order) else order for order in market]
    return action


def price_floor_guard(obs, action, step):
    if not _P["price_floor_enabled"]:
        return action
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    market = list(action.get("market") or [])
    if len(market) < 10:
        return action
    out = []
    for order in market:
        if _is_sell(order):
            current_price = float(_get(prices, str(order[1]), 999) or 999)
            if current_price <= _PRICE_FLOOR:
                continue
        out.append(order)
    action["market"] = out
    return action


# ===========================================================================
# Opportunistic surplus sell.
# ===========================================================================

_OPP_SELL_ITEMS = ("MILK", "WOOL", "STRAWBERRY", "MELON")


def _threshold_fraction(step):
    if step <= _P["opp_sell_ramp_start"]:
        return _P["opp_sell_base_fraction"]
    span = max(1, _P["opp_sell_stop"] - _P["opp_sell_ramp_start"])
    t = min(1.0, (step - _P["opp_sell_ramp_start"]) / span)
    return _P["opp_sell_base_fraction"] + t * (_P["opp_sell_floor_fraction"] - _P["opp_sell_base_fraction"])


def _reserve_price(obs, item, step):
    base = float(_MARKET_PARAMS[item][0])
    fraction = _threshold_fraction(step)
    supply_scale = _opponent_supply_scale(obs, item)
    supply_discount = min(1.0, 1.0 / max(1.0, supply_scale))
    supply_discount = max(_P["opp_sell_min_supply_fraction"], supply_discount)
    return base * fraction * supply_discount


def opportunistic_sell(obs, action, step):
    if not _P["opp_sell_enabled"] or not (_P["opp_sell_start"] <= step <= _P["opp_sell_stop"]):
        return action
    action = _copy_action(action)
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    projected = _projected_shed(obs, action)
    planned_sells = {}
    for order in market:
        if _is_sell(order):
            planned_sells[str(order[1])] = planned_sells.get(str(order[1]), 0) + max(0, int(order[2]))
    for item in _OPP_SELL_ITEMS:
        if len(market) >= 10:
            break
        current_price = float(_get(prices, item, 0) or 0)
        threshold = _reserve_price(obs, item, step)
        if current_price <= _PRICE_FLOOR or current_price < threshold:
            continue
        available = max(0, int(projected.get(item, 0) or 0))
        surplus = max(0, available - planned_sells.get(item, 0))
        if surplus <= 0:
            continue
        market.append(["SELL", item, min(surplus, int(_P["opp_sell_batch_cap"]))])
    action["market"] = market[:10]
    return action


# ===========================================================================
# Terminal liquidation.
# ===========================================================================

def terminal_liquidation(obs, action, step):
    if step < _P["terminal_soft_start"]:
        return action
    action = _copy_action(action)
    shed = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    exposure = _opponent_exposure(obs)
    planned = {item: 0 for item in _SELLABLE}
    for order in action.get("market", []):
        if _is_sell(order):
            planned[str(order[1])] += max(0, int(order[2]))
    full_dump = step >= _P["terminal_hard_start"]
    rows = []
    for item in _SELLABLE:
        available = max(0, int(_get(shed, item, 0) or 0))
        extra = available if full_dump else max(0, available - planned[item])
        if extra <= 0:
            continue
        score = ((1.0 + exposure.get(item, 0.0)) * _GLUT_WEIGHT.get(item, 1.0)
                 * max(1.0, float(_get(prices, item, 1) or 1)) * math.log1p(extra))
        rows.append((score, item, extra))
    rows.sort(key=lambda row: row[0], reverse=True)
    for _score, item, extra in rows:
        if len(action["market"]) >= 10:
            break
        action["market"].append(["SELL", item, extra])
    return action
