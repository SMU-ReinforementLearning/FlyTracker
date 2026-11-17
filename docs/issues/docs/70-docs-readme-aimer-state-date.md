# 70 README의 조준기 state 기준 날짜 고치기

## Document Relations
- Issue: #70
- Branch: `70-docs-readme-aimer-state-date`
- Umbrella: (none)
- Status: in progress

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
- [ ] The date in the aimer state paragraph is the date the 17-dimension state was fixed (#45, 2026-11-15).
- [ ] The fly state paragraph is checked against `FLY_OBS_FIELDS` history and left alone if its date is still right.
- [ ] No other README text changes.

## Current State
README date edited in the worktree, not yet committed. Waiting for the user's approval at the review gate (seed commit, then the README commit).

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

## Management Notes
### Follow-up Candidates
- `README.md`, aimer reward paragraph: "항목과 가중치는 2026-11-12 기준으로 정한 가정" although the visible-step penalty changed to beam distance in #49 (env version 5). The fly reward paragraph already carries a sentence about that change; the aimer one does not.
### References
- #32 (README state and reward, 13-dimension state, 2026-11-12), #45 (`target_rate`, `uv_fine`, env version 4, merged 2026-11-15 as d38e931).
