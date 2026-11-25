"""각가속도 행동(AccelControl), 규칙 발사(RuleFire), 오발 벌점 (#88)."""

from dataclasses import replace

import numpy as np
import pytest

from flytracker import EnvConfig, make_env
from flytracker.env import OBS, OBS_DIM, FlyChaseEnv, RewardWeights
from flytracker.players import PolicyPlayer, baseline_player
from flytracker.wrappers import AccelControl, RuleFire, accel_gain, accel_to_rate


class Scripted:
    """정해 둔 행동을 차례로 내는 정책."""

    def __init__(self, actions):
        self.actions, self.i, self.seen = actions, 0, []

    def predict(self, obs, deterministic=True):
        self.seen.append(np.array(obs))
        a = self.actions[self.i % len(self.actions)]
        self.i += 1
        return np.array(a, dtype=np.float32), None


def test_accel_gain_is_the_rate_change_of_one_step():
    assert accel_gain(EnvConfig()) == pytest.approx([0.08, 0.12])  # 720°/s² × 0.02s = 14.4°/s


def test_zero_accel_keeps_the_current_rate_and_fire_passes_through():
    obs = np.zeros(OBS_DIM)
    obs[OBS["yaw_rate"]], obs[OBS["pitch_rate"]] = 0.5, -0.25
    out = accel_to_rate(obs, [0.0, 0.0, 0.7], accel_gain(EnvConfig()))
    assert out == pytest.approx([0.5, -0.25, 0.7])
    out = accel_to_rate(obs, [1.0, -1.0, -1.0], accel_gain(EnvConfig()))
    assert out == pytest.approx([0.58, -0.37, -1.0])


def test_accel_command_is_clipped_to_the_rate_range():
    obs = np.zeros(OBS_DIM)
    obs[OBS["yaw_rate"]] = 0.97
    assert accel_to_rate(obs, [1.0, 0.0, 0.0], accel_gain(EnvConfig()))[0] == pytest.approx(1.0)


def test_full_accel_reaches_the_commanded_rate_within_the_step():
    env = make_env(control="accel")
    obs, _ = env.reset(seed=3)
    rates = []
    for _ in range(5):
        obs, *_ = env.step(np.array([1.0, 0.0, -1.0]))
        rates.append(float(obs[OBS["yaw_rate"]][0]))
    assert rates == pytest.approx([0.08 * k for k in range(1, 6)], abs=1e-6)
    for _ in range(3):  # 행동 0 이면 같은 속도로 계속 돈다
        obs, *_ = env.step(np.array([0.0, 0.0, -1.0]))
        assert float(obs[OBS["yaw_rate"]][0]) == pytest.approx(0.4, abs=1e-6)


def test_rule_fire_hides_shot_and_fires_by_the_baseline_rule():
    cfg = replace(EnvConfig(), start_facing_fly=True)
    env = make_env(cfg, fire="rule")
    assert env.observation_space.shape == (OBS_DIM - 1,) and env.action_space.shape == (2,)
    inner = env.unwrapped
    tracker = baseline_player(cfg).policy
    obs, _ = env.reset(seed=1)
    assert obs.shape == (OBS_DIM - 1,)
    fired = set()
    for _ in range(150):
        full = inner._observation()
        want = tracker.wants_fire(full)
        shots, busy = inner.shots, inner._shot_left > 0
        a = tracker.track(full)[:2] if full[OBS["visible"]][0] > 0.5 else np.zeros(2)
        obs, _, terminated, truncated, _ = env.step(a)
        if not busy:
            assert (inner.shots > shots) == want
            fired.add(want)
        if terminated or truncated:
            break
    assert fired == {True, False}


@pytest.mark.parametrize("control,fire", [("accel", "policy"), ("accel", "rule"), ("rate", "rule")])
def test_player_reproduces_the_training_wrappers(control, fire):
    cfg = EnvConfig()
    rng = np.random.default_rng(0)
    dim = 2 if fire == "rule" else 3
    actions = rng.uniform(-1, 1, size=(60, dim))
    wrapped = make_env(cfg, control=control, fire=fire)
    obs_w, _ = wrapped.reset(seed=7)
    plain = FlyChaseEnv(cfg)
    obs_p, _ = plain.reset(seed=7)
    policy = Scripted(actions)
    player = PolicyPlayer(policy, tracker=baseline_player(cfg).policy, rule_fire=fire == "rule",
                          accel_gain=accel_gain(cfg) if control == "accel" else None)
    for a in actions:
        obs_w, r_w, term_w, trunc_w, _ = wrapped.step(a)
        obs_p, r_p, term_p, trunc_p, _ = plain.step(player.act(obs_p))
        assert r_w == pytest.approx(r_p)
        assert (term_w, trunc_w) == (term_p, trunc_p)
        if term_w or trunc_w:
            break
    assert policy.seen[0].shape == wrapped.observation_space.shape
    assert plain.aimer.yaw == pytest.approx(wrapped.unwrapped.aimer.yaw)
    assert plain.aimer.pitch == pytest.approx(wrapped.unwrapped.aimer.pitch)
    assert plain.shots == wrapped.unwrapped.shots


def test_wrappers_refuse_discrete_actions():
    with pytest.raises(ValueError):
        make_env(action_mode="discrete", control="accel")
    with pytest.raises(ValueError):
        make_env(action_mode="discrete", fire="rule")
    with pytest.raises(ValueError):
        make_env(control="jerk")


def test_misfire_penalty_is_charged_once_in_the_step_the_shot_goes_off_target():
    def rewards(weight):
        env = FlyChaseEnv(replace(EnvConfig(), reward=replace(RewardWeights(), misfire=weight)))
        env.reset(seed=5)
        out = []
        for _ in range(12):  # 초파리를 보지 않고 쏜다. 첫 물리 step 에서 빗나간다
            _, r, *_ = env.step(np.array([0.0, 0.0, 1.0]))
            out.append((r, env.misfires))
        return out

    free, charged = rewards(0.0), rewards(0.5)
    assert [m for _, m in free] == [m for _, m in charged]
    assert free[0][1] == 1 and free[-1][1] >= 2
    seen = 0
    for (r0, m), (r1, _) in zip(free, charged):
        assert r0 - r1 == pytest.approx(0.5 * (m - seen))
        seen = m


def test_default_reward_has_no_misfire_term():
    assert RewardWeights().misfire == 0.0
    assert isinstance(AccelControl(FlyChaseEnv()), AccelControl) and isinstance(RuleFire(FlyChaseEnv()), RuleFire)
