# 29 viewer 실행 패널의 에피소드를 checkpoint별 세로 목록으로 바꾸기

## Document Relations
- Issue: #29
- Branch: `29-fix-viewer-episode-list`
- Umbrella: (none)
- Status: in progress

## Summary
The run panel's episode grid (#27) puts every episode of a checkpoint on one horizontal row of fixed 34 px cells, so a checkpoint with more than about 5 episodes overflows the 300 px panel; this replaces it with a vertical list grouped by checkpoint. The user pointed at the row on 2026-11-11 ("episode가 다섯개 수준이 아니고 엄청 많을 거잖아"), said the panel only holds one run so a vertical list is enough, and chose the collapsible variant from two previews.

## Goal
- A run whose checkpoints hold many episodes (for example `record_baseline.py --episodes 40`) shows all of them in the run panel with no horizontal overflow; the panel scrolls vertically.
- A run with many checkpoints stays short: only the selected checkpoint is open, the others are one header line each.

## Scope
- `viewer/src/components/RunPanel.jsx`: `EpisodeGrid` → `EpisodeList`. One section per checkpoint: a header button (checkpoint name, captured / total, disclosure) and, when open, one row per episode (number, outcome with capture time, return).
- Open state: the selected checkpoint is open; headers toggle; moving the selection to another checkpoint opens it.
- Keys inside the list: ArrowUp/ArrowDown previous/next episode across checkpoints, ArrowLeft/ArrowRight previous/next checkpoint keeping the episode number (same eval seed), Space toggles play.
- `viewer/src/styles.css`: grid styles replaced by list styles.
- `README.md` 실행 패널 subsection.

## Out Of Scope
- Virtualised rendering for thousands of rows.
- Filtering or sorting episodes (captured only, by time).
- The "faster capture = darker dot" encoding of the grid; the row now shows the capture time as text.
- The issue page and the sidebar.

## Done Criteria
- [ ] A 40-episode baseline run: 40 rows in the panel, no horizontal overflow of the panel or the page at 1600x900 and 390x844.
- [ ] A 12-checkpoint run: 12 headers, only the selected checkpoint's rows rendered at load.
- [ ] Row click plays that episode and pushes history; header click toggles without changing the selection.
- [ ] ArrowUp/Down cross checkpoint boundaries and open the next checkpoint; ArrowLeft/Right change checkpoint keeping the episode number; Space toggles play; focus follows the selection.
- [ ] Curve click still selects that checkpoint and opens it.
- [ ] `npm run build` passes; `uv run pytest -q` passes; README passes ko-writing `check.py` and `readme_check.py`.

## Current State
- Seeded. Test data in this worktree's gitignored `runs/`: `2026-11-11_164643_baseline` (40 episodes, real).

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: viewer 실행 패널의 에피소드를 checkpoint별 세로 목록으로 바꾸기 (#29)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, AGENTS.md pointer.
#### Changes
- Seeded by `issue-start.mjs`; sections filled from the 2026-11-11 conversation.
#### Verification
- `git status --short`: only the three seeded files.
#### Notes
- (none)

## Management Notes
### Follow-up Candidates
- Virtualised list if a checkpoint ever holds thousands of episodes.
### References
- #27 / PR #28 introduced the grid. Panel inner width is 268 px; with the checkpoint label that left room for about 5 cells of 34 px.
