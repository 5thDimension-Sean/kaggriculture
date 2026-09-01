"""Build a standalone fixed-route agent from one public replay.

The emitted agent preserves the replay's farmer, hand, and market tape.  With
``--weed-repair`` it changes only a productive action blocked by a visible
WEED: DIG now, replay that actor's delayed actions, and consume the next PASS
within eight turns so the actor rejoins the original tape.  Other actors and
market orders remain on their exact scheduled steps.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import zlib


def _actions(path: Path, seat: int) -> list[dict]:
    replay = json.loads(path.read_text(encoding="utf-8"))
    actions = []
    for row in replay["steps"]:
        raw = row[seat].get("action") or {}
        actions.append({
            "farmer": list(raw.get("farmer") or ["PASS"]),
            "hands": [list(op or ["PASS"]) for op in (raw.get("hands") or [])],
            "market": [list(order) for order in (raw.get("market") or [])],
        })
    if actions and actions[0] == {"farmer": ["PASS"], "hands": [], "market": []}:
        actions = actions[1:]
    return actions


def _source(actions: list[dict], provenance: str, weed_repair: bool) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(actions, separators=(",", ":")).encode("utf-8"), level=9
    )).decode("ascii")
    return f'''"""Fixed public replay route: {provenance}."""
import base64
import copy
import json
import zlib

_ROUTE = json.loads(zlib.decompress(base64.b85decode({payload!r})).decode("utf-8"))
_REPAIR = {weed_repair!r}
_BLOCKED = {{"BUILD_PASTURE", "BUILD_COOP", "PLANT", "PLACE"}}
_STATE = {{0: {{"last": -1, "pending": {{}}}}, 1: {{"last": -1, "pending": {{}}}}}}

def _is_weed(tiles, position):
    try:
        x, y = int(position[0]), int(position[1])
        tile = tiles[y][x]
        return isinstance(tile, dict) and tile.get("kind") == "WEED"
    except (IndexError, TypeError, ValueError):
        return False

def agent(obs, config=None):
    step = min(max(0, int(obs.get("step", 0) or 0)), len(_ROUTE) - 1)
    seat = 1 if int(obs.get("player", 0) or 0) == 1 else 0
    state = _STATE[seat]
    if step == 0 or step <= state["last"]:
        state["pending"] = {{}}
    state["last"] = step
    action = copy.deepcopy(_ROUTE[step])
    if not _REPAIR or step >= 717:
        return action
    farm = (obs.get("farms") or [{{}}, {{}}])[seat]
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    tiles = farm.get("tiles") or []
    ops = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
    original_len = len(ops)
    ops.extend([["PASS"]] * max(0, len(positions) - len(ops)))
    for actor, position in enumerate(positions):
        scheduled = ops[actor] if ops[actor] else ["PASS"]
        pending = state["pending"].get(actor)
        if pending:
            delayed = pending.pop(0)
            ops[actor] = delayed
            if scheduled[0] != "PASS" and len(pending) < 8:
                pending.append(scheduled)
            if pending:
                state["pending"][actor] = pending
            else:
                state["pending"].pop(actor, None)
        elif scheduled[0] in _BLOCKED and _is_weed(tiles, position):
            ops[actor] = ["DIG"]
            state["pending"][actor] = [scheduled]
    keep = max(original_len, len(positions))
    action["farmer"] = ops[0]
    action["hands"] = ops[1:keep]
    return action
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay", type=Path)
    parser.add_argument("--seat", type=int, choices=(0, 1), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--weed-repair", action="store_true")
    args = parser.parse_args()
    actions = _actions(args.replay, args.seat)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        _source(actions, f"{args.replay.name} seat {args.seat}", args.weed_repair),
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote {args.out} with {len(actions)} route steps")


if __name__ == "__main__":
    main()
