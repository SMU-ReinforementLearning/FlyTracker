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
- [x] Issue pages #22, #35, #42 show phase, purpose, fly card, aimer card, conditions; no run table; #35 keeps its learning curve with a legend. (2026-11-15)
- [x] Every derived value on those pages matches the runs' `config.json` (checked field by field against the 9 published configs). (2026-11-15)
- [x] #35 and #42 show the changes against #22; #22 (no `compare`) shows none. (2026-11-15)
- [x] #35 shows variation buttons 전체 / 1개 / 4개; choosing 4개 narrows cards, record count and curve to the three frame-stack-4 runs. (2026-11-15)
- [x] An issue without a file shows the derived sections and a one-line empty state; checked on the build where the missing file comes back as HTML. (2026-11-15)
- [x] Sidebar groups start collapsed; the disclosure toggles; an issue name opens the page and its group; the player still works. (2026-11-15)
- [x] `npm run build` emits `runs/issues/*.json`. (2026-11-15)
- [x] ui-evidence screenshots at 1600px and 390px, no overflow, console clean apart from the existing favicon 404. (2026-11-15)
- [x] Explanation text is 한다체; README prose passes ko-writing `check.py` and `readme_check.py`. (2026-11-15)
- [x] `uv run pytest` passes. (2026-11-15)
- [x] After merging main (#44, #45, #49): every issue with published runs has a file; #42 shows the #44 SAC runs as a variation; #45 shows the new baseline's tracking; #49 shows the reward change. (2026-11-16)

## Current State
2026-11-16: all done criteria met; main (#44, #45, #49) merged into the branch and the page extended for their runs. Next: the closing commit (pointer removed, Status done), then push, PR and squash merge at the user's request ("머지해"), then the post-PR cleanup gate.

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

### feat: viewer issue 화면에 실험 정보와 비교 보여 주기 (#47)
> why: the issue page repeated the sidebar as a run table; the user wants it to say what the experiment is, how it differs from a chosen comparison issue, and to pick a variation inside one issue
#### Scope
viewer issue page, sidebar default, per-issue description files, publish warning and test, README, UI glossary and tone.
#### Changes
- `viewer/src/data/experiment.js` (new): fly and aimer cards (kind, version, 한다체 description, training rows), condition rows (environment version, capture range, capture hold, capture distance, episode length, room, turret position, field of view, pitch limit, start direction), facts (record count, file `notes`); `variationsOf` groups runs whose configs are equal except `algo.seed` and labels each by the shown values that differ; `compareExperiments` adds `prev` / `delta` per row and `was` per card.
- `viewer/src/components/IssuePage/`: rewritten. Sections 실험 (phase, purpose, 비교 대상 link), variation buttons, 초파리, 조준기, 조건, 학습 곡선 with a legend. Changed rows get a blue dot and `old → new` plus a delta pill. Rows: label at the left edge, value from the centre line (user: names and values were too far apart; keep labels left). `word-break: keep-all`.
- `viewer/src/data/api.js`: `fetchIssueInfo`; any failure → null, because Cloudflare Pages answers a missing file with `index.html` (reproduced with `vite preview`: 200 text/html).
- `viewer/src/data/runs.js`: `compareGroup` (explicit `compare` only, no "previous issue" default, per the user), `byCreatedAt` with a name tie-break; table-only helpers removed.
- `viewer/src/components/Sidebar/Sidebar.jsx`: groups start collapsed; clicking an issue name also opens its group.
- `viewer/src/App.jsx`: passes `groups` and `openIssue` to the issue page. `CurveChart.jsx`: comment now points at the legend.
- `published/issues/22.json`, `35.json`, `42.json` (new): drafts from the #22, #35, #42 management docs and #35 `gate.md`; #35 `aimer: v1`; #35 and #42 `compare: 22`.
- `flytracker/record.py` `issue_info_path`; `scripts/publish_run.py` warns when the file is missing; `tests/test_published_issue_info.py` requires a well-formed file for every issue with published runs and a `compare` that points at an issue with runs.
- `README.md` (실행 올리기 file format, 실행 목록 collapsed groups, issue 화면), `ui-text.glossary.md` (11 terms), `ui-text.config.md` (explanation text is 한다체).
#### Verification
- `uv run pytest`: 116 passed, 45 skipped (all skips need a local neural source; `FLYTRACKER_NEURAL_SOURCE`).
- `npm run build`: `dist/runs/issues/{22,35,42}.json` emitted; `publishedRuns()` ignores the folder (9 runs in `index.json`).
- Derived values checked against the 9 published `config.json`: #22 version 1, 3°/0.2 s, pitch ±80°, 1 run 5 episodes; #35 version 2, SAC 1,000,000 step, seeds 0, 1, 2, frame stack 1 and 4, 6 runs 378 episodes; #42 version 3, 1.25 mm/0.15 s, 2 runs 8 episodes.
- Comparison (probe of changed rows): #35 vs #22 → aimer 기준선 v0, environment 1 → 2, pitch ±80° → ±89° (+9°); #42 vs #22 → environment 1 → 3, capture range 3° → 1.25 mm, hold 0.2 s → 0.15 s (−0.05초), pitch +9°; #22 → none.
- Variation: #35 buttons 전체 / 1개 / 4개; 4개 → frame stack 4개, 실행 3개, 에피소드 189개, legend sac-fs4-s0..s2.
- Sidebar (probes on `/`): 0 groups open at start; disclosure → 1 open; clicking #35's name → `?issue=35`, 2 open; player renders (2 canvases).
- Missing file on the build (`dist/runs/issues/42.json` deleted, `vite preview`): empty state shown, no comparison, no errors.
- ko-writing `check.py` on the new README prose and the 한다체 texts: no forbidden patterns, endings unified; `readme_check.py`: 0 fail.

ui-evidence (Chrome 157.0.8103.52; working tree on base 7a81d0a before this commit; dev server on 127.0.0.1:5187, `vite preview` on 5189 for the missing-file case):

| page | viewport | file | overflow | console |
| --- | --- | --- | --- | --- |
| `/?issue=35` (before, main) | 1600x900 | `47-feature-viewer-issue-info/captures/before-35-1600x900.png` | none (390px: 54 elements past the right edge, the run table) | favicon 404 |
| `/?issue=35` | 1600x2100 | `47-feature-viewer-issue-info/captures/rows-35-1600x2100.png` | none | favicon 404 |
| `/?issue=35`, 4개 chosen | 390x3000 | `47-feature-viewer-issue-info/captures/var4-390x3000.png` | none | favicon 404 |
| `/?issue=42` | 1600x2100 | `47-feature-viewer-issue-info/captures/rows-42-1600x2100.png` | none | favicon 404 |
| `/?issue=42` | 390x3000 | `47-feature-viewer-issue-info/captures/rows-42-390x3000.png` | none | clean |
| `/?issue=22` | 1600x2100 | `47-feature-viewer-issue-info/captures/cmp-22-1600x2100.png` | none | favicon 404 |
| `/?issue=42`, file missing (build) | 1600x1400, 390x1600 | `47-feature-viewer-issue-info/captures/no-info-*.png` | none | favicon 404 |
| `/` (player, sidebar collapsed) | 1600x900 | `47-feature-viewer-issue-info/captures/root-1600x900.png` | none | favicon 404, three.js warnings |

The favicon 404 is on main too (before capture). The two `rows-42-*` captures were removed in the next commit: after merging main, #42 also holds the #44 SAC runs, and `m-42-1600x2600.png` replaces them.
#### Notes
- User decisions on 2026-11-15: issue name → experiment page, no run table; sidebar collapsed; 한다체 for explanation text; Apple style, no subtitles; comparison per section against an explicit `compare` flag; variation buttons; row labels left, values from the centre.
- Not compared: results (capture rate, time), reward weights and turning speed (equal in every published run). The chosen variation is not kept in the URL.
- Leftover dev servers: `TaskStop` ended the shell but left `vite` running on 5188 and 5189 (Windows); stopped by PID after checking the command line.

### feat: main에 들어온 실행에 맞춰 issue 화면 넓히기 (#47)
> why: merging main brought five published runs (#44 under #42, #45, #49) that the page did not describe: the #45 baseline tracks the fly's angular velocity, #49 changes the reward, and #44 plays a version-2 model under version 3; the description-file test failed for #45 and #49
#### Scope
viewer experiment model and issue page, description files, README.
#### Changes
- Merge commit 83b7eaa: `origin/main` @ c4dd7e1 into the branch; conflicts only in the registry rows and the glossary history (both sides kept).
- `experiment.js`: baseline card gets a 따라가는 방식 row (environment version 4 and later: tracks the fly's angular velocity, #45; earlier: aim error only) and a description that fits both; learned-aimer rows 학습한 환경 버전 and 모델 from `algo.trainedEnvVersion` / `algo.model`; condition row 확대 화면 (`fov_v_deg / fine_error_deg`, 80배); reward rows from `env.reward` (시간 벌점, 빔까지 거리 벌점, 빔 벌점이 가장 큰 거리, 조준 오차 벌점, 놓쳤을 때 벌점, 행동 변화 벌점, 포획 보상) compared like conditions; variation labels use only the fly/aimer kinds when those differ (#42: 기준선 v0 / 학습한 조준기 v1) and the description file's version labels.
- `IssuePage.jsx`: 보상 section after 조건.
- `published/issues/42.json`: the #44 SAC runs, `aimer: v1`, phase 레이저 포획에서 다시 재기. New `45.json` (compare 42) and `49.json` (compare 45), drafted from their management docs.
- `README.md` issue page section: 보상, 따라가는 방식, model rows, 확대 화면, variation naming.
#### Verification
- `uv run pytest`: 133 passed, 45 skipped (local neural source).
- `npm run build`: `runs/issues/{22,35,42,45,49}.json`.
- Changed rows (probe): #42 vs #22 → environment 1 → 3, capture range and hold (−0.05초), pitch +9°; 학습한 조준기 v1 variation adds 학습한 환경 버전 2 and 모델 2026-11-12_131635_sac-fs1-s0. #45 vs #42 → 따라가는 방식 조준 오차만 보고 돌림 → 초파리 각속도에 맞춰 돌림, environment 3 → 4, pitch ±89° → ±90° (+1°), 확대 화면 없음 → 80배. #49 vs #45 → environment 4 → 5, 빔까지 거리 벌점 없음 → 0.1, 빔 벌점이 가장 큰 거리 없음 → 1m, 조준 오차 벌점 0.05 → 0 (−0.05). Matches the env.py version notes and the #45/#49 docs.
- ko-writing `check.py` on the new texts and README section: no forbidden patterns, endings unified (one heading warning is an extraction artefact: a paragraph that starts with `#44`). `readme_check.py`: 0 fail.

| page | viewport | file | overflow | console |
| --- | --- | --- | --- | --- |
| `/?issue=42`, 학습한 조준기 v1 chosen | 1600x2600 | `47-feature-viewer-issue-info/captures/m-42-1600x2600.png` | none | favicon 404 |
| `/?issue=45` | 1600x2600 | `47-feature-viewer-issue-info/captures/m-45-1600x2600.png` | none | favicon 404 |
| `/?issue=49` | 390x3600 | `47-feature-viewer-issue-info/captures/m-49-390x3600.png` | none | clean |
#### Notes
- Behaviour that lives only in code (not in `config.json`) is visible only where it can be tied to the environment version, as for the baseline. Anything else needs the description file's `purpose`.

## Management Notes
### Follow-up Candidates
- #44 publishes version-3 SAC runs: it must add `published/issues/44.json` (pytest requires it); a natural `compare` is 42 (same environment, baseline).
- Keep the chosen variation in the URL (`route.js`), so a link opens the same variation.
- Compare results (capture rate, time to capture) between an issue and its comparison target, not only settings.
### References
- README `### 대전표` (version numbering v0, v1), `### 실행 올리기` (description file format), `### issue 화면`.
- `docs/issues/feature/35-feature-sac-aimer-training/gate.md` (numbers quoted in `35.json`), `docs/issues/feature/42-feature-laser-hit-capture.md` (numbers quoted in `42.json`).
