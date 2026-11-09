"""초파리 모델의 비행 통계를 재서 문헌값과 견준다.

    uv run python docs/issues/feature/9-feature-fly-realism-search/fly_stats.py

조준기를 방 밖 멀리 두어 위협이 없는 평시 비행만 잰다. 기본 방(4 × 2.5 × 3m)에서
초파리 200마리를 10초씩 날리고, 물리 step 은 환경과 같은 10ms 다.
"""

from __future__ import annotations

import math

import numpy as np

from flytracker.fly import Fly, FlyParams
from flytracker.world import Room

DT = 0.01
FLIES = 200
SECONDS = 10.0
FAR = np.array([100.0, 100.0, 100.0])  # 위협이 생기지 않는 조준기 자리


def horizontal_angle(a: np.ndarray, b: np.ndarray) -> float:
    """두 방향의 수평 방위 차이 (도, 부호 있음)."""
    return math.degrees(math.atan2(a[0] * b[2] - a[2] * b[0], a[0] * b[0] + a[2] * b[2]))


def main() -> None:
    room, params = Room(), FlyParams()
    speeds, amplitudes, durations, peaks, gaps, runs = [], [], [], [], [], []
    saccades, total_time = 0, 0.0
    for seed in range(FLIES):
        rng = np.random.default_rng(seed)
        fly = Fly(params, rng)
        fly.reset(room.sample(rng, margin=0.4), np.array([rng.normal(), 0.0, rng.normal()]))
        was_turning, turn_start, turn_t, peak = False, None, 0.0, 0.0
        last_end_pos, last_sign, run = None, 0, 0
        prev_heading = fly.heading.copy()
        for _ in range(int(SECONDS / DT)):
            fly.step(DT, room, FAR)
            speeds.append(fly.speed)
            rate = abs(horizontal_angle(prev_heading, fly.heading)) / DT
            prev_heading = fly.heading.copy()
            if fly.turning and not was_turning:
                turn_start, turn_t, peak = fly._turn[0].copy(), 0.0, 0.0
                if last_end_pos is not None:
                    gaps.append(float(np.linalg.norm(fly.pos - last_end_pos)))
            if fly.turning or was_turning:
                turn_t += DT
                peak = max(peak, rate)
            if was_turning and not fly.turning:
                amp = horizontal_angle(turn_start, fly.heading)
                amplitudes.append(abs(amp))
                durations.append(turn_t)
                peaks.append(peak)
                saccades += 1
                sign = 1 if amp > 0 else -1
                if sign == last_sign:
                    run += 1
                else:
                    if run:
                        runs.append(run)
                    run, last_sign = 1, sign
                last_end_pos = fly.pos.copy()
            was_turning = fly.turning
        if run:
            runs.append(run)
        total_time += SECONDS

    s, a, d, pk, g = map(np.asarray, (speeds, amplitudes, durations, peaks, gaps))
    print(f"초파리 {FLIES}마리 × {SECONDS:.0f}초, 급선회 {saccades}번 (벽 회피 포함)")
    print(f"속도: 평균 {s.mean():.3f} m/s, 표준편차 {s.std():.3f}, 95% 구간 {np.percentile(s, 2.5):.2f}~{np.percentile(s, 97.5):.2f}")
    print(f"급선회 빈도: {saccades / total_time:.2f} /s")
    print(f"급선회 각도: 평균 {a.mean():.0f}°, 표준편차 {a.std():.0f}°, 범위 {a.min():.0f}~{a.max():.0f}°")
    print(f"급선회 시간: 평균 {d.mean() * 1000:.0f} ms, 표준편차 {d.std() * 1000:.0f} ms")
    print(f"최대 각속도: 중앙값 {np.median(pk):.0f}°/s, 95% 구간 {np.percentile(pk, 2.5):.0f}~{np.percentile(pk, 97.5):.0f}°/s")
    print(f"같은 방향 연속 급선회: 평균 {np.mean(runs):.1f}번, 4번 이상인 묶음 {np.mean(np.asarray(runs) >= 4):.0%}")
    bins = np.logspace(math.log10(0.01), math.log10(0.1), 8)
    hist, edges = np.histogram(g, bins=bins, density=True)
    centers = np.sqrt(edges[:-1] * edges[1:])
    ok = hist > 0
    slope = np.polyfit(np.log10(centers[ok]), np.log10(hist[ok]), 1)[0]
    print(f"급선회 사이 거리: 평균 {g.mean():.3f} m, 중앙값 {np.median(g):.3f} m, 10~100mm 로그 기울기 {slope:.2f}")


if __name__ == "__main__":
    main()
