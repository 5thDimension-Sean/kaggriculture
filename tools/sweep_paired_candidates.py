"""Rank candidate agents against one baseline on paired seeds and both seats."""

from __future__ import annotations

import argparse
import glob
import multiprocessing as mp
import os


_WORKER = {"candidates": {}}


def _init(baseline_path: str) -> None:
    from tools import benchmark
    _WORKER["benchmark"] = benchmark
    _WORKER["baseline"] = benchmark.load_agent(baseline_path)


def _play(task: tuple[str, int, int]) -> tuple[str, int, float]:
    candidate_path, seed, seat = task
    benchmark = _WORKER["benchmark"]
    candidate = _WORKER["candidates"].get(candidate_path)
    if candidate is None:
        candidate = benchmark.load_agent(candidate_path)
        _WORKER["candidates"][candidate_path] = candidate
    baseline = _WORKER["baseline"]
    if seat == 0:
        left, right = benchmark.run_game(candidate, baseline, seed)
    else:
        right, left = benchmark.run_game(baseline, candidate, seed)
    return candidate_path, seat, left - right


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--seed-base", type=int, default=99_000_000)
    parser.add_argument(
        "--seat",
        type=int,
        choices=(0, 1),
        default=None,
        help="Only benchmark the candidate in this seat.",
    )
    parser.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 2))
    args = parser.parse_args()
    candidates = sorted(os.path.abspath(path) for path in glob.glob(args.candidates))
    seats = (args.seat,) if args.seat is not None else (0, 1)
    tasks = [
        (path, args.seed_base + offset, seat)
        for path in candidates
        for offset in range(args.seeds)
        for seat in seats
    ]
    grouped = {path: [] for path in candidates}
    with mp.Pool(
        processes=args.workers,
        initializer=_init,
        initargs=(os.path.abspath(args.baseline),),
    ) as pool:
        for path, seat, delta in pool.imap_unordered(_play, tasks, chunksize=1):
            grouped[path].append((seat, delta))
    rows = []
    for path, values in grouped.items():
        deltas = [delta for _, delta in values]
        seat0 = [delta for seat, delta in values if seat == 0]
        seat1 = [delta for seat, delta in values if seat == 1]
        rows.append((sum(x > 0 for x in deltas), sum(deltas), path, deltas, seat0, seat1))
    rows.sort(reverse=True)
    for wins, total, path, deltas, seat0, seat1 in rows:
        seat_parts = []
        if seat0:
            seat_parts.append(f"p0={sum(x > 0 for x in seat0)}/{len(seat0)}")
        if seat1:
            seat_parts.append(f"p1={sum(x > 0 for x in seat1)}/{len(seat1)}")
        print(
            f"wins={wins:2d}/{len(deltas):2d} mean={total / len(deltas):+9,.0f} "
            f"{' '.join(seat_parts)} {path}"
        )


if __name__ == "__main__":
    main()
