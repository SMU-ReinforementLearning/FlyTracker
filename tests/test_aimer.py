import math

import numpy as np
import pytest

from flytracker.aimer import ACTION_DIM, Aimer, AimerLimits

DT = 0.01
START = np.array([0.0, 1.2, 1.4])


def test_action_is_yaw_and_pitch_only():
    assert ACTION_DIM == 2


def test_positive_yaw_rate_increases_yaw_within_accel_limit():
    lim = AimerLimits()
    aimer = Aimer(lim)
    aimer.reset(START, yaw=0.0)
    aimer.step(np.array([1.0, 0.0]), DT)
    assert aimer.yaw_rate == pytest.approx(math.radians(lim.max_ang_accel_deg) * DT)  # 첫 step 은 각가속도 제한
    for _ in range(20):
        aimer.step(np.array([1.0, 0.0]), DT)
    assert aimer.yaw > 0


def test_pitch_is_clamped():
    aimer = Aimer(AimerLimits(max_pitch_deg=80.0))
    aimer.reset(START, yaw=0.0)
    for _ in range(300):
        aimer.step(np.array([0.0, 1.0]), DT)
    assert aimer.pitch == pytest.approx(math.radians(80.0))


def test_turret_never_moves():
    aimer = Aimer(AimerLimits())
    aimer.reset(START, yaw=0.0)
    rng = np.random.default_rng(0)
    for _ in range(200):
        aimer.step(rng.uniform(-1, 1, ACTION_DIM), DT)
    assert np.array_equal(aimer.pos, START)
    assert aimer.yaw != 0.0
