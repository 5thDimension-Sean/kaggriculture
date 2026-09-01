"""Test spatial mirrors of MtN's seat-1 logistics when deployed as seat 0."""

from __future__ import annotations

import copy
import os
import subprocess

import main
from tools import benchmark


TRANSFORMS = {
    "unmirrored": {},
    "east_west": {"EAST": "WEST", "WEST": "EAST"},
    "north_south": {"NORTH": "SOUTH", "SOUTH": "NORTH"},
    "rotate_180": {
        "EAST": "WEST",
        "WEST": "EAST",
        "NORTH": "SOUTH",
        "SOUTH": "NORTH",
    },
}


def transform_route(route, directions):
    transformed = copy.deepcopy(route)
    for action in transformed:
        actors = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
        for actor_action in actors:
            if actor_action:
                actor_action[0] = directions.get(actor_action[0], actor_action[0])
    return transformed


def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (farm.get("tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _production_with_recovery(obs, route, step, state):
    """Historical weed-recovery replay, kept local now that main.py issues
    the schedule unconditionally (see docs/aether-1.0-research.md)."""
    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    farm = (obs.get("farms") or [{}, {}])[seat]
    positions = [farm.get("farmer"), *list(farm.get("hands", []) or [])]
    delays = state.setdefault("delays", {})
    actions = []
    for index, position in enumerate(positions):
        actor = "farmer" if index == 0 else index - 1
        delay = int(delays.get(actor, 0))
        source = main._route_action(route, max(0, step - delay))
        intended = list(source["farmer"]) if actor == "farmer" else list(
            source["hands"][actor] if actor < len(source["hands"]) else ["PASS"]
        )
        tile = _tile_at(farm, position)
        if (
            intended
            and intended[0] in ("BUILD_PASTURE", "PLANT")
            and isinstance(tile, dict)
            and tile.get("kind") == "WEED"
        ):
            delays[actor] = delay + 1
            intended = ["DIG"]
        actions.append(intended)
    return (actions[0] if actions else ["PASS"]), actions[1:]


def route_agent(route):
    state = {"last_step": -1, "delays": {}}

    def run(obs):
        step = max(0, int(obs.get("step", 0) or 0))
        if step == 0 or step < state["last_step"]:
            state.update(last_step=step, delays={})
        state["last_step"] = step
        scheduled = main._route_action(route, step)
        farmer, hands = _production_with_recovery(obs, route, step, state)
        return {
            "farmer": farmer,
            "hands": hands,
            "market": main._sanitize_market(scheduled["market"]),
        }

    return run


def git_agent(ref):
    source = subprocess.check_output(
        ["git", "show", f"{ref}:main.py"], cwd=os.path.dirname(os.path.dirname(__file__))
    ).decode("utf-8")
    namespace = {"__file__": os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")}
    exec(compile(source, f"{ref}:main.py", "exec"), namespace)
    return namespace["agent"]


def main_cli():
    opponent = benchmark.load_agent("opponents/mapleleaf_6_7.py")
    seeds = benchmark._SEEDS_P0[:5]
    rows = {}
    for name, directions in TRANSFORMS.items():
        agent = route_agent(transform_route(main._ROUTES["mtn_p1"], directions))
        scores = [benchmark.run_game(agent, opponent, seed) for seed in seeds]
        rows[name] = scores
    rows["before_a6c0506"] = [
        benchmark.run_game(git_agent("a6c0506"), opponent, seed) for seed in seeds
    ]
    baseline_scores = [score[0] for score in rows["unmirrored"]]
    for name, scores in rows.items():
        own = [score[0] for score in scores]
        other = [score[1] for score in scores]
        wins = sum(left > right for left, right in scores)
        mean = sum(own) / len(own)
        margin = sum(left - right for left, right in scores) / len(scores)
        paired = sum(value - base for value, base in zip(own, baseline_scores)) / len(own)
        print(
            f"{name:14s} wins={wins}/{len(scores)} mean={mean:9,.0f} "
            f"margin={margin:+9,.0f} paired_vs_before={paired:+9,.0f}"
        )


if __name__ == "__main__":
    main_cli()
