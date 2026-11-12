"""에피소드 기록과 실행 폴더 관리.

viewer 는 서버 없이 이 파일들만 읽는다.

runs/
  index.json                      실행 목록
  <run_id>/
    config.json                   환경 설정과 알고리즘 설정
    episodes.json                 이 실행의 에피소드 목록
    episodes/<tag>/ep_000.json    에피소드 하나

runs/ 는 git 에 올리지 않는다. 저장소에 올릴 실행은 `publish_run()` 으로 published/ 에 복사한다.
published/ 는 runs/ 와 구조가 같고, index.json 대신 실행마다 run.json(실행 목록의 한 줄)을 둔다.
run.json 에는 목록의 한 줄에 더해 실행이 속한 issue(number, title, url)와 올린 사람(author)이 들어간다.
여러 사람이 각자 실행을 올려도 한 파일을 함께 고치지 않게 하려는 것이다. 목록은 viewer 가 build 할 때 만든다.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

import gymnasium as gym

from .world import AXES, UNIT

EPISODE_FORMAT = "flytracker.episode/1"
INDEX_FORMAT = "flytracker.runs/1"

# 항목별 배열로 저장한다. 프레임마다 객체를 두는 것보다 파일이 작다.
FRAME_KEYS = ("t", "fly", "flyHeading", "aimerC", "aimerLook", "visible", "uv", "angleErrDeg", "distance", "alarmed", "captureProgress")


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
        base = self.env.unwrapped
        if not base.config.capture_enabled:
            self._frames.setdefault("flySpeed", []).append(_round(float(base.fly.speed)))
        if hasattr(base, "observation_aim_on"):
            self._frames.setdefault("aimCommanded", []).append(bool(base.observation_aim_on))
        if base.config.fly_model == "neural":
            self._frames.setdefault("neuralPhase", []).append(base.fly.sim.motor.phase)
            self._frames.setdefault("neuralDiagnostics", []).append(base.fly.diagnostics())

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
            **base.recording_metadata(),
        }
        summary = {
            "frames": n,
            "duration": frames["t"][-1],
            "captured": bool(base.captured),
            "return": round(sum(self._rewards), 4),
            "visibleRatio": round(sum(frames["visible"]) / n, 4),
        }
        if not cfg.capture_enabled:
            summary.update(mode="tracking-observation", result="observation_complete")
        episode = {"format": EPISODE_FORMAT, "meta": meta, "summary": summary, "frames": frames}
        diagnostics = base.recording_diagnostics()
        if diagnostics:
            episode["diagnostics"] = diagnostics
        return episode


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


def publish_run(
    runs_root: str | os.PathLike,
    run_id: str,
    dest_root: str | os.PathLike,
    overwrite: bool = False,
    extra: dict | None = None,
) -> list[Path]:
    """실행 하나의 JSON 을 dest_root/<run_id>/ 로 복사하고, 쓴 파일 목록을 돌려준다.

    config.json, episodes.json, episodes.json 에 적힌 에피소드 파일, 그리고 runs/index.json 에서 꺼낸
    이 실행의 한 줄(run.json)만 쓴다. 모델 파일과 TensorBoard 기록은 복사하지 않는다.
    extra 는 run.json 에 더 적을 값이다. scripts/publish_run.py 가 issue 와 올린 사람을 넘긴다.
    원본을 모두 확인한 뒤 임시 폴더에 쓰고 바꿔치기하므로, 중간에 실패해도 반쯤 복사된 폴더가 남지 않는다.
    """
    runs_root, dest_root = Path(runs_root), Path(dest_root)
    src = runs_root / run_id
    entry = next((r for r in _read_json(runs_root / "index.json", {"runs": []})["runs"] if r["id"] == run_id), None)
    if entry is None:
        raise FileNotFoundError(f"{runs_root / 'index.json'} 에 실행 {run_id} 가 없다")
    manifest = _read_json(src / "episodes.json", None)
    if manifest is None:
        raise FileNotFoundError(f"{src / 'episodes.json'} 가 없다")

    prefix = f"{run_id}/"
    rels = ["config.json", "episodes.json"]
    for ep in manifest["episodes"]:
        if not ep["file"].startswith(prefix) or ".." in ep["file"].split("/"):
            raise ValueError(f"에피소드 경로 {ep['file']} 가 실행 폴더 밖을 가리킨다")
        rels.append(ep["file"][len(prefix) :])
    missing = [r for r in rels if not (src / r).is_file()]
    if missing:
        raise FileNotFoundError(f"{src} 에 없는 파일: {', '.join(missing)}")

    dest = dest_root / run_id
    if dest.exists() and not overwrite:
        raise FileExistsError(f"{dest} 가 이미 있다. 덮어쓰려면 overwrite 를 켠다")
    tmp = dest_root / f".{run_id}.tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    for rel in rels:
        (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / rel, tmp / rel)
    _write_json(tmp / "run.json", {**entry, **(extra or {}), "episodeCount": len(manifest["episodes"])})
    if dest.exists():
        shutil.rmtree(dest)
    os.replace(tmp, dest)
    return [dest / r for r in (*rels, "run.json")]
