# 25 README의 agent 안내를 Claude Code 외 도구에도 맞게 고치기

## Document Relations
- Issue: #25
- Branch: `25-docs-readme-agent-tools`
- Umbrella: (none)
- Status: in progress

## Summary
Fixes one paragraph of `README.md` `## 시작하기` that #21 wrote as "팀 작업은 Claude Code로 한다": some team members use ChatGPT desktop or Codex, so the paragraph must hold for any AI coding tool. The user pointed this out on 2026-11-11 right after #21 merged.

## Goal
- A team member who uses Codex or ChatGPT desktop reads the README and knows where the rules are (`AGENTS.md`) and how to enable the git hooks without Claude Code's `run onboarding`.

## Scope
- `README.md`: the one paragraph in `## 시작하기` about AI coding tools.
- `README.md`: mark "조준기가 자기를 겨누는지는 모른다" (`### 초파리`) as a dated assumption that may change, and the sentence in `### 에피소드` that depends on it. Added at the same review gate on the user's request.
- `README.md`: spell out the acceleration limit in `### 관측과 행동` (the user asked what "각가속도 제한 720°/s² 안에서 따라간다" means). Added at the same gate.

## Out Of Scope
- Changes to `AGENTS.md`, the onboarding runbook or the hooks themselves.
- Documenting any tool-specific setup beyond "read `AGENTS.md`" and the hook command.

## Done Criteria
- [ ] The paragraph names Claude Code, Codex and ChatGPT desktop as examples and gives the manual hook command (`git config core.hooksPath .githooks`, as in `docs/agent-workflow/onboarding.md` §3).
- [ ] The fly's ignorance of the aim direction is stated as an assumption dated 2026-11-11, and the episode sentence that depends on it says so.
- [ ] `check.py` shows no new finding in the changed text; `readme_check.py` passes.
- [ ] The user approved the text at the review gate.

## Current State
- Issue, branch and worktree created from `origin/main` @ 25af854; this document seeded.
- Paragraph rewritten; waiting for the review gate.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: README의 agent 안내를 Claude Code 외 도구에도 맞게 고치기 (#25)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management document, Master Registry row, `AGENTS.md` pointer line.
#### Changes
- Seeded by `issue-start`; Summary, Goal, Scope, Out Of Scope, Done Criteria filled from the user's correction.
#### Verification
- `issue-start` reported base `origin/main` @ 25af854.
#### Notes
- No umbrella issue exists in this repo yet, so no `--parent`.

### docs: README의 agent 안내를 Claude Code 외 도구에도 맞게 고치기 (#25)
> why: the user said "chatgpt desktop, codex 쓰는 팀원도 있어" — the README must not assume Claude Code
#### Scope
- `README.md` `## 시작하기`, last paragraph; this doc.
#### Changes
- "팀 작업은 Claude Code로 한다" → the rules live in `AGENTS.md` for any AI coding tool (Claude Code, Codex, ChatGPT desktop named as examples); Claude Code's `run onboarding` enables the hooks and checks Node and GitHub CLI; other tools are pointed at `AGENTS.md` and the git hooks are enabled by hand with `git config core.hooksPath .githooks`.
- "AI 코딩 도구" is used instead of "agent" because the README reserves agent for the reinforcement-learning policy.
#### Verification
- Hook command taken from `docs/agent-workflow/onboarding.md` §3.
- ko-writing `check.py README.md`: no new finding (the known false positives from #21 remain); `readme_check.py`: 0 fail, 0 warn.
#### Notes
- `PYTHONUTF8=1` (onboarding §3, Windows only) is not in the README; the hook prints the message itself when it trips.

### docs: 초파리가 조준 방향을 모른다는 것을 가정으로 표시 (#25)
> why: the user said this may change ("오늘 기준 가정이라고 써놔. 바뀔 수 있는 부분이니까"); the fly's threat rule for a turret is an open decision since #7
#### Scope
- `README.md` `### 초파리` last sentence and `### 에피소드` last sentence; this doc.
#### Changes
- "조준기가 자기를 겨누는지는 모른다." → "…모른다고 가정한다. 이 가정은 2026-11-11 기준이고 바뀔 수 있다."
- `### 에피소드`: the claim "정책이 달라도 경로는 같다" now says it follows from that assumption and changes with it.
#### Verification
- ko-writing `check.py README.md`: no new finding; `readme_check.py`: 0 fail, 0 warn.
#### Notes
- The code today matches the assumption: `FlyParams` reacts to distance and closing rate only (`evade_radius`, `evade_looming_rate`, `evade_proximity`), never to the aim direction.

### docs: 행동의 각가속도 제한을 풀어 쓰기 (#25)
> why: the user asked what "각가속도 제한 720°/s² 안에서 따라가고" means; the sentence named the limit without saying what it does
#### Scope
- `README.md` `### 관측과 행동`, the action paragraph; this doc.
#### Changes
- The action is now called the target angular rate; the real rate moves toward it by at most 720°/s per second, so 0 → 180°/s takes 0.25 s. Same facts as before, stated as a consequence a reader can picture.
#### Verification
- `Aimer.step` (`flytracker/aimer.py`): `approach(rate, action × max_rate, max_ang_accel × dt)` per 0.01 s physics step → 7.2°/s per step, 180 ÷ 720 = 0.25 s from rest to full yaw rate.
- ko-writing `check.py README.md`: no new finding; `readme_check.py`: 0 fail, 0 warn.
#### Notes
- The 0.25 s figure is for yaw; pitch (120°/s) reaches its top rate in 0.17 s, not stated to keep the sentence short.

## Management Notes
### Follow-up Candidates
### References
