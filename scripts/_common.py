"""스크립트들이 같이 쓰는 명령줄 옵션과 에피소드 실행 함수."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from flytracker import EnvConfig, EpisodeRecorder
from flytracker.camera import CameraIntrinsics

# Windows 콘솔이 cp949 여도 한국어 출력이 깨지지 않게 한다
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def add_env_args(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("환경")
    g.add_argument(
        "--turret-pos",
        type=float,
        nargs=3,
        metavar=("X", "Y", "Z"),
        default=EnvConfig.turret_pos,
        help="조준기 자리 (m). 기본은 +z 벽 앞 가운데, 높이 1.2",
    )
    g.add_argument("--fov", type=float, default=CameraIntrinsics.fov_v_deg, help="세로 시야각 (도)")
    g.add_argument(
        "--capture-range",
        type=float,
        default=None,
        help="포획 거리 (m). 없으면 거리 조건 없음",
    )
    g.add_argument("--max-seconds", type=float, default=EnvConfig.max_seconds)
    g.add_argument("--start-facing-fly", action="store_true", help="시작할 때 파리를 바라보게 한다. 없으면 방 가운데를 본다")


def config_from_args(args: argparse.Namespace) -> EnvConfig:
    return replace(
        EnvConfig(),
        turret_pos=tuple(args.turret_pos),
        capture_range=args.capture_range,
        camera=CameraIntrinsics(fov_v_deg=args.fov),
        max_seconds=args.max_seconds,
        start_facing_fly=args.start_facing_fly,
    )


def run_episode(env: EpisodeRecorder, policy, seed: int) -> dict:
    """policy 는 predict(obs, deterministic=True) 를 가진 객체 (SB3 모델 또는 RuleAimer)."""
    obs, _ = env.reset(seed=seed)
    done = False
    while not done:
        action, _ = policy.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
    return env.last_episode


def summarize(episodes: list[dict]) -> str:
    n = len(episodes)
    caught = [e for e in episodes if e["summary"]["captured"]]
    mean_ret = sum(e["summary"]["return"] for e in episodes) / n
    mean_vis = sum(e["summary"]["visibleRatio"] for e in episodes) / n
    text = f"포획 {len(caught)}/{n}, 평균 보상 {mean_ret:.2f}, 보인 비율 {mean_vis:.0%}"
    if caught:
        text += f", 포획까지 평균 {sum(e['summary']['duration'] for e in caught) / len(caught):.2f}초"
    return text
