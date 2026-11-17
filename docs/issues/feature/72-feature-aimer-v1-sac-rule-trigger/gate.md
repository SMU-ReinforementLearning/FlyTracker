# Gate — SAC aiming with rule firing (aimer v1 candidate) vs rule baseline (aimer v0), env version 6

<!-- Every section above "Verdict" was written BEFORE the candidate was measured on the gate seeds. -->

Written 2026-11-18 (KST), before the candidate was run on seeds 20000-20199. Numbers that
existed when this was written:

- Env version 5 (#51), same seeds, laser always on: `sac-beam-assist` 2.941 s, 585/600 captured; baseline 4.858 s, 198/200. This is why the candidate is expected to pass on time.
- Env version 6 (#69), baseline on the gate seeds: 4.894 s, 198/200, 0.50 misfires per episode (frozen below).
- Env version 6, candidate, 9 episodes on seeds 10000-10002 (not gate seeds), run once to check that the adapter loads and steers as the models did under version 5: all 9 captured; times 3.07, 2.75, 1.65 / 3.03, 2.61, 8.71 / 1.31, 1.33, 2.41 s; misfires 2, 0, 0 / 1, 0, 8 / 0, 1, 0 (12 in 9 episodes, 8 of them in one episode). Under version 5 the same models took 3.03, 2.73, 1.63 / 3.02, 2.59, 5.37 / 1.29, 1.19, 2.40 s on this machine (#61). So the candidate is expected to misfire more than the baseline; the misfire rule below was written knowing this.

## Question

Under env version 6 (shots of 0.15 s, capture = a whole shot on the fly), does the #51 SAC
aimer, steering as trained and firing by the baseline's rule, catch the rule fly faster than
the rule baseline without losing flies, over the 200 evaluation seeds 20000-20199? If yes
it becomes aimer v1; the rule baseline stays as v0.

## Baseline

- Predictions file: `gate/baseline.csv` — sha256 `70a62ab3d45dc31d10524a514587e59edec48bed0e217f0d3cb32b9559808b1c` (frozen; regenerate = a new gate)
- Produced by: `measure_aimers.py baseline --out data/rule-fly/baseline` on this branch (`load_opponent("baseline", ...)`, default `EnvConfig`), 2026-11-18, local machine (Windows, CPU). `gate/baseline.csv` is a byte copy of that folder's `gate.csv`. Its values equal #69's `data/rule-fly` rows for the 1.25 mm trigger.
- Metric value: time 4.894 s (mean), capture rate 0.990 (198/200), misfires 0.500 per episode
- Truth file: `gate/truth.csv` — sha256 `0f577c4c706f728dccaa660ab6c7640e4eeb69c84e112ddcc29d8396d5f3669b` (capture = 1, time = 0, misfires = 0 for every id)

## Candidate(s)

| name | what changes vs baseline | predictions file (filled when measured) |
| --- | --- | --- |
| `sac-beam-assist+rule-fire` | Steering: the final `model.zip` of `sac-beam-assist-s0/-s1/-s2` (#51, env version 5, 1,000,000 steps, tracking assist 0.2), fed the observation without `shot`. Firing: the baseline's rule, unchanged (`RuleAimer.wants_fire`: visible and estimated beam distance within 1.25 mm). | `gate/sac-beam-assist-rule-fire.csv` (mean of the three models per seed); per model `data/rule-fly/sac-beam-assist-s<k>/gate.csv` |

- Model files (sha256): s0 `51b3ae38b0f6…`, s1 `dcd7aaca8f89…`, s2 `af296f02dbc8…` (full hashes in each `meta.json`). They are the files evaluated in #51; nothing is trained here.
- Loaded by `load_opponent`, which for an env version 5 aimer model drops `shot` from the observation, applies the run's tracking assist, and sets `fire` by the rule. The policy never learned to fire and does not see whether a shot is running.

## Metric

- Per evaluation seed: `time` = seconds from reset until capture, 10 s when not captured. `capture` = 1 if captured. `misfires` = shots during which the beam left the fly.
- One episode per seed, deterministic policy. A candidate's value per seed is the mean over its 3 models (`measure_aimers.py mean`).
- Formula: mean over the 200 seeds = `mae` against the truth (time 0, capture 1, misfires 0). Lower is better. In the tool's `capture` rows the value is the miss rate.
- Rounding: none. Clip: none.
- Targets: `time` (gated), `capture` (reported; exclusion below), `misfires` (reported; rule below).
- Tool: `paired_bootstrap.py --truth gate/truth.csv --a gate/baseline.csv --b gate/<cand>.csv --targets time --metric mae --lower-is-better --resamples 10000 --seed 42 --threshold 0.90`

## Data

- Item ids: evaluation seeds 20000-20199, N = 200, listed in `gate/truth.csv`
- Items that must be present: all 200
- The models were trained with env seeds 0, 1, 2 and evaluated during training on 10000-10002; #51 gated them on these same 200 seeds under version 5, so the seeds are not fresh for the models, but nothing was selected or tuned on them (the final model was fixed in advance, and nothing is tuned here).

## Threshold

- Adopt when P(candidate faster) ≥ `0.90` by paired bootstrap, 10,000 resamples, seed 42, on `time`
- Below the threshold the answer is "not adopted", including at 0.85

## Selection rule

None — a single candidate. The trigger radius is the baseline's (1.25 mm = the capture radius) and is not tuned; #69's sweep of the radius was done with the baseline only and is not used to pick a value here.

## Pre-declared exclusions / sensitivity checks

- Pooled capture rate below 0.97 → not adopted even if `time` passes.
- Any single model with P(faster than baseline) < 0.50 on `time` → **undecided**: the result depends on the training seed.
- Misfires: no cost has been set for a misfire (#69: "measure first, then decide"), so misfires do not gate. But if the candidate's pooled misfires per episode exceed twice the baseline's (more than 1.00), the verdict is **undecided — the user decides**, because "faster but firing at nothing more than twice as often" is a trade the user has not been asked about. P(candidate misfires less) is reported either way.
- A run that covers fewer than 200 seeds is void.

## Reported, not gated: the neural fly

The same aimers against the neural fly (#31, bundled assets), seeds 20000-20059 (N = 60, `gate/truth-neural.csv`, sha256 `b31947f3e8ef7ce7e620a9ae56e264ef7da77b9fe145ff49c43a9260e9dbb196`), once with the aim stimulus off and once on. The same bootstrap is run and its tables pasted. It carries no decision: the aimers were trained against the rule fly only, and "v1" here means "the reference aimer trained against the rule fly". If the candidate is slower than the baseline against the neural fly, the verdict says so in its first lines and the README states it next to the v1 numbers.

## Gates

1. Offline: `paired_bootstrap.py` on the files above → P(win), CI, pooled and per model.
2. Deployed: none — nothing ships; the viewer replays recorded episodes.

## Decision rule

- **adopt** — the gate passes and no exclusion fires: `sac-beam-assist+rule-fire` is aimer v1 under env version 6. README and the issue page name the rule aimer v0 and this one v1, and later results report both. The rule aimer stays the fixed yardstick.
- **reject** — the gate fails or the capture exclusion fires: the rule aimer stays the only reference; the numbers go into the management doc; no tweak is re-run under this gate.
- **undecided** — a per-model or misfire condition fires: the numbers are reported, nothing is renamed, and the user is asked.

Whatever the verdict, the candidate's episodes are published under issue #72.

## Verdict

Measured 2026-11-18 (KST) on the local machine. **Adopt: `sac-beam-assist+rule-fire` is aimer v1 under env version 6. Against the neural fly it is faster on average but loses far more flies than v0 and, with the stimulus off, misfires three times as often; that is stated wherever v1's numbers are shown.**

Unedited tool output with the sha256 of every file: [`gate/bootstrap-rule-fly.md`](gate/bootstrap-rule-fly.md), [`gate/bootstrap-neural-fly-nostim.md`](gate/bootstrap-neural-fly-nostim.md), [`gate/bootstrap-neural-fly-stim.md`](gate/bootstrap-neural-fly-stim.md). The baseline and truth hashes match the ones frozen above. In the tool's `capture` rows the value is the miss rate; the tables below convert it.

### Gate: rule fly, seeds 20000-20199 (N = 200)

| aimer | time, mean (s) | Δ vs v0 | 95 % CI of Δ | P(faster) | captured | capture rate | misfires / episode | P(fewer misfires) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v0 rule aimer | 4.894 | | | | 198/200 | 0.990 | 0.500 | |
| candidate, pooled | 3.026 | −1.869 | [−2.161, −1.560] | 1.000 | 584/600 | 0.973 | 0.600 | 0.122 |
| s0 | 3.034 | −1.860 | [−2.189, −1.506] | 1.000 | 193/200 | 0.965 | 0.535 | |
| s1 | 3.356 | −1.538 | [−1.902, −1.152] | 1.000 | 193/200 | 0.965 | 0.890 | |
| s2 | 2.686 | −2.208 | [−2.541, −1.858] | 1.000 | 198/200 | 0.990 | 0.375 | |

- Threshold P(faster) ≥ 0.90: **PASS** (1.000).
- Capture rate below 0.97: does not fire (0.973), by two episodes out of 600. P(candidate misses fewer) = 0.072, reported only: it loses 16 of 600 where v0 loses 2 of 200.
- Any model with P < 0.50: does not fire (1.000 for all three).
- Misfires more than twice v0's (1.00): does not fire (0.600). The difference from 0.500 is not established (95 % CI of Δ [−0.068, +0.262]); s1 alone is at 0.890.
- Against version 5 (laser always on, #51): 2.941 s and 585/600 then, 3.026 s and 584/600 now. The shot rule costs the candidate 0.09 s and one capture; it cost v0 0.04 s (4.858 to 4.894).

### Reported, not gated: neural fly, seeds 20000-20059 (N = 60)

| stimulus | aimer | time, mean (s) | Δ vs v0, 95 % CI | P(faster) | captured | capture rate | P(misses fewer) | misfires / episode | P(fewer misfires) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| off | v0 | 5.110 | | | 59/60 | 0.983 | | 0.617 | |
| off | candidate, pooled | 4.258 | −0.852 [−1.558, −0.114] | 0.989 | 155/180 | 0.861 | 0.001 | 1.939 | 0.000 |
| off | s0 / s1 / s2 | 5.351 / 3.871 / 3.552 | | 0.320 / 0.999 / 1.000 | 44 / 57 / 54 of 60 | 0.733 / 0.950 / 0.900 | | 2.133 / 2.400 / 1.283 | |
| on | v0 | 5.397 | | | 59/60 | 0.983 | | 1.933 | |
| on | candidate, pooled | 4.058 | −1.339 [−1.946, −0.712] | 1.000 | 164/180 | 0.911 | 0.012 | 2.039 | 0.388 |
| on | s0 / s1 / s2 | 4.810 / 3.670 / 3.693 | | 0.908 / 1.000 / 1.000 | 51 / 57 / 56 of 60 | 0.850 / 0.950 / 0.933 | | 2.567 / 2.000 / 1.550 | |

- Had the gate's exclusions applied here, the capture exclusion would fire in both settings (0.861, 0.911 < 0.97) and, with the stimulus off, the per-model one (s0, P = 0.320) and the misfire one (1.939 > 2 × 0.617). They do not apply: this section was declared as reported only, before measuring.
- Reading: the candidate reaches the neural fly sooner but cannot hold it. It was trained against the rule fly only, and the neural fly changes direction far more often (#61).
- With the stimulus on, v0's own misfires triple (0.617 to 1.933): the stimulus is triggered by an aim held within 2.5° for 120 ms, which is the moment before a shot.

### Decision

- **adopt**: gate passed, no exclusion fired. README and the issue page name the rule aimer v0 and `sac-beam-assist+rule-fire` v1 and show both. v0 stays the fixed yardstick.
- v1 here means "three models"; no single model is chosen from these seeds.
- Not shown by this gate: that v1 is the better aimer against the neural fly (it is faster on average and worse at not losing the fly), or that it fires well (it does not decide when to fire; the rule does).

### Deviations from the plan above

- The gate document and the baseline file were written before the candidate was measured on the gate seeds but were not yet committed at that time; they enter the repository together with the results in one commit. The order is recorded only in this session's log.
- All measurements were made on an uncommitted tree on top of 61d2b6b (`gitDirty: true` in every `meta.json`); the code they used is what commit a4a6c12 holds.
- The label change (`+rule-fire`) landed between runs, so `aimer.label` in `meta.json` has the suffix for the stimulus-on runs only. Same models, same code path.
