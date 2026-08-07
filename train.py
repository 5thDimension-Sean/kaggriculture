"""
GPU-accelerated RL training for Kaggriculture.

Algorithm : PPO (Proximal Policy Optimization) via stable-baselines3
Hardware  : CUDA GPU (falls back to CPU if unavailable)
Opponent  : "random" during training; self-play can be added later

Install deps:
    pip install torch stable-baselines3 kaggle-environments

Run:
    python train.py                      # 2M steps (~30 min on GPU)
    python train.py --steps 5000000      # more training
    python train.py --resume             # continue from weights.npz
"""

import argparse
import os
import sys
import math
import numpy as np

# ── Model constants shared with main.py ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from model import OBS_DIM, N_ACTIONS, ACTIONS, encode_obs, BOARD_SIZE, SHED_ADJ, BASE_PRICES

# ── Lazy imports (only needed for training) ───────────────────────────────────

def _require(pkg):
    try:
        return __import__(pkg)
    except ImportError:
        sys.exit(f"Missing package: {pkg}\n  pip install {pkg}")


# ─────────────────────────────────────────────────────────────────────────────
# MARKET RULE MODULE  (used both in gym wrapper and in main.py)
# ─────────────────────────────────────────────────────────────────────────────

MARKET_PARAMS = {
    "WHEAT":      {"base": 25,  "I0": 10000, "T": 400,  "bf": "sqrt",   "bt": 0.80, "af": "log",    "at": 0.20},
    "CARROT":     {"base": 35,  "I0": 10000, "T": 450,  "bf": "log",    "bt": 0.20, "af": "sqrt",   "at": 0.70},
    "TOMATO":     {"base": 60,  "I0": 10000, "T": 200,  "bf": "linear", "bt": 0.40, "af": "sqrt",   "at": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100,  "bf": "sqrt",   "bt": 0.70, "af": "linear", "at": 1.60},
    "MELON":      {"base": 250, "I0": 10000, "T": 300,  "bf": "log",    "bt": 0.20, "af": "sq",     "at": 3.60},
    "EGG":        {"base": 50,  "I0": 10000, "T": 332,  "bf": "linear", "bt": 0.40, "af": "log",    "at": 0.20},
    "MILK":       {"base": 160, "I0": 10000, "T": 122,  "bf": "sqrt",   "bt": 0.60, "af": "linear", "at": 1.60},
    "WOOL":       {"base": 200, "I0": 10000, "T": 105,  "bf": "log",    "bt": 0.20, "af": "sq",     "at": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200,  "bf": "linear", "bt": 0.40, "af": "linear", "at": 0.40},
}


def _shape_f(name, x):
    x = float(x)
    if name == "linear": return x
    if name == "sq":     return x * x
    if name == "sqrt":   return math.sqrt(max(0.0, x))
    if name == "log":    return math.log(1.0 + x)
    if name == "log10":  return math.log10(1.0 + x) if x > 0 else 0.0
    return x


def market_sell_qty(product, market_inv, available, min_ratio=0.75):
    """Find sell quantity that maximises revenue given the price curve."""
    p = MARKET_PARAMS.get(product)
    if not p or available <= 0:
        return 0
    base = p["base"]
    min_price = max(1, base * min_ratio)
    best_rev = best_qty = 0
    total = 0.0
    inv = market_inv
    for qty in range(1, available + 1):
        delta = inv - p["I0"]
        if delta <= 0:
            denom = _shape_f(p["bf"], p["T"])
            amp = p["bt"] * base / denom if denom else 0
            price = base + amp * _shape_f(p["bf"], abs(delta))
        else:
            denom = _shape_f(p["af"], p["T"])
            amp = p["at"] * base / denom if denom else 0
            price = base - amp * _shape_f(p["af"], delta)
        price = max(1, round(price))
        if price < min_price:
            break
        total += price
        inv += 1
        if total > best_rev:
            best_rev = total
            best_qty = qty
    return best_qty if best_qty else min(2, available)


def market_orders(obs):
    """
    Rule-based market orders: sell harvested goods, buy wheat for feed,
    buy seeds, hire one farmhand, buy land when profitable.
    Returns list of market order lists.
    """
    player = obs["player"]
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    me = obs["farms"][player]
    private = obs.get("private", {})
    mkt = obs.get("market", {"prices": {}, "inventory": {}})
    money = float(me.get("money", 0))
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    prices = mkt.get("prices", {})
    inv_mkt = mkt.get("inventory", {})
    tiles = me.get("tiles", [])

    orders = []

    # Count animals for feed planning
    num_animals = sum(
        1 for row in tiles for t in row
        if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and t.get("animal")
    )

    # ── Sell all non-wheat products ──
    for item in ["EGG", "MILK", "WOOL", "MELON", "STRAWBERRY", "TOMATO", "CARROT"]:
        qty = shed.get(item, 0)
        if qty > 0:
            inv = inv_mkt.get(item, 10000)
            sell_qty = market_sell_qty(item, inv, qty, min_ratio=0.70)
            if sell_qty > 0:
                orders.append(["SELL", item, sell_qty])

    # ── Sell wheat above buffer ──
    wheat_buffer = max(num_animals * 4, 8)  # keep enough for animal feed
    wheat_qty = shed.get("WHEAT", 0)
    surplus = wheat_qty - wheat_buffer
    if surplus > 0:
        inv = inv_mkt.get("WHEAT", 10000)
        sell_qty = market_sell_qty("WHEAT", inv, surplus, min_ratio=0.80)
        if sell_qty > 0:
            orders.append(["SELL", "WHEAT", sell_qty])

    # ── Buy wheat if animals need feed ──
    if num_animals > 0 and wheat_qty < num_animals * 2:
        need = num_animals * 3 - wheat_qty
        wheat_price = prices.get("WHEAT", 25)
        cost = need * wheat_price
        if money > cost + 200:
            orders.append(["BUY_PRODUCT", "WHEAT", need])
            money -= cost

    # ── Buy wheat seeds (only what we can plant in ~2 days) ──
    num_workers = 1 + len(me.get("hands", []))
    n_empty = sum(1 for row in tiles for t in row if t is None)
    wheat_seeds = seeds.get("WHEAT", 0)
    # Each worker can plant ~10 per day; buy enough for 2 days minus what we have
    seed_want = min(n_empty, num_workers * 8) - wheat_seeds
    if seed_want > 0 and money > seed_want * 10 + 300:
        orders.append(["BUY_SEED", "WHEAT", seed_want])
        money -= seed_want * 10

    # ── Hire 1 farm hand at hour 0 (costs $1, enormous ROI) ──
    hires = me.get("hires_today", 0)
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34]
    hire_cost = fib[hires] if hires < len(fib) else 9999
    if hour == 0 and hires < 2 and money >= hire_cost + 100:
        orders.append(["HIRE"])
        money -= hire_cost

    # ── Buy land: only after day 8, profitable revenue, and have workers ──
    unlocked = me.get("unlocked_quadrants", ["NW"])
    num_quad = len(unlocked)
    land_cost_map = {1: 1000, 2: 2000, 3: 4000}
    land_cost = land_cost_map.get(num_quad, 99999)
    if (day >= 8 and num_quad < 4 and
            money > land_cost + 500 and
            n_empty < 5 and num_workers >= 2):
        orders.append(["BUY_LAND"])

    # ── Sell fertilizer if price is decent ──
    fert = shed.get("FERTILIZER", 0)
    fert_price = prices.get("FERTILIZER", 100)
    if fert > 3 and fert_price >= 80:
        orders.append(["SELL", "FERTILIZER", fert - 1])

    return orders[:10]


# ─────────────────────────────────────────────────────────────────────────────
# GYM ENVIRONMENT WRAPPER
# ─────────────────────────────────────────────────────────────────────────────

class KagricultureGym:
    """
    Minimal gym-like wrapper around kaggriculture for use with stable-baselines3.
    Compatible with gym >= 0.26 (step returns 5-tuple).
    """

    metadata = {"render_modes": []}

    def __init__(self, opponent="random"):
        try:
            import gymnasium as gym
        except ImportError:
            import gym
        self.observation_space = gym.spaces.Box(
            low=-1.0, high=3.0, shape=(OBS_DIM,), dtype=np.float32
        )
        self.action_space = gym.spaces.Discrete(N_ACTIONS)
        self.opponent = opponent
        self.trainer = None
        self.last_obs = None
        self.prev_money = 3000.0
        self.prev_n_weeds = 0
        self.prev_n_animals = 0

    def reset(self, seed=None, options=None):
        from kaggle_environments import make
        env = make("kaggriculture", configuration={"episodeSteps": 720})
        self.trainer = env.train([None, self.opponent])
        raw = self.trainer.reset()
        self.last_obs = raw
        self.prev_money = float(raw["farms"][raw["player"]]["money"])
        self.prev_n_weeds = 0
        self.prev_n_animals = 0
        return encode_obs(raw), {}

    def step(self, action_idx):
        farmer_action = ACTIONS[int(action_idx)]
        game_action = {
            "farmer": farmer_action,
            "hands": [],
            "market": market_orders(self.last_obs),
        }
        try:
            raw, _terminal_reward, done, info = self.trainer.step(game_action)
        except Exception as e:
            return np.zeros(OBS_DIM, dtype=np.float32), 0.0, True, True, {}

        if raw is None:
            return np.zeros(OBS_DIM, dtype=np.float32), 0.0, True, True, {}

        self.last_obs = raw
        player = raw["player"]
        me = raw["farms"][player]
        money = float(me.get("money", self.prev_money))
        tiles = me.get("tiles", [])

        # Dense reward: normalised money gain
        reward = (money - self.prev_money) / 100.0
        self.prev_money = money

        # Penalty: new weeds (missed watering)
        n_weeds = sum(1 for row in tiles for t in row
                      if isinstance(t, dict) and t.get("kind") == "WEED")
        if n_weeds > self.prev_n_weeds:
            reward -= 0.5 * (n_weeds - self.prev_n_weeds)
        self.prev_n_weeds = n_weeds

        obs = encode_obs(raw)
        return obs, float(reward), bool(done), False, {}

    def render(self):
        pass

    def close(self):
        pass


# ─────────────────────────────────────────────────────────────────────────────
# PYTORCH POLICY (for training only; inference uses numpy PolicyNet in model.py)
# ─────────────────────────────────────────────────────────────────────────────

def build_torch_policy():
    torch = _require("torch")
    nn = torch.nn

    class ActorCritic(nn.Module):
        def __init__(self):
            super().__init__()
            self.shared = nn.Sequential(
                nn.Linear(OBS_DIM, 256), nn.ReLU(),
                nn.Linear(256, 256),     nn.ReLU(),
            )
            self.actor  = nn.Linear(256, N_ACTIONS)
            self.critic = nn.Linear(256, 1)

        def forward(self, x):
            h = self.shared(x)
            return self.actor(h), self.critic(h)

    return ActorCritic()


def export_weights(sb3_policy, out_path):
    """
    Extract weights from a stable-baselines3 policy and save as weights.npz
    for pure-numpy inference in main.py.
    """
    import torch
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from model import PolicyNet

    sd = sb3_policy.mlp_extractor.policy_net.state_dict()
    pn = sb3_policy.action_net

    net = PolicyNet()
    # SB3 names shared layers net.0, net.2; action net is separate
    net.W1 = sd["0.weight"].cpu().numpy().astype(np.float32)
    net.b1 = sd["0.bias"].cpu().numpy().astype(np.float32)
    net.W2 = sd["2.weight"].cpu().numpy().astype(np.float32)
    net.b2 = sd["2.bias"].cpu().numpy().astype(np.float32)
    net.Wp = pn.weight.detach().cpu().numpy().astype(np.float32)
    net.bp = pn.bias.detach().cpu().numpy().astype(np.float32)
    net.save(out_path)
    print(f"[export] Weights → {out_path}.npz")
    return net


# ─────────────────────────────────────────────────────────────────────────────
# TRAINING ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps",  type=int,   default=2_000_000,
                        help="Total PPO timesteps (default 2M)")
    parser.add_argument("--envs",   type=int,   default=4,
                        help="Parallel environments (default 4)")
    parser.add_argument("--lr",     type=float, default=3e-4)
    parser.add_argument("--resume", action="store_true",
                        help="Resume from weights.npz if present")
    parser.add_argument("--out",    default="weights",
                        help="Output weights filename (no extension)")
    args = parser.parse_args()

    torch  = _require("torch")
    sb3    = _require("stable_baselines3")
    PPO    = sb3.PPO

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training on: {device}")
    if device == "cuda":
        print(f"  GPU: {torch.cuda.get_device_name(0)}")

    # Vectorised environments
    try:
        from stable_baselines3.common.vec_env import SubprocVecEnv
        def make_env(i):
            def _init():
                return KagricultureGym(opponent="random")
            return _init
        vec_env = SubprocVecEnv([make_env(i) for i in range(args.envs)])
    except Exception as e:
        print(f"SubprocVecEnv failed ({e}), falling back to DummyVecEnv")
        from stable_baselines3.common.vec_env import DummyVecEnv
        vec_env = DummyVecEnv([lambda: KagricultureGym(opponent="random")
                                for _ in range(args.envs)])

    policy_kwargs = dict(
        net_arch=dict(pi=[256, 256], vf=[256, 256]),
        activation_fn=torch.nn.ReLU,
    )

    model = PPO(
        policy          = "MlpPolicy",
        env             = vec_env,
        learning_rate   = args.lr,
        n_steps         = 1024,
        batch_size      = 256,
        n_epochs        = 10,
        gamma           = 0.995,    # high because game horizon is 720 steps
        gae_lambda      = 0.95,
        clip_range      = 0.2,
        ent_coef        = 0.01,     # encourage exploration
        vf_coef         = 0.5,
        max_grad_norm   = 0.5,
        verbose         = 1,
        device          = device,
        policy_kwargs   = policy_kwargs,
        tensorboard_log = "./tb_logs/",
    )

    print(f"\nStarting PPO training: {args.steps:,} timesteps across {args.envs} envs")
    print("Progress logs → ./tb_logs/  (tensorboard --logdir=tb_logs)")

    model.learn(
        total_timesteps = args.steps,
        progress_bar    = True,
    )

    # Save SB3 checkpoint
    model.save("ppo_checkpoint")
    print("Saved SB3 checkpoint → ppo_checkpoint.zip")

    # Export weights to numpy for deployment
    out_path = os.path.join(os.path.dirname(__file__), args.out)
    export_weights(model.policy, out_path)

    vec_env.close()
    print("\nTraining complete. Run the agent with the trained weights:")
    print("  kaggle competitions submit kaggriculture -f main.py -m 'RL v1'")
    print("  # or bundle: tar -czf submission.tar.gz main.py model.py weights.npz")


if __name__ == "__main__":
    main()
