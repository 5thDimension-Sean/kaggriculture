"""Benchmark two frozen agents on identical seeds with both seat assignments."""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os


_AGENTS = {}


def _init(agent_a_path: str, agent_b_path: str) -> None:
    from tools import benchmark

    _AGENTS["run"] = benchmark.run_game
    _AGENTS["a"] = benchmark.load_agent(agent_a_path)
    _AGENTS["b"] = benchmark.load_agent(agent_b_path)


def _play(task: tuple[int, int]) -> tuple[int, int, float, float]:
    seed, a_seat = task
    if a_seat == 0:
        score_a, score_b = _AGENTS["run"](_AGENTS["a"], _AGENTS["b"], seed)
    else:
        score_b, score_a = _AGENTS["run"](_AGENTS["b"], _AGENTS["a"], seed)
    return seed, a_seat, score_a, score_b


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--seed-base", type=int, default=91_000_000)
    parser.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 2))
    args = parser.parse_args()

    path_a = os.path.abspath(args.a)
    path_b = os.path.abspath(args.b)
    tasks = [
        (args.seed_base + offset, seat)
        for offset in range(args.seeds)
        for seat in (0, 1)
    ]
    with mp.Pool(
        processes=args.workers,
        initializer=_init,
        initargs=(path_a, path_b),
    ) as pool:
        rows = list(pool.imap_unordered(_play, tasks, chunksize=1))

    rows.sort()
    deltas = [score_a - score_b for _, _, score_a, score_b in rows]
    print(f"A: {path_a}")
    print(f"B: {path_b}")
    print(
        f"overall: {sum(d > 0 for d in deltas)}-"
        f"{sum(d < 0 for d in deltas)}-{sum(d == 0 for d in deltas)}, "
        f"mean delta {sum(deltas) / len(deltas):+,.0f}"
    )
    for seat in (0, 1):
        selected = [score_a - score_b for _, a_seat, score_a, score_b in rows if a_seat == seat]
        print(
            f"A as seat {seat}: {sum(d > 0 for d in selected)}-"
            f"{sum(d < 0 for d in selected)}-{sum(d == 0 for d in selected)}, "
            f"mean delta {sum(selected) / len(selected):+,.0f}"
        )
    paired = []
    for offset in range(args.seeds):
        seed = args.seed_base + offset
        paired.append(sum(score_a - score_b for row_seed, _, score_a, score_b in rows if row_seed == seed))
    print(
        f"paired seeds: {sum(d > 0 for d in paired)}-"
        f"{sum(d < 0 for d in paired)}-{sum(d == 0 for d in paired)}"
    )


if __name__ == "__main__":
    main()
