"""#88 stage 2. What the fire-only policies do with the trigger, next to the fire rule on the same aim.

    uv run python docs/issues/feature/88-feature-aimer-accel-action-sac-fire/fire_only_diag.py runs/g88f > data/fire-only.md

Table 1: deterministic, seeds 20000-20199 (the gate's episodes). Only steps where a new shot can start (obs `shot` is 0).
The fire value is the policy's output after tanh; without the prior it fires above 0, with the rule prior above -0.5 when
the rule says fire and above +0.5 when it does not. Beam distance is the true one (info), of the observation acted on.
Table 2: the same models with sampled actions, as in training, 50 episodes (seeds 20000-20049).
"""

from __future__ import annotations

import sys
import warnings
from collections import deque
from pathlib import Path

import numpy as np
import torch

from flytracker.env import OBS, EnvConfig, FlyChaseEnv
from flytracker.players import load_opponent
from flytracker.wrappers import fire_decision

CONDITIONS = ("fire-m1", "fire-m5", "fire-prior-m1", "fire-prior-m5")
BANDS = ((0, 0.5), (0.5, 1.25), (1.25, 3), (3, 1e9))
SAMPLED_EPISODES = 50


def rollout(player, env, seeds, deterministic: bool) -> dict:
    """Play the episodes; return per free step (value, sd, beam distance mm, visible, rule verdict, fired, shot outcome)."""
    model = player.policy
    rows, caps, shots, miss = [], 0, 0, 0
    for seed in seeds:
        obs, info = env.reset(seed=seed)
        player.aim.reset()
        stack = None
        pending = None  # index in rows of the shot in flight
        while True:
            x = np.asarray(obs, dtype=np.float32)
            if stack is None:  # as FireOnlyPlayer: the first observation fills the stack
                stack = deque([x] * player.frame_stack, maxlen=player.frame_stack)
            else:
                stack.append(x)
            xs = np.stack(stack) if player.frame_stack > 1 else x
            value, _ = model.predict(xs, deterministic=deterministic)
            value = float(np.asarray(value).reshape(-1)[0])
            with torch.no_grad():
                mean, log_std, _ = model.actor.get_action_dist_params(model.policy.obs_to_tensor(xs)[0])
            a = np.asarray(player.aim.act(obs), dtype=float)
            rule = bool(a[2] > 0.0)
            fire = fire_decision(value, rule, player.prior)
            a[2] = 1.0 if fire else -1.0
            free = float(x[OBS["shot"]][0]) == 0.0
            if free:
                rows.append([float(torch.tanh(mean)[0, 0]), float(log_std.exp()[0, 0]), info["beam_dist"] * 1000, float(info["visible"]),
                             float(rule), float(fire), np.nan])
                if fire:
                    pending = len(rows) - 1
            before = info["misfires"]
            obs, _, terminated, truncated, info = env.step(a)
            if pending is not None:
                if terminated:
                    rows[pending][6] = 1.0
                    pending = None
                elif info["misfires"] > before:
                    rows[pending][6] = 0.0
                    pending = None
            if terminated or truncated:
                break
        caps += int(terminated)
        shots += info["shots"]
        miss += info["misfires"]
    return {"rows": np.array(rows), "caps": caps, "shots": shots, "miss": miss, "n": len(seeds)}


def pct(x) -> str:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]  # a shot still in flight when the episode was cut at 10 s has no outcome
    return "-" if len(x) == 0 else f"{100 * np.mean(x):.1f} %"


def main() -> None:
    root = Path(sys.argv[1])
    torch.set_num_threads(1)
    cfg = EnvConfig()
    env = FlyChaseEnv(cfg)
    t1 = ["| model | " + " | ".join(f"value at {a:g}-{b:g} mm" if b < 1e8 else f"value over {a:g} mm" for a, b in BANDS)
          + " | value, not visible | rule says fire, policy holds | shots the rule would not take | hit rate of shots the rule would take"
          " | hit rate of shots the rule would not take |", "|" + " --- |" * (len(BANDS) + 6)]
    t2 = ["| model | captures of 50 | shots per episode | misfires per episode | fire sd (median) | share of free steps fired |",
          "|" + " --- |" * 6]
    for cond in CONDITIONS:
        for s in range(3):
            run = next((root / f"{cond}-s{s}").glob("2*"))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                player = load_opponent(str(run), "aimer", cfg).player
            d = rollout(player, env, range(20000, 20200), True)["rows"]
            val, bd, vis, rule, fire, hit = d[:, 0], d[:, 2], d[:, 3] > 0.5, d[:, 4] > 0.5, d[:, 5] > 0.5, d[:, 6]
            cells = [f"{np.median(val[vis & (bd >= a) & (bd < b)]):+.2f}" for a, b in BANDS]
            t1.append(f"| {cond}-s{s} | " + " | ".join(cells) + f" | {np.median(val[~vis]):+.2f} | {pct(~fire[rule])} | {pct(~rule[fire])}"
                      f" | {pct(hit[fire & rule])} | {pct(hit[fire & ~rule])} |")
            player.policy.set_random_seed(20000)
            r = rollout(player, env, range(20000, 20000 + SAMPLED_EPISODES), False)
            t2.append(f"| {cond}-s{s} | {r['caps']} | {r['shots'] / r['n']:.2f} | {r['miss'] / r['n']:.2f} | {np.median(r['rows'][:, 1]):.3f}"
                      f" | {pct(r['rows'][:, 5] > 0.5)} |")
            print(f"{cond}-s{s} done", file=sys.stderr)
    print("## 1. Deterministic, seeds 20000-20199, steps where a new shot can start\n")
    print("\n".join(t1))
    print("\nValue = the policy's output after tanh (median). A hit is a shot that captured; the rest are misfires.\n")
    print("## 2. Sampled actions (as in training), seeds 20000-20049\n")
    print("\n".join(t2))


if __name__ == "__main__":
    main()
