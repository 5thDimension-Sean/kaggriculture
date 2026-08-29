"""Small, intentional CMA-ES search space for MapleLeaf 7.2.

The production policy is heuristic-first. CMA-ES only adjusts thresholds
whose effects are monotonic and understandable; it does not select routes,
invent new actions, or toggle a large library of speculative overlays.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Parameter:
    name: str
    low: float
    high: float
    default: float
    kind: str = "float"


# Full promoted configuration. Values outside PARAMETERS stay fixed while the
# compact search runs, so a default vector reproduces main.py exactly.
BASE_DEFAULTS = {
    "weed_replay_steps": 11,
    "town_demand_pulse_period": 10,
    "town_demand_check_interval": 7,
    "town_demand_single_shop_bonus": 0.0006157003847131392,
    "town_demand_multi_shop_bonus": 0.42366855104471457,
    "front_run_lead": 4,
    "front_run_start": 48,
    "front_run_stop": 669,
    "front_run_max_batch": 20,
}

HEURISTIC_DEFAULTS = {
    "premium_shift_enabled": 1.0,
    "premium_shift_start": 287,
    "premium_shift_stop": 682,
    "premium_shift_fraction": 2.507174265974758,
    "premium_shift_max_batch": 5,
    "premium_shift_min_future_qty": 3,
    "premium_shift_opp_ready_threshold": 4,
    "mirror_max_distance": 34.86886877003725,
    "fert_relay_enabled": 0.0,
    "fert_relay_lead": 3,
    "fert_relay_lead_heavy_animal": 5,
    "fert_relay_start": 353,
    "fert_relay_stop": 610,
    "price_floor_enabled": 0.0,
    "rank_sell_slots_enabled": 1.0,
    "demand_alpha": 0.21164025445907636,
    "opp_sell_enabled": 1.0,
    "opp_sell_start": 45,
    "opp_sell_stop": 704,
    "opp_sell_batch_cap": 5,
    "opp_sell_base_fraction_MILK": 0.12226358671010273,
    "opp_sell_base_fraction_WOOL": 0.19196433115965672,
    "opp_sell_base_fraction_STRAWBERRY": 0.26729391318181406,
    "opp_sell_base_fraction_MELON": 0.5838257424438272,
    "opp_sell_floor_fraction_MILK": 0.46780182162339207,
    "opp_sell_floor_fraction_WOOL": 0.11239281181508977,
    "opp_sell_floor_fraction_STRAWBERRY": 0.07987627492305109,
    "opp_sell_floor_fraction_MELON": 0.41240677828767486,
    "opp_sell_ramp_start": 697,
    "opp_sell_min_supply_fraction": 0.10081480241978077,
    "terminal_soft_start": 708,
    "terminal_hard_start": 708,
    "shed_guard_enabled": 0.0,
    "shed_guard_start": 420,
    "shed_guard_stop": 487,
    "shed_guard_batch_cap": 19,
    "shed_guard_threshold": 94,
}


PARAMETERS = (
    Parameter("weed_replay_steps", 6, 14, 11, "int"),
    Parameter("front_run_lead", 1, 5, 4, "int"),
    Parameter("front_run_start", 0, 540, 48, "int"),
    Parameter("front_run_stop", 540, 718, 669, "int"),
    Parameter("front_run_max_batch", 1, 30, 20, "int"),
    Parameter("premium_shift_start", 220, 340, 287, "int"),
    Parameter("premium_shift_stop", 630, 710, 682, "int"),
    Parameter("premium_shift_fraction", 1.25, 3.50, 2.507174265974758),
    Parameter("premium_shift_max_batch", 3, 12, 5, "int"),
    Parameter("premium_shift_min_future_qty", 1, 6, 3, "int"),
    Parameter("premium_shift_opp_ready_threshold", 2, 8, 4, "int"),
    Parameter("mirror_max_distance", 15, 55, 34.86886877003725),
    Parameter("demand_alpha", 0.0, 0.50, 0.21164025445907636),
    Parameter("opp_sell_batch_cap", 2, 12, 5, "int"),
    Parameter("terminal_soft_start", 696, 714, 708, "int"),
    Parameter("terminal_hard_start", 700, 718, 708, "int"),
)

NAMES = tuple(parameter.name for parameter in PARAMETERS)
LOWS = tuple(parameter.low for parameter in PARAMETERS)
HIGHS = tuple(parameter.high for parameter in PARAMETERS)
DEFAULTS = tuple(parameter.default for parameter in PARAMETERS)
DIM = len(PARAMETERS)


def clip_real(vector):
    if len(vector) != DIM:
        raise ValueError(f"expected {DIM} parameters, got {len(vector)}")
    return [max(parameter.low, min(parameter.high, float(value)))
            for parameter, value in zip(PARAMETERS, vector)]


def to_normalized(real_vector):
    return [(value - parameter.low) / (parameter.high - parameter.low)
            for parameter, value in zip(PARAMETERS, clip_real(real_vector))]


def from_normalized(normalized_vector):
    if len(normalized_vector) != DIM:
        raise ValueError(f"expected {DIM} normalized parameters, got {len(normalized_vector)}")
    real = [parameter.low + max(0.0, min(1.0, float(value))) * (parameter.high - parameter.low)
            for parameter, value in zip(PARAMETERS, normalized_vector)]
    return clip_real(real)


def default_vector():
    return list(DEFAULTS)


def vector_to_config(real_vector):
    values = {}
    for parameter, raw_value in zip(PARAMETERS, clip_real(real_vector)):
        if parameter.kind == "int":
            values[parameter.name] = int(round(raw_value))
        else:
            values[parameter.name] = float(raw_value)

    base = dict(BASE_DEFAULTS)
    heuristics = dict(HEURISTIC_DEFAULTS)
    for name, value in values.items():
        target = base if name in base else heuristics
        target[name] = value

    # Preserve the intended phase ordering even when CMA samples crossed
    # integer boundaries near the search-space edges.
    heuristics["premium_shift_stop"] = max(
        heuristics["premium_shift_start"] + 24,
        heuristics["premium_shift_stop"],
    )
    heuristics["terminal_hard_start"] = max(
        heuristics["terminal_soft_start"],
        heuristics["terminal_hard_start"],
    )
    return base, heuristics


def describe():
    return [
        {
            "name": parameter.name,
            "low": parameter.low,
            "high": parameter.high,
            "default": parameter.default,
            "kind": parameter.kind,
        }
        for parameter in PARAMETERS
    ]
