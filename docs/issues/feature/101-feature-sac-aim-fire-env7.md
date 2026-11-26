# 101 환경 버전 7에서 SAC로 조준과 발사 학습하기

## Document Relations
- Issue: #101
- Branch: `101-feature-sac-aim-fire-env7`
- Umbrella: (none)
- Status: in progress
- Follows: #91 (environment version 7: the rule fly escapes when the beam touches it; grazes and wall shots), #88 (acceleration action; fire learning not faster than the rule under version 6)

## Summary
Train SAC aimers under environment version 7, where a rule fly touched by the beam escapes: the aim again (the existing models never saw an escaping fly), and the fire decision with a price on wall shots, then gate them by rules written before measuring. Under version 6 a learned fire decision had nothing to win (#88); under version 7 a badly timed shot makes the fly escape, and a shot that never touches the fly is counted as a wall shot that the user wants reduced for safety and damage to walls and furniture.

## Goal
- A learned aimer that is better than aimer v2 under version 7 (v2: 506/600 captured, 4.85 s; the rule aimer v0 captures 192/200).
- An answer to "does a learned fire decision do at least as well as the baseline's firing rule when a misfire costs something", measured by time and wall shots together.
- The trade-off between capture time and wall shots at three prices of a wall shot, so that the user can choose the final price.

## Scope
PLAN — every item below is a proposal until the user confirms it at the first review. Nothing is implemented.

1. Reward term `RewardWeights.wall_shot` (default 0, so existing rewards do not change): a penalty when a shot ends as a wall shot (the beam never touched the fly during it). Grazes get no reward term; the environment already prices them (the fly escapes).
2. Price of a wall shot, set by the user on 2026-11-26: **1 s** as the main condition, **0 s** as control, **3 s** beside it. Conversion to reward used in training (agent's proposal): 1 s = 0.5, the time penalty of 1 s (0.01 per 0.02 s step); so 0, 0.5 and 1.5. The gate does not use this conversion; it uses seconds directly (item 5).
3. Conditions, SAC, acceleration action, action-change weight 1.0 (the settings of `accel-pen-rule`), trained under version 7 against the rule fly, 1,000,000 steps, training seeds 0, 1, 2 (12 runs):

   | name | fire | wall-shot price |
   | --- | --- | --- |
   | `v7-rule` | baseline rule | none (the rule fires) |
   | `v7-fire-w0` | learned with the aim | 0 s (control) |
   | `v7-fire-w1` | learned with the aim | 1 s |
   | `v7-fire-w3` | learned with the aim | 3 s |

4. Pre-declared fallback when the joint conditions do not fire (in #88 both joint conditions ended never firing): fire-only on the fixed aim of `v7-rule` (`--aim`), same three prices, 500,000 steps, started from the baseline rule (`--fire-prior rule`). Decided by a rule written in the gate (for example: fewer than 0.5 shots per episode in the last training evaluations), not after looking at gate numbers.
5. Gates, written before any model of this issue is measured (seeds 20000-20199, rule fly, paired bootstrap, 10,000 resamples, seed 42, P >= 0.90):
   - Gate A (aim): `v7-rule` against aimer v2 under version 7 (`gate/accel-pen-rule.csv` of #91, sha256 `1a7fbb93...`), on `time`; capture exclusion as in #91.
   - Gate B (fire): `v7-fire-w1` against `v7-rule` on `score = time + 1.0 s x wall shots`; capture exclusion as in #91. The other two prices are reported with their own score (0 s and 3 s), not gated.
   - Reported, not gated: grazes, shots, the calibrated neural fly (60 episodes, stimulus off and on), v0.
6. Measurement with #91's `measure_v7.py`, on the same library versions as #91's instance (torch 2.15.0, stable-baselines3 2.9.2, gymnasium 1.4.0).
7. README, viewer data (history, lineage; aimer v3 if a gate adopts), glossary if a new on-screen term appears, published runs and `published/issues/101.json`.

## Out Of Scope
- The neural fly's reaction to the beam (to be agreed with the teammate who owns it); training against the neural fly.
- Several flies; a cooldown of the laser.
- Showing grazes and wall shots in the viewer's readouts.
- Changing the capture radius (1.25 mm) or the shot length (0.15 s).

## Done Criteria
- [ ] The user confirmed the plan (conditions, reward conversion, gates) at the first review.
- [ ] `wall_shot` reward term implemented and tested; default rewards unchanged.
- [ ] Gate document complete above "Verdict" and committed before any model of this issue is measured.
- [ ] 12 runs trained (and the fallback runs if its rule fires); training curves kept.
- [ ] Gates A and B measured; verdicts written; trade-off table reported to the user.
- [ ] README, viewer data, published runs and `published/issues/101.json` updated.
- [ ] `uv run pytest -q` and the viewer build pass.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-26: issue registered by `issue-start` after the user said "환경 7에서 발사 학습하는 거 준비하자". The plan above is written; nothing is committed, implemented, trained or rented. The first commit (this document, the registry row, the `AGENTS.md` pointer) waits for the user's approval.

Decided by the user (2026-11-26): fire learning continues under an environment where a misfire costs something; misfires are to be reduced for safety and damage; the misfire penalty goes to wall shots with a zero-penalty control; a wall shot costs 1 s (main), with 0 s and 3 s beside it; aimer v2 is `accel-pen-rule`.

Answered at the first review (2026-11-26, "커밋해도 돼. 조준도 버젼 7에서 다시 학습해"): the first commit is approved, and the aim is trained again under version 7 (`v7-rule` stays in the plan). Items 2-4 below were shown in the same report and not answered; they are still open, and no instance is rented before item 4 is.

After the first commit (f1fea2e): the `wall_shot` reward term with its test, the gate document, `score.py` and `gate/truth.csv` are written and tested (286 passed) but NOT committed — two commits prepared in the Work Log (feat, then docs gate) wait for the user's review. Nothing is trained; no instance is rented. vast.ai helper scripts are to be adapted from `C:\Users\neighbor\Documents\Code\Github\FlyTracker-88\runs\_ops\` (training) and `FlyTracker-91\runs\_ops91\` (measuring).

Open:
1. (answered: yes, train the aim again.)
2. Reward conversion 1 s = 0.5 (time penalty only). While the fly is visible near the beam the reward actually falls by about 0.5 to 1.0 per second, so 0.5 is the low end.
3. Gate B compares learned fire with rule fire trained the same way (`v7-rule`), not with v2. Agent's proposal.
4. Cost: 12 runs of 1,000,000 steps on vast.ai, the size of #88's first stage.

Where things are:
- Models: v1 in the #51 worktree's `runs/g51`, v2 (`accel-pen-rule`) in `C:\Users\neighbor\Documents\Code\Github\FlyTracker-88\runs\g88\`; both gitignored, do not remove those worktrees.
- #91's full measurement outputs: `C:\Users\neighbor\Documents\Code\Github\FlyTracker-91\runs\_ops91\dl\all\` (gitignored). vast.ai helper scripts of #91: `runs/_ops91/` in the same worktree.
- Trap from #91: three rented instances failed before one worked. Read `vastai logs <id>` after 3 minutes without SSH instead of waiting; an onstart command that fixes owner and modes of `/root/.ssh` avoided `bad ownership or modes for file /root/.ssh/authorized_keys`.
- Trap: sessions bound to another worktree cannot `EnterWorktree` here; work by absolute path and put multi-step shell work into script files.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 환경 버전 7에서 SAC로 조준과 발사 학습하기 (#101)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
This document, the registry row in `docs/issues/README.md`, the pointer line in `AGENTS.md`.
#### Changes
- Summary, goal, plan, out of scope, done criteria and open questions written from the conversation of 2026-11-26 and #91's verdict.
#### Verification
- `issue-start` summary: issue #101 (Feature, labels enhancement and training, Priority High, assigned), branch from `origin/main` @ 5c37aba (the squash merge of #91).
#### Notes
- No code yet.

### feat: 벽에 맞은 발에 벌점을 주는 보상 항목 넣기 (#101)
> why: Scope 1 — the fire conditions need a price on wall shots only
#### Scope
`flytracker/env.py`, `tests/test_control.py`, `viewer/src/data/experiment.js`, this doc.
#### Changes
- `RewardWeights.wall_shot` (default 0): subtracted once in the step in which a shot ends as a wall shot. `--reward wall_shot=<value>` works without a change to `train.py` (it lists the fields of `RewardWeights`).
- Viewer: the aimer reward card shows the row "벽에 맞은 발 벌점".
#### Verification
- `uv run pytest -q`: 286 passed (285 of main + the new test: the penalty is charged in the step the wall shot is counted, counters unchanged by the weight, default 0).
- Smoke (3,000 steps each, not a result): `--control accel --fire rule --reward action_change=1.0` and `--control accel --reward action_change=1.0 wall_shot=0.5` both train under version 7; `config.json` records `envVersion` 7 and the weight.
#### Notes
- `ENV_VERSION` stays 7: the default reward is unchanged, as with `misfire` in #88.
- The penalty arrives when the shot ends, up to 0.15 s (8 decision steps) after the trigger.
- Not done yet: a `history.js` line for the new row and a glossary entry (the term "벽에 맞은 발" is there since #91); they go in with the results.

### docs: 환경 버전 7에서 조준과 발사를 견줄 판정 기준을 학습 전에 적기 (#101)
> why: the comparison rules have to exist before anything of this issue is trained or measured
#### Scope
`docs/issues/feature/101-feature-sac-aim-fire-env7/gate.md`, `score.py`, `gate/truth.csv`, this doc.
#### Changes
- Gate A (`v7-rule` against aimer v2 on time) and Gate B (`v7-fire-w1` against `v7-rule` on `score_w1 = time + 1.0 x wall_shots`), exclusions, the pre-declared second stage (fire-only) and its trigger.
- `score.py`: adds `score_w1`, `score_w3` to a gate CSV; writes the truth file.
#### Verification
- `score.py truth`: 200 rows, sha256 in the gate. `score.py` on #91's `accel-pen-rule.csv`: time 4.851, wall shots 0.252, `score_w1` 5.103, `score_w3` 5.606.
#### Notes
- Reward conversion (1 s = 0.5), Gate B's baseline (`v7-rule`, not v2) and the cost (12 runs on vast.ai) were the agent's proposals; the user approved all of them, both commits and the start of training on 2026-11-27 ("다 승인. commit하고 vast.ai에서 학습 시작해").

## Management Notes
### Follow-up Candidates
- The neural fly's reaction to the beam (teammate).
- Several flies seeing each other's flashes.
- Moving #59's training script from `algo.fireMode` to `algo.fire` (teammate).
- #85's diagnosis documents are still unpushed.
### References
- #91: `docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/gate.md` (version 7 numbers and v2 verdict), `measure_v7.py`.
- #88: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate-fire.md`, `conditions.md`.
