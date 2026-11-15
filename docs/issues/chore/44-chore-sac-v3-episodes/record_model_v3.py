"""Record episodes of a trained aimer under the current environment, even if it was trained under an older version.

usage (from the repo root):
  uv run python docs/issues/chore/44-chore-sac-v3-episodes/record_model_v3.py <model run dir> --seed 10000 --episodes 3

Same environment as `scripts/record_baseline.py` with no flags (default `EnvConfig`, rule fly), so a run made here
with the same --seed and --episodes pairs episode by episode with a baseline run.

`load_opponent` refuses a model whose `envVersion` differs from the current one. That check is skipped here on
purpose: issue #44 asks how the #35 models (version 2) look under the version-3 capture rule. Observation and
action spaces did not change between the two versions. The run's config.json records the version the model was
trained under (`algo.trainedEnvVersion`) and where it came from (`algo.model`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))

from _common import run_episode, summarize  # noqa: E402

from flytracker import ENV_VERSION, EnvConfig, EpisodeRecorder, RunStore, make_env  # noqa: E402
from flytracker.players import algo_classes  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("model_run", help="run folder holding model.zip and config.json")
    p.add_argument("--episodes", type=int, default=5)
    p.add_argument("--seed", type=int, default=0, help="episode i starts from seed + i")
    p.add_argument("--name", default=None, help="run name; default <model run name>-v<env version>")
    p.add_argument("--runs-dir", default="runs")
    p.add_argument("--no-save", action="store_true")
    args = p.parse_args()

    src = Path(args.model_run)
    trained = json.loads((src / "config.json").read_text(encoding="utf-8"))
    algo = trained["algo"]
    if algo.get("side", "aimer") != "aimer":
        p.error(f"{src}: not an aimer model")
    model_name = src.name.split("_", 2)[-1]  # run id is <date>_<time>_<name>
    steps = int(algo["steps"])
    frame_stack = int(algo.get("frameStack", 1))

    cfg = EnvConfig()
    model = algo_classes()[algo["name"]].load(src / "model.zip", device="cpu")
    meta = {"policy": algo["name"], "side": "aimer", "opponent": "rule", "step": steps}
    env = EpisodeRecorder(make_env(cfg, "continuous", frame_stack), meta=meta)

    run = None
    if not args.no_save:
        seeds = f"{args.seed}-{args.seed + args.episodes - 1}"
        algo_cfg = {**algo, "model": src.name, "trainedEnvVersion": trained.get("envVersion", 1)}
        notes = (
            f"{model_name} final model from #35 (trained under env version {algo_cfg['trainedEnvVersion']}) "
            f"played under env version {ENV_VERSION}, seeds {seeds}"
        )
        run = RunStore(args.runs_dir).create_run(
            args.name or f"{model_name}-v{ENV_VERSION}", algo["name"], "continuous",
            {"env": cfg.to_dict(), "algo": algo_cfg}, notes=notes,
        )

    episodes = []
    for i in range(args.episodes):
        ep = run_episode(env, model, seed=args.seed + i)
        episodes.append(ep)
        if run:
            run.save_episode(ep, f"step_{steps:07d}")
    print(summarize(episodes))
    if run:
        print(f"saved: {run.dir}")


if __name__ == "__main__":
    main()
