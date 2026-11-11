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
- [x] A 40-episode baseline run: 40 rows in the panel, no horizontal overflow of the panel or the page at 1600x900 and 390x844.
- [x] A 12-checkpoint run: 12 headers, only the selected checkpoint's rows rendered at load.
- [x] Row click plays that episode and pushes history; header click toggles without changing the selection.
- [x] ArrowUp/Down cross checkpoint boundaries and open the next checkpoint; ArrowLeft/Right change checkpoint keeping the episode number; Space toggles play; focus follows the selection.
- [x] Curve click still selects that checkpoint and opens it.
- [x] `npm run build` passes; `uv run pytest -q` passes; README passes ko-writing `check.py` and `readme_check.py`.

## Current State
- The list is implemented, verified and committed; all Done Criteria are met. Left: remove the AGENTS.md pointer line and set Status to done as the last commit, then the PR. Push only when the user asks.
- Test data in this worktree's gitignored `runs/`: `2026-11-11_164643_baseline` (40 episodes) and `2026-11-11_164919_ppo-list` (PPO, 30,000 step, 12 checkpoints × 3 episodes, no captures). Both real.
- A dev server started in this session listens on 127.0.0.1:5181 from this worktree; stop it before removing the worktree.

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

### fix: viewer 실행 패널의 에피소드를 checkpoint별 세로 목록으로 바꾸기 (#29)
> why: the grid row overflowed the panel past about 5 episodes per checkpoint
#### Scope
- `viewer/src/components/RunPanel.jsx`, `viewer/src/App.jsx` (one `key`), `viewer/src/styles.css`, `README.md`.
#### Changes
- `EpisodeGrid` → `EpisodeList`: per checkpoint a header button (disclosure, name, `captured / total`) and, when open, one row per episode (number, 포획 + time or 시간 초과, return). Rows reuse the sidebar `.row` style.
- Open state: only explicit header toggles are stored; otherwise the selected checkpoint is open. Selecting an explicitly closed checkpoint (keys, curve click) reopens it. `RunPanel` is keyed by run id so toggles reset per run.
- Keys: ArrowUp/Down step through episodes across checkpoint boundaries; ArrowLeft/Right change checkpoint keeping the episode number; Space toggles play. The selected row is scrolled into view.
- Focus follows a keyboard move through a ref set in the key handler. The first version checked `document.activeElement`, which failed when the move collapsed the checkpoint holding the focused row (found by the interaction script: ArrowUp across a boundary lost focus and later keys did nothing).
- Grid CSS (`.ep-row`, `.ep-cell`, `.ep-dot`, `.ep-miss`) removed; README 실행 패널 rewritten for the list.
#### Verification
- Interaction script as an async ui-evidence probe, 1600x900, 12-checkpoint PPO run, dev server on 5181 (serve-check `.ep-list`), all as expected after the focus fix: load shows 12 headers and 3 rows (last checkpoint open); a header click opens a second checkpoint without changing the selection or history; row click selects `step_0006000` ep 2 and pushes one entry; ArrowDown twice crosses into `step_0009000` ep 1 with focus on it and no new history entry; ArrowUp returns to `step_0006000` ep 3 with focus kept; ArrowRight twice reaches `step_0012000` ep 3, ArrowLeft `step_0009000` ep 3; Space toggles 일시정지 → 재생; closing the selected checkpoint leaves the selection; a curve click selects 학습 전 and opens it. Console errors: none.
- ui-evidence captures (Chrome 156), overflow none in all four, panel `scrollWidth <= clientWidth` and page `scrollWidth <= innerWidth` true in all four:

| run | viewport | headers | rows |
| --- | --- | --- | --- |
| baseline, 40 episodes, `ep=12` | 1600x900 | 1 (`40 / 40`) | 40 |
| baseline, 40 episodes | 390x844 | 1 | 40 |
| PPO, 12 checkpoints, `tag=step_0012000&ep=2` | 1600x900 | 12 | 3 |
| PPO, 12 checkpoints | 390x844 | 12 | 3 |

  The two 1600x900 PNGs were looked at (dark scheme): rows fit the 300 px panel, the selected row is highlighted, the panel scrolls. PNGs stay in the session scratchpad.
- `npm run build --prefix viewer` passes; `uv run pytest -q` 33 passed; ko-writing `check.py README.md` no banned pattern, no long paragraph; `readme_check.py` 0 fail, 0 warn.
#### Notes
- Not checked: light colour scheme, Firefox and Safari, more than 40 episodes in one checkpoint (rows are plain DOM; no virtualisation).
- The capture-speed shading of the grid is gone; the time is text now.

## Management Notes
### Follow-up Candidates
- Virtualised list if a checkpoint ever holds thousands of episodes.
### References
- #27 / PR #28 introduced the grid. Panel inner width is 268 px; with the checkpoint label that left room for about 5 cells of 34 px.
