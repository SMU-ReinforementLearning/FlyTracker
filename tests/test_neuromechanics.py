"""새 날개 동역학의 물리·회로·재현성 계약. 생체 행동 일치 시험과 구분한다."""
from dataclasses import replace
import math
import os

import numpy as np
import pytest

from flytracker import EnvConfig, FlyChaseEnv, EpisodeRecorder, NeuralConfig, NeuralFly, StimulusConfig
from flytracker.flight_network import expand_flight_network
from flytracker.neural_fly import load_backend
from flytracker.neuromechanics import MechanicsParameters, integrate, array
from flytracker.world import Room


@pytest.fixture(scope='module')
def config():
    if not os.environ.get('FLYTRACKER_NEURAL_SOURCE'):
        pytest.skip('FLYTRACKER_NEURAL_SOURCE로 로컬 원본을 지정해야 합니다.')
    return NeuralConfig(dynamics='neuromechanical',boundary_enabled=False)


def make(config,seed=301):
    f=NeuralFly(config,np.random.default_rng(seed))
    f.reset([0,1.2,0],[0,0,-1])
    return f


def test_no_force_has_gravity_and_bank_rotates_lift(config):
    f=make(config); b=f.backend; p=MechanicsParameters()
    body=b.physics.BodyState(position=b.core.Vec3(0,0,1.2))
    falling=integrate(body,np.zeros(3),np.zeros(3),0.,.005,b,p)
    assert falling.velocity.z == pytest.approx(-p.gravity*.005)
    assert falling.position.z == pytest.approx(1.2-p.gravity*.005**2/2)
    banked=replace(body,quaternion=(math.sqrt(.5),math.sqrt(.5),0.,0.))
    turned=integrate(banked,np.array([0,0,p.mass_kg*p.gravity]),np.zeros(3),0.,.005,b,p)
    assert turned.velocity.y == pytest.approx(-p.gravity*.005)
    assert turned.velocity.z == pytest.approx(-p.gravity*.005)
    assert turned.quaternion == pytest.approx(banked.quaternion)


def test_zero_neural_power_cannot_hover_or_restore_pose(config):
    f=make(config); motor=f.sim.motor; b=f.backend
    body=replace(f.sim.body,quaternion=(math.sqrt(.5),0,math.sqrt(.5),0),angular_rate=b.core.Vec3(1,2,3))
    original=body
    motor.reflex_activation[:]=1e-10
    for _ in range(5):
        motor.decode(np.zeros(len(b.circuit.ids)),.005,body)
        np.testing.assert_array_equal(motor.force_body,[0,0,0])
        np.testing.assert_array_equal(motor.torque_body,[0,0,0])
    assert body == original
    assert motor.drag == 0


def test_published_fct_units_frame_and_decay(config):
    f=make(config); b=f.backend
    p=MechanicsParameters(body_length_m=.001)
    drag=(p.air_density*p.total_wing_area_m2*p.drag_coefficient*4*p.wingbeat_hz*p.wing_arm
          *p.fct_reference_half_stroke_rad)
    damping=p.rotational_damping(drag)
    np.testing.assert_allclose(np.linalg.eigvalsh(damping),np.sort([p.fct_roll_nms,p.fct_pitch_nms,p.fct_yaw_nms])*p.wingbeat_hz/p.fct_reference_hz,rtol=1e-14)
    axis=np.array([math.sin(p.stroke_plane_forward_rad),0,math.cos(p.stroke_plane_forward_rad)])
    body=b.physics.BodyState(angular_rate=b.core.Vec3(*(3*axis)))
    result=integrate(body,np.zeros(3),np.zeros(3),drag,.001,b,p)
    expected=3*math.exp(-p.fct_yaw_nms*(p.wingbeat_hz/p.fct_reference_hz)*.001/p.inertia[0])
    assert np.linalg.norm(array(result.angular_rate))==pytest.approx(expected,rel=5e-4)
    np.testing.assert_array_equal(p.rotational_damping(0),np.zeros((3,3)))


def test_muscle_feedback_has_no_world_up_or_quaternion_oracle(config):
    a,b=make(config),make(config)
    # 각속도 기록이 같으면 외부에서 자세만 순간 변경해도 근육 피드백은 이를 알 수 없다.
    # 실제 물리 적분의 회전은 각속도 감각에 나타나며 별도 내부 적분 상태로 누적된다.
    altered=replace(b.sim.body,quaternion=(math.sqrt(.5),0,math.sqrt(.5),0))
    for f,body in ((a,a.sim.body),(b,altered)):
        f.sim.motor.filtered[f.sim.motor.normal]=f.sim.motor.reference_rate
        for _ in range(3):
            f.sim.motor.decode(np.zeros(len(f.backend.circuit.ids)),.005,body)
    np.testing.assert_array_equal(a.sim.motor.force_body,b.sim.motor.force_body)
    np.testing.assert_array_equal(a.sim.motor.torque_body,b.sim.motor.torque_body)


def test_initial_trim_frame_tracks_body_pitch_without_using_velocity(config):
    f=make(config);b=f.backend;p=f.sim.physics
    for pitch in (-.3,0.,.3):
        f.reset([0,1.2,0],[0,math.sin(pitch),-math.cos(pitch)])
        direction=f.sim.motor.trim_force_direction.copy()
        world=array(b.behavior.rotate(f.sim.body.quaternion,b.core.Vec3(*direction)))
        np.testing.assert_allclose(world,[math.sin(p.stroke_plane_forward_rad),0,math.cos(p.stroke_plane_forward_rad)],atol=1e-14)
        changed=replace(f.sim.body,velocity=b.core.Vec3(8,9,10))
        f.sim.initialize(changed)
        np.testing.assert_array_equal(direction,f.sim.motor.trim_force_direction)
        for yaw in (0.,math.pi/2,math.pi):
            q=b.physics.qmultiply((math.cos(yaw/2),0,0,math.sin(yaw/2)),f.sim.body.quaternion)
            force=array(b.behavior.rotate(q,b.core.Vec3(*direction)))
            assert force[2]==pytest.approx(math.cos(p.stroke_plane_forward_rad))


def test_contact_preserves_pose_neural_and_muscle_state(config):
    f=make(replace(config,boundary_enabled=True)); body=f.sim.body
    f.pos=[2.1,1.2,0]
    f.sim.motor.force_body[:]=[1e-6,0,1e-5]
    f.sim.motor.torque_body[:]=[1e-11,0,2e-11]
    f.sim.motor.reflex_activation[:]=[2e-12,1e-12,0]
    before=[x.copy() for x in (f.sim.motor.force_body,f.sim.motor.torque_body,f.sim.motor.reflex_activation)]
    pending=f.sim.neural.pending
    f._correct_room(Room())
    assert f.sim.body.quaternion==body.quaternion and f.sim.body.angular_rate==body.angular_rate
    assert f.boundary_corrections==1 and Room().contains(f.pos,margin=.02-1e-10)
    assert f.sim.neural.pending is pending
    for a,b in zip(before,(f.sim.motor.force_body,f.sim.motor.torque_body,f.sim.motor.reflex_activation)):
        np.testing.assert_array_equal(a,b)


def test_previous_command_is_applied_before_next_neural_output(config):
    f=make(replace(config,lesion='disconnected')); b=f.backend; p=f.sim.physics
    f.sim.body=replace(f.sim.body,velocity=b.physics.ZERO)
    f.sim.motor.force_body[:]=[0,0,p.mass_kg*p.gravity]
    f.step(.005,Room())
    assert f.velocity == pytest.approx([0,0,0],abs=1e-15)
    assert f.diagnostics()['applied_control']['wing_force_body']==[0,0,p.mass_kg*p.gravity]
    np.testing.assert_array_equal(f.sim.motor.force_body,[0,0,0])
    f.step(.005,Room())
    assert f.velocity[1] == pytest.approx(-p.gravity*.005)
    assert f.sim.neural.tick==100 and f.sim.clock.tick==10


def test_chunking_preserves_new_physics_and_state(config):
    a,b=make(config),make(config)
    a.step(.5,Room())
    for _ in range(50): b.step(.01,Room())
    for x,y in ((a.pos,b.pos),(a.velocity,b.velocity),(a.quaternion,b.quaternion),
                (a.sim.neural.pending,b.sim.neural.pending),(a.sim.neural.voltage,b.sim.neural.voltage),
                (a.sim.motor.reflex_activation,b.sim.motor.reflex_activation),
                (a.sim.motor.sensed_rotation,b.sim.motor.sensed_rotation),
                (a.sim.motor.delayed_sense,b.sim.motor.delayed_sense),
                (a.sim.motor.filtered,b.sim.motor.filtered)):
        np.testing.assert_array_equal(x,y)
    assert a.diagnostics()['speed_command_mps'] is None


def test_motor_ablations_remove_wing_power_and_saccade_output(config):
    f=make(replace(config,lesion='DNg02'))
    f.step(.5,Room())
    assert f.sim.last_record['normal_rate_hz']==0
    np.testing.assert_array_equal(f.sim.motor.force_body,[0,0,0])
    assert f.pos[1]<.1
    g=make(replace(config,lesion='SGU'))
    g.step(.5,Room())
    assert g.sim.last_record['sgu_left_hz']==g.sim.last_record['sgu_right_hz']==0


def test_reset_recording_and_provenance(config):
    env=EpisodeRecorder(FlyChaseEnv(EnvConfig(fly_model='neural',neural=config,
                                             max_seconds=.2,capture_enabled=False,
                                             stimulus=StimulusConfig(enabled=False))))
    def episode():
        env.reset(seed=303)
        while True:
            _,_,done,truncated,_=env.step([.1,-.2])
            if done or truncated: return env.last_episode
    a,b=episode(),episode()
    assert a['frames']==b['frames']
    p=a['meta']['neural']
    assert p['backend']=='local_flysim_neuromechanical'
    assert p['neuromechanics']['network']['neurons']>273
    assert p['biological_validation']['status']=='not_calibrated'
    assert 'raw_connectivity' in p['sha256']
    assert a['frames']['neuralDiagnostics'][-1]['wing']['wing_force_body'] is not None
    assert a['frames']['neuralDiagnostics'][-1]['speed_command_mps'] is None


def test_missing_raw_data_has_explicit_error(config,tmp_path):
    backend=load_backend(config); backend.root=tmp_path
    with pytest.raises(ValueError,match='로컬 원자료'):
        expand_flight_network(backend)


def test_added_graph_preserves_measured_base_and_exact_cell_types(config):
    b=load_backend(config)
    old={(b.circuit.ids[a],b.circuit.ids[c]):w for a,c,w in zip(b.circuit.pre,b.circuit.post,b.circuit.signed_counts)}
    b=expand_flight_network(b)
    new={(b.circuit.ids[a],b.circuit.ids[c]):w for a,c,w in zip(b.circuit.pre,b.circuit.post,b.circuit.signed_counts)}
    assert all(new[k]==v for k,v in old.items())
    assert len(b.flight_inputs['LC4'])==104
    assert all(b.circuit.nodes[i]['cell_type']=='LC4' for i in b.flight_inputs['LC4'])
    assert b.flight_network['neurons']==547


def test_cli_selects_new_dynamics_without_changing_rule_default():
    import argparse
    from scripts._common import add_env_args,config_from_args
    parser=argparse.ArgumentParser(); add_env_args(parser)
    assert config_from_args(parser.parse_args([])).fly_model=='rule'
    assert config_from_args(parser.parse_args(['--fly-model','neural'])).neural.dynamics=='neuromechanical'


def test_alignment_can_end_in_capture_without_detected_threat(config):
    env=FlyChaseEnv(EnvConfig(fly_model='neural',neural=config,max_seconds=.3))
    env.reset(seed=301)
    env.fly.reset([0,1.5,-1.5],[0,0,-1])
    d=env.fly.pos-env.aimer.pos; d/=np.linalg.norm(d)
    env.aimer.reset(env.aimer.pos,math.atan2(-d[0],-d[2]),math.asin(d[1]))
    peak=0.
    while env.t<.3:
        _,_,terminated,truncated,_=env.step([0,0])
        diag=env.fly.diagnostics(); peak=max(peak,diag['left_input_hz'],diag['right_input_hz'])
        if terminated or truncated: break
    assert env._stimulus.events[0]['onset_ms']==120
    assert env.captured and env.t==pytest.approx(.2)
    assert peak==0 and not env.fly.phase_events


def test_stimulus_comparison_requires_matching_lesion_seed_and_time():
    from scripts.validate_neuromechanics import compare
    def row(lesion='none',seed=1,time=1005):
        return dict(seed=seed,lesion=lesion,trace=[dict(time_ms=time,heading=[1,0,0],position=[0,0,0])])
    for wrong in (row(lesion='DNp06'),row(seed=2),row(time=1010)):
        with pytest.raises(ValueError): compare(row(),wrong)
    a=row('DNp06'); compare(a,row('DNp06'))
    assert not a['kinematic_response_over_15deg']
    a=row('DNg02'); compare(a,row(),stimulus_comparison=False)
    assert 'kinematic_response_over_15deg' not in a


def test_control_uses_its_own_unstimulated_circuit(monkeypatch):
    from scripts import validate_neuromechanics as v
    calls=[]
    def fake(config,seed,stimulus):
        calls.append((config.lesion,seed,stimulus))
        return dict(seed=seed,lesion=config.lesion,trace=[dict(time_ms=1005,heading=[1,0,0],position=[0,0,0])])
    monkeypatch.setattr(v,'response',fake)
    config=NeuralConfig(dynamics='neuromechanical',lesion='escape')
    r=v.control_response(config,501,None)
    assert calls==[('escape',501,True),('escape',501,False)]
    assert r['paired_no_stimulus']['lesion']=='escape' and not r['kinematic_response_over_15deg']


def test_retired_motor_classes_are_not_instantiated_or_executed(config, monkeypatch):
    b = load_backend(config)
    def forbidden(*args, **kwargs):
        raise AssertionError("이전 운동 모델을 실행하면 안 됩니다.")
    monkeypatch.setattr(b.behavior, "FlightSimulation", forbidden)
    monkeypatch.setattr(b.behavior, "MotorDecoder", forbidden)
    # 다른 자료 해시로 캐시를 분리해 기준 발화 보정도 이전 모델 없이 수행한다.
    from flytracker import neuromechanics as mechanics
    with mechanics._RATE_LOCK:
        mechanics._RATE_CACHE.clear()
    f = make(config)
    f.step(.05, Room())
    assert not hasattr(f.sim.motor, "base") and not hasattr(f.sim.motor, "spontaneous")
    assert np.isfinite(f.pos).all()


@pytest.mark.parametrize("lesion", ["none", "DNp06", "escape", "disconnected"])
def test_real_looming_response_is_compared_to_its_own_circuit(config, lesion):
    from scripts.validate_neuromechanics import response, compare
    cfg = replace(config, lesion=lesion)
    control = response(cfg, 801, stimulus=False)
    row = response(cfg, 801)
    compare(row, control)
    assert row["first_sensory_sample_ms"] is not None
    escape = any(e["phase"] == "escape" for e in row["phase_events"])
    if lesion in ("none", "DNp06"):
        assert escape and row["kinematic_response_over_15deg"]
    else:
        assert not escape
    if lesion == "disconnected":
        assert not row["kinematic_response_over_15deg"]
