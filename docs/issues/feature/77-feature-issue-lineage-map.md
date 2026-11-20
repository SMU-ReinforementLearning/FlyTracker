# 77 viewer 첫 화면에 issue 계보 넣고 사이드바 실행을 조건으로 묶기

## Document Relations
- Issue: #77
- Branch: `77-feature-issue-lineage-map`
- Umbrella: (none)
- Status: in progress

## Summary
The viewer opens on a lineage map: issues laid out as nodes in three lanes (fly, aimer, environment), ordered by time, joined by lines to the issues they build on. Before, the only level above an issue page was the sidebar's flat list of issues, where the user's and the teammate's work were interleaved and the order of development could not be read. The sidebar also changes: inside an opened issue, runs are grouped by variation, each headed by label/value lines saying what differs, instead of being told apart by run name only.

## Goal
- A reader sees at a glance which area each issue belongs to, what it came from, and what it led to — including across lanes (environment #42 → aimer #45).
- The issue page and everything below it stay as they are; the map is a new level above them.
- Inside an issue, a reader can tell runs apart by what was varied (fly kind, aimer kind, stimulus, reward), not by parsing `neural-nostim-sac-beam-assist-s0`.

## Scope
- `viewer/src/data/lineage.js` (new): hand-written table `issue → { lane, also, parents, name, result, envVersion }` and `lineageOf()`, which assigns rows and returns nodes and edges.
- Issue names (user review, 2026-11-20): `name` in `lineage.js` says what changed in 15 characters or fewer ("포획을 레이저 명중으로"), and `issueName()` makes the map node, the sidebar group, the issue page title, the provenance popover and the compare link all use it. The GitHub issue title stays as the hover tooltip. `name` no longer has to equal `phase`; the test now checks length, uniqueness, and that no name is the issue title.
- `viewer/src/data/history.js`: `ISSUES` gains #22, #61, #64; new `issueOf(number)`.
- `viewer/src/components/Lineage/` (new): the map. Nodes are grid children; lines are an SVG drawn from measured node positions.
- `viewer/src/App.jsx`: a URL with no `run` or `issue` (or an unknown one) shows the map instead of the latest run.
- `viewer/src/components/Sidebar/`: "계보" row at the top; opened issue lists runs by variation; the group opens when its issue page is entered from the map or a URL.
- `viewer/src/data/experiment.js`: `variationsOf` items carry `parts` (`[{ label, value }]`).
- `viewer/src/data/useIssueData.js` (new): `useConfigs`, `useIssueInfo` moved out of `IssuePage.jsx` so the sidebar can use them.
- `tests/test_viewer_lineage.py` (new), `README.md` viewer section, `ui-text.glossary.md`.

## Out Of Scope
- Open issues (#13, #59) as "in progress" nodes: what they build on is not recorded, so placing them would be a guess.
- The issue page, the run panel and the replay screen.
- Lineage fields in `published/issues/<n>.json`. Proposed to the user first, then dropped: issues with no published runs (#1, #4, #7, #9, #34, #44, #64) have no such file and the file requires `purpose`.

## Done Criteria
- [x] `/` shows the map with every issue that has published runs; a node with runs opens its issue page, a node without opens GitHub in a new window.
- [x] Lines only go downward and no two nodes share a cell (test).
- [x] An opened issue in the sidebar lists runs under variation headings with label/value lines.
- [x] No horizontal overflow of the map at 1600, 1000 and 390 px.
- [x] `pytest` and `npm run build` pass.
- [x] User approved the map and the sidebar.

## Current State
Implemented, reviewed by the user on the preview and approved for merge ("머지해 이제", 2026-11-20). Nothing is left open on this branch.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### feat: viewer 첫 화면에 issue 계보 넣고 사이드바 실행을 조건으로 묶기 (#77)
> why: the only level above an issue page was a flat list of issue titles; the order of development and what each issue changed could not be read from it
#### Scope
Everything in this issue, in one commit: the seed (this document, the registry row, the AGENTS.md pointer), the lineage map, the sidebar, issue names, the arrowheads and the AGENTS.md domain rule. The seed was never committed on its own: the session that registered the issue was isolated in the #62 worktree, and it ended (laptop shut down) before the first commit. A new session picked the uncommitted tree up on 2026-11-20.
#### Changes
- `viewer/src/data/lineage.js` (new): `NODES` table, `lineageOf()` (rows from merge dates and `parents`, so lines only go down), `issueName()`.
- `viewer/src/components/Lineage/` (new): nodes as grid children, lines as SVG paths drawn from measured node boxes, an arrowhead (`marker-end`, 7 px) on the child's end of every line. Hovering a node highlights its lines and dims unrelated nodes.
- `viewer/src/App.jsx`: a URL with no known `run` or `issue` shows the map; the toolbar title is the issue name.
- `viewer/src/components/Sidebar/`: "계보" row above the search; an opened issue lists runs under variation headings (label/value lines), runs inside a variation are called "학습 seed N"; the group opens when its issue page is entered from the map or a URL; group names use `issueName()`, the GitHub title is the tooltip.
- `viewer/src/data/experiment.js`: `variationsOf` items carry `parts`. `viewer/src/data/useIssueData.js` (new): `useConfigs`, `useIssueInfo` moved out of `IssuePage.jsx`. `viewer/src/data/history.js`: #22, #61, #64 and `issueOf()`. `viewer/src/data/runs.js`: search also matches the issue name.
- `viewer/src/components/IssuePage/IssuePage.jsx`: provenance popover and compare link use `issueName()`.
- Issue names (user review, 2026-11-20: "이슈명을 그대로 쓰고 있잖아 ... 어떻게 바뀌었는지 한번에 알아볼 수 있는 간결하고 명료한 걸로"): all 17 names rewritten to say what changed in 15 characters or fewer. `name` no longer has to equal the info file's `phase`; `phase` was left untouched so the issue page does not repeat its own title.
- Arrowheads (user: "선에다가 화살표 추가해서 선후관계좀 나타내봐").
- `AGENTS.md` Domain Rules: an issue that changes the environment, the fly or the aimer adds its row to `history.js` and `lineage.js` in the same PR (the user asked whether the map updates on merge; it does not, and tests only catch issues with published runs).
- `tests/test_viewer_lineage.py` (new, 5 tests), `README.md` viewer section, `ui-text.glossary.md` (계보, 조준기도 바꿈).
#### Verification
- `.venv/Scripts/python -m pytest -q` → 216 passed (run after the name change; the later arrowhead change touched only `Lineage.jsx` and its CSS).
- `npm run build --prefix viewer` → built, after the last change.
- ui-evidence on the built site (`vite preview`, port 4977), commit: uncommitted tree on 2b841e9, serve check: a "계보" button exists in the sidebar, ready when more than 5 sidebar groups exist:

| page | viewport | overflow | probes | console |
| --- | --- | --- | --- | --- |
| / | 1600x900 | none | 19 lines with an arrowhead; first sidebar group #72 | favicon 404 only (present on main) |
| / | 1000x900 | none | 19 | clean |
| / | 390x844 (mobile, dpr 2) | none | 19 | clean |
| /?issue=72 | 1600x900 | none | 6 variation headings in the sidebar | clean |
| /?issue=72 | 1000x900 | none | 6 | clean |
| /?issue=72 | 390x844 (mobile, dpr 2) | one variation-switch button ends at 408 px | 6 | clean |
| /?issue=51 | 1600x900 | none | 4 | clean |
| /?issue=51 | 1000x900 | none | 4 | clean |
| /?issue=51 | 390x844 (mobile, dpr 2) | none | 4 | clean |

  The 408 px button is inside `.variationSwitch`, which has `overflow-x: auto` (issue page, from #72, not changed here): it scrolls inside its own box and the document does not overflow. Captures are in `.ui-evidence/` (gitignored). Looked at: the map at 1600, 1000 and 390 px (arrowheads point at the child node; at 390 px the result text is hidden and three lanes stay side by side), #51 at 390 px (sidebar variation lines, new title).
- Not verified: real mouse hover (highlight colour of lines and arrowheads), the light colour scheme, `readme_check.py` (not found in this checkout), lint.
#### Notes
- The three `/?issue=` rows were written by the capture script with page `/` and overwrote each other's PNG; they are told apart by the sidebar probe (which group is open). The map was captured again on its own for the PNGs that were looked at.
- Open issues (#13, #59) are not on the map: what they build on is not recorded.

### chore: #77 마무리 (#77)
> why: last commit before the PR
#### Scope
Status done, AGENTS.md pointer removed, registry row set to done.
#### Changes
- This document: Status. `docs/issues/README.md`: #77 row → done. `AGENTS.md`: pointer line removed.
#### Verification
None needed.
#### Notes
The user said "머지해 이제" on 2026-11-20; taken as approval to commit, push, open the PR and squash-merge it, as for #57 and #62.

## Management Notes
### Follow-up Candidates
- Code-only issues are kept on the map by the AGENTS.md rule alone; a test over the Master Registry could enforce it, at the cost of an exclusion list for docs-only issues.
- The info files' `phase` still carries the old wording ("조준기 v1 학습"); the user was told and has not asked to change it.
- Real mouse hover on the map and the light colour scheme were not captured.
### References
