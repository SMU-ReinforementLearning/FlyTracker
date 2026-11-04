"""방향 벡터 계산 도우미."""

from __future__ import annotations

import math

import numpy as np

from .world import UP


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else np.zeros_like(v)


def look_dir(yaw: float, pitch: float) -> np.ndarray:
    """yaw, pitch 로 바라보는 방향을 만든다.

    yaw 0, pitch 0 이면 −z 를 본다. three.js 카메라의 기본 방향과 같다.
    yaw 가 커지면 위에서 볼 때 반시계(왼쪽)로 돌고, pitch 가 커지면 위를 본다.
    three.js 의 Euler 순서 'YXZ' 에 rotation.y = yaw, rotation.x = pitch 를 넣은 것과 같다.
    """
    cp = math.cos(pitch)
    return np.array([-math.sin(yaw) * cp, math.sin(pitch), -math.cos(yaw) * cp])


def yaw_pitch_of(d: np.ndarray) -> tuple[float, float]:
    """look_dir 의 역함수."""
    d = unit(d)
    return math.atan2(-d[0], -d[2]), math.asin(float(np.clip(d[1], -1.0, 1.0)))


def horizontal_basis(yaw: float) -> tuple[np.ndarray, np.ndarray]:
    """yaw 만 반영한 수평 앞 방향과 오른쪽 방향."""
    forward = np.array([-math.sin(yaw), 0.0, -math.cos(yaw)])
    right = np.array([math.cos(yaw), 0.0, -math.sin(yaw)])
    return forward, right


def angle_between(a: np.ndarray, b: np.ndarray) -> float:
    ua, ub = unit(a), unit(b)
    return math.acos(float(np.clip(ua @ ub, -1.0, 1.0)))


def slerp(a: np.ndarray, b: np.ndarray, s: float) -> np.ndarray:
    """두 단위 벡터 사이를 구면 보간한다. 정반대이면 수직축(y)에 가까운 축으로 돈다."""
    a, b = unit(a), unit(b)
    dot = float(np.clip(a @ b, -1.0, 1.0))
    if dot > 0.9995:
        return unit(a + s * (b - a))
    if dot < -0.9995:
        axis = unit(np.cross(a, UP))
        if not axis.any():
            axis = np.array([1.0, 0.0, 0.0])
        mid = unit(np.cross(axis, a))
        theta = math.pi * s
        return unit(a * math.cos(theta) + mid * math.sin(theta))
    theta = math.acos(dot)
    sin_t = math.sin(theta)
    return (math.sin((1 - s) * theta) * a + math.sin(s * theta) * b) / sin_t


def rotate_about_y(v: np.ndarray, angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([c * v[0] + s * v[2], v[1], -s * v[0] + c * v[2]])


def wrap_angle(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


def approach(x: float, target: float, max_delta: float) -> float:
    return x + float(np.clip(target - x, -max_delta, max_delta))
