"""Diagnostic flight recordings: fly-only or gaze tracking without capture."""

import math
from dataclasses import replace

import numpy as np

from .env import EnvConfig
from .env import FlyChaseEnv
from .baseline import RuleAimer
from .fly import Fly
from .geometry import unit
from .geometry import wrap_angle
from .neural_fly import NeuralFly
from .record import EPISODE_FORMAT, FRAME_KEYS, EpisodeRecorder, _round
from .world import AXES, UNIT


def record_tracking_observation(config: EnvConfig, seed: int = 0,
                                aim_on_seconds: float | None = None, aim_off_seconds: float = 4.) -> dict:
    """Use the real observation-only baseline/gaze gate, with capture disabled.

    The default baseline receives the ordinary 13D observation. An explicit
    on/off diagnostic schedule uses a truth director and is not a policy score.
    Only the configured time horizon ends this recording. Stimulus configuration
    is respected; a presentation does not imply sensory detection or escape.
    """
    if config.dt != .01 or config.frame_skip != 2:
        raise ValueError("Tracking observation requires 10 ms vision / 20 ms actions")
    ticks = config.max_seconds/.01
    if not math.isfinite(ticks) or ticks <= 0 or not math.isclose(ticks, round(ticks), abs_tol=1e-8, rel_tol=0):
        raise ValueError("Observation duration must be a positive multiple of 10 ms")
    cfg = replace(config, capture_enabled=False, start_facing_fly=True)
    recorder = EpisodeRecorder(FlyChaseEnv(cfg), meta={
        "policy": "rule-baseline", "trailSeconds": 5.,
    })
    policy = RuleAimer(max_pitch_deg=cfg.aimer.max_pitch_deg,
                       max_yaw_rate_deg=cfg.aimer.max_yaw_rate_deg,
                       max_pitch_rate_deg=cfg.aimer.max_pitch_rate_deg,
                       fov_v_deg=cfg.camera.fov_v_deg, decision_dt=.02)
    scheduled = aim_on_seconds is not None
    if scheduled:
        if any(not math.isfinite(v) or v <= 0 or not math.isclose(v/.02, round(v/.02), rel_tol=0, abs_tol=1e-8)
               for v in (aim_on_seconds, aim_off_seconds)):
            raise ValueError("Aim schedule durations must be positive 20 ms multiples")
        recorder.extra_meta.update(policy="diagnostic-truth-director",
                                   aimSchedule={"on_s": aim_on_seconds, "off_s": aim_off_seconds},
                                   controllerPurpose="Controlled stimulation fixture, not a tracking benchmark")
        recorder.unwrapped.observation_aim_on = True
    obs, _ = recorder.reset(seed=seed)
    done = False
    previous_on = True
    previous_target = None
    off_yaw = 0.
    while not done:
        if not scheduled:
            action, _ = policy.predict(obs, deterministic=True)
        else:
            env = recorder.unwrapped
            on = (round(env.t/.02) % round((aim_on_seconds+aim_off_seconds)/.02)) < round(aim_on_seconds/.02)
            env.observation_aim_on = on
            if on:
                # Explicit diagnostic oracle, not an observation-only policy.
                # Real actuator rate/acceleration limits still apply; no teleport.
                d = unit(env.fly.pos-env.aimer.pos)
                target = (math.atan2(-d[0], -d[2]), math.asin(float(np.clip(d[1], -1, 1))))
                feed = [0., 0.] if previous_target is None or not previous_on else [
                    wrap_angle(target[0]-previous_target[0])/.02, (target[1]-previous_target[1])/.02]
                previous_target = target
            else:
                if previous_on:
                    off_yaw = env.aimer.yaw+math.pi/2
                target, feed = (off_yaw, -math.radians(cfg.aimer.max_pitch_deg)), [0., 0.]
                previous_target = None
            action = np.clip([
                (feed[0]+8.*wrap_angle(target[0]-env.aimer.yaw))/math.radians(cfg.aimer.max_yaw_rate_deg),
                (feed[1]+8.*(target[1]-env.aimer.pitch))/math.radians(cfg.aimer.max_pitch_rate_deg),
            ], -1, 1)
            previous_on = on
        obs, _, terminated, truncated, _ = recorder.step(action)
        done = terminated or truncated
    recorder.last_episode["meta"]["config"] = cfg.to_dict()
    return recorder.last_episode


def record_free_flight(config: EnvConfig, seed: int = 0) -> dict:
    """Record at 20 ms (short final 10 ms allowed), without constructing an aimer.

    Aimer/projection fields are inert placeholders for episode/1 compatibility;
    meta.aimerEnabled=False tells the viewer not to render or interpret them.
    viewer는 기준선과 같은 원래 메시 크기를 사용한다.
    """
    if config.dt != .01 or config.frame_skip != 2:
        raise ValueError("Free flight requires 10 ms config steps / 20 ms recording")
    duration = config.max_seconds
    ticks = duration / .01
    if not math.isfinite(ticks) or ticks <= 0 or not math.isclose(ticks, round(ticks), abs_tol=1e-8, rel_tol=0):
        raise ValueError("Free-flight duration must be a positive multiple of 10 ms")
    rng = np.random.default_rng(seed)
    fly = NeuralFly(config.neural, rng) if config.fly_model == "neural" else Fly(config.fly, rng)
    position = config.room.sample(rng, margin=.4)
    heading = unit(np.array([rng.normal(), .2*rng.normal(), rng.normal()]))
    fly.reset(position, heading)
    frames = {key: [] for key in (*FRAME_KEYS, "reward", "flySpeed")}
    neural = config.fly_model == "neural"
    if neural:
        frames.update(neuralPhase=[], neuralDiagnostics=[])

    def append(time_ms):
        values = dict(t=time_ms/1000, fly=fly.pos.tolist(), flyHeading=fly.heading.tolist(),
                      aimerC=[0., 0., 0.], aimerLook=[0., 0., -1.], visible=False,
                      uv=[0., 0.], angleErrDeg=0., distance=0., alarmed=fly.alarmed,
                      captureProgress=0., reward=0., flySpeed=float(fly.speed))
        for key, value in values.items():
            frames[key].append(_round(value))
        if neural:
            frames["neuralPhase"].append(fly.sim.motor.phase)
            frames["neuralDiagnostics"].append(fly.diagnostics())

    append(0)
    end_ms = round(ticks) * 10
    step_ms = 5 if neural else 10
    for tick in range(step_ms, end_ms+1, step_ms):
        # No observer location reaches the model; rule distance threats are off.
        fly.step(step_ms/1000, config.room)
        if tick % 20 == 0 or tick == end_ms:
            append(tick)
    meta = dict(mode="free-flight", aimerEnabled=False, captureEnabled=False,
                flyModel=config.fly_model, unit=UNIT, axes=AXES,
                room=[config.room.width, config.room.height, config.room.depth],
                frameDt=.02, fovV=config.camera.fov_v_deg, aspect=config.camera.aspect,
                captureAngleDeg=config.capture_angle_deg, captureRange=None,
                seed=seed, trailSeconds=5., bodyDt=step_ms/1000,
                stimulus={"enabled": False}, policyDependentTrajectory=False,
                config=config.to_dict())
    # Explicit effective settings override inactive tracking-only config values.
    meta["config"]["stimulus"]["enabled"] = False
    meta["config"]["capture_enabled"] = False
    meta["config"]["mode"] = "free-flight"
    if neural:
        meta["neural"] = fly.provenance()
    episode = dict(format=EPISODE_FORMAT, meta=meta, frames=frames,
                   summary=dict(mode="free-flight", result="observation_complete", frames=len(frames["t"]),
                                duration=duration, captured=False, return_=0., visibleRatio=0.))
    episode["summary"]["return"] = episode["summary"].pop("return_")
    episode["diagnostics"] = {"stimulus": {"event_count": 0, "events": [], "exposure_ms": 0},
                               "phaseEvents": fly.phase_events if neural else []}
    if neural:
        episode["diagnostics"]["finalNeural"] = fly.diagnostics()
    return episode
