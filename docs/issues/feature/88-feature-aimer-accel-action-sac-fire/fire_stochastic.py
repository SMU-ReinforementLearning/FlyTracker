"""#88. The fire-learning models acting as in training (actions sampled, fire allowed): shots, misfires, captures.

    uv run python docs/issues/feature/88-feature-aimer-accel-action-sac-fire/fire_stochastic.py runs/g88 > data/fire-stochastic.md

50 episodes per model, seeds 20000-20049. Also the fire action's distribution (mean and sd before tanh, median over steps).
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import torch

from flytracker.env import EnvConfig, FlyChaseEnv
from flytracker.players import load_opponent
from flytracker.wrappers import accel_to_rate

EPISODES = 50


def main() -> None:
    root = Path(sys.argv[1])
    torch.set_num_threads(1)
    cfg = EnvConfig()
    print("| model | captures of 50 | shots per episode | misfires per episode | fire mean (before tanh) | fire sd | share of steps with a sampled fire above 0 |")
    print("|" + " --- |" * 7)
    for cond in ("accel-fire-m03", "accel-fire-m10"):
        for s in range(3):
            run = next((root / f"{cond}-s{s}").glob("2*"))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                opp = load_opponent(str(run), "aimer", cfg)
            model, gain = opp.player.policy, opp.player.accel_gain
            model.set_random_seed(20000)
            env = FlyChaseEnv(cfg)
            caps = shots = miss = 0
            means, sds, pulls = [], [], []
            for ep in range(EPISODES):
                obs, _ = env.reset(seed=20000 + ep)
                while True:
                    action, _ = model.predict(obs, deterministic=False)
                    with torch.no_grad():
                        mean, log_std, _ = model.actor.get_action_dist_params(torch.as_tensor(obs[None]))
                    means.append(float(mean[0, 2]))
                    sds.append(float(log_std[0, 2].exp()))
                    pulls.append(action[2] > 0)
                    obs, _, terminated, truncated, info = env.step(accel_to_rate(obs, np.asarray(action, dtype=float), gain))
                    if terminated or truncated:
                        break
                caps += int(terminated)
                shots += info["shots"]
                miss += info["misfires"]
            print(f"| {cond}-s{s} | {caps} | {shots / EPISODES:.2f} | {miss / EPISODES:.2f} | {np.median(means):+.2f} | {np.median(sds):.3f} | {np.mean(pulls):.4f} |")


if __name__ == "__main__":
    main()
