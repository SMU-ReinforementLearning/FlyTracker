import json

import gymnasium as gym
import numpy as np
import pytest

from flytracker import ENV_VERSION, EnvConfig, FlyChaseEnv, FlyEscapeEnv, PolicyPlayer, RunStore, load_opponent, make_env, make_fly_env


class Recorder:
    """받은 관측을 모아 두는 정책."""

    def __init__(self):
        self.seen = []

    def predict(self, obs, deterministic=True):
        self.seen.append(np.array(obs))
        return np.zeros(3, dtype=np.float32), None


def test_policy_player_stacks_frames_like_the_gymnasium_wrapper():
    stacked = gym.wrappers.FrameStackObservation(FlyChaseEnv(), 3)
    plain = FlyChaseEnv()
    player = PolicyPlayer(Recorder(), frame_stack=3)
    player.reset()
    expected = [stacked.reset(seed=5)[0]]
    obs, _ = plain.reset(seed=5)
    player.act(obs)
    for _ in range(6):
        expected.append(stacked.step(np.zeros(3))[0])
        player.act(plain.step(np.zeros(3))[0])
    for want, got in zip(expected, player.policy.seen):
        np.testing.assert_array_equal(want, got)


def test_rule_opponents():
    cfg = EnvConfig()
    assert isinstance(load_opponent("baseline", "aimer", cfg).player, PolicyPlayer)
    assert load_opponent("rule", "fly", cfg).player is None
    with pytest.raises(ValueError):
        load_opponent("rule", "aimer", cfg)


def _train_and_save(tmp_path, side: str):
    """PPO 를 64 step 만 학습해 실행 폴더에 저장한다. 불러오기를 시험하려는 것이라 성적은 보지 않는다."""
    sb3 = pytest.importorskip("stable_baselines3")
    cfg = EnvConfig()
    env = make_env(cfg) if side == "aimer" else make_fly_env(cfg)
    model = sb3.PPO("MlpPolicy", env, n_steps=64, batch_size=64, n_epochs=1, device="cpu", seed=0)
    model.learn(total_timesteps=64)
    algo = {"name": "ppo", "frameStack": 1, "side": side}
    run = RunStore(tmp_path).create_run(f"{side}-ppo", "ppo", "continuous", {"env": cfg.to_dict(), "algo": algo})
    model.save(run.dir / "model")
    (run.dir / "checkpoints").mkdir()
    model.save(run.dir / "checkpoints" / "step_0000064")
    return run.dir


def _play(env, act) -> int:
    obs, _ = env.reset(seed=0)
    for steps in range(1, 501):
        obs, _, terminated, truncated, _ = env.step(act(obs))
        if terminated or truncated:
            return steps
    raise AssertionError("에피소드가 끝나지 않았다")


def test_saved_models_load_back_as_opponents(tmp_path):
    cfg = EnvConfig()
    fly_run = _train_and_save(tmp_path, "fly")
    aimer_run = _train_and_save(tmp_path, "aimer")

    fly = load_opponent(str(fly_run), "fly", cfg)
    assert fly.label == fly_run.name and fly.env_version == ENV_VERSION
    assert _play(FlyChaseEnv(cfg, fly=fly.player), lambda obs: np.zeros(3)) > 0

    aimer = load_opponent(str(aimer_run / "checkpoints" / "step_0000064.zip"), "aimer", cfg)
    assert aimer.label == f"{aimer_run.name}/step_0000064"
    assert _play(FlyEscapeEnv(cfg, aimer=aimer.player), lambda obs: np.zeros(4)) > 0

    with pytest.raises(ValueError, match="쪽 모델이라"):
        load_opponent(str(fly_run), "aimer", cfg)


def test_model_from_another_env_version_is_refused(tmp_path):
    run_dir = _train_and_save(tmp_path, "fly")
    path = run_dir / "config.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["envVersion"] = 5  # 조준기 관측에 shot 이 없던 버전
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="환경 버전"):
        load_opponent(str(run_dir), "fly", EnvConfig())

    config["envVersion"] = 6  # 관측, 행동, 보상이 버전 7과 같다. 학습한 버전을 적어서 불러온다 (#91)
    path.write_text(json.dumps(config), encoding="utf-8")
    assert load_opponent(str(run_dir), "fly", EnvConfig()).env_version == 6 and ENV_VERSION == 7


class TwoValuePolicy(Recorder):
    """발사 행동이 없던 때의 정책처럼 yaw, pitch 두 값만 낸다."""

    def predict(self, obs, deterministic=True):
        self.seen.append(np.array(obs))
        return np.array([0.5, -0.5], dtype=np.float32), None


def test_rule_fire_player_hides_shot_and_fires_by_the_baseline_rule():
    cfg = EnvConfig(start_facing_fly=True)
    tracker = load_opponent("baseline", "aimer", cfg).player.policy
    player = PolicyPlayer(TwoValuePolicy(), tracker=tracker, rule_fire=True)
    env = FlyChaseEnv(cfg)
    obs, _ = env.reset(seed=3)
    fired = set()
    for _ in range(40):
        a = player.act(obs)
        assert a.shape == (3,) and tuple(a[:2]) == (0.5, -0.5)
        assert a[2] == (1.0 if tracker.wants_fire(obs) else -1.0)
        fired.add(float(a[2]))
        np.testing.assert_array_equal(player.policy.seen[-1], np.asarray(obs, dtype=np.float32)[:-1])  # shot 은 마지막 칸이다
        obs, _, terminated, truncated, _ = env.step(tracker.act(obs))  # 기준선이 몰아서 쏘는 상황과 안 쏘는 상황을 다 지난다
        if terminated or truncated:
            break
    assert fired == {1.0, -1.0}
    with pytest.raises(ValueError):
        PolicyPlayer(TwoValuePolicy(), rule_fire=True)  # 쏘는 규칙을 줄 tracker 가 없다


class Version5AimerEnv(gym.Env):
    """환경 버전 5의 조준기 쪽 모양: 관측 17차원, 행동 2차원."""

    observation_space = gym.spaces.Box(-1.0, 1.0, (17,), np.float32)
    action_space = gym.spaces.Box(-1.0, 1.0, (2,), np.float32)

    def reset(self, *, seed=None, options=None):
        return np.zeros(17, np.float32), {}

    def step(self, action):
        return np.zeros(17, np.float32), 0.0, False, False, {}


def test_version_5_aimer_model_loads_with_rule_fire(tmp_path):
    sb3 = pytest.importorskip("stable_baselines3")
    cfg = EnvConfig()
    model = sb3.PPO("MlpPolicy", Version5AimerEnv(), n_steps=64, batch_size=64, n_epochs=1, device="cpu", seed=0)
    model.learn(total_timesteps=64)
    algo = {"name": "ppo", "frameStack": 1, "side": "aimer", "assist": 0.2}
    run = RunStore(tmp_path).create_run("old-aimer", "ppo", "continuous", {"env": cfg.to_dict(), "algo": algo})
    model.save(run.dir / "model")
    path = run.dir / "config.json"
    config = json.loads(path.read_text(encoding="utf-8"))

    config["envVersion"] = 5
    path.write_text(json.dumps(config), encoding="utf-8")
    aimer = load_opponent(str(run.dir), "aimer", cfg)
    assert (aimer.env_version, aimer.fire) == (5, "rule") and aimer.player.rule_fire
    assert _play(FlyChaseEnv(cfg), aimer.player.act) > 0

    config["envVersion"] = 4  # 관측이 더 다르다. 붙일 수 없다
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="환경 버전"):
        load_opponent(str(run.dir), "aimer", cfg)
