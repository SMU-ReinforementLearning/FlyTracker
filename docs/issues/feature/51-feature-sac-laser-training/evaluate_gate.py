"""Gate evaluation for issue #51: one row per evaluation seed, for paired_bootstrap.py.

Run from the repo root:
    uv run python docs/issues/feature/51-feature-sac-laser-training/evaluate_gate.py baseline --out gate/baseline.csv
    uv run python docs/issues/feature/51-feature-sac-laser-training/evaluate_gate.py model runs/<id> --out c.csv
    uv run python docs/issues/feature/51-feature-sac-laser-training/evaluate_gate.py truth --out gate/truth.csv
    uv run python docs/issues/feature/51-feature-sac-laser-training/evaluate_gate.py mean a.csv b.csv c.csv --out pooled.csv

Columns: id (episode seed), capture (1 if captured), time (seconds until capture; the
episode length, 10 s, when not captured). The environment is the default EnvConfig with the
rule fly. A model is loaded with `load_opponent`, which rebuilds the frame stack and the
tracking assist the run was trained with; it acts deterministically. Nothing is recorded to runs/.
The reward weights of a run do not enter: time and capture do not depend on them.
"""

from __future__ import annotations

import argparse
import csv
import warnings
from pathlib import Path

from flytracker import EnvConfig, FlyChaseEnv, load_opponent

SEED0 = 20_000
N = 200


def evaluate(player, seeds: range) -> list[dict]:
    env = FlyChaseEnv(EnvConfig())
    rows = []
    for seed in seeds:
        obs, info = env.reset(seed=seed)
        player.reset()
        done = False
        while not done:
            obs, _, terminated, truncated, info = env.step(player.act(obs))
            done = terminated or truncated
        rows.append({"id": seed, "capture": int(info["captured"]), "time": round(info["t"], 4)})
    return rows


def write(rows: list[dict], out: str) -> None:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        # LF line endings, so the file (and its sha256 in gate.md) is the same after a git checkout anywhere
        w = csv.DictWriter(f, fieldnames=["id", "capture", "time"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    n = len(rows)
    caught = sum(float(r["capture"]) for r in rows)
    print(f"{out}: n={n} capture={caught / n:.4f} mean_time={sum(float(r['time']) for r in rows) / n:.3f}s")


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
    p.add_argument("paths", nargs="*", help="model: one run folder; mean: the CSVs to average")
    p.add_argument("--seed0", type=int, default=SEED0)
    p.add_argument("--n", type=int, default=N)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    seeds = range(args.seed0, args.seed0 + args.n)

    if args.what == "baseline":
        rows = evaluate(load_opponent("baseline", "aimer", EnvConfig()).player, seeds)
    elif args.what == "model":
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # a run trained with other reward weights differs from the default config only there
            player = load_opponent(args.paths[0], "aimer", EnvConfig()).player
        rows = evaluate(player, seeds)
    elif args.what == "truth":
        rows = [{"id": s, "capture": 1, "time": 0.0} for s in seeds]
    else:
        rows = mean_of(args.paths)
    write(rows, args.out)


if __name__ == "__main__":
    main()
