"""
Shared model definition and observation encoder.
Supports both PyTorch training (train.py) and pure-numpy inference (main.py).
"""

import math
import numpy as np

# ── Dimensions ────────────────────────────────────
OBS_DIM = 82   # 74 base + 8 town shop flags
N_ACTIONS = 21  # +FERTILIZE

BOARD_SIZE = 10
HALF = BOARD_SIZE // 2
SHED_ADJ = frozenset([(HALF-1, HALF-1), (HALF, HALF-1), (HALF-1, HALF), (HALF, HALF)])

BASE_PRICES = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120,
    "MELON": 250, "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100,
}
CROP_KEYS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
PRODUCT_KEYS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
                "EGG", "MILK", "WOOL", "FERTILIZER"]
ANIMAL_PRODUCT = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}

SHOP_KEYS = [
    "BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE",
    "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP", "FARMERS_MARKET",
]

# Farmer action index → game action list
ACTIONS = [
    ["PASS"],                                      # 0
    ["NORTH"], ["SOUTH"], ["EAST"], ["WEST"],       # 1-4
    ["WATER"], ["HARVEST"], ["FEED"],               # 5-7
    ["CARE"], ["COLLECT_FERTILIZER"],               # 8-9
    ["DIG"], ["BUILD_COOP"], ["BUILD_PASTURE"],     # 10-12
    ["PLANT", "WHEAT"], ["PLANT", "CARROT"],        # 13-14
    ["PLANT", "TOMATO"], ["PLANT", "STRAWBERRY"],  # 15-16
    ["PLANT", "MELON"],                             # 17
    ["PICKUP", "WHEAT", 5], ["DROP"],               # 18-19
    ["FERTILIZE"],                                  # 20
]


def md(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def encode_obs(obs):
    """
    Encode the raw game observation into a fixed-size float32 numpy array.
    OBS_DIM = 74.
    """
    feats = []
    player = obs["player"]
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    me = obs["farms"][player]
    private = obs.get("private", {})
    market = obs.get("market", {"prices": {}, "inventory": {}})
    tiles = me.get("tiles", [[None] * BOARD_SIZE] * BOARD_SIZE)

    fx, fy = me.get("farmer", [HALF - 1, HALF - 1])
    fpos = (fx, fy)
    prices = market.get("prices", {})
    inv_mkt = market.get("inventory", {})
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    inventories = private.get("inventories", [{}])
    inv0 = inventories[0] if inventories else {}
    unlocked = set(me.get("unlocked_quadrants", ["NW"]))

    # 1. Time  (2)
    feats += [day / 29.0, hour / 23.0]

    # 2. Money log-scale  (1)
    money = float(me.get("money", 3000))
    feats += [min(1.0, math.log1p(money) / math.log1p(100_000))]

    # 3. Farmer position + shed adjacency  (3)
    feats += [fx / 9.0, fy / 9.0, float(fpos in SHED_ADJ)]

    # 4. Land ownership  (4)
    feats += [float(q in unlocked) for q in ["NW", "NE", "SW", "SE"]]

    # 5. Hires today  (1)
    feats += [min(1.0, me.get("hires_today", 0) / 5.0)]

    # 6. Market prices ratio to base  (9)
    for p in PRODUCT_KEYS:
        base = BASE_PRICES[p]
        feats += [min(3.0, prices.get(p, base) / base) / 3.0]

    # 7. Market inventory ratio  (9)
    for p in PRODUCT_KEYS:
        feats += [min(1.0, inv_mkt.get(p, 10_000) / 10_000)]

    # 8. Seeds owned  (5)
    for c in CROP_KEYS:
        feats += [min(1.0, seeds.get(c, 0) / 30.0)]

    # 9. Shed contents  (9)
    for p in PRODUCT_KEYS:
        feats += [min(1.0, shed.get(p, 0) / 50.0)]

    # 10. Farmer inventory  (9)
    for p in PRODUCT_KEYS:
        feats += [min(1.0, inv0.get(p, 0) / 20.0)]

    # 11. Farm summary + nearest-task distances  (14)
    n_empty = n_plant = n_animal_struct = n_weed = 0
    n_unwatered = n_urgent_w = n_harvest_p = 0
    n_unfed = n_urgent_f = n_harvest_a = 0
    d_nearest_unwater = d_nearest_harvest = d_nearest_plant_slot = 14.0

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            t = tiles[y][x]
            dist = md((x, y), fpos)
            if t is None:
                n_empty += 1
                d_nearest_plant_slot = min(d_nearest_plant_slot, dist)
            elif isinstance(t, dict):
                k = t.get("kind")
                if k == "PLANT":
                    n_plant += 1
                    if not t.get("watered_today"):
                        n_unwatered += 1
                        d_nearest_unwater = min(d_nearest_unwater, dist)
                        if t.get("consecutive_unwatered", 0) >= 1:
                            n_urgent_w += 1
                    if t.get("yield_units", 0) > 0:
                        n_harvest_p += 1
                        d_nearest_harvest = min(d_nearest_harvest, dist)
                elif k in ("COOP", "PASTURE"):
                    n_animal_struct += 1
                    if t.get("animal"):
                        if not t.get("fed_today"):
                            n_unfed += 1
                            if t.get("consecutive_unfed", 0) >= 1:
                                n_urgent_f += 1
                        if t.get("yield_units", 0) > 0:
                            n_harvest_a += 1
                            d_nearest_harvest = min(d_nearest_harvest, dist)
                elif k == "WEED":
                    n_weed += 1

    denom_p = max(1, n_plant)
    denom_a = max(1, n_animal_struct)
    feats += [
        n_empty / 25.0,
        n_plant / 25.0,
        n_animal_struct / 10.0,
        n_weed / 5.0,
        n_unwatered / denom_p,
        n_urgent_w / denom_p,
        n_harvest_p / denom_p,
        n_unfed / denom_a,
        n_urgent_f / denom_a,
        n_harvest_a / denom_a,
        d_nearest_unwater / 14.0,
        d_nearest_harvest / 14.0,
        d_nearest_plant_slot / 14.0,
        min(1.0, n_weed / 5.0),
    ]

    # 12. Town shops unlocked  (8)
    town = obs.get("town", {}) or {}
    unlocked_shops = set(town.get("unlocked_shops", []) or [])
    feats += [float(s in unlocked_shops) for s in SHOP_KEYS]

    # 13. Current tile features  (8)
    ftile = tiles[fy][fx] if 0 <= fy < BOARD_SIZE and 0 <= fx < BOARD_SIZE else None
    if ftile is None:
        feats += [1, 0, 0, 0, 0, 0, 0, 0]
    elif ftile == "LOCKED":
        feats += [0, 1, 0, 0, 0, 0, 0, 0]
    elif isinstance(ftile, dict):
        k = ftile.get("kind")
        if k == "PLANT":
            ci = CROP_KEYS.index(ftile.get("crop", "WHEAT")) / 4.0
            age = (day - ftile.get("planted_day", 0)) / 20.0
            feats += [0, 0, 1, ci, float(ftile.get("watered_today", False)),
                      ftile.get("yield_units", 0) / 6.0,
                      ftile.get("consecutive_unwatered", 0) / 2.0,
                      min(1.0, age)]
        elif k in ("COOP", "PASTURE"):
            feats += [0, 0, 0, 0, float(ftile.get("fed_today", False)),
                      ftile.get("yield_units", 0) / 4.0,
                      float(bool(ftile.get("animal"))),
                      float(ftile.get("fertilizer_available", False))]
        elif k == "WEED":
            feats += [0, 0, 0, 0, 0, 0, 0, 1]
        else:
            feats += [0] * 8
    else:
        feats += [0] * 8

    # Verify dimension  (74 base + 8 town shop flags = 82)
    assert len(feats) == OBS_DIM, f"Expected {OBS_DIM} got {len(feats)}"
    return np.array(feats, dtype=np.float32)


# ── Numpy-only policy for inference (no PyTorch dependency) ──────────────────

class PolicyNet:
    """
    2-layer MLP: OBS_DIM → 256 → 256 → N_ACTIONS.
    Runs in pure numpy – no ML framework needed for deployment.
    """

    def __init__(self):
        self.W1 = np.zeros((256, OBS_DIM), dtype=np.float32)
        self.b1 = np.zeros(256, dtype=np.float32)
        self.W2 = np.zeros((256, 256), dtype=np.float32)
        self.b2 = np.zeros(256, dtype=np.float32)
        self.Wp = np.zeros((N_ACTIONS, 256), dtype=np.float32)
        self.bp = np.zeros(N_ACTIONS, dtype=np.float32)

    def forward(self, x):
        h = np.maximum(0, self.W1 @ x + self.b1)
        h = np.maximum(0, self.W2 @ h + self.b2)
        return self.Wp @ h + self.bp

    def act_greedy(self, x):
        return int(np.argmax(self.forward(x)))

    def act_sample(self, x, temp=1.0):
        logits = self.forward(x) / temp
        logits -= logits.max()
        probs = np.exp(logits)
        probs /= probs.sum()
        return int(np.random.choice(N_ACTIONS, p=probs))

    def save(self, path):
        np.savez_compressed(path,
                            W1=self.W1, b1=self.b1,
                            W2=self.W2, b2=self.b2,
                            Wp=self.Wp, bp=self.bp)
        print(f"Saved weights to {path}")

    def load(self, path):
        d = np.load(path)
        self.W1 = d["W1"]; self.b1 = d["b1"]
        self.W2 = d["W2"]; self.b2 = d["b2"]
        self.Wp = d["Wp"]; self.bp = d["bp"]
        return self
