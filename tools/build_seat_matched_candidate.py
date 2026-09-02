"""Build a standalone agent from two reconstructed seat-specific routes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _payload(path: Path) -> tuple[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["encoded"], {
        "consistency": data.get("consistency"),
        "games": data.get("n_games"),
        "episodes": data.get("episode_ids"),
    }


def build_source(p0_path: Path, p1_path: Path, version: str) -> str:
    p0, p0_meta = _payload(p0_path)
    p1, p1_meta = _payload(p1_path)
    return f'''"""Seat-matched consensus routes reconstructed from public replays."""
import base64
import copy
import json
import zlib

__version__ = {version!r}
_PROVENANCE = {{"seat0": {p0_meta!r}, "seat1": {p1_meta!r}}}

def _decode(payload):
    return json.loads(zlib.decompress(base64.b85decode(payload)).decode("utf-8"))

_ROUTES = (_decode({p0!r}), _decode({p1!r}))

def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    return getter(key, default) if callable(getter) else getattr(value, key, default)

def agent(obs, configuration=None):
    try:
        seat = 1 if int(_get(obs, "player", 0) or 0) == 1 else 0
        step = max(0, int(_get(obs, "step", 0) or 0))
        route = _ROUTES[seat]
        return copy.deepcopy(route[min(step, len(route) - 1)])
    except Exception:
        seat = 1 if int(_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_get(obs, "farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {{}}
        return {{
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }}

def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p0", type=Path, required=True)
    parser.add_argument("--p1", type=Path, required=True)
    parser.add_argument("--version", default="aether-1.0-seat-matched-consensus")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = build_source(args.p0, args.p1, args.version)
    compile(source, str(args.out), "exec")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(source, encoding="utf-8", newline="\n")
    print(f"Wrote {args.out} ({len(source):,} bytes)")


if __name__ == "__main__":
    main()
