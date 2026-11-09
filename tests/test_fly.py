import numpy as np

from flytracker.fly import Fly, FlyParams
from flytracker.world import Room

DT = 0.01
HOVER = FlyParams.hovering()


def hovering_fly(pos=(0.0, 1.2, 0.0)) -> Fly:
    fly = Fly(HOVER, np.random.default_rng(0))
    fly.reset(np.array(pos), np.array([0.0, 0.0, -1.0]))
    return fly


def test_still_aimer_inside_threat_radius_does_not_alarm():
    """조준기가 0.8m 앞에 가만히 있으면 초파리는 위협을 느끼지 않는다. 조준선 방향은 초파리가 모른다."""
    room, fly = Room(), hovering_fly()
    aimer = fly.pos + np.array([0.0, 0.0, 0.8])
    for _ in range(100):
        fly.step(DT, room, aimer)
        assert not fly.alarmed


def test_fast_approach_alarms_then_returns_to_normal():
    room, fly = Room(), hovering_fly()
    p = fly.p
    aimer = fly.pos + np.array([0.0, 0.0, 0.9])
    fly.step(DT, room, aimer)
    aimer = aimer - np.array([0.0, 0.0, 1.5 * DT])  # 1.5 m/s 로 다가온다. 1.5 / 0.885 > 1/s
    fly.step(DT, room, aimer)
    assert fly.alarmed
    for _ in range(int((p.evade_reaction + p.evade_boost_time) / DT) + 2):
        fly.step(DT, room, aimer)  # 조준기는 멈췄고 0.35m 보다 멀다
    assert not fly.alarmed


def test_very_close_aimer_alarms():
    room, fly = Room(), hovering_fly()
    aimer = fly.pos + np.array([0.0, 0.0, 0.3])
    fly.step(DT, room, aimer)
    fly.step(DT, room, aimer)
    assert fly.alarmed
