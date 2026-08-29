"""Build a standalone 7.2 candidate with an opening-classified anti-player route."""

import argparse
import base64
import json
import os
import zlib

from tools import build_submission
from tuning import space


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_actions(path):
    namespace = {"__file__": os.path.abspath(path)}
    with open(path, encoding="utf-8") as handle:
        exec(compile(handle.read(), path, "exec"), namespace)
    return namespace["_ACTIONS"]


def _encoded_actions(actions):
    payload = json.dumps(actions, separators=(",", ":")).encode("utf-8")
    return base64.b85encode(zlib.compress(payload, 9)).decode("ascii")


def build_source(
    main_path,
    anti_route_path,
    checkpoint_path=None,
    opening_variant="exact",
    front_run_lead=None,
    extra_hand="pass",
):
    source = build_submission.build_merged_source(PROJECT_ROOT, main_path=main_path)
    if checkpoint_path:
        with open(checkpoint_path, encoding="utf-8") as handle:
            checkpoint = json.load(handle)
        if tuple(checkpoint.get("param_names", ())) != space.NAMES:
            raise ValueError("checkpoint parameter names do not match the 7.2 tuning space")
        base_config, heuristic_config = space.vector_to_config(checkpoint["best_params"])
        if front_run_lead is not None:
            base_config["front_run_lead"] = int(front_run_lead)
        source += (
            "\n# Frozen compact CMA-ES configuration.\n"
            f"configure_base({base_config!r})\n"
            f"heuristics.configure({heuristic_config!r})\n"
        )
    encoded = _encoded_actions(_load_actions(anti_route_path))
    if opening_variant not in {"exact", "five_hands"}:
        raise ValueError(f"unsupported opening variant: {opening_variant}")
    if extra_hand not in {"pass", "general"}:
        raise ValueError(f"unsupported extra-hand policy: {extra_hand}")
    opening_patch = ""
    if opening_variant == "five_hands":
        opening_patch = '''
        if step == 0:
            action = _copy_action(action)
            action["market"] = [
                ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
                ["BUY_ANIMAL", "COW", 2],
                ["BUY_ANIMAL", "SHEEP", 2],
                ["BUY_SEED", "MELON", 5],
                ["BUY_SEED", "WHEAT", 9],
            ]
        elif step == 1 and mode == "general":
            action = _copy_action(action)
            action["market"] = [
                ["BUY_SEED", "MELON", 7],
                ["BUY_PRODUCT", "WHEAT", 6],
            ]
'''
    extra_hand_patch = ""
    if extra_hand == "general":
        extra_hand_patch = '''
        if step >= 1 and mode == "anti":
            action = _copy_action(action)
            general_hands = list(_GENERAL_ACTIONS[step].get("hands") or [])
            hands = list(action.get("hands") or [])
            if len(general_hands) >= 5 and len(hands) >= 5:
                hands[4] = list(general_hands[4])
                action["hands"] = hands
'''
    adaptive = f'''\n
# Opponent-adaptive 7.2 route selector. Crop Dusta's public replay policy hires
# four hands in its opening; Mapleleaf 7.1 hires five. We retain the general
# opening until that public board-state distinction is observable at step 1.
_GENERAL_ACTIONS = _ACTIONS
_ANTI_ACTIONS = json.loads(zlib.decompress(base64.b85decode({encoded!r})).decode("utf-8"))
_ROUTE_MODE_STATE = {{0: {{"last_step": -1, "mode": None}}, 1: {{"last_step": -1, "mode": None}}}}


def _route_mode(obs, step):
    seat = _seat(obs)
    state = _ROUTE_MODE_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state["mode"] = None
    state["last_step"] = step
    if step >= 1 and state.get("mode") is None:
        farms = list(_get(obs, "farms", []) or [])
        opponent = farms[1 - seat] if len(farms) > 1 else {{}}
        opponent_hands = list(_get(opponent, "hands", []) or [])
        state["mode"] = "anti" if len(opponent_hands) <= 4 else "general"
    return state.get("mode")


def _run_action_tape(obs, tape):
    global _ACTIONS
    previous_tape = _ACTIONS
    _ACTIONS = tape
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(tape) - 1)
        action = _weed_repair_action(obs, _copy_action(tape[step]), step)
        state = _fr_state(obs, step)
        action = _repay(action, state, step)
        action = heuristics.repay_premium_shift(obs, action, step)
        action = heuristics.repay_fertilizer_relay(obs, action, step)
        action = _front_run(action, obs, state, step)
        heuristics._detect_opponent_type(obs, step)
        action = heuristics.price_floor_guard(obs, action, step)
        action = heuristics.rank_sell_slots(obs, action)
        action = heuristics.premium_shift(obs, action, step, tape)
        action = heuristics.fertilizer_relay(obs, action, step, tape)
        action = heuristics.opportunistic_sell(obs, action, step)
        action = heuristics.shed_guard(obs, action, step)
        action = heuristics.terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    finally:
        _ACTIONS = previous_tape


def agent(obs):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_GENERAL_ACTIONS) - 1)
        mode = _route_mode(obs, step)
        tape = _ANTI_ACTIONS if step == 0 or mode == "anti" else _GENERAL_ACTIONS
        action = _run_action_tape(obs, tape)
{opening_patch}{extra_hand_patch}        return action
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {{
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }}
'''
    return source + adaptive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", default=os.path.join(PROJECT_ROOT, "main.py"))
    parser.add_argument("--checkpoint")
    parser.add_argument("--opening", choices=("exact", "five_hands"), default="exact")
    parser.add_argument("--front-run-lead", type=int, choices=range(1, 6))
    parser.add_argument("--extra-hand", choices=("pass", "general"), default="pass")
    parser.add_argument("--anti-route", required=True)
    parser.add_argument("--out", default=os.path.join(PROJECT_ROOT, "artifacts", "candidate", "mapleleaf-7.2-adaptive.py"))
    args = parser.parse_args()

    output_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    source = build_source(
        args.main,
        args.anti_route,
        args.checkpoint,
        args.opening,
        args.front_run_lead,
        args.extra_hand,
    )
    compile(source, output_path, "exec")
    with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(source)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
