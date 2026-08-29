# MapleLeaf 7.2

MapleLeaf is a heuristic-first agent for Kaggle's
[Kaggriculture](https://www.kaggle.com/competitions/kaggriculture) simulation.
Version 7.2 keeps a strong deterministic production route, then reacts to the
live observation where the opponent and environment actually change value:
weed recovery, premium-market timing, sell-order impact, opponent production,
shed pressure, terminal liquidation, and public-opening route selection.

CMA-ES is deliberately small. It tunes 16 readable thresholds around the
hand-written policy; it does not search the route or choose among dozens of
on/off overlays.

## Layout

- `main.py` — Kaggle entry point, shared opening, and adaptive route selector
- `anti_route.py` — compressed anti–Crop Dusta production tape
- `heuristics.py` — observation-driven safety and market policy
- `tuning/` — compact search space, CMA-ES runner, and candidate builder
- `tools/` — packaging, benchmarks, and replay analysis
- `tests/` — loader, full-episode, isolation, and tuning regressions
- `docs/` — research notes, rules, and tuning protocol
- `opponents/mapleleaf_6_7.py` — immutable promotion baseline
- `artifacts/reference/` — the original 6.7 submission archive

Historical experiments, raw replay corpora, obsolete PPO code, and old
submission bundles remain recoverable from Git history but are not part of the
active 7.2 tree.

## Setup

```powershell
py -m pip install -r requirements-dev.txt
```

The submission itself uses only Python's standard library.

## Validate

```powershell
py -m unittest discover -s tests -v
py -m tools.benchmark --n 20
py -m tools.build_submission --out artifacts/submission/main.py
```

The submission builder exercises the same file-path loading mechanism used by
Kaggle Environments. This catches failures that direct Python imports miss.

## Tune a small threshold set

```powershell
py -m tuning.cmaes --dry-run
py -m tuning.cmaes --front-run-only --baseline submission_main_v7_1.py --generations 4 --games 10 --workers 8
py -m tuning.build_candidate --checkpoint artifacts/tuning/cmaes-7.2-front-run.json
py -m tools.benchmark --a artifacts/candidate/main.py --b main.py --n 20
```

Do not promote a checkpoint on optimizer fitness alone. Build a standalone
candidate, run fresh-seed head-to-head games against `main.py`, then verify it
against `opponents/mapleleaf_6_7.py`. See [docs/tuning.md](docs/tuning.md).

## Kaggle CLI

Once authenticated (`kaggle auth login`), the useful workflow is:

```powershell
kaggle competitions submissions kaggriculture
kaggle competitions episodes SUBMISSION_ID
kaggle competitions replay EPISODE_ID -p artifacts/replays
kaggle competitions logs EPISODE_ID 0 -p artifacts/logs
```

The official competition requires `main.py` at the archive root and forbids
network ingress/egress during an episode.

## Verified 7.2 gates

On Kaggle Environments 1.32.7, the production `main.py` achieved **20/20 wins**
against the supplied Mapleleaf 7.1 file and **15/20 wins** against 10 paired-seat
exact-seed replays from current #1 player Crop Dusta. The replay opponent is
non-reactive, so this is a reproducible replay-policy benchmark rather than a
claim about private live source. Full results and the CMA-ES checkpoint are in
[docs/progress-2026-08-28.md](docs/progress-2026-08-28.md).
