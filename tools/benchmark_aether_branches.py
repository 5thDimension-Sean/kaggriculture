"""Measure Aether's seat-0 demonstration branches independently."""

import argparse

import main
from tools import benchmark


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


def forced_agent(mode):
    state = {"last_step": -1, "mode": mode, "delays": {}}
    route = main._ROUTES[mode]

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


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()
    opponent = benchmark.load_agent("opponents/mapleleaf_6_7.py")
    seeds = benchmark._SEEDS_P0[: args.n]
    for mode in ("animal_pressure", "dairy_pressure", "crop_pressure", "mtn_p1"):
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
