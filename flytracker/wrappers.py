"""행동 방식과 관측 묶음을 바꾸는 wrapper, 그리고 환경을 만드는 함수."""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .aimer import ACTION_DIM
from .baseline import RuleAimer
from .env import EnvConfig, FlyChaseEnv


def _axis(i: int, sign: float) -> np.ndarray:
    v = np.zeros(ACTION_DIM, dtype=np.float32)
    v[i] = sign
    return v


# 한 step 에 축 하나만 돌리거나 한 발 쏘는 이산 행동 6개. 순서가 행동 번호다.
# 한 발은 여러 step 이어지므로, 쏜 뒤에는 돌리는 행동으로 초파리를 따라갈 수 있다.
DISCRETE_ACTIONS: tuple[tuple[str, np.ndarray], ...] = (
    ("idle", np.zeros(ACTION_DIM, dtype=np.float32)),
    ("yaw_left", _axis(0, 1.0)),
    ("yaw_right", _axis(0, -1.0)),
    ("pitch_up", _axis(1, 1.0)),
    ("pitch_down", _axis(1, -1.0)),
    ("fire", _axis(2, 1.0)),
)


class DiscreteActions(gym.ActionWrapper):
    """DQN 처럼 이산 행동만 받는 알고리즘용."""

    def __init__(self, env: gym.Env):
        super().__init__(env)
        self.action_space = spaces.Discrete(len(DISCRETE_ACTIONS))

    def action(self, action):
        return DISCRETE_ACTIONS[int(action)][1]


class TrackingAssist(gym.Wrapper):
    """정책의 행동에 기준선의 추적을 더한다 (RuleAimer.assisted).

    초파리가 보이면 환경에 들어가는 행동은 추적 행동 + scale × 정책 행동이고, 안 보이면 정책 행동 그대로다.
    정책이 아무것도 배우지 않은 때에도 보이는 초파리는 빔 근처에 있게 된다.
    추적 행동은 쏘지 않으므로 쏠지는 정책의 fire 값이 정한다.
    """

    def __init__(self, env: gym.Env, scale: float):
        super().__init__(env)
        self.scale = scale
        cfg = env.unwrapped.config
        self.tracker = RuleAimer(
            max_pitch_deg=cfg.aimer.max_pitch_deg,
            max_yaw_rate_deg=cfg.aimer.max_yaw_rate_deg,
            max_pitch_rate_deg=cfg.aimer.max_pitch_rate_deg,
            fov_v_deg=cfg.camera.fov_v_deg,
            aspect=cfg.camera.aspect,
        )
        self._obs = None

    def reset(self, **kwargs):
        self._obs, info = self.env.reset(**kwargs)
        return self._obs, info

    def step(self, action):
        out = self.env.step(self.tracker.assisted(self._obs, action, self.scale))
        self._obs = out[0]
        return out


def make_env(
    config: EnvConfig | None = None, action_mode: str = "continuous", frame_stack: int = 1, fly=None, assist: float = 0.0
) -> gym.Env:
    """조준기 쪽 환경. action_mode 는 'continuous' 또는 'discrete'. frame_stack 이 2 이상이면 최근 관측을 쌓는다.

    fly 는 학습한 초파리 player 다(players.py). None 이면 규칙 초파리.
    assist 가 0 보다 크면 정책의 행동에 기준선의 추적을 더한다(TrackingAssist). 연속 행동에서만 쓴다.
    """
    env: gym.Env = FlyChaseEnv(config, fly=fly)
    if assist > 0:
        if action_mode != "continuous":
            raise ValueError("assist needs action_mode 'continuous'")
        env = TrackingAssist(env, assist)
    if action_mode == "discrete":
        env = DiscreteActions(env)
    elif action_mode != "continuous":
        raise ValueError(f"action_mode must be 'continuous' or 'discrete', got {action_mode!r}")
    if frame_stack > 1:
        env = gym.wrappers.FrameStackObservation(env, frame_stack)
    return env
