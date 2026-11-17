"""Measure the rule baseline under the shot rule: capture time, shots and misfires over a seed range.

usage (from the repo root):
  uv run python docs/issues/feature/69-feature-aimer-fire-action-misfire/measure_fire.py
  uv run python docs/issues/feature/69-feature-aimer-fire-action-misfire/measure_fire.py --fire-radius-mm 0.6 1.25 2.5 --fly-model neural --episodes 20
  uv run python docs/issues/feature/69-feature-aimer-fire-action-misfire/measure_fire.py --out docs/issues/feature/69-feature-aimer-fire-action-misfire/data/rule-fly

`--fire-radius-mm` is the baseline's trigger: it fires when the beam looks closer to the fly than this.
`always` holds the trigger down (a new shot the moment the last one ends), which is the closest the shot rule
gets to the laser that was always on before env version 6.
A missed episode counts as the time limit in the mean time.

`--out DIR` also writes the raw rows (see data/README.md next to this script for the columns):
  DIR/episodes.csv  one row per trigger and seed
  DIR/shots.csv     one row per shot
  DIR/meta.json     command line, env version, git commit, env config
The env and the baseline are deterministic for a seed, so the same commit and command give the same rows.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))

from _common import add_env_args, config_from_args  # noqa: E402

from flytracker import ENV_VERSION  # noqa: E402
from flytracker.env import OBS, FlyChaseEnv  # noqa: E402
from flytracker.players import baseline_player  # noqa: E402

EPISODE_COLUMNS = ["trigger", "fire_radius_mm", "seed", "captured", "time_s", "steps", "shots", "misfires",
                   "visible_ratio", "return", "first_visible_s", "first_shot_s"]
SHOT_COLUMNS = ["trigger", "fire_radius_mm", "seed", "shot", "t_start_s", "outcome", "t_off_s", "visible",
                "est_beam_mm", "true_beam_mm", "distance_m", "target_rate_yaw", "target_rate_pitch"]


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _f(x: float, nd: int = 4):
    return "" if x is None else round(float(x), nd)


def run_episode(env: FlyChaseEnv, player, cfg, seed: int, always: bool):
    """One episode. Returns (episode row values, list of shot rows) without the trigger columns."""
    player.reset()
    obs, info = env.reset(seed=seed)
    done, steps, visible_steps, ret = False, 0, 0, 0.0
    first_visible = first_shot = None
    shots: list[dict] = []
    while not done:
        a = player.act(obs)
        if always:
            a[2] = 1.0
        # the state the trigger was pulled in: the observation the aimer acted on, and the truth behind it
        visible = bool(obs[OBS["visible"]][0] > 0.5)
        before = {
            "t_start_s": _f(info["t"]),
            "visible": int(visible),
            "est_beam_mm": _f(player.policy.beam_distance(obs) * 1000) if visible else "",
            "true_beam_mm": _f(info["beam_dist"] * 1000),
            "distance_m": _f(info["distance"]),
            "target_rate_yaw": _f(obs[OBS["target_rate"]][0]),
            "target_rate_pitch": _f(obs[OBS["target_rate"]][1]),
        }
        n_shots, n_miss = info["shots"], info["misfires"]
        obs, r, terminated, truncated, info = env.step(a)
        done = terminated or truncated
        steps += 1
        ret += float(r)
        visible_steps += int(info["visible"])
        if first_visible is None and info["visible"]:
            first_visible = info["t"]
        if info["shots"] > n_shots:
            if first_shot is None:
                first_shot = before["t_start_s"]
            shots.append({"shot": info["shots"], **before, "outcome": "unfinished", "t_off_s": ""})
        if info["misfires"] > n_miss:
            # seen at the end of the action step (20 ms) in which the beam first left the fly
            shots[-1].update(outcome="misfire", t_off_s=_f(info["t"]))
    if info["captured"]:
        shots[-1]["outcome"] = "hit"
    episode = {
        "seed": seed,
        "captured": int(info["captured"]),
        "time_s": _f(info["t"]),
        "steps": steps,
        "shots": info["shots"],
        "misfires": info["misfires"],
        "visible_ratio": _f(visible_steps / steps),
        "return": _f(ret),
        "first_visible_s": _f(first_visible),
        "first_shot_s": _f(first_shot),
    }
    return episode, shots


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_env_args(p)
    p.add_argument("--fire-radius-mm", nargs="+", default=["always", "1.25"], help="trigger radii in mm, or `always`")
    p.add_argument("--episodes", type=int, default=200)
    p.add_argument("--seed", type=int, default=20_000, help="episode i starts from seed + i")
    p.add_argument("--out", default=None, help="folder for episodes.csv, shots.csv and meta.json")
    args = p.parse_args()

    cfg = config_from_args(args)
    env = FlyChaseEnv(cfg)
    episode_rows, shot_rows = [], []
    print(f"env version {ENV_VERSION}, fly {cfg.fly_model}, seeds {args.seed}-{args.seed + args.episodes - 1}, limit {cfg.max_seconds:g} s")
    print("trigger   captured  mean time  shots/ep  misfires/ep  no-misfire eps  hit rate")
    for spec in args.fire_radius_mm:
        player = baseline_player(cfg)
        always = spec == "always"
        if not always:
            player.policy.fire_radius = float(spec) / 1000
        label = "always" if always else f"{float(spec):g} mm"
        tag = {"trigger": "always" if always else "radius", "fire_radius_mm": "" if always else float(spec)}
        times, shots, misfires, captured = [], [], [], 0
        for i in range(args.episodes):
            ep, ep_shots = run_episode(env, player, cfg, args.seed + i, always)
            episode_rows.append({**tag, **ep})
            shot_rows.extend({**tag, "seed": ep["seed"], **s} for s in ep_shots)
            captured += ep["captured"]
            times.append(ep["time_s"] if ep["captured"] else cfg.max_seconds)
            shots.append(ep["shots"])
            misfires.append(ep["misfires"])
        total = max(sum(shots), 1)
        print(
            f"{label:8s}  {captured:3d}/{args.episodes}  {np.mean(times):8.3f}s  {np.mean(shots):8.2f}  {np.mean(misfires):11.2f}"
            f"  {sum(m == 0 for m in misfires):8d}/{args.episodes}  {1 - sum(misfires) / total:8.3f}"
        )

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for name, columns, rows in (("episodes.csv", EPISODE_COLUMNS, episode_rows), ("shots.csv", SHOT_COLUMNS, shot_rows)):
            with open(out / name, "w", newline="\n", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
        meta = {
            "envVersion": ENV_VERSION,
            "gitCommit": _git("rev-parse", "HEAD"),
            "gitDirty": bool(_git("status", "--porcelain", "--untracked-files=no")),
            "argv": sys.argv[1:],
            "seeds": [args.seed, args.seed + args.episodes - 1],
            "triggers": args.fire_radius_mm,
            "policy": "rule-baseline (flytracker.players.baseline_player)",
            "env": cfg.to_dict(),
        }
        (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {out / 'episodes.csv'} ({len(episode_rows)} rows), {out / 'shots.csv'} ({len(shot_rows)} rows), {out / 'meta.json'}")


if __name__ == "__main__":
    main()
