# 18 viewer 스타일을 CSS module로 나누기

## Document Relations
- Issue: #18
- Branch: `18-refactor-viewer-css-modules`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #1 (created `viewer/src/styles.css`)
- Status: done

## Summary
Splits the viewer's single 1,053-line `viewer/src/styles.css` into one CSS module per component plus two shared files, `variables.css` (design tokens) and `global.css` (reset and base elements), following the layout of the user's wenivBlog project (`origin/develop:app/src/assets/styles/`, `app/src/components/<name>/<Name>.module.css`). Sizes move to rem on a 62.5% root (1rem = 10px) with the same pixel values, so the rendered page does not change. Restarted on 2026-11-12 from `origin/main` @ 15f5ac6: the first attempt (2026-11-10, on 74818f1, never committed) targeted a 594-line stylesheet that #22, #27 and #29 have since replaced.

## Goal
- One `.module.css` per component, in a folder per component next to its JSX (wenivBlog layout; the user chose folders over keeping the flat layout).
- Tokens (color, typography, spacing, radius, shadow) in `viewer/src/assets/styles/variables.css`, light and dark; reset and base element rules in `viewer/src/assets/styles/global.css`.
- rem units on a `html { font-size: 62.5% }` root. Borders, hairlines, 1px nudges, shadow offsets and media-query breakpoints stay px (rem in a media query is relative to the browser default, not the root).
- No visible change at the default browser font size.

## Scope
- Removed: `viewer/src/styles.css`.
- New: `viewer/src/assets/styles/variables.css`, `viewer/src/assets/styles/global.css`, `viewer/src/App.module.css`, `viewer/src/scene/FirstPersonView.module.css`.
- Moved into folders, each with its module: `viewer/src/components/{CurveChart,IssuePage,LineChart,Readouts,RunPanel,Sidebar,Transport}/<Name>.{jsx,module.css}`.
- New shared components, because their style is used by more than one component and needs one owner:
  - `IconButton` (toolbar reload and issue link, transport previous/next),
  - `Segmented` (playback speed, learning-curve metric),
  - `ListRow` with `RowList` (sidebar run rows, run-panel episode rows),
  - `Outcome` (capture dot in the toolbar and in episode rows),
  - `Tooltip` with `TooltipRow` (episode chart, learning curve),
  - `Swatch` (learning-curve tooltip, issue table).
- Import paths in `viewer/src/main.jsx`, `viewer/src/App.jsx`; the `theme.js` comment and the `IssuePage` comment that point at `styles.css`; `IssuePage` series colors read `--color-series-N`.
- `RunPanel` finds the selected episode row by its module class (`CSS.escape(styles.item)`) instead of `.ep-item`.
- `ui-evidence.config.json`: the probe that selects `.toolbar-title` (module class names are hashed).

## Out Of Scope
- Any visual change: colors, spacing, sizes, breakpoints.
- Scene files without DOM styling (`Room`, `FlyMarker`, `AimerRig`, `FrameCounter`, `ThirdPersonView`) stay where they are.
- 3D scene colors in `theme.js`.
- The duplicated `Chevron` SVG in `Sidebar` and `RunPanel` (markup, not style).
- Closed management docs that mention `styles.css`.

## Done Criteria
- [x] `npm run build` in `viewer/` passes. (2026-11-12)
- [x] Computed styles of every DOM element (and `::before`, `::after`, `::placeholder`) are identical before and after, custom properties aside, in 14 page states (run with episode chart tooltip; run with learning-curve tooltip; hover forced on every button, link and input; toggled issue group and checkpoint; baseline run; issue page with multi-series tooltip; issue page with hover forced; search with no match; search with a match; no runs; runs folder error; runs loading; run with no episodes; episode loading) × 4 widths (1600, 1200, 1000, 390 px, one per layout band) × light and dark = 112 cases, on the dev server and on the production build. The one intended difference is `html` font-size 16px → 10px (the 62.5% root). (2026-11-12)
- [x] Screenshots with the WebGL canvases hidden are pixel-identical before and after for the same cases. (2026-11-12)
- [x] `styles.css` is gone and no string-literal `className` is left in `viewer/src`. (2026-11-12)

## Current State
- Branch reset to `origin/main` @ 15f5ac6 on 2026-11-12; the 2026-11-10 attempt was saved outside the repo before the reset (patch and 11 untracked files) and used only as a reference for token names and the `IconButton` split.
- Done. Module split verified on dev and production (112 cases each); rebased onto `origin/main` @ 8e63f40 (#34, #35 touch no viewer file) and `npm run build` passes there. The user approved on 2026-11-13 and asked for the merge.
- The comparison harness stays in the session scratchpad and is not committed; whether to keep it in the repo is still open for the user.
- The fixture runs used for the comparison were removed from `runs/` afterwards; `runs/index.json` is back to its three baseline runs.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: viewer 스타일을 CSS module로 나누기 (#18)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/refactor/18-refactor-viewer-css-modules.md` filled from the user's request (CSS modules per component, rem system, shared files split out, wenivBlog layout) and the folder-layout answer.
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start`: issue #18, branch from `origin/main` @ 74818f1 (2026-11-10).
#### Notes
- No umbrella issue yet, so `--parent` was not passed.
- This seed was never committed on 2026-11-10. On 2026-11-12 the branch was reset to `origin/main` @ 15f5ac6, and the registry row and pointer line were re-added on top of it, so this commit sits on 15f5ac6.

### refactor: viewer 스타일을 CSS module로 나누기 (#18)
> why: one 1,053-line stylesheet for every screen; the user asked for one module per component on a rem system, in the wenivBlog layout
#### Scope
- `viewer/src/**` (styles, component folders, imports), `ui-evidence.config.json`, this doc.
#### Changes
- `styles.css` removed. Tokens moved to `assets/styles/variables.css` with prefixed names (`--color-*`, `--font-*`, `--space-*`, `--radius-*`, `--shadow-*`); `--series-N` became `--color-series-N` and `IssuePage` builds the new name. Base element rules moved to `assets/styles/global.css`, which also sets `html { font-size: 62.5% }`.
- `CurveChart`, `IssuePage`, `LineChart`, `Readouts`, `RunPanel`, `Sidebar`, `Transport` moved into `components/<Name>/` with a `<Name>.module.css`; `App.module.css` and `scene/FirstPersonView.module.css` next to their JSX.
- New shared components for styles that more than one component used: `IconButton` (button or new-tab link), `Segmented`, `ListRow`/`RowList`, `Outcome`, `Tooltip`/`TooltipRow`, `Swatch`.
- Overrides that crossed two modules use one more selector level instead of relying on stylesheet order: `.group .row` in `Sidebar`, `.episodes .item` in `RunPanel`. Every component imports its own module last.
- Sizes in rem (same pixel values at 1rem = 10px). Borders, 1px nudges, 1.5px hairlines, shadow offsets, outlines and media-query breakpoints stay px.
- `RunPanel` scrolls to the selected episode row via `CSS.escape(styles.item)`; `Transport` keeps `{s}×` as two text nodes (one combined string measured 1/64 px narrower in Chrome).
- `ui-evidence.config.json` probe `.toolbar-title` → `main h1`; comments in `theme.js` and `IssuePage` point at `variables.css`.
#### Verification
- Comparison harness (scratchpad `css18/compare.mjs`, headless Chrome over CDP): per case it records every element's computed style (all properties except custom properties, plus `::before`, `::after`, `::placeholder`), its bounding box, and a screenshot with the WebGL canvases hidden. Playback is paused at a fixed time first. 14 states × 4 widths × light/dark = 112 cases.
- Fixture data: two training runs written into the gitignored `runs/` for issue 99 (PPO with 3 checkpoints, SAC with 2, differing config keys); removed afterwards.
- Production build, before (`15f5ac6`) vs after: 112/112 identical screenshots; computed styles identical except `html` font-size 16px → 10px. Two "before" cases were flaky, a chevron mid-transition and 15 pixels near the transport card. The first "before" capture also differed from its own re-capture in those cases. Re-captured on both sides, they match.
- Dev server, before vs after: same result, 112/112. The two flaky "before" cases were checked against clean production "before" captures; screenshots match.
- Dev vs production, before only (88 cases): screenshots identical; styles differ only in `background-position` (the minifier rewrites `background: none`). This is why each side is compared within one build mode.
- `npm run build` passes. `grep` finds no `styles.css`, `.toolbar-title`, `.ep-item` or `icon-button` left outside closed issue docs.
#### Notes
- Claude Code stopped the background servers and one capture midway because the machine ran low on memory (1.3 GB free of 15.6 GB). The user said to continue; the rest ran in the foreground, one width at a time.
- Two vite processes from the old `FlyTracker-22` folder hold ports 5191 and 5192. They are not from this work and were left running.

### chore: #18 마무리 (#18)
> why: the branch's last commit before the PR; `main` takes PRs only, so the pointer must go now
#### Scope
- `AGENTS.md`, this doc's Status and Current State, the registry row.
#### Changes
- `AGENTS.md` Recent Active Context: pointer line removed, `- (none)` placeholder restored.
- Status: in progress → done, here and in `docs/issues/README.md`.
#### Verification
- Branch rebased onto `origin/main` @ 8e63f40 without conflicts; `git diff --stat 15f5ac6 origin/main -- viewer ui-evidence.config.json` is empty, so the before/after comparison still holds. `npm run build` passes after the rebase.
- `grep -c 18-refactor-viewer-css-modules AGENTS.md` prints 0.
#### Notes
- The user asked to merge ("머지까지 해놔"), which covers the two commits, push, PR and merge.

## Management Notes
### Follow-up Candidates
### References
- wenivBlog: `C:\Users\neighbor\Documents\Code\Github\winivBlog`, branch `origin/develop`, `app/src/assets/styles/variables.css`, `global.css`, `app/src/components/buttons/Button.module.css`.
