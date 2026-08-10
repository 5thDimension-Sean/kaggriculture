"""
benchmark.py — Head-to-head benchmarker for Kaggriculture agents.

Usage:
    python benchmark.py                              # main.py vs models/5_0.py
    python benchmark.py --a main.py --b models/5_0.py
    python benchmark.py --a main.py --b route-only  # vs bare route (no market logic)
    python benchmark.py --n 40                       # run 40 games

Each run plays N//2 games with agent A as P0, N//2 games with agent A as P1.

Passing --b route-only generates a stripped version of agent A that skips all
market-intelligence overlays and executes the raw route actions literally.
This lets you measure how much the market logic contributes.

Seeds are fixed so the same matchup always produces the same numbers.
"""

import argparse
import os
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_agent(path):
    """Load an agent function from a .py file."""
    path = os.path.abspath(path)
    ns = {"__file__": path}
    with open(path) as f:
        exec(compile(f.read(), path, "exec"), ns)
    if "agent" not in ns:
        raise ValueError(f"No 'agent' function found in {path}")
    return ns["agent"]


def make_route_only_agent(path):
    """Return an agent that executes the raw route with NO market overlays.

    Used as a baseline to measure how much market intelligence contributes.
    The agent still calls _align_hands and _weed_repair_action (safety only),
    but skips all sell-reordering, premium-shift, price-gate, etc.
    """
    path = os.path.abspath(path)
    ns = {"__file__": path}
    with open(path) as f:
        exec(compile(f.read(), path, "exec"), ns)

    _ACTIONS       = ns["_ACTIONS"]
    _align_hands   = ns["_align_hands"]
    _copy_action   = ns["_copy_action"]
    _weed_repair   = ns.get("_weed_repair_action")

    def route_only_agent(obs):
        try:
            step = min(max(0, int((obs.get("step") or 0))), len(_ACTIONS) - 1)
            action = _copy_action(_ACTIONS[step])
            if _weed_repair is not None:
                action = _weed_repair(obs, action, _ACTIONS, step)
            return _align_hands(action, obs)
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return route_only_agent


def run_game(agent_a, agent_b, seed):
    from kaggle_environments import make
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed},
        debug=False,
    )
    env.run([agent_a, agent_b])
    final = env.steps[-1]
    return float(final[0].reward or 0), float(final[1].reward or 0)


_SEEDS_P0 = [
    7030039913, 1767950141, 2067004398, 4263648760, 3313394522,
    3101419947, 3930751749, 5948990031, 3837117532, 2455163851,
]
_SEEDS_P1 = [
    4326338643, 7309474672, 2729251472, 5327694078, 6170128796,
    3294844113, 4866511089, 7895609197, 5194945606, 2535557871,
]


def benchmark(agent_a, agent_b, name_a, name_b, n_games=20):
    half     = n_games // 2
    seeds_p0 = _SEEDS_P0[:half]
    seeds_p1 = _SEEDS_P1[:half]

    wins_a = wins_b = ties = 0
    scores_a = []
    scores_b = []

    print(f"\n{'─'*62}")
    print(f"  {name_a:25s}  vs  {name_b}")
    print(f"{'─'*62}")

    print(f"\n  [{name_a} as P0]")
    for i, seed in enumerate(seeds_p0):
        sa, sb = run_game(agent_a, agent_b, seed)
        scores_a.append(sa); scores_b.append(sb)
        if   sa > sb: wins_a += 1; tag = f"{name_a} WIN"
        elif sb > sa: wins_b += 1; tag = f"{name_b} WIN"
        else:         ties   += 1; tag = "TIE"
        print(f"    game {i+1:2d} (seed={seed}): "
              f"{name_a}={sa:>8,.0f}  {name_b}={sb:>8,.0f}  → {tag}")

    print(f"\n  [{name_a} as P1]")
    for i, seed in enumerate(seeds_p1):
        sb, sa = run_game(agent_b, agent_a, seed)
        scores_a.append(sa); scores_b.append(sb)
        if   sa > sb: wins_a += 1; tag = f"{name_a} WIN"
        elif sb > sa: wins_b += 1; tag = f"{name_b} WIN"
        else:         ties   += 1; tag = "TIE"
        print(f"    game {i+1:2d} (seed={seed}): "
              f"{name_a}={sa:>8,.0f}  {name_b}={sb:>8,.0f}  → {tag}")

    total  = wins_a + wins_b + ties
    mean_a = sum(scores_a) / len(scores_a)
    mean_b = sum(scores_b) / len(scores_b)
    delta  = mean_a - mean_b

    print(f"\n{'═'*62}")
    print(f"  RESULTS ({total} games)")
    print(f"  {name_a:25s}  wins: {wins_a}/{total}  mean: {mean_a:>8,.0f}")
    print(f"  {name_b:25s}  wins: {wins_b}/{total}  mean: {mean_b:>8,.0f}")
    print(f"  delta (A - B):               {delta:>+9,.0f} per game")
    print(f"{'═'*62}\n")

    return wins_a, wins_b, ties, mean_a, mean_b


def sanity_check(agent, name):
    """Print first 3 actions and env version."""
    from kaggle_environments import make
    import kaggle_environments
    print(f"\n[sanity] kaggle_environments version: {kaggle_environments.__version__}")

    globs = getattr(agent, "__globals__", {})
    net = globs.get("_NET")
    if net is not None:
        import numpy as np
        print(f"[sanity] _NET W1 norm: {float(__import__('numpy').linalg.norm(net.W1)):.2f}")
    else:
        print("[sanity] (no _NET — route-replay agent)")

    env = make("kaggriculture", configuration={"episodeSteps": 4}, debug=False)
    results = []

    def spy(obs):
        action = agent(obs)
        results.append(action)
        return action

    env.run([spy, "random"])
    print(f"\n[sanity] {name} first {len(results)} actions (as P0):")
    for i, a in enumerate(results):
        print(f"  step {i}: farmer={a.get('farmer')}  market={a.get('market', [])[:2]}")
    print()


def main():
    ap = argparse.ArgumentParser(
        description="Kaggriculture head-to-head benchmarker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python benchmark.py                              # main.py vs models/5_0.py
              python benchmark.py --b route-only              # vs bare route (measures market logic)
              python benchmark.py --a models/5_1.py --b models/5_0.py
              python benchmark.py --n 40
        """),
    )
    ap.add_argument("--a", default="main.py",         help="Agent A (default: main.py)")
    ap.add_argument("--b", default="models/5_0.py",   help="Agent B or 'route-only' (default: models/5_0.py)")
    ap.add_argument("--n", type=int, default=20,       help="Total games, must be even (default: 20)")
    args = ap.parse_args()

    if args.n % 2 != 0:
        sys.exit("--n must be even")

    project_root = os.path.dirname(os.path.abspath(__file__))
    path_a = args.a if os.path.isabs(args.a) else os.path.join(project_root, args.a)

    print(f"Loading agents...")
    print(f"  A: {path_a}")

    agent_a = load_agent(path_a)
    name_a  = os.path.splitext(os.path.basename(path_a))[0]

    if args.b == "route-only":
        print(f"  B: route-only (bare route from {path_a}, no market overlays)")
        agent_b = make_route_only_agent(path_a)
        name_b  = "route-only"
    else:
        path_b = args.b if os.path.isabs(args.b) else os.path.join(project_root, args.b)
        print(f"  B: {path_b}")
        agent_b = load_agent(path_b)
        name_b  = os.path.splitext(os.path.basename(path_b))[0]

    sanity_check(agent_b, name_b)
    benchmark(agent_a, agent_b, name_a, name_b, n_games=args.n)


if __name__ == "__main__":
    main()
