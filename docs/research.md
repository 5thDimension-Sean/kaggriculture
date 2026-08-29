# Kaggriculture research brief for MapleLeaf 6.8

Research was refreshed on 2026-08-28 from the public competition pages,
official environment source, public notebooks, discussions, and the local
Kaggle Environments 1.32.7 implementation.

## Reliable facts from the environment

The official environment documents a 720-turn, two-player season with a shared
dynamic market, ten market orders per turn, a 100-item non-seed shed cap, public
opponent farms, private sheds, and silent no-ops for invalid actions. Farmer
actions execute before market orders, which makes final-turn drop-and-sell
recovery possible. Sources:

- [Official Kaggriculture environment guide](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md)
- [Official rules and market mechanics](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/README.md)
- [Reference interpreter](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py)
- [Competition overview](https://www.kaggle.com/competitions/kaggriculture/overview)

`heuristics._verify_against_live_engine()` confirms that the submission-safe
hand-copied price model matches version 1.32.7 exactly.

## Public-meta signals used

The strongest public agents are predominantly deterministic production tapes
with targeted observation-driven market logic. Public discussion also notes
that early routes are often identical while interaction matters most at shared
market dumps. That supports a hybrid: preserve a high-output route and spend
complexity on state-dependent market and recovery decisions.

- [Findings from Zero to Top Meta](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta)
  emphasizes engine edge cases, route restoration after weeds, conditional
  policy memory, market-meta evolution, and disciplined local evaluation.
- [Conditional Memory](https://www.kaggle.com/code/kaitofukami/177-180-fresh-top-30-v21-1-conditional-memory)
  supports short-lived state that is reset every episode rather than a large
  learned policy.
- [Premium Market Lead](https://www.kaggle.com/code/boatlee/v16-rc5-high-score-8c-4s-premium-market-lead)
  supports front-running premium dumps when the opponent is near-mirroring or
  visibly ready to supply the same product.
- [Breaking the Tie](https://www.kaggle.com/code/andrewsokolovsky/kaggriculture-breaking-the-tie/output?scriptVersionId=341994976)
  demonstrates market-inventory inference, guarded multi-horizon preemption,
  terminal liquidation, and observation-driven final-turn harvesting.
- [Trajectory-copying discussion](https://www.kaggle.com/competitions/kaggriculture/discussion/732613)
  identifies the shared market as the main channel where live reactions change
  the value of an otherwise stable production route.
- [RL ceiling discussion](https://www.kaggle.com/competitions/kaggriculture/discussion/736917)
  reports that behavior cloning can be competitive while PPO is noisy and can
  regress, reinforcing the choice to avoid reviving the repository's stale PPO
  pipeline for this draft.

## 6.8 design consequences

1. Keep the deterministic production route because it is the strongest proven
   source of action efficiency in this repository.
2. Repair only route-breaking weeds and replay the displaced local sequence.
3. Front-run known future sells, with explicit repayment so the route does not
   double-sell later.
4. Use public opponent production and near-mirror confidence to gate broader
   premium shifts.
5. Sort competing sell orders by estimated price impact and demand recovery.
6. Sell opportunistic premium surplus using item-specific reserve fractions.
7. Liquidate remaining shed inventory in the final phase. A public-style
   final-turn movement controller was implemented and rejected locally: it
   went 2-15-3 and lost $140/game against the identical policy without it.
8. Restrict CMA-ES to 12 interpretable thresholds and require a separate
   promotion benchmark.

Public notebook bodies are partly sign-in gated. Only publicly rendered
metadata/code and independently verifiable mechanics were used; no private
Kaggle data or credentials are embedded in the repository.
