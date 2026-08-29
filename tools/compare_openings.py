"""Inspect route divergence and recorded-opponent opening actions."""

import argparse
import json
import os


def _namespace(path):
    namespace = {"__file__": os.path.abspath(path)}
    with open(path, encoding="utf-8") as handle:
        exec(compile(handle.read(), path, "exec"), namespace)
    return namespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="main.py")
    parser.add_argument("--routes", nargs="+", required=True)
    parser.add_argument("--player-dir", required=True)
    parser.add_argument("--steps", type=int, default=8)
    args = parser.parse_args()

    base = _namespace(args.base)["_ACTIONS"]
    for path in args.routes:
        route = _namespace(path)["_ACTIONS"]
        divergence = next(
            (step for step, pair in enumerate(zip(base, route)) if pair[0] != pair[1]),
            None,
        )
        print(f"{path}: first route divergence={divergence}")
        for step in range(min(args.steps, len(route))):
            print(f"  {step:3d}: {route[step]}")

    manifest_path = os.path.join(args.player_dir, "manifest.json")
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    for entry in manifest:
        episode_path = os.path.join(
            args.player_dir, f"episode-{entry['episode_id']}-replay.json"
        )
        with open(episode_path, encoding="utf-8") as handle:
            episode = json.load(handle)
        seat = int(entry["seat"])
        actions = [(step[seat].get("action") or {}) for step in episode["steps"]]
        while actions and not any(actions[0].get(key) for key in ("farmer", "hands", "market")):
            actions.pop(0)
        print(f"episode-{entry['episode_id']} seat={seat}")
        for step, action in enumerate(actions[:args.steps]):
            print(f"  {step:3d}: {action}")


if __name__ == "__main__":
    main()
