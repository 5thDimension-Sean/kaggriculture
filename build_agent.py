"""build_agent.py -- Compose main.py's route+core pipeline with overlays.py's
revived market-intelligence overlays, driven by a single params vector (see
tuning_spec.py). Two use modes:

  1. In-process (used by evolve.py's fitness evaluation): call
     make_agent(params_vector) to get a live agent(obs) callable in the
     current Python process.

  2. Materialize a standalone submission-safe candidate file:
     write_self_contained_candidate(params_vector, out_path).

Both modes build main.py + overlays.py as ISOLATED, freshly-exec'd modules
(via make_submission.build_merged_source(), types.ModuleType) rather than
real `import main`/`import overlays` statements. This matters, not just for
Kaggle submission safety (see make_submission.py's docstring), but for
CORRECTNESS of evolve.py's own fitness evaluation: a real `import overlays`
caches ONE singleton module in sys.modules, shared by EVERY agent in the
process that also does a real import of it -- including any opponent loaded
via benchmark.load_agent() with __file__ set (e.g. "main.py", used as
evolve.py v3's own dedicated baseline opponent!). That means a candidate
built via a real `import main`/`import overlays` was silently sharing
mutable per-seat state (overlays._OPPONENT_TYPE, _MIRROR_STATE, etc.) with
its own opponent whenever both were real-imported in the same worker
process -- found 2026-08-22 by diffing a candidate's actions between this
(old, buggy) in-process path and the isolated file-based path for the exact
same params vector and seed: they diverged (an extra opportunistic SELL
appeared in the correctly-isolated version), traced to
_OPPONENT_TYPE[1] being polluted by the opponent's own self-classification
calls bleeding into the candidate's "isolated" module instance. Every prior
evolve.py run (v1, v2) built candidates this same buggy way, so their
fitness numbers carried some amount of this contamination too -- not
re-litigated here, but v3 onward is clean.

The default params vector (tuning_spec.default_vector()) reproduces main.py's
pre-CMA-ES-tuning (6.5) behavior exactly -- every revived overlay defaults
OFF. Only a CMA-ES-discovered vector that wins a real benchmark should ever
be promoted into main.py itself.
"""

import os

import tuning_spec


def _isolated_modules():
    """Fresh, mutually-isolated (main, overlays) module pair -- no
    sys.modules caching, so no possibility of sharing state with any other
    agent instance in the same process (see module docstring)."""
    import make_submission
    merged_src = make_submission.build_merged_source()
    ns = {"__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")}
    exec(compile(merged_src, "main.py", "exec"), ns)
    return ns


def make_agent(params_vector):
    """Returns a live agent(obs) function combining main.py + overlays.py,
    configured with the given params vector, in a freshly-built isolated
    module pair (see module docstring for why not a real import)."""
    ns = _isolated_modules()
    base_params, overlay_params, fr_order = tuning_spec.vector_to_params(params_vector)
    ns["configure_base"](base_params)
    ns["_FR_ITEMS"] = fr_order
    ns["overlays"].configure(overlay_params)
    return ns["agent"]


def write_self_contained_candidate(params_vector, out_path):
    """Write a SINGLE self-contained .py -- no dependency on
    build_agent.py/main.py/overlays.py/tuning_spec.py being present
    alongside it -- the only form safe to actually submit to Kaggle (see
    make_submission.py's docstring). Reuses make_submission.build_merged_source()
    and appends the CMA-ES-searched params as a configure_base/
    overlays.configure override, resolved to concrete literal dicts at build
    time via tuning_spec.vector_to_params -- so the written file needs no
    tuning_spec.py at runtime either."""
    import make_submission
    merged = make_submission.build_merged_source()
    base_params, overlay_params, fr_order = tuning_spec.vector_to_params(params_vector)
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
    ap.add_argument("--from-checkpoint", default="evolve_checkpoint.json",
                     help="Read best params vector from this evolve.py checkpoint")
    ap.add_argument("--out", default="/tmp/candidate.py")
    ap.add_argument("--default", action="store_true", help="Use tuning_spec defaults instead")
    args = ap.parse_args()

    if args.default:
        vec = tuning_spec.default_vector()
    else:
        import json
        with open(args.from_checkpoint) as f:
            ckpt = json.load(f)
        vec = ckpt["best_params"]
    write_self_contained_candidate(vec, args.out)
    print(f"Wrote self-contained candidate -> {args.out}")
