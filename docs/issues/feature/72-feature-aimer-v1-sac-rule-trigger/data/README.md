# Raw rows of the #72 measurements

Aimer v0 (rule aimer) and the v1 candidate (`sac-beam-assist` models of #51 steering, the baseline's rule firing)
under env version 6. One folder per fly setting and aimer; each holds `episodes.csv`, `shots.csv`, `gate.csv`
and `meta.json`, written by `../measure_aimers.py`.

| Folder | Fly | Seeds | Aimers |
|---|---|---|---|
| `rule-fly/` | rule fly | 20000-20199 | `baseline`, `sac-beam-assist-s0`, `-s1`, `-s2` |
| `neural-fly-nostim/` | neural fly, aim stimulus off | 20000-20059 | same four |
| `neural-fly-stim/` | neural fly, aim stimulus on (default) | 20000-20059 | same four |

## Re-running
Setup: `uv sync --extra train --extra neural --extra dev`. The three model folders are not in the repository
(`runs/` is gitignored): they are the final `model.zip` + `config.json` of #51's `sac-beam-assist-s0/-s1/-s2`,
whose sha256 is in each `meta.json` (`aimer.modelSha256`). Put them under `runs/` as
`runs/2026-11-15_151701_sac-beam-assist-s<k>/`.

```sh
M=docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger
uv run python $M/measure_aimers.py baseline --out $M/data/rule-fly/baseline
uv run python $M/measure_aimers.py runs/2026-11-15_151701_sac-beam-assist-s0 --out $M/data/rule-fly/sac-beam-assist-s0
uv run python $M/measure_aimers.py baseline --fly-model neural --no-stimulus --episodes 60 --out $M/data/neural-fly-nostim/baseline
uv run python $M/measure_aimers.py baseline --fly-model neural --episodes 60 --out $M/data/neural-fly-stim/baseline
# pooled candidate (mean of the three models per seed), then the bootstraps of gate.md
uv run python $M/measure_aimers.py mean $M/data/rule-fly/sac-beam-assist-s{0,1,2}/gate.csv --out $M/gate/sac-beam-assist-rule-fire.csv
uv run python $M/run_gate.py rule-fly
```
The exact arguments of each run are in its `meta.json` (`argv`). Results are deterministic for a seed on one
machine; across machines a trained model's trajectory can differ in the last digits and diverge within an episode.
The rule-fly runs take a few minutes each, the neural ones about fifteen.

## Files
- `episodes.csv`: one row per seed. `seed, captured, time_s, steps, shots, misfires, visible_ratio, return, first_visible_s, first_shot_s`.
- `shots.csv`: one row per shot. `seed, shot, t_start_s, outcome (hit | misfire | unfinished), t_off_s, visible, est_beam_mm, true_beam_mm, distance_m, target_rate_yaw, target_rate_pitch`.
- `gate.csv`: `id, capture, time, misfires`; `time` is 10 when not captured. Input of `paired_bootstrap.py`.
- `meta.json`: `envVersion`, `gitCommit`, `gitDirty`, `argv`, `seeds`, `aimer` (`label`, `trainedEnvVersion`, `fire`, `modelSha256`), `env`.

Column meanings are those of #69's data (`docs/issues/feature/69-feature-aimer-fire-action-misfire/data/README.md`);
there is no trigger column here because every aimer fires by the same rule (estimated beam distance within 1.25 mm).
`est_beam_mm` is what that rule saw.

## Limits
- `gitDirty` is true in every `meta.json`: the runs were made before the code was committed. The code is that of commit a4a6c12.
- Sixty seeds for the neural fly; three models, one training condition.
- The verdict and the tables are in `../gate.md`; the unedited bootstrap output in `../gate/`.
