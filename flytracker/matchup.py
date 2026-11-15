"""조준기 버전과 초파리 버전을 맞붙여 대전표를 만든다. scripts/match.py 가 쓴다.

칸 하나는 조준기 하나와 초파리 하나를 같은 seed 목록으로 맞붙인 결과다. 포획률과 포획까지 평균 시간을 적는다.
seed 가 같으면 시작 위치는 같다. 학습한 초파리는 조준선을 보고 피하므로 경로는 조준기마다 달라질 수 있다.
"""

from __future__ import annotations

from dataclasses import dataclass

from .env import EnvConfig, FlyChaseEnv
from .players import Opponent


@dataclass
class Cell:
    episodes: int
    captured: int
    capture_times: list[float]

    @property
    def capture_rate(self) -> float:
        return self.captured / self.episodes

    @property
    def mean_capture_time(self) -> float | None:
        return sum(self.capture_times) / len(self.capture_times) if self.capture_times else None

    def text(self) -> str:
        t = self.mean_capture_time
        return f"{self.captured}/{self.episodes}, " + (f"{t:.2f}초" if t is not None else "-")

    def to_dict(self) -> dict:
        return {"episodes": self.episodes, "captured": self.captured, "meanCaptureTime": self.mean_capture_time}


def play_cell(config: EnvConfig, aimer: Opponent, fly: Opponent, seeds: range) -> Cell:
    """aimer 와 fly 를 seeds 의 seed 마다 한 번씩 맞붙인다."""
    env = FlyChaseEnv(config, fly=fly.player)
    captured, times = 0, []
    for seed in seeds:
        obs, _ = env.reset(seed=seed)
        aimer.player.reset()
        done = False
        while not done:
            obs, _, terminated, truncated, info = env.step(aimer.player.act(obs))
            done = terminated or truncated
        if info["captured"]:
            captured += 1
            times.append(info["t"])
    return Cell(len(seeds), captured, times)


def play_table(config: EnvConfig, aimers: list[Opponent], flies: list[Opponent], seeds: range) -> list[list[Cell]]:
    """행은 조준기, 열은 초파리다."""
    return [[play_cell(config, a, f, seeds) for f in flies] for a in aimers]


def format_table(aimers: list[Opponent], flies: list[Opponent], cells: list[list[Cell]]) -> str:
    """Markdown 표. 칸은 "포획 수/에피소드 수, 포획까지 평균 시간" 이다."""
    lines = ["| 조준기 \\ 초파리 | " + " | ".join(f.label for f in flies) + " |", "|---" * (len(flies) + 1) + "|"]
    for a, row in zip(aimers, cells):
        lines.append(f"| {a.label} | " + " | ".join(c.text() for c in row) + " |")
    return "\n".join(lines)
