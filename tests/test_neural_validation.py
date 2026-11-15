"""Additional Issue #31 contracts discovered during bounded validation."""

from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

from flytracker import EnvConfig, EpisodeRecorder, FlyChaseEnv, NeuralConfig, NeuralFly, RunStore, StimulusConfig
from flytracker.neural_fly import load_backend
from flytracker.world import Room


@pytest.fixture
def local_config():
    root = os.environ.get("FLYTRACKER_NEURAL_SOURCE")
    if not root:
        pytest.skip("Local neural integration needs FLYTRACKER_NEURAL_SOURCE")
    return NeuralConfig(source_root=root)


def test_nonexistent_source_reports_root_and_missing_module(tmp_path):
    root = tmp_path / "missing-source"
    with pytest.raises(ValueError, match="Cannot read local neural source/data") as exc:
        load_backend(NeuralConfig(source_root=str(root)))
    assert "missing-source" in str(exc.value) and "core.py" in str(exc.value)


def test_missing_data_reports_exact_csv(local_config, tmp_path):
    with pytest.raises(ValueError, match="Cannot read local neural source/data") as exc:
        load_backend(replace(local_config, data_dir=str(tmp_path / "missing-data")))
    assert "missing-data" in str(exc.value) and "neurons.csv" in str(exc.value)


@pytest.mark.parametrize("duration", [.01, .03, .05])
def test_neural_odd_10ms_horizon_does_not_overrun(local_config, duration):
    recorder = EpisodeRecorder(FlyChaseEnv(EnvConfig(fly_model="neural", neural=local_config,
                                                    max_seconds=duration, capture_hold=2.)))
    recorder.reset(seed=0)
    for _ in range(10):
        _, _, terminated, truncated, _ = recorder.step([0, 0])
        if terminated or truncated:
            break
    assert truncated and not terminated
    assert recorder.unwrapped.t == duration
    assert recorder.last_episode["frames"]["t"][-1] == duration
    times = recorder.last_episode["frames"]["t"]
    assert times[-1] - times[-2] == pytest.approx(.01)


def test_saved_neural_events_config_and_hashes_are_actual(local_config, tmp_path):
    cfg = EnvConfig(fly_model="neural", neural=local_config, max_seconds=.4,
                    capture_hold=2., start_facing_fly=True)
    recorder = EpisodeRecorder(FlyChaseEnv(cfg))
    recorder.reset(seed=0)
    for _ in range(20):
        recorder.step([0, 0])
    store = RunStore(tmp_path / "new-run-store")
    run = store.create_run("validation", "fixed-action", "continuous", {"env": cfg.to_dict()})
    relative = run.save_episode(recorder.last_episode, "test")
    saved = json.loads((store.root / relative).read_text(encoding="utf-8"))
    assert saved == recorder.last_episode
    stored_cfg = json.loads((run.dir / "config.json").read_text(encoding="utf-8"))["env"]
    assert EnvConfig.from_dict(stored_cfg) == cfg
    events = saved["diagnostics"]["stimulus"]["events"]
    assert events[0]["onset_ms"] == 120
    assert events[0]["end_ms"] == 370
    assert events[0]["exposure_ms"] == 250
    assert saved["meta"]["stimulus"] == asdict(cfg.stimulus)
    root = Path(local_config.source_root)
    for name in ("core", "neural", "neural_state", "physics", "behavior"):
        key = f"flysim/{name}.py"
        assert saved["meta"]["neural"]["sha256"][key] == hashlib.sha256((root / key).read_bytes()).hexdigest()
    for name in ("neurons.csv", "edges.csv"):
        assert saved["meta"]["neural"]["sha256"]["data/"+name] == hashlib.sha256((root/"data/stage2"/name).read_bytes()).hexdigest()


def test_chunked_adapter_replays_rng_neural_and_wall_state(local_config):
    a = NeuralFly(local_config, np.random.default_rng(13))
    b = NeuralFly(local_config, np.random.default_rng(13))
    for fly in (a, b):
        fly.reset([1.97, 1.2, 0], [1, 0, 0])
    a.step(1., Room())
    for _ in range(100):
        b.step(.01, Room())
    assert a.sim.body == b.sim.body
    for name in ("voltage", "synaptic", "pending", "next_active", "counts"):
        np.testing.assert_array_equal(getattr(a.sim.neural, name), getattr(b.sim.neural, name))
    np.testing.assert_array_equal(a.sim.motor.filtered, b.sim.motor.filtered)
    assert a.sim.neural.rng.bit_generator.state == b.sim.neural.rng.bit_generator.state
    np.testing.assert_array_equal(a.sim.motor.force_body, b.sim.motor.force_body)
    np.testing.assert_array_equal(a.sim.motor.reflex_activation, b.sim.motor.reflex_activation)
    assert a.boundary_corrections == b.boundary_corrections
