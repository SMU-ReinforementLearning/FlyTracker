"""Stable-Baselines3 로 조준기를 학습하고, 일정 step 마다 평가 에피소드를 runs/ 에 저장한다.

예: python scripts/train.py --algo sac --steps 200000 --eval-every 20000
    python scripts/train.py --algo dqn --steps 200000

DQN 은 이산 행동 5개, 나머지는 연속 행동 2차원으로 학습한다.
학습 곡선은 runs/<run_id>/tb 의 TensorBoard 기록으로 본다.
"""

from __future__ import annotations

import argparse
import importlib.util

from _common import add_env_args, config_from_args, run_episode, summarize
from stable_baselines3 import DQN, PPO, SAC, TD3
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor

from flytracker import EnvConfig, EpisodeRecorder, RunStore, make_env
from flytracker.record import Run

ALGOS = {"sac": SAC, "td3": TD3, "ppo": PPO, "dqn": DQN}


class RecordEvalCallback(BaseCallback):
    """학습 시작, eval_every step 마다, 학습 끝에 평가 에피소드를 저장하고 모델을 체크포인트로 남긴다.

    평가 에피소드는 매번 같은 seed 로 시작한다. 시선 연동 자극에서는 정책에 따라 비행 경로가 달라진다.
    """

    def __init__(self, run: Run, cfg: EnvConfig, action_mode: str, frame_stack: int, every: int, episodes: int, seed: int, algo: str):
        super().__init__()
        self.run, self.cfg, self.action_mode, self.frame_stack = run, cfg, action_mode, frame_stack
        self.every, self.episodes, self.seed, self.algo = every, episodes, seed, algo
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
        env = EpisodeRecorder(
            make_env(self.cfg, self.action_mode, self.frame_stack),
            meta={"policy": self.algo, "step": step},
        )
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
    p.add_argument("--algo", choices=sorted(ALGOS), default="sac")
    p.add_argument("--steps", type=int, default=200_000, help="총 학습 step 수")
    p.add_argument("--eval-every", type=int, default=20_000)
    p.add_argument("--eval-episodes", type=int, default=3)
    p.add_argument("--frame-stack", type=int, default=1)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--eval-seed", type=int, default=10_000)
    p.add_argument("--device", default="cpu", help="작은 MLP 는 대개 CPU 가 빠르다")
    p.add_argument("--name", default=None, help="실행 이름. 없으면 <algo>")
    p.add_argument("--notes", default="")
    p.add_argument("--runs-dir", default="runs")
    args = p.parse_args()

    cfg = config_from_args(args)
    action_mode = "discrete" if args.algo == "dqn" else "continuous"
    name = args.name or args.algo
    algo_cfg = {"name": args.algo, "steps": args.steps, "seed": args.seed, "frameStack": args.frame_stack}
    run = RunStore(args.runs_dir).create_run(name, args.algo, action_mode, {"env": cfg.to_dict(), "algo": algo_cfg}, notes=args.notes)

    env = Monitor(make_env(cfg, action_mode, args.frame_stack))
    tb_dir = str(run.dir / "tb") if importlib.util.find_spec("tensorboard") else None
    model = ALGOS[args.algo]("MlpPolicy", env, seed=args.seed, device=args.device, tensorboard_log=tb_dir, verbose=0)
    callback = RecordEvalCallback(run, cfg, action_mode, args.frame_stack, args.eval_every, args.eval_episodes, args.eval_seed, args.algo)
    model.learn(total_timesteps=args.steps, callback=callback, tb_log_name=args.algo)
    model.save(run.dir / "model")
    print(f"저장 위치: {run.dir}")


if __name__ == "__main__":
    main()
