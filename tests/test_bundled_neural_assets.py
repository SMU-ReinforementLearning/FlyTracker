"""동봉 실행, 명시적 외부 경로 및 기존 계산의 동등성."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import pytest

from flytracker import EnvConfig, EpisodeRecorder, FlyChaseEnv, NeuralConfig, NeuralFly, RunStore
from flytracker.neural_fly import BUNDLED_SOURCE_ROOT, BUNDLED_SOURCE_ID, load_backend
from flytracker.world import Room


@pytest.mark.parametrize("source", [None, BUNDLED_SOURCE_ID, str(BUNDLED_SOURCE_ROOT), BUNDLED_SOURCE_ID.replace("/", "\\")])
def test_bundled_source_works_without_environment_or_repository_cwd(monkeypatch, tmp_path, source):
    monkeypatch.delenv("FLYTRACKER_NEURAL_SOURCE", raising=False)
    monkeypatch.chdir(tmp_path)
    backend = load_backend(NeuralConfig(source_root=source))
    assert backend.root == BUNDLED_SOURCE_ROOT
    assert backend.data == BUNDLED_SOURCE_ROOT / "data/stage2"


def test_explicit_source_then_environment_then_bundle(monkeypatch, tmp_path):
    missing = tmp_path / "explicit-missing"
    monkeypatch.setenv("FLYTRACKER_NEURAL_SOURCE", BUNDLED_SOURCE_ID)
    with pytest.raises(ValueError, match="explicit-missing"):
        load_backend(NeuralConfig(source_root=str(missing)))
    assert load_backend(NeuralConfig()).root == BUNDLED_SOURCE_ROOT
    monkeypatch.setenv("FLYTRACKER_NEURAL_SOURCE", str(tmp_path / "environment-missing"))
    with pytest.raises(ValueError, match="environment-missing"):
        load_backend(NeuralConfig())
    assert load_backend(NeuralConfig(source_root=BUNDLED_SOURCE_ID)).root == BUNDLED_SOURCE_ROOT
    with pytest.raises(ValueError, match="벗어"):
        load_backend(NeuralConfig(source_root=BUNDLED_SOURCE_ID + "/../../escape"))


def test_all_bundled_bytes_match_manifest_and_published_episode():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((BUNDLED_SOURCE_ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    reference = json.loads((root / manifest["reference_episode"]).read_text(encoding="utf-8"))["meta"]["neural"]["sha256"]
    assert len(manifest["files"]) == 13
    for row in manifest["files"]:
        data = (BUNDLED_SOURCE_ROOT / row["path"]).read_bytes()
        assert len(data) == row["bytes"] and len(data) < 100 * 1024**2
        assert hashlib.sha256(data).hexdigest() == row["sha256"] == reference[row["episode_hash_key"]]
    assert (BUNDLED_SOURCE_ROOT / "NOTICE.md").is_file()


@pytest.mark.parametrize("explicit", [False, True])
def test_bundled_record_and_config_contain_no_absolute_local_paths(monkeypatch, tmp_path, explicit):
    monkeypatch.delenv("FLYTRACKER_NEURAL_SOURCE", raising=False)
    cfg = EnvConfig(fly_model="neural", max_seconds=.04,
                    neural=NeuralConfig(source_root=str(BUNDLED_SOURCE_ROOT) if explicit else None,
                                        data_dir=str(BUNDLED_SOURCE_ROOT / "data/stage2") if explicit else None))
    cfg_data = cfg.to_dict()
    restored = EnvConfig.from_dict(cfg_data)
    recorder = EpisodeRecorder(FlyChaseEnv(restored))
    recorder.reset(seed=42)
    recorder.step([0, 0]); recorder.step([0, 0])
    ep = recorder.last_episode
    assert ep["meta"]["neural"]["source_kind"] == "bundled"
    assert ep["meta"]["neural"]["resolved_source_root"] == BUNDLED_SOURCE_ID
    assert ep["meta"]["neural"]["resolved_data_dir"] == BUNDLED_SOURCE_ID + "/data/stage2"
    store = RunStore(tmp_path)
    run = store.create_run("bundled", "test", "continuous", {"env": cfg_data})
    relative = run.save_episode(ep, "test")
    def strings(value):
        if isinstance(value, dict):
            for child in value.values(): yield from strings(child)
        elif isinstance(value, list):
            for child in value: yield from strings(child)
        elif isinstance(value, str): yield value
    saved = [json.loads((run.dir / "config.json").read_text(encoding="utf-8")),
             json.loads((store.root / relative).read_text(encoding="utf-8"))]
    assert not any(Path(value).is_absolute() for value in strings(saved))
    assert restored.to_dict() == cfg_data


def test_external_copy_and_bundled_flight_have_identical_neural_and_physical_states(monkeypatch, tmp_path):
    monkeypatch.delenv("FLYTRACKER_NEURAL_SOURCE", raising=False)
    external = tmp_path / "external"
    shutil.copytree(BUNDLED_SOURCE_ROOT, external)
    a = NeuralFly(NeuralConfig(boundary_enabled=False), np.random.default_rng(17))
    b = NeuralFly(NeuralConfig(source_root=str(external), boundary_enabled=False), np.random.default_rng(17))
    for fly in (a, b):
        fly.reset([0, 1.2, 0], [0, 0, -1])
        fly.step(.05, Room())
    for name in ("pos", "heading", "velocity", "quaternion", "angular_velocity"):
        np.testing.assert_array_equal(getattr(a, name), getattr(b, name))
    for name in ("voltage", "synaptic", "pending", "next_active", "counts"):
        np.testing.assert_array_equal(getattr(a.sim.neural, name), getattr(b.sim.neural, name))
    assert a.sim.neural.rng.bit_generator.state == b.sim.neural.rng.bit_generator.state
    assert a.provenance()["sha256"] == b.provenance()["sha256"]
    assert b.provenance()["resolved_source_root"] == str(external.resolve())
