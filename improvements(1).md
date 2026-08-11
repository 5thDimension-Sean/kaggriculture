# Replacement `improvements.md` — routing/scoring audit for `91816042.json`

## Executive conclusion

The lower score is **not** explained by the seed.

Both replays explicitly report `seed: 0`, use the same Kaggriculture module/version, the same 720-step episode length, and the same configuration. The important difference is that the agents do **not** take the same actions. In this environment, the seed controls deterministic/random event generation, but market inventory, prices, cash, farm state, hired-hand count, inventory, and future opportunities are endogenous to the actions. Once the agents make different purchases/sales/movement decisions, the two games are no longer on the same state trajectory.

The strongest concrete bug in the supplied `main.py` is an **off-by-one route-indexing error**.

The embedded route arrays have **719 actions**, while the environment has **720 steps**. The first embedded route action is the action that appears at **step 1** of `91816042.json`, not step 0. However, `agent()` uses:

```python
step = min(max(0, int(obs["step"])), len(actions) - 1)
action = actions[step]
```

Therefore:

```text
environment step 0 -> route[0]
environment step 1 -> route[1]
...
environment step 718 -> route[718]
environment step 719 -> route[718]   # clamped/repeated
```

but the replay alignment is:

```text
environment step 0 -> PASS/default
environment step 1 -> route[0]
environment step 2 -> route[1]
...
environment step 719 -> route[718]
```

That is a one-step shift for the entire backbone route.

This is not theoretical: programmatic comparison of the embedded routes against `91816042.json` shows that, after shifting the replay by one step, the P0 route matches **647/719** route actions and the P1 route matches **668/719** route actions. The first substantial mismatch then occurs much later (P0 route index 174; P1 route index 77), which is exactly what you would expect from a replay-derived route plus runtime repair overlays.

### Immediate fix

Do **not** try to tune the market scoring first.

Fix route indexing first:

```python
replay_index = int(obs_step) - 1

if replay_index < 0:
    action = {
        "farmer": ["PASS"],
        "hands": [["PASS"] for _ in current_hands],
        "market": [],
    }
else:
    replay_index = min(replay_index, len(actions) - 1)
    action = actions[replay_index]
```

Then make **all** route-relative logic use the same `replay_index`, including:

- future sell lookup,
- preemption,
- fertilizer relay,
- weed replay/tracing,
- terminal route handling,
- any due/repayment bookkeeping.

Do not fix only the main `actions[step]` lookup. That would leave the preemption/relay subsystems internally misaligned.

---

# 1. What the two JSONs actually show

## 1.1 Episode metadata

`thunder(1).json`:

- Episode: `91706798`
- Seed: `0`
- Rewards: `[48602.0, 49152.0]`

`91816042.json`:

- Episode: `91816042`
- Seed: `0`
- Rewards: `[45207.0, 46452.0]`

Reward gaps:

- P0: `48602 - 45207 = +3395`
- P1: `49152 - 46452 = +2700`

Both episodes have:

- `episodeSteps = 720`
- `boardSize = 10`
- `turnsPerDay = 24`
- `townShopSellInterval = 4`
- `townCenterSellInterval = 24`
- `maxMarketOrdersPerTurn = 10`
- `startingMoney = 3000`
- same Kaggriculture module version `1.32.6`

So the seed/configuration mismatch hypothesis is not supported by the supplied files.

## 1.2 Same seed does not mean same game trajectory

The environment is not a fixed precomputed sequence of states.

For example, at the beginning:

### THUNDER

At step 1, both players:

- hire 4 hands,
- buy 19 WHEAT,
- buy 4 SHEEP,
- buy 5 WHEAT seeds,
- buy 5 MELON seeds.

Cash becomes:

```text
$3000 -> $69
```

At step 2 they:

- sell 14 WHEAT,
- buy 1 COW.

### `91816042`

At step 1, both players:

- hire 4 hands,
- buy 1 COW,
- buy 4 SHEEP,
- buy 5 WHEAT seeds,
- buy 5 MELON seeds,
- buy 5 WHEAT product.

Cash becomes:

```text
$3000 -> $7
```

At step 2 they do **not** perform the THUNDER WHEAT sale/cow-purchase sequence.

This is the first meaningful state divergence.

The important observation is that the different actions affect the market and the player's cash immediately. From there, farm operations and later market prices become path-dependent.

---

# 2. The most important routing bug: one-step offset

## 2.1 Evidence from `main.py`

The route selector is:

```python
def _actions_for_seat(seat):
    return _ACTIONS_P1 if seat == 1 else _ACTIONS_P0
```

and `agent()` does:

```python
actions = _actions_for_seat(seat)
step = min(max(0, int(_get(obs, "step", 0) or 0)), len(actions) - 1)
...
action = _weed_repair_action(obs, _copy_action(actions[step]), step)
```

The route arrays contain 719 actions, not 720.

That means the code assumes:

```text
route index == environment step
```

but the replay evidence says:

```text
route index == environment step - 1
```

## 2.2 Direct proof

The embedded route's P0 action at route index 0 is:

```text
BUY_ANIMAL COW 1
BUY_ANIMAL SHEEP 4
BUY_SEED WHEAT 5
BUY_SEED MELON 5
BUY_PRODUCT WHEAT 5
```

That is not the environment's step-0 action.

The environment's step 0 is:

```text
PASS
```

The route index-0 action corresponds to the next replay step.

Likewise, route index 1 is the COW pickup/movement action, which corresponds to step 2 in `91816042.json`.

So the actual alignment is:

```text
route[0] == replay step 1
route[1] == replay step 2
route[2] == replay step 3
...
```

not:

```text
route[0] == replay step 0
```

## 2.3 Quantified alignment

When comparing the embedded P0 route against `91816042.json` using:

```text
route[index] == replay[index + 1]
```

the match is:

```text
647 / 719 = 89.99%
```

For P1:

```text
668 / 719 = 92.91%
```

That is extremely strong evidence that the route arrays themselves are basically aligned to replay step 1 onward.

The first mismatch after this correction is:

- P0: route index 174
- P1: route index 77

Those later mismatches are consistent with runtime modifications such as weed repair and state-dependent overlays.

This makes the one-step indexing bug the first thing to fix.

---

# 3. Why the existing "step-indexing was verified" claim is misleading

The top of `main.py` says the route/replay step indexing was empirically verified and that `obs.step` maps 1:1 onto the embedded route arrays.

That conclusion is contradicted by the actual supplied route/replay data.

The route arrays have length 719 while the game has 720 steps, and the first route entry matches step 1 rather than step 0.

The statement should therefore be removed/replaced with an explicit invariant test.

Do not trust a manually inspected replay for indexing.

Add an automated test:

```python
assert len(_ACTIONS_P0) == 719
assert len(_ACTIONS_P1) == 719

# If routes are derived from a replay whose step 0 is the initial PASS:
# route[0] must correspond to replay step 1.
```

Even better, store metadata next to the compressed route:

```python
_ROUTE_START_STEP = 1
_ROUTE_END_STEP = 719
```

Then centralize:

```python
def _route_index(env_step):
    return env_step - _ROUTE_START_STEP
```

No other function should calculate route indices itself.

---

# 4. The off-by-one bug contaminates more than the backbone action

This is important.

Fixing only:

```python
actions[step]
```

is insufficient.

The route index is also used indirectly by:

## 4.1 Preemption

`_future_sells_at()` currently does:

```python
actions[step + horizon]
```

If `step` is the environment step but `actions` is indexed from replay step 1, the future lookup is also shifted.

Correct conceptual form:

```python
current_route_index = route_index(env_step)
future_route_index = current_route_index + horizon
```

or:

```python
future_env_step = env_step + horizon
future_route_index = route_index(future_env_step)
```

The second form is safer because it keeps the semantic unit explicit.

## 4.2 Fertilizer relay

`_fertilizer_relay_qty()` currently calculates:

```python
future_step = step + _RELAY_LEAD
...
actions[future_step]
```

Again, this treats an environment step as a route index.

It should use the centralized route-index conversion.

## 4.3 Weed repair

`_weed_repair_action()` traces:

```python
_trace_actor_action(step - 1, actor, seat)
```

while `_trace_actor_action()` directly indexes the route.

Once the base route is corrected, this code needs to be rewritten around **environment-step semantics**, not mixed route/environment indices.

Otherwise a DIG repair can replay the wrong actor action after the weed is removed.

## 4.4 Final-step behavior

There are 720 environment steps but only 719 route entries.

Current code clamps:

```python
step = min(..., len(actions) - 1)
```

so step 719 becomes route index 718.

That is an implicit duplicate of the previous route action.

This is especially dangerous because the terminal liquidation layer also starts at step 716.

The final four steps should be handled explicitly, not by accidentally repeating route index 718.

---

# 5. The current route is not THUNDER's route

Another important distinction:

`main.py` describes its embedded routes as coming from:

```text
P0: episode 91385999
P1: episode 91471546
```

Those are not the supplied `thunder(1).json` episode (`91706798`).

The supplied THUNDER replay scores:

```text
P0 = 48,602
P1 = 49,152
```

The embedded route's header claims source replays with much higher individual scores:

```text
P0 = 139,403
P1 = 148,866
```

Therefore there are multiple layers of confusion:

1. `thunder(1).json` is one replay.
2. `main.py` embeds routes from other replay IDs.
3. `91816042.json` is the current replay generated by `main.py`.
4. The current route is shifted relative to the environment step numbering.
5. Runtime overlays modify the route further.

Do not treat `main.py` as a literal reproduction of `thunder(1).json`.

It is a replay-derived controller with overlays.

That is why comparing only final scores is misleading.

---

# 6. Exact behavioral difference at the beginning

The first seven steps are especially revealing.

## THUNDER

```text
step 0: PASS

step 1:
  HIRE x4
  BUY_PRODUCT WHEAT 19
  BUY_ANIMAL SHEEP 4
  BUY_SEED WHEAT 5
  BUY_SEED MELON 5

step 2:
  farmer PICKUP COW
  hands move toward animals/resources
  SELL WHEAT 14
  BUY_ANIMAL COW 1

step 3:
  PICKUP WHEAT
  hands continue route

step 4:
  BUILD_PASTURE
  one hand picks up COW

step 5:
  BUILD_PASTURE
  PLACE SHEEP

step 6:
  PLACE COW
  PLANT MELON
  FEED WHEAT

step 7:
  FEED/WATER/CARE operations
```

## `91816042`

```text
step 0: PASS

step 1:
  HIRE x4
  BUY_ANIMAL COW 1
  BUY_ANIMAL SHEEP 4
  BUY_SEED WHEAT 5
  BUY_SEED MELON 5
  BUY_PRODUCT WHEAT 5

step 2:
  PICKUP COW
  movement
  no WHEAT sale
  no COW purchase

step 3:
  PICKUP WHEAT
  movement

step 4:
  BUILD_PASTURE
  no COW pickup on the third hand

step 5:
  BUILD_PASTURE
  PLACE SHEEP

step 6:
  PLACE COW
  PLANT MELON
  third hand remains PASS

step 7:
  FEED/WATER/CARE
```

The first major discrepancy is therefore not a sophisticated market-ranking issue.

It is a **capital allocation / route timing discrepancy at step 1**.

---

# 7. Why THUNDER can be ahead even though it buys the same broad resources

The important distinction is **timing**.

THUNDER effectively performs:

```text
buy WHEAT -> use/position workers -> sell WHEAT -> buy COW
```

The current replay does:

```text
buy COW -> buy some WHEAT -> keep COW
```

The THUNDER sequence preserves the ability to generate an early sale and uses that sale to fund the COW.

The current sequence spends the money before generating the sale.

That explains the immediate cash difference:

```text
THUNDER after step 1: $69
CURRENT after step 1: $7
```

The difference is only $62 at that instant, but the bigger issue is that the **actions taken to reach that cash position are different**.

The farm hands also move differently, which affects when pasture placement, crop planting, feeding, watering, care, and harvesting happen.

---

# 8. A second major issue: hardcoded replay control is fragile

The controller is fundamentally:

```text
choose prerecorded action
    ↓
repair obvious invalid/weed actions
    ↓
modify market sells
    ↓
preempt premium sales
    ↓
relay fertilizer
    ↓
liquidate at terminal
```

That is a useful competition strategy when the replay is extremely close to the target environment.

It is not a robust general policy.

The supplied current game demonstrates why.

A single early deviation can cause:

- different cash,
- different shed inventory,
- different per-hand inventory,
- different farm positions,
- different animal placement timing,
- different crop maturity timing,
- different market inventory,
- different market prices,
- different number of hands,
- different public farm signature,
- different clone distance,
- different preemption activation,
- different fertilizer-relay activation.

At that point, a prerecorded action sequence is no longer a faithful plan.

---

# 9. `_clone_distance()` is too coarse for route gating

Current clone distance is based on:

```python
(
    abs(hand_count_difference)
    + 3 * abs(unlocked_quadrant_difference)
    + crop/animal/structure/weed count differences
)
```

This is useful as a cheap similarity metric, but it ignores:

- exact hand positions,
- farmer position,
- crop positions,
- animal positions,
- crop age,
- crop watering state,
- fertilizer duration,
- shed inventory,
- per-hand inventory,
- money,
- market inventory,
- current market price.

Two farms can have the same counts while being operationally very different.

That means a clone gate can incorrectly classify two games as "close".

The preemption code should use a multi-level similarity test:

### Level 1: cheap signature

Use current count-based signature.

### Level 2: positional signature

When the cheap signature passes, compare:

- farmer position,
- every hand position,
- unlocked quadrants,
- number of hands.

### Level 3: farm-state signature

Compare:

- crop type/count,
- animal count,
- structure count,
- watered state,
- fertilized state,
- approximate maturity.

Only enable aggressive preemption when the state is genuinely close.

---

# 10. Preemption can become self-referential

The preemption system uses future sells from the same embedded route:

```python
future = _future_sells_at(step, horizon, seat)
```

and then changes the current action.

That is reasonable for a replay optimizer, but it creates a hidden dependency:

```text
route -> preemption -> altered market -> altered state -> clone distance
        -> later preemption decision
```

This means a small early route mismatch can alter whether future preemption activates.

The result is path-dependent and difficult to debug.

The replacement implementation should log every preemption decision:

```text
step
seat
clone_distance
future_horizon
item
future_quantity
current_price
target_quantity
reason
```

Without this telemetry, score regressions are hard to attribute.

---

# 11. The fertilizer relay has the same indexing problem

The relay uses checkpoints:

```text
216
240
264
```

and then looks at a future route sell.

Because the route/environment index relationship is currently wrong, these checkpoints are semantically ambiguous.

The correct implementation should explicitly say:

```python
RELAY_CHECKPOINT_ENV_STEPS = (216, 240, 264)
```

and then:

```python
route_index = _route_index(env_step)
```

only when looking into the prerecorded route.

Never pass an environment step directly into a route array.

---

# 12. Market ranking is not the first problem

The code contains a market-impact model:

```python
current_quote
later_quote
quantity * (current_quote - later_quote)
```

and demand urgency:

```python
score * (1 + alpha * urgency)
```

This is a reasonable secondary optimization.

But it should not be used to compensate for a bad route.

A controller that executes the wrong crop/animal/farm schedule but sells its wrong inventory in an excellent order can still score badly.

The correct priority is:

```text
1. route alignment
2. farm-state alignment
3. resource/cash feasibility
4. action validity
5. market timing
6. preemption
7. terminal liquidation
```

not:

```text
market scoring first
```

---

# 13. The market-price model must remain secondary

The code reconstructs market prices using `_MARKET_PARAMS`.

That is useful for scoring sell orders, but it should not become the source of truth if the observation already contains:

```python
obs["market"]["prices"]
```

The environment's reported current price should be authoritative for:

```text
current sale value
```

The reconstructed curve should only be used for:

```text
estimated post-sale price / marginal impact
```

That distinction should remain explicit.

---

# 14. The exception fallback is dangerous for scoring

The main agent catches all exceptions:

```python
except Exception:
    return PASS...
```

This prevents crashes, but it can silently turn a logic bug into hundreds of wasted actions.

For development/testing, replace the silent fallback with diagnostic logging.

Recommended:

```python
except Exception as exc:
    _LAST_ERROR = {
        "step": obs.get("step"),
        "player": obs.get("player"),
        "error": repr(exc),
    }
    ...
```

For the final competition version, a safe fallback can remain, but debugging mode must make the exception visible.

A route controller that silently PASSes after an indexing/state error can look like a "bad strategy" when the real problem is a code exception.

---

# 15. The route should have explicit metadata

Instead of relying on comments, store:

```python
_ROUTE_META = {
    "P0": {
        "source_episode": 91385999,
        "source_start_step": 1,
        "source_end_step": 719,
    },
    "P1": {
        "source_episode": 91471546,
        "source_start_step": 1,
        "source_end_step": 719,
    },
}
```

Then enforce:

```python
assert len(_ACTIONS_P0) == 719
assert len(_ACTIONS_P1) == 719
```

and:

```python
def _route_action(actions, env_step):
    if env_step < 1:
        return _initial_action(...)
    index = env_step - 1
    if index >= len(actions):
        return _terminal_default(...)
    return actions[index]
```

This makes the semantics obvious.

---

# 16. Recommended replacement architecture

The improved controller should have five layers.

## Layer A — deterministic replay backbone

```text
environment step
      ↓
route index conversion
      ↓
position-specific route
```

This layer must be exact.

## Layer B — state validity

Before returning the route action:

```text
Does this action make sense in the current state?
```

Check:

- enough money,
- enough seeds,
- enough shed inventory,
- enough hand inventory,
- correct tile type,
- correct position,
- animal/building compatibility,
- current number of hands.

## Layer C — repair

If the route action is invalid:

```text
repair minimally
```

Do not rewrite the whole route.

Examples:

```text
weed where PLANT -> DIG
weed where BUILD_PASTURE -> DIG
missing item -> skip impossible action
missing hand -> PASS
```

## Layer D — market optimization

Only after the route is aligned:

```text
price floor
market impact
demand urgency
preemption
fertilizer relay
```

## Layer E — terminal liquidation

Only after all other layers:

```text
steps 716-719
```

Liquidate remaining shed inventory subject to the 10-order limit.

---

# 17. Exact replacement for route indexing

Use this pattern:

```python
_ROUTE_START_STEP = 1

def _route_index(env_step):
    try:
        env_step = int(env_step)
    except (TypeError, ValueError):
        env_step = 0
    return env_step - _ROUTE_START_STEP


def _route_action(actions, env_step):
    idx = _route_index(env_step)

    if idx < 0:
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": [],
        }

    if idx >= len(actions):
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": [],
        }

    return _copy_action(actions[idx])
```

Then:

```python
env_step = int(obs["step"])
action = _route_action(actions, env_step)
```

This is much safer than clamping.

Clamping hides missing-route errors.

---

# 18. Exact replacement for future route lookups

Use:

```python
def _route_future_action(actions, env_step, delta):
    future_env_step = int(env_step) + int(delta)
    return _route_action(actions, future_env_step)
```

Then:

```python
future_action = _route_future_action(actions, step, horizon)
```

This ensures preemption uses the same coordinate system as the main route.

---

# 19. Exact replacement for fertilizer relay lookup

Instead of:

```python
future_step = step + _RELAY_LEAD
actions[future_step]
```

use:

```python
future_action = _route_future_action(
    _actions_for_seat(seat),
    step,
    _RELAY_LEAD,
)

for order in future_action.get("market", []):
    ...
```

This removes the hidden index conversion.

---

# 20. Required tests before submitting another run

## Test 1 — initial alignment

At environment step 0:

```text
expected: PASS / no market orders
```

At environment step 1:

```text
expected: route[0]
```

At environment step 2:

```text
expected: route[1]
```

## Test 2 — route length

```python
assert len(_ACTIONS_P0) == 719
assert len(_ACTIONS_P1) == 719
```

## Test 3 — no accidental clamping

At step 719:

```text
do not silently use route[718]
```

Handle terminal behavior explicitly.

## Test 4 — preemption coordinate system

For a route sell at environment step X:

```text
future +3 must inspect environment step X+3,
not array index X+3 by accident.
```

## Test 5 — fertilizer coordinate system

Same test for fertilizer.

## Test 6 — hand alignment

After every action:

```python
len(action["hands"]) == len(obs["farms"][seat]["hands"])
```

## Test 7 — deterministic replay

Run the exact same agent twice against seed 0.

If the environment and agent are deterministic, action hashes should be identical.

## Test 8 — route-only baseline

Disable all overlays:

```text
weed repair = OFF
preemption = OFF
relay = OFF
liquidation = OFF
ranking = OFF
```

Run one episode.

Then enable each overlay one at a time.

This identifies which mechanism actually helps.

---

# 21. Recommended A/B test matrix

Do not compare only final score.

Run:

| Variant | Route offset | Weed repair | Sell ranking | Preemption | Relay | Liquidation |
|---|---:|---:|---:|---:|---:|---:|
| A | fixed | off | off | off | off | off |
| B | fixed | on | off | off | off | off |
| C | fixed | on | on | off | off | off |
| D | fixed | on | on | on | off | off |
| E | fixed | on | on | on | on | off |
| F | fixed | on | on | on | on | on |

The important first comparison is:

```text
BROKEN OFFSET vs FIXED OFFSET
```

If fixing the offset produces a large score jump, do not spend time tuning the market model until that experiment is complete.

---

# 22. What to log for every episode

Create a compact diagnostic log:

```text
step
seat
route_index
route_action
final_action
repair_reason
clone_distance
preempted
relay_fired
terminal_liquidation
money
market_price
market_inventory
shed_summary
hand_count
unlocked_quadrants
```

For every changed action, log:

```text
ORIGINAL:
...

FINAL:
...

REASON:
...
```

This turns "why did the score fall?" into a directly answerable question.

---

# 23. Score attribution

For each run, compute:

```text
final money
money spent
money earned
number of sells
sell revenue
number of hires
hire cost
animals purchased
seeds purchased
land purchases
wasted inventory
terminal inventory
terminal liquidation revenue
weed repairs
preemption count
relay count
invalid/skipped route actions
```

The current JSONs already show that the score difference is not simply "one bad final sell".

The cash trajectories diverge early and substantially.

At selected checkpoints:

### Step 216

THUNDER:

```text
P0: $342
P1: $342
```

CURRENT:

```text
P0: $145
P1: $71
```

### Step 264

THUNDER:

```text
P0/P1: $4338
```

CURRENT:

```text
P0: $5485
P1: $4628
```

This is important: the current agent is not uniformly behind.

At some checkpoints it is ahead.

That means the problem is **trajectory quality**, not simply a constant percentage penalty.

### Step 600

THUNDER:

```text
P0: $31851
P1: $32412
```

CURRENT:

```text
P0: $31590
P1: $36861
```

Again, P1 is substantially ahead at this checkpoint but ends at only:

```text
P1 = $46452
```

versus THUNDER:

```text
P1 = $49152
```

Therefore the final ~120 steps and/or inventory/liquidation decisions matter substantially.

---

# 24. Important observation about P0/P1

The controller deliberately uses separate routes:

```python
_ACTIONS_P0
_ACTIONS_P1
```

That is correct in principle.

P1 should not simply copy P0 because:

- P0 acts first,
- P1 sees market effects from P0,
- P1's starting farm state is similar but not identical in temporal context,
- market prices are already changed.

The supplied THUNDER replay also shows symmetric-looking early actions, but later states need not remain symmetric.

The P1 route should therefore be evaluated independently.

Do not "average" P0/P1 routes.

---

# 25. Do not over-tighten the profit gate

The existing comments say that a base-price-ratio gate was tested and rejected because it suppressed relay/preemption activity.

That conclusion should be retained unless new experiments contradict it.

The market is intentionally dynamic and can trade below configured base prices.

Therefore:

```text
current price < configured base
```

does **not** automatically mean:

```text
selling now is bad
```

The better signal is:

```text
marginal price impact
+
near-term demand
+
future planned quantity
+
terminal horizon
```

not a simple base-price comparison.

---

# 26. What I would change first, in exact order

## Priority 0 — FIX NOW

### A. Route index

Change:

```python
step -> actions[step]
```

to:

```python
route_index = step - 1
```

with explicit step-0 handling.

### B. Remove route clamping

Do not silently map step 719 to route 718.

### C. Centralize route indexing

Every route lookup must use one helper.

---

## Priority 1 — VERIFY

### D. Replay parity test

Verify:

```text
route[0] == source replay step 1
route[1] == source replay step 2
...
```

for both routes.

### E. Confirm source replay IDs

Make sure the route actually corresponds to the intended source episodes.

Do not label a route "THUNDER" if it is actually from another replay.

---

## Priority 2 — MAKE OVERLAYS SAFE

### F. Rewrite weed repair around environment-step semantics.

### G. Rewrite preemption future lookup around environment-step semantics.

### H. Rewrite fertilizer relay future lookup around environment-step semantics.

### I. Add diagnostic counters.

---

## Priority 3 — IMPROVE ROBUSTNESS

### J. Add farm-state validation before route actions.

### K. Add positional clone similarity.

### L. Detect when the current game has diverged too far from the replay.

If divergence is large, stop blindly replaying and switch to a fallback policy.

---

# 27. Recommended divergence detector

Define:

```text
route confidence =
    farm similarity
    + hand count similarity
    + unlocked quadrant similarity
    + position similarity
    + inventory feasibility
```

Then use:

```text
HIGH confidence:
    replay route

MEDIUM confidence:
    replay route + conservative repairs

LOW confidence:
    stop using replay-specific movement
    use a state-driven farming policy
```

This is much safer than continuing to execute an old route after the state has diverged.

---

# 28. Replacement control flow

The final controller should conceptually be:

```python
def agent(obs, configuration=None):
    seat = _seat(obs)
    env_step = _env_step(obs)

    # 1. Get correctly aligned replay action.
    action = _route_action(
        _actions_for_seat(seat),
        env_step,
    )

    # 2. Ensure the number of hands is valid.
    action = _align_hands(action, obs)

    # 3. Check whether route action is feasible.
    action = _repair_invalid_route_action(obs, action, env_step)

    # 4. Weed repair.
    action = _weed_repair_action(obs, action, env_step)

    # 5. Market safety.
    action = _price_floor_guard(obs, action)

    # 6. Market ordering.
    action = _rank_sell_slots(obs, action, configuration)

    # 7. Only if replay confidence is high:
    action = _preempt_shift(obs, action, env_step)
    action = _fertilizer_relay(obs, action, env_step)

    # 8. Terminal liquidation.
    action = _terminal_liquidation(obs, action, env_step)

    return _align_hands(action, obs)
```

The important change is not the exact order of every overlay.

The important change is that **all overlays share one definition of `env_step` vs `route_index`.**

---

# 29. Bottom line

The supplied evidence points to this hierarchy:

### Very high confidence

**1. The route is indexed one step too early.**

This is directly supported by:

- 720 environment steps,
- 719 route actions,
- route[0] matching replay step 1,
- ~90% route parity after shifting the current replay by one step.

### Very high confidence

**2. Same seed does not imply same score.**

The agents take different actions immediately, and the market/farm state is action-dependent.

### High confidence

**3. The first capital-allocation decision is materially different.**

THUNDER delays the COW purchase and funds it with an early WHEAT sale; the current replay buys the COW immediately and leaves only $7.

### High confidence

**4. The indexing bug also affects preemption, fertilizer relay, and weed replay.**

Those systems use route arrays based on the same ambiguous `step` coordinate.

### High confidence

**5. The current route is not literally the supplied THUNDER replay.**

`main.py` identifies different source episode IDs.

### Medium/high confidence

**6. The hardcoded route needs a divergence fallback.**

A replay controller is strongest when the current game remains close to its source replay. Once farm state diverges, blindly replaying movement and production decisions becomes increasingly expensive.

---

# 30. Minimal patch that should happen before anything else

If you only make one change, make this one:

```python
def _route_index(env_step):
    return int(env_step) - 1


def _route_action(actions, env_step):
    idx = _route_index(env_step)

    if idx < 0:
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": [],
        }

    if idx >= len(actions):
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": [],
        }

    return _copy_action(actions[idx])
```

Then replace the current:

```python
step = min(max(0, int(_get(obs, "step", 0) or 0)), len(actions) - 1)
action = _weed_repair_action(obs, _copy_action(actions[step]), step)
```

with:

```python
env_step = int(_get(obs, "step", 0) or 0)
action = _route_action(actions, env_step)
action = _weed_repair_action(obs, action, env_step)
```

Then update `_future_sells_at()` and `_fertilizer_relay_qty()` to use the same route-index helper.

**Do not tune thresholds until this is fixed and tested.**

That is the highest-value correction supported by the supplied files.
