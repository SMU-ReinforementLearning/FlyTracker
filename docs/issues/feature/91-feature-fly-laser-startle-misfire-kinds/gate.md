# Gate — the acceleration-action aimer against v1 under environment version 7

<!-- Every section above "Verdict" was written BEFORE any candidate was measured. -->

Written 2026-11-26, before any learned aimer was run under environment version 7. Numbers seen so far under version 7: one smoke run of the measuring script with the rule aimer (v0) on three episodes outside the gate's seeds (10000-10002: 3/3 captured, 6.26 s, 6.67 misfires per episode, all of them grazes). Nothing with v1 or the candidate. Numbers seen under version 6 on the gate's seeds (#72, #88): v0 4.894 s, 198/200, 0.50 misfires; v1 3.026 s, 584/600, 0.60; `accel-pen-rule` 2.611 s, 589/600, 0.47, descriptively faster than v1 (P 1.000, not a pre-registered comparison).

## Question

Under environment version 7, where a rule fly touched by the beam is startled and escapes, does the acceleration-action aimer of #88 (`accel-pen-rule`, policy alone, rule fire) catch the fly faster than aimer v1 (#51's `sac-beam-assist` models with tracking assist, rule fire), without catching fewer flies, over evaluation seeds 20000-20199?

Both were trained under earlier versions (5 and 6) against a fly that does not react to the beam. The gate decides which existing aimer is the reference under version 7 (aimer v2 or not), not whether either is good there.

## Baseline

- Aimer v1: the three final models of #51, `sac-beam-assist-s0`, `-s1`, `-s2` (environment version 5, loaded with the baseline's firing rule), measured under version 7. Value per seed = mean over the three models.
- Predictions file: `gate/v1.csv` — measured first and frozen by sha256 here, before the candidate is measured: `cfcd2ffd60fc6dc2cf0cd5b07881f1f4755ccaa680c0173e507fe67149d172f8` (LF line endings, as written on the instance; measured 2026-11-26 from commit b967875: capture 0.780, 5.442 s, 6.408 misfires per episode = 6.013 grazes + 0.372 wall shots + shots still on at the end). `gate/v0.csv`: `34a572c5d373421f6cd42272aaaa4d2868dc2215b7305cbb86beb649b5db41d0` (capture 0.960, 6.037 s, 5.010 = 4.770 + 0.240).
- Truth file: `gate/truth.csv` (capture 1, time 0, misfires 0, grazes 0, wall_shots 0 for ids 20000-20199) — sha256 `81ae80c6b41bb8084206bc5a953051ac25b737513604d3d4781d78d3818a60f5`

Reference, not the baseline: v0 (the rule aimer) under version 7, `gate/v0.csv`.

## Candidate(s)

| name | what | predictions file |
| --- | --- | --- |
| `accel-pen-rule` | #88's three final models `accel-pen-rule-s0`, `-s1`, `-s2` (environment version 6, acceleration action, action-change weight 1.0, no tracking assist, rule fire), measured under version 7 | `gate/accel-pen-rule.csv` |

No training, no tuning: both sides are existing models played as trained, deterministic.

## Metric

- Per evaluation seed: `time` (seconds to capture; 10 s when not captured), `capture` (1 or 0), `misfires`, `grazes`, `wall_shots`. A condition's value per seed is the mean over its three models.
- `mae` against the truth, lower is better; no rounding, no clip. For `capture` the truth is 1, so the value is the miss rate.
- Targets: `time` (gated). `capture` (exclusion below). `misfires`, `grazes`, `wall_shots`: reported per condition, not gated; what a wall shot may cost is set by the user after these numbers.
- Where: one vast.ai instance (Linux, CPU, torch 2.15.0, stable-baselines3 2.9.2, gymnasium 1.4.0), as the user asked on 2026-11-26. Baseline and candidate are measured on the same instance from the same code bundle (the commit that holds this gate), in two steps: v0 and v1 first, `gate/v1.csv` fetched and its sha256 committed here, then the candidate. Version 6 numbers quoted above were measured on the local Windows machine; they are context, not part of the comparison.
- Tools: `measure_v7.py <run> --out <dir>`, `measure_v7.py mean`, then `paired_bootstrap.py --truth gate/truth.csv --a gate/v1.csv --b gate/accel-pen-rule.csv --targets time --metric mae --lower-is-better --resamples 10000 --seed 42 --threshold 0.90`.

## Data

- Item ids: evaluation seeds 20000-20199, N = 200, rule fly, default `EnvConfig` of version 7. All must be present.
- The same seeds were used under version 6 (#72, #88). The fly's path now depends on when it is hit, so episodes differ from those seen; the seed list is kept so that the versions can be set side by side.
- Neural fly (calibrated profile of #59, stimulus off and on), seeds 20000-20059, N = 60: reported, not gated. The neural fly does not react to the beam, so this part differs from version 6 only by #59's calibration.

## Threshold

- Adopt when P(candidate faster) ≥ `0.90` by paired bootstrap, 10,000 resamples, seed 42, on `time`.
- Below the threshold the answer is "not adopted", including at 0.85.

## Selection rule

None. One candidate, no knob.

## Pre-declared exclusions / sensitivity checks

- Capture: a bootstrap of its own on `capture`. If P(candidate misses fewer flies than v1) < 0.10 → not adopted even if `time` passes. (Capture rates under version 7 are unknown, so the floor is relative to v1 instead of #72's fixed 0.97. Proposed by the agent; the user approved the gate as written on 2026-11-26, before anything was measured.)
- Per model: any of the three candidate models with P(faster than pooled v1) < 0.50 on `time` → **undecided**.
- If both conditions capture fewer than half of the 600 episodes, the comparison says little about a usable aimer → **undecided**, reported as "neither works under version 7".
- An episode set with a missing seed is a failed run, not a smaller N.

## Gates

1. Offline: the bootstraps above → P(win), CI, pooled and per model.
2. Deployed: none — nothing ships.

## Decision rule

- **adopt** — the time gate passes and no exclusion fires: `accel-pen-rule` becomes aimer v2 (README, lineage).
- **reject** — the time gate fails or the capture exclusion fires: v1 stays the learned reference.
- **undecided** — a per-model or the "neither works" condition fires: numbers reported, the user decides.

## Verdict

Measured 2026-11-26 on vast.ai instance 62693179 from the bundle of commit b967875 (the candidate after `gate/v1.csv` was frozen in 6e40c1c). `gate/accel-pen-rule.csv` sha256 `1a7fbb9333bc644dcba973219a478cef387e0b8d242f707a42fbb4ae526ea567`.

**Decision: adopt.** `accel-pen-rule` becomes aimer v2.

Rule fly, seeds 20000-20199, per episode:

| condition | captured | time | misfires | grazes | wall shots |
| --- | --- | --- | --- | --- | --- |
| v0 (rule aimer, reference) | 192/200 (0.960) | 6.037 s | 5.010 | 4.770 | 0.240 |
| v1 (3 models) | 468/600 (0.780) | 5.442 s | 6.408 | 6.013 | 0.372 |
| `accel-pen-rule` (3 models) | 506/600 (0.843) | 4.851 s | 6.205 | 5.928 | 0.252 |

Per model: v1 s0 0.715 / 5.976 s, s1 0.730 / 5.979 s, s2 0.895 / 4.372 s; candidate s0 0.860 / 4.697 s, s1 0.800 / 5.072 s, s2 0.870 / 4.784 s.

Paired bootstrap, candidate against v1 (10,000 resamples, seed 42):

| target | v1 | candidate | Δ | 95% CI | P(candidate better) |
| --- | --- | --- | --- | --- | --- |
| time (gated) | 5.4422 | 4.8511 | -0.5911 | [-0.8793, -0.3034] | 1.000 |
| capture, as miss rate (exclusion) | 0.2200 | 0.1567 | -0.0633 | [-0.1050, -0.0217] | 0.998 |
| misfires (reported) | 6.4083 | 6.2050 | -0.2033 | [-0.7784, +0.3667] | 0.761 |
| grazes (reported) | 6.0133 | 5.9283 | -0.0850 | [-0.6300, +0.4483] | 0.627 |
| wall shots (reported) | 0.3717 | 0.2517 | -0.1200 | [-0.1967, -0.0450] | 1.000 |

- Time gate: P 1.000 ≥ 0.90 → pass.
- Capture exclusion: P(candidate misses fewer) 0.998, not below 0.10 → does not fire.
- Per model, P(faster than pooled v1): s0 1.000, s1 0.957, s2 0.999, none below 0.50 → does not fire.
- "Neither captures half": 468 and 506 of 600 → does not fire.
- Deployed gate: none.

What the gate does not say (read before using the verdict):

- Both learned aimers got worse under version 7; neither was trained against a fly that reacts. Version 6 on the same seeds: v1 584/600 at 3.026 s, candidate 589/600 at 2.611 s.
- The rule aimer v0 captures more flies than either (0.960 against 0.843 and 0.780) though it is slower in mean time (6.037 s, a miss counted as 10 s). The gate compared the candidate with v1 only. "v2" means the learned reference, not the best aimer on capture under version 7.
- About 6 shots per episode end as misfires, and about 95% of those are grazes: the beam reaches the fly, the fly leaves before 0.15 s. Wall shots are 0.24 to 0.37 per episode.

Neural fly (calibrated profile, seeds 20000-20059, 60 episodes per model; reported, not gated; the neural fly does not react to the beam):

| condition | stimulus off: captured, time, misfires (grazes, wall) | stimulus on |
| --- | --- | --- |
| v0 | 0.983, 5.285 s, 1.233 (1.100, 0.133) | 0.983, 5.395 s, 1.633 (1.517, 0.117) |
| v1 (3 models) | 0.906, 3.971 s, 1.750 (1.556, 0.183) | 0.933, 4.044 s, 2.139 (1.928, 0.200) |
| `accel-pen-rule` (3 models) | 0.956, 3.263 s, 1.861 (1.772, 0.083) | 0.972, 3.132 s, 2.083 (1.994, 0.078) |
