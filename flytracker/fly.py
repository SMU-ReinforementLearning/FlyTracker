"""초파리. 규칙대로 움직이는 상대다.

행동은 평시와 비상시 두 가지 상태를 오간다.
- 평시: 직선으로 날다가 무작위로 급선회(saccade)한다. 벽이 가까우면 방 안쪽으로 꺾는다.
- 비상시: 위협을 느낀 때부터 반응 지연 뒤 옆으로 급선회하고 잠깐 빨라졌다가 평시로 돌아간다.

위협은 초파리가 감각으로 알 수 있는 것만 센다. 조준기가 빠르게 다가오거나(접근 속도 / 거리,
곧 겉보기 크기가 커지는 빠르기가 문턱을 넘음) 아주 가까우면 위협으로 느낀다.
조준선이 자기를 겨누는지는 초파리가 알 수 없으므로 세지 않는다.

초파리는 거의 모든 방향을 본다고 두어서 조준기 위치를 늘 안다.
기본값은 출발점으로 잡은 값이다. 실제 초파리 비행 문헌값과 대조하지 않았다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .geometry import rotate_about_y, slerp, unit
from .world import Room


@dataclass(frozen=True)
class FlyParams:
    cruise_speed: float = 0.5  # m/s
    speed_jitter: float = 0.2  # 급선회마다 속도를 cruise × (1 ± jitter) 안에서 다시 고른다
    saccade_rate: float = 1.0  # 1초당 평균 급선회 횟수
    saccade_min_deg: float = 60.0
    saccade_max_deg: float = 120.0
    saccade_duration: float = 0.05  # s
    max_climb: float = 0.4  # 진행 방향의 y 성분 상한
    wall_lookahead: float = 0.3  # m
    wall_margin: float = 0.15  # m
    evade_radius: float = 1.0  # m. 이 거리 안에서만 다가옴을 위협으로 느낀다
    evade_looming_rate: float = 1.0  # 1/s. 접근 속도 / 거리가 이 값을 넘으면 위협
    evade_proximity: float = 0.35  # m. 이보다 가까우면 접근 속도와 관계없이 위협
    evade_reaction: float = 0.06  # s
    evade_cooldown: float = 0.4  # s
    evade_speed_gain: float = 1.6  # 회피 직후 속도 배율
    evade_boost_time: float = 0.3  # s


class Fly:
    def __init__(self, params: FlyParams, rng: np.random.Generator):
        self.p = params
        self.rng = rng
        self.pos = np.zeros(3)
        self.heading = np.array([0.0, 0.0, -1.0])
        self.speed = params.cruise_speed
        self._turn: tuple[np.ndarray, np.ndarray, float, float] | None = None  # 시작, 목표, 지난 시간, 길이
        self._react_in: float | None = None
        self._cooldown = 0.0
        self._boost_left = 0.0
        self._prev_aimer_dist: float | None = None

    @property
    def alarmed(self) -> bool:
        """비상시면 True. 위협을 느낀 때부터 반응 지연과 회피 가속이 끝날 때까지다."""
        return self._react_in is not None or self._boost_left > 0.0

    def reset(self, pos: np.ndarray, heading: np.ndarray) -> None:
        self.pos = np.asarray(pos, dtype=float).copy()
        self.heading = self._limit_climb(unit(np.asarray(heading, dtype=float)))
        self.speed = self._pick_speed()
        self._turn = None
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
                self._start_turn(self._toward_inside(room))
            elif self.rng.random() < p.saccade_rate * dt:
                self._start_turn(self._random_saccade())

        if self._turn is not None:
            start, target, elapsed, duration = self._turn
            elapsed += dt
            s = min(elapsed / duration, 1.0)
            self.heading = slerp(start, target, s)
            self._turn = None if s >= 1.0 else (start, target, elapsed, duration)

        speed = self.speed * (p.evade_speed_gain if self._boost_left > 0.0 else 1.0)
        new_pos = self.pos + self.heading * speed * dt
        self.pos, hit = room.clamp(new_pos, margin=0.02)
        if hit.any():  # 안전장치. 벽 회피가 늦었으면 부딪힌 축의 방향을 뒤집는다
            self.heading = unit(np.where(hit, -self.heading, self.heading))

    # 내부 규칙

    def _pick_speed(self) -> float:
        j = self.p.speed_jitter
        return self.p.cruise_speed * self.rng.uniform(1 - j, 1 + j)

    def _limit_climb(self, d: np.ndarray) -> np.ndarray:
        c = self.p.max_climb
        if abs(d[1]) <= c:
            return d
        horiz = np.array([d[0], 0.0, d[2]])
        if not horiz.any():
            horiz = np.array([1.0, 0.0, 0.0])
        horiz = unit(horiz) * math.sqrt(1 - c * c)
        return unit(horiz + np.array([0.0, math.copysign(c, d[1]), 0.0]))

    def _start_turn(self, target: np.ndarray) -> None:
        self._turn = (self.heading.copy(), self._limit_climb(unit(target)), 0.0, self.p.saccade_duration)
        self.speed = self._pick_speed()

    def _random_saccade(self) -> np.ndarray:
        p = self.p
        angle = math.radians(self.rng.uniform(p.saccade_min_deg, p.saccade_max_deg))
        angle *= 1 if self.rng.random() < 0.5 else -1
        d = rotate_about_y(self.heading, angle)
        d[1] = d[1] + self.rng.normal(0.0, 0.2)
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
                self._start_turn(self._escape_dir(room, aimer_pos))
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
