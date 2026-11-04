import math

import numpy as np
import pytest

from flytracker.aimer import Aimer, AimerLimits
from flytracker.world import Room

ROOM = Room()
DT = 0.01


def forward_action():
    return np.array([1.0, 0.0, 0.0, 0.0, 0.0])


def test_forward_moves_toward_minus_z_at_yaw_zero_and_respects_limits():
    lim = AimerLimits()
    aimer = Aimer(lim)
    aimer.reset(np.array([0.0, 1.0, 1.0]), yaw=0.0)
    aimer.step(forward_action(), DT, ROOM)
    assert np.linalg.norm(aimer.vel) == pytest.approx(lim.max_accel * DT)  # 첫 step 은 가속도 제한
    for _ in range(200):
        aimer.reset(np.array([0.0, 1.0, 1.0]), yaw=0.0) if aimer.pos[2] < -1.0 else None
        aimer.step(forward_action(), DT, ROOM)
    assert aimer.vel[2] < 0
    assert np.linalg.norm(aimer.vel) <= lim.max_speed + 1e-9


def test_positive_yaw_rate_increases_yaw():
    aimer = Aimer(AimerLimits())
    aimer.reset(np.array([0.0, 1.0, 0.0]), yaw=0.0)
    for _ in range(20):
        aimer.step(np.array([0.0, 0.0, 0.0, 1.0, 0.0]), DT, ROOM)
    assert aimer.yaw > 0


def test_pitch_is_clamped():
    lim = AimerLimits(max_pitch_deg=80.0)
    aimer = Aimer(lim)
    aimer.reset(np.array([0.0, 1.0, 0.0]), yaw=0.0)
    for _ in range(300):
        aimer.step(np.array([0.0, 0.0, 0.0, 0.0, 1.0]), DT, ROOM)
    assert aimer.pitch == pytest.approx(math.radians(80.0))


def test_wall_stops_aimer_and_reports_collision():
    lim = AimerLimits()
    aimer = Aimer(lim)
    aimer.reset(np.array([0.0, 1.0, -ROOM.depth / 2 + 0.15]), yaw=0.0)  # −z 벽 바로 앞
    collided = False
    for _ in range(100):
        collided |= aimer.step(forward_action(), DT, ROOM)
    assert collided
    assert ROOM.contains(aimer.pos, margin=lim.radius - 1e-9)


def test_fixed_aimer_only_rotates():
    aimer = Aimer(AimerLimits(can_move=False))
    start = np.array([0.0, 1.0, 0.0])
    aimer.reset(start, yaw=0.0)
    for _ in range(50):
        aimer.step(np.ones(5), DT, ROOM)
    assert np.allclose(aimer.pos, start)
    assert aimer.yaw != 0.0
