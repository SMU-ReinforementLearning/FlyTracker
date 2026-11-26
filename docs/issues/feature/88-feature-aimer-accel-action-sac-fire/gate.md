# Gate — SAC aimers with angular-acceleration actions, with and without learning to fire

<!-- Every section above "Verdict" was written BEFORE any candidate was measured. -->

Written 2026-11-25, before any training run of this issue started. Numbers seen so far on
this branch: three 3,000-step smoke runs (`smoke-accel`, `smoke-fire`, `smoke-rate`), each
evaluated on seeds 20000-20002 only to check that the evaluation script loads the model
(0/3 each). None is a candidate. Numbers that shaped the candidates: #85's diagnosis of
#51's policy-alone models (rate command scatters by about ±25 °/s, median 3.0-3.8 mm from
the beam, no captures seen in training), and #72's v0 / v1 numbers.

Environment version 6 (`origin/main` @ 813b1b9 plus this branch). The branch adds a
misfire weight to the aimer reward (default 0, so the default environment is unchanged:
the baseline file below is reproduced byte for byte on this branch) and two training
wrappers that do not change the environment: `AccelControl` and `RuleFire`.

## Question

Under environment version 6, with the rule fly, does a SAC aimer that steers alone catch
the fly faster than the rule aimer (v0), without losing flies, over the 200 evaluation
seeds 20000-20199? Asked separately for five training conditions: three where the
baseline's rule fires (does the aim work?) and two where the policy also learns to fire.

## Baseline

- Predictions file: `gate/baseline.csv` — sha256 `70a62ab3d45dc31d10524a514587e59edec48bed0e217f0d3cb32b9559808b1c` (frozen; regenerate = a new gate). The same bytes as #72's `gate/baseline.csv`.
- Produced by: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/measure_aimers.py baseline` (#72, 2026-11-17, local Windows machine); regenerated on this branch 2026-11-25 with an identical sha256.
- Metric value: time 4.894 s (mean), capture rate 0.990 (198/200), misfires 0.500 per episode
- Truth file: `gate/truth.csv` — sha256 `0f577c4c706f728dccaa660ab6c7640e4eeb69c84e112ddcc29d8396d5f3669b` (capture = 1, time = 0, misfires = 0 for every id)

Reference, not a baseline of this gate: aimer v1 (`sac-beam-assist` + rule fire, #72)
3.026 s, 584/600, 0.60 misfires per episode on the same seeds.

## Candidate(s)

| name | steering action | who fires | reward change | predictions file (filled when measured) |
| --- | --- | --- | --- | --- |
| `rate-rule` | angular rate (as now) | baseline's rule | none | `gate/rate-rule.csv` |
| `accel-rule` | angular acceleration | baseline's rule | none | `gate/accel-rule.csv` |
| `accel-pen-rule` | angular acceleration | baseline's rule | `action_change=1.0` (default 0.01) | `gate/accel-pen-rule.csv` |
| `accel-fire-m03` | angular acceleration | policy | `misfire=0.3` | `gate/accel-fire-m03.csv` |
| `accel-fire-m10` | angular acceleration | policy | `misfire=1.0` | `gate/accel-fire-m10.csv` |

- Angular-acceleration action (`--control accel`): commanded rate = current rate + action × 14.4 °/s per step (yaw 0.08, pitch 0.12 in action units), clipped to the rate range. Action ±1 equals the turret's acceleration limit.
- Rule fire (`--fire rule`): the policy outputs yaw and pitch only and does not observe `shot`; `RuleAimer.wants_fire` decides each step, as for v0 and v1.
- `action_change=1.0`: the existing penalty on the squared change of the rate command, 100 times the default. Under acceleration actions it is a penalty on acceleration. Full acceleration costs about 0.010 per step; the beam penalty between 3 mm and 1.25 mm is 0.008 per step. A reasoned starting value, not tuned.
- `misfire`: subtracted once per shot that leaves the fly. 0.3 and 1.0 were agreed with the user (2026-11-25) as two conditions instead of one chosen value; the capture reward is 10 and the time penalty is 0.5 per second.
- `rate-rule` repeats #51's `sac-beam` under version 6 with rule fire, as the comparison for the two `accel-*-rule` conditions.

Training, identical except for the options above:

- `scripts/train.py --algo sac --steps 1000000 --eval-every 50000 --eval-episodes 3 --seed <0|1|2> --device cpu` plus the condition's options; frame stack 1; no tracking assist.
- Stable-Baselines3 `SAC("MlpPolicy")` defaults (lr 3e-4, buffer 1e6, batch 256, tau 0.005, gamma 0.99, `ent_coef="auto"`, train_freq 1, gradient_steps 1, learning_starts 100), `OMP_NUM_THREADS=1`.
- Platform: a rented vast.ai instance (id and hardware recorded in the management doc when created), Linux, Python 3.11, torch 2.15.0, stable-baselines3 2.9.2, gymnasium 1.4.0.
- Default `EnvConfig` otherwise, rule fly, environment version 6.
- 1,000,000 steps, as in #35 and #51. It is part of the candidate.
- The candidate model is the **final** `model.zip`. No checkpoint is picked.

## Metric

- Per evaluation seed: `time` = seconds from reset until capture, 10 s when not captured. `capture` = 1 if captured. `misfires` = shots during which the beam left the fly.
- The model acts with `deterministic=True` through `load_opponent`, which rebuilds the run's control and fire settings. One episode per seed.
- A candidate's value per seed is the mean over its 3 training seeds (`measure_aimers.py mean`).
- Formula: mean over the 200 seeds = `mae` against the truth. Lower is better. Rounding: none. Clip: none.
- Targets: `time` (gated), `capture` (reported; exclusion below), `misfires` (reported; rule below).
- Tools: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/measure_aimers.py <run> --out <dir>` on the local Windows machine (where the baseline was produced), then `paired_bootstrap.py --truth gate/truth.csv --a gate/baseline.csv --b gate/<cand>.csv --targets time --metric mae --lower-is-better --resamples 10000 --seed 42 --threshold 0.90`

## Data

- Item ids: evaluation seeds 20000-20199, N = 200, listed in `gate/truth.csv`
- Items that must be present: all 200
- Both systems are scored on exactly these ids; a missing id is a failed run, not a smaller N
- Training never resets the environment with these seeds explicitly (training env seed = 0, 1, 2; in-training evaluation uses 10000-10002)

## Threshold

- Adopt when P(candidate faster) ≥ `0.90` by paired bootstrap, 10,000 resamples, seed 42, on `time` (the threshold of #35, #51 and #72)
- Below the threshold the answer is "not adopted", including at 0.85
- Five candidates are gated against the same baseline. A candidate of baseline quality has about a 1 − 0.9⁵ ≈ 41 % chance that at least one of five crosses 0.90 by luck; the threshold is not relaxed, and the verdict states how many of the five passed.

## Selection rule

None. Each candidate is gated against the baseline on its own. Comparisons between
conditions (`accel-rule` vs `rate-rule`; `accel-pen-rule` vs `accel-rule`; the two misfire
weights; each against v1) are reported descriptively with the same bootstrap and carry no
decision. If more than one candidate passes, none is chosen from these 200 seeds.

## Pre-declared exclusions / sensitivity checks

- Candidate capture rate (mean over its 3 models) below 0.97 → not adopted even if `time` passes.
- Any single training seed whose model has P(faster than baseline) < 0.50 on `time` → **undecided**, not adopt.
- Pooled misfires per episode above twice the baseline's (more than 1.00) → **undecided — the user decides** (as in #72; no cost has been set for a misfire outside training).
- A run that does not reach 1,000,000 steps voids that candidate; it is re-run with the same seed, not replaced by a checkpoint.
- A run that captures nothing, or a policy that never fires, is a valid measurement.

## Gates

1. Offline: `paired_bootstrap.py` on the files above → P(win), CI, per training seed and pooled.
2. Deployed: none — nothing ships.

## Decision rule

- **adopt** — the gate passes and no exclusion fires: that condition is a working policy-alone aimer. Whether it replaces v1 is a separate decision (a new gate against v1).
- **reject** — the gate fails or the capture exclusion fires. The diagnosis of #85 (distance to the beam, command scatter, captures seen in training) is repeated on the models and reported; this gate is not re-run with a tweak.
- **undecided** — a per-seed or misfire condition fires: the numbers are reported and the user is asked.

Whatever the verdicts, the result decides the design of the staged step (fire learning on top of a working aim), which is not part of this gate.

## Verdict

Measured 2026-11-26 on the local Windows machine. All 15 runs reached 1,000,000 steps on the instance (vast.ai 62522764, started 2026-11-25 13:10:47 UTC, results packed 17:30 UTC); the archive's sha256 matched after download and the instance was destroyed 2026-11-26 02:49 KST. Each final `model.zip` was measured with #72's `measure_aimers.py` on seeds 20000-20199; all 200 ids present for every model. Bootstraps: `run_gate.py`; the complete unedited output with the sha256 of every input is `gate/bootstrap-output.md`. The rows below are copied from it.

Columns: target | A (baseline) | B (candidate) | Δ | bootstrap mean Δ | 95% CI | P(B better). For `capture` the value is the miss rate.

### Gated: time against the baseline (v0), pooled over 3 training seeds

| candidate | row from the tool | gate |
| --- | --- | --- |
| `rate-rule` | time \| 4.8943 \| 9.9675 \| +5.0732 \| +5.0723 \| [+4.8696, +5.2718] \| 0.000 | FAIL |
| `accel-rule` | time \| 4.8943 \| 3.0215 \| -1.8728 \| -1.8714 \| [-2.1370, -1.5912] \| 1.000 | PASS |
| `accel-pen-rule` | time \| 4.8943 \| 2.6114 \| -2.2829 \| -2.2825 \| [-2.5372, -2.0240] \| 1.000 | PASS |
| `accel-fire-m03` | time \| 4.8943 \| 10.0000 \| +5.1057 \| +5.1050 \| [+4.9094, +5.2978] \| 0.000 | FAIL |
| `accel-fire-m10` | time \| 4.8943 \| 10.0000 \| +5.1057 \| +5.1050 \| [+4.9094, +5.2978] \| 0.000 | FAIL |

### Exclusions

| candidate | capture (pooled; 0.97 needed) | per training seed P(faster), s0 / s1 / s2 (0.50 needed) | misfires per episode (pooled; above 1.00 → undecided) |
| --- | --- | --- | --- |
| `rate-rule` | 0.0200 (12/600) | 0.000 / 0.000 / 0.000 | 19.578 |
| `accel-rule` | 0.9650 (579/600) — **fires** | 1.000 / 1.000 / 1.000 | 0.687 |
| `accel-pen-rule` | 0.9817 (589/600) | 1.000 / 1.000 / 1.000 | 0.472 |
| `accel-fire-m03` | 0.0000 (0/600) | 0.000 / 0.000 / 0.000 | 0.007 |
| `accel-fire-m10` | 0.0000 (0/600) | 0.000 / 0.000 / 0.000 | 0.007 |

Per model (capture of 200, mean time, misfires per episode): `accel-rule` s0 194, 3.030 s, 0.640; s1 191, 3.047 s, 0.700; s2 194, 2.987 s, 0.720. `accel-pen-rule` s0 193, 2.851 s, 0.320; s1 198, 2.574 s, 0.650; s2 198, 2.409 s, 0.445. `rate-rule` s0 6, s1 3, s2 3. The fire-learning models captured nothing and fired about 0.01 shots per episode.

### Decisions

One of the five candidates passed.

- `rate-rule` — **reject** (gate fails). The rule fires about 19.6 times per episode and nearly every shot leaves the fly: the same near miss as #51's `sac-beam`, now visible as misfires.
- `accel-rule` — **reject**. Time passes with P = 1.000, but the pre-declared capture exclusion fires: 0.9650 is below 0.97 (579/600; the baseline 198/200). The time result is real and is reported; the rule written before measuring decides.
- `accel-pen-rule` — **adopt**: a working policy-alone aimer. P = 1.000 on time (2.611 s against 4.894 s), capture 0.9817, every training seed P = 1.000, misfires 0.472 per episode (baseline 0.500). One of its three models (s0) is at 193/200 on its own; the exclusion is written on the mean over the three models, which is above 0.97.
- `accel-fire-m03`, `accel-fire-m10` — **reject** (gate fails). The policies learned not to fire at all; both misfire weights give the same result, so the weight is not what decided it.

Not a decision of this gate (Selection rule): whether `accel-pen-rule` replaces v1. Descriptive rows, B against A:

| comparison | row from the tool |
| --- | --- |
| `accel-rule` (B) vs `rate-rule` (A) | time \| 9.9675 \| 3.0215 \| -6.9460 \| -6.9438 \| [-7.1655, -6.7047] \| 1.000 |
| `accel-pen-rule` (B) vs `accel-rule` (A) | time \| 3.0215 \| 2.6114 \| -0.4101 \| -0.4111 \| [-0.5877, -0.2446] \| 1.000 |
| `accel-pen-rule` (B) vs `accel-rule` (A) | capture \| 0.0350 \| 0.0183 \| -0.0167 \| -0.0168 \| [-0.0333, -0.0017] \| 0.984 |
| `accel-pen-rule` (B) vs `accel-rule` (A) | misfires \| 0.6867 \| 0.4717 \| -0.2150 \| -0.2150 \| [-0.3383, -0.0983] \| 1.000 |
| `accel-rule` (B) vs v1 (A) | time \| 3.0256 \| 3.0215 \| -0.0042 \| -0.0030 \| [-0.1977, +0.1973] \| 0.514 |
| `accel-pen-rule` (B) vs v1 (A) | time \| 3.0256 \| 2.6114 \| -0.4142 \| -0.4141 \| [-0.5755, -0.2573] \| 1.000 |
| `accel-pen-rule` (B) vs v1 (A) | capture \| 0.0267 \| 0.0183 \| -0.0083 \| -0.0083 \| [-0.0250, +0.0067] \| 0.869 |
| `accel-pen-rule` (B) vs v1 (A) | misfires \| 0.6000 \| 0.4717 \| -0.1283 \| -0.1287 \| [-0.2533, +0.0000] \| 0.975 |

The comparison with v1 was not pre-registered as a gate and the `action_change=1.0` value was the only one tried, so these rows are a reason to write a gate against v1, not a replacement of v1.

Consequences: acceleration control is what made a policy-alone aim work (same reward, same fire rule, rate 12/600 against acceleration 579/600). Learning to fire from scratch together with the aim fails by never firing; the staged step (fire learning on top of a working aim) starts from `accel-pen-rule`. Deployed gate: none.
