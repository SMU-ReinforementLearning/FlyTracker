"""현재 18차원 관측으로 조준을 학습하고 기준선 규칙으로 발사한다."""
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from .players import baseline_player

class RuleFireTraining(gym.Wrapper):
    def __init__(self,env,assist=0.):
        super().__init__(env)
        self.action_space=spaces.Box(-1.,1.,shape=(2,),dtype=np.float32)
        self.tracker=baseline_player(env.unwrapped.config).policy
        self.obs=None
        self.assist=assist
    def reset(self,**kwargs):
        self.obs,info=self.env.reset(**kwargs)
        self.tracker.reset()
        return self.obs,info
    def step(self,action):
        full=np.append(np.asarray(action,dtype=float),0.)
        if self.assist>0:full=self.tracker.assisted(self.obs,full,self.assist)
        full[2]=1. if self.tracker.wants_fire(self.obs) else -1.
        result=self.env.step(full)
        self.obs=result[0]
        return result
