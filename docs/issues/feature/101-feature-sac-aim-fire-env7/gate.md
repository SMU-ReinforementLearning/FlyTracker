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

(not measured yet)
