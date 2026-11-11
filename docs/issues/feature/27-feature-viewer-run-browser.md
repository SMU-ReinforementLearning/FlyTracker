# 27 viewer 실행 목록을 issue별로 묶고 학습 곡선과 에피소드 격자 넣기

## Document Relations
- Issue: #27
- Branch: `27-feature-viewer-run-browser`
- Umbrella: (none)
- Status: in progress

## Summary
Reshapes the viewer for many runs from many issues: runs grouped by the issue they belong to, a run panel with the learning curve and a checkpoint × start-condition episode grid, an issue page that compares its runs, and the selection kept in the URL so a link opens the same episode. The user asked for the four steps proposed in a Q&A on 2026-11-11 ("4번까지 진행해"), Apple-style minimal, with no captions or subtitles.

## Goal
- A teammate finds a run by its issue, sees whether it learned, and picks an episode from a grid instead of scrolling a list of 30+ rows per run.
- A link such as `/?run=<id>&tag=<tag>&ep=<n>` opens that episode, so it can go into a PR or issue comment.
- An issue page overlays the learning curves of the issue's runs and lists the config values that differ.

## Scope
- GitHub label `training` (created 2026-11-11, outside git) marks issues whose PRs publish runs.
- `scripts/publish_run.py --issue N` (required): reads number, title, URL and labels with `gh issue view`, warns when the issue lacks `training`, takes the author from `git config user.name`; `publish_run()` gains `extra` fields written into `run.json`.
- `published/2026-11-11_133858_baseline/run.json`: issue #22 and author added by hand (its source folder is gone).
- `viewer/vite.config.js`: every index entry (build and dev) gains `checkpoints`, per-tag aggregates computed from `episodes.json`; in dev a run present in both `runs/` and `published/` keeps the published issue and author.
- `viewer/src`: URL state; sidebar grouped by issue with search and collapse; run panel (last-checkpoint numbers, learning curve, episode grid with arrow-key moves); issue page (overlaid curves, run table with the differing config values).
- `README.md`: publish with `--issue`, the `training` label, the new viewer screens.
- `tests/test_publish.py`.

## Out Of Scope
- Comparing runs from different issues; sorting runs by capture rate (it conflicts with grouping by issue).
- A phone navigation stack (list → run → episode); phone width keeps the stacked layout.
- Playing two episodes side by side.
- Choosing which checkpoints to publish; recording the issue at training time (`train.py`).
- #18 (CSS modules) is open with uncommitted work in `FlyTracker-18` that moves the same components; whichever lands second redoes its part.

## Done Criteria
- [ ] pytest: `publish_run()` writes `extra` fields into `run.json`; the full suite passes.
- [ ] `publish_run.py` without `--issue` exits with a usage error; with `--issue` it records number, title, URL and author; a non-`training` issue prints a warning.
- [ ] `npm run build`: each `dist/runs/index.json` entry carries `checkpoints` matching a recount from `episodes.json`.
- [ ] dev server: local runs get the same `checkpoints`; a run in both folders shows its published issue.
- [ ] URL: reload restores the run, episode and issue page; Back and Forward move between them; an unknown id falls back to the newest run.
- [ ] Sidebar: groups by issue (newest group first, runs without an issue last), search by run name, issue title, author or algorithm, groups collapse.
- [ ] Run panel: grid cell click plays that episode; arrow keys move within the grid and Space plays; learning curve shown only with 2+ checkpoints.
- [ ] Issue page: one line per run, a dashed line for runs without steps (baseline), the table shows only config keys whose values differ.
- [ ] No caption or subtitle lines added; ko-ui-text check on the new strings.
- [ ] ui-evidence, 1600x900 and 390x844, run view and issue page: overflow none, no console errors.
- [ ] README passes ko-writing `check.py` and `readme_check.py`.

## Current State
- Seeded. Test data: three short local training runs (PPO, PPO with `--fov 60`, DQN; 30,000 step, evaluation every 3,000) in this worktree's gitignored `runs/`.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: viewer 실행 목록을 issue별로 묶고 학습 곡선과 에피소드 격자 넣기 (#27)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, AGENTS.md pointer.
#### Changes
- Seeded by `issue-start.mjs`; Summary, Goal, Scope, Out Of Scope, Done Criteria filled from the 2026-11-11 Q&A (four steps, label name `training`, Apple-style minimal, no captions or subtitles).
#### Verification
- `git diff --stat`: only the three seeded files.
#### Notes
- #18 overlap noted under Out Of Scope; the user chose to go ahead.

### feat: 실행을 올릴 때 issue와 올린 사람 적기 (#27)
> why: the viewer groups runs by issue, so each published run must say which issue it belongs to
#### Scope
- `flytracker/record.py`, `scripts/publish_run.py`, `tests/test_publish.py`, `published/2026-11-11_133858_baseline/run.json`.
#### Changes
- `publish_run(..., extra=None)`: `extra` is merged into `run.json`; `episodeCount` is still counted and cannot be overridden.
- `publish_run.py --issue N` is required. `gh issue view N --json number,title,url,labels` gives `issue: {number, title, url}`; `author` = `git config user.name` (empty when unset). Without the `training` label it prints a warning to stderr and still copies. gh missing or the issue unknown → exit 1 with the reason.
- Baseline run: `issue` = #22 (the issue that published it), `author` = `lhk0721`, written by hand because its `runs/` source folder no longer exists.
- GitHub label `training` created (green, "실행을 올려 viewer에서 보는 학습 작업"); not part of git.
#### Verification
- `uv run pytest -q`: 33 passed (1 new: extra fields land in `run.json`, `episodeCount` not overridable, `runs/index.json` untouched).
- CLI by hand, `--dest` in the scratchpad, on a local 30,000-step PPO run: no `--issue` → argparse usage error, exit 2; `--issue 27` → warning about the missing label, 39 files, `run.json` has number, title, URL and `author: lhk0721`, exit 0; `--issue 99999` → `issue #99999 정보를 읽지 못했다: GraphQL: Could not resolve…`, exit 1.
#### Notes
- That PPO run is 2,524 KB for 36 episodes, about 70 KB per episode; the baseline episodes are 10–38 KB because they end sooner. A default 200,000-step run (33 episodes) would be about 2.3 MB in git.

## Management Notes
### Follow-up Candidates
- `train.py --issue N` so local runs group by issue before publishing.
- Cross-issue comparison (multi-select in the sidebar).
- Phone navigation stack.
### References
- Eval seeds: `scripts/train.py` `RecordEvalCallback._record` uses `seed + i` at every checkpoint, so column i of the grid is the same start condition throughout a run.
