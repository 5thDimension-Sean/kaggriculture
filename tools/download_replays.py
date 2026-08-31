"""download_replays.py -- Pull real episode replays for arbitrary Kaggriculture
teams via the Kaggle API.

Key discovery (2026-08-22): kaggle.api's `competition_list_episodes(submission_id)`
and `competition_episode_replay(episode_id)` are NOT restricted to your own
submissions -- any completed submission's episode list and any episode's full
replay JSON is fetchable if you know the submission/episode id. This makes it
possible to mine real replays for *any* current leaderboard team, not just
opponents we've personally been matched against.

Submission IDs for arbitrary teams aren't listed anywhere directly, but can be
discovered by a BFS graph-walk: start from our own submission, collect every
opponent (submissionId, teamName) pair seen across our episodes, then expand
to those opponents' own episode lists, and so on. Because Bradley-Terry
matchmaking is a small-world graph, 2-3 hops from even a low-rated submission
is enough to discover the entire visible leaderboard's submission IDs.

Usage:
    python3 download_replays.py --discover --targets "Ryo Hasegawa,Subramanya N,..."
    python3 download_replays.py --fetch --manifest top_player_submissions.json --per-player 20
"""

import argparse
import json
import os
import time

MANIFEST_DEFAULT = "top_player_submissions.json"
OUT_DIR_DEFAULT = "top-players-data"


def discover(seed_submission_id, target_names, max_hops=3, breadth_cap=60, sleep=0.05):
    """BFS from seed_submission_id, returns {team_name: submission_id} for every
    target_names member found, plus the full discovered name->submission map."""
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    targets = set(target_names)
    visited = set()
    name_to_sub = {}
    found = {}
    frontier = [seed_submission_id]

    for hop in range(max_hops):
        next_frontier = []
        for sub_id in frontier:
            if sub_id in visited:
                continue
            visited.add(sub_id)
            try:
                eps = api.competition_list_episodes(sub_id)
            except Exception as e:
                print(f"  [discover] sub {sub_id} failed: {e}")
                continue
            for ep in eps:
                for a in ep.agents:
                    name_to_sub.setdefault(a.team_name, a.submission_id)
                    if a.submission_id not in visited:
                        next_frontier.append(a.submission_id)
                    if a.team_name in targets and a.team_name not in found:
                        found[a.team_name] = a.submission_id
            time.sleep(sleep)
        print(f"[discover] hop {hop}: visited={len(visited)} names={len(name_to_sub)} found={len(found)}/{len(targets)}")
        if len(found) >= len(targets):
            break
        frontier = list(set(next_frontier))[:breadth_cap]

    return found, name_to_sub


def fetch_replays(manifest, out_dir, per_player=20, sleep=0.1):
    """For each {name: submission_id} in manifest, download up to per_player
    most-recent episode replays into out_dir/<safe_name>/episode-<id>-replay.json.
    Writes out_dir/<safe_name>/manifest.json recording which seat (0/1) that
    team occupied in each downloaded episode -- needed to align actions later.
    """
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    os.makedirs(out_dir, exist_ok=True)
    summary = {}
    for name, sub_id in manifest.items():
        safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name).strip()
        player_dir = os.path.join(out_dir, safe)
        os.makedirs(player_dir, exist_ok=True)

        try:
            eps = api.competition_list_episodes(sub_id)
        except Exception as e:
            print(f"  [{name}] list_episodes failed: {e}")
            continue

        eps_sorted = sorted(eps, key=lambda e: e.create_time, reverse=True)
        eps_sorted = [e for e in eps_sorted if str(e.state) == "EpisodeState.COMPLETED" or "COMPLETED" in str(e.state)]
        chosen = eps_sorted[:per_player]

        seat_manifest = []
        for ep in chosen:
            seat = next((a.index for a in ep.agents if a.submission_id == sub_id), None)
            if seat is None:
                continue
            out_path = os.path.join(player_dir, f"episode-{ep.id}-replay.json")
            if not os.path.exists(out_path):
                try:
                    api.competition_episode_replay(ep.id, path=player_dir, quiet=True)
                except Exception as e:
                    print(f"  [{name}] episode {ep.id} download failed: {e}")
                    continue
                time.sleep(sleep)
            replay_path = os.path.join(player_dir, f"episode-{ep.id}-replay.json")
            seed = None
            try:
                with open(replay_path, encoding="utf-8") as replay_file:
                    replay = json.load(replay_file)
                seed = replay.get("info", {}).get("seed")
                if seed is None:
                    seed = replay.get("configuration", {}).get("seed")
            except (OSError, ValueError):
                pass
            seat_manifest.append({
                "episode_id": ep.id,
                "seat": seat,
                "seed": seed,
                "create_time": str(ep.create_time),
            })

        with open(os.path.join(player_dir, "manifest.json"), "w") as f:
            json.dump(seat_manifest, f, indent=2)
        summary[name] = len(seat_manifest)
        print(f"[{name}] downloaded {len(seat_manifest)} episodes -> {player_dir}")

    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--seed-submission", type=int, default=None,
                     help="Our own submission id to BFS from (required for --discover)")
    ap.add_argument("--targets", default="", help="Comma-separated team names to find")
    ap.add_argument("--manifest", default=MANIFEST_DEFAULT)
    ap.add_argument("--out", default=OUT_DIR_DEFAULT)
    ap.add_argument("--per-player", type=int, default=20)
    args = ap.parse_args()

    if args.discover:
        targets = [t.strip() for t in args.targets.split(",") if t.strip()]
        found, all_names = discover(args.seed_submission, targets)
        with open(args.manifest, "w") as f:
            json.dump(found, f, indent=2, ensure_ascii=False)
        print(f"\nWrote {len(found)}/{len(targets)} target submission ids -> {args.manifest}")
        missing = set(targets) - set(found)
        if missing:
            print(f"NOT FOUND (try more hops or larger breadth_cap): {missing}")

    if args.fetch:
        with open(args.manifest) as f:
            manifest = json.load(f)
        fetch_replays(manifest, args.out, per_player=args.per_player)


if __name__ == "__main__":
    main()
