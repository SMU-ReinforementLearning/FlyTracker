"""Measurement conventions must not confuse source and tracker axes."""
from dataclasses import replace
import math
import os

import numpy as np
import pytest

from scripts.validate_neuromechanics import angular_difference, bank_angle, heading_angles, make
from flytracker import NeuralConfig
from scripts.inspect_flight_reference import summarize_reference


def test_native_yaw_elevation_from_tracker_headings():
    assert heading_angles([0, 0, -1]) == (0., 0.)
    assert heading_angles([-1, 0, 0])[0] == pytest.approx(math.pi/2)
    assert heading_angles([1, 0, 0])[0] == pytest.approx(-math.pi/2)
    assert heading_angles([0, .5, -math.sqrt(.75)])[1] == pytest.approx(math.pi/6)
    assert angular_difference(math.radians(-179), math.radians(179)) == pytest.approx(math.radians(2))


def test_bank_is_attitude_tilt_not_heading_elevation():
    source = os.environ.get('FLYTRACKER_NEURAL_SOURCE')
    if not source:
        pytest.skip('Local neural source not selected')
    fly = make(NeuralConfig(source_root=source, boundary_enabled=False), 11)
    fly.heading = [0, .5, -math.sqrt(.75)]
    assert bank_angle(fly) == pytest.approx(0., abs=1e-14)
    # Native +X forward; a +90 degree body roll tilts body-up toward right.
    delta = (math.sqrt(.5), math.sqrt(.5), 0., 0.)
    fly.sim.body = replace(fly.sim.body, quaternion=fly.backend.physics.qmultiply(fly.sim.body.quaternion, delta))
    assert bank_angle(fly) == pytest.approx(-math.pi/2)


def reference_fixture():
    t = np.array([0., .01, .02])
    q = np.zeros((3, 2, 4))
    q[..., 0] = np.cos(t[:, None]/2)
    q[..., 3] = np.sin(t[:, None]/2)
    q[2] *= -1  # Quaternion sign changes must not imply a physical flip.
    velocity = np.zeros((3, 2, 3)); velocity[..., 0] = .2
    position = velocity*t[:, None, None]
    return dict(body_data=dict(t=t, qbody=q, vel=velocity, pos=position, accel=np.zeros_like(velocity)),
                settings_variables=dict(seq=np.array([[1,1],[1,2]]), fps=100, g=9.81,
                                        expansion={'speed': np.array([0,1])}, Lbody=.003, Mfly=1.8e-6),
                stimulus_data={'teta': np.ones((3,2))})


def test_empirical_metric_is_sign_invariant_and_exports_only_aggregates():
    summary = summarize_reference(reference_fixture())
    assert summary['peak_angular_speed_distribution']['median'] == pytest.approx(1., abs=1e-9)
    assert summary['kinematic_unit_consistency']
    assert summary['pre_speed_median_distribution']['n'] == 0
    assert 'rows' not in summary and 'body_data' not in summary


def test_empirical_metric_records_small_norm_correction_and_rejects_corrupt_data():
    data = reference_fixture(); data['body_data']['qbody'][0] *= .997
    assert summarize_reference(data)['raw_quaternions_over_1e3_error'] == 2
    data['body_data']['qbody'][0] *= .5
    with pytest.raises(ValueError, match='norm'):
        summarize_reference(data)


def test_empirical_metric_rejects_ambiguous_clock():
    data = reference_fixture(); data['body_data']['t'][1] = 0.
    with pytest.raises(ValueError, match='increasing'):
        summarize_reference(data)


def test_source_encoder_saturates_across_published_expansion_speed_range():
    source = os.environ.get('FLYTRACKER_NEURAL_SOURCE')
    if not source:
        pytest.skip('Local neural source not selected')
    fly = make(NeuralConfig(source_root=source, boundary_enabled=False), 11)
    b = fly.backend
    body = replace(fly.sim.body, velocity=b.physics.ZERO)
    rates = []
    for degrees_per_ms in (.65, 1.3, 2.1):
        expansion = math.radians(degrees_per_ms)*1000
        # Same distance, angular size and bearing at the radius-growth midpoint;
        # select duration analytically to vary only optical expansion speed.
        duration = .11*math.pi/(expansion*(1+.065**2))
        disc = b.behavior.LoomingDisc(center=b.core.Vec3(math.sqrt(.5), math.sqrt(.5), 1.2),
                                     onset_s=0., duration_s=duration)
        sensory = disc.sample(duration/2, body)
        assert sensory['expansion_rad_s'] == pytest.approx(expansion)
        assert sensory['left']+sensory['right'] == pytest.approx(1.)
        drive, _ = fly.sim.encoder.encode(body, duration/2, disc)
        rates.append(drive)
    np.testing.assert_allclose(rates[0], rates[1], atol=1e-12)
    np.testing.assert_allclose(rates[0], rates[2], atol=1e-12)
