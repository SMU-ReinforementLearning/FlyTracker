# 19 README에 기준선과 강화학습의 차이 넣기

## Document Relations
- Issue: #19
- Branch: `19-docs-readme-baseline-vs-rl`
- Umbrella: (none)
- Status: done

## Summary
Adds a README section on what stays the same and what changes when the rule-based baseline is replaced by a reinforcement-learning agent, with the training speed and baseline numbers measured for it. The user asked for this after a Q&A (2026-11-10) that followed #15.

## Goal
- A teammate about to run `scripts/train.py` for the first time knows: that the environment, observation and records do not change; that only the action chooser does; and the five things that start to matter (reward weights, memory, training time, how to compare with the baseline, what the records lack).

## Scope
- `README.md`: one new section after `## 에피소드와 기록`.

## Out Of Scope
- Any code change: no checkpoint evaluation script, no recurrent policy, no observation or reward change, no extra recorded fields.
- Running a real training run.

## Done Criteria
- [x] Every fact is checked against the source or measured, and each measured number states its conditions (machine, steps, seeds). (2026-11-10)
- [x] ko-writing `check.py` on `README.md` shows nothing in the new section except known false positives. (2026-11-10)
- [x] `readme_check.py` passes. (2026-11-10)
- [x] A cold-reader review of the new section is applied. (2026-11-10, two passes)
- [x] The user approved the text. (2026-11-10, "머지해")

## Current State
- Issue, branch and worktree created from `origin/main` @ 74818f1; this document seeded.
- README section committed after two cold-reader passes.
- `AGENTS.md` pointer removed in the branch's last commit; PR opened and squash-merged at the user's request.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: README에 기준선과 강화학습의 차이 넣기 (#19)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management document, Master Registry row, `AGENTS.md` pointer line.
#### Changes
- Seeded by `issue-start`; Summary, Goal, Scope, Out Of Scope, Done Criteria filled from the conversation.
#### Verification
- `issue-start` reported base `origin/main` @ 74818f1.
#### Notes
- No umbrella issue exists in this repo yet, so no `--parent`.

### docs: README에 기준선과 강화학습의 차이 넣기 (#19)
> why: the user asked for the Q&A answer on what changes when moving from the rule baseline to RL to be written down like #15
#### Scope
- `README.md` (new section `## 기준선과 강화학습` before `## viewer`), this doc.
#### Changes
- Intro: same 13-dim observation for both; the baseline chooses by rules plus its own search state, the agent by an MLP policy learned from reward only; "탐색" means searching for the lost fly, not RL exploration; the viewer labels the step-0 evaluation "학습 전".
- `### 보상`: the five reward terms with values and how the aim-error term scales; why there is no positive per-step reward.
- `### 기억`: the baseline's search state vs the MLP's two memory-like observation fields (2 s cap); three ways to add memory, of which only frame stack works without code changes and it is too short for multi-second search.
- `### 학습 시간`: measured training speed per algorithm and the 200,000-step estimate, with the measurement conditions.
- `### 기준선과 비교`: baseline numbers on 200 seeds with the command; why the agent can only win on time to capture; match seeds; 3 eval episodes are too few and no checkpoint evaluation script exists.
- `### 관측과 행동 기록`: observations and actions are not recorded, which matters more for a learned policy.
#### Verification
- Training speed, Intel Core i9-13900H, CPU only, SB3 2.9.2 defaults, torch 2.15.0+cpu: SAC 6,000 steps in 112.5 s (53/s), TD3 6,000 in 141.2 s (42/s), DQN 20,000 in 32.7 s (611/s), PPO 16,384 in 33.2 s (493/s). Environment alone with random actions: 2,486 steps/s over 5 s.
- Baseline: `record_baseline.py --episodes 200 --seed 10000 --no-save` printed 포획 200/200, 평균 보상 -19.22, 보인 비율 18%, 포획까지 평균 4.21초.
- Code facts: `RuleAimer` reads only the observation and keeps `mode`, figure-8 and band state (`flytracker/baseline.py`); `RewardWeights` and `memory_horizon=2.0` (`flytracker/env.py`); eval at training start and every `--eval-every`, seeds `--eval-seed` + i, default 3 episodes (`scripts/train.py`); `tagLabel` shows step 0 as 학습 전 (`viewer/src/data/labels.js`); no `sb3-contrib` in `pyproject.toml`; no script loads a saved model (grep for `.load(` in `scripts/` and `flytracker/` is empty).
- ko-writing `check.py README.md`: sections 1-8 clean; the one section-9 warning is the pre-existing line 36 false positive. `readme_check.py`: 0 fail, 0 warn.
- Two cold-reader passes (fresh subagent each, README only). Fixed: "one difference" contradicted by the memory difference; DQN 5.5 min rounded to 6; "학습 전" undefined; baseline command and conditions missing; 고도 띠 vs 높이 띠; agent scope; frame stack presented as memory although it covers only N × 0.02 s; the conclusion "win on time" now rests on 200/200 captured; "+ 보상"; the aim-error term's scale and its dependence on the FOV; which weights produced −19.22; 탐색 vs exploration.
#### Notes
- Left as is, with reasons: speeds measured over different step counts (each run 30 s–2 min; the 14× gap is far beyond that noise); "모델" in the run-folder tree and "놓쳤을 때 고정 벌점" in the environment table are pre-#19 text; no baseline numbers on the 3 eval seeds (the section says 3 episodes are too few to judge). No third cold-reader pass was run after the second round of fixes.

### chore: 작업 마무리와 AGENTS.md 포인터 제거 (#19)
> why: the branch's last commit before the PR; `main` takes PRs only, so the pointer must go now
#### Scope
- `AGENTS.md`, this doc's Status, Done Criteria and Current State, the registry row.
#### Changes
- `AGENTS.md` Recent Active Context: pointer line removed, `- (none)` placeholder restored.
- Status: in progress → done, here and in `docs/issues/README.md`.
#### Verification
- `grep -c 19-docs-readme-baseline-vs-rl AGENTS.md` prints 0.
#### Notes
- The user approved the text by saying "머지해".

## Management Notes
### Follow-up Candidates
- A script that loads a saved checkpoint and runs it on many seeds (the baseline has `record_baseline.py`; trained models have no equivalent), so a checkpoint can be compared with the baseline on hundreds of episodes.
- When #13 changes the observation, policies trained before it will likely need retraining.
### References
- `flytracker/baseline.py` (`RuleAimer`), `flytracker/env.py` (`RewardWeights`, `memory_horizon`), `scripts/train.py`, `scripts/record_baseline.py`, `viewer/src/data/labels.js` (`tagLabel`).
