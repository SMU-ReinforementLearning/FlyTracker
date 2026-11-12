"""Unit tests plus opt-in integration with a user-selected local flysim source.

Set FLYTRACKER_NEURAL_SOURCE to run the real circuit tests. No source or data is
copied, generated, downloaded, or written in that project.
"""

import argparse
from dataclasses import replace
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from flytracker import EnvConfig, EpisodeRecorder, FlyChaseEnv, NeuralConfig, NeuralFly, StimulusConfig
from flytracker.neural_fly import SOURCE_TO_TRACKER, heading_quaternion, load_backend, to_source, to_tracker
from flytracker.record import FRAME_KEYS
from flytracker.stimulus import StimulusScheduler
from flytracker.world import Room


@pytest.fixture(scope="module")
def local_config():
    root = os.environ.get("FLYTRACKER_NEURAL_SOURCE")
    if not root:
        pytest.skip("Select a local source with FLYTRACKER_NEURAL_SOURCE")
    root = Path(root)
    def inventory():
        return {str(p): (p.stat().st_size, p.stat().st_mtime_ns)
                for name in ("flysim", "data/stage2", "output")
                for p in (root / name).rglob("*") if p.is_file()}
    before = inventory()
    yield NeuralConfig(source_root=str(root), boundary_enabled=False)
    assert inventory() == before, "Source project was modified"


def make_fly(config, seed=0):
    fly = NeuralFly(config, np.random.default_rng(seed))
    fly.reset([0, 1, 0], [0, 0, -1])
    return fly


@pytest.mark.parametrize("seed,position,heading", [
    (0, [-1.356542935371831, 1.8102409888925446, .8052172885781888],
     [.8729220691255766, .12679874928711615, -.4710935559023763]),
    (123, [1.4018224595746644, .8629790781344107, .7070343275027754],
     [.8380315003108386, -.11869856995643341, .5325540854946688]),
])
def test_default_rule_matches_prechange_rollout(seed, position, heading):
    env = FlyChaseEnv()
    env.reset(seed=seed)
    rng = np.random.default_rng(987)
    rewards = []
    for _ in range(30):
        _, reward, *_ = env.step(rng.uniform(-1, 1, 2))
        rewards.append(reward)
    np.testing.assert_allclose(env.fly.pos, position, atol=1e-12)
    np.testing.assert_allclose(env.fly.heading, heading, atol=1e-12)
    assert sum(rewards) == pytest.approx(-4.99468802723724)
    assert env._stimulus is None


def test_old_and_new_config_roundtrip():
    assert EnvConfig.from_dict({}).fly_model == "rule"
    cfg = EnvConfig(fly_model="neural", neural=NeuralConfig(source_root="local"),
                    stimulus=StimulusConfig(charge_ms=100, max_events=0))
    assert EnvConfig.from_dict(json.loads(json.dumps(cfg.to_dict()))) == cfg


@pytest.mark.parametrize("kwargs", [{"dt": .005}, {"dt": .015}, {"frame_skip": 1},
                                    {"max_seconds": .015}, {"max_seconds": float("nan")}])
def test_unsupported_environment_time_is_rejected(kwargs):
    with pytest.raises(ValueError):
        EnvConfig(fly_model="neural", **kwargs)


@pytest.mark.parametrize("kwargs", [{"charge_ms": 121}, {"max_events": -1},
                                    {"pulse_ms": 0}, {"align_deg": float("nan")},
                                    {"contrast": 2}, {"min_radius_m": .2}])
def test_bad_stimulus_config_is_rejected(kwargs):
    with pytest.raises(ValueError):
        StimulusConfig(**kwargs)


def test_stimulus_charge_causality_cooldown_budget_and_duration():
    gate = StimulusScheduler(StimulusConfig())
    for tick in range(0, 3500, 5):
        event = gate.advance(tick, True, 0., [1, 2, 3])
        if tick == 110:
            assert event is None
        if tick == 115:
            assert event["onset_ms"] == 120
            assert gate.exposure_ms == 0
        if tick == 120:
            assert gate.exposure_ms == 5
    assert [e["onset_ms"] for e in gate.events] == [120, 1290, 2460]
    assert gate.exposure_ms == 750
    assert [e["exposure_ms"] for e in gate.events] == [250, 250, 250]
    assert gate.charge == 0
    with pytest.raises(ValueError):
        gate.advance(3505, True, 0., [1, 2, 3])


def test_charge_decays_and_visibility_is_required():
    gate = StimulusScheduler(StimulusConfig())
    for tick in range(0, 60, 5):
        gate.advance(tick, True, 0., [0, 0, 0])
    assert gate.charge == pytest.approx(.5)
    for tick in range(60, 110, 5):
        gate.advance(tick, False, 0., [0, 0, 0])
    assert gate.charge == pytest.approx(.25)
    assert gate.events == []


@pytest.mark.parametrize("config", [StimulusConfig(enabled=False), StimulusConfig(max_events=0)])
def test_disabled_stimulus(config):
    gate = StimulusScheduler(config)
    for tick in range(0, 300, 5):
        assert gate.advance(tick, True, 0, [0, 0, 0]) is None


def rotate_independent(q, v):
    w, *xyz = q
    xyz = np.array(xyz)
    return np.asarray(v) + 2 * np.cross(xyz, np.cross(xyz, v) + w * np.asarray(v))


def test_coordinate_map_is_proper_rotation_and_heading_convention():
    assert np.linalg.det(SOURCE_TO_TRACKER) == 1
    np.testing.assert_array_equal(to_tracker([1, 2, 3]), [-2, 3, -1])
    for d in ([1, 0, 0], [0, 1, 0], [0, 0, 1], [.3, -.4, .5]):
        np.testing.assert_allclose(to_source(to_tracker(d)), d)
        np.testing.assert_allclose(rotate_independent(heading_quaternion(d), [1, 0, 0]),
                                   np.array(d) / np.linalg.norm(d), atol=1e-15)
    np.testing.assert_array_equal(np.cross(to_tracker([1,0,0]), to_tracker([0,1,0])), to_tracker([0,0,1]))


def test_missing_local_source_fails_explicitly(monkeypatch):
    monkeypatch.delenv("FLYTRACKER_NEURAL_SOURCE", raising=False)
    with pytest.raises(ValueError, match="requires"):
        load_backend(NeuralConfig())


def test_common_cli_selects_model_and_stimulus():
    from scripts._common import add_env_args, config_from_args
    parser = argparse.ArgumentParser()
    add_env_args(parser)
    assert config_from_args(parser.parse_args([])).fly_model == "rule"
    args = parser.parse_args(["--fly-model", "neural", "--neural-source", "local",
                              "--no-stimulus", "--stimulus-charge-ms", "100"])
    cfg = config_from_args(args)
    assert cfg.neural.source_root == "local"
    assert cfg.stimulus.charge_ms == 100 and not cfg.stimulus.enabled


def test_neuromechanical_persistent_state_and_time_grid(local_config):
    fly = make_fly(local_config)
    pending, filtered = fly.sim.neural.pending, fly.sim.motor.filtered
    fly.step(.2, Room())
    assert fly.sim.neural.pending is pending and fly.sim.motor.filtered is filtered
    assert fly.sim.neural.tick == 2000 and fly.sim.clock.tick == 200
    with pytest.raises(ValueError, match="5 ms"):
        fly.step(.007, Room())
    assert fly.backend.hashes["data/edges.csv"] == hashlib.sha256((fly.backend.data / "edges.csv").read_bytes()).hexdigest()


def test_velocity_attitude_and_angular_rate_mapping(local_config):
    fly = make_fly(local_config)
    b = fly.backend
    q = heading_quaternion([.3, .4, .5])
    fly.sim.body = replace(fly.sim.body, quaternion=q, velocity=b.core.Vec3(1,2,3), angular_rate=b.core.Vec3(.1,.2,.3))
    np.testing.assert_array_equal(fly.velocity, [-2, 3, -1])
    np.testing.assert_allclose(rotate_independent(fly.quaternion, [1,0,0]), fly.heading, atol=1e-15)
    expected = to_tracker(rotate_independent(q, [.1,.2,.3]))
    np.testing.assert_allclose(fly.angular_velocity, expected, atol=1e-15)


def test_neural_reset_and_seed_reproduce(local_config):
    cfg = EnvConfig(fly_model="neural", neural=local_config, max_seconds=.1)
    env = FlyChaseEnv(cfg)
    def rollout():
        obs, _ = env.reset(seed=123)
        assert env.fly.sim.neural.tick == 0 and not env.fly.sim.neural.pending.any()
        assert not env.fly.sim.motor.filtered.any() and env.fly.sim.motor.phase == "normal"
        rows = [obs]
        for _ in range(5):
            obs, *_ = env.step([.2, -.1]); rows.append(obs)
            assert obs.shape == (13,) and env.observation_space.contains(obs)
        return np.array(rows), env.snapshot(), env.fly.sim.neural.voltage.copy()
    a = rollout(); b = rollout()
    np.testing.assert_array_equal(a[0], b[0]); assert a[1] == b[1]
    np.testing.assert_array_equal(a[2], b[2])
    assert env.fly.sim.clock.tick == 100




@pytest.mark.parametrize("axis,side", [(0,-1),(0,1),(1,-1),(1,1),(2,-1),(2,1)])
def test_hard_boundary_keeps_motion_and_pose_inside_without_neural_escape(local_config, axis, side):
    fly = make_fly(replace(local_config, boundary_enabled=True))
    room = Room(); position = room.center.copy(); direction = np.zeros(3); direction[axis] = side
    position[axis] = (room.hi[axis] + .1) if side > 0 else (room.lo[axis] - .1)
    fly.pos = position; fly.heading = direction
    fly.sim.body = replace(fly.sim.body, velocity=fly._vec(to_source(direction)))
    voltage = fly.sim.neural.voltage
    fly.step(.005, room)
    assert room.contains(fly.pos, margin=.02-1e-12)
    assert fly.velocity[axis] * side <= 0
    np.testing.assert_allclose(fly.heading, direction, atol=1e-14)
    assert fly.boundary_corrections == 1
    assert fly.sim.neural.voltage is voltage
    assert fly.sim.motor.phase == "normal"
    assert np.linalg.norm(fly.quaternion) == pytest.approx(1)


def test_recording_preserves_old_fields_and_viewer_loader(local_config):
    cfg = EnvConfig(fly_model="neural", neural=local_config, max_seconds=.04)
    recorder = EpisodeRecorder(FlyChaseEnv(cfg))
    recorder.reset(seed=0)
    for _ in range(2):
        recorder.step([0,0])
    ep = recorder.last_episode
    assert ep["format"] == "flytracker.episode/1"
    assert set(FRAME_KEYS) <= ep["frames"].keys()
    assert all(len(rows) == 3 for rows in ep["frames"].values())
    assert ep["frames"]["t"] == [0., .02, .04]
    assert ep["meta"]["neural"]["body_dt_s"] == .005
    assert ep["meta"]["policyDependentTrajectory"] is True
    assert ep["diagnostics"]["finalNeural"]["neural_tick"] == 400
    encoded = json.dumps(ep, allow_nan=False)
    if shutil.which("node"):
        url = (Path(__file__).resolve().parents[1] / "viewer/src/data/episode.js").as_uri()
        script = f"import {{prepareEpisode,sample,newSample}} from {json.dumps(url)}; let s=''; for await (const c of process.stdin) s+=c; const ep=prepareEpisode(JSON.parse(s)); sample(ep,0.02,newSample()); if(ep.n!==3) process.exit(1);"
        subprocess.run(["node", "--input-type=module", "-e", script], input=encoded, text=True, check=True, capture_output=True)




def test_corner_contact_preserves_pose_and_wing_commands(local_config):
    fly = make_fly(replace(local_config, boundary_enabled=True))
    room = Room()
    fly.pos = room.hi + .1
    fly.heading = [1, 1, 1]
    fly.sim.body = replace(fly.sim.body, velocity=fly._vec(to_source([1, 1, 1])))
    quaternion = fly.quaternion
    force = fly.sim.motor.force_body.copy()
    fly._correct_room(room)
    assert room.contains(fly.pos, margin=.02-1e-12)
    assert (fly.velocity <= 0).all()
    np.testing.assert_array_equal(fly.quaternion, quaternion)
    np.testing.assert_array_equal(fly.sim.motor.force_body, force)


def test_capture_before_charge_does_not_present_future_stimulus(local_config):
    env = FlyChaseEnv(EnvConfig(fly_model="neural", neural=local_config,
                              capture_hold=.05, max_seconds=.3, start_facing_fly=True))
    env.reset(seed=0)
    for _ in range(5):
        _,_,terminated,_,_ = env.step([0,0])
        if terminated:
            break
    assert terminated and env.t <= .05
    assert env._stimulus.events == [] and env.fly.phase_events == []


def test_capture_at_pulse_onset_has_zero_delivered_exposure(local_config):
    # Existing reset vision contributes one capture tick. At 120 ms the gate
    # schedules onset and capture terminates before a sensory sample at 120 ms.
    env = FlyChaseEnv(EnvConfig(fly_model="neural", neural=local_config,
                              capture_hold=.13, max_seconds=.3, start_facing_fly=True))
    env.reset(seed=0)
    for _ in range(10):
        _,_,terminated,_,_ = env.step([0,0])
        if terminated:
            break
    assert terminated and env.t == .12
    assert env._stimulus.events[0]["onset_ms"] == 120
    assert env._stimulus.events[0]["exposure_ms"] == 0
    assert env._stimulus.exposure_ms == 0 and env.fly.phase_events == []


def test_disabled_stimulus_metadata_and_gym_contract(local_config):
    from gymnasium.utils.env_checker import check_env
    env = FlyChaseEnv(EnvConfig(fly_model="neural", neural=local_config,
                              stimulus=StimulusConfig(enabled=False), max_seconds=.1))
    check_env(env, skip_render_check=True)
    assert env.recording_metadata()["policyDependentTrajectory"] is False
    assert env.recording_metadata()["neural"]["resolved_source_root"] == str(Path(local_config.source_root).resolve())
