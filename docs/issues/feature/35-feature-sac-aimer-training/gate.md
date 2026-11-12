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
| `sac-fs1` | SAC policy, observation as is (frame stack 1) | `gate/sac-fs1.csv` (mean of `gate/sac-fs1-s{0,1,2}.csv`) |
| `sac-fs4` | SAC policy, last 4 observations stacked (frame stack 4) | `gate/sac-fs4.csv` (mean of `gate/sac-fs4-s{0,1,2}.csv`) |

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
