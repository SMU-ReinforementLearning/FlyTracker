"""Experiment-owned gaze gate. Alignment presents a stimulus, never an escape command."""

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class StimulusConfig:
    enabled: bool = True
    align_deg: float = 2.5
    charge_ms: int = 120
    discharge_ms: int = 200
    pulse_ms: int = 250
    cooldown_ms: int = 800
    max_events: int = 3
    min_radius_m: float = 0.01
    max_radius_m: float = 0.12
    contrast: float = 1.0
    mode: str = "looming"

    def __post_init__(self):
        if self.mode != "looming":
            raise ValueError("가상 자극은 looming만 지원합니다.")
        if type(self.enabled) is not bool:
            raise ValueError("stimulus.enabled must be boolean")
        if not math.isfinite(self.align_deg) or not 0 < self.align_deg < 30:
            raise ValueError("align_deg must be in (0, 30)")
        for key in ("charge_ms", "discharge_ms", "pulse_ms", "cooldown_ms"):
            value = getattr(self, key)
            if type(value) is not int or value <= 0 or value % 5:
                raise ValueError(f"{key} must be a positive multiple of 5 ms")
        if type(self.max_events) is not int or self.max_events < 0:
            raise ValueError("max_events must be a nonnegative integer")
        if not all(math.isfinite(v) for v in (self.min_radius_m, self.max_radius_m, self.contrast)):
            raise ValueError("Nonfinite disc setting")
        if not 0 < self.min_radius_m < self.max_radius_m or not 0 <= self.contrast <= 1:
            raise ValueError("Invalid disc radii/contrast")

    @classmethod
    def from_dict(cls, values):
        values = dict(values)
        if "release_ms" in values and values.pop("release_ms") != 200:
            raise ValueError("현재 자극에서 지원하지 않는 release_ms 설정입니다.")
        return cls(**values)


class StimulusScheduler:
    """Sample at t; charge covers [t,t+5), so a new pulse starts at t+5.

    Source position is latched in FlyTracker coordinates at trigger time. Events
    and neural phases are evaluator data and must not enter policy observations.
    """

    def __init__(self, config: StimulusConfig):
        self.config = config
        self.tick_ms = 0
        self.charge = 0.0
        self.events: list[dict] = []
        self._next_allowed_ms = 0
        self._current: dict | None = None
        self.aligned_ms = 0
        self.exposure_ms = 0

    def advance(self, time_ms: int, visible: bool, angle_rad: float, source) -> dict | None:
        if type(time_ms) is not int or time_ms != self.tick_ms:
            raise ValueError("Stimulus clock must advance in exact 5 ms steps")
        if not math.isfinite(angle_rad) or not 0 <= angle_rad <= math.pi:
            raise ValueError("Invalid alignment angle")
        p = self.config
        aligned = visible and angle_rad <= math.radians(p.align_deg)
        self.aligned_ms += 5 * int(aligned)
        if self._current and time_ms >= self._current["end_ms"]:
            self._current = None
        eligible = p.enabled and len(self.events) < p.max_events and time_ms >= self._next_allowed_ms
        if eligible:
            delta = 5 / (p.charge_ms if aligned else p.discharge_ms)
            self.charge = min(1.0, max(0.0, self.charge + (delta if aligned else -delta)))
            if self.charge >= 1 - 1e-12:
                onset = time_ms + 5
                self._current = {
                    "event_id": len(self.events) + 1,
                    "onset_ms": onset,
                    "end_ms": onset + p.pulse_ms,
                    "source": [float(v) for v in source],
                    "alignment_deg": math.degrees(angle_rad),
                    "mode": "gaze_contingent_virtual_loom",
                    "exposure_ms": 0,
                }
                self.events.append(self._current.copy())
                self._next_allowed_ms = onset + p.pulse_ms + p.cooldown_ms
                self.charge = 0.0
        else:
            self.charge = 0.0
        active = self._current is not None and self._current["onset_ms"] <= time_ms < self._current["end_ms"]
        self.exposure_ms += 5 * int(active)
        if active:
            self.events[-1]["exposure_ms"] += 5
        self.tick_ms += 5
        return self._current.copy() if self._current else None

    def diagnostics(self) -> dict:
        return {"settings": asdict(self.config), "charge": self.charge,
                "event_count": len(self.events), "events": [e.copy() for e in self.events],
                "aligned_ms": self.aligned_ms, "exposure_ms": self.exposure_ms}
