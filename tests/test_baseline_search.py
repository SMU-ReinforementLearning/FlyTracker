import math
from dataclasses import replace

import numpy as np

from flytracker import EnvConfig, FlyChaseEnv, RuleAimer
from flytracker.fly import FlyParams
from flytracker.geometry import rotate_about_y


def hover_env(**kw) -> FlyChaseEnv:
    return FlyChaseEnv(replace(EnvConfig(fly=FlyParams.hovering()), **kw))


def run_until_visible(env, policy, obs, max_steps):
    modes = []
    for i in range(max_steps):
        action = policy.act(obs)
        modes.append(policy.mode)
        obs, _, terminated, truncated, info = env.step(action)
        if info["visible"]:
            return i + 1, modes
        if terminated or truncated:
            break
    return None, modes


def test_sweep_covers_every_band_and_finds_fly_behind_turret():
    env = hover_env(max_seconds=10.0)
    obs, _ = env.reset(seed=0)
    look = env.aimer.look
    behind = np.array([-look[0], 0.0, -look[2]])
    behind = behind / np.linalg.norm(behind)
    env.fly.pos = env.aimer.pos + behind * 1.5 + np.array([0.0, 1.6, 0.0])  # 뒤쪽 1.5m, 1.6m 위. 높이각 약 47°
    env._update_vision()
    obs = env._observation()
    assert obs[0] == 0.0  # 처음에는 안 보인다
    policy = RuleAimer()
    one_turn = 2 * math.pi / (policy.sweep_rate * policy.max_yaw_rate)
    steps, modes = run_until_visible(env, policy, obs, max_steps=int(len(policy.sweep_bands) * one_turn / 0.02) + 50)
    assert steps is not None  # 띠를 모두 한 바퀴씩 도는 안에 찾는다
    assert set(modes) == {"sweep"}


def test_figure8_reacquires_fly_that_slipped_out_of_view():
    env = hover_env(max_seconds=10.0)
    obs, _ = env.reset(seed=1)
    env.fly.pos = env.aimer.pos + np.array([0.0, 0.5, -1.8])  # 앞쪽 1.8m, 높이각 약 15°
    d = env.fly.pos - env.aimer.pos
    env.aimer.reset(env.aimer.pos, math.atan2(-d[0], -d[2]), math.asin(d[1] / np.linalg.norm(d)))
    env._update_vision()
    policy = RuleAimer()
    obs, *_ = env.step(policy.act(env._observation()))  # 가운데에 잡힌 상태
    assert env._proj.visible and policy.mode == "track"

    offset = env.fly.pos - env.aimer.pos
    env.fly.pos = env.aimer.pos + rotate_about_y(offset, math.radians(55.0))  # 옆으로 55° 밀어 시야 밖으로
    env._update_vision()
    obs = env._observation()
    assert obs[0] == 0.0
    steps, modes = run_until_visible(env, policy, obs, max_steps=300)
    assert steps is not None
    assert "figure8" in modes and "sweep" not in modes  # 전역 탐색까지 가지 않고 8자로 다시 찾는다
