"""make_submission.py -- Produce a SINGLE, self-contained submission .py by
inlining overlays.py's source into main.py, so the actual Kaggle artifact
never relies on `import overlays` finding a sibling file at grading time.

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
    python3 make_submission.py --out /tmp/submission_main.py
    tar czf submissions/submission_v6_7.tar.gz -C /tmp submission_main.py \\
        --transform 's/^submission_main.py$/main.py/'
"""

import argparse
import base64
import os
import sys
import zlib

_ROOT = os.path.dirname(os.path.abspath(__file__))
_IMPORT_LINE = "import overlays\n"


def build_merged_source(root=_ROOT):
    with open(os.path.join(root, "main.py")) as f:
        main_src = f.read()
    with open(os.path.join(root, "overlays.py")) as f:
        overlays_src = f.read()

    if main_src.count(_IMPORT_LINE) != 1:
        raise SystemExit(
            f"Expected exactly one '{_IMPORT_LINE.strip()}' line in main.py, "
            f"found {main_src.count(_IMPORT_LINE)} -- update make_submission.py"
        )

    encoded = base64.b85encode(zlib.compress(overlays_src.encode("utf-8"), level=9)).decode("ascii")
    inline = (
        "import base64 as _sub_b64, types as _sub_types, zlib as _sub_zlib\n"
        f"_OVERLAYS_SRC = _sub_zlib.decompress(_sub_b64.b85decode({encoded!r})).decode('utf-8')\n"
        "overlays = _sub_types.ModuleType('overlays')\n"
        "exec(compile(_OVERLAYS_SRC, 'overlays.py', 'exec'), overlays.__dict__)\n"
    )
    return main_src.replace(_IMPORT_LINE, inline, 1)


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
    ap.add_argument("--out", default="/tmp/submission_main.py")
    ap.add_argument("--skip-self-test", action="store_true")
    args = ap.parse_args()

    merged = build_merged_source()
    with open(args.out, "w") as f:
        f.write(merged)
    print(f"Wrote self-contained submission agent -> {args.out} ({len(merged)} bytes)")

    if not args.skip_self_test:
        self_test(args.out)


if __name__ == "__main__":
    main()
