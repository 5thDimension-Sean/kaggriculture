"""Discover coherent route families by branching complete replay action tapes.

Unlike per-turn majority voting, this tool never creates a synthetic route.
Every leaf corresponds to one or more complete observed episode routes. Shared
prefixes are path-compressed, and the first manifest route is marked as the
parent path at every branch it traverses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from collections import OrderedDict
from pathlib import Path

from tools.route_mining import _clean_action, encode_actions


END = "<END>"


def _action_key(action: dict) -> str:
    return json.dumps(action, sort_keys=True, separators=(",", ":"))


def _route_fingerprint(action_keys: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for action in action_keys:
        digest.update(action.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _reward_pair(replay: dict) -> tuple[float, float]:
    rewards = replay.get("rewards")
    if isinstance(rewards, list) and len(rewards) >= 2:
        return float(rewards[0]), float(rewards[1])
    final = replay["steps"][-1]
    return float(final[0].get("reward") or 0), float(final[1].get("reward") or 0)


def load_replay_games(player_dir: str | Path, seat: int) -> list[dict]:
    """Load complete routes and outcome metadata in manifest order."""
    directory = Path(player_dir)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    games = []
    for entry in manifest:
        if int(entry["seat"]) != seat:
            continue
        episode_id = int(entry["episode_id"])
        replay_path = directory / f"episode-{episode_id}-replay.json"
        if not replay_path.exists():
            continue
        replay = json.loads(replay_path.read_text(encoding="utf-8"))
        actions = []
        for step in replay["steps"]:
            raw = step[seat].get("action") if seat < len(step) else None
            actions.append(_clean_action(raw))
        bootstrap = {"farmer": ["PASS"], "hands": [], "market": []}
        if actions and actions[0] == bootstrap:
            actions = actions[1:]
        if len(actions) < 100:
            continue

        rewards = _reward_pair(replay)
        names = replay.get("info", {}).get("TeamNames", [])
        opponent = names[1 - seat] if len(names) >= 2 else None
        margin = rewards[seat] - rewards[1 - seat]
        games.append(
            {
                "episode_id": episode_id,
                "seat": seat,
                "actions": actions,
                "margin": margin,
                "opponent": opponent,
                "seed": entry.get("seed", replay.get("info", {}).get("seed")),
                "create_time": entry.get("create_time"),
            }
        )
    return games


def group_unique_routes(games: list[dict]) -> list[dict]:
    """Group byte-equivalent complete routes while preserving first-seen order."""
    grouped: OrderedDict[tuple[str, ...], dict] = OrderedDict()
    for game in games:
        keys = tuple(_action_key(action) for action in game["actions"])
        group = grouped.get(keys)
        if group is None:
            group = {
                "actions": game["actions"],
                "action_keys": keys,
                "games": [],
            }
            grouped[keys] = group
        group["games"].append(game)

    routes = []
    total = len(games)
    for index, group in enumerate(grouped.values(), start=1):
        members = group["games"]
        margins = [game["margin"] for game in members]
        wins = sum(margin > 0 for margin in margins)
        losses = sum(margin < 0 for margin in margins)
        ties = len(margins) - wins - losses
        routes.append(
            {
                **group,
                "route_id": f"R{index:03d}",
                "fingerprint": _route_fingerprint(group["action_keys"]),
                "support": len(members),
                "support_fraction": len(members) / total if total else 0.0,
                "episodes": [game["episode_id"] for game in members],
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "mean_margin": sum(margins) / len(margins),
            }
        )
    return routes


def build_route_tree(routes: list[dict]) -> tuple[dict, dict[str, list[float]]]:
    """Build a path-compressed prefix tree and collect branch probabilities."""
    branch_probabilities = {route["route_id"]: [] for route in routes}

    def build(members: list[dict], start_step: int) -> dict:
        support = sum(route["support"] for route in members)
        step = start_step
        while True:
            tokens = {
                route["action_keys"][step] if step < len(route["action_keys"]) else END
                for route in members
            }
            if len(tokens) > 1 or tokens == {END}:
                break
            step += 1

        node = {
            "prefix_start": start_step,
            "prefix_end_exclusive": step,
            "support": support,
            "route_ids": [route["route_id"] for route in members],
        }
        if tokens == {END}:
            node["leaf_route_ids"] = [route["route_id"] for route in members]
            return node

        buckets: OrderedDict[str, list[dict]] = OrderedDict()
        for route in members:
            token = route["action_keys"][step] if step < len(route["action_keys"]) else END
            buckets.setdefault(token, []).append(route)

        children = []
        parent_route_id = members[0]["route_id"]
        for token, child_members in buckets.items():
            child_support = sum(route["support"] for route in child_members)
            fraction = child_support / support
            for route in child_members:
                branch_probabilities[route["route_id"]].append(fraction)
            children.append(
                {
                    "action_hash": (
                        END if token == END else hashlib.sha256(token.encode()).hexdigest()[:12]
                    ),
                    "action": None if token == END else json.loads(token),
                    "support": child_support,
                    "support_fraction": fraction,
                    "parent_path": any(
                        route["route_id"] == parent_route_id for route in child_members
                    ),
                    "leaf_route_ids": (
                        [route["route_id"] for route in child_members]
                        if token == END
                        else []
                    ),
                    "node": None if token == END else build(child_members, step + 1),
                }
            )
        node["branch_step"] = step
        node["children"] = children
        return node

    if not routes:
        return {}, branch_probabilities
    return build(routes, 0), branch_probabilities


def score_routes(
    routes: list[dict],
    probabilities: dict[str, list[float]],
    min_support: int,
    min_branch_fraction: float,
) -> None:
    """Attach conservative evidence labels for selecting benchmark candidates."""
    for route in routes:
        values = probabilities[route["route_id"]]
        branch_floor = min(values, default=1.0)
        branch_geomean = (
            math.exp(sum(math.log(value) for value in values) / len(values))
            if values
            else 1.0
        )
        # Beta(1, 1) smoothing prevents a one-game win from being called 100%.
        bayes_win_rate = (route["wins"] + 1) / (route["support"] + 2)
        supported = route["support"] >= min_support
        positive = route["wins"] > route["losses"] and route["mean_margin"] > 0
        plausible = positive and (supported or branch_geomean >= min_branch_fraction)
        if plausible and supported:
            evidence = "high"
        elif plausible:
            evidence = "medium"
        else:
            evidence = "low"
        support_score = min(1.0, route["support"] / max(1, min_support))
        route["branch_floor"] = branch_floor
        route["branch_geomean"] = branch_geomean
        route["bayes_win_rate"] = bayes_win_rate
        route["plausible"] = plausible
        route["evidence"] = evidence
        route["plausibility_score"] = (
            0.45 * bayes_win_rate + 0.35 * branch_geomean + 0.20 * support_score
        )


def analyze_games(
    games: list[dict], min_support: int = 2, min_branch_fraction: float = 0.2
) -> dict:
    routes = group_unique_routes(games)
    tree, probabilities = build_route_tree(routes)
    score_routes(routes, probabilities, min_support, min_branch_fraction)
    ranked = sorted(
        routes,
        key=lambda route: (
            route["plausible"],
            route["plausibility_score"],
            route["support"],
        ),
        reverse=True,
    )
    first_branch = tree.get("branch_step") if tree else None
    return {
        "episodes": len(games),
        "unique_routes": len(routes),
        "duplicate_routes": len(games) - len(routes),
        "plausible_routes": sum(route["plausible"] for route in routes),
        "first_branch_step": first_branch,
        "routes": ranked,
        "tree": tree,
    }


def _serializable_route(route: dict) -> dict:
    omitted = {"actions", "action_keys", "games"}
    return {key: value for key, value in route.items() if key not in omitted}


def _action_summary(action: dict | None) -> str:
    if action is None:
        return "END"
    farmer = "/".join(str(part) for part in action.get("farmer", ["PASS"]))
    hands = [
        f"{index}:{'/'.join(str(part) for part in order)}"
        for index, order in enumerate(action.get("hands", []))
        if order and order != ["PASS"]
    ]
    market = ["/".join(str(part) for part in order) for order in action.get("market", [])]
    parts = [f"farmer={farmer}"]
    if hands:
        parts.append("hands=" + ",".join(hands[:3]) + ("…" if len(hands) > 3 else ""))
    if market:
        parts.append("market=" + ",".join(market[:3]) + ("…" if len(market) > 3 else ""))
    return " ".join(parts)


def render_tree(tree: dict) -> str:
    """Render the compact branch structure without dumping every shared action."""
    if not tree:
        return "(no routes)\n"
    lines = []

    def render_node(node: dict, indent: str) -> None:
        start = node["prefix_start"]
        end = node["prefix_end_exclusive"]
        if end > start:
            lines.append(f"{indent}shared steps {start}-{end - 1} (support {node['support']})")
        if "leaf_route_ids" in node:
            lines.append(f"{indent}leaf {', '.join(node['leaf_route_ids'])}")
            return
        lines.append(f"{indent}branch at step {node['branch_step']}")
        for index, child in enumerate(node["children"]):
            marker = "parent" if child["parent_path"] else "child"
            lines.append(
                f"{indent}  [{index}] {marker} support={child['support']} "
                f"({child['support_fraction']:.1%}) {_action_summary(child['action'])}"
            )
            if child["node"] is not None:
                render_node(child["node"], indent + "      ")

    render_node(tree, "")
    return "\n".join(lines) + "\n"


def _write_route_payloads(routes: list[dict], output_dir: Path, seat: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for route in routes:
        payload = {
            "encoded": encode_actions(route["actions"]),
            "seat": seat,
            "route_id": route["route_id"],
            "fingerprint": route["fingerprint"],
            "episodes": route["episodes"],
            "support": route["support"],
            "n_games": route["support"],
            "episode_ids": route["episodes"],
            "plausible": route["plausible"],
            "evidence": route["evidence"],
            "plausibility_score": route["plausibility_score"],
        }
        path = output_dir / f"seat{seat}-{route['route_id']}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", required=True, help="Player replay directory")
    parser.add_argument("--seat", choices=("0", "1", "both"), default="both")
    parser.add_argument("--out", required=True, help="Route-tree JSON report")
    parser.add_argument("--tree-out", help="Optional human-readable tree report")
    parser.add_argument("--emit-routes", help="Directory for reusable route payloads")
    parser.add_argument("--min-support", type=int, default=2)
    parser.add_argument("--min-branch-fraction", type=float, default=0.2)
    args = parser.parse_args()

    seats = (0, 1) if args.seat == "both" else (int(args.seat),)
    report = {
        "player": os.path.basename(os.path.normpath(args.dir)),
        "source_directory": os.path.abspath(args.dir),
        "thresholds": {
            "min_support": args.min_support,
            "min_branch_fraction": args.min_branch_fraction,
        },
        "seats": {},
    }
    rendered_trees = []
    for seat in seats:
        analysis = analyze_games(
            load_replay_games(args.dir, seat),
            min_support=args.min_support,
            min_branch_fraction=args.min_branch_fraction,
        )
        if args.emit_routes:
            _write_route_payloads(
                analysis["routes"], Path(args.emit_routes) / f"seat{seat}", seat
            )
        report["seats"][str(seat)] = {
            **analysis,
            "routes": [_serializable_route(route) for route in analysis["routes"]],
        }
        rendered_trees.append(f"seat {seat}\n{'=' * 6}\n{render_tree(analysis['tree'])}")
        print(
            f"seat {seat}: episodes={analysis['episodes']} "
            f"unique_routes={analysis['unique_routes']} "
            f"plausible={analysis['plausible_routes']} "
            f"first_branch={analysis['first_branch_step']}"
        )
        for route in analysis["routes"][:10]:
            print(
                f"  {route['route_id']} plausible={route['plausible']} "
                f"evidence={route['evidence']} support={route['support']} "
                f"record={route['wins']}-{route['losses']}-{route['ties']} "
                f"mean={route['mean_margin']:+,.0f} "
                f"branch={route['branch_geomean']:.3f} "
                f"score={route['plausibility_score']:.3f} "
                f"episodes={route['episodes']}"
            )

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {output}")
    if args.tree_out:
        tree_output = Path(args.tree_out)
        tree_output.parent.mkdir(parents=True, exist_ok=True)
        tree_output.write_text("\n".join(rendered_trees), encoding="utf-8")
        print(f"Wrote {tree_output}")


if __name__ == "__main__":
    main()
