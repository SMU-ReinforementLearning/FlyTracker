import math
from dataclasses import replace

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from flytracker import FLY_OBS, FLY_OBS_DIM, EnvConfig, FlyChaseEnv, FlyEscapeEnv
from flytracker.fly import Fly, FlyParams
from flytracker.world import Room


class IdleFly:
    """회피하지 않는 학습한 초파리."""

    def reset(self):
        pass

    def act(self, obs):
        return np.array([-1.0, 0.0, 0.0, 0.0])


def test_fly_observation_lags_by_reaction_delay():
    env = FlyChaseEnv(fly=IdleFly())
    env.reset(seed=3)
    assert env._fly_delay_steps == 3  # 0.06초 / 0.02초
    now, seen = [env._fly_obs_now()], [env.fly_observation()]
    for _ in range(20):
        env.step(np.array([0.5, 0.2]))
        now.append(env._fly_obs_now())
        seen.append(env.fly_observation())
    for k, obs in enumerate(seen):
        np.testing.assert_array_equal(obs, now[max(0, k - 3)].astype(np.float32))
    assert obs.shape == (FLY_OBS_DIM,)


def test_fly_observation_sees_turret_and_laser_in_body_frame():
    env = FlyChaseEnv(replace(EnvConfig(fly=FlyParams.hovering()), start_facing_fly=False), fly=IdleFly())
    env.reset(seed=0)
    env.aimer.reset(env.aimer.pos, yaw=0.0, pitch=0.0)  # −z 를 본다
    env.fly.pos = env.aimer.pos + np.array([0.5, 0.0, -1.0])  # 조준선 오른쪽 0.5m, 앞 1m
    env.fly.heading = np.array([0.0, 0.0, -1.0])  # 조준기와 같은 쪽을 보며 난다. 몸의 오른쪽이 +x
    env._update_vision()
    o = env._fly_obs_now()
    diag = env.config.room.diagonal
    np.testing.assert_allclose(o[FLY_OBS["turret_dir"]], np.array([-0.5, 0.0, 1.0]) @ np.diag([1, 1, -1]) / math.sqrt(1.25), atol=1e-9)
    assert o[FLY_OBS["turret_dist"]][0] == pytest.approx(math.sqrt(1.25) / diag)
    np.testing.assert_allclose(o[FLY_OBS["laser_dir"]], [-1.0, 0.0, 0.0], atol=1e-9)  # 빔은 몸의 왼쪽에 있다
    assert o[FLY_OBS["laser_dist"]][0] == pytest.approx(0.5 / diag)
    assert o[FLY_OBS["aim_error"]][0] == pytest.approx(math.atan2(0.5, 1.0) / math.pi)
    np.testing.assert_allclose(o[FLY_OBS["heading_sincos"]], [0.0, 1.0], atol=1e-9)  # 조준기 yaw 0 과 같은 방향
    assert o[FLY_OBS["escape_ready"]][0] == 1.0


def test_learned_fly_does_not_use_threat_rule():
    env = FlyChaseEnv(replace(EnvConfig(fly=FlyParams.hovering())), fly=IdleFly())
    env.reset(seed=0)
    env.fly.pos = env.aimer.pos + np.array([0.0, 0.2, -0.2])  # 0.35m 안. 규칙 초파리라면 위협으로 느낀다
    for _ in range(10):
        env.step(np.zeros(2))
        assert not env.fly.alarmed


def test_escape_command_turns_speeds_up_and_cools_down():
    p = FlyParams()
    fly = Fly(p, np.random.default_rng(0))
    fly.external_escape = True
    fly.reset(np.array([0.0, 1.2, 0.0]), np.array([0.0, 0.0, -1.0]))
    room, far = Room(), np.array([0.0, 0.1, 1.4])
    assert fly.command_escape(turn=math.pi / 2, climb=0.0, speed_gain=1.6)
    assert not fly.command_escape(turn=0.0, climb=0.0, speed_gain=1.0)  # cooldown 중
    for _ in range(3):  # 회피 선회는 25ms
        fly.step(0.01, room, far)
    np.testing.assert_allclose(fly.heading, [-1.0, 0.0, 0.0], atol=1e-9)  # −z 에서 왼쪽으로 90°
    assert fly.effective_speed == pytest.approx(fly.speed * 1.6)
    steps = math.ceil((p.evade_cooldown - 0.03) / 0.01) + 1
    for _ in range(steps):
        fly.step(0.01, room, far)
    assert fly.escape_ready


@pytest.mark.parametrize("gain_action, gain", [(-1.0, 1.0), (0.0, 1.3), (1.0, 1.6)])
def test_fly_action_maps_to_escape_command(gain_action, gain):
    env = FlyChaseEnv(fly=IdleFly())
    env.reset(seed=0)
    assert not env.apply_fly_action([0.0, 0.5, 0.0, gain_action])  # escape 가 0 이하면 피하지 않는다
    assert env.apply_fly_action([1.0, 0.5, 1.0, gain_action])
    assert env.fly._boost_gain == pytest.approx(gain)
    goal = env.fly._turn[1]
    assert goal[1] == pytest.approx(env.config.fly.max_climb)  # climb 1 → 최대로 오른다


def test_fly_side_env_passes_gymnasium_checker():
    check_env(FlyEscapeEnv(), skip_render_check=True)


def test_fly_reward_is_aimer_reward_with_sign_flipped():
    env = FlyEscapeEnv(EnvConfig(fly=FlyParams.hovering()))
    env.reset(seed=0)
    core = env.core
    behind = -np.array([core.aimer.look[0], 0.0, core.aimer.look[2]])
    core.fly.pos = core.aimer.pos + behind * 1.5 + np.array([0.0, 0.3, 0.0])  # 조준기 뒤. 안 보인다
    core._update_vision()
    _, r, _, _, info = env.step(np.zeros(4))
    assert not info["visible"]
    w = core.config.fly_reward
    assert r == pytest.approx(w.time + w.lost)
    assert r == pytest.approx(-info["aimer_reward"] - core.config.reward.action_change * np.mean(core._prev_action**2))


def test_captured_fly_loses_capture_reward():
    env = FlyEscapeEnv(replace(EnvConfig(fly=FlyParams.hovering()), start_facing_fly=True))
    env.reset(seed=0)
    terminated, r = False, 0.0
    for _ in range(200):
        _, r, terminated, truncated, info = env.step(np.zeros(4))
        if terminated or truncated:
            break
    assert terminated and info["captured"]
    assert r < -env.config.fly_reward.capture + 1.0
