"""행동 방식과 관측 묶음을 바꾸는 wrapper, 그리고 환경을 만드는 함수."""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .aimer import ACTION_DIM
from .env import EnvConfig, FlyChaseEnv


def _axis(i: int, sign: float) -> np.ndarray:
    v = np.zeros(ACTION_DIM, dtype=np.float32)
    v[i] = sign
    return v


# 한 step 에 축 하나만 돌리는 이산 행동 5개. 순서가 행동 번호다.
DISCRETE_ACTIONS: tuple[tuple[str, np.ndarray], ...] = (
    ("idle", np.zeros(ACTION_DIM, dtype=np.float32)),
    ("yaw_left", _axis(0, 1.0)),
    ("yaw_right", _axis(0, -1.0)),
    ("pitch_up", _axis(1, 1.0)),
    ("pitch_down", _axis(1, -1.0)),
)


class DiscreteActions(gym.ActionWrapper):
    """DQN 처럼 이산 행동만 받는 알고리즘용."""

    def __init__(self, env: gym.Env):
        super().__init__(env)
        self.action_space = spaces.Discrete(len(DISCRETE_ACTIONS))

    def action(self, action):
        return DISCRETE_ACTIONS[int(action)][1]


def make_env(config: EnvConfig | None = None, action_mode: str = "continuous", frame_stack: int = 1, fly=None) -> gym.Env:
    """조준기 쪽 환경. action_mode 는 'continuous' 또는 'discrete'. frame_stack 이 2 이상이면 최근 관측을 쌓는다.

    fly 는 학습한 초파리 player 다(players.py). None 이면 규칙 초파리.
    """
    env: gym.Env = FlyChaseEnv(config, fly=fly)
    if action_mode == "discrete":
        env = DiscreteActions(env)
    elif action_mode != "continuous":
        raise ValueError(f"action_mode must be 'continuous' or 'discrete', got {action_mode!r}")
    if frame_stack > 1:
        env = gym.wrappers.FrameStackObservation(env, frame_stack)
    return env
