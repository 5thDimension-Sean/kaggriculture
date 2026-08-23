"""evolve.py -- v6 CMA-ES self-improvement loop for MapleLeaf.

v5 and earlier evaluated every CMA-ES candidate once per generation against
seeds partly keyed off the candidate's own index, then fed that single noisy
score straight into `es.tell()` AND used it directly to decide the checkpoint's
"best" candidate. Two consequences, both confirmed empirically this session:
candidate-to-candidate comparisons were partly comparing different random
games rather than different policies, and a candidate could become "the
best ever seen" purely from a lucky seed draw with no independent check.
v5's own best checkpoint, warm-started and validated with a real 40-game
benchmark, LOST to the baseline (-367/game) despite looking good in-loop --
the same false-positive pattern v3 hit first.

v6 restructures the evaluator around five ideas, in priority order (fair
evaluation first, mathematical smoothing last):

  1. COMMON RANDOM NUMBERS: every candidate in a generation (and every
     survivor within a stage) sees the exact same seed batch. The candidate
     index never appears in any seed computation. This isolates
     candidate-vs-candidate score differences to the policy itself.
  2. ROTATING DETERMINISTIC SEED BATCHES: a large seed pool (built once from
     a fixed `SEED_SELECTION_SEED`, extending the original hand-picked
     `_SEEDS`/`_BASELINE_SEEDS`), sliced into batches that rotate every
     `--seed-batch-generations` generations -- candidates never get to
     overfit one fixed tiny seed set indefinitely.
  3. SUCCESSIVE-HALVING / RACING within each generation: Stage A screens
     every candidate cheaply (small opponent subset, common seeds), keeps
     the top `--survivor-fraction`; Stage B re-evaluates survivors on a
     larger opponent subset with fresh seeds, keeps `--finalists`; Stage C
     evaluates finalists against the full diverse pool AND the protected
     baseline matchup (only finalists pay the baseline-check cost -- cheap
     screening no longer wastes 25% of every candidate's budget on a check
     it doesn't need yet). Survivors carry their earlier stages' games
     forward rather than re-measuring from scratch.
  4. THREE EVALUATION TIERS, kept explicitly separate: Level A (the racing
     pipeline above) drives CMA-ES's own `tell()`. Level B (verification)
     re-checks a new generation-best on FRESH seeds disjoint from every
     Level-A pool, deciding whether it becomes `best_verified` -- a noisy
     Level-A score alone can never silently become the checkpoint's
     production-candidate. Level C (`--promote`) is the existing rigorous
     head-to-head vs. main.py on a large fresh seed set, now with full
     mean/median/std/win-rate/worst/best/trend/terminal reporting.
  5. Everything v3/v4/v5 already got right is kept: dedicated
     baseline weighting with an asymmetric regression penalty (now with an
     explicit `--baseline-tolerance` beyond which the penalty steepens),
     trend-checkpoint scoring (239/479/718, weights 0.15/0.25/0.60 -- still
     logged alongside the plain terminal delta so the proxy's own
     usefulness stays checkable), game-level multiprocessing, the
     fast-deepcopy worker patch, and leg-local-reset IPOP restarts (now
     with a sigma schedule and varying restart locations instead of always
     resuming at the exact same sigma/point).

v7 fixes a structural blind spot found by reading v6's own 23-generation
checkpoint (evolve_checkpoint_v6.json): `best_verified_params` was still
null and every single logged `baseline_mean` was negative (-624 to -1934),
i.e. no candidate ever came close to beating main.py, despite
`best_optimization_fitness` climbing to 6291. The cause: `es.tell()` was
fed `diverse_fitness` -- by construction the score against the diverse
historical-bot pool ONLY, with zero baseline component -- because only
FINALISTS (post successive-halving) ever played baseline games, making a
population-wide baseline-inclusive score heterogeneous. Consequence: CMA-ES
itself had literally no selection pressure toward beating main.py for 23
generations; it only ever got better at beating weak historical bots, and
`baseline_mean` wandered as an unselected byproduct. This is exactly
module-docstring section 11/13's "is the optimizer optimizing the proxy
instead of the real objective" failure mode, empirically confirmed rather
than hypothetical.

  6. EVERY population member (not just finalists) now plays a small
     common-random-number baseline probe during Stage A
     (`--screening-baseline-seeds`, default 2 games) that IS folded into
     the score `es.tell()` receives. `fitness` (diverse_fitness plus a
     `--baseline-weight`-scaled, variance- and tolerance-aware baseline
     term -- see `_score_accumulated`) replaces `diverse_fitness` as the
     tell() signal. This costs ~2x popsize extra games/generation (a few
     percent of the existing ~1000/generation budget) in exchange for the
     search actually being pointed at the thing --promote ultimately
     gates on. Finalists still additionally get the larger, more precise
     baseline batch from Stage C for verification-quality reporting.

Usage (unchanged surface):
    python3 evolve.py                       # run indefinitely, checkpointing every generation
    python3 evolve.py --generations 50       # bounded run (counts across restarts)
    python3 evolve.py --resume               # continue from evolve_checkpoint_v6.json
    python3 evolve.py --report               # print current best without running anything
    python3 evolve.py --dry-run              # print the derived config/game-budget, run nothing
    python3 evolve.py --promote CAND.py      # Level C: rigorous benchmark of CAND.py vs. main.py
    nohup python3 -u evolve.py > evolve_v6.log 2>&1 &

New optional controls (all have defaults; routine experimentation shouldn't
need source edits -- see main()'s argparse block for the full list):
    --screening-opponents, --screening-seeds, --survivor-fraction,
    --finalists, --verification-seeds, --seed-batch-generations,
    --baseline-tolerance, --staged-params, --sensitivity-every,
    --screening-baseline-seeds, --baseline-weight (v7)

Opponent pool, worker architecture, and the fast-deepcopy patch are
unchanged from v5 -- see their own docstrings/comments below.
"""

import argparse
import json
import math
import multiprocessing as mp
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tuning_spec

CHECKPOINT_PATH_DEFAULT = tuning_spec.CHECKPOINT_PATH_DEFAULT

# -- Fitness shaping (unchanged intent from v3-v5; see module docstring #5) --
LAMBDA_VARIANCE = 0.35
STAGNATION_WINDOW = 20
NOISE_FLOOR = 100.0  # per-game $
BASELINE_FRACTION = 0.25          # target share of a FINALIST's total games that are vs. the baseline
BASELINE_TOLERANCE_DEFAULT = 150.0    # $/game -- beyond this much regression, an additional steeper penalty applies
EXTRA_REGRESSION_PENALTY_MULT = 2.0   # slope of that additional penalty, applied to the excess beyond tolerance
MIN_BASELINE_GAMES = 8
BASELINE_WEIGHT_DEFAULT = 8.0     # v7: multiplier on the baseline component of `fitness` (the value es.tell()
                                  # now receives, see module docstring #6) -- needs to be large because raw
                                  # diverse-pool deltas run 10-30x bigger than baseline deltas (weak historical
                                  # bots get blown out for $10-20k/game; main.py loses/wins by $100s-$1000s), so
                                  # without an explicit multiplier a baseline-losing candidate's diverse blowout
                                  # trivially swamps the baseline penalty and CMA-ES never feels it.
SCREENING_BASELINE_SEEDS_DEFAULT = 2   # per-candidate common-random-number baseline games added to Stage A

# Trend-checkpoint scoring: reads money at three points in the 720-step
# episode (env.steps already holds this post-env.run(), no extra sims).
_CHECKPOINT_STEPS = [239, 479, 718]
_CHECKPOINT_WEIGHTS = [0.15, 0.25, 0.60]

# -- Racing / successive-halving defaults (module docstring #3) --
SCREENING_OPPONENT_COUNT_DEFAULT = 6
SCREENING_SEEDS_DEFAULT = 1
STAGE_B_OPPONENT_MULT = 2          # Stage B opponent count = min(n_diverse, SCREENING_OPPONENT_COUNT * this)
STAGE_B_SEEDS_DEFAULT = 2
SURVIVOR_FRACTION_DEFAULT = 0.3
FINALIST_COUNT_DEFAULT = 6
STAGE_C_SEEDS_DEFAULT = 2          # additional (fresh) seeds per diverse opponent at Stage C, on top of A+B

# -- Verification (Level B) defaults (module docstring #4) --
VERIFICATION_SEEDS_DEFAULT = 12    # per diverse opponent, on FRESH (disjoint) seeds
VERIFICATION_BASELINE_GAMES_DEFAULT = 24

# -- Seed pools (module docstring #1-2) --
SEED_SELECTION_SEED = 1337031      # arbitrary but FIXED -- every pool below is 100% reproducible from this
SEED_BATCH_GENERATIONS_DEFAULT = 4
_POOL_SIZE_OPTIMIZATION = 600
_POOL_SIZE_OPTIMIZATION_BASELINE = 400
_POOL_SIZE_VERIFICATION = 300
_POOL_SIZE_VERIFICATION_BASELINE = 200
_POOL_SIZE_PROMOTION = 200

# -- IPOP restart defaults (module docstring #5, "kept") --
RESTART_SIGMAS = [0.30, 0.45, 0.60]  # in the normalized [0,1] search cube; last value repeats if more restarts occur


def _build_seed_pool(n, tag, seed_selection_seed=SEED_SELECTION_SEED, seed_low=10**9, seed_high=10**10):
    """A deterministic, reproducible list of n distinct pseudo-random integers
    in [seed_low, seed_high) -- these are ENGINE seeds (arbitrary-looking
    integers fed to the game's own RNG), not claims of any special
    statistical validation; generating them from a fixed `random.Random`
    seed is exactly as legitimate as the original hand-picked `_SEEDS` list
    was, just reproducible and easy to extend. `tag` makes different pools
    (optimization/verification/promotion/baseline) derive from independent
    streams so they are guaranteed disjoint by construction (collision
    probability across ~9e9 possible values is astronomically small, but
    the loop below also explicitly de-dupes)."""
    rng = random.Random(f"{seed_selection_seed}:{tag}")
    seen = set()
    out = []
    while len(out) < n:
        s = rng.randrange(seed_low, seed_high)
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


# The original hand-picked seeds (used successfully in v1-v5) lead each pool,
# followed by a much larger deterministically-generated extension -- "prefer
# adding a substantially larger pool" while still reusing what's known-good.
_LEGACY_SEEDS = [
    7030039913, 1767950141, 2067004398, 4263648760, 3313394522,
    3101419947, 3930751749, 5948990031, 3837117532, 2455163851,
]
_LEGACY_BASELINE_SEEDS = [
    4326338643, 7309474672, 2729251472, 5327694078, 6170128796,
    3294844113, 4866511089, 7895609197, 5194945606, 2535557871,
    8321094765, 1928374650, 6675432198, 3345678912, 9988776655,
    5566778899, 2233445566, 7788990011, 4455667788, 1122334455,
]

_OPTIMIZATION_SEED_POOL = _LEGACY_SEEDS + _build_seed_pool(
    _POOL_SIZE_OPTIMIZATION - len(_LEGACY_SEEDS), "optimization")
_OPTIMIZATION_BASELINE_SEED_POOL = _LEGACY_BASELINE_SEEDS + _build_seed_pool(
    _POOL_SIZE_OPTIMIZATION_BASELINE - len(_LEGACY_BASELINE_SEEDS), "optimization-baseline")
# Verification/promotion pools are entirely fresh (independent `tag`), never
# overlapping the optimization pools above -- see module docstring #4 and
# "Level B ... FRESH seeds disjoint from every Level-A pool".
_VERIFICATION_SEED_POOL = _build_seed_pool(_POOL_SIZE_VERIFICATION, "verification")
_VERIFICATION_BASELINE_SEED_POOL = _build_seed_pool(_POOL_SIZE_VERIFICATION_BASELINE, "verification-baseline")
_PROMOTION_SEED_POOL = _build_seed_pool(_POOL_SIZE_PROMOTION, "promotion")

# Stage A/B/C each get their own disjoint-by-construction third of the
# optimization pool (round-robin interleaved, so the known-good _LEGACY_SEEDS
# are spread across all three rather than concentrated in Stage A). This
# replaces an earlier draw-from-the-shared-pool-then-filter-out-overlap
# scheme: filtering after the fact can't GUARANTEE freshness -- if every
# freshly-drawn seed happened to already be in an earlier stage's batch, the
# filter emptied the list and fell back to the original (non-fresh) draw,
# silently contradicting the "fresh seeds" comments/docs. Partitioning the
# pool up front makes Stage B and Stage C structurally unable to ever draw a
# seed Stage A (or, for C, Stage B) already used.
_STAGE_A_SEED_POOL = _OPTIMIZATION_SEED_POOL[0::3]
_STAGE_B_SEED_POOL = _OPTIMIZATION_SEED_POOL[1::3]
_STAGE_C_SEED_POOL = _OPTIMIZATION_SEED_POOL[2::3]

# v7: the optimization-baseline pool is split the same disjoint-by-construction
# way -- one half for the NEW all-population Stage A baseline probe (module
# docstring #6), the other for the existing finalists-only baseline batch --
# so the two can never draw the same seed in the same generation.
_STAGE_A_BASELINE_SEED_POOL = _OPTIMIZATION_BASELINE_SEED_POOL[0::2]
_FINALIST_BASELINE_SEED_POOL = _OPTIMIZATION_BASELINE_SEED_POOL[1::2]


def get_generation_seed_batch(generation, batch_size, pool, batch_generations):
    """Deterministic + reproducible: the same (generation, batch_size, pool,
    batch_generations) always returns the same batch. Generations
    [0, batch_generations) share cycle 0's batch, the next batch_generations
    share cycle 1's, etc. (module docstring #2) -- wraps around the pool if
    a run goes on long enough to exhaust it."""
    cycle_index = generation // batch_generations
    n = len(pool)
    start = (cycle_index * batch_size) % n
    if start + batch_size <= n:
        return pool[start:start + batch_size]
    return pool[start:] + pool[:(start + batch_size) - n]


# ===========================================================================
# Opponent pool -- UNCHANGED from v5 (see TUNING_NOTES.md's methodology
# section: legacy 6.3 script + 3 real replay episodes each from the 8 LEAST
# self-consistent / most-adaptive top-20 players).
# ===========================================================================

def _least_consistent_players(summary_path="routes_6_6/_summary.json", n=8):
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


def _fast_deepcopy(obj):
    """Drop-in replacement for copy.deepcopy, applied ONLY inside evolve.py's
    worker processes (never touches the actual submitted agent) -- profiling
    a real game found 56% of wall-clock time inside the kaggle_environments
    engine's OWN internal copy.deepcopy calls. Verified byte-identical game
    outcomes across 8 real games with vs. without this patch; 1.51x faster.
    See TUNING_NOTES.md for the full writeup."""
    t = type(obj)
    if t is dict:
        return {k: _fast_deepcopy(v) for k, v in obj.items()}
    if t is list:
        return [_fast_deepcopy(v) for v in obj]
    if t is tuple:
        return tuple(_fast_deepcopy(v) for v in obj)
    from kaggle_environments.utils import Struct
    if t is Struct:
        return Struct(**{k: _fast_deepcopy(v) for k, v in obj.items()})
    return obj


def _worker_init():
    import copy
    copy.deepcopy = _fast_deepcopy
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
    _worker_state["agent_cache"] = {}


def _get_candidate_agent(candidate_key, params_vector):
    cache = _worker_state["agent_cache"]
    if cache.get("key") != candidate_key:
        cache.clear()
        cache["key"] = candidate_key
        cache["agent"] = _worker_state["build_agent"].make_agent(params_vector)
    return cache["agent"]


def _run_game_scores(agent_a, agent_b, seed):
    """Play one real game; return (trend, terminal) -- the checkpoint-
    weighted trend delta AND the plain terminal delta, logged separately
    (module docstring #5 / spec section 12: "do not silently replace
    terminal performance with trend performance") even though `trend` is
    still what drives fitness. Reads money directly from env.steps'
    recorded observations (reward is only populated by the engine at the
    terminal step)."""
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
    ta, tb = money_at(last_idx)
    terminal = ta - tb
    return trend, terminal


def _play_game_task(task):
    """One game. task = (candidate_key, params_vector, pool, opp_name_or_None, opp_idx_or_None, seed, candidate_is_p0)."""
    candidate_key, params_vector, pool, opp_name, opp_idx, seed, candidate_is_p0 = task
    candidate = _get_candidate_agent(candidate_key, params_vector)
    if pool == "baseline":
        opponent = _worker_state["baseline_agent"]
    else:
        opponent = _worker_state["diverse_opponents"][opp_idx]["agent"]
    if candidate_is_p0:
        trend, terminal = _run_game_scores(candidate, opponent, seed)
    else:
        trend_r, terminal_r = _run_game_scores(opponent, candidate, seed)
        trend, terminal = -trend_r, -terminal_r
    return candidate_key, pool, opp_name, trend, terminal


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
    opt_fitness = ckpt.get("best_optimization_fitness", ckpt.get("best_fitness", float("-inf")))
    opt_mean = ckpt.get("best_optimization_mean_delta", ckpt.get("best_mean_delta", 0.0))
    opt_std = ckpt.get("best_optimization_std_delta", ckpt.get("best_std_delta", 0.0))
    opt_baseline = ckpt.get("best_optimization_baseline_mean_delta", ckpt.get("best_baseline_mean_delta", 0.0))
    print(f"Best OPTIMIZATION fitness: {opt_fitness:.1f} "
          f"(mean={opt_mean:.1f}, std={opt_std:.1f}, baseline_mean={opt_baseline:.1f})")
    if ckpt.get("best_verified_fitness") is not None:
        print(f"Best VERIFIED fitness:    {ckpt['best_verified_fitness']:.1f} "
              f"(mean={ckpt.get('best_verified_mean_delta', 0.0):.1f}, "
              f"std={ckpt.get('best_verified_std_delta', 0.0):.1f}, "
              f"baseline_mean={ckpt.get('best_verified_baseline_mean_delta', 0.0):.1f}, "
              f"baseline_win_rate={ckpt.get('best_verified_baseline_win_rate', float('nan')):.2f})")
        gap = opt_fitness - ckpt["best_verified_fitness"]
        flag = " POSSIBLE_OVERFIT" if gap > 0.5 * max(1.0, abs(opt_fitness)) else ""
        print(f"  optimization - verification gap: {gap:.1f}{flag}")
    else:
        print("Best VERIFIED fitness:    none yet (no candidate has passed Level-B verification)")
    print(f"Converged: {ckpt.get('converged', False)}")
    print(f"Diverse opponent pool size: {len(ckpt.get('diverse_opponents', []))}")
    opp_stats = ckpt.get("opponent_stats", {})
    if opp_stats:
        print("Opponent informativeness (mean_delta / games / win_rate):")
        for name, s in sorted(opp_stats.items(), key=lambda kv: -kv[1].get("informativeness", 0.0))[:10]:
            print(f"  {name:28s} mean={s.get('mean_delta', 0.0):>9.1f}  games={s.get('games', 0):4d}  "
                  f"win_rate={s.get('win_rate', 0.0):.2f}  informativeness={s.get('informativeness', 0.0):.1f}")
    best_params = ckpt.get("best_verified_params") or ckpt["best_params"]
    param_names = ckpt.get("param_names", tuning_spec.NAMES)
    if param_names != tuning_spec.NAMES:
        best_params, _ = tuning_spec.remap_checkpoint_vector(param_names, best_params)
    print("Best params (name=value):")
    for name, value in zip(tuning_spec.NAMES, best_params):
        print(f"  {name:34s} {value}")
    hist = ckpt.get("fitness_history", [])
    if hist:
        recent = hist[-10:]
        print(f"\nLast {len(recent)} generation best-fitness values: {[round(v, 1) for v in recent]}")


# ===========================================================================
# Opponent statistics -- section 18/19: track how informative each diverse
# opponent has been (does it actually separate good candidates from
# mediocre ones?) and use that, with a floor so no opponent starves, to
# bias which opponents get sampled into the cheap Stage A/B subsets.
# ===========================================================================

def _update_opponent_stats(stats, name, deltas):
    """`deltas` = list of trend deltas one or more candidates recorded
    against this opponent THIS generation. Updates a simple running
    (count, mean, M2-for-variance, wins) accumulator plus this generation's
    own spread (a proxy for "does this opponent discriminate candidates?",
    since across-candidate spread is what Stage A actually needs, distinct
    from the opponent's own game-to-game noise)."""
    s = stats.setdefault(name, {"games": 0, "mean_delta": 0.0, "_m2": 0.0, "wins": 0, "informativeness": 0.0})
    for d in deltas:
        s["games"] += 1
        delta_from_mean = d - s["mean_delta"]
        s["mean_delta"] += delta_from_mean / s["games"]
        s["_m2"] += delta_from_mean * (d - s["mean_delta"])
        if d > 0:
            s["wins"] += 1
    s["win_rate"] = s["wins"] / s["games"] if s["games"] else 0.0
    if len(deltas) >= 2:
        s["informativeness"] = statistics.pstdev(deltas)


def _opponent_sampling_weights(stats, names, min_floor=0.30):
    """Weighted-without-replacement sampling weights: opponents with higher
    recorded informativeness (this-generation across-candidate spread) get
    sampled more for the cheap screening stages, but every opponent keeps
    at least `min_floor` share of a uniform draw so none disappears
    permanently (an opponent every candidate loses to identically is less
    useful early, but may become discriminating again once the population
    improves -- the floor keeps it in rotation for that). v7: raised from
    0.15 to 0.30 to better match the "adaptive selection should never
    fully replace a stable canonical ruler" guidance -- a purely
    informativeness-driven 85% share let the evaluation mix drift enough
    generation-to-generation to add its own noise on top of an
    already-noisy fitness signal."""
    raw = [stats.get(n, {}).get("informativeness", 0.0) for n in names]
    total_raw = sum(raw)
    n = len(names)
    if total_raw <= 0:
        return [1.0 / n] * n
    uniform = 1.0 / n
    return [min_floor * uniform + (1 - min_floor) * (r / total_raw) for r in raw]


def _weighted_sample_without_replacement(items, weights, k, rng):
    k = min(k, len(items))
    pool_items, pool_weights = list(items), list(weights)
    chosen = []
    for _ in range(k):
        total = sum(pool_weights)
        r = rng.uniform(0, total) if total > 0 else 0.0
        acc = 0.0
        idx = len(pool_items) - 1
        for i, w in enumerate(pool_weights):
            acc += w
            if r <= acc:
                idx = i
                break
        chosen.append(pool_items.pop(idx))
        pool_weights.pop(idx)
    return chosen


def _select_fresh_opponents(all_indices, used_indices, weights, k, rng):
    """Weighted sample of k opponent indices, preferring ones NOT in
    `used_indices` -- guarantees freshness BY CONSTRUCTION (sample the
    disjoint remainder first) rather than sampling from the whole pool and
    discarding overlaps afterward, which can silently fall back to
    reusing the exact same opponents whenever the filtered result comes up
    empty (a real risk here specifically: the diverse-opponent pool is only
    ~25 entries, far smaller than the seed pools, so an all-fresh draw
    failing isn't a theoretical edge case)."""
    used_indices = set(used_indices)
    fresh = [i for i in all_indices if i not in used_indices]
    if len(fresh) >= k:
        return _weighted_sample_without_replacement(fresh, [weights[i] for i in fresh], k, rng)
    # Not enough unseen opponents to fill the stage -- take every fresh one,
    # then top up with just the shortfall from the already-used set (never
    # silently substitute the entire original, fully-overlapping draw).
    used = [i for i in all_indices if i in used_indices]
    topped_up = (_weighted_sample_without_replacement(used, [weights[i] for i in used], k - len(fresh), rng)
                 if used else [])
    return fresh + topped_up


# ===========================================================================
# Racing / successive-halving pipeline (module docstring #3).
# ===========================================================================

def _build_diverse_tasks(candidate_keys, params_by_key, opp_indices, seeds, orientations_both=True):
    tasks = []
    for opp_idx in opp_indices:
        name = DIVERSE_OPPONENTS[opp_idx]["name"]
        for seed in seeds:
            for cand_key in candidate_keys:
                tasks.append((cand_key, params_by_key[cand_key], "diverse", name, opp_idx, seed, True))
                if orientations_both:
                    tasks.append((cand_key, params_by_key[cand_key], "diverse", name, opp_idx, seed, False))
    return tasks


def _build_baseline_tasks(candidate_keys, params_by_key, seeds):
    tasks = []
    for i, seed in enumerate(seeds):
        p0 = (i % 2 == 0)
        for cand_key in candidate_keys:
            tasks.append((cand_key, params_by_key[cand_key], "baseline", "main_baseline", None, seed, p0))
    return tasks


def _run_tasks(pool, tasks, accum):
    """Execute `tasks` and fold results into `accum` (mutated in place):
    accum[cand_key] = {"diverse": [(trend,terminal),...], "baseline": [...],
    "by_opponent": {name: [trend,...]}}. Returns elapsed seconds and total
    game count for logging."""
    if not tasks:
        return 0.0, 0
    t0 = time.time()
    for cand_key, pool_type, opp_name, trend, terminal in pool.map(_play_game_task, tasks, chunksize=4):
        a = accum[cand_key]
        a[pool_type].append((trend, terminal))
        if pool_type == "diverse":
            a["by_opponent"].setdefault(opp_name, []).append(trend)
    return time.time() - t0, len(tasks)


def _spearman_rho(xs, ys):
    """Spearman rank correlation between two equal-length lists (no
    ties-correction -- fine here since these are noisy float fitness scores,
    exact ties are rare). Returns None if undefined (n<2 or a constant
    list). Used to check whether Stage A's cheap screening ranking survives
    into the final (Stage A+B+C) ranking for the candidates that made it to
    Stage B -- if this correlation is weak, Stage A is eliminating good
    candidates on noise rather than signal (a real risk of successive
    halving that's otherwise invisible from the fitness numbers alone)."""
    n = len(xs)
    if n < 2:
        return None

    def _ranks(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0] * len(vals)
        for r, i in enumerate(order):
            ranks[i] = r
        return ranks

    rx, ry = _ranks(xs), _ranks(ys)
    mean_r = (n - 1) / 2
    num = sum((a - mean_r) * (b - mean_r) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mean_r) ** 2 for a in rx) * sum((b - mean_r) ** 2 for b in ry))
    return num / den if den > 0 else None


def _score_accumulated(acc, baseline_tolerance, baseline_weight=BASELINE_WEIGHT_DEFAULT):
    """Turn one candidate's accumulated (diverse, baseline) game results into
    a fitness value plus every component spec section 10/26/27 wants logged
    separately."""
    diverse = acc["diverse"]
    baseline = acc["baseline"]
    diverse_trend = [t for t, _ in diverse]
    diverse_terminal = [te for _, te in diverse]
    baseline_trend = [t for t, _ in baseline]

    diverse_mean = statistics.mean(diverse_trend) if diverse_trend else 0.0
    diverse_std = statistics.pstdev(diverse_trend) if len(diverse_trend) > 1 else 0.0
    terminal_mean = statistics.mean(diverse_terminal) if diverse_terminal else 0.0
    baseline_mean = statistics.mean(baseline_trend) if baseline_trend else 0.0
    baseline_std = statistics.pstdev(baseline_trend) if len(baseline_trend) > 1 else 0.0
    baseline_win_rate = (sum(1 for d in baseline_trend if d > 0) / len(baseline_trend)) if baseline_trend else None
    worst_opponent = None
    worst_opponent_mean = None
    for name, deltas in acc["by_opponent"].items():
        m = statistics.mean(deltas)
        if worst_opponent_mean is None or m < worst_opponent_mean:
            worst_opponent_mean, worst_opponent = m, name

    # diverse_fitness: computable identically for EVERY candidate regardless
    # of how far it got in the Stage A/B/C race (an eliminated candidate only
    # ever has Stage-A/B diverse games; a finalist has A+B+C) -- kept as its
    # own field (still used e.g. by run_sensitivity_analysis) even though it
    # is no longer what es.tell() is fed (see below).
    diverse_fitness = diverse_mean - LAMBDA_VARIANCE * diverse_std

    # v7: `fitness` = diverse_fitness plus an EXPLICIT, separately-weighted
    # baseline term, instead of pooling diverse+baseline deltas into one
    # combined mean. Pooling let raw diverse-pool blowout wins (weak
    # historical bots, $10-20k/game deltas) completely swamp the baseline
    # term (main.py, $100s-$1000s/game deltas) despite an "extra regression
    # penalty" on top -- confirmed empirically: v6's checkpoint reached
    # fitness=6291 with baseline_mean=-625 (a candidate that reliably LOSES
    # to main.py). `baseline_weight` makes the baseline term's scale
    # commensurate with diverse_fitness's by construction rather than by
    # accident of how many games happen to be in each list. Every candidate
    # now has a baseline sample (see module docstring #6 / _run_generation_
    # racing's Stage A), so this is a homogeneous, tell()-safe objective for
    # the whole population, not just finalists.
    fitness = diverse_fitness
    if baseline_trend:
        baseline_component = baseline_weight * (baseline_mean - LAMBDA_VARIANCE * baseline_std)
        if baseline_mean < -baseline_tolerance:
            baseline_component += EXTRA_REGRESSION_PENALTY_MULT * baseline_weight * (baseline_mean + baseline_tolerance)
        fitness = diverse_fitness + baseline_component

    return {
        "fitness": fitness,
        "diverse_fitness": diverse_fitness,
        "diverse_mean": diverse_mean,
        "diverse_std": diverse_std,
        "terminal_mean": terminal_mean,
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "baseline_win_rate": baseline_win_rate,
        "worst_opponent": worst_opponent,
        "worst_opponent_mean": worst_opponent_mean,
        "n_diverse_games": len(diverse_trend),
        "n_baseline_games": len(baseline_trend),
    }


def _run_generation_racing(es, pool, generation, args, opponent_stats, rng):
    """The Stage A -> B -> C successive-halving pipeline. Returns
    (fitnesses_in_population_order, scores_by_cand_idx, stats_for_logging)."""
    solutions_norm = es.ask()
    solutions_real = [_to_real(s) for s in solutions_norm]
    n_pop = len(solutions_real)
    cand_keys = list(range(n_pop))
    params_by_key = {i: solutions_real[i] for i in cand_keys}
    accum = {i: {"diverse": [], "baseline": [], "by_opponent": {}} for i in cand_keys}

    n_diverse = len(DIVERSE_OPPONENTS)
    all_opp_indices = list(range(n_diverse))
    names = [o["name"] for o in DIVERSE_OPPONENTS]
    weights = _opponent_sampling_weights(opponent_stats, names)

    total_games = 0
    total_elapsed = 0.0

    # ---- Stage A: screen everyone, cheap. ----
    screen_count = min(args.screening_opponents, n_diverse)
    stage_a_opp = _weighted_sample_without_replacement(all_opp_indices, weights, screen_count, rng)
    seeds_a = get_generation_seed_batch(generation, args.screening_seeds, _STAGE_A_SEED_POOL,
                                         args.seed_batch_generations)
    tasks_a = _build_diverse_tasks(cand_keys, params_by_key, stage_a_opp, seeds_a)
    elapsed, n = _run_tasks(pool, tasks_a, accum)
    total_games += n
    total_elapsed += elapsed

    # v7: EVERY population member (not just eventual finalists) also plays a
    # small common-random-number baseline probe right here in Stage A -- see
    # module docstring #6. Without this, `fitness` below would still only
    # have a baseline component for finalists, and es.tell() (which now
    # reads `fitness`, not `diverse_fitness`) would be back to comparing a
    # baseline-blind score for most of the population against a
    # baseline-aware one for a few survivors -- the same "two different
    # objectives" problem the Stage A/B/C split was built to avoid.
    seeds_a_baseline = get_generation_seed_batch(generation, args.screening_baseline_seeds,
                                                  _STAGE_A_BASELINE_SEED_POOL, args.seed_batch_generations)
    tasks_a_baseline = _build_baseline_tasks(cand_keys, params_by_key, seeds_a_baseline)
    elapsed, n = _run_tasks(pool, tasks_a_baseline, accum)
    total_games += n
    total_elapsed += elapsed

    stage_a_scores = {i: _score_accumulated(accum[i], args.baseline_tolerance, args.baseline_weight)["fitness"]
                       for i in cand_keys}
    n_survive_b = max(1, math.ceil(n_pop * args.survivor_fraction))
    survivors_b = sorted(cand_keys, key=lambda i: -stage_a_scores[i])[:n_survive_b]

    # ---- Stage B: survivors only, bigger opponent subset, fresh seeds.
    # Opponents preferred-fresh via _select_fresh_opponents (guaranteed by
    # construction when the pool allows it, see its docstring); seeds drawn
    # from Stage B's OWN disjoint third of the pool, so they can never
    # collide with Stage A's regardless of batch sizes. ----
    stage_b_count = min(n_diverse, screen_count * STAGE_B_OPPONENT_MULT)
    stage_b_opp = _select_fresh_opponents(all_opp_indices, stage_a_opp, weights, stage_b_count, rng)
    seeds_b = get_generation_seed_batch(generation, args.stage_b_seeds, _STAGE_B_SEED_POOL,
                                         args.seed_batch_generations)
    params_by_key_b = {i: params_by_key[i] for i in survivors_b}
    tasks_b = _build_diverse_tasks(survivors_b, params_by_key_b, stage_b_opp, seeds_b)
    elapsed, n = _run_tasks(pool, tasks_b, accum)
    total_games += n
    total_elapsed += elapsed

    stage_b_scores = {i: _score_accumulated(accum[i], args.baseline_tolerance, args.baseline_weight)["fitness"]
                       for i in survivors_b}
    n_finalists = min(args.finalists, len(survivors_b))
    finalists = sorted(survivors_b, key=lambda i: -stage_b_scores[i])[:n_finalists]

    # ---- Stage C: finalists get the FULL diverse pool + the protected
    # baseline matchup -- only candidates that already look strong pay for
    # the baseline check, instead of diluting it across the whole population
    # (the exact failure mode that sank round 2 -- see TUNING_NOTES.md).
    # Seeds come from Stage C's own disjoint third of the pool (structurally
    # can't collide with A/B). Opponents: whatever's left after A+B (already
    # genuinely disjoint by construction here -- a plain set difference,
    # no filter-then-fallback needed), falling back to the full pool only
    # when there's truly nothing left unseen. ----
    seeds_c = get_generation_seed_batch(generation, args.stage_c_seeds, _STAGE_C_SEED_POOL,
                                         args.seed_batch_generations)
    params_by_key_c = {i: params_by_key[i] for i in finalists}
    remaining_opp = [i for i in all_opp_indices if i not in stage_a_opp and i not in stage_b_opp]
    stage_c_opp = remaining_opp if remaining_opp else all_opp_indices
    tasks_c = _build_diverse_tasks(finalists, params_by_key_c, stage_c_opp, seeds_c)
    elapsed, n = _run_tasks(pool, tasks_c, accum)
    total_games += n
    total_elapsed += elapsed

    # Baseline games sized so they're ~BASELINE_FRACTION of a FINALIST's
    # total accumulated diverse games (module docstring #3/#5).
    diverse_games_so_far = max(1, len(accum[finalists[0]]["diverse"])) if finalists else 1
    n_baseline = max(MIN_BASELINE_GAMES, round(diverse_games_so_far * BASELINE_FRACTION / (1 - BASELINE_FRACTION)))
    if n_baseline % 2:
        n_baseline += 1
    seeds_baseline = get_generation_seed_batch(generation, n_baseline, _FINALIST_BASELINE_SEED_POOL,
                                                args.seed_batch_generations)
    tasks_baseline = _build_baseline_tasks(finalists, params_by_key_c, seeds_baseline)
    elapsed, n = _run_tasks(pool, tasks_baseline, accum)
    total_games += n
    total_elapsed += elapsed

    # ---- Score everyone; eliminated candidates keep their lower-fidelity
    # (Stage-A/B-only diverse games, Stage-A-only baseline games) score --
    # standard successive-halving practice: a pruned arm's fitness estimate
    # is real, just noisier. ----
    final_scores = {i: _score_accumulated(accum[i], args.baseline_tolerance, args.baseline_weight)
                     for i in cand_keys}
    fitnesses = [final_scores[i]["fitness"] for i in cand_keys]

    # Diagnostic only (does not affect selection): does Stage A's cheap
    # screening ranking of the survivors agree with their FINAL (Stage
    # A+B+C) ranking? A weak correlation would mean Stage A is eliminating
    # good candidates on noise, not signal -- invisible from the fitness
    # numbers alone, so it's tracked explicitly.
    stage_a_vs_final_rho = _spearman_rho([stage_a_scores[i] for i in survivors_b],
                                          [final_scores[i]["fitness"] for i in survivors_b])
    # v7: es.tell() now gets `fitness` (diverse_fitness + weighted baseline
    # component), NOT `diverse_fitness` -- see module docstring #6. This is
    # now safe/homogeneous because EVERY candidate in cand_keys has at least
    # the Stage A baseline probe above, not just finalists; a finalist's
    # baseline sample is simply larger/less noisy (same successive-halving
    # logic already applied to diverse games). Feeding CMA-ES diverse_fitness
    # alone -- v6's approach -- gave it literally no gradient toward beating
    # the baseline at all, which matches what the checkpoint showed: fitness
    # climbing generation over generation while baseline_mean stayed
    # negative throughout.
    es.tell(solutions_norm, [-f for f in fitnesses])

    # Update opponent informativeness stats from this generation's Stage A
    # spread (the cheapest, broadest-coverage signal -- see section 18).
    per_opp_this_gen = {}
    for i in cand_keys:
        for name, deltas in accum[i]["by_opponent"].items():
            per_opp_this_gen.setdefault(name, []).extend(deltas)
    for name, deltas in per_opp_this_gen.items():
        _update_opponent_stats(opponent_stats, name, deltas)

    diag = {
        "n_games": total_games,
        "elapsed": total_elapsed,
        "stage_a_opponents": [names[i] for i in stage_a_opp],
        "stage_b_opponents": [names[i] for i in stage_b_opp],
        "finalists": finalists,
        "solutions_norm": solutions_norm,
        "solutions_real": solutions_real,
        "stage_a_vs_final_rho": stage_a_vs_final_rho,
    }
    return fitnesses, final_scores, diag


# ===========================================================================
# Level B -- verification on fresh, disjoint seeds (module docstring #4).
# ===========================================================================

def verify_candidate(pool, params_vector, n_verification_seeds, n_verification_baseline_games,
                      baseline_tolerance, baseline_weight=BASELINE_WEIGHT_DEFAULT):
    cand_key = "verify"
    accum = {cand_key: {"diverse": [], "baseline": [], "by_opponent": {}}}
    params_by_key = {cand_key: params_vector}
    n_diverse = len(DIVERSE_OPPONENTS)
    seeds = _VERIFICATION_SEED_POOL[:n_verification_seeds]
    tasks = _build_diverse_tasks([cand_key], params_by_key, list(range(n_diverse)), seeds)
    _run_tasks(pool, tasks, accum)

    baseline_seeds = _VERIFICATION_BASELINE_SEED_POOL[:n_verification_baseline_games]
    tasks_b = _build_baseline_tasks([cand_key], params_by_key, baseline_seeds)
    _run_tasks(pool, tasks_b, accum)

    return _score_accumulated(accum[cand_key], baseline_tolerance, baseline_weight)


# ===========================================================================
# Level C -- promotion benchmark: candidate vs. main.py, large fresh seed
# set, full statistics. This is a deliberately separate, user-invoked path
# (`--promote`), not run automatically every generation.
# ===========================================================================

def _promote_worker_init(candidate_path, baseline_path):
    import copy
    copy.deepcopy = _fast_deepcopy
    import benchmark as bm
    _worker_state["promote_agent_a"] = bm.load_agent(candidate_path)
    _worker_state["promote_agent_b"] = bm.load_agent(baseline_path)


def _promote_one_task(task):
    """Module-level (picklable) worker function for promotion_benchmark's
    Pool -- a closure over agent_a/agent_b cannot be sent to worker
    processes (multiprocessing pickles the callable itself), so the agents
    live in _worker_state instead, set up once per worker by
    _promote_worker_init, matching this file's existing worker pattern."""
    seed, a_is_p0 = task
    agent_a = _worker_state["promote_agent_a"]
    agent_b = _worker_state["promote_agent_b"]
    if a_is_p0:
        return _run_game_scores(agent_a, agent_b, seed)
    trend, terminal = _run_game_scores(agent_b, agent_a, seed)
    return -trend, -terminal


def promotion_benchmark(candidate_path, baseline_path="main.py", n_games=40, workers=None):
    import benchmark as bm
    seeds = _PROMOTION_SEED_POOL[:max(2, n_games)]
    half = len(seeds) // 2
    jobs = [(seeds[i], True) for i in range(half)] + [(seeds[i], False) for i in range(half, len(seeds))]

    if workers and workers > 1:
        with mp.Pool(processes=workers, initializer=_promote_worker_init,
                      initargs=(candidate_path, baseline_path)) as p:
            results = p.map(_promote_one_task, jobs)
    else:
        agent_a = bm.load_agent(candidate_path)
        agent_b = bm.load_agent(baseline_path)
        results = []
        for seed, a_is_p0 in jobs:
            if a_is_p0:
                results.append(_run_game_scores(agent_a, agent_b, seed))
            else:
                t, te = _run_game_scores(agent_b, agent_a, seed)
                results.append((-t, -te))

    trends = [t for t, _ in results]
    terminals = [te for _, te in results]
    wins = sum(1 for t in terminals if t > 0)
    losses = sum(1 for t in terminals if t < 0)
    ties = len(terminals) - wins - losses
    sorted_terminals = sorted(terminals)
    mid = len(sorted_terminals) // 2
    median_terminal = (sorted_terminals[mid] if len(sorted_terminals) % 2 else
                        (sorted_terminals[mid - 1] + sorted_terminals[mid]) / 2)

    stats = {
        "n_games": len(terminals),
        "wins": wins, "losses": losses, "ties": ties,
        "win_rate": wins / len(terminals),
        "mean_terminal_delta": statistics.mean(terminals),
        "median_terminal_delta": median_terminal,
        "std_terminal_delta": statistics.pstdev(terminals) if len(terminals) > 1 else 0.0,
        "worst_game": min(terminals),
        "best_game": max(terminals),
        "mean_trend_delta": statistics.mean(trends),
    }
    print(f"\n{'=' * 62}\n  PROMOTION BENCHMARK: {candidate_path} vs {baseline_path}\n{'=' * 62}")
    for k, v in stats.items():
        print(f"  {k:24s} {v:.3f}" if isinstance(v, float) else f"  {k:24s} {v}")
    verdict = "PROMOTE" if stats["mean_terminal_delta"] > 0 and stats["win_rate"] >= 0.5 else "DO NOT PROMOTE"
    print(f"  {'-' * 58}\n  VERDICT: {verdict} (do not promote based solely on the average -- "
          f"check win_rate and worst_game too)\n{'=' * 62}\n")
    return stats


# ===========================================================================
# Diagnostics: parameter-population diversity (section 21) and sensitivity
# analysis (section 22). Diagnostic only -- never fed back into fitness.
# ===========================================================================

def _log_param_diversity(solutions_norm, active_names, top_k=3):
    if not solutions_norm or len(solutions_norm) < 2:
        return
    n_dims = len(solutions_norm[0])
    stds = [statistics.pstdev([sol[i] for sol in solutions_norm]) for i in range(n_dims)]
    order = sorted(range(n_dims), key=lambda i: stds[i])
    collapsed = [(active_names[i], stds[i]) for i in order[:top_k]]
    variable = [(active_names[i], stds[i]) for i in order[-top_k:]]
    print(f"  [diversity] most collapsed: {[(n, round(s, 3)) for n, s in collapsed]}")
    print(f"  [diversity] most variable:  {[(n, round(s, 3)) for n, s in variable]}")


def run_sensitivity_analysis(pool, elite_params, active_names, n_seeds=6, delta_frac=0.1):
    """Perturb each of `active_names` one at a time around `elite_params` by
    +-delta_frac of that parameter's range, evaluate on a small FIXED seed
    set (same seeds for every perturbation -- common-random-numbers again,
    for a fair local comparison), and report which parameters barely move
    the score ("dead") vs. which move it a lot ("sensitive"). Expensive
    relative to one generation (2 * len(active_names) extra evaluations) --
    intended to run periodically (--sensitivity-every), not every generation."""
    seeds = _VERIFICATION_SEED_POOL[-n_seeds:]
    n_diverse = min(6, len(DIVERSE_OPPONENTS))
    opp_indices = list(range(n_diverse))
    name_to_idx = {n: i for i, n in enumerate(tuning_spec.NAMES)}

    def _score_vector(vec):
        cand_key = "sens"
        accum = {cand_key: {"diverse": [], "baseline": [], "by_opponent": {}}}
        tasks = _build_diverse_tasks([cand_key], {cand_key: vec}, opp_indices, seeds)
        _run_tasks(pool, tasks, accum)
        return _score_accumulated(accum[cand_key], BASELINE_TOLERANCE_DEFAULT)["diverse_mean"]

    base_score = _score_vector(elite_params)
    results = []
    for name in active_names:
        i = name_to_idx[name]
        lo, hi = tuning_spec.LOWS[i], tuning_spec.HIGHS[i]
        span = (hi - lo) * delta_frac
        minus = list(elite_params); minus[i] = max(lo, elite_params[i] - span)
        plus = list(elite_params); plus[i] = min(hi, elite_params[i] + span)
        s_minus = _score_vector(minus)
        s_plus = _score_vector(plus)
        sensitivity = abs(s_plus - base_score) + abs(s_minus - base_score)
        results.append({"name": name, "base": base_score, "minus": s_minus, "plus": s_plus,
                         "sensitivity": sensitivity})
    results.sort(key=lambda r: -r["sensitivity"])
    print("  [sensitivity] most sensitive:", [(r["name"], round(r["sensitivity"], 1)) for r in results[:5]])
    print("  [sensitivity] most dead:     ", [(r["name"], round(r["sensitivity"], 1)) for r in results[-5:]])
    return results


# ===========================================================================
# Restart location selection (module docstring #5 / section 20).
# ===========================================================================

def _restart_x0(restart_number, global_best_norm, leg_bests_norm, rng):
    """restart 1 -> global best (unchanged). restart 2 -> a perturbed
    version of the global best (explores nearby without discarding it).
    restart 3+ -> a different leg's best if one exists (genuine basin
    diversity), else the global best perturbed more strongly. The global
    best itself is ALWAYS tracked separately in the caller and never lost,
    regardless of where a restart begins from."""
    if restart_number == 1:
        return list(global_best_norm)
    if restart_number == 2:
        return [min(1.0, max(0.0, v + rng.gauss(0, 0.08))) for v in global_best_norm]
    others = [b for b in leg_bests_norm if b != global_best_norm]
    if others:
        base = rng.choice(others)
        return [min(1.0, max(0.0, v + rng.gauss(0, 0.05))) for v in base]
    return [min(1.0, max(0.0, v + rng.gauss(0, 0.15))) for v in global_best_norm]


# ===========================================================================
# Staged parameter activation (sections 13-14) -- OPT-IN via --staged-params.
# Default behavior (matching v3-v5) activates every parameter immediately.
# ===========================================================================

DEFAULT_STAGE_ORDER = ["core_strategy", "premium_shift", "item_reserves", "shed_overflow",
                        "front_run_priority", "front_run_gates", "fert_relay", "price_floor",
                        "rank_sell_slots", "terminal_liquidation"]


def _active_mask_for_stage(stage_index, stage_order=DEFAULT_STAGE_ORDER):
    """Cumulative: stage N activates its own group PLUS every group from
    earlier stages (matches spec section 14's "Stage 4: jointly fine-tune
    all active parameters" -- by the last stage everything is active)."""
    active_groups = set(stage_order[:stage_index + 1])
    return [any(name in tuning_spec.PARAM_GROUPS[g] for g in active_groups) for name in tuning_spec.NAMES]


def dry_run(args):
    n_diverse = len(DIVERSE_OPPONENTS)
    popsize = args.popsize or (4 + int(3 * math.log(tuning_spec.DIM)))
    screen_count = min(args.screening_opponents, n_diverse)
    stage_b_count = min(n_diverse, screen_count * STAGE_B_OPPONENT_MULT)
    n_survive_b = max(1, math.ceil(popsize * args.survivor_fraction))
    n_finalists = min(args.finalists, n_survive_b)

    stage_a_games = popsize * screen_count * args.screening_seeds * 2
    stage_a_baseline_games = popsize * args.screening_baseline_seeds
    stage_b_games = n_survive_b * stage_b_count * args.stage_b_seeds * 2
    stage_c_diverse_games = n_finalists * max(0, n_diverse - screen_count - stage_b_count) * args.stage_c_seeds * 2
    approx_baseline_games = max(MIN_BASELINE_GAMES, round(
        (screen_count * args.screening_seeds * 2) * BASELINE_FRACTION / (1 - BASELINE_FRACTION)))
    stage_c_baseline_games = n_finalists * approx_baseline_games
    total = stage_a_games + stage_a_baseline_games + stage_b_games + stage_c_diverse_games + stage_c_baseline_games

    print("=== evolve.py v7 dry run (no games will be played) ===")
    print(f"parameter dimensions: {tuning_spec.DIM}")
    print(f"parameter groups: {[(g, len(v)) for g, v in tuning_spec.PARAM_GROUPS.items()]}")
    print(f"kind groups: {[(k, len(v)) for k, v in tuning_spec.KIND_GROUPS.items()]}")
    print(f"population size: {popsize}")
    print(f"diverse opponent pool: {n_diverse} ({[o['name'] for o in DIVERSE_OPPONENTS]})")
    print(f"screening opponents: {screen_count}, screening seeds: {args.screening_seeds}")
    print(f"stage B opponents: {stage_b_count}, stage B seeds: {args.stage_b_seeds}")
    print(f"survivor fraction: {args.survivor_fraction} -> {n_survive_b} survivors into stage B")
    print(f"finalists: {n_finalists}")
    print(f"stage C seeds/opponent: {args.stage_c_seeds}")
    print(f"expected stage A games/generation: {stage_a_games}")
    print(f"expected stage A baseline-probe games/generation: {stage_a_baseline_games} "
          f"(v7: every population member, not just finalists -- see module docstring #6)")
    print(f"expected stage B games/generation: {stage_b_games}")
    print(f"expected stage C diverse games/generation: {stage_c_diverse_games}")
    print(f"expected stage C baseline games/generation: {stage_c_baseline_games} "
          f"(target baseline fraction: {BASELINE_FRACTION:.0%})")
    print(f"TOTAL expected games/generation (approx): {total}")
    print(f"verification seeds/opponent: {args.verification_seeds}  "
          f"verification baseline games: {args.verification_baseline_games}")
    print(f"seed batch generations: {args.seed_batch_generations}")
    print(f"baseline tolerance: {args.baseline_tolerance}  baseline weight: {args.baseline_weight}  "
          f"extra penalty mult beyond tolerance: {EXTRA_REGRESSION_PENALTY_MULT}")
    print(f"staged params: {args.staged_params}  stage order: {DEFAULT_STAGE_ORDER if args.staged_params else 'n/a (all active)'}")
    print(f"sensitivity analysis every: {args.sensitivity_every or 'off'}")
    print(f"seed pools: optimization={len(_OPTIMIZATION_SEED_POOL)}, "
          f"optimization_baseline={len(_OPTIMIZATION_BASELINE_SEED_POOL)}, "
          f"verification={len(_VERIFICATION_SEED_POOL)}, "
          f"verification_baseline={len(_VERIFICATION_BASELINE_SEED_POOL)}, "
          f"promotion={len(_PROMOTION_SEED_POOL)}")
    sample_batch = get_generation_seed_batch(0, args.screening_seeds, _OPTIMIZATION_SEED_POOL,
                                              args.seed_batch_generations)
    print(f"generation-0 screening seed batch (sample): {sample_batch}")
    print("=== dry run complete -- no checkpoint written, no games played ===")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generations", type=int, default=None,
                     help="Stop after this many generations total, across restarts")
    ap.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 4))
    ap.add_argument("--checkpoint", default=CHECKPOINT_PATH_DEFAULT)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--promote", metavar="CANDIDATE.py",
                     help="Level C: run the promotion benchmark of CANDIDATE.py vs. --baseline, then exit")
    ap.add_argument("--baseline", default="main.py", help="--promote's baseline (default main.py)")
    ap.add_argument("--promote-games", type=int, default=40)
    ap.add_argument("--popsize", type=int, default=None)
    ap.add_argument("--max-restarts", type=int, default=3)
    ap.add_argument("--screening-opponents", type=int, default=SCREENING_OPPONENT_COUNT_DEFAULT)
    ap.add_argument("--screening-seeds", type=int, default=SCREENING_SEEDS_DEFAULT)
    ap.add_argument("--stage-b-seeds", type=int, default=STAGE_B_SEEDS_DEFAULT)
    ap.add_argument("--stage-c-seeds", type=int, default=STAGE_C_SEEDS_DEFAULT)
    ap.add_argument("--survivor-fraction", type=float, default=SURVIVOR_FRACTION_DEFAULT)
    ap.add_argument("--finalists", type=int, default=FINALIST_COUNT_DEFAULT)
    ap.add_argument("--verification-seeds", type=int, default=VERIFICATION_SEEDS_DEFAULT)
    ap.add_argument("--verification-baseline-games", type=int, default=VERIFICATION_BASELINE_GAMES_DEFAULT)
    ap.add_argument("--seed-batch-generations", type=int, default=SEED_BATCH_GENERATIONS_DEFAULT)
    ap.add_argument("--baseline-tolerance", type=float, default=BASELINE_TOLERANCE_DEFAULT)
    ap.add_argument("--screening-baseline-seeds", type=int, default=SCREENING_BASELINE_SEEDS_DEFAULT,
                     help="v7: common-random-number baseline games EVERY population member plays in Stage A, "
                          "so es.tell() gets a homogeneous baseline signal instead of zero baseline signal")
    ap.add_argument("--baseline-weight", type=float, default=BASELINE_WEIGHT_DEFAULT,
                     help="v7: multiplier on the baseline component of `fitness` (see module docstring #6)")
    ap.add_argument("--staged-params", action="store_true",
                     help="Optimize PARAM_GROUPS one stage at a time (cumulative) instead of all 60 dims at once")
    ap.add_argument("--stage-generations", type=int, default=15,
                     help="Generations per parameter stage when --staged-params is set")
    ap.add_argument("--sensitivity-every", type=int, default=0,
                     help="Run a local parameter-sensitivity sweep on the elite every N generations (0 = off)")
    args = ap.parse_args()

    if args.dry_run:
        dry_run(args)
        return

    if args.report:
        report(args.checkpoint)
        return

    if args.promote:
        promotion_benchmark(args.promote, args.baseline, args.promote_games, args.workers)
        return

    import cma

    ckpt = load_checkpoint(args.checkpoint) if args.resume else None
    if ckpt is not None:
        old_names = ckpt.get("param_names", tuning_spec.NAMES)
        raw_best = ckpt.get("best_verified_params") or ckpt["best_params"]
        if old_names == tuning_spec.NAMES:
            best_params = raw_best
        else:
            best_params, _ = tuning_spec.remap_checkpoint_vector(old_names, raw_best)
        x0_norm = _to_normalized(best_params)
        fitness_history = ckpt.get("fitness_history", [])
        best_fitness_history = ckpt.get("best_fitness_history") or list(fitness_history)
        generation = ckpt["generation"]
        best_opt_fitness = ckpt.get("best_optimization_fitness", ckpt.get("best_fitness", float("-inf")))
        best_opt_params = best_params
        best_opt_score = {
            "diverse_mean": ckpt.get("best_optimization_mean_delta", ckpt.get("best_mean_delta", 0.0)),
            "diverse_std": ckpt.get("best_optimization_std_delta", ckpt.get("best_std_delta", 0.0)),
            "baseline_mean": ckpt.get("best_optimization_baseline_mean_delta", ckpt.get("best_baseline_mean_delta", 0.0)),
        }
        best_verified_fitness = ckpt.get("best_verified_fitness")
        best_verified_params = ckpt.get("best_verified_params")
        best_verified_score = ckpt.get("best_verified_score", {})
        sigma0 = ckpt.get("sigma0", 0.2)
        restarts_used = ckpt.get("restarts_used", 0)
        base_popsize = ckpt.get("base_popsize", args.popsize)
        opponent_stats = ckpt.get("opponent_stats", {})
        leg_bests_norm = [x0_norm]
        print(f"Resuming from generation {generation}, best_optimization_fitness={best_opt_fitness:.1f}, "
              f"restarts_used={restarts_used}"
              + (f", best_verified_fitness={best_verified_fitness:.1f}" if best_verified_fitness is not None else ""))
    else:
        x0_norm = _to_normalized(tuning_spec.default_vector())
        fitness_history = []
        best_fitness_history = []
        generation = 0
        best_opt_fitness = float("-inf")
        best_opt_params = tuning_spec.default_vector()
        best_opt_score = {"diverse_mean": 0.0, "diverse_std": 0.0, "baseline_mean": 0.0}
        best_verified_fitness = None
        best_verified_params = None
        best_verified_score = {}
        sigma0 = 0.2
        restarts_used = 0
        base_popsize = args.popsize
        opponent_stats = {}
        leg_bests_norm = [x0_norm]

    n_diverse = len(DIVERSE_OPPONENTS)
    print(f"evolve.py v7: {tuning_spec.DIM} dims, workers={args.workers}, "
          f"diverse_opponents={n_diverse} ({[o['name'] for o in DIVERSE_OPPONENTS]}), "
          f"screening={args.screening_opponents}op/{args.screening_seeds}sd/"
          f"{args.screening_baseline_seeds}bsd, "
          f"survivor_fraction={args.survivor_fraction}, finalists={args.finalists}, "
          f"seed_batch_generations={args.seed_batch_generations}, "
          f"baseline_tolerance={args.baseline_tolerance}, baseline_weight={args.baseline_weight}, "
          f"staged_params={args.staged_params}, max_restarts={args.max_restarts}")

    stage_order = DEFAULT_STAGE_ORDER if args.staged_params else None
    stage_index = 0 if stage_order else None

    def _checkpoint_state(es_sigma, converged):
        return {
            "generation": generation, "restarts_used": restarts_used, "base_popsize": base_popsize,
            "best_optimization_fitness": best_opt_fitness,
            "best_optimization_mean_delta": best_opt_score.get("diverse_mean", 0.0),
            "best_optimization_std_delta": best_opt_score.get("diverse_std", 0.0),
            "best_optimization_baseline_mean_delta": best_opt_score.get("baseline_mean", 0.0),
            "best_params": list(best_opt_params),
            "best_verified_fitness": best_verified_fitness,
            "best_verified_params": list(best_verified_params) if best_verified_params else None,
            "best_verified_mean_delta": best_verified_score.get("diverse_mean"),
            "best_verified_std_delta": best_verified_score.get("diverse_std"),
            "best_verified_baseline_mean_delta": best_verified_score.get("baseline_mean"),
            "best_verified_baseline_win_rate": best_verified_score.get("baseline_win_rate"),
            "fitness_history": fitness_history, "best_fitness_history": best_fitness_history,
            "sigma0": float(es_sigma), "converged": converged,
            "param_names": tuning_spec.NAMES,
            "diverse_opponents": [o["name"] for o in DIVERSE_OPPONENTS],
            "opponent_stats": opponent_stats,
            "param_groups": {g: v for g, v in tuning_spec.PARAM_GROUPS.items()},
            "seed_batch_config": {
                "seed_selection_seed": SEED_SELECTION_SEED,
                "seed_batch_generations": args.seed_batch_generations,
                "optimization_pool_size": len(_OPTIMIZATION_SEED_POOL),
                "verification_pool_size": len(_VERIFICATION_SEED_POOL),
            },
        }

    pool = mp.Pool(processes=args.workers, initializer=_worker_init)
    try:
        popsize = base_popsize
        while True:
            active_mask = _active_mask_for_stage(stage_index) if stage_order else [True] * tuning_spec.DIM
            active_indices = [i for i, a in enumerate(active_mask) if a]
            active_names = [tuning_spec.NAMES[i] for i in active_indices]
            frozen_values_norm = list(x0_norm)  # frozen dims stay at the current best's value

            x0_active = [x0_norm[i] for i in active_indices]
            opts = {"bounds": [0.0, 1.0], "verbose": -9}
            if popsize:
                opts["popsize"] = popsize
            es = cma.CMAEvolutionStrategy(x0_active, sigma0, opts)
            if not popsize:
                popsize = es.popsize

            def _expand(active_solution):
                full = list(frozen_values_norm)
                for j, i in enumerate(active_indices):
                    full[i] = active_solution[j]
                return full

            gen_this_leg = 0
            leg_best_history = []
            # Separate from best_opt_params (the ALL-TIME record, only
            # updated when a generation beats it): this leg's own best,
            # regardless of whether it ever set a global record. A staged
            # run can spend `--stage-generations` improving the CURRENT
            # stage's (reduced-dimension) objective without ever beating an
            # earlier leg's global-best fitness -- carrying forward the
            # stale global best as the next stage's x0 would silently
            # discard that improvement. See the stage-advance block below.
            leg_best_fitness = float("-inf")
            leg_best_params = best_opt_params
            while not es.stop():
                if args.generations is not None and generation >= args.generations:
                    print(f"Reached --generations {args.generations}, stopping.")
                    save_checkpoint(args.checkpoint, _checkpoint_state(es.sigma, True))
                    return

                class _FakeES:
                    """Adapter so _run_generation_racing (written against a
                    full-dimensionality es.ask()/es.tell(), doing its own
                    internal _to_real() on whatever ask() returns) can drive
                    a real `es` that's actually operating on the reduced
                    ACTIVE subspace when --staged-params is set. ask() must
                    return EXPANDED (full 60-dim) normalized vectors --
                    _run_generation_racing's own _to_real() call needs the
                    full length to zip correctly against tuning_spec.LOWS/
                    HIGHS (60 each), and vector_to_params() needs every name
                    present. tell() receives those same full-length vectors
                    back (unused) plus fitnesses, and must translate to the
                    REAL es's actual active-only representation, which this
                    class remembers from its own last ask() call rather than
                    re-deriving it. (Found via this file's own smoke test:
                    the original version returned the RAW un-expanded
                    active vector from ask(), causing vector_to_params() to
                    KeyError on frozen dimension names that were silently
                    missing from the too-short vector.)"""
                    def ask(self_):
                        self_.last_active = es.ask()
                        return [_expand(s) for s in self_.last_active]

                    def tell(self_, _solutions_norm_full_unused, neg_fitnesses):
                        es.tell(self_.last_active, neg_fitnesses)

                # Derived fresh from (SEED_SELECTION_SEED, generation) rather
                # than threaded through a single continuously-mutated rng:
                # a shared/mutable rng makes generation N's opponent subset
                # depend on every prior generation's call history, which (a)
                # can't be reproduced in isolation and (b) silently resets on
                # every --resume (main() re-seeds `rng` from scratch every
                # process start, but never persists/restores its state), so
                # a resumed run's generation N would NOT reselect the same
                # opponents a single uninterrupted run would have. Keying by
                # generation number makes each generation's opponent
                # selection a pure, resumption-safe function of its own
                # index (spec's "deterministic seed batches" requirement,
                # applied consistently to opponent sampling too).
                gen_rng = random.Random(f"{SEED_SELECTION_SEED}:opponents:{generation}")
                result_fitnesses, final_scores, diag = _run_generation_racing(
                    _FakeES(), pool, generation, args, opponent_stats, gen_rng)
                solutions_real = diag["solutions_real"]
                generation += 1
                gen_this_leg += 1

                # IMPORTANT: gen_best must be chosen from FINALISTS ONLY.
                # Eliminated (Stage A/B) candidates never got baseline-tested,
                # so their `fitness` has no baseline term at all and is on a
                # different, not-comparable scale from a finalist's full
                # (diverse + baseline) score -- an eliminated candidate with
                # an inflated diverse-only score could otherwise outrank
                # every genuine finalist and become "best" despite never
                # having been fully vetted. Caught empirically during v6's
                # own smoke test: a non-finalist became gen_best with
                # baseline_mean=0.0, and Level-B verification correctly
                # flagged it POSSIBLE_OVERFIT (gap > 13,000) -- this fix
                # addresses the root cause the verification step was
                # papering over.
                gen_best_idx = max(diag["finalists"], key=lambda i: result_fitnesses[i])
                gen_best_fitness = result_fitnesses[gen_best_idx]
                fitness_history.append(gen_best_fitness)

                new_record = gen_best_fitness > best_opt_fitness
                if new_record:
                    best_opt_fitness = gen_best_fitness
                    best_opt_params = solutions_real[gen_best_idx]
                    best_opt_score = final_scores[gen_best_idx]
                if gen_best_fitness > leg_best_fitness:
                    leg_best_fitness = gen_best_fitness
                    leg_best_params = solutions_real[gen_best_idx]
                best_fitness_history.append(best_opt_fitness)
                leg_best_history.append(best_opt_fitness)
                leg_bests_norm.append(_to_normalized(best_opt_params))

                s = final_scores[gen_best_idx]
                rho = diag["stage_a_vs_final_rho"]
                print(f"[gen {generation}] popsize={len(solutions_real)} games={diag['n_games']} "
                      f"elapsed={diag['elapsed']:.1f}s  gen_best={gen_best_fitness:.1f}  "
                      f"overall_best={best_opt_fitness:.1f} (diverse_mean={s['diverse_mean']:.1f} "
                      f"diverse_std={s['diverse_std']:.1f} baseline_mean={s['baseline_mean']:.1f} "
                      f"terminal_mean={s['terminal_mean']:.1f} n_finalist_games={s['n_diverse_games']}) "
                      f"finalists={len(diag['finalists'])} "
                      f"stage_a_vs_final_rho={'n/a' if rho is None else f'{rho:.2f}'}")
                # diag["solutions_norm"] is always full 60-dim (expanded
                # inside _run_generation_racing via _FakeES.ask()), so this
                # must index against the FULL name list, not the reduced
                # per-stage `active_names` -- else a --staged-params run
                # indexes stds computed over 60 dims with a short name list.
                _log_param_diversity(diag["solutions_norm"], tuning_spec.NAMES)

                # Level B: verify only when a new optimization-level record
                # is set -- re-check on FRESH, disjoint seeds before it's
                # allowed to become the checkpoint's "verified" candidate.
                if new_record:
                    v = verify_candidate(pool, best_opt_params, args.verification_seeds,
                                          args.verification_baseline_games, args.baseline_tolerance,
                                          args.baseline_weight)
                    print(f"  [verify] fresh-seed check: fitness={v['fitness']:.1f} "
                          f"diverse_mean={v['diverse_mean']:.1f} baseline_mean={v['baseline_mean']:.1f} "
                          f"baseline_win_rate={v.get('baseline_win_rate')}")
                    gap = gen_best_fitness - v["fitness"]
                    if gap > 0.5 * max(1.0, abs(gen_best_fitness)):
                        print(f"  [verify] POSSIBLE_OVERFIT: optimization={gen_best_fitness:.1f} "
                              f"verification={v['fitness']:.1f} (gap={gap:.1f})")
                    if (best_verified_fitness is None or v["fitness"] > best_verified_fitness) and \
                            v["baseline_mean"] >= -args.baseline_tolerance:
                        best_verified_fitness = v["fitness"]
                        best_verified_params = best_opt_params
                        best_verified_score = v
                        print(f"  [verify] new best_verified_fitness={best_verified_fitness:.1f}")

                if args.sensitivity_every and generation % args.sensitivity_every == 0:
                    run_sensitivity_analysis(pool, best_opt_params, active_names)

                converged = (len(leg_best_history) >= STAGNATION_WINDOW and
                             best_opt_fitness - leg_best_history[-STAGNATION_WINDOW] < NOISE_FLOOR)

                save_checkpoint(args.checkpoint, _checkpoint_state(
                    es.sigma, converged and restarts_used >= args.max_restarts))

                if stage_order and gen_this_leg >= args.stage_generations and stage_index < len(stage_order) - 1:
                    print(f"  [staged-params] advancing from stage '{stage_order[stage_index]}' "
                          f"to '{stage_order[stage_index + 1]}'")
                    # Seed the next stage from THIS leg's own best (which may
                    # never have beaten the all-time global record) rather
                    # than best_opt_params -- else a stage that spent its
                    # whole budget improving the current-stage objective
                    # without ever setting a new global record would have
                    # that local improvement silently discarded at the
                    # stage boundary. best_opt_params/best_opt_fitness stay
                    # untouched here -- they remain the independent
                    # all-time record used for the checkpoint and the
                    # restart anchor.
                    x0_norm = _to_normalized(leg_best_params)
                    stage_index += 1
                    break  # rebuild es for the newly-widened active set
                if converged:
                    break

            if stage_order and stage_index < len(stage_order) - 1 and not converged:
                continue  # advancing stages, not a real restart

            if restarts_used >= args.max_restarts or gen_this_leg == 0:
                print(f"Converged (restarts_used={restarts_used}/{args.max_restarts}). Stopping.")
                break

            restarts_used += 1
            popsize = int(round(popsize * 2))
            global_best_norm = _to_normalized(best_verified_params or best_opt_params)
            # Same reasoning as gen_rng above: derive from the restart index
            # rather than a shared mutable stream, so restart #k's location
            # is reproducible on its own and unaffected by --resume.
            restart_rng = random.Random(f"{SEED_SELECTION_SEED}:restart:{restarts_used}")
            x0_norm = _restart_x0(restarts_used, global_best_norm, leg_bests_norm, restart_rng)
            sigma0 = RESTART_SIGMAS[min(restarts_used - 1, len(RESTART_SIGMAS) - 1)]
            leg_bests_norm = [x0_norm]
            print(f"--- Plateau hit: IPOP restart #{restarts_used}/{args.max_restarts}, "
                  f"popsize -> {popsize}, sigma -> {sigma0}, "
                  f"best_optimization_fitness={best_opt_fitness:.1f} ---")
    finally:
        pool.close()
        pool.join()

    print(f"\nFinal best OPTIMIZATION fitness: {best_opt_fitness:.1f}")
    if best_verified_fitness is not None:
        print(f"Final best VERIFIED fitness:     {best_verified_fitness:.1f} "
              f"(baseline_mean={best_verified_score.get('baseline_mean', 0.0):.1f}, "
              f"baseline_win_rate={best_verified_score.get('baseline_win_rate')})")
    else:
        print("No candidate ever passed Level-B verification.")
    print(f"Checkpoint: {args.checkpoint}")
    print("Materialize a candidate to run the Level-C promotion benchmark with:")
    print(f"  python3 build_agent.py --from-checkpoint {args.checkpoint} --out /tmp/candidate.py")
    print(f"  python3 evolve.py --promote /tmp/candidate.py --baseline main.py --promote-games 40")


if __name__ == "__main__":
    main()
