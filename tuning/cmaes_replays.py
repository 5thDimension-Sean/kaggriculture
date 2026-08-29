"""Tune the compact 6.8 heuristic space against one recorded opponent route."""

import argparse
import json
import multiprocessing as mp
import os
import statistics
import time

from tuning import space


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WORKER = {}


def _worker_init(template_path, replay_path, opponent_seat, seed):
    from tools import benchmark

    _WORKER["benchmark"] = benchmark
    _WORKER["template"] = template_path
    _WORKER["opponent"] = benchmark.make_replay_agent(replay_path, opponent_seat)
    _WORKER["seed"] = seed
    _WORKER["candidates"] = {}


def _candidate(vector):
    key = tuple(round(float(value), 12) for value in vector)
    candidate = _WORKER["candidates"].get(key)
    if candidate is None:
        from tuning.build_candidate import make_agent

        candidate = make_agent(vector, template_path=_WORKER["template"])
        _WORKER["candidates"][key] = candidate
    return candidate


def _play(task):
    candidate_index, vector, candidate_is_p0 = task
    benchmark = _WORKER["benchmark"]
    candidate = _candidate(vector)
    opponent = _WORKER["opponent"]
    if candidate_is_p0:
        candidate_score, opponent_score = benchmark.run_game(
            candidate, opponent, _WORKER["seed"]
        )
    else:
        opponent_score, candidate_score = benchmark.run_game(
            opponent, candidate, _WORKER["seed"]
        )
    return candidate_index, candidate_score - opponent_score


def _evaluate(pool, vectors):
    tasks = [
        (candidate_index, vector, candidate_is_p0)
        for candidate_index, vector in enumerate(vectors)
        for candidate_is_p0 in (True, False)
    ]
    grouped = [[] for _ in vectors]
    for candidate_index, delta in pool.imap_unordered(_play, tasks, chunksize=1):
        grouped[candidate_index].append(delta)
    return [
        {
            "fitness": statistics.fmean(deltas) - 0.1 * (
                statistics.pstdev(deltas) if len(deltas) > 1 else 0.0
            ),
            "mean_delta": statistics.fmean(deltas),
            "worst_delta": min(deltas),
            "deltas": deltas,
        }
        for deltas in grouped
    ]


def _save(path, generation, params, score, args):
    payload = {
        "version": "mapleleaf-6.8-cma-replay-v1",
        "generation": generation,
        "seed": args.seed,
        "template": os.path.abspath(args.template),
        "replay": os.path.abspath(args.replay),
        "opponent_seat": args.opponent_seat,
        "game_seed": args.game_seed,
        "param_names": list(space.NAMES),
        "best_params": list(params),
        "best_score": score,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", required=True)
    parser.add_argument("--replay", required=True)
    parser.add_argument("--opponent-seat", type=int, choices=(0, 1), required=True)
    parser.add_argument("--game-seed", type=int, required=True)
    parser.add_argument("--generations", type=int, default=4)
    parser.add_argument("--popsize", type=int, default=12)
    parser.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 2))
    parser.add_argument("--seed", type=int, default=681491)
    parser.add_argument("--sigma", type=float, default=0.2)
    parser.add_argument(
        "--checkpoint",
        default=os.path.join(PROJECT_ROOT, "artifacts", "tuning", "crop-dusta.json"),
    )
    args = parser.parse_args()

    import cma

    strategy = cma.CMAEvolutionStrategy(
        space.to_normalized(space.default_vector()),
        args.sigma,
        {
            "bounds": [0.0, 1.0],
            "popsize": args.popsize,
            "seed": args.seed,
            "verb_disp": 0,
        },
    )
    best_params = space.default_vector()
    best_score = {"fitness": float("-inf")}
    context = mp.get_context("spawn")
    initargs = (
        os.path.abspath(args.template),
        os.path.abspath(args.replay),
        args.opponent_seat,
        args.game_seed,
    )
    with context.Pool(args.workers, initializer=_worker_init, initargs=initargs) as pool:
        for generation in range(args.generations):
            normalized = strategy.ask()
            vectors = [space.from_normalized(vector) for vector in normalized]
            scores = _evaluate(pool, vectors)
            strategy.tell(normalized, [-score["fitness"] for score in scores])
            winner = max(range(len(scores)), key=lambda index: scores[index]["fitness"])
            if scores[winner]["fitness"] > best_score["fitness"]:
                best_params = list(vectors[winner])
                best_score = dict(scores[winner])
            _save(args.checkpoint, generation, best_params, best_score, args)
            print(
                f"generation={generation:03d} "
                f"gen_mean={scores[winner]['mean_delta']:+.0f} "
                f"gen_worst={scores[winner]['worst_delta']:+.0f} "
                f"best_mean={best_score['mean_delta']:+.0f}"
            )

    print(f"checkpoint: {os.path.abspath(args.checkpoint)}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
