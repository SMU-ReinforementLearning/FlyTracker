"""축약 날개/신체 동역학. 실제 뇌 연결과 기능적 근육 피드백 근사를 구분한다.

고정 속도 명령, 방향 난수, 자세 덮어쓰기, 자동 중력 보상을 사용하지 않는다.
하위 근육/공력 계수는 연결 자료에서 복원한 값이 아닌 명시적 모델 가정이다.
"""
from dataclasses import asdict, dataclass, replace
import math
from threading import RLock

import numpy as np


@dataclass(frozen=True)
class MechanicsParameters:
    mass_kg: float = 1e-6
    gravity: float = 9.81
    body_length_m: float = .003
    body_radius_m: float = .0005
    wing_length_m: float = .002
    total_wing_area_m2: float = 4e-6
    air_density: float = 1.225
    wingbeat_hz: float = 200.
    fct_roll_nms: float = 18.33e-12
    fct_pitch_nms: float = 6.42e-12
    fct_yaw_nms: float = 26.84e-12
    fct_reference_hz: float = 212.
    fct_reference_half_stroke_rad: float = math.radians(70.)
    lift_coefficient: float = 1.5
    drag_coefficient: float = .7
    max_stroke_amplitude_rad: float = math.pi/2  # 반진폭, 전진폭 상한 180도
    escape_rotation_gain_rad: float = .06
    escape_roll_gain_rad: float = .004
    escape_reference_hz: float = 200.
    steering_recruitment_hz: float = 40.
    saccade_reference_hz: float = 100.
    saccade_rotation_gain_rad: float = .06
    stroke_plane_forward_rad: float = math.radians(10.)
    background_drive_hz: float = 1.
    ves_motion_gain_hz_s: float = 5.
    wall_expansion_on_s: float = .5
    wall_expansion_full_s: float = 2.
    reflex_frequency_rad_s: float = 35.
    reflex_damping: float = 1.
    yaw_reflex_time_s: float = .15
    muscle_tau_s: float = .005
    pitch_lever_m: float = .0003
    max_wing_rotation_rad: float = .25
    speed_warning_mps: float = 1.5
    angular_warning_rad_s: float = 300.

    def __post_init__(self):
        if any(not math.isfinite(v) or v <= 0 for v in asdict(self).values()):
            raise ValueError('생체역학 매개변수는 양의 유한값이어야 합니다.')
        if self.wall_expansion_full_s <= self.wall_expansion_on_s:
            raise ValueError('벽 확장의 최대 구동 기준은 시작 기준보다 커야 합니다.')

    @property
    def wing_arm(self): return .7*self.wing_length_m

    @property
    def lift_scale(self):
        # 준정상 근사: 1/2 rho S Cl <u²>, 정현 날갯짓의 <u²>=Ω² A² r²/2.
        return .25*self.air_density*self.total_wing_area_m2*self.lift_coefficient*(2*math.pi*self.wingbeat_hz*self.wing_arm)**2

    @property
    def trim_amplitude(self): return math.sqrt(self.mass_kg*self.gravity/self.lift_scale)

    @property
    def inertia(self):
        # 질량/기하가 주어진 균일 타원체의 관성 근사. 실측 관성으로 주장하지 않는다.
        a, b = self.body_length_m/2, self.body_radius_m
        return self.mass_kg/5*np.array([2*b*b, a*a+b*b, a*a+b*b])

    def rotational_damping(self,drag,stroke_direction=None):
        # Cheng 등(2010) 표 2의 A 패턴, 스트로크 면 좌표에서 N·m·s 단위다.
        # 주파수의 선형 스케일링은 논문 근거, 진폭 선형 스케일링은 축약 근사다.
        amplitude=drag/(self.air_density*self.total_wing_area_m2*self.drag_coefficient*4*self.wingbeat_hz*self.wing_arm)
        scale=(self.wingbeat_hz/self.fct_reference_hz)*(amplitude/self.fct_reference_half_stroke_rad)
        direction=np.array(stroke_direction if stroke_direction is not None else
                           [math.sin(self.stroke_plane_forward_rad),0.,math.cos(self.stroke_plane_forward_rad)])
        direction=direction/np.linalg.norm(direction)
        x=np.cross([0.,1.,0.],direction)
        if np.linalg.norm(x)<1e-8: x=np.cross([1.,0.,0.],direction)
        x/=np.linalg.norm(x)
        rotation=np.column_stack((x,np.cross(direction,x),direction))
        return scale*rotation@np.diag([self.fct_roll_nms,self.fct_pitch_nms,self.fct_yaw_nms])@rotation.T


@dataclass(frozen=True)
class SensoryParameters:
    """원본 감각 인코더와 발화 필터에 필요한 결합값만 유지한다."""
    flow_reference_s: float = .25
    flow_height_floor_m: float = .2
    normal_baseline_hz: float = 150.
    normal_flow_gain: float = 200.
    max_input_hz: float = 250.
    escape_input_hz: float = 180.
    rate_tau_s: float = .05


_RATE_CACHE = {}
_RATE_LOCK = RLock()


def trim_rate(backend):
    """고정 시드 무손상 회로의 기준 활성. 생체 Hz→날개 진폭 실측값은 아니다."""
    key = tuple(sorted(backend.hashes.items()))
    with _RATE_LOCK:
        if key not in _RATE_CACHE:
            encoder = backend.behavior.SensoryEncoder(backend.circuit, SensoryParameters())
            neural = backend.behavior.NeuralState(backend.circuit, encoder.inputs, seed=314159)
            normal = backend.circuit.group("DNg02")
            rates = np.zeros(len(backend.circuit.ids))
            rates[encoder.normal] = encoder.p.normal_baseline_hz
            total = 0.
            for tick in range(400):
                counts = neural.advance(rates, 5.)
                if tick >= 200:
                    total += float(np.mean(counts[normal]))
            if total <= 0:
                raise ValueError('무손상 회로에서 기준 DNg02 활성을 얻지 못했습니다.')
            _RATE_CACHE[key] = total  # 마지막 1초의 평균 발화 수 = Hz.
        return _RATE_CACHE[key]


def array(v): return np.array([v.x, v.y, v.z], dtype=float)


class WingMotor:
    """실제 발화→날개 운동, 감각 지연→기능적 근육 반사. 뇌 연결은 바꾸지 않는다."""
    def __init__(self, backend, physics, reference_rate, rate_tau_s):
        self.b, self.p, self.reference_rate = backend, physics, reference_rate
        self.rate_tau_s = rate_tau_s
        self.filtered = np.zeros(len(backend.circuit.ids))
        self.normal = backend.circuit.group("DNg02")
        self.escape = {side: [i for i, n in enumerate(backend.circuit.nodes)
                              if n["cell_type"] == "DNp06" and n["side"] == side]
                       for side in ("left", "right")}
        if not self.normal or not all(self.escape.values()):
            raise ValueError("필수 운동 출력 세포가 없습니다.")
        self.phase = 'normal'
        self.phase_age_s = self.above_threshold_s = self.quiet_s = 0.
        self.force_body = np.zeros(3)
        self.torque_body = np.zeros(3)
        self.drag = 0.
        self.saturated = False
        self.reflex_activation = np.zeros(3)
        self.reference_up = np.array([0.,0.,1.])
        self.delayed_sense = (np.zeros(3), np.zeros(3), self.reference_up.copy())
        self.sensed_rotation = (1.,0.,0.,0.)
        self.previous_angular = np.zeros(3)
        self.trim_force_direction = np.array([0., 0., 1.])
        self.groups = {kind: {s:[i for i,n in enumerate(backend.circuit.nodes)
                                if n['cell_type'] in names and n['side']==s]
                              for s in ('left','right')}
                       for kind,names in (('sgu',('DNa15','DNb01')),('dnp03',('DNp03',)),('ves',('VES041',)))}

    def sense(self, body, dt_s):
        # 평형곤의 각속도 신호를 이상적으로 근사한다. 실제 자세나 세계 수평을 읽지 않는다.
        omega=array(body.angular_rate)
        middle=(omega+self.previous_angular)/2
        magnitude=float(np.linalg.norm(middle))
        if magnitude:
            angle=magnitude*dt_s
            delta=(math.cos(angle/2),*(middle*(math.sin(angle/2)/magnitude)))
            q=np.array(self.b.physics.qmultiply(self.sensed_rotation,delta))
            self.sensed_rotation=tuple(q/np.linalg.norm(q))
        self.previous_angular=omega
        relative_up=array(self.b.behavior.rotate(self.sensed_rotation,self.b.core.Vec3(*self.reference_up),inverse=True))
        return np.cross(relative_up,self.reference_up),omega,relative_up

    def decode(self, counts, dt_s, body):
        # 원본과 같은 지수 발화 필터만 사용한다. 이전 운동 해독기는 실행하지 않는다.
        alpha = -math.expm1(-dt_s / self.rate_tau_s)
        self.filtered += alpha * (np.asarray(counts) / dt_s - self.filtered)
        p, b = self.p, self.b
        normal = float(np.mean(self.filtered[self.normal]))
        left, right = (float(np.mean(self.filtered[self.escape[side]])) for side in ("left", "right"))
        raw = dict(normal_rate_hz=normal, dnp06_left_hz=left, dnp06_right_hz=right)
        group_rates = {kind:{s:float(np.mean(self.filtered[ix])) if ix else 0.
                            for s,ix in groups.items()} for kind,groups in self.groups.items()}
        p03 = group_rates['dnp03']
        strength = max(left, right, *p03.values())
        self.above_threshold_s = self.above_threshold_s+dt_s if strength >= 40 else 0.
        self.quiet_s = self.quiet_s+dt_s if strength <= 5 else 0.
        previous = self.phase
        self.phase_age_s += dt_s
        if self.above_threshold_s >= .015:
            self.phase = 'escape'
        elif self.phase == 'escape' and self.quiet_s >= .1:
            self.phase = 'recovery'
        elif self.phase == 'recovery' and self.phase_age_s >= .5:
            self.phase = 'normal'
        if previous != self.phase: self.phase_age_s = 0.

        amplitude = min(p.max_stroke_amplitude_rad,
                        p.trim_amplitude*math.sqrt(max(normal,0)/self.reference_rate))
        power = amplitude**2/p.trim_amplitude**2
        sense = self.sense(body,dt_s)
        error, omega, up = self.delayed_sense
        self.delayed_sense = sense  # 한 신체 구간(5ms)의 감각 지연. 과거 구간을 수정하지 않는다.
        yaw_rate=up*float(np.dot(omega,up))
        desired = -p.inertia*(p.reflex_frequency_rad_s**2*error
                             +2*p.reflex_damping*p.reflex_frequency_rad_s*(omega-yaw_rate)
                             +yaw_rate/p.yaw_reflex_time_s)
        self.reflex_activation += (-math.expm1(-dt_s/p.muscle_tau_s))*(desired-self.reflex_activation)
        reflex = self.reflex_activation*min(power,1.)

        # 발화 문턱은 모델 가정이다. 평시의 약한 비대칭을 지속 회전으로 해독하지 않는다.
        recruit = lambda x: max(x-p.steering_recruitment_hz,0.)
        escape = (recruit(left)-recruit(right)+recruit(p03['left'])-recruit(p03['right']))/p.escape_reference_hz
        # DNa15/DNb01의 동측 선회와 DNp03의 반대측 선회를 구분한다.
        sgu = group_rates['sgu']
        saccade = (sgu['right']-sgu['left'])/p.saccade_reference_hz
        roll_bias = p.escape_roll_gain_rad*(escape+saccade)
        raw_l = p.lift_scale*.5*(max(amplitude*(1+roll_bias),0)**2) + reflex[0]/(2*p.wing_arm)
        raw_r = p.lift_scale*.5*(max(amplitude*(1-roll_bias),0)**2) - reflex[0]/(2*p.wing_arm)
        max_lift = p.lift_scale*.5*p.max_stroke_amplitude_rad**2
        lift_l, lift_r = np.clip([raw_l,raw_r],0,max_lift)
        total = lift_l+lift_r

        # 날개 회전의 좌우 차이가 전후 힘의 차이와 yaw 토크를 만든다.
        rotation = (p.escape_rotation_gain_rad*escape
                    +p.saccade_rotation_gain_rad*saccade)
        forward_l = lift_l*math.sin(rotation)-reflex[2]/(2*p.wing_arm)
        forward_r = -lift_r*math.sin(rotation)+reflex[2]/(2*p.wing_arm)
        limits = np.array([lift_l,lift_r])*math.sin(p.max_wing_rotation_rad)
        forward = np.clip([forward_l,forward_r],-limits,limits)
        raw_cp=-reflex[1]/max(total,1e-15)
        cp_x = float(np.clip(raw_cp,-p.pitch_lever_m,p.pitch_lever_m))
        self.force_body = total*self.trim_force_direction + np.array([forward.sum(),0.,0.])
        self.torque_body = np.array([p.wing_arm*(lift_l-lift_r)*self.trim_force_direction[2],
                                     -cp_x*total*self.trim_force_direction[2],
                                     p.wing_arm*((lift_r-lift_l)*self.trim_force_direction[0]+forward[1]-forward[0])])
        tip_speed = 4*p.wingbeat_hz*amplitude*p.wing_arm
        self.drag = p.air_density*p.total_wing_area_m2*p.drag_coefficient*tip_speed
        self.saturated = bool(np.any(np.array([raw_l,raw_r]) < 0) or np.any(np.array([raw_l,raw_r]) > max_lift)
                              or np.any(np.abs([forward_l,forward_r])>limits) or abs(raw_cp)>p.pitch_lever_m)
        raw.update(phase=self.phase,
                   stroke_amplitude_rad=amplitude, wing_lift_left_n=float(lift_l), wing_lift_right_n=float(lift_r),
                   wing_force_body=self.force_body.tolist(), wing_torque_body=self.torque_body.tolist(),
                   muscle_reflex_torque=self.reflex_activation.tolist(), normal_reference_hz=self.reference_rate,
                   dnp03_left_hz=p03['left'],dnp03_right_hz=p03['right'],
                   sgu_left_hz=sgu['left'],sgu_right_hz=sgu['right'],
                   ves_left_hz=group_rates['ves']['left'],ves_right_hz=group_rates['ves']['right'])
        return raw


def integrate(body, force_body, torque_body, drag, dt, b, p, stroke_direction=None):
    """자세에 따라 날개 힘을 회전시키며 병진과 각운동을 함께 적분한다."""
    position, velocity = array(body.position), array(body.velocity)
    omega, q = array(body.angular_rate), np.array(body.quaternion)
    inertia = p.inertia
    rot_drag = p.rotational_damping(drag,stroke_direction)
    h = dt/5  # 신체 구간 5ms 안에서 1ms씩 적분한다. 감각/운동 명령은 유지한다.
    for _ in range(5):
        torque = torque_body - np.cross(omega,inertia*omega) - rot_drag@omega
        alpha = torque/inertia
        middle_omega = omega+alpha*h/2
        middle_alpha = (torque_body-np.cross(middle_omega,inertia*middle_omega)-rot_drag@middle_omega)/inertia
        angle = float(np.linalg.norm(middle_omega))*h
        if angle:
            delta = np.r_[math.cos(angle/2),middle_omega*(math.sin(angle/2)/np.linalg.norm(middle_omega))]
            q_mid = b.physics.qmultiply(q, np.r_[math.cos(angle/4),middle_omega*(math.sin(angle/4)/np.linalg.norm(middle_omega))])
            q_new = np.array(b.physics.qmultiply(q,delta))
            q_new /= np.linalg.norm(q_new)
        else: q_mid, q_new = q, q
        world_force = array(b.behavior.rotate(q_mid,b.core.Vec3(*force_body)))
        acceleration = world_force/p.mass_kg - np.array([0.,0.,p.gravity]) - (drag/p.mass_kg)*velocity
        midpoint_velocity = velocity+acceleration*h/2
        acceleration = world_force/p.mass_kg - np.array([0.,0.,p.gravity]) - (drag/p.mass_kg)*midpoint_velocity
        position += midpoint_velocity*h
        velocity += acceleration*h
        omega += middle_alpha*h
        q = q_new
        if not np.isfinite(np.r_[position,velocity,omega,q]).all() or np.linalg.norm(omega) > 2000:
            raise FloatingPointError('날개/신체 적분이 불안정합니다. 값을 잘라 정상 동작으로 처리하지 않습니다.')
    return b.physics.BodyState(b.core.Vec3(*position),b.core.Vec3(*velocity),tuple(q),b.core.Vec3(*omega))


class NeuromechanicalSimulation:
    dt_s = .005
    force_based = True

    def __init__(self, b, seed=0, silenced=(), disconnected=False, physics=None):
        self.b = b
        self.circuit = b.circuit
        self.params = SensoryParameters()
        self.encoder = b.behavior.SensoryEncoder(b.circuit, self.params)
        self.body = b.physics.BodyState()
        self.clock = b.behavior.Clock()
        self.disc = None
        self.total_spikes = np.zeros(len(b.circuit.ids), dtype=np.int64)
        self.last_record = None
        self.physics = physics or MechanicsParameters()
        self.inputs = b.flight_inputs
        self.visual_sides = {name:{side:[i for i in self.inputs[name] if self.circuit.nodes[i]['side']==side]
                                   for side in ('left','right')} for name in ('LC4','LPLC1')}
        input_indices = sorted(set(self.encoder.inputs).union(*(set(x) for x in self.inputs.values())))
        self.neural = b.behavior.NeuralState(b.circuit,input_indices,seed=seed,
                                         silenced=silenced,disconnected=disconnected)
        self.motor = WingMotor(b, self.physics, trim_rate(b), self.params.rate_tau_s)
        self.bounds = None

    def initialize(self, body):
        self.body = body
        p, b = self.physics,self.b
        # reset의 비행 트림 기준만 설정한다. 속도 목표를 역산하거나 이후 자세를 읽어 복원하지 않는다.
        up=b.core.Vec3(0,0,1)
        self.motor.reference_up=array(b.behavior.rotate(body.quaternion,up,inverse=True))
        self.motor.delayed_sense=(np.zeros(3),np.zeros(3),self.motor.reference_up.copy())
        forward=array(b.behavior.rotate(body.quaternion,b.core.Vec3(1,0,0)))
        horizontal=np.r_[forward[:2],0.]
        if np.linalg.norm(horizontal)<1e-8: horizontal=np.array([1.,0.,0.])
        horizontal/=np.linalg.norm(horizontal)
        direction=math.cos(p.stroke_plane_forward_rad)*array(up)+math.sin(p.stroke_plane_forward_rad)*horizontal
        self.motor.trim_force_direction=array(b.behavior.rotate(body.quaternion,b.core.Vec3(*direction),inverse=True))

    def step(self):
        b,p = self.b,self.physics
        rates,sensory = self.encoder.encode(self.body,self.clock.time_s,self.disc)
        height = max(abs(self.body.position.z),self.params.flow_height_floor_m)
        # 수직 망막 흐름/접근에 대한 입력 근사. 고도 목표나 신체 복원력은 없다.
        vertical_flow = self.body.velocity.z/height
        if self.bounds is not None:
            top = max(self.bounds[1][2]-self.body.position.z,.02)
            bottom = max(self.body.position.z-self.bounds[0][2],.02)
            vertical_flow += max(self.body.velocity.z,0.)/top - max(-self.body.velocity.z,0.)/bottom
        normal_drive = np.clip(self.params.normal_baseline_hz - self.params.normal_flow_gain*vertical_flow,
                               0,self.params.max_input_hz)
        rates[self.encoder.normal] = normal_drive
        # 부분 회로 바깥의 활동 및 감각 경계 근사. 실제 연결 행렬은 변경하지 않는다.
        rates[list(self.inputs['background'])] = p.background_drive_hz
        for name in ('LC4','LPLC1'):
            for side in ('left','right'):
                indices = self.visual_sides[name][side]
                rates[indices] = self.params.escape_input_hz*sensory[side]
        rates[list(self.inputs['VES041'])] = min(250.,p.ves_motion_gain_hz_s*abs(self.body.angular_rate.z))
        sensory['normal_drive_hz'] = float(normal_drive)
        sensory['vertical_flow_s'] = self.body.velocity.z/height
        sensory['wall_left_input_hz'] = sensory['wall_right_input_hz'] = 0.
        if self.bounds is not None:
            position, velocity = array(self.body.position),array(self.body.velocity)
            for axis in (0,1):
                for side in (0,1):
                    distance = max(abs(self.bounds[side][axis]-position[axis]),.01)
                    approach = velocity[axis]*(1 if side else -1)
                    strength = np.clip((approach/distance-p.wall_expansion_on_s)/
                                       (p.wall_expansion_full_s-p.wall_expansion_on_s),0,1)
                    direction = np.zeros(3); direction[axis] = 1 if side else -1
                    local = array(b.behavior.rotate(self.body.quaternion,b.core.Vec3(*direction),inverse=True))
                    bearing = math.atan2(local[1],local[0])
                    if abs(bearing) > math.radians(150): continue
                    lateral = math.tanh(bearing/.4)
                    for name,weight in (('left',(1+lateral)/2),('right',(1-lateral)/2)):
                        drive = self.params.escape_input_hz*strength*weight
                        idx = self.encoder.lplc[name]
                        rates[idx] = np.maximum(rates[idx],drive)
                        sensory[f'wall_{name}_input_hz'] = max(sensory[f'wall_{name}_input_hz'],float(drive))
        old_velocity = array(self.body.velocity)
        applied_saturation = self.motor.saturated
        self.body = integrate(self.body,self.motor.force_body,self.motor.torque_body,self.motor.drag,self.dt_s,b,p,
                              self.motor.trim_force_direction)
        counts = self.neural.advance(rates,5.)
        self.total_spikes += counts
        for _ in range(5): self.clock.advance()
        motor = self.motor.decode(counts,self.dt_s,self.body)
        if not math.isclose(self.neural.tick*self.neural.params.dt_ms/1000,self.clock.time_s,abs_tol=1e-10):
            raise RuntimeError('신경 시계와 신체 시계가 일치하지 않습니다.')
        self.last_record = dict(time_s=self.clock.time_s,sensory_time_s=self.clock.time_s-self.dt_s,
                                speed_mps=float(np.linalg.norm(array(self.body.velocity))),
                                force_saturated=int(applied_saturation),speed_warning=int(np.linalg.norm(array(self.body.velocity))>p.speed_warning_mps),
                                physical_acceleration=((array(self.body.velocity)-old_velocity)/self.dt_s).tolist(),
                                **sensory,**motor)
        return self.last_record
