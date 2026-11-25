# 80 계보에서 버전과 변경점이 한눈에 보이게 하기

## Document Relations
- Issue: #80
- Branch: `80-feature-lineage-version-change-visibility`
- Umbrella: (none)
- Status: in progress

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
- [ ] Environment lane reads 버전 1 → 6 top to bottom (nodes + marks); aimer lane shows v0 (#45) and v1 (#72).
- [ ] Nodes with a recorded change show `what from → to`; measured numbers show on their own line.
- [ ] No horizontal overflow at 1600, 1100 and 390 px; light and dark both checked.
- [ ] `tests/test_viewer_lineage.py` and `npm run build` pass.
- [ ] User approved the screen.

## Current State
Implemented and captured, not committed. Waiting at the pre-commit review gate for the seed commit and the feature commit. Dev server for review was started on `http://127.0.0.1:5187` from this worktree.

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

## Management Notes
### Follow-up Candidates
- The user asked (2026-11-25) for the lineage to be the landing screen of https://flytracker-ewk.pages.dev/. Captured the deployed site: `/` already opens the lineage at 1600 px and 390 px (`main h1` = 계보). At 390 px the run list takes the top 40vh and the map starts below it — ask whether that is what they meant before changing the phone layout.
- Full `pytest` in a fresh worktree venv fails 49 tests on missing optional extras (`pyarrow`, `train`); unrelated to this branch.
### References
