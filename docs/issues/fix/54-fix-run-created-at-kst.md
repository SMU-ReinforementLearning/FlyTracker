# 54 #51 실행의 만든 시각을 한국 시각으로 고치기

## Document Relations
- Issue: #54
- Branch: `54-fix-run-created-at-kst`
- Umbrella: (none)
- Status: in progress

## Summary
The 12 SAC runs published under #51 carry a UTC `createdAt` because they were created on a rented instance, so the viewer sidebar sorts issue #51 below #49, #45 and #42 although it is the newest work. Their `createdAt` is rewritten to Korean time, the convention of every run made on the team's machines.

## Goal
- Issue #51 appears at the top of the sidebar (groups are ordered by their most recent run's `createdAt`).

## Scope
- `createdAt` in `published/2026-11-15_151701_sac-*/run.json` (12 files): `2026-11-15T15:17:01` (UTC) → `2026-11-16T00:17:01` (KST, +9 h).

## Out Of Scope
- Run ids and folder names (they also contain the UTC time; renaming 12 folders is not needed for the order, and the user chose to fix `createdAt` only).
- Making `record.py` write a time zone; a guard for runs produced on other machines.

## Done Criteria
- [ ] The 12 `run.json` files hold `2026-11-16T00:17:01` and nothing else changed in them.
- [ ] The built `viewer/dist/runs/index.json` lists the #51 runs last (most recent); `uv run python -m pytest -q` passes.

## Current State
Seeded 2026-11-16. The fix is a 12-file text replacement; then build, test, PR, merge (the user asked to proceed).

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: #51 실행의 만든 시각을 한국 시각으로 고치기 (#54)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
This doc, `docs/issues/README.md`, `AGENTS.md`.
#### Changes
- Management doc filled; registry row and pointer added by `issue-start`.
#### Verification
- `issue-start` real run: issue #54, branch from `origin/main` @ d06bc53.
#### Notes
- None.

### fix: #51 실행의 만든 시각을 한국 시각으로 고치기 (#54)
> why: the UTC stamp from the instance sorted the newest issue below three older ones in the sidebar
#### Scope
`published/2026-11-15_151701_sac-*/run.json` (12 files).
#### Changes
- `createdAt` `2026-11-15T15:17:01` → `2026-11-16T00:17:01` (the same instant in KST).
#### Verification
- `git diff --stat`: 12 files, 12 insertions, 12 deletions; one line per file.
- `npm run build --prefix viewer`: `viewer/dist/runs/index.json` ends with the 12 #51 runs, after #49's `2026-11-15T22:30:16`.
- `uv run python -m pytest -q`: 139 passed, 45 skipped.
#### Notes
- The sidebar was not opened in a browser; the order follows from the index order (`groupByIssue` keeps the order of the most recent run).

## Management Notes
### Follow-up Candidates
- `record.py` writes `datetime.now()` without a zone, so a run made on a machine in another zone sorts wrongly again; write the zone or convert at publish time.
### References
- `viewer/src/data/runs.js` (`groupByIssue`), `viewer/vite.config.js` (`byCreatedAt`).
