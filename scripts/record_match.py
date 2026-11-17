"""Record episodes of one aimer (the rule baseline or a trained model) under any environment setting.

usage (from the repo root):
  uv run python scripts/record_match.py baseline --fly-model neural
  uv run python scripts/record_match.py runs/<model run> --fly-model neural --no-stimulus

The aimer is `baseline` or a run folder holding `model.zip` and `config.json`. The environment flags are those of
`scripts/record_baseline.py` (`--fly-model`, `--no-stimulus`, ...). Defaults: seeds 10000-10002, as in the runs
published so far.

The aimer is built by `load_opponent`, the same way `scripts/match.py` builds it, so a model trained with a
tracking assist (`algo.assist` in its config.json) plays with that assist. Calling `model.predict` directly, as
#44's `record_model_v3.py` does, would drop it. An aimer model trained under env version 5 (no fire action) is
loaded with the baseline's firing rule; the run's config.json then has `algo.fire: "rule"` (#72).

Moved here from docs/issues/chore/61-chore-neural-fly-sac-episodes/ in #72, after three issues had used it.

The neural fly needs the local flysim project. Give it with the FLYTRACKER_NEURAL_SOURCE environment variable,
not with `--neural-source`: the flag writes the local path into the run's config.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _common import add_env_args, config_from_args, summarize  # noqa: E402

from flytracker import ENV_VERSION, EpisodeRecorder, RunStore, load_opponent  # noqa: E402
from flytracker.env import FlyChaseEnv  # noqa: E402

BASELINE = "baseline"


def stimulus_label(cfg) -> str:
    if cfg.fly_model != "neural":
        return "rule"
    return "neural-stim" if cfg.stimulus.enabled else "neural-nostim"


def play(env: EpisodeRecorder, player, seed: int) -> dict:
    """One episode. The player sees the raw observation, as in `matchup.play_cell`."""
    player.reset()
    obs, _ = env.reset(seed=seed)
    done = False
    while not done:
        obs, _, terminated, truncated, _ = env.step(player.act(obs))
        done = terminated or truncated
    return env.last_episode


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("aimer", help="baseline, or a run folder holding model.zip and config.json")
    add_env_args(p)
    p.add_argument("--episodes", type=int, default=3)
    p.add_argument("--seed", type=int, default=10_000, help="episode i starts from seed + i")
    p.add_argument("--name", default=None, help="run name; default <fly setting>-<aimer name>")
    p.add_argument("--runs-dir", default="runs")
    p.add_argument("--no-save", action="store_true", help="print the summary only")
    args = p.parse_args()

    cfg = config_from_args(args)
    try:
        aimer = load_opponent(args.aimer, "aimer", cfg)
    except (ValueError, FileNotFoundError) as e:
        p.error(str(e))

    seeds = f"{args.seed}-{args.seed + args.episodes - 1}"
    if args.aimer == BASELINE:
        aimer_name, policy, tag = BASELINE, "rule-baseline", BASELINE
        algo_cfg = {"name": "rule-baseline"}
        meta = {"policy": policy}
        notes = f"rule baseline aimer, fly {stimulus_label(cfg)}, seeds {seeds}"
    else:
        src = Path(args.aimer)
        trained = json.loads((src / "config.json").read_text(encoding="utf-8"))
        algo = trained["algo"]
        aimer_name = src.name.split("_", 2)[-1]  # run id is <date>_<time>_<name>
        policy, steps = algo["name"], int(algo["steps"])
        tag = f"step_{steps:07d}"
        # `opponent` stays what the model was trained against; the fly of this run is in env.fly_model
        algo_cfg = {**algo, "model": src.name, "trainedEnvVersion": trained.get("envVersion", 1), "fire": aimer.fire}
        meta = {"policy": policy, "side": "aimer", "opponent": cfg.fly_model, "step": steps}
        notes = (
            f"{aimer_name} final model (trained against the {algo.get('opponent', 'rule')} fly, "
            f"env version {algo_cfg['trainedEnvVersion']}{', fires by the baseline rule' if aimer.fire == 'rule' else ''}), "
            f"fly {stimulus_label(cfg)}, seeds {seeds}"
        )

    env = EpisodeRecorder(FlyChaseEnv(cfg), meta=meta)
    run = None
    episodes = []
    for i in range(args.episodes):
        ep = play(env, aimer.player, args.seed + i)
        episodes.append(ep)
        s = ep["summary"]
        print(f"seed {args.seed + i}: captured={s['captured']} duration={s['duration']} visible={s['visibleRatio']}")
        if args.no_save:
            continue
        if run is None:  # after the first episode, so a fly that fails to load leaves no empty run
            run = RunStore(args.runs_dir).create_run(
                args.name or f"{stimulus_label(cfg)}-{aimer_name}", policy, "continuous",
                {"env": cfg.to_dict(), "algo": algo_cfg}, notes=notes,
            )
        run.save_episode(ep, tag)
    print(f"env version {ENV_VERSION}, {notes}")
    print(summarize(episodes))
    if run:
        print(f"saved: {run.dir}")


if __name__ == "__main__":
    main()
