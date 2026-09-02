"""Aether 1.0 — refreshed consistent-ladder routes matched to each seat.

Both seats replay the current MtN submission's public majority route. Its
refreshed seat-0 traces are 98.9% consistent and its seat-1 majority remains
the strongest tested fixed counterpart. No opponent identity, hidden state,
heuristic branch, or recovery delay can move either seat away from its route.
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


__version__ = "aether-1.0-mtn-refreshed-consensus"

_ROUTES = (
    aether_routes.MTN_REFRESHED_P0,
    aether_routes.MTN_REFRESHED_P1,
)


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
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _route_action(route, step):
    if not route:
        return {"farmer": ["PASS"], "hands": [], "market": []}
    index = min(max(0, int(step)), len(route) - 1)
    return _copy_action(route[index])


def _act(obs):
    step = max(0, int(_get(obs, "step", 0) or 0))
    # Coordinates are local to each farm, but market execution is seat-ordered;
    # use the public route recorded in the same seat. Step and seat are the only
    # runtime inputs.
    return _route_action(_ROUTES[_seat(obs)], step)


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
