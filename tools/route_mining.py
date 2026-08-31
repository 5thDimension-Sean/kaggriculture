"""route_mining.py -- Majority-vote route reconstruction + self-consistency
scoring from real Kaggriculture replay JSONs.

Prior MapleLeaf versions (6.2-6.5, per main.py's docstring history) did this
by hand each time: pull several real games for a candidate player, check
whether they play the *same* deterministic script every game ("self-
consistency"), and if so, reconstruct their route by taking the per-step
majority action across games. That process was never saved as code -- this
is the first reusable implementation of it.

Self-consistency is computed separately for P0 and P1 seats (a player's two
seats can differ slightly -- documented for Filip Strzalka in 6.5). For each
seat, at every step, we take the most common (farmer, hands-per-index,
market) values across that player's games in that seat, and report what
fraction of games agreed with that per-step majority. A high percentage
(~95%+, matching the ~98-99% bar that qualified Filip/Nikita previously)
means the player is running a fixed, non-adaptive script safe to clone
wholesale; a low percentage (Kawashigi/researchstudio.site were ~48-63% in
6.5's survey) means they're actually reacting to the game state and can't be
usefully reconstructed this way.

Usage:
    python3 route_mining.py --dir "top-players-data/Ryo Hasegawa" --out routes_6_6
    python3 route_mining.py --scan top-players-data --out routes_6_6
"""

import argparse
import base64
import glob
import json
import os
import zlib
from collections import Counter


def _canon(value):
    """Recursively convert lists to tuples so actions are hashable for voting."""
    if isinstance(value, list):
        return tuple(_canon(v) for v in value)
    return value


def _clean_action(action):
    action = action or {}
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(h or ["PASS"]) for h in (action.get("hands") or [])],
        "market": [list(m) for m in (action.get("market") or [])],
    }


def load_player_games(player_dir):
    """Read manifest.json + replay files, return {0: [action_lists...], 1: [...]}
    keyed by the seat this player occupied in each game."""
    manifest_path = os.path.join(player_dir, "manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)

    games_by_seat = {0: [], 1: []}
    for entry in manifest:
        ep_id, seat = entry["episode_id"], entry["seat"]
        fpath = os.path.join(player_dir, f"episode-{ep_id}-replay.json")
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            data = json.load(f)
        actions = []
        for step in data["steps"]:
            if seat < len(step):
                actions.append(_clean_action(step[seat].get("action")))
            else:
                actions.append(_clean_action(None))
        # Strip exactly one replay bootstrap entry. A second empty PASS can be
        # the player's intentional step-0 action (notably in current MtN and
        # Driz Lo routes) and must remain on the tape.
        if actions and actions[0]["farmer"] == ["PASS"] and not actions[0]["hands"] and not actions[0]["market"]:
            actions = actions[1:]
        if len(actions) >= 100:
            games_by_seat[seat].append({"episode_id": ep_id, "actions": actions})
    return games_by_seat


def majority_vote_route(games):
    """games: list of {"episode_id":..., "actions": [...]}. Returns
    (reconstructed_actions, overall_consistency, breakdown_dict) or (None, 0, {})
    if fewer than 2 games."""
    if len(games) < 2:
        return None, 0.0, {}

    n_steps = min(len(g["actions"]) for g in games)
    reconstructed = []
    agree_farmer = agree_hands = agree_market = 0
    hand_obs = 0

    for step in range(n_steps):
        acts = [g["actions"][step] for g in games]

        farmer_votes = Counter(_canon(a["farmer"]) for a in acts)
        farmer_mode, farmer_count = farmer_votes.most_common(1)[0]
        agree_farmer += farmer_count

        market_votes = Counter(_canon(a["market"]) for a in acts)
        market_mode, market_count = market_votes.most_common(1)[0]
        agree_market += market_count

        max_hands = max(len(a["hands"]) for a in acts)
        hands_mode = []
        for h_idx in range(max_hands):
            h_votes = Counter(
                _canon(a["hands"][h_idx]) if h_idx < len(a["hands"]) else ("PASS",)
                for a in acts
            )
            h_mode, h_count = h_votes.most_common(1)[0]
            hands_mode.append(list(h_mode))
            agree_hands += h_count
            hand_obs += len(acts)

        reconstructed.append({
            "farmer": list(farmer_mode),
            "hands": hands_mode,
            "market": [list(m) for m in market_mode],
        })

    n_games = len(games)
    farmer_pct = agree_farmer / (n_steps * n_games)
    market_pct = agree_market / (n_steps * n_games)
    hands_pct = agree_hands / hand_obs if hand_obs else 1.0
    overall = (farmer_pct + hands_pct + market_pct) / 3.0

    breakdown = {
        "n_games": n_games,
        "n_steps": n_steps,
        "farmer_consistency": farmer_pct,
        "hands_consistency": hands_pct,
        "market_consistency": market_pct,
        "overall_consistency": overall,
        "episode_ids": [g["episode_id"] for g in games],
    }
    return reconstructed, overall, breakdown


def encode_actions(actions):
    raw = json.dumps(actions, separators=(",", ":")).encode()
    return base64.b85encode(zlib.compress(raw, level=9)).decode()


def reconstruct_player(player_dir, out_dir, name):
    games_by_seat = load_player_games(player_dir)
    result = {"name": name}
    for seat in (0, 1):
        games = games_by_seat[seat]
        route, consistency, breakdown = majority_vote_route(games)
        result[f"p{seat}"] = breakdown
        if breakdown:
            breakdown["qualifies"] = consistency >= 0.95
        if route is not None:
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{name}_p{seat}_route.json")
            with open(out_path, "w") as f:
                json.dump({"encoded": encode_actions(route), "consistency": consistency,
                           "n_games": len(games), "episode_ids": breakdown["episode_ids"]}, f, indent=2)
            result[f"p{seat}"]["route_file"] = out_path
    return result


def _reconstruct_one(task):
    name, path, out_dir = task
    return reconstruct_player(path, out_dir, name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="Single player directory (has manifest.json)")
    ap.add_argument("--scan", help="Directory of player subdirectories to process all of")
    ap.add_argument("--out", default="routes_6_6")
    ap.add_argument("--workers", type=int, default=1,
                     help="Parallelize across players with a multiprocessing.Pool (--scan only)")
    args = ap.parse_args()

    targets = []
    if args.dir:
        targets = [(os.path.basename(args.dir.rstrip("/")), args.dir)]
    elif args.scan:
        for sub in sorted(os.listdir(args.scan)):
            full = os.path.join(args.scan, sub)
            if os.path.isdir(full) and os.path.exists(os.path.join(full, "manifest.json")):
                targets.append((sub, full))
    else:
        raise SystemExit("Pass --dir or --scan")

    os.makedirs(args.out, exist_ok=True)
    tasks = [(name, path, args.out) for name, path in targets]

    if args.workers > 1 and len(tasks) > 1:
        import multiprocessing as mp
        with mp.Pool(processes=min(args.workers, len(tasks))) as pool:
            results = pool.map(_reconstruct_one, tasks)
    else:
        results = [_reconstruct_one(t) for t in tasks]

    for r in results:
        name = r["name"]
        for seat in (0, 1):
            b = r[f"p{seat}"]
            if not b:
                continue
            tag = "QUALIFIES" if b.get("qualifies") else "too adaptive"
            print(f"  {name:30s} P{seat}  games={b['n_games']:3d}  "
                  f"overall={b['overall_consistency']*100:5.1f}%  "
                  f"(farmer={b['farmer_consistency']*100:.1f}% hands={b['hands_consistency']*100:.1f}% "
                  f"market={b['market_consistency']*100:.1f}%)  -> {tag}")

    with open(os.path.join(args.out, "_summary.json"), "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSummary written to {os.path.join(args.out, '_summary.json')}")


if __name__ == "__main__":
    main()
