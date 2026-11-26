"""#85. measure_tracking.py 가 적은 npz 를 읽어 표를 만든다.

    uv run python docs/issues/chore/85-chore-sac-alone-near-miss-diagnosis/analyze.py runs/d85 \
        docs/issues/chore/85-chore-sac-alone-near-miss-diagnosis/data [#51 gate 폴더]

출력 (data 폴더): tables.md (표 전부), episodes.csv (조준기 × seed 한 줄), capture-grid.csv (반경 × 유지 시간).

용어
- 추적 구간: 행동을 낼 때 초파리가 보였고, 그 step 이 끝났을 때도 보이며 빔까지 20mm 안인 step. 처음 찾아 다가가는 구간을 뺀다.
- 뒤처짐: 어긋남을 초파리가 화면에서 움직이는 방향으로 잰 값. + 면 초파리가 빔보다 앞에 있다(빔이 뒤따라간다).
- 옆 어긋남: 움직이는 방향에 수직인 성분.
- 느린 성분: 어긋남의 0.22초 이동 평균. 빠른 성분: 어긋남에서 느린 성분을 뺀 나머지(떨림).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

RADII_MM = (1.25, 2.0, 3.0, 5.0, 10.0)
HOLDS_S = (0.05, 0.10, 0.15)
CONDITIONS = ("rate-rule", "accel-rule", "accel-pen-rule", "accel-fire-m03", "accel-fire-m10")  # #88's five
ORDER = ["baseline"] + [f"{c}-s{s}" for c in CONDITIONS for s in range(3)]
TRACK_MM = 20.0
WINDOW = 11  # step. 0.22초
RATE_DEG = np.array([180.0, 120.0])  # 행동 1 이 뜻하는 각속도 (yaw, pitch)


def first_capture(inside: np.ndarray, need: int, dt: float) -> float:
    """inside 가 need 번 이어진 첫 시각 (s). 없으면 nan."""
    run = 0
    for i, x in enumerate(inside):
        run = run + 1 if x else 0
        if run >= need:
            return (i + 1) * dt
    return float("nan")


def longest(inside: np.ndarray) -> int:
    best = run = 0
    for x in inside:
        run = run + 1 if x else 0
        best = max(best, run)
    return best


def segments(mask: np.ndarray, min_len: int):
    """mask 가 True 로 이어진 구간 (시작, 끝)."""
    start = None
    for i, x in enumerate(np.append(mask, False)):
        if x and start is None:
            start = i
        elif not x and start is not None:
            if i - start >= min_len:
                yield start, i
            start = None


def rms(x) -> float:
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(x**2))) if x.size else float("nan")


def analyse(name: str, d) -> tuple[dict, list[dict], dict]:
    vis, bd, obs_vis = d["vis"], d["bd"].astype(float) * 1000, d["obs_vis"]
    n, steps = vis.shape
    dt, pdt = 10.0 / steps, 10.0 / d["bd_phys"].shape[1]
    track = vis & obs_vis & (bd <= TRACK_MM)
    err = d["err"].astype(float) * 1000  # mm
    vel = d["vel"].astype(float)  # m/s
    speed = np.linalg.norm(vel, axis=-1)
    moving = track & (speed > 0.02)
    vhat = vel / np.maximum(speed, 1e-9)[..., None]
    lag = np.sum(err * vhat, axis=-1)
    side = err[..., 0] * vhat[..., 1] - err[..., 1] * vhat[..., 0]

    slow_parts, fast_parts, flips = [], [], []
    for ep in range(n):
        for a, b in segments(track[ep], 2 * WINDOW):
            e = err[ep, a:b]
            kernel = np.ones(WINDOW) / WINDOW
            slow = np.stack([np.convolve(e[:, k], kernel, mode="valid") for k in range(2)], axis=1)
            fast = e[WINDOW // 2 : WINDOW // 2 + len(slow)] - slow
            slow_parts.append(slow)
            fast_parts.append(fast)
            de = np.diff(e, axis=0)
            flips.append(np.mean(np.sum(de[1:] * de[:-1], axis=1) < 0))
    slow_all = np.concatenate(slow_parts) if slow_parts else np.zeros((0, 2))
    fast_all = np.concatenate(fast_parts) if fast_parts else np.zeros((0, 2))

    # 행동: 정책이 낸 값과 기준선의 추적 행동, 그리고 관측에 대한 선형 맞춤
    act, trk = d["act"].astype(float), d["trk"].astype(float)
    m = track
    diff = (act - trk)[m] * RATE_DEG
    dact = np.diff(act, axis=1)[m[:, 1:] & m[:, :-1]] * RATE_DEG
    dtrk = np.diff(trk, axis=1)[m[:, 1:] & m[:, :-1]] * RATE_DEG
    fit = {}
    for k, axis in enumerate(("yaw", "pitch")):
        x = np.column_stack([d["obs_rate"][m][:, k], d["obs_fine"][m][:, k], np.ones(m.sum())]).astype(float)
        y = act[m][:, k]
        if len(y) > 10:
            coef, *_ = np.linalg.lstsq(x, y, rcond=None)
            res = y - x @ coef
            fit[axis] = (coef[0], coef[1], coef[2] * RATE_DEG[k], res.std() * RATE_DEG[k])
        else:
            fit[axis] = (np.nan,) * 4
    std_act = d["std"].astype(float) * (1 - np.tanh(d["mean"].astype(float)) ** 2)  # 행동 눈금의 표준편차 (1차 어림)

    first_seen = np.where(vis.any(axis=1), vis.argmax(axis=1) * dt, np.nan)
    row = {
        "name": name,
        "visible": vis.mean(),
        "first_seen_s": np.nanmean(first_seen),
        "never_seen": int((~vis.any(axis=1)).sum()),
        "bd_median_mm": np.median(bd[vis]),
        "bd_p10_mm": np.percentile(bd[vis], 10),
        "bd_p90_mm": np.percentile(bd[vis], 90),
        "in_1.25": (vis & (bd <= 1.25)).sum() / vis.sum(),
        "in_2.5": (vis & (bd <= 2.5)).sum() / vis.sum(),
        "in_5": (vis & (bd <= 5)).sum() / vis.sum(),
        "track_share": track.sum() / vis.sum(),
        "track_median_mm": np.median(bd[track]),
        "lag_mean_mm": lag[moving].mean(),
        "lag_sd_mm": lag[moving].std(),
        "side_mean_mm": side[moving].mean(),
        "side_sd_mm": side[moving].std(),
        "lag_ms": np.median(lag[moving] / 1000 / speed[moving]) * 1000,
        "slow_rms_mm": rms(np.linalg.norm(slow_all, axis=1)),
        "fast_rms_mm": rms(np.linalg.norm(fast_all, axis=1)),
        "flip_rate": float(np.mean(flips)) if flips else np.nan,
        "act_minus_trk_mean": diff.mean(axis=0),
        "act_minus_trk_sd": diff.std(axis=0),
        "dact_rms": np.sqrt((dact**2).mean(axis=0)),
        "dtrk_rms": np.sqrt((dtrk**2).mean(axis=0)),
        "fit": fit,
        "std_act_deg": np.nanmedian(std_act[m], axis=0) * RATE_DEG if np.isfinite(std_act[m]).any() else np.array([np.nan, np.nan]),
        "dist_median_m": np.median(d["dist"][track]),
    }

    grid, episodes = {}, []
    inside_all = d["vis_phys"][:, None, :] & (d["bd_phys"][:, None, :] * 1000 <= np.array(RADII_MM)[None, :, None])
    times = np.full((n, len(RADII_MM), len(HOLDS_S)), np.nan)
    for ep in range(n):
        for i in range(len(RADII_MM)):
            for j, hold in enumerate(HOLDS_S):
                times[ep, i, j] = first_capture(inside_all[ep, i], round(hold / pdt), pdt)
    for i, r in enumerate(RADII_MM):
        for j, hold in enumerate(HOLDS_S):
            t = times[:, i, j]
            grid[(r, hold)] = (int(np.isfinite(t).sum()), float(np.where(np.isfinite(t), t, 10.0).mean()))
    for ep in range(n):
        v = vis[ep]
        episodes.append({
            "aimer": name, "seed": int(d_first_seed(name)) + ep, "visible": round(float(v.mean()), 4),
            "first_seen_s": "" if not v.any() else round(float(first_seen[ep]), 2),
            "bd_median_mm": "" if not v.any() else round(float(np.median(bd[ep][v])), 4),
            "in_1.25": round(float((v & (bd[ep] <= 1.25)).mean()), 4),
            "longest_in_1.25_s": round(longest(inside_all[ep, 0]) * pdt, 2),
            **{f"t_{r}mm_{hold}s": "" if not np.isfinite(times[ep, i, j]) else round(float(times[ep, i, j]), 2)
               for i, r in enumerate(RADII_MM) for j, hold in enumerate(HOLDS_S)},
        })
    return row, episodes, grid


def d_first_seed(name: str) -> int:
    return 20000


def main() -> None:
    src, dest = Path(sys.argv[1]), Path(sys.argv[2])
    gate = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    dest.mkdir(parents=True, exist_ok=True)
    rows, all_eps, grids = [], [], {}
    for name in ORDER:
        f = src / f"{name}.npz"
        if not f.exists():
            print(f"missing {f}", file=sys.stderr)
            continue
        row, eps, grid = analyse(name, np.load(f))
        rows.append(row)
        all_eps += eps
        grids[name] = grid

    L = []
    L += ["## 1. Distance to the beam, seeds 20000-20199, 10 s each, fire held off", "",
          "| aimer | visible | first seen (s) | never seen | median (mm) | p10 | p90 | time ≤1.25 mm | ≤2.5 | ≤5 |", "|" + " --- |" * 10]
    for r in rows:
        L.append(f"| {r['name']} | {r['visible']:.3f} | {r['first_seen_s']:.2f} | {r['never_seen']} | {r['bd_median_mm']:.2f} | {r['bd_p10_mm']:.2f} | "
                 f"{r['bd_p90_mm']:.1f} | {r['in_1.25']:.3f} | {r['in_2.5']:.3f} | {r['in_5']:.3f} |")
    L += ["", "Distances and shares are over the steps where the fly is visible.", ""]

    L += ["## 2. Counterfactual capture: captures of 200 and mean time (s; 10 s when not captured)", ""]
    for hold in HOLDS_S[::-1]:
        L += [f"Hold {hold:.2f} s", "", "| aimer | " + " | ".join(f"{r} mm" for r in RADII_MM) + " |", "|" + " --- |" * (len(RADII_MM) + 1)]
        for r in rows:
            g = grids[r["name"]]
            L.append(f"| {r['name']} | " + " | ".join(f"{g[(x, hold)][0]}, {g[(x, hold)][1]:.2f}" for x in RADII_MM) + " |")
        L.append("")

    if gate is not None:
        L += ["## 3. Check against #51's gate files (radius 1.25 mm, hold 0.15 s)", "",
              "| aimer | captures here | captures in #51 | seeds where both agree | mean time here | in #51 |", "|" + " --- |" * 6]
        by_name = {}
        for e in all_eps:
            by_name.setdefault(e["aimer"], []).append(e)
        for name in ORDER:
            f = gate / f"{name}.csv"
            if not f.exists() or name not in by_name:
                continue
            ref = {int(x["id"]): x for x in csv.DictReader(f.open(encoding="utf-8"))}
            mine = by_name[name]
            cap_here = [e["t_1.25mm_0.15s"] != "" for e in mine]
            cap_ref = [float(ref[e["seed"]]["capture"]) > 0.5 for e in mine]
            t_here = np.mean([e["t_1.25mm_0.15s"] or 10.0 for e in mine])
            t_ref = np.mean([float(ref[e["seed"]]["time"]) for e in mine])
            agree = sum(a == b for a, b in zip(cap_here, cap_ref))
            L.append(f"| {name} | {sum(cap_here)} | {sum(cap_ref)} | {agree}/200 | {t_here:.3f} | {t_ref:.3f} |")
        L.append("")

    L += ["## 4. What the residual error is made of (tracking steps: visible, within 20 mm)", "",
          "| aimer | tracking share of visible | median (mm) | lag mean (mm) | lag sd | side mean | side sd | lag as time (ms) | slow rms (mm) | fast rms (mm) | direction flips |",
          "|" + " --- |" * 11]
    for r in rows:
        L.append(f"| {r['name']} | {r['track_share']:.3f} | {r['track_median_mm']:.2f} | {r['lag_mean_mm']:+.2f} | {r['lag_sd_mm']:.2f} | {r['side_mean_mm']:+.2f} | "
                 f"{r['side_sd_mm']:.2f} | {r['lag_ms']:+.1f} | {r['slow_rms_mm']:.2f} | {r['fast_rms_mm']:.2f} | {r['flip_rate']:.2f} |")
    L += ["", "Lag: error along the fly's on-screen motion, + when the fly is ahead of the beam. Slow: 0.22 s moving average of the error vector; fast: the rest. "
          "Direction flips: share of steps where the change of the error reverses direction.", ""]

    L += ["## 5. Action against the rule tracker on the same observations (tracking steps; °/s)", "",
          "| aimer | action − tracker, mean (yaw, pitch) | sd | step-to-step change of action, rms | of tracker | policy sd in training, median |", "|" + " --- |" * 6]
    p = lambda v: f"{v[0]:+.2f}, {v[1]:+.2f}"  # noqa: E731
    u = lambda v: f"{v[0]:.2f}, {v[1]:.2f}"  # noqa: E731
    for r in rows:
        L.append(f"| {r['name']} | {p(r['act_minus_trk_mean'])} | {u(r['act_minus_trk_sd'])} | {u(r['dact_rms'])} | {u(r['dtrk_rms'])} | {u(r['std_act_deg'])} |")
    L += ["", "Median distance to the fly on tracking steps: " + ", ".join(f"{r['name']} {r['dist_median_m']:.2f} m" for r in rows[:2]) +
          ". At 1.5 m, 1 °/s moves the beam 26 mm/s, 0.5 mm per step.", ""]

    L += ["## 6. Linear fit of the action on tracking steps: action = a × target_rate + b × uv_fine + c, residual sd", "",
          "| aimer | yaw a | yaw b | yaw c (°/s) | yaw residual sd (°/s) | pitch a | pitch b | pitch c (°/s) | pitch residual sd (°/s) |", "|" + " --- |" * 9]
    for r in rows:
        y, q = r["fit"]["yaw"], r["fit"]["pitch"]
        L.append(f"| {r['name']} | {y[0]:.3f} | {y[1]:.3f} | {y[2]:+.2f} | {y[3]:.2f} | {q[0]:.3f} | {q[1]:.3f} | {q[2]:+.2f} | {q[3]:.2f} |")
    L += ["", "The rule tracker is a = 1 and, near the centre, b ≈ 25/s × 0.5° ÷ max rate = 0.069 (yaw) and 0.104 (pitch), with the yaw value divided by cos(pitch).", ""]

    (dest / "tables.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    with (dest / "episodes.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(all_eps[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(all_eps)
    with (dest / "capture-grid.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["aimer", "radius_mm", "hold_s", "captures", "mean_time_s"])
        for name, g in grids.items():
            for (r, hold), (c, t) in g.items():
                w.writerow([name, r, hold, c, round(t, 4)])
    print(f"wrote {dest / 'tables.md'}")


if __name__ == "__main__":
    main()
