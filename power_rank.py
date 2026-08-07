"""
power_rank.py — Benchmark all MapleLeaf versions against the 4_1 baseline
and print a power ranking table.

Usage:
    python power_rank.py
    python power_rank.py --n 20      # games per matchup (default 20, must be even)
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSIONS = [
    ("4.2", "main_bc.py"),
    ("4.3", "4_3.py"),
    ("4.4", "4_4.py"),
    ("4.5", "4_5.py"),
    ("4.6", "4_6.py"),
]
BASELINE = ("4.1", "4_1.py")


def load_agent(path):
    path = os.path.abspath(path)
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


def matchup(challenger_agent, baseline_agent, n_games=20):
    half  = n_games // 2
    seeds = list(range(3000, 3000 + half))
    wins = losses = ties = 0
    scores_c = []
    scores_b = []

    for seed in seeds:
        sc, sb = run_game(challenger_agent, baseline_agent, seed)
        scores_c.append(sc); scores_b.append(sb)
        if sc > sb: wins += 1
        elif sb > sc: losses += 1
        else: ties += 1

    for seed in seeds:
        sb, sc = run_game(baseline_agent, challenger_agent, seed + 10000)
        scores_c.append(sc); scores_b.append(sb)
        if sc > sb: wins += 1
        elif sb > sc: losses += 1
        else: ties += 1

    total  = wins + losses + ties
    mean_c = sum(scores_c) / len(scores_c)
    mean_b = sum(scores_b) / len(scores_b)
    return wins, losses, ties, total, mean_c, mean_b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20, help="Games per matchup (must be even)")
    args = ap.parse_args()
    if args.n % 2 != 0:
        sys.exit("--n must be even")

    root = os.path.dirname(os.path.abspath(__file__))

    print(f"\nLoading agents...")
    baseline_agent = load_agent(os.path.join(root, BASELINE[1]))
    challengers = []
    for label, fname in VERSIONS:
        path = os.path.join(root, fname)
        ag = load_agent(path)
        challengers.append((label, fname, ag))
        print(f"  MapleLeaf {label}  ← {fname}")

    print(f"\nBaseline: MapleLeaf {BASELINE[0]}  ← {BASELINE[1]}")
    print(f"Games per matchup: {args.n}")
    print(f"\nRunning {len(challengers)} matchups ({len(challengers) * args.n} games total)...\n")

    results = []
    for label, fname, ag in challengers:
        t0 = time.time()
        print(f"  MapleLeaf {label} vs {BASELINE[0]}...", end=" ", flush=True)
        w, l, t, total, mc, mb = matchup(ag, baseline_agent, args.n)
        elapsed = time.time() - t0
        delta = mc - mb
        print(f"{w}/{total} wins  delta={delta:+,.0f}  ({elapsed:.0f}s)")
        results.append((label, fname, w, l, t, total, mc, mb, delta))

    # Sort by win count desc, then by delta desc
    results.sort(key=lambda r: (r[2], r[8]), reverse=True)

    print(f"\n{'═'*72}")
    print(f"  POWER RANKINGS  (vs MapleLeaf 4.1 baseline, {args.n} games each)")
    print(f"{'═'*72}")
    print(f"  {'Rank':<5} {'Version':<12} {'File':<14} {'W/L/T':<12} {'Win%':<8} {'Mean Score':>12} {'Delta vs 4.1':>14}")
    print(f"  {'─'*5} {'─'*12} {'─'*14} {'─'*12} {'─'*8} {'─'*12} {'─'*14}")
    for rank, (label, fname, w, l, t, total, mc, mb, delta) in enumerate(results, 1):
        wlt = f"{w}/{l}/{t}"
        winpct = f"{100*w/total:.1f}%"
        print(f"  #{rank:<4} {'ML '+label:<12} {fname:<14} {wlt:<12} {winpct:<8} {mc:>12,.0f} {delta:>+14,.0f}")
    print(f"  {'─'*72}")
    print(f"  {'(base)':<5} {'ML 4.1':<12} {'4_1.py':<14} {'—':<12} {'—':<8} {mb:>12,.0f} {'—':>14}")
    print(f"{'═'*72}\n")


if __name__ == "__main__":
    main()
