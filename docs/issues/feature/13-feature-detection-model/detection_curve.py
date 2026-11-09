"""검출 모델의 출발값으로 거리별 검출 확률을 계산하고, 초파리가 그 거리에 얼마나 머무는지 잰다.

    uv run python docs/issues/feature/13-feature-detection-model/detection_curve.py

- 카메라는 세로 1080 px, 세로 시야각 40° (환경 기본값)다.
- 초파리 겉보기 크기(영상에서 차지하는 px 수)는 초점 거리에 몸길이 3.0 mm 를 곱하고 깊이로 나눠 구한다. 몸길이는 viewer/public/models/fruitfly.glb 를 잰 값이다.
- 검출 확률은 ACQUIRE 모델의 TTPF 식에 Johnson 기준(검출 50% = 1 cycle = 2 px)을 넣은 것이다.
- 초파리 거리 분포는 fly_stats.py 와 같은 200마리 × 10초이고, 시작 자리는 환경처럼 조준기에서 1.5 m 넘게 떨어뜨린다.
  조준기가 초파리를 정면으로 본다고 치고 깊이 = 직선 거리로 둔다.
"""

from __future__ import annotations

import math

import numpy as np

from flytracker.env import EnvConfig
from flytracker.fly import Fly, FlyParams

HEIGHT_PX = 1080
BODY_LENGTH = 0.003  # m
N50_CYCLES = 1.0  # Johnson 기준 검출
PX_PER_CYCLE = 2.0
DT = 0.01
FLIES = 200
SECONDS = 10.0


def focal_px(fov_v_deg: float, height_px: int) -> float:
    return (height_px / 2) / math.tan(math.radians(fov_v_deg) / 2)


def size_px(depth: float, f: float) -> float:
    return f * BODY_LENGTH / depth


def p_detect(s_px: float) -> float:
    """TTPF: P = r^E / (1 + r^E), r = N / N50, E = 2.7 + 0.7 r."""
    r = (s_px / PX_PER_CYCLE) / N50_CYCLES
    e = 2.7 + 0.7 * r
    return r**e / (1 + r**e)


def main() -> None:
    cfg = EnvConfig()
    room, turret = cfg.room, np.asarray(cfg.turret_pos)
    f = focal_px(cfg.camera.fov_v_deg, HEIGHT_PX)
    z50 = f * BODY_LENGTH / (N50_CYCLES * PX_PER_CYCLE)
    corners = np.array([[x, y, z] for x in (room.lo[0], room.hi[0]) for y in (room.lo[1], room.hi[1]) for z in (room.lo[2], room.hi[2])])
    far = float(np.max(np.linalg.norm(corners - turret, axis=1)))

    print(f"focal length: {f:.1f} px (image {HEIGHT_PX * cfg.camera.aspect:.0f} x {HEIGHT_PX})")
    print(f"50% detection depth: {z50:.2f} m  (size {N50_CYCLES * PX_PER_CYCLE:.1f} px)")
    print(f"farthest room corner from the turret: {far:.2f} m")
    print()
    print("depth m | size px | P(detect)")
    for z in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, round(far, 2)):
        s = size_px(z, f)
        print(f"{z:7.2f} | {s:7.2f} | {p_detect(s):.3f}")

    dists = []
    for seed in range(FLIES):
        rng = np.random.default_rng(seed)
        fly = Fly(FlyParams(), rng)
        pos = room.sample(rng, margin=0.4)
        for _ in range(100):
            if np.linalg.norm(pos - turret) >= cfg.min_start_distance:
                break
            pos = room.sample(rng, margin=0.4)
        fly.reset(pos, np.array([rng.normal(), 0.0, rng.normal()]))
        for _ in range(int(SECONDS / DT)):
            fly.step(DT, room, turret)
            dists.append(float(np.linalg.norm(fly.pos - turret)))
    d = np.array(dists)
    p = np.array([p_detect(size_px(x, f)) for x in d])
    print()
    print(f"fly distance from the turret ({FLIES} flies x {SECONDS:.0f} s): median {np.median(d):.2f} m, 90th percentile {np.percentile(d, 90):.2f} m")
    for lim in (1.0, 2.0, z50, 3.0):
        print(f"  time farther than {lim:.2f} m: {np.mean(d > lim) * 100:.1f}%")
    print(f"mean per-frame detection probability when aimed at the fly: {p.mean():.3f}")


if __name__ == "__main__":
    main()
