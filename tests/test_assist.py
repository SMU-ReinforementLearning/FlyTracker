from dataclasses import replace

import numpy as np
import pytest

from flytracker import OBS, EnvConfig, PolicyPlayer, RuleAimer, make_env
from flytracker.players import baseline_player


class Constant:
    """늘 같은 행동을 내는 정책."""

    def __init__(self, action):
        self.action = np.asarray(action, dtype=np.float32)

    def predict(self, obs, deterministic=True):
        return self.action, None


def _spy(env):
    """환경에 실제로 들어간 행동을 모은다."""
    base, seen = env.unwrapped, []
    step = base.step

    def wrapped(action):
        seen.append(np.asarray(action, dtype=float).copy())
        return step(action)

    base.step = wrapped
    return seen


def test_assist_adds_tracking_only_while_visible():
    tracker = RuleAimer()
    policy_action = np.array([0.5, -0.5, 0.0])
    visible_steps = hidden_steps = 0
    # 초파리를 바라보며 시작하는 환경(보인다)과 seed 0 의 기본 환경(처음에 안 보인다)을 차례로 돌린다.
    for cfg, seed in ((replace(EnvConfig(), start_facing_fly=True, capture_enabled=False), 3), (EnvConfig(), 0)):
        env = make_env(cfg, assist=0.2)
        seen = _spy(env)
        obs, _ = env.reset(seed=seed)
        for _ in range(20):
            visible = obs[OBS["visible"]][0] > 0.5
            expected = np.clip(tracker.track(np.asarray(obs, dtype=float)) + 0.2 * policy_action, -1, 1) if visible else policy_action
            obs, *_ = env.step(policy_action)
            assert seen[-1] == pytest.approx(expected)
            visible_steps += visible
            hidden_steps += not visible
    assert visible_steps > 0 and hidden_steps > 0  # 두 경우를 모두 지났다


def test_policy_that_only_fires_captures_with_assist_once_the_fly_is_seen():
    # 정책이 돌리는 값을 0 으로 두고 쏘기만 해도, 보이는 초파리에는 기준선처럼 빔이 붙어서 잡힌다.
    env = make_env(replace(EnvConfig(), start_facing_fly=True), assist=0.2)
    obs, info = env.reset(seed=1)
    done = False
    while not done:
        obs, _, terminated, truncated, info = env.step(np.array([0.0, 0.0, 1.0]))
        done = terminated or truncated
    assert info["captured"]


def test_player_applies_the_same_assist_as_the_wrapper():
    cfg = replace(EnvConfig(), start_facing_fly=True, capture_enabled=False, max_seconds=0.6)
    policy = Constant([0.3, 0.1, 0.0])
    wrapped = make_env(cfg, assist=0.2)
    seen = _spy(wrapped)
    obs, _ = wrapped.reset(seed=5)
    plain = make_env(cfg)
    player = PolicyPlayer(policy, assist=0.2, tracker=baseline_player(cfg).policy)
    player.reset()
    obs2, _ = plain.reset(seed=5)
    for _ in range(30):
        obs, *_ = wrapped.step(policy.action)
        action = player.act(obs2)
        assert action == pytest.approx(seen[-1])
        obs2, *_ = plain.step(action)
        assert obs2 == pytest.approx(obs)


def test_assist_needs_continuous_actions():
    with pytest.raises(ValueError):
        make_env(action_mode="discrete", assist=0.2)
