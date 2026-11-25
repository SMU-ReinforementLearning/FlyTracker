"""평시 비행의 좁은 분포를 신경 출력과 기계적 수렴으로 나누어 진단한다."""

from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import calibrate_free_flight as calibration
from flytracker.flight_calibration import METRICS, motion_features, stable_key
from flytracker.neural_fly import to_tracker
from flytracker.neuromechanics import MechanicsParameters, NeuromechanicalSimulation, array, integrate
from flytracker.world import Room

DT = .005
TRACE_NAMES = (
    "time_s", "speed_mps", "horizontal_speed_mps", "vertical_speed_mps",
    "normal_input_hz", "normal_rate_hz", "raw_normal_rate_hz",
    "amplitude_rad", "drag_kg_s", "relaxation_s",
    "next_force_tilt_deg", "next_horizontal_equilibrium_mps",
    "sgu_difference_hz", "yaw_rate_rad_s", "reflex_norm_nm",
    "amplitude_limited", "lift_limited", "forward_limited", "pressure_limited",
)


def equilibrium(physics=None):
    p = physics or MechanicsParameters()
    amplitude = math.sqrt(p.mass_kg * p.gravity /
                          (p.lift_scale * math.cos(p.stroke_plane_forward_rad)))
    drag = (p.air_density * p.total_wing_area_m2 * p.drag_coefficient *
            4 * p.wingbeat_hz * amplitude * p.wing_arm)
    return dict(amplitudeRad=amplitude, dragKgS=drag,
                horizontalSpeedMps=p.mass_kg * p.gravity *
                    math.tan(p.stroke_plane_forward_rad) / drag,
                relaxationSeconds=p.mass_kg / drag)


def clipping_flags(motor, record):
    """기존 decode의 제한 판정을 상태에서 재구성하고 실제 판정과 대조한다."""
    p = motor.p
    amplitude = record["stroke_amplitude_rad"]
    unconstrained = p.trim_amplitude * math.sqrt(max(record["normal_rate_hz"], 0.) /
                                               motor.reference_rate)
    power = amplitude ** 2 / p.trim_amplitude ** 2
    reflex = motor.reflex_activation * min(power, 1.)

    def recruit(rate):
        return max(rate - p.steering_recruitment_hz, 0.)

    escape = (recruit(record["dnp06_left_hz"]) - recruit(record["dnp06_right_hz"]) +
              recruit(record["dnp03_left_hz"]) - recruit(record["dnp03_right_hz"])) / p.escape_reference_hz
    saccade = (record["sgu_right_hz"] - record["sgu_left_hz"]) / p.saccade_reference_hz
    bias = p.escape_roll_gain_rad * (escape + saccade)
    raw_left = p.lift_scale * .5 * max(amplitude * (1 + bias), 0.) ** 2 + reflex[0] / (2 * p.wing_arm)
    raw_right = p.lift_scale * .5 * max(amplitude * (1 - bias), 0.) ** 2 - reflex[0] / (2 * p.wing_arm)
    maximum = p.lift_scale * .5 * p.max_stroke_amplitude_rad ** 2
    left, right = record["wing_lift_left_n"], record["wing_lift_right_n"]
    rotation = p.escape_rotation_gain_rad * escape + p.saccade_rotation_gain_rad * saccade
    raw_forward = np.array([left * math.sin(rotation) - reflex[2] / (2 * p.wing_arm),
                            -right * math.sin(rotation) + reflex[2] / (2 * p.wing_arm)])
    forward_limits = np.array([left, right]) * math.sin(p.max_wing_rotation_rad)
    flags = dict(
        amplitude_limited=unconstrained > p.max_stroke_amplitude_rad,
        lift_limited=bool(np.any(np.array([raw_left, raw_right]) < 0.) or
                          np.any(np.array([raw_left, raw_right]) > maximum)),
        forward_limited=bool(np.any(np.abs(raw_forward) > forward_limits)),
        pressure_limited=abs(-reflex[1] / max(left + right, 1e-15)) > p.pitch_lever_m,
    )
    combined = flags["lift_limited"] or flags["forward_limited"] or flags["pressure_limited"]
    if combined != motor.saturated:
        raise AssertionError("Diagnostic clipping flags differ from the actual decoder")
    return flags


def final_state_hash(fly):
    neural, motor = fly.sim.neural, fly.sim.motor
    digest = hashlib.sha256()
    for value in (neural.voltage, neural.synaptic, neural.pending, neural.next_active,
                  motor.filtered, motor.force_body, motor.torque_body, motor.reflex_activation,
                  fly.quaternion, fly.velocity, fly.angular_velocity):
        digest.update(np.asarray(value).tobytes())
    digest.update(json.dumps(neural.rng.bit_generator.state, sort_keys=True).encode())
    return digest.hexdigest()


def describe(values):
    values = np.asarray(values, dtype=float)
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("Diagnostic summary requires finite samples")
    mean = float(values.mean())
    return dict(mean=mean, std=float(values.std()),
                cv=float(values.std() / abs(mean)) if abs(mean) > 1e-12 else None,
                quantiles=np.quantile(values, [.05, .25, .5, .75, .95]).tolist())


def run_case(payload):
    case, profile, duration = payload
    start = time.monotonic()
    fly = calibration._FLY
    fly.rng = np.random.default_rng(case["seed"])
    velocity = np.asarray(case["initialVelocity"], dtype=float)
    fly.reset(to_tracker(case["initialPosition"]), to_tracker(velocity / np.linalg.norm(velocity)))
    initial = replace(fly.sim.body, velocity=fly.backend.core.Vec3(*velocity))
    if profile["physics"]:
        fly.sim = NeuromechanicalSimulation(fly.backend, seed=fly.seed,
                                            physics=MechanicsParameters(**profile["physics"]))
    fly.sim.initialize(initial)
    if profile.get("sensory"):
        fly.sim.params = replace(fly.sim.params, **profile["sensory"])
        fly.sim.encoder.p = fly.sim.params
    initial_weights = calibration.weights_sha256(fly)
    positions = [case["initialPosition"]]
    traces, normal_cells = [], []
    ticks = round(duration / DT)
    if duration <= 0 or not math.isclose(ticks * DT, duration, abs_tol=1e-10):
        raise ValueError("Duration must be a positive multiple of 5ms")
    for tick in range(ticks):
        before = fly.sim.total_spikes[fly.sim.motor.normal].copy()
        try:
            fly.step(DT, Room())
        except FloatingPointError as exc:
            raise FloatingPointError(f"At {(tick + 1) * DT:.3f}s: {exc}") from exc
        record, motor, body = fly.sim.last_record, fly.sim.motor, fly.sim.body
        velocity = array(body.velocity)
        next_force = array(fly.backend.behavior.rotate(
            body.quaternion, fly.backend.core.Vec3(*motor.force_body)))
        force_norm = float(np.linalg.norm(next_force))
        tilt = math.degrees(math.acos(np.clip(next_force[2] / force_norm, -1., 1.))) if force_norm else 0.
        flags = clipping_flags(motor, record)
        raw_rate = float(np.mean(fly.sim.total_spikes[motor.normal] - before)) / DT
        traces.append([
            (tick + 1) * DT, np.linalg.norm(velocity), np.linalg.norm(velocity[:2]), velocity[2],
            record["normal_drive_hz"], record["normal_rate_hz"], raw_rate,
            record["stroke_amplitude_rad"], motor.drag,
            fly.sim.physics.mass_kg / motor.drag if motor.drag else 0.,
            tilt, np.linalg.norm(next_force[:2]) / motor.drag if motor.drag else 0.,
            record["sgu_right_hz"] - record["sgu_left_hz"], body.angular_rate.z,
            np.linalg.norm(motor.reflex_activation), *[int(flags[k]) for k in TRACE_NAMES[-4:]],
        ])
        normal_cells.append(motor.filtered[motor.normal].copy())
        states = (fly.sim.neural.voltage, fly.sim.neural.synaptic, fly.sim.neural.pending,
                  fly.quaternion, fly.velocity, fly.angular_velocity, motor.filtered,
                  motor.force_body, motor.torque_body, motor.reflex_activation)
        if not all(np.isfinite(value).all() for value in states):
            raise FloatingPointError(f"Nonfinite state at {(tick + 1) * DT} seconds")
        if (tick + 1) % 2 == 0:
            positions.append(array(body.position).tolist())
    if calibration.weights_sha256(fly) != initial_weights:
        raise AssertionError("Neural weights changed during diagnosis")
    trace = np.asarray(traces)
    cells = np.asarray(normal_cells)
    steady = trace[:, 0] > .5
    summary = {name: describe(trace[steady, i]) for i, name in enumerate(TRACE_NAMES[1:], start=1)}
    cell_std = cells[steady].std(axis=0)
    summary["averagingStdRatio"] = float(trace[steady, 5].std() / cell_std.mean()) if cell_std.mean() else None
    summary["normalCellTemporalStdMeanHz"] = float(cell_std.mean())
    features, quality = motion_features(positions)
    return dict(id=case["id"], experiment=case["experiment"], seed=case["seed"],
                profile=profile["id"], positions=positions,
                features={k: v.tolist() for k, v in features.items()}, quality=quality,
                summary=summary, weightsSha256=initial_weights, finalStateSha256=final_state_hash(fly),
                spikes=int(fly.sim.total_spikes.sum()), neuralTicks=fly.sim.neural.tick,
                phaseEvents=fly.phase_events, boundaryCorrections=fly.boundary_corrections,
                wallSeconds=time.monotonic() - start, trace=trace, normalCells=cells)


def profiles():
    p = MechanicsParameters()
    return [
        dict(id="base", physics={}),
        dict(id="initial-slow", physics={}, initialSpeed=.1),
        dict(id="initial-fast", physics={}, initialSpeed=.7),
        dict(id="tilt-half", physics={"stroke_plane_forward_rad": math.radians(5)}),
        dict(id="tilt-double", physics={"stroke_plane_forward_rad": math.radians(20)}),
        dict(id="no-vertical-flow", physics={}, sensory={"normal_flow_gain": 0.}),
        dict(id="weaker-reflex", physics={"reflex_frequency_rad_s": p.reflex_frequency_rad_s / 2,
                                        "yaw_reflex_time_s": p.yaw_reflex_time_s * 2}),
        dict(id="background-tenfold", physics={"background_drive_hz": 10.}),
        dict(id="cap-roomier", physics={"max_stroke_amplitude_rad": 2.}),
    ]


def mechanical_control(backend, duration=3.):
    results = []
    for angle in (5., 10., 20.):
        p = MechanicsParameters(stroke_plane_forward_rad=math.radians(angle))
        values = equilibrium(p)
        force = backend.core.Vec3(p.mass_kg * p.gravity * math.tan(p.stroke_plane_forward_rad),
                                 0., p.mass_kg * p.gravity)
        for speed in (.1, .35, .7):
            body = backend.physics.BodyState(velocity=backend.core.Vec3(speed, 0., 0.))
            rows = [[0., speed, speed]]
            for tick in range(round(duration / DT)):
                body = integrate(body, array(force), np.zeros(3), values["dragKgS"], DT,
                                 backend, p, np.array([0., 0., 1.]))
                t = (tick + 1) * DT
                expected = values["horizontalSpeedMps"] + (speed - values["horizontalSpeedMps"]) * math.exp(-t / values["relaxationSeconds"])
                rows.append([t, body.velocity.x, expected])
            values_array = np.asarray(rows)
            results.append(dict(angleDeg=angle, initialSpeed=speed, theory=values,
                                maximumErrorMps=float(np.max(abs(values_array[:, 1] - values_array[:, 2]))),
                                trajectory=rows))
    return results


def save_case(result, folder):
    identifier = stable_key(result["id"])
    folder.mkdir(parents=True, exist_ok=True)
    trace = result.pop("trace")
    cells = result.pop("normalCells")
    np.savez_compressed(folder / (identifier + ".npz"), trace=trace, normal_cells=cells,
                        names=np.asarray(TRACE_NAMES))
    calibration.write_json(folder / (identifier + ".json"), result)


def pooled_features(rows):
    return {key: describe(np.concatenate([r["features"][key] for r in rows])) for key in METRICS}


def paired_width_differences(reference, candidate):
    reference = {r["id"]: r for r in reference}
    rng = np.random.default_rng(59020)
    indices = rng.integers(0, len(candidate), size=(10000, len(candidate)))
    result = {}
    for metric in METRICS:
        differences = []
        for row in candidate:
            a = np.quantile(reference[row["id"]]["features"][metric], [.05, .95])
            b = np.quantile(row["features"][metric], [.05, .95])
            differences.append(float((b[1] - b[0]) - (a[1] - a[0])))
        samples = np.asarray(differences)[indices].mean(axis=1)
        result[metric] = dict(mean=float(np.mean(differences)),
                              ci95=np.quantile(samples, [.025, .975]).tolist())
    return result


def run(prepared, previous, output, workers):
    if output.exists():
        raise FileExistsError("Choose a new diagnostic output directory")
    cases = json.loads((prepared / "cases.json").read_text(encoding="utf-8"))
    train = [c for c in cases if c["split"] == "train"]
    chosen = [min([c for c in train if c["experiment"] == e], key=lambda c: stable_key(c["id"]))
              for e in sorted({c["experiment"] for c in train})]
    output.mkdir(parents=True)
    plan = ROOT / "docs/issues/feature/59-feature-neural-fly-learning/normal-flight-diagnosis.md"
    (output / "plan.md").write_bytes(plan.read_bytes())
    sources = {**calibration.code_signature(),
               "scripts/diagnose_free_flight.py": calibration.file_sha256(Path(__file__))}
    calibration.write_json(output / "manifest.json", dict(
        sources=sources, circuit=calibration.circuit_signature(),
        preparedCasesSha256=calibration.file_sha256(prepared / "cases.json"),
        planSha256=calibration.file_sha256(ROOT / "docs/issues/feature/59-feature-neural-fly-learning/normal-flight-diagnosis.md"),
        profiles=profiles(), physics=asdict(MechanicsParameters()), workers=workers,
        host=platform.platform(), python=platform.python_version(),
        numpy=np.__version__, createdUtc=datetime.now(timezone.utc).isoformat()))
    started = time.monotonic()
    def progress(stage, **kwargs):
        record = dict(stage=stage, elapsedSeconds=time.monotonic() - started,
                      utc=datetime.now(timezone.utc).isoformat(), **kwargs)
        calibration.write_json(output / "progress.json", record)
        print(json.dumps(record), flush=True)

    groups, failures = {}, []
    batches = [("observed-initial", train, dict(id="observed-initial", physics={}))]
    for profile in profiles():
        synthetic = [dict(id=c["id"], experiment=c["experiment"], seed=c["seed"],
                          initialPosition=[0., 0., .5],
                          initialVelocity=[profile.get("initialSpeed", .35), 0., 0.]) for c in chosen]
        batches.append((profile["id"], synthetic, profile))

    for name, selected, profile in batches:
        progress(name, completed=0, total=len(selected))
        rows = []
        with ProcessPoolExecutor(max_workers=workers, initializer=calibration.initialize_worker) as pool:
            jobs = {pool.submit(run_case, (c, profile, 3.)): c for c in selected}
            for job in as_completed(jobs):
                case = jobs[job]
                try:
                    result = job.result()
                except (FloatingPointError, ValueError, AssertionError) as exc:
                    failures.append(dict(profile=name, id=case["id"], error=str(exc)))
                    calibration.write_json(output / "failures.json", failures)
                else:
                    if name == "observed-initial":
                        prior = json.loads((previous / "simulations/baseline" /
                                            (stable_key(case["id"]) + ".json")).read_text(encoding="utf-8"))
                        if result["positions"] != prior["positions"] or result["finalStateSha256"] != prior["diagnostics"]["finalStateSha256"]:
                            raise AssertionError("Tracing changed the original baseline simulation")
                    save_case(result, output / name)
                    rows.append(result)
                progress(name, completed=len(rows), failures=len(failures), total=len(selected))
                if time.monotonic() - started > 1800:
                    raise TimeoutError("Diagnosis exceeded the 30-minute limit")
        groups[name] = sorted(rows, key=lambda r: r["id"])
    calibration.initialize_worker()
    mechanical = mechanical_control(calibration._FLY.backend)
    calibration.write_json(output / "mechanical-control.json", mechanical)
    summary = dict(failures=failures, replayMatched=len(groups["observed-initial"]),
                   theory=equilibrium(), observed=pooled_features(train), conditions={})
    for name, rows in groups.items():
        if len(rows) != next(len(batch[1]) for batch in batches if batch[0] == name):
            summary["conditions"][name] = dict(completed=len(rows), failed=True)
            continue
        stats = {key: describe([r["summary"][key]["mean"] for r in rows])
                 for key in TRACE_NAMES[1:]}
        summary["conditions"][name] = dict(completed=len(rows), features=pooled_features(rows),
            meanDiagnostics=stats,
            meanAveragingStdRatio=float(np.mean([r["summary"]["averagingStdRatio"] for r in rows])),
            meanNormalRateCV=float(np.mean([r["summary"]["normal_rate_hz"]["cv"] for r in rows])),
            meanAmplitudeCV=float(np.mean([r["summary"]["amplitude_rad"]["cv"] for r in rows])),
            saturationCounts={key:sum(round(r["summary"][key]["mean"] * 500) for r in rows)
                              for key in TRACE_NAMES[-4:]},
            pairedWidthChange=paired_width_differences(groups["base"], rows)
                if name not in ("base", "observed-initial") and len(groups["base"]) == len(chosen) else None)
    calibration.write_json(output / "result.json", summary)
    initial_speed_contraction(output)
    render_plot(output, groups, train)
    progress("completed", failures=len(failures), replayMatched=summary["replayMatched"])
    return summary


def render_plot(output, groups, observed):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    if any(font.name == "Malgun Gothic" for font in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    figure, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    metric = "speed_mps"
    for label, rows, color in (("실측 보정 자료", observed, "black"),
                                ("신경 모델", groups["observed-initial"], "#0072B2")):
        values = np.sort(np.concatenate([r["features"][metric] for r in rows]))
        axes[0, 0].plot(values, np.arange(1, len(values) + 1) / len(values), label=label, color=color)
    axes[0, 0].set(xlabel="속력 (m/s)", ylabel="누적 비율")
    axes[0, 0].legend()
    for name, label in (("initial-slow", "초기 0.1m/s"), ("base", "초기 0.35m/s"), ("initial-fast", "초기 0.7m/s")):
        if not groups[name]:
            continue
        rows = []
        for record in groups[name]:
            path = output / name / (stable_key(record["id"]) + ".npz")
            with np.load(path) as archive:
                rows.append(archive["trace"][:, 2])
        times = np.arange(1, len(rows[0]) + 1) * DT
        axes[0, 1].plot(times, np.mean(rows, axis=0), label=label)
    axes[0, 1].axhline(equilibrium()["horizontalSpeedMps"], color="black", linestyle="--", label="중량 평형 근사")
    axes[0, 1].set(xlabel="시간 (s)", ylabel="수평 속력 (m/s)")
    axes[0, 1].legend()
    for name, label in (("tilt-half", "5도"), ("base", "10도"), ("tilt-double", "20도")):
        rows = groups[name]
        if not rows:
            continue
        values = np.concatenate([r["features"][metric] for r in rows])
        axes[1, 0].hist(values, bins=50, density=True, histtype="step", label=label)
    axes[1, 0].set(xlabel="속력 (m/s)", ylabel="확률 밀도")
    axes[1, 0].legend()
    record = groups["observed-initial"][0]
    with np.load(output / "observed-initial" / (stable_key(record["id"]) + ".npz")) as archive:
        trace = archive["trace"]
    axes[1, 1].plot(trace[:, 0], trace[:, 6], alpha=.4, label="5ms DNg02 평균 발화")
    axes[1, 1].plot(trace[:, 0], trace[:, 5], label="50ms 필터 후")
    axes[1, 1].set(xlabel="시간 (s)", ylabel="평균 발화율 (Hz)")
    axes[1, 1].legend()
    for axis in axes.flat:
        axis.grid(alpha=.2)
    figure.savefig(output / "diagnosis.png", dpi=160)
    plt.close(figure)




def initial_speed_contraction(output):
    """동일 운동 명령에서 초기 속도 차이가 항력만으로 줄어드는지 재구성한다."""
    metadata = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    mass = metadata["physics"]["mass_kg"]
    speeds = {row["id"]: row.get("initialSpeed", .35) for row in metadata["profiles"]}
    initial_difference = speeds["initial-fast"] - speeds["initial-slow"]
    results = []
    files = sorted((output / "base").glob("*.npz"))
    for path in files:
        slow_path = output / "initial-slow" / path.name
        fast_path = output / "initial-fast" / path.name
        if not slow_path.exists() or not fast_path.exists():
            return dict(complete=False, reason="An initial-speed condition did not finish")
        with np.load(path) as base, np.load(slow_path) as slow, np.load(fast_path) as fast:
            slow_trace, fast_trace = slow["trace"], fast["trace"]
            identical = (np.array_equal(base["trace"][:, 3:], slow_trace[:, 3:]) and
                         np.array_equal(slow_trace[:, 3:], fast_trace[:, 3:]) and
                         np.array_equal(base["normal_cells"], slow["normal_cells"]) and
                         np.array_equal(slow["normal_cells"], fast["normal_cells"]))
            # trace의 항력은 다음 5ms 구간의 명령이며 첫 구간 항력은 0이다.
            drag = np.r_[0., slow_trace[:-1, TRACE_NAMES.index("drag_kg_s")]]
        velocity_difference, position_difference = initial_difference, 0.
        predicted_position = [0.]
        h = DT / 5
        for tick, coefficient in enumerate(drag):
            ratio = coefficient / mass
            for _ in range(5):
                position_difference += velocity_difference * (1 - ratio * h / 2) * h
                velocity_difference *= 1 - ratio * h + .5 * (ratio * h) ** 2
            if (tick + 1) % 2 == 0:
                predicted_position.append(position_difference)
        slow_record = json.loads(slow_path.with_suffix(".json").read_text(encoding="utf-8"))
        fast_record = json.loads(fast_path.with_suffix(".json").read_text(encoding="utf-8"))
        position_delta = np.asarray(fast_record["positions"]) - np.asarray(slow_record["positions"])
        results.append(dict(id=slow_record["id"], recordedCommandsIdentical=identical,
                            maximumPositionErrorM=float(np.max(abs(position_delta[:, 0] - predicted_position))),
                            otherAxesMaximumDifferenceM=float(np.max(abs(position_delta[:, 1:]))),
                            finalVelocityDifferenceMps=float(velocity_difference)))
    result = dict(complete=True, cases=len(results),
                  recordedCommandsIdentical=sum(r["recordedCommandsIdentical"] for r in results),
                  casesDetail=results)
    calibration.write_json(output / "initial-speed-contraction.json", result)
    return result


def horizontal_features(positions):
    projected = np.asarray(positions, dtype=float).copy()
    projected[:, 2] = 0.
    features, quality = motion_features(projected)
    return {key: value.tolist() for key, value in features.items()}, quality


def analyze_horizontal(output, prepared, raw_series):
    """기존 궤적만 읽어 수평 선회와 수직 변화의 영향을 분리한다."""
    import h5py
    selected = json.loads((prepared / "cases.json").read_text(encoding="utf-8"))
    train = [case for case in selected if case["split"] == "train"]
    selection = json.loads((prepared / "selection.json").read_text(encoding="utf-8"))
    expected = selection["rawSha256"]["series.h5"]
    if calibration.file_sha256(raw_series) != expected:
        raise ValueError("Raw trajectory hash differs from the fixed calibration dataset")
    observed = []
    with h5py.File(raw_series, "r") as archive:
        basic = archive["basic"]
        columns = [c.decode() if isinstance(c, bytes) else str(c) for c in basic.attrs["col_ids"]]
        indices = [columns.index(name) for name in ("x", "y", "z")]
        for case in train:
            positions = np.asarray(basic[case["experiment"]][case["id"].split("/")[1]][:301], dtype=float)[:, indices]
            features, quality = horizontal_features(positions)
            observed.append(dict(id=case["id"], features=features, quality=quality))
    groups = {"observed": observed}
    for name in ["observed-initial", *[p["id"] for p in profiles()]]:
        directory = output / name
        if name == "cap-roomier" and not directory.exists():
            directory = output / "cap-control"
        if not directory.exists():
            continue
        rows = []
        for path in sorted(directory.glob("*.json")):
            if len(path.stem) != 64:
                continue
            source = json.loads(path.read_text(encoding="utf-8"))
            features, quality = horizontal_features(source["positions"])
            rows.append(dict(id=source["id"], features=features, quality=quality))
        if rows:
            groups[name] = rows
    summary = dict(sourceSha256=calibration.file_sha256(Path(__file__)),
                   rawSeriesSha256=expected,
                   definition="XY projection followed by the identical position smoother, derivatives and 0.05m/s threshold",
                   conditions={})
    for name, rows in groups.items():
        summary["conditions"][name] = dict(
            cases=len(rows), features=pooled_features(rows),
            turnSamples=sum(row["quality"]["validTurnSamples"] for row in rows),
            excludedTurnSamples=sum(row["quality"]["excludedTurnSamples"] for row in rows),
            pairedWidthChange=paired_width_differences(groups["base"], rows)
                if name not in ("observed", "observed-initial", "base") and len(rows) == len(groups["base"]) else None)
    calibration.write_json(output / "horizontal-analysis.json", summary)
    render_horizontal_plot(output, groups)
    return summary


def render_horizontal_plot(output, groups):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    if any(font.name == "Malgun Gothic" for font in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for axis, metric, label in zip(axes, ("speed_mps", "turn_angle_50ms_deg"),
                                   ("수평 속력 (m/s)", "50ms 수평 방향 변화 (deg)")):
        for name, title, color in (("observed", "실측 보정 자료", "black"),
                                    ("observed-initial", "같은 초기 조건의 신경 모델", "#0072B2")):
            rows = groups[name]
            values = np.sort(np.concatenate([r["features"][metric] for r in rows]))
            axis.plot(values, np.arange(1, len(values) + 1) / len(values), label=title, color=color)
        axis.set(xlabel=label, ylabel="누적 비율")
        axis.grid(alpha=.2)
        axis.legend()
    figure.suptitle("실험 16개, 궤적 64개를 수평면에 투영한 비교")
    figure.savefig(output / "horizontal-diagnosis.png", dpi=160)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--raw-series", type=Path)
    args = parser.parse_args()
    run(args.prepared, args.previous, args.output, args.workers)
    if args.raw_series is not None:
        analyze_horizontal(args.output, args.prepared, args.raw_series)


if __name__ == "__main__":
    main()
