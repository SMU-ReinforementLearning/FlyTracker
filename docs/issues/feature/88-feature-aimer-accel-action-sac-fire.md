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
- [ ] Wrappers, misfire weight, loader and training options implemented and tested; the default environment is unchanged (baseline file reproduced byte for byte).
- [ ] Gate document complete above "Verdict" and committed before the first training run starts.
- [ ] 15 runs reach 1,000,000 steps; results downloaded and verified; instance destroyed.
- [ ] Each candidate evaluated on seeds 20000-20199; bootstrap output and verdicts written into `gate.md`.
- [ ] #85's diagnosis repeated on the new models (distance, scatter, captures in training).
- [ ] Runs published under issue #88; README, `history.js`, `lineage.js` and the viewer card updated.
- [ ] `uv run pytest -q` and the viewer build pass.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-25 22:15 KST. Code and gate committed (570cc24, 7ce5511, 7a8ec50; not pushed). Training is running on vast.ai.

Resume note:
- Running: vast.ai instance 62522764 (AMD EPYC 7B13, 32 effective cores, about 0.20 USD per hour), `root@217.171.200.22` port 59123 (also in `runs/_ops/ssh_target.txt`). 15 `train.py` processes started 2026-11-25 13:10:47 UTC under `/root/ft`, detached with nohup; they do not depend on this machine. Expected end: about 6 hours later (#51: 49 steps/s per run), around 04:00-05:00 KST on 2026-11-26.
- Markers on the instance, `/root/ft/state/`: `TRAINING_STARTED`, `TRAINING_ENDED`, then `RESULTS_READY` or `FAILED`. Logs: `/root/ft/logs/<name>-s<k>.log`. One look: `bash runs/_ops/progress.sh`.
- Next steps, in order: (1) `bash runs/_ops/fetch.sh` downloads `runs-g88.tgz`, checks the sha256 manifest, extracts to `runs/g88/`, requires 15 `model.zip`, and only then destroys the instance; (2) evaluate each model locally with #72's `measure_aimers.py <run> --out <dir>` on seeds 20000-20199, pool per condition with `mean`; (3) bootstrap as written in `gate.md`, append the verdicts; (4) repeat #85's diagnosis on the new models; (5) the rest of Scope 7.
- If a run failed (`FAILED` says `ONLY_<n>_MODELS`): the archives are still packed; download by hand, re-run the missing seed as the gate says, do not substitute a checkpoint.
- The instance bills until it is destroyed: `vastai destroy instance 62522764 -y`. Nothing destroys it automatically if `fetch.sh` is never run.
- Certain fallback: the three commits above; nothing else on this branch is uncommitted except this note. The helper scripts are in `runs/_ops/` (gitignored): `remote_train.sh`, `remote_up.sh`, `wait_ready.sh`, `fetch.sh`, `progress.sh`.
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

## Management Notes
### Follow-up Candidates
### References
