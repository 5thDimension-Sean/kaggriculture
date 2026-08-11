# Replacement `improvements.md` — routing, scoring, and replay-parity audit

## Executive summary

The lower-scoring run is **not failing because the seed is different**. Both supplied replays report:

- `seed: 0`
- `module_version: 1.32.6`
- `kaggriculture`
- `720` steps
- the same board/game configuration
- `DONE` for both players

The scores are nevertheless very different:

| Run | P0 | P1 |
|---|---:|---:|
| `thunder.json` | 59,137 | 61,422 |
| `91802898.json` | 43,625 | 51,475 |
| Difference | **15,512** | **9,947** |

The important point is:

> **Same environment seed does not imply same trajectory when the agents take different actions.**

This game has shared farm state and, critically, a shared dynamic market. An agent's sales change market inventory and therefore future prices. Town demand is also shared. The observation explicitly marks `market`, `farms`, `day`, `hour`, `step`, and `town` as shared, while shed/farmer inventories are private. Therefore two agents playing against different policies can diverge substantially even with the same seed.

The lower-scoring replay also has a very large behavioral difference: its action stream differs from Thunder's at **533 of 720 step indices** (counting a step as different if either player's action differs).

The main conclusion is that the current implementation is too heavily based on a fixed replay route plus ad-hoc overlays. It needs to become a **state-conditioned controller** with explicit route phase/state validation, correct replay-step alignment, economic guardrails, and much more conservative preemption.

---

# 1. What the two JSON replays actually prove

## 1.1 Environment configuration is effectively identical

Both files report:

- `boardSize = 10`
- `episodeSteps = 720`
- `farmHandCostMult = 1`
- `maxMarketOrdersPerTurn = 10`
- `startingMoney = 3000`
- `turnsPerDay = 24`
- `townCenterSellInterval = 24`
- `townShopSellInterval = 4`
- `townShopUnlockInterval = 3`
- `weedSpawnChance = 0.005`
- `seed = 0` in `info`

The Thunder replay reports rewards `[59137.0, 61422.0]`; the other replay reports `[43625.0, 51475.0]`.

So this is **not a configuration mismatch**.

The supplied replay schema also explicitly says the final reward is player money at the end of the game. In other words, the lower number is an economic result, not a mysterious scoring/display issue.

---

# 2. The single biggest conceptual mistake: treating the seed as the whole game state

A deterministic seed determines the environment's random events, but the environment is not an isolated sequence of random events.

Actions modify state.

In this game:

1. Player 0 acts.
2. Player 1 acts.
3. Both players affect public farm state.
4. Both players interact with the same market.
5. Selling changes market inventory.
6. Market inventory changes future prices.
7. Town shops unlock and create demand.
8. Crop/animal production changes inventory available for future sales.
9. Hiring and land purchases change future capacity and expenses.

Therefore:

```text
same seed
    !=
same market trajectory
    !=
same farm trajectory
    !=
same private inventory
    !=
same optimal route
```

This explains why copying a high-scoring Thunder replay and running a different agent against it does not reproduce Thunder's score.

The replay itself demonstrates this: both runs have the same seed but end at very different balances.

---

# 3. The current code is replay-driven rather than state-driven

The implementation says it uses two fixed position-specific routes extracted from Thunder replays:

- P0 route from episode `91385999`
- P1 route from episode `91471546`

The route data is embedded as compressed/base85 JSON.

That is a useful optimization source, but it is dangerous as the primary policy.

The important distinction is:

```text
GOOD:
Thunder replay -> discover a strong schedule -> use it as a prior

BAD:
Thunder replay -> hard-code every action -> assume the same state will exist
```

The current code is much closer to the second model.

The code selects `_ACTIONS_P0` or `_ACTIONS_P1` based almost entirely on seat and step, then applies overlays. The relevant implementation is the route selection and action pipeline in `agent()`.

The route constants are explicitly described as replay-derived in the source. fileciteturn2file0L11-L24

---

# 4. Critical routing bug: replay step indexing must be verified

This is one of the first things to fix.

The replay JSON has a bootstrap observation at `step = 0` whose recorded action is `PASS`.

The next recorded action occurs with the observation whose state has advanced to `step = 1`.

The embedded route, however, starts with:

```python
_Actions_P0[0] =
{
    "farmer": ["PASS"],
    "market": [
        ["HIRE"],
        ...
    ]
}
```

and `_ACTIONS_P0[1]` is already the first physical movement/pickup sequence.

The current implementation does:

```python
step = ...
action = _copy_action(actions[step])
```

That is a red flag because the replay representation needs to be treated explicitly as:

```text
observation step 0 -> bootstrap/pass
observation step 1 -> route action 0
observation step 2 -> route action 1
...
```

Do not assume this without testing the actual submission harness, but **the replay evidence strongly indicates that route-indexing and replay-indexing are not the same coordinate system**.

### Required fix

Create one explicit conversion:

```python
def _route_index(obs_step):
    # Verify this against the actual harness.
    # For the supplied replay representation:
    if obs_step <= 0:
        return None
    return min(obs_step - 1, ROUTE_LENGTH - 1)
```

Then make every route-dependent function use the same route index.

Do NOT independently use:

- `step`
- `step - 1`
- `step + 1`

in different overlays.

Right now that would create subtle temporal inconsistencies between:

- weed repair
- future sell lookup
- preemption
- fertilizer relay
- terminal liquidation

This is especially dangerous because the code uses future route actions for economic decisions.

---

# 5. The biggest routing design flaw: overlays mutate a fixed route without validating the resulting state

The current pipeline is approximately:

```text
fixed route
 -> weed repair
 -> repay preemption
 -> price guard
 -> sell ranking
 -> preemption
 -> fertilizer relay
 -> terminal liquidation
 -> hand alignment
```

The code explicitly applies those transformations sequentially. fileciteturn1file1L125-L145

This is fragile because each transformation assumes the previous transformation preserved the assumptions of the route.

For example:

```text
route says:
    hand 4 -> PLANT WHEAT

weed overlay says:
    tile is WEED
    -> DIG instead

next step:
    replay intended action
```

That can be valid.

But the route may have also assumed:

- a specific unit is carrying seeds,
- a specific unit is standing at a specific coordinate,
- another hand is moving through that coordinate,
- the tile was planted already,
- the crop's growth clock started at the original time,
- a future harvest happens on a specific step.

A one-turn mutation can therefore invalidate a sequence much farther downstream.

The weed overlay is implemented as a stateful transaction and replays the intended action after DIG. fileciteturn2file2L496-L536

That is clever, but it is not enough to guarantee route validity.

---

# 6. Concrete evidence of route disruption from the supplied replays

At step 84, Thunder performs:

```json
{
  "hands": [
    ["WEST"],
    ["PLANT", "STRAWBERRY"],
    ["WEST"]
  ]
}
```

The lower-scoring replay instead performs:

```json
{
  "hands": [
    ["WEST"],
    ["DIG"],
    ["WEST"]
  ]
}
```

At step 85 the lower-scoring run performs the delayed `PLANT STRAWBERRY`.

This shows the weed-repair overlay is actually changing the schedule.

The immediate money balance does not diverge there, so this is **not by itself the explanation for the entire 15,512-point deficit**. It is evidence that the controller is not executing the Thunder route.

There are additional weed substitutions later, including steps around 519, 568–569, 630–641.

### Required improvement

Every route mutation must be recorded as a transaction:

```text
original route action
actual replacement
reason
start step
expected repair step
whether downstream route is still valid
```

If a route action is delayed, the controller should either:

1. replay a verified repair micro-route, or
2. abandon the route segment and enter a local state-based controller.

Do not blindly resume the old route after an arbitrary number of turns.

---

# 7. The other replay is not simply "Thunder but worse"

This is important.

The lower-scoring replay changes strategy in ways that materially affect economics.

By the end of the two runs:

## P0

Thunder:

- 266 hires
- 8 cows purchased
- 6 sheep purchased
- 234 fertilizer sold
- 458 wheat sold
- 143 wool sold
- 218 milk sold
- 114 melon sold
- 283 strawberry sold

Other:

- 280 hires
- 10 cows purchased
- 4 sheep purchased
- 253 fertilizer sold
- 438 wheat sold
- 122 wool sold
- 245 milk sold
- 102 melon sold
- 254 strawberry sold

## P1

Thunder:

- 259 hires
- 8 cows purchased
- 6 sheep purchased
- 237 fertilizer sold
- 445 wheat sold
- 144 wool sold
- 220 milk sold
- 114 melon sold
- 286 strawberry sold

Other:

- 278 hires
- 10 cows purchased
- 4 sheep purchased
- 254 fertilizer sold
- 459 wheat sold
- 120 wool sold
- 242 milk sold
- 114 melon sold
- 252 strawberry sold

This is a major strategic change:

```text
Thunder:
    more sheep
    more wool
    fewer cows
    fewer hires

Other:
    more cows
    more milk
    more hires
```

So the lower-scoring controller is not just losing because of one routing mistake. It is making a different production portfolio.

---

# 8. Why the animal strategy matters

The supplied replay data shows the lower-scoring controller produced much less wool and much more milk.

Approximate realized sell revenue from the recorded sell actions:

| Resource | Thunder P0 | Other P0 |
|---|---:|---:|
| Wool | 15,661 | 3,276 |
| Milk | 8,843 | 23,096 |

For P1:

| Resource | Thunder P1 | Other P1 |
|---|---:|---:|
| Wool | 16,566 | 3,274 |
| Milk | 8,136 | 22,765 |

This is a huge change in what the agent is putting into the market.

The other run does generate more gross sell revenue overall in this replay, but that does **not** translate into more final money.

That is the critical economic lesson:

> Optimize final cash, not gross sales.

The lower run buys more animals and hires more workers, while changing the production mix.

That can increase gross revenue while reducing net profit.

---

# 9. Hiring is another clear source of leakage

The other run hires substantially more:

| Player | Thunder hires | Other hires | Extra |
|---|---:|---:|---:|
| P0 | 266 | 280 | +14 |
| P1 | 259 | 278 | +19 |

The game uses a Fibonacci-based daily hire-cost sequence.

Therefore "hire as much as possible" is not free capacity.

The controller should not treat every available worker as automatically beneficial.

### Required hiring rule

Before a hire:

```text
expected incremental production value
    >
incremental hire cost
+ expected food/care/input costs
+ opportunity cost
```

At minimum, use a phase-specific maximum worker count.

Do not allow a route overlay or fallback to add workers simply because money happens to be available.

---

# 10. The market strategy needs to be less reactive

The current code contains a reasonable market impact model.

It computes:

```python
quantity * max(0, current_quote - later_quote)
```

and then adds a demand-urgency multiplier.

The implementation is here. fileciteturn2file2L569-L614

However, there are three problems.

## Problem A — It scores the route, not the complete economic decision

The score estimates price impact.

It does not directly ask:

```text
If I sell this now,
what happens to my final cash compared with waiting?
```

It should include:

- current sale proceeds,
- future expected price,
- expected town demand,
- inventory carrying risk,
- production timing,
- terminal liquidation,
- opponent's likely market actions.

---

## Problem B — Sell ranking can reorder actions that were deliberately timed

The function `_rank_sell_slots()` reorders sell orders by computed score while keeping their slots occupied. fileciteturn2file2L617-L630

This can destroy deliberate ordering.

If a replay was discovered with:

```text
SELL A
SELL B
SELL C
```

because A/B/C were deliberately timed around market state, a generic ranking layer can silently transform it into:

```text
SELL C
SELL A
SELL B
```

without checking whether those sales were supposed to be coupled to:

- a crop harvest,
- a worker movement,
- an animal output event,
- a town consumption tick,
- an opponent's sale.

### Improvement

Only reorder **independent sell orders**.

Tag route orders as:

```python
{
    "item": "WOOL",
    "quantity": 12,
    "timing_class": "flexible"
}
```

versus:

```python
{
    "item": "WHEAT",
    "quantity": 25,
    "timing_class": "fixed"
}
```

Never reorder fixed-timing sales.

---

# 11. The preemption logic is too aggressive

The current configuration contains:

```python
_PREEMPT_FRACTION = 2.0
_PREEMPT_MAX_BATCH = 30
_PREEMPT_MIN_FUTURE_QUANTITY = 4
```

and can shift premium products up to three turns early.

The implementation is in `_preempt_shift()`. fileciteturn2file1L268-L319

The fundamental issue is that "opponent is nearby" is not sufficient evidence that moving a sale earlier is profitable.

The code uses a clone-distance score derived from public farm state. fileciteturn2file1L204-L213

But farm-state similarity does not guarantee:

```text
same private inventory
same shed stock
same production timing
same market intentions
same future sales
```

The observation explicitly keeps shed/private inventories private.

Therefore:

```text
farm clone
!=
economic clone
```

### Improvement

Use at least three signals:

1. public farm similarity,
2. market trajectory similarity,
3. observed opponent sales.

Only preempt if all three are sufficiently similar.

---

# 12. P1 needs a different model from P0

The source correctly recognizes that P1 acts after P0 and uses a tighter clone threshold. fileciteturn2file0L36-L39

But this should be taken further.

P1 observes the market **after P0's action**.

Therefore P1 has an information advantage.

P1 should not blindly execute a P0-derived schedule.

Instead:

```text
P0:
    route-first

P1:
    route + market correction
```

For P1, before selling:

```text
Was P0's sale already made?
Did P0 push inventory up?
Did the price already move?
Is the route's planned sale still optimal?
```

This is particularly important for shared-market games.

---

# 13. Fertilizer relay is not safe merely because the game looks like a clone

The fertilizer relay uses checkpoints at steps:

```text
216
240
264
```

and locks if all three are within the clone threshold. fileciteturn2file2L395-L406

It then pre-sells fertilizer three turns early.

The quantity is later repaid at the original scheduled step. fileciteturn2file2L424-L475

This is quantity-neutral, but not necessarily value-neutral.

The price at:

```text
t - 3
```

can be lower than the price at:

```text
t
```

even if the opponent is following a similar farm route.

### Improvement

Only relay fertilizer when:

```text
price(t-3) >= price(t) * safety_factor
```

or when expected market impact makes the earlier sale better.

Otherwise keep the original sale.

---

# 14. There is a hidden state-machine problem in the overlay stack

The code has several independent state stores:

```python
_WEED_STATE
_SHIFT_STATE
_RELAY_STATE
```

Each is indexed by seat.

Each has its own step bookkeeping.

This creates a risk where:

```text
weed repair
    changes route timing

preemption
    assumes old route timing

fertilizer relay
    assumes old route timing

terminal liquidation
    assumes current shed state
```

All four can be operating on different notions of "what the route is doing."

### Required architecture

Replace independent overlays with one controller state:

```python
ControllerState(
    route_index,
    route_phase,
    repair_transaction,
    sale_transactions,
    preemption_transaction,
    relay_transaction,
    expected_positions,
    expected_inventory,
)
```

Every modification updates the same state.

---

# 15. The code's fallback is dangerous for scoring

The exception handler returns:

```python
{
    "farmer": ["PASS"],
    "hands": [["PASS"], ...],
    "market": []
}
```

This is safe from a schema perspective but potentially disastrous economically.

The code currently catches **all exceptions** and silently converts them into PASS actions.

That means a bug can become:

```text
exception
 -> PASS
 -> no market action
 -> no production action
 -> score loss
```

without any visible failure.

### Required improvement

During development, never swallow the exception.

Use:

```python
except Exception as exc:
    # record a compact diagnostic
    ...
    raise
```

For the final submission, use a minimal safe fallback, but only after the implementation has been validated.

At minimum, maintain a counter or deterministic diagnostic flag so a scoring run can tell whether the fallback ever fired.

---

# 16. The route should be validated against the observation before execution

Before using a route action, verify:

## Farmer/hand count

```text
route hand count <= actual hand count
```

## Position

For movement actions:

```text
expected route position ~= actual position
```

## Inventory

For:

```text
PLANT
FEED
PLACE
PICKUP
SELL
```

verify the necessary inventory exists.

## Tile state

For:

```text
PLANT
BUILD_PASTURE
HARVEST
WATER
FERTILIZE
```

verify the tile is compatible.

## Market order

For every sell:

```text
quantity <= available shed quantity
```

and:

```text
current price > configured floor
```

## Route drift

If too many assumptions fail:

```text
abandon fixed route segment
enter recovery planner
```

Do not continue executing stale route actions.

---

# 17. A better route architecture

The replacement should use four layers.

## Layer 1 — Deterministic bootstrap

Steps 0–20:

Use the proven opening.

This is where fixed routes are most reliable because the state is nearly identical.

---

## Layer 2 — Route with state assertions

For each route action:

```python
if state_matches_route(obs, route_node):
    execute(route_node.action)
else:
    recover()
```

The route node should contain expected state, not just an action.

Example:

```python
{
    "action": {
        "farmer": ["PLANT", "WHEAT"]
    },
    "preconditions": {
        "tile_kind": "EMPTY",
        "seed": {"WHEAT": ">=1"}
    },
    "tolerance": {
        "position": 0
    }
}
```

---

## Layer 3 — Local economic controller

For market decisions:

```text
fixed route recommendation
        +
current price
        +
market inventory
        +
town demand
        +
own inventory
        +
opponent observed behavior
        ->
final sell quantity
```

This should override only the market portion when justified.

---

## Layer 4 — Endgame liquidation

At the final 4–8 turns:

1. stop buying anything unnecessary,
2. stop hiring unless a final production cycle is clearly profitable,
3. sell all useful liquid inventory,
4. preserve enough action slots for liquidation,
5. never leave valuable shed inventory stranded.

The existing terminal liquidation concept is directionally correct. fileciteturn2file2L647-L661

---

# 18. Specific economic changes recommended

## 18.1 Prefer sheep when replay evidence says wool is superior

Do not hard-code:

```text
10 cows / 4 sheep
```

from the lower replay.

Use observed profitability.

The supplied Thunder run demonstrates that the higher-scoring policy maintained:

```text
8 cows / 6 sheep
```

purchases per player and generated substantially more wool sales.

Therefore the default animal portfolio should be closer to the Thunder portfolio unless the current market strongly favors milk.

---

## 18.2 Cap hires

Add:

```python
MAX_HIRES_BY_PHASE = {
    "early": ...,
    "mid": ...,
    "late": ...,
}
```

The exact values should be calibrated from replay data.

The key rule is:

> Never hire simply because the route contains a HIRE.

---

## 18.3 Track marginal worker value

For every additional worker:

```text
incremental expected sell value
-
incremental worker cost
```

If negative, do not hire.

---

## 18.4 Track animal marginal value

For each animal type:

```text
expected remaining production
*
expected sale price
-
animal purchase cost
-
feed/care/input cost
```

Use this rather than a fixed cow/sheep schedule.

---

# 19. Market strategy replacement

Replace "rank every sell" with:

### Step A — classify

Every route sell becomes one of:

```text
FIXED
FLEXIBLE
OPPORTUNISTIC
TERMINAL
```

### Step B — calculate value of waiting

For each flexible sale:

```text
wait_value =
    expected_future_price
    - current_price
    - expected_price_impact_difference
```

### Step C — calculate opponent impact

Estimate whether the opponent is likely to sell the same item soon.

### Step D — execute only if expected value is positive

This is much safer than blindly moving a sale because another farm looks similar.

---

# 20. What the score trajectory says about the actual failure

The money difference is initially tiny.

For P0, the Thunder-minus-other cash gap is approximately:

```text
step 0       0
step 160     0
step 193    -75
step 216    -76
step 240    -77
step 264   -879
step 300  -1,331
step 360    -502
step 480  +3,319
step 600 +11,210
step 680 +14,477
step 719 +15,512
```

For P1:

```text
step 0        0
step 160      0
step 193     +9
step 216     +8
step 240     +7
step 264    -12
step 300   +103
step 360   +350
step 480 +5,368
step 600 +7,350
step 680 +11,305
step 719 +9,947
```

This is extremely useful.

It proves the score problem is **not primarily an opening failure**.

The lower-scoring controller is competitive early and loses most of its money during the mid/late economic phase.

Therefore do NOT spend the next iteration primarily optimizing steps 0–100.

Focus on:

```text
~250 onward
animal portfolio
hiring
sell timing
market adaptation
late production
terminal sales
```

---

# 21. The most important observed economic divergence

The other run sells more gross product but earns substantially different revenue composition.

Across both players:

### Thunder

High-value wool revenue:

```text
P0: 15,661
P1: 16,566
```

### Other

High-value wool revenue:

```text
P0: 3,276
P1: 3,274
```

The other run replaces that production with milk.

This is the clearest sign that the lower-scoring policy has drifted into the wrong production specialization.

Do not interpret:

```text
more milk sold
```

as:

```text
better strategy
```

because final score is net money after costs.

---

# 22. Do not compare action sequences without comparing state

A useful replay comparison tool should output:

```text
step
seat
Thunder action
Other action
farm-state delta
private-inventory delta
market-price delta
money delta
reason for divergence
```

The current raw JSON comparison is not enough.

For every divergence, classify it:

```text
ROUTE
WEED_REPAIR
MARKET
PREEMPTION
RELAY
ANIMAL
HIRE
MOVEMENT
RECOVERY
```

Then calculate score contribution by category.

That will tell you which modification actually helps.

---

# 23. Required replay-diff harness

Build a script that takes:

```text
thunder.json
candidate.json
```

and produces:

```text
same_seed: true
same_config: true
step_count: 720

action_divergence_steps: 533

first_divergence:
    step: 84
    seat: 0
    actor: hand1
    thunder: PLANT STRAWBERRY
    candidate: DIG

money_gap:
    P0: +15512 Thunder
    P1: +9947 Thunder

largest_gap:
    P0: step 698
    P1: step 679
```

Then produce a second table:

```text
category            count
movement            ...
planting            ...
watering            ...
harvest             ...
market buy          ...
market sell         ...
hire                ...
animal purchase     ...
weed repair         ...
```

This should become mandatory for every new iteration.

---

# 24. Do not use the current compressed route as an opaque artifact

The enormous base85/zlib strings make the strategy very difficult to audit.

They are acceptable for deployment but bad for development.

During development, keep:

```text
routes/p0.json
routes/p1.json
```

with readable records.

Then optionally compile/compress them for final submission.

This lets you answer:

```text
Why is P0 selling wool here?
Why is P1 buying a cow here?
Why is this worker moving north?
Why is this sell three turns early?
```

without reverse-engineering compressed data.

---

# 25. Replacement controller design

The new controller should follow this structure:

```python
def agent(obs, configuration=None):
    state = get_controller_state(obs)

    if is_bootstrap(state):
        return bootstrap_action(state)

    if route_is_valid(state):
        action = route_action(state)
    else:
        action = recover_route(state)

    action = validate_and_repair_farm_actions(obs, action)

    action = optimize_market_actions(
        obs,
        configuration,
        action,
        state,
    )

    action = apply_conservative_preemption(
        obs,
        action,
        state,
    )

    action = apply_fertilizer_relay_if_profitable(
        obs,
        action,
        state,
    )

    action = terminal_cleanup(obs, action, state)

    return validate_action(obs, action)
```

The important difference is:

```text
route -> mutate
```

becomes:

```text
state -> route candidate -> validate -> optimize -> validate -> execute
```

---

# 26. Route validity score

Implement a route confidence score:

```text
confidence =
    position_match
  + hand_count_match
  + tile_match
  + inventory_match
  + crop_state_match
  + animal_state_match
  + market_regime_match
```

Example:

```python
if confidence >= 0.90:
    use_route
elif confidence >= 0.70:
    use_route_with_local_repairs
else:
    enter_recovery
```

The exact thresholds should be calibrated.

The important principle is that a route must be allowed to fail gracefully.

---

# 27. Recovery should be local, not global

If one hand hits a weed:

Do NOT discard the whole farm plan.

Instead:

```text
hand 3:
    DIG
    repeat intended action

other hands:
    continue route
```

If the farmer is displaced:

```text
farmer:
    recalculate shortest path to next required task
```

If the market diverges:

```text
market:
    re-optimize sell quantity
```

Only abandon the whole route if multiple independent state assumptions fail.

---

# 28. Preemption should have a profit gate

Before moving a sale from `t` to `t-k`, calculate:

```text
current_sale_value
+
expected_saved_price_impact
-
expected_lost_future_price
-
opportunity_cost
```

Only preempt if positive.

Minimum rule:

```python
if expected_gain <= 0:
    do_not_preempt()
```

Do not use clone distance as the only reason.

---

# 29. Fertilizer relay should also have a profit gate

The relay currently uses clone confirmation and a fixed three-turn lead.

Change it to:

```text
clone confidence
AND
future fertilizer sale exists
AND
current fertilizer price is attractive
AND
earlier sale is not worse than expected future sale
AND
market order capacity remains
```

If any condition fails:

```text
do not relay
```

---

# 30. Market-order capacity must be treated as a scarce resource

The environment allows at most 10 market orders per player per turn.

The current code checks this in several places.

But multiple overlays can consume those slots.

Example:

```text
base route:       8 orders
preemption:      +2 orders
relay:           +1 order
terminal:        +1 order
```

Now the environment can silently drop orders beyond the maximum.

The configuration explicitly says extra orders beyond the limit are silently dropped.

Therefore the controller must reserve capacity:

```text
fixed route orders
>
required corrective orders
>
opportunistic orders
```

Never let an optimization layer silently crowd out required orders.

---

# 31. The market optimizer should not buy inventory just to support a stale route

The lower replay repeatedly buys WHEAT at slightly different quantities/times.

Some of these differences are only small, but once the route has drifted, buying inputs to preserve an invalid route can create unnecessary expenses.

Before every route-driven buy:

```text
Is this input still needed?
Will it be consumed by a valid downstream action?
Will the resulting production happen before season end?
```

If not:

```text
do not buy
```

---

# 32. The agent needs a "season remaining" model

At every production decision:

```text
remaining_steps
remaining_days
crop growth time
animal output cycle
expected sale opportunity
```

must be considered.

Late-season inputs should be rejected if they cannot produce saleable output before the end.

This is especially important because the final reward is cash, not production count.

---

# 33. What not to do in the next version

Do NOT:

- simply copy more Thunder actions,
- increase the number of preemption rules,
- increase hiring,
- increase animal count,
- sell more total product,
- add another overlay on top of the existing overlays,
- assume same seed means same market,
- use farm clone distance as proof of identical strategy,
- swallow exceptions and continue silently,
- reorder all market sells indiscriminately,
- let route timing and replay timing use different step conventions.

These changes may make the code look more sophisticated while making it less stable.

---

# 34. Priority order for fixes

## P0 — Must fix

### 1. Route/replay step alignment

Verify exactly whether:

```text
obs step 0 -> PASS
obs step 1 -> route[0]
```

is required by the submission harness.

Make one canonical route-index function.

### 2. Add route-state validation

Never execute a fixed action when its prerequisites are absent.

### 3. Stop treating clone distance as economic identity

Require market/behavior evidence too.

### 4. Cap hiring and animal expansion

Prevent the lower-run pattern of excessive hires and cow purchases.

### 5. Add final-cash optimization

Evaluate actions by net money, not gross revenue.

---

# 35. P1 — High-value improvements

1. Preserve Thunder's sheep/wool specialization unless the live market clearly disproves it.
2. Make P1 market-aware because P1 sees P0's effects.
3. Make sell reordering conditional on timing class.
4. Add profit-gated preemption.
5. Add profit-gated fertilizer relay.
6. Add route drift detection.
7. Build the replay-diff diagnostic.

---

# 36. P2 — Engineering improvements

1. Uncompress route data during development.
2. Give route nodes readable names.
3. Add deterministic controller state.
4. Add assertions for inventory and positions.
5. Log fallback exceptions during development.
6. Track action transformations by overlay.
7. Record every shifted sale as a transaction.

---

# 37. Recommended validation experiment

Run four agents with the **same seed**:

### Experiment A

```text
Thunder vs Thunder
```

Expected benchmark:

```text
~59k / ~61k
```

for the supplied Thunder replay.

### Experiment B

```text
Candidate vs Candidate
```

Measures whether the candidate is internally stable.

### Experiment C

```text
Candidate vs Thunder
```

Measures opponent adaptation.

### Experiment D

```text
Thunder vs Candidate
```

Measures the reverse seat effect.

Then compare:

```text
P0 score
P1 score
market prices
animal mix
hire count
wool produced
milk produced
sell timing
```

This is far more informative than comparing two independent replay files.

---

# 38. What "scoring" is actually doing here

There is no evidence in the supplied files that the scoring system is refusing to score the candidate.

The lower replay has:

```text
statuses = ["DONE", "DONE"]
```

and a numeric reward for both players.

Therefore it **is scoring**.

The issue is that the candidate simply earns less money.

The supplied reward values are:

```text
Thunder:
    P0 = 59137
    P1 = 61422

Candidate:
    P0 = 43625
    P1 = 51475
```

So the debugging target should be:

```text
why did the candidate finish with less cash?
```

not:

```text
why did the scorer fail?
```

---

# 39. Final diagnosis

The lower score is best explained by a combination of:

1. **Different trajectory despite identical seed** because the agents affect shared state.
2. **Fixed replay routing** that assumes a replay state instead of validating the live state.
3. **Route/step-index ambiguity** between replay actions and embedded route actions.
4. **Weed repair and other overlays modifying the route**, creating schedule drift.
5. **Over-hiring** relative to Thunder.
6. **Different animal portfolio**, especially substantially fewer sheep and much less wool production.
7. **Too much reliance on farm-state clone distance** for economic preemption.
8. **Market sell transformations that can interfere with deliberate replay timing.**
9. **Fertilizer relay based on clone confirmation rather than explicit profitability.**
10. **No strong net-profit model** connecting production decisions, input costs, worker costs, animal costs, and final liquidation.
11. **Silent exception fallback to PASS**, which can hide real code defects.

The most important insight is:

> The candidate should not try to reproduce Thunder's action sequence. It should reproduce Thunder's **decision logic under the candidate's actual state**.

---

# 40. Target architecture

The desired final architecture is:

```text
                 ┌────────────────────┐
                 │ current observation│
                 └─────────┬──────────┘
                           │
                           v
                ┌──────────────────────┐
                │ state normalization  │
                └──────────┬───────────┘
                           │
                           v
                ┌──────────────────────┐
                │ route-state matcher  │
                └───────┬───────┬──────┘
                        │       │
                  valid │       │ invalid
                        │       v
                        │   local recovery
                        v
                  route candidate
                        │
                        v
                farm-action validator
                        │
                        v
                 market optimizer
                        │
                        v
                 preemption gate
                        │
                        v
                 fertilizer gate
                        │
                        v
                terminal liquidation
                        │
                        v
                   final validator
                        │
                        v
                     action
```

This is the replacement strategy to implement.

The fixed Thunder route should remain as a **prior**, because it contains useful information. It should not remain the unquestioned source of truth.

---

# 41. Bottom line

If only five changes are made, make these:

```text
1. Fix/verify route indexing against the replay step convention.
2. Add strict route-state validation and local recovery.
3. Stop using clone distance alone to justify market preemption.
4. Restore a profit-driven animal/hiring policy instead of the lower run's
   extra cows + extra hires.
5. Optimize final cash, not gross sales.
```

The supplied data strongly indicates that the big score loss happens in the middle/late game rather than the opening. The P0 gap grows from roughly hundreds of dollars around the midgame to **15,512 dollars by the end**, while P1 ends **9,947 dollars behind**. That is exactly the signature of an economic-policy drift, not a scoring-system failure.

---

## Evidence references

- The Thunder replay reports seed `0`, the official configuration, and rewards `59137 / 61422`. fileciteturn3file1L19-L19
- The candidate replay reports the same seed/configuration and rewards `43625 / 51475`. fileciteturn1file6L387-L395
- The code identifies its routes as P0/P1 routes extracted from Thunder replays and lists its runtime overlays. fileciteturn2file0L11-L39
- The code selects the seat-specific fixed route and applies the overlay stack in sequence. fileciteturn1file1L125-L145
- The preemption logic uses public farm clone distance and can shift premium sales by up to three turns. fileciteturn2file1L204-L319
- The fertilizer relay similarly uses checkpoint-based clone detection and a three-step lead. fileciteturn2file2L395-L475
- Weed repair replaces route planting/building with DIG and then replays the intended action. fileciteturn2file2L496-L536
- The market scorer ranks sales using estimated price impact and demand urgency. fileciteturn2file2L569-L630
- Terminal liquidation is implemented in the final four steps. fileciteturn2file2L647-L661
