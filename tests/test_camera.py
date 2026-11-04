import math

import numpy as np
import pytest

from flytracker.camera import CameraIntrinsics, intrinsics_K, project, project_pixels
from flytracker.geometry import look_dir, yaw_pitch_of

INTR = CameraIntrinsics(fov_v_deg=40.0, aspect=4 / 3)
C = np.array([0.0, 1.0, 0.0])
LOOK = np.array([0.0, 0.0, -1.0])


def test_point_straight_ahead_is_centered():
    p = project(C + LOOK * 2.0, C, LOOK, INTR)
    assert p.visible
    assert np.allclose(p.uv, 0.0)
    assert p.angle_error == pytest.approx(0.0)
    assert p.distance == pytest.approx(2.0)


def test_point_behind_is_not_visible():
    p = project(C - LOOK * 2.0, C, LOOK, INTR)
    assert not p.in_front
    assert not p.visible


def test_right_and_top_edges_map_to_one():
    depth = 2.0
    right = C + LOOK * depth + np.array([depth * INTR.tan_half_h, 0.0, 0.0])
    top = C + LOOK * depth + np.array([0.0, depth * INTR.tan_half_v, 0.0])
    assert project(right, C, LOOK, INTR).uv[0] == pytest.approx(1.0)
    assert project(top, C, LOOK, INTR).uv[1] == pytest.approx(1.0)


def test_pixels_from_K_R_t_match_uv():
    rng = np.random.default_rng(0)
    height = 480
    width = height * INTR.aspect
    look = look_dir(0.7, -0.2)
    for _ in range(20):
        point = C + look * rng.uniform(0.5, 3.0) + rng.normal(scale=0.3, size=3)
        proj = project(point, C, look, INTR)
        if not proj.in_front:
            continue
        px = project_pixels(point, C, look, INTR, height)
        expected = [(proj.uv[0] + 1) / 2 * width, (1 - proj.uv[1]) / 2 * height]
        assert np.allclose(px, expected, atol=1e-6)


def test_K_has_square_pixels():
    K = intrinsics_K(INTR, 480)
    assert K[0, 0] == pytest.approx(K[1, 1])


def test_positive_yaw_turns_left_and_roundtrips():
    d = look_dir(math.radians(30), math.radians(10))
    assert d[0] < 0  # 왼쪽은 −x
    yaw, pitch = yaw_pitch_of(d)
    assert yaw == pytest.approx(math.radians(30))
    assert pitch == pytest.approx(math.radians(10))
