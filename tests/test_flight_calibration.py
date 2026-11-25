"""실측 보정의 단위, 경계 처리, 실험 분리와 실제 신경 상태 재현을 검사한다."""

from dataclasses import asdict
import csv
import gzip
import hashlib
import json

import numpy as np
import pytest

from flytracker.flight_calibration import (METRICS, candidate_profiles, distribution_scales,
    experiment_errors, motion_features, split_experiments, wasserstein_1d)
from flytracker.neuromechanics import MechanicsParameters
from scripts import calibrate_free_flight as calibration


def test_constant_velocity_and_acceleration_keep_physical_units():
    t=np.arange(301)*.01
    position=np.column_stack((.2*t,.3*t,np.full(len(t),.5)))
    values,_=motion_features(position)
    assert values["speed_mps"] == pytest.approx(np.hypot(.2,.3),abs=1e-12)
    assert values["acceleration_mps2"] == pytest.approx(0,abs=2e-12)
    position[:,0]=.2*t+.5*.4*t*t
    position[:,1]=0
    values,_=motion_features(position)
    assert values["acceleration_mps2"] == pytest.approx(.4,abs=1e-11)
    assert values["vertical_speed_mps"] == pytest.approx(0,abs=1e-12)


def test_direction_change_uses_velocity_not_body_attitude():
    t=np.arange(301)*.01
    position=np.column_stack((.2*np.cos(t),.2*np.sin(t),np.full(len(t),.5)))
    values,_=motion_features(position)
    assert np.median(values["turn_angle_50ms_deg"]) == pytest.approx(np.degrees(.05),abs=1e-6)
    with pytest.raises(ValueError,match="100Hz"):
        motion_features(position,dt=.02)
    position[80,0]=np.nan
    with pytest.raises(ValueError,match="유한"):
        motion_features(position)


def test_wasserstein_handles_unequal_samples_duplicates_and_invalid_values():
    assert wasserstein_1d([0,1],[1,2]) == pytest.approx(1)
    assert wasserstein_1d([0,0],[0,2]) == pytest.approx(1)
    assert wasserstein_1d([0],[0,0,0]) == 0
    with pytest.raises(ValueError):
        wasserstein_1d([], [1])
    with pytest.raises(ValueError):
        wasserstein_1d([float("inf")],[1])


def test_experiment_split_and_candidate_plan_are_deterministic():
    names=[f"experiment-{i}" for i in range(27)]
    splits=split_experiments(names+names[:5])
    assert splits==split_experiments(list(reversed(names)))
    assert {s:list(splits.values()).count(s) for s in set(splits.values())} == {
        "train":16,"development":5,"test":6}
    candidates=candidate_profiles()
    assert candidates==candidate_profiles()
    assert len(candidates)==16
    base=MechanicsParameters()
    for p in candidates:
        for key,value in p["physics"].items():
            assert .5*getattr(base,key) < value < 2*getattr(base,key)


def test_scaling_uses_training_only_and_requires_complete_matched_cases():
    def case(identifier,split,values):
        return dict(id=identifier,experiment=identifier,split=split,
                    features={key:values for key in METRICS})
    cases=[case("train","train",[0.,1.,2.,3.]),case("test","test",[100.,1000.])]
    scales=distribution_scales(cases)
    assert all(value==1.5 for value in scales.values())
    rows=experiment_errors(cases,cases,scales)
    assert all(row[key]==0 for row in rows for key in METRICS)
    with pytest.raises(ValueError,match="항목"):
        experiment_errors(cases,cases[:1],scales)


def test_prepare_selects_gray_controls_and_keeps_experiments_separate(tmp_path):
    h5py=pytest.importorskip("h5py")
    data=tmp_path/"raw";data.mkdir()
    rows=[];t=np.arange(301)*.01
    with h5py.File(data/"series.h5","w") as f:
        basic=f.create_group("basic")
        basic.attrs["col_ids"]=["x","y","z"]
        for i in range(7):
            name=f"experiment-{i}"
            positions=np.column_stack((.3*t+.02*np.cos(2*t+i),
                .1*np.sin(3*t+i),.4+.01*np.sin(5*t+i)))
            basic.create_group(name).create_dataset("1_0",data=positions)
            rows.append(dict(uuid=name,oid=1,startf=0,condition="gray",impaired="False",
                length_s=3.,dt=.01,arena="fixture",genotype="GFP"))
    rows.append(dict(rows[0],condition="rotation"))
    rows.append(dict(rows[0],impaired="True"))
    with gzip.open(data/"trials.csv.gz","wt",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (data/"README.txt").write_text("fixture",encoding="utf-8")
    (data/"experiments.csv").write_text("fixture",encoding="utf-8")
    manifest={"files":{p.name:{"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                       for p in data.iterdir()}}
    (data/"manifest.json").write_text(json.dumps(manifest),encoding="utf-8")
    out=tmp_path/"prepared"
    cases=calibration.prepare(data,out)
    assert len(cases)==7
    assert len({c["id"] for c in cases})==7
    assert all(c["genotype"]=="GFP" for c in cases)
    selection=json.loads((out/"selection.json").read_text(encoding="utf-8"))
    assert selection["controls"]==7
    assert all(c["split"]==selection["experiments"][c["experiment"]] for c in cases)
    with pytest.raises(FileExistsError):
        calibration.prepare(data,out)


def test_neural_simulation_replays_state_and_preserves_weights():
    calibration.initialize_worker()
    case=dict(id="fixture",experiment="fixture",seed=71,
              initialPosition=[0.,0.,.5],initialVelocity=[.3,0.,0.])
    a=calibration.simulate((case,{},.6,False))
    b=calibration.simulate((case,{"drag_coefficient":MechanicsParameters().drag_coefficient},.6,False))
    assert calibration.same_simulation_state(a,b)
    assert a["diagnostics"]["neurons"]==547
    assert a["diagnostics"]["connections"]==16344
    assert a["diagnostics"]["neuralTicks"]==6000
    assert a["diagnostics"]["spikes"]>0
    c=json.loads(json.dumps(b));c["diagnostics"]["finalStateSha256"]="different"
    assert not calibration.same_simulation_state(a,c)

def test_atomic_json_retries_a_temporary_windows_file_lock(tmp_path,monkeypatch):
    target=tmp_path/"progress.json"
    original=type(target).replace
    calls=[]
    def replace(path,destination):
        calls.append(path)
        if len(calls)<=2:
            raise PermissionError("temporary reader lock")
        return original(path,destination)
    monkeypatch.setattr(type(target),"replace",replace)
    calibration.write_json(target,{"completed":3})
    assert json.loads(target.read_text(encoding="utf-8"))=={"completed":3}
    assert len(calls)==3


def test_run_freezes_baseline_before_candidate_without_external_release(tmp_path, monkeypatch):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    cases = [dict(id="train-case", experiment="train", split="train"),
             dict(id="test-case", experiment="test", split="test")]
    profile = dict(id="candidate-00", physics={"drag_coefficient": .6})
    calibration.write_json(prepared / "cases.json", cases)
    calibration.write_json(prepared / "profiles.json", [profile])
    calibration.write_json(prepared / "selection.json", dict(
        scales={key: 1. for key in METRICS},
        experiments={"train": "train", "test": "test"}))
    monkeypatch.setattr(calibration, "code_signature", lambda: {})
    monkeypatch.setattr(calibration, "circuit_signature", lambda: {})
    monkeypatch.setattr(calibration.importlib.metadata, "version", lambda name: "fixture")
    rows = [dict(id=name, **{key: .1 for key in METRICS}) for name in ("train", "test")]
    monkeypatch.setattr(calibration, "experiment_errors", lambda *args: rows)
    output = tmp_path / "results"
    measured = []

    class CandidateReached(RuntimeError):
        pass

    def evaluate(cases, profile, *args, **kwargs):
        measured.append(profile["id"])
        if profile["id"] == "baseline":
            return cases
        frozen = json.loads((output / "baseline-freeze.json").read_text(encoding="utf-8"))
        assert len(frozen) == 3
        for name, expected in frozen.items():
            assert calibration.file_sha256(output / name) == expected
        assert not (output / "release-candidates").exists()
        raise CandidateReached()

    monkeypatch.setattr(calibration, "evaluate_profile", evaluate)
    with pytest.raises(CandidateReached):
        calibration.run_experiment(prepared, output, workers=1)
    assert measured == ["baseline", "candidate-00"]
