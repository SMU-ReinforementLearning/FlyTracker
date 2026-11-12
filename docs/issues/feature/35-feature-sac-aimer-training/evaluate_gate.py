"""Gate evaluation for issue #35: one row per evaluation seed, for paired_bootstrap.py.

Run from the repo root:
    uv run python docs/issues/feature/35-feature-sac-aimer-training/evaluate_gate.py baseline --out base.csv
    uv run python docs/issues/feature/35-feature-sac-aimer-training/evaluate_gate.py model runs/<id>/model.zip --frame-stack 4 --out c.csv
    uv run python docs/issues/feature/35-feature-sac-aimer-training/evaluate_gate.py truth --out truth.csv
    uv run python docs/issues/feature/35-feature-sac-aimer-training/evaluate_gate.py mean a.csv b.csv c.csv --out pooled.csv

Columns: id (episode seed), capture (1 if captured), time (seconds until capture; the
episode length, 10 s by default, when not captured). The environment is the default
EnvConfig, the policy acts deterministically, nothing is recorded to runs/.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from flytracker import EnvConfig, RuleAimer, make_env

SEED0 = 20_000
N = 200


def evaluate(policy, frame_stack: int, seeds: range) -> list[dict]:
    env = make_env(EnvConfig(), "continuous", frame_stack)
    rows = []
    for seed in seeds:
        if hasattr(policy, "reset"):  # RuleAimer clears its search state per episode
            policy.reset()
        obs, info = env.reset(seed=seed)
        done = False
        while not done:
            action, _ = policy.predict(obs, deterministic=True)
            obs, _, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        rows.append({"id": seed, "capture": int(info["captured"]), "time": round(info["t"], 4)})
    return rows


def write(rows: list[dict], out: str) -> None:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "capture", "time"])
        w.writeheader()
        w.writerows(rows)
    n = len(rows)
    caught = sum(r["capture"] for r in rows)
    print(f"{out}: n={n} capture={caught / n:.4f} mean_time={sum(r['time'] for r in rows) / n:.3f}s")


def mean_of(paths: list[str]) -> list[dict]:
    tables = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            tables.append({int(r["id"]): r for r in csv.DictReader(f)})
    ids = sorted(tables[0])
    if any(sorted(t) != ids for t in tables):
        raise SystemExit("files cover different ids")
    k = len(tables)
    return [
        {
            "id": i,
            "capture": round(sum(float(t[i]["capture"]) for t in tables) / k, 6),
            "time": round(sum(float(t[i]["time"]) for t in tables) / k, 4),
        }
        for i in ids
    ]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("what", choices=["baseline", "model", "truth", "mean"])
    p.add_argument("paths", nargs="*", help="model: one .zip; mean: the CSVs to average")
    p.add_argument("--frame-stack", type=int, default=1)
    p.add_argument("--seed0", type=int, default=SEED0)
    p.add_argument("--n", type=int, default=N)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    seeds = range(args.seed0, args.seed0 + args.n)

    if args.what == "baseline":
        rows = evaluate(RuleAimer(max_pitch_deg=EnvConfig().aimer.max_pitch_deg), 1, seeds)
    elif args.what == "model":
        from stable_baselines3 import SAC

        rows = evaluate(SAC.load(args.paths[0], device="cpu"), args.frame_stack, seeds)
    elif args.what == "truth":
        rows = [{"id": s, "capture": 1, "time": 0.0} for s in seeds]
    else:
        rows = mean_of(args.paths)
    write(rows, args.out)


if __name__ == "__main__":
    main()
