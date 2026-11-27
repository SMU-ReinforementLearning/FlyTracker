"""Issue #101 diagnosis: #91's measure_v7.py with the aimer's actions sampled, as during SAC training.

usage (from the repo root): python docs/issues/feature/101-feature-sac-aim-fire-env7/diagnosis/measure_stochastic.py <model run> --out <dir>

Same arguments, episodes, seeds and outputs as measure_v7.py (env version 7, the fly reacts to the beam); the only
difference is that the model's `predict` is called with `deterministic=False`. The fire rule is unchanged.
The sampling is seeded once (torch seed 0), so a run repeats.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[5]
_spec = importlib.util.spec_from_file_location(
    "measure_v7", ROOT / "docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/measure_v7.py")
m7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m7)

_orig = m7.load_opponent


def _sampled(spec, side, cfg):
    opp = _orig(spec, side, cfg)
    policy = opp.player.policy
    predict = policy.predict
    policy.predict = lambda obs, *a, **k: predict(obs, *a, **{**k, "deterministic": False})
    return opp


m7.load_opponent = _sampled

if __name__ == "__main__":
    torch.manual_seed(0)
    m7.main()
