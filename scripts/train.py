"""Stable-Baselines3 로 조준기나 초파리를 학습하고, 일정 step 마다 평가 에피소드를 runs/ 에 저장한다.

예: python scripts/train.py --algo sac --steps 200000 --eval-every 20000
    python scripts/train.py --algo dqn --steps 200000
    python scripts/train.py --side fly --opponent runs/<조준기 실행 id> --algo sac

--side 는 학습할 쪽이고 기본은 조준기(aimer)다. --opponent 는 고정해 둘 상대다. 조준기 쪽 기본은 rule(규칙 초파리),
초파리 쪽 기본은 baseline(기준선)이다. 실행 폴더나 checkpoint 파일(.zip)을 주면 그 모델을 상대로 쓴다.
DQN 은 조준기 쪽에서만 쓰고 이산 행동 6개로 학습한다. 나머지는 연속 행동이다.
학습 곡선은 runs/<run_id>/tb 의 TensorBoard 기록으로 본다.
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
from pathlib import Path
from typing import Callable

import gymnasium as gym
from _common import add_env_args, config_from_args, run_episode, summarize
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor

from flytracker import EpisodeRecorder, RunStore, load_opponent, make_env, make_fly_env
from flytracker.players import RULE_SPECS, SIDES, algo_classes
from flytracker.record import Run
from flytracker.wrappers import CONTROLS, FIRE_PRIORS, FIRES

ALGOS = algo_classes()


class RecordEvalCallback(BaseCallback):
    """학습 시작, eval_every step 마다, 학습 끝에 평가 에피소드를 저장하고 모델을 체크포인트로 남긴다.

    평가 에피소드는 매번 같은 seed 로 시작한다. 시선 연동 자극에서는 정책에 따라 비행 경로가 달라진다.
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
    p.add_argument(
        "--assist",
        type=float,
        default=0.0,
        help="0 보다 크면 조준기 정책의 행동에 기준선의 추적을 더한다. 보이는 동안 환경에 들어가는 행동은 "
        "추적 행동 + 이 값 × 정책 행동이다. 조준기 쪽 연속 행동에서만 쓴다",
    )
    p.add_argument(
        "--control",
        choices=CONTROLS,
        default="rate",
        help="조준기 정책의 돌리는 행동이 뜻하는 것. rate 는 각속도, accel 은 각가속도(행동 0 이면 지금 속도로 계속 돈다). "
        "조준기 쪽 연속 행동에서만 쓴다",
    )
    p.add_argument(
        "--fire",
        choices=FIRES,
        default="policy",
        help="쏠지를 누가 정하나. policy 는 정책, rule 은 기준선의 규칙(정책은 돌리는 두 값만 낸다). 조준기 쪽 연속 행동에서만 쓴다",
    )
    p.add_argument(
        "--aim",
        default=None,
        help="조준을 맡길 조준기 실행 폴더(쏘는 것을 규칙에 맡긴 모델). 주면 조준은 그 모델이 하고 정책은 쏠지만 학습한다. "
        "조준 모델은 새 실행 폴더의 aim/ 에 복사한다",
    )
    p.add_argument(
        "--fire-prior",
        choices=FIRE_PRIORS,
        default="none",
        help="--aim 과 함께 쓴다. rule 이면 정책의 값에 규칙의 판단을 ±0.5 로 더해서, 값이 0 일 때 규칙과 똑같이 쏜다",
    )
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
    if args.assist > 0 and (args.side != "aimer" or action_mode != "continuous"):
        p.error("--assist 는 조준기 쪽 연속 행동에서만 쓴다")
    if (args.control != "rate" or args.fire != "policy") and (args.side != "aimer" or action_mode != "continuous"):
        p.error("--control accel 과 --fire rule 은 조준기 쪽 연속 행동에서만 쓴다")
    if args.aim and (args.side != "aimer" or action_mode != "continuous" or args.assist > 0 or args.control != "rate" or args.fire != "policy"):
        p.error("--aim 은 조준기 쪽 연속 행동에서, --assist, --control, --fire 없이 쓴다")
    if args.fire_prior != "none" and not args.aim:
        p.error("--fire-prior 는 --aim 과 함께 쓴다")
    # 학습 환경과 평가 환경이 조준 모델의 상태를 나누지 않게 따로 불러온다
    aims = [load_opponent(args.aim, "aimer", cfg) for _ in range(2)] if args.aim else [None, None]
    if args.aim and aims[0].fire != "rule":
        p.error("--aim 은 쏘는 것을 규칙에 맡긴 조준기 모델이어야 한다")
    other = "fly" if args.side == "aimer" else "aimer"
    spec = args.opponent or RULE_SPECS[other]
    # 학습 환경과 평가 환경이 상대의 상태(frame stack, 기준선의 탐색 상태)를 나누지 않게 따로 불러온다
    train_opponent = load_opponent(spec, other, cfg)
    eval_opponent = load_opponent(spec, other, cfg)

    def build_env(opponent, aim=None) -> gym.Env:
        if args.side == "aimer":
            return make_env(cfg, action_mode, args.frame_stack, fly=opponent.player, assist=args.assist,
                            control=args.control, fire=args.fire, aim=aim.player if aim else None, fire_prior=args.fire_prior)
        return make_fly_env(cfg, aimer=opponent.player, frame_stack=args.frame_stack)

    name = args.name or (args.algo if args.side == "aimer" else f"fly-{args.algo}")
    algo_cfg = {
        "name": args.algo,
        "steps": args.steps,
        "seed": args.seed,
        "frameStack": args.frame_stack,
        "assist": args.assist,
        "control": args.control,
        "fire": args.fire,
        "side": args.side,
        "opponent": train_opponent.label,
    }
    if args.aim:
        algo_cfg.update(aim=aims[0].label, firePrior=args.fire_prior)
    run = RunStore(args.runs_dir).create_run(name, args.algo, action_mode, {"env": cfg.to_dict(), "algo": algo_cfg}, notes=args.notes)
    if args.aim:  # 실행 폴더만으로 모델을 다시 쓸 수 있게 조준 모델을 함께 둔다
        src = Path(args.aim)
        (run.dir / "aim").mkdir()
        for f in ("model.zip", "config.json"):
            shutil.copy2(src / f, run.dir / "aim" / f)

    env = Monitor(build_env(train_opponent, aims[0]))
    tb_dir = str(run.dir / "tb") if importlib.util.find_spec("tensorboard") else None
    model = ALGOS[args.algo]("MlpPolicy", env, seed=args.seed, device=args.device, tensorboard_log=tb_dir, verbose=0)
    meta = {"policy": args.algo, "side": args.side, "opponent": train_opponent.label}
    callback = RecordEvalCallback(
        run, lambda: build_env(eval_opponent, aims[1]), meta, args.eval_every, args.eval_episodes, args.eval_seed
    )
    model.learn(total_timesteps=args.steps, callback=callback, tb_log_name=args.algo)
    model.save(run.dir / "model")
    print(f"저장 위치: {run.dir}")


if __name__ == "__main__":
    main()
