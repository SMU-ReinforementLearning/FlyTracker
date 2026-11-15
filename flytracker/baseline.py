"""규칙 기반 조준기. RL 결과를 견줄 기준선이다.

관측 벡터만 보고 움직인다. 환경 내부 상태(파리의 실제 위치)는 보지 않는다.
- 보이면: 화면 좌표(u, v)에 비례해 조준선을 돌린다.
- 놓쳤으면: 국소 탐색. 마지막으로 본 방향(datum)으로 돌린 뒤, 그 방향을 가운데 두고 8자를 그리며
  한 바퀴마다 8자를 키운다. 8자는 yaw 와 pitch 의 주파수 비가 1:2 인 Lissajous 곡선이다.
  datum 에서 시작해 점점 넓히는 생각은 IAMSAR 의 확장 사각형 탐색과 섹터 탐색에서 가져왔다.
- 본 적이 없거나 국소 탐색으로 못 찾으면: 전역 탐색. yaw 를 한 방향으로 돌려 360° 를 훑고, 한 바퀴마다
  pitch 높이(띠)를 바꾼다. 띠 간격은 세로 시야각보다 조금 좁게 두어 띠끼리 겹치지 않고 빈틈도 없게 한다.
  훑는 폭만큼 간격을 두는 것은 Koopman 탐색 이론의 평행 탐색과 같은 생각이다.
근거 문헌은 docs/issues/feature/9-feature-fly-realism-search/fly-flight-and-search-model.md 에 있다.
"""

from __future__ import annotations

import math

import numpy as np

from .aimer import ACTION_DIM
from .camera import camera_basis
from .env import OBS
from .geometry import look_dir, wrap_angle


class RuleAimer:
    def __init__(
        self,
        turn_gain: float = 2.5,
        max_pitch_deg: float = 89.0,
        max_yaw_rate_deg: float = 180.0,
        max_pitch_rate_deg: float = 120.0,
        decision_dt: float = 0.02,  # 행동 한 번이 유지되는 시간 (s). 환경의 dt × frame_skip
        datum_tol_deg: float = 5.0,  # datum 에 이만큼 가까워지면 8자를 시작한다
        figure8_period: float = 1.6,  # s. 8자 한 바퀴
        figure8_amp_deg: float = 15.0,  # 첫 바퀴의 yaw 진폭. pitch 진폭은 그 절반
        figure8_growth_deg: float = 15.0,  # 한 바퀴마다 늘리는 yaw 진폭
        figure8_max_deg: float = 45.0,  # 이 진폭까지 그려도 못 찾으면 전역 탐색으로 넘어간다
        sweep_rate: float = 0.9,  # 전역 탐색의 yaw 각속도 (최대 각속도에 대한 비율)
        fov_v_deg: float = 40.0,  # 카메라 세로 시야각. 전역 탐색의 띠 간격을 정한다
        band_overlap_deg: float = 5.0,  # 이웃한 띠가 겹치는 폭
        min_pitch_deg: float = -10.0,  # 탐색할 때 이보다 아래는 보지 않는다 (바닥)
        error_full_deg: float = 30.0,  # 목표 방향과 이만큼 어긋나면 최대 각속도로 돈다
    ):
        self.turn_gain = turn_gain
        self.max_pitch = math.radians(max_pitch_deg)
        self.max_yaw_rate = math.radians(max_yaw_rate_deg)
        self.max_pitch_rate = math.radians(max_pitch_rate_deg)
        self.dt = decision_dt
        self.datum_tol = math.radians(datum_tol_deg)
        self.f8_period = figure8_period
        self.f8_amp = math.radians(figure8_amp_deg)
        self.f8_growth = math.radians(figure8_growth_deg)
        self.f8_max = math.radians(figure8_max_deg)
        self.sweep_rate = sweep_rate
        self.min_pitch = math.radians(min_pitch_deg)
        # 띠는 시야각과 조준 범위만으로 정한다. 초파리가 어디에 많은지는 기준선도 모르는 것으로 둔다.
        # 가장 낮은 띠부터 시야각에서 겹침을 뺀 간격으로 쌓는다 (Koopman: 훑는 폭만큼 띄운 평행 탐색)
        # 띠의 위 끝이 천정(90°)에 닿으면 더 쌓지 않는다. 그 위로 띠를 더 두면 제자리에서 도는 것뿐이다.
        bands, center = [], min_pitch_deg + fov_v_deg / 2
        while True:
            bands.append(math.radians(min(center, max_pitch_deg)))
            if center >= max_pitch_deg or center + fov_v_deg / 2 >= 90.0:
                break
            center += fov_v_deg - band_overlap_deg
        self.sweep_bands = tuple(bands)
        self.error_full = math.radians(error_full_deg)
        self.reset()

    def reset(self) -> None:
        """에피소드를 시작할 때 부른다. 탐색 상태를 지운다."""
        self.mode = "track"  # track | datum | figure8 | sweep
        self._f8_t = 0.0
        self._local_done = False
        self._band = 0
        self._sweep_travel = 0.0
        self._prev_yaw: float | None = None

    def predict(self, obs, state=None, episode_start=None, deterministic: bool = True):
        """Stable-Baselines3 모델과 같은 모양으로 부를 수 있게 한다."""
        return self.act(obs), state

    def act(self, obs) -> np.ndarray:
        o = np.asarray(obs, dtype=float)
        if o.ndim == 2:  # frame stack 이면 가장 최근 관측만 쓴다
            o = o[-1]
        s, c = o[OBS["yaw_sincos"]]
        yaw = math.atan2(s, c)
        pitch = float(o[OBS["pitch"]][0]) * self.max_pitch
        prev_yaw, self._prev_yaw = self._prev_yaw, yaw

        if o[OBS["visible"]][0] > 0.5:
            self.mode, self._f8_t, self._local_done = "track", 0.0, False
            u, v = o[OBS["uv"]]
            a = np.zeros(ACTION_DIM, dtype=np.float32)
            a[0] = np.clip(-self.turn_gain * u, -1, 1)  # 파리가 오른쪽(u > 0)이면 yaw 를 줄여 오른쪽으로 돈다
            a[1] = np.clip(self.turn_gain * v, -1, 1)
            return a

        last = o[OBS["last_seen_dir"]]
        if np.any(last != 0) and not self._local_done:
            return self._local_search(yaw, pitch, last)
        return self._sweep(yaw, pitch, prev_yaw)

    # 탐색

    def _local_search(self, yaw: float, pitch: float, last: np.ndarray) -> np.ndarray:
        r, u, f = camera_basis(look_dir(yaw, pitch))
        w = last[0] * r + last[1] * u + last[2] * f  # 마지막으로 본 방향 (세계 좌표)
        d_yaw, d_pitch = math.atan2(-w[0], -w[2]), math.asin(float(np.clip(w[1], -1, 1)))
        if self.mode != "figure8":
            self.mode = "datum"
            if abs(wrap_angle(d_yaw - yaw)) > self.datum_tol or abs(d_pitch - pitch) > self.datum_tol:
                return self._steer(yaw, pitch, d_yaw, d_pitch)
            self.mode, self._f8_t = "figure8", 0.0

        cycle = int(self._f8_t // self.f8_period)
        amp = self.f8_amp + self.f8_growth * cycle
        if amp > self.f8_max + 1e-9:
            self._local_done = True
            return self._sweep(yaw, pitch, None)
        w8 = 2 * math.pi / self.f8_period
        th = w8 * self._f8_t
        t_yaw = d_yaw + amp * math.sin(th)
        t_pitch = d_pitch + 0.5 * amp * math.sin(2 * th)
        ff_yaw = amp * w8 * math.cos(th)
        ff_pitch = amp * w8 * math.cos(2 * th)
        self._f8_t += self.dt
        return self._steer(yaw, pitch, t_yaw, t_pitch, ff_yaw, ff_pitch)

    def _sweep(self, yaw: float, pitch: float, prev_yaw: float | None) -> np.ndarray:
        if self.mode != "sweep":
            self.mode, self._sweep_travel = "sweep", 0.0
        elif prev_yaw is not None:
            self._sweep_travel += abs(wrap_angle(yaw - prev_yaw))
            if self._sweep_travel >= 2 * math.pi:  # 한 바퀴 돌았으면 다음 띠로
                self._band = (self._band + 1) % len(self.sweep_bands)
                self._sweep_travel = 0.0
        a = self._steer(yaw, pitch, yaw, self.sweep_bands[self._band])
        a[0] = self.sweep_rate
        return a

    def _steer(self, yaw, pitch, t_yaw, t_pitch, ff_yaw=0.0, ff_pitch=0.0) -> np.ndarray:
        """목표 방향으로 돌린다. ff 는 목표가 움직이는 각속도 (rad/s)."""
        t_pitch = min(max(t_pitch, self.min_pitch), self.max_pitch)
        a = np.zeros(ACTION_DIM, dtype=np.float32)
        a[0] = np.clip(ff_yaw / self.max_yaw_rate + wrap_angle(t_yaw - yaw) / self.error_full, -1, 1)
        a[1] = np.clip(ff_pitch / self.max_pitch_rate + (t_pitch - pitch) / self.error_full, -1, 1)
        return a
