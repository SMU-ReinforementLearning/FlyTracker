"""현재 환경 계약을 시험하기 위한 공통 조준 fixture."""

import math

import numpy as np
import pytest


@pytest.fixture
def track_neural_fly_on_beam(monkeypatch):
    """시간 순서 시험만을 위한 완전 추적. 학습 정책의 포획 성능이 아니다.

    실제 신경 초파리는 그대로 비행한다. 5ms 신체 갱신 뒤 조준 방향만
    정답 위치로 맞춰 1.25mm 빔 안의 연속 명중을 통제한다.
    """
    def install(env):
        def point_at_fly(action, dt):
            direction = env.fly.pos - env.aimer.pos
            direction /= np.linalg.norm(direction)
            env.aimer.reset(env.aimer.pos, math.atan2(-direction[0], -direction[2]),
                            math.asin(float(np.clip(direction[1], -1., 1.))))
        monkeypatch.setattr(env.aimer, "step", point_at_fly)
    return install
