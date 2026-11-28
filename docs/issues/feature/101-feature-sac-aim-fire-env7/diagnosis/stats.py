"""Issue #101 diagnosis: per-model tracking and shot statistics from measure_v7.py output folders.

usage: python stats.py <label>=<out dir> [<label>=<out dir> ...]
Reads episodes.csv and shots.csv of each folder and prints one row per folder.
"""

from __future__ import annotations

import csv
import statistics as st
import sys
from pathlib import Path


def rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(v: str) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def mean(xs) -> float:
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def main() -> None:
    head = ("label", "n", "capture", "time", "visible", "never_seen", "first_vis_s", "first_shot_s", "shots/ep",
            "no_shot_eps", "shots_per_vis_s", "hit/shot", "graze/shot", "wall/shot", "shot_len_s", "beam_mm@start")
    print("| " + " | ".join(head) + " |")
    print("| " + " | ".join("---" for _ in head) + " |")
    for arg in sys.argv[1:]:
        label, folder = arg.split("=", 1)
        eps = rows(Path(folder) / "episodes.csv")
        shots = rows(Path(folder) / "shots.csv")
        n = len(eps)
        cap = mean(float(e["captured"]) for e in eps)
        time = mean(float(e["time_s"]) if e["captured"] == "1" else 10.0 for e in eps)
        vis = mean(float(e["visible_ratio"]) for e in eps)
        never = sum(1 for e in eps if fnum(e["first_visible_s"]) is None) / n
        fvis = mean(fnum(e["first_visible_s"]) for e in eps)
        fshot = mean(fnum(e["first_shot_s"]) for e in eps)
        nshots = sum(int(e["shots"]) for e in eps)
        noshot = sum(1 for e in eps if int(e["shots"]) == 0) / n
        vis_s = sum(float(e["visible_ratio"]) * float(e["time_s"]) for e in eps)
        hits = sum(int(e["captured"]) for e in eps)
        grazes = sum(int(e["grazes"]) for e in eps)
        walls = sum(int(e["wall_shots"]) for e in eps)
        lens = [fnum(s["t_off_s"]) - fnum(s["t_start_s"]) for s in shots if fnum(s["t_off_s"]) is not None]
        beam = [fnum(s["est_beam_mm"]) for s in shots if fnum(s["est_beam_mm"]) is not None]
        d = max(nshots, 1)
        vals = (label, n, f"{cap:.3f}", f"{time:.3f}", f"{vis:.3f}", f"{never:.3f}", f"{fvis:.2f}", f"{fshot:.2f}",
                f"{nshots / n:.2f}", f"{noshot:.3f}", f"{nshots / max(vis_s, 1e-9):.2f}", f"{hits / d:.3f}",
                f"{grazes / d:.3f}", f"{walls / d:.3f}", f"{mean(lens):.3f}", f"{st.median(beam) if beam else float('nan'):.3f}")
        print("| " + " | ".join(str(v) for v in vals) + " |")


if __name__ == "__main__":
    main()
