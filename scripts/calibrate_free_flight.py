"""공개 대조군 궤적을 선별하고 같은 초기 조건의 신경 비행 분포를 비교한다."""

from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from dataclasses import asdict, replace
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flytracker import NeuralConfig, NeuralFly
from flytracker.flight_calibration import (file_sha256, weights_sha256, DT, SAMPLES,
    METRICS, candidate_profiles,
    distribution_scales, experiment_errors, initial_velocity, motion_features,
    split_experiments, stable_key)
from flytracker.neural_fly import to_tracker, BUNDLED_SOURCE_ID
from flytracker.neuromechanics import MechanicsParameters, NeuromechanicalSimulation
from flytracker.world import Room


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    for attempt in range(20):
        try:
            temporary.replace(path)
            break
        except PermissionError:
            if attempt==19:
                raise
            time.sleep(.02*(attempt+1))


def prepare(data, output):
    import h5py
    data, output = Path(data), Path(output)
    if output.exists():
        raise FileExistsError("기존 선별 결과를 덮어쓰지 않습니다: " + str(output))
    manifest = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
    for name in ("trials.csv.gz", "series.h5", "README.txt", "experiments.csv"):
        if file_sha256(data / name) != manifest["files"][name]["sha256"]:
            raise ValueError("원본 자료 해시가 다릅니다: " + name)
    with gzip.open(data / "trials.csv.gz", "rt", encoding="utf-8") as stream:
        all_rows = list(csv.DictReader(stream))
    controls = [row for row in all_rows if row["condition"] == "gray" and row["impaired"] == "False"]
    eligible = [row for row in controls if float(row["length_s"]) >= 3.0 and float(row["dt"]) == DT]
    groups = {}
    for row in eligible:
        groups.setdefault(row["uuid"], []).append(row)
    cases, exclusions = [], []
    with h5py.File(data / "series.h5", "r") as archive:
        basic = archive["basic"]
        columns = [c.decode() if isinstance(c, bytes) else str(c) for c in basic.attrs["col_ids"]]
        indices = [columns.index(name) for name in ("x", "y", "z")]
        for experiment, rows in sorted(groups.items()):
            def identity(row):
                return f"{row['uuid']}/{row['oid']}_{row['startf']}"
            selected = 0
            for row in sorted(rows, key=lambda row: stable_key(identity(row))):
                identity_value = identity(row)
                try:
                    positions = np.asarray(basic[experiment][f"{int(row['oid'])}_{int(row['startf'])}"][:SAMPLES], dtype=float)[:, indices]
                    if len(positions) != SAMPLES:
                        raise ValueError("3초의 연속 위치 표본이 부족합니다.")
                    features, quality = motion_features(positions)
                    velocity = initial_velocity(positions)
                    if np.linalg.norm(velocity) < .05:
                        raise ValueError("초기 진행 방향을 정할 비행 속력이 부족합니다.")
                except (ValueError, KeyError) as exc:
                    exclusions.append(dict(id=identity_value, reason=str(exc)))
                    continue
                cases.append(dict(id=identity_value, experiment=experiment, arena=row["arena"],
                    genotype=row["genotype"], seed=int(stable_key(identity_value)[:8],16) % (2**31-1),
                    initialPosition=positions[0].tolist(), initialVelocity=velocity.tolist(),
                    features={key: values.tolist() for key, values in features.items()},
                    quality=quality))
                selected += 1
                if selected == 4:
                    break
            if not selected:
                exclusions.append(dict(experiment=experiment, reason="유효한 3초 구간이 없습니다."))
    splits = split_experiments([case["experiment"] for case in cases])
    for case in cases:
        case["split"] = splits[case["experiment"]]
    scales = distribution_scales(cases)
    output.mkdir(parents=True)
    write_json(output / "cases.json", cases)
    write_json(output / "profiles.json", candidate_profiles())
    write_json(output / "selection.json", dict(
        sourceRecord=29193, rawSha256={key: value["sha256"] for key,value in manifest["files"].items()},
        controls=len(controls), eligible=len(eligible), selectedCases=len(cases),
        experiments=splits, scales=scales, exclusions=exclusions,
        sourceColumns=columns, samplingDt=DT, sourceXYHorizontalZUp=True,
        selectionRule="First 301 samples, up to 4 hash-selected valid snippets per experiment",
        identityLimit="Trajectories do not identify independent flies"))
    result = {split:dict(experiments=sum(value==split for value in splits.values()),
                        cases=sum(case["split"]==split for case in cases))
              for split in ("train","development","test")}
    print(json.dumps(dict(state="prepared",splits=result,scales=scales)),flush=True)
    return cases


_FLY = None


def initialize_worker():
    global _FLY
    _FLY = NeuralFly(NeuralConfig(profile_id="original",source_root=BUNDLED_SOURCE_ID,boundary_enabled=False), np.random.default_rng(0))


def simulate(payload):
    case, overrides, duration, bounded = payload
    started_cpu, started_wall = time.process_time(), time.monotonic()
    fly = _FLY
    fly.p = replace(fly.p, boundary_enabled=bounded)
    fly.rng = np.random.default_rng(case["seed"])
    position = np.asarray(case["initialPosition"], dtype=float)
    velocity = np.asarray(case["initialVelocity"], dtype=float)
    fly.reset(to_tracker(position), to_tracker(velocity/np.linalg.norm(velocity)))
    initial_body = replace(fly.sim.body, velocity=fly.backend.core.Vec3(*velocity))
    if overrides:
        fly.sim = NeuromechanicalSimulation(fly.backend, seed=fly.seed,
                                            physics=MechanicsParameters(**overrides))
    fly.sim.initialize(initial_body)
    before = weights_sha256(fly)
    trajectory = [position.tolist()]
    max_quaternion_error = 0.
    min_height = float(position[2])
    for tick in range(round(duration/.005)):
        fly.step(.005, Room())
        neural, motor = fly.sim.neural, fly.sim.motor
        states = (fly.pos, fly.velocity, fly.quaternion, fly.angular_velocity,
                  neural.voltage, neural.synaptic, neural.pending, motor.filtered,
                  motor.force_body, motor.torque_body, motor.reflex_activation)
        if not all(np.isfinite(value).all() for value in states):
            raise FloatingPointError("신경 또는 신체 상태에 유한하지 않은 값이 있습니다.")
        max_quaternion_error = max(max_quaternion_error,abs(float(np.linalg.norm(fly.quaternion))-1))
        min_height = min(min_height,float(fly.pos[1]))
        if (tick+1)%2 == 0:
            b = fly.sim.body.position
            trajectory.append([b.x,b.y,b.z])
    if weights_sha256(fly) != before:
        raise ValueError("비행 중 고정 신경 가중치가 달라졌습니다.")
    state_hash=hashlib.sha256()
    for values in (neural.voltage,neural.synaptic,neural.pending,neural.next_active,
                   motor.filtered,motor.force_body,motor.torque_body,motor.reflex_activation,
                   fly.quaternion,fly.velocity,fly.angular_velocity):
        state_hash.update(np.asarray(values).tobytes())
    state_hash.update(json.dumps(neural.rng.bit_generator.state,sort_keys=True).encode())
    features, quality = motion_features(trajectory)
    return dict(id=case["id"], experiment=case["experiment"], seed=case["seed"],
        features={key:values.tolist() for key,values in features.items()}, quality=quality,
        positions=trajectory, initialVelocity=velocity.tolist(),
        diagnostics=dict(neurons=len(fly.sim.circuit.ids),connections=len(fly.sim.neural.weights),
            neuralWeightsSha256=before, neuralTicks=fly.sim.neural.tick,
            spikes=int(fly.sim.total_spikes.sum()), boundaryCorrections=fly.boundary_corrections,
            forceSaturatedSteps=fly.force_saturated_steps,speedWarningSteps=fly.speed_warning_steps,
            minHeight=min_height,maxQuaternionError=max_quaternion_error,
            finalStateSha256=state_hash.hexdigest(),
            phaseEvents=fly.phase_events,cpuSeconds=time.process_time()-started_cpu,
            wallSeconds=time.monotonic()-started_wall))


_CIRCUIT_SIGNATURE = None


def circuit_signature():
    global _CIRCUIT_SIGNATURE
    if _CIRCUIT_SIGNATURE is None:
        probe=NeuralFly(NeuralConfig(profile_id="original",source_root=BUNDLED_SOURCE_ID,boundary_enabled=False),
                        np.random.default_rng(0))
        probe.reset([0.,1.,0.],[0.,0.,-1.])
        provenance=probe.provenance()
        _CIRCUIT_SIGNATURE=dict(assetSha256=provenance["sha256"],
            weightsSha256=weights_sha256(probe),neurons=provenance["neurons"],
            connections=provenance["connections"])
    return _CIRCUIT_SIGNATURE


def code_signature():
    names = ("scripts/calibrate_free_flight.py", "flytracker/flight_calibration.py",
             "flytracker/neural_fly.py", "flytracker/flight_profiles.py", "flytracker/neuromechanics.py", "flytracker/flight_network.py")
    return {name:file_sha256(ROOT/name) for name in names}


def evaluate_profile(cases, profile, output, workers=4, duration=3., bounded=False, max_seconds=1800):
    output = Path(output)
    signature = dict(profile=profile, source=code_signature(),circuit=circuit_signature(),
        cases=[dict(id=c["id"],seed=c["seed"],position=c["initialPosition"],velocity=c["initialVelocity"]) for c in cases],
        duration=duration,bounded=bounded)
    metadata = output/"manifest.json"
    if metadata.exists():
        if json.loads(metadata.read_text(encoding="utf-8")) != signature:
            raise ValueError("이전 계산의 코드, 계수 또는 초기 조건이 다릅니다.")
    else:
        output.mkdir(parents=True,exist_ok=True)
        write_json(metadata,signature)
    start = time.monotonic()
    results, pending = [], []
    for case in cases:
        path = output/(stable_key(case["id"])+".json")
        if path.exists():
            results.append(json.loads(path.read_text(encoding="utf-8")))
        else:
            pending.append(case)
    progress = output.parent.parent/"progress.json"
    with ProcessPoolExecutor(max_workers=workers,initializer=initialize_worker) as pool:
        futures = {pool.submit(simulate,(case,profile["physics"],duration,bounded)):case for case in pending}
        for future in as_completed(futures):
            case = futures[future]
            result = future.result()
            write_json(output/(stable_key(case["id"])+".json"),result)
            results.append(result)
            status = dict(state="simulating",profile=profile["id"],completed=len(results),total=len(cases),
                elapsedSeconds=time.monotonic()-start,utc=datetime.now(timezone.utc).isoformat())
            write_json(progress,status)
            print(json.dumps(status),flush=True)
            if time.monotonic()-start>max_seconds:
                for job in futures:
                    job.cancel()
                raise TimeoutError("후보 계산의 시간 상한을 넘었습니다.")
    expected_weights=signature["circuit"]["weightsSha256"]
    if any(row["diagnostics"]["neuralWeightsSha256"]!=expected_weights for row in results):
        raise ValueError("Neural circuit weights differ from the frozen baseline")
    by_id={row["id"]:row for row in results}
    return [by_id[case["id"]] for case in cases]


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=["id",*METRICS])
        writer.writeheader()
        writer.writerows(rows)


def same_simulation_state(a, b):
    def state(row):
        values=dict(row)
        values["diagnostics"]={key:value for key,value in row["diagnostics"].items()
                               if key not in ("cpuSeconds","wallSeconds")}
        return values
    return state(a)==state(b)


def run_gate_tool(script, arguments, log):
    import subprocess
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run([sys.executable,"-B",str(ROOT/".claude/skills/experiment-gate/scripts"/script),
                        *map(str,arguments)],stdout=stream,stderr=subprocess.STDOUT,check=True)


def run_experiment(prepared, output, workers):
    prepared, output = Path(prepared), Path(output)
    cases=json.loads((prepared/"cases.json").read_text(encoding="utf-8"))
    selection=json.loads((prepared/"selection.json").read_text(encoding="utf-8"))
    profiles=json.loads((prepared/"profiles.json").read_text(encoding="utf-8"))
    context=dict(source=code_signature(),circuit=circuit_signature(),casesSha256=file_sha256(prepared/"cases.json"),
                 profilesSha256=file_sha256(prepared/"profiles.json"),workers=workers,
                 physicsDefaults=asdict(MechanicsParameters()),
                 versions={name:importlib.metadata.version(name) for name in
                           ("numpy","h5py","matplotlib","gymnasium","pyarrow")},
                 host=platform.platform(),python=platform.python_version())
    output.mkdir(parents=True,exist_ok=True)
    runtime=output/"runtime.json"
    if runtime.exists() and json.loads(runtime.read_text(encoding="utf-8"))!=context:
        raise ValueError("실행 코드, 자료나 계산 환경이 이전 실행과 다릅니다.")
    write_json(runtime,context)
    started=time.monotonic()
    def status(state,**values):
        write_json(output/"progress.json",dict(state=state,
            elapsedSeconds=time.monotonic()-started,utc=datetime.now(timezone.utc).isoformat(),**values))
        print(json.dumps(dict(state=state,**values)),flush=True)
    calibration=[c for c in cases if c["split"]!="test"]
    heldout=[c for c in cases if c["split"]=="test"]
    scales=selection["scales"]
    baseline_profile=dict(id="baseline",physics={})
    status("baseline",cases=len(cases))
    baseline=evaluate_profile(cases,baseline_profile,output/"simulations/baseline",workers)
    rows=experiment_errors(cases,baseline,scales)
    base_all=output/"baseline-all.csv"
    if base_all.exists():
        original=base_all.read_bytes()
        write_csv(output/"baseline-check.csv",rows)
        if original!=(output/"baseline-check.csv").read_bytes():
            raise ValueError("고정 기준선의 재계산 결과가 다릅니다.")
    else:
        write_csv(base_all,rows)
    split_by_exp=selection["experiments"]
    base_cal=[r for r in rows if split_by_exp[r["id"]]!="test"]
    base_test=[r for r in rows if split_by_exp[r["id"]]=="test"]
    write_csv(output/"calibration/baseline.csv",base_cal)
    write_csv(output/"calibration/truth.csv",[{k:(r[k] if k=="id" else 0.) for k in r} for r in base_cal])
    write_csv(output/"test/baseline.csv",base_test)
    write_csv(output/"test/truth.csv",[{k:(r[k] if k=="id" else 0.) for k in r} for r in base_test])
    frozen={str(p.relative_to(output)):file_sha256(p) for p in
            (base_all,output/"calibration/baseline.csv",output/"test/baseline.csv")}
    freeze=output/"baseline-freeze.json"
    if freeze.exists() and json.loads(freeze.read_text(encoding="utf-8"))!=frozen:
        raise ValueError("고정 기준선 해시가 다릅니다.")
    write_json(freeze,frozen)
    status("baseline_frozen", hashes=frozen)
    failures=[]
    for index,profile in enumerate(profiles):
        if time.monotonic()-started>5400:
            raise TimeoutError("전체 보정 실행 90분 상한을 넘었습니다.")
        status("candidate",candidate=profile["id"],index=index+1,total=len(profiles))
        try:
            simulated=evaluate_profile(calibration,profile,output/"simulations"/profile["id"],workers)
            errors=experiment_errors(calibration,simulated,scales)
            write_csv(output/"calibration/candidates"/(profile["id"]+".csv"),errors)
        except (ValueError,FloatingPointError,TimeoutError) as exc:
            failures.append(dict(candidate=profile["id"],error=str(exc)))
            write_json(output/"candidate-failures.json",failures)
    if not list((output/"calibration/candidates").glob("*.csv")):
        raise ValueError("완료한 보정 후보가 없습니다.")
    status("selection")
    run_gate_tool("holdout_select.py",[
        "--truth",output/"calibration/truth.csv","--baseline",output/"calibration/baseline.csv",
        "--candidates",output/"calibration/candidates","--metric","composite","--composite","1-mae",
        "--round","none","--seeds","8","--folds","2","--seed","42",
        "--json",output/"selection.json"],output/"selection.log")
    picked=json.loads((output/"selection.json").read_text(encoding="utf-8"))
    ranked=sorted(picked["holdout"]["picks"],key=lambda row:(-row[1],Path(row[0]).stem))
    selected_id=Path(ranked[0][0]).stem
    profile=next(p for p in profiles if p["id"]==selected_id)
    profile_path=output/"calibration-profile.json"
    write_json(profile_path,dict(profile=profile,source=context,condition="3-second gray-control free flight",
        defaultsApplied=False,selectionPicks=ranked))
    status("heldout",candidate=selected_id,cases=len(heldout))
    test=evaluate_profile(heldout,profile,output/"simulations/final-test",workers)
    errors=experiment_errors(heldout,test,scales)
    write_csv(output/"test/candidate.csv",errors)
    run_gate_tool("paired_bootstrap.py",[
        "--truth",output/"test/truth.csv","--a",output/"test/baseline.csv",
        "--b",output/"test/candidate.csv","--metric","composite","--composite","1-mae",
        "--round","none","--resamples","10000","--seed","42","--threshold",".90",
        "--json",output/"test/bootstrap.json"],output/"test/bootstrap.log")
    status("replay",candidate=selected_id)
    loaded=json.loads(profile_path.read_text(encoding="utf-8"))["profile"]
    replay=evaluate_profile(heldout,loaded,output/"simulations/reloaded-test",workers)
    replay_equal=all(same_simulation_state(a,b) for a,b in zip(test,replay))
    write_json(output/"test/replay.json",dict(equal=replay_equal,episodes=len(test)))
    status("room_stability",candidate=selected_id)
    validation=[]
    for seed in (59001,59002,59003):
        rng=np.random.default_rng(seed)
        pos=Room().sample(rng,margin=.4)
        heading=np.array([rng.normal(),.2*rng.normal(),rng.normal()])
        heading/=np.linalg.norm(heading)
        native=np.array([-heading[2],-heading[0],heading[1]])
        validation.append(dict(id=f"room-{seed}",experiment="room",seed=seed,
            initialPosition=[-pos[2],-pos[0],pos[1]],initialVelocity=(.35*native).tolist()))
    room_base=evaluate_profile(validation,baseline_profile,output/"simulations/room-baseline",
                               workers,duration=30.,bounded=True)
    room_candidate=evaluate_profile(validation,profile,output/"simulations/room-candidate",
                                    workers,duration=30.,bounded=True)
    write_json(output/"room-stability.json",dict(secondsPerEpisode=30,seeds=[59001,59002,59003],
        baseline=[r["diagnostics"] for r in room_base],
        candidate=[r["diagnostics"] for r in room_candidate]))
    gate=json.loads((output/"test/bootstrap.json").read_text(encoding="utf-8"))
    all_targets_improved=all(row["delta"]>0 for row in gate["rows"])
    finite_and_stable=all(row["diagnostics"]["maxQuaternionError"]<1e-8 and
                          row["diagnostics"]["speedWarningSteps"]==0 for row in room_candidate)
    decision="adopt_candidate" if (gate["macro"]["p_better"]>=.9 and all_targets_improved
                                   and replay_equal and finite_and_stable) else "retain_baseline"
    summary=dict(state="completed",decision=decision,selected=profile,
        calibrationExperiments=len(base_cal),testExperiments=len(base_test),
        candidateFailures=failures,replayEqual=replay_equal,allTargetsImproved=all_targets_improved,
        roomStable=finite_and_stable,elapsedSeconds=time.monotonic()-started,
        perTarget=gate["rows"],macro=gate["macro"],source=context)
    write_json(output/"result.json",summary)
    render_plot(cases,baseline,heldout,test,output/"heldout-distributions.png")
    status("completed",decision=decision,selected=selected_id)
    return summary


def render_plot(cases,baseline,heldout,candidate,target):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    names={font.name for font in font_manager.fontManager.ttflist}
    if "Malgun Gothic" in names:
        plt.rcParams["font.family"]="Malgun Gothic"
    plt.rcParams["axes.unicode_minus"]=False
    labels=("속력 (m/s)","가속도 크기 (m/s²)","50ms 진행 방향 변화 (deg)","수직 속도 (m/s)")
    baseline_by_id={row["id"]:row for row in baseline}
    groups=[("실측",heldout,"black"),("보정 전",[baseline_by_id[c["id"]] for c in heldout],"#0072B2"),
            ("보정 후보",candidate,"#D55E00")]
    figure,axes=plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
    for axis,key,label in zip(axes.flat,METRICS,labels):
        for name,rows,color in groups:
            values=np.sort(np.concatenate([row["features"][key] for row in rows]))
            axis.plot(values,np.arange(1,len(values)+1)/len(values),label=name,color=color)
        axis.set_xlabel(label);axis.set_ylabel("누적 비율");axis.grid(alpha=.2)
        axis.legend()
    figure.suptitle("독립 실험 6개, 3초 궤적 24개")
    figure.savefig(target,dpi=160)
    plt.close(figure)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    ready=sub.add_parser("prepare")
    ready.add_argument("--data",required=True)
    ready.add_argument("--output",required=True)
    benchmark=sub.add_parser("benchmark")
    benchmark.add_argument("--prepared",required=True)
    benchmark.add_argument("--output",required=True)
    benchmark.add_argument("--workers",type=int,default=4)
    run=sub.add_parser("run")
    run.add_argument("--prepared",required=True)
    run.add_argument("--output",required=True)
    run.add_argument("--workers",type=int,default=4)
    args=parser.parse_args()
    if args.command=="prepare":
        prepare(args.data,args.output)
    elif args.command=="run":
        run_experiment(args.prepared,args.output,args.workers)
    else:
        prepared=Path(args.prepared);cases=json.loads((prepared/"cases.json").read_text(encoding="utf-8"))
        cases=[case for case in cases if case["split"]=="train"][:4]
        start=time.monotonic()
        results=evaluate_profile(cases,dict(id="benchmark",physics={}),Path(args.output)/"simulations/benchmark",args.workers)
        print(json.dumps(dict(cases=len(results),wallSeconds=time.monotonic()-start,
            diagnoses=[r["diagnostics"] for r in results])),flush=True)


if __name__=="__main__":
    main()
