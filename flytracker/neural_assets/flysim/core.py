"""SI world: +X forward, +Y left, +Z up. Angles in radians."""
from dataclasses import dataclass
from math import cos, sin, tan, pi, isfinite


@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.x, self.y, self.z)):
            raise ValueError('Vector components must be finite')

    def __sub__(self, other):
        return Vec3(self.x-other.x, self.y-other.y, self.z-other.z)

    def dot(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z


@dataclass(frozen=True)
class Projection:
    u: float | None
    v: float | None
    depth_m: float
    in_view: bool


@dataclass(frozen=True)
class Gaze:
    origin: Vec3 = Vec3(0, 0, 0)
    pan: float = 0.0
    tilt: float = 0.0
    width: int = 320
    height: int = 240
    horizontal_fov: float = pi/3
    near_m: float = 0.001

    def __post_init__(self):
        if not all(isfinite(v) for v in (self.pan, self.tilt, self.horizontal_fov, self.near_m)):
            raise ValueError('Gaze parameters must be finite')
        if not (0 < self.horizontal_fov < pi and self.near_m > 0):
            raise ValueError('Invalid FOV or near plane')
        if not (-pi/2 < self.tilt < pi/2):
            raise ValueError('Tilt must be strictly between -pi/2 and pi/2')
        if any(type(n) is not int or n <= 0 for n in (self.width, self.height)):
            raise ValueError('Image dimensions must be positive integers')

    def project(self, point: Vec3) -> Projection:
        # Camera axes: right, down, forward. Positive pan turns left.
        cp, sp, ct, st = cos(self.pan), sin(self.pan), cos(self.tilt), sin(self.tilt)
        forward = Vec3(ct*cp, ct*sp, st)
        right = Vec3(sp, -cp, 0)
        down = Vec3(st*cp, st*sp, -ct)
        delta = point - self.origin
        depth = delta.dot(forward)
        if depth <= self.near_m:
            return Projection(None, None, depth, False)
        focal = self.width / (2*tan(self.horizontal_fov/2))
        u = self.width/2 + focal*delta.dot(right)/depth
        v = self.height/2 + focal*delta.dot(down)/depth
        return Projection(u, v, depth, 0 <= u < self.width and 0 <= v < self.height)


@dataclass
class Clock:
    tick: int = 0
    quantum_s: float = 0.001

    def __post_init__(self):
        if type(self.tick) is not int or self.tick < 0:
            raise ValueError('tick must be a nonnegative integer')
        if not isfinite(self.quantum_s) or self.quantum_s <= 0:
            raise ValueError('quantum_s must be positive and finite')

    @property
    def time_s(self):
        return self.tick * self.quantum_s

    def advance(self):
        self.tick += 1

    def due(self, every_ticks: int):
        if type(every_ticks) is not int or every_ticks <= 0:
            raise ValueError('period must be positive integer ticks')
        return self.tick % every_ticks == 0
