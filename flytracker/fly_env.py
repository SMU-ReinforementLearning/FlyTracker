"""초파리 쪽에서 학습하는 Gymnasium 환경.

조준기 자리에는 기준선(기본)이나 학습을 멈춘 조준기 모델이 player 로 들어간다. 시뮬레이션은 FlyChaseEnv 와 같은 것을 쓴다.
관측은 FLY_OBS_FIELDS(17차원, fly_reaction_delay 만큼 늦게), 행동은 FLY_ACTION_NAMES(4차원),
보상은 EnvConfig.fly_reward 다. 에피소드는 조준기 쪽과 같이 포획되거나 시간이 다 되면 끝난다.
"""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .env import FLY_ACTION_DIM, FLY_OBS_FIELDS, EnvConfig, FlyChaseEnv, _bounds
from .players import baseline_player


class _Relay:
    """FlyEscapeEnv.step 이 받은 행동을 FlyChaseEnv 의 초파리 자리에 그대로 넘긴다."""

    def __init__(self):
        self.action = np.zeros(FLY_ACTION_DIM)

    def reset(self) -> None:
        self.action = np.zeros(FLY_ACTION_DIM)

    def act(self, obs) -> np.ndarray:
        return self.action


class FlyEscapeEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, config: EnvConfig | None = None, aimer=None):
        """aimer 는 조준기 player 다(players.py). None 이면 기준선."""
        super().__init__()
        self._relay = _Relay()
        self.core = FlyChaseEnv(config, fly=self._relay)
        self.config = self.core.config
        self.aimer_player = aimer if aimer is not None else baseline_player(self.config)
        self.action_space = spaces.Box(-1.0, 1.0, shape=(FLY_ACTION_DIM,), dtype=np.float32)
        low, high = _bounds(FLY_OBS_FIELDS)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        self._aimer_obs: np.ndarray | None = None

    @property
    def captured(self) -> bool:
        return self.core.captured

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self._aimer_obs, info = self.core.reset(seed=seed, options=options)
        self.aimer_player.reset()
        return self.core.fly_observation(), info

    def step(self, action):
        self._relay.action = np.asarray(action, dtype=float)
        aimer_action = self.aimer_player.act(self._aimer_obs)
        self._aimer_obs, aimer_reward, terminated, truncated, info = self.core.step(aimer_action)
        info = {**info, "aimer_reward": aimer_reward}
        return self.core.fly_observation(), self.core.fly_reward(), terminated, truncated, info

    def snapshot(self) -> dict:
        """EpisodeRecorder 가 기록하는 상태. 조준기 쪽과 같다."""
        return self.core.snapshot()


def make_fly_env(config: EnvConfig | None = None, aimer=None, frame_stack: int = 1) -> gym.Env:
    """초파리 쪽 환경. frame_stack 이 2 이상이면 최근 초파리 관측을 쌓는다."""
    env: gym.Env = FlyEscapeEnv(config, aimer)
    if frame_stack > 1:
        env = gym.wrappers.FrameStackObservation(env, frame_stack)
    return env
