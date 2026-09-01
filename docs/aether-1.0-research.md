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
sales finance later purchases and hires within the same turn. The corrected
policy leaves every sale/buy/hire slot in place and can only reorder which
product occupies an existing sale slot.

The Driz Lo/MtN wool threshold and tetsuya milk/crop distinction are retained
only as a day-boundary sales-priority rule. Aether reorders existing sales
toward the observed shortage but never invents inventory or changes quantities.

The original Aether fusion benchmark exposed a seat asymmetry (5/5 from seat
1, 1/5 from seat 0). The corrected seat-1 translation won 10/10 across paired
seats against MapleLeaf 6.7, averaging 101,184 versus 92,608 for a +8,576
margin. This remains a local fixed-seed result, not a guarantee of live
leaderboard performance.

## Mirror experiment

Both farms expose the same player-local map: the farmer starts at `[4, 4]`,
the northwest quadrant is unlocked, and the initial tile coordinates are
identical. Five fixed seat-0 seeds confirmed that no spatial transform helps:

| Transform | Wins | Mean score | Paired change vs unmirrored |
|---|---:|---:|---:|
| Unmirrored seat-1 route | 5/5 | 100,037 | — |
| Swap east/west | 0/5 | 0 | -100,037 |
| Swap north/south | 0/5 | 234 | -99,803 |
| Rotate 180° | 0/5 | 0 | -100,037 |

The pre-translation seat-0 build at commit `a6c0506` averaged 76,523 on the
same seeds. The current unmirrored translation improves that by 23,514 per
game. Aether therefore retains the unmirrored route.
