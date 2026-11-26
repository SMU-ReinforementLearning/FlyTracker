"""Measure one aimer under env version 7: #72's measurement plus the two misfire kinds (grazes, wall shots).

usage (from the repo root):
  uv run python docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/measure_v7.py baseline --out <dir>
  uv run python docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/measure_v7.py <model run> --out <dir>
  uv run python docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/measure_v7.py <model run> --out <dir> --fly-model neural --no-stimulus --episodes 60
  uv run python docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/measure_v7.py mean a/gate.csv b/gate.csv c/gate.csv --out pooled.csv

Episodes and shots are played and recorded by #72's `measure_aimers.py` (`run_episode`); this script adds, per episode,
`grazes` (misfires in which the beam was on the fly for part of the shot) and `wall_shots` (misfires in which it never
was) from the environment, and carries them into gate.csv. A shot still in flight when the episode ends is in neither.

Writes into --out: episodes.csv, shots.csv, gate.csv (id, capture, time, misfires, grazes, wall_shots), meta.json.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_spec = importlib.util.spec_from_file_location("measure_aimers", ROOT / "docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/measure_aimers.py")
m72 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m72)  # also puts scripts/ on sys.path

from _common import add_env_args, config_from_args  # noqa: E402

from flytracker import ENV_VERSION, load_opponent  # noqa: E402
from flytracker.env import FlyChaseEnv  # noqa: E402
from flytracker.players import baseline_player  # noqa: E402

KINDS = ["grazes", "wall_shots"]
EPISODE_COLUMNS = m72.EPISODE_COLUMNS + KINDS
GATE_COLUMNS = m72.GATE_COLUMNS + KINDS


def mean_of(paths: list[str]) -> list[dict]:
    """Seed-by-seed mean of gate.csv files (a condition's value per seed is the mean over its models)."""
    tables = []
    for p in paths:
        with open(p, newline="", encoding="utf-8") as f:
            tables.append({int(r["id"]): r for r in csv.DictReader(f)})
    ids = sorted(tables[0])
    if any(sorted(t) != ids for t in tables):
        raise SystemExit("the gate files do not hold the same ids")
    return [{"id": i, **{c: round(sum(float(t[i][c]) for t in tables) / len(tables), 6) for c in GATE_COLUMNS[1:]}} for i in ids]


def summary(rows: list[dict]) -> str:
    n = len(rows)
    mean = lambda c: sum(float(r[c]) for r in rows) / n  # noqa: E731
    return (f"n={n} capture={mean('capture'):.4f} mean_time={mean('time'):.3f}s misfires/ep={mean('misfires'):.3f} "
            f"grazes/ep={mean('grazes'):.3f} wall_shots/ep={mean('wall_shots'):.3f}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("aimer", help="baseline, a run folder, or `mean`")
    p.add_argument("gate_files", nargs="*", help="mean: the gate.csv files to average")
    add_env_args(p)
    p.add_argument("--episodes", type=int, default=200)
    p.add_argument("--seed", type=int, default=20_000, help="episode i starts from seed + i")
    p.add_argument("--out", required=True, help="folder (or, for mean, the CSV to write)")
    args = p.parse_args()

    if args.aimer == "mean":
        rows = mean_of(args.gate_files)
        m72.write_csv(Path(args.out), GATE_COLUMNS, rows)
        print(f"{args.out}: {summary(rows)}")
        return

    cfg = config_from_args(args)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # a model trained under another fly, reward or version 6 differs only there
        aimer = load_opponent(args.aimer, "aimer", cfg)
    estimator = baseline_player(cfg).policy
    env = FlyChaseEnv(cfg)
    episodes, shots = [], []
    for i in range(args.episodes):
        ep, ep_shots = m72.run_episode(env, aimer.player, estimator, args.seed + i)
        ep.update(grazes=env.grazes, wall_shots=env.wall_shots)
        episodes.append(ep)
        shots.extend(ep_shots)
    gate = [{"id": e["seed"], "capture": e["captured"], "time": e["time_s"] if e["captured"] else cfg.max_seconds,
             "misfires": e["misfires"], "grazes": e["grazes"], "wall_shots": e["wall_shots"]} for e in episodes]

    out = Path(args.out)
    m72.write_csv(out / "episodes.csv", EPISODE_COLUMNS, episodes)
    m72.write_csv(out / "shots.csv", m72.SHOT_COLUMNS, shots)
    m72.write_csv(out / "gate.csv", GATE_COLUMNS, gate)
    model = Path(args.aimer) / "model.zip"
    meta = {
        "envVersion": ENV_VERSION,
        "gitCommit": os.environ.get("FLYTRACKER_COMMIT") or m72._git("rev-parse", "HEAD"),  # a bundle has no .git
        "gitDirty": bool(m72._git("status", "--porcelain", "--untracked-files=no")),
        "argv": [a if not Path(a).is_dir() else Path(a).name for a in sys.argv[1:]],  # no local paths
        "seeds": [args.seed, args.seed + args.episodes - 1],
        "aimer": {
            "label": aimer.label,
            "trainedEnvVersion": aimer.env_version,
            "fire": "rule" if args.aimer == "baseline" else aimer.fire,
            "modelSha256": hashlib.sha256(model.read_bytes()).hexdigest() if model.is_file() else None,
        },
        "env": cfg.to_dict(),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    total = max(sum(e["shots"] for e in episodes), 1)
    print(f"env version {ENV_VERSION}, aimer {aimer.label} (fire: {meta['aimer']['fire']}), fly {cfg.fly_model}"
          f"{'' if cfg.fly_model != 'neural' else ' stimulus ' + ('on' if cfg.stimulus.enabled else 'off')}, "
          f"seeds {args.seed}-{args.seed + args.episodes - 1}")
    print(f"{summary(gate)} shots/ep={total / len(episodes):.2f} -> {out.name}")


if __name__ == "__main__":
    main()
