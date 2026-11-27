"""Issue #101 diagnosis: training curves of runs from their TensorBoard logs.

usage: python curves.py <label>=<run dir> [...] [--tags]
Prints, per run, the mean of each scalar over five equal parts of training (by step). --tags lists the scalar tags.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

WANT = ["rollout/ep_rew_mean", "rollout/ep_len_mean", "train/ent_coef", "train/actor_loss", "train/critic_loss"]


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--tags"]
    for arg in args:
        label, run = arg.split("=", 1)
        files = sorted(Path(run).rglob("events.out.tfevents.*"))
        acc = EventAccumulator(str(files[0].parent), size_guidance={"scalars": 0})
        acc.Reload()
        tags = acc.Tags()["scalars"]
        if "--tags" in sys.argv:
            print(label, tags)
            continue
        for tag in [t for t in tags if t in WANT or t.startswith(("rollout/", "episode/", "env/"))]:
            ev = acc.Scalars(tag)
            last = ev[-1].step
            parts = []
            for i in range(5):
                lo, hi = last * i / 5, last * (i + 1) / 5
                vals = [e.value for e in ev if lo < e.step <= hi]
                parts.append(sum(vals) / len(vals) if vals else float("nan"))
            print(f"{label:12s} {tag:28s} " + " ".join(f"{p:9.3f}" for p in parts) + f"  (last step {last})")


if __name__ == "__main__":
    main()
