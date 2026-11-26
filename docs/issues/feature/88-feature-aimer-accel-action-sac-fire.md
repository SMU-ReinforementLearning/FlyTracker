# 88 조준기 행동을 각가속도로 바꾸고 SAC로 조준과 발사 학습하기

## Document Relations
- Issue: #88
- Branch: `88-feature-aimer-accel-action-sac-fire`
- Umbrella: (none)
- Status: in progress

## Summary
Train SAC aimers that steer alone with angular-acceleration actions instead of angular-rate actions, with and without learning to fire, and gate each against the rule aimer (v0) by rules written before training. #85 found that #51's policy-alone aimer did learn to aim but its rate command scatters by about ±25 °/s, so the beam jitters around the fly at 3 mm; the observation has a magnified aim error (`uv_fine`) while the action has one ±180 °/s scale. The user (2026-11-25): the capture radius stays 1.25 mm; make the command finer by driving the turret by acceleration, re-set the action penalty, and look at firing too, which today is a rule that only checks the current instant.

## Goal
- Learn whether acceleration actions let a policy-alone SAC aimer hold the beam on the fly for a whole shot (fire by the baseline's rule), with and without a larger action penalty.
- Learn whether the same policy can also learn when to fire when a misfire costs something (two weights).
- The staged step the user asked for (fire learning on top of a working aim) is designed after these results; it need not finish in the first night.

## Scope
1. `flytracker/wrappers.py`: `AccelControl` (`accel_to_rate`, `accel_gain`), `RuleFire`, `make_env(control=, fire=)`. Wrappers, not environment changes; `ENV_VERSION` stays 6.
2. `flytracker/env.py`: `RewardWeights.misfire` (default 0; subtracted once per misfire).
3. `flytracker/players.py`: `load_opponent` / `PolicyPlayer` rebuild control and fire from `config.json` (`algo.control`, `algo.fire`).
4. `scripts/train.py`: `--control rate|accel`, `--fire policy|rule`. `tests/test_control.py`.
5. Gate: `88-feature-aimer-accel-action-sac-fire/gate.md`, frozen baseline and truth (the bytes of #72's).
6. Training: 5 conditions x 3 seeds x 1,000,000 steps on a rented vast.ai instance (the user's instruction, 2026-11-25; cost cap 10 USD).
7. After the results: evaluation, verdicts, #85's diagnosis repeated on the new models, published runs, README, viewer rows (`history.js`, `lineage.js`, a card row for the control), a Korean result note.

## Out Of Scope
- Changing the capture radius or the shot length, in training or evaluation (the user, 2026-11-25).
- Tuning weights, the entropy target or SAC hyper-parameters after seeing results (a new gate).
- The neural fly; detection noise (#13); replacing v1 (a separate gate against v1).

## Done Criteria
- [x] Wrappers, misfire weight, loader and training options implemented and tested; the default environment is unchanged (baseline file reproduced byte for byte).
- [x] Gate document complete above "Verdict" and committed before the first training run starts.
- [x] 15 runs reach 1,000,000 steps; results downloaded and verified; instance destroyed.
- [x] Each candidate evaluated on seeds 20000-20199; bootstrap output and verdicts written into `gate.md`.
- [x] #85's diagnosis repeated on the new models (distance, scatter, captures in training).
- [ ] Runs published under issue #88; README, `history.js`, `lineage.js` and the viewer card updated.
- [ ] `uv run pytest -q` and the viewer build pass.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-26 03:30 KST. Training finished, results downloaded and verified, instance destroyed (nothing is running or billing). Verdicts are in `gate.md`: one of five adopted (`accel-pen-rule`: 2.611 s, 589/600, 0.47 misfires per episode; v0 4.894 s). `accel-rule` passes on time but is rejected by the capture exclusion (0.965 < 0.97); `rate-rule` and both fire-learning conditions are rejected. Korean results: `conditions.md`, section "결과". Nothing pushed.

Stage 2 (2026-11-26, the user: proceed with the staged fire learning as proposed) is finished: 4 conditions x 3 seeds x 500,000 steps trained on vast.ai, downloaded and verified, instance 62621473 destroyed (`vastai show instances` lists none; nothing is running or billing). Verdict in `gate-fire.md`: all four rejected, every candidate is slower than `accel-pen-rule` with rule fire (P(faster) 0.000-0.001). Fire stays with the rule. Korean results: `conditions.md`, section "발사만 학습한 단계". The user said (2026-11-26) a separate 1,000,000-step run would be decided after seeing the results; the curves are flat from 50,000 steps, the agent's opinion is not to run it. Nothing pushed.

Left, waiting for the user (screen text and a decision are involved):
- Scope 7 remainder: published runs (`published/issues/88.json`), README training options, viewer rows (`history.js`, `lineage.js`, the control row on the card).
- Whether to gate `accel-pen-rule` against v1 (descriptively 0.41 s faster, P = 1.000; not a pre-registered comparison).
- Whether to run the 1,000,000-step fire-only variant (a new gate) or close fire learning here.

Where things are:
- Models: `runs/g88/<condition>-s<k>/<run>/` (gitignored, only on this machine; archive `runs/_download/runs-g88.tgz`, 869 MB, sha256 in `runs/_download/manifest.sha256`). Diagnosis traces: `runs/d88/*.npz`.
- Helper scripts (gitignored): `runs/_ops/` (`fetch.sh`, `eval_all.sh`, `diag_all.sh`, `diag_fire.sh`).
- Stage-2 models: `runs/g88f/<condition>-s<k>/<run>/` with the aim model copied to `aim/` (gitignored, only on this machine; archive `runs/_download2/runs-g88f.tgz`, sha256 in `runs/_download2/manifest.sha256`). Helpers: `runs/_ops2/` (`fetch.sh`, `eval_all.sh`, `diag_fire.sh`).
- Trap: this session could not `EnterWorktree` into `FlyTracker-88`; it works there by absolute path, and compound shell commands that mention git are refused, so multi-step work goes into script files.

Standing permissions from the user (2026-11-25, before going to sleep): commit on this branch without the review gate when the tests pass; no push, PR or merge; rent one vast.ai instance within 10 USD in total and destroy it after the results are downloaded and verified.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 조준기 행동을 각가속도로 바꾸고 SAC로 조준과 발사 학습하기 (#88)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, `AGENTS.md` pointer.
#### Changes
- Doc filled from the 2026-11-25 conversation and #85's result.
#### Verification
- `issue-start.mjs` created issue #88 (Type Feature, labels enhancement and training, assignee the user, Priority High), branch from `origin/main` @ 813b1b9, worktree `FlyTracker-88`.
#### Notes
- Priority High was chosen by the agent: the user runs the training the same night.
- #85's branch is not merged; this branch does not contain its result note.

### feat: 각가속도 행동, 규칙 발사, 오발 벌점을 학습 옵션으로 넣기 (#88)
> why: #85 showed the rate command is too coarse a scale for the last 0.04 degrees; the conditions of the gate need these three switches
#### Scope
`flytracker/wrappers.py`, `env.py`, `players.py`, `scripts/train.py`, `tests/test_control.py`. `ENV_VERSION` stays 6.
#### Changes
- `wrappers.AccelControl` / `accel_to_rate` / `accel_gain`: the policy's two steering values are angular accelerations; commanded rate = observed rate + action x 14.4 deg/s per step (yaw 0.08, pitch 0.12 in action units), clipped. Action 0 keeps the current rate.
- `wrappers.RuleFire`: the policy outputs yaw and pitch, does not observe `shot`, and `RuleAimer.wants_fire` fires. `make_env(control=, fire=)`; both refuse discrete actions.
- `RewardWeights.misfire` (default 0): subtracted once in the step a shot first leaves the fly.
- `PolicyPlayer(accel_gain=)`; `load_opponent` reads `algo.control` and `algo.fire` from `config.json`, so a model plays as it was trained. `train.py --control`, `--fire` write them.
#### Verification
- `uv run pytest -q`: 231 passed (11 new in `tests/test_control.py`: gain values, zero acceleration keeps the rate, clipping, full acceleration reaches 0.08 per step, the rule-fire wrapper fires exactly when the baseline rule says, a `PolicyPlayer` reproduces the wrappers' rewards, turret angles and shots for three combinations, discrete refused, the misfire penalty charged once per misfire, default weight 0).
- Smoke: `train.py --steps 3000` for `--control accel --fire rule`, `--control accel --reward misfire=0.3` and `--fire rule` each trains, saves and loads through #72's `measure_aimers.py` (0/3 on seeds 20000-20002, untrained; labels end in `+rule-fire` where the rule fires).
- Default environment unchanged: `measure_aimers.py baseline` on this branch gives sha256 `70a62ab3...`, the frozen file of #72.
#### Notes
- Wrappers instead of an environment change: the baseline, v1 and the teammate's fly training keep working, and no env version bump is needed. The cost: a model's control lives in its run's `config.json`.
- The existing `action_change` penalty is computed on the rate command the environment receives, so under acceleration actions it already penalises acceleration; no new term was added for it.
- README, the viewer card row for the control and the `history.js` / `lineage.js` rows are left for after the results (Scope 7).

### docs: 각가속도 조준기의 판정 기준을 학습 전에 적기 (#88)
> why: the comparison rules have to exist before any candidate is measured
#### Scope
`docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate.md`, `gate/baseline.csv`, `gate/truth.csv`.
#### Changes
- Gate: five candidates (`rate-rule`, `accel-rule`, `accel-pen-rule`, `accel-fire-m03`, `accel-fire-m10`), 3 training seeds, 1,000,000 steps, time to capture on seeds 20000-20199 against v0, paired bootstrap P >= 0.90, exclusions for capture rate below 0.97, a training seed below 0.50 and misfires above twice v0's, no selection among candidates.
- Baseline and truth are the bytes of #72's files (sha256 `70a62ab3...`, `0f577c4c...`).
#### Verification
- `sha256sum` of both files matches `gate.md`. No training run of this issue had started when this was committed; the instance (vast.ai 62522764, AMD EPYC 7B13, 32 effective cores, about 0.20 USD per hour) was booting and had received nothing.
#### Notes
- The thresholds and exclusions repeat #51 and #72; the two misfire weights were agreed with the user as two conditions.
- Evaluation will run on the local machine, where the baseline file was produced, not on the instance.

### docs: 각가속도 조준기 실험 조건을 한국어로 정리하기 (#88)
> why: the user asked for the conditions table to be documented so it can be used in a presentation (2026-11-25)
#### Scope
`docs/issues/feature/88-feature-aimer-accel-action-sac-fire/conditions.md`, this doc (resume note in Current State).
#### Changes
- `conditions.md` (Korean): background, the five conditions, what each column means (rate vs acceleration actions, who fires, the reward table with the changed item per condition), which comparison answers which question, common settings, the judging rule in plain words, v0 and v1 reference numbers. Results section empty.
- Current State: resume note for the running instance (id, ssh target, markers, next steps, how to destroy it).
#### Verification
- Every value was read from `gate.md`, `RewardWeights` or `remote_train.sh`. `ko-writing` `check.py`: no banned pattern, endings consistent.
- Training was confirmed running before this commit: 15 `train.py` processes, `TRAINING_STARTED` 2026-11-25 13:10:47 UTC, remote setup log `47 passed`.
#### Notes
- No cold-reader pass. No code changed since the last full test run (231 passed).

### docs: 각가속도 조준기 15개의 판정과 진단 결과 적기 (#88)
> why: training finished on 2026-11-26; the gate's verdicts and the repeated #85 diagnosis have to be on record with the files they came from
#### Scope
`gate.md` (Verdict), `gate/` (pooled files, `v1.csv`, `bootstrap-output.md`), `data/` (per-model measurements, diagnosis tables, `README.md`), `conditions.md` (Korean results), `run_gate.py`, `measure_tracking.py`, `analyze.py`, `response_curve.py`, `training_logs.py`, `fire_head.py`, `fire_stochastic.py`, this doc.
#### Changes
- Verdicts: `accel-pen-rule` adopt (time 2.611 s vs 4.894 s, P = 1.000; capture 589/600; per-seed P 1.000 each; misfires 0.472). `accel-rule` reject by the capture exclusion (579/600 = 0.965) although time P = 1.000. `rate-rule` reject (12/600). `accel-fire-m03`, `accel-fire-m10` reject (0/600, about 0.01 shots per episode).
- Diagnosis (fire held off): median beam distance on tracking steps 0.40-0.56 mm for the rule-fire acceleration models against 2.82-3.12 mm for `rate-rule`; error-direction flips 11-24 % against 86-89 %; step-to-step yaw command change 2.9-4.0 °/s against 46.6-52.4; no command beyond the turret's acceleration limit against 86-94 %. Training episode length fell from 500 to 129-182 steps for the two rule-fire acceleration conditions and stayed at 500 for the rest.
- Fire-learning models aim (0.63-1.05 mm; 182-200 of 200 would have been caught had something fired) but the fire action's mean is about -0.5 at every beam distance with sd 0.12-0.15, so even sampled actions fire on 0.1 % of steps or fewer.
- The four diagnosis scripts are #85's (that branch is not merged), copied with the model names changed; `measure_tracking.py` additionally converts acceleration actions and records the fire action's mean.
#### Verification
- Download: `sha256sum -c manifest.sha256` OK for `runs-g88.tgz` and `state-logs.tgz`; 15 `model.zip`; `vastai show instances` lists none after the destroy (2026-11-26 02:49 KST).
- All 200 ids per model (`measure_aimers.py` printed n=200 for each). `run_gate.py` wrote `gate/bootstrap-output.md` with the sha256 of every input; baseline `70a62ab3...`, truth `0f577c4c...` as frozen.
- `rate-rule` reproduces #85's picture of #51's `sac-beam` (3 mm, flips near 0.87), which checks the copied diagnosis against a known case.
- `uv run pytest -q`: 231 passed (no library code changed in this commit). `ko-writing` `check.py` on `conditions.md`: no banned pattern, endings consistent.
#### Notes
- First diagnosis pass failed on the six fire-learning models (three-value action written into a two-value field); fixed and re-run for those six only.
- The explanation of why fire learning collapsed (early shots all penalised before the aim existed) is an inference; shots during training were not logged.
- No cold-reader pass on `conditions.md`. Viewer, README and published runs are left for the user's review because they add screen text.
- Cost: instance ran 2026-11-25 13:00 UTC to 17:49 UTC at about 0.20 USD per hour, about 1 USD, within the 10 USD cap (figure from the hourly rate, not from the invoice).

### feat: 조준을 고정하고 발사만 학습하는 옵션 넣기 (#88)
> why: the user approved the staged fire-learning proposal (2026-11-26); stage 1 showed that fire learned together with the aim collapses to never firing
#### Scope
`flytracker/wrappers.py`, `players.py`, `scripts/train.py`, `tests/test_control.py`. `ENV_VERSION` stays 6.
#### Changes
- `wrappers.FireOnly` / `fire_decision` / `make_env(aim=, fire_prior=)`: a fixed aim player steers, the policy outputs one fire value; with `fire_prior="rule"` the rule's verdict is added as ±0.5, so value 0 fires as the rule.
- `players.FireOnlyPlayer`; `load_opponent` rebuilds it when the run's `algo.aim` is set, loading the aim model from the run's own `aim/` folder.
- `train.py --aim <run> --fire-prior none|rule`: copies the aim run's `model.zip` and `config.json` into `<run>/aim/` so a fire run is self-contained.
#### Verification
- `uv run pytest -q`: 236 passed (5 new: the decision table, rule prior with value 0 plays exactly as the aim player, `FireOnlyPlayer` reproduces the training wrapper with frame stack 2 for both priors, refusals).
- Smoke: `train.py --steps 3000 --aim <accel-pen-rule-s0> --frame-stack 4 --reward misfire=1.0` with each prior trains, saves, and loads through #72's `measure_aimers.py` (5 seeds: 5/5 both; numbers recorded in `gate-fire.md` as seen, not candidates).
#### Notes
- The aim is a player inside the wrapper, not a frozen part of one network: simplest, and the aim provably does not change.
- The default environment and stage 1's models are untouched (their tests still pass).

### docs: 발사 학습 단계의 판정 기준을 학습 전에 적기 (#88)
> why: the comparison rules have to exist before any stage-2 candidate is measured
#### Scope
`docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate-fire.md`, this doc.
#### Changes
- Gate: four candidates (`fire-m1`, `fire-m5`, `fire-prior-m1`, `fire-prior-m5`), aim fixed to `accel-pen-rule-s<k>` for training seed k, frame stack 4, 500,000 steps, time against `accel-pen-rule` with rule fire (frozen `gate/accel-pen-rule.csv`, sha256 `9996b2a3...`), P >= 0.90; exclusions for capture below 0.97, a training seed below 0.50 against its own aim model, misfires above the baseline's 0.472; a declared "fewer misfires at equal time" case goes to the user.
#### Verification
- sha256 of the baseline and per-model files read with `sha256sum` and matching `gate/bootstrap-output.md`. No stage-2 training run had started.
#### Notes
- Misfire weight 5.0 is the agent's choice (reason in the gate); 1.0 comes from stage 1. The user confirmed the pair 1.0 / 5.0 before training (2026-11-26).
- The user's permissions for this stage (2026-11-26): commit on this branch without the review gate when the tests pass, no push, PR or merge; one vast.ai instance within 5 USD, destroyed after the results are downloaded and verified.

### docs: 발사만 학습한 조준기 12개의 판정과 진단 결과 적기 (#88)
> why: stage 2 was trained and measured; the verdict and what the policies do with the trigger have to be on record
#### Scope
`gate-fire.md` (Verdict), `conditions.md` (Korean results), `data/fire-*-s<k>/`, `data/fire-only.md`, `data/training-logs-fire.md`, `data/README.md`, `gate/fire-*.csv`, `gate/bootstrap-output-fire.md`, `run_gate_fire.py`, `fire_only_diag.py`, `training_logs.py`, this doc.
#### Changes
- Verdict: all four candidates rejected. Time against `accel-pen-rule` with rule fire (2.611 s): `fire-m1` +0.065 s, `fire-m5` +0.228 s, `fire-prior-m1` +0.047 s, `fire-prior-m5` +0.025 s; P(faster) 0.000-0.001. Capture 587-589 of 600. Misfires 1.060 / 0.378 / 0.617 / 0.425 against 0.472.
- `run_gate_fire.py`: every bootstrap of `gate-fire.md` into `gate/bootstrap-output-fire.md`. `fire_only_diag.py`: fire value by beam distance, agreement with the rule, hit rate of shots the rule would and would not take, sampled-action play. `training_logs.py`: a `fire` argument for the stage-2 runs.
#### Verification
- 12 runs at `step_0500000`; `sha256sum -c` of the downloaded archives OK; 12 `model.zip` and 12 `aim/model.zip` found before the instance was destroyed; `vastai show instances`: none.
- Each model measured on all 200 seeds (N = 200 in every bootstrap table); the baseline sha256 in the tool output is the frozen `9996b2a3...`.
- `pytest -q`: 236 passed (no library code changed in this commit).
#### Notes
- The declared "fewer misfires at equal time" case did not apply to `fire-m5` / `fire-prior-m5`: misfires P(fewer) 0.987 / 0.936 but time P(faster) 0.000 / 0.001.
- Why the policy does not beat the rule is not measured; `conditions.md` marks its explanation (0.08 s of history against a 0.15 s shot) as a guess.
- vast.ai: one instance, about 3.6 hours at about 0.08 USD per hour (the agent's estimate from the hourly price, not read from the bill); within the 5 USD limit.

## Management Notes
### Proposal: staged fire learning (approved by the user 2026-11-26; gate in `gate-fire.md`)
- Start from an `accel-pen-rule` model with the steering frozen (or a low learning rate) and learn only the fire decision; the aim then already holds the beam inside the radius, so a shot can succeed from the first episode.
- Do not start the fire output from scratch: begin from the rule's behaviour (imitate `wants_fire` first, or let the rule fire with some probability during early training), because the collapse seen here happens when every early shot is a miss.
- Give the fire decision what the rule lacks: recent aim error (frame stack or the error's rate), so it can predict whether the next 0.15 s will hold. #85: a shot on entering the radius hits 59 %, after dwelling 0.16 s 89 %.
- Gate it against `accel-pen-rule` with rule fire on time and misfires, written before training.
### Follow-up Candidates
- Gate `accel-pen-rule` against v1.
- A second `action_change` weight (only 1.0 was tried) belongs to a new gate.
### References
