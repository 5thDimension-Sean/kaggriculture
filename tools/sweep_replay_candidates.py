"""Rank candidate agents against a directory of recorded opponent replays."""

import argparse
import glob
import json
import multiprocessing as mp
import os


_WORKER = {"candidates": {}, "replays": {}}


def _worker_init():
    from tools import benchmark

    _WORKER["benchmark"] = benchmark


def _play(task):
    candidate_path, episode_path, opponent_seat, seed, candidate_is_p0 = task
    benchmark = _WORKER["benchmark"]
    candidate = _WORKER["candidates"].get(candidate_path)
    if candidate is None:
        candidate = benchmark.load_agent(candidate_path)
        _WORKER["candidates"][candidate_path] = candidate
    replay_key = (episode_path, opponent_seat)
    opponent = _WORKER["replays"].get(replay_key)
    if opponent is None:
        opponent = benchmark.make_replay_agent(episode_path, opponent_seat)
        _WORKER["replays"][replay_key] = opponent
    if candidate_is_p0:
        candidate_score, opponent_score = benchmark.run_game(candidate, opponent, seed)
    else:
        opponent_score, candidate_score = benchmark.run_game(opponent, candidate, seed)
    return candidate_path, candidate_score - opponent_score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, help="Glob for candidate Python files")
    parser.add_argument("--player-dir", required=True)
    parser.add_argument("--episode-id", type=int, help="Evaluate only one replay episode")
    parser.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 2))
    args = parser.parse_args()

    candidates = sorted(os.path.abspath(path) for path in glob.glob(args.candidates))
    if not candidates:
        raise SystemExit(f"no candidates matched {args.candidates!r}")
    with open(os.path.join(args.player_dir, "manifest.json"), encoding="utf-8") as handle:
        manifest = json.load(handle)
    if args.episode_id is not None:
        manifest = [entry for entry in manifest if int(entry["episode_id"]) == args.episode_id]

    tasks = []
    for candidate_path in candidates:
        for entry in manifest:
            episode_path = os.path.abspath(os.path.join(
                args.player_dir, f"episode-{entry['episode_id']}-replay.json"
            ))
            if not os.path.exists(episode_path):
                continue
            seed = int(entry["seed"])
            tasks.append((candidate_path, episode_path, int(entry["seat"]), seed, True))
            tasks.append((candidate_path, episode_path, int(entry["seat"]), seed, False))

    grouped = {path: [] for path in candidates}
    print(f"Running {len(tasks)} exact-seed games for {len(candidates)} candidates...")
    with mp.Pool(processes=args.workers, initializer=_worker_init) as pool:
        for candidate_path, delta in pool.imap_unordered(_play, tasks, chunksize=1):
            grouped[candidate_path].append(delta)

    rows = []
    for path, deltas in grouped.items():
        wins = sum(delta > 0 for delta in deltas)
        losses = sum(delta < 0 for delta in deltas)
        ties = len(deltas) - wins - losses
        mean_delta = sum(deltas) / len(deltas)
        rows.append((wins, mean_delta, -losses, path, ties))
    rows.sort(reverse=True)
    for wins, mean_delta, neg_losses, path, ties in rows:
        print(
            f"  wins={wins:2d}/{len(grouped[path]):2d} losses={-neg_losses:2d} "
            f"ties={ties:2d} mean_delta={mean_delta:+10,.0f}  {path}"
        )


if __name__ == "__main__":
    main()
