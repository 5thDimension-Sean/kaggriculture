"""test_build_agent.py -- real-game integration tests for build_agent.py's
candidate-construction guarantees. Unlike test_evolve.py (pure
orchestration-logic assertions, no real games -- see its own docstring),
these tests DO run short real kaggle_environments episodes: verifying "these
two code paths produce the same actions" or "this matches main.py exactly"
isn't possible any other way. Kept in a separate file so test_evolve.py
stays fast and dependency-light. Run with:

    python3 test_build_agent.py

Exits non-zero (and prints which test failed) on any failure.
"""

import os
import sys
import tempfile

import benchmark
import build_agent
import tuning_spec

_STEPS = 80  # short episode -- enough to exercise route + early market/overlay
             # decisions without paying for a full 720-step game per check.


def _run(name, fn):
    try:
        fn()
        print(f"  PASS  {name}")
        return True
    except AssertionError as e:
        print(f"  FAIL  {name}: {e}")
        return False
    except Exception as e:
        print(f"  ERROR {name}: {type(e).__name__}: {e}")
        return False


def _actions_for(agent_a, agent_b, seed):
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": _STEPS, "seed": seed}, debug=False)
    env.run([agent_a, agent_b])
    return [[p.action for p in step] for step in env.steps]


def test_validate_params_vector_rejects_bad_input():
    good = tuning_spec.default_vector()
    build_agent.validate_params_vector(good)  # must not raise

    too_short = good[:-1]
    try:
        build_agent.validate_params_vector(too_short)
        raise AssertionError("expected ValueError for a wrong-length vector")
    except ValueError:
        pass

    non_finite = list(good)
    non_finite[0] = float("nan")
    try:
        build_agent.validate_params_vector(non_finite)
        raise AssertionError("expected ValueError for a non-finite value")
    except ValueError:
        pass

    out_of_range = list(good)
    out_of_range[0] = tuning_spec.HIGHS[0] + 1000
    try:
        build_agent.validate_params_vector(out_of_range)
        raise AssertionError("expected ValueError for an out-of-range value")
    except ValueError:
        pass


def test_isolated_modules_do_not_share_overlays_state():
    m1 = build_agent._isolated_modules()
    m2 = build_agent._isolated_modules()
    assert m1.overlays is not m2.overlays, \
        "two isolated builds share the same overlays module object -- not isolated"
    m1.overlays._OPPONENT_TYPE[0] = "mutated_by_m1"
    assert m2.overlays._OPPONENT_TYPE[0] != "mutated_by_m1", \
        "mutating one candidate's overlays state leaked into another -- the exact " \
        "contamination bug this file exists to prevent"


def test_in_process_and_materialized_candidate_match():
    """make_agent() (in-process) and write_self_contained_candidate() (written
    to disk, loaded back via benchmark.load_agent() -- the same loader
    evolve.py uses for its baseline/opponents) must behave identically for
    the same params vector -- the "explicit test" this project's own history
    of in-process-vs-file-loaded divergence calls for."""
    vec = list(tuning_spec.default_vector())
    for name in ("weed_replay_steps", "town_demand_pulse_period", "demand_alpha"):
        i = tuning_spec.NAMES.index(name)
        vec[i] = (tuning_spec.LOWS[i] + tuning_spec.HIGHS[i]) / 2

    in_process_agent = build_agent.make_agent(vec)

    tmp_path = tempfile.mktemp(suffix=".py")
    try:
        build_agent.write_self_contained_candidate(vec, tmp_path)
        file_agent = benchmark.load_agent(tmp_path)

        for seed in (12345, 67890):
            actions_in_process = _actions_for(in_process_agent, benchmark.load_agent("main.py"), seed)
            actions_file = _actions_for(file_agent, benchmark.load_agent("main.py"), seed)
            assert actions_in_process == actions_file, \
                f"in-process and materialized candidate diverged at seed={seed}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_default_vector_matches_main_py():
    """module docstring's claim: default_vector() reproduces main.py's
    pre-CMA-ES-tuning behavior EXACTLY (every revived overlay off)."""
    default_agent = build_agent.make_agent(tuning_spec.default_vector())
    for seed in (111, 222):
        actions_default = _actions_for(default_agent, benchmark.load_agent("main.py"), seed)
        actions_plain = _actions_for(benchmark.load_agent("main.py"), benchmark.load_agent("main.py"), seed)
        assert actions_default == actions_plain, \
            f"default-vector candidate diverged from plain main.py at seed={seed}"


TESTS = [
    test_validate_params_vector_rejects_bad_input,
    test_isolated_modules_do_not_share_overlays_state,
    test_in_process_and_materialized_candidate_match,
    test_default_vector_matches_main_py,
]

if __name__ == "__main__":
    print(f"Running {len(TESTS)} tests...")
    results = [_run(t.__name__, t) for t in TESTS]
    passed = sum(results)
    print(f"\n{passed}/{len(results)} passed")
    if passed != len(results):
        sys.exit(1)
