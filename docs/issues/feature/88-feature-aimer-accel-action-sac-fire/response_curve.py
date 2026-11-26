"""#85. 조준 오차(uv_fine)에 정책이 얼마나 세게 반응하는지와, 오차가 step 마다 뒤집히는지를 본다.

    uv run python docs/issues/chore/85-chore-sac-alone-near-miss-diagnosis/response_curve.py runs/d85 > data/response.md

추적 구간(보이고 빔까지 20mm 안)만 쓴다. 행동에서 관측 target_rate 를 뺀 값이 조준 오차를 고치려고 더한 각속도다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

NAMES = ["baseline"] + [f"{c}-s{s}" for c in ("rate-rule", "accel-rule", "accel-pen-rule", "accel-fire-m03", "accel-fire-m10") for s in range(3)]
EDGES = [-1, -0.3, -0.1, -0.05, -0.02, -0.005, 0.005, 0.02, 0.05, 0.1, 0.3, 1]
RATE = (180.0, 120.0)


def main() -> None:
    src = Path(sys.argv[1])
    head = " | ".join(f"{a:g}..{b:g}" for a, b in zip(EDGES[:-1], EDGES[1:]))
    print("## Correction added to the fly's rate, by aim error (mean ± sd, °/s)\n")
    print("uv_fine: ±1 is 0.5°; 0.02 is 0.01°, about 0.3 mm at 1.8 m.\n")
    print(f"| aimer | axis | {head} |")
    print("|" + " --- |" * (len(EDGES) + 1))
    rows = []
    for name in NAMES:
        d = np.load(src / f"{name}.npz")
        m = d["vis"] & d["obs_vis"] & (d["bd"] * 1000 <= 20)
        act, rate, fine = d["act"].astype(float), d["obs_rate"].astype(float), d["obs_fine"].astype(float)
        for k, axis in enumerate(("yaw", "pitch")):
            y, x = (act[..., k] - rate[..., k])[m] * RATE[k], fine[..., k][m]
            cells = []
            for a, b in zip(EDGES[:-1], EDGES[1:]):
                s = (x > a) & (x <= b)
                cells.append(f"{y[s].mean():+.1f} ± {y[s].std():.1f}" if s.sum() > 50 else "")
            print(f"| {name} | {axis} | " + " | ".join(cells) + " |")
        e = d["err"][..., 0].astype(float) * 1000
        ac = []
        for lag in (1, 2, 3, 4):
            mm = m[:, lag:] & m[:, :-lag]
            ac.append(np.corrcoef(e[:, lag:][mm], e[:, :-lag][mm])[0, 1])
        de = np.diff(e, axis=1)
        mm = m[:, 2:] & m[:, 1:-1] & m[:, :-2]
        yr = np.diff(d["act"][..., 0].astype(float), axis=1)[m[:, 1:] & m[:, :-1]] * RATE[0]
        rows.append((name, ac, np.corrcoef(de[:, 1:][mm], de[:, :-1][mm])[0, 1], np.sqrt((de[:, 1:][mm] ** 2).mean()), np.mean(np.abs(yr) > 14.4)))
    print("\n## Horizontal error over time (tracking steps)\n")
    print("| aimer | autocorrelation at 1 step | 2 | 3 | 4 | autocorrelation of the step change | rms step change (mm) | share of steps where the yaw command jumps more than the turret can follow (14.4 °/s) |")
    print("|" + " --- |" * 8)
    for name, ac, dac, step, over in rows:
        print(f"| {name} | " + " | ".join(f"{x:+.2f}" for x in ac) + f" | {dac:+.2f} | {step:.2f} | {over:.2f} |")


if __name__ == "__main__":
    main()
