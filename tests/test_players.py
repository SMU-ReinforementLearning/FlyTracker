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
        return np.zeros(2, dtype=np.float32), None


def test_policy_player_stacks_frames_like_the_gymnasium_wrapper():
    stacked = gym.wrappers.FrameStackObservation(FlyChaseEnv(), 3)
    plain = FlyChaseEnv()
    player = PolicyPlayer(Recorder(), frame_stack=3)
    player.reset()
    expected = [stacked.reset(seed=5)[0]]
    obs, _ = plain.reset(seed=5)
    player.act(obs)
    for _ in range(6):
        expected.append(stacked.step(np.zeros(2))[0])
        player.act(plain.step(np.zeros(2))[0])
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
    assert _play(FlyChaseEnv(cfg, fly=fly.player), lambda obs: np.zeros(2)) > 0

    aimer = load_opponent(str(aimer_run / "checkpoints" / "step_0000064.zip"), "aimer", cfg)
    assert aimer.label == f"{aimer_run.name}/step_0000064"
    assert _play(FlyEscapeEnv(cfg, aimer=aimer.player), lambda obs: np.zeros(4)) > 0

    with pytest.raises(ValueError, match="쪽 모델이라"):
        load_opponent(str(fly_run), "aimer", cfg)


def test_model_from_another_env_version_is_refused(tmp_path):
    run_dir = _train_and_save(tmp_path, "fly")
    path = run_dir / "config.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["envVersion"] = ENV_VERSION - 1
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="환경 버전"):
        load_opponent(str(run_dir), "fly", EnvConfig())
