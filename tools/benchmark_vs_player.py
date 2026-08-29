"""benchmark_vs_player.py -- Benchmark a candidate agent against a downloaded
top player's real, recorded games (via benchmark.py's non-reactive `replay:`
agent mode), both seats, parallelized across CPU cores.

The opponent is non-reactive (it blindly replays their exact recorded
actions) but the market/prices/town state evolves live and correctly in
response to whatever our candidate actually does -- a much more meaningful
test than self-play against our own overlay-laden agents. See benchmark.py's
own module docstring for the caveats already documented there.

Usage:
    python -m tools.benchmark_vs_player --candidate artifacts/candidate.py \
        --player-dir "top-players-data/Ryo Hasegawa" --seeds-per-episode 1
"""

import argparse
import multiprocessing as mp
import os

_worker_state = {}


def _worker_init(candidate_path):
    from tools import benchmark
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
    return sa, sb, os.path.basename(episode_path), candidate_is_p0, seed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--player-dir", required=True)
    ap.add_argument("--seeds-per-episode", type=int, default=1)
    ap.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 4))
    ap.add_argument("--minimum-wins", type=int, default=0,
                    help="Exit unsuccessfully unless the candidate reaches this many wins")
    args = ap.parse_args()

    candidate_path = os.path.abspath(args.candidate)
    if not os.path.isfile(candidate_path):
        ap.error(f"candidate file does not exist: {candidate_path}")
    manifest_path = os.path.join(args.player_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        ap.error(f"player manifest does not exist: {os.path.abspath(manifest_path)}")

    # Validate in the parent process. A failing Pool initializer is otherwise
    # repeatedly respawned by multiprocessing and can flood the machine.
    from tools import benchmark
    benchmark.load_agent(candidate_path)

    import json
    with open(manifest_path) as f:
        manifest = json.load(f)

    fallback_seeds = [7030039913, 1767950141, 2067004398, 4263648760, 3313394522]
    tasks = []
    for i, entry in enumerate(manifest):
        ep_path = os.path.join(args.player_dir, f"episode-{entry['episode_id']}-replay.json")
        if not os.path.exists(ep_path):
            continue
        for s in range(args.seeds_per_episode):
            # The first pair uses the episode's real competition seed. Extra
            # pairs retain deterministic synthetic seeds for robustness runs.
            seed = int(entry.get("seed", fallback_seeds[i % len(fallback_seeds)])) if s == 0 else fallback_seeds[(i + s) % len(fallback_seeds)]
            tasks.append((ep_path, entry["seat"], seed, True))   # candidate as P0
            tasks.append((ep_path, entry["seat"], seed, False))  # candidate as P1

    print(f"Running {len(tasks)} games (candidate={args.candidate} vs {args.player_dir}) "
          f"across {args.workers} workers...")

    with mp.Pool(processes=args.workers, initializer=_worker_init, initargs=(candidate_path,)) as pool:
        results = pool.map(_play_one, tasks)

    wins = losses = ties = 0
    deltas = []
    results.sort(key=lambda row: (row[2], not row[3]))
    for sa, sb, ep, is_p0, seed in results:
        delta = sa - sb
        deltas.append(delta)
        if sa > sb: wins += 1
        elif sb > sa: losses += 1
        else: ties += 1
        result = "WIN" if delta > 0 else "LOSS" if delta < 0 else "TIE"
        print(f"  {ep:34s} candidate=P{0 if is_p0 else 1} seed={seed:10d} "
              f"delta={delta:+9,.0f}  {result}")

    n = len(results)
    mean_delta = sum(deltas) / n if n else 0.0
    print(f"\n{'='*62}")
    print(f"  vs {args.player_dir}  ({n} games)")
    print(f"  wins={wins}  losses={losses}  ties={ties}")
    print(f"  mean delta (candidate - opponent): {mean_delta:+,.0f}/game")
    print(f"{'='*62}")

    if args.minimum_wins and wins < args.minimum_wins:
        raise SystemExit(
            f"minimum-win check failed: {wins} < {args.minimum_wins}"
        )


if __name__ == "__main__":
    main()
