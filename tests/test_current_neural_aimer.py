import json
import numpy as np
import pytest
from flytracker import EnvConfig,FlyChaseEnv
from flytracker.players import PolicyPlayer,baseline_player,load_opponent
from flytracker.wrappers import TrackingAssist
from flytracker.aimer_training_env import RuleFireTraining

class TwoAxis:
    def predict(self,obs,deterministic=True):
        self.observed=np.asarray(obs).copy()
        return np.array([.1,-.1]),None

def test_training_and_player_match_current_observation_and_rule_fire():
    cfg=EnvConfig(max_seconds=.04,start_facing_fly=True)
    env=RuleFireTraining(FlyChaseEnv(cfg),assist=.05)
    obs,_=env.reset(seed=91);policy=TwoAxis()
    player=PolicyPlayer(policy,rule_fire=True,strip_shot=False,assist=.05,tracker=baseline_player(cfg).policy)
    expected=player.act(obs)
    assert policy.observed.shape==(18,) and env.action_space.shape==(2,)
    env.step([.1,-.1])
    np.testing.assert_allclose(env.unwrapped._prev_action,expected)
    env.close()

def test_current_loader_preserves_shot_for_rule_fire(tmp_path,monkeypatch):
    from flytracker import players
    cfg=EnvConfig()
    (tmp_path/"model.zip").write_bytes(b"test-only")
    (tmp_path/"config.json").write_text(json.dumps(dict(envVersion=6,env=cfg.to_dict(),algo=dict(name="sac",fireMode="rule"))))
    policy=TwoAxis()
    class Loader:
        @staticmethod
        def load(*args,**kwargs):return policy
    monkeypatch.setattr(players,"algo_classes",lambda:{"sac":Loader})
    loaded=load_opponent(str(tmp_path),"aimer",cfg)
    env=FlyChaseEnv(cfg);obs,_=env.reset(seed=1)
    assert loaded.player.act(obs).shape==(3,) and loaded.fire=="rule"
    assert policy.observed.shape==(18,)
    (tmp_path/"config.json").write_text(json.dumps(dict(envVersion=4,algo=dict(name="sac",fireMode="rule"))))
    with pytest.raises(ValueError):load_opponent(str(tmp_path),"aimer",cfg)
    env.close()

def test_evaluation_uses_the_same_deployed_action_transform():
    from types import SimpleNamespace
    from flytracker.neural_training import calibrated_config,WeightedEnv
    from scripts.train_calibrated_neural import episode
    cfg=calibrated_config(max_seconds=.04,start_facing_fly=True)
    model=TwoAxis();model.action_space=SimpleNamespace(shape=(2,))
    result=episode(cfg,91,model)
    env=WeightedEnv(cfg);obs,_=env.reset(seed=91)
    player=PolicyPlayer(model,rule_fire=True,strip_shot=False,assist=.05,tracker=baseline_player(cfg).policy)
    total=0.
    while True:
        obs,reward,done,trunc,_=env.step(player.act(obs));total+=reward
        if done or trunc:break
    assert result["return_"]==pytest.approx(total)
    env.close()
