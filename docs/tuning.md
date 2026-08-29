# Compact CMA-ES protocol

MapleLeaf 7.2 treats CMA-ES as a threshold calibrator, not as the policy.
`tuning/space.py` contains 16 dimensions covering weed recovery, market lead,
market-lead phase and batch size, premium-shift
timing and quantity, mirror tolerance, sell-order urgency, opportunistic batch
size, and terminal liquidation timing.

## Objective

Every candidate plays common seeds in both seats against the same baseline.
For terminal score deltas `d`, the optimizer maximizes:

```text
mean(d) - 0.25 * population_std(d) - 0.05 * max(0, -min(d))
```

The variance term favors steady improvements. The downside term prevents a
large average gain from hiding one catastrophic game.

## Workflow

1. Inspect the search space with `py -m tuning.cmaes --dry-run`.
2. Run a short `--front-run-only` search against `submission_main_v7_1.py`.
3. Materialize the checkpoint with `py -m tuning.build_candidate`.
4. Benchmark the file-loaded candidate against `main.py` on fresh seeds.
5. Benchmark the survivor against `submission_main_v7_1.py` and the current
   #1 replay-policy corpus.
6. Package only after the file-path loader test and a full 720-turn episode
   finish with `DONE` status for both players.

Optimizer fitness is a discovery signal, not promotion evidence. A checkpoint
must never be copied directly into `main.py` without the independent gate.
