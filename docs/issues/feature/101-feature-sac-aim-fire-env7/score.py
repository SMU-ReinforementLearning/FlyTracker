"""Add the gate's score columns to a gate CSV of measure_v7.py (issue #101).

usage: uv run python docs/issues/feature/101-feature-sac-aim-fire-env7/score.py <in.csv> --out <out.csv>
       uv run python docs/issues/feature/101-feature-sac-aim-fire-env7/score.py truth --out gate/truth.csv

score_w1 = time + 1.0 x wall_shots, score_w3 = time + 3.0 x wall_shots (seconds): a wall shot priced at 1 s and at 3 s.
`truth` writes the truth file for seeds 20000-20199 (capture 1, everything else 0).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

PRICES = {"score_w1": 1.0, "score_w3": 3.0}
BASE = ["id", "capture", "time", "misfires", "grazes", "wall_shots"]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help="a gate CSV, or `truth`")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    if args.source == "truth":
        rows = [{"id": i, "capture": 1, **{c: 0 for c in BASE[2:]}} for i in range(20_000, 20_200)]
    else:
        with open(args.source, newline="", encoding="utf-8") as f:
            rows = [{c: r[c] for c in BASE} for r in csv.DictReader(f)]
    for r in rows:
        for name, price in PRICES.items():
            r[name] = round(float(r["time"]) + price * float(r["wall_shots"]), 6)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=BASE + list(PRICES), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    n = len(rows)
    print(f"{out}: n={n} " + " ".join(f"{c}={sum(float(r[c]) for r in rows) / n:.3f}" for c in ["time", "wall_shots", *PRICES]))


if __name__ == "__main__":
    main()
