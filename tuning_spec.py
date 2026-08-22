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
"""

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
    ("opp_sell_base_fraction",         0.1,  0.9,  0.5,  "float"),
    ("opp_sell_floor_fraction",        0.05, 0.6,  0.15, "float"),
    ("opp_sell_ramp_start",            400,  719,  600,  "int"),
    ("opp_sell_min_supply_fraction",   0.1,  1.0,  0.5,  "float"),

    # -- terminal liquidation --
    ("terminal_soft_start",            650,  719,  706,  "int"),
    ("terminal_hard_start",            660,  719,  708,  "int"),

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
                       if k not in base_params and not k.startswith("fr_priority_")}
    priorities = {item: d[f"fr_priority_{item}"] for item in _FR_ITEMS_DEFAULT_ORDER}
    fr_items_order = tuple(sorted(priorities, key=lambda item: -priorities[item]))
    return base_params, overlay_params, fr_items_order


def default_vector():
    return list(DEFAULTS)


def initial_std():
    """Per-dimension initial CMA-ES step size: 25% of each param's range."""
    return [0.25 * (hi - lo) for lo, hi in zip(LOWS, HIGHS)]
