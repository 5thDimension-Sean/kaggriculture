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
    nohup python3 -u evolve.py > evolve.log 2>&1 &   # for real long-running background use

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

Opponent pool (v2): one real replay game from EVERY currently-downloaded
top-20 player (top-players-data/*/manifest.json) plus the current main.py
and the revived legacy 6.3 script, for maximum diversity against overfitting
to a narrow test set -- a v1 run with only 3 opponents found a real +2,303/
game winner, but a broader pool makes it much harder for CMA-ES to find a
params vector that only exploits quirks of a small fixed test set.

Parallelization: v1 parallelized at the CANDIDATE level (one pool task per
population member), which wasted most of a 110-worker pool whenever
popsize < workers (only ever using popsize-many workers per generation).
v2 flattens every (candidate, opponent, seed, orientation) combination into
one big task list and parallelizes at the GAME level instead, so all
workers stay busy regardless of population size.

Convergence: if the best fitness hasn't improved by more than NOISE_FLOOR
over STAGNATION_WINDOW generations, the run logs "converged" and stops
automatically -- this is a fixed-size parameter search (the route itself is
frozen), so it genuinely plateaus, and there's no point burning CPU past
that point. Real further gains require new mined routes / newly-revived
overlays (a new tuning_spec.SPEC), not more generations on this one.
"""

import argparse
import glob
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
STAGNATION_WINDOW = 20
NOISE_FLOOR = 100.0  # per-game $ -- recalibrated down from v1's 150 now that more games/candidate shrinks real per-generation noise
SEEDS_PER_MATCHUP = 2

_SEEDS = [
    7030039913, 1767950141, 2067004398, 4263648760, 3313394522,
    3101419947, 3930751749, 5948990031, 3837117532, 2455163851,
]


def _least_consistent_players(summary_path="routes_6_6/_summary.json", n=8):
    """Rank players by route_mining.py's self-consistency score (ascending --
    least consistent / most adaptive first) and return the bottom `n` names.
    These are the players who *aren't* running a fixed script, so beating
    their real games is a meaningfully harder, more representative test than
    the highly-consistent ones (which are closer to clonable bots -- see
    ReCurSiON/Kobe BRYANT at 94-95% vs. Crop Dusta/Arman Tuganbaev/Subramanya
    N/Kaan Dınız at ~50%, per the Phase A survey)."""
    if not os.path.exists(summary_path):
        return []
    with open(summary_path) as f:
        data = json.load(f)
    rows = []
    for r in data:
        vals = [r.get(seat, {}).get("overall_consistency") for seat in ("p0", "p1")]
        vals = [v for v in vals if v is not None]
        if vals:
            rows.append((sum(vals) / len(vals), r["name"]))
    rows.sort()
    return [name for _avg, name in rows[:n]]


def _build_opponent_specs(player_data_dir="top-players-data", episodes_per_player=3, n_players=8):
    """Real replay opponents drawn from the LEAST consistent (most adaptive)
    top players only, plus the two script opponents. Multiple episodes per
    player so each hard opponent is represented by more than one sample of
    their (non-repeating) behavior, not just whichever the majority-vote
    self-consistency check saw first."""
    specs = [
        {"kind": "path", "value": "main.py", "name": "main_6.6"},
        {"kind": "path", "value": "opponents/legacy_6_3.py", "name": "legacy_6.3"},
    ]
    targets = _least_consistent_players(n=n_players)
    if not targets or not os.path.isdir(player_data_dir):
        return specs
    for player_dir in targets:
        full = os.path.join(player_data_dir, player_dir)
        manifest_path = os.path.join(full, "manifest.json")
        if not os.path.isdir(full) or not os.path.exists(manifest_path):
            continue
        with open(manifest_path) as f:
            manifest = json.load(f)
        for entry in manifest[:episodes_per_player]:
            ep_path = os.path.join(full, f"episode-{entry['episode_id']}-replay.json")
            if os.path.exists(ep_path):
                specs.append({
                    "kind": "replay",
                    "value": (ep_path, entry["seat"]),
                    "name": f"{player_dir}_{entry['episode_id']}",
                })
    return specs


OPPONENTS = _build_opponent_specs()

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
    _worker_state["agent_cache"] = {}  # candidate_key -> built agent, reused across tasks in this worker


def _get_candidate_agent(candidate_key, params_vector):
    cache = _worker_state["agent_cache"]
    if cache.get("key") != candidate_key:
        cache.clear()
        cache["key"] = candidate_key
        cache["agent"] = _worker_state["build_agent"].make_agent(params_vector)
    return cache["agent"]


def _play_game_task(task):
    """One game. task = (candidate_key, params_vector, opponent_idx, seed, candidate_is_p0)."""
    candidate_key, params_vector, opponent_idx, seed, candidate_is_p0 = task
    benchmark = _worker_state["benchmark"]
    candidate = _get_candidate_agent(candidate_key, params_vector)
    opponent = _worker_state["opponents"][opponent_idx]["agent"]
    if candidate_is_p0:
        sa, sb = benchmark.run_game(candidate, opponent, seed)
    else:
        sb, sa = benchmark.run_game(opponent, candidate, seed)
    return candidate_key, sa - sb


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
    print(f"Opponent pool size: {len(ckpt.get('opponents', []))}")
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
    n_opponents = len(OPPONENTS)
    games_per_candidate = n_opponents * SEEDS_PER_MATCHUP * 2
    print(f"evolve.py v2: {tuning_spec.DIM} dims, popsize={es.popsize}, workers={args.workers}, "
          f"opponents={n_opponents} ({[o['name'] for o in OPPONENTS]}), "
          f"seeds/matchup={SEEDS_PER_MATCHUP}, games/candidate={games_per_candidate}")

    try:
        while not es.stop():
            if args.generations is not None and generation >= args.generations:
                print(f"Reached --generations {args.generations}, stopping.")
                break

            solutions_norm = es.ask()
            solutions_real = [_to_real(s) for s in solutions_norm]

            # Flatten every (candidate, opponent, seed, orientation) combo into
            # one task list so all workers stay busy regardless of popsize.
            tasks = []
            for cand_idx, params_vector in enumerate(solutions_real):
                for opp_idx in range(n_opponents):
                    for s in range(SEEDS_PER_MATCHUP):
                        seed_a = _SEEDS[(cand_idx * SEEDS_PER_MATCHUP + s) % len(_SEEDS)]
                        seed_b = _SEEDS[(cand_idx * SEEDS_PER_MATCHUP + s + len(_SEEDS) // 2) % len(_SEEDS)]
                        tasks.append((cand_idx, params_vector, opp_idx, seed_a, True))
                        tasks.append((cand_idx, params_vector, opp_idx, seed_b, False))

            t0 = time.time()
            deltas_by_candidate = {i: [] for i in range(len(solutions_real))}
            for cand_idx, delta in pool.map(_play_game_task, tasks, chunksize=4):
                deltas_by_candidate[cand_idx].append(delta)
            elapsed = time.time() - t0

            fitnesses = []
            mean_deltas = []
            std_deltas = []
            for i in range(len(solutions_real)):
                d = deltas_by_candidate[i]
                m = statistics.mean(d)
                s = statistics.pstdev(d) if len(d) > 1 else 0.0
                fitnesses.append(m - LAMBDA_VARIANCE * s)
                mean_deltas.append(m)
                std_deltas.append(s)

            es.tell(solutions_norm, [-f for f in fitnesses])  # cma minimizes

            gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
            gen_best_fitness = fitnesses[gen_best_idx]
            fitness_history.append(gen_best_fitness)
            generation += 1

            if gen_best_fitness > best_fitness:
                best_fitness = gen_best_fitness
                best_params = solutions_real[gen_best_idx]
                best_mean_delta = mean_deltas[gen_best_idx]
                best_std_delta = std_deltas[gen_best_idx]

            print(f"[gen {generation}] pop={len(solutions_real)} games={len(tasks)} "
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
                "opponents": [o["name"] for o in OPPONENTS],
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
