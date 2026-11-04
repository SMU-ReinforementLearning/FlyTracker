"""규칙 기반 조준기. RL 결과를 견줄 기준선이다.

관측 벡터만 보고 움직인다. 환경 내부 상태(파리의 실제 위치)는 보지 않는다.
- 보이면: 화면 좌표(u, v)에 비례해 조준선을 돌리고, 가운데에 잡히면 바라보는 방향으로 다가간다.
- 놓쳤으면: 마지막으로 본 방향으로 돈다.
- 본 적이 없으면: 수평을 맞추고 제자리에서 돌며 찾는다.
"""

from __future__ import annotations

import math

import numpy as np

from .aimer import ACTION_DIM
from .env import OBS


class RuleAimer:
    def __init__(
        self,
        turn_gain: float = 2.5,
        center_tol: float = 0.3,
        approach_gain: float = 1.5,
        scan_rate: float = 0.7,
        max_pitch_deg: float = 80.0,
        can_move: bool = True,
    ):
        self.turn_gain = turn_gain
        self.center_tol = center_tol
        self.approach_gain = approach_gain
        self.scan_rate = scan_rate
        self.max_pitch = math.radians(max_pitch_deg)
        self.can_move = can_move

    def predict(self, obs, state=None, episode_start=None, deterministic: bool = True):
        """Stable-Baselines3 모델과 같은 모양으로 부를 수 있게 한다."""
        return self.act(obs), state

    def act(self, obs) -> np.ndarray:
        o = np.asarray(obs, dtype=float)
        if o.ndim == 2:  # frame stack 이면 가장 최근 관측만 쓴다
            o = o[-1]
        a = np.zeros(ACTION_DIM, dtype=np.float32)
        k = self.turn_gain
        pitch = float(o[OBS["pitch"]][0]) * self.max_pitch

        if o[OBS["visible"]][0] > 0.5:
            u, v = o[OBS["uv"]]
            a[3] = np.clip(-k * u, -1, 1)  # 파리가 오른쪽(u > 0)이면 yaw 를 줄여 오른쪽으로 돈다
            a[4] = np.clip(k * v, -1, 1)
            closeness = float(o[OBS["closeness"]][0])
            centered = abs(u) < self.center_tol and abs(v) < self.center_tol
            if self.can_move and centered:
                speed = float(np.clip(self.approach_gain * (1.0 - closeness) + 0.3, -0.5, 1.0))
                a[0] = speed * math.cos(pitch)
                a[2] = speed * math.sin(pitch)
            return a

        last = o[OBS["last_seen_dir"]]
        if np.any(last != 0):
            dr, du, df = last
            a[3] = np.clip(-k * math.atan2(dr, df) / (math.pi / 2), -1, 1)
            a[4] = np.clip(k * du, -1, 1)
            return a

        a[3] = self.scan_rate
        a[4] = np.clip(-k * pitch / self.max_pitch, -1, 1)
        return a
