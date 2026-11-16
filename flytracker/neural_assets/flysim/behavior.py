"""Stage 4: abstract sensory encoders, real graph, explicit motor adapters.

No RGB vision, gaze-contingent trigger, learning, walls, or muscle simulation.
An external panoramic-flow assay and a growing disc define controlled inputs.
"""
from dataclasses import dataclass, asdict
import math
import numpy as np
from .core import Vec3, Clock
from .physics import (BodyState, PhysicsParameters, ZERO, add, scale, norm,
                      qmultiply, acceleration_to_force, step as body_step)
from .neural_state import NeuralState


def rotate(q, vector, inverse=False):
    """Map body->world (or inverse) without changing the vector magnitude."""
    qc = (q[0], -q[1], -q[2], -q[3])
    a, b = (qc, q) if inverse else (q, qc)
    result = qmultiply(qmultiply(a, (0., vector.x, vector.y, vector.z)), b)
    return Vec3(*result[1:])


def clip(x, low, high):
    return max(low, min(high, x))


@dataclass(frozen=True)
class LoomingDisc:
    center: Vec3 = Vec3(.4, .35, 1.)
    onset_s: float = 1.
    duration_s: float = .25
    min_radius_m: float = .01
    max_radius_m: float = .12
    contrast: float = 1.

    def __post_init__(self):
        vals = (self.onset_s, self.duration_s, self.min_radius_m, self.max_radius_m, self.contrast)
        if not all(math.isfinite(x) for x in vals):
            raise ValueError('Nonfinite stimulus')
        if self.onset_s < 0 or self.duration_s <= 0 or not 0 < self.min_radius_m < self.max_radius_m or not 0 <= self.contrast <= 1:
            raise ValueError('Invalid disc parameters')

    def sample(self, time_s, body):
        """Analytic angular size/rate including translation; lateral weights are approximations."""
        u = (time_s - self.onset_s) / self.duration_s
        if not 0 <= u < 1:
            return dict(theta_rad=0., expansion_rad_s=0., left=0., right=0., bearing_rad=0.)
        delta = self.center - body.position
        distance = norm(delta)
        if distance <= 1e-6:
            raise ValueError('Body overlaps the visual stimulus center')
        radius = self.min_radius_m + (self.max_radius_m - self.min_radius_m) * (1-math.cos(math.pi*u))/2
        growth = (self.max_radius_m - self.min_radius_m)*math.pi*math.sin(math.pi*u)/(2*self.duration_s)
        distance_rate = -delta.dot(body.velocity)/distance
        expansion = max(0., 2*(growth*distance-radius*distance_rate)/(distance**2+radius**2))
        local = rotate(body.quaternion, delta, inverse=True)
        bearing = math.atan2(local.y, local.x)
        # Coarse hemispheres, not measured per-column LPLC2 receptive fields.
        visibility = max(0., 1-abs(math.atan2(local.z, math.hypot(local.x, local.y)))/(math.pi/2))
        if abs(bearing) > math.radians(150):
            visibility = 0.
        strength = self.contrast*visibility*clip(expansion/2., 0., 1.)
        lateral = math.tanh(bearing/.4)
        return dict(theta_rad=2*math.atan2(radius, distance), expansion_rad_s=expansion,
                    left=strength*(1+lateral)/2, right=strength*(1-lateral)/2, bearing_rad=bearing)


@dataclass(frozen=True)
class CouplingParameters:
    flow_reference_s: float = .25
    flow_height_floor_m: float = .2
    normal_baseline_hz: float = 150.
    normal_flow_gain: float = 200.
    max_input_hz: float = 250.
    escape_input_hz: float = 180.
    rate_tau_s: float = .05
    base_speed_mps: float = .14
    normal_speed_gain: float = .018
    escape_speed_gain: float = .0003
    max_speed_command_mps: float = .45
    velocity_tau_s: float = .18
    escape_yaw_gain: float = .025
    escape_on_hz: float = 40.
    escape_trigger_dwell_s: float = .015
    escape_off_hz: float = 5.
    escape_max_s: float = .25
    recovery_s: float = .5
    spontaneous_yaw_sd: float = .18
    spontaneous_pitch_sd: float = .035
    spontaneous_tau_s: float = .8

    def __post_init__(self):
        if not all(math.isfinite(v) and v >= 0 for v in asdict(self).values()):
            raise ValueError('Coupling parameters must be finite and nonnegative')
        for key in ('flow_height_floor_m','rate_tau_s','velocity_tau_s','escape_max_s','escape_trigger_dwell_s','recovery_s','spontaneous_tau_s','max_speed_command_mps'):
            if getattr(self, key) <= 0:
                raise ValueError('Invalid positive time/scale')
        if self.escape_off_hz >= self.escape_on_hz or self.max_input_hz > 1000 or self.escape_input_hz > 1000:
            raise ValueError('Invalid thresholds/rates')


class SensoryEncoder:
    def __init__(self, circuit, params):
        self.circuit, self.p = circuit, params
        self.normal = [i for i, r in enumerate(circuit.nodes) if r['selection'] == 'top3_input_to_DNg02']
        self.lplc = {side: [i for i, r in enumerate(circuit.nodes) if r['cell_type'] == 'LPLC2' and r['side'] == side]
                     for side in ('left','right')}
        if not self.normal or not all(self.lplc.values()):
            raise ValueError('Missing annotated input groups')
        self.inputs = sorted(set(self.normal + self.lplc['left'] + self.lplc['right']))

    def encode(self, body, time_s, disc=None, flow_bias_s=0., normal_enabled=True):
        if not math.isfinite(flow_bias_s):
            raise ValueError('Nonfinite flow bias')
        p = self.p
        forward = rotate(body.quaternion, Vec3(1,0,0))
        # Geometric proxy for ventral optic flow over an implicit textured plane.
        # The floor is not a collision surface. RGB/retinal motion detectors are absent.
        flow = body.velocity.dot(forward)/max(abs(body.position.z), p.flow_height_floor_m) + flow_bias_s
        drive = clip(p.normal_baseline_hz+p.normal_flow_gain*(p.flow_reference_s-flow), 0., p.max_input_hz) if normal_enabled else 0.
        rates = np.zeros(len(self.circuit.ids))
        rates[self.normal] = drive
        sensory = (disc.sample(time_s, body) if disc else
                   dict(theta_rad=0., expansion_rad_s=0., left=0., right=0., bearing_rad=0.))
        for side in ('left','right'):
            rates[self.lplc[side]] = p.escape_input_hz*sensory[side]
        return rates, dict(sensory, flow_s=flow, normal_drive_hz=drive,
                           left_input_hz=p.escape_input_hz*sensory['left'], right_input_hz=p.escape_input_hz*sensory['right'])


class MotorDecoder:
    def __init__(self, circuit, params, seed=0):
        self.p = params
        self.normal = circuit.group('DNg02')
        self.escape = {side:[i for i,r in enumerate(circuit.nodes) if r['cell_type']=='DNp06' and r['side']==side]
                       for side in ('left','right')}
        if not self.normal or not all(self.escape.values()):
            raise ValueError('Missing annotated motor groups')
        self.filtered = np.zeros(len(circuit.ids))
        self.phase = 'normal'
        self.phase_age_s = 0.
        self.above_threshold_s = 0.
        self.rng = np.random.default_rng(seed)
        self.spontaneous = np.zeros(2)

    def decode(self, counts, dt_s, body):
        p = self.p
        alpha = -math.expm1(-dt_s/p.rate_tau_s)
        self.filtered += alpha*(np.asarray(counts)/dt_s-self.filtered)
        normal = float(np.mean(self.filtered[self.normal]))
        left, right = (float(np.mean(self.filtered[self.escape[s]])) for s in ('left','right'))
        self.phase_age_s += dt_s
        strength = max(left, right)
        self.above_threshold_s = self.above_threshold_s + dt_s if strength >= p.escape_on_hz else 0.
        if self.phase == 'normal' and self.above_threshold_s >= p.escape_trigger_dwell_s:
            self.phase, self.phase_age_s = 'escape', 0.
        elif self.phase == 'escape' and (strength <= p.escape_off_hz or self.phase_age_s >= p.escape_max_s):
            self.phase, self.phase_age_s = 'recovery', 0.
        elif self.phase == 'recovery' and self.phase_age_s >= p.recovery_s and strength <= p.escape_off_hz:
            self.phase, self.phase_age_s = 'normal', 0.
        # Slowly varying spontaneous drive is an explicit body-control scaffold.
        decay = math.exp(-dt_s/p.spontaneous_tau_s)
        self.spontaneous = decay*self.spontaneous + math.sqrt(1-decay**2)*self.rng.normal(size=2)*np.array([p.spontaneous_yaw_sd,p.spontaneous_pitch_sd])
        fleeing = self.phase == 'escape'
        escape_yaw = clip(p.escape_yaw_gain*(right-left), -4., 4.) if fleeing else 0.
        speed = clip(p.base_speed_mps+p.normal_speed_gain*normal+(p.escape_speed_gain*(right+left) if fleeing else 0.), 0., p.max_speed_command_mps)
        forward = rotate(body.quaternion, Vec3(1,0,0))
        target_velocity = scale(forward, speed)
        acceleration = scale(target_velocity-body.velocity, 1/p.velocity_tau_s)
        # Mild pitch leveling is engineering stabilization, not a neural inference.
        angular = Vec3(0., float(self.spontaneous[1])+2.*forward.z, float(self.spontaneous[0])+escape_yaw)
        telemetry = dict(normal_rate_hz=normal, dnp06_left_hz=left, dnp06_right_hz=right,
                         speed_command_mps=speed, escape_yaw_rad_s=escape_yaw, phase=self.phase)
        return acceleration, angular, telemetry


class FlightSimulation:
    dt_s = .005

    def __init__(self, circuit, seed=0, disc=None, flow_bias_s=0., normal_enabled=True,
                 disconnected=False, silenced=(), coupling=None, physics=None):
        self.circuit = circuit
        self.params = coupling or CouplingParameters()
        self.physics = physics or PhysicsParameters()
        self.encoder = SensoryEncoder(circuit, self.params)
        self.neural = NeuralState(circuit, self.encoder.inputs, seed=seed, disconnected=disconnected, silenced=silenced)
        self.motor = MotorDecoder(circuit, self.params, seed=seed+100000)
        self.body = BodyState(velocity=Vec3(self.params.base_speed_mps,0,0))
        self.clock = Clock()
        self.disc, self.flow_bias_s, self.normal_enabled = disc, flow_bias_s, normal_enabled
        self.acceleration, self.angular = ZERO, ZERO
        self.total_spikes = np.zeros(len(circuit.ids), dtype=np.int64)
        self.last_record = None

    def step(self):
        # Sample at t; hold inputs/previous motor commands until t+dt.
        # Spikes over this interval affect the NEXT interval, never its past.
        rates, sensory = self.encoder.encode(self.body, self.clock.time_s, self.disc,
                                              self.flow_bias_s, self.normal_enabled)
        force = acceleration_to_force(self.body, self.acceleration, self.physics)
        result = body_step(self.body, force, self.dt_s, self.physics, angular_rate_command=self.angular)
        counts = self.neural.advance(rates, self.dt_s*1000)
        self.total_spikes += counts
        self.body = result.state
        for _ in range(5):
            self.clock.advance()
        self.acceleration, self.angular, motor = self.motor.decode(counts, self.dt_s, self.body)
        if not math.isclose(self.neural.tick*self.neural.params.dt_ms/1000, self.clock.time_s, abs_tol=1e-10):
            raise RuntimeError('Neural/physics clock mismatch')
        forward = rotate(self.body.quaternion, Vec3(1,0,0))
        self.last_record = dict(time_s=self.clock.time_s, sensory_time_s=self.clock.time_s-self.dt_s,
            x=self.body.position.x, y=self.body.position.y, z=self.body.position.z,
            vx=self.body.velocity.x, vy=self.body.velocity.y, vz=self.body.velocity.z,
            yaw_rad=math.atan2(forward.y,forward.x), speed_mps=norm(self.body.velocity),
            force_saturated=int(result.force_saturated), speed_warning=int(result.speed_warning),
            **sensory, **motor)
        return self.last_record
