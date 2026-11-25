"""새 기본 보정 선택과 이전 설정의 실행 의미를 함께 보호한다."""
import argparse
import json
import numpy as np
import pytest
from flytracker.env import EnvConfig, FlyChaseEnv
from flytracker.neural_fly import NeuralConfig
from flytracker.flight_profiles import PROFILE, PROFILE_ID
from flytracker.neuromechanics import MechanicsParameters
from scripts._common import add_env_args, config_from_args

def test_new_api_and_common_cli_apply_empirical_coefficients():
    parser=argparse.ArgumentParser();add_env_args(parser)
    cfg=config_from_args(parser.parse_args(["--fly-model","neural","--max-seconds",".04"]))
    assert cfg.neural==NeuralConfig()
    assert cfg.neural.profile_id==PROFILE_ID
    for selected in (cfg,EnvConfig(fly_model="neural",max_seconds=.04)):
        env=FlyChaseEnv(selected);env.reset(seed=8)
        assert all(getattr(env.fly.sim.physics,k)==v for k,v in PROFILE.items())
        meta=env.recording_metadata()["neural"]
        assert meta["flight_profile"]["preregistered_gate_passed"] is False
        assert meta["flight_profile"]["data_sha256"]
        assert EnvConfig.from_dict(json.loads(json.dumps(selected.to_dict())))==selected
        env.close()

def test_explicit_original_and_old_missing_settings_stay_original():
    old=EnvConfig.from_dict({"fly_model":"neural","max_seconds":.04})
    older=EnvConfig.from_dict({"fly_model":"neural","max_seconds":.04,"neural":{}})
    parser=argparse.ArgumentParser();add_env_args(parser)
    explicit=config_from_args(parser.parse_args(["--fly-model","neural","--neural-profile","original","--max-seconds",".04"]))
    rows=[]
    for cfg in (old,older,explicit):
        assert cfg.neural.physics_overrides=={}
        env=FlyChaseEnv(cfg);obs,_=env.reset(seed=91)
        assert env.fly.sim.physics==MechanicsParameters()
        env.step([0,0,-1]);rows.append(env.fly.pos.copy());env.close()
    assert all(np.array_equal(rows[0],r) for r in rows[1:])
    assert old.neural.profile_id is None

def test_profile_names_cannot_mislabel_custom_parameters():
    with pytest.raises(ValueError,match="Named profile"):
        NeuralConfig(profile_id=PROFILE_ID,physics_overrides={"drag_coefficient":.2})
    cfg=NeuralConfig(profile_id=None,physics_overrides={"drag_coefficient":.2})
    assert cfg.physics_overrides["drag_coefficient"]==.2
    with pytest.raises(ValueError,match="Unknown"):NeuralConfig(profile_id="unknown")
    a=NeuralConfig();a.physics_overrides["drag_coefficient"]=.3
    assert NeuralConfig().physics_overrides==PROFILE

def test_angular_warning_is_counted_and_reset():
    from dataclasses import replace
    from flytracker.neural_fly import NeuralFly
    from flytracker.world import Room
    fly=NeuralFly(NeuralConfig(),np.random.default_rng(2))
    fly.reset([0,1.2,0],[0,0,-1])
    fly.sim.physics=replace(fly.sim.physics,angular_warning_rad_s=1e-12)
    fly.sim.body=replace(fly.sim.body,angular_rate=fly.backend.core.Vec3(.1,0,0))
    fly.step(.005,Room())
    assert fly.diagnostics()["angular_warning_steps"]==1
    fly.reset([0,1.2,0],[0,0,-1])
    assert fly.diagnostics()["angular_warning_steps"]==0
