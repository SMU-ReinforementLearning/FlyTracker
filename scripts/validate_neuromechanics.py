"""축약 신경 생체역학의 인과·반응·안정성 검사. 생체 일치 판정은 하지 않는다."""
from dataclasses import asdict, replace
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
from threading import Event, Thread
import time

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from flytracker import NeuralConfig, NeuralFly, StimulusConfig
from flytracker.neural_fly import to_tracker
from flytracker.geometry import unit
from flytracker.world import Room
from scripts.record_neural_demo_suite import source_inventory

SEEDS=(801,802,803,804,805)


def heading_angles(heading):
    """Tracker world heading -> native yaw (left positive), elevation, radians."""
    x, y, z = heading
    return math.atan2(-x, -z), math.asin(float(np.clip(y, -1., 1.)))


def angular_difference(a, b):
    return math.atan2(math.sin(a-b), math.cos(a-b))


def bank_angle(fly):
    """Signed tilt of native body-up against roll-free world-up, radians."""
    body_up = to_tracker(list(asdict(fly.backend.behavior.rotate(
        fly.sim.body.quaternion, fly.backend.core.Vec3(0, 0, 1))).values()))
    forward = fly.heading
    left = np.cross([0., 1., 0.], forward)
    n = np.linalg.norm(left)
    if n < 1e-8:
        return None  # Roll reference is singular for a vertical heading.
    left /= n
    upright = np.cross(forward, left)
    return math.atan2(float(body_up @ left), float(body_up @ upright))


class StateAudit:
    """Observe every body substep, including neural queues and motor commands."""
    def __init__(self):
        self.samples = self.nonfinite = self.outside = self.bad_quaternion = 0
        self.speed_min = math.inf
        self.speed_max = self.angular_max = self.quaternion_error = self.bank_max = 0.
        self.height_min, self.height_max = math.inf, -math.inf

    def observe(self, fly, room):
        s = fly.sim
        arrays = [fly.pos, fly.velocity, fly.quaternion, fly.angular_velocity,
                  s.neural.voltage, s.neural.synaptic, s.neural.pending,
                  s.motor.filtered, s.motor.force_body, s.motor.torque_body,
                  s.motor.reflex_activation, *s.motor.delayed_sense, s.motor.sensed_rotation]
        self.samples += 1
        self.nonfinite += int(not all(np.isfinite(a).all() for a in arrays))
        self.outside += int(not room.contains(fly.pos, margin=.02-1e-10))
        error = abs(float(np.linalg.norm(fly.quaternion))-1.)
        self.quaternion_error = max(self.quaternion_error, error)
        self.bad_quaternion += int(error > 1e-9)
        self.speed_min = min(self.speed_min, fly.speed)
        self.speed_max = max(self.speed_max, fly.speed)
        self.angular_max = max(self.angular_max, float(np.linalg.norm(fly.angular_velocity)))
        bank = bank_angle(fly)
        if bank is not None:
            self.bank_max = max(self.bank_max, abs(bank))
        self.height_min = min(self.height_min, float(fly.pos[1]))
        self.height_max = max(self.height_max, float(fly.pos[1]))


def make(config,seed,random_initial=False):
    f=NeuralFly(config,np.random.default_rng(seed))
    if random_initial:
        position=Room().sample(f.rng,margin=.4)
        heading=unit(np.array([f.rng.normal(),.2*f.rng.normal(),f.rng.normal()]))
        f.reset(position,heading)
    else:
        f.reset([0,1.2,0],[0,0,-1])
    return f


def response(config,seed,distance=1.,azimuth=90.,elevation=0.,stimulus=True):
    f,room=make(config,seed),Room()
    f.step(1.,room)
    a,e=math.radians(azimuth),math.radians(elevation)
    delta=f.backend.core.Vec3(distance*math.cos(e)*math.cos(a),distance*math.cos(e)*math.sin(a),distance*math.sin(e))
    delta=f.backend.behavior.rotate(f.sim.body.quaternion,delta)
    origin=f.pos+to_tracker([delta.x,delta.y,delta.z])
    event=dict(event_id=1,onset_ms=1000,source=origin.tolist())
    settings=StimulusConfig()
    keys=('left_input_hz','right_input_hz','dnp06_left_hz','dnp06_right_hz','dnp03_left_hz','dnp03_right_hz')
    peaks={k:0. for k in keys}
    first_input=first_neural=None
    trace=[]
    start=time.perf_counter()
    for tick in range(1000,2000,5):
        f.present_stimulus(event if stimulus and tick<1250 else None,settings)
        f.step(.005,room)
        d=f.diagnostics(); raw=f.sim.last_record
        for k in keys: peaks[k]=max(peaks[k],raw[k])
        if first_input is None and max(raw['left_input_hz'],raw['right_input_hz'])>0: first_input=tick
        if first_neural is None and max(raw[k] for k in keys[2:])>=40: first_neural=tick+5
        trace.append(dict(time_ms=tick+5,heading=f.heading.tolist(),position=f.pos.tolist(),
                          speed=f.speed,angular_speed=float(np.linalg.norm(f.angular_velocity)),
                          bank_rad=bank_angle(f),phase=d['phase']))
    return dict(seed=seed,lesion=config.lesion,distance_m=distance,azimuth_deg=azimuth,elevation_deg=elevation,
                presentation=event if stimulus else None,first_sensory_sample_ms=first_input,
                first_motor_rate_over_40_ms=first_neural,peaks=peaks,
                phase_events=[e for e in f.phase_events if e['time_ms']>=1000],trace=trace,
                final=f.diagnostics(),poststim_wall_s=time.perf_counter()-start)


def compare(row,control,stimulus_comparison=True):
    if row['seed']!=control['seed'] or (stimulus_comparison and row['lesion']!=control['lesion']):
        raise ValueError('자극 반응은 같은 seed와 같은 회로의 무자극 실행과 비교해야 합니다.')
    if len(row['trace'])!=len(control['trace']) or any(a['time_ms']!=b['time_ms'] for a,b in zip(row['trace'],control['trace'])):
        raise ValueError('비교 궤적의 시간 표본이 일치하지 않습니다.')
    dots=[float(np.dot(a['heading'],b['heading'])) for a,b in zip(row['trace'],control['trace'])]
    angles=np.degrees(np.arccos(np.clip(dots,-1,1)))
    row['max_heading_separation_deg']=float(max(angles))
    row['final_position_separation_m']=float(np.linalg.norm(np.subtract(row['trace'][-1]['position'],control['trace'][-1]['position'])))
    if stimulus_comparison:
        row['kinematic_response_over_15deg']=bool(max(angles)>=15)
        row['comparison']='같은 회로·seed의 무자극 비행'
    else:
        row['comparison']='무손상 무자극 비행과 억제 무자극 비행의 차이. 자극 반응이 아님'


def control_response(config,seed,baseline):
    stimulated=config.lesion in ('DNp06','escape','disconnected')
    row=response(config,seed,stimulus=stimulated)
    if stimulated:
        paired=response(config,seed,stimulus=False)
        row['paired_no_stimulus']=paired
        compare(row,paired)
    elif baseline is not None:
        compare(row,baseline,stimulus_comparison=False)
    return row


def longer(config,seed,seconds,progress):
    f,room=make(config,seed,random_initial=True),Room(); audit=StateAudit()
    initial=dict(position=f.pos.tolist(),heading=f.heading.tolist(),velocity=f.velocity.tolist())
    start=time.perf_counter(); trace=[]; phases={p:0 for p in ('normal','escape','recovery')}
    force_nonfinite=angular_warnings=0; stroke_max=0.
    contact_run=max_contact_run=0
    for tick in range(round(seconds/.005)):
        old_contacts=f.boundary_corrections
        f.step(.005,room); audit.observe(f,room)
        contact_run=contact_run+1 if f.boundary_corrections>old_contacts else 0
        max_contact_run=max(max_contact_run,contact_run)
        m=f.sim.motor; r=f.sim.last_record
        force_nonfinite+=int(not np.isfinite(np.r_[m.force_body,m.torque_body,m.reflex_activation,
                                                  m.delayed_sense[0],m.delayed_sense[1],m.delayed_sense[2],
                                                  m.sensed_rotation]).all())
        angular_warnings+=int(np.linalg.norm(f.angular_velocity)>f.sim.physics.angular_warning_rad_s)
        stroke_max=max(stroke_max,r['stroke_amplitude_rad'])
        phases[m.phase]+=1
        if (tick+1)%4==0:
            trace.append([f.sim.clock.tick,*f.pos,f.speed,*f.angular_velocity,bank_angle(f)])
        if (tick+1)%2000==0:
            progress(dict(section='long',seed=seed,simulated_s=(tick+1)*.005,
                          contact=f.boundary_corrections,nonfinite=audit.nonfinite+force_nonfinite))
    return dict(seed=seed,simulated_s=seconds,wall_s=time.perf_counter()-start,
                checks=vars(audit),force_nonfinite=force_nonfinite,angular_warning_steps=angular_warnings,
                stroke_amplitude_max_rad=stroke_max,phase_steps=phases,trace_20ms=trace,
                max_continuous_contact_ms=max_contact_run*5,contact_sticking_warning=max_contact_run*5>100,
                trace_columns=['time_ms','x','y','z','speed','omega_x','omega_y','omega_z','bank_rad'],
                initial=initial,final=f.diagnostics(),phase_events=f.phase_events)


def run(source,out):
    source,out=source.resolve(),out.resolve()
    allowed=ROOT/'docs/issues/feature/31-feature-neural-flight'
    if allowed not in out.parents or source==out or source in out.parents:
        raise ValueError('출력은 원본 밖 Issue #31의 새 하위 폴더여야 합니다.')
    before=source_inventory(source)
    config=NeuralConfig(source_root=str(source),boundary_enabled=False)
    probe=make(config,SEEDS[0])
    out.mkdir()
    stop=Event(); heartbeat=[time.monotonic()]
    hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
            ('flytracker/neural_fly.py','flytracker/flight_network.py','flytracker/neuromechanics.py',
             'flytracker/stimulus.py','scripts/validate_neuromechanics.py')}
    result=dict(python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),
                cpu=os.environ.get('PROCESSOR_IDENTIFIER'),seeds=SEEDS,source_provenance=probe.provenance(),
                integration_sha256=hashes,timing='CPU 독점 보장 없음. 실행 비용은 기술적 기록이며 성능 우월성 판정에 사용하지 않음',
                biological_verdict='미검증: 실측 정답 및 발화–날개 변환 자료가 없음',
                responses=[],controls=[],long=[],failures=[])
    with (out/'frozen-inputs.json').open('x',encoding='utf-8') as h:
        json.dump({k:v for k,v in result.items() if k not in ('responses','controls','long','failures')},h,indent=2,ensure_ascii=False)
    with (out/'progress.jsonl').open('x',encoding='utf-8') as ledger:
        def progress(row):
            heartbeat[0]=time.monotonic()
            row=dict(utc=datetime.now(timezone.utc).isoformat(),**row)
            ledger.write(json.dumps(row,ensure_ascii=False)+'\n'); ledger.flush()
            print(json.dumps(row,ensure_ascii=True),flush=True)
        def watch():
            while not stop.wait(10):
                if time.monotonic()-heartbeat[0]>90:
                    print('STALL_WARNING: 90초 넘게 검사 진행 기록이 없습니다.',flush=True)
        Thread(target=watch,daemon=True).start()
        def save(name,row):
            with (out/name).open('x',encoding='utf-8') as h: json.dump(row,h,indent=2,ensure_ascii=False,allow_nan=False)
        def guarded(section,condition,fn):
            try:
                row=fn(); result[section].append(row); return row
            except Exception as exc:
                result['failures'].append(dict(section=section,condition=condition,error=repr(exc)))
                progress(dict(section='failure',condition=condition,error=repr(exc)))
                return None
        try:
            progress(dict(section='start',expected_responses=60,expected_controls=30,additional_matched_no_stimulus=15,expected_long=7))
            row=guarded('long',dict(seed=0,seconds=30.),
                        lambda:longer(replace(config,boundary_enabled=True),0,30.,progress))
            if row is not None: save('long-0.json',row)
            geometries=[(d,a,0.) for d in (.3,1.,3.) for a in (-90.,0.,90.)]+[(1.,180.,0.),(1.,45.,-30.),(1.,45.,30.)]
            for seed in SEEDS:
                baseline=guarded('controls',dict(seed=seed,lesion='none',stimulus=False),lambda:response(config,seed,stimulus=False))
                for distance,azimuth,elevation in geometries:
                    row=guarded('responses',dict(seed=seed,distance=distance,azimuth=azimuth,elevation=elevation),
                                lambda:response(config,seed,distance,azimuth,elevation))
                    if row is not None and baseline is not None: compare(row,baseline)
                    progress(dict(section='response',seed=seed,completed=len(result['responses']),failures=len(result['failures'])))
                for lesion in ('DNp06','escape','disconnected','DNg02','SGU'):
                    cfg=replace(config,lesion=lesion)
                    row=guarded('controls',dict(seed=seed,lesion=lesion),
                                lambda:control_response(cfg,seed,baseline))
                    progress(dict(section='control',seed=seed,lesion=lesion,completed=len(result['controls'])))
                save(f'response-{seed}.json',dict(responses=[r for r in result['responses'] if r['seed']==seed],
                                                controls=[r for r in result['controls'] if r['seed']==seed]))
            for seed in (*SEEDS,806):
                seconds=60. if seed==806 else 30.
                row=guarded('long',dict(seed=seed,seconds=seconds),
                            lambda:longer(replace(config,boundary_enabled=True),seed,seconds,progress))
                if row is not None: save(f'long-{seed}.json',row)
            result['source_files_checked']=len(before)
            for row in result['long']:
                if row['contact_sticking_warning']:
                    result['failures'].append(dict(section='long',condition=dict(seed=row['seed']),error='연속 경계 보정이 100ms를 초과함'))
            result['source_unchanged']=before==source_inventory(source)
            result['code_unchanged_during_run']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
            save('results.json',result)
            progress(dict(section='complete',responses=len(result['responses']),controls=len(result['controls']),
                          long=len(result['long']),failures=len(result['failures']),source_unchanged=result['source_unchanged']))
            if result['failures'] or not result['source_unchanged'] or not result['code_unchanged_during_run']:
                raise RuntimeError('실패 또는 실행 중 변경이 있습니다. 보존된 결과를 확인하세요.')
        except Exception as exc:
            progress(dict(section='aborted',error=repr(exc)))
            save('aborted.json',dict(error=repr(exc),responses=len(result['responses']),controls=len(result['controls']),long=len(result['long'])))
            raise
        finally: stop.set()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--output-dir',required=True,type=Path)
    args=parser.parse_args(); run(args.source,args.output_dir)
