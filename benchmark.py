"""
benchmark.py — Head-to-head benchmarker for Kaggriculture agents.

Usage:
    python benchmark.py                              # main.py vs models/5_0.py
    python benchmark.py --a main.py --b models/5_0.py
    python benchmark.py --a main.py --b route-only  # vs bare route (no market logic)
    python benchmark.py --b "replay:training data v3/91385999.json:0"  # vs a real
                                                      # recorded episode's exact actions
    python benchmark.py --n 40                       # run 40 games

Each run plays N//2 games with agent A as P0, N//2 games with agent A as P1.

Passing --b route-only generates a stripped version of agent A that skips all
market-intelligence overlays and executes the raw route actions literally.
This lets you measure how much the market logic contributes.

Passing --b "replay:<path>:<player_index>" builds an agent that blindly
replays a REAL recorded episode's exact actions for that player (0 or 1) —
e.g. one of the THUNDER THUNDER games in training data v3/. This is a much
more meaningful opponent than self-play or another one of our own overlay-
laden models: the replayed side is non-reactive (it won't adapt to what
agent A does), but the actual market/prices/town state IS computed live and
correctly by the real engine from both sides' real actions. Self-play can't
tell you whether your own overlays are actually paying off against a
genuinely different opponent — this can. (Caveat discovered the hard way:
main.py's own two route backbones are NOT equally strong — episode 91471546
[P1 backbone] reliably beats episode 91385999 [P0 backbone] head-to-head
with zero overlays on either side. Don't mistake that source-route gap for
an overlay effect when comparing two different replay files.)

IMPORTANT: always confirm kaggle_environments matches the real competition
version before trusting these numbers (see sanity_check's version warning).
A local install can silently diverge from production — this project's
own dev environment was 3 minor versions behind and scored premium goods
2-3x too generously as a result before that was caught.

Seeds are fixed so the same matchup always produces the same numbers.
"""

import argparse
import json
import os
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_KNOWN_GOOD_VERSION = "1.32.7"  # confirmed live 2026-08-22 via a fresh episode's module_version field


def load_agent(path):
    """Load an agent function from a .py file."""
    path = os.path.abspath(path)
    ns = {"__file__": path}
    with open(path) as f:
        exec(compile(f.read(), path, "exec"), ns)
    if "agent" not in ns:
        raise ValueError(f"No 'agent' function found in {path}")
    return ns["agent"]


def make_route_only_agent(path):
    """Return an agent that executes the raw route with NO market overlays.

    Used as a baseline to measure how much market intelligence contributes.
    The agent still calls _align_hands and _weed_repair_action (safety only),
    but skips all sell-reordering, premium-shift, price-gate, etc.
    """
    path = os.path.abspath(path)
    ns = {"__file__": path}
    with open(path) as f:
        exec(compile(f.read(), path, "exec"), ns)

    _ACTIONS       = ns["_ACTIONS"]
    _align_hands   = ns["_align_hands"]
    _copy_action   = ns["_copy_action"]
    _weed_repair   = ns.get("_weed_repair_action")

    def route_only_agent(obs):
        try:
            step = min(max(0, int((obs.get("step") or 0))), len(_ACTIONS) - 1)
            action = _copy_action(_ACTIONS[step])
            if _weed_repair is not None:
                action = _weed_repair(obs, action, _ACTIONS, step)
            return _align_hands(action, obs)
        except Exception:
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return route_only_agent


def make_replay_agent(episode_path, player_index):
    """Return an agent that blindly replays a real episode's exact recorded
    actions for one player. Non-reactive (ignores the live observation
    entirely, aside from reading the current step) but mechanically valid —
    the underlying market/town state still evolves correctly in response to
    whatever the OTHER, live agent does, since the real engine processes it.
    Falls back to PASS if the episode runs out of recorded steps.
    """
    with open(episode_path) as f:
        data = json.load(f)
    steps = data["steps"]
    actions = []
    for step in steps:
        if player_index < len(step):
            action = step[player_index].get("action") or {}
            actions.append({
                "farmer": action.get("farmer", ["PASS"]),
                "hands": action.get("hands", []),
                "market": action.get("market", []),
            })
    # Recorded episodes include a leading bootstrap entry (step 0's action is
    # always an empty PASS — it's recorded before that player ever makes a
    # real decision), so actions[0] as-loaded is one step stale relative to
    # obs["step"]. Strip it so actions[step] lines up with the step at which
    # it was ACTUALLY submitted (matches the convention main.py's own
    # extracted _ACTIONS_P0/_ACTIONS_P1 already use — see extract_routes.py).
    while actions and actions[0]["farmer"] == ["PASS"] and not actions[0]["hands"] and not actions[0]["market"]:
        actions = actions[1:]

    def replay_agent(obs, configuration=None):
        step = int(obs.get("step", 0) or 0)
        if step < len(actions):
            return actions[step]
        return {"farmer": ["PASS"], "hands": [], "market": []}

    return replay_agent


def run_game(agent_a, agent_b, seed):
    from kaggle_environments import make
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed},
        debug=False,
    )
    env.run([agent_a, agent_b])
    final = env.steps[-1]
    return float(final[0].reward or 0), float(final[1].reward or 0)


_SEEDS_P0 = [
    7030039913, 1767950141, 2067004398, 4263648760, 3313394522,
    3101419947, 3930751749, 5948990031, 3837117532, 2455163851,
]
_SEEDS_P1 = [
    4326338643, 7309474672, 2729251472, 5327694078, 6170128796,
    3294844113, 4866511089, 7895609197, 5194945606, 2535557871,
]


def benchmark(agent_a, agent_b, name_a, name_b, n_games=20):
    half     = n_games // 2
    seeds_p0 = _SEEDS_P0[:half]
    seeds_p1 = _SEEDS_P1[:half]

    wins_a = wins_b = ties = 0
    scores_a = []
    scores_b = []

    print(f"\n{'─'*62}")
    print(f"  {name_a:25s}  vs  {name_b}")
    print(f"{'─'*62}")

    print(f"\n  [{name_a} as P0]")
    for i, seed in enumerate(seeds_p0):
        sa, sb = run_game(agent_a, agent_b, seed)
        scores_a.append(sa); scores_b.append(sb)
        if   sa > sb: wins_a += 1; tag = f"{name_a} WIN"
        elif sb > sa: wins_b += 1; tag = f"{name_b} WIN"
        else:         ties   += 1; tag = "TIE"
        print(f"    game {i+1:2d} (seed={seed}): "
              f"{name_a}={sa:>8,.0f}  {name_b}={sb:>8,.0f}  → {tag}")

    print(f"\n  [{name_a} as P1]")
    for i, seed in enumerate(seeds_p1):
        sb, sa = run_game(agent_b, agent_a, seed)
        scores_a.append(sa); scores_b.append(sb)
        if   sa > sb: wins_a += 1; tag = f"{name_a} WIN"
        elif sb > sa: wins_b += 1; tag = f"{name_b} WIN"
        else:         ties   += 1; tag = "TIE"
        print(f"    game {i+1:2d} (seed={seed}): "
              f"{name_a}={sa:>8,.0f}  {name_b}={sb:>8,.0f}  → {tag}")

    total  = wins_a + wins_b + ties
    mean_a = sum(scores_a) / len(scores_a)
    mean_b = sum(scores_b) / len(scores_b)
    delta  = mean_a - mean_b

    print(f"\n{'═'*62}")
    print(f"  RESULTS ({total} games)")
    print(f"  {name_a:25s}  wins: {wins_a}/{total}  mean: {mean_a:>8,.0f}")
    print(f"  {name_b:25s}  wins: {wins_b}/{total}  mean: {mean_b:>8,.0f}")
    print(f"  delta (A - B):               {delta:>+9,.0f} per game")
    print(f"{'═'*62}\n")

    return wins_a, wins_b, ties, mean_a, mean_b


def sanity_check(agent, name):
    """Print first 3 actions and env version."""
    from kaggle_environments import make
    import kaggle_environments
    print(f"\n[sanity] kaggle_environments version: {kaggle_environments.__version__}")
    if kaggle_environments.__version__ != _KNOWN_GOOD_VERSION:
        print(
            f"[sanity] WARNING: installed version does not match the last known "
            f"real-competition version ({_KNOWN_GOOD_VERSION}). Market dynamics "
            f"(especially premium-item glut behavior) can differ significantly "
            f"between versions — do not trust these numbers as production-accurate "
            f"until you've confirmed which version the competition is actually running."
        )

    globs = getattr(agent, "__globals__", {})
    net = globs.get("_NET")
    if net is not None:
        import numpy as np
        print(f"[sanity] _NET W1 norm: {float(__import__('numpy').linalg.norm(net.W1)):.2f}")
    else:
        print("[sanity] (no _NET — route-replay agent)")

    env = make("kaggriculture", configuration={"episodeSteps": 4}, debug=False)
    results = []

    def spy(obs):
        action = agent(obs)
        results.append(action)
        return action

    env.run([spy, "random"])
    print(f"\n[sanity] {name} first {len(results)} actions (as P0):")
    for i, a in enumerate(results):
        print(f"  step {i}: farmer={a.get('farmer')}  market={a.get('market', [])[:2]}")
    print()


def resolve_agent(spec, project_root, route_only_source):
    """Resolve a --a/--b spec into (agent, name).

    Supported forms:
      <path.py>                        — load agent() from a file
      route-only                       — bare route from route_only_source, no overlays
      replay:<episode.json>:<player>   — blind replay of a real episode's actions
    """
    if spec == "route-only":
        return make_route_only_agent(route_only_source), "route-only"
    if spec.startswith("replay:"):
        _, episode_path, player_str = spec.split(":", 2)
        player = int(player_str)
        episode_path = episode_path if os.path.isabs(episode_path) else os.path.join(project_root, episode_path)
        name = f"replay:{os.path.basename(episode_path)}:p{player}"
        return make_replay_agent(episode_path, player), name
    path = spec if os.path.isabs(spec) else os.path.join(project_root, spec)
    return load_agent(path), os.path.splitext(os.path.basename(path))[0]


def main():
    ap = argparse.ArgumentParser(
        description="Kaggriculture head-to-head benchmarker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python benchmark.py                              # main.py vs models/5_0.py
              python benchmark.py --b route-only              # vs bare route (measures market logic)
              python benchmark.py --a models/5_1.py --b models/5_0.py
              python benchmark.py --b "replay:training data v3/91385999.json:0"
                                                                # vs a real recorded episode
              python benchmark.py --n 40
        """),
    )
    ap.add_argument("--a", default="main.py",         help="Agent A: path, 'route-only', or 'replay:<json>:<player>' (default: main.py)")
    ap.add_argument("--b", default="models/5_0.py",   help="Agent B: path, 'route-only', or 'replay:<json>:<player>' (default: models/5_0.py)")
    ap.add_argument("--n", type=int, default=20,       help="Total games, must be even (default: 20)")
    args = ap.parse_args()

    if args.n % 2 != 0:
        sys.exit("--n must be even")

    project_root = os.path.dirname(os.path.abspath(__file__))
    route_only_source = args.a if os.path.isabs(args.a) else os.path.join(project_root, args.a)

    print(f"Loading agents...")
    agent_a, name_a = resolve_agent(args.a, project_root, route_only_source)
    print(f"  A: {name_a}")
    agent_b, name_b = resolve_agent(args.b, project_root, route_only_source)
    print(f"  B: {name_b}")

    sanity_check(agent_b, name_b)
    benchmark(agent_a, agent_b, name_a, name_b, n_games=args.n)


if __name__ == "__main__":
    main()
