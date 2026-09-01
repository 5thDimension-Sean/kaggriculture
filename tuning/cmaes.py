"""Compact CMA-ES tuner for the MapleLeaf 7.2 heuristic thresholds.

The optimizer searches sixteen interpretable values and evaluates every
candidate on common seeds in both seats. Fitness rewards mean score delta,
penalizes variance, and adds a small downside penalty for catastrophic games.
"""

import argparse
import json
import multiprocessing as mp
import os
import random
import statistics
import time

from tuning import space


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORKER = {}
_FRONT_RUN_NAMES = (
    "front_run_lead",
    "front_run_start",
    "front_run_stop",
    "front_run_max_batch",
)


def _worker_init(baseline_path, template_path=None):
    from tools import benchmark

    _WORKER["benchmark"] = benchmark
    _WORKER["baseline"] = benchmark.load_agent(baseline_path)
    _WORKER["candidates"] = {}
    _WORKER["template_path"] = template_path


def _candidate(vector):
    key = tuple(round(float(value), 12) for value in vector)
    cache = _WORKER["candidates"]
    if key not in cache:
        if len(cache) >= 32:
            cache.clear()
        from tuning.build_candidate import make_agent

        cache[key] = make_agent(vector, template_path=_WORKER.get("template_path"))
    return cache[key]


def _play(task):
    candidate_index, vector, seed, candidate_is_p0 = task
    benchmark = _WORKER["benchmark"]
    candidate = _candidate(vector)
    baseline = _WORKER["baseline"]
    if candidate_is_p0:
        candidate_score, baseline_score = benchmark.run_game(candidate, baseline, seed)
    else:
        baseline_score, candidate_score = benchmark.run_game(baseline, candidate, seed)
    return candidate_index, candidate_score - baseline_score


def _seed_batch(master_seed, generation, game_count):
    rng = random.Random(f"mapleleaf-7.2:{master_seed}:{generation}")
    return [rng.randrange(1_000_000_000, 9_999_999_999) for _ in range(game_count // 2)]


def _fitness(deltas):
    mean = statistics.fmean(deltas)
    deviation = statistics.pstdev(deltas) if len(deltas) > 1 else 0.0
    downside = max(0.0, -min(deltas))
    return mean - 0.25 * deviation - 0.05 * downside


def evaluate_population(pool, vectors, seeds):
    tasks = []
    for candidate_index, vector in enumerate(vectors):
        for seed in seeds:
            tasks.append((candidate_index, vector, seed, True))
            tasks.append((candidate_index, vector, seed, False))
    grouped = [[] for _ in vectors]
    for candidate_index, delta in pool.imap_unordered(_play, tasks, chunksize=1):
        grouped[candidate_index].append(delta)
    return [
        {
            "fitness": _fitness(deltas),
            "mean_delta": statistics.fmean(deltas),
            "std_delta": statistics.pstdev(deltas) if len(deltas) > 1 else 0.0,
            "worst_delta": min(deltas),
            "deltas": deltas,
        }
        for deltas in grouped
    ]


def _save_checkpoint(path, generation, best_params, best_score, seed, baseline, template=None):
    payload = {
        "version": "mapleleaf-7.2-cma-lite-v1",
        "generation": generation,
        "seed": seed,
        "baseline": baseline,
        "template": template,
        "param_names": list(space.NAMES),
        "best_params": list(best_params),
        "best_score": best_score,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generations", type=int, default=20)
    parser.add_argument("--games", type=int, default=6, help="games per candidate; must be even")
    parser.add_argument("--popsize", type=int, default=10)
    parser.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 2))
    parser.add_argument("--seed", type=int, default=68013)
    parser.add_argument("--sigma", type=float, default=0.16)
    parser.add_argument("--baseline", default=os.path.join(PROJECT_ROOT, "main.py"))
    parser.add_argument(
        "--template",
        default=None,
        help="Alternate route-backbone source for candidates (default: main.py itself)",
    )
    parser.add_argument(
        "--checkpoint",
        default=os.path.join(PROJECT_ROOT, "artifacts", "tuning", "cmaes-7.2.json"),
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--front-run-only",
        action="store_true",
        help="Keep the promoted route/overlay values fixed and search only the four market-lead controls",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.games < 2 or args.games % 2:
        parser.error("--games must be an even number of at least 2")
    if args.dry_run:
        print(json.dumps({"dimensions": space.DIM, "parameters": space.describe()}, indent=2))
        return

    import cma

    start_vector = space.default_vector()
    start_generation = 0
    best_params = list(start_vector)
    best_score = {
        "fitness": float("-inf"),
        "mean_delta": float("-inf"),
        "std_delta": float("inf"),
        "worst_delta": float("-inf"),
    }
    if args.resume and os.path.exists(args.checkpoint):
        with open(args.checkpoint, encoding="utf-8") as handle:
            checkpoint = json.load(handle)
        if tuple(checkpoint.get("param_names", ())) != space.NAMES:
            raise SystemExit("checkpoint does not match the compact 7.2 parameter space")
        start_vector = checkpoint["best_params"]
        best_params = list(start_vector)
        best_score = dict(checkpoint["best_score"])
        start_generation = int(checkpoint.get("generation", -1)) + 1

    full_start_normalized = space.to_normalized(start_vector)
    search_indices = (
        [space.NAMES.index(name) for name in _FRONT_RUN_NAMES]
        if args.front_run_only else list(range(space.DIM))
    )
    search_start = [full_start_normalized[index] for index in search_indices]
    strategy = cma.CMAEvolutionStrategy(
        search_start,
        args.sigma,
        {
            "bounds": [0.0, 1.0],
            "popsize": args.popsize,
            "seed": args.seed,
            "verb_disp": 0,
        },
    )
    baseline_path = os.path.abspath(args.baseline)
    template_path = os.path.abspath(args.template) if args.template else None
    context = mp.get_context("spawn")
    with context.Pool(args.workers, initializer=_worker_init, initargs=(baseline_path, template_path)) as pool:
        for generation in range(start_generation, start_generation + args.generations):
            normalized = strategy.ask()
            full_normalized = []
            for search_vector in normalized:
                vector = list(full_start_normalized)
                for index, value in zip(search_indices, search_vector):
                    vector[index] = value
                full_normalized.append(vector)
            vectors = [space.from_normalized(vector) for vector in full_normalized]
            seeds = _seed_batch(args.seed, generation, args.games)
            scores = evaluate_population(pool, vectors, seeds)
            strategy.tell(normalized, [-score["fitness"] for score in scores])
            winner = max(range(len(scores)), key=lambda index: scores[index]["fitness"])
            if scores[winner]["fitness"] > best_score["fitness"]:
                best_params = list(vectors[winner])
                best_score = dict(scores[winner])
            _save_checkpoint(
                args.checkpoint,
                generation,
                best_params,
                best_score,
                args.seed,
                baseline_path,
                template_path,
            )
            print(
                f"generation={generation:03d} "
                f"gen_fitness={scores[winner]['fitness']:+.1f} "
                f"gen_mean={scores[winner]['mean_delta']:+.1f} "
                f"best_fitness={best_score['fitness']:+.1f}"
            )
            if strategy.stop():
                print(f"CMA-ES stop conditions: {strategy.stop()}")
                break

    print(f"checkpoint: {os.path.abspath(args.checkpoint)}")
    print("materialize with: python -m tuning.build_candidate --checkpoint " + args.checkpoint)


if __name__ == "__main__":
    mp.freeze_support()
    main()
