"""#88. Episode length, reward and entropy coefficient during training, from the tensorboard logs (#85's script, new names).

Episodes are cut at 500 steps (10 s), so a mean length below 500 means that share of recent episodes ended in a capture.

    uv run python docs/issues/feature/88-feature-aimer-accel-action-sac-fire/training_logs.py [runs/g88] > data/training-logs.md
    uv run python docs/issues/feature/88-feature-aimer-accel-action-sac-fire/training_logs.py runs/g88f fire > data/training-logs-fire.md
"""

from __future__ import annotations

import sys
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

MODELS = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/g88")
TAGS = ("rollout/ep_len_mean", "rollout/ep_rew_mean", "train/ent_coef")
STAGE2 = len(sys.argv) > 2 and sys.argv[2] == "fire"  # the fire-only runs of gate-fire.md (500,000 steps)
AT = (50_000, 100_000, 200_000, 300_000, 350_000, 400_000, 450_000, 500_000) if STAGE2 else (
    50_000, 100_000, 200_000, 300_000, 500_000, 700_000, 1_000_000)
CONDITIONS = ("fire-m1", "fire-m5", "fire-prior-m1", "fire-prior-m5") if STAGE2 else (
    "rate-rule", "accel-rule", "accel-pen-rule", "accel-fire-m03", "accel-fire-m10")


def main() -> None:
    print("| run | tag | " + " | ".join(f"{s // 1000}k" for s in AT) + " |")
    print("| --- | --- | " + " | ".join("---" for _ in AT) + " |")
    for cond in CONDITIONS:
        for seed in range(3):
            name = f"{cond}-s{seed}"
            tb = next((MODELS / name).glob("*/tb/*"))
            acc = EventAccumulator(str(tb), size_guidance={"scalars": 0})
            acc.Reload()
            for tag in TAGS:
                events = acc.Scalars(tag)
                cells = []
                for at in AT:
                    e = min(events, key=lambda x: abs(x.step - at))
                    cells.append(f"{e.value:.4g}")
                print(f"| {name} | {tag} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
