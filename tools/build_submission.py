"""Build and verify Aether's single-file Kaggle submission."""

import argparse
import base64
import os
import zlib


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPORT_LINE = "import aether_routes\n"


def build_merged_source(root=ROOT, main_path=None):
    main_path = main_path or os.path.join(root, "main.py")
    with open(main_path, encoding="utf-8") as handle:
        main_source = handle.read()
    with open(os.path.join(root, "aether_routes.py"), encoding="utf-8") as handle:
        routes_source = handle.read()
    if main_source.count(IMPORT_LINE) != 1:
        raise SystemExit(
            f"Expected one {IMPORT_LINE.strip()!r} import, found "
            f"{main_source.count(IMPORT_LINE)}"
        )
    encoded = base64.b85encode(
        zlib.compress(routes_source.encode("utf-8"), level=9)
    ).decode("ascii")
    inline = (
        "import base64 as _sub_b64, types as _sub_types, zlib as _sub_zlib\n"
        f"_ROUTES_SOURCE = _sub_zlib.decompress(_sub_b64.b85decode({encoded!r})).decode('utf-8')\n"
        "aether_routes = _sub_types.ModuleType('aether_routes')\n"
        "exec(compile(_ROUTES_SOURCE, 'aether_routes.py', 'exec'), aether_routes.__dict__)\n"
    )
    return main_source.replace(IMPORT_LINE, inline, 1)


def self_test(out_path):
    """Exercise Kaggle Environments' real file-path loading harness."""
    from kaggle_environments import make

    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 96, "seed": 1},
        debug=True,
    )
    env.run([out_path, out_path])
    for index, step in enumerate(env.steps):
        for player in step:
            if player.status not in ("ACTIVE", "DONE"):
                raise SystemExit(
                    f"Self-test failed at step {index}: status={player.status}"
                )
    print("Self-test OK: file-path loader completed 96 steps.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out", default=os.path.join(ROOT, "artifacts", "submission", "main.py")
    )
    parser.add_argument("--skip-self-test", action="store_true")
    args = parser.parse_args()
    merged = build_merged_source()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(merged)
    print(f"Wrote {args.out} ({len(merged):,} bytes)")
    if not args.skip_self_test:
        self_test(args.out)


if __name__ == "__main__":
    main()
