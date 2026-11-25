"""실측 위치 궤적과 신경 비행의 평시 분포를 같은 단위로 비교한다."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np

from .neuromechanics import MechanicsParameters

def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def weights_sha256(fly):
    weights = np.asarray(fly.sim.neural.weights)
    header = (str(weights.dtype), weights.shape)
    return hashlib.sha256(repr(header).encode() + weights.tobytes()).hexdigest()


METRICS = ("speed_mps", "acceleration_mps2", "turn_angle_50ms_deg", "vertical_speed_mps")
DT = .01
SAMPLES = 301
CANDIDATE_KEYS = ("drag_coefficient", "stroke_plane_forward_rad",
                  "saccade_rotation_gain_rad", "background_drive_hz")


def stable_key(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def split_experiments(experiments):
    experiments = sorted(set(experiments), key=lambda x: stable_key("flytracker59-normal-v1|" + x))
    train_end = math.floor(.6 * len(experiments))
    dev_end = train_end + math.floor(.2 * len(experiments))
    if train_end < 2 or dev_end == train_end or dev_end == len(experiments):
        raise ValueError("보정, 개발 및 독립 평가를 나눌 실험 수가 부족합니다.")
    return {name: ("train" if i < train_end else "development" if i < dev_end else "test")
            for i, name in enumerate(experiments)}


def motion_features(positions, dt=DT):
    positions = np.asarray(positions, dtype=float)
    if positions.ndim != 2 or positions.shape[1] != 3 or len(positions) < 60:
        raise ValueError("3차원 위치의 연속 표본이 필요합니다.")
    if not np.isfinite(positions).all() or not math.isclose(dt, DT, abs_tol=1e-12, rel_tol=0):
        raise ValueError("유한한 위치와 100Hz 간격이 필요합니다.")
    kernel = np.array([1., 4., 6., 4., 1.]) / 16
    padded = np.pad(positions, ((2, 2), (0, 0)), mode="edge")
    smooth = sum(weight * padded[i:i+len(positions)] for i, weight in enumerate(kernel))
    velocity = np.gradient(smooth, dt, axis=0, edge_order=2)
    acceleration = np.gradient(velocity, dt, axis=0, edge_order=2)
    speed = np.linalg.norm(velocity, axis=1)
    # 0.5초 준비 구간과 미분 경계 표본을 양쪽 자료에서 동일하게 제외한다.
    begin, end = 50, len(positions)-4
    selected = slice(begin, end)
    before, after = velocity[begin:end-5], velocity[begin+5:end]
    norm_before, norm_after = np.linalg.norm(before, axis=1), np.linalg.norm(after, axis=1)
    valid = (norm_before >= .05) & (norm_after >= .05)
    cosine = np.sum(before[valid]*after[valid], axis=1) / (norm_before[valid]*norm_after[valid])
    angles = np.degrees(np.arccos(np.clip(cosine, -1., 1.)))
    if not len(angles):
        raise ValueError("진행 방향 변화각을 계산할 비행 표본이 없습니다.")
    features = dict(speed_mps=speed[selected],
                    acceleration_mps2=np.linalg.norm(acceleration[selected], axis=1),
                    turn_angle_50ms_deg=angles,
                    vertical_speed_mps=velocity[selected, 2])
    return features, dict(positionSamples=len(positions), validTurnSamples=int(valid.sum()),
                          excludedTurnSamples=int((~valid).sum()))


def initial_velocity(positions):
    positions = np.asarray(positions, dtype=float)
    return (positions[4]-positions[0])/(4*DT)


def wasserstein_1d(a, b):
    """경험 누적분포 차이의 적분. 입력 단위를 보존한다."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.ndim != 1 or b.ndim != 1 or not len(a) or not len(b):
        raise ValueError("비어 있지 않은 1차원 분포가 필요합니다.")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("분포 값은 유한해야 합니다.")
    a, b = np.sort(a), np.sort(b)
    support = np.sort(np.r_[a, b])
    widths = np.diff(support)
    cdf_a = np.searchsorted(a, support[:-1], side="right")/len(a)
    cdf_b = np.searchsorted(b, support[:-1], side="right")/len(b)
    return float(np.sum(abs(cdf_a-cdf_b)*widths))


def distribution_scales(cases):
    train = [case for case in cases if case["split"] == "train"]
    result = {}
    for key in METRICS:
        values = np.concatenate([case["features"][key] for case in train])
        lower, upper = np.quantile(values, [.25, .75])
        result[key] = float(upper-lower)
        if result[key] <= 0 or not math.isfinite(result[key]):
            raise ValueError("보정 자료의 IQR이 0이거나 유한하지 않습니다: " + key)
    return result


def experiment_errors(cases, simulations, scales):
    by_id = {row["id"]: row for row in simulations}
    if set(by_id) != {case["id"] for case in cases} or len(by_id) != len(simulations):
        raise ValueError("모델과 실측 구간의 항목이 다릅니다.")
    result = []
    for experiment in sorted({case["experiment"] for case in cases}):
        group = [case for case in cases if case["experiment"] == experiment]
        row = {"id": experiment}
        for key in METRICS:
            observed = np.concatenate([case["features"][key] for case in group])
            simulated = np.concatenate([by_id[case["id"]]["features"][key] for case in group])
            row[key] = wasserstein_1d(observed, simulated)/scales[key]
        result.append(row)
    return result


def candidate_profiles(seed=5901, count=16):
    """고정된 Latin hypercube 후보. 기준값의 0.5~2배인 로그 공간을 쓴다."""
    rng = np.random.default_rng(seed)
    defaults = MechanicsParameters()
    values = np.column_stack([(rng.permutation(count)+rng.random(count))/count
                              for _ in CANDIDATE_KEYS])
    profiles = []
    for index, row in enumerate(values):
        overrides = {key: float(getattr(defaults, key)*2**(2*value-1))
                     for key, value in zip(CANDIDATE_KEYS, row)}
        profiles.append(dict(id=f"candidate-{index:02d}", physics=overrides))
    return profiles
