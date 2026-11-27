# Gate — aim and fire learned under environment version 7

<!-- Every section above "Verdict" was written BEFORE any candidate was measured. -->

Written 2026-11-26, before any model of this issue was trained. Numbers known when this was written (#91, version 7, seeds 20000-20199, rule fly): v0 192/200, 6.037 s, 0.240 wall shots per episode; v1 468/600, 5.442 s, 0.372; aimer v2 (`accel-pen-rule`, trained under version 6) 506/600, 4.851 s, 6.205 misfires of which 5.928 grazes and 0.252 wall shots.

The training settings and both gates below were proposed by the agent and approved by the user as written on 2026-11-27 ("다 승인"), before anything was trained. The user had set the price of a wall shot (1 s main, 0 s control, 3 s beside it) and that the aim is trained again under version 7.

## Questions

- **A (aim).** Does an aimer trained under version 7 against the escaping rule fly, firing by the baseline rule (`v7-rule`), catch the fly faster than aimer v2, without catching fewer flies?
- **B (fire).** With the same training, does a policy that also learned when to fire, with a wall shot priced at 1 s (`v7-fire-w1`), do better than the baseline rule (`v7-rule`) on time and wall shots together?

## Baselines

- Gate A: aimer v2 under version 7. Predictions file: #91's `docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/gate/accel-pen-rule.csv`, frozen, sha256 `1a7fbb9333bc644dcba973219a478cef387e0b8d242f707a42fbb4ae526ea567`. Not regenerated.
- Gate B: `v7-rule` of this issue, `gate/v7-rule.csv` with the score columns — measured first and frozen by sha256 here before any fire condition is measured: `c51d1ddbac79b57946dc7eb3cfd312f869eb8b65231b98becc83aa75e0675396` (measured 2026-11-27 00:26 UTC on the training instance, before any fire condition was measured)
- Truth file: `gate/truth.csv` (capture 1, every other column 0, ids 20000-20199) — sha256 `eb8cdd78c937e285a4a0f589e05c385a5a903a446334c3e8631ab49b7ce76c57`

## Candidates

All: SAC, 1,000,000 steps, acceleration action, action-change weight 1.0, no tracking assist, no frame stack (the settings of #88's `accel-pen-rule` and joint conditions), environment version 7, rule fly, training seeds 0, 1, 2. The final model is used; no checkpoint is selected.

| name | options added to `scripts/train.py --algo sac --steps 1000000 --eval-every 50000 --eval-episodes 3 --device cpu --control accel --reward action_change=1.0` | gate |
| --- | --- | --- |
| `v7-rule` | `--fire rule` | A (candidate), B (baseline) |
| `v7-fire-w0` | `wall_shot=0` | reported (control: no price) |
| `v7-fire-w1` | `wall_shot=0.5` | B (candidate) |
| `v7-fire-w3` | `wall_shot=1.5` | reported |

Training reward for a wall shot: 0.5 per second of price, the time penalty of one second (0.01 per 0.02 s step). This is a training setting, not the metric; the metric below uses seconds.

## Metric

- Per evaluation seed: `time` (seconds to capture; 10 s when not captured), `capture`, `misfires`, `grazes`, `wall_shots`; `score_w1 = time + 1.0 x wall_shots`, `score_w3 = time + 3.0 x wall_shots` (seconds). A condition's value per seed is the mean over its three models.
- `mae` against the truth, lower is better; no rounding, no clip.
- Gate A target: `time`. Gate B target: `score_w1`.
- Reported, not gated: `time`, `wall_shots`, `grazes`, `misfires`, shots per episode for every condition; `score_w3` for `v7-fire-w3` against `v7-rule`; `time` for `v7-fire-w0` against `v7-rule`; v0.
- Tools: #91's `measure_v7.py <run> --out <dir>` and `measure_v7.py mean`; `score.py` in this folder adds the two score columns; `paired_bootstrap.py --metric mae --lower-is-better --resamples 10000 --seed 42 --threshold 0.90`.
- Where: one vast.ai instance with the library versions of #91's measurement (torch 2.15.0, stable-baselines3 2.9.2, gymnasium 1.4.0). Gate A's baseline file comes from #91's instance with the same versions; both sides are deterministic policies.

## Data

- Item ids: evaluation seeds 20000-20199, N = 200, rule fly, default `EnvConfig` of version 7. All must be present.
- Training evaluations use seeds from 10000; the gate's seeds are not used in training.
- Neural fly (calibrated profile, stimulus off and on), seeds 20000-20059: reported, not gated. It does not react to the beam.

## Threshold

- Adopt when P(candidate better) >= `0.90` by paired bootstrap, 10,000 resamples, seed 42, on the gate's target. Below it the answer is "not adopted".

## Selection rule

None. No knob is tuned on the gate's seeds: the three prices are fixed conditions, and only `v7-fire-w1` is gated.

## Pre-declared exclusions / sensitivity checks

- Capture (both gates): a bootstrap on `capture`. P(candidate misses fewer flies than its baseline) < 0.10 -> not adopted even if the target passes.
- Per model (both gates): any of the three candidate models with P(better than the pooled baseline) < 0.50 on the target -> **undecided**.
- Gate B, wall shots: if `v7-fire-w1` passes on `score_w1` but has more wall shots per episode than `v7-rule` (P(fewer) < 0.50), it is reported as "faster, not safer" and the user decides -> **undecided**.
- A policy that never fires is a valid measurement (time 10 s, capture 0); it fails the gate.
- An episode set with a missing seed is a failed run, not a smaller N.

## Second stage, declared now

If Gate B is not passed and `v7-fire-w1` fires fewer than 0.5 shots per episode on the gate's seeds (pooled), the joint training did not learn to fire (as in #88), and the fire decision is trained alone: the aim fixed to the `v7-rule` model of the same training seed (`--aim`), `--fire-prior rule`, `--frame-stack 4`, 500,000 steps, prices 0, 0.5 and 1.5. Its gate is the same as Gate B (same baseline file, same target and exclusions), written as `gate-fire.md` before those models are measured. If Gate B fails while the policy does fire, no second stage is run from this gate; the result is reported and the user decides.

## Gates

1. Offline: the bootstraps above -> P(win), CI, pooled and per model.
2. Deployed: none — nothing ships.

## Decision rule

- Gate A **adopt** -> `v7-rule` becomes aimer v3 (README, lineage). **reject** -> v2 stays.
- Gate B **adopt** -> the learned fire decision replaces the baseline rule for that aimer; which aimer is "v3" then follows the better of the two on `score_w1`, stated in the verdict. **reject** -> rule fire stays; the trade-off table at the three prices is still reported.
- **undecided** -> numbers reported, the user decides.

## Verdict

Measured 2026-11-27 (UTC) on the training instance, commit b1b5aef; `gate/v7-rule.csv` frozen in bbaeec5 before the fire conditions were measured. Bootstraps: `paired_bootstrap.py`, 10,000 resamples, seed 42, N = 200. The `capture` rows of the tool show the miss rate (lower is better).

### Measured (rule fly, seeds 20000-20199, 3 models pooled)

| condition | capture | time (s) | misfires | grazes | wall shots | shots/ep | `score_w1` | `score_w3` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aimer v2 (`accel-pen-rule`, #91) | 0.843 | 4.851 | 6.205 | 5.928 | 0.252 | — | 5.103 | 5.606 |
| `v7-rule` | 0.478 | 7.485 | 6.648 | 5.963 | 0.610 | 7.14 | 8.095 | 9.315 |
| `v7-fire-w0` | 0.003 | 9.985 | 12.287 | 1.467 | 10.692 | 12.29 | 20.677 | 42.060 |
| `v7-fire-w1` | 0.000 | 10.000 | 0.063 | 0.000 | 0.063 | 0.07 | 10.063 | 10.190 |
| `v7-fire-w3` | 0.000 | 10.000 | 0.025 | 0.000 | 0.022 | 0.03 | 10.022 | 10.065 |

Per model, capture / time: `v7-rule` s0 0.690 / 6.131, s1 0.420 / 7.891, s2 0.325 / 8.433. `v7-fire-w0` s0 0.005 / 9.958 (19.0 wall shots), s1 0.000 / 10.000 (4.7), s2 0.005 / 9.997 (8.4). `v7-fire-w1` and `v7-fire-w3`: every model 0.000 / 10.000, at most 0.18 shots per episode.

### Gate A — `v7-rule` against aimer v2, target `time`

| target | v2 | `v7-rule` | Δ | 95% CI | P(`v7-rule` better) |
| --- | --- | --- | --- | --- | --- |
| time | 4.8511 | 7.4850 | +2.6338 | [+2.3359, +2.9289] | 0.000 |
| miss rate | 0.1567 | 0.5217 | +0.3650 | [+0.3217, +0.4083] | 0.000 |
| misfires | 6.2050 | 6.6483 | +0.4433 | [-0.2067, +1.0767] | 0.091 |
| grazes | 5.9283 | 5.9633 | +0.0350 | [-0.5750, +0.6267] | 0.456 |
| wall shots | 0.2517 | 0.6100 | +0.3583 | [+0.2750, +0.4433] | 0.000 |

Per model on time, against pooled v2: s0 +1.280 (P 0.000), s1 +3.040 (P 0.000), s2 +3.582 (P 0.000).

**Gate A: reject.** P = 0.000 < 0.90; the capture exclusion fires as well (P(fewer misses) 0.000). Aimer v2 stays; there is no aimer v3.

### Gate B — `v7-fire-w1` against `v7-rule`, target `score_w1`

| target | `v7-rule` | `v7-fire-w1` | Δ | 95% CI | P(`v7-fire-w1` better) |
| --- | --- | --- | --- | --- | --- |
| `score_w1` | 8.0950 | 10.0633 | +1.9684 | [+1.6899, +2.2477] | 0.000 |
| miss rate | 0.5217 | 1.0000 | +0.4783 | [+0.4383, +0.5183] | 0.000 |
| time | 7.4850 | 10.0000 | +2.5150 | [+2.2591, +2.7711] | 0.000 |
| wall shots | 0.6100 | 0.0633 | -0.5467 | [-0.6200, -0.4750] | 1.000 |
| grazes | 5.9633 | 0.0000 | -5.9633 | [-6.3833, -5.5333] | 1.000 |

Per model on `score_w1`, against pooled `v7-rule`: s0 +1.905, s1 +1.915, s2 +2.085, P 0.000 each.

Reported beside it: `v7-fire-w3` on `score_w3` 10.065 against 9.315 (P 0.000); `v7-fire-w0` on time 9.985 against 7.485 (P 0.000) with 10.69 wall shots against 0.61.

**Gate B: reject.** P = 0.000 < 0.90; the capture exclusion fires (the candidate captures nothing). Rule fire stays. The fewer wall shots are not a gain: the policy does not fire at all.

### Trade-off at the three prices

There is no trade-off to choose from. With no price the policy fires often and into the wall (10.7 wall shots per episode, 0.3% capture). With a price of 1 s or 3 s it stops firing (0.07 and 0.03 shots per episode) and captures nothing. No condition learned to fire at the fly.

### Second-stage trigger

Gate B is not passed and `v7-fire-w1` fires 0.07 shots per episode pooled (0.01, 0.01, 0.18 per model), below 0.5: the trigger declared above **fires**. The second stage was not started; it needs the user's go-ahead (cost) and `gate-fire.md` written first. One fact to weigh before it: its fixed aim would be `v7-rule`, which is clearly worse than v2 (capture 0.478 against 0.843), and Gate B's frozen baseline is that same weak aimer.

### Neural fly (reported, not gated; 60 episodes, seeds 20000-20059)

| condition | stimulus off: capture / time | stimulus on: capture / time |
| --- | --- | --- |
| `v7-rule` s0, s1, s2 | 0.950 / 4.517, 0.750 / 6.116, 0.583 / 7.272 | 0.967 / 3.813, 0.800 / 5.581, 0.700 / 6.176 |
| `v7-fire-w0` s0, s1, s2 | 0.117 / 9.607, 0.000 / 10.000, 0.033 / 9.881 | 0.117 / 9.253, 0.000 / 10.000, 0.017 / 9.913 |
| `v7-fire-w1`, `v7-fire-w3` | all 0.000 / 10.000 | all 0.000 / 10.000 |

### Caveats

- `v7-rule` uses the same recipe as v2 (`--control accel`, `action_change=1.0`, rule fire, 1M steps) but was trained under version 7, where the fly is startled by the beam; v2 was trained under version 6. Training against the startled fly gave a worse aimer, with a wide spread between seeds (capture 0.325 to 0.690). Why is not measured here.
- Gate B's baseline was fixed as `v7-rule` before training. Against v2 the fire conditions would lose by more.
- Deployed gate: none.
