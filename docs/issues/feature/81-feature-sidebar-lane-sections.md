# 81 사이드바의 issue 묶음을 초파리, 조준기, 환경으로 나누기

## Document Relations
- Issue: #81
- Branch: `81-feature-sidebar-lane-sections`
- Umbrella: (none)
- Status: in progress

## Summary
The viewer sidebar lists its issue groups under three area headings (fly, aimer, environment), the same areas the lineage map uses as lanes. Before, the sidebar was one flat list ordered by the latest run, so the area an issue belongs to could be read on the map but not in the sidebar next to it.

## Goal
- A reader finds an issue in the sidebar by its area, with the same area names and the same order as the lineage map.
- The area of an issue comes from one place (`lane` in `viewer/src/data/lineage.js`); the sidebar adds no second table.

## Scope
- `viewer/src/data/lineage.js`: `laneOf(issueNumber)` returns the lane key of an issue, or null when the issue is not a node.
- `viewer/src/data/runs.js`: `sectionsByLane(groups)` splits the issue groups into one section per lane, in `LANES` order, keeping the order inside a section (latest run first). Groups with no lane (runs without an issue, or an issue missing from the map) go into a last section with no heading.
- `viewer/src/components/Sidebar/`: a heading per section; a section with no group left (none published, or filtered out by the search) is not drawn.
- `tests/test_viewer_lineage.py`: a test for the split.
- `README.md` viewer section, `ui-text.glossary.md`.

## Out Of Scope
- Showing an issue under every area it changed (`also`). An issue appears once, under its main lane, as on the map.
- Regrouping runs by the fly, aimer or environment version they used (proposed first from a stale checkout, then dropped; the user chose the lane sections on 2026-11-25).
- The lineage map itself (#80 is working on it) and the issue page.

## Done Criteria
- [x] The sidebar shows the headings 초파리, 조준기, 환경 in that order, each followed by the issue groups of that lane. (2026-11-25 20:25)
- [x] Every issue group that was in the sidebar before is still there, exactly once. (2026-11-25 20:25)
- [x] Searching hides a section that has no matching run. (2026-11-25 20:40)
- [x] No horizontal overflow at 1600 and 390 px; screenshots taken. (2026-11-25 20:25)
- [x] `pytest` and `npm run build` pass. (2026-11-25 20:25)
- [x] User approved the sidebar. (2026-11-25 20:40)

## Current State
Implemented, verified and approved for merge by the user ("머지해", 2026-11-25). Nothing is left open on this branch.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 사이드바의 issue 묶음을 초파리, 조준기, 환경으로 나누기 (#81)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Seed only: this document, the registry row, the AGENTS.md pointer.
#### Changes
- `docs/issues/feature/81-feature-sidebar-lane-sections.md` (new), `docs/issues/README.md` (+1 row), `AGENTS.md` (pointer line).
#### Verification
None needed; no code changed.
#### Notes
The first proposal in the session (a switch that regroups runs by the fly, aimer or environment version they used) was written from a local `main` four commits behind `origin/main`, before #77's lineage map was known to exist. After `git fetch` the user was asked again and chose sections that follow the map's lanes.

### feat: 사이드바의 issue 묶음을 초파리, 조준기, 환경으로 나누기 (#81)
> why: the lineage map shows which area an issue belongs to, but the sidebar beside it was one flat list
#### Scope
Lane sections in the sidebar, their test, README and glossary.
#### Changes
- `viewer/src/data/lineage.js`: `laneOf(number)`.
- `viewer/src/data/runs.js`: `sectionsByLane(groups)`; sections in `LANES` order, groups keep their order, groups without a lane go to a last unnamed section, empty sections are dropped.
- `viewer/src/components/Sidebar/Sidebar.jsx`: groups are drawn inside `<section>` per lane with an `<h2>` heading. `Sidebar.module.css`: `.lane`, `.laneName` (13px semibold, primary colour; group names stay 12px secondary).
- `tests/test_viewer_lineage.py`: `test_sidebar_sections_follow_the_lanes`.
- `README.md` (실행 목록), `ui-text.glossary.md` (area names are also the sidebar headings).
#### Verification
- `uv run python -m pytest -q`: 217 passed (after `uv sync --extra neural --extra train --extra dev`; a first run with the main checkout's interpreter failed 47 tests on missing `pyarrow`, unrelated to this change).
- `npm run build` in `viewer/`: built.
- ui-evidence, base `http://127.0.0.1:5181` (this worktree's dev server), commit ee4c5a1 (dirty), Chrome 157.0.8103.80, serve check `document.querySelectorAll('nav h2').length === 3`:

| page | viewport | overflow | probes | console |
| --- | --- | --- | --- | --- |
| /?issue=69 | 1600x900 | none | headings and groups: 초파리:1 조준기:7 환경:2; heading font 13px | clean |
| /?issue=69 | 390x844 (mobile, dpr 2) | none | same | clean |
| / | 1600x900 | none | three headings present | 404 for favicon.ico only |
| / | 390x844 (mobile, dpr 2) | none | three headings present | clean |

  Captures are not committed (`.ui-evidence/` is gitignored). The 1600px capture of `/?issue=69` shows 초파리 (#31), 조준기 (#72, #61, #51, #49, #45, #35, #22), 환경 (#69 opened with its three variations, #42). Ten groups, the same ten issues that have published runs.
#### Notes
Search checked in the browser after the first review summary: typing `#69` into the search box leaves the single heading 환경 (ui-evidence probe at 1600x900). The user approved with "머지해" (2026-11-25).

## Management Notes
### Follow-up Candidates
### References
