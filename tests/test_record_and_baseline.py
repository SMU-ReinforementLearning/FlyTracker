import json
import math
from dataclasses import replace

from flytracker import ENV_VERSION, EnvConfig, EpisodeRecorder, RuleAimer, RunStore, make_env
from flytracker.fly import FlyParams
from flytracker.record import FRAME_KEYS


def run_episode(env, policy, seed):
    policy.reset()
    obs, _ = env.reset(seed=seed)
    done = False
    while not done:
        action, _ = policy.predict(obs)
        obs, _, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
    return env.last_episode


def test_recorder_writes_run_files(tmp_path):
    cfg = replace(EnvConfig(), max_seconds=1.0)
    store = RunStore(tmp_path)
    run = store.create_run("test", "rule-baseline", "continuous", {"env": cfg.to_dict()})
    env = EpisodeRecorder(make_env(cfg), meta={"policy": "rule-baseline"})
    episode = run_episode(env, RuleAimer(), seed=1)
    rel = run.save_episode(episode, "baseline")

    loaded = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
    n = loaded["summary"]["frames"]
    for key in (*FRAME_KEYS, "reward"):
        assert len(loaded["frames"][key]) == n, key
    assert loaded["meta"]["policy"] == "rule-baseline"

    index = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    assert index["runs"][0]["episodeCount"] == 1
    manifest = json.loads((tmp_path / run.id / "episodes.json").read_text(encoding="utf-8"))
    assert manifest["episodes"][0]["file"] == rel


def test_config_roundtrip():
    cfg = EnvConfig(fly=FlyParams(speed_long=0.4))
    assert EnvConfig.from_dict(json.loads(json.dumps(cfg.to_dict()))) == cfg


def test_baseline_catches_hovering_fly():
    fly = FlyParams.hovering()
    cfg = EnvConfig(fly=fly, start_facing_fly=True)
    env = EpisodeRecorder(make_env(cfg))
    caught = sum(run_episode(env, RuleAimer(), seed=s)["summary"]["captured"] for s in range(5))
    assert caught == 5


def test_config_json_records_env_version(tmp_path):
    run = RunStore(tmp_path).create_run("test", "rule-baseline", "continuous", {"env": EnvConfig().to_dict()})
    config = json.loads((tmp_path / run.id / "config.json").read_text(encoding="utf-8"))
    assert config["envVersion"] == ENV_VERSION
    assert EnvConfig.from_dict(config["env"]) == EnvConfig()


def test_baseline_sweep_bands_stop_once_zenith_is_in_view():
    bands = [round(math.degrees(b), 6) for b in RuleAimer().sweep_bands]
    assert bands == [10.0, 45.0, 80.0]  # 80° 띠의 위 끝이 100° 라 천정이 이미 보인다
