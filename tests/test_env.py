from dataclasses import replace

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from flytracker import OBS, OBS_DIM, EnvConfig, FlyChaseEnv, make_env
from flytracker.fly import FlyParams


def test_env_passes_gymnasium_checker():
    check_env(FlyChaseEnv(), skip_render_check=True)


def test_discrete_actions_drive_one_axis():
    env = make_env(action_mode="discrete")
    env.reset(seed=0)
    assert env.action_space.n == 5
    for a in range(env.action_space.n):
        obs, *_ = env.step(a)
        assert env.observation_space.contains(obs)


def test_same_seed_same_episode():
    def rollout():
        env = FlyChaseEnv(EnvConfig())
        obs, _ = env.reset(seed=123)
        rng = np.random.default_rng(0)
        seq = [obs]
        for _ in range(100):
            obs, *_ = env.step(rng.uniform(-1, 1, 2))
            seq.append(obs)
        return np.array(seq)

    assert np.array_equal(rollout(), rollout())


def static_fly_config(**kw) -> EnvConfig:
    fly = FlyParams.hovering()
    return replace(EnvConfig(fly=fly), **kw)


def test_holding_fly_in_center_captures():
    cfg = static_fly_config()
    env = FlyChaseEnv(cfg)
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos + env.aimer.look * 0.3  # 바로 앞 0.3m 에 둔다
    env._update_vision()
    total, steps, terminated = 0.0, 0, False
    while not terminated and steps < 100:
        _, r, terminated, truncated, info = env.step(np.zeros(2))
        total += r
        steps += 1
    assert terminated and info["captured"]
    expected_steps = round(cfg.capture_hold / (cfg.dt * cfg.frame_skip))
    assert steps == pytest.approx(expected_steps, abs=1)
    assert total > cfg.reward.capture - 1.0


def test_time_limit_truncates():
    env = FlyChaseEnv(replace(EnvConfig(), max_seconds=0.1))
    env.reset(seed=0)
    truncated = False
    for _ in range(5):
        _, _, terminated, truncated, _ = env.step(np.zeros(2))
    assert truncated and not terminated


def test_frame_stack_shape():
    env = make_env(frame_stack=4)
    obs, _ = env.reset(seed=0)
    assert obs.shape == (4, OBS_DIM)


def test_observation_hides_fly_when_out_of_view():
    env = FlyChaseEnv(static_fly_config())
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos - env.aimer.look * 1.0  # 바로 뒤
    env._update_vision()
    obs = env._observation()
    assert obs[OBS["visible"]][0] == 0.0
    assert np.all(obs[OBS["uv"]] == 0.0)


def test_turret_stays_at_configured_position():
    cfg = replace(EnvConfig(), turret_pos=(1.0, 0.8, -1.0))
    env = FlyChaseEnv(cfg)
    env.reset(seed=3)
    rng = np.random.default_rng(1)
    for _ in range(50):
        env.step(rng.uniform(-1, 1, 2))
        assert np.array_equal(env.aimer.pos, np.array(cfg.turret_pos))


def test_turret_outside_room_is_rejected():
    with pytest.raises(ValueError):
        FlyChaseEnv(replace(EnvConfig(), turret_pos=(0.0, 1.0, 5.0)))


def test_capture_range_none_captures_far_fly():
    cfg = static_fly_config()
    env = FlyChaseEnv(cfg)
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos + env.aimer.look * 2.5  # 2.5m 앞. 거리 조건이 없으면 잡힌다
    env._update_vision()
    terminated, steps = False, 0
    while not terminated and steps < 100:
        _, _, terminated, _, info = env.step(np.zeros(2))
        steps += 1
    assert info["captured"]


def test_fly_straight_above_turret_is_not_capturable():
    # pitch 는 89° 까지라 바로 위(90°)와는 1° 가 남는다. 1.9m 에서 빔과 33mm 떨어져 레이저 명중(1.25mm)이 되지 않는다.
    env = FlyChaseEnv(static_fly_config())
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos + np.array([0.0, 1.9, 0.0])  # 바로 위 1.9m. 위협 반경(1m) 밖이라 피하지 않는다
    env._update_vision()
    info = {"captured": False}
    for _ in range(150):  # 3초 동안 위로 돌린다
        _, _, terminated, _, info = env.step(np.array([0.0, 1.0]))
        if terminated:
            break
    assert info["captured"] is False
    assert info["beam_dist"] == pytest.approx(1.9 * np.sin(np.radians(1.0)), rel=0.02)


def _held_fly_env(offset_m: float = 0.0, distance: float = 2.0, **kw) -> FlyChaseEnv:
    """가만히 있는 초파리를 조준 방향에서 옆으로 offset_m 만큼 떨어뜨려 둔다."""
    env = FlyChaseEnv(static_fly_config(**kw))
    env.reset(seed=0)
    side = np.cross(env.aimer.look, np.array([0.0, 1.0, 0.0]))
    env.fly.pos = env.aimer.pos + env.aimer.look * distance + side / np.linalg.norm(side) * offset_m
    env._capture_timer = 0.0
    env._update_vision()
    env._capture_timer = 0.0  # 놓은 뒤부터 센다
    return env


def test_capture_needs_fifteen_physics_steps_on_the_beam():
    env = _held_fly_env()
    assert env.config.capture_hold == pytest.approx(0.15) and env.config.dt == 0.01
    for _ in range(7):  # 물리 step 14번
        _, _, terminated, _, info = env.step(np.zeros(2))
        assert not terminated and not info["captured"]
    _, _, terminated, _, info = env.step(np.zeros(2))  # 15번째에서 잡힌다
    assert terminated and info["captured"]
    assert info["t"] == pytest.approx(0.15)


@pytest.mark.parametrize("offset_mm, captured", [(1.2, True), (1.3, False), (52.0, False)])
def test_capture_is_decided_by_distance_to_the_beam(offset_mm, captured):
    # 52mm 는 1m 에서 3° 다. 이전 조건(3°)으로는 잡히던 자리다.
    env = _held_fly_env(offset_m=offset_mm / 1000, distance=1.0)
    info = {}
    for _ in range(20):
        _, _, terminated, _, info = env.step(np.zeros(2))
        if terminated:
            break
    assert info["captured"] is captured
    assert info["beam_dist"] * 1000 == pytest.approx(offset_mm, abs=1e-6)


def test_capture_timer_restarts_when_the_fly_leaves_the_beam():
    env = _held_fly_env()
    for _ in range(6):
        env.step(np.zeros(2))
    on_beam = env.fly.pos.copy()
    env.fly.pos = on_beam + np.array([0.0, 0.01, 0.0])  # 빔에서 1cm 벗어난다
    _, _, terminated, _, _ = env.step(np.zeros(2))
    assert not terminated and env._capture_timer == 0.0
    env.fly.pos = on_beam
    for _ in range(7):
        _, _, terminated, _, _ = env.step(np.zeros(2))
        assert not terminated
    _, _, terminated, _, info = env.step(np.zeros(2))
    assert terminated and info["captured"]


def test_fly_behind_the_turret_is_not_hit():
    env = FlyChaseEnv(static_fly_config())
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos - env.aimer.look * 0.5  # 빔의 연장선 위지만 조준기 뒤다
    env._update_vision()
    assert env._info()["beam_dist"] == pytest.approx(0.5)
    for _ in range(20):
        _, _, terminated, _, info = env.step(np.zeros(2))
    assert not info["captured"]
