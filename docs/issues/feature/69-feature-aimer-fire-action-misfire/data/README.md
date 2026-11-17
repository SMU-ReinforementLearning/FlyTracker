# Raw rows of the #69 baseline measurement

What the rule baseline does under the shot rule (env version 6), one row per episode and one row per shot.
Written by `../measure_fire.py --out <folder>`. The env and the baseline are deterministic for a seed, so the
command in each `meta.json` (`argv`), run at its `gitCommit`, writes the same rows again.

| Folder | Fly | Seeds | Triggers | Command |
|---|---|---|---|---|
| `rule-fly/` | rule fly | 20000-20199 | always, 2.5, 1.25, 0.9, 0.6, 0.3 mm | `uv run python docs/issues/feature/69-feature-aimer-fire-action-misfire/measure_fire.py --fire-radius-mm always 2.5 1.25 0.9 0.6 0.3 --out docs/issues/feature/69-feature-aimer-fire-action-misfire/data/rule-fly` |
| `neural-fly-nostim/` | neural fly, aim stimulus off | 20000-20019 | always, 1.25 mm | `uv run python docs/issues/feature/69-feature-aimer-fire-action-misfire/measure_fire.py --fire-radius-mm always 1.25 --fly-model neural --no-stimulus --episodes 20 --out docs/issues/feature/69-feature-aimer-fire-action-misfire/data/neural-fly-nostim` |

Setup: `uv sync --extra train --extra neural --extra dev` at the repo root. The rule-fly run takes a few minutes,
the neural one about ten.

Seeds 20000 and up are the evaluation seeds used since #35; the README table uses 10000-10199. Everything else
is the default `EnvConfig` (dumped in full under `env` in `meta.json`).

## Files

### `meta.json`
`envVersion`, `gitCommit` and `gitDirty` (tracked files changed at the time of the run), `argv`, `seeds`
(first, last), `triggers`, `policy`, and `env` (the full env config).

### `episodes.csv`
One row per (trigger, seed).

| Column | Meaning |
|---|---|
| `trigger` | `radius`: the baseline fires when its estimate of the beam distance is within `fire_radius_mm`. `always`: the trigger is held down, a new shot starts the step after the last one ends |
| `fire_radius_mm` | trigger radius; empty for `always` |
| `seed` | episode seed. Same seed = same start; the rule fly's path does not depend on the aimer, so rows with the same seed are paired across triggers (the neural fly's path is also independent of the aimer here because the aim stimulus is off) |
| `captured` | 1 if a shot stayed on the fly for its whole 0.15 s |
| `time_s` | episode length. 10.0 when not captured (the limit) |
| `steps` | action steps (20 ms each) |
| `shots`, `misfires` | counts for the episode. `shots - misfires` is 1 when captured, else 0 (or 1 unfinished shot at the limit) |
| `visible_ratio` | fraction of action steps with the fly inside the aimer's view |
| `return` | sum of the aimer's reward |
| `first_visible_s` | time of the first step with the fly in view; empty if never |
| `first_shot_s` | time the first trigger was pulled; empty if never |

### `shots.csv`
One row per shot. `t_start_s`, `visible`, `est_beam_mm`, `true_beam_mm`, `distance_m`, `target_rate_*` describe
the moment the trigger was pulled: the observation the aimer acted on and the env's truth at that time.

| Column | Meaning |
|---|---|
| `trigger`, `fire_radius_mm`, `seed` | as above |
| `shot` | 1-based index within the episode |
| `t_start_s` | time the trigger was pulled |
| `outcome` | `hit` (captured), `misfire` (beam left the fly during the shot), `unfinished` (episode hit the time limit during a shot that had not yet missed) |
| `t_off_s` | for a misfire, end of the action step in which the beam was first off the fly (20 ms resolution); empty otherwise |
| `visible` | 1 if the fly was in view at the trigger |
| `est_beam_mm` | beam distance the baseline estimated from its observation (`RuleAimer.beam_distance`); empty when not visible. Clipped low when the aim error exceeds `fine_error_deg` |
| `true_beam_mm` | true distance from the fly's centre to the beam at the trigger |
| `distance_m` | true distance from the aimer to the fly |
| `target_rate_yaw`, `target_rate_pitch` | observed angular rate of the fly's direction, as a fraction of the aimer's maximum rate (180 and 120 deg/s) |

## Reading the rows
```python
import pandas as pd
d = "docs/issues/feature/69-feature-aimer-fire-action-misfire/data/rule-fly/"
ep = pd.read_csv(d + "episodes.csv")
ep["time_or_limit"] = ep.time_s.where(ep.captured == 1, 10.0)
print(ep.groupby(["trigger", "fire_radius_mm"], dropna=False)[["captured", "time_or_limit", "shots", "misfires"]].mean())
shots = pd.read_csv(d + "shots.csv")
print(shots[shots.trigger == "radius"].groupby("fire_radius_mm").outcome.value_counts(normalize=True))
```
`pandas` is not a project dependency; the files are plain CSV.

## Limits
- One policy (the rule baseline), one fly per folder. No learned aimer exists for env version 6 yet.
- The neural folder has 20 seeds; it shows direction, not a rate to quote.
- Misfire timing is at action-step resolution (20 ms); the env judges at 10 ms.
- Full frame-by-frame traces are not here. Episodes with frames are under `published/` (issue page #69), seeds 10000-10002.
