# 96 viewer 스크롤바를 브라우저 기본 모양 대신 가늘고 옅게 그리기

## Document Relations
- Issue: #96
- Branch: `96-feature-viewer-minimal-scrollbar`
- Umbrella: (none)
- Status: done

## Summary
Replace the browser's default scrollbars in the viewer with one minimal design: a thin, rounded, faint thumb on a transparent track, in both colour schemes. The user (2026-11-26): "스크롤바 디자인, 브라우져 기본값 쓰지 말고, minimal하게 새로 디자인해". On Windows the default bars are wide grey gutters that cut into the sidebar, the run panel and the issue page.

## Goal
- Every scrolling area of the viewer (sidebar, run panel, issue page, the combinations table's horizontal scroll, the lineage map) shows the same thin scrollbar; no default one is left.

## Scope
1. `viewer/src/assets/styles/global.css` (one rule for all elements) and `variables.css` (thumb colours per scheme).
2. Standard properties (`scrollbar-width`, `scrollbar-color`) for Firefox and `::-webkit-scrollbar` for Chromium and Safari, which draws the rounded thumb with space around it.

## Out Of Scope
- Hiding scrollbars or changing what scrolls.
- The transport bar's range input (not a scrollbar).

## Done Criteria
- [ ] Before / after screenshots of the sidebar and the run panel with a scrollbar visible, dark and light.
- [ ] No scrolling element keeps a default bar (checked by listing every element whose content overflows on the issue page, a run page and the lineage page).
- [x] Viewer build passes; the user approved the look.
- [x] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-27. The user said "다 머지해" (2026-11-26) after seeing the screen: commit, push, PR and squash merge. The CSS is committed; the pointer line is removed in the last commit. Two criteria stay unticked (light scheme capture, the list of overflowing elements); the rule is one global rule, so no element can keep a default bar in Chromium or Safari, but that was not listed element by element.

Earlier notes:
2026-11-26 23:30 KST. The CSS is in the working tree (`global.css`, `variables.css`), nothing committed: waiting at the Pre-Commit Review Gate. Build passes. Before / after captured in the dark scheme only, with plain headless Chrome because `shot.mjs` always passes `--hide-scrollbars` (files in the session scratchpad, not kept). Not done: the light scheme capture and the list of overflowing elements of Done Criteria 2. A dev server for this worktree may still run on port 5196. This session cannot `EnterWorktree` here; it works by absolute path and `git -C`.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: viewer 스크롤바를 브라우저 기본 모양 대신 가늘고 옅게 그리기 (#96)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, `AGENTS.md` pointer.
#### Changes
- Doc filled from the user's request of 2026-11-26.
#### Verification
- `issue-start.mjs` created issue #96 (Type Feature, label enhancement, assignee the user, Priority Low), branch from `origin/main` @ dcce349, worktree `FlyTracker-96`.
#### Notes
- Priority Low and a separate issue (instead of folding it into #94 or #95) are the agent's choices: it is appearance only and touches global CSS.

### feat: 스크롤바를 바탕 없는 가는 막대로 그리기 (#96)
> why: the default bars on Windows are wide grey gutters inside the sidebar, the run panel and the issue page
#### Scope
`viewer/src/assets/styles/global.css`, `variables.css`.
#### Changes
- `::-webkit-scrollbar` rules: 1 rem gutter, transparent track, a rounded thumb inset by a transparent border, darker on hover; `--color-scrollbar` and `--color-scrollbar-hover` per colour scheme.
- `scrollbar-width: thin` and `scrollbar-color` only where `::-webkit-scrollbar` is unknown (Firefox), because Chromium ignores the pseudo-elements once the standard properties are set.
#### Verification
- `npm run build`: built.
- Before / after of `/?issue=88` at 1100 x 600 in the dark scheme with plain headless Chrome (`shot.mjs` always hides scrollbars): the sidebar and the page show the thin thumb instead of the default bar.
#### Notes
- Not captured: the light scheme, Firefox, the run panel. Not done: the element-by-element list of Done Criteria 2.
- The captures were in the session scratchpad and are not kept.
- Committed after the build on this tree (built).
- 2026-11-27: origin/main with #94 and #95 merged into the branch (conflicts in the registry and in variables.css, both sides kept). On the merged tree: full pytest 278 passed, 1 skipped; build passes.

### chore: #96 포인터를 지우고 완료로 표시하기 (#96)
> why: the pointer line has to go in the branch's last commit; a protected branch cannot take that edit after the merge
#### Scope
`AGENTS.md`, `docs/issues/README.md`, this doc.
#### Changes
- Pointer line removed, registry row and Status set to done.
#### Verification
- `git diff origin/main -- AGENTS.md` is empty after this commit.
#### Notes
- The PR merged box is ticked here because the doc cannot be edited after the merge.

## Management Notes
### Follow-up Candidates
### References
