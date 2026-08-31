"""
extract_routes.py — Extract + benchmark every top-route from training JSON replays.

Usage:
    python3 extract_routes.py                       # uses training data/ folder
    python3 extract_routes.py --dir /path/to/json  # custom folder
    python3 extract_routes.py --top 10 --games 10  # test top 10 routes, 10 games each

Outputs:
    routes/route_<episode>_p<player>.py    — standalone agent file for each route
    routes/best_route.py                   — best-performing route (copy to use as 4.6 backbone)
"""

import argparse
import base64
import glob
import json
import os
import sys
import zlib


# ── Route extraction ──────────────────────────────────────────────────────────

def extract_routes_from_episode(fpath):
    """Return list of (player_idx, score, actions) for each player."""
    with open(fpath) as f:
        data = json.load(f)
    rewards = data.get("rewards", [0, 0])
    steps   = data.get("steps", [])
    results = []
    for player in range(min(2, len(rewards))):
        score   = float(rewards[player] or 0)
        actions = []
        for step in steps:
            if player < len(step):
                action = step[player].get("action", {})
                # Normalize: keep farmer, hands, market; drop debug fields
                clean = {
                    "farmer": action.get("farmer", ["PASS"]),
                    "hands":  action.get("hands", []),
                    "market": action.get("market", []),
                }
                actions.append(clean)
        # Strip leading empty step (training JSONs include a step-0 PASS that
        # the 4.5 route backbone omits — dropping it keeps the index aligned).
        if actions and (
            actions[0].get("farmer") == ["PASS"]
            and not actions[0].get("hands")
            and not actions[0].get("market")
        ):
            actions = actions[1:]
        if len(actions) >= 100:   # skip truncated episodes
            results.append((player, score, actions))
    return results


def encode_actions(actions):
    """Compress actions to base85 string (same format as MapleLeaf _ACTIONS)."""
    raw     = json.dumps(actions, separators=(",", ":")).encode()
    return base64.b85encode(zlib.compress(raw, level=9)).decode()


def make_agent_py(encoded, episode_id, player, score, template_path="4_5.py"):
    """Build a standalone agent .py that uses the given encoded route + template overlays."""
    with open(template_path) as f:
        src = f.read()

    import re
    # The action tape is deliberately kept on one line in the production
    # source. Replace that complete assignment instead of coupling this tool
    # to the exact decode/parenthesis formatting used by a particular version.
    new_actions = (
        "_ACTIONS = json.loads(zlib.decompress(base64.b85decode("
        f"{encoded!r})).decode('utf-8'))"
    )
    new_src, replacement_count = re.subn(
        r"^_ACTIONS\s*=.*$", new_actions, src, count=1, flags=re.MULTILINE
    )
    if replacement_count != 1:
        raise ValueError("template must contain exactly one one-line _ACTIONS assignment")

    # Update the docstring header — works for any MapleLeaf version
    new_src = re.sub(
        r'"""Kaggriculture agent — MapleLeaf \d+\.\d+[^\n]*',
        f'"""Kaggriculture agent — Route candidate ep={episode_id} P{player} score={score:,.0f}',
        new_src,
        count=1,
    )
    return new_src


# ── Benchmark helper ──────────────────────────────────────────────────────────

def run_benchmark(agent_a_path, agent_b_path, n_games=10):
    """Quick benchmark: returns (wins_a, mean_a, mean_b)."""
    import importlib.util

    def load(path):
        ns = {"__file__": os.path.abspath(path)}
        with open(path) as f:
            exec(compile(f.read(), path, "exec"), ns)
        return ns["agent"]

    agent_a = load(agent_a_path)
    agent_b = load(agent_b_path)

    from kaggle_environments import make

    half = n_games // 2
    seeds_a = list(range(3000, 3000 + half))
    wins_a = 0
    scores_a, scores_b = [], []

    for seed in seeds_a:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([agent_a, agent_b])
        final = env.steps[-1]
        sa, sb = float(final[0].reward or 0), float(final[1].reward or 0)
        scores_a.append(sa); scores_b.append(sb)
        if sa > sb: wins_a += 1

    for seed in seeds_a:
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed + 10000}, debug=False)
        env.run([agent_b, agent_a])
        final = env.steps[-1]
        sb, sa = float(final[0].reward or 0), float(final[1].reward or 0)
        scores_a.append(sa); scores_b.append(sb)
        if sa > sb: wins_a += 1

    mean_a = sum(scores_a) / len(scores_a)
    mean_b = sum(scores_b) / len(scores_b)
    return wins_a, mean_a, mean_b


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir",   default="training data", help="Folder with episode JSONs")
    ap.add_argument("--top",   type=int, default=20,    help="Number of top routes to test")
    ap.add_argument("--games", type=int, default=10,    help="Games per route benchmark")
    ap.add_argument("--vs",    default="4_5.py",         help="Baseline agent to beat")
    ap.add_argument("--out",   default="routes",         help="Output folder")
    ap.add_argument("--team",  default="",               help="Only extract the named team's seat from each replay")
    ap.add_argument("--skip-benchmark", action="store_true", help="Only generate route agents")
    args = ap.parse_args()

    replay_dir = args.dir
    os.makedirs(args.out, exist_ok=True)

    # ── Step 1: Scan all episodes, rank by winner score ───────────────────────
    print(f"\nScanning {replay_dir} ...")
    all_candidates = []
    for fpath in sorted(glob.glob(os.path.join(replay_dir, "*.json"))):
        try:
            routes = extract_routes_from_episode(fpath)
            if args.team:
                with open(fpath) as handle:
                    team_names = json.load(handle).get("info", {}).get("TeamNames", [])
                if args.team not in team_names:
                    continue
                team_seat = team_names.index(args.team)
                routes = [route for route in routes if route[0] == team_seat]
            for player, score, actions in routes:
                ep_id = os.path.basename(fpath).replace(".json", "")
                all_candidates.append((score, ep_id, player, fpath, actions))
        except Exception as e:
            print(f"  skip {os.path.basename(fpath)}: {e}")

    if not all_candidates:
        sys.exit("No valid episodes found.")

    # Sort by winner score, deduplicate by episode (keep highest scorer)
    all_candidates.sort(reverse=True)
    seen_eps = {}
    unique = []
    for score, ep_id, player, fpath, actions in all_candidates:
        if ep_id not in seen_eps:
            seen_eps[ep_id] = True
            unique.append((score, ep_id, player, fpath, actions))

    top = unique[: args.top]
    print(f"Found {len(all_candidates)} player-routes across {len(unique)} episodes.")
    print(f"Testing top {len(top)} routes vs {args.vs}:\n")

    # ── Step 2: Write each route as a standalone agent .py ───────────────────
    route_files = []
    for rank, (score, ep_id, player, fpath, actions) in enumerate(top, 1):
        encoded = encode_actions(actions)
        py_src  = make_agent_py(encoded, ep_id, player, score, template_path=args.vs)
        out_path = os.path.join(args.out, f"route_{rank:02d}_ep{ep_id}_p{player}.py")
        with open(out_path, "w") as f:
            f.write(py_src)
        route_files.append((rank, score, ep_id, player, out_path))
        print(f"  [{rank:02d}] ep={ep_id} P{player} score={score:,.0f}  ->  {out_path}")

    print()

    if args.skip_benchmark:
        print(f"Generated {len(route_files)} route agents in {args.out}")
        return

    # ── Step 3: Benchmark each route against the baseline ────────────────────
    results = []
    for rank, score, ep_id, player, rpath in route_files:
        try:
            wins, mean_r, mean_b = run_benchmark(rpath, args.vs, n_games=args.games)
            delta = mean_r - mean_b
            tag   = "+" if delta >= 0 else ""
            print(f"  [{rank:02d}] ep={ep_id} P{player}  wins={wins}/{args.games}  "
                  f"mean={mean_r:,.0f}  delta={tag}{delta:,.0f}")
            results.append((delta, wins, mean_r, rank, ep_id, player, rpath))
        except Exception as e:
            print(f"  [{rank:02d}] BENCHMARK ERROR: {e}")

    if not results:
        sys.exit("No benchmark results.")

    # ── Step 4: Report winner and write best_route.py ─────────────────────────
    results.sort(reverse=True)
    best_delta, best_wins, best_mean, best_rank, best_ep, best_player, best_path = results[0]

    print(f"\n{'='*62}")
    print(f"  WINNER: rank={best_rank}  ep={best_ep}  P{best_player}")
    print(f"  mean={best_mean:,.0f}  delta vs {args.vs}: {'+' if best_delta>=0 else ''}{best_delta:,.0f}")
    print(f"{'='*62}")

    import shutil
    best_out = os.path.join(args.out, "best_route.py")
    shutil.copy(best_path, best_out)
    print(f"\n  Best route saved to: {best_out}")
    print(f"  Copy to 4_6.py and run: python3 benchmark.py --a 4_6.py --b 4_5.py --n 20\n")


if __name__ == "__main__":
    main()
