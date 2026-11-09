"""규칙 기반 조준기로 에피소드를 돌려 runs/ 에 저장한다.

예: python scripts/record_baseline.py --episodes 5
"""

from __future__ import annotations

import argparse

from _common import add_env_args, config_from_args, run_episode, summarize

from flytracker import EpisodeRecorder, RuleAimer, RunStore, make_env


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_env_args(p)
    p.add_argument("--episodes", type=int, default=5)
    p.add_argument("--seed", type=int, default=0, help="에피소드 i 는 seed + i 로 시작한다")
    p.add_argument("--name", default=None, help="실행 이름. 없으면 baseline")
    p.add_argument("--runs-dir", default="runs")
    p.add_argument("--no-save", action="store_true", help="저장하지 않고 요약만 출력한다")
    args = p.parse_args()

    cfg = config_from_args(args)
    policy = RuleAimer(max_pitch_deg=cfg.aimer.max_pitch_deg)
    env = EpisodeRecorder(make_env(cfg), meta={"policy": "rule-baseline"})
    run = None
    if not args.no_save:
        name = args.name or "baseline"
        run = RunStore(args.runs_dir).create_run(name, "rule-baseline", "continuous", {"env": cfg.to_dict(), "algo": {"name": "rule-baseline"}})

    episodes = []
    for i in range(args.episodes):
        ep = run_episode(env, policy, seed=args.seed + i)
        episodes.append(ep)
        if run:
            run.save_episode(ep, "baseline")
    print(summarize(episodes))
    if run:
        print(f"저장 위치: {run.dir}")


if __name__ == "__main__":
    main()
