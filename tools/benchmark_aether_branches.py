"""Measure Aether's seat-0 demonstration branches independently."""

import argparse

import main
from tools import benchmark


def forced_agent(mode):
    state = {"last_step": -1, "mode": mode, "delays": {}}
    route = main._ROUTES[mode]

    def run(obs):
        step = max(0, int(obs.get("step", 0) or 0))
        if step == 0 or step < state["last_step"]:
            state.update(last_step=step, delays={})
        state["last_step"] = step
        scheduled = main._route_action(route, step)
        farmer, hands = main._production_with_recovery(obs, route, step, state)
        return {
            "farmer": farmer,
            "hands": hands,
            "market": main._sanitize_market(scheduled["market"]),
        }

    return run


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()
    opponent = benchmark.load_agent("opponents/mapleleaf_6_7.py")
    seeds = benchmark._SEEDS_P0[: args.n]
    for mode in ("animal_pressure", "dairy_pressure", "crop_pressure"):
        agent = forced_agent(mode)
        rows = []
        for seed in seeds:
            own, other = benchmark.run_game(agent, opponent, seed)
            rows.append((own, other))
        wins = sum(own > other for own, other in rows)
        mean = sum(own for own, _ in rows) / len(rows)
        delta = sum(own - other for own, other in rows) / len(rows)
        print(f"{mode:18s} wins={wins}/{len(rows)} mean={mean:,.0f} delta={delta:+,.0f}")


if __name__ == "__main__":
    main_cli()
