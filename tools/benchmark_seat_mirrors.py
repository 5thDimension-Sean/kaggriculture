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


def route_agent(route):
    state = {"last_step": -1, "pressure": "crop_pressure", "delays": {}}

    def run(obs):
        step = max(0, int(obs.get("step", 0) or 0))
        if step == 0 or step < state["last_step"]:
            state.update(last_step=step, pressure="crop_pressure", delays={})
        state["last_step"] = step
        if step >= main._P0_FORK_STEP and (step - main._P0_FORK_STEP) % 72 == 0:
            state["pressure"] = main._public_route_mode(obs)
        scheduled = main._route_action(route, step)
        farmer, hands = main._production_with_recovery(obs, route, step, state)
        return {
            "farmer": farmer,
            "hands": hands,
            "market": main._prioritize_pressure_sales(
                scheduled["market"], state["pressure"]
            ),
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
