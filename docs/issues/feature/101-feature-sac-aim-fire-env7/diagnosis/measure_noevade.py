"""Issue #101 diagnosis: #91's measure_v7.py with the rule fly's reaction to the beam switched off.

usage (from the repo root): python docs/issues/feature/101-feature-sac-aim-fire-env7/diagnosis/measure_noevade.py <model run> --out <dir>

Same arguments, episodes, seeds and outputs as measure_v7.py; the only difference is `FlyParams.evade_laser = False`,
which is the rule fly of env version 6. meta.json records the switched-off value under env.fly.
"""

from __future__ import annotations

import dataclasses
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location(
    "measure_v7", ROOT / "docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/measure_v7.py")
m7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m7)

_orig = m7.config_from_args


def _no_evade(args):
    cfg = _orig(args)
    return dataclasses.replace(cfg, fly=dataclasses.replace(cfg.fly, evade_laser=False))


m7.config_from_args = _no_evade

if __name__ == "__main__":
    import flytracker
    print("flytracker from", Path(flytracker.__file__).resolve().parent)
    m7.main()
