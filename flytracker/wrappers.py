"""행동 방식과 관측 묶음을 바꾸는 wrapper, 그리고 환경을 만드는 함수."""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .aimer import ACTION_DIM
from .baseline import RuleAimer
from .env import OBS, EnvConfig, FlyChaseEnv


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


CONTROLS = ("rate", "accel")  # 정책의 돌리는 행동이 뜻하는 것. rate 는 각속도, accel 은 각가속도
FIRES = ("policy", "rule")  # 쏠지를 누가 정하나. policy 는 정책, rule 은 기준선의 규칙


def accel_gain(config: EnvConfig) -> np.ndarray:
    """각가속도 행동 1 이 행동 한 번(dt × frame_skip) 동안 바꾸는 각속도. 각속도 행동과 같은 눈금 (yaw, pitch).

    기본 설정에서 yaw 0.08 (14.4°/s ÷ 180°/s), pitch 0.12 (14.4°/s ÷ 120°/s) 이다.
    """
    lim = config.aimer
    dv = lim.max_ang_accel_deg * config.dt * config.frame_skip
    return np.array([dv / lim.max_yaw_rate_deg, dv / lim.max_pitch_rate_deg])


def accel_to_rate(obs, action, gain: np.ndarray) -> np.ndarray:
    """각가속도 행동을 환경이 받는 각속도 행동으로 바꾼다. 쏘는 값은 그대로 둔다.

    목표 각속도 = 지금 각속도(관측 yaw_rate, pitch_rate) + 행동 × gain. 행동 0 이면 지금 속도로 계속 돈다.
    행동 ±1 이 조준기의 각가속도 한계와 같아서, 정책이 낼 수 있는 명령은 모두 조준기가 한 step 안에 따라간다.
    obs 는 가장 최근 관측 하나다.
    """
    o = np.asarray(obs, dtype=float)
    a = np.array(action, dtype=float)
    now = np.array([o[OBS["yaw_rate"]][0], o[OBS["pitch_rate"]][0]])
    a[:2] = np.clip(now + np.clip(a[:2], -1.0, 1.0) * gain, -1.0, 1.0)
    return a


class AccelControl(gym.Wrapper):
    """정책의 돌리는 행동을 각속도가 아니라 각가속도로 받는다 (accel_to_rate).

    각속도 행동은 탐색할 때와 마지막 조준에 같은 눈금(±1 이 최대 각속도)을 쓴다. 각가속도 행동은 한 step 에
    바꿀 수 있는 각속도만큼만 움직여서 눈금이 12배쯤 곱다. 근거는 docs/issues/chore/85-chore-sac-alone-near-miss-diagnosis/result.md
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)
        self.gain = accel_gain(env.unwrapped.config)
        self._obs = None

    def reset(self, **kwargs):
        self._obs, info = self.env.reset(**kwargs)
        return self._obs, info

    def step(self, action):
        out = self.env.step(accel_to_rate(self._obs, action, self.gain))
        self._obs = out[0]
        return out


class RuleFire(gym.Wrapper):
    """쏠지를 기준선의 규칙(RuleAimer.wants_fire)에 맡긴다. 정책은 돌리는 두 값만 낸다.

    정책의 관측에서는 shot 을 뺀다. 쏘는 것을 정책이 정하지 않으니 필요 없고, 환경 버전 5 모델을 불러올 때와 같은 모양이 된다.
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)
        cfg = env.unwrapped.config
        self.tracker = RuleAimer(
            max_pitch_deg=cfg.aimer.max_pitch_deg,
            fov_v_deg=cfg.camera.fov_v_deg,
            aspect=cfg.camera.aspect,
            fire_radius=cfg.capture_radius,
            fine_error_deg=cfg.fine_error_deg,
            room_diagonal=cfg.room.diagonal,
        )
        space = env.observation_space
        self._keep = np.delete(np.arange(space.shape[0]), np.arange(space.shape[0])[OBS["shot"]])
        self.observation_space = spaces.Box(space.low[self._keep], space.high[self._keep], dtype=np.float32)
        self.action_space = spaces.Box(-1.0, 1.0, shape=(ACTION_DIM - 1,), dtype=np.float32)
        self._obs = None

    def reset(self, **kwargs):
        self._obs, info = self.env.reset(**kwargs)
        return self._obs[self._keep], info

    def step(self, action):
        a = np.append(np.asarray(action, dtype=float), 1.0 if self.tracker.wants_fire(self._obs) else -1.0)
        obs, reward, terminated, truncated, info = self.env.step(a)
        self._obs = obs
        return obs[self._keep], reward, terminated, truncated, info


FIRE_PRIORS = ("none", "rule")  # 발사만 학습할 때 정책의 값에 규칙의 판단을 더할지
FIRE_PRIOR_BIAS = 0.5  # 규칙이 쏘라고 하면 +, 아니면 − 로 더하는 크기


def fire_decision(value: float, rule_wants: bool, prior: str) -> bool:
    """발사만 학습하는 정책의 값 하나로 쏠지를 정한다. 0 을 넘으면 쏜다.

    prior 가 'rule' 이면 규칙의 판단을 ±FIRE_PRIOR_BIAS 로 더한 뒤에 본다. 정책의 값이 0 이면 규칙과 똑같이 쏘고,
    −0.5 아래면 규칙이 쏘라고 해도 참고, +0.5 를 넘으면 규칙이 말려도 쏜다.
    """
    v = float(value)
    if prior == "rule":
        v += FIRE_PRIOR_BIAS if rule_wants else -FIRE_PRIOR_BIAS
    return v > 0.0


class FireOnly(gym.Wrapper):
    """조준은 고정한 조준기 player(aim)가 하고, 정책은 쏠지만 정한다. 행동은 값 하나다.

    aim 은 쏘는 것을 규칙에 맡긴 player 다 (players.load_opponent 로 불러온 algo.fire 가 "rule" 인 모델).
    aim 이 낸 행동의 fire 칸이 규칙의 판단이고, 이것을 정책의 값으로 바꿔 넣는다 (fire_decision).
    정책의 관측은 환경의 관측 그대로다 (shot 포함).
    """

    def __init__(self, env: gym.Env, aim, prior: str = "none"):
        super().__init__(env)
        if prior not in FIRE_PRIORS:
            raise ValueError(f"fire prior must be one of {FIRE_PRIORS}, got {prior!r}")
        self.aim, self.prior = aim, prior
        self.action_space = spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32)
        self._obs = None

    def reset(self, **kwargs):
        self.aim.reset()
        self._obs, info = self.env.reset(**kwargs)
        return self._obs, info

    def step(self, action):
        a = np.asarray(self.aim.act(self._obs), dtype=float)
        a[2] = 1.0 if fire_decision(np.asarray(action).reshape(-1)[0], a[2] > 0.0, self.prior) else -1.0
        out = self.env.step(a)
        self._obs = out[0]
        return out


def make_env(
    config: EnvConfig | None = None,
    action_mode: str = "continuous",
    frame_stack: int = 1,
    fly=None,
    assist: float = 0.0,
    control: str = "rate",
    fire: str = "policy",
    aim=None,
    fire_prior: str = "none",
) -> gym.Env:
    """조준기 쪽 환경. action_mode 는 'continuous' 또는 'discrete'. frame_stack 이 2 이상이면 최근 관측을 쌓는다.

    fly 는 학습한 초파리 player 다(players.py). None 이면 규칙 초파리.
    assist 가 0 보다 크면 정책의 행동에 기준선의 추적을 더한다(TrackingAssist). 연속 행동에서만 쓴다.
    control 이 'accel' 이면 정책의 돌리는 행동을 각가속도로 받는다(AccelControl). 연속 행동에서만 쓴다.
    fire 가 'rule' 이면 쏠지를 기준선의 규칙이 정하고 정책은 돌리는 두 값만 낸다(RuleFire). 연속 행동에서만 쓴다.
    aim 을 주면 조준은 그 player 가 하고 정책은 쏠지만 정한다(FireOnly). fire_prior 는 그때만 쓴다.
    aim 이 스스로 조종하므로 assist, control, fire 는 기본값이어야 한다.
    """
    if aim is not None:
        if action_mode != "continuous" or assist > 0 or control != "rate" or fire != "policy":
            raise ValueError("aim needs action_mode 'continuous' and default assist, control and fire")
        env = FireOnly(FlyChaseEnv(config, fly=fly), aim, fire_prior)
        return gym.wrappers.FrameStackObservation(env, frame_stack) if frame_stack > 1 else env
    if fire_prior != "none":
        raise ValueError("fire_prior needs aim")
    if control not in CONTROLS:
        raise ValueError(f"control must be one of {CONTROLS}, got {control!r}")
    if fire not in FIRES:
        raise ValueError(f"fire must be one of {FIRES}, got {fire!r}")
    if (control != "rate" or fire != "policy") and action_mode != "continuous":
        raise ValueError("control 'accel' and fire 'rule' need action_mode 'continuous'")
    env: gym.Env = FlyChaseEnv(config, fly=fly)
    if assist > 0:
        if action_mode != "continuous":
            raise ValueError("assist needs action_mode 'continuous'")
        env = TrackingAssist(env, assist)
    if control == "accel":
        env = AccelControl(env)
    if fire == "rule":
        env = RuleFire(env)
    if action_mode == "discrete":
        env = DiscreteActions(env)
    elif action_mode != "continuous":
        raise ValueError(f"action_mode must be 'continuous' or 'discrete', got {action_mode!r}")
    if frame_stack > 1:
        env = gym.wrappers.FrameStackObservation(env, frame_stack)
    return env
