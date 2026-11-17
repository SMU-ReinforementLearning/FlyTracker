"""Run every bootstrap named in gate.md and write the unedited output to gate/bootstrap-<fly>.md.

usage (from the repo root; pool the three models first with `measure_aimers.py mean`):
  uv run python docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/run_gate.py rule-fly
  uv run python docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/run_gate.py neural-fly-nostim
  uv run python docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/run_gate.py neural-fly-stim

rule-fly is the gate (baseline = gate/baseline.csv, frozen). The neural runs are reported only.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = ROOT / ".claude/skills/experiment-gate/scripts/paired_bootstrap.py"
MODELS = ["sac-beam-assist-s0", "sac-beam-assist-s1", "sac-beam-assist-s2"]


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def boot(truth: Path, a: Path, b: Path, target: str, threshold: float | None) -> str:
    cmd = [sys.executable, str(TOOL), "--truth", rel(truth), "--a", rel(a), "--b", rel(b), "--targets", target,
           "--metric", "mae", "--lower-is-better", "--resamples", "10000", "--seed", "42"]
    if threshold is not None:
        cmd += ["--threshold", str(threshold)]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT, check=True).stdout


def main() -> None:
    fly = sys.argv[1]
    gate = fly == "rule-fly"
    truth = HERE / "gate" / ("truth.csv" if gate else "truth-neural.csv")
    base = HERE / "gate" / "baseline.csv" if gate else HERE / "data" / fly / "baseline" / "gate.csv"
    pooled = HERE / "gate" / ("sac-beam-assist-rule-fire.csv" if gate else f"sac-beam-assist-rule-fire-{fly}.csv")
    per_model = [HERE / "data" / fly / m / "gate.csv" for m in MODELS]

    out = ["== sha256"]
    for p in [truth, base, pooled, *per_model]:
        out.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()} *{rel(p)}")
    out.append("")
    label = "gated" if gate else "reported"
    out += [f"########## pooled vs baseline: time ({label})", boot(truth, base, pooled, "time", 0.90)]
    out += ["########## pooled vs baseline: capture (value = miss rate; reported)", boot(truth, base, pooled, "capture", None)]
    out += ["########## pooled vs baseline: misfires (reported)", boot(truth, base, pooled, "misfires", None)]
    for m, p in zip(MODELS, per_model):
        out += [f"########## per model: {m} vs baseline, time (undecided if P < 0.50)", boot(truth, base, p, "time", 0.50)]
    dest = HERE / "gate" / f"bootstrap-{fly}.md"
    dest.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {rel(dest)}")  # the tables hold characters a cp949 console cannot print; read the file


if __name__ == "__main__":
    main()
