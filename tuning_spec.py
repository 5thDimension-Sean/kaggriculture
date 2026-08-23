"""tuning_spec.py -- Single source of truth for the CMA-ES search space over
main.py's own knobs (_BASE_PARAMS) and the revived overlays (overlays.py's
DEFAULT_PARAMS).

Each entry is (name, low, high, default, kind) where kind is "float", "int",
or "bool" (bool params are searched as a continuous gate in [0,1] and
thresholded at 0.5 -- this lets CMA-ES smoothly "turn off" an overlay it
doesn't want, matching the sentinel-value pattern already used in this
project's history for disabling a gate).

`x` throughout is a plain list/array of floats in the same order as SPEC,
each already scaled to its own [low, high] range (not a further-normalized
[0,1] cube) -- CMA-ES is given per-dimension initial std proportional to
each range in evolve.py, which handles the scale mismatch directly.

v6: added PARAM_GROUPS (a name -> [param names] mapping used by evolve.py's
optional staged-parameter-activation mode) and KIND_GROUPS (continuous vs.
integer vs. boolean name lists, derived from the existing per-entry `kind`
field -- discreteness was already correctly modeled via `kind` and
vector_to_params()'s int-round/bool-threshold logic; these are just a
convenience view over it for reporting/dry-run, not a behavior change).
Also reparameterized the shed-capacity guard's threshold as
`shed_guard_overflow_buffer` (games-until-the-100-item-cap, 1-30) instead
of the raw `shed_guard_threshold` (70-99) -- purely a search-space
relabeling (buffer = SHED_CAPACITY - threshold, an invertible affine
transform), vector_to_params() still emits `shed_guard_threshold` in
overlay_params so overlays.py itself needs no change.
"""

SHED_CAPACITY = 100  # engine's real shed-item hard cap (kaggle_environments default; see overlays.py's shed_guard docstring)

# Single source of truth for evolve.py's default checkpoint path -- lives
# here (not in evolve.py) so build_agent.py can reference the SAME name
# without importing evolve.py itself (that import triggers evolve.py's
# module-level opponent-pool construction, see remap_checkpoint_vector()'s
# docstring for why build_agent.py deliberately avoids it).
CHECKPOINT_PATH_DEFAULT = "evolve_checkpoint_v6.json"

SPEC = [
    # -- main.py's own knobs --
    ("weed_replay_steps",              2,    16,   8,    "int"),
    ("town_demand_pulse_period",       8,    48,   24,   "int"),
    ("town_demand_check_interval",     1,    12,   4,    "int"),
    ("town_demand_single_shop_bonus",  0.0,  4.0,  2.0,  "float"),
    ("town_demand_multi_shop_bonus",   0.0,  4.0,  1.0,  "float"),

    # -- premium market-lead preemption --
    ("premium_shift_enabled",          0.0,  1.0,  0.0,  "bool"),   # default OFF: unproven on this route
    ("premium_shift_start",            40,   300,  120,  "int"),
    ("premium_shift_stop",             400,  719,  680,  "int"),
    ("premium_shift_fraction",         0.5,  4.0,  2.0,  "float"),
    ("premium_shift_max_batch",        5,    60,   30,   "int"),
    ("premium_shift_min_future_qty",   1,    10,   2,    "int"),
    ("premium_shift_opp_ready_threshold", 1, 12,   4,    "int"),
    ("mirror_max_distance",            5,    50,   20,   "float"),

    # -- fertilizer relay --
    ("fert_relay_enabled",             0.0,  1.0,  0.0,  "bool"),
    ("fert_relay_lead",                1,    10,   3,    "int"),
    ("fert_relay_lead_heavy_animal",   1,    12,   6,    "int"),
    ("fert_relay_start",               150,  400,  278,  "int"),
    ("fert_relay_stop",                500,  719,  662,  "int"),

    # -- price floor guard --
    ("price_floor_enabled",            0.0,  1.0,  0.0,  "bool"),

    # -- sell-slot ranking by price impact --
    ("rank_sell_slots_enabled",        0.0,  1.0,  0.0,  "bool"),
    ("demand_alpha",                   0.0,  1.0,  0.25, "float"),

    # -- opportunistic surplus sell --
    ("opp_sell_enabled",               0.0,  1.0,  0.0,  "bool"),
    ("opp_sell_start",                 10,   200,  50,   "int"),
    ("opp_sell_stop",                  500,  719,  705,  "int"),
    ("opp_sell_batch_cap",             1,    30,   8,    "int"),
    # v5: per-item base/floor reserve fractions (was one shared pair) --
    # inspired by a real public notebook's per-item reserve-fraction sell
    # mechanism (values there ranged 0.40-0.68 across items, not one shared
    # constant).
    ("opp_sell_base_fraction_MILK",       0.1,  0.9,  0.5,  "float"),
    ("opp_sell_base_fraction_WOOL",       0.1,  0.9,  0.5,  "float"),
    ("opp_sell_base_fraction_STRAWBERRY", 0.1,  0.9,  0.5,  "float"),
    ("opp_sell_base_fraction_MELON",      0.1,  0.9,  0.5,  "float"),
    ("opp_sell_floor_fraction_MILK",       0.05, 0.6,  0.15, "float"),
    ("opp_sell_floor_fraction_WOOL",       0.05, 0.6,  0.15, "float"),
    ("opp_sell_floor_fraction_STRAWBERRY", 0.05, 0.6,  0.15, "float"),
    ("opp_sell_floor_fraction_MELON",      0.05, 0.6,  0.15, "float"),
    ("opp_sell_ramp_start",            400,  719,  600,  "int"),
    ("opp_sell_min_supply_fraction",   0.1,  1.0,  0.5,  "float"),

    # -- terminal liquidation --
    ("terminal_soft_start",            650,  719,  706,  "int"),
    ("terminal_hard_start",            660,  719,  708,  "int"),

    # -- v5: shed-capacity overflow guard -- confirmed empirically that our
    #    own route drives shed occupancy to exactly the engine's 100-item
    #    hard cap around steps 432-480, identically across seeds. Inspired
    #    by a real public notebook's proactive room-guard mechanism.
    ("shed_guard_enabled",             0.0,  1.0,  0.0,   "bool"),
    ("shed_guard_start",               300,  719,  300,   "int"),
    ("shed_guard_stop",                300,  719,  719,   "int"),
    # v6: reparameterized from the raw shed_guard_threshold (70-99) to a
    # "how many items of headroom before the 100-item cap" buffer (1-30) --
    # buffer = SHED_CAPACITY - threshold. Same information, more legible
    # search variable; vector_to_params() converts back to
    # overlay_params["shed_guard_threshold"] so overlays.py is unchanged.
    ("shed_guard_overflow_buffer",     1,    30,   10,    "int"),
    ("shed_guard_batch_cap",           1,    30,   20,    "int"),

    # -- front-run item priority (order = argsort, highest weight sells first
    #    when multiple items compete for the 10-order market cap) --
    ("fr_priority_MELON",              0.0, 10.0,  9.0,  "float"),
    ("fr_priority_MILK",               0.0, 10.0,  8.0,  "float"),
    ("fr_priority_STRAWBERRY",         0.0, 10.0,  7.0,  "float"),
    ("fr_priority_WOOL",               0.0, 10.0,  6.0,  "float"),
    ("fr_priority_WHEAT",              0.0, 10.0,  5.0,  "float"),
    ("fr_priority_FERTILIZER",         0.0, 10.0,  4.0,  "float"),
    ("fr_priority_EGG",                0.0, 10.0,  3.0,  "float"),
    ("fr_priority_CARROT",             0.0, 10.0,  2.0,  "float"),
    ("fr_priority_TOMATO",             0.0, 10.0,  1.0,  "float"),

    # -- v4: whether an item gets front-run AT ALL, not just its priority
    #    order -- default ON (1.0) for every item so the default vector still
    #    reproduces the unconditional-front-run behavior every prior version
    #    used. Lets CMA-ES fully exclude an item (e.g. one whose front-run
    #    timing never pays off) instead of only being able to deprioritize it.
    ("fr_enabled_MELON",               0.0,  1.0,  1.0,  "bool"),
    ("fr_enabled_MILK",                0.0,  1.0,  1.0,  "bool"),
    ("fr_enabled_STRAWBERRY",          0.0,  1.0,  1.0,  "bool"),
    ("fr_enabled_WOOL",                0.0,  1.0,  1.0,  "bool"),
    ("fr_enabled_WHEAT",               0.0,  1.0,  1.0,  "bool"),
    ("fr_enabled_FERTILIZER",          0.0,  1.0,  1.0,  "bool"),
    ("fr_enabled_EGG",                 0.0,  1.0,  1.0,  "bool"),
    ("fr_enabled_CARROT",              0.0,  1.0,  1.0,  "bool"),
    ("fr_enabled_TOMATO",              0.0,  1.0,  1.0,  "bool"),
]

NAMES = [s[0] for s in SPEC]
LOWS = [s[1] for s in SPEC]
HIGHS = [s[2] for s in SPEC]
DEFAULTS = [s[3] for s in SPEC]
KINDS = [s[4] for s in SPEC]
DIM = len(SPEC)

_FR_ITEMS_DEFAULT_ORDER = ('MELON', 'MILK', 'STRAWBERRY', 'WOOL', 'WHEAT', 'FERTILIZER', 'EGG', 'CARROT', 'TOMATO')


def clip(x):
    return [max(lo, min(hi, v)) for v, lo, hi in zip(x, LOWS, HIGHS)]


def vector_to_params(x):
    """x: list of DIM floats (already in each param's real range). Returns
    (base_params, overlay_params, fr_items_order) ready for
    main.configure_base / overlays.configure / _FR_ITEMS respectively."""
    x = clip(x)
    d = {}
    for name, value, kind in zip(NAMES, x, KINDS):
        if kind == "int":
            d[name] = int(round(value))
        elif kind == "bool":
            d[name] = 1.0 if value >= 0.5 else 0.0
        else:
            d[name] = float(value)

    base_params = {
        "weed_replay_steps": d["weed_replay_steps"],
        "town_demand_pulse_period": d["town_demand_pulse_period"],
        "town_demand_check_interval": d["town_demand_check_interval"],
        "town_demand_single_shop_bonus": d["town_demand_single_shop_bonus"],
        "town_demand_multi_shop_bonus": d["town_demand_multi_shop_bonus"],
    }
    overlay_params = {k: v for k, v in d.items()
                       if k not in base_params
                       and not k.startswith("fr_priority_")
                       and not k.startswith("fr_enabled_")
                       and k != "shed_guard_overflow_buffer"}
    overlay_params["shed_guard_threshold"] = SHED_CAPACITY - d["shed_guard_overflow_buffer"]
    priorities = {item: d[f"fr_priority_{item}"] for item in _FR_ITEMS_DEFAULT_ORDER}
    enabled = {item: d[f"fr_enabled_{item}"] >= 0.5 for item in _FR_ITEMS_DEFAULT_ORDER}
    fr_items_order = tuple(
        item for item in sorted(priorities, key=lambda item: -priorities[item])
        if enabled[item]
    )
    return base_params, overlay_params, fr_items_order


def default_vector():
    return list(DEFAULTS)


def remap_checkpoint_vector(old_names, old_values, warn=True):
    """Rebuild a full-length, CURRENT-NAMES-ordered params vector from an
    older checkpoint's (param_names, best_params) pair. Needed because NAMES
    can change shape/order/meaning across versions (v6 renamed
    shed_guard_threshold -> shed_guard_overflow_buffer; v4 added
    fr_enabled_* gates; v5 split opp_sell_*_fraction into per-item names) --
    blindly reusing an old vector POSITIONALLY would silently misinterpret
    values under the new semantics. Matching names carry over directly; the
    one known rename is inverse-transformed explicitly; anything else
    missing falls back to the current default -- which can silently produce
    a candidate that's part old-checkpoint, part current-defaults, so by
    default (`warn=True`) this prints a one-line summary whenever that
    happens rather than doing it invisibly. Lives here (not in evolve.py)
    so build_agent.py -- which only needs to materialize a candidate file --
    doesn't have to import the optimizer module to do it (that import used
    to trigger evolve.py's module-level opponent-pool construction as a
    side effect of just building a submission file).

    Returns (vector, report): report is {'preserved', 'renamed', 'defaulted'}
    -- each a list of names -- for a caller that wants to inspect or print
    it in more detail than the default one-line warning."""
    old = dict(zip(old_names, old_values))
    defaults = default_vector()
    out = []
    preserved, renamed, defaulted = [], [], []
    for name, default in zip(NAMES, defaults):
        if name in old:
            out.append(old[name])
            preserved.append(name)
        elif name == "shed_guard_overflow_buffer" and "shed_guard_threshold" in old:
            out.append(SHED_CAPACITY - old["shed_guard_threshold"])
            renamed.append(name)
        else:
            out.append(default)
            defaulted.append(name)
    report = {"preserved": preserved, "renamed": renamed, "defaulted": defaulted}
    if warn and (renamed or defaulted):
        print(f"REMAPPING CHECKPOINT: preserved={len(preserved)} renamed={len(renamed)} "
              f"defaulted={len(defaulted)}")
        if renamed:
            print(f"  renamed (value transformed, not copied positionally): {renamed}")
        if defaulted:
            print(f"  WARNING: {len(defaulted)} current parameter(s) absent from the checkpoint "
                  f"-- falling back to current defaults: {defaulted}")
    return out, report


def initial_std():
    """Per-dimension initial CMA-ES step size: 25% of each param's range."""
    return [0.25 * (hi - lo) for lo, hi in zip(LOWS, HIGHS)]


# ===========================================================================
# v6: parameter groups (evolve.py's optional staged-activation mode) and
# kind groups (continuous/integer/boolean views over the existing per-entry
# `kind` field, for dry-run reporting). Built from the ACTUAL names in SPEC
# above -- never hand-duplicated -- so they can't silently drift out of sync
# with it.
# ===========================================================================

PARAM_GROUPS = {
    "core_strategy": [
        "weed_replay_steps", "town_demand_pulse_period", "town_demand_check_interval",
        "town_demand_single_shop_bonus", "town_demand_multi_shop_bonus",
    ],
    "premium_shift": [
        "premium_shift_enabled", "premium_shift_start", "premium_shift_stop",
        "premium_shift_fraction", "premium_shift_max_batch", "premium_shift_min_future_qty",
        "premium_shift_opp_ready_threshold", "mirror_max_distance",
    ],
    "fert_relay": [
        "fert_relay_enabled", "fert_relay_lead", "fert_relay_lead_heavy_animal",
        "fert_relay_start", "fert_relay_stop",
    ],
    "price_floor": ["price_floor_enabled"],
    "rank_sell_slots": ["rank_sell_slots_enabled", "demand_alpha"],
    "item_reserves": [
        "opp_sell_enabled", "opp_sell_start", "opp_sell_stop", "opp_sell_batch_cap",
        "opp_sell_base_fraction_MILK", "opp_sell_base_fraction_WOOL",
        "opp_sell_base_fraction_STRAWBERRY", "opp_sell_base_fraction_MELON",
        "opp_sell_floor_fraction_MILK", "opp_sell_floor_fraction_WOOL",
        "opp_sell_floor_fraction_STRAWBERRY", "opp_sell_floor_fraction_MELON",
        "opp_sell_ramp_start", "opp_sell_min_supply_fraction",
    ],
    "terminal_liquidation": ["terminal_soft_start", "terminal_hard_start"],
    "shed_overflow": [
        "shed_guard_enabled", "shed_guard_start", "shed_guard_stop",
        "shed_guard_overflow_buffer", "shed_guard_batch_cap",
    ],
    "front_run_priority": [f"fr_priority_{item}" for item in _FR_ITEMS_DEFAULT_ORDER],
    "front_run_gates": [f"fr_enabled_{item}" for item in _FR_ITEMS_DEFAULT_ORDER],
}

# Sanity: every name in SPEC must be in exactly one group, and vice versa --
# a hard AssertionError here (not a silent drift) if a future SPEC edit adds
# a name and forgets to group it.
_grouped = [n for names in PARAM_GROUPS.values() for n in names]
assert sorted(_grouped) == sorted(NAMES), (
    "PARAM_GROUPS is out of sync with SPEC -- "
    f"in SPEC but ungrouped: {sorted(set(NAMES) - set(_grouped))}, "
    f"grouped but not in SPEC: {sorted(set(_grouped) - set(NAMES))}"
)
assert len(_grouped) == len(set(_grouped)), "PARAM_GROUPS has a name listed in more than one group"

KIND_GROUPS = {
    "continuous": [n for n, k in zip(NAMES, KINDS) if k == "float"],
    "integer": [n for n, k in zip(NAMES, KINDS) if k == "int"],
    "boolean": [n for n, k in zip(NAMES, KINDS) if k == "bool"],
}
