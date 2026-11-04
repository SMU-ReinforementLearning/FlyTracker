"""방 공간과 좌표 규약.

좌표 규약은 RackTracker 리그 규약과 같다. x 오른쪽, y 위, z 정면, 오른손 좌표다.
단위는 m 이고 원점은 바닥 중심이다. three.js 도 y 위 오른손 좌표라서 viewer 에 값을 그대로 넘긴다.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

AXES = "x right, y up, z front (right-handed)"
UNIT = "m"
UP = np.array([0.0, 1.0, 0.0])


@dataclass(frozen=True)
class Room:
    """바닥 중심이 원점인 직육면체 방."""

    width: float = 4.0  # x 방향 (m)
    height: float = 2.5  # y 방향 (m)
    depth: float = 3.0  # z 방향 (m)

    @property
    def lo(self) -> np.ndarray:
        return np.array([-self.width / 2, 0.0, -self.depth / 2])

    @property
    def hi(self) -> np.ndarray:
        return np.array([self.width / 2, self.height, self.depth / 2])

    @property
    def size(self) -> np.ndarray:
        return np.array([self.width, self.height, self.depth])

    @property
    def center(self) -> np.ndarray:
        return (self.lo + self.hi) / 2

    @property
    def diagonal(self) -> float:
        return float(np.linalg.norm(self.size))

    def contains(self, p: np.ndarray, margin: float = 0.0) -> bool:
        return bool(np.all(p >= self.lo + margin) and np.all(p <= self.hi - margin))

    def clamp(self, p: np.ndarray, margin: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
        """방 안으로 잘라낸 점과, 벽에 닿은 축을 표시한 bool 배열을 돌려준다."""
        lo, hi = self.lo + margin, self.hi - margin
        clamped = np.clip(p, lo, hi)
        return clamped, clamped != p

    def normalize(self, p: np.ndarray) -> np.ndarray:
        """방 안의 점을 축마다 −1~1 로 바꾼다."""
        return (p - self.center) / (self.size / 2)

    def sample(self, rng: np.random.Generator, margin: float = 0.0) -> np.ndarray:
        return rng.uniform(self.lo + margin, self.hi - margin)
