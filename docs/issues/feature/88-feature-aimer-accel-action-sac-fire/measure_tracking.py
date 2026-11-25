"""#88. #85's measure_tracking.py with acceleration-control models supported (the only change: the policy's output is
converted to a rate command with wrappers.accel_to_rate before it is recorded as "act" and sent to the environment).

Runs one aimer for the full 10 s on each seed with the fire action held off, so no episode ends in a capture; analyze.py
applies the capture rule (15 consecutive physics steps inside the radius) to the recorded beam distance afterwards.

    uv run python docs/issues/feature/88-feature-aimer-accel-action-sac-fire/measure_tracking.py \
        <baseline | run folder> --name <name> --out runs/d88 [--stochastic] [--first-seed 20000] [--episodes 200]

출력: <out>/<이름>.npz. 배열은 [에피소드, step] 이고 step 은 행동 하나(0.02초)다. *_phys 는 물리 step(0.01초)이다.
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np

from flytracker.env import OBS, EnvConfig, FlyChaseEnv
from flytracker.players import baseline_player, load_opponent
from flytracker.wrappers import accel_to_rate


class TracedEnv(FlyChaseEnv):
    """물리 step 마다 보이는지와 빔까지 거리를 적는다."""

    def reset(self, **kwargs):
        self.trace: list[tuple[bool, float]] = []
        return super().reset(**kwargs)

    def _update_vision(self) -> None:
        super()._update_vision()
        self.trace.append((self._proj.visible, self._beam_dist))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("spec")
    p.add_argument("--name", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--stochastic", action="store_true", help="학습할 때처럼 행동을 분포에서 뽑는다")
    p.add_argument("--first-seed", type=int, default=20000)
    p.add_argument("--episodes", type=int, default=200)
    args = p.parse_args()

    cfg = EnvConfig()
    env = TracedEnv(cfg)
    tracker = baseline_player(cfg).policy  # 추적 행동의 기준. 탐색 상태는 쓰지 않는다 (track 은 상태가 없다)
    if args.spec == "baseline":
        rule, model, assist, shot_free = baseline_player(cfg).policy, None, 0.0, False
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            opp = load_opponent(args.spec, "aimer", cfg)
        rule, model, assist, shot_free = None, opp.player.policy, opp.player.assist, opp.player.rule_fire
        gain = opp.player.accel_gain  # None unless the model was trained with --control accel
        import torch

        torch.set_num_threads(1)
        if args.stochastic:
            model.set_random_seed(args.first_seed)

    steps = round(cfg.max_seconds / (cfg.dt * cfg.frame_skip))
    phys = steps * cfg.frame_skip
    n = args.episodes
    f32 = lambda *shape: np.full((n, *shape), np.nan, dtype=np.float32)  # noqa: E731
    out = {
        "vis": np.zeros((n, steps), bool),  # step 이 끝났을 때 보이는가
        "bd": f32(steps),  # m. 초파리 중심에서 빔까지
        "dist": f32(steps),  # m. 조준기에서 초파리까지
        "err": f32(steps, 2),  # m. 빔에서 본 초파리의 어긋남 (카메라 오른쪽, 위)
        "vel": f32(steps, 2),  # m/s. 초파리가 화면에서 움직이는 속도 (카메라 오른쪽, 위). 조준기가 돈 것은 빼지 않은 초파리 자체의 속도
        "act": f32(steps, 2),  # 환경에 들어간 행동 (yaw, pitch)
        "pol": f32(steps, 2),  # 정책이 낸 행동 (assist 를 더하기 전)
        "trk": f32(steps, 2),  # 같은 관측에서 기준선의 추적 행동. 행동을 낼 때 보였던 step 만
        "std": f32(steps, 2),  # 정책 분포의 표준편차 (tanh 앞). SAC 모델만
        "mean": f32(steps, 2),  # 정책 분포의 평균 (tanh 앞). SAC 모델만
        "fire_mean": f32(steps),  # mean of the fire action before tanh (fires when the action is above 0). Policy-fire models only
        "obs_rate": f32(steps, 2),  # 행동을 낼 때의 관측 target_rate (행동과 같은 눈금)
        "obs_fine": f32(steps, 2),  # 행동을 낼 때의 관측 uv_fine (±1 이 0.5°)
        "obs_vis": np.zeros((n, steps), bool),  # 행동을 낼 때 보였는가
        "alarmed": np.zeros((n, steps), bool),
        "vis_phys": np.zeros((n, phys), bool),
        "bd_phys": f32(phys),
    }

    for ep in range(n):
        obs, _ = env.reset(seed=args.first_seed + ep)
        if rule is not None:
            rule.reset()
        env.trace.clear()
        prev_pos = env.fly.pos.copy()
        for t in range(steps):
            seen = obs[OBS["visible"]][0] > 0.5
            out["obs_vis"][ep, t] = seen
            if seen:
                out["obs_rate"][ep, t], out["obs_fine"][ep, t] = obs[OBS["target_rate"]], obs[OBS["uv_fine"]]
                out["trk"][ep, t] = tracker.track(np.asarray(obs, dtype=float))[:2]
            if rule is not None:
                a = rule.act(obs)
                out["pol"][ep, t] = a[:2]
            else:
                x = np.delete(obs, np.arange(len(obs))[OBS["shot"]]) if shot_free else obs
                action, _ = model.predict(x, deterministic=not args.stochastic)
                pol = np.zeros(3)
                pol[: len(action)] = action
                out["pol"][ep, t] = pol[:2]
                if hasattr(model, "actor"):
                    import torch

                    with torch.no_grad():
                        mean, log_std, _ = model.actor.get_action_dist_params(torch.as_tensor(x[None]))
                    out["mean"][ep, t], out["std"][ep, t] = mean[0].numpy()[:2], log_std[0].exp().numpy()[:2]
                    out["fire_mean"][ep, t] = mean[0].numpy()[2] if mean.shape[1] > 2 else np.nan
                if gain is not None:
                    pol = accel_to_rate(obs, pol, gain)  # "act" below is the rate command the environment receives
                a = tracker.assisted(obs, pol, assist) if assist > 0 else pol
            a = np.asarray(a, dtype=float)
            a[2] = -1.0  # 쏘지 않는다
            out["act"][ep, t] = a[:2]
            obs, _, terminated, truncated, info = env.step(a)

            r, u, f = env.aimer.basis
            off = env.fly.pos - env.aimer.pos
            out["vis"][ep, t] = info["visible"]
            out["bd"][ep, t] = info["beam_dist"]
            out["dist"][ep, t] = info["distance"]
            out["err"][ep, t] = [off @ r, off @ u]
            v = (env.fly.pos - prev_pos) / (cfg.dt * cfg.frame_skip)
            prev_pos = env.fly.pos.copy()
            out["vel"][ep, t] = [v @ r, v @ u]
            out["alarmed"][ep, t] = info["fly_alarmed"]
            if terminated or truncated:
                break
        tr = env.trace
        out["vis_phys"][ep, : len(tr)] = [x[0] for x in tr]
        out["bd_phys"][ep, : len(tr)] = [x[1] for x in tr]
        if terminated:
            raise RuntimeError("captured although the fire action is held off")

    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(dest / f"{args.name}.npz", **out)
    meta = {"name": args.name, "spec": args.spec, "stochastic": args.stochastic, "firstSeed": args.first_seed,
            "episodes": n, "assist": assist, "stepSeconds": cfg.dt * cfg.frame_skip, "physSeconds": cfg.dt}
    (dest / f"{args.name}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    vis = out["vis"]
    print(f"{args.name}: visible {vis.mean():.3f}, median beam distance while visible {np.nanmedian(out['bd'][vis]) * 1000:.2f} mm")


if __name__ == "__main__":
    main()
