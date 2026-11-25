# 80 계보에서 버전과 변경점이 한눈에 보이게 하기

## Document Relations
- Issue: #80
- Branch: `80-feature-lineage-version-change-visibility`
- Umbrella: (none)
- Status: done

## Summary
Make the lineage map show, per lane, which version each issue raised and what value changed. The #77 map drew every node the same size, showed the environment version as a small grey badge next to the issue number, had no aimer version at all, and buried the change inside the result sentence. The user asked (2026-11-25) for versions and changes to stand out, and approved the recommended plan.

## Goal
- A reader scanning one lane top to bottom sees its versions in order without reading sentences.
- Each node states the changed value as before → after and the measured number, separately from prose.

## Scope
- `viewer/src/data/lineage.js`: new optional fields `aimerVersion`, `fly`, `change`, `metric`; `lineageOf()` also returns `badges`/`major` per node, `marks`, `current`.
- `viewer/src/components/Lineage/`: version badges with a per-lane colour dot, large nodes for version-raising issues and small ones for the rest, change line, metric line, result sentence moved to a hover/focus popover, version marks in the owning lane (environment version 4 and 5 were raised by aimer-lane issues #45 and #49), current state next to each lane name.
- `tests/test_viewer_lineage.py`: environment versions run without a gap, marks sit in empty cells, change/metric shape.
- `README.md` (계보 section), `ui-text.glossary.md`.

## Out Of Scope
- Numbering fly versions. The fly lane shows kinds (규칙 초파리, 신경 초파리) as agreed with the user.
- The phone layout where the run list sits above the map (see Follow-up Candidates).
- Changing `result` texts or node names.

## Done Criteria
- [x] Environment lane reads 버전 1 → 6 top to bottom (nodes + marks); aimer lane shows v0 (#45) and v1 (#72). (2026-11-25 20:21)
- [x] Nodes with a recorded change show `what from → to`; measured numbers show on their own line. (2026-11-25 20:21)
- [x] No horizontal overflow at 1600, 1100 and 390 px; light and dark both checked. (2026-11-25 20:21)
- [x] `tests/test_viewer_lineage.py` and `npm run build` pass. (2026-11-25 20:21)
- [x] User approved the screen. (2026-11-25 20:21) ("머지해")

## Current State
Implemented; the user reviewed the summary and said "머지해" (2026-11-25). The open question is in Follow-up Candidates: whether the phone layout (run list above the map) is what the user meant by "landing".

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 계보에서 버전과 변경점이 한눈에 보이게 하기 (#80)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
The seed only: this document, the registry row, the AGENTS.md pointer.
#### Changes
- `docs/issues/feature/80-feature-lineage-version-change-visibility.md` (new), `docs/issues/README.md` (+1 row), `AGENTS.md` (pointer line).
#### Verification
None needed.
#### Notes
- The session was isolated in the #79 worktree and could not `EnterWorktree` into this one; files were edited by absolute path and git was run with `git -C`.
- Sidebar: Type Feature, label enhancement, Priority Medium (planned readability work, blocks nothing).

### feat: 계보에 버전 표시와 바뀐 값을 드러내기 (#80)
> why: the user could not see, per lane, which version each issue raised or what changed ("핵심 버젼이나 변경점 이런게 눈에 잘 안들어오는데", 2026-11-25)
#### Scope
The whole change in one commit: lineage data fields, the Lineage component and its CSS, tests, README, glossary.
#### Changes
- `viewer/src/data/lineage.js`: optional `aimerVersion` (#45 v0, #72 v1), `fly` (#4 규칙 초파리, #31 신경 초파리), `change` on 8 nodes, `metric` on 8 nodes. Change values were copied from `history.js` (`env.capture_radius`, `env.aimer.max_pitch_deg`, `baseline.tracking`, `env.reward.beam`, …), metrics from the existing `result` sentences; nothing new was measured. `lineageOf()` returns `badges`/`major`/`change`/`metric` per node, `marks` (a version raised by a node of another lane, placed in the owning lane's cell on the same row: environment version 4 ← #45, 5 ← #49) and `current` (fly "규칙, 신경", aimer "v1", environment "버전 6").
- `viewer/src/components/Lineage/Lineage.jsx`, `Lineage.module.css`: badges at the top of a node (13 px semibold, tinted pill, a dot in the lane colour: fly `--color-series-3`, aimer `-2`, environment `-7`); nodes with a badge keep the card size and a 15 px name, the rest are narrower with a 13 px name and no shadow; change line `what from → to` with `to` in semibold; metric line; the result sentence is an absolutely positioned box shown on `:hover`/`:focus-visible` (above the node in the last two rows); marks as pills on the lane's line, hovering one highlights the issue that raised it; lane name carries the dot and the current state. A dashed (no published runs) node that raised a version is no longer faded. Under 620 px of map width the change, metric and result are hidden; badges and names stay.
- Badge wording follows the glossary ("환경 버전 3", not "환경 v3"). Fly versions are not numbered: kinds only, as proposed to and accepted by the user.
- `tests/test_viewer_lineage.py`: +3 tests (environment versions 1..n without a gap and equal to `current`; marks in empty cells of another lane; change/metric shape and `major == bool(badges)`).
- `README.md` 계보 section: what a node shows now and a table of the new fields. `ui-text.glossary.md`: badge wording, "포획 5/200".
#### Verification
- `uv run pytest tests/test_viewer_lineage.py tests/test_viewer_experiment.py tests/test_viewer_attitude.py -q` → 16 passed. `npm run build --prefix viewer` → exit 0 (after the last CSS change).
- Full `uv run pytest -q` in this worktree's fresh venv → 170 passed, 49 failed: 46 `ModuleNotFoundError: pyarrow`, 3 in `tests/test_players.py`/`test_neuromechanics.py`; no Python source was changed on this branch and the optional extras were not installed.
- ui-evidence, dev server of this worktree (`vite --port 5187`), uncommitted tree on ee4c5a1, Chrome 157.0.8103.80, ready when lane elements and an arrowed line exist:

| page | viewport | overflow | probes | console |
| --- | --- | --- | --- | --- |
| / | 1600x1900 | none | `main h1` = 계보; lane headings 초파리 규칙, 신경 / 조준기 v1 / 환경 버전 6 | favicon 404 only (present on main) |
| / | 1100x1900 | none | same | clean |
| / | 390x2600 (mobile, dpr 2) | none | same | clean |
| / | 1600x1650, `prefers-color-scheme: light` | none | light scheme matched | favicon 404 only |

  Looked at: dark at 1600, 1100, 390 px and light at 1600 px (badges, marks on the environment line between #42 and #69, small and large nodes); the result box forced open by script on #42 (below the node) and #72 (above it). Captures are in the session scratchpad, not committed.
- Not verified: the result box appearing on a real mouse hover or keyboard focus (a scripted `focus()` in headless Chrome did not match `:focus-visible`; the box was opened by setting `display` instead), lint.
- The deployed site was captured too (see Follow-up Candidates): `/` opens the lineage at 1600x900 and 390x844.
#### Notes
- The first capture run passed `--path /` through Git Bash, which rewrote it to `/C:/Program Files/Git/`; the app showed the lineage for the unknown path, so the pictures are of the right screen. Later runs used `--url`.

### chore: #80 마무리 (#80)
> why: last commit before the PR
#### Scope
Status done, AGENTS.md pointer removed, registry row set to done.
#### Changes
- This document: Status. `docs/issues/README.md`: #80 row → done. `AGENTS.md`: pointer line removed.
#### Verification
None needed.
#### Notes
The user said "머지해" on 2026-11-25; taken as approval to commit, push, open the PR and squash-merge this branch.

## Management Notes
### Follow-up Candidates
- The user asked (2026-11-25) for the lineage to be the landing screen of https://flytracker-ewk.pages.dev/. Captured the deployed site: `/` already opens the lineage at 1600 px and 390 px (`main h1` = 계보). At 390 px the run list takes the top 40vh and the map starts below it — ask whether that is what they meant before changing the phone layout.
- Full `pytest` in a fresh worktree venv fails 49 tests on missing optional extras (`pyarrow`, `train`); unrelated to this branch.
### References
