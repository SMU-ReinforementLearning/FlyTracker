# 36 README에서 조준기 쪽 state와 R을 공통 부분과 나누기

## Document Relations
- Issue: #36
- Branch: `36-docs-readme-aimer-side`
- Umbrella: (none)
- Status: done

## Summary
Separates, in the README's `## 환경`, what the aimer and the fly share (room, aimer, fly, episode) from what belongs to the aimer agent only (state, action, R), and calls the learned aimer "조준기 agent" everywhere. The user asked on 2026-11-12 right after #32 merged, because #31/#34 will add a learned fly with its own state, action and R ("조준기 입장의 state와 R, 에피소드 … 구분해야 할 거 같은데").

## Goal
- A reader can tell which parts of `## 환경` hold for both sides and which are the aimer agent's, so the fly side can be added later without rewording the aimer side.

## Scope
- `README.md` `## 환경`: move `### 에피소드` before the state section; rename `### state와 action` → `### 조준기의 state와 action` and `### R` → `### 조준기의 R`; add a short paragraph under `## 환경` saying which sections are shared and which are the aimer agent's, and that no fly-side training environment exists yet.
- `README.md`: every "agent" that means the aimer policy becomes "조준기 agent" (user's choice, AskUserQuestion 2026-11-12); "정책이 달라도" in `### 에피소드` becomes "조준기 정책이 달라도".
- Structure chosen by the user: "공통과 조준기 쪽 분리" (AskUserQuestion, 2026-11-12).

## Out Of Scope
- Writing the fly's state, action or R; they do not exist yet (#31, #34).
- `### 초파리` (fly motion will change with the learned fly model).
- Code changes.

## Done Criteria
- [x] `### 에피소드` sits before `### 조준기의 state와 action` and `### 조준기의 R`; the `## 환경` intro names the shared and the aimer-only sections. (2026-11-12)
- [x] No bare "agent" meaning the aimer policy is left in `README.md`. (2026-11-12)
- [x] No link in the repo points at the renamed anchors; `#에피소드` still resolves. (2026-11-12)
- [x] ko-writing `check.py README.md` shows no new finding except the user-chosen heading length; `readme_check.py` passes. (2026-11-12)
- [x] The user approved the text at the review gate. (2026-11-12, "머지해")

## Current State
- Issue, branch and worktree created from `origin/main` @ 0cda845; this document seeded and filled.
- #34 (조준기와 초파리를 번갈아 학습하는 환경 만들기) and #35 were opened just before this issue; neither has a branch on the remote yet, so no README conflict today.
- README change committed after the user's approval ("머지해").
- `AGENTS.md` pointer removed in the branch's last commit; PR opened and squash-merged at the user's request.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: README에서 조준기 쪽 state와 R을 공통 부분과 나누기 (#36)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management document, Master Registry row, `AGENTS.md` pointer line.
#### Changes
- Seeded by `issue-start`; Summary, Goal, Scope, Out Of Scope, Done Criteria filled from the conversation.
#### Verification
- `issue-start` reported base `origin/main` @ 0cda845.
#### Notes
- No umbrella issue exists in this repo yet, so no `--parent`.

### docs: README에서 조준기 쪽 state와 R을 공통 부분과 나누기 (#36)
> why: a learned fly (#31, #34) will get its own state, action and R, so the README must say which parts are the aimer's and which both sides share
#### Scope
- `README.md` intro, parts table, `## 환경`, `## 학습 코드`; this doc.
#### Changes
- `## 환경`: new paragraph after the step sentence. Only the aimer is trained today; 방과 좌표, 조준기, 초파리, 에피소드 are shared; 조준기의 state와 action and 조준기의 R are the aimer agent's; no fly-training environment exists yet, and when one does the fly gets its own state, action, R.
- Section order: 방과 좌표, 조준기, 초파리, 에피소드, 조준기의 state와 action, 조준기의 R (episode moved up unchanged except "조준기 정책이 달라도").
- Headings: `### state와 action` → `### 조준기의 state와 action`, `### R` → `### 조준기의 R`.
- Every "agent" meaning the aimer policy → "조준기 agent" (lines in the intro, the parts table, `## 환경`, state, R, 기준선, 학습, 기준선과 비교, 에피소드 파일의 한계). In 에피소드 파일의 한계 the fourth repeat was dropped by making "이상하게 움직이는 이유" subjectless; the subject is the previous clause's.
#### Verification
- `grep -n agent README.md | grep -v "조준기 agent"` prints nothing.
- No file in the repo links to `#state와-action`, `#r` or the new anchors; `#에피소드` (used by the R details) still exists.
- ko-writing `check.py README.md` vs `origin/main`: one new finding, heading length 18 > 15 for `조준기의 state와 action`; kept because the user picked this exact heading. `readme_check.py`: 0 fail, 0 warn.
#### Notes
- #34 (alternating aimer/fly training env) will add the fly side; that branch should add `### 초파리의 state와 action` and `### 초파리의 R` after the aimer sections.

### chore: #36 마무리 (#36)
> why: the branch's last commit before the PR; `main` takes PRs only, so the pointer must go now
#### Scope
- `AGENTS.md`, this doc's Status and Current State, the registry row.
#### Changes
- `AGENTS.md` Recent Active Context: pointer line removed, `- (none)` placeholder restored.
- Status: in progress → done, here and in `docs/issues/README.md`.
#### Verification
- `grep -c 36-docs-readme-aimer-side AGENTS.md` prints 0.
#### Notes
- The user asked to merge ("머지해"), which covers push, PR and merge.

## Management Notes
### Follow-up Candidates
### References
