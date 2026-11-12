"""Stable-Baselines3 로 조준기나 초파리를 학습하고, 일정 step 마다 평가 에피소드를 runs/ 에 저장한다.

예: python scripts/train.py --algo sac --steps 200000 --eval-every 20000
    python scripts/train.py --algo dqn --steps 200000
    python scripts/train.py --side fly --opponent runs/<조준기 실행 id> --algo sac

--side 는 학습할 쪽이고 기본은 조준기(aimer)다. --opponent 는 고정해 둘 상대다. 조준기 쪽 기본은 rule(규칙 초파리),
초파리 쪽 기본은 baseline(기준선)이다. 실행 폴더나 checkpoint 파일(.zip)을 주면 그 모델을 상대로 쓴다.
DQN 은 조준기 쪽에서만 쓰고 이산 행동 5개로 학습한다. 나머지는 연속 행동이다.
학습 곡선은 runs/<run_id>/tb 의 TensorBoard 기록으로 본다.
"""

from __future__ import annotations

import argparse
import importlib.util
from typing import Callable

import gymnasium as gym
from _common import add_env_args, config_from_args, run_episode, summarize
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor

from flytracker import EpisodeRecorder, RunStore, load_opponent, make_env, make_fly_env
from flytracker.players import RULE_SPECS, SIDES, algo_classes
from flytracker.record import Run

ALGOS = algo_classes()


class RecordEvalCallback(BaseCallback):
    """학습 시작, eval_every step 마다, 학습 끝에 평가 에피소드를 저장하고 모델을 체크포인트로 남긴다.

    평가 에피소드는 매번 같은 seed 로 시작한다. 그래서 체크포인트끼리 같은 상황에서 비교된다.
    """

    def __init__(self, run: Run, make_eval_env: Callable[[], gym.Env], meta: dict, every: int, episodes: int, seed: int):
        super().__init__()
        self.run, self.make_eval_env, self.meta = run, make_eval_env, meta
        self.every, self.episodes, self.seed = every, episodes, seed
        self._last = -1

    def _on_training_start(self) -> None:
        self._record()

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last >= self.every:
            self._record()
        return True

    def _on_training_end(self) -> None:
        if self._last != self.num_timesteps:
            self._record()

    def _record(self) -> None:
        step = self.num_timesteps
        self._last = step
        tag = f"step_{step:07d}"
        env = EpisodeRecorder(self.make_eval_env(), meta={**self.meta, "step": step})
        episodes = [run_episode(env, self.model, seed=self.seed + i) for i in range(self.episodes)]
        for ep in episodes:
            self.run.save_episode(ep, tag)
        caught = sum(e["summary"]["captured"] for e in episodes)
        self.logger.record("eval/capture_rate", caught / len(episodes))
        self.logger.record("eval/mean_return", sum(e["summary"]["return"] for e in episodes) / len(episodes))
        (self.run.dir / "checkpoints").mkdir(parents=True, exist_ok=True)
        self.model.save(self.run.dir / "checkpoints" / tag)
        print(f"[{tag}] {summarize(episodes)}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_env_args(p)
    p.add_argument("--side", choices=SIDES, default="aimer", help="학습할 쪽")
    p.add_argument(
        "--opponent",
        default=None,
        help="고정해 둘 상대. 조준기 쪽 기본 rule, 초파리 쪽 기본 baseline. 실행 폴더나 checkpoint(.zip) 경로도 된다",
    )
    p.add_argument("--algo", choices=sorted(ALGOS), default="sac")
    p.add_argument("--steps", type=int, default=200_000, help="총 학습 step 수")
    p.add_argument("--eval-every", type=int, default=20_000)
    p.add_argument("--eval-episodes", type=int, default=3)
    p.add_argument("--frame-stack", type=int, default=1)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--eval-seed", type=int, default=10_000)
    p.add_argument("--device", default="cpu", help="작은 MLP 는 대개 CPU 가 빠르다")
    p.add_argument("--name", default=None, help="실행 이름. 없으면 조준기 쪽은 <algo>, 초파리 쪽은 fly-<algo>")
    p.add_argument("--notes", default="")
    p.add_argument("--runs-dir", default="runs")
    args = p.parse_args()
    if args.side == "fly" and args.algo == "dqn":
        p.error("DQN 은 이산 행동이라 초파리 쪽에서는 쓸 수 없다")

    cfg = config_from_args(args)
    action_mode = "discrete" if args.algo == "dqn" else "continuous"
    other = "fly" if args.side == "aimer" else "aimer"
    spec = args.opponent or RULE_SPECS[other]
    # 학습 환경과 평가 환경이 상대의 상태(frame stack, 기준선의 탐색 상태)를 나누지 않게 따로 불러온다
    train_opponent = load_opponent(spec, other, cfg)
    eval_opponent = load_opponent(spec, other, cfg)

    def build_env(opponent) -> gym.Env:
        if args.side == "aimer":
            return make_env(cfg, action_mode, args.frame_stack, fly=opponent.player)
        return make_fly_env(cfg, aimer=opponent.player, frame_stack=args.frame_stack)

    name = args.name or (args.algo if args.side == "aimer" else f"fly-{args.algo}")
    algo_cfg = {
        "name": args.algo,
        "steps": args.steps,
        "seed": args.seed,
        "frameStack": args.frame_stack,
        "side": args.side,
        "opponent": train_opponent.label,
    }
    run = RunStore(args.runs_dir).create_run(name, args.algo, action_mode, {"env": cfg.to_dict(), "algo": algo_cfg}, notes=args.notes)

    env = Monitor(build_env(train_opponent))
    tb_dir = str(run.dir / "tb") if importlib.util.find_spec("tensorboard") else None
    model = ALGOS[args.algo]("MlpPolicy", env, seed=args.seed, device=args.device, tensorboard_log=tb_dir, verbose=0)
    meta = {"policy": args.algo, "side": args.side, "opponent": train_opponent.label}
    callback = RecordEvalCallback(
        run, lambda: build_env(eval_opponent), meta, args.eval_every, args.eval_episodes, args.eval_seed
    )
    model.learn(total_timesteps=args.steps, callback=callback, tb_log_name=args.algo)
    model.save(run.dir / "model")
    print(f"저장 위치: {run.dir}")


if __name__ == "__main__":
    main()
