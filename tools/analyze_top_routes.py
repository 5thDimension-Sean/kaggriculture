"""Mine route families and simple conditional branches from public replays.

The report is diagnostic: it distinguishes fixed production backbones from
steps whose action is well explained by a one-feature threshold over the live
observation (price, inventory, money, opponent build state, and so on).
"""

import argparse
import glob
import json
import os
from collections import Counter, defaultdict


ITEMS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER", "COW", "SHEEP", "GOOSE",
)


def _canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _clean(action):
    action = action or {}
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _features(obs, seat):
    obs = obs if isinstance(obs, dict) else {}
    farms = list(obs.get("farms") or [])
    own = farms[seat] if seat < len(farms) and isinstance(farms[seat], dict) else {}
    opp_seat = 1 - seat
    opp = farms[opp_seat] if opp_seat < len(farms) and isinstance(farms[opp_seat], dict) else {}
    market = obs.get("market") if isinstance(obs.get("market"), dict) else {}
    prices = market.get("prices") if isinstance(market.get("prices"), dict) else {}
    supply = market.get("inventory") if isinstance(market.get("inventory"), dict) else {}
    private = obs.get("private") if isinstance(obs.get("private"), dict) else {}
    shed = private.get("shed") if isinstance(private.get("shed"), dict) else {}
    seeds = private.get("seeds") if isinstance(private.get("seeds"), dict) else {}
    inventories = list(private.get("inventories") or [])
    out = {
        "money": _number(own.get("money")),
        "own_hands": float(len(own.get("hands") or [])),
        "opp_hands": float(len(opp.get("hands") or [])),
        "own_quadrants": float(len(own.get("unlocked_quadrants") or [])),
        "opp_quadrants": float(len(opp.get("unlocked_quadrants") or [])),
        "shed_total": sum(_number(v) for v in shed.values()),
        "hand_inventory_total": sum(
            _number(value)
            for inventory in inventories if isinstance(inventory, dict)
            for value in inventory.values()
        ),
    }
    for item in ITEMS:
        out[f"price_{item}"] = _number(prices.get(item))
        out[f"supply_{item}"] = _number(supply.get(item))
        out[f"shed_{item}"] = _number(shed.get(item))
        out[f"seed_{item}"] = _number(seeds.get(item))
    own_tiles = _canon(own.get("tiles") or [])
    opp_tiles = _canon(opp.get("tiles") or [])
    for kind in ("WEED", "PASTURE", "WHEAT", "MELON", "COW", "SHEEP"):
        out[f"own_tiles_{kind}"] = float(own_tiles.count(kind))
        out[f"opp_tiles_{kind}"] = float(opp_tiles.count(kind))
    return out


def load_games(root):
    games = []
    for player_dir in sorted(glob.glob(os.path.join(root, "*"))):
        manifest_path = os.path.join(player_dir, "manifest.json")
        if not os.path.isfile(manifest_path):
            continue
        team = os.path.basename(player_dir)
        with open(manifest_path, encoding="utf-8") as handle:
            manifest = json.load(handle)
        for entry in manifest:
            episode_id = int(entry["episode_id"])
            seat = int(entry["seat"])
            replay_path = os.path.join(player_dir, f"episode-{episode_id}-replay.json")
            with open(replay_path, encoding="utf-8") as handle:
                replay = json.load(handle)
            raw_steps = replay.get("steps") or []
            samples = []
            # raw_steps[0] is the bootstrap observation. The action stored in
            # raw_steps[t + 1] was selected from raw_steps[t]'s observation.
            for step in range(max(0, len(raw_steps) - 1)):
                before = raw_steps[step][seat] if seat < len(raw_steps[step]) else {}
                after = raw_steps[step + 1][seat] if seat < len(raw_steps[step + 1]) else {}
                samples.append({
                    "step": step,
                    "action": _clean(after.get("action")),
                    "features": _features(before.get("observation"), seat),
                })
            games.append({
                "team": team,
                "episode_id": episode_id,
                "seat": seat,
                "seed": entry.get("seed"),
                "samples": samples,
            })
    return games


def _mode(values):
    return Counter(values).most_common(1)[0][0]


def _stump(rows, channel):
    labels = [_canon(row["action"][channel]) for row in rows]
    baseline_label = _mode(labels)
    baseline = sum(label == baseline_label for label in labels) / len(labels)
    best = None
    feature_names = sorted(set().union(*(row["features"].keys() for row in rows)))
    for feature in feature_names:
        values = [row["features"].get(feature, 0.0) for row in rows]
        unique = sorted(set(values))
        for left_value, right_value in zip(unique, unique[1:]):
            threshold = (left_value + right_value) / 2.0
            left = [label for label, value in zip(labels, values) if value <= threshold]
            right = [label for label, value in zip(labels, values) if value > threshold]
            if not left or not right:
                continue
            left_label, right_label = _mode(left), _mode(right)
            correct = sum(
                label == (left_label if value <= threshold else right_label)
                for label, value in zip(labels, values)
            )
            accuracy = correct / len(labels)
            candidate = (accuracy, feature, threshold, left_label, right_label)
            if best is None or candidate[:3] > best[:3]:
                best = candidate
    if best is None:
        return baseline, None
    accuracy, feature, threshold, left_label, right_label = best
    return baseline, {
        "accuracy": accuracy,
        "gain": accuracy - baseline,
        "feature": feature,
        "threshold": threshold,
        "if_le": json.loads(left_label),
        "if_gt": json.loads(right_label),
    }


def analyze(games):
    report = {"groups": [], "seat0_cross_team": [], "rules": []}
    grouped = defaultdict(list)
    for game in games:
        grouped[(game["team"], game["seat"])].append(game)

    majority_routes = {}
    for (team, seat), team_games in sorted(grouped.items()):
        n_steps = min(len(game["samples"]) for game in team_games)
        counters = Counter()
        route = []
        for step in range(n_steps):
            rows = [game["samples"][step] for game in team_games]
            action = {}
            variants = {}
            for channel in ("farmer", "hands", "market"):
                labels = [_canon(row["action"][channel]) for row in rows]
                action[channel] = json.loads(_mode(labels))
                variants[channel] = len(set(labels))
                counters[f"{channel}_fixed_steps"] += variants[channel] == 1
                if variants[channel] > 1:
                    baseline, stump = _stump(rows, channel)
                    rule = {
                        "team": team,
                        "seat": seat,
                        "step": step,
                        "channel": channel,
                        "samples": len(rows),
                        "variants": variants[channel],
                        "baseline_accuracy": baseline,
                    }
                    if stump:
                        rule.update(stump)
                    report["rules"].append(rule)
            if variants["farmer"] == variants["hands"] == 1 and variants["market"] > 1:
                counters["market_only_branch_steps"] += 1
            if variants["market"] == 1 and (variants["farmer"] > 1 or variants["hands"] > 1):
                counters["production_only_branch_steps"] += 1
            if variants["farmer"] > 1 or variants["hands"] > 1:
                counters["production_branch_steps"] += 1
            if variants["market"] > 1:
                counters["market_branch_steps"] += 1
            route.append(action)
        majority_routes[(team, seat)] = route
        report["groups"].append({
            "team": team,
            "seat": seat,
            "games": len(team_games),
            "steps": n_steps,
            **counters,
        })

    seat0_teams = sorted(team for team, seat in majority_routes if seat == 0)
    for index, left_team in enumerate(seat0_teams):
        for right_team in seat0_teams[index + 1:]:
            left = majority_routes[(left_team, 0)]
            right = majority_routes[(right_team, 0)]
            n_steps = min(len(left), len(right))
            row = {"left": left_team, "right": right_team, "steps": n_steps}
            for channel in ("farmer", "hands", "market"):
                matches = sum(
                    _canon(left[step][channel]) == _canon(right[step][channel])
                    for step in range(n_steps)
                )
                row[f"{channel}_agreement"] = matches / n_steps
            report["seat0_cross_team"].append(row)

    report["rules"].sort(
        key=lambda row: (row.get("gain", 0.0), row.get("accuracy", 0.0)),
        reverse=True,
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=os.path.join("top-players-data", "aether-top3"))
    parser.add_argument("--out", default=os.path.join("artifacts", "aether_route_analysis.json"))
    parser.add_argument("--top-rules", type=int, default=40)
    args = parser.parse_args()
    games = load_games(args.root)
    report = analyze(games)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps({
        "groups": report["groups"],
        "seat0_cross_team": report["seat0_cross_team"],
        "top_rules": report["rules"][: args.top_rules],
    }, indent=2, ensure_ascii=False))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
