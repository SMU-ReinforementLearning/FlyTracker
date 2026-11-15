"""Gymnasium 환경. 방 안 정해진 자리의 조준기(고정 포대)가 초파리를 겨눈다.

행동은 조준 방향을 돌리는 연속 2차원(`aimer.ACTION_NAMES`)이다. 이산 행동은 `wrappers.DiscreteActions` 로 감싼다.
관측은 조준기가 자기 시야로 아는 정보와 자기 상태뿐이다. 3인칭 viewer 가 보여 주는 정보는 넣지 않는다.

초파리 자리에는 규칙 초파리(기본) 또는 학습한 초파리를 넣는다. 학습한 초파리는 `fly` 인자로 넘기는 player 이고,
step 마다 초파리 관측(`FLY_OBS_FIELDS`)을 받아 회피 행동(`FLY_ACTION_NAMES`)을 돌려준다.
초파리 쪽에서 학습하는 환경은 `fly_env.FlyEscapeEnv` 다.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import asdict, dataclass, field, fields

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .aimer import ACTION_DIM, Aimer, AimerLimits
from .camera import CameraIntrinsics, Projection, project
from .fly import Fly, FlyParams
from .geometry import unit, wrap_angle, yaw_pitch_of
from .neural_fly import NeuralConfig, NeuralFly
from .stimulus import StimulusConfig, StimulusScheduler
from .world import UP, Room

# 환경 버전. 관측, 행동, 보상, 물리 제한처럼 학습한 모델이 기대는 가정이 바뀌면 올린다.
# 실행마다 config.json 의 envVersion 에 적히고, 버전이 다른 모델끼리는 견주지 않는다.
# 1: #33 까지. pitch 제한 80°.
# 2: #34. pitch 제한 89°. 학습한 초파리를 넣는 자리, 초파리 관측(초록 레이저로 조준선을 봄, 0.06초 늦게), 초파리 보상.
# 3: #42. 포획을 레이저 명중으로 바꿈. 조준 오차 3° 에 0.2초 → 초파리 중심에서 빔까지 1.25mm 에 0.15초.
# 4: #45. pitch 제한 90°. 조준기 관측에 초파리 방향의 각속도(target_rate)와 가운데를 확대한 조준 오차(uv_fine)를 넣음.
ENV_VERSION = 4


@dataclass(frozen=True)
class RewardWeights:
    """step 마다 받는 보상의 가중치. 출발값이며 실험하며 고친다.

    추적 보상을 모두 벌점으로 둔 이유: 보이는 동안 + 보상을 주면 포획을 미루는 편이 이득이 될 수 있다.
    """

    time: float = 0.01  # 매 step 벌점
    angle: float = 0.05  # 보일 때, 조준 오차 / 세로 반시야각 (최대 1)
    lost: float = 0.15  # 안 보일 때 고정 벌점
    action_change: float = 0.01  # 이전 행동과의 차이 제곱 평균
    capture: float = 10.0  # 포획 보상


@dataclass(frozen=True)
class FlyRewardWeights:
    """학습한 초파리가 step 마다 받는 보상의 가중치. 시작값이며 초파리 담당이 고친다.

    조준기 보상의 부호를 뒤집은 값이다. 조준기의 행동 변화 벌점은 초파리와 상관없어서 뺐다.
    """

    time: float = 0.01  # 버틴 step 마다
    angle: float = 0.05  # 조준기에 보일 때, 조준 오차 / 세로 반시야각 (최대 1)
    lost: float = 0.15  # 조준기에 안 보일 때
    capture: float = 10.0  # 포획되면 잃는다


@dataclass(frozen=True)
class EnvConfig:
    room: Room = field(default_factory=Room)
    camera: CameraIntrinsics = field(default_factory=CameraIntrinsics)
    aimer: AimerLimits = field(default_factory=AimerLimits)
    fly: FlyParams = field(default_factory=FlyParams)
    reward: RewardWeights = field(default_factory=RewardWeights)
    fly_reward: FlyRewardWeights = field(default_factory=FlyRewardWeights)
    fly_reaction_delay: float = 0.06  # s. 학습한 초파리는 이만큼 전의 관측을 받는다. 규칙 초파리의 evade_reaction 과 같은 값
    dt: float = 0.01  # 물리 step (s)
    frame_skip: int = 2  # 행동 하나를 몇 물리 step 동안 유지하나
    max_seconds: float = 10.0
    turret_pos: tuple[float, float, float] = (0.0, 0.1, 0.0)  # m. 조준기 자리. 기본은 바닥 정가운데, 회전축 높이 0.1m
    # 포획은 레이저 명중이다. 값의 근거는 docs/issues/feature/42-feature-laser-hit-capture/laser-capture-condition.md
    capture_radius: float = 0.00125  # m. 초파리 중심에서 빔 중심선까지 이 거리 안이면 맞은 것이다. 빔 지름 2.5mm 의 절반
    capture_range: float | None = None  # m. None 이면 거리 조건 없음
    capture_hold: float = 0.15  # s. 이 시간 동안 이어서 맞아야 포획. 치사 에너지 74mJ ÷ 출력 500mW
    fine_error_deg: float = 0.5  # 도. 관측 uv_fine 이 ±1 로 나타내는 범위. 2m 에서 약 ±17mm
    min_start_distance: float = 1.5  # m. 시작할 때 초파리와 조준기 사이 최소 거리
    start_facing_fly: bool = False  # True 면 초파리를, False 면 방 가운데 쪽(바로 아래면 −z)을 수평으로 바라보며 시작한다
    memory_horizon: float = 2.0  # s. 놓친 뒤 지난 시간을 이 값으로 나눈다
    fly_model: str = "rule"
    neural: NeuralConfig = field(default_factory=NeuralConfig)
    stimulus: StimulusConfig = field(default_factory=StimulusConfig)
    capture_enabled: bool = True

    def __post_init__(self):
        if type(self.capture_enabled) is not bool:
            raise ValueError("capture_enabled must be boolean")
        if self.fly_model not in ("rule", "neural"):
            raise ValueError("fly_model must be rule or neural")
        if self.fly_model == "neural":
            if self.dt != 0.01 or type(self.frame_skip) is not int or self.frame_skip != 2:
                raise ValueError("Neural mode requires dt=0.01 and frame_skip=2 (10 ms capture / 20 ms actions)")
            ticks = self.max_seconds / 0.01
            if not math.isfinite(ticks) or ticks <= 0 or not math.isclose(ticks, round(ticks), rel_tol=0, abs_tol=1e-8):
                raise ValueError("Neural max_seconds must be a positive multiple of 10 ms")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EnvConfig":
        nested = {
            "room": Room,
            "camera": CameraIntrinsics,
            "aimer": AimerLimits,
            "fly": FlyParams,
            "reward": RewardWeights,
            "fly_reward": FlyRewardWeights,
            "neural": NeuralConfig,
            "stimulus": StimulusConfig,
        }
        kwargs = {}
        for f in fields(cls):
            if f.name not in d:
                continue
            if f.name in nested:
                kwargs[f.name] = (NeuralConfig.from_dict(d[f.name]) if f.name == "neural" else\
                                  StimulusConfig.from_dict(d[f.name]) if f.name == "stimulus" else\
                                  nested[f.name](**d[f.name]))
            elif f.name == "turret_pos":
                kwargs[f.name] = tuple(d[f.name])  # JSON 에서는 list 로 돌아온다
            else:
                kwargs[f.name] = d[f.name]
        return cls(**kwargs)


# 관측 벡터 배치. 규칙 기반 조준기와 테스트가 이 이름으로 값을 꺼낸다.
OBS_FIELDS: tuple[tuple[str, int, float, float], ...] = (
    ("visible", 1, 0.0, 1.0),
    ("uv", 2, -1.0, 1.0),  # 보이면 화면 정규 좌표, 아니면 0
    ("distance", 1, 0.0, 1.0),  # 보이면 거리 / 방 대각선, 아니면 0
    # 보이면 조준기에서 본 초파리 방향이 도는 각속도 (yaw, pitch) / 조준기 최대 각속도, 아니면 0. 행동과 같은 눈금이라
    # 이 값을 그대로 행동으로 내면 초파리와 같은 각속도로 돈다. 지금은 참값이다. 검출 오차를 넣을 때(#13) 추정값으로 바꾼다.
    ("target_rate", 2, -1.0, 1.0),
    # 보이면 화면 가운데에서 벗어난 각 (가로, 세로) / fine_error_deg, 아니면 0. uv 의 가운데만 확대한 값이다.
    # 레이저 명중은 2m 에서 0.036° 안이라 uv 로는 0.002 차이다. 이 값으로는 약 0.07 이다.
    ("uv_fine", 2, -1.0, 1.0),
    ("last_seen_dir", 3, -1.0, 1.0),  # 마지막으로 본 위치의 방향 (카메라 r, u, f 축). 본 적 없으면 0
    ("time_since_seen", 1, 0.0, 1.0),  # 놓친 뒤 지난 시간 / memory_horizon
    ("yaw_sincos", 2, -1.0, 1.0),
    ("pitch", 1, -1.0, 1.0),  # pitch / 최대 pitch
    ("yaw_rate", 1, -1.0, 1.0),
    ("pitch_rate", 1, -1.0, 1.0),
)


def _slices(layout: tuple[tuple[str, int, float, float], ...]) -> dict[str, slice]:
    out, i = {}, 0
    for name, n, _, _ in layout:
        out[name] = slice(i, i + n)
        i += n
    return out


def _bounds(layout: tuple[tuple[str, int, float, float], ...]) -> tuple[np.ndarray, np.ndarray]:
    low = np.concatenate([np.full(n, lo) for _, n, lo, _ in layout]).astype(np.float32)
    high = np.concatenate([np.full(n, hi) for _, n, _, hi in layout]).astype(np.float32)
    return low, high


OBS = _slices(OBS_FIELDS)
OBS_DIM = sum(n for _, n, _, _ in OBS_FIELDS)

# 학습한 초파리의 관측 벡터 배치. 시작값이며 초파리 담당이 고친다.
# 방향은 초파리 몸 기준 (오른쪽, 위, 앞) 세 값이다. 앞은 진행 방향을 수평으로 눕힌 방향, 위는 방의 위(+y)다.
# 조준선에는 초록 레이저가 켜져 있다고 두어서 초파리가 조준선을 본다. 초파리는 빨간빛을 잘 보지 못해서 초록으로 둔다.
# 모든 값은 fly_reaction_delay 만큼 늦게 받는다.
FLY_OBS_FIELDS: tuple[tuple[str, int, float, float], ...] = (
    ("turret_dir", 3, -1.0, 1.0),  # 초파리에서 조준기 쪽 방향
    ("turret_dist", 1, 0.0, 1.0),  # 조준기까지 거리 / 방 대각선
    ("laser_dir", 3, -1.0, 1.0),  # 레이저 빔에서 가장 가까운 점 쪽 방향. 빔 위에 있으면 0
    ("laser_dist", 1, 0.0, 1.0),  # 그 점까지 거리 / 방 대각선
    ("aim_error", 1, 0.0, 1.0),  # 조준선이 조준기에서 본 초파리 방향과 이루는 각 / 180°
    ("climb", 1, -1.0, 1.0),  # 진행 방향의 y 성분 / max_climb
    ("speed", 1, 0.0, 1.0),  # 회피 가속까지 반영한 속도 / (speed_max × evade_speed_gain)
    ("room_pos", 3, -1.0, 1.0),  # 방 안 위치. 축마다 양쪽 벽이 −1 과 1
    ("heading_sincos", 2, -1.0, 1.0),  # 진행 방향의 수평 각 (sin, cos). 조준기 yaw 와 같은 규약
    ("escape_ready", 1, 0.0, 1.0),  # 지금 회피를 시작할 수 있으면 1
)
FLY_OBS = _slices(FLY_OBS_FIELDS)
FLY_OBS_DIM = sum(n for _, n, _, _ in FLY_OBS_FIELDS)

# 학습한 초파리의 행동. 모두 −1 ~ 1 이다. 평소 비행은 규칙대로 하고 회피만 정한다.
# escape: 0 보다 크면 지금 피한다 (cooldown 중이면 무시). turn: × 180°, 진행 방향 기준 수평 선회각, + 가 왼쪽.
# climb: × max_climb, 회피 방향의 y 성분. speed_gain: −1 → 1배, 1 → evade_speed_gain 배.
FLY_ACTION_NAMES = ("escape", "turn", "climb", "speed_gain")
FLY_ACTION_DIM = len(FLY_ACTION_NAMES)


class FlyChaseEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, config: EnvConfig | None = None, fly=None):
        """fly 는 학습한 초파리 player 다. reset() 과 act(초파리 관측) -> 행동 을 가진다. None 이면 규칙 초파리."""
        super().__init__()
        self.config = config or EnvConfig()
        if not self.config.room.contains(np.asarray(self.config.turret_pos, dtype=float)):
            raise ValueError(f"turret_pos {self.config.turret_pos} is outside the room")
        if fly is not None and self.config.fly_model != "rule":
            # 학습한 초파리는 규칙 초파리의 회피 명령(command_escape)으로 움직인다. 신경 초파리에는 그 자리가 없다.
            raise ValueError("A learned fly player requires fly_model='rule'")
        self.action_space = spaces.Box(-1.0, 1.0, shape=(ACTION_DIM,), dtype=np.float32)
        low, high = _bounds(OBS_FIELDS)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        self._obs_low, self._obs_high = low, high
        self._fly_obs_low, self._fly_obs_high = _bounds(FLY_OBS_FIELDS)
        self.aimer = Aimer(self.config.aimer)
        self.fly: Fly | NeuralFly | None = None
        self._stimulus: StimulusScheduler | None = None
        self.fly_player = fly
        self._proj: Projection | None = None
        step_time = self.config.dt * self.config.frame_skip
        self._fly_delay_steps = max(0, round(self.config.fly_reaction_delay / step_time))

    # Gymnasium API

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        cfg, rng = self.config, self.np_random
        room = cfg.room
        aimer_pos = np.asarray(cfg.turret_pos, dtype=float)
        self.fly = Fly(cfg.fly, rng) if cfg.fly_model == "rule" else NeuralFly(cfg.neural, rng)
        self._stimulus = StimulusScheduler(cfg.stimulus) if cfg.fly_model == "neural" else None
        fly_pos = room.sample(rng, margin=0.4)
        for _ in range(100):
            if np.linalg.norm(fly_pos - aimer_pos) >= cfg.min_start_distance:
                break
            fly_pos = room.sample(rng, margin=0.4)
        fly_heading = unit(np.array([rng.normal(), rng.normal() * 0.2, rng.normal()]))
        self.fly.reset(fly_pos, fly_heading)
        self.fly.external_escape = self.fly_player is not None

        if cfg.start_facing_fly:
            d = unit(fly_pos - aimer_pos)
            yaw = math.atan2(-d[0], -d[2])
            pitch = float(np.clip(math.asin(d[1]), -math.radians(cfg.aimer.max_pitch_deg), math.radians(cfg.aimer.max_pitch_deg)))
        else:  # 방 가운데 쪽을 수평으로 바라본다. 방 가운데 바로 아래면 −z 를 본다
            d = room.center - aimer_pos
            yaw = math.atan2(-d[0], -d[2]) if math.hypot(d[0], d[2]) > 1e-6 else 0.0
            pitch = 0.0
        self.aimer.reset(aimer_pos, yaw, pitch)

        self.t = 0.0
        self.steps = 0
        self.captured = False
        self._capture_timer = 0.0
        self._last_seen_pos: np.ndarray | None = None
        self._time_since_seen = cfg.memory_horizon
        self._prev_action = np.zeros(ACTION_DIM)
        self._target_angles: tuple[float, float] | None = None
        self._target_rate = np.zeros(2)
        self._update_vision()
        now = self._fly_obs_now()
        self._fly_obs_buf = deque([now] * (self._fly_delay_steps + 1), maxlen=self._fly_delay_steps + 1)
        if self.fly_player is not None and hasattr(self.fly_player, "reset"):
            self.fly_player.reset()
        return self._observation(), self._info()

    def step(self, action):
        cfg = self.config
        a = np.clip(np.asarray(action, dtype=float).reshape(ACTION_DIM), -1.0, 1.0)
        if self.fly_player is not None:  # 학습한 초파리는 늦게 받은 관측으로 이번 step 의 회피를 정한다
            self.apply_fly_action(self.fly_player.act(self.fly_observation()))
        for _ in range(cfg.frame_skip):
            if self._stimulus is None:
                # Preserve the original rule path, including RNG and integration.
                self.aimer.step(a, cfg.dt)
                self.fly.step(cfg.dt, cfg.room, self.aimer.pos)
                self.t += cfg.dt
            else:
                for _ in range(2):
                    tick = self.fly.sim.clock.tick
                    view = project(self.fly.pos, self.aimer.pos, self.aimer.look, cfg.camera, self.aimer.basis)
                    event = self._stimulus.advance(tick, view.visible, view.angle_error, self.aimer.pos)
                    self.fly.present_stimulus(event, cfg.stimulus)
                    self.fly.step(0.005, cfg.room)
                    self.aimer.step(a, 0.005)
                    if self._stimulus.tick_ms != self.fly.sim.clock.tick:
                        raise RuntimeError("Stimulus/body clock mismatch")
                self.t = self.fly.sim.clock.tick / 1000
            self._update_vision()
            if cfg.capture_enabled and self._capture_timer >= cfg.capture_hold - 1e-9:
                self.captured = True
                break
            if (self._stimulus is not None or not cfg.capture_enabled) and self.t >= cfg.max_seconds - 1e-9:
                # Neural horizons are on the 10 ms grid, including an odd final
                # half-action. Do not overrun a supported 30 ms horizon to 40 ms.
                break
        self.steps += 1
        self._fly_obs_buf.append(self._fly_obs_now())

        reward = self._reward(a)
        self._prev_action = a
        terminated = self.captured
        truncated = (not terminated) and self.t >= cfg.max_seconds - 1e-9
        return self._observation(), reward, terminated, truncated, self._info()

    # 학습한 초파리

    def fly_observation(self) -> np.ndarray:
        """학습한 초파리가 지금 받는 관측. fly_reaction_delay 만큼 전의 값이다."""
        return self._fly_obs_buf[0].astype(np.float32)

    def apply_fly_action(self, action) -> bool:
        """초파리 행동(FLY_ACTION_NAMES)을 회피 명령으로 바꿔 준다. 회피를 시작했으면 True."""
        a = np.clip(np.asarray(action, dtype=float).reshape(FLY_ACTION_DIM), -1.0, 1.0)
        if a[0] <= 0.0:
            return False
        p = self.config.fly
        return self.fly.command_escape(
            turn=float(a[1]) * math.pi,
            climb=float(a[2]) * p.max_climb,
            speed_gain=1.0 + (float(a[3]) + 1.0) / 2.0 * (p.evade_speed_gain - 1.0),
        )

    def fly_reward(self) -> float:
        """직전 step 에 학습한 초파리가 받는 보상. 조준기 보상의 부호를 뒤집은 값에서 행동 변화 벌점을 뺐다."""
        w = self.config.fly_reward
        r = w.time + (w.angle * self._aim_error_ratio() if self._proj.visible else w.lost)
        if self.captured:
            r -= w.capture
        return float(r)

    # 기록용 상태. viewer 가 그리는 값이며 관측에는 쓰지 않는다.

    def snapshot(self) -> dict:
        proj = self._proj
        return {
            "t": self.t,
            "fly": self.fly.pos.tolist(),
            "flyHeading": self.fly.heading.tolist(),  # viewer 가 초파리 모델을 진행 방향으로 돌린다
            "aimerC": self.aimer.pos.tolist(),
            "aimerLook": self.aimer.look.tolist(),
            "aimerAngles": [self.aimer.yaw, self.aimer.pitch],  # rad. 바로 위를 볼 때는 aimerLook 만으로 yaw 를 알 수 없다
            "visible": proj.visible,
            "uv": proj.uv.tolist() if proj.in_front else [0.0, 0.0],
            "angleErrDeg": math.degrees(proj.angle_error),
            "beamDistMm": self._beam_dist * 1000,  # 초파리 중심에서 빔까지. 4자리로 반올림해 저장하므로 mm 로 둔다
            "distance": proj.distance,
            "alarmed": self.fly.alarmed,
            "captureProgress": min(self._capture_timer / self.config.capture_hold, 1.0),
        }

    # 내부 계산

    def recording_metadata(self) -> dict:
        observation = {} if self.config.capture_enabled else {
            "mode": "tracking-observation", "aimerEnabled": True, "captureEnabled": False,
            "flyModel": self.config.fly_model,
        }
        if self._stimulus is None:
            return observation
        return {**observation, "flyModel": "neural", "neural": self.fly.provenance(),
                "stimulus": asdict(self.config.stimulus),
                "aimerIntegrationDt": 0.005, "visionCaptureDt": 0.01,
                "policyDependentTrajectory": self.config.stimulus.enabled and self.config.stimulus.max_events > 0}

    def recording_diagnostics(self) -> dict:
        if self._stimulus is None:
            return {}
        return {"stimulus": self._stimulus.diagnostics(),
                "phaseEvents": [e.copy() for e in self.fly.phase_events],
                "finalNeural": self.fly.diagnostics()}

    def _update_vision(self) -> None:
        cfg = self.config
        proj = project(self.fly.pos, self.aimer.pos, self.aimer.look, cfg.camera, self.aimer.basis)
        self._proj = proj
        # 조준기에서 본 초파리 방향이 직전 물리 step 부터 돈 각을 시간으로 나눈다. 두 경로 모두 cfg.dt 마다 여기에 온다.
        angles = yaw_pitch_of(self.fly.pos - self.aimer.pos)
        if self._target_angles is not None:
            prev = self._target_angles
            self._target_rate = np.array([wrap_angle(angles[0] - prev[0]), angles[1] - prev[1]]) / cfg.dt
        self._target_angles = angles
        if proj.visible:
            self._last_seen_pos = self.fly.pos.copy()
            self._time_since_seen = 0.0
        else:
            self._time_since_seen = min(self._time_since_seen + cfg.dt, cfg.memory_horizon)
        self._beam_dist = float(np.linalg.norm(self._to_beam()))
        in_capture = (
            cfg.capture_enabled
            and proj.visible
            and self._beam_dist <= cfg.capture_radius
            and (cfg.capture_range is None or proj.distance <= cfg.capture_range)
        )
        self._capture_timer = self._capture_timer + cfg.dt if in_capture else 0.0

    def _to_beam(self) -> np.ndarray:
        """초파리 중심에서 빔 위의 가장 가까운 점으로 가는 벡터. 빔은 조준기에서 앞으로만 나간다."""
        fly, aimer = self.fly, self.aimer
        along = max(0.0, float((fly.pos - aimer.pos) @ aimer.look))
        return aimer.pos + aimer.look * along - fly.pos

    def _aim_error_ratio(self) -> float:
        """조준 오차 / 세로 반시야각. 1 에서 자른다."""
        half_fov = math.radians(self.config.camera.fov_v_deg) / 2
        return min(self._proj.angle_error / half_fov, 1.0)

    def _reward(self, a: np.ndarray) -> float:
        w, proj = self.config.reward, self._proj
        r = -w.time
        if proj.visible:
            r -= w.angle * self._aim_error_ratio()
        else:
            r -= w.lost
        r -= w.action_change * float(np.mean((a - self._prev_action) ** 2))
        if self.captured:
            r += w.capture
        return float(r)

    def _observation(self) -> np.ndarray:
        cfg, proj, aimer = self.config, self._proj, self.aimer
        lim = cfg.aimer
        o = np.zeros(OBS_DIM, dtype=np.float64)
        if proj.visible:
            o[OBS["visible"]] = 1.0
            o[OBS["uv"]] = proj.uv
            o[OBS["distance"]] = proj.distance / cfg.room.diagonal
            o[OBS["target_rate"]] = self._target_rate / np.radians([lim.max_yaw_rate_deg, lim.max_pitch_rate_deg])
            cam = cfg.camera
            off = np.arctan(proj.uv * [cam.tan_half_h, cam.tan_half_v])
            o[OBS["uv_fine"]] = off / math.radians(cfg.fine_error_deg)
        if self._last_seen_pos is not None:
            r, u, f = aimer.basis
            d = unit(self._last_seen_pos - aimer.pos)
            o[OBS["last_seen_dir"]] = [d @ r, d @ u, d @ f]
        o[OBS["time_since_seen"]] = self._time_since_seen / cfg.memory_horizon
        o[OBS["yaw_sincos"]] = [math.sin(aimer.yaw), math.cos(aimer.yaw)]
        o[OBS["pitch"]] = aimer.pitch / math.radians(lim.max_pitch_deg)
        o[OBS["yaw_rate"]] = aimer.yaw_rate / math.radians(lim.max_yaw_rate_deg)
        o[OBS["pitch_rate"]] = aimer.pitch_rate / math.radians(lim.max_pitch_rate_deg)
        return np.clip(o, self._obs_low, self._obs_high).astype(np.float32)

    def _fly_obs_now(self) -> np.ndarray:
        """학습한 초파리의 관측을 늦추지 않고 계산한다. 배치는 FLY_OBS_FIELDS."""
        if self._stimulus is not None:  # 신경 초파리는 이 관측을 쓰지 않는다 (player 를 받지 않는다)
            return np.zeros(FLY_OBS_DIM, dtype=np.float64)
        cfg, fly, aimer, room = self.config, self.fly, self.aimer, self.config.room
        forward = unit(np.array([fly.heading[0], 0.0, fly.heading[2]]))
        right = np.cross(forward, UP)

        def body(v: np.ndarray) -> list[float]:
            return [float(v @ right), float(v @ UP), float(v @ forward)]

        o = np.zeros(FLY_OBS_DIM, dtype=np.float64)
        to_turret = aimer.pos - fly.pos
        o[FLY_OBS["turret_dir"]] = body(unit(to_turret))
        o[FLY_OBS["turret_dist"]] = np.linalg.norm(to_turret) / room.diagonal
        to_beam = self._to_beam()
        o[FLY_OBS["laser_dir"]] = body(unit(to_beam))
        o[FLY_OBS["laser_dist"]] = np.linalg.norm(to_beam) / room.diagonal
        o[FLY_OBS["aim_error"]] = self._proj.angle_error / math.pi
        o[FLY_OBS["climb"]] = fly.heading[1] / cfg.fly.max_climb
        o[FLY_OBS["speed"]] = fly.effective_speed / max(cfg.fly.speed_max * cfg.fly.evade_speed_gain, 1e-9)
        o[FLY_OBS["room_pos"]] = (fly.pos - room.center) / (room.size / 2)
        yaw = math.atan2(-forward[0], -forward[2])
        o[FLY_OBS["heading_sincos"]] = [math.sin(yaw), math.cos(yaw)]
        o[FLY_OBS["escape_ready"]] = float(fly.escape_ready)
        return np.clip(o, self._fly_obs_low, self._fly_obs_high)

    def _info(self) -> dict:
        proj = self._proj
        info = {
            "t": self.t,
            "visible": proj.visible,
            "angle_error_deg": math.degrees(proj.angle_error),
            "beam_dist": self._beam_dist,
            "distance": proj.distance,
            "captured": self.captured,
            "fly_alarmed": self.fly.alarmed,
        }
        if self._stimulus is not None:
            info["neural"] = self.fly.diagnostics()
            info["stimulus"] = {"event_count": len(self._stimulus.events), "charge": self._stimulus.charge}
        return info
