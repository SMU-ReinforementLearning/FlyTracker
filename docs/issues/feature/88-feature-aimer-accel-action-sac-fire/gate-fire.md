# Gate — learning to fire on top of a fixed acceleration aim (stage 2 of #88)

<!-- Every section above "Verdict" was written BEFORE any candidate was measured. -->

Written 2026-11-26, before any training run of this stage started. Numbers seen so far:
everything in `gate.md` (stage 1, including the baseline of this gate), and two 3,000-step
smoke runs of the new training path on aim model `accel-pen-rule-s0` with `misfire=1.0`,
evaluated on seeds 20000-20004 only to check that the model loads: without the prior
5/5 captures, 2.722 s, 1.8 misfires per episode; with the rule prior 5/5, 2.674 s, 0.4.
Neither is a candidate (3,000 steps, 5 seeds).

Why this stage: in stage 1 the two conditions that learned to fire together with the aim
ended up never firing (fire action mean about -0.5 at every beam distance), although their
aim was good enough to catch 182-200 of 200 flies had something fired. The user
(2026-11-26) asked for the staged step as proposed: aim fixed, fire started from the rule,
recent observations given to the fire decision.

## Question

With the aim fixed to an `accel-pen-rule` model, does a learned fire decision catch the
fly faster than the baseline's fire rule on the same aim, without losing flies and without
more misfires, over evaluation seeds 20000-20199?

## Baseline

- Predictions file: `gate/accel-pen-rule.csv` — sha256 `9996b2a30098ff52da88c1821e114f02d3bbe0bbf8c255d31800c78f7a091e38` (frozen; produced in stage 1 on 2026-11-26, the per-seed mean of the three `accel-pen-rule` models with rule fire)
- Per aim model, for the per-seed check: `data/accel-pen-rule-s0/gate.csv` `f01bd040...2faf`, `-s1` `edda5bc8...d37b`, `-s2` `611fba48...4629` (full sha256 in `gate/bootstrap-output.md`)
- Metric value: time 2.611 s (mean), capture rate 0.9817 (589/600), misfires 0.472 per episode
- Truth file: `gate/truth.csv` — sha256 `0f577c4c706f728dccaa660ab6c7640e4eeb69c84e112ddcc29d8396d5f3669b`

References, not baselines of this gate: v0 4.894 s, 198/200, 0.500 misfires; v1 3.026 s, 584/600, 0.600.

## Candidate(s)

| name | fire value starts from | misfire weight | predictions file (filled when measured) |
| --- | --- | --- | --- |
| `fire-m1` | nothing (fires when the value is above 0) | 1.0 | `gate/fire-m1.csv` |
| `fire-m5` | nothing | 5.0 | `gate/fire-m5.csv` |
| `fire-prior-m1` | the rule (value ± 0.5 by the rule's verdict) | 1.0 | `gate/fire-prior-m1.csv` |
| `fire-prior-m5` | the rule | 5.0 | `gate/fire-prior-m5.csv` |

- Fixed aim (`--aim <run>`): the `accel-pen-rule` model steers, deterministic, exactly as in stage 1's evaluation. It is not trained further. Training seed k uses aim model `accel-pen-rule-s<k>` (k = 0, 1, 2).
- The policy outputs one value per step and observes the full observation, `shot` included, stacked over the last 4 steps (`--frame-stack 4`, 0.08 s), so that it can see how the aim error has been moving.
- Without the prior the shot is fired when the value is above 0. With the rule prior (`--fire-prior rule`) the rule's verdict is added first: +0.5 when `RuleAimer.wants_fire` says fire, -0.5 otherwise. Value 0 then fires exactly as the rule; below -0.5 it holds a shot the rule would take; above +0.5 it takes a shot the rule would not.
- Misfire weight: subtracted once per shot that leaves the fly. The capture reward is 10, so a shot pays off when its chance of holding is above weight ÷ (10 + weight): 9 % for 1.0, 33 % for 5.0 (ignoring the time a wasted shot costs). 1.0 is the heavier weight of stage 1; 5.0 was chosen by the agent to make a second condition that should hold fire more. Neither is tuned. Other reward terms are the defaults (`action_change` does not matter here: the aim is fixed).
- Two starts because stage 1's failure may or may not return once the aim is good from the first step: `fire-m*` tests the fixed aim alone, `fire-prior-m*` adds the rule start.

Training, identical except for the options above:

- `scripts/train.py --algo sac --steps 500000 --eval-every 50000 --eval-episodes 3 --seed <k> --device cpu --aim <accel-pen-rule-s<k> run> --frame-stack 4 --reward misfire=<w> [--fire-prior rule]`
- Stable-Baselines3 `SAC("MlpPolicy")` defaults, `OMP_NUM_THREADS=1`, default `EnvConfig`, rule fly, environment version 6.
- 500,000 steps: half of stage 1, because only one output is learned and episodes end after about 130 steps with this aim. It is part of the candidate.
- The candidate model is the **final** `model.zip`. No checkpoint is picked.
- Platform: recorded in the management doc when training starts.

## Metric

As in `gate.md`: per evaluation seed `time` (10 s when not captured), `capture`, `misfires`; `deterministic=True` through `load_opponent`, which rebuilds the aim model from the run's `aim/` folder; a candidate's value per seed is the mean over its 3 models; `mae` against the truth, lower is better; no rounding, no clip.

- Targets: `time` (gated), `capture` and `misfires` (reported; rules below).
- Tools: #72's `measure_aimers.py <run> --out <dir>` on the local Windows machine, `measure_aimers.py mean`, then `paired_bootstrap.py --truth gate/truth.csv --a gate/accel-pen-rule.csv --b gate/<cand>.csv --targets time --metric mae --lower-is-better --resamples 10000 --seed 42 --threshold 0.90`

## Data

- Item ids: evaluation seeds 20000-20199, N = 200, all must be present.
- Training never resets the environment with these seeds explicitly (training env seed = 0, 1, 2; in-training evaluation uses 10000-10002). The aim models were not trained on them either.
- These 200 seeds were already used to gate the aim models in stage 1. The baseline of this gate is one of them, so candidate and baseline share whatever the aim owes to that look; the comparison between fire decisions on the same aim is still paired and fair.

## Threshold

- Adopt when P(candidate faster) ≥ `0.90` by paired bootstrap, 10,000 resamples, seed 42, on `time`.
- Below the threshold the answer is "not adopted", including at 0.85.
- Four candidates against one baseline: with baseline-quality candidates the chance that at least one crosses by luck is about 1 − 0.9⁴ ≈ 34 %. The threshold is not relaxed; the verdict states how many passed.

## Selection rule

None. Each candidate is gated on its own. Comparisons between the four are descriptive.

## Pre-declared exclusions / sensitivity checks

- Candidate capture rate (mean over its 3 models) below 0.97 → not adopted even if `time` passes.
- Any training seed k whose model has P(faster than `accel-pen-rule-s<k>` with rule fire) < 0.50 on `time` → **undecided**.
- Pooled misfires per episode above the baseline's 0.472 → **undecided — the user decides**: time bought with more misfires is a trade nobody has priced.
- `time` fails the gate, but misfires pass a bootstrap of their own at P(fewer) ≥ 0.90 while `time` has P(faster) ≥ 0.50 and capture ≥ 0.97 → **undecided — the user decides** (fewer misfires at no cost in time is what the fire rule's weakness in #85 suggested looking for). Any other failure of the time gate → reject.
- A run that does not reach 500,000 steps voids that candidate; it is re-run with the same seed.
- A policy that never fires, or that fires exactly as the rule, is a valid measurement.

## Gates

1. Offline: the bootstraps above → P(win), CI, pooled and per training seed.
2. Deployed: none — nothing ships.

## Decision rule

- **adopt** — the time gate passes and no exclusion fires: the fire decision is learned on top of the fixed aim. Whether the pair replaces v1 is a separate gate against v1.
- **reject** — the time gate fails (outside the declared misfire case) or the capture exclusion fires. The fire value by beam distance and the shots in training are reported, as in stage 1; the gate is not re-run with a tweak.
- **undecided** — a per-seed or misfire condition fires: the numbers are reported and the user is asked.

## Verdict

Measured 2026-11-26 on the local Windows machine. All 12 runs reached 500,000 steps (trained on vast.ai, 12 processes on one 16-core instance, 03:02-06:3x UTC; archive sha256 verified before the instance was destroyed). Tool output, unedited: `gate/bootstrap-output-fire.md` (sha256 of every input at its top; the baseline's is the frozen one).

**Decision: reject, all four. 0 of 4 candidates passed the time gate.** With the aim fixed, none of the learned fire decisions catches the fly faster than the fire rule on the same aim; every one is slower.

Gated and reported rows (A = `accel-pen-rule` with rule fire, N = 200, 10,000 resamples, seed 42):

| candidate | time A | time B | Δ (B−A) | 95% CI | P(faster) | capture (of 600) | misfires/ep (A 0.472) | P(fewer misfires) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `fire-m1` | 2.6114 | 2.6760 | +0.0646 | [+0.0411, +0.0926] | 0.000 FAIL | 0.9800 (588) | 1.060 | 0.000 |
| `fire-m5` | 2.6114 | 2.8394 | +0.2280 | [+0.1616, +0.3020] | 0.000 FAIL | 0.9800 (588) | 0.378 | 0.987 |
| `fire-prior-m1` | 2.6114 | 2.6584 | +0.0470 | [+0.0193, +0.0835] | 0.000 FAIL | 0.9783 (587) | 0.617 | 0.000 |
| `fire-prior-m5` | 2.6114 | 2.6359 | +0.0245 | [+0.0087, +0.0437] | 0.001 FAIL | 0.9817 (589) | 0.425 | 0.936 |

Per training seed, P(faster than `accel-pen-rule-s<k>` with rule fire) on time, s0 / s1 / s2: `fire-m1` 0.000 / 0.003 / 0.000; `fire-m5` 0.000 / 0.000 / 0.000; `fire-prior-m1` 0.000 / 0.000 / 0.002; `fire-prior-m5` 0.001 / 0.137 / 0.000. All twelve models are slower than their own aim model with the rule.

Exclusions and conditions:

- Capture below 0.97: did not fire for any candidate (0.9783-0.9817; baseline 0.9817).
- Per-seed P < 0.50: fired for all twelve models. Pooled misfires above 0.472: fired for `fire-m1` and `fire-prior-m1`. Both would have made a passing candidate undecided; none passed, so the verdict is the time gate's.
- Declared misfire case (time fails, misfires P(fewer) ≥ 0.90, time P(faster) ≥ 0.50, capture ≥ 0.97): `fire-m5` and `fire-prior-m5` have fewer misfires (P 0.987, 0.936) and capture ≥ 0.97, but time P(faster) is 0.000 and 0.001, not ≥ 0.50. The case does not apply → reject, not undecided. The fewer misfires were paid for in time.

Descriptive (not gated; from the same tool output):

- The rule start helps: `fire-prior-m5` vs `fire-m5` time −0.204 s (P 1.000); `fire-prior-m1` vs `fire-m1` misfires −0.443 (P 1.000), time −0.018 s (P 0.801).
- The heavier misfire weight cuts misfires: with the prior 0.617 → 0.425 (P 1.000); without it 1.060 → 0.378, at +0.16 s.
- Against v1 (3.026 s, 0.600 misfires) all four are faster (P 0.983-1.000); that is the aim's doing, already seen in stage 1.

What the policies do (`data/fire-only.md`, required by the decision rule; deterministic, the gate's 200 episodes, steps where a new shot can start):

- Unlike stage 1, none collapsed to never firing: every model fires and captures.
- Without the prior the policy rebuilt something close to the rule but worse: the fire value falls with beam distance (median about 0 inside 1.25 mm, −0.4 to −0.8 beyond), `m1` models take 32-51 % of their shots where the rule would not, and those shots hit 11-27 % of the time against 70-76 % for the shots the rule would also take. `m5` models take few such shots (5-10 %) but hold on 81-90 % of the steps where the rule says fire, which is where their extra 0.15-0.36 s goes.
- With the prior and weight 5.0 the policy almost only removes shots: 0.7-2.0 % of its shots are ones the rule would not take, and it holds on 38-49 % of the steps where the rule says fire. Shots it does take hit 69-72 %, about the rule's own rate, so the held steps removed some misfires (0.472 → 0.425) and cost 0.025 s.
- In no model do the shots the rule would not take hit more often than the ones it would. Nothing here found an earlier good shot than the rule's.
- Training curves (`data/training-logs-fire.md`): mean episode length and reward are flat from 50,000 to 500,000 steps in all 12 runs (e.g. `fire-prior-m5-s2` 115 → 115 steps, `fire-m1-s2` 119 → 123). Sampled-action play (table 2 of `data/fire-only.md`) looks like the deterministic play: 1.2-2.3 shots per episode, fire sd 0.15-0.23.

Consequences:

- `accel-pen-rule` with rule fire remains the best pair measured in #88.
- Scope of this verdict (added 2026-11-26 after the user's review; the rows and the decision above are unchanged): it answers only this gate's question, "faster than the rule". It does not close fire learning. The rule mirrors the capture condition, so on time there was at most about 0.07 s to win (0.472 misfires x 0.15 s lock-out; the agent's bound, not measured), and the misfire weight pulled against time. The user wants a policy that fires on its own and wants misfires reduced for a reason that exists in the environment (safety, damage, the fly reacting to a grazing shot). The next gates ask different questions: "as good as the rule without the rule" (non-inferiority, no misfire weight), then fire learning in an environment where a misfire has a cost.
- Per the decision rule the gate is not re-run with a tweak. A longer run (1,000,000 steps) would be a new gate; the flat curves give no sign that it would change the answer.
- Limit: 200 evaluation seeds already used in stage 1; one observation window (4 steps); two misfire weights, neither tuned; rule fly only.
