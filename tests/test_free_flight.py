import json
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from flytracker import EnvConfig, FlyChaseEnv, NeuralConfig, StimulusConfig
from flytracker.free_flight import record_free_flight, record_tracking_observation
from flytracker.record import FRAME_KEYS


@pytest.mark.parametrize('model', ['rule', 'neural'])
def test_free_flight_has_no_aim_stimulus_or_capture_and_replays(model, monkeypatch):
    root = os.environ.get('FLYTRACKER_NEURAL_SOURCE')
    if model == 'neural' and not root:
        pytest.skip('Local neural source not selected')
    # Prove that the recording path never constructs an Aimer or queries vision.
    def forbidden(*args, **kwargs):
        raise AssertionError('Aiming must not run during free flight')
    monkeypatch.setattr('flytracker.env.Aimer', forbidden)
    monkeypatch.setattr('flytracker.env.project', forbidden)
    cfg = EnvConfig(fly_model=model, neural=NeuralConfig(source_root=root), max_seconds=.25)
    ep = record_free_flight(cfg, seed=12)
    again = record_free_flight(cfg, seed=12)
    assert ep == again
    assert ep['meta']['aimerEnabled'] is False and ep['meta']['captureEnabled'] is False
    assert ep['meta']['stimulus']['enabled'] is False
    assert ep['meta']['config']['capture_enabled'] is False
    assert cfg.capture_enabled is True  # Effective recording settings do not mutate the caller.
    assert ep['summary']['mode'] == 'free-flight'
    assert ep['summary']['duration'] == .25 and not ep['summary']['captured']
    assert ep['frames']['t'][-2:] == [.24, .25]
    assert set(FRAME_KEYS) <= ep['frames'].keys()
    assert all(len(row) == 14 for row in ep['frames'].values())
    assert not any(ep['frames']['captureProgress']) and not any(ep['frames']['reward'])
    assert ep['diagnostics']['stimulus']['event_count'] == 0
    assert np.isfinite(ep['frames']['fly']).all()
    assert not np.array_equal(ep['frames']['fly'][0], ep['frames']['fly'][-1])
    if model == 'neural':
        assert ep['diagnostics']['finalNeural']['body_time_ms'] == 250
        assert ep['diagnostics']['finalNeural']['neural_tick'] == 2500
        assert 'data/edges.csv' in ep['meta']['neural']['sha256']
    if shutil.which('node'):
        url = (Path(__file__).resolve().parents[1]/'viewer/src/data/episode.js').as_uri()
        code = f"import {{prepareEpisode}} from {json.dumps(url)};let s='';for await(const c of process.stdin)s+=c;const ep=prepareEpisode(JSON.parse(s));if(ep.duration!==.25||ep.speed.length!==14||ep.meta.aimerEnabled!==false)process.exit(1);"
        subprocess.run(['node', '--input-type=module', '-e', code], input=json.dumps(ep), text=True, check=True, capture_output=True)


@pytest.mark.parametrize('duration', [0, -.1, .015, float('nan')])
def test_free_flight_rejects_off_grid_duration(duration):
    with pytest.raises(ValueError):
        record_free_flight(EnvConfig(max_seconds=duration))




@pytest.mark.parametrize('kwargs', [{'dt': .02}, {'frame_skip': 1}])
def test_free_flight_rejects_ignored_clock_settings(kwargs):
    with pytest.raises(ValueError, match='10 ms'):
        record_free_flight(EnvConfig(max_seconds=.02, **kwargs))


@pytest.mark.parametrize('model', ['rule', 'neural'])
def test_disabled_capture_keeps_aligned_tracking_alive_until_horizon(model):
    root = os.environ.get('FLYTRACKER_NEURAL_SOURCE')
    if model == 'neural' and not root:
        pytest.skip('Local neural source not selected')
    cfg = EnvConfig(fly_model=model, neural=NeuralConfig(source_root=root), capture_enabled=False,
                    capture_hold=.01, start_facing_fly=True, max_seconds=.3)
    env = FlyChaseEnv(cfg)
    env.reset(seed=0)
    for _ in range(15):
        _, _, terminated, truncated, _ = env.step([0, 0])
        assert not terminated and env.snapshot()['captureProgress'] == 0
    assert truncated and env.t == pytest.approx(.3)
    assert not env.captured


def test_tracking_observation_has_real_aim_and_stimulus_but_no_capture():
    root = os.environ.get('FLYTRACKER_NEURAL_SOURCE')
    if not root:
        pytest.skip('Local neural source not selected')
    cfg = EnvConfig(fly_model='neural', neural=NeuralConfig(source_root=root),
                    stimulus=StimulusConfig(max_events=100), turret_pos=(0, 1.2, 0),
                    capture_hold=.01, max_seconds=.3)
    episode = record_tracking_observation(cfg, seed=0)
    assert cfg.capture_enabled is True  # The tracking/training configuration is not mutated.
    assert episode['meta']['captureEnabled'] is False and episode['meta']['aimerEnabled'] is True
    assert episode['meta']['mode'] == episode['summary']['mode'] == 'tracking-observation'
    assert episode['meta']['config']['capture_enabled'] is False
    assert episode['summary']['duration'] == .3 and not episode['summary']['captured']
    assert not any(episode['frames']['captureProgress'])
    assert len(episode['frames']['flySpeed']) == len(episode['frames']['t']) == 16
    assert episode['frames']['aimerLook'][0] != episode['frames']['aimerLook'][-1]
    assert episode['diagnostics']['stimulus']['events'][0]['onset_ms'] == 120
    assert episode['diagnostics']['stimulus']['exposure_ms'] == 180
    assert episode['meta']['stimulus']['max_events'] == 100


def test_capture_flag_defaults_on_and_roundtrips():
    assert EnvConfig.from_dict({}).capture_enabled is True
    assert EnvConfig.from_dict(EnvConfig(capture_enabled=False).to_dict()).capture_enabled is False
    with pytest.raises(ValueError, match='capture_enabled'):
        EnvConfig(capture_enabled='false')


def test_aim_schedule_uses_current_circuit_and_remains_diagnostic():
    root = os.environ.get("FLYTRACKER_NEURAL_SOURCE")
    if not root:
        pytest.skip("Local neural source not selected")
    cfg = EnvConfig(fly_model="neural", neural=NeuralConfig(source_root=root),
                    max_seconds=2.)
    ep = record_tracking_observation(cfg, seed=0, aim_on_seconds=1., aim_off_seconds=1.)
    assert ep["meta"]["policy"] == "diagnostic-truth-director"
    assert ep["frames"]["aimCommanded"][1] is True and ep["frames"]["aimCommanded"][-1] is False
    assert ep["meta"]["neural"]["neurons"] == 547
    assert ep["meta"]["neural"]["effective_connections"] == 16344
    assert ep["summary"]["duration"] == 2. and not ep["summary"]["captured"]
