"""Local-only adapter for neural wing/body dynamics.

No flysim code or biological data is vendored. Only explicitly selected local
Python files are executed; their rights are separate from this adapter's code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import math
import os
from pathlib import Path
import sys
from threading import RLock
from types import ModuleType, SimpleNamespace

import numpy as np

from .geometry import unit
from .world import Room
from .neuromechanics import NeuromechanicalSimulation
from .flight_network import expand_flight_network


# Proper rotation: source +X forward -> tracker -z, +Y left -> -x,
# +Z up -> +y. Internal body axes and physics remain source-native.
SOURCE_TO_TRACKER = np.array([[0., -1., 0.], [0., 0., 1.], [-1., 0., 0.]])
MAP_QUATERNION = (0.5, -0.5, 0.5, 0.5)  # w,x,y,z; source world -> tracker world
_MODULES = ("core", "neural", "neural_state", "physics", "behavior")
_LOAD_LOCK = RLock()


def to_tracker(vector) -> np.ndarray:
    return SOURCE_TO_TRACKER @ np.asarray(vector, dtype=float)


def to_source(vector) -> np.ndarray:
    return SOURCE_TO_TRACKER.T @ np.asarray(vector, dtype=float)


def _array(vector):
    return np.array([vector.x, vector.y, vector.z], dtype=float)


def heading_quaternion(source_heading) -> tuple:
    """Roll-free body->source-world rotation with body +X along heading."""
    d = unit(np.asarray(source_heading, dtype=float))
    if not np.isfinite(d).all() or np.linalg.norm(d) < 0.5:
        raise ValueError("Heading must be a finite nonzero vector")
    yaw = math.atan2(d[1], d[0])
    pitch = -math.atan2(d[2], math.hypot(d[0], d[1]))
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    return (cy * cp, -sy * sp, cy * sp, sy * cp)


@dataclass(frozen=True)
class NeuralConfig:
    source_root: str | None = None
    data_dir: str | None = None
    boundary_enabled: bool = True
    wall_margin: float = 0.02
    lesion: str = "none"
    dynamics: str = "neuromechanical"

    def __post_init__(self):
        if self.dynamics != "neuromechanical":
            raise ValueError("신경 비행은 neuromechanical 동역학만 지원합니다.")
        if self.lesion not in ("none", "LPLC2", "DNp06", "DNg02", "disconnected", "DNp03", "SGU", "escape"):
            raise ValueError("지원하지 않는 회로 억제 설정입니다.")
        if not math.isfinite(self.wall_margin) or self.wall_margin < 0:
            raise ValueError("wall_margin은 0 이상의 유한값이어야 합니다.")
        if type(self.boundary_enabled) is not bool:
            raise ValueError("boundary_enabled는 bool이어야 합니다.")

    @classmethod
    def from_dict(cls, values):
        # 현재 보존한 기록의 사용하지 않던 설정만 읽는다. 다른 운동 모델은 허용하지 않는다.
        values = dict(values)
        legacy_fields = {"motion_profile", "wall_lookahead", "wall_accel", "wall_turn_rate"}
        if legacy_fields.intersection(values) and values.get("dynamics") != "neuromechanical":
            raise ValueError("이전 운동 모델 설정을 현재 모델로 자동 변환하지 않습니다.")
        for key, expected in (("motion_profile", "basic"), ("wall_lookahead", .25),
                              ("wall_accel", 1.), ("wall_turn_rate", 2.)):
            if key in values and values.pop(key) != expected:
                raise ValueError(f"현재 모델에서 지원하지 않는 기록 설정: {key}")
        return cls(**values)


def load_backend(config: NeuralConfig):
    """Load five local modules without sys.path changes, __init__ or pyc writes.

    Private, content-addressed namespaces allow two different local sources to
    coexist. No gym/rendering/controller modules are imported. Local Python is
    trusted executable input, explicitly selected by API/CLI/environment.
    """
    root_value = config.source_root or os.environ.get("FLYTRACKER_NEURAL_SOURCE")
    if not root_value:
        raise ValueError("Neural flight requires neural.source_root / --neural-source / FLYTRACKER_NEURAL_SOURCE")
    root = Path(root_value).expanduser().resolve()
    data = Path(config.data_dir).expanduser().resolve() if config.data_dir else root / "data" / "stage2"
    paths = {f"flysim/{name}.py": root / "flysim" / f"{name}.py" for name in _MODULES}
    paths.update({f"data/{name}": data / name for name in ("neurons.csv", "edges.csv")})
    for name in ("selection.json", "zenodo_licenses.json"):
        if (data / name).is_file():
            paths[f"data/{name}"] = data / name
    for name in ("data/raw/manifest.json", "data/raw/Drosophila_brain_model/LICENSE"):
        if (root / name).is_file():
            paths[name] = root / name
    try:
        contents = {key: path.read_bytes() for key, path in paths.items()}
    except OSError as exc:
        raise ValueError(f"Cannot read local neural source/data: {exc}") from exc
    hashes = {key: hashlib.sha256(value).hexdigest() for key, value in contents.items()}
    identity = str(root) + repr(sorted((k, v) for k, v in hashes.items() if k.startswith("flysim/")))
    package_name = "_flytracker_local_" + hashlib.sha256(identity.encode()).hexdigest()
    with _LOAD_LOCK:
        if package_name not in sys.modules:
            package = ModuleType(package_name)
            package.__path__ = []
            sys.modules[package_name] = package
            try:
                for name in _MODULES:
                    full_name = f"{package_name}.{name}"
                    module = ModuleType(full_name)
                    module.__file__ = str(paths[f"flysim/{name}.py"])
                    module.__package__ = package_name
                    sys.modules[full_name] = module
                    exec(compile(contents[f"flysim/{name}.py"], module.__file__, "exec"), module.__dict__)
                    setattr(package, name, module)
            except Exception:
                for key in [k for k in sys.modules if k == package_name or k.startswith(package_name + ".")]:
                    del sys.modules[key]
                raise
        package = sys.modules[package_name]
    circuit = package.neural.Circuit.load(data)
    return SimpleNamespace(core=package.core, physics=package.physics, behavior=package.behavior,
                           circuit=circuit, root=root, data=data, hashes=hashes)


class NeuralFly:
    dt_s = 0.005

    def __init__(self, config: NeuralConfig, rng: np.random.Generator):
        self.p = config
        self.rng = rng
        self.backend = expand_flight_network(load_backend(config))
        self.sim = None

    def _vec(self, array):
        return self.backend.core.Vec3(*(float(x) for x in array))

    def reset(self, pos, heading):
        # Draw only in neural mode, AFTER the environment samples position/heading.
        self.seed = int(self.rng.integers(0, 2**31 - 1))
        b = self.backend
        groups = {'SGU':('DNa15','DNb01'),'escape':('DNp06','DNp03')}
        selected = groups.get(self.p.lesion,(self.p.lesion,))
        muted = sorted({i for group in selected for i in b.circuit.group(group)}) if self.p.lesion not in ('none','disconnected') else ()
        self.sim = NeuromechanicalSimulation(b, seed=self.seed, silenced=muted,
                                             disconnected=self.p.lesion == "disconnected")
        if self.sim.dt_s != self.dt_s or self.sim.neural.params.dt_ms != 0.1:
            raise ValueError("신체 5ms, 신경 0.1ms 간격이 필요합니다.")
        q = heading_quaternion(to_source(heading))
        forward = b.behavior.rotate(q, b.core.Vec3(1, 0, 0))
        # 초기 상태만 표본화한다. 반복 적용하는 목표 속도가 아니다.
        init_rng = np.random.default_rng(self.seed + 300000)
        speed = float(np.clip(init_rng.normal(.356, .183), .05, 1.))
        self.sim.initialize(b.physics.BodyState(position=self._vec(to_source(pos)), quaternion=q,
                                               velocity=b.physics.scale(forward, speed)))
        self.boundary_corrections = 0
        self.force_saturated_steps = 0
        self.speed_warning_steps = 0
        self.phase_events = []
        self._phase = "normal"
        self._disc_event = None
        self.last_applied_control = None

    @property
    def pos(self):
        return to_tracker(_array(self.sim.body.position))

    @pos.setter
    def pos(self, value):
        self.sim.body = replace(self.sim.body, position=self._vec(to_source(value)))

    @property
    def heading(self):
        return to_tracker(_array(self.backend.behavior.rotate(self.sim.body.quaternion, self.backend.core.Vec3(1, 0, 0))))

    @heading.setter
    def heading(self, value):
        self.sim.body = replace(self.sim.body, quaternion=heading_quaternion(to_source(value)))

    @property
    def velocity(self):
        return to_tracker(_array(self.sim.body.velocity))

    @property
    def quaternion(self):
        return self.backend.physics.qmultiply(MAP_QUATERNION, self.sim.body.quaternion)

    @property
    def angular_velocity(self):
        world = self.backend.behavior.rotate(self.sim.body.quaternion, self.sim.body.angular_rate)
        return to_tracker(_array(world))

    @property
    def speed(self):
        return float(np.linalg.norm(self.velocity))

    @property
    def alarmed(self):
        return self.sim.motor.phase in ("escape", "recovery")

    @property
    def turning(self):
        return np.linalg.norm(self.angular_velocity) > 1e-9

    def present_stimulus(self, event: dict | None, settings):
        # The fly receives a disc in space/time, never gaze or alignment state.
        identity = event["event_id"] if event else None
        if identity == self._disc_event:
            return
        self._disc_event = identity
        self.sim.disc = None if event is None else self.backend.behavior.LoomingDisc(
            center=self._vec(to_source(event["source"])), onset_s=event["onset_ms"] / 1000,
            duration_s=settings.pulse_ms / 1000, min_radius_m=settings.min_radius_m,
            max_radius_m=settings.max_radius_m, contrast=settings.contrast)

    def _correct_room(self, room):
        if not self.p.boundary_enabled:
            return
        position, hit = room.clamp(self.pos, margin=self.p.wall_margin)
        if not hit.any():
            return
        self.boundary_corrections += 1
        velocity = self.velocity
        for axis in np.flatnonzero(hit):
            inward = 1 if position[axis] <= room.lo[axis] + self.p.wall_margin else -1
            velocity[axis] = inward * abs(velocity[axis]) * .2
        # 비탄성 접촉 근사. 자세, 신경 상태와 다음 날개 명령은 보존한다.
        self.sim.body = replace(self.sim.body, position=self._vec(to_source(position)),
                                velocity=self._vec(to_source(velocity)))

    def step(self, dt, room: Room, aimer_pos=None):
        # aimer_pos is accepted only for Fly interface compatibility; never read.
        ratio = dt / self.dt_s
        if not math.isfinite(ratio) or ratio <= 0 or not math.isclose(ratio, round(ratio), abs_tol=1e-10, rel_tol=0):
            raise ValueError("NeuralFly dt must be a positive integer multiple of 5 ms")
        for _ in range(round(ratio)):
            lo, hi = to_source(room.lo), to_source(room.hi)
            self.sim.bounds = (np.minimum(lo, hi), np.maximum(lo, hi)) if self.p.boundary_enabled else None
            self.last_applied_control = {
                "start_ms": self.sim.clock.tick, "end_ms": self.sim.clock.tick + 5,
                "wing_force_body": self.sim.motor.force_body.tolist(),
                "wing_torque_body": self.sim.motor.torque_body.tolist(),
            }
            record = self.sim.step()
            self._correct_room(room)
            self.force_saturated_steps += record["force_saturated"]
            self.speed_warning_steps += record["speed_warning"]
            phase = self.sim.motor.phase
            if phase != self._phase:
                self.phase_events.append({"time_ms": self.sim.clock.tick, "phase": phase})
                self._phase = phase

    def diagnostics(self):
        record = self.sim.last_record or {}
        result = {"phase": self.sim.motor.phase, "neural_tick": self.sim.neural.tick,
                "body_time_ms": self.sim.clock.tick,
                "normal_rate_hz": record.get("normal_rate_hz", 0.0),
                "normal_input_hz": record.get("normal_drive_hz", 0.0),
                "dnp06_left_hz": record.get("dnp06_left_hz", 0.0),
                "dnp06_right_hz": record.get("dnp06_right_hz", 0.0),
                "left_input_hz": record.get("left_input_hz", 0.0),
                "right_input_hz": record.get("right_input_hz", 0.0),
                "speed_command_mps": None,
                "applied_control": self.last_applied_control,
                "velocity": self.velocity.tolist(), "quaternion": list(self.quaternion),
                "angular_velocity": self.angular_velocity.tolist(),
                "boundary_corrections": self.boundary_corrections,
                "force_saturated_steps": self.force_saturated_steps,
                "speed_warning_steps": self.speed_warning_steps}
        result.update(dynamics="neuromechanical",
                      wing={key: record.get(key) for key in ("stroke_amplitude_rad", "wing_lift_left_n",
                            "wing_lift_right_n", "wing_force_body", "wing_torque_body", "muscle_reflex_torque",
                            "normal_reference_hz")},
                      wall_sensory={side: record.get(f"wall_{side}_input_hz", 0.) for side in ("left", "right")},
                      extended_rates={key: record.get(key, 0.) for key in ("dnp03_left_hz", "dnp03_right_hz",
                                      "sgu_left_hz", "sgu_right_hz", "ves_left_hz", "ves_right_hz")})
        return result

    def provenance(self):
        return {"backend": "local_flysim_neuromechanical", "sha256": self.backend.hashes,
                "neurons": len(self.backend.circuit.ids), "connections": len(self.backend.circuit.pre),
                "effective_connections": int(np.count_nonzero(self.sim.neural.weights)),
                "synapses": int(np.abs(self.backend.circuit.signed_counts).sum()),
                "resolved_source_root": str(self.backend.root), "resolved_data_dir": str(self.backend.data),
                "settings": asdict(self.p), "coupling": asdict(self.sim.params),
                "physics": asdict(self.sim.physics), "lif": asdict(self.sim.neural.params),
                "seed": self.seed,
                "rights": "Local flysim code and annotation/derived CSV redistribution rights unresolved; not bundled",
                "surveyed_references": {
                    "shiu_model": "https://github.com/philshiu/Drosophila_brain_model/tree/91bdd1e7dcf193f3e7ca5a8933497fcef63b7960",
                    "annotations": "https://github.com/flyconnectome/flywire_annotations/tree/a83b2776d60d5764cef36b927f5f9679c16c47a2",
                    "connectivity": "https://zenodo.org/records/10676866",
                    "terms": "https://flywire.ai/tos"},
                "source_to_tracker": "(-Y,Z,-X)", "body_dt_s": 0.005, "neural_dt_ms": 0.1,
                "alarmed_phases": ["escape", "recovery"],
                "dynamics": self.p.dynamics,
                "neuromechanics": {
                    "brain": "Local measured connectivity, inherited LIF assumptions",
                    "reflex": "각속도와 그 내부 적분 상태의 지연된 근육 기능 모델. 세계 수평 또는 실제 quaternion으로 복원하지 않으며 VNC 시냅스 재구성은 아님",
                    "aerodynamics": "축약 준정상 날개 힘. 회전 감쇠는 Cheng2010 표2 A를 스트로크 면에서 변환. 주파수 스케일링은 논문 근거이며 진폭 스케일링/기하/양력 계수는 미보정 근사",
                    "trim_rate_hz": self.sim.motor.reference_rate,
                    "initial_velocity": "Long-segment first-1/30-s prior: normal(0.356,0.183) m/s clipped to [0.05,1]; initialization only",
                    "initial_state_seed": self.seed+300000,
                    "initial_trim": "reset 시 초기 자세로 날개 기준면과 감각 기준을 설정한다. 초기 속도로 추력을 역산하지 않고 이후 실제 자세를 읽어 복원하지 않는다. 이 초기 기준 설정도 모델 가정이다.",
                    "network": self.backend.flight_network,
                    "external_inputs": "LC4/LPLC1은 LPLC2와 같은 반구 자극 근사. SGU 상위 입력의 1Hz 배경 및 각속도→VES041 구동은 측정값이 아닌 기능 가정",
                    "contact": "Inelastic normal velocity impulse; no pose reset",
                    "sources": ["10.1016/j.cub.2022.01.008","10.1126/sciadv.abo7461","10.1016/j.cub.2010.07.025","10.1098/rstb.2015.0388","10.1016/j.cub.2023.12.047","10.1016/j.cub.2025.11.035","10.1242/jeb.038778"]},
                "biological_validation": {
                    "status": "not_calibrated",
                    "speed_mapping": "날개 힘과 항력의 적분 결과. Hz→날개 변환은 실측 보정 전",
                    "missing_mechanisms": ["검증된 발화→근육 변환", "재구성된 VNC 시냅스", "날갯짓 주기 내 비정상 공력", "동일 조건 행동 검증"],
                    "flight_speed_reference_mps": None,
                },
                "integration_sha256": {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                       for name in ("neural_fly.py", "stimulus.py", "neuromechanics.py", "flight_network.py")},
                "boundary": "시각 확장 입력과 비탄성 접촉. 위치/법선 속도만 보정, 자세/신경/근육 상태 보존"}
