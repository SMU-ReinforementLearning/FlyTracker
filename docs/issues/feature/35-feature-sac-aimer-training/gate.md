# Gate — SAC aimer vs rule baseline

<!-- Fill every section above "Verdict" BEFORE the candidate is measured. -->

Written 2026-11-12, before any training run started. The only SAC number seen so far is a
4,000-step throughput smoke run (3 episodes, 0 captures) that is not a candidate.

Environment version 2 (the user's request, 2026-11-12): the code part of #34's commit
f8cfa78 (pitch limit 80° → 89°, `RuleAimer` bands stop at the zenith, `envVersion` in
`config.json`) applied on `origin/main` @ 0cda845. The first baseline file was made on
version 1 (198/200, 4.127 s, sha256 `adcbc9bb…`); it was replaced before any candidate
existed, so this is still the first gate.

## Question

Does an aimer trained with SAC catch the fly faster than the rule baseline, over the 200
evaluation seeds 20000-20199 of the default environment, version 2?

## Baseline

- Predictions file: `gate/baseline.csv` — sha256 `4aec8f8eecf6074d73e37bdd132b6c54b00cd2cd3113e46ed57e2ea36b06b08d` (frozen; regenerate = a new gate)
- Line endings: the first frozen file had CRLF (Python `csv` default; sha256 `b1ea2e87…`), which git stores as LF, so the hash would not survive a checkout. `evaluate_gate.py` now writes LF; the values are identical line by line, and the hash above equals the committed blob's. No candidate had been measured.
- Produced by: `evaluate_gate.py baseline`, environment version 2 as above (`RuleAimer` defaults, `max_pitch_deg` 89)
- Cross-check: the same command with branch `34-feature-fly-vs-aimer-env` @ 50c05b7's `flytracker` package (learned-fly slot added, rule fly by default) gives a byte-identical file, so the aimer's environment is the same there.
- Metric value: time 4.100 s (mean), capture rate 0.995 (199/200)
- Truth file: `gate/truth.csv` — sha256 `630ec5b311a118169c3d0a5872638c13680f0a02d3f509cf98f52238aad98089` (capture = 1, time = 0 for every id)

Capture rate is already 0.995, so a candidate can gain at most 1 capture on it; it cannot
carry the gate. Time to capture can.

## Candidate(s)

| name | what changes vs baseline | predictions file (filled when measured) |
| --- | --- | --- |
| `sac-fs1` | SAC policy, observation as is (frame stack 1) | `gate/sac-fs1.csv` (mean of `gate/sac-fs1-s{0,1,2}.csv`), sha256 `87157690c9ff…` |
| `sac-fs4` | SAC policy, last 4 observations stacked (frame stack 4) | `gate/sac-fs4.csv` (mean of `gate/sac-fs4-s{0,1,2}.csv`), sha256 `51ab848c6116…` |

Per-seed files (sha256 prefixes): `sac-fs1-s0` `3b6869d1b868`, `sac-fs1-s1` `54622a2ee46f`, `sac-fs1-s2` `fcaca01b249d`, `sac-fs4-s0` `86c30eecf606`, `sac-fs4-s1` `dc676f615b40`, `sac-fs4-s2` `02abbc5c6b68`. Produced on the vast.ai instance by `evaluate_gate.py model` on each final `model.zip` (torch 2.15.0+cpu, deterministic policy), 2026-11-12 15:51 UTC.

Training, identical for both except the frame stack:

- `scripts/train.py --algo sac --steps 1000000 --eval-every 50000 --eval-episodes 3 --seed <0|1|2> --frame-stack <1|4>`
- Stable-Baselines3 2.9.2 `SAC("MlpPolicy")` defaults (lr 3e-4, buffer 1e6, batch 256, tau 0.005, gamma 0.99, `ent_coef="auto"`, train_freq 1, gradient_steps 1, learning_starts 100), CPU, one torch thread per run.
- Default `EnvConfig`, environment version 2 (dt 0.01, frame skip 2, 10 s episodes, fov 40°, pitch limit 89°, capture 3° for 0.2 s, turret at the floor centre).
- The candidate model is the **final** `model.zip` at 1,000,000 steps. Checkpoints are kept for the viewer and the learning curve only; no checkpoint is picked.

## Metric

- Per evaluation seed: `time` = seconds from reset until capture; the full episode length (10 s) when the fly is not captured. `capture` = 1 if captured.
- Policy acts with `deterministic=True`. One episode per seed.
- A candidate's value per seed is the mean over its 3 training seeds (`evaluate_gate.py mean`).
- Formula: mean `time` over the 200 seeds = `mae` against truth time 0. Lower is better.
- Rounding: none. Clip: none.
- Targets: `time` (gated), `capture` (reported, and used by an exclusion below).
- Tool: `paired_bootstrap.py --truth gate/truth.csv --a gate/baseline.csv --b gate/<cand>.csv --targets time --metric mae --lower-is-better --resamples 10000 --seed 42 --threshold 0.90`

## Data

- Item ids: evaluation seeds 20000-20199, N = 200, listed in `gate/truth.csv` (sha256 above)
- Items that must be present: all 200
- Both systems are scored on exactly these ids; a missing id is a failed run, not a smaller N
- Training never resets the environment with these seeds explicitly (training env seed = 0, 1, 2; in-training evaluation uses 10000-10002)

## Threshold

- Adopt when P(candidate faster) ≥ `0.90` by paired bootstrap, 10,000 resamples, seed 42, on `time`
- Below the threshold the answer is "not adopted", including at 0.85

## Selection rule

None — two fixed candidates, each gated against the baseline on its own. `sac-fs1` vs
`sac-fs4` is reported descriptively (same bootstrap, A = `sac-fs1`), and no choice between
them is adopted from these 200 seeds; picking one would need a new gate on fresh seeds.

## Pre-declared exclusions / sensitivity checks

- Candidate capture rate (mean over its 3 models) below 0.97 → not adopted even if `time` passes. Faster on average but losing flies the baseline catches is not better.
- Any single training seed whose model has P(faster than baseline) < 0.50 on `time` → **undecided**, not adopt: the result depends on the training seed.
- A run that does not reach 1,000,000 steps voids that candidate; it is re-run with the same seed, not replaced by a checkpoint.

## Gates

1. Offline: `paired_bootstrap.py` on the files above → P(win), CI, per training seed and pooled.
2. Deployed: none — nothing ships; the viewer only replays recorded episodes.

## Decision rule

- **adopt** — the offline gate passes and no exclusion fires: that SAC setting becomes the reference RL aimer for later issues (#34), and the rule baseline stays as the comparison.
- **reject** — the gate fails or the capture exclusion fires: the numbers and learning curves are written into the management doc; this gate is not re-run with a tweak. A changed setup (more steps, other hyper-parameters, reward change) is a new gate.
- **undecided** — passes pooled but a training seed is worse than the baseline: report the spread; more training seeds are a new gate.

## Verdict

<!-- Filled after measuring. Paste the script's Markdown tables here unedited. -->

- Date: 2026-11-13 (KST)
- Full, unedited script output for every call below: `gate/bootstrap-output.md` (produced by `runs/_ops/run_gate.sh`, a local helper that runs exactly the commands in "Metric" and "Pre-declared exclusions").

### sac-fs1

- P(candidate faster): **1.000** (threshold 0.90) — **PASS**
- Mean time: 4.0999 s → 2.1836 s, Δ −1.9163 s, 95% CI [−2.1957, −1.6234]

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.1836 | -1.9163 | -1.9150 | [-2.1957, -1.6234] | 1.000 |
| **macro** | 4.0999 | 2.1836 | -1.9163 | -1.9150 | [-2.1957, -1.6234] | 1.000 |

- Capture (reported; `capture` column scored as mae against 1, i.e. miss rate): baseline 0.0050, sac-fs1 0.0200, Δ +0.0150, 95% CI [−0.0033, +0.0350], P(sac-fs1 better) 0.055. Pooled capture rate 0.980 ≥ 0.97: the capture exclusion does not fire.
- Per training seed, time (exclusion if P < 0.50): s0 2.7278 s (P 1.000), s1 1.8014 s (P 1.000), s2 2.0217 s (P 1.000). Does not fire.

### sac-fs4

- P(candidate faster): **1.000** (threshold 0.90) — **PASS**
- Mean time: 4.0999 s → 2.1232 s, Δ −1.9767 s, 95% CI [−2.2707, −1.6688]

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.1232 | -1.9767 | -1.9762 | [-2.2707, -1.6688] | 1.000 |
| **macro** | 4.0999 | 2.1232 | -1.9767 | -1.9762 | [-2.2707, -1.6688] | 1.000 |

- Capture (reported): baseline miss rate 0.0050, sac-fs4 0.0283, Δ +0.0233, 95% CI [+0.0033, +0.0450], P(sac-fs4 better) 0.013. Pooled capture rate 0.9717 ≥ 0.97: the capture exclusion does not fire, by a margin of 0.0017 (about one third of one missed seed).
- Per training seed, time: s0 2.1561 s, s1 2.1523 s, s2 2.0612 s, each P 1.000. Does not fire.

### Descriptive: sac-fs4 vs sac-fs1 (no decision)

- Time: 2.1836 → 2.1232 s, Δ −0.0604, 95% CI [−0.1851, +0.0642], P(fs4 faster) 0.832.
- Miss rate: 0.0200 → 0.0283, Δ +0.0083, 95% CI [−0.0050, +0.0233], P(fs4 better) 0.118.
- Frame stack 4 did not separate from frame stack 1 on these 200 seeds.

### Where SAC loses

- Seeds not captured: baseline 1 (20068); SAC models 1 to 8 each (`sac-fs1-s1` 1, `sac-fs1-s2` 3, `sac-fs4-s1` and `-s2` 5, `sac-fs4-s0` 7, `sac-fs1-s0` 8). Seed 20112 is missed by all 6 SAC models and caught by the baseline; 20084 by 4 models, 20037 and 20062 by 3.
- On 5 seeds (20033, 20045, 20093, 20112, 20180) the baseline is faster than every SAC model.
- Among captured episodes, median time: baseline 4.25 s, SAC 1.65-1.89 s; 90th percentile: baseline 5.44 s, SAC 2.41-3.31 s.
- Learning curve (training rollouts, stochastic policy, `rollout/ep_len_mean`): from 394-485 steps at 50k to 95-137 steps at 1M; every run is flat within about ±10 steps from 500k on. More steps under these settings are unlikely to change the result; this is a reading of 6 curves, not a gate.

### Decision

- Exclusions fired: none (sac-fs4's capture exclusion missed firing by 0.0017).
- Deployed gate: not applicable.
- Decision: **adopt** — SAC passes for both frame-stack settings: it catches the fly in about half the baseline's time (2.12-2.18 s vs 4.10 s), consistently over 3 training seeds each. SAC becomes the reference RL aimer for later issues (#34), and the rule baseline stays as the comparison. Its weakness is written down with it: SAC misses more flies than the baseline (2.0-2.8 % vs 0.5 %), significantly so for frame stack 4.
- No choice between `sac-fs1` and `sac-fs4` is made from these seeds, as pre-declared; picking one is a new gate on fresh seeds. Of the two, `sac-fs1` has the simpler observation and the lower miss rate.
