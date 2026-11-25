from dataclasses import replace
import numpy as np
import pytest
from flytracker.env import EnvConfig
from flytracker.neural_fly import NeuralConfig
from flytracker.neural_training import calibrated_config, WeightedEnv, GroupedWeights, PROFILE

def test_profile_roundtrip_and_new_default_applied():
    cfg=calibrated_config(max_seconds=.04)
    assert EnvConfig.from_dict(cfg.to_dict())==cfg
    assert NeuralConfig().physics_overrides==PROFILE
    env=WeightedEnv(cfg); env.reset(seed=8)
    assert env.fly.sim.physics.drag_coefficient==PROFILE["drag_coefficient"]
    assert env.recording_metadata()["neural"]["settings"]["profile_id"]==cfg.neural.profile_id
    env.close()

@pytest.mark.parametrize("overrides",[{"bad":1},{"drag_coefficient":0},{"drag_coefficient":float("nan")}])
def test_reject_invalid_override(overrides):
    with pytest.raises(ValueError):NeuralConfig(physics_overrides=overrides)

def test_weights_affect_actual_lif_keep_sign_and_reset_reproducible(tmp_path):
    cfg=calibrated_config(max_seconds=.04)
    env=WeightedEnv(cfg); obs,_=env.reset(seed=91)
    original=env.fly.sim.neural.weights.copy()
    identity=GroupedWeights.identity(env)
    weights=identity.updated(np.full_like(identity.theta,.2))
    weights.save(tmp_path/"weights.npz")
    loaded=GroupedWeights.load(tmp_path/"weights.npz")
    env.weights=loaded
    env.reset(seed=91)
    assert np.allclose(env.fly.sim.neural.weights,original*np.exp(.2))
    with pytest.raises(ValueError):loaded.apply(env)
    assert np.array_equal(np.sign(original),np.sign(env.fly.sim.neural.weights))
    with pytest.raises(FileExistsError):weights.save(tmp_path/"weights.npz")
    a=env.step(np.array([0,0,-1.])); state=env.fly.pos.copy()
    with pytest.raises(ValueError):loaded.apply(env)
    env.reset(seed=91); b=env.step(np.array([0,0,-1.]))
    assert np.array_equal(a[0],b[0]) and np.array_equal(state,env.fly.pos)
    assert env.recording_metadata()["neural"]["learned_weights"]["groups"]==len(weights.theta)
    env.close()

def test_wrong_contract_rejected():
    env=WeightedEnv(calibrated_config(max_seconds=.02));env.reset(seed=1)
    weights=GroupedWeights.identity(env)
    weights.signature["edgeOrder"]="changed"
    with pytest.raises(ValueError):weights.apply(env)
    env.close()
