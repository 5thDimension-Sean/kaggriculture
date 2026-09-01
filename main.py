"""Aether 1.0 — exact seat-1 logistics copied to both Kaggriculture seats.

Both seats issue MtN's 99.2%-consistent seat-1 action schedule unchanged:
same directions, worker actions, crops, animals, market order slots, and
quantities, on every step, regardless of either farm's own tile state. The
runtime contains no player-name or hidden-state checks.
"""

from __future__ import annotations

import copy
import os
import sys

# Kaggle can exec this source without defining __file__. The submission
# builder replaces this import with an in-memory module.
if "__file__" in globals():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aether_routes


__version__ = "aether-1.0-seat1-exact-copy"

_P0_FORK_STEP = 73
_PRESSURE_THRESHOLD = 9995
_ROUTES = {
    "animal_pressure": aether_routes.P0_ANIMAL_PRESSURE,
    "dairy_pressure": aether_routes.P0_DAIRY_PRESSURE,
    "crop_pressure": aether_routes.P0_CROP_PRESSURE,
    "mtn_p1": aether_routes.P1_MTN_CONSENSUS,
}


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


def _market_inventory(obs):
    market = _get(obs, "market", {}) or {}
    return _get(market, "inventory", {}) or {}


def _public_route_mode(obs):
    """Reconstruct the leaders' first-day opponent fingerprint.

    In the sampled public games, Driz Lo and MtN both forked their complete
    seat-0 route when WOOL supply fell to 9995 or below. Tetsuya used that
    same signal plus MILK supply to choose a melon-heavy or
    strawberry-heavy crop branch. These tests use public state only.
    """
    inventory = _market_inventory(obs)
    wool = int(_get(inventory, "WOOL", 10000) or 0)
    milk = int(_get(inventory, "MILK", 10000) or 0)
    if wool <= _PRESSURE_THRESHOLD:
        return "animal_pressure"
    if milk <= _PRESSURE_THRESHOLD:
        return "dairy_pressure"
    return "crop_pressure"


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _route_action(route, step):
    if not route:
        return {"farmer": ["PASS"], "hands": [], "market": []}
    index = min(max(0, int(step)), len(route) - 1)
    return _copy_action(route[index])


def _sanitize_market(orders):
    clean = []
    for order in list(orders or []):
        if not isinstance(order, (list, tuple)) or not order:
            continue
        item = list(order)
        if len(item) >= 3:
            try:
                item[2] = max(0, int(item[2]))
            except (TypeError, ValueError):
                continue
            if item[2] == 0:
                continue
        clean.append(item)
        if len(clean) == 10:
            break
    return clean


def _act(obs):
    step = max(0, int(_get(obs, "step", 0) or 0))
    # Kaggriculture farm coordinates are local to each player, so the stable
    # seat-1 worker schedule transfers directly to seat 0—no EAST/WEST mirror.
    # The schedule is issued verbatim from `step` alone, with no dependence on
    # either farm's own tile state, so both seats always emit byte-identical
    # actions regardless of where weeds randomly spawn on each farm.
    scheduled = _route_action(_ROUTES["mtn_p1"], step)
    return {
        "farmer": scheduled["farmer"],
        "hands": scheduled["hands"],
        "market": _sanitize_market(scheduled["market"]),
    }


def agent(obs):
    try:
        return _act(obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs)
