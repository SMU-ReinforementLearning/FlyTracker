"""에피소드 기록과 실행 폴더 관리.

viewer 는 서버 없이 이 파일들만 읽는다.

runs/
  index.json                      실행 목록
  <run_id>/
    config.json                   환경 설정과 알고리즘 설정
    episodes.json                 이 실행의 에피소드 목록
    episodes/<tag>/ep_000.json    에피소드 하나
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

import gymnasium as gym

from .world import AXES, UNIT

EPISODE_FORMAT = "flytracker.episode/1"
INDEX_FORMAT = "flytracker.runs/1"

# 항목별 배열로 저장한다. 프레임마다 객체를 두는 것보다 파일이 작다.
FRAME_KEYS = ("t", "fly", "aimerC", "aimerLook", "visible", "uv", "angleErrDeg", "distance", "alarmed", "captureProgress")


def _round(v, nd: int = 4):
    if isinstance(v, float):
        return round(v, nd)
    if isinstance(v, list):
        return [_round(x, nd) for x in v]
    return v


def _write_json(path: Path, data) -> None:
    """임시 파일에 쓰고 바꿔치기한다. viewer 가 반쯤 쓴 파일을 읽지 않게 한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for attempt in range(10):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:  # Windows 에서 다른 프로세스가 읽는 중이면 잠깐 막힌다
            time.sleep(0.05 * (attempt + 1))
    os.replace(tmp, path)


def _read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


class EpisodeRecorder(gym.Wrapper):
    """에피소드를 프레임 단위로 모으고, 끝나면 `last_episode` 에 담아 콜백을 부른다.

    프레임은 agent step 마다 하나다. 포획으로 중간에 끝난 마지막 step 은 간격이 짧을 수 있어서
    viewer 는 frameDt 가 아니라 frames.t 로 시간을 맞춘다.
    """

    def __init__(self, env: gym.Env, meta: dict | None = None, on_episode: Callable[[dict], None] | None = None):
        super().__init__(env)
        self.extra_meta = meta or {}
        self.on_episode = on_episode
        self.last_episode: dict | None = None
        self._frames: dict[str, list] = {}
        self._rewards: list[float] = []
        self._seed: int | None = None

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        obs, info = self.env.reset(seed=seed, options=options)
        self._seed = seed
        self._frames = {k: [] for k in FRAME_KEYS}
        self._rewards = [0.0]
        self._append()
        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        self._rewards.append(float(reward))
        self._append()
        if terminated or truncated:
            self.last_episode = self._build()
            if self.on_episode:
                self.on_episode(self.last_episode)
        return obs, reward, terminated, truncated, info

    def _append(self) -> None:
        snap = self.env.unwrapped.snapshot()
        for k in FRAME_KEYS:
            self._frames[k].append(_round(snap[k]))

    def _build(self) -> dict:
        base = self.env.unwrapped
        cfg = base.config
        frames = dict(self._frames)
        frames["reward"] = _round(self._rewards)
        n = len(frames["t"])
        meta = {
            "room": [cfg.room.width, cfg.room.height, cfg.room.depth],
            "unit": UNIT,
            "axes": AXES,
            "frameDt": cfg.dt * cfg.frame_skip,
            "fovV": cfg.camera.fov_v_deg,
            "aspect": cfg.camera.aspect,
            "captureAngleDeg": cfg.capture_angle_deg,
            "captureRange": cfg.capture_range,
            "seed": self._seed,
            **self.extra_meta,
        }
        summary = {
            "frames": n,
            "duration": frames["t"][-1],
            "captured": bool(base.captured),
            "return": round(sum(self._rewards), 4),
            "visibleRatio": round(sum(frames["visible"]) / n, 4),
        }
        return {"format": EPISODE_FORMAT, "meta": meta, "summary": summary, "frames": frames}


def _slug(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z._-]+", "-", text).strip("-") or "run"


class Run:
    def __init__(self, store: "RunStore", run_id: str):
        self.store = store
        self.id = run_id
        self.dir = store.root / run_id

    def save_episode(self, episode: dict, tag: str) -> str:
        """에피소드를 저장하고 runs/ 기준 상대 경로를 돌려준다."""
        manifest_path = self.dir / "episodes.json"
        manifest = _read_json(manifest_path, {"run": self.id, "episodes": []})
        same_tag = [e for e in manifest["episodes"] if e["tag"] == tag]
        rel = f"{self.id}/episodes/{_slug(tag)}/ep_{len(same_tag):03d}.json"
        _write_json(self.store.root / rel, episode)
        manifest["episodes"].append({"tag": tag, "file": rel, "summary": episode["summary"]})
        _write_json(manifest_path, manifest)
        self.store._update_run(self.id, episodeCount=len(manifest["episodes"]))
        return rel


class RunStore:
    def __init__(self, root: str | os.PathLike = "runs"):
        self.root = Path(root)

    def create_run(self, name: str, algo: str, action_mode: str, config: dict, notes: str = "") -> Run:
        now = datetime.now()
        run_id = f"{now:%Y-%m-%d_%H%M%S}_{_slug(name)}"
        run = Run(self, run_id)
        _write_json(run.dir / "config.json", config)
        _write_json(run.dir / "episodes.json", {"run": run_id, "episodes": []})
        index = self._index()
        index["runs"].append(
            {
                "id": run_id,
                "name": name,
                "createdAt": now.isoformat(timespec="seconds"),
                "algo": algo,
                "actionMode": action_mode,
                "notes": notes,
                "episodeCount": 0,
            }
        )
        _write_json(self.root / "index.json", index)
        return run

    def _index(self) -> dict:
        return _read_json(self.root / "index.json", {"format": INDEX_FORMAT, "runs": []})

    def _update_run(self, run_id: str, **changes) -> None:
        index = self._index()
        for r in index["runs"]:
            if r["id"] == run_id:
                r.update(changes)
        _write_json(self.root / "index.json", index)
