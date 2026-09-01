# Aether 1.0

Aether is a full rewrite of the Kaggriculture agent around public replay
behavior from the current leaderboard leaders: tetsuya, Driz Lo, and MtN.
It does not identify players or use hidden state.

## Policy

- Both seats use a per-action majority reconstruction of MtN's four public
  seat-1 games. That logistics route measured 99.2% self-consistency and
  transfers directly because farm coordinates are player-local.
- Workers follow the seat-1 rule of thumb: establish five specialized hands,
  keep animal care and crop watering continuous, and synchronize pickup,
  placement, harvest, and market replenishment instead of making isolated
  greedy moves.
- Seat 0 copies the seat-1 tape exactly: no direction transform, crop fork,
  market reordering, or quantity change, and no runtime deviation of any
  kind. The action for a given step depends only on `step`, never on either
  seat's own farm/tile state, so both seats issue byte-identical actions on
  every step of every episode.
- Market order positions are a cash-flow invariant: sales, purchases, and
  hires stay in their demonstrated slots because an early sale may finance a
  later action in the same turn.
- An earlier version added a per-worker delay to dodge weeds that randomly
  block a scheduled build/plant tile. It was removed: `weedSpawnChance` in
  the real environment spawns weeds independently per farm, so the delay
  desynchronized seat 0 from seat 1 (confirmed via the real Kaggle validation
  episode for submission 55929599 -- episode 104481488 -- which showed
  460/720 divergent steps and a 36,988 vs. 43,951 final-reward gap between
  the two seats of the identical agent). See
  `tests/test_agent.py::test_action_ignores_farm_tile_state`.

The evidence and limitations are in
[`docs/aether-1.0-research.md`](docs/aether-1.0-research.md).

## Layout

- `main.py` — Aether runtime and exact seat-1-to-seat-0 logistics copy
- `aether_routes.py` — generated, compressed route library
- `tools/build_aether_routes.py` — reproducible route generator
- `tools/analyze_top_routes.py` — route divergence and threshold analysis
- `tools/build_submission.py` — single-file package builder and loader test
- `tests/` — branch, loader, and full-episode regression tests

## Validate and package

```powershell
py -m unittest discover -s tests -v
py -m tools.benchmark --a main.py --b opponents/mapleleaf_6_7.py --n 10
py -m tools.build_submission --out artifacts/submission/main.py
tar -czf artifacts/aether-1.0.tar.gz -C artifacts/submission main.py
```

The Kaggle artifact contains one root-level `main.py` and uses only Python's
standard library at runtime.
