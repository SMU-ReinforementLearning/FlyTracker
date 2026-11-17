"""Measure one aimer under the shot rule (env version 6): capture, time, shots and misfires per episode seed.

usage (from the repo root):
  uv run python docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/measure_aimers.py baseline --out <dir>
  uv run python docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/measure_aimers.py runs/<model run> --out <dir> --fly-model neural --no-stimulus --episodes 60
  uv run python docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/measure_aimers.py mean a/gate.csv b/gate.csv c/gate.csv --out pooled.csv

The aimer is `baseline` or a run folder holding `model.zip` and `config.json`, built by `load_opponent`. An aimer
model trained under env version 5 has no fire action: `load_opponent` gives it the baseline's firing rule
(`Opponent.fire == "rule"`), and its tracking assist if it was trained with one.

Writes into --out:
  episodes.csv  one row per seed
  shots.csv     one row per shot (the state at the trigger and how the shot ended)
  gate.csv      id, capture, time (10 s when not captured), misfires: the input of paired_bootstrap.py
  meta.json     command line, env version, git commit, aimer (label, trained env version, who fires, model sha256), env config
Columns are those of #69's data (docs/issues/feature/69-feature-aimer-fire-action-misfire/data/README.md) without the
trigger columns. The env and the aimers are deterministic for a seed on one machine.

`mean` averages gate.csv files seed by seed (a candidate's value per seed is the mean over its training seeds).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))

from _common import add_env_args, config_from_args  # noqa: E402

from flytracker import ENV_VERSION, load_opponent  # noqa: E402
from flytracker.env import OBS, FlyChaseEnv  # noqa: E402
from flytracker.players import baseline_player  # noqa: E402

EPISODE_COLUMNS = ["seed", "captured", "time_s", "steps", "shots", "misfires", "visible_ratio", "return",
                   "first_visible_s", "first_shot_s"]
SHOT_COLUMNS = ["seed", "shot", "t_start_s", "outcome", "t_off_s", "visible", "est_beam_mm", "true_beam_mm",
                "distance_m", "target_rate_yaw", "target_rate_pitch"]
GATE_COLUMNS = ["id", "capture", "time", "misfires"]


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _f(x, nd: int = 4):
    return "" if x is None else round(float(x), nd)


def run_episode(env: FlyChaseEnv, player, estimator, seed: int):
    """One episode. estimator is a RuleAimer used only to read the beam distance the firing rule sees."""
    player.reset()
    obs, info = env.reset(seed=seed)
    done, steps, visible_steps, ret = False, 0, 0, 0.0
    first_visible = first_shot = None
    shots: list[dict] = []
    while not done:
        a = player.act(obs)
        visible = bool(obs[OBS["visible"]][0] > 0.5)
        before = {
            "t_start_s": _f(info["t"]),
            "visible": int(visible),
            "est_beam_mm": _f(estimator.beam_distance(obs) * 1000) if visible else "",
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
            shots.append({"seed": seed, "shot": info["shots"], **before, "outcome": "unfinished", "t_off_s": ""})
        if info["misfires"] > n_miss:
            shots[-1].update(outcome="misfire", t_off_s=_f(info["t"]))  # end of the 20 ms step in which the beam left
    if info["captured"]:
        shots[-1]["outcome"] = "hit"
    episode = {
        "seed": seed, "captured": int(info["captured"]), "time_s": _f(info["t"]), "steps": steps,
        "shots": info["shots"], "misfires": info["misfires"], "visible_ratio": _f(visible_steps / steps),
        "return": _f(ret), "first_visible_s": _f(first_visible), "first_shot_s": _f(first_shot),
    }
    return episode, shots


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="\n", encoding="utf-8") as f:  # LF, so the sha256 in gate.md survives a checkout
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def mean_of(paths: list[str]) -> list[dict]:
    tables = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            tables.append({int(r["id"]): r for r in csv.DictReader(f)})
    ids = sorted(tables[0])
    if any(sorted(t) != ids for t in tables):
        raise SystemExit("files cover different ids")
    k = len(tables)
    return [{"id": i, **{c: round(sum(float(t[i][c]) for t in tables) / k, 6) for c in GATE_COLUMNS[1:]}} for i in ids]


def summary(rows: list[dict]) -> str:
    n = len(rows)
    return (f"n={n} capture={sum(float(r['capture']) for r in rows) / n:.4f} "
            f"mean_time={sum(float(r['time']) for r in rows) / n:.3f}s misfires/ep={sum(float(r['misfires']) for r in rows) / n:.3f}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("aimer", help="baseline, a run folder, or `mean`")
    p.add_argument("gate_files", nargs="*", help="mean: the gate.csv files to average")
    add_env_args(p)
    p.add_argument("--episodes", type=int, default=200)
    p.add_argument("--seed", type=int, default=20_000, help="episode i starts from seed + i")
    p.add_argument("--out", required=True, help="folder (or, for mean, the CSV to write)")
    args = p.parse_args()

    if args.aimer == "mean":
        rows = mean_of(args.gate_files)
        write_csv(Path(args.out), GATE_COLUMNS, rows)
        print(f"{args.out}: {summary(rows)}")
        return

    cfg = config_from_args(args)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # a model trained with another fly or reward differs from this config only there
        aimer = load_opponent(args.aimer, "aimer", cfg)
    estimator = baseline_player(cfg).policy
    env = FlyChaseEnv(cfg)
    episodes, shots = [], []
    for i in range(args.episodes):
        ep, ep_shots = run_episode(env, aimer.player, estimator, args.seed + i)
        episodes.append(ep)
        shots.extend(ep_shots)
    gate = [{"id": e["seed"], "capture": e["captured"], "time": e["time_s"] if e["captured"] else cfg.max_seconds,
             "misfires": e["misfires"]} for e in episodes]

    out = Path(args.out)
    write_csv(out / "episodes.csv", EPISODE_COLUMNS, episodes)
    write_csv(out / "shots.csv", SHOT_COLUMNS, shots)
    write_csv(out / "gate.csv", GATE_COLUMNS, gate)
    model = Path(args.aimer) / "model.zip"
    meta = {
        "envVersion": ENV_VERSION,
        "gitCommit": _git("rev-parse", "HEAD"),
        "gitDirty": bool(_git("status", "--porcelain", "--untracked-files=no")),
        "argv": sys.argv[1:],
        "seeds": [args.seed, args.seed + args.episodes - 1],
        "aimer": {
            "label": aimer.label,
            "trainedEnvVersion": aimer.env_version,
            "fire": "rule" if args.aimer == "baseline" else aimer.fire,
            "modelSha256": hashlib.sha256(model.read_bytes()).hexdigest() if model.is_file() else None,
        },
        "env": cfg.to_dict(),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    total = max(sum(e["shots"] for e in episodes), 1)
    print(f"env version {ENV_VERSION}, aimer {aimer.label} (fire: {meta['aimer']['fire']}), fly {cfg.fly_model}"
          f"{'' if cfg.fly_model != 'neural' else ' stimulus ' + ('on' if cfg.stimulus.enabled else 'off')}, "
          f"seeds {args.seed}-{args.seed + args.episodes - 1}")
    print(f"{summary(gate)} shots/ep={total / len(episodes):.2f} no-misfire eps={sum(e['misfires'] == 0 for e in episodes)}/{len(episodes)} -> {out}")


if __name__ == "__main__":
    main()
