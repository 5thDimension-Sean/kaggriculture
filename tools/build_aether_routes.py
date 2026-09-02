"""Generate Aether's compact fixed-route library from a public Kaggle replay.

The generated module is committed so the runtime never needs replay files.
Run this tool again after refreshing ``top-players-data/final-research``.
"""

from __future__ import annotations

import argparse
import json
import os

from tools.route_mining import encode_actions, load_player_games


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "top-players-data", "final-research")


def _episode_actions(team: str, episode_id: int, seat: int) -> list[dict]:
    directory = os.path.join(CORPUS, team)
    games = load_player_games(directory)[seat]
    for game in games:
        if int(game["episode_id"]) == episode_id:
            return game["actions"]
    raise ValueError(f"missing {team} episode {episode_id} seat {seat}")


def build_source() -> str:
    routes = {
        "TETSUYA_EP104492175_P0": _episode_actions("tetsuya", 104492175, 0),
        "TETSUYA_EP104466724_P1": _episode_actions("tetsuya", 104466724, 1),
    }

    encoded = {name: encode_actions(actions) for name, actions in routes.items()}
    metadata = {
        "seat0_source": "tetsuya episode 104492175 player 0",
        "seat1_source": "tetsuya episode 104466724 player 1",
        "steps": 719,
        "selection": "each route went 30-4-2 over 36 fresh exact-seed top-three replay cases",
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
