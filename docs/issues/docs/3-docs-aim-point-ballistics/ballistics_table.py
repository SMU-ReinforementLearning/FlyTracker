"""aim-point-and-projectile-speed.md 의 표를 다시 만드는 계산.

    uv run python docs/issues/docs/3-docs-aim-point-ballistics/ballistics_table.py

투사체는 공 모양으로 두고, 공기저항은 속도 제곱에 비례한다고 놓는다.
가속도 a = -(|v| / L) v - g (y 방향). L 은 공기저항만 받을 때 속도가 1/e 로 줄어드는 거리다.
수평으로 쏜다고 놓고 목표 거리까지 0.01 ms 간격으로 적분한다.
"""

from __future__ import annotations

import math

G = 9.81  # m/s²
RHO_AIR = 1.2  # kg/m³


def decay_length(density: float, diameter: float, cd: float) -> float:
    """L = (4/3) × (투사체 밀도 / 공기 밀도) × (지름 / C_d)."""
    return 4 / 3 * (density / RHO_AIR) * (diameter / cd)


def fly_to(v0: float, length: float, distance: float, dt: float = 1e-5) -> tuple[float, float, float]:
    """수평 거리 distance 까지의 (비행시간 s, 낙차 m, 도착 속도 m/s)."""
    x = y = t = 0.0
    vx, vy = v0, 0.0
    while x < distance:
        v = math.hypot(vx, vy)
        vx += -(v / length) * vx * dt
        vy += (-(v / length) * vy - G) * dt
        x += vx * dt
        y += vy * dt
        t += dt
    return t, -y, math.hypot(vx, vy)


def hit_probability(n: int, hit_area: float, radius: float) -> float:
    """알갱이 n 개가 반지름 radius 원에 고르게 퍼질 때 한 개 이상 맞을 확률."""
    return 1 - math.exp(-n * hit_area / (math.pi * radius**2))


def main() -> None:
    print("L (속도가 1/e 로 줄어드는 거리)")
    for name, density, diameter, cd in [
        ("소금 0.4 mm, C_d 0.5", 2160, 0.4e-3, 0.5),
        ("소금 0.4 mm, C_d 1.0", 2160, 0.4e-3, 1.0),
        ("물방울 1 mm", 1000, 1e-3, 0.47),
        ("BB탄 6 mm 0.2 g", 1770, 6e-3, 0.47),
    ]:
        print(f"  {name:22s} {decay_length(density, diameter, cd):6.2f} m")

    print("\n비행시간과 낙차 (수평 발사)")
    for name, v0, length in [
        ("소금 30 m/s", 30, 1.5),
        ("소금 50 m/s", 50, 1.5),
        ("소금 100 m/s", 100, 1.5),
        ("BB탄 100 m/s", 100, 25),
    ]:
        cells = []
        for d in (1.0, 2.0):
            t, drop, v_end = fly_to(v0, length, d)
            cells.append(f"{d:.0f} m: {t * 1000:4.0f} ms, 낙차 {drop * 100:4.1f} cm, 도착 {v_end:5.1f} m/s")
        print(f"  {name:16s} | " + " | ".join(cells))

    # 몸통 옆면 2.5 mm × 1 mm 를 알갱이 반지름 0.2 mm 만큼 사방으로 넓힌 넓이
    r = 0.2
    body = (2.5 + 2 * r) * (1 + 2 * r) - (4 - math.pi) * r**2
    print(f"\n몸통을 알갱이 반지름만큼 넓힌 넓이 {body:.1f} mm². 다리와 날개 일부를 더해 5 mm² 로 어림한다")
    print("명중 확률 (맞을 수 있는 넓이 5 mm²)")
    a = 5e-6
    for radius in (0.01, 0.03):
        n63 = math.pi * radius**2 / a
        n90 = n63 * math.log(10)
        print(f"  R {radius * 100:.0f} cm: 63% {n63:5.0f}개, 90% {n90:5.0f}개, 검산 P(n63)={hit_probability(round(n63), a, radius):.2f}")

    grain = 2160 * math.pi / 6 * (0.4e-3) ** 3
    print(f"\n소금 0.4 mm 한 알 {grain * 1e6:.3f} mg, 0.1 g 에 {1e-4 / grain:.0f}개")


if __name__ == "__main__":
    main()
