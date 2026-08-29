"""benchmark_vs_player.py -- Benchmark a candidate agent against a downloaded
top player's real, recorded games (via benchmark.py's non-reactive `replay:`
agent mode), both seats, parallelized across CPU cores.

The opponent is non-reactive (it blindly replays their exact recorded
actions) but the market/prices/town state evolves live and correctly in
response to whatever our candidate actually does -- a much more meaningful
test than self-play against our own overlay-laden agents. See benchmark.py's
own module docstring for the caveats already documented there.

Usage:
    python3 benchmark_vs_player.py --candidate /tmp/candidate_final.py \
        --player-dir "top-players-data/Ryo Hasegawa" --seeds-per-episode 1
"""

import argparse
import multiprocessing as mp
import os

_worker_state = {}


def _worker_init(candidate_path):
    import benchmark
    _worker_state["benchmark"] = benchmark
    _worker_state["candidate"] = benchmark.load_agent(candidate_path)


def _play_one(task):
    episode_path, seat, seed, candidate_is_p0 = task
    benchmark = _worker_state["benchmark"]
    candidate = _worker_state["candidate"]
    opponent = benchmark.make_replay_agent(episode_path, seat)
    if candidate_is_p0:
        sa, sb = benchmark.run_game(candidate, opponent, seed)
    else:
        sb, sa = benchmark.run_game(opponent, candidate, seed)
    return sa, sb, os.path.basename(episode_path), candidate_is_p0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--player-dir", required=True)
    ap.add_argument("--seeds-per-episode", type=int, default=1)
    ap.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 4))
    args = ap.parse_args()

    import json
    with open(os.path.join(args.player_dir, "manifest.json")) as f:
        manifest = json.load(f)

    seeds = [7030039913, 1767950141, 2067004398, 4263648760, 3313394522]
    tasks = []
    for i, entry in enumerate(manifest):
        ep_path = os.path.join(args.player_dir, f"episode-{entry['episode_id']}-replay.json")
        if not os.path.exists(ep_path):
            continue
        for s in range(args.seeds_per_episode):
            seed = seeds[(i + s) % len(seeds)]
            tasks.append((ep_path, entry["seat"], seed, True))   # candidate as P0
            tasks.append((ep_path, entry["seat"], seed + 1, False))  # candidate as P1

    print(f"Running {len(tasks)} games (candidate={args.candidate} vs {args.player_dir}) "
          f"across {args.workers} workers...")

    with mp.Pool(processes=args.workers, initializer=_worker_init, initargs=(args.candidate,)) as pool:
        results = pool.map(_play_one, tasks)

    wins = losses = ties = 0
    deltas = []
    for sa, sb, ep, is_p0 in results:
        delta = sa - sb
        deltas.append(delta)
        if sa > sb: wins += 1
        elif sb > sa: losses += 1
        else: ties += 1

    n = len(results)
    mean_delta = sum(deltas) / n if n else 0.0
    print(f"\n{'='*62}")
    print(f"  vs {args.player_dir}  ({n} games)")
    print(f"  wins={wins}  losses={losses}  ties={ties}")
    print(f"  mean delta (candidate - opponent): {mean_delta:+,.0f}/game")
    print(f"{'='*62}")


if __name__ == "__main__":
    main()
