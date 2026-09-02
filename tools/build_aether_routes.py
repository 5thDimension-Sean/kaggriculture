"""Generate Aether's compact fixed-route library from public Kaggle replays.

The generated module is committed so the runtime never needs replay files.
Run this tool again after refreshing ``top-players-data/refreshed-consistent``.
"""

from __future__ import annotations

import argparse
import json
import os

from tools.route_mining import encode_actions, load_player_games, majority_vote_route


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "top-players-data", "refreshed-consistent")


def _consensus_actions(team: str, seat: int) -> tuple[list[dict], dict]:
    directory = os.path.join(CORPUS, team)
    games = load_player_games(directory)[seat]
    route, consistency, breakdown = majority_vote_route(games)
    if route is None:
        raise ValueError(f"need at least two {team} replays in seat {seat}")
    return route, {**breakdown, "overall_consistency": consistency}


def build_source() -> str:
    p0, p0_meta = _consensus_actions("MtN", 0)
    p1, p1_meta = _consensus_actions("MtN", 1)
    routes = {"MTN_REFRESHED_P0": p0, "MTN_REFRESHED_P1": p1}

    encoded = {name: encode_actions(actions) for name, actions in routes.items()}
    metadata = {
        "team": "MtN",
        "submission_id": 55947910,
        "seat0_source": "majority of refreshed MtN seat-0 public replays",
        "seat1_source": "majority of refreshed MtN seat-1 public replays",
        "seat0_consistency": p0_meta["overall_consistency"],
        "seat1_consistency": p1_meta["overall_consistency"],
        "seat0_episodes": p0_meta["episode_ids"],
        "seat1_episodes": p1_meta["episode_ids"],
        "steps": 719,
        "selection": "refreshed current-ladder consensus by seat",
        "execution": "fixed seat-matched consensus routes; no runtime branches",
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
