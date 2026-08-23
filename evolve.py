"""evolve.py -- v5 CMA-ES self-improvement loop for MapleLeaf 6.8.

Searches tuning_spec.SPEC's ~60 continuous knobs (main.py's own overlay
constants + every revived overlays.py mechanism's thresholds/gates + v4's
per-item front-run enable gates + v5's per-item opportunistic-sell reserve
fractions and shed-capacity overflow guard) to maximize a variance-
penalized, trend-aware fitness against a diverse opponent pool, WITH a
protected, heavily-weighted regression guard against the current baseline
(main.py) -- see FITNESS below.

Usage:
    python3 evolve.py                       # run indefinitely, checkpointing every generation
    python3 evolve.py --generations 50       # run a bounded number of generations (total, across restarts)
    python3 evolve.py --resume               # continue from evolve_checkpoint_v5.json
    python3 evolve.py --report               # print current best without running anything
    nohup python3 -u evolve.py > evolve_v5.log 2>&1 &   # for real long-running background use

Why v5 (postmortem of v4, see TUNING_NOTES.md): v4's own best-fitness
checkpoint, warm-started into v5's wider space and validated with a real
40-game benchmark, still LOST to the current baseline (-367/game) -- same
pattern as v3's false positive. Two independent parameter searches (v3, v4)
across a combined ~150+ generations have now failed to find anything that
survives real validation, a strong signal that pure retuning of the
EXISTING overlay mechanisms has hit a real ceiling. v5 adds two genuinely
NEW, safe (reorder/retime-only, no new sell VOLUME beyond what's already
owned) mechanisms mined from real public Kaggriculture notebooks instead of
just widening the same knobs further:
  1. Per-item opportunistic-sell reserve fractions (was one shared pair for
     all of MILK/WOOL/STRAWBERRY/MELON -- a real public notebook uses
     distinct per-item values ranging 0.40-0.68).
  2. A shed-capacity overflow guard: confirmed empirically that our OWN
     route drives shed occupancy to EXACTLY the engine's 100-item hard cap
     around steps 432-480, identically across every seed tested (a route-
     timing artifact, not opponent-dependent) -- a real, if narrow, source
     of silently lost production. Forces extra sells of already-owned
     surplus (cheapest items first) when projected occupancy would breach
     a tunable threshold below the cap.
Default vector for both reproduces the exact prior (v4) behavior -- new
per-item fractions default to the same values the old shared pair used,
and the guard defaults OFF.

Why v3 (postmortem of round 2, see TUNING_NOTES.md):

Round 1 (3-opponent pool: {main_6.5, legacy_6.3, 1 real replay}) found a
real +2,303/game winner over the then-current baseline, later promoted into
main.py. Round 2 widened the pool to 26 real+script opponents for diversity
robustness, but that DILUTED the one matchup that actually determines
promotion (beat the current baseline) down to ~1/26 (~4%) of the fitness
signal -- round 2's winner had a *higher* raw fitness number than round 1
ever reached, but LOST 2/20, -458/game to the actual baseline on real
validation. Widening the pool for robustness and protecting the regression
guard are two different needs; round 2 conflated them into one flat average
and lost the regression guard as a result.

v3's fix, concretely:
  1. The current baseline (main.py) is no longer just one more entry in the
     diverse pool -- it gets its own dedicated, larger seed set, sized so it
     always contributes BASELINE_FRACTION (default 25%) of the total game
     count regardless of how large the diverse pool grows.
  2. On top of that proportional weight, an explicit asymmetric penalty
     applies if the candidate's mean delta vs. the baseline is negative:
     REGRESSION_PENALTY_MULT * that (negative) mean is subtracted again from
     the blended fitness -- losing to the current baseline hurts strictly
     more than winning against it helps, by design.
  3. Per-game scoring is now a weighted TREND across three in-game
     checkpoints (~1/3, ~2/3, terminal of the 720-step episode: steps
     239/479/718, weights 0.15/0.25/0.60) rather than the single terminal
     delta -- a candidate that leads throughout the game scores better than
     one that's only ahead exactly at the final tally, at equal terminal
     score. This is free (reads already-simulated env.steps, no extra
     games), and is the concrete "steadier, long-term growth" refinement
     flagged as not-yet-done after round 1.
  4. Automatic IPOP-style restarts: if CMA-ES plateaus (the same
     stagnation check as v1/v2), it now doubles popsize and restarts from
     the best point found so far (instead of just stopping), up to
     --max-restarts times, so a single run doesn't get stuck in one basin.
     The global best across all restarts is always what gets checkpointed.

Opponent pool (diverse, non-baseline): legacy 6.3 script + 3 real replay
episodes from each of the 8 LEAST self-consistent (most adaptive) top-20
players, per the Phase A survey methodology in TUNING_NOTES.md -- this part
is unchanged from v2 and still a good idea; it just no longer competes with
the regression guard for signal.

Parallelization: same as v2 -- every (candidate, opponent-or-baseline, seed,
orientation) combination is flattened into one task list, parallelized at
the GAME level so all workers stay busy regardless of population size.

Convergence: if the best fitness hasn't improved by more than NOISE_FLOOR
over STAGNATION_WINDOW generations, the run either restarts (see #4 above)
or, once --max-restarts is exhausted, logs "converged" and stops.
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

CHECKPOINT_PATH_DEFAULT = "evolve_checkpoint_v5.json"
LAMBDA_VARIANCE = 0.35
STAGNATION_WINDOW = 20
NOISE_FLOOR = 100.0  # per-game $
SEEDS_PER_MATCHUP = 3  # v4: bumped from 2 -- v3's false-positive candidate (looked +104/game in-loop, actually -214/game on real validation) came from a signal that was too noisy at the smaller sample
BASELINE_FRACTION = 0.25  # target share of total games/candidate that are vs. the current baseline (main.py)
REGRESSION_PENALTY_MULT = 1.0  # extra fitness subtracted (on top of the proportional share) if baseline_mean_delta < 0
MIN_BASELINE_GAMES = 8

# Trend-checkpoint scoring: reads money at three points in the 720-step
# episode (env.steps already holds this post-run.run(), no extra sims).
_CHECKPOINT_STEPS = [239, 479, 718]
_CHECKPOINT_WEIGHTS = [0.15, 0.25, 0.60]

_SEEDS = [
    7030039913, 1767950141, 2067004398, 4263648760, 3313394522,
    3101419947, 3930751749, 5948990031, 3837117532, 2455163851,
]
_BASELINE_SEEDS = [
    4326338643, 7309474672, 2729251472, 5327694078, 6170128796,
    3294844113, 4866511089, 7895609197, 5194945606, 2535557871,
    8321094765, 1928374650, 6675432198, 3345678912, 9988776655,
    5566778899, 2233445566, 7788990011, 4455667788, 1122334455,
]


def _least_consistent_players(summary_path="routes_6_6/_summary.json", n=8):
    """Rank players by route_mining.py's self-consistency score (ascending --
    least consistent / most adaptive first) and return the bottom `n` names."""
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
    """Diverse pool -- NOT including the current baseline (main.py), which
    is scored separately (see module docstring). Legacy 6.3 script + real
    replays from the least self-consistent (most adaptive) top players."""
    specs = [
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


DIVERSE_OPPONENTS = _build_opponent_specs()
BASELINE_SPEC = {"kind": "path", "value": "main.py", "name": "main_baseline"}

_worker_state = {}


def _worker_init():
    import benchmark
    import build_agent
    _worker_state["benchmark"] = benchmark
    _worker_state["build_agent"] = build_agent

    def _load(spec):
        if spec["kind"] == "path":
            return benchmark.load_agent(spec["value"])
        episode_path, player_index = spec["value"]
        return benchmark.make_replay_agent(episode_path, player_index)

    _worker_state["diverse_opponents"] = [
        {"name": s["name"], "agent": _load(s)} for s in DIVERSE_OPPONENTS
    ]
    _worker_state["baseline_agent"] = _load(BASELINE_SPEC)
    _worker_state["agent_cache"] = {}  # candidate_key -> built agent, reused across tasks in this worker


def _get_candidate_agent(candidate_key, params_vector):
    cache = _worker_state["agent_cache"]
    if cache.get("key") != candidate_key:
        cache.clear()
        cache["key"] = candidate_key
        cache["agent"] = _worker_state["build_agent"].make_agent(params_vector)
    return cache["agent"]


def _run_game_trend(agent_a, agent_b, seed):
    """Play one real game; return a checkpoint-weighted trend delta (A - B)
    instead of just the terminal delta -- rewards a candidate that leads
    throughout the episode, not just at the final tally. Reads money
    directly from env.steps' recorded observations (reward is only
    populated by the engine at the terminal step)."""
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    env.run([agent_a, agent_b])
    steps = env.steps
    last_idx = len(steps) - 1

    def money_at(idx):
        idx = min(max(0, idx), last_idx)
        farms = steps[idx][0]["observation"]["farms"]
        return float(farms[0]["money"]), float(farms[1]["money"])

    trend = 0.0
    for cp, w in zip(_CHECKPOINT_STEPS, _CHECKPOINT_WEIGHTS):
        ma, mb = money_at(cp)
        trend += w * (ma - mb)
    return trend


def _play_game_task(task):
    """One game. task = (candidate_key, params_vector, pool, opp_idx_or_None, seed, candidate_is_p0)."""
    candidate_key, params_vector, pool, opp_idx, seed, candidate_is_p0 = task
    candidate = _get_candidate_agent(candidate_key, params_vector)
    if pool == "baseline":
        opponent = _worker_state["baseline_agent"]
    else:
        opponent = _worker_state["diverse_opponents"][opp_idx]["agent"]
    if candidate_is_p0:
        delta = _run_game_trend(candidate, opponent, seed)
    else:
        delta = -_run_game_trend(opponent, candidate, seed)
    return candidate_key, pool, delta


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
    print(f"Generation: {ckpt['generation']}  Restarts used: {ckpt.get('restarts_used', 0)}")
    print(f"Best fitness so far: {ckpt['best_fitness']:.1f}  "
          f"(mean_delta={ckpt['best_mean_delta']:.1f}, std_delta={ckpt['best_std_delta']:.1f}, "
          f"baseline_mean_delta={ckpt.get('best_baseline_mean_delta', float('nan')):.1f})")
    print(f"Converged: {ckpt.get('converged', False)}")
    print(f"Diverse opponent pool size: {len(ckpt.get('diverse_opponents', []))}")
    print(f"Best params (name=value):")
    for name, value in zip(tuning_spec.NAMES, ckpt["best_params"]):
        print(f"  {name:34s} {value}")
    hist = ckpt.get("fitness_history", [])
    if hist:
        recent = hist[-10:]
        print(f"\nLast {len(recent)} generation best-fitness values: {[round(v, 1) for v in recent]}")


def _n_baseline_games(n_diverse_games):
    target = round(n_diverse_games * BASELINE_FRACTION / (1.0 - BASELINE_FRACTION))
    target = max(MIN_BASELINE_GAMES, target)
    if target % 2 != 0:
        target += 1
    return target


def _run_generation(es, pool, n_diverse, n_baseline_per_cand, generation_offset):
    solutions_norm = es.ask()
    solutions_real = [_to_real(s) for s in solutions_norm]

    tasks = []
    for cand_idx, params_vector in enumerate(solutions_real):
        # Diverse pool: every opponent, SEEDS_PER_MATCHUP seeds, both orientations.
        for opp_idx in range(n_diverse):
            for s in range(SEEDS_PER_MATCHUP):
                seed_a = _SEEDS[(cand_idx * SEEDS_PER_MATCHUP + s) % len(_SEEDS)]
                seed_b = _SEEDS[(cand_idx * SEEDS_PER_MATCHUP + s + len(_SEEDS) // 2) % len(_SEEDS)]
                tasks.append((cand_idx, params_vector, "diverse", opp_idx, seed_a, True))
                tasks.append((cand_idx, params_vector, "diverse", opp_idx, seed_b, False))
        # Baseline (main.py): dedicated, weighted seed set -- half P0, half P1.
        half = n_baseline_per_cand // 2
        for s in range(half):
            seed_a = _BASELINE_SEEDS[(cand_idx * half + s) % len(_BASELINE_SEEDS)]
            seed_b = _BASELINE_SEEDS[(cand_idx * half + s + len(_BASELINE_SEEDS) // 2) % len(_BASELINE_SEEDS)]
            tasks.append((cand_idx, params_vector, "baseline", None, seed_a, True))
            tasks.append((cand_idx, params_vector, "baseline", None, seed_b, False))

    t0 = time.time()
    diverse_deltas = {i: [] for i in range(len(solutions_real))}
    baseline_deltas = {i: [] for i in range(len(solutions_real))}
    for cand_idx, task_pool, delta in pool.map(_play_game_task, tasks, chunksize=4):
        (diverse_deltas if task_pool == "diverse" else baseline_deltas)[cand_idx].append(delta)
    elapsed = time.time() - t0

    fitnesses, mean_deltas, std_deltas, baseline_means = [], [], [], []
    for i in range(len(solutions_real)):
        all_deltas = diverse_deltas[i] + baseline_deltas[i]
        m = statistics.mean(all_deltas)
        s = statistics.pstdev(all_deltas) if len(all_deltas) > 1 else 0.0
        b_mean = statistics.mean(baseline_deltas[i]) if baseline_deltas[i] else 0.0
        fitness = m - LAMBDA_VARIANCE * s
        if b_mean < 0:
            fitness += REGRESSION_PENALTY_MULT * b_mean  # b_mean negative -> subtracts extra
        fitnesses.append(fitness)
        mean_deltas.append(m)
        std_deltas.append(s)
        baseline_means.append(b_mean)

    es.tell(solutions_norm, [-f for f in fitnesses])  # cma minimizes

    return {
        "solutions_real": solutions_real,
        "fitnesses": fitnesses,
        "mean_deltas": mean_deltas,
        "std_deltas": std_deltas,
        "baseline_means": baseline_means,
        "n_games": len(tasks),
        "elapsed": elapsed,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generations", type=int, default=None, help="Stop after this many generations total, across restarts (default: run until converged + restarts exhausted)")
    ap.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 4))
    ap.add_argument("--checkpoint", default=CHECKPOINT_PATH_DEFAULT)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--popsize", type=int, default=None)
    ap.add_argument("--max-restarts", type=int, default=3, help="IPOP-style restarts (doubled popsize each time) once a run plateaus")
    args = ap.parse_args()

    if args.report:
        report(args.checkpoint)
        return

    import cma

    ckpt = load_checkpoint(args.checkpoint) if args.resume else None
    if ckpt is not None:
        x0_norm = _to_normalized(ckpt["best_params"])
        fitness_history = ckpt.get("fitness_history", [])
        best_fitness_history = ckpt.get("best_fitness_history") or list(fitness_history)
        generation = ckpt["generation"]
        best_fitness = ckpt["best_fitness"]
        best_params = ckpt["best_params"]
        best_mean_delta = ckpt["best_mean_delta"]
        best_std_delta = ckpt["best_std_delta"]
        best_baseline_mean_delta = ckpt.get("best_baseline_mean_delta", 0.0)
        sigma0 = ckpt.get("sigma0", 0.2)
        restarts_used = ckpt.get("restarts_used", 0)
        base_popsize = ckpt.get("base_popsize", args.popsize)
        print(f"Resuming from generation {generation}, best_fitness={best_fitness:.1f}, restarts_used={restarts_used}")
    else:
        x0_norm = _to_normalized(tuning_spec.default_vector())
        fitness_history = []
        best_fitness_history = []
        generation = 0
        best_fitness = float("-inf")
        best_params = tuning_spec.default_vector()
        best_mean_delta = best_std_delta = best_baseline_mean_delta = 0.0
        sigma0 = 0.2
        restarts_used = 0
        base_popsize = args.popsize

    n_diverse = len(DIVERSE_OPPONENTS)
    diverse_games_per_cand = n_diverse * SEEDS_PER_MATCHUP * 2
    n_baseline_per_cand = _n_baseline_games(diverse_games_per_cand)
    total_games_per_cand = diverse_games_per_cand + n_baseline_per_cand
    print(f"evolve.py v5: {tuning_spec.DIM} dims, workers={args.workers}, "
          f"diverse_opponents={n_diverse} ({[o['name'] for o in DIVERSE_OPPONENTS]}), "
          f"seeds/matchup={SEEDS_PER_MATCHUP}, diverse_games/candidate={diverse_games_per_cand}, "
          f"baseline_games/candidate={n_baseline_per_cand} (target {BASELINE_FRACTION:.0%} of signal), "
          f"total_games/candidate={total_games_per_cand}, max_restarts={args.max_restarts}")

    pool = mp.Pool(processes=args.workers, initializer=_worker_init)
    try:
        popsize = base_popsize
        while True:
            opts = {"bounds": [0.0, 1.0], "verbose": -9}
            if popsize:
                opts["popsize"] = popsize
            es = cma.CMAEvolutionStrategy(x0_norm, sigma0, opts)
            if not popsize:
                popsize = es.popsize  # remember the natural default so restarts can double it

            gen_this_leg = 0
            # Leg-local record of best_fitness, reset on every restart -- the
            # stagnation check below must only look back within the CURRENT
            # leg. Using the global best_fitness_history directly was a real
            # bug: right after a restart it's still full of pre-restart
            # entries at the same (stagnant) value, so even ONE post-restart
            # generation that doesn't beat the old record immediately
            # re-triggers "no improvement in STAGNATION_WINDOW generations"
            # -- observed burning through 2 of 3 restarts in a single
            # generation each before this fix.
            leg_best_history = []
            while not es.stop():
                if args.generations is not None and generation >= args.generations:
                    print(f"Reached --generations {args.generations}, stopping.")
                    save_checkpoint(args.checkpoint, {
                        "generation": generation, "best_fitness": best_fitness,
                        "best_mean_delta": best_mean_delta, "best_std_delta": best_std_delta,
                        "best_baseline_mean_delta": best_baseline_mean_delta,
                        "best_params": list(best_params), "fitness_history": fitness_history,
                        "best_fitness_history": best_fitness_history,
                        "sigma0": float(es.sigma), "converged": True, "restarts_used": restarts_used,
                        "base_popsize": base_popsize, "param_names": tuning_spec.NAMES,
                        "diverse_opponents": [o["name"] for o in DIVERSE_OPPONENTS],
                    })
                    return

                result = _run_generation(es, pool, n_diverse, n_baseline_per_cand, generation)
                generation += 1
                gen_this_leg += 1

                gen_best_idx = max(range(len(result["fitnesses"])), key=lambda i: result["fitnesses"][i])
                gen_best_fitness = result["fitnesses"][gen_best_idx]
                fitness_history.append(gen_best_fitness)

                if gen_best_fitness > best_fitness:
                    best_fitness = gen_best_fitness
                    best_params = result["solutions_real"][gen_best_idx]
                    best_mean_delta = result["mean_deltas"][gen_best_idx]
                    best_std_delta = result["std_deltas"][gen_best_idx]
                    best_baseline_mean_delta = result["baseline_means"][gen_best_idx]
                best_fitness_history.append(best_fitness)
                leg_best_history.append(best_fitness)

                print(f"[gen {generation}] popsize={len(result['solutions_real'])} games={result['n_games']} "
                      f"elapsed={result['elapsed']:.1f}s  gen_best={gen_best_fitness:.1f}  "
                      f"overall_best={best_fitness:.1f} (mean={best_mean_delta:.1f} std={best_std_delta:.1f} "
                      f"baseline_mean={best_baseline_mean_delta:.1f})")

                # Stagnation = the RUNNING RECORD hasn't improved by more than
                # NOISE_FLOOR over the window -- checking raw per-generation
                # gen_best spread instead (v3's original approach) never
                # fires in practice: per-generation noise from CMA-ES's own
                # stochastic sampling routinely exceeds NOISE_FLOOR even at a
                # genuine plateau, so a real 100-generation run with zero new
                # records never triggered a single IPOP restart. This
                # measures "has a new best been set recently", which is what
                # "plateaued" actually means. Uses leg_best_history (reset on
                # every restart), not the global best_fitness_history -- see
                # the comment where it's initialized.
                converged = False
                if len(leg_best_history) >= STAGNATION_WINDOW:
                    if best_fitness - leg_best_history[-STAGNATION_WINDOW] < NOISE_FLOOR:
                        converged = True

                save_checkpoint(args.checkpoint, {
                    "generation": generation, "best_fitness": best_fitness,
                    "best_mean_delta": best_mean_delta, "best_std_delta": best_std_delta,
                    "best_baseline_mean_delta": best_baseline_mean_delta,
                    "best_params": list(best_params), "fitness_history": fitness_history,
                    "best_fitness_history": best_fitness_history,
                    "sigma0": float(es.sigma), "converged": converged and restarts_used >= args.max_restarts,
                    "restarts_used": restarts_used, "base_popsize": base_popsize,
                    "param_names": tuning_spec.NAMES,
                    "diverse_opponents": [o["name"] for o in DIVERSE_OPPONENTS],
                })

                if converged:
                    break

            # This leg either converged or cma's own es.stop() fired.
            if restarts_used >= args.max_restarts or gen_this_leg == 0:
                print(f"Converged (restarts_used={restarts_used}/{args.max_restarts}). Stopping.")
                break

            restarts_used += 1
            popsize = int(round(popsize * 2))
            x0_norm = _to_normalized(best_params)
            sigma0 = 0.25
            print(f"--- Plateau hit: IPOP restart #{restarts_used}/{args.max_restarts}, "
                  f"popsize -> {popsize}, resuming from current best (fitness={best_fitness:.1f}) ---")
    finally:
        pool.close()
        pool.join()

    print(f"\nFinal best fitness: {best_fitness:.1f} (mean_delta={best_mean_delta:.1f}, "
          f"std_delta={best_std_delta:.1f}, baseline_mean_delta={best_baseline_mean_delta:.1f})")
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Materialize a candidate to benchmark with:")
    print(f"  python3 build_agent.py --from-checkpoint {args.checkpoint} --out /tmp/candidate.py")
    print(f"  python3 benchmark.py --a /tmp/candidate.py --b main.py --n 40")


if __name__ == "__main__":
    main()
