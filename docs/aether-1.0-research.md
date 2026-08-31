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

## Implementation choice

Aether keeps tetsuya's internally compatible seat-0 geometry and uses the
Driz Lo/MtN wool threshold as the leading public-state signal. It does not
splice arbitrary worker actions from incompatible maps. MtN's seat-1 route is
safe to reconstruct by majority vote because that seat is genuinely stable.

Local reference benchmarking confirms the asymmetry: in ten games against
the previous MapleLeaf 6.7 reference, Aether won 6/10 overall and all five
games from seat 1, while seat 0 won only one. Public leaderboard routes are
opponent-coupled; replay consistency alone is not evidence of universal
strength.
