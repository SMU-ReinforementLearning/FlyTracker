# 47 viewer issue 페이지에 실험 정보 보여 주기

## Document Relations
- Issue: #47
- Branch: `47-feature-viewer-issue-info`
- Umbrella: (none)
- Status: in progress

## Summary
Clicking an issue name in the viewer sidebar shows what that batch of episodes is: which fly and which aimer (version and a readable description), the other conditions, why the episodes were made (which experiment step), and how each of those changed against a chosen comparison issue. The user asked for it on 2026-11-15: the issue page repeated the sidebar as a run table, which is not needed because the sidebar already lists the runs and a run opens the player; an issue, the unit that groups episodes, should explain itself instead. Later the same day the user added: sidebar groups start collapsed; explanation text in 한다체; show what changed against the comparison target, set by an explicit field, not "the previous issue"; and a selector for the variations inside one issue.

## Goal
- Issue page = experiment card (phase, purpose, comparison target), variation selector, fly card, aimer card, conditions, learning curve. The run table goes.
- Everything that `config.json` already records is derived, so it cannot drift from the runs: fly kind, aimer kind, algorithm, frame stack, training steps and seeds, environment version, capture range and hold time, episode length, room, turret position, field of view, pitch limit, start direction.
- What no run records (why the episodes exist, which step of the experiment, version numbers of learned models, which issue to compare with) is written by a person in one Korean file per issue.
- With a comparison target, each card and each condition row shows what changed: kind or version (`비교 대상: 기준선 v0`), `old → new`, and the numeric difference when the unit matches (`−0.05초`).
- Variation = runs whose configs are equal except the training seed. Two or more → buttons (전체 plus one per variation); the cards, conditions, comparison and curve follow the choice.
- Sidebar issue groups start collapsed.

## Scope
- `published/issues/<n>.json` (new, hand-written Korean, 한다체): `phase`, `purpose` (paragraph list), optional `fly` / `aimer` version labels (default `v0` for the rule fly and the baseline, README `### 대전표` numbering), optional `compare` (issue number), optional `notes` (label/value rows not in `config.json`). Drafts for #22, #35, #42 written from their management docs; #35 and #42 compare with #22 (baseline only, so #42 isolates the environment change). The user reviews wording, version labels and comparison targets.
- `viewer/vite.config.js`: no change needed; verified that build emits `published/issues/*.json` to `dist/runs/issues/`, dev serves it, and `publishedRuns()` skips the folder (no `run.json`).
- `viewer/src/data/api.js`: `fetchIssueInfo(n)`; any failure → null (Cloudflare Pages answers a missing file with `index.html`).
- `viewer/src/data/experiment.js` (new): cards and condition rows from configs, `variationsOf`, `compareExperiments`.
- `viewer/src/data/runs.js`: `compareGroup`, `byCreatedAt` (name tie-break so colours are stable); drop the table-only helpers.
- `viewer/src/components/IssuePage/`: new page; legend under the curve replaces the table's colour swatches.
- `viewer/src/components/Sidebar/Sidebar.jsx`: groups collapsed at start; clicking an issue name also opens its group; search still opens matching groups.
- `flytracker/record.py` `issue_info_path`, `scripts/publish_run.py` warning, `tests/test_published_issue_info.py` (every issue with published runs has a well-formed file; `compare` points at an issue with runs).
- `README.md` (publish flow, run list, issue page), `ui-text.glossary.md` (11 terms), `ui-text.config.md` (explanation text is 한다체).

## Out Of Scope
- Changing the run or episode format, `train.py`, `record.py`'s recording.
- Pulling text from GitHub issue bodies (English, agent-facing; would call the GitHub API on every view).
- Comparing results (capture rate, time) between issues; comparing reward weights or turning speed (equal in every published run so far).
- Keeping the chosen variation in the URL.
- The run panel and the episode player.
- `44.json` for the open #44: that branch publishes its runs and writes its own file (pytest now requires it).
- Neural-fly demo runs (#31): not published; the page must not break on their configs, nothing more.

## Done Criteria
- [ ] Issue pages #22, #35, #42 show phase, purpose, fly card, aimer card, conditions; no run table; #35 keeps its learning curve with a legend.
- [ ] Every derived value on those pages matches the runs' `config.json` (checked field by field against the 9 published configs).
- [ ] #35 and #42 show the changes against #22; #22 (no `compare`) shows none.
- [ ] #35 shows variation buttons 전체 / 1개 / 4개; choosing 4개 narrows cards, record count and curve to the three frame-stack-4 runs.
- [ ] An issue without a file shows the derived sections and a one-line empty state; checked on the build where the missing file comes back as HTML.
- [ ] Sidebar groups start collapsed; the disclosure toggles; an issue name opens the page and its group; the player still works.
- [ ] `npm run build` emits `runs/issues/*.json`.
- [ ] ui-evidence screenshots at 1600px and 390px, no overflow, console clean apart from the existing favicon 404.
- [ ] Explanation text is 한다체; README prose passes ko-writing `check.py` and `readme_check.py`.
- [ ] `uv run pytest` passes.

## Current State
2026-11-15: implementation done and verified in the worktree, not committed. Waiting for the user's approval of the two commits (seed, then feature). Dev server for review: `npx vite --port 5187` in `viewer/` (port 5180 is taken by another checkout's server).

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: viewer issue 페이지에 실험 정보 보여 주기 (#47)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Tracking only; no code.
#### Changes
- This document: Summary, Goal, Scope, Out Of Scope, Done Criteria from the 2026-11-15 chat.
- `docs/issues/README.md`: registry row. `AGENTS.md`: pointer line.
#### Verification
- Branch cut from `origin/main` @ 7a81d0a by `issue-start`.
#### Notes
- The issue body was rewritten in English (Goal, Done criteria) after creation; the script seeds it with the Korean title.

## Management Notes
### Follow-up Candidates
### References
