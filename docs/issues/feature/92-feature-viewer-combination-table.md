# 92 viewer에서 실행의 초파리, 조준기, 환경 조합을 표로 보여 주기

## Document Relations
- Issue: #92
- Branch: `92-feature-viewer-combination-table`
- Umbrella: (none)
- Status: in progress

## Summary
The viewer now states each run's fly, aimer and environment in fixed places: a combination table on the issue page, a three-row block on the run panel, and fixed lines in the sidebar's run rows. Before this, the sidebar and the issue page's variation buttons listed only "what differs", so the same slot held a fly kind in one issue and a reward weight in another, and the run page showed nothing but the run name.

## Goal
A reader can tell, for any run, which fly met which aimer under which environment version — on the issue page, on the run page and in the sidebar — without decoding the run name.

## Scope
- `viewer/src/data/experiment.js`: `combinationsOf` replaces `variationsOf`. One row per combination (runs that differ only in training seed), each with a `fly`, `aimer`, `environment` cell (`title` + the rows that differ among combinations of the same kind).
- Issue page: a "조합" table (초파리, 조준기, 환경, 실행). Clicking a row selects that combination and filters the cards and the learning curve; clicking it again returns to all runs. This replaces the variation segmented control (user request, 2026-11-26). Run buttons in the last column open the run.
- Run panel: the run's combination at the top, in the order 초파리, 조준기, 환경.
- Sidebar: each run row reads aimer (first line), the aimer's differing settings (when any), then fly. Environment is written once above the rows when all combinations share it, else per row.
- README viewer section, `ui-text.glossary.md` (조합), a test over the published runs.

## Out Of Scope
- Showing 200-seed measurement results in the table (#79).
- The toolbar title of the run page (still the run name).
- Config gaps that make two combinations read the same: #88's fire-only runs do not record the misfire penalty they were trained with, and #59 has two runs whose configs differ only in `evaluation.flyWeights` `original` vs `baseline` (the same weights).

## Done Criteria
- [x] Issue page shows one table row per combination with fly, aimer, environment in fixed columns, for every published issue (2026-11-26 19:55)
- [x] Selecting a table row filters the cards and the learning curve; the variation buttons are gone (2026-11-26 19:55)
- [x] Run panel shows the run's fly, aimer, environment (2026-11-26 19:55)
- [x] Sidebar run rows put aimer and fly on fixed lines (2026-11-26 19:55)
- [x] Tests pass, `npm run build` passes, captures at 1600 and 390 width looked at (2026-11-26 19:55)
- [ ] Captures retaken with the row letters and the "실험 목록" title, and looked at
- [ ] User approves the sidebar layout — it was proposed as option 1 and built without an explicit answer

## Current State
Code, README, glossary, test and captures are committed. The user approved the merge on 2026-11-26 without a new capture run ("이렇게 머지해볼래?"), so the row letters, the "실험 목록" title and the lettered sidebar rows went in without being looked at in a browser; the PNGs in `captures/` show the state before them. Nothing was added to `history.js`/`lineage.js` (viewer-only change, no env/fly/aimer change).

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: viewer에서 실행의 초파리, 조준기, 환경 조합을 표로 보여 주기 (#92)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, AGENTS.md pointer.
#### Changes
- `docs/issues/feature/92-feature-viewer-combination-table.md` created
- `docs/issues/README.md` +1 row
- `AGENTS.md` pointer line
#### Verification
None needed; no code.
#### Notes
Branch cut from `origin/main` @ ca60b27. Priority Medium.

### feat: issue 화면에 조합 표를 두고 실행 화면과 사이드바에 조합 적기 (#92)
> why: the user could not tell which fly, aimer and environment a run used, in the sidebar, on the run page or from the variation buttons
#### Scope
`viewer/src/data/experiment.js`, `useIssueData.js`, new `components/Combinations/`, `IssuePage`, `RunPanel`, `Sidebar`, `App.jsx`, README, glossary, `tests/test_viewer_combinations.py`.
#### Changes
- `combinationsOf(runs, configs, info)` returns `[{ key, fly, aimer, environment, runs: [{ id, seed }] }]`. A cell's `details` are the rows that differ among combinations with the same cell title. A row missing on one side (undefined) is kept apart from the value "없음" (추적 보조 없음); presence-only rows are dropped when a row with two real values already separates the combinations (자극 켬/끔 hides 자극 길이). `모델` is excluded like the training seed.
- `variationsOf` removed; both callers moved to `combinationsOf`. `useCombinations(runs, key)` hook shared by the sidebar and the run panel.
- `Combinations` table: rows are selectable (click, Enter, Space; `aria-selected`) only when there are two or more; run buttons stop propagation.
- Issue page: the variation bar and its CSS removed; `onSelectRun` passed from `App`.
- Sidebar: variation headers removed; the old "algo · author / date" line moved into the row tooltip (run name · author · date).
#### Verification
- `python -m pytest tests/test_viewer_combinations.py tests/test_viewer_experiment.py tests/test_viewer_lineage.py tests/test_published_issue_info.py` → 44 passed
- `npm run build` in `viewer/` → built
- Row selection: on `/?issue=72`, clicking row 5 gave 1 selected row and the cards went from `규칙 초파리|신경 초파리|설정|기준선|학습한 조준기|설정|보상` to `신경 초파리|설정|학습한 조준기|설정|보상`
- Captures (dev server of this worktree on 127.0.0.1:5192, working tree on top of ca60b27, Chrome 158.0.8127.38, reduced motion on):

| page | viewport | file | overflow | probe |
| --- | --- | --- | --- | --- |
| `/?issue=72` | 1600x1500 | `92-feature-viewer-combination-table/captures/issue72-1600x1500.png` | none | table rows = 6 |
| `/?issue=72` | 390x2600 (mobile, dpr 2) | `92-feature-viewer-combination-table/captures/issue72-390x2600.png` | table is 588 wide inside its own scroll box (intended) | table rows = 6 |
| `/?issue=88` | 1600x2000 | `92-feature-viewer-combination-table/captures/issue88-1600x2000.png` | none | table rows = 7 |
| `/?run=2026-11-18_000726_neural-stim-sac-beam-assist-s1` | 1600x900 | `92-feature-viewer-combination-table/captures/run72-1600x900.png` | none | panel = 초파리 신경 초파리 자극 켬 / 조준기 학습한 조준기 v1 학습 seed 1 / 환경 버전 6 |
| same | 390x844 (mobile, dpr 2) | `92-feature-viewer-combination-table/captures/run72-390x844.png` | none | same |

Console: only the favicon 404 and THREE.Clock deprecation warnings, both present before this change.
- After the first review (user requests, 2026-11-26): the table section is titled "실험 목록" instead of "조합"; every row gets a letter (A, B, C — `letter` from `combinationsOf`) in a leading "실험" column; the run panel shows it as a "실험" row; sidebar run rows start with the same letter and no longer print the aimer's differing settings. The sidebar computes combinations from the unfiltered runs (`group.all`) so a search does not shift the letters.
- Re-run after those changes: the four test files → 44 passed; `npm run build` → built. NOT re-captured: the dev server was stopped by the harness for low memory, so the PNGs in `captures/` predate the letters and the new title.
#### Notes
- Not checked: the letter column, the new title and the lettered sidebar rows in a browser; keyboard selection; light colour scheme.
- The captures must be retaken before the commit.

## Management Notes
### Follow-up Candidates
- Record the training-time misfire penalty in replayed runs' config so #88's fire-only combinations can be told apart.
- Run page toolbar title could name the combination instead of the run name.
### References
- Proposal and decisions: conversation of 2026-11-26 (table rows instead of variation buttons — user request)
