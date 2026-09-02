"""Generate Aether's compact fixed-route library from a public Kaggle replay.

The generated module is committed so the runtime never needs replay files.
Run this tool again after refreshing ``top-players-data/number1-audit``.
"""

from __future__ import annotations

import argparse
import json
import os

from tools.route_mining import encode_actions, load_player_games


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "top-players-data", "number1-audit")


def _route_distance(left: list[dict], right: list[dict]) -> int:
    """Action-channel Hamming distance used by the public route audits."""
    steps = min(len(left), len(right))
    return sum(
        left[step][channel] != right[step][channel]
        for step in range(steps)
        for channel in ("farmer", "hands", "market")
    ) + 3 * abs(len(left) - len(right))


def _seat_medoid(team: str, seat: int) -> tuple[list[dict], int, int, int]:
    games = load_player_games(os.path.join(CORPUS, team))[seat]
    if not games:
        raise ValueError(f"no {team} seat-{seat} games in {CORPUS}")
    ranked = []
    for candidate in games:
        distance = sum(
            _route_distance(candidate["actions"], other["actions"])
            for other in games
            if other is not candidate
        )
        ranked.append((distance, int(candidate["episode_id"]), candidate["actions"]))
    distance, episode_id, actions = min(ranked, key=lambda row: (row[0], row[1]))
    return actions, episode_id, distance, len(games)


def build_source() -> str:
    p0, p0_episode, p0_distance, p0_games = _seat_medoid("tetsuya", 0)
    p1, p1_episode, p1_distance, p1_games = _seat_medoid("tetsuya", 1)
    routes = {
        "TETSUYA_MEDOID_P0": p0,
        "TETSUYA_MEDOID_P1": p1,
    }

    encoded = {name: encode_actions(actions) for name, actions in routes.items()}
    metadata = {
        "seat0_source": f"tetsuya episode {p0_episode} player 0",
        "seat1_source": f"tetsuya episode {p1_episode} player 1",
        "seat0_medoid_distance": p0_distance,
        "seat1_medoid_distance": p1_distance,
        "seat0_games": p0_games,
        "seat1_games": p1_games,
        "steps": 719,
        "selection": "minimum total action-channel Hamming distance among 15 newest replays in each seat",
        "execution": "exact seat-matched routes; no runtime branches",
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
