"""조준기. 방 안을 움직이고 회전하는 카메라 개체이며, 학습하는 agent 다."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .geometry import approach, horizontal_basis, look_dir, wrap_angle
from .world import UP, Room

ACTION_NAMES = ("forward", "right", "up", "yaw_rate", "pitch_rate")
ACTION_DIM = len(ACTION_NAMES)


@dataclass(frozen=True)
class AimerLimits:
    max_speed: float = 1.5  # m/s
    max_accel: float = 4.0  # m/s²
    max_yaw_rate_deg: float = 180.0  # 도/s
    max_pitch_rate_deg: float = 120.0  # 도/s
    max_ang_accel_deg: float = 720.0  # 도/s²
    max_pitch_deg: float = 80.0  # 위아래로 볼 수 있는 한계 (도)
    radius: float = 0.1  # 벽과 떨어져야 하는 거리 (m)
    can_move: bool = True  # False 면 제자리에서 회전만 한다


class Aimer:
    """행동은 −1~1 범위의 5차원 벡터다.

    0 forward, 1 right, 2 up: 이동 목표 속도. 앞과 오른쪽은 yaw 만 반영한 수평 방향이고 위는 +y 다.
    3 yaw_rate: + 이면 왼쪽(위에서 볼 때 반시계)으로 돈다.
    4 pitch_rate: + 이면 위를 본다.
    실제 속도와 각속도는 가속도 제한 안에서 목표값을 따라간다.
    """

    def __init__(self, limits: AimerLimits):
        self.limits = limits
        self.pos = np.zeros(3)
        self.vel = np.zeros(3)
        self.yaw = 0.0
        self.pitch = 0.0
        self.yaw_rate = 0.0
        self.pitch_rate = 0.0

    def reset(self, pos: np.ndarray, yaw: float, pitch: float = 0.0) -> None:
        self.pos = np.asarray(pos, dtype=float).copy()
        self.vel = np.zeros(3)
        self.yaw = wrap_angle(yaw)
        self.pitch = pitch
        self.yaw_rate = 0.0
        self.pitch_rate = 0.0

    @property
    def look(self) -> np.ndarray:
        return look_dir(self.yaw, self.pitch)

    def step(self, action: np.ndarray, dt: float, room: Room) -> bool:
        """한 물리 step 을 진행하고 벽에 부딪혔는지 돌려준다."""
        lim = self.limits
        a = np.clip(np.asarray(action, dtype=float), -1.0, 1.0)

        max_ang_dv = math.radians(lim.max_ang_accel_deg) * dt
        self.yaw_rate = approach(self.yaw_rate, a[3] * math.radians(lim.max_yaw_rate_deg), max_ang_dv)
        self.pitch_rate = approach(self.pitch_rate, a[4] * math.radians(lim.max_pitch_rate_deg), max_ang_dv)
        self.yaw = wrap_angle(self.yaw + self.yaw_rate * dt)
        max_pitch = math.radians(lim.max_pitch_deg)
        pitch = self.pitch + self.pitch_rate * dt
        if abs(pitch) > max_pitch:
            pitch = math.copysign(max_pitch, pitch)
            self.pitch_rate = 0.0
        self.pitch = pitch

        if not lim.can_move:
            self.vel[:] = 0.0
            return False

        forward, right = horizontal_basis(self.yaw)
        target_v = (a[0] * forward + a[1] * right + a[2] * UP) * lim.max_speed
        speed = float(np.linalg.norm(target_v))
        if speed > lim.max_speed:
            target_v *= lim.max_speed / speed
        dv = target_v - self.vel
        dv_norm = float(np.linalg.norm(dv))
        max_dv = lim.max_accel * dt
        if dv_norm > max_dv:
            dv *= max_dv / dv_norm
        self.vel = self.vel + dv
        self.pos, hit = room.clamp(self.pos + self.vel * dt, margin=lim.radius)
        self.vel[hit] = 0.0
        return bool(hit.any())
