"""스크립트들이 같이 쓰는 명령줄 옵션과 에피소드 실행 함수."""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from flytracker import EnvConfig, EpisodeRecorder
from flytracker.camera import CameraIntrinsics
from flytracker.neural_fly import NeuralConfig
from flytracker.stimulus import StimulusConfig

# Windows 콘솔이 cp949 여도 한국어 출력이 깨지지 않게 한다
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def add_env_args(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("환경")
    g.add_argument("--fly-model", choices=("rule", "neural"), default="rule")
    g.add_argument("--neural-source", default=None, help="로컬 flysim 프로젝트 경로. 지정한 Python 코드를 실행하며 FLYTRACKER_NEURAL_SOURCE도 사용할 수 있습니다.")
    g.add_argument("--neural-data", default=None, help="neurons.csv와 edges.csv가 있는 로컬 폴더")
    g.add_argument("--no-stimulus", action="store_true", help="신경 비행의 가상 자극 끄기")
    for name in ("align_deg", "charge_ms", "discharge_ms", "pulse_ms", "cooldown_ms", "max_events",
                 "min_radius_m", "max_radius_m", "contrast"):
        default = getattr(StimulusConfig(), name)
        g.add_argument("--stimulus-" + name.replace("_", "-"), type=type(default), default=default)
    g.add_argument(
        "--turret-pos",
        type=float,
        nargs=3,
        metavar=("X", "Y", "Z"),
        default=EnvConfig.turret_pos,
        help="조준기 자리 (m). 기본은 바닥 정가운데, 회전축 높이 0.1",
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
        fly_model=args.fly_model,
        neural=NeuralConfig(source_root=args.neural_source, data_dir=args.neural_data),
        stimulus=StimulusConfig(enabled=not args.no_stimulus, **{
            name: getattr(args, "stimulus_" + name) for name in (
                "align_deg", "charge_ms", "discharge_ms", "pulse_ms", "cooldown_ms", "max_events",
                "min_radius_m", "max_radius_m", "contrast")}),
    )


def run_episode(env: EpisodeRecorder, policy, seed: int) -> dict:
    """policy 는 predict(obs, deterministic=True) 를 가진 객체 (SB3 모델 또는 RuleAimer)."""
    if hasattr(policy, "reset"):  # RuleAimer 는 탐색 상태를 에피소드마다 지운다
        policy.reset()
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
