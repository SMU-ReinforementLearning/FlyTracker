# Why `v7-rule` is worse than aimer v2 — diagnosis

Date: 2026-11-27. No training; everything is measured locally from the models and outputs already on disk.
Asked by the user after the verdicts ("v7-rule이 왜 v2보다 못한지 원인부터 재봐"). Scripts: `diagnosis/`.

The startle of the fly is an intended difficulty of env version 7 (user, 2026-11-27). This note does not treat
"numbers fall under version 7" as a defect. Both aimers are compared in the same environment each time; the question is
why the same recipe learns less when it is trained under version 7.

## Answer

`v7-rule` never learned to capture during training. Under version 7 the training episodes almost never ended in a
capture, from the first step to the last, so the policy was shaped by the dense reward terms only (keep the fly in
view and near the beam) and stayed imprecise and noisy. Under version 6 the same recipe started capturing after about
200,000 steps and then sharpened. The first half of this is measured; the causal link ("because captures were missing,
precision did not develop") is the reading that fits all five measurements below, not a tested fact.

## Measurements

Rule fly, seeds 20000-20199, 200 episodes per model, three models per aimer. "v2" is `accel-pen-rule` of #88.

1. **Training setup is the same.** `config.json` of the two runs differs only in `envVersion` 6 -> 7
   (`fly.evade_laser`) and in defaults recorded since (`reward.wall_shot` 0, neural profile fields). `cfgdiff` in
   `runs/_ops101/diag/` (gitignored).

2. **Training rollouts (TensorBoard, mean over five equal parts of training).**

   | run | episode length (steps of 500), parts 1-5 | episode reward, parts 1-5 | critic loss, part 5 |
   | --- | --- | --- | --- |
   | v2 s0 | 496, 376, 215, 184, 151 | -48.6, -21.5, -11.3, -10.8, -8.7 | 0.365 |
   | v2 s1 | 500, 463, 312, 224, 178 | -52.9, -27.8, -14.8, -11.0, -8.4 | 0.312 |
   | v2 s2 | 500, 480, 331, 180, 140 | -54.4, -26.7, -18.3, -6.9, -5.1 | 0.311 |
   | `v7-rule` s0 | 500, 497, 498, 490, 489 | -46.4, -29.2, -28.3, -28.2, -27.3 | 0.028 |
   | `v7-rule` s1 | 500, 499, 499, 498, 496 | -46.5, -31.6, -30.2, -28.9, -27.1 | 0.036 |
   | `v7-rule` s2 | 500, 500, 500, 497, 495 | -57.5, -35.0, -33.4, -33.1, -29.4 | 0.047 |

   An episode shorter than 500 steps is a capture. v2's episodes shrink to about 150 steps; `v7-rule`'s stay at
   489-500, and its reward stops improving after the second part.

3. **With sampled actions (as in training), version 7.**

   | aimer | deterministic: capture / time / shots per episode | sampled: capture / time / shots per episode |
   | --- | --- | --- |
   | v2 s0, s1, s2 | 0.860 / 4.697 / 6.73, 0.800 / 5.072 / 7.01, 0.870 / 4.784 / 7.43 | 0.855 / 5.061 / 8.07, 0.555 / 6.954 / 12.47, 0.815 / 5.449 / 9.33 |
   | `v7-rule` s0, s1, s2 | 0.690 / 6.131 / 7.23, 0.420 / 7.891 / 7.47, 0.325 / 8.433 / 6.71 | 0.180 / 9.222 / 20.82, 0.020 / 9.936 / 18.27, 0.015 / 9.907 / 16.30 |

   Pooled: v2 0.843 -> 0.742; `v7-rule` 0.478 -> 0.072. The sampled `v7-rule` fires 16 to 21 shots per episode and
   nearly all are grazes, each of which startles the fly. v2's sampled policy still captures under version 7, so the
   startle plus exploration noise does not by itself prevent capture; a policy that is already precise keeps capturing.

4. **With the beam reaction switched off** (`evade_laser` off, the fly of version 6; deterministic).

   | aimer | capture | time (s) | per model capture / time |
   | --- | --- | --- | --- |
   | v2 | 0.982 | 2.611 | 0.965 / 2.851, 0.990 / 2.574, 0.990 / 2.409 |
   | `v7-rule` | 0.843 | 4.649 | 0.930 / 3.537, 0.840 / 4.780, 0.760 / 5.630 |

   `v7-rule` is the worse aimer against the easy fly too. It did not trade easy-fly skill for startle skill; it is
   less skilled overall.

5. **Shot statistics from the gate measurements (version 7, deterministic).**

   | model | visible ratio | shots per visible second | captures per shot | beam-to-fly at trigger, median (mm) |
   | --- | --- | --- | --- | --- |
   | v2 s0, s1, s2 | 0.583, 0.711, 0.671 | 2.49, 1.84, 2.18 | 0.128, 0.114, 0.117 | 0.807, 0.800, 0.867 |
   | `v7-rule` s0, s1, s2 | 0.675, 0.807, 0.740 | 1.64, 1.14, 1.04 | 0.095, 0.056, 0.048 | 0.998, 0.953, 0.992 |

   `v7-rule` keeps the fly in view longer than v2 but gets it inside the trigger radius about half as often, and when
   the rule fires the beam sits nearer the edge of the 1.25 mm radius. That is what a policy rewarded for "near and
   visible" but not for "captured" looks like.

## What is not measured

- The causal test. It would be a training run under version 7 that does experience captures early (for example a
  warm start from v2, or the beam reaction switched on only after captures begin) and then a comparison with
  `v7-rule`. Nothing of that kind was run.
- Whether more steps alone would help. The reward of `v7-rule` was still creeping up at 1,000,000 steps
  (-28.2 -> -27.3, -28.9 -> -27.1, -33.1 -> -29.4) while episode length barely moved.
- The spread between `v7-rule` seeds (capture 0.325 to 0.690) is reported, not explained.

## Consequences for the open decisions

- v2 remains the best aimer under version 7 (0.843 / 4.851 s); nothing here argues against the environment.
- A second stage (fire-only training) on the fixed aim of `v7-rule` would build on an aimer that is known to be
  imprecise. If it is run, v2 is the better fixed aim; that changes the pre-declared second stage and needs a new gate.
- The joint fire conditions (`v7-fire-w*`) share the same start-up problem and add a second one: a policy that must
  also learn when to fire experiences even fewer captures.

## Reproduce

```
python docs/issues/feature/101-feature-sac-aim-fire-env7/diagnosis/measure_noevade.py <model run> --out <dir>
python docs/issues/feature/101-feature-sac-aim-fire-env7/diagnosis/measure_stochastic.py <model run> --out <dir>
python docs/issues/feature/101-feature-sac-aim-fire-env7/diagnosis/stats.py <label>=<out dir> ...
python docs/issues/feature/101-feature-sac-aim-fire-env7/diagnosis/curves.py <label>=<run dir> ...
```

Outputs of this diagnosis: `runs/_diag101/` in the #101 worktree (gitignored). The sampled measurement is seeded
(torch seed 0); `v7-rule` s2 was run twice and gave the identical `gate.csv`.
