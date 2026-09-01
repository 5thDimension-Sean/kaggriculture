# MapleLeaf Improvement Notes

## Current State (as of 2026-08-08)

| Model | Games | W/L | Avg win margin | Avg loss margin |
|-------|-------|-----|---------------|-----------------|
| 4.7   | 96 total | 75W/21L (~78%) overall | — | — |
| 4.7   | 20 recent | 10W/10L (50%) recent | +3,228 | -2,800 |
| 5.0   | 8     | 7W/1L  (87%) | +23,437 | -1,127 |

**Context:** 4.7 was strong overall (75W/21L, ~2946 ELO) but has been losing more
recently as new stronger models entered the competition. The 20-game sample analyzed
is a "hardest recent opponents" slice — the losses reflect the current meta, not
overall model weakness.

**5.0 early signal is strong** but only 8 games — too early to be confident.
Real test: does 5.0 hold against the same opponents now beating 4.7?

---

## The #1 Vulnerability (both models)

**Heavy wheat sellers beat us every time.**

| Model | Opp wheat in WINS | Opp wheat in LOSSES | Delta |
|-------|-------------------|---------------------|-------|
| 4.7   | 447               | 1,059               | -612  |
| 5.0   | 548               | 1,899               | -1,351 |

When the opponent sells 1,000+ wheat (or 1,899 like Yonatan Nemtsov), they win.
Both models sell a fixed amount of wheat regardless — zero adaptation.

### Why this happens
- NPC demand keeps wheat prices rising throughout the game (25 → 50+)
- Heavy wheat sellers (e.g. Yonatan: 1,899 wheat; lucaskna: 1,314) ride this curve
- They buy wheat from town early (cheap) and sell mid-to-late (expensive) — arbitrage
- Our routes don't detect or respond to this pattern

### Possible fix
Detect heavy wheat activity early via cumulative wheat sold by opponent (observable
indirectly: if wheat price is *not* dropping despite our own wheat sells, opp is also
selling wheat heavily OR buying it). When detected:
- Shift sell priority AWAY from wheat (de-prioritise in impact_score)
- Front-load MELON/MILK/WOOL while those prices are uncontested
- This is purely an ordering change — safe, no new sells, no quantity changes

---

## The Melon Gap

5.0 sells **only 66 melon** per game. Top opponents sell 91–133.
At base price 250, that's ~(100–66) × 250 = **+8,500 revenue** left on the table.

4.7 also sells exactly 144 melon every game (fixed route).

The route (ep=91128753) was the highest-scoring in training data but it has
low melon sell volume. Worth investigating whether the route's melon harvest
timing aligns poorly with our market sell windows.

---

## Neither Model Is Adaptive

Both 4.7 and 5.0 execute identical sell signatures every single game:
- 4.7: W=2121, Me=144, Mi=213, Wo=148, F=209 — zero variance
- 5.0: W=437±2, Me=66, Mi=225, Wo=92, F=235 — zero variance

The market intelligence layer (impact_score, clone_detection, premium_shift)
**reorders** sells but never changes quantities or adds extra sells.
The route IS the ceiling — the market layer can only do so much.

---

## Proposed Improvements (priority order)

### 1. Wheat-arbitrage counter (HIGH PRIORITY, LOW RISK)
- Observable signal: by day 8 (step 192), track cumulative wheat sold vs expected
  baseline. If opponent wheat cumulative > 2× baseline, they're a wheat arbitrageur.
- Response: reorder sell queue to push MELON/MILK/WOOL before WHEAT
- Risk: ordering-only change; worst case = no-op

### 2. Opponent cash exploit (MEDIUM PRIORITY, LOW RISK)
- Already partially discussed; opponent cash is directly observable via obs.farms[opp].money
- If opp money < 500 at any point, they can't respond to market moves → front-load
  contested item sells to lock in revenue before they recover
- Risk: ordering-only; worst case = no-op

### 3. Melon route investigation (MEDIUM PRIORITY)
- Find a v3 route that produces similar overall score but sells 90–100+ melon
- Alternatively: see if the market layer can squeeze more melon sells by
  widening the preterminal window or loosening shed projection clamp for melon
- Risk: route change = always risky; market-layer tweak = lower risk

### 4. Late-game wheat bleed (LOW PRIORITY)
- Currently: pre-terminal bleed starts at step -10 for MELON/WOOL/FERTILIZER
- 5.0 sells only 437 wheat total; late-game wheat prices reach 50+ (2× base)
- Could add late-game wheat sells into preterminal window if shed has wheat stock
- Risk: verify shed has wheat at step -10 before adding; qty must be small

### 5. P1 disadvantage compensation (INVESTIGATE)
- When we're P1, opponent sells before us each turn → prices slightly worse for us
- Check if P0 vs P1 split in wins/losses shows a pattern
- If P1 disadvantage is real, could slightly front-load sells on P1 games
  (detected via obs.player == 1 at step 0)

---

## What NOT to do (lessons from 4.8/4.9)

- DO NOT add 3-step premium lookahead (tested: -765/game)
- DO NOT add overflow_sells or cash_exploit_sells as NEW sell sources (4.8 = 1300 ELO)
- DO NOT change price gate from 20% (4.7's conservative floor; higher thresholds hurt)
- DO NOT add quantity changes — only reordering is safe

---

## Data sources
- myreplay/ — 28 games (20 × 4.7, 8 × 5.0)
- training data v3/ — 50 top-player games for strategy fingerprinting
