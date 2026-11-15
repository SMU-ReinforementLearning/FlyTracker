# Gate — SAC aimers vs rule baseline under the laser capture rule

<!-- Every section above "Verdict" was written BEFORE any candidate was measured. -->

Written 2026-11-15, before any training run of this issue started. SAC numbers seen so far
under environment version 5: two 6,000-step throughput smoke runs (`smoke-assist`,
`smoke-1thread`; the first evaluated on 5 seeds only to check that the evaluation script
loads a model: 0/5). Neither is a candidate. Numbers from earlier versions that shaped the
candidates: #35's SAC models caught 1/1200 under version 3; a scratch run in #42 with a
version-2 SAC model for search plus rule tracking caught 191/200 in 3.24 s (seeds
10000-10199, version 3).

Environment version 5 (`origin/main` @ c4dd7e1 plus this branch's tracking-assist wrapper,
which does not change the environment): capture is a laser hit (fly centre within 1.25 mm
of the beam for 0.15 s), pitch limit 90°, 17-dim observation with `target_rate` and
`uv_fine`, dense penalty on the log-scaled beam distance.

Amended 2026-11-16 00:25 KST, still before any candidate was measured: the user asked for
1,000,000 steps (as in #35) on a rented instance instead of 500,000 steps on the local
machine. The local runs started under the first version were stopped at about 28,000 steps
and deleted without being evaluated; their in-training evaluations at step 0 (untrained,
0/3 each) are the only numbers that existed. Every "500,000" below was changed to
"1,000,000" and the platform lines were rewritten; nothing else changed.

## Question

Under environment version 5, does an aimer trained with SAC catch the rule fly faster than
the rule baseline, without losing flies, over the 200 evaluation seeds 20000-20199? Asked
separately for four training conditions.

## Baseline

- Predictions file: `gate/baseline.csv` — sha256 `6ac2f0bd223aea7cd0d1850ae48e7ed624ccfe8b345f02352d6ade3961e259ae` (frozen; regenerate = a new gate)
- Produced by: `evaluate_gate.py baseline` on this branch (`RuleAimer` defaults via `load_opponent("baseline", ...)`, default `EnvConfig`), 2026-11-15, local machine (Windows, torch 2.15.0, CPU)
- Metric value: time 4.858 s (mean), capture rate 0.990 (198/200)
- Truth file: `gate/truth.csv` — sha256 `630ec5b311a118169c3d0a5872638c13680f0a02d3f509cf98f52238aad98089` (capture = 1, time = 0 for every id)

Capture rate is 0.990, so a candidate can gain at most 2 captures; capture cannot carry the
gate. Time to capture can: the baseline spends most of its time searching.

## Candidate(s)

A 2 x 2 design: which dense reward, and whether the policy steers alone or corrects the
baseline's tracker.

| name | reward while visible | control | predictions file (filled when measured) |
| --- | --- | --- | --- |
| `sac-beam` | version 5: log-scaled beam distance (default weights) | policy alone | `gate/sac-beam.csv` |
| `sac-angle` | version 4: aim error in proportion to angle (`--reward beam=0 angle=0.05`) | policy alone | `gate/sac-angle.csv` |
| `sac-beam-assist` | version 5 | tracking assist 0.2 (`--assist 0.2`) | `gate/sac-beam-assist.csv` |
| `sac-angle-assist` | version 4 | tracking assist 0.2 | `gate/sac-angle-assist.csv` |

"Tracking assist 0.2": while the fly is visible the action sent to the environment is the
baseline's tracking action plus 0.2 x the policy's action; while it is not visible the
policy's action is used as is. The policy therefore learns the search and a correction.

Training, identical except for the two options above:

- `scripts/train.py --algo sac --steps 1000000 --eval-every 50000 --eval-episodes 3 --seed <0|1|2> --device cpu` plus the condition's options; frame stack 1.
- Stable-Baselines3 2.9.2 `SAC("MlpPolicy")` defaults (lr 3e-4, buffer 1e6, batch 256, tau 0.005, gamma 0.99, `ent_coef="auto"`, train_freq 1, gradient_steps 1, learning_starts 100), `OMP_NUM_THREADS=1`.
- Platform: vast.ai instance 60797094 (AMD EPYC 7B13, RTX 5060 Ti), Linux, Python 3.11.18, torch 2.15.0+cu132, numpy 2.4.6. Device: a throughput check on the instance with 12 parallel 4,000-step runs took 88 s on CPU and 107 s on CUDA, so the runs use the CPU. The check runs were deleted unevaluated. Evaluation for the gate runs on the same instance.
- Default `EnvConfig` otherwise, rule fly, environment version 5.
- 1,000,000 steps, the same budget as #35. It is part of the candidate: "not adopted" means not adopted at this budget.
- The candidate model is the **final** `model.zip` at 1,000,000 steps. Checkpoints are for the viewer and the learning curve only; no checkpoint is picked.

## Metric

- Per evaluation seed: `time` = seconds from reset until capture; the full episode length (10 s) when the fly is not captured. `capture` = 1 if captured.
- The model acts with `deterministic=True` through `load_opponent`, which applies the run's tracking assist. One episode per seed.
- A candidate's value per seed is the mean over its 3 training seeds (`evaluate_gate.py mean`).
- Formula: mean `time` over the 200 seeds = `mae` against truth time 0. Lower is better.
- Rounding: none. Clip: none.
- Targets: `time` (gated), `capture` (reported, and used by an exclusion below).
- Tool: `paired_bootstrap.py --truth gate/truth.csv --a gate/baseline.csv --b gate/<cand>.csv --targets time --metric mae --lower-is-better --resamples 10000 --seed 42 --threshold 0.90`

## Data

- Item ids: evaluation seeds 20000-20199, N = 200, listed in `gate/truth.csv`
- Items that must be present: all 200
- Both systems are scored on exactly these ids; a missing id is a failed run, not a smaller N
- Training never resets the environment with these seeds explicitly (training env seed = 0, 1, 2; in-training evaluation uses 10000-10002)

## Threshold

- Adopt when P(candidate faster) ≥ `0.90` by paired bootstrap, 10,000 resamples, seed 42, on `time`
- Below the threshold the answer is "not adopted", including at 0.85
- Four candidates are gated against the same baseline. With four looks, a candidate of baseline quality has about a 1 − 0.9⁴ ≈ 34 % chance that at least one of four crosses 0.90 by luck; the threshold is not relaxed, and the verdict states how many of the four passed.

## Selection rule

None. Each candidate is gated against the baseline on its own. Comparisons between
conditions (beam vs angle with the same control; assist vs alone with the same reward) are
reported descriptively with the same bootstrap and carry no decision. If more than one
candidate passes, no single one is chosen from these 200 seeds; choosing one is a new gate
on fresh seeds.

## Pre-declared exclusions / sensitivity checks

- Candidate capture rate (mean over its 3 models) below 0.97 → not adopted even if `time` passes. Faster on average but losing flies the baseline catches is not better.
- Any single training seed whose model has P(faster than baseline) < 0.50 on `time` → **undecided**, not adopt: the result depends on the training seed.
- A run that does not reach 1,000,000 steps voids that candidate; it is re-run with the same seed, not replaced by a checkpoint.
- A run that captures nothing (0/200) is a valid measurement, not a failed run.

## Gates

1. Offline: `paired_bootstrap.py` on the files above → P(win), CI, per training seed and pooled.
2. Deployed: none — nothing ships; the viewer only replays recorded episodes.

## Decision rule

- **adopt** — the offline gate passes and no exclusion fires: that condition is a working RL aimer under the laser rule and a reference for later issues; the rule baseline stays as the comparison.
- **reject** — the gate fails or the capture exclusion fires: the numbers and learning curves go into the management doc; this gate is not re-run with a tweak. A changed setup (more steps, other weights, other assist scale) is a new gate.
- **undecided** — passes pooled but a training seed is worse than the baseline: report the spread; more training seeds are a new gate.

Whatever the verdicts, all runs are published under issue #51 so the conditions can be compared in the viewer.

## Verdict

<!-- Filled after measuring. -->
