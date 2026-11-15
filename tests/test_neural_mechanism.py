"""현재 신경 날개 모델의 선택, 출처, 회로 대조 계약."""
from dataclasses import replace
import hashlib
import os
from pathlib import Path

import numpy as np
import pytest

from flytracker import NeuralConfig, NeuralFly
from flytracker.world import Room


@pytest.mark.parametrize("settings", [
    {"dynamics": "source"}, {"dynamics": "inspection-3d"}, {"lesion": "unknown"}])
def test_only_current_neural_model_is_selectable(settings):
    with pytest.raises(ValueError):
        NeuralConfig(**settings)


def test_provenance_contains_only_active_physics():
    root = os.environ.get("FLYTRACKER_NEURAL_SOURCE")
    if not root:
        pytest.skip("Local neural source not selected")
    fly = NeuralFly(NeuralConfig(source_root=root), np.random.default_rng(101))
    fly.reset([0, 1.2, 0], [0, 0, -1])
    fly.step(.05, Room())
    d, p = fly.diagnostics(), fly.provenance()
    assert d["speed_command_mps"] is None
    assert "speed_components" not in d and "motor_seed" not in p
    assert p["dynamics"] == "neuromechanical"
    assert p["biological_validation"]["status"] == "not_calibrated"
    for name, sha in p["integration_sha256"].items():
        assert sha == hashlib.sha256((Path(__file__).resolve().parents[1]/"flytracker"/name).read_bytes()).hexdigest()
    assert d["applied_control"]["end_ms"] - d["applied_control"]["start_ms"] == 5
    assert "decoded_acceleration" not in d["applied_control"]


def test_generated_demos_share_one_motor_without_selecting_for_escape_success():
    from scripts.record_neural_demo_suite import demo_specs, verify_episode
    specs = demo_specs({'env': {}}, 'local')
    assert {s.config.neural.dynamics for s in specs} == {'neuromechanical'}
    assert specs[1].config.neural.lesion == 'DNg02'
    assert not specs[5].config.stimulus.enabled
    # No-response observations are valid evidence, not failed demonstrations.
    state = dict(velocity=[0, 0, 0], quaternion=[1, 0, 0, 0], angular_velocity=[0, 0, 0],
                 left_input_hz=0, right_input_hz=0, dnp06_left_hz=0, dnp06_right_hz=0,
                 boundary_corrections=0)
    ep = dict(meta={'flyModel': 'neural', 'seed': 0, 'neural': {'connections': 1}},
              summary={'duration': 30., 'captured': False},
              frames={**{k: [[0, 0, 0]] for k in ('fly','flyHeading','aimerC','aimerLook')},
                      't': [30.], 'neuralDiagnostics': [state], 'neuralPhase': ['normal']},
              diagnostics={'stimulus': {'event_count': 0}, 'phaseEvents': []})
    assert verify_episode(ep, specs[2])['escapes'] == 0


def test_retained_current_record_config_loads_but_retired_models_do_not():
    from flytracker import EnvConfig, StimulusConfig
    old_neutral = dict(dynamics="neuromechanical", motion_profile="basic",
                       wall_lookahead=.25, wall_accel=1., wall_turn_rate=2.)
    assert EnvConfig.from_dict({"neural": old_neutral, "stimulus": {"release_ms": 200}}).neural == NeuralConfig()
    with pytest.raises(ValueError):
        EnvConfig.from_dict({"neural": dict(old_neutral, dynamics="source")})
    with pytest.raises(ValueError):
        EnvConfig.from_dict({"neural": dict(old_neutral, motion_profile="inspection-3d")})
    with pytest.raises(ValueError):
        StimulusConfig(mode="beam")


def test_ambiguous_old_config_cannot_silently_select_current_model():
    from flytracker import EnvConfig
    with pytest.raises(ValueError):
        EnvConfig.from_dict({"neural": {"motion_profile": "basic"}})
