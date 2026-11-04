"""조준기 카메라 모델.

RackTracker 와 같은 핀홀 카메라다. 위치 C, 바라보는 방향 look, 세로 시야각과 화면비로 정한다.
보이는지 판정은 화면 정규 좌표(uv)로 한다. uv 는 −1~1 이고 x 오른쪽, y 위라서 three.js NDC 와 같다.
픽셀 좌표가 필요하면 `intrinsics_K`, `extrinsics_opencv` 로 P = K[R|t] 를 만든다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .geometry import angle_between, unit
from .world import UP


@dataclass(frozen=True)
class CameraIntrinsics:
    fov_v_deg: float = 40.0  # 세로 시야각 (도)
    aspect: float = 4 / 3  # 가로 / 세로
    near: float = 0.02  # m
    far: float = 10.0  # m

    @property
    def tan_half_v(self) -> float:
        return math.tan(math.radians(self.fov_v_deg) / 2)

    @property
    def tan_half_h(self) -> float:
        return self.aspect * self.tan_half_v


@dataclass(frozen=True)
class Projection:
    in_front: bool  # 카메라 앞(near 보다 멀리)에 있는가
    visible: bool  # 화면 안에 들어오는가
    uv: np.ndarray  # 화면 정규 좌표. 보이지 않으면 화면 밖 값일 수 있다
    depth: float  # 바라보는 방향으로 잰 거리 (m)
    distance: float  # 직선 거리 (m)
    angle_error: float  # 조준선과 대상 방향 사이 각 (rad)


def camera_basis(look: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """카메라 오른쪽 r, 위 u, 앞 f. 굴림(roll)은 없다. pitch 를 ±90° 미만으로 제한해 퇴화를 피한다."""
    f = unit(look)
    r = unit(np.cross(f, UP))
    u = np.cross(r, f)
    return r, u, f


def project(point: np.ndarray, C: np.ndarray, look: np.ndarray, intr: CameraIntrinsics) -> Projection:
    r, u, f = camera_basis(look)
    p = point - C
    xc, yc, zc = float(p @ r), float(p @ u), float(p @ f)
    distance = float(np.linalg.norm(p))
    angle = angle_between(f, p) if distance > 1e-9 else 0.0
    if zc <= intr.near:
        return Projection(False, False, np.zeros(2), zc, distance, angle)
    uv = np.array([xc / zc / intr.tan_half_h, yc / zc / intr.tan_half_v])
    visible = bool(abs(uv[0]) <= 1.0 and abs(uv[1]) <= 1.0 and zc <= intr.far)
    return Projection(True, visible, uv, zc, distance, angle)


def intrinsics_K(intr: CameraIntrinsics, height_px: int) -> np.ndarray:
    """세로 픽셀 수를 정하면 K 가 나온다. 가로 픽셀 수는 height_px × aspect 다."""
    width_px = height_px * intr.aspect
    focal = (height_px / 2) / intr.tan_half_v
    return np.array([[focal, 0.0, width_px / 2], [0.0, focal, height_px / 2], [0.0, 0.0, 1.0]])


def extrinsics_opencv(C: np.ndarray, look: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """OpenCV 카메라 축(x 오른쪽, y 아래, z 앞)의 R, t. 카메라 좌표 = R·X + t."""
    r, u, f = camera_basis(look)
    R = np.stack([r, -u, f])
    t = -R @ C
    return R, t


def project_pixels(point: np.ndarray, C: np.ndarray, look: np.ndarray, intr: CameraIntrinsics, height_px: int) -> np.ndarray:
    """P = K[R|t] 로 픽셀 좌표를 낸다. 이미지 관측을 만들 때 쓴다."""
    K = intrinsics_K(intr, height_px)
    R, t = extrinsics_opencv(C, look)
    x = K @ (R @ point + t)
    return x[:2] / x[2]
