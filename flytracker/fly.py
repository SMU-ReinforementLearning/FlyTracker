"""초파리. 규칙대로 움직이는 상대다.

비행은 실제 초파리 자유비행 측정값을 따른다. 값마다 출처는 FlyParams 주석과
docs/issues/feature/9-feature-fly-realism-search/fly-flight-and-search-model.md 에 있다.

- 직선 구간과 급선회(body saccade)를 번갈아 한다. 직선 구간 길이는 거듭제곱 분포를 따라
  짧은 구간이 자주, 긴 구간이 드물게 나온다(Reynolds & Frye 2007).
- 짧은 구간은 느리고 긴 구간은 빠르다. 급선회하는 동안 속도가 잠깐 떨어졌다가 다시 오른다.
- 급선회는 평균 93°를 평균 49ms 동안 돈다(Muijres et al. 2015). 같은 방향으로 여러 번 연달아 돈다.

행동은 평시와 비상시 두 가지 상태를 오간다.
- 평시: 위 규칙대로 난다. 벽이 가까우면 방 안쪽으로 급선회한다.
- 비상시: 위협을 느낀 때부터 반응 지연 뒤 위협 반대쪽으로 빠르게 선회하고 잠깐 빨라졌다가 평시로 돌아간다.

위협은 초파리가 감각으로 알 수 있는 것만 센다. 조준기와의 거리가 빠르게 줄거나(줄어드는 속도 / 거리,
곧 겉보기 크기가 커지는 빠르기가 문턱을 넘음) 아주 가까우면 위협으로 느낀다. 조준기는 고정 포대라서
거리는 초파리가 조준기 쪽으로 날아갈 때만 준다. 조준선이 자기를 겨누는지는 초파리가 알 수 없으므로 세지 않는다.

초파리는 거의 모든 방향을 본다고 두어서 조준기 위치를 늘 안다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .geometry import rotate_about_y, slerp, unit
from .world import Room


@dataclass(frozen=True)
class FlyParams:
    # 직선 구간(급선회 사이) 길이. p(l) ∝ l^-지수, [최소, 최대] 에서 자른다.
    # Reynolds & Frye 2007: 10~100mm 에서 기울기 −1.3. 평균 약 0.21m 가 된다.
    segment_exponent: float = 1.3
    segment_min: float = 0.01  # m
    segment_max: float = 2.0  # m
    # 구간 속도. Reynolds & Frye 2007: 30mm 보다 짧은 구간 285mm/s, 긴 구간 356mm/s, 표준편차 약 190mm/s
    short_segment: float = 0.03  # m
    speed_short: float = 0.285  # m/s
    speed_long: float = 0.356  # m/s
    speed_sd: float = 0.19  # m/s
    speed_min: float = 0.05  # m/s
    speed_max: float = 1.0  # m/s
    speed_tau: float = 0.1  # s. 새 구간 속도로 다가가는 시간 상수 (가정)
    saccade_speed_dip: float = 0.25  # 급선회하는 동안 속도를 이 비율만큼 줄인다 (가정. Muijres 2015 는 "잠깐 떨어짐"만 보고)
    # 급선회. Muijres et al. 2015 (D. hydei, N=44): 93 ± 27°, 20~180°, 49 ± 18ms
    saccade_mean_deg: float = 93.0
    saccade_sd_deg: float = 27.0
    saccade_min_deg: float = 20.0
    saccade_max_deg: float = 180.0
    saccade_duration_mean: float = 0.049  # s
    saccade_duration_sd: float = 0.018  # s
    saccade_duration_min: float = 0.02  # s
    turn_persistence: float = 0.8  # 직전 급선회와 같은 방향으로 돌 확률 (가정. Reynolds & Frye 2007: 4번 넘게 같은 방향)
    climb_sd: float = 0.2  # 급선회 뒤 진행 방향 y 성분에 더하는 잡음 (가정)
    max_climb: float = 0.4  # 진행 방향의 y 성분 상한 (가정)
    wall_lookahead: float = 0.3  # m
    wall_margin: float = 0.15  # m
    # 위협과 회피
    evade_radius: float = 1.0  # m. 이 거리 안에서만 다가옴을 위협으로 느낀다 (가정)
    evade_looming_rate: float = 1.0  # 1/s. 줄어드는 속도 / 거리가 이 값을 넘으면 위협 (가정)
    evade_proximity: float = 0.35  # m. 이보다 가까우면 줄어드는 속도와 관계없이 위협 (가정)
    evade_reaction: float = 0.06  # s. 시각 위협에서 회피까지의 감각-운동 지연 약 60ms (Muijres 2014 를 인용한 2차 자료)
    escape_turn_duration: float = 0.025  # s. 회피 선회. 기울였다 되돌리기까지 약 25ms (Muijres 2014 를 인용한 2차 자료)
    evade_cooldown: float = 0.4  # s (가정)
    evade_speed_gain: float = 1.6  # 회피 직후 속도 배율 (가정)
    evade_boost_time: float = 0.3  # s (가정)

    @classmethod
    def hovering(cls) -> "FlyParams":
        """제자리에 떠 있는 초파리. 테스트에서 쓴다."""
        return cls(speed_short=0.0, speed_long=0.0, speed_sd=0.0, speed_min=0.0)


class Fly:
    def __init__(self, params: FlyParams, rng: np.random.Generator):
        self.p = params
        self.rng = rng
        self.pos = np.zeros(3)
        self.heading = np.array([0.0, 0.0, -1.0])
        self.speed = 0.0
        self._target_speed = 0.0
        self._segment_left = 0.0  # 다음 급선회까지 남은 거리 (m)
        self._turn_sign = 1.0
        self._turn: tuple[np.ndarray, np.ndarray, float, float] | None = None  # 시작, 목표, 지난 시간, 길이
        self._react_in: float | None = None
        self._cooldown = 0.0
        self._boost_left = 0.0
        self._prev_aimer_dist: float | None = None

    @property
    def alarmed(self) -> bool:
        """비상시면 True. 위협을 느낀 때부터 반응 지연과 회피 가속이 끝날 때까지다."""
        return self._react_in is not None or self._boost_left > 0.0

    @property
    def turning(self) -> bool:
        return self._turn is not None

    def reset(self, pos: np.ndarray, heading: np.ndarray) -> None:
        self.pos = np.asarray(pos, dtype=float).copy()
        self.heading = self._limit_climb(unit(np.asarray(heading, dtype=float)))
        self._turn = None
        self._turn_sign = 1.0 if self.rng.random() < 0.5 else -1.0
        self._new_segment()
        self.speed = self._target_speed
        self._react_in = None
        self._cooldown = 0.0
        self._boost_left = 0.0
        self._prev_aimer_dist = None

    def step(self, dt: float, room: Room, aimer_pos: np.ndarray) -> None:
        p = self.p
        self._cooldown = max(0.0, self._cooldown - dt)
        self._boost_left = max(0.0, self._boost_left - dt)
        self._update_threat(dt, room, aimer_pos)

        if self._turn is None:
            ahead = self.pos + self.heading * p.wall_lookahead
            if not room.contains(ahead, margin=p.wall_margin):
                self._start_turn(self._toward_inside(room), self._saccade_duration())
            elif self._segment_left <= 0.0:
                self._start_turn(self._random_saccade(), self._saccade_duration())

        target = self._target_speed
        if self._turn is not None:
            start, goal, elapsed, duration = self._turn
            elapsed += dt
            x = min(elapsed / duration, 1.0)
            s = x - math.sin(2 * math.pi * x) / (2 * math.pi)  # 각속도가 가운데에서 가장 빠른 종 모양 (최대 = 평균의 2배)
            self.heading = slerp(start, goal, s)
            self._turn = None if x >= 1.0 else (start, goal, elapsed, duration)
            target *= 1.0 - p.saccade_speed_dip
        self.speed += (target - self.speed) * min(dt / p.speed_tau, 1.0)

        speed = self.speed * (p.evade_speed_gain if self._boost_left > 0.0 else 1.0)
        new_pos = self.pos + self.heading * speed * dt
        self.pos, hit = room.clamp(new_pos, margin=0.02)
        if self._turn is None:  # 직선 구간 길이는 급선회 사이에서만 센다
            self._segment_left -= speed * dt
        if hit.any():  # 안전장치. 벽 회피가 늦었으면 부딪힌 축의 방향을 뒤집는다
            self.heading = unit(np.where(hit, -self.heading, self.heading))

    # 내부 규칙

    def _new_segment(self) -> None:
        """다음 직선 구간의 길이와 속도를 고른다."""
        p = self.p
        a = 1.0 - p.segment_exponent
        u = self.rng.random()
        length = (p.segment_min**a + u * (p.segment_max**a - p.segment_min**a)) ** (1.0 / a)
        mean = p.speed_short if length < p.short_segment else p.speed_long
        self._segment_left = length
        self._target_speed = float(np.clip(self.rng.normal(mean, p.speed_sd), p.speed_min, p.speed_max))

    def _saccade_duration(self) -> float:
        p = self.p
        return max(p.saccade_duration_min, float(self.rng.normal(p.saccade_duration_mean, p.saccade_duration_sd)))

    def _limit_climb(self, d: np.ndarray) -> np.ndarray:
        c = self.p.max_climb
        if abs(d[1]) <= c:
            return d
        horiz = np.array([d[0], 0.0, d[2]])
        if not horiz.any():
            horiz = np.array([1.0, 0.0, 0.0])
        horiz = unit(horiz) * math.sqrt(1 - c * c)
        return unit(horiz + np.array([0.0, math.copysign(c, d[1]), 0.0]))

    def _start_turn(self, target: np.ndarray, duration: float) -> None:
        self._turn = (self.heading.copy(), self._limit_climb(unit(target)), 0.0, duration)
        self._new_segment()

    def _random_saccade(self) -> np.ndarray:
        p = self.p
        if self.rng.random() >= p.turn_persistence:
            self._turn_sign = -self._turn_sign
        deg = float(np.clip(self.rng.normal(p.saccade_mean_deg, p.saccade_sd_deg), p.saccade_min_deg, p.saccade_max_deg))
        d = rotate_about_y(self.heading, self._turn_sign * math.radians(deg))
        d[1] = d[1] + self.rng.normal(0.0, p.climb_sd)
        return unit(d)

    def _toward_inside(self, room: Room) -> np.ndarray:
        inner = room.center + self.rng.uniform(-0.5, 0.5, size=3) * room.size / 2
        return unit(inner - self.pos)

    def _update_threat(self, dt: float, room: Room, aimer_pos: np.ndarray) -> None:
        p = self.p
        dist = float(np.linalg.norm(self.pos - aimer_pos))
        prev = self._prev_aimer_dist
        self._prev_aimer_dist = dist
        if self._react_in is not None:
            self._react_in -= dt
            if self._react_in <= 0.0:
                self._react_in = None
                self._start_turn(self._escape_dir(room, aimer_pos), p.escape_turn_duration)
                self._boost_left = p.evade_boost_time
                self._cooldown = p.evade_cooldown
            return
        if prev is None or self._cooldown > 0.0:
            return
        closing = (prev - dist) / dt
        looming = dist < p.evade_radius and closing / max(dist, 1e-6) > p.evade_looming_rate
        if looming or dist < p.evade_proximity:
            self._react_in = p.evade_reaction

    def _escape_dir(self, room: Room, aimer_pos: np.ndarray) -> np.ndarray:
        away = unit(self.pos - aimer_pos)
        perp = np.cross(away, self.rng.normal(size=3))
        perp = unit(perp) if np.linalg.norm(perp) > 1e-6 else unit(np.cross(away, [0.0, 1.0, 0.0]))
        for candidate in (perp, -perp):
            d = self._limit_climb(unit(candidate + 0.5 * away))
            if room.contains(self.pos + d * self.p.wall_lookahead, margin=self.p.wall_margin):
                return d
        return self._limit_climb(away)
