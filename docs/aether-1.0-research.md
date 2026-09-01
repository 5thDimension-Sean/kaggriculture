# Aether 1.0 replay research

Research date: 2026-08-31. Source: ten latest public replays for each of
tetsuya, Driz Lo, and MtN, downloaded from their live Kaggriculture
submissions.

## Fact check: “100% consistent”

The claim is false when measured action-by-action and split by seat:

| Player | Seat | Games | Overall | Farmer | Hands | Market |
|---|---:|---:|---:|---:|---:|---:|
| tetsuya | 0 | 6 | 70.0% | 69.3% | 59.9% | 80.9% |
| tetsuya | 1 | 4 | 75.9% | 80.7% | 65.7% | 81.4% |
| Driz Lo | 0 | 5 | 68.0% | 65.1% | 60.0% | 78.8% |
| Driz Lo | 1 | 5 | 87.3% | 89.0% | 85.3% | 87.6% |
| MtN | 0 | 6 | 87.9% | 88.8% | 86.8% | 88.3% |
| MtN | 1 | 4 | 99.2% | 99.9% | 99.4% | 98.3% |

Only MtN seat 1 is close enough to treat as a fixed route. The other traces
contain structured whole-route branches, not random per-step noise.

## Pinpointed seat-0 branch

Driz Lo and MtN share an intentional opening `PASS`, then an almost identical
first market build. Their first large route split occurs at the day boundary
around local step 73. Across the sampled seat-0 games, public market
`inventory["WOOL"] <= 9995` perfectly separated the minority production route
from the normal route. The split immediately changes several workers, then
cascades into hiring, crops, and later market orders.

Tetsuya starts from a different geometry, but its step-73 crop purchase is
also state-dependent:

- wool pressure selects two strawberry and three melon seeds;
- without wool pressure, milk pressure selects the same melon-heavy mix;
- otherwise it selects four strawberry and one melon seed.

Later apparent “ifs” are mostly consequences of that fork. For example,
tetsuya's step-82 planting action is perfectly separated by its remaining
strawberry seed count, and its step-97 purchase is perfectly separated by its
melon tile count.

This is replay inference, not access to private source. The causal model most
consistent with the observations is one early opponent-production fingerprint
followed by state-driven route execution.

## Seat-1 logistics translation

A direct local isolation test showed that the MtN seat-1 consensus route also
works from seat 0. Against the MapleLeaf 6.7 reference on five fixed seat-0
seeds, it won 5/5 with a mean score of 100,096 and a +9,960 margin. The three
tetsuya-derived seat-0 branches won at most 1/5 in the same test. Farm
coordinates are player-local, so no EAST/WEST mirror is required.

Aether therefore applies the stable seat-1 logistics cadence to both seats:

1. establish five specialized workers and the animal/crop inventory together;
2. keep care, fertilizer collection, watering, and harvest loops synchronized;
3. treat pickup/place actions as scheduled handoffs rather than greedy choices;
4. replenish workers and seeds at route checkpoints; and
5. preserve the full production geometry when public market conditions change.

Market action order is part of the logistics policy, not presentation. An
initial attempt to move all purchases ahead of sales lost 0/10 because the
sales finance later purchases and hires within the same turn. A later version
only exchanged products among sale slots, but the final exact-copy policy
removes that difference too: every market order matches the seat-1 tape.

The Driz Lo/MtN wool threshold and tetsuya milk/crop distinction remain useful
research findings, but the exact-copy policy does not use them at runtime.
Seat 0 retains every demonstrated seat-1 market order and quantity.

The original Aether fusion benchmark exposed a seat asymmetry (5/5 from seat
1, 1/5 from seat 0). The final exact seat-1 copy won 10/10 across paired seats
against MapleLeaf 6.7, averaging 101,221 versus 92,576 for a +8,645 margin.
This remains a local fixed-seed result, not a guarantee of live leaderboard
performance.

## Weed-recovery removal (2026-09-01)

The exact-copy submission (Kaggle submission 55929599, "Aether 1.0 exact
seat-1 copy") still carried a per-worker delay tracker: if a scheduled
`BUILD_PASTURE`/`PLANT` landed on a weed tile, that worker DIG'd instead and
every later action for that worker shifted back by one step, forever.

The real validation episode for that submission (episode 104481488, both
seats run by the same agent) showed this was not actually seat-parity: 460 of
720 steps had different farmer/hand actions between seat 0 and seat 1, and
the two seats finished with rewards of 36,988 and 43,951. `weedSpawnChance`
(0.005/tile/turn in the live configuration) spawns weeds independently on
each farm, so the two seats' workers got blocked at different times, and once
one worker's schedule slipped it never resynced -- the offset compounded for
the rest of the game.

`main.py` no longer tracks per-worker delays or reads either farm's tiles at
all for farmer/hand actions: `_act()` returns `route[step]` verbatim, exactly
as it already did for market orders. This guarantees byte-identical actions
for both seats on every step, at the cost of occasionally wasting a single
`PLANT`/`BUILD_PASTURE` action if a weed happens to be on that exact tile
that turn (no schedule-wide delay, no seat divergence). Verified locally via
`tests/test_agent.py::test_both_seats_identical_across_full_random_episode`,
which runs full unseeded episodes through the real environment and asserts
`step[0].action == step[1].action` for every step.

## Mirror experiment

Both farms expose the same player-local map: the farmer starts at `[4, 4]`,
the northwest quadrant is unlocked, and the initial tile coordinates are
identical. Five fixed seat-0 seeds confirmed that no spatial transform helps:

| Transform | Wins | Mean score | Paired change vs unmirrored |
|---|---:|---:|---:|
| Exact, unchanged seat-1 copy | 5/5 | 100,096 | — |
| Swap east/west | 0/5 | 0 | -100,096 |
| Swap north/south | 0/5 | 234 | -99,862 |
| Rotate 180° | 0/5 | 0 | -100,096 |

The pre-translation seat-0 build at commit `a6c0506` averaged 76,523 on the
same seeds. The exact seat-1 copy improves that by 23,573 per game. Aether
therefore retains the unchanged seat-1 moves on seat 0.
