# MapleLeaf 6.6 tuning notes — what's been found, so we don't re-derive it

## Simulator accuracy (2026-08-22)

- The engine (`kaggle_environments`) is the literal same package Kaggle's
  servers run — not an approximation. Confirmed the live competition is on
  **1.32.7** by reading a fresh episode's `module_version` field directly,
  and upgraded the local install to match exactly.
- Every source of "randomness" in the engine is a `random.Random(seed)`
  object seeded from a value that's recorded in each replay (`info.seed` —
  note: NOT `configuration.seed`, which is deliberately scrubbed to `null`
  so agents can't read it via their own observation; the real value only
  shows up in `info.seed`). Traced this to `kaggle_environments/utils.py`'s
  `resolve_episode_seed()`.
- **Conclusion: the simulator is 100% reconstructable given seed + source —
  there is no true unresolvable randomness in the mechanics.** The only
  thing that can't be pre-simulated is a live opponent's actual decision
  logic (not a pseudo-random input — a private, possibly-adaptive strategy
  we don't have code for).
- A residual effect that LOOKS like noise but isn't: `_end_of_day()` spawns
  weeds for both farms from **one shared RNG stream, consumed sequentially**
  (player 0's farm rolls first, then player 1's, every day). So two
  identical-strategy agents in different seats will deterministically
  diverge slightly — same seed, same result every time (verified: 4 repeat
  runs, `PYTHONHASHSEED` pinned or not, always identical) — it's a real,
  permanent seat-order effect, not run-to-run randomness. `benchmark.py`
  already runs both orientations and averages, which cancels this out.

## Bug found and fixed: stale market-price model in overlays.py (2026-08-22)

`overlays.py`'s own `_MARKET_PARAMS` was a hand-copied snapshot that had
drifted stale relative to a real 1.32.7 engine change: CARROT/TOMATO/EGG's
scarcity curve switched from `log`/`linear` to a `hinge` shape (linear up to
a knee at `T`, then `+ 8*(x/T - 1)^2` runaway past it), and CARROT's
`below_target` roughly doubled (0.20 → 1.00). Found by reading the installed
engine's actual source
(`kaggle_environments/envs/kaggriculture/kaggriculture.py`) instead of
continuing to trust the copy. **Fixed by importing the real
`MARKET_PARAMS`/`SHOPS`/`market_price`/`PRICE_FLOOR`/`MARKET_I0` directly
from the engine module** rather than reimplementing them — this class of
drift can't recur as long as the installed package stays in sync with
production (check via `benchmark.py`'s `_KNOWN_GOOD_VERSION`).
**Takeaway: prefer importing real engine constants over hand-copying them,
anywhere else this project does that.**

## Opponent pool methodology: use the LEAST self-consistent top players

route_mining.py's self-consistency check (majority-vote agreement across a
player's real games) ranks how "clonable" vs. "genuinely adaptive" each top
player is. Full ranking from the 2026-08-22 top-20 survey (`routes_6_6/_summary.json`):

| Player | Avg. self-consistency |
|---|---|
| Crop Dusta | 49.5% (least repeatable) |
| Arman Tuganbaev | 50.5% |
| Subramanya N | 50.7% |
| Kaan Dınız | 51.3% |
| Seb (allegedly) | 55.4% |
| MiMi | 61.7% |
| Ryo Hasegawa | 64.1% |
| Excluding | 68.0% |
| カワシギ | 72.4% |
| Izzoudine Mohamed KANTA | 76.2% |
| fufufukakaka | 76.8% |
| James Holland | 79.8% |
| ActiveMusyoku | 80.2% |
| Lucien de Rubempre | 81.1% |
| peikopon | 83.1% |
| SaiKushal185 | 85.6% |
| Xiaowenhao404 | 86.4% |
| Efe Can Celiksoy | 88.2% |
| ReCurSiON | 94.2% |
| Kobe BRYANT | 95.4% (most repeatable) |

**Decision: `evolve.py`'s opponent pool uses the bottom 8 (Crop Dusta through
Excluding, all <70%), 3 real episodes each, instead of 1 episode from all 20
equally.** Rationale: the highly-consistent players (ReCurSiON, Kobe BRYANT)
are close to clonable scripts — beating their replay is a weaker signal than
beating a genuinely adaptive player's real game, even non-reactively. This
is `evolve.py`'s `_least_consistent_players()` / `_build_opponent_specs()`.
**If re-running the Phase A player survey later (ladder reshuffles daily),
recompute this ranking from the fresh `_summary.json` rather than reusing
this snapshot — it will drift.**

## Round 1 (3-opponent pool, promoted to main.py 2026-08-22)

- Opponent pool: unmodified 6.5, legacy 6.3, one ReCurSiON real replay.
- 53 generations, ~65 min wall-clock, plateaued at fitness 3335.7
  (mean_delta +4,883, std_delta +4,421).
- Validated: **20/20 wins, +2,303/game vs. unmodified 6.5**; 36/40 wins vs.
  a real Ryo Hasegawa replay (+6,626/game — but see the adaptive-opponent
  caveat below, this number is optimistic).
- Winning config: premium market-lead preemption ON, impact-based sell-slot
  ranking ON; fertilizer relay, price-floor guard, opportunistic sell all
  tuned OFF. Full params baked into `main.py`'s `_BAKED_*` constants.
- **Caveat on any non-reactive-replay comparison**: `benchmark.py`'s
  `replay:` mode blindly replays a real player's exact recorded actions —
  it does not react to what our candidate does. For a player we already
  measured as low self-consistency (adaptive), that recorded trace reflects
  what they did against whoever they actually faced, not how they'd react
  to us. Treat those numbers as "we extract more value from the same
  realistic market conditions," not as a win-probability estimate against
  that player head-to-head. Only the live ladder is a fully faithful test
  against a genuinely adaptive opponent.

## Round 1 → Round 2 fixes (both applied before round 2's real run)

1. **Opponent pool widened + hardened**: 3 opponents → 26 (2 script + the
   8 least-consistent top players × 3 episodes each — see methodology
   above). Makes it much harder for CMA-ES to find a params vector that
   only exploits quirks of a narrow, easy-to-predict test set.
2. **Parallelization fixed**: v1 parallelized at the CANDIDATE level (one
   pool task per population member) — wasted most of a 110-worker pool
   whenever popsize (24) < workers (110), since only popsize-many workers
   ever had anything to do per generation. v2 flattens every (candidate,
   opponent, seed, orientation) combination into one task list so all
   workers stay busy regardless of population size.
3. **Stale price-model bug fixed** (see above) before the real round-2 run
   — round 2's first attempt was restarted once already to pick this fix up.
4. **Stagnation noise floor recalibrated**: v1 used $150 based on a guess;
   real per-generation noise turned out to be $100-300 with only 18
   games/candidate, so v1's auto-stop never cleanly triggered and had to be
   stopped manually. v2 uses $100 with more games/candidate (should be
   less noisy per generation, though this hasn't been empirically
   re-verified against the new, harder opponent pool yet).

## Operational lesson: PID tracking for background evolve.py runs

Using `pgrep -f "<cmd>" | sort -n | head -1` to find the "main" evolve.py
process after a `nohup ... & disown` launch is unreliable — got a stale/
wrong PID twice this session, causing a watcher script to fire against a
checkpoint that hadn't been written yet (a garbage "benchmark" result had
to be thrown out). **Fix that worked**: `ps -eo pid,ppid,cmd | grep '<cmd>' | awk '$2==1 {print}'`
— the real long-running process is a direct child of PID 1 after disown;
grep/pgrep alone can match transient wrapper processes with lower PIDs that
exit almost immediately.

## Next things worth trying (not yet done)

- CMA-ES restarts (IPOP/BIPOP) if a run plateaus — a single run can get
  stuck in one basin.
- Let the optimizer choose *which* items get front-run at all, not just
  their priority order.
- A literal "steadier growth" fitness refinement: score on the trend across
  in-game day-10/20/29 checkpoints, not just the terminal delta.
- Re-run the Phase A route-mining survey periodically — the ladder
  reshuffles daily and today's "nobody beats Filip's route" result isn't
  permanent.
- Revive `train.py`/`model.py`'s dormant PPO pipeline for a genuinely
  learned (not scripted) policy, if scripted-route cloning keeps hitting
  diminishing returns as the ladder gets more adaptive.
