# 18 viewer 스타일을 CSS module로 나누기

## Document Relations
- Issue: #18
- Branch: `18-refactor-viewer-css-modules`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #1 (created `viewer/src/styles.css`)
- Status: in progress

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
- [ ] `npm run build` in `viewer/` passes.
- [ ] Computed styles of every DOM element (and `::before`, `::after`, `::placeholder`) are identical before and after, custom properties aside, in 14 page states (run with episode chart tooltip; run with learning-curve tooltip; hover forced on every button, link and input; toggled issue group and checkpoint; baseline run; issue page with multi-series tooltip; issue page with hover forced; search with no match; search with a match; no runs; runs folder error; runs loading; run with no episodes; episode loading) × 4 widths (1600, 1200, 1000, 390 px, one per layout band) × light and dark = 112 cases, on the dev server and on the production build. The one intended difference is `html` font-size 16px → 10px (the 62.5% root).
- [ ] Screenshots with the WebGL canvases hidden are pixel-identical before and after for the same cases.
- [ ] `styles.css` is gone and no string-literal `className` is left in `viewer/src`.

## Current State
- Branch reset to `origin/main` @ 15f5ac6 on 2026-11-12; the 2026-11-10 attempt was saved outside the repo before the reset (patch and 11 untracked files) and used only as a reference for token names and the `IconButton` split.
- Next: split `styles.css` into modules, then compare computed styles and screenshots before and after.

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

## Management Notes
### Follow-up Candidates
### References
- wenivBlog: `C:\Users\neighbor\Documents\Code\Github\winivBlog`, branch `origin/develop`, `app/src/assets/styles/variables.css`, `global.css`, `app/src/components/buttons/Button.module.css`.
