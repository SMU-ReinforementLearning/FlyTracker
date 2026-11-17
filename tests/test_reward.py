import math
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from flytracker import EnvConfig, FlyChaseEnv, RewardWeights
from flytracker.fly import FlyParams

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


def _env_with_fly_at(offset_m: float, distance: float = 2.0, reward: RewardWeights | None = None) -> FlyChaseEnv:
    """가만히 있는 초파리를 빔에서 옆으로 offset_m 만큼 떨어뜨려 둔다. 포획은 꺼서 에피소드가 끝나지 않게 한다."""
    cfg = replace(EnvConfig(fly=FlyParams.hovering()), start_facing_fly=True, capture_enabled=False)
    if reward is not None:
        cfg = replace(cfg, reward=reward)
    env = FlyChaseEnv(cfg)
    env.reset(seed=0)
    r, _, f = env.aimer.basis
    env.fly.pos = env.aimer.pos + f * distance + r * offset_m
    env._update_vision()
    return env


def _step_reward(env: FlyChaseEnv) -> float:
    pos = env.fly.pos.copy()
    env.fly.step = lambda *a, **k: None  # 초파리를 그 자리에 둔다
    _, reward, _, _, info = env.step(np.zeros(3))
    assert info["visible"] and np.allclose(env.fly.pos, pos)
    return reward


@pytest.mark.parametrize("offset_mm", [0.0, 1.25, 12.5, 125.0])
def test_beam_penalty_is_log_scaled_distance(offset_mm):
    env = _env_with_fly_at(offset_mm / 1000)
    w = env.config.reward
    expected = math.log1p(offset_mm / 1.25) / math.log1p(1000 / 1.25)
    assert _step_reward(env) == pytest.approx(-w.time - w.beam * expected, abs=1e-6)


def test_beam_penalty_still_changes_near_the_capture_radius():
    # 12.5mm 에서 1.25mm 로 줄 때와 1.25mm 에서 빔 위로 갈 때 모두 벌점이 뚜렷하게 준다.
    # 각도에 비례하던 벌점은 2m 거리의 12.5mm(0.36°)에서 이미 최댓값의 2% 아래였다.
    far, near, on = (_step_reward(_env_with_fly_at(mm / 1000)) for mm in (12.5, 1.25, 0.0))
    w = EnvConfig().reward
    assert near - far > 0.2 * w.beam
    assert on - near > 0.1 * w.beam


def test_beam_penalty_stops_growing_at_beam_far():
    w = EnvConfig().reward
    env = _env_with_fly_at(0.6, distance=4.0)  # 빔에서 0.6m
    env2 = _env_with_fly_at(0.6, distance=4.0, reward=replace(w, beam_far=0.5))
    assert _step_reward(env2) == pytest.approx(-w.time - w.beam)
    assert _step_reward(env) > -w.time - w.beam


def test_visible_is_always_better_than_lost():
    w = EnvConfig().reward
    assert w.beam + w.angle < w.lost


def test_old_reward_is_available_by_weights():
    # 환경 버전 4 까지의 보상: 조준 오차 / 세로 반시야각 × 0.05
    old = replace(RewardWeights(), beam=0.0, angle=0.05)
    env = _env_with_fly_at(2.0 * math.tan(math.radians(5.0)), reward=old)
    assert _step_reward(env) == pytest.approx(-old.time - 0.05 * 5.0 / 20.0, abs=1e-6)


def test_reward_option_parses_and_rejects_unknown_items():
    from _common import reward_from_args

    assert reward_from_args([]) == RewardWeights()
    assert reward_from_args(["beam=0", "angle=0.05"]) == replace(RewardWeights(), beam=0.0, angle=0.05)
    with pytest.raises(SystemExit):
        reward_from_args(["beem=1"])


def test_fly_reward_mirrors_the_beam_term():
    cfg = EnvConfig()
    assert cfg.fly_reward.beam == cfg.reward.beam and cfg.fly_reward.angle == cfg.reward.angle
    env = _env_with_fly_at(0.0125)
    _step_reward(env)
    w = cfg.fly_reward
    assert env.fly_reward() == pytest.approx(w.time + w.beam * math.log1p(10) / math.log1p(800), abs=1e-6)
