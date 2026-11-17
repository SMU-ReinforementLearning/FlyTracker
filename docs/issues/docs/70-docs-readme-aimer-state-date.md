# 70 README의 조준기 state 기준 날짜 고치기

## Document Relations
- Issue: #70
- Branch: `70-docs-readme-aimer-state-date`
- Umbrella: (none)
- Status: done

## Summary
The README's aimer state paragraph dates the choice of state items to 2026-11-12, but the 17-dimension state it describes was fixed by #45 on 2026-11-15. This issue corrects that one date.

## Goal
The date in `README.md`, section "조준기의 state와 action", matches the state the paragraph describes.

## Scope
- `README.md`: the sentence "어떤 항목을 넣을지는 2026-11-12 기준으로 정한 가정이고" in the aimer state paragraph. 2026-11-12 → 2026-11-15.

## Out Of Scope
- The other "2026-11-12 기준" sentences in the README (fly assumptions, aimer reward, fly state, fly reward). The aimer reward sentence may be stale in the same way (the reward changed in #49); see Follow-up Candidates.
- Any code or viewer change.

## Done Criteria
- [x] The date in the aimer state paragraph is the date the 17-dimension state was fixed (#45, 2026-11-15). (2026-11-18 00:00)
- [x] The fly state paragraph is checked against `FLY_OBS_FIELDS` history and left alone if its date is still right. (2026-11-18 00:00)
- [x] No other README text changes. (2026-11-18 00:00)

## Current State
Done 2026-11-18. The aimer state paragraph of the README now says 2026-11-15. The aimer reward paragraph's date is a follow-up candidate, not handled here.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: README의 조준기 state 기준 날짜 고치기 (#70)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, Master Registry row, `AGENTS.md` pointer line.
#### Changes
- `docs/issues/docs/70-docs-readme-aimer-state-date.md` created and filled.
- `docs/issues/README.md`: row for #70.
- `AGENTS.md`: pointer line under Recent Active Context.
#### Verification
- `issue-start.mjs` summary: issue #70, branch from `origin/main` @ fdbb86e.
#### Notes

### docs: README의 조준기 state 기준 날짜 고치기 (#70)
> why: the paragraph says "17차원" but dated the choice of items to 2026-11-12, when the state had 13 dimensions
#### Scope
`README.md`, aimer state paragraph, one date.
#### Changes
- "어떤 항목을 넣을지는 2026-11-12 기준으로 정한 가정" → "2026-11-15 기준". 2026-11-15 is the merge date of #45 (d38e931), which added `target_rate` and `uv_fine`.
#### Verification
- `git diff --stat -- README.md`: 1 file changed, 1 insertion, 1 deletion.
- `git log -L` on `OBS_FIELDS` history (`-G'target_rate|uv_fine'`): only d38e931, 2026-11-15.
- Fly state paragraph left alone: `git log -L` on `FLY_OBS_FIELDS` shows 64c60ff (#34, 2026-11-12) and 7a81d0a (#42), and the #42 diff changes one comment, no item.
#### Notes
- The aimer reward paragraph's date was not touched (out of scope, listed under Follow-up Candidates).

### chore: #70 마무리 (#70)
> why: last commit before the PR; a protected base branch cannot take the pointer removal after the merge
#### Scope
`AGENTS.md`, `docs/issues/README.md`, this doc.
#### Changes
- Status done here and in the Master Registry; `AGENTS.md` pointer line removed.
#### Verification
- `git diff --stat`: three files, no README change.
#### Notes

## Management Notes
### Follow-up Candidates
- `README.md`, aimer reward paragraph: "항목과 가중치는 2026-11-12 기준으로 정한 가정" although the visible-step penalty changed to beam distance in #49 (env version 5). The fly reward paragraph already carries a sentence about that change; the aimer one does not.
### References
- #32 (README state and reward, 13-dimension state, 2026-11-12), #45 (`target_rate`, `uv_fine`, env version 4, merged 2026-11-15 as d38e931).
