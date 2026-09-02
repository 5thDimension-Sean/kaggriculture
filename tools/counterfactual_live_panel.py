"""Replay a submission's actual opponents while replacing only that submission."""

from __future__ import annotations

import argparse
import glob
import json
import multiprocessing as mp
import os


def _play(task):
    candidate_path, replay_path, original_seat, seed = task
    from tools import benchmark

    candidate = benchmark.load_agent(candidate_path)
    opponent = benchmark.make_replay_agent(replay_path, 1 - original_seat)
    if original_seat == 0:
        candidate_score, opponent_score = benchmark.run_game(candidate, opponent, seed)
    else:
        opponent_score, candidate_score = benchmark.run_game(opponent, candidate, seed)
    return candidate_path, original_seat, candidate_score - opponent_score


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--player-dir", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 2))
    args = parser.parse_args()

    candidates = sorted(os.path.abspath(path) for path in glob.glob(args.candidates))
    with open(os.path.join(args.player_dir, "manifest.json"), encoding="utf-8") as handle:
        manifest = json.load(handle)
    # Skip validation self-play by content. Manifests are newest-first, so the
    # validation game is normally last rather than at a stable list index.
    rated_manifest = []
    for entry in manifest:
        replay_path = os.path.join(
            args.player_dir, f"episode-{entry['episode_id']}-replay.json"
        )
        with open(replay_path, encoding="utf-8") as replay_handle:
            replay = json.load(replay_handle)
        names = replay.get("info", {}).get("TeamNames", [])
        if len(names) >= 2 and names[0] == names[1]:
            continue
        rated_manifest.append(entry)
    manifest = rated_manifest
    if args.limit:
        manifest = manifest[: args.limit]
    tasks = []
    for candidate in candidates:
        for entry in manifest:
            replay = os.path.abspath(os.path.join(
                args.player_dir, f"episode-{entry['episode_id']}-replay.json"
            ))
            tasks.append((candidate, replay, int(entry["seat"]), int(entry["seed"])))

    grouped = {candidate: [] for candidate in candidates}
    with mp.Pool(processes=args.workers) as pool:
        for candidate, seat, delta in pool.imap_unordered(_play, tasks, chunksize=1):
            grouped[candidate].append((seat, delta))
    for candidate, rows in grouped.items():
        wins = sum(delta > 0 for _, delta in rows)
        losses = sum(delta < 0 for _, delta in rows)
        ties = len(rows) - wins - losses
        mean = sum(delta for _, delta in rows) / len(rows)
        print(f"{os.path.basename(candidate)}: {wins}-{losses}-{ties}, mean {mean:+,.0f}")
        for seat in (0, 1):
            deltas = [delta for row_seat, delta in rows if row_seat == seat]
            print(
                f"  seat {seat}: {sum(d > 0 for d in deltas)}-"
                f"{sum(d < 0 for d in deltas)}-{sum(d == 0 for d in deltas)}, "
                f"mean {sum(deltas) / len(deltas):+,.0f}"
            )


if __name__ == "__main__":
    main()
