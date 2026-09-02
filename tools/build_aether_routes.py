"""Generate Aether's compact fixed-route library from public Kaggle replays.

The generated module is committed so the runtime never needs replay files.
Each seat is copied from one complete observed episode; actions are never
spliced across games.
"""

from __future__ import annotations

import argparse
import os

from tools.route_mining import encode_actions, load_player_games


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONSISTENT_CORPUS = os.path.join(ROOT, "top-players-data", "refreshed-consistent")
CLIMBER_CORPUS = os.path.join(ROOT, "top-players-data", "refreshed-climbers")
SEAT0_EPISODE = 104686146
SEAT1_EPISODE = 104683334


def _episode_actions(directory: str, seat: int, episode_id: int) -> list[dict]:
    games = load_player_games(directory)[seat]
    for game in games:
        if int(game["episode_id"]) == episode_id:
            return game["actions"]
    raise ValueError(f"episode {episode_id} was not found in {directory} seat {seat}")


def build_source() -> str:
    p0 = _episode_actions(
        os.path.join(CLIMBER_CORPUS, "RngRng"), 0, SEAT0_EPISODE
    )
    p1 = _episode_actions(
        os.path.join(CONSISTENT_CORPUS, "MtN"), 1, SEAT1_EPISODE
    )
    routes = {"RNGRNG_P0": p0, "MTN_P1": p1}

    encoded = {name: encode_actions(actions) for name, actions in routes.items()}
    metadata = {
        "seat0_team": "RngRng",
        "seat1_team": "MtN",
        "seat0_submission_id": 55948382,
        "seat1_submission_id": 55947910,
        "seat0_source": f"exact RngRng public episode {SEAT0_EPISODE}, seat 0",
        "seat1_source": f"exact MtN public episode {SEAT1_EPISODE}, seat 1",
        "seat0_episode": SEAT0_EPISODE,
        "seat1_episode": SEAT1_EPISODE,
        "steps": 719,
        "selection": "coherent whole-route selection by seat",
        "execution": "fixed exact episode routes; no runtime branches or voting",
    }
    lines = [
        '"""Generated compact public-replay routes for Aether 1.0."""',
        "import base64",
        "import json",
        "import zlib",
        "",
        f"METADATA = {metadata!r}",
        "",
        "def _decode(payload):",
        "    return json.loads(zlib.decompress(base64.b85decode(payload)).decode('utf-8'))",
        "",
    ]
    for name, payload in encoded.items():
        lines.append(f"{name} = _decode({payload!r})")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(ROOT, "aether_routes.py"))
    args = parser.parse_args()
    source = build_source()
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(source)
    print(f"Wrote {args.out} ({len(source):,} bytes)")


if __name__ == "__main__":
    main()
