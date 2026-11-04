"""Gymnasium 환경. 방 안에서 조준기가 초파리를 쫓는다.

행동은 연속 5차원(`aimer.ACTION_NAMES`)이다. 이산 행동은 `wrappers.DiscreteActions` 로 감싼다.
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
from .world import Room


@dataclass(frozen=True)
class RewardWeights:
    """step 마다 받는 보상의 가중치. 출발값이며 실험하며 고친다.

    추적 보상을 모두 벌점으로 둔 이유: 보이는 동안 + 보상을 주면 포획을 미루는 편이 이득이 될 수 있다.
    """

    time: float = 0.01  # 매 step 벌점
    angle: float = 0.05  # 보일 때, 조준 오차 / 세로 반시야각 (최대 1)
    distance: float = 0.05  # 보일 때, 포획 거리를 넘은 만큼 / 방 대각선 (최대 1)
    lost: float = 0.15  # 안 보일 때 고정 벌점
    collision: float = 0.1  # 벽에 부딪힌 step
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
    capture_angle_deg: float = 3.0
    capture_range: float = 0.5  # m
    capture_hold: float = 0.2  # s. 이 시간 동안 조건을 이어서 지키면 포획
    min_start_distance: float = 1.5  # m
    start_facing_fly: bool = False  # 시작할 때 조준기가 파리를 바라보게 할지
    memory_horizon: float = 2.0  # s. 놓친 뒤 지난 시간을 이 값으로 나눈다

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EnvConfig":
        nested = {"room": Room, "camera": CameraIntrinsics, "aimer": AimerLimits, "fly": FlyParams, "reward": RewardWeights}
        kwargs = {}
        for f in fields(cls):
            if f.name not in d:
                continue
            kwargs[f.name] = nested[f.name](**d[f.name]) if f.name in nested else d[f.name]
        return cls(**kwargs)


# 관측 벡터 배치. 규칙 기반 조준기와 테스트가 이 이름으로 값을 꺼낸다.
OBS_FIELDS: tuple[tuple[str, int, float, float], ...] = (
    ("visible", 1, 0.0, 1.0),
    ("uv", 2, -1.0, 1.0),  # 보이면 화면 정규 좌표, 아니면 0
    ("closeness", 1, 0.0, 2.0),  # 보이면 포획 거리 / 거리 (2 에서 자름), 아니면 0
    ("last_seen_dir", 3, -1.0, 1.0),  # 마지막으로 본 위치의 방향 (카메라 r, u, f 축). 본 적 없으면 0
    ("time_since_seen", 1, 0.0, 1.0),  # 놓친 뒤 지난 시간 / memory_horizon
    ("position", 3, -1.0, 1.0),  # 방 안 위치 (축마다 −1~1)
    ("velocity", 3, -1.0, 1.0),  # 속도 / 최대 속도
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
        self.action_space = spaces.Box(-1.0, 1.0, shape=(ACTION_DIM,), dtype=np.float32)
        low = np.concatenate([np.full(n, lo) for _, n, lo, _ in OBS_FIELDS]).astype(np.float32)
        high = np.concatenate([np.full(n, hi) for _, n, _, hi in OBS_FIELDS]).astype(np.float32)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        self._obs_low, self._obs_high = low, high
        self.aimer = Aimer(self.config.aimer)
        self.fly: Fly | None = None
        self._proj: Projection | None = None

    # Gymnasium API

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        cfg, rng = self.config, self.np_random
        room = cfg.room
        self.fly = Fly(cfg.fly, rng)
        fly_pos = room.sample(rng, margin=0.4)
        fly_heading = unit(np.array([rng.normal(), rng.normal() * 0.2, rng.normal()]))
        self.fly.reset(fly_pos, fly_heading)

        margin = cfg.aimer.radius + 0.2
        aimer_pos = room.sample(rng, margin=margin)
        for _ in range(100):
            if np.linalg.norm(aimer_pos - fly_pos) >= cfg.min_start_distance:
                break
            aimer_pos = room.sample(rng, margin=margin)
        if cfg.start_facing_fly:
            d = unit(fly_pos - aimer_pos)
            yaw = math.atan2(-d[0], -d[2])
            pitch = float(np.clip(math.asin(d[1]), -math.radians(cfg.aimer.max_pitch_deg), math.radians(cfg.aimer.max_pitch_deg)))
        else:
            yaw, pitch = float(rng.uniform(-math.pi, math.pi)), 0.0
        self.aimer.reset(aimer_pos, yaw, pitch)

        self.t = 0.0
        self.steps = 0
        self.captured = False
        self.collided = False
        self._capture_timer = 0.0
        self._last_seen_pos: np.ndarray | None = None
        self._time_since_seen = cfg.memory_horizon
        self._prev_action = np.zeros(ACTION_DIM)
        self._update_vision()
        return self._observation(), self._info()

    def step(self, action):
        cfg = self.config
        a = np.clip(np.asarray(action, dtype=float).reshape(ACTION_DIM), -1.0, 1.0)
        collided = False
        for _ in range(cfg.frame_skip):
            collided |= self.aimer.step(a, cfg.dt, cfg.room)
            self.fly.step(cfg.dt, cfg.room, self.aimer.pos, self.aimer.look)
            self.t += cfg.dt
            self._update_vision()
            if self._capture_timer >= cfg.capture_hold - 1e-9:
                self.captured = True
                break
        self.steps += 1
        self.collided = collided

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
            "aimerC": self.aimer.pos.tolist(),
            "aimerLook": self.aimer.look.tolist(),
            "visible": proj.visible,
            "uv": proj.uv.tolist() if proj.in_front else [0.0, 0.0],
            "angleErrDeg": math.degrees(proj.angle_error),
            "distance": proj.distance,
            "evading": self.fly.evading,
            "captureProgress": min(self._capture_timer / self.config.capture_hold, 1.0),
            "collided": self.collided,
        }

    # 내부 계산

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
            proj.visible
            and proj.angle_error <= math.radians(cfg.capture_angle_deg)
            and proj.distance <= cfg.capture_range
        )
        self._capture_timer = self._capture_timer + cfg.dt if in_capture else 0.0

    def _reward(self, a: np.ndarray) -> float:
        cfg, w, proj = self.config, self.config.reward, self._proj
        r = -w.time
        if proj.visible:
            half_fov = math.radians(cfg.camera.fov_v_deg) / 2
            r -= w.angle * min(proj.angle_error / half_fov, 1.0)
            r -= w.distance * min(max(proj.distance - cfg.capture_range, 0.0) / cfg.room.diagonal, 1.0)
        else:
            r -= w.lost
        if self.collided:
            r -= w.collision
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
            o[OBS["closeness"]] = min(cfg.capture_range / max(proj.distance, 1e-6), 2.0)
        if self._last_seen_pos is not None:
            r, u, f = camera_basis(aimer.look)
            d = unit(self._last_seen_pos - aimer.pos)
            o[OBS["last_seen_dir"]] = [d @ r, d @ u, d @ f]
        o[OBS["time_since_seen"]] = self._time_since_seen / cfg.memory_horizon
        o[OBS["position"]] = cfg.room.normalize(aimer.pos)
        o[OBS["velocity"]] = aimer.vel / lim.max_speed
        o[OBS["yaw_sincos"]] = [math.sin(aimer.yaw), math.cos(aimer.yaw)]
        o[OBS["pitch"]] = aimer.pitch / math.radians(lim.max_pitch_deg)
        o[OBS["yaw_rate"]] = aimer.yaw_rate / math.radians(lim.max_yaw_rate_deg)
        o[OBS["pitch_rate"]] = aimer.pitch_rate / math.radians(lim.max_pitch_rate_deg)
        return np.clip(o, self._obs_low, self._obs_high).astype(np.float32)

    def _info(self) -> dict:
        proj = self._proj
        return {
            "t": self.t,
            "visible": proj.visible,
            "angle_error_deg": math.degrees(proj.angle_error),
            "distance": proj.distance,
            "captured": self.captured,
            "collided": self.collided,
            "fly_evading": self.fly.evading,
        }
