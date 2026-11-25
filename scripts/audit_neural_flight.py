"""보정 후 비행의 유한성, 보조 제어와 경계 의존도를 짧은 고정 조건에서 검사한다."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from flytracker.env import EnvConfig,FlyChaseEnv
from flytracker.flight_profiles import PROFILE_ID
from flytracker.neural_fly import NeuralConfig
from flytracker.players import baseline_player
from flytracker.stimulus import StimulusConfig
from flytracker.geometry import wrap_angle
from flytracker.neuromechanics import array
from scripts.validate_neuromechanics import StateAudit,bank_angle
from scripts.diagnose_free_flight import equilibrium

MODES=("original-free","calibrated-free","calibrated-gaze")

def describe(values):
    x=np.asarray(values,dtype=float)
    return dict(n=len(x),p05=float(np.quantile(x,.05)),median=float(np.median(x)),
                p95=float(np.quantile(x,.95)),min=float(x.min()),max=float(x.max()))

def write(path,value):
    (ROOT/"docs/issues/feature/59-feature-neural-fly-learning.md").read_text(encoding="utf-8")
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
    temp.replace(path)

def run_case(task):
    mode,seed,seconds=task
    os.environ.pop("FLYTRACKER_NEURAL_SOURCE",None)
    config=EnvConfig(fly_model="neural",max_seconds=seconds,capture_enabled=False,
        neural=NeuralConfig(profile_id="original" if mode=="original-free" else PROFILE_ID),
        stimulus=StimulusConfig(enabled=mode=="calibrated-gaze"),start_facing_fly=mode=="calibrated-gaze")
    env=FlyChaseEnv(config);obs,_=env.reset(seed=seed)
    baseline=baseline_player(config);baseline.reset()
    health=StateAudit()
    step=env.fly.step
    def observed_step(*args,**kwargs):
        step(*args,**kwargs)
        health.observe(env.fly,config.room)
    env.fly.step=observed_step
    columns=("time_s","speed_mps","horizontal_speed_mps","vertical_speed_mps","bank_deg",
        "angular_speed_deg_s","heading_velocity_deg","normal_hz","escape_hz","input_hz",
        "reflex_nm","torque_nm","corrections","events","phase","height_m")
    traces=[];off_yaw=0.;previous_on=True
    start=time.perf_counter()
    try:
        while True:
            if mode=="calibrated-gaze":
                on=round(env.t/.02)%400<200
                if on:action=baseline.act(obs)
                else:
                    if previous_on:off_yaw=env.aimer.yaw+math.pi/2
                    action=np.clip([8*wrap_angle(off_yaw-env.aimer.yaw)/math.radians(config.aimer.max_yaw_rate_deg),
                        8*(-math.pi/2-env.aimer.pitch)/math.radians(config.aimer.max_pitch_rate_deg),-1],-1,1)
                previous_on=on
                action[2]=-1
            else:action=np.array([0.,0.,-1.])
            obs,_,term,trunc,info=env.step(action)
            fly=env.fly;s=fly.sim;r=s.last_record or {}
            velocity=fly.velocity;speed=float(np.linalg.norm(velocity));bank=bank_angle(fly)
            slip=math.degrees(math.acos(float(np.clip(np.dot(fly.heading,velocity)/speed,-1,1)))) if speed>1e-9 else 0.
            traces.append([env.t,speed,float(np.linalg.norm(velocity[[0,2]])),float(velocity[1]),
                math.degrees(bank) if bank is not None else 0.,math.degrees(float(np.linalg.norm(fly.angular_velocity))),slip,
                r.get("normal_rate_hz",0.),max(r.get(k,0.) for k in
                    ("dnp06_left_hz","dnp06_right_hz","dnp03_left_hz","dnp03_right_hz")),
                max(r.get("left_input_hz",0.),r.get("right_input_hz",0.)),
                float(np.linalg.norm(s.motor.reflex_activation)),float(np.linalg.norm(s.motor.torque_body)),
                fly.boundary_corrections,len(env._stimulus.events),s.motor.phase,float(fly.pos[1])])
            if term or trunc:break
        ticks=round(seconds/.005)
        summaries={key:describe([row[i] for row in traces]) for i,key in enumerate(columns) if i not in (0,12,13,14)}
        return dict(mode=mode,seed=seed,seconds=env.t,wallSeconds=time.perf_counter()-start,
            sampleSeconds=.02,health=vars(health),metrics=summaries,bodyTicks=ticks,
            boundaryCorrections=fly.boundary_corrections,forceSaturatedSteps=fly.force_saturated_steps,
            speedWarningSteps=fly.speed_warning_steps,angularWarningSteps=fly.angular_warning_steps,
            stimulus=env._stimulus.diagnostics(),phaseEvents=fly.phase_events,
            phaseSeconds={p:.02*sum(row[14]==p for row in traces) for p in ("normal","escape","recovery")},
            analyticEquilibrium=equilibrium(s.physics),provenance=fly.provenance(),
            trace=dict(columns=columns,rows=traces))
    finally:env.close()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--seconds",type=float,default=30)
    parser.add_argument("--workers",type=int,default=3)
    parser.add_argument("--seeds",type=int,nargs="+",default=[0,1,2])
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    if args.workers<1 or len(args.seeds)!=len(set(args.seeds)):parser.error("workers/seeds")
    EnvConfig(fly_model="neural",max_seconds=args.seconds)
    names=("flytracker/neural_fly.py","flytracker/neuromechanics.py","flytracker/flight_network.py",
           "flytracker/flight_profiles.py","flytracker/env.py","flytracker/stimulus.py","scripts/audit_neural_flight.py")
    source={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
    manifest=dict(utc=datetime.now(timezone.utc).isoformat(),source=source,seconds=args.seconds,seeds=args.seeds,
        modes=MODES,workers=args.workers,host=platform.platform(),python=platform.python_version(),numpy=np.__version__,
        condition="bounded 4x2.5x3m room; capture disabled; gaze 4s baseline tracking/4s looking away; no learned policy")
    write(args.output/"manifest.json",manifest)
    completed=[];start=time.perf_counter()
    with ProcessPoolExecutor(args.workers) as pool:
        tasks={pool.submit(run_case,(mode,seed,args.seconds)):(mode,seed) for mode in MODES for seed in args.seeds}
        for future in as_completed(tasks):
            mode,seed=tasks[future]
            try:
                row=future.result();write(args.output/(mode+"-"+str(seed)+".json"),row)
                summary={k:v for k,v in row.items() if k not in ("trace","provenance")}
                completed.append(summary)
            except Exception as exc:
                write(args.output/("error-"+mode+"-"+str(seed)+".json"),dict(error=repr(exc)))
                raise
            progress=dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(completed),total=len(tasks),
                lastMode=mode,lastSeed=seed,wallSeconds=time.perf_counter()-start)
            write(args.output/"progress.json",progress);print(json.dumps(progress),flush=True)
    for name,expected in source.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:raise RuntimeError("Source changed during audit")
    write(args.output/"summary.json",dict(manifest=manifest,results=completed,wallSeconds=time.perf_counter()-start))
if __name__=="__main__":main()
