# Aether 1.0

Aether is a full rewrite of the Kaggriculture agent around public replay
behavior from the current leaderboard leaders: tetsuya, Driz Lo, and MtN.
It does not identify players or use hidden state.

## Policy

- Seat 0 uses tetsuya's production geometry and forks at the first day
  boundary from public market inventory.
- `WOOL <= 9995` selects the animal-pressure branch. This exact boundary
  separated the sampled Driz Lo and MtN seat-0 route families.
- Otherwise `MILK <= 9995` selects tetsuya's melon-heavy dairy-pressure
  branch; the remaining state selects its strawberry-heavy crop branch.
- Seat 1 uses a per-action majority reconstruction of MtN's four public
  games. That route measured 99.2% self-consistency.
- A per-worker delay tracker repairs route-breaking weeds without shifting
  every other worker's schedule.

The evidence and limitations are in
[`docs/aether-1.0-research.md`](docs/aether-1.0-research.md).

## Layout

- `main.py` — Aether runtime and public-state route selector
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
