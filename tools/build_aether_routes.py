"""Generate Aether's compact route library from public Kaggle replays.

The generated module is committed so the runtime never needs replay files.
Run this tool again after refreshing ``top-players-data/aether-top3``.
"""

from __future__ import annotations

import argparse
import json
import os

from tools.route_mining import encode_actions, load_player_games, majority_vote_route


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "top-players-data", "aether-top3")


def _episode_actions(team: str, episode_id: int, seat: int) -> list[dict]:
    directory = os.path.join(CORPUS, team)
    games = load_player_games(directory)[seat]
    for game in games:
        if int(game["episode_id"]) == episode_id:
            return game["actions"]
    raise ValueError(f"missing {team} episode {episode_id} seat {seat}")


def build_source() -> str:
    # These are demonstrations, not hand-authored magic numbers.  The two
    # seat-0 branches share tetsuya's opening and fork at the first day
    # boundary.  MtN P1 is reconstructed by majority vote because its four
    # public games agree on 99.2% of actions.
    routes = {
        "P0_ANIMAL_PRESSURE": _episode_actions("tetsuya", 104058487, 0),
        "P0_DAIRY_PRESSURE": _episode_actions("tetsuya", 104060611, 0),
        "P0_CROP_PRESSURE": _episode_actions("tetsuya", 104129942, 0),
    }
    mtn_p1_games = load_player_games(os.path.join(CORPUS, "MtN"))[1]
    mtn_p1, consistency, breakdown = majority_vote_route(mtn_p1_games)
    if mtn_p1 is None or consistency < 0.99:
        raise ValueError(f"MtN P1 route is unexpectedly unstable: {consistency:.4f}")
    routes["P1_MTN_CONSENSUS"] = mtn_p1

    encoded = {name: encode_actions(actions) for name, actions in routes.items()}
    metadata = {
        "seat0_sources": {
            "animal_pressure": "tetsuya episode 104058487 P0",
            "dairy_pressure": "tetsuya episode 104060611 P0",
            "crop_pressure": "tetsuya episode 104129942 P0",
        },
        "seat1_source": "MtN P1 majority of 4 public replays",
        "seat1_consistency": consistency,
        "seat1_breakdown": breakdown,
        "branch_evidence": "Driz Lo and MtN P0 both fork at step 73 on public WOOL inventory <= 9995",
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
