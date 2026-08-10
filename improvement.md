# Kaggriculture Improvement Plan

## Purpose

This document records the replay analysis of the current Kaggriculture agents and turns the findings into an implementation plan that another AI/coder can use later.

Primary models analyzed:

- **THUNDER THUNDER**
- **Sean Zhang**

Opponent behavior was also analyzed because the market is shared and opponent production affects prices.

---

# 1. Executive Summary

The main conclusion is:

> **Do not rewrite the farming/production system from scratch.**

THUNDER THUNDER already has a very strong production template. Sean Zhang's model is also mechanically competent and reaches roughly 61k–70k depending on the seed.

The largest weakness is the **economic/market layer**, especially selling products without sufficiently considering the current and expected market price.

The strongest evidence is the difference in realized revenue despite similar production:

### Milk

THUNDER:
- 221 milk sold
- $27,833 revenue
- ~$125.94 average realized price

Sean:
- 236 milk sold
- $6,889 revenue
- ~$29.19 average realized price

Sean actually produced/sold more milk but made about **$20.9k less**.

### Strawberry

THUNDER:
- 282 sold
- $30,868 revenue

Sean:
- 272 sold
- $22,572 revenue

Only 10 units difference, but about **$8.3k** revenue difference.

This strongly suggests that the next major improvement should be **dynamic market timing**, not simply increasing production.

---

# 2. Replay Scores

| Replay | Player | Opponent | Score |
|---|---|---|---:|
| No. 1 | THUNDER THUNDER | Jince | 90,112 |
| Thunder replay | THUNDER THUNDER | saitamad | 82,397 |
| Sean replay | Sean Zhang | Jesse Ferguson | 70,257 |
| Sean replay | Sean Zhang | Nirav Mehta 1612 | 61,816 |

Important observation:

The same model varies substantially between seeds.

THUNDER:
- 90,112
- 82,397

Sean:
- 70,257
- 61,816

Therefore, the goal is not simply to copy one replay. The agent needs to be robust to different market conditions and opponent behavior.

---

# 3. Environment Facts From the Replays

The uploaded replay specification identifies:

- Environment: `kaggriculture`
- Module version: `1.32.6`
- Board size: 10×10
- Four 5×5 quadrants
- 720 episode steps
- 24 turns/day
- 30 days
- Starting money: 3000
- Shed capacity: 100 non-seed items
- Maximum market orders per turn: 10
- Initial farmhand hiring follows a Fibonacci-style cost sequence
- Town-center selling occurs every 24 turns
- Town-shop selling occurs every 4 turns
- Shops unlock at intervals during the game
- Weed spawn chance is 0.005

Available farmer/hand operations include:

- NORTH
- SOUTH
- EAST
- WEST
- PASS
- PICKUP
- PLANT
- WATER
- HARVEST
- FERTILIZE
- BUILD_COOP
- BUILD_PASTURE
- DIG
- PLACE
- FEED
- COLLECT_FERTILIZER
- CARE

Market operations include:

- BUY_SEED
- BUY_PRODUCT
- BUY_ANIMAL
- SELL
- HIRE
- BUY_LAND

Do not assume any additional mechanics until the actual Kaggriculture source code is verified.

---

# 4. What THUNDER THUNDER Does

## 4.1 Opening

The No. 1 THUNDER replay establishes the economy immediately.

Early actions include:

- HIRE ×4
- BUY_ANIMAL COW ×1
- BUY_ANIMAL SHEEP ×4
- BUY_SEED WHEAT ×5
- BUY_SEED MELON ×5
- BUY_PRODUCT WHEAT ×5
- Build/establish pasture
- Place animals
- Plant crops
- Water crops
- Feed animals
- Care for animals

This should be treated as a strong opening-book candidate.

### Recommendation

Keep this opening mostly unchanged until simulation testing proves a better alternative.

---

# 5. THUNDER's Production Strategy

The No. 1 replay concentrates on a small set of resources.

Main production:

- WHEAT
- STRAWBERRY
- MELON
- MILK
- WOOL
- FERTILIZER

Animals:

- COW
- SHEEP

It largely avoids spending meaningful resources on:

- CARROT
- TOMATO
- EGG
- GOOSE

This specialization appears intentional and effective.

## Principle

Do not grow everything.

Focus on the products with strong expected economic value.

---

# 6. THUNDER's Labor Strategy

THUNDER continuously hires farmhands.

The No. 1 replay reaches approximately 10 farmhands.

The replay contains very large numbers of:

- WATER
- movement
- HARVEST
- FERTILIZE
- FEED
- CARE
- COLLECT_FERTILIZER
- PLANT

The hands effectively form a production machine while the farmer acts as a support/logistics unit.

### Important lesson

Do not over-optimize individual farmer movement at the expense of overall production.

The farmhand system is one of the main reasons the strategy scales.

---

# 7. THUNDER's Land Strategy

Strong replays eventually unlock:

- NW
- NE
- SW

and do not appear to prioritize unlocking every possible area.

The agent also buys land during the season.

### Recommendation

Retain the two-land-expansion strategy as the baseline.

Only change it after testing the economic value of the additional land against hiring/production costs.

---

# 8. THUNDER's Wheat Strategy

Wheat is especially important.

THUNDER uses wheat as:

1. A crop
2. Animal input/feed
3. A product to buy from the market
4. A product to sell
5. A production buffer

This is an important economic feature of the strategy.

The agent is not simply trying to produce all inputs itself.

It can:

> Buy cheap wheat → use it for production → produce higher-value outputs → sell those outputs.

This creates an input/output arbitrage strategy.

---

# 9. THUNDER Revenue

Approximate No. 1 THUNDER sales:

| Product | Quantity | Revenue |
|---|---:|---:|
| Strawberry | 282 | 30,868 |
| Milk | 221 | 27,833 |
| Wheat | 443 | 18,655 |
| Melon | 114 | 14,862 |
| Fertilizer | 228 | 11,900 |
| Wool | 132 | 3,478 |
| **Total** | | **107,596** |

Approximate wheat purchases:

- 9,107 spent

This demonstrates the scale of the production/trading engine.

---

# 10. Sean Zhang's Current Strengths

Sean already has many of the correct mechanics.

The replay shows:

- Early hiring
- Animal setup
- Pasture setup
- Wheat production
- Melon production
- Strawberry production
- Watering
- Animal care
- Fertilizer collection
- Continuous hiring
- Land expansion
- 10 farmhands
- Wheat market activity

Therefore:

> **Sean should not be rewritten from scratch.**

The production system is already viable.

The largest gains should come from improving the economic controller.

---

# 11. Sean's Biggest Problem: Market Timing

The most important fix is:

> **Do not sell merely because inventory exists.**

Current behavior can result in products being sold at poor prices.

Milk is the clearest example.

### Sean, 61,816 replay

- 236 milk
- $6,889 revenue
- ~$29.19/unit

### THUNDER, 90,112 replay

- 221 milk
- $27,833 revenue
- ~$125.94/unit

The difference is approximately $20,944 despite THUNDER selling fewer units.

This means:

> The economic controller can be worth more than another production expansion.

---

# 12. Strawberry Evidence

THUNDER:

- 282 strawberry
- $30,868

Sean:

- 272 strawberry
- $22,572

The production difference is tiny.

The revenue difference is large.

This is another strong indication that price timing matters.

---

# 13. Wool Evidence

Wool is an important counterexample.

THUNDER:

- 132 wool
- $3,478

Sean:

- 132 wool
- $12,602

Sean wins massively here.

This proves that the issue is not simply "Sean sells badly."

Instead:

> Different products have different profitable selling windows.

The strategy must therefore be product-specific.

---

# 14. Sean's Other Replay

Sean's 70,257 replay had approximately:

| Product | Revenue |
|---|---:|
| Strawberry | 49,362 |
| Wheat | 20,828 |
| Melon | 16,950 |
| Fertilizer | 12,758 |
| Milk | 11,780 |
| Wool | 7,610 |

Strawberry alone generated nearly $50k.

This demonstrates that the same general production strategy can perform much better under favorable market conditions.

Therefore:

> The agent needs to adapt to market conditions rather than assuming one fixed sales schedule is optimal.

---

# 15. Opponent Behavior

Opponent behavior matters because market inventory/prices are shared.

The analyzed opponents include:

- Jince
- saitamad
- Jesse Ferguson
- Nirav Mehta 1612

Jesse/Nirav use a more aggressive high-action strategy than Sean in several respects.

They can reach approximately 12 farmhands and perform much larger quantities of:

- PICKUP
- FEED
- WATER
- HARVEST
- movement
- wheat buying/selling

One observed opponent pattern included roughly:

- 1,100 wheat sold
- 967 wheat bought

This is far more market activity than Sean's approximately 450 wheat sold / 240 wheat bought range.

---

# 16. Do NOT Blindly Copy the Opponent

The aggressive opponent strategy is not automatically better.

Example:

Jesse Ferguson scored approximately:

- 66,777

while Sean scored:

- 70,257

Therefore:

> More actions, more wheat, and more farmhands do not automatically equal a higher score.

The goal is efficient production and profitable conversion to cash.

---

# 17. Opponent-Aware Market Model

The agent can observe public opponent information such as their farm state.

It should estimate opponent production.

Useful signals:

- Opponent farmhand count
- Opponent crop distribution
- Opponent animal count
- Opponent planted crops
- Opponent active production
- Opponent visible inventory/production indicators
- Market inventory
- Market price
- Recent price movement

Do not assume private opponent inventory is observable unless the source code confirms it.

---

# 18. Market Analyzer

Create a dedicated market-analysis module.

For every product maintain:

```text
current_price
rolling_average_price
rolling_min_price
rolling_max_price
price_velocity
market_inventory
market_inventory_velocity
my_inventory
my_production_rate
days_remaining
```

Potentially also:

```text
opponent_estimated_production
expected_future_price
storage_value
```

---

# 19. Price Score

A simple first version:

```python
price_score = current_price / rolling_average_price
```

Example policy:

```text
price_score > 1.15
    → sell aggressively

0.90 <= price_score <= 1.15
    → sell only if storage is getting full

price_score < 0.90
    → hold
```

These thresholds are only initial hypotheses.

They must be tuned through simulations.

---

# 20. Better Market Model

A stronger controller should predict future value.

Conceptually:

```python
expected_future_price =
    current_price
    + predicted_price_change
```

Where predicted price change depends on:

- market inventory trend
- recent price trend
- opponent production
- own production
- town consumption
- remaining time

Then compare:

```python
sell_now_value
```

against:

```python
hold_value
```

---

# 21. Market Inventory Direction

If market inventory is falling:

```text
inventory ↓
→ scarcity ↑
→ price may rise
```

If market inventory is rising:

```text
inventory ↑
→ supply ↑
→ price may fall
```

The exact relationship must be confirmed from the source code.

Do not hard-code this assumption until the market implementation is inspected.

---

# 22. Product-Specific Selling

Do not use one universal threshold.

For example:

```text
strawberry:
    potentially hold for high-value windows

milk:
    highly price-sensitive

wool:
    highly price-sensitive

wheat:
    can be sold OR used internally

fertilizer:
    sell when excess production exists

melon:
    sell according to price and remaining production cycles
```

Exact thresholds should be learned from replay data and source-code economics.

---

# 23. Shed Management

Shed capacity is approximately:

```text
100 non-seed items
```

Therefore production must consider storage.

Create a value-per-slot concept:

```python
value_per_storage_slot =
    expected_sell_price * expected_quantity
```

When storage is close to full:

1. Sell high-price items first.
2. Sell low-value excess items if necessary.
3. Preserve inputs required for upcoming production.
4. Avoid selling resources that are more valuable internally than externally.

---

# 24. Important Distinction: External vs Internal Value

For each item calculate:

```text
external_value = expected sale price
```

and:

```text
internal_value = value of using it as an input
```

For wheat, internal value can be substantial.

Therefore:

```python
effective_wheat_value =
    max(external_sale_value, internal_production_value)
```

This prevents the agent from selling wheat that it should have used for production.

---

# 25. Production Planner

Separate the production planner from the market controller.

The production planner should decide:

- What crops to plant
- How much land to dedicate to each
- Which animals to maintain
- Whether to buy another animal
- Whether to buy land
- Whether to hire another hand
- How much wheat to reserve

The market controller should decide:

- BUY
- HOLD
- SELL SMALL
- SELL MEDIUM
- SELL LARGE

Do not mix these systems into one giant decision function.

---

# 26. Crop Specialization

Baseline crops:

```text
WHEAT
STRAWBERRY
MELON
```

Use a profit-per-tile/day estimate.

Conceptually:

```python
expected_profit_per_tile =
    expected_yield
    * expected_sell_price
    / growth_time
```

Also account for:

- seed cost
- watering cost/action
- fertilizer
- labor
- opportunity cost
- remaining days
- storage
- market saturation

Only new planting decisions should be changed dynamically.

Do not destroy profitable existing crops just because another crop temporarily has a better price.

---

# 27. Animal Strategy

Baseline:

- 1 cow
- multiple sheep

Animal decisions should use:

```text
expected output
× expected price
− feed cost
− labor cost
− opportunity cost
```

Do not add animals just because money is available.

Add them when the expected remaining-season profit is positive.

---

# 28. Hiring Strategy

The Fibonacci hiring cost means the marginal value of another hand eventually increases.

Use:

```python
expected_future_profit_from_hand
>
hire_cost
```

as the conceptual decision rule.

However, retain the current aggressive hiring baseline because it is clearly part of the successful strategy.

The first ~4 hires should probably remain fixed unless simulation shows a better opening.

Later hires can become adaptive.

---

# 29. Land Strategy

Baseline:

- Buy land twice.
- Reach approximately NW + NE + SW.

Potential future improvement:

Calculate:

```python
land_value =
    expected_additional_production
    - land_cost
```

and compare it with:

```python
hire_value
animal_value
crop_value
```

Buy whichever produces the highest expected remaining-season return.

---

# 30. Fixed Opening + Adaptive Endgame

Recommended structure:

## Days 0–5

Mostly fixed.

Use the successful THUNDER opening.

## Days 6–12

Semi-adaptive.

Begin monitoring:

- prices
- market inventory
- crop profitability
- storage
- opponent production

## Days 13–20

Adaptive specialization.

Increase production of the most profitable resources.

## Days 21–29

Maximum profitable production.

Sell according to market conditions.

## Final day

Liquidation mode.

Do not preserve inventory unnecessarily.

---

# 31. Final-Day Liquidation

At the end of the season:

```text
remaining production time ≈ 0
```

Therefore the value of holding most products collapses.

Prioritize:

1. Sell high-value products.
2. Sell excess inventory.
3. Sell resources that cannot be converted into another profitable production cycle.
4. Use remaining turns for actions that actually create score.

Do not leave valuable sellable inventory sitting in the shed.

---

# 32. Four Versions to Test

Create four experimental agents.

## Version A — Current THUNDER

Exact baseline.

Purpose:

- benchmark

---

## Version B — THUNDER + Dynamic Selling

Keep production identical.

Only replace sales logic.

Purpose:

- isolate market timing improvement

This should be the first experiment.

---

## Version C — THUNDER + Dynamic Selling + Opponent Model

Add:

- opponent production estimation
- market inventory trend
- price prediction

Purpose:

- exploit shared market dynamics

---

## Version D — THUNDER + Adaptive Production

Add:

- crop specialization
- animal optimization
- dynamic hiring
- dynamic land purchases

Purpose:

- maximize long-run adaptability

---

# 33. Experimental Method

Do not judge a strategy from one replay.

Run many seeds.

For every version record:

```text
final_score
final_money
total_sales_revenue
total_buy_cost
wheat_revenue
strawberry_revenue
melon_revenue
milk_revenue
wool_revenue
fertilizer_revenue
farmhand_count
land_count
animal_count
crop_count
average_sell_price_per_product
number_of_sell_actions
number_of_buy_actions
```

Especially track:

```text
revenue / unit
```

because raw production volume can be misleading.

---

# 34. Key Metrics

The most useful metrics are:

### Revenue per unit

```python
revenue / units_sold
```

### Profit per tile

```python
profit / tile / day
```

### Profit per farmhand

```python
profit / farmhand / day
```

### Market timing gain

```python
actual_sale_price / rolling_average_price
```

### Storage efficiency

```python
revenue / average_storage_used
```

---

# 35. Exact Source-Code Investigation Needed

Before implementing advanced market prediction, inspect the Kaggriculture source code for:

1. Crop growth times
2. Crop yields
3. Seed costs
4. Water requirements
5. Fertilizer effects
6. Animal production rates
7. Feed requirements
8. Animal care bonuses
9. Animal purchase costs
10. Farmhand costs
11. Farmhand behavior
12. Land costs
13. Shed overflow behavior
14. Town-center selling
15. Town-shop selling
16. Market price calculation
17. Market inventory update
18. Market purchase behavior
19. Market selling behavior
20. End-of-day mechanics
21. End-of-season scoring
22. Opponent observation visibility

This should be done before hard-coding economic constants.

---

# 36. Critical Market Equation Goal

The ultimate goal is to determine:

```text
price(t + 1)
```

from:

```text
price(t)
market_inventory(t)
buy_volume(t)
sell_volume(t)
town_consumption(t)
```

If the exact market function can be reconstructed, implement a simulator for price changes.

Then the agent can ask:

> "What happens to the price if I sell 20 milk right now?"

rather than guessing.

---

# 37. Potential Advanced Strategy: Internal Market Simulator

Build a lightweight market simulator.

Input:

```python
current_market_state
candidate_action
```

Output:

```python
predicted_price_after_action
predicted_future_price
predicted_profit
```

Then evaluate:

```text
SELL NOW
vs
HOLD
vs
SELL 25%
vs
SELL 50%
vs
SELL 100%
```

Choose the action with the highest expected value.

This could be significantly stronger than fixed thresholds.

---

# 38. Potential Advanced Strategy: Rolling Replay Learning

Store historical observations:

```text
state
action
price_before
quantity_sold
price_after
reward
```

Then learn empirical relationships.

Example:

```python
milk_price_after_selling(q)
```

could be estimated directly from previous game states.

This is safer than blindly using an RL model.

---

# 39. Potential Advanced Strategy: Opponent Forecast

Estimate:

```text
opponent_wheat_supply
opponent_strawberry_supply
opponent_milk_supply
opponent_wool_supply
```

from their visible farm.

Then estimate market pressure.

Example:

```text
opponent has huge wheat production
+
market wheat inventory increasing
=
do not expand wheat purely for sale
```

But if wheat is cheap:

```text
BUY WHEAT
```

and convert it into a higher-value product.

---

# 40. Potential Advanced Strategy: Price Shock Detection

If a product suddenly moves far above its rolling average:

```text
current_price >> rolling_average
```

trigger:

```text
SELL LARGE
```

But avoid immediately selling the entire inventory if the price is still rising.

A better controller could use staged sales:

```text
25%
25%
25%
25%
```

with reassessment after each market update.

---

# 41. Potential Advanced Strategy: Price Floor

If a product becomes extremely cheap:

```text
current_price << rolling_average
```

consider buying it.

Especially for:

- wheat
- other reusable inputs

Only do this if:

```text
storage capacity available
AND
internal consumption exists
AND
expected future value > purchase price
```

---

# 42. Potential Advanced Strategy: Production Lock-In

When a crop is already planted:

Do not constantly reconsider it.

Instead:

```text
existing_crop = locked
new_tiles = adaptive
```

This avoids wasting actions and resources chasing short-term price noise.

---

# 43. Potential Advanced Strategy: Endgame Forecast

Calculate:

```python
remaining_days
remaining_growth_cycles
```

Then decide whether a new crop/animal/land purchase can actually pay back before the episode ends.

Example:

```text
if crop_growth_time > remaining_time:
    don't plant
```

Likewise:

```text
if animal_payback_period > remaining_time:
    don't buy
```

---

# 44. Potential Advanced Strategy: Opportunity Cost

Every action has an opportunity cost.

A farmer moving 10 tiles to sell an item may be losing the opportunity to:

- harvest
- plant
- care
- collect fertilizer
- feed

The controller should eventually estimate:

```text
action_value =
    direct_profit
    + future_profit
    - opportunity_cost
```

This is a later optimization, not the first change.

---

# 45. What NOT to Optimize First

Do not spend the first iteration optimizing:

- individual NORTH/SOUTH/EAST/WEST movements
- exact farmer path
- obscure crops
- goose production
- tomato production
- carrot production
- tiny fertilizer timing differences

These are likely much smaller gains than market timing.

---

# 46. Recommended Development Order

## Phase 1

Preserve the existing THUNDER production script.

Add logging.

---

## Phase 2

Add rolling price history.

---

## Phase 3

Implement dynamic selling.

---

## Phase 4

Implement storage-aware selling.

---

## Phase 5

Implement dynamic wheat purchasing.

---

## Phase 6

Reverse-engineer the market equation from source.

---

## Phase 7

Implement opponent production estimation.

---

## Phase 8

Implement adaptive crop allocation.

---

## Phase 9

Optimize hiring and land timing.

---

## Phase 10

Optimize movement/routing.

---

# 47. Target Architecture

Recommended modules:

```text
agent/
├── main.py
├── strategy.py
├── production.py
├── market.py
├── market_model.py
├── opponent_model.py
├── farmhands.py
├── animals.py
├── crops.py
├── inventory.py
├── economy.py
├── routing.py
├── endgame.py
└── logging.py
```

---

# 48. Strategy Responsibilities

## strategy.py

High-level phase control:

```text
OPENING
SETUP
PRODUCTION
ADAPTATION
ENDGAME
```

---

## market.py

Decide:

```text
BUY
SELL
HOLD
```

---

## market_model.py

Predict:

```text
future price
price response to quantity sold
market pressure
```

---

## production.py

Decide:

```text
crop allocation
animal allocation
land usage
```

---

## farmhands.py

Manage:

```text
worker assignments
routing
watering
planting
harvesting
feeding
care
fertilizer
```

---

## opponent_model.py

Estimate:

```text
opponent production
market pressure
```

---

## economy.py

Calculate:

```text
profit
expected ROI
hire ROI
land ROI
animal ROI
```

---

# 49. Baseline Policy

The initial baseline should remain approximately:

```text
4 early hires
1 cow
4 sheep
wheat + melon opening
pasture setup
aggressive watering/care
continuous farmhand hiring
two land purchases
wheat market activity
strawberry/melon/wheat production
milk/wool/fertilizer production
```

Then improve only one component at a time.

---

# 50. Core Hypothesis

The central hypothesis to test is:

> **THUNDER's high score comes primarily from an efficient fixed production engine, while a substantial amount of Sean's lost score comes from selling products during poor price windows.**

Therefore:

> **The best next agent is likely not "more farming." It is THUNDER's farming engine plus a substantially smarter economic controller.**

---

# 51. Priority List

## Priority 1 — Dynamic selling
Expected impact: VERY HIGH

## Priority 2 — Price history
Expected impact: VERY HIGH

## Priority 3 — Market inventory trend
Expected impact: HIGH

## Priority 4 — Storage-aware decisions
Expected impact: HIGH

## Priority 5 — Wheat arbitrage
Expected impact: HIGH

## Priority 6 — Opponent market-pressure model
Expected impact: MEDIUM/HIGH

## Priority 7 — Adaptive crop allocation
Expected impact: MEDIUM

## Priority 8 — Dynamic hiring
Expected impact: MEDIUM

## Priority 9 — Dynamic land timing
Expected impact: MEDIUM

## Priority 10 — Movement optimization
Expected impact: LOW/MEDIUM

---

# 52. Final Recommendation

Start from **THUNDER THUNDER's No. 1 replay**.

Do NOT rewrite its opening.

Do NOT immediately add complicated RL.

First implement:

```text
THUNDER production
+
price history
+
dynamic selling
+
storage management
+
wheat buy/hold/sell logic
```

Then test across many seeds.

Only after that should opponent modeling and adaptive production be added.

The likely winning architecture is:

> **Deterministic production + adaptive economics + opponent-aware market prediction.**

That gives the agent the reliability of the No. 1 fixed script while addressing the biggest weakness visible in the Sean replays.
