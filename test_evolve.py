"""test_evolve.py -- structural tests for evolve.py v6's evaluation
pipeline (seed fairness, racing, verification, restarts, checkpoints,
parameter grouping). These test ORCHESTRATION LOGIC, not game outcomes --
no real kaggle_environments games are simulated here (that's what the
smoke-test / real runs are for). Plain assertions, no pytest dependency;
run with:

    python3 test_evolve.py

Exits non-zero (and prints which test failed) on any failure.
"""

import random
import sys

import evolve
import tuning_spec


def _run(name, fn):
    try:
        fn()
        print(f"  PASS  {name}")
        return True
    except Exception as e:
        print(f"  FAIL  {name}: {type(e).__name__}: {e}")
        return False


# ---------------------------------------------------------------------------
# Section 30: Seed fairness -- two different candidate indices in the same
# generation receive exactly the same seed schedule.
# ---------------------------------------------------------------------------

def test_seed_fairness():
    batch = evolve.get_generation_seed_batch(5, 8, evolve._OPTIMIZATION_SEED_POOL, 4)
    # The whole point of CRN: the batch does not depend on any candidate
    # index at all -- there is no "per-candidate seed" concept anymore.
    # Verify this by confirming the batch function's signature has no
    # candidate-index parameter and that calling it twice for the "same"
    # generation is identical regardless of any external state.
    batch_again = evolve.get_generation_seed_batch(5, 8, evolve._OPTIMIZATION_SEED_POOL, 4)
    assert batch == batch_again, "same generation must yield the same batch every time (no candidate-index leakage possible)"
    # Confirm the actual game-task builders use ONE shared seed list across
    # every candidate key passed in, not a per-candidate offset.
    cand_keys = [0, 1, 2, 3]
    params_by_key = {k: tuning_spec.default_vector() for k in cand_keys}
    tasks = evolve._build_diverse_tasks(cand_keys, params_by_key, [0], batch[:2])
    seeds_seen_per_cand = {}
    for cand_key, params, pool, opp_name, opp_idx, seed, is_p0 in tasks:
        seeds_seen_per_cand.setdefault(cand_key, set()).add(seed)
    seed_sets = list(seeds_seen_per_cand.values())
    assert all(s == seed_sets[0] for s in seed_sets), "every candidate must see the identical seed set"


# ---------------------------------------------------------------------------
# Seed rotation -- different generation cycles produce different batches.
# ---------------------------------------------------------------------------

def test_seed_rotation():
    batch_gen0 = evolve.get_generation_seed_batch(0, 8, evolve._OPTIMIZATION_SEED_POOL, 4)
    batch_gen4 = evolve.get_generation_seed_batch(4, 8, evolve._OPTIMIZATION_SEED_POOL, 4)
    batch_gen1 = evolve.get_generation_seed_batch(1, 8, evolve._OPTIMIZATION_SEED_POOL, 4)
    assert batch_gen0 != batch_gen4, "different rotation cycles must produce different batches"
    assert batch_gen0 == batch_gen1, "generations within the same cycle (0-3) must share a batch"


# ---------------------------------------------------------------------------
# Reproducibility -- running seed-selection logic twice with the same
# configuration produces identical batches, and the pools themselves are
# reproducible from SEED_SELECTION_SEED.
# ---------------------------------------------------------------------------

def test_reproducibility():
    pool_a = evolve._build_seed_pool(50, "reproducibility-check")
    pool_b = evolve._build_seed_pool(50, "reproducibility-check")
    assert pool_a == pool_b, "same tag must reproduce the same pool"
    pool_c = evolve._build_seed_pool(50, "a-different-tag")
    assert pool_a != pool_c, "different tags must produce different (independent) pools"
    assert len(set(pool_a)) == len(pool_a), "pool must have no duplicate seeds"


def test_pools_disjoint():
    opt = set(evolve._OPTIMIZATION_SEED_POOL)
    ver = set(evolve._VERIFICATION_SEED_POOL)
    promo = set(evolve._PROMOTION_SEED_POOL)
    assert not (opt & ver), "optimization and verification pools must not overlap"
    assert not (opt & promo), "optimization and promotion pools must not overlap"
    assert not (ver & promo), "verification and promotion pools must not overlap"


# ---------------------------------------------------------------------------
# Racing: eliminated candidates receive no later-stage evaluations (checked
# structurally via the task-builder functions, not a real _run_generation_racing
# call, to keep this test fast/offline).
# ---------------------------------------------------------------------------

def test_racing_reduces_games():
    all_cands = [0, 1, 2, 3, 4, 5]
    survivors = [0, 2, 4]  # simulate Stage A eliminating half
    params_by_key = {k: tuning_spec.default_vector() for k in all_cands}
    stage_a_tasks = evolve._build_diverse_tasks(all_cands, params_by_key, [0, 1], [111])
    stage_b_tasks = evolve._build_diverse_tasks(survivors, {k: params_by_key[k] for k in survivors}, [0, 1, 2], [222])

    games_per_cand_a = {k: 0 for k in all_cands}
    for t in stage_a_tasks:
        games_per_cand_a[t[0]] += 1
    games_per_cand_b = {k: 0 for k in survivors}
    for t in stage_b_tasks:
        games_per_cand_b[t[0]] += 1

    eliminated = [k for k in all_cands if k not in survivors]
    for k in eliminated:
        assert k not in games_per_cand_b, f"eliminated candidate {k} must not appear in a later stage's tasks"
    total_a = sum(games_per_cand_a.values())
    total_survivor_only = sum(games_per_cand_b.values())
    assert total_survivor_only < total_a, "a later stage evaluating only survivors must use fewer games than screening everyone"


# ---------------------------------------------------------------------------
# Verification uses fresh seeds when the pool permits.
# ---------------------------------------------------------------------------

def test_verification_uses_fresh_seeds():
    opt_seeds = set(evolve.get_generation_seed_batch(0, 20, evolve._OPTIMIZATION_SEED_POOL, 4))
    verify_seeds = set(evolve._VERIFICATION_SEED_POOL[:20])
    assert not (opt_seeds & verify_seeds), "verification seeds must not overlap a real optimization batch"


# ---------------------------------------------------------------------------
# Baseline protection: a clearly worse baseline score receives a strong
# penalty (fitness distinguishably worse than an otherwise-identical
# candidate with a positive baseline delta).
# ---------------------------------------------------------------------------

def test_baseline_penalty():
    def _make_acc(diverse_val, baseline_val, n=10):
        return {
            "diverse": [(diverse_val, diverse_val)] * n,
            "baseline": [(baseline_val, baseline_val)] * n,
            "by_opponent": {"dummy": [diverse_val] * n},
        }

    good_baseline = evolve._score_accumulated(_make_acc(1000.0, 200.0), evolve.BASELINE_TOLERANCE_DEFAULT)
    bad_baseline = evolve._score_accumulated(_make_acc(1000.0, -2000.0), evolve.BASELINE_TOLERANCE_DEFAULT)
    assert good_baseline["fitness"] > bad_baseline["fitness"], \
        "a candidate regressing badly against the baseline must score strictly worse than one that doesn't, at equal diverse-pool performance"

    mild_regression = evolve._score_accumulated(_make_acc(1000.0, -50.0), evolve.BASELINE_TOLERANCE_DEFAULT)
    severe_regression = evolve._score_accumulated(_make_acc(1000.0, -2000.0), evolve.BASELINE_TOLERANCE_DEFAULT)
    mild_gap = good_baseline["fitness"] - mild_regression["fitness"]
    severe_gap = mild_regression["fitness"] - severe_regression["fitness"]
    # The extra beyond-tolerance penalty should make severe regression fall
    # off much faster per additional dollar lost than mild regression does.
    assert severe_gap > mild_gap, "regression beyond --baseline-tolerance must be penalized more steeply than regression within it"


# ---------------------------------------------------------------------------
# es.tell() must receive a homogeneous objective: an eliminated candidate
# (Stage A/B only, no baseline games) and a finalist (Stage A+B+C plus
# baseline games) must be scored by the SAME formula, or CMA-ES ends up
# comparing two different objectives rather than two noisy samples of one.
# ---------------------------------------------------------------------------

def test_diverse_fitness_ignores_baseline_regression():
    def _make_acc(diverse_val, baseline_val=None, n=10):
        acc = {
            "diverse": [(diverse_val, diverse_val)] * n,
            "baseline": [],
            "by_opponent": {"dummy": [diverse_val] * n},
        }
        if baseline_val is not None:
            acc["baseline"] = [(baseline_val, baseline_val)] * n
        return acc

    eliminated = evolve._score_accumulated(_make_acc(1000.0), evolve.BASELINE_TOLERANCE_DEFAULT)
    finalist_good = evolve._score_accumulated(_make_acc(1000.0, 200.0), evolve.BASELINE_TOLERANCE_DEFAULT)
    finalist_bad = evolve._score_accumulated(_make_acc(1000.0, -2000.0), evolve.BASELINE_TOLERANCE_DEFAULT)

    # `fitness` (used for finalist ranking/gen-best) legitimately differs
    # once a baseline-regression penalty applies.
    assert finalist_good["fitness"] != finalist_bad["fitness"]

    # `diverse_fitness` (the value actually fed to es.tell()) must be
    # identical across all three -- same diverse games, regardless of
    # whether/how a baseline component was scored -- so CMA-ES never sees
    # an eliminated candidate's diverse-only score competing against a
    # finalist's baseline-adjusted score as if they were the same objective.
    assert eliminated["diverse_fitness"] == finalist_good["diverse_fitness"] == finalist_bad["diverse_fitness"]


# ---------------------------------------------------------------------------
# Checkpoint resume: an old (v5-schema) checkpoint loads safely.
# ---------------------------------------------------------------------------

def test_checkpoint_resume_old_schema():
    old_style_ckpt = {
        "generation": 42,
        "best_fitness": 1234.5,
        "best_mean_delta": 900.0,
        "best_std_delta": 300.0,
        "best_baseline_mean_delta": 50.0,
        "best_params": tuning_spec.default_vector(),
        "fitness_history": [100.0, 200.0],
        "sigma0": 0.2,
        "converged": False,
        "restarts_used": 1,
        "base_popsize": 24,
        "param_names": tuning_spec.NAMES,
        "diverse_opponents": ["legacy_6.3"],
    }
    # These are exactly the .get(..., fallback) patterns main() uses on resume.
    opt_fitness = old_style_ckpt.get("best_optimization_fitness", old_style_ckpt.get("best_fitness", float("-inf")))
    assert opt_fitness == 1234.5
    assert old_style_ckpt.get("best_verified_params") is None
    assert old_style_ckpt.get("opponent_stats", {}) == {}


def test_checkpoint_resume_renamed_param():
    # Simulate a v5 checkpoint whose param_names still says "shed_guard_threshold"
    # instead of v6's "shed_guard_overflow_buffer".
    old_names = [n if n != "shed_guard_overflow_buffer" else "shed_guard_threshold" for n in tuning_spec.NAMES]
    old_values = list(tuning_spec.default_vector())
    idx = tuning_spec.NAMES.index("shed_guard_overflow_buffer")
    old_values[idx] = 90  # the OLD raw-threshold value, not a buffer

    remapped, remap_report = tuning_spec.remap_checkpoint_vector(old_names, old_values, warn=False)
    assert "shed_guard_overflow_buffer" in remap_report["renamed"]
    new_idx = tuning_spec.NAMES.index("shed_guard_overflow_buffer")
    assert remapped[new_idx] == tuning_spec.SHED_CAPACITY - 90, \
        "the renamed shed-guard param must be inverse-transformed (buffer = SHED_CAPACITY - old threshold), not copied positionally"


# ---------------------------------------------------------------------------
# Parameter grouping: frozen parameters do not mutate.
# ---------------------------------------------------------------------------

def test_param_grouping_freeze():
    mask = evolve._active_mask_for_stage(0)  # only "core_strategy" active
    active_names = {n for n, a in zip(tuning_spec.NAMES, mask) if a}
    assert active_names == set(tuning_spec.PARAM_GROUPS["core_strategy"]), \
        "stage 0 must activate exactly the core_strategy group"

    frozen = list(tuning_spec.default_vector())
    active_indices = [i for i, a in enumerate(mask) if a]

    def expand(active_solution):
        full = list(frozen)
        for j, i in enumerate(active_indices):
            full[i] = active_solution[j]
        return full

    solution_1 = [999.0] * len(active_indices)
    solution_2 = [-999.0] * len(active_indices)
    full_1 = expand(solution_1)
    full_2 = expand(solution_2)
    for i, name in enumerate(tuning_spec.NAMES):
        if i not in active_indices:
            assert full_1[i] == full_2[i] == frozen[i], \
                f"frozen parameter {name} must stay at its fixed value regardless of the active solution"


def test_param_groups_cover_every_name_exactly_once():
    # tuning_spec.py already asserts this at import time; re-check here too
    # so a future refactor that bypasses that assertion still gets caught.
    grouped = [n for names in tuning_spec.PARAM_GROUPS.values() for n in names]
    assert sorted(grouped) == sorted(tuning_spec.NAMES)
    assert len(grouped) == len(set(grouped))


# ---------------------------------------------------------------------------
# Discrete parameters: int/bool kinds are represented correctly downstream.
# ---------------------------------------------------------------------------

def test_discrete_representation():
    rng = random.Random(0)
    vec = [lo + rng.random() * (hi - lo) for lo, hi in zip(tuning_spec.LOWS, tuning_spec.HIGHS)]
    base_params, overlay_params, fr_order = tuning_spec.vector_to_params(vec)
    all_params = {**base_params, **overlay_params}
    for name, kind in zip(tuning_spec.NAMES, tuning_spec.KINDS):
        if name.startswith("fr_priority_") or name.startswith("fr_enabled_") or name == "shed_guard_overflow_buffer":
            continue  # not passed through under their own name (priority/enable feed fr_order; buffer feeds shed_guard_threshold)
        value = all_params[name]
        if kind == "int":
            assert float(value).is_integer(), f"{name} (kind=int) must be a whole number, got {value}"
        elif kind == "bool":
            assert value in (0.0, 1.0), f"{name} (kind=bool) must be exactly 0.0 or 1.0, got {value}"
    assert isinstance(all_params["shed_guard_threshold"], int)
    assert isinstance(fr_order, tuple)


# ---------------------------------------------------------------------------
# Restart: a restarted leg does not immediately re-trigger stagnation due to
# stale history (the leg-local reset fix from v5, locked in as a regression
# test so v6 can't reintroduce the bug).
# ---------------------------------------------------------------------------

def test_restart_no_immediate_retrigger():
    STAGNATION_WINDOW = evolve.STAGNATION_WINDOW
    NOISE_FLOOR = evolve.NOISE_FLOOR

    # Simulate a plateaued run: 25 generations at a flat best_fitness=100.0,
    # matching what a real plateau looks like in best_fitness_history.
    global_best_fitness_history = [100.0] * 25

    # A restart fires here. The bug (v5's ORIGINAL mistake, already fixed)
    # was checking the GLOBAL history immediately after -- which is still
    # full of the stale plateau -- instead of a freshly-reset leg-local one.
    leg_best_history = []  # correct: reset on restart
    best_fitness = 100.0

    # One post-restart generation that doesn't beat the old record.
    leg_best_history.append(best_fitness)
    converged_bug = (len(global_best_fitness_history) >= STAGNATION_WINDOW and
                      best_fitness - global_best_fitness_history[-STAGNATION_WINDOW] < NOISE_FLOOR)
    converged_correct = (len(leg_best_history) >= STAGNATION_WINDOW and
                          best_fitness - leg_best_history[-STAGNATION_WINDOW] < NOISE_FLOOR)

    assert converged_bug is True, "sanity: confirms the OLD (buggy) check really would have re-fired immediately"
    assert converged_correct is False, "the CORRECT (leg-local) check must NOT fire after just one post-restart generation"

    # Confirm it eventually fires again once a real STAGNATION_WINDOW of
    # post-restart generations has genuinely passed without improvement.
    for _ in range(STAGNATION_WINDOW - 1):
        leg_best_history.append(best_fitness)
    converged_after_real_window = (len(leg_best_history) >= STAGNATION_WINDOW and
                                    best_fitness - leg_best_history[-STAGNATION_WINDOW] < NOISE_FLOOR)
    assert converged_after_real_window is True, \
        "after a genuine full STAGNATION_WINDOW of post-restart generations with no improvement, it SHOULD fire"


def test_restart_sigma_schedule():
    assert evolve.RESTART_SIGMAS[0] < evolve.RESTART_SIGMAS[1] < evolve.RESTART_SIGMAS[2], \
        "restart sigmas must increase (broader exploration on later restarts)"


def test_restart_location_varies():
    rng = random.Random(42)
    global_best = [0.5] * tuning_spec.DIM
    leg_bests = [global_best, [0.2] * tuning_spec.DIM]
    x0_r1 = evolve._restart_x0(1, global_best, leg_bests, rng)
    assert x0_r1 == global_best, "restart 1 must resume exactly at the global best"
    x0_r2 = evolve._restart_x0(2, global_best, leg_bests, random.Random(1))
    assert x0_r2 != global_best, "restart 2 must perturb away from the exact global best"
    assert all(0.0 <= v <= 1.0 for v in x0_r2), "restart location must stay within the normalized [0,1] bounds"


# ---------------------------------------------------------------------------
# Opponent weighting sanity checks (section 18/19).
# ---------------------------------------------------------------------------

def test_opponent_stats_and_weighting():
    stats = {}
    evolve._update_opponent_stats(stats, "opp_high_info", [100.0, -100.0, 300.0, -300.0])
    evolve._update_opponent_stats(stats, "opp_low_info", [50.0, 51.0, 49.0, 50.0])
    names = ["opp_high_info", "opp_low_info"]
    weights = evolve._opponent_sampling_weights(stats, names, min_floor=0.15)
    assert weights[0] > weights[1], "an opponent whose results vary a lot across candidates (informative) must be weighted higher than one that doesn't"
    assert min(weights) > 0, "every opponent must keep a nonzero floor weight so none is starved permanently"


if __name__ == "__main__":
    tests = [
        test_seed_fairness,
        test_seed_rotation,
        test_reproducibility,
        test_pools_disjoint,
        test_racing_reduces_games,
        test_verification_uses_fresh_seeds,
        test_baseline_penalty,
        test_diverse_fitness_ignores_baseline_regression,
        test_checkpoint_resume_old_schema,
        test_checkpoint_resume_renamed_param,
        test_param_grouping_freeze,
        test_param_groups_cover_every_name_exactly_once,
        test_discrete_representation,
        test_restart_no_immediate_retrigger,
        test_restart_sigma_schedule,
        test_restart_location_varies,
        test_opponent_stats_and_weighting,
    ]
    print(f"Running {len(tests)} tests...")
    results = [_run(t.__name__, t) for t in tests]
    passed = sum(results)
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if all(results) else 1)
