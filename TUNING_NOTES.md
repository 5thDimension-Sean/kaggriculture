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

## Round 2 (26-opponent, least-consistent-8 pool): NEGATIVE RESULT (2026-08-22)

- 8 generations, ~19 min wall-clock (~140s/gen, consistent). Plateaued
  immediately: best fitness 18,005.8 hit at generation 2, generations 3-8
  all came in below that (17,820-17,978, a ~160 spread) with no new record
  -- a real plateau, not early noise, so the run was stopped manually per
  the 20-minute check-in rather than waiting out the full 20-generation
  auto-stop for what looked like the same flat result.
- **Benchmarked against v1 (current main.py) and LOST: 2/20 games,
  -458/game.** Despite a higher fitness number than round 1 ever reached,
  that fitness is on a different, non-comparable scale (bigger opponent
  pool, bigger score swings from harder opponents) and does not translate
  to winning the actual promotion gate.
- **Root cause**: opponent-pool weighting diluted the regression guard.
  Round 1's pool was `{main_6.5, legacy_6.3, 1 real replay}` -- beating the
  actual baseline was 1/3 of the fitness signal. Round 2's pool was
  `{main_6.6, legacy_6.3, 24 real replays from the 8 hardest players}` --
  beating the baseline dropped to 1/26 (~4%) of the signal. The tuner
  optimized for the new harder pool at the expense of the one matchup that
  actually determines promotion.
- **Verdict: discarded, not promoted.** `main.py` is unchanged from the
  round-1 winner.
- **Fix for a future attempt**: don't let the baseline-regression check
  compete equally with every other opponent in the average -- duplicate
  `main.py` several times in the pool (so it's weighted like 15-20% of the
  signal, not 4%), or score it as a separate hard constraint ("candidate
  fitness = diverse-pool-fitness, but reject/heavily penalize any candidate
  that loses to the current baseline on its own dedicated seed set") rather
  than just one more entry in a flat average. Widening the opponent pool
  for robustness and protecting the regression guard are two different
  needs; round 2 conflated them into one averaged score and lost the
  regression guard as a result.

## Next things worth trying (not yet done)

- Let the optimizer choose *which* items get front-run at all, not just
  their priority order.
- Re-run the Phase A route-mining survey periodically — the ladder
  reshuffles daily and today's "nobody beats Filip's route" result isn't
  permanent.
- Revive `train.py`/`model.py`'s dormant PPO pipeline for a genuinely
  learned (not scripted) policy, if scripted-route cloning keeps hitting
  diminishing returns as the ladder gets more adaptive.

(CMA-ES restarts on plateau and a checkpoint-weighted "steadier growth"
fitness were both DONE in v3 below.)

## MapleLeaf 6.7: three real submission bugs found the hard way (2026-08-22)

6.6 was promoted into main.py after round 1's local validation (20/20 vs.
6.5, +2,303/game) but its ACTUAL Kaggle submission (2026-08-22 20:47) came
back `SubmissionStatus.ERROR` / "Validation Episode failed" — **it never
ran on the real ladder at all**. Chasing this down took three attempts,
each disproven by the next real submission, because every purely-local test
this project had ever written (direct exec, cold-sandbox exec, passing an
already-imported function object to `env.run()`) passed cleanly every time
and never reproduced the failure. **The lesson that mattered most: only
invoking the agent BY FILE PATH — `env.run(["main.py", "main.py"])`, the
same mechanism a real Kaggle submission goes through — reproduces this
whole class of bug locally.** All three fixes below are real and stayed
in; only the third was actually sufficient by itself, but the first two
were also worth doing (a genuine drift-safety fix and a genuine robustness
fix), and none of them mattered until the real one was found.

1. **Attempt 1 (insufficient alone)**: `overlays.py` imported
   `kaggle_environments.envs.kaggriculture.kaggriculture` (an internal
   engine submodule) at module load to source its market-price model.
   Reaching into env internals from a submitted agent is a bad idea
   regardless of whether it was the actual crash cause — replaced with a
   hand-copied constant table, verified byte-exact against the installed
   engine via a new dev-only `overlays._verify_against_live_engine()`.
   Resubmitted → still `SubmissionStatus.ERROR`, same generic message.
2. **Attempt 2 (insufficient alone)**: theorized the two-file
   `main.py`+`overlays.py` structure itself (joined by `import overlays`)
   was the problem, since every single-file version before 6.6 had
   validated fine. Built `make_submission.py`, which inlines `overlays.py`'s
   source into a single merged file via an in-memory `types.ModuleType`
   (needed because main.py and overlays.py have real top-level name
   collisions — `_get`/`_farm`/`_seat`/`_copy_action`/`_SHOP_PRODUCTS` — so a
   flat textual merge would silently clobber them). Resubmitted → still
   `SubmissionStatus.ERROR`.
3. **Attempt 3 (the actual root cause)**: downloaded the validation
   episode's replay directly (`api.competition_episode_replay`) for all
   three failed submissions — each was 2 steps long, both players ERROR at
   step 1, farms still in their pristine step-0 state (the very first
   action never even applied). Reproduced locally for the first time ever
   by invoking `kaggle_environments.make(...).run(["main.py","main.py"])`
   with `debug=True`: `NameError: name '__file__' is not defined`, coming
   from `main.py`'s own `sys.path.insert(0, os.path.dirname(os.path.abspath(
   __file__)))`. Root cause: `kaggle_environments/agent.py`'s
   `get_last_callable()` — the function Kaggle's real grading harness (and,
   confirmed, the local pip package too) uses to load a submitted file by
   path — `exec()`s the file's source into a **bare `{}` globals dict, with
   no `__file__` key at all**. That line has been in main.py only since 6.6
   (added to support `import overlays`), so 6.5 and earlier never hit it —
   completely independent of both of the first two (real, but insufficient)
   theories. Fixed with `if "__file__" in globals(): sys.path.insert(...)`.
   Verified via the real file-path harness (`env.run(["main.py", ...])`,
   debug=True, full 720 steps) before resubmitting → `SubmissionStatus.
   COMPLETE`, publicScore 600.0 (a fresh submission's rating before it's
   played enough ladder games to converge — not directly comparable to an
   established submission's score yet).
   **How to apply**: any future "why does this only fail on Kaggle, never
   locally" mystery should reach for file-path invocation with `debug=True`
   FIRST, not last — it is the only local test that actually matches how a
   submission gets loaded.

`make_submission.py` is now the ONLY way a MapleLeaf submission should ever
be packaged (`python3 make_submission.py --out ... ` then tar just that one
output file as `main.py`) — never `tar czf ... main.py overlays.py`
directly, and never submit dev-mode main.py raw. Its `self_test()` exercises
the real file-path harness automatically on every build.

## Bug found: build_agent.make_agent() shared singleton state with its own opponent (2026-08-22)

While verifying the submission fix, found a SECOND, independent bug while
diffing `build_agent.make_agent(vec)`'s in-process agent against a
file-loaded copy of the exact same candidate for the exact same seed: their
actions diverged at step 215 of a real game (an extra opportunistic SELL
appeared in one but not the other). Root cause: `make_agent()` used real
`import main as _base; import overlays` — real imports are cached as ONE
singleton module in `sys.modules`, SHARED by every agent in the process that
also does a real import of the same module. `benchmark.load_agent(path)`
sets `ns["__file__"] = path` before exec'ing, so any opponent file that
itself contains a bare `import overlays` (main.py always does) hits that
*same* cached singleton — meaning a CMA-ES candidate and an opponent playing
against it in the same worker process were silently sharing mutable
per-seat state (confirmed: `overlays._OPPONENT_TYPE[1]` was being written by
the opponent's own self-classification calls and read back by "our" module
instance). **This means evolve.py's fitness signal was never as clean as
intended whenever a path-based opponent (any real `.py` file, not a replay)
was in the pool — round 1's `{main_6.5, legacy_6.3}` and round 2's `{main_
6.6, legacy_6.3}` pool entries both qualify.** Not re-litigated retroactively
(round 1's winner is still what's live), but v3 onward is clean: `build_agent
.make_agent()` now builds `main`/`overlays` as freshly-exec'd, mutually
isolated `types.ModuleType` instances (reusing `make_submission.
build_merged_source()`) every call, with zero `sys.modules` involvement —
verified by re-running the same diff test post-fix and getting byte-identical
results between the in-process and file-loaded paths.
**How to apply**: never add a real `import main`/`import overlays` back into
any in-process evaluation code path. If a new tool needs to build an agent
in-process, route it through `build_agent.make_agent()` or
`make_submission.build_merged_source()`, never a bare `import`.

## evolve.py v3 (2026-08-22) — fixes round 2's regression-guard dilution + two "next things" from above

Round 2's postmortem (above) identified the real failure: widening the
opponent pool to 26 for diversity diluted the baseline-regression check
(beat the current promoted version) down to ~1/26 (~4%) of the fitness
signal, so the tuner optimized for the wrong thing and lost 2/20 to the
actual baseline on real validation despite a higher raw fitness number.
v3's fixes, all in the same run:

1. **Protected regression guard**: the current baseline (main.py) is no
   longer just one more pool entry — it gets a dedicated seed set sized to
   always be `BASELINE_FRACTION` (25%) of total games/candidate regardless
   of diverse-pool size, PLUS an explicit penalty
   (`REGRESSION_PENALTY_MULT * baseline_mean_delta` when negative) added on
   top if the candidate loses to it on average.
2. **Checkpoint-weighted "steadier growth" scoring**: per-game score is now
   a weighted trend across three in-game checkpoints (steps 239/479/718,
   weights 0.15/0.25/0.60) instead of just the terminal delta — free
   (reads `env.steps`' already-simulated observations, no extra games),
   rewards a candidate that leads throughout the episode over one that's
   only ahead at the final tally.
3. **IPOP-style restarts**: on plateau, doubles popsize and restarts from
   the current best point (up to `--max-restarts`, default 3) instead of
   just stopping — a single CMA-ES run can get stuck in one basin.

Diverse pool unchanged from v2's methodology (legacy 6.3 + 3 real episodes
each from the 8 least self-consistent/most-adaptive top-20 players, per the
methodology section above) — 25 opponents as of this run. See
`evolve_checkpoint_v3.json` / `evolve_v3.log` for live results; only promote
a winner into main.py after it beats the current baseline on a real
`benchmark.py` validation run (same promotion-gate discipline as round 1),
built via `build_agent.write_self_contained_candidate()` (NOT the old
multi-file `write_candidate()`, removed) and verified via
`make_submission.py`-style file-path self-test before ever submitting.

**v3 run 1 result (100 generations, no restarts fired)**: found a checkpoint
whose OWN small-sample (34-game) baseline estimate looked positive
(+104/game), but a real 40-game `benchmark.py` validation showed it actually
**loses** -214/game to the current 6.7 baseline — close-margin, statistical
noise, not a real win. NOT promoted. Root cause of the "no restarts fired"
part: the stagnation detector compared raw per-generation `gen_best` values,
which fluctuate by more than `NOISE_FLOOR` from CMA-ES's own sampling noise
even at a genuine plateau — so it never once triggered in 100 generations.
Fixed to compare the RUNNING RECORD (`best_fitness_history`) instead: "has a
new best been set in the last `STAGNATION_WINDOW` generations", which is
what "plateaued" actually means. **v3 run 2** (same config, fixed detector)
found a genuine IPOP restart at gen ~20-25, but converged to essentially the
same fitness ceiling (~6,600-6,700) as run 1 — two independent runs landing
in the same place is a real signal that this 40-dim search space (fixed
route) has been largely exhausted by round 1's original tuning, not a fluke
of one run.

## Route re-survey (2026-08-23): still no win, but real signal about the ladder's shape

Per the plateau above, paused CMA-ES tuning to re-check whether a stronger
backbone route now exists (the Phase A survey data was ~1 day stale, and the
ladder reshuffles daily). Re-ran `download_replays.py` with a much deeper
per-player sample (35 games, up from 3-20) and parallelized
`route_mining.py` across players (`--workers N`, new) to make this
practical to re-run — a full 22-player scan with ~1.1GB/player of replay
JSON took several minutes even at 22-way parallelism.

Result: **Kobe BRYANT's earlier "98.4%, but only n=3 — too thin to trust"
qualification evaporated with a deeper sample** (92.6% at n=8) — confirms
that flag was right to be skeptical. **Three players newly qualified**:
ReCurSiON (96.6%/97.4%, was already known), and two brand-new top-20
entrants, mandgeee (99.4%/99.5%) and "u" (99.2%/99.1%) — both near-perfect
scripted bots, even more consistent than Filip's own 98.7%/99.3%. All three
have near-symmetric P0/P1 routes (98-99% step-identical, like Filip's), so
no dual-route architecture was needed to test them.

**All three lost to Filip's route**, including a bare-route (no overlays)
head-to-head for ReCurSiON specifically, ruling out "the overlay tuning is
mismatched to the new route" as an excuse:
- mandgeee: -16,524/game (0/20) with overlays
- u: -15,799/game (0/20) with overlays
- ReCurSiON: -1,453/game (5/20) with overlays, -1,828/game (5/20) bare-route

**Real structural finding, not just a rejection**: the most-clonable players
(mandgeee/u, 99%+ consistency) sit LOWER on the actual leaderboard
(2,735-2,800) than the genuinely adaptive players we can't clone at all
(Ryo Hasegawa/Crop Dusta/Subramanya N, 3,000-3,100+, all under 65%
consistency). Clonability and route strength appear inversely correlated on
this ladder -- Filip being both strong AND highly consistent looks like a
rare exception, not a pattern likely to repeat on a re-survey.
**How to apply**: don't expect a future re-survey to find a better route
unless the ladder's TOP players (not just newcomers) become more
consistent -- that would be a bigger shift than day-to-day reshuffling
typically produces. The remaining real lever for a route-quality jump is
`train.py`/`model.py`'s dormant PPO pipeline (a learned, not cloned, policy),
not more mining.

## Bug found: benchmark.py's route-only mode was silently broken (2026-08-23)

While isolating route strength from overlay-tuning effects (bare-route
ReCurSiON vs. bare-route Filip), found `make_route_only_agent()` called
`_weed_repair_action(obs, action, _ACTIONS, step)` -- FOUR args -- against a
function whose real signature is `_weed_repair_action(obs, action, step)`
-- THREE. The TypeError was silently caught by the wrapper's own
`except Exception: return PASS` fallback, so every route-only agent this
project has EVER benchmarked was actually a do-nothing PASS-bot (confirmed:
both sides finished a full 720-step game at a flat, unchanged 3,000 starting
money before the fix). Fixed by dropping the extra `_ACTIONS` argument.
**How to apply**: any historical "route-only" / "how much does market logic
contribute" comparison in this project's memory or old commit messages was
measuring against a broken baseline -- don't trust the specific numbers,
only the fixed version going forward.

## Route re-survey (2026-08-24): ladder reshuffled, still no win

One day after the 2026-08-23 re-survey, re-checked the CURRENT top-of-leaderboard
for a stronger clonable route. The roster changed meaningfully: 9 of the top 20
names weren't in the prior 22-player survey (junseok lee #4, Say My Name ? #6,
Yizuki #11, test_money #13, Kazama Yusuke #14, satoooh #15, Ömer Faruk Yüce #16,
Ueddy #17, Egor Trushin #18), and Filip Strzalka (the current backbone donor)
dropped off the visible top 20 entirely.

Investigated 7 of the 9 (BFS discovery from our own submission hit Kaggle API
rate limits within 3 hops for `Kazama Yusuke`, `Yizuki`, and re-resolving
`Filip Strzalka` himself -- not chased further, worth a follow-up if throttling
clears). Self-consistency on real replays:

- junseok lee 71.7%/91.2% (unusually asymmetric between seats), Say My Name ?
  74.4%/81.1%, Ömer Faruk Yüce 77.2%/75.9%, Ueddy 90.1%/87.2%, Egor Trushin
  93.3%/93.5% -- all too adaptive to clone, same pattern as most top-ranked
  players historically.
- **satoooh** and **test_money** qualified (~99%/99%), re-checked on a deepened
  sample (satoooh n=18/17, test_money n=21/14 both seats) specifically to rule
  out the Kobe BRYANT-style thin-sample false positive -- held at 99.2-99.3%
  both seats, genuinely scripted.

Head-to-head vs. the current backbone (`benchmark_vs_player.py --candidate
main.py`, replaying each player's own real recorded actions, 70 games/seat):
- satoooh: main.py wins 70/70, +15,930/game
- test_money: main.py wins 70/70, +16,122/game

Both lose as decisively as mandgeee/u did on 2026-08-23 (-16,524/-15,799/game).
**Same structural finding holds one day later**: the most self-consistent/
clonable players sit lower on this ladder and lose decisively to Filip's route;
no basis to swap the backbone right now.
**How to apply**: don't re-run this survey again on a whim -- only worth
repeating if `Kazama Yusuke`/`Yizuki` become resolvable (rate-limited this
round) or if the top-of-leaderboard roster shows another significant reshuffle.
The real lever for a route-quality jump is still `train.py`/`model.py`'s
dormant PPO pipeline, not more mining (per the 2026-08-23 note above).
