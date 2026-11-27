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
- [x] The user confirmed the plan (conditions, reward conversion, gates) at the first review.
- [x] `wall_shot` reward term implemented and tested; default rewards unchanged.
- [x] Gate document complete above "Verdict" and committed before any model of this issue is measured.
- [x] 12 runs trained; training curves kept (in the worktree's `runs/g101/`, gitignored). The fallback stage's rule fired but the stage was not run: after the diagnosis the user chose to fine-tune v2 instead, in a follow-up issue.
- [x] Gates A and B measured; verdicts written; trade-off table reported to the user.
- [x] README, viewer data, published runs and `published/issues/101.json` updated.
- [x] `uv run pytest -q` and the viewer build pass.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-26: issue registered by `issue-start` after the user said "환경 7에서 발사 학습하는 거 준비하자". The plan above is written; nothing is committed, implemented, trained or rented. The first commit (this document, the registry row, the `AGENTS.md` pointer) waits for the user's approval.

Decided by the user (2026-11-26): fire learning continues under an environment where a misfire costs something; misfires are to be reduced for safety and damage; the misfire penalty goes to wall shots with a zero-penalty control; a wall shot costs 1 s (main), with 0 s and 3 s beside it; aimer v2 is `accel-pen-rule`.

Answered at the first review (2026-11-26, "커밋해도 돼. 조준도 버젼 7에서 다시 학습해"): the first commit is approved, and the aim is trained again under version 7 (`v7-rule` stays in the plan). Items 2-4 below were shown in the same report and not answered; they are still open, and no instance is rented before item 4 is.

2026-11-27: the user approved everything open ("다 승인. commit하고 vast.ai에서 학습 시작해"). Commits: f1fea2e (seed), 61890d2 (`wall_shot` reward term), then the gate. The training bundle is built from the gate commit; training of the 12 runs starts on vast.ai right after it. Later commits (results, verdicts) go through the review gate again.

RUNNING since 2026-11-26 15:30 UTC (2026-11-27 00:30 KST): vast.ai instance **62712329** (36 cores, about $0.11/h) trains the 12 runs from the bundle of commit b1b5aef; setup tests 59 passed, torch 2.15.0+cpu, sb3 2.9.2, gymnasium 1.4.0, numpy 2.4.6. It bills until destroyed. On the instance: `/root/ft/state/` (markers `TRAINING_STARTED`, then `RESULTS_READY` or `FAILED`), `/root/ft/logs/<name>-s<k>.log`, models in `/root/ft/runs/g101/`; when done it packs `/root/runs-g101.tgz`, `/root/state-logs.tgz`, `/root/manifest.sha256`. Local helpers in this worktree's `runs/_ops101/` (gitignored): `steps.sh` (progress), `rsh.sh '<cmd>'`, `wait_ready.sh`, `ssh_target.txt`, `instance_id.txt`. Not written yet: the fetch script (model on `FlyTracker-88/runs/_ops2/fetch.sh`: verify sha256 and 12 `model.zip`, then destroy) and the measuring steps (gate order: `v7-rule` first, freeze `gate/v7-rule.csv` with the score columns in a commit, verdict A, then the fire conditions). One instance (62710745) was destroyed before this one: it stayed `loading` for 8 minutes with no status message. vast.ai helper scripts are to be adapted from `C:\Users\neighbor\Documents\Code\Github\FlyTracker-88\runs\_ops\` (training) and `FlyTracker-91\runs\_ops91\` (measuring).

2026-11-27 00:24 UTC: all 12 runs finished (`RESULTS_READY`, about 8 h 55 min). The helper scripts now exist in `runs/_ops101/`: `poll.sh`, `measure.sh pA|pB`, `remote_measure.sh`, `boot.sh A|B`, `fetch.sh`. `v7-rule` was measured first (`measure.sh pA`) and `gate/v7-rule.csv` is frozen by sha256 in the gate. The background waiter was killed by the harness for low memory; polling went on in the foreground. Next, in the gate's order: `boot.sh A`, `measure.sh pB`, `boot.sh B`, wait for the neural phases, `fetch.sh` (destroys the instance), verdicts (uncommitted, for review).

2026-11-27 (after the review): the user approved the verdict commit and asked to measure first why `v7-rule` is worse than v2 ("commit해. v7-rule이 왜 v2보다 못한지 원인부터 재봐"). The second stage stays unstarted until that diagnosis is reported. The "uncommitted" line below is superseded by the verdict commit.

DIAGNOSIS DONE, NOT COMMITTED (waits for review): `docs/issues/feature/101-feature-sac-aim-fire-env7/diagnosis.md` and `diagnosis/` (four scripts). Finding: under version 7 the training episodes almost never ended in a capture (episode length 489-500 of 500 throughout; v2's fell to about 150), so `v7-rule` learned from the dense terms only and is imprecise: worse than v2 also with the beam reaction off (0.843 / 4.649 s against 0.982 / 2.611 s), and with sampled actions it captures 0.072 against v2's 0.742. The causal link is a reading, not tested. The user noted that the startle is an intended difficulty and is no ground for rejecting anything by itself; the note is written on that footing. Outputs in `runs/_diag101/` (gitignored). A background run of the sampled measurement was killed by the harness for low memory and redone in the foreground at the user's request. Next decision is the user's: how to train under version 7 so that captures are experienced (warm start from v2 is the agent's proposal), and whether the fire-only stage uses v2 as the fixed aim.

2026-11-27: the user called the finding a good presentation topic and asked to document it ("이거 정말 좋은 발표 주제가 될 것 같아. 문서화해놔"). Written in Korean for people (precedent: #73's `sac-concepts.md`): `docs/issues/feature/101-feature-sac-aim-fire-env7/hard-env-from-scratch.md` — conclusion, the two environments and aimers, the three measurements, the episode-length table, the reading, the bicycle analogy the user liked, confirmed versus interpretation, the fine-tuning experiment (not run), a presentation outline. `ko-writing` `check.py` run; headings fixed. NOT COMMITTED, together with the diagnosis. The user also pointed out that fine-tuning the aim was already a listed option (#88 follow-up (b), #91); `scripts/train.py` cannot continue from a model yet.

2026-11-27, CLOSING: the user approved commit, push, PR and merge of this branch and the next experiment ("머지까지 하고 다음 실험 진행해"). This issue ends with both gates rejected and the diagnosis documented; the fine-tuning of v2 under version 7 continues in a new issue. The `--init-from` change to `scripts/train.py` is NOT in this branch: it is kept as `runs/_ops101/init-from.patch` (gitignored, in this worktree) for the new issue. This worktree must stay: `runs/g101/` (models), `runs/_download101/`, `runs/_diag101/`. Notes below that say "not committed" are superseded.

2026-11-27, later: the user put documentation first ("먼저 지금까지 결론 재현 가능하게 결과까지 다 문서화해놔. publish도 해놓고"). Done and NOT COMMITTED (waits for the review): README (`wall_shot` option, new section "환경 버전 7에서 처음부터 한 학습" with results, diagnosis and the commands to train, measure, gate and diagnose), `published/` (the 12 training runs, 63 MB, and `published/issues/101.json`), `viewer/src/data/history.js` (issue 101, `env.reward.wall_shot`), `lineage.js` (node 101, no new aimer version), glossary ("벽에 맞은 발 벌점"), `diagnosis.md`, `diagnosis/`, `hard-env-from-scratch.md`. `history.js` carries `merged: '2026-11-27'` — correct it if the merge lands on another day. `scripts/train.py --init-from` is written in the working tree but untested and belongs to the next commit (fine-tuning), not to the documentation commit. No screenshots of the new lineage node yet (check on the PR preview).

2026-11-27: the user ordered the fine-tuning ("v2를 fine-tuning 하는 거로 학습 진행해봐"). Plan (the agent's proposal of 500,000 steps and 3 seeds was on the table and not objected to): (1) `scripts/train.py --init-from <run>`: load the model, keep training in the new environment, record `algo.initFrom` (run name and model sha256, no path); (2) `gate-finetune.md` written before training: `v7-ft` (v2 model of the same seed, fine-tuned under version 7, `--control accel --fire rule --reward action_change=1.0`, SAC, 500,000 steps) against aimer v2 on `time`, same seeds, threshold and exclusions as Gate A; (3) train the 3 runs on vast.ai, measure, verdict. This replaces the pre-declared second stage for now (fire-only on `v7-rule`), which stays unstarted. The commits for (1) and (2) and the pending diagnosis documents go through the review gate before the instance is rented.

Diagnosis plan (no training, local, scripts in `diagnosis/`): (1) config diff of v2 and `v7-rule` runs — done: only `envVersion` 6 -> 7 (`fly.evade_laser`) differs, plus recorded defaults; (2) per-model tracking and shot statistics from the outputs already on disk (`runs/_download101/measure/out/rule-v7-rule-s*`, #91's `rule-cand-s*` for v2); (3) both aimers measured again with `evade_laser` off, to separate "worse tracker" from "worse against the startle"; (4) evaluation episodes recorded during training (`episodes.json`) for both. Verdict commit: 396e0fe.

2026-11-27 01:00 UTC — MEASURED, INSTANCE DESTROYED, VERDICTS WRITTEN. Both gates are **reject** (details and tables in `gate.md`, `## Verdict`):
- Gate A: `v7-rule` 7.485 s / capture 0.478 against aimer v2 4.851 s / 0.843, P 0.000. v2 stays, no aimer v3.
- Gate B: `v7-fire-w1` never fires (0.07 shots per episode, capture 0.000, `score_w1` 10.063 against 8.095), P 0.000. `v7-fire-w3` the same; `v7-fire-w0` fires into the wall (10.7 wall shots per episode, capture 0.003).
- The second-stage trigger fires (Gate B failed, shots per episode < 0.5). NOT started: it waits for the user (cost, `gate-fire.md` first). Its fixed aim would be the weak `v7-rule`.
- Uncommitted in this worktree: the verdict in `gate.md`, the three fire gate CSVs and their per-model files under `gate/`, this doc. They wait for the user's review. Push, PR and merge are not granted.
- Fetched and verified (sha256, 12 `model.zip`, gate CSVs equal the repo copies): models in `runs/g101/`, archives and full measurement outputs in `runs/_download101/` (`measure/out/rule-*`, `neural-*`), both gitignored — do not remove this worktree. Instance 62712329 destroyed at about 00:57 UTC (`vastai show instances`: none); rented about 9.5 h at about $0.11/h, roughly $1.
- Not done, after the review: README, `history.js`, glossary, published runs and `published/issues/101.json`, lineage (no new aimer), pointer removal, PR.

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

### docs: 발사 조건을 재기 전에 v7-rule 측정값을 고정하기 (#101)
> why: the gate orders Gate B's baseline to be measured and frozen by sha256 in a commit before any fire condition is measured
#### Scope
`gate/v7-rule.csv`, `gate/models/v7-rule-s{0,1,2}.csv`, the sha256 line in `gate.md`, this doc.
#### Changes
- `v7-rule` (3 models, 200 episodes each, seeds 20000-20199, rule fly, env version 7) measured on the training instance with #91's `measure_v7.py`; `score.py` added the score columns.
- sha256 of `gate/v7-rule.csv`: c51d1ddbac79b57946dc7eb3cfd312f869eb8b65231b98becc83aa75e0675396.
#### Verification
- Measured values (not a verdict): pooled capture 0.478, time 7.485 s, misfires 6.648 (grazes 5.963, wall shots 0.610), `score_w1` 8.095. Per model: s0 0.690 / 6.131 s, s1 0.420 / 7.891 s, s2 0.325 / 8.433 s.
- The local copies' sha256 equal the instance's `state/pA_GATE_SHA256`.
#### Notes
- Mechanical commit made without a review while the user is asleep, as the approved gate orders it (same precedent as #91's freeze). No fire condition had been measured at this point. Verdicts are not in this commit.

### docs: 환경 버전 7 조준·발사 학습의 측정값과 판정 적기 (#101)
> why: the 12 runs are measured; the gate needs its verdict. The user reviewed the report and approved the commit on 2026-11-27 ("commit해. v7-rule이 왜 v2보다 못한지 원인부터 재봐")
#### Scope
`gate.md` (`## Verdict`), `gate/v7-fire-w{0,1,3}.csv`, `gate/models/v7-fire-*.csv`, this doc.
#### Changes
- Verdict A reject, verdict B reject, the table at the three prices, the second-stage trigger (fires, not started), neural-fly numbers, caveats.
#### Verification
- `boot.sh A`, `boot.sh B`: every gated P(better) is 0.000; outputs pasted into the verdict. Capture exclusion fires in both gates.
- `fetch.sh`: sha256 of the three archives OK, 12 models, 12 rule and 24 neural outputs, gate CSVs identical to the repo copies; instance destroyed.
#### Notes
- Gate B's baseline `v7-rule` is itself much worse than v2. Why training under version 7 gives a worse aimer than the same recipe under version 6 is not measured.

### docs: 환경 버전 7 학습의 결과와 원인 진단을 문서화하고 실행 올리기 (#101)
> why: the user asked for everything so far to be documented reproducibly, results included, and published; approved together with push, PR and merge on 2026-11-27 ("머지까지 하고 다음 실험 진행해")
#### Scope
`README.md`, `published/2026-11-26_15*_v7-*` (12 runs), `published/issues/101.json`, `viewer/src/data/history.js`, `viewer/src/data/lineage.js`, `ui-text.glossary.md`, `diagnosis.md`, `diagnosis/` (4 scripts), `hard-env-from-scratch.md`, this doc. Not `scripts/train.py`.
#### Changes
- Diagnosis of why `v7-rule` is worse than v2: config diff, training curves, measurement with the beam reaction off, measurement with sampled actions, shot statistics. Finding and limits in `diagnosis.md`; a plain-Korean version for a presentation in `hard-env-from-scratch.md`.
- README: results table of the four conditions, both verdicts, the diagnosis table, commands to reproduce training, measuring, the gate bootstrap and the diagnosis.
- Published the 12 training runs (eval episodes every 50,000 steps) and the issue page text.
- Viewer data: issue 101 in the history table, the reason for `wall_shot`, lineage node 101 under #91 (no aimer version). Glossary term.
#### Verification
- `pytest -q`: 288 passed (includes the published-run checks). `npm run build` in `viewer/`: built.
- Diagnosis numbers: `runs/_diag101/` outputs; the sampled measurement of `v7-rule` s2 run twice with identical `gate.csv`.
- `ko-writing` `check.py` on `hard-env-from-scratch.md`: no banned pattern, endings uniform, headings fixed.
#### Notes
- The causal reading (no captures during training, so no precision) is not tested; the fine-tuning run is its test.
- UI evidence not captured for the lineage node.

## Management Notes
### Follow-up Candidates
- The neural fly's reaction to the beam (teammate).
- Several flies seeing each other's flashes.
- Moving #59's training script from `algo.fireMode` to `algo.fire` (teammate).
- #85's diagnosis documents are still unpushed.
### References
- #91: `docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/gate.md` (version 7 numbers and v2 verdict), `measure_v7.py`.
- #88: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate-fire.md`, `conditions.md`.
