"""조준기. 방공포처럼 정해진 자리에서 조준 방향만 돌리는 카메라이며, 학습하는 agent 다."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .geometry import approach, look_dir, wrap_angle

ACTION_NAMES = ("yaw_rate", "pitch_rate")
ACTION_DIM = len(ACTION_NAMES)


@dataclass(frozen=True)
class AimerLimits:
    max_yaw_rate_deg: float = 180.0  # 도/s
    max_pitch_rate_deg: float = 120.0  # 도/s
    max_ang_accel_deg: float = 720.0  # 도/s²
    # 위아래로 볼 수 있는 한계 (도). 90° 에서는 카메라 방향 계산이 퇴화한다(camera_basis).
    # 89° 면 바로 위의 초파리도 포획 각도(3°) 안에 든다. 80° 였을 때는 올려다보는 각이 83° 를 넘는 곳을 포획하지 못했다.
    max_pitch_deg: float = 89.0


class Aimer:
    """고정 포대. 자리는 reset 때 정하고 그 뒤로 움직이지 않는다.

    행동은 −1~1 범위의 2차원 벡터다.
    0 yaw_rate: + 이면 왼쪽(위에서 볼 때 반시계)으로 돈다.
    1 pitch_rate: + 이면 위를 본다.
    실제 각속도는 각가속도 제한 안에서 목표값을 따라간다.
    """

    def __init__(self, limits: AimerLimits):
        self.limits = limits
        self.pos = np.zeros(3)
        self.yaw = 0.0
        self.pitch = 0.0
        self.yaw_rate = 0.0
        self.pitch_rate = 0.0

    def reset(self, pos: np.ndarray, yaw: float, pitch: float = 0.0) -> None:
        self.pos = np.asarray(pos, dtype=float).copy()
        self.yaw = wrap_angle(yaw)
        self.pitch = pitch
        self.yaw_rate = 0.0
        self.pitch_rate = 0.0

    @property
    def look(self) -> np.ndarray:
        return look_dir(self.yaw, self.pitch)

    def step(self, action: np.ndarray, dt: float) -> None:
        """한 물리 step 동안 조준 방향을 돌린다."""
        lim = self.limits
        a = np.clip(np.asarray(action, dtype=float), -1.0, 1.0)

        max_ang_dv = math.radians(lim.max_ang_accel_deg) * dt
        self.yaw_rate = approach(self.yaw_rate, a[0] * math.radians(lim.max_yaw_rate_deg), max_ang_dv)
        self.pitch_rate = approach(self.pitch_rate, a[1] * math.radians(lim.max_pitch_rate_deg), max_ang_dv)
        self.yaw = wrap_angle(self.yaw + self.yaw_rate * dt)
        max_pitch = math.radians(lim.max_pitch_deg)
        pitch = self.pitch + self.pitch_rate * dt
        if abs(pitch) > max_pitch:
            pitch = math.copysign(max_pitch, pitch)
            self.pitch_rate = 0.0
        self.pitch = pitch
