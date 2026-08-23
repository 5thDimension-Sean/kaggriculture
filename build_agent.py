"""build_agent.py -- Compose main.py's route+core pipeline with overlays.py's
revived market-intelligence overlays, driven by a single params vector (see
tuning_spec.py). Two use modes, both resolving a params vector to
(base_params, overlay_params, fr_order) through the SAME primitive
(_resolve_candidate_config) so they can never silently diverge in how a
candidate gets configured:

  1. In-process (used by evolve.py's fitness evaluation): call
     make_agent(params_vector) to get a live agent(obs) callable in the
     current Python process.

  2. Materialize a standalone submission-safe candidate file:
     write_self_contained_candidate(params_vector, out_path).

Both modes build main.py + overlays.py as an ISOLATED, freshly-exec'd
types.ModuleType (via make_submission.build_merged_source()) rather than
real `import main`/`import overlays` statements. This matters, not just for
Kaggle submission safety (see make_submission.py's docstring), but for
CORRECTNESS of evolve.py's own fitness evaluation: a real `import overlays`
caches ONE singleton module in sys.modules, shared by EVERY agent in the
process that also does a real import of it -- including any opponent loaded
via benchmark.load_agent() with __file__ set (e.g. "main.py", used as
evolve.py's own dedicated baseline opponent!). That means a candidate built
via a real `import main`/`import overlays` was silently sharing mutable
per-seat state (overlays._OPPONENT_TYPE, _MIRROR_STATE, etc.) with its own
opponent whenever both were real-imported in the same worker process --
found 2026-08-22 by diffing a candidate's actions between this (old, buggy)
in-process path and the isolated file-based path for the exact same params
vector and seed: they diverged (an extra opportunistic SELL appeared in the
correctly-isolated version), traced to _OPPONENT_TYPE[1] being polluted by
the opponent's own self-classification calls bleeding into the candidate's
"isolated" module instance. Every prior evolve.py run (v1, v2) built
candidates this same buggy way, so their fitness numbers carried some
amount of this contamination too -- not re-litigated here, but v3 onward is
clean for the CANDIDATE side specifically. (benchmark.load_agent(), used to
load opponents/baseline, still does a real `import overlays` when the
loaded file contains one -- currently only main.py, the baseline, does; see
benchmark.py's own docstring for why that hasn't reproduced this bug in
practice and what would make it do so again.)

The default params vector (tuning_spec.default_vector()) is INTENDED to
reproduce main.py's pre-CMA-ES-tuning (6.5) behavior exactly -- every
revived overlay defaults OFF. That claim is only as good as its last actual
check; see test_build_agent.py's test_default_vector_matches_main_py for a
real-game regression test of it (and for a real-game check that this file's
two candidate-construction paths -- in-process vs. materialized-to-disk --
produce byte-identical actions for the same params vector). Only a
CMA-ES-discovered vector that wins a real benchmark should ever be promoted
into main.py itself.
"""

import itertools
import math
import os
import types

import tuning_spec

_MODULE_COUNTER = itertools.count()


def validate_params_vector(params_vector):
    """Guard against a corrupted or version-mismatched checkpoint producing
    a nonsense (or crashing) agent deep inside a worker process, far from
    wherever the bad vector actually originated. Checks length against the
    CURRENT tuning_spec.py (a stale checkpoint's vector should go through
    tuning_spec.remap_checkpoint_vector() first, not straight here), and
    that every value is finite and within its declared [low, high] range."""
    if len(params_vector) != tuning_spec.DIM:
        raise ValueError(
            f"params_vector has {len(params_vector)} entries, expected {tuning_spec.DIM} "
            f"(tuning_spec.NAMES/LOWS/HIGHS length) -- checkpoint from a different/older "
            f"tuning_spec.py? Remap it with tuning_spec.remap_checkpoint_vector() first."
        )
    for i, (value, lo, hi, name) in enumerate(
            zip(params_vector, tuning_spec.LOWS, tuning_spec.HIGHS, tuning_spec.NAMES)):
        if not math.isfinite(value):
            raise ValueError(f"params_vector[{i}] ({name}) is not finite: {value!r}")
        if not (lo <= value <= hi):
            raise ValueError(f"params_vector[{i}] ({name}) = {value} is outside its declared range [{lo}, {hi}]")


def _isolated_modules():
    """Fresh, mutually-isolated (main, overlays) MODULE pair -- a real
    types.ModuleType with normal module globals (__name__, __package__),
    not just a bare exec() namespace dict, so code relying on ordinary
    module identity/globals behaves the same as it would under a real
    import. Never registered in sys.modules (nothing needs to look it up
    there, and it doesn't need a meaningful/persistent name), so a plain
    incrementing counter is all __name__ needs -- it exists only for
    repr()/tracebacks.

    Isolation itself comes from make_submission.build_merged_source():
    the merged source it returns embeds a FRESH
    `overlays = types.ModuleType('overlays'); exec(overlays_src, overlays.__dict__)`
    construction directly in the text, so every exec() of it here builds a
    brand-new overlays module instance -- never a sys.modules singleton.
    That's what actually prevents two candidates built by this function
    (or one built here and main.py loaded elsewhere via a real
    `import overlays`, e.g. by benchmark.load_agent("main.py")) from
    sharing mutable overlays state like _OPPONENT_TYPE/_MIRROR_STATE (see
    this module's docstring for the bug that taught us that).

    Sets __file__ to main.py's real path -- a DELIBERATE compatibility
    shim, not incidental setup: it makes the merged candidate believe it
    was loaded from main.py itself, matching what Kaggle's real file-path
    loader (and anything in main.py that might do a filesystem-relative
    lookup off __file__) expects. Don't remove it as dead boilerplate."""
    import make_submission
    merged_src = make_submission.build_merged_source()
    module = types.ModuleType(f"_candidate_{next(_MODULE_COUNTER)}")
    module.__file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    module.__package__ = None
    exec(compile(merged_src, module.__file__, "exec"), module.__dict__)
    return module


def _resolve_candidate_config(params_vector):
    """The single primitive make_agent() (via _build_candidate_module) and
    write_self_contained_candidate() both call to turn a params vector into
    (base_params, overlay_params, fr_order) -- exactly once, exactly the
    same way. Both callers reuse this instead of each re-deriving the config
    independently, which is precisely the kind of divergence that let the
    in-process-vs-file-loaded discrepancy in this module's docstring go
    unnoticed for two whole evolve.py generations (v1, v2)."""
    validate_params_vector(params_vector)
    return tuning_spec.vector_to_params(params_vector)


def _build_candidate_module(params_vector):
    module = _isolated_modules()
    base_params, overlay_params, fr_order = _resolve_candidate_config(params_vector)
    module.configure_base(base_params)
    module._FR_ITEMS = fr_order
    module.overlays.configure(overlay_params)
    return module


def make_agent(params_vector):
    """Returns a live agent(obs) function combining main.py + overlays.py,
    configured with the given params vector, in a freshly-built isolated
    module (see _isolated_modules for why not a real import)."""
    return _build_candidate_module(params_vector).agent


def write_self_contained_candidate(params_vector, out_path):
    """Write a SINGLE self-contained .py -- no dependency on
    build_agent.py/main.py/overlays.py/tuning_spec.py being present
    alongside it -- the only form safe to actually submit to Kaggle (see
    make_submission.py's docstring). Computes (base_params, overlay_params,
    fr_order) via the exact same _resolve_candidate_config() call
    _build_candidate_module() uses for the in-process path, then appends
    them as a configure_base/overlays.configure override resolved to
    concrete literal dicts at build time -- so the written file needs no
    tuning_spec.py at runtime either, and (per test_build_agent.py) produces
    byte-identical actions to make_agent() for the same vector and seed."""
    import make_submission
    merged = make_submission.build_merged_source()
    base_params, overlay_params, fr_order = _resolve_candidate_config(params_vector)
    override = (
        "\n# --- CMA-ES candidate override (build_agent.write_self_contained_candidate) ---\n"
        f"configure_base({base_params!r})\n"
        f"_FR_ITEMS = {fr_order!r}\n"
        f"overlays.configure({overlay_params!r})\n"
    )
    with open(out_path, "w") as f:
        f.write(merged + override)
    return out_path


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-checkpoint", default=tuning_spec.CHECKPOINT_PATH_DEFAULT,
                     help="Read best params vector from this evolve.py checkpoint")
    ap.add_argument("--out", default="/tmp/candidate.py")
    ap.add_argument("--default", action="store_true", help="Use tuning_spec defaults instead")
    args = ap.parse_args()

    if args.default:
        vec = tuning_spec.default_vector()
        print("Using tuning_spec DEFAULTS (not a checkpoint candidate).")
    else:
        import json
        with open(args.from_checkpoint) as f:
            ckpt = json.load(f)
        # v6 checkpoints track a verified-on-fresh-seeds candidate separately
        # from the raw (noisier) optimization-loop best -- prefer it when
        # present (see evolve.py's module docstring on the three evaluation
        # tiers), and say explicitly which one is being materialized so a
        # promotion workflow can't accidentally ship an unverified
        # optimization-only candidate without realizing it.
        verified_vec = ckpt.get("best_verified_params")
        if verified_vec is not None:
            vec = verified_vec
            gen = ckpt.get("generation", "?")
            fit = ckpt.get("best_verified_fitness")
            fit_str = f"{fit:.1f}" if isinstance(fit, (int, float)) else "?"
            print(f"Using VERIFIED candidate (checkpoint generation {gen}, verified fitness {fit_str}).")
        else:
            vec = ckpt["best_params"]
            print("No verified candidate in this checkpoint yet -- "
                  "falling back to the raw optimization-loop best (NOT Level-B verified).")
        # Remap by name if the checkpoint predates a tuning_spec rename/
        # reshape (e.g. v5's shed_guard_threshold -> v6's
        # shed_guard_overflow_buffer) instead of trusting positional order.
        # tuning_spec.remap_checkpoint_vector() lives in tuning_spec.py, not
        # evolve.py, specifically so this script doesn't have to import the
        # optimizer module (which would trigger evolve.py's module-level
        # opponent-pool construction as a side effect of just building a
        # submission file) just to materialize a candidate.
        old_names = ckpt.get("param_names", tuning_spec.NAMES)
        if old_names != tuning_spec.NAMES:
            vec, _ = tuning_spec.remap_checkpoint_vector(old_names, vec)
    write_self_contained_candidate(vec, args.out)
    print(f"Wrote self-contained candidate -> {args.out}")
