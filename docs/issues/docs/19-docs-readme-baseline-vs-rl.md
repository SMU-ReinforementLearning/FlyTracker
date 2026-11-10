# 19 README에 기준선과 강화학습의 차이 넣기

## Document Relations
- Issue: #19
- Branch: `19-docs-readme-baseline-vs-rl`
- Umbrella: (none)
- Status: in progress

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
- [ ] The user approved the text.

## Current State
- Issue, branch and worktree created from `origin/main` @ 74818f1; this document seeded.
- README section written, measured and reviewed; nothing committed yet. Waiting for the user's approval at the pre-commit review gate.

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

## Management Notes
### Follow-up Candidates
- A script that loads a saved checkpoint and runs it on many seeds (the baseline has `record_baseline.py`; trained models have no equivalent), so a checkpoint can be compared with the baseline on hundreds of episodes.
- When #13 changes the observation, policies trained before it will likely need retraining.
### References
- `flytracker/baseline.py` (`RuleAimer`), `flytracker/env.py` (`RewardWeights`, `memory_horizon`), `scripts/train.py`, `scripts/record_baseline.py`, `viewer/src/data/labels.js` (`tagLabel`).
