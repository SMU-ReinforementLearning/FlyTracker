"""SI point-mass flight with independent kinematic attitude (stage 3)."""
from dataclasses import dataclass
import math
from .core import Vec3

ZERO=Vec3(0.,0.,0.)
def add(a,b): return Vec3(a.x+b.x,a.y+b.y,a.z+b.z)
def scale(a,s): return Vec3(a.x*s,a.y*s,a.z*s)
def norm(a): return math.hypot(a.x,a.y,a.z)
def limit(a,maximum):
    size=norm(a)
    return scale(a,maximum/size) if size>maximum else a

@dataclass(frozen=True)
class PhysicsParameters:
    mass_kg: float=1e-6
    gravity: float=9.81
    drag_per_mass: float=.2
    max_force_n: float=1.962e-5
    max_command_accel: float=3.
    speed_warning_mps: float=.8
    max_angular_rate: float=2*math.pi
    attitude_tau_s: float=.05
    def __post_init__(self):
        for name,value in vars(self).items():
            if not math.isfinite(value): raise ValueError('Nonfinite '+name)
            if value<0 or (name not in ('gravity','drag_per_mass') and value==0):
                raise ValueError('Invalid '+name)

@dataclass(frozen=True)
class BodyState:
    position: Vec3=Vec3(0,0,1)
    velocity: Vec3=ZERO
    quaternion: tuple=(1.,0.,0.,0.) # body->world, w,x,y,z
    angular_rate: Vec3=ZERO # body axes; rad/s, kinematic only
    def __post_init__(self):
        q=self.quaternion
        if len(q)!=4 or not all(math.isfinite(x) for x in q): raise ValueError('Invalid quaternion')
        if not math.isclose(sum(x*x for x in q),1.,abs_tol=1e-9): raise ValueError('Quaternion must be unit length')

@dataclass(frozen=True)
class StepResult:
    state: BodyState
    applied_force: Vec3
    acceleration: Vec3 # midpoint acceleration used by integrator
    force_saturated: bool
    speed_warning: bool

def qmultiply(a,b):
    w,x,y,z=a; v,i,j,k=b
    return (w*v-x*i-y*j-z*k,w*i+x*v+y*k-z*j,w*j-x*k+y*v+z*i,w*k+x*j-y*i+z*v)

def acceleration_to_force(state,command,params=None,wind=ZERO):
    """Engineering adapter: clamp commanded acceleration; compensate gravity/drag.
    Returns REQUESTED world force. step() applies the actual force limit.
    """
    p=params or PhysicsParameters(); a=limit(command,p.max_command_accel)
    relative=state.velocity-wind
    compensated=add(add(a,Vec3(0,0,p.gravity)),scale(relative,p.drag_per_mass*norm(relative)))
    return scale(compensated,p.mass_kg)

def step(state,requested_force,dt_s=.005,params=None,wind=ZERO,angular_rate_command=ZERO):
    """Midpoint RK2 translation; quaternion rotation, no wall/ground collisions.
    Force and wind are held fixed during the step. Attitude does not steer force.
    Large dt is rejected; a speed warning never silently clips velocity.
    """
    p=params or PhysicsParameters()
    if not math.isfinite(dt_s) or not 0<dt_s<=.02: raise ValueError('dt must be in (0, .02] s')
    force=limit(requested_force,p.max_force_n)
    def accel(velocity):
        rel=velocity-wind
        return add(scale(force,1/p.mass_kg),add(Vec3(0,0,-p.gravity),scale(rel,-p.drag_per_mass*norm(rel))))
    a0=accel(state.velocity)
    mid_velocity=add(state.velocity,scale(a0,dt_s/2))
    amid=accel(mid_velocity)
    velocity=add(state.velocity,scale(amid,dt_s))
    position=add(state.position,scale(mid_velocity,dt_s))
    target=limit(angular_rate_command,p.max_angular_rate)
    # Exact first-order rate filter and its integrated rotation vector over dt.
    decay=math.exp(-dt_s/p.attitude_tau_s)
    old=limit(state.angular_rate,p.max_angular_rate)
    rate=add(target,scale(old-target,decay))
    rot=add(scale(target,dt_s),scale(old-target,p.attitude_tau_s*(1-decay)))
    angle=norm(rot)
    if angle:
        axis=scale(rot,math.sin(angle/2)/angle)
        delta=(math.cos(angle/2),axis.x,axis.y,axis.z)
        q=qmultiply(state.quaternion,delta)
        length=math.sqrt(sum(x*x for x in q)); q=tuple(x/length for x in q)
    else: q=state.quaternion
    result=BodyState(position,velocity,q,rate)
    return StepResult(result,force,amid,norm(requested_force)>p.max_force_n,norm(velocity)>p.speed_warning_mps)
