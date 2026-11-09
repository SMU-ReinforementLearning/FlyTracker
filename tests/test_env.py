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
