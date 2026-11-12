"""Gymnasium 환경. 방 안 정해진 자리의 조준기(고정 포대)가 초파리를 겨눈다.

행동은 조준 방향을 돌리는 연속 2차원(`aimer.ACTION_NAMES`)이다. 이산 행동은 `wrappers.DiscreteActions` 로 감싼다.
관측은 조준기가 자기 시야로 아는 정보와 자기 상태뿐이다. 3인칭 viewer 가 보여 주는 정보는 넣지 않는다.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, fields

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .aimer import ACTION_DIM, Aimer, AimerLimits
from .camera import CameraIntrinsics, Projection, camera_basis, project
from .fly import Fly, FlyParams
from .geometry import unit
from .neural_fly import NeuralConfig, NeuralFly
from .stimulus import StimulusConfig, StimulusScheduler
from .world import Room


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
class EnvConfig:
    room: Room = field(default_factory=Room)
    camera: CameraIntrinsics = field(default_factory=CameraIntrinsics)
    aimer: AimerLimits = field(default_factory=AimerLimits)
    fly: FlyParams = field(default_factory=FlyParams)
    reward: RewardWeights = field(default_factory=RewardWeights)
    dt: float = 0.01  # 물리 step (s)
    frame_skip: int = 2  # 행동 하나를 몇 물리 step 동안 유지하나
    max_seconds: float = 10.0
    turret_pos: tuple[float, float, float] = (0.0, 0.1, 0.0)  # m. 조준기 자리. 기본은 바닥 정가운데, 회전축 높이 0.1m
    capture_angle_deg: float = 3.0
    capture_range: float | None = None  # m. None 이면 거리 조건 없음
    capture_hold: float = 0.2  # s. 이 시간 동안 조건을 이어서 지키면 포획
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
        nested = {"room": Room, "camera": CameraIntrinsics, "aimer": AimerLimits, "fly": FlyParams, "reward": RewardWeights,
                  "neural": NeuralConfig, "stimulus": StimulusConfig}
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
    ("last_seen_dir", 3, -1.0, 1.0),  # 마지막으로 본 위치의 방향 (카메라 r, u, f 축). 본 적 없으면 0
    ("time_since_seen", 1, 0.0, 1.0),  # 놓친 뒤 지난 시간 / memory_horizon
    ("yaw_sincos", 2, -1.0, 1.0),
    ("pitch", 1, -1.0, 1.0),  # pitch / 최대 pitch
    ("yaw_rate", 1, -1.0, 1.0),
    ("pitch_rate", 1, -1.0, 1.0),
)


def _obs_slices() -> dict[str, slice]:
    out, i = {}, 0
    for name, n, _, _ in OBS_FIELDS:
        out[name] = slice(i, i + n)
        i += n
    return out


OBS = _obs_slices()
OBS_DIM = sum(n for _, n, _, _ in OBS_FIELDS)


class FlyChaseEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, config: EnvConfig | None = None):
        super().__init__()
        self.config = config or EnvConfig()
        if not self.config.room.contains(np.asarray(self.config.turret_pos, dtype=float)):
            raise ValueError(f"turret_pos {self.config.turret_pos} is outside the room")
        self.action_space = spaces.Box(-1.0, 1.0, shape=(ACTION_DIM,), dtype=np.float32)
        low = np.concatenate([np.full(n, lo) for _, n, lo, _ in OBS_FIELDS]).astype(np.float32)
        high = np.concatenate([np.full(n, hi) for _, n, _, hi in OBS_FIELDS]).astype(np.float32)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        self._obs_low, self._obs_high = low, high
        self.aimer = Aimer(self.config.aimer)
        self.fly: Fly | NeuralFly | None = None
        self._stimulus: StimulusScheduler | None = None
        self._proj: Projection | None = None

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
        self._update_vision()
        return self._observation(), self._info()

    def step(self, action):
        cfg = self.config
        a = np.clip(np.asarray(action, dtype=float).reshape(ACTION_DIM), -1.0, 1.0)
        for _ in range(cfg.frame_skip):
            if self._stimulus is None:
                # Preserve the original rule path, including RNG and integration.
                self.aimer.step(a, cfg.dt)
                self.fly.step(cfg.dt, cfg.room, self.aimer.pos)
                self.t += cfg.dt
            else:
                for _ in range(2):
                    tick = self.fly.sim.clock.tick
                    view = project(self.fly.pos, self.aimer.pos, self.aimer.look, cfg.camera)
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

        reward = self._reward(a)
        self._prev_action = a
        terminated = self.captured
        truncated = (not terminated) and self.t >= cfg.max_seconds - 1e-9
        return self._observation(), reward, terminated, truncated, self._info()

    # 기록용 상태. viewer 가 그리는 값이며 관측에는 쓰지 않는다.

    def snapshot(self) -> dict:
        proj = self._proj
        return {
            "t": self.t,
            "fly": self.fly.pos.tolist(),
            "flyHeading": self.fly.heading.tolist(),  # viewer 가 초파리 모델을 진행 방향으로 돌린다
            "aimerC": self.aimer.pos.tolist(),
            "aimerLook": self.aimer.look.tolist(),
            "visible": proj.visible,
            "uv": proj.uv.tolist() if proj.in_front else [0.0, 0.0],
            "angleErrDeg": math.degrees(proj.angle_error),
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
        proj = project(self.fly.pos, self.aimer.pos, self.aimer.look, cfg.camera)
        self._proj = proj
        if proj.visible:
            self._last_seen_pos = self.fly.pos.copy()
            self._time_since_seen = 0.0
        else:
            self._time_since_seen = min(self._time_since_seen + cfg.dt, cfg.memory_horizon)
        in_capture = (
            cfg.capture_enabled
            and proj.visible
            and proj.angle_error <= math.radians(cfg.capture_angle_deg)
            and (cfg.capture_range is None or proj.distance <= cfg.capture_range)
        )
        self._capture_timer = self._capture_timer + cfg.dt if in_capture else 0.0

    def _reward(self, a: np.ndarray) -> float:
        cfg, w, proj = self.config, self.config.reward, self._proj
        r = -w.time
        if proj.visible:
            half_fov = math.radians(cfg.camera.fov_v_deg) / 2
            r -= w.angle * min(proj.angle_error / half_fov, 1.0)
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
        if self._last_seen_pos is not None:
            r, u, f = camera_basis(aimer.look)
            d = unit(self._last_seen_pos - aimer.pos)
            o[OBS["last_seen_dir"]] = [d @ r, d @ u, d @ f]
        o[OBS["time_since_seen"]] = self._time_since_seen / cfg.memory_horizon
        o[OBS["yaw_sincos"]] = [math.sin(aimer.yaw), math.cos(aimer.yaw)]
        o[OBS["pitch"]] = aimer.pitch / math.radians(lim.max_pitch_deg)
        o[OBS["yaw_rate"]] = aimer.yaw_rate / math.radians(lim.max_yaw_rate_deg)
        o[OBS["pitch_rate"]] = aimer.pitch_rate / math.radians(lim.max_pitch_rate_deg)
        return np.clip(o, self._obs_low, self._obs_high).astype(np.float32)

    def _info(self) -> dict:
        proj = self._proj
        info = {
            "t": self.t,
            "visible": proj.visible,
            "angle_error_deg": math.degrees(proj.angle_error),
            "distance": proj.distance,
            "captured": self.captured,
            "fly_alarmed": self.fly.alarmed,
        }
        if self._stimulus is not None:
            info["neural"] = self.fly.diagnostics()
            info["stimulus"] = {"event_count": len(self._stimulus.events), "charge": self._stimulus.charge}
        return info
