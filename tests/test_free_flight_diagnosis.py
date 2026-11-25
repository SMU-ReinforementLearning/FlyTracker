"""진단이 신경 비행을 바꾸지 않는지, 기계적 수렴식이 실제 적분과 맞는지 검사한다."""

import numpy as np

from scripts import calibrate_free_flight as calibration
from scripts import diagnose_free_flight as diagnosis


def test_mechanical_control_matches_exponential_relaxation():
    calibration.initialize_worker()
    results = diagnosis.mechanical_control(calibration._FLY.backend)
    assert len(results) == 9
    assert max(row["maximumErrorMps"] for row in results) < 3e-6
    prediction = diagnosis.equilibrium()
    assert .33 < prediction["horizontalSpeedMps"] < .35
    assert .19 < prediction["relaxationSeconds"] < .20


def test_diagnostic_trace_preserves_baseline_and_isolates_sensory_override():
    calibration.initialize_worker()
    case = dict(id="diagnosis-fixture", experiment="fixture", seed=71,
                initialPosition=[0., 0., .5], initialVelocity=[.35, 0., 0.])
    profile = dict(id="base", physics={})
    traced = diagnosis.run_case((case, profile, .6))
    original = calibration.simulate((case, {}, .6, False))
    assert traced["positions"] == original["positions"]
    assert traced["finalStateSha256"] == original["diagnostics"]["finalStateSha256"]
    assert traced["weightsSha256"] == original["diagnostics"]["neuralWeightsSha256"]
    assert traced["trace"].shape == (120, len(diagnosis.TRACE_NAMES))
    assert np.isfinite(traced["trace"]).all()
    assert traced["normalCells"].shape[0] == 120

    variant = dict(id="no-vertical-flow", physics={}, sensory={"normal_flow_gain": 0.})
    changed = diagnosis.run_case((case, variant, .6))
    assert np.all(changed["trace"][:, 4] == 150.)
    restored = diagnosis.run_case((case, profile, .6))
    assert restored["positions"] == traced["positions"]
    assert restored["finalStateSha256"] == traced["finalStateSha256"]


def test_horizontal_projection_separates_vertical_bobbing_from_turning():
    t = np.arange(301) * .01
    positions = np.column_stack((.3 * t, np.zeros(len(t)), .5 + .1 * np.sin(6 * t)))
    features, _ = diagnosis.motion_features(positions)
    horizontal, quality = diagnosis.horizontal_features(positions)
    assert np.median(features["turn_angle_50ms_deg"]) > 1.
    assert max(horizontal["turn_angle_50ms_deg"]) < 1e-5
    assert np.allclose(horizontal["speed_mps"], .3, atol=1e-12)
    assert quality["validTurnSamples"] == 242
