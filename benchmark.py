"""
benchmark.py — Local 20-game head-to-head benchmarker.

Usage:
    python benchmark.py                          # main.py vs main_bc.py (default)
    python benchmark.py --a main.py --b main_bc.py
    python benchmark.py --n 40                   # run 40 games instead of 20

Each run plays N//2 games with agent A as P0 and N//2 games with A as P1,
covering both market-position advantages.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_agent(path):
    """Load an agent function from a .py file."""
    path = os.path.abspath(path)
    # Inject __file__ so agents can resolve sibling files (e.g. weights_bc.npz)
    ns = {"__file__": path}
    with open(path) as f:
        exec(compile(f.read(), path, "exec"), ns)
    if "agent" not in ns:
        raise ValueError(f"No 'agent' function found in {path}")
    return ns["agent"]


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


def benchmark(agent_a, agent_b, name_a, name_b, n_games=20):
    half   = n_games // 2
    seeds  = list(range(3000, 3000 + half))

    wins_a = wins_b = ties = 0
    scores_a = []
    scores_b = []

    print(f"\n{'─'*62}")
    print(f"  {name_a:25s}  vs  {name_b}")
    print(f"{'─'*62}")

    # A as P0 (goes first in market each turn)
    print(f"\n  [{name_a} as P0]")
    for i, seed in enumerate(seeds):
        sa, sb = run_game(agent_a, agent_b, seed)
        scores_a.append(sa); scores_b.append(sb)
        if   sa > sb: wins_a += 1; tag = f"{name_a} WIN"
        elif sb > sa: wins_b += 1; tag = f"{name_b} WIN"
        else:         ties   += 1; tag = "TIE"
        print(f"    game {i+1:2d} (seed={seed}): "
              f"{name_a}={sa:>8,.0f}  {name_b}={sb:>8,.0f}  → {tag}")

    # A as P1 (market second)
    print(f"\n  [{name_a} as P1]")
    for i, seed in enumerate(seeds):
        sb, sa = run_game(agent_b, agent_a, seed + 10000)
        scores_a.append(sa); scores_b.append(sb)
        if   sa > sb: wins_a += 1; tag = f"{name_a} WIN"
        elif sb > sa: wins_b += 1; tag = f"{name_b} WIN"
        else:         ties   += 1; tag = "TIE"
        print(f"    game {i+1:2d} (seed={seed+10000}): "
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


def sanity_check(agent_b, name_b):
    """Run 3 steps with agent_b and print what it returns, so we can confirm it's acting."""
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 3}, debug=False)
    results = []

    def spy(obs):
        action = agent_b(obs)
        results.append(action)
        return action

    env.run(["random", spy])
    print(f"\n[sanity] {name_b} first 3 actions:")
    for i, a in enumerate(results):
        print(f"  step {i}: farmer={a.get('farmer')}  market={a.get('market', [])[:2]}")
    print()


def main():
    ap = argparse.ArgumentParser(description="20-game head-to-head benchmark")
    ap.add_argument("--a", default="main.py",    help="Agent A file (default: main.py)")
    ap.add_argument("--b", default="main_bc.py", help="Agent B file (default: main_bc.py)")
    ap.add_argument("--n", type=int, default=20,  help="Total games (default: 20, must be even)")
    args = ap.parse_args()

    if args.n % 2 != 0:
        sys.exit("--n must be even (half played as P0, half as P1)")

    project_root = os.path.dirname(os.path.abspath(__file__))
    path_a = args.a if os.path.isabs(args.a) else os.path.join(project_root, args.a)
    path_b = args.b if os.path.isabs(args.b) else os.path.join(project_root, args.b)

    print(f"Loading agents...")
    print(f"  A: {path_a}")
    print(f"  B: {path_b}")

    agent_a = load_agent(path_a)
    agent_b = load_agent(path_b)

    name_a = os.path.splitext(os.path.basename(path_a))[0]
    name_b = os.path.splitext(os.path.basename(path_b))[0]

    sanity_check(agent_b, name_b)
    benchmark(agent_a, agent_b, name_a, name_b, n_games=args.n)


if __name__ == "__main__":
    main()
