"""Run every bootstrap named in gate.md and write the unedited output to gate/bootstrap-output.md.

usage (from the repo root, after the 15 models were measured and pooled; see data/README.md):
  uv run python docs/issues/feature/88-feature-aimer-accel-action-sac-fire/run_gate.py

Inputs: gate/baseline.csv and gate/truth.csv (frozen), gate/<candidate>.csv (mean of the three models per seed),
data/<candidate>-s<k>/gate.csv (one model each), and gate/v1.csv when present (#72's pooled v1 file, descriptive only).
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = ROOT / ".claude/skills/experiment-gate/scripts/paired_bootstrap.py"
CANDIDATES = ["rate-rule", "accel-rule", "accel-pen-rule", "accel-fire-m03", "accel-fire-m10"]
PAIRS = [("rate-rule", "accel-rule"), ("accel-rule", "accel-pen-rule"), ("accel-rule", "accel-fire-m03"),
         ("accel-rule", "accel-fire-m10"), ("accel-fire-m03", "accel-fire-m10")]


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
    base = gate / "baseline.csv"
    files = [gate / "truth.csv", base] + [gate / f"{c}.csv" for c in CANDIDATES] + [data / f"{c}-s{s}" / "gate.csv" for c in CANDIDATES for s in range(3)]
    v1 = gate / "v1.csv"
    if v1.exists():
        files.append(v1)
    out = ["== sha256"] + [f"{hashlib.sha256(p.read_bytes()).hexdigest()} *{rel(p)}" for p in files] + [""]
    for c in CANDIDATES:
        pooled = gate / f"{c}.csv"
        out += [f"########## GATE {c} vs baseline: time (gated)", boot(base, pooled, "time", 0.90)]
        out += [f"########## {c} vs baseline: capture (value = miss rate; exclusion if pooled capture < 0.97)", boot(base, pooled, "capture", None)]
        out += [f"########## {c} vs baseline: misfires (undecided if pooled misfires per episode > 1.00)", boot(base, pooled, "misfires", None)]
        for s in range(3):
            out += [f"########## per training seed: {c}-s{s} vs baseline, time (undecided if P < 0.50)",
                    boot(base, data / f"{c}-s{s}" / "gate.csv", "time", 0.50)]
    for a, b in PAIRS:
        for t in ("time", "capture", "misfires"):
            out += [f"########## descriptive: {b} (B) vs {a} (A), {t}", boot(gate / f"{a}.csv", gate / f"{b}.csv", t, None)]
    if v1.exists():
        for c in CANDIDATES:
            for t in ("time", "capture", "misfires"):
                out += [f"########## descriptive: {c} (B) vs v1 (A), {t}", boot(v1, gate / f"{c}.csv", t, None)]
    dest = gate / "bootstrap-output.md"
    dest.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {rel(dest)}")  # the tables hold characters a cp949 console cannot print; read the file


if __name__ == "__main__":
    main()
