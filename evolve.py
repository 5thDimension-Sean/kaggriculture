"""evolve.py -- Long-running CMA-ES self-improvement loop for MapleLeaf 6.6.

Searches tuning_spec.SPEC's ~40 continuous knobs (main.py's own overlay
constants + every revived overlays.py mechanism's thresholds/gates) to
maximize a variance-penalized fitness against a diverse, fixed opponent
pool -- see FITNESS below for exactly what "long-term growth and steadier
growth" means here in concrete terms.

Usage:
    python3 evolve.py                       # run indefinitely, checkpointing every generation
    python3 evolve.py --generations 50       # run a bounded number of generations
    python3 evolve.py --resume               # continue from evolve_checkpoint.json
    python3 evolve.py --report               # print current best without running anything
    nohup python3 evolve.py > evolve.log 2>&1 &   # for real long-running background use

Fitness (per candidate params vector):
    For every (opponent, seed, seat) triple in the opponent pool, play a real
    game and record delta = candidate_score - opponent_score. Fitness =
    mean(deltas) - LAMBDA_VARIANCE * std(deltas). The variance term is the
    concrete "steadier growth" mechanism requested: a candidate that wins big
    sometimes and loses big other times scores worse than one that wins
    modestly but consistently, even at equal mean. Scoring on final money
    only (already how the game scores) is what makes this long-horizon
    rather than short-term-greedy -- there's no literal RL discount factor
    to set here since this isn't a step-by-step policy, but this is the
    CMA-ES equivalent of that intent.

Convergence: if the best fitness hasn't improved by more than NOISE_FLOOR
over STAGNATION_WINDOW generations, the run logs "converged" and stops
automatically -- this is a fixed-size parameter search (the route itself is
frozen), so it genuinely plateaus, and there's no point burning CPU past
that point. Real further gains require new mined routes / newly-revived
overlays (a new tuning_spec.SPEC), not more generations on this one.
"""

import argparse
import json
import multiprocessing as mp
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tuning_spec

CHECKPOINT_PATH_DEFAULT = "evolve_checkpoint.json"
LAMBDA_VARIANCE = 0.35
STAGNATION_WINDOW = 15
NOISE_FLOOR = 150.0  # per-game $ -- smaller than the environmental noise floor measured empirically (~150-3000/game)
SEEDS_PER_MATCHUP = 3

OPPONENTS = [
    {"kind": "path", "value": "main.py", "name": "main_6.5"},
    {"kind": "path", "value": "opponents/legacy_6_3.py", "name": "legacy_6.3"},
    {"kind": "replay", "value": ("top-players-data/ReCurSiON/episode-96975971-replay.json", 1), "name": "ReCurSiON_real"},
]

_SEEDS = [
    7030039913, 1767950141, 2067004398, 4263648760, 3313394522,
    3101419947, 3930751749, 5948990031, 3837117532, 2455163851,
]

_worker_state = {}


def _worker_init():
    import benchmark
    import build_agent
    _worker_state["benchmark"] = benchmark
    _worker_state["build_agent"] = build_agent
    opponents = []
    for spec in OPPONENTS:
        if spec["kind"] == "path":
            agent = benchmark.load_agent(spec["value"])
        else:
            episode_path, player_index = spec["value"]
            agent = benchmark.make_replay_agent(episode_path, player_index)
        opponents.append({"name": spec["name"], "agent": agent})
    _worker_state["opponents"] = opponents


def _evaluate(params_vector):
    """Runs in a worker process. Returns (fitness, mean_delta, std_delta, n_games)."""
    benchmark = _worker_state["benchmark"]
    build_agent = _worker_state["build_agent"]
    candidate = build_agent.make_agent(params_vector)

    deltas = []
    for opp in _worker_state["opponents"]:
        for i in range(SEEDS_PER_MATCHUP):
            seed_p0 = _SEEDS[i % len(_SEEDS)]
            seed_p1 = _SEEDS[(i + len(_SEEDS) // 2) % len(_SEEDS)]
            sa, sb = benchmark.run_game(candidate, opp["agent"], seed_p0)
            deltas.append(sa - sb)
            sb2, sa2 = benchmark.run_game(opp["agent"], candidate, seed_p1)
            deltas.append(sa2 - sb2)

    mean_delta = statistics.mean(deltas)
    std_delta = statistics.pstdev(deltas) if len(deltas) > 1 else 0.0
    fitness = mean_delta - LAMBDA_VARIANCE * std_delta
    return fitness, mean_delta, std_delta, len(deltas)


def _to_normalized(real_vector):
    return [(v - lo) / (hi - lo) for v, lo, hi in zip(real_vector, tuning_spec.LOWS, tuning_spec.HIGHS)]


def _to_real(norm_vector):
    return [lo + max(0.0, min(1.0, v)) * (hi - lo)
            for v, lo, hi in zip(norm_vector, tuning_spec.LOWS, tuning_spec.HIGHS)]


def load_checkpoint(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_checkpoint(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)


def report(path):
    ckpt = load_checkpoint(path)
    if ckpt is None:
        print(f"No checkpoint at {path} yet.")
        return
    print(f"Generation: {ckpt['generation']}")
    print(f"Best fitness so far: {ckpt['best_fitness']:.1f}  (mean_delta={ckpt['best_mean_delta']:.1f}, std_delta={ckpt['best_std_delta']:.1f})")
    print(f"Converged: {ckpt.get('converged', False)}")
    print(f"Best params (name=value):")
    for name, value in zip(tuning_spec.NAMES, ckpt["best_params"]):
        print(f"  {name:34s} {value}")
    hist = ckpt.get("fitness_history", [])
    if hist:
        recent = hist[-10:]
        print(f"\nLast {len(recent)} generation best-fitness values: {[round(v, 1) for v in recent]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generations", type=int, default=None, help="Stop after this many generations (default: run until convergence)")
    ap.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 4))
    ap.add_argument("--checkpoint", default=CHECKPOINT_PATH_DEFAULT)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--popsize", type=int, default=None)
    args = ap.parse_args()

    if args.report:
        report(args.checkpoint)
        return

    import cma

    ckpt = load_checkpoint(args.checkpoint) if args.resume else None
    if ckpt is not None:
        x0_norm = _to_normalized(ckpt["best_params"])
        fitness_history = ckpt.get("fitness_history", [])
        generation = ckpt["generation"]
        best_fitness = ckpt["best_fitness"]
        best_params = ckpt["best_params"]
        best_mean_delta = ckpt["best_mean_delta"]
        best_std_delta = ckpt["best_std_delta"]
        sigma0 = ckpt.get("sigma0", 0.2)
        print(f"Resuming from generation {generation}, best_fitness={best_fitness:.1f}")
    else:
        x0_norm = _to_normalized(tuning_spec.default_vector())
        fitness_history = []
        generation = 0
        best_fitness = float("-inf")
        best_params = tuning_spec.default_vector()
        best_mean_delta = best_std_delta = 0.0
        sigma0 = 0.2

    opts = {"bounds": [0.0, 1.0], "verbose": -9}
    if args.popsize:
        opts["popsize"] = args.popsize
    es = cma.CMAEvolutionStrategy(x0_norm, sigma0, opts)

    pool = mp.Pool(processes=args.workers, initializer=_worker_init)
    print(f"evolve.py: {tuning_spec.DIM} dims, popsize={es.popsize}, workers={args.workers}, "
          f"opponents={[o['name'] for o in OPPONENTS]}, seeds/matchup={SEEDS_PER_MATCHUP}")

    try:
        while not es.stop():
            if args.generations is not None and generation >= args.generations:
                print(f"Reached --generations {args.generations}, stopping.")
                break

            solutions_norm = es.ask()
            solutions_real = [_to_real(s) for s in solutions_norm]
            t0 = time.time()
            results = pool.map(_evaluate, solutions_real)
            elapsed = time.time() - t0

            fitnesses = [r[0] for r in results]
            es.tell(solutions_norm, [-f for f in fitnesses])  # cma minimizes

            gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
            gen_best_fitness = fitnesses[gen_best_idx]
            fitness_history.append(gen_best_fitness)
            generation += 1

            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_params = solutions_real[gen_best_idx]
                best_mean_delta = results[gen_best_idx][1]
                best_std_delta = results[gen_best_idx][2]

            n_games_total = sum(r[3] for r in results)
            print(f"[gen {generation}] pop={len(results)} games={n_games_total} "
                  f"elapsed={elapsed:.1f}s  gen_best={gen_best_fitness:.1f}  "
                  f"overall_best={best_fitness:.1f} (mean={best_mean_delta:.1f} std={best_std_delta:.1f})")

            converged = False
            if len(fitness_history) >= STAGNATION_WINDOW:
                window = fitness_history[-STAGNATION_WINDOW:]
                if max(window) - min(window) < NOISE_FLOOR and best_fitness - window[0] < NOISE_FLOOR:
                    converged = True

            save_checkpoint(args.checkpoint, {
                "generation": generation,
                "best_fitness": best_fitness,
                "best_mean_delta": best_mean_delta,
                "best_std_delta": best_std_delta,
                "best_params": list(best_params),
                "fitness_history": fitness_history,
                "sigma0": float(es.sigma),
                "converged": converged,
                "param_names": tuning_spec.NAMES,
            })

            if converged:
                print(f"Converged: no improvement > {NOISE_FLOOR} over last {STAGNATION_WINDOW} generations. Stopping.")
                break
    finally:
        pool.close()
        pool.join()

    print(f"\nFinal best fitness: {best_fitness:.1f} (mean_delta={best_mean_delta:.1f}, std_delta={best_std_delta:.1f})")
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Materialize a candidate to benchmark with:")
    print(f"  python3 build_agent.py --from-checkpoint {args.checkpoint} --out /tmp/candidate.py")
    print(f"  python3 benchmark.py --a /tmp/candidate.py --b main.py --n 40")


if __name__ == "__main__":
    main()
