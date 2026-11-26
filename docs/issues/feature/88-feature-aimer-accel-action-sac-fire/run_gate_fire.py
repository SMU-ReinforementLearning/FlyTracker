"""Run every bootstrap named in gate-fire.md and write the unedited output to gate/bootstrap-output-fire.md.

usage (from the repo root, after the 12 fire-only models were measured and pooled; see data/README.md):
  uv run python docs/issues/feature/88-feature-aimer-accel-action-sac-fire/run_gate_fire.py

Inputs: gate/accel-pen-rule.csv (frozen baseline of this gate) and gate/truth.csv, data/accel-pen-rule-s<k>/gate.csv
(the aim model with rule fire, for the per-seed check), gate/<candidate>.csv (mean of the three models per seed),
data/<candidate>-s<k>/gate.csv, and gate/baseline.csv, gate/v1.csv (v0 and v1, descriptive only).
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = ROOT / ".claude/skills/experiment-gate/scripts/paired_bootstrap.py"
CANDIDATES = ["fire-m1", "fire-m5", "fire-prior-m1", "fire-prior-m5"]
PAIRS = [("fire-m1", "fire-prior-m1"), ("fire-m5", "fire-prior-m5"), ("fire-m1", "fire-m5"), ("fire-prior-m1", "fire-prior-m5")]
TARGETS = ("time", "capture", "misfires")


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def boot(a: Path, b: Path, target: str, threshold: float | None) -> str:
    cmd = [sys.executable, str(TOOL), "--truth", rel(HERE / "gate/truth.csv"), "--a", rel(a), "--b", rel(b), "--targets", target,
           "--metric", "mae", "--lower-is-better", "--resamples", "10000", "--seed", "42"]
    if threshold is not None:
        cmd += ["--threshold", str(threshold)]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT, check=True).stdout


def main() -> None:
    gate, data = HERE / "gate", HERE / "data"
    base = gate / "accel-pen-rule.csv"
    aims = [data / f"accel-pen-rule-s{s}" / "gate.csv" for s in range(3)]
    refs = {"v0": gate / "baseline.csv", "v1": gate / "v1.csv"}
    files = [gate / "truth.csv", base, *aims, *refs.values()] + [gate / f"{c}.csv" for c in CANDIDATES] + [
        data / f"{c}-s{s}" / "gate.csv" for c in CANDIDATES for s in range(3)]
    out = ["== sha256"] + [f"{hashlib.sha256(p.read_bytes()).hexdigest()} *{rel(p)}" for p in files] + [""]
    for c in CANDIDATES:
        pooled = gate / f"{c}.csv"
        out += [f"########## GATE {c} vs accel-pen-rule (rule fire): time (gated)", boot(base, pooled, "time", 0.90)]
        out += [f"########## {c} vs accel-pen-rule: capture (value = miss rate; exclusion if pooled capture < 0.97)", boot(base, pooled, "capture", None)]
        out += [f"########## {c} vs accel-pen-rule: misfires (undecided if pooled above the baseline's; declared case needs P >= 0.90)",
                boot(base, pooled, "misfires", 0.90)]
        for s in range(3):
            own = data / f"{c}-s{s}" / "gate.csv"
            out += [f"########## per training seed: {c}-s{s} vs accel-pen-rule-s{s} (rule fire), time (undecided if P < 0.50)", boot(aims[s], own, "time", 0.50)]
            out += [f"########## per training seed, descriptive: {c}-s{s} vs accel-pen-rule-s{s}, misfires", boot(aims[s], own, "misfires", None)]
    for a, b in PAIRS:
        for t in TARGETS:
            out += [f"########## descriptive: {b} (B) vs {a} (A), {t}", boot(gate / f"{a}.csv", gate / f"{b}.csv", t, None)]
    for name, ref in refs.items():
        for c in CANDIDATES:
            for t in TARGETS:
                out += [f"########## descriptive: {c} (B) vs {name} (A), {t}", boot(ref, gate / f"{c}.csv", t, None)]
    dest = gate / "bootstrap-output-fire.md"
    dest.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {rel(dest)}")  # the tables hold characters a cp949 console cannot print; read the file


if __name__ == "__main__":
    main()
