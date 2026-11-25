# Data of issue #88

Everything here was produced on the local Windows machine on 2026-11-26 from the 15 final models in `runs/g88/<condition>-s<seed>/<run>/` (gitignored; trained on vast.ai, 1,000,000 steps each).

## Files

| path | what | made by |
| --- | --- | --- |
| `<condition>-s<k>/gate.csv`, `episodes.csv`, `shots.csv`, `meta.json` | one model on seeds 20000-20199, as it was trained (control and fire read from the run's `config.json`) | #72's `measure_aimers.py <run> --out <dir>` |
| `../gate/<condition>.csv` | per-seed mean of the condition's three models | `measure_aimers.py mean` |
| `../gate/v1.csv` | copy of #72's `gate/sac-beam-assist-rule-fire.csv` (descriptive comparison only) | `cp` |
| `../gate/bootstrap-output.md` | every bootstrap named in `gate.md`, unedited | `run_gate.py` |
| `tables.md`, `episodes.csv`, `capture-grid.csv` | #85's diagnosis with the fire action held off: beam distance, counterfactual capture, error composition, command scatter | `measure_tracking.py`, `analyze.py` |
| `response.md` | correction by aim error; error autocorrelation; share of commands the turret cannot follow | `response_curve.py` |
| `training-logs.md` | episode length, reward, entropy coefficient during training | `training_logs.py` |
| `fire-head.md` | the fire action's mean by beam distance (fire-learning models) | `fire_head.py` |
| `fire-stochastic.md` | fire-learning models with sampled actions, 50 episodes: shots, misfires, captures, fire sd | `fire_stochastic.py` |

## Re-run (from the repo root, models in `runs/g88`)

```
D=docs/issues/feature/88-feature-aimer-accel-action-sac-fire
M=docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/measure_aimers.py
# per model
uv run python $M runs/g88/accel-rule-s0/<run> --out $D/data/accel-rule-s0
# per condition
uv run python $M mean $D/data/accel-rule-s0/gate.csv $D/data/accel-rule-s1/gate.csv $D/data/accel-rule-s2/gate.csv --out $D/gate/accel-rule.csv
uv run python $D/run_gate.py
# diagnosis (raw traces go to runs/d88, gitignored)
uv run python $D/measure_tracking.py baseline --name baseline --out runs/d88
uv run python $D/measure_tracking.py runs/g88/accel-rule-s0/<run> --name accel-rule-s0 --out runs/d88
uv run python $D/analyze.py runs/d88 $D/data
uv run python $D/response_curve.py runs/d88 > $D/data/response.md
uv run python $D/training_logs.py runs/g88 > $D/data/training-logs.md
uv run python $D/fire_head.py runs/d88 > $D/data/fire-head.md
uv run python $D/fire_stochastic.py runs/g88 > $D/data/fire-stochastic.md
```

## Reading notes

- In `tables.md` section 5, "policy sd in training" is scaled as if the action were a rate; for the acceleration-control models the action is an acceleration, so that column is not comparable across the two controls. The other columns use the rate command the environment received and are comparable.
- `tables.md` has no section 3 (the check against #51's gate files does not apply here).
- Counterfactual captures (fire held off) differ slightly from the gate's captures (the rule fires): a misfire changes nothing in the fly's path, but the gate counts the first clean shot, which can come later than the first 0.15 s inside the radius.
