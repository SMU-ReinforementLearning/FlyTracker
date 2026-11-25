"""#88. How far the fire-learning policies are from firing: the mean of the fire action (before tanh) by beam distance.

The policy fires when the fire action is above 0. Reads the npz files of measure_tracking.py (fire held off).

    uv run python docs/issues/feature/88-feature-aimer-accel-action-sac-fire/fire_head.py runs/d88 > data/fire-head.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

BANDS = ((0, 0.5), (0.5, 1.25), (1.25, 3), (3, 20), (20, 1e9))


def main() -> None:
    src = Path(sys.argv[1])
    print("| model | " + " | ".join(f"{a:g}-{b:g} mm" if b < 1e8 else f"over {a:g} mm" for a, b in BANDS) + " | not visible | share of visible steps with mean above 0 |")
    print("|" + " --- |" * (len(BANDS) + 3))
    for cond in ("accel-fire-m03", "accel-fire-m10"):
        for s in range(3):
            d = np.load(src / f"{cond}-s{s}.npz")
            # fire_mean[t] was computed from the observation before step t; bd[t-1] is the beam distance of that observation
            fm, bd, vis = d["fire_mean"][:, 1:].astype(float), d["bd"][:, :-1].astype(float) * 1000, d["obs_vis"][:, 1:]
            ok = np.isfinite(fm)
            cells = [f"{np.median(fm[ok & vis & (bd >= a) & (bd < b)]):+.2f}" for a, b in BANDS]
            print(f"| {cond}-s{s} | " + " | ".join(cells) + f" | {np.median(fm[ok & ~vis]):+.2f} | {np.mean(fm[ok & vis] > 0):.4f} |")
    print("\nMedian of the fire action's mean before tanh. Fire needs a value above 0; tanh(-2) = -0.96.")


if __name__ == "__main__":
    main()
