"""
train_bc.py — MapleLeaf 4.1: Behavioral cloning from top-player replay JSONs.

Downloads replays via:
    kaggle competitions replay <EPISODE_ID> -p ./replays/

Usage:
    python train_bc.py --replays ./replays/ --out weights_bc.npz

    # Learn from both players (2× data):
    python train_bc.py --replays ./replays/ --both-players --min-score 80000

    # Fine-tune with more epochs:
    python train_bc.py --replays ./replays/ --epochs 80 --lr 3e-4

The output weights_bc.npz matches PolicyNet's format (W1,b1,W2,b2,Wp,bp).
To use in an agent: PolicyNet().load('weights_bc.npz').act_greedy(encode_obs(obs))
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

sys.path.insert(0, os.path.dirname(__file__))
from model import encode_obs, ACTIONS, OBS_DIM, N_ACTIONS, PolicyNet


# ── Action mapping ─────────────────────────────────────────────────────────────

# Normalise every ACTIONS entry to a string-tuple for comparison, since JSON
# serialises integers (e.g. the "5" in PICKUP WHEAT 5) as strings.
_EXACT = {tuple(str(x) for x in a): i for i, a in enumerate(ACTIONS)}

# Actions whose base verb always maps to a fixed index regardless of extra args.
# PICKUP: any item/qty → index 18 (PICKUP WHEAT 5 approximation)
# FEED: 'FEED WHEAT' appears in replays but our ACTIONS only has bare 'FEED'
_VERB_FALLBACK = {
    a[0]: i
    for i, a in enumerate(ACTIONS)
    if a[0] in ("PICKUP", "FEED")
}


def _farmer_to_idx(farmer):
    """Map a replay farmer action list → ACTIONS index, or None to skip.

    Exact match is tried first. PICKUP and FEED with any extra arguments
    (e.g. ['FEED', 'WHEAT'], ['PICKUP', 'SHEEP', 1]) fall back to the base
    verb index. PLACE and HIRE are not in ACTIONS and are skipped.
    """
    if isinstance(farmer, str):
        farmer = [farmer]
    if not farmer:
        return 0  # treat empty as PASS

    norm = [str(x) for x in farmer]
    key = tuple(norm)

    if key in _EXACT:
        return _EXACT[key]
    base = norm[0]
    if base in _VERB_FALLBACK:
        return _VERB_FALLBACK[base]
    return None   # PLACE, HIRE, etc. — skip


# ── Replay parser ──────────────────────────────────────────────────────────────

def parse_replay(path, min_score=0.0, both_players=False):
    """Extract (obs_vec, action_idx) pairs from one replay JSON.

    Parameters
    ----------
    path        : path to a replay .json file
    min_score   : skip a player whose final reward is below this threshold
    both_players: if True, extract from both players; otherwise only the winner

    Returns
    -------
    obs  : float32 ndarray of shape (N, OBS_DIM)
    acts : int64  ndarray of shape (N,)
    """
    with open(path) as f:
        data = json.load(f)

    steps = data.get("steps", [])
    if not steps:
        return np.empty((0, OBS_DIM), np.float32), np.empty(0, np.int64)

    # Determine which players to learn from using top-level rewards field
    top_rewards = data.get("rewards") or [None, None]
    r = [float(v or 0) for v in top_rewards]

    if both_players:
        players = [j for j in (0, 1) if r[j] >= min_score]
    else:
        winner = 0 if r[0] >= r[1] else 1
        players = [winner] if r[winner] >= min_score else []

    if not players:
        return np.empty((0, OBS_DIM), np.float32), np.empty(0, np.int64)

    obs_list, act_list = [], []

    for player in players:
        # The replay stores obs[i] = state AFTER action[i] was applied.
        # For BC training we want (obs_before_action[i], action[i]) pairs,
        # which equals (obs[i-1], action[i]).  Shift by one step here.
        prev_obs = None
        for step_entry in steps:
            if len(step_entry) <= player:
                prev_obs = None
                continue
            entry = step_entry[player]

            action_dict = entry.get("action")
            obs_dict    = entry.get("observation")

            # pair: previous step's observation + current step's action
            if prev_obs is not None and action_dict is not None:
                farmer = action_dict.get("farmer")
                if farmer:
                    idx = _farmer_to_idx(farmer)
                    if idx is not None:
                        try:
                            vec = encode_obs(prev_obs)
                        except Exception:
                            pass
                        else:
                            obs_list.append(vec)
                            act_list.append(idx)

            prev_obs = obs_dict  # advance the sliding window

    if not obs_list:
        return np.empty((0, OBS_DIM), np.float32), np.empty(0, np.int64)

    return np.stack(obs_list), np.array(act_list, dtype=np.int64)


# ── Dataset builder ────────────────────────────────────────────────────────────

def build_dataset(replay_dir, min_score=0.0, both_players=False):
    paths = sorted(Path(replay_dir).glob("*.json"))
    if not paths:
        sys.exit(f"No .json files found in: {replay_dir}")

    all_obs, all_acts = [], []
    n_skipped = 0

    for p in paths:
        try:
            obs, acts = parse_replay(p, min_score=min_score, both_players=both_players)
        except Exception as e:
            print(f"  [skip] {p.name}: {e}")
            n_skipped += 1
            continue

        if len(obs) == 0:
            print(f"  [skip] {p.name}: below min_score or no matchable actions")
            n_skipped += 1
            continue

        all_obs.append(obs)
        all_acts.append(acts)
        print(f"  [ok]   {p.name}: {len(obs)} samples  (winner score: {Path(p).stem})")

    if not all_obs:
        sys.exit("No usable replays found.")

    X = np.concatenate(all_obs, axis=0)
    y = np.concatenate(all_acts, axis=0)

    print(f"\nDataset: {len(X):,} samples from {len(all_obs)} replays ({n_skipped} skipped)")

    # Class distribution summary
    counts = np.bincount(y, minlength=N_ACTIONS)
    print(f"{'idx':<4} {'action':<25} {'count':>7}  {'%':>6}")
    for i, (a, c) in enumerate(zip(ACTIONS, counts)):
        if c == 0:
            continue
        label = a[0] + (f" {a[1]}" if len(a) > 1 else "")
        print(f"  {i:<3} {label:<25} {c:>7,}  ({100*c/len(y):>5.1f}%)")

    return X, y


# ── PyTorch model (matches PolicyNet architecture exactly) ─────────────────────

class BCNet(nn.Module):
    """2-layer MLP matching model.py's PolicyNet for weight-compatible export."""

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(OBS_DIM, 256), nn.ReLU(),   # net.0 / net.1
            nn.Linear(256, 256),     nn.ReLU(),   # net.2 / net.3
            nn.Linear(256, N_ACTIONS),             # net.4
        )

    def forward(self, x):
        return self.net(x)

    def export(self, path):
        """Save weights in PolicyNet-compatible .npz format."""
        sd = {k: v.cpu().numpy() for k, v in self.state_dict().items()}
        pol = PolicyNet()
        pol.W1 = sd["net.0.weight"]
        pol.b1 = sd["net.0.bias"]
        pol.W2 = sd["net.2.weight"]
        pol.b2 = sd["net.2.bias"]
        pol.Wp = sd["net.4.weight"]
        pol.bp = sd["net.4.bias"]
        pol.save(path)


# ── Training ───────────────────────────────────────────────────────────────────

def train(X, y, epochs=40, lr=1e-3, batch=256, device=None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nTraining on {device}  |  samples={len(X):,}  epochs={epochs}  lr={lr}")

    Xt = torch.tensor(X, dtype=torch.float32, device=device)
    yt = torch.tensor(y, dtype=torch.long, device=device)

    model = BCNet().to(device)
    opt = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    n = len(Xt)

    for epoch in range(1, epochs + 1):
        perm = torch.randperm(n, device=device)
        Xs, ys = Xt[perm], yt[perm]
        total_loss = total_correct = 0

        for i in range(0, n, batch):
            xb, yb = Xs[i:i+batch], ys[i:i+batch]
            logits = model(xb)
            loss = criterion(logits, yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item() * len(xb)
            total_correct += (logits.argmax(1) == yb).sum().item()

        if epoch % 5 == 0 or epoch == 1 or epoch == epochs:
            print(f"  epoch {epoch:3d}/{epochs}  "
                  f"loss={total_loss/n:.4f}  "
                  f"acc={100*total_correct/n:.1f}%")

    return model


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="MapleLeaf 4.1 — Behavioral cloning from replay JSONs"
    )
    ap.add_argument("--replays",      required=True,
                    help="Folder containing replay .json files (100 recommended)")
    ap.add_argument("--out",          default="weights_bc.npz",
                    help="Output weights file (default: weights_bc.npz)")
    ap.add_argument("--epochs",       type=int,   default=40)
    ap.add_argument("--lr",           type=float, default=1e-3)
    ap.add_argument("--batch",        type=int,   default=256)
    ap.add_argument("--min-score",    type=float, default=0.0, dest="min_score",
                    help="Minimum player final score to include (default: 0)")
    ap.add_argument("--both-players", action="store_true",
                    help="Learn from both players, not just the winner")
    ap.add_argument("--device",       default=None,
                    help="PyTorch device override (e.g. 'cpu', 'cuda:0')")
    args = ap.parse_args()

    print("=== MapleLeaf 4.1 — Behavioral Cloning ===")
    print(f"Replays      : {args.replays}")
    print(f"Output       : {args.out}")
    print(f"Both players : {args.both_players}")
    print(f"Min score    : {args.min_score:,.0f}")
    print()

    X, y = build_dataset(
        args.replays,
        min_score=args.min_score,
        both_players=args.both_players,
    )

    model = train(
        X, y,
        epochs=args.epochs,
        lr=args.lr,
        batch=args.batch,
        device=args.device,
    )

    model.export(args.out)
    print(f"\nDone. Use weights with:")
    print(f"  from model import PolicyNet, encode_obs")
    print(f"  net = PolicyNet().load('{args.out}')")
    print(f"  action_idx = net.act_greedy(encode_obs(obs))")


if __name__ == "__main__":
    main()
