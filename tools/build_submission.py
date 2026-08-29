"""Build a single-file MapleLeaf submission and exercise Kaggle's loader.

``main.py`` imports ``heuristics.py`` for readable local development. The
submitted artifact embeds that module in memory, so Kaggle only needs one
root-level ``main.py`` and the grading sandbox never has to resolve siblings.

Why this exists (2026-08-22): MapleLeaf 6.6 was the first version to split
logic across two files (main.py + overlays.py, joined by `import overlays`).
Both 6.6 (which also had an unrelated live-engine-import bug) AND 6.7 (that
bug fixed, but still two files) came back Kaggle SubmissionStatus.ERROR /
"Validation Episode failed" -- every single-file version before that
(6.5 and earlier) validated fine. `kaggle_environments`' own local agent
loader (agent.py's get_last_callable) does append the executed file's
directory to sys.path, so a sibling import works fine in local dev/benchmark
runs -- but Kaggle's actual competition grading infrastructure evidently
does not preserve/mount sibling files the same way. The fix: never rely on
that at submission time. This script builds a merged file that constructs
overlays as an in-memory module (via `types.ModuleType` + `exec`, avoiding
the top-level name collisions between main.py and overlays.py -- e.g. both
define `_get`/`_farm`/`_seat`/`_copy_action`/`_SHOP_PRODUCTS` -- a flat
textual merge would silently clobber these) instead of importing a second
file. main.py/overlays.py themselves are UNCHANGED and keep working exactly
as before for local dev, evolve.py, build_agent.py, benchmark.py, etc. --
this script only affects what gets packaged for the actual Kaggle upload.

Usage:
    python -m tools.build_submission --out artifacts/submission/main.py
"""

import argparse
import base64
import os
import sys
import zlib

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_IMPORT_LINE = "import heuristics\n"
_ANTI_IMPORT_LINE = "import anti_route\n"


def build_merged_source(root=_ROOT, main_path=None):
    main_path = main_path or os.path.join(root, "main.py")
    with open(main_path) as f:
        main_src = f.read()
    with open(os.path.join(root, "heuristics.py")) as f:
        heuristics_src = f.read()
    with open(os.path.join(root, "anti_route.py")) as f:
        anti_route_src = f.read()

    if main_src.count(_IMPORT_LINE) != 1:
        raise SystemExit(
            f"Expected exactly one '{_IMPORT_LINE.strip()}' line in main.py, "
            f"found {main_src.count(_IMPORT_LINE)} -- update tools/build_submission.py"
        )
    if main_src.count(_ANTI_IMPORT_LINE) > 1:
        raise SystemExit(
            f"Expected at most one '{_ANTI_IMPORT_LINE.strip()}' line in main.py, "
            f"found {main_src.count(_ANTI_IMPORT_LINE)} -- update tools/build_submission.py"
        )

    encoded = base64.b85encode(zlib.compress(heuristics_src.encode("utf-8"), level=9)).decode("ascii")
    inline = (
        "import base64 as _sub_b64, types as _sub_types, zlib as _sub_zlib\n"
        f"_HEURISTICS_SRC = _sub_zlib.decompress(_sub_b64.b85decode({encoded!r})).decode('utf-8')\n"
        "heuristics = _sub_types.ModuleType('heuristics')\n"
        "exec(compile(_HEURISTICS_SRC, 'heuristics.py', 'exec'), heuristics.__dict__)\n"
    )
    anti_encoded = base64.b85encode(
        zlib.compress(anti_route_src.encode("utf-8"), level=9)
    ).decode("ascii")
    anti_inline = (
        f"_ANTI_ROUTE_SRC = _sub_zlib.decompress(_sub_b64.b85decode({anti_encoded!r})).decode('utf-8')\n"
        "anti_route = _sub_types.ModuleType('anti_route')\n"
        "exec(compile(_ANTI_ROUTE_SRC, 'anti_route.py', 'exec'), anti_route.__dict__)\n"
    )
    merged = main_src.replace(_IMPORT_LINE, inline, 1)
    if _ANTI_IMPORT_LINE in merged:
        merged = merged.replace(_ANTI_IMPORT_LINE, anti_inline, 1)
    return merged


def self_test(out_path):
    """Exercise the REAL Kaggle file-PATH loading harness (get_last_callable,
    which execs the file's source into a bare `{}` globals dict -- no
    __file__ key at all -- plus argcount-based invocation), not a direct
    exec or passing an already-imported function object to env.run().

    This distinction matters: 6.6/6.7's first THREE submission attempts all
    passed every local test this project had (direct exec, cold-sandbox
    exec, passing the loaded function object to env.run()) yet still came
    back Kaggle SubmissionStatus.ERROR / "Validation Episode failed". The
    real bug (a bare `sys.path.insert(0, os.path.dirname(os.path.abspath(
    __file__)))` at module scope, which NameErrors when __file__ isn't
    defined) only reproduces when the agent is loaded BY FILE PATH, exactly
    like `env.run(["main.py", "main.py"])` -- never when a pre-loaded
    function object is passed directly. Always test this way before ever
    trusting a submission artifact again."""
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 20, "seed": 1}, debug=True)
    env.run([out_path, out_path])
    for i, step in enumerate(env.steps):
        for p in step:
            if p.status not in ("ACTIVE", "DONE"):
                raise SystemExit(f"Self-test FAILED at step {i}: status={p.status}")
    print("Self-test OK: loaded and ran via the real file-path harness (matches Kaggle's actual loading mechanism), all steps ACTIVE/DONE.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(_ROOT, "artifacts", "submission", "main.py"))
    ap.add_argument("--skip-self-test", action="store_true")
    args = ap.parse_args()

    merged = build_merged_source()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(merged)
    print(f"Wrote self-contained submission agent -> {args.out} ({len(merged)} bytes)")

    if not args.skip_self_test:
        self_test(args.out)


if __name__ == "__main__":
    main()
