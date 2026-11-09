import json
from dataclasses import replace

from flytracker import EnvConfig, EpisodeRecorder, RuleAimer, RunStore, make_env
from flytracker.fly import FlyParams
from flytracker.record import FRAME_KEYS


def run_episode(env, policy, seed):
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
    cfg = EnvConfig(fly=FlyParams(cruise_speed=0.3))
    assert EnvConfig.from_dict(json.loads(json.dumps(cfg.to_dict()))) == cfg


def test_baseline_catches_hovering_fly():
    fly = FlyParams(cruise_speed=0.0, speed_jitter=0.0, saccade_rate=0.0)
    cfg = EnvConfig(fly=fly, start_facing_fly=True)
    env = EpisodeRecorder(make_env(cfg))
    caught = sum(run_episode(env, RuleAimer(), seed=s)["summary"]["captured"] for s in range(5))
    assert caught == 5
