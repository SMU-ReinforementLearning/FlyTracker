# 32 README에 state와 R 항목 설명 넣기

## Document Relations
- Issue: #32
- Branch: `32-docs-readme-state-reward`
- Umbrella: (none)
- Status: in progress

## Summary
Renames the README's `### 관측과 행동` to `### state와 action` and `### 보상` to `### R`, and adds a folded per-row explanation under the state table and the R table. The user asked on 2026-11-12, after walking through the 13-dim observation and the reward terms in chat, for "토글로 쉽게 각 설명 … 사람이 읽히게, 간단명료하게", and for the state layout and reward to be marked as assumptions that may change.

## Goal
- A team member reading `## 환경` can tell what each state row and each R row means without opening `flytracker/env.py`, and knows both are current assumptions, not fixed design.

## Scope
- `README.md` `### 관측과 행동` → `### state와 action`: first sentence ties state to 관측; a `<details>` under the table explains each row; one sentence marks the state layout as an assumption dated 2026-11-12.
- `README.md` `### 보상` → `### R`: first sentence ties R to 보상; a `<details>` under the table explains each row; the closing sentence marks terms and weights as an assumption dated 2026-11-12.
- Heading structure chosen by the user: "state와 action, R 따로" (AskUserQuestion, 2026-11-12).

## Out Of Scope
- `### 초파리`: the user said fly motion will change when a teammate trains it, so it is left as is.
- Any code change; the explanations describe `flytracker/env.py` and `flytracker/camera.py` as they are at 7237428.
- Renaming 관측/행동/보상 elsewhere in the README body.

## Done Criteria
- [ ] Both headings renamed; no link in the repo pointed at the old anchors (`#관측과-행동`, `#보상`).
- [ ] Every row of both tables has an explanation in its `<details>`, and each stated number matches the code.
- [ ] State layout and R are marked as assumptions with the date.
- [ ] ko-writing `check.py README.md` shows no new finding in the changed text; `readme_check.py` passes.
- [ ] The user approved the text at the review gate.

## Current State
- Issue, branch and worktree created from `origin/main` @ 7237428; this document seeded and filled.
- README change written and checked; waiting for the user's approval at the review gate.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: README에 state와 R 항목 설명 넣기 (#32)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management document, Master Registry row, `AGENTS.md` pointer line.
#### Changes
- Seeded by `issue-start`; Summary, Goal, Scope, Out Of Scope, Done Criteria filled from the conversation.
#### Verification
- `issue-start` reported base `origin/main` @ 7237428.
#### Notes
- No umbrella issue exists in this repo yet, so no `--parent`.

### docs: README에 state와 R 항목 설명 넣기 (#32)
> why: the user asked for the README to name the section in RL terms and to explain each state row and each reward row in plain words, marked as assumptions that may change
#### Scope
- `README.md` `### state와 action` (was `### 관측과 행동`) and `### R` (was `### 보상`); this doc.
#### Changes
- `### state와 action`: opens with "state는 agent가 step마다 받는 관측이고 13차원이다" so the rest of the README can keep saying 관측; adds the dated assumption sentence; adds `<details>` "항목별 설명" under the table (8 dims fly, 5 dims aimer; one bullet per row); the action paragraph now starts "action은 … 2차원 행동이고".
- `### R`: opens with "R은 agent가 step마다 받는 보상이다"; adds `<details>` "항목별 설명" under the table (lost and aim-error penalties are mutually exclusive; one bullet per row with a worked action-change example); the closing sentence marks terms and weights as an assumption dated 2026-11-12.
#### Verification
- Facts checked against code at 7237428: `visible` = in front, |u|,|v| ≤ 1, depth ≤ far 10 m (`camera.py:62`), far exceeds the 5.59 m room diagonal; `uv` x right / y up; distance ÷ `room.diagonal`; `last_seen_dir` recomputed in the current camera basis each step, 0 before the first sighting (`env.py:229-232`); `time_since_seen` starts at `memory_horizon` → 1.0 (`env.py:148`); yaw wraps (`aimer.py:60`), pitch ÷ 80°; rates ÷ 180°/s and 120°/s; reward terms and weights from `RewardWeights`, lost vs aim-error branch in `_reward`, `_prev_action` zeroed at reset.
- Action-change example: mean((2, 0)²) × 0.01 = 0.02.
- ko-writing `check.py README.md` vs the `origin/main` README: only new findings are the two assumption dates (section 13), intended, same pattern as the 2026-11-11 fly assumption. `readme_check.py`: 0 fail, 0 warn.
- `grep` for `#관측과-행동` and `#보상`: no links; only historical mentions in the #19, #21, #25 docs.
#### Notes
- 관측/행동/보상 stay in the rest of the README body; the two opening sentences tie state, action and R to them.

## Management Notes
### Follow-up Candidates
### References
