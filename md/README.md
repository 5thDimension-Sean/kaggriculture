# Kaggriculture — PPO RL Agent

Submission for the [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture) competition hosted by Google LLC on Kaggle.

## Approach

A Proximal Policy Optimization (PPO) agent trained via [stable-baselines3](https://github.com/DLR-RM/stable-baselines3) against a random opponent. At inference, the trained weights are embedded as a pure-numpy model so no PyTorch dependency is required in the submission environment.

Key components:
- **Observation encoder** (`model.py`): 74-dimensional feature vector encoding board state, inventory, market prices, and opponent position
- **Market module** (`train.py`): price-impact sell sorting with NPC-demand persistence weighting
- **Terminal liquidation** (`main.py`): Town Center phase-aware liquidation strategy that prioritizes items with no NPC price recovery
- **Opponent exposure scoring**: weights opponent crop production by NPC demand recovery rate

## Reproduce

Install dependencies:

```bash
pip install torch stable-baselines3 kaggle-environments
```

Train from scratch (requires GPU, ~30 min for 2M steps):

```bash
python train.py --steps 2000000
```

Resume from existing weights:

```bash
python train.py --resume
```

The trained weights are embedded into `main.py` as a base64-encoded numpy array. After training, copy the printed weights block into `main.py`.

## Files

| File | Description |
|------|-------------|
| `main.py` | Competition submission entry point (self-contained, no external deps) |
| `model.py` | Shared observation encoder and model constants |
| `train.py` | PPO training script |

## Credits and Inspiration

Code written with assistance from Claude Sonnet 4.6.

Ideas and approaches drawn from publicly shared notebooks on the Kaggle forum. All code was independently implemented.

- https://www.kaggle.com/code/kaitofukami/41-49-future-unseen-v19-replication-to-control
- https://www.kaggle.com/code/navazshfathi/177-180-fresh-top-30-v21-1-conditional-memory
- https://www.kaggle.com/code/rahuljiwane/kaggriculture-rahul-jiwane
- https://www.kaggle.com/code/flexonafft/kaggriculture-adaptive-replay-agent
- https://www.kaggle.com/code/bruceqdu/my-2026-08-04-high-score-pipeline
- https://www.kaggle.com/code/boatlee/v13-r3-top-meta-order-safe-premium-control
- https://www.kaggle.com/code/raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta
- https://www.kaggle.com/code/romantamrazov/kaggriculture-yummers
- https://www.kaggle.com/code/anasriaz/kaggriculture
- https://www.kaggle.com/code/kaitofukami/44-46-strict-future-top-30-v22-price-impact

## License

Code: [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)

If this submission wins a prize, the winning submission will additionally be licensed under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) per competition rules (Section 2.5).
