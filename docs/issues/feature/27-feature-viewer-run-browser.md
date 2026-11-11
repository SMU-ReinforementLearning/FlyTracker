# 27 viewer 실행 목록을 issue별로 묶고 학습 곡선과 에피소드 격자 넣기

## Document Relations
- Issue: #27
- Branch: `27-feature-viewer-run-browser`
- Umbrella: (none)
- Status: done

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
- `viewer/src`: URL state; sidebar grouped by issue with search and collapse; run panel (numbers of the selected checkpoint, learning curve, episode grid with arrow-key moves); issue page (overlaid curves, run table with the differing config values).
- `README.md`: publish with `--issue`, the `training` label, the new viewer screens.
- `tests/test_publish.py`.

## Out Of Scope
- Comparing runs from different issues; sorting runs by capture rate (it conflicts with grouping by issue).
- A phone navigation stack (list → run → episode); phone width keeps the stacked layout.
- Playing two episodes side by side.
- Choosing which checkpoints to publish; recording the issue at training time (`train.py`).
- #18 (CSS modules) is open with uncommitted work in `FlyTracker-18` that moves the same components; whichever lands second redoes its part.

## Done Criteria
- [x] pytest: `publish_run()` writes `extra` fields into `run.json`; the full suite passes.
- [x] `publish_run.py` without `--issue` exits with a usage error; with `--issue` it records number, title, URL and author; a non-`training` issue prints a warning.
- [x] `npm run build`: each `dist/runs/index.json` entry carries `checkpoints` matching a recount from `episodes.json`.
- [x] dev server: local runs get the same `checkpoints`; a run in both folders shows its published issue.
- [x] URL: reload restores the run, episode and issue page; Back and Forward move between them; an unknown id falls back to the newest run.
- [x] Sidebar: groups by issue (newest group first, runs without an issue last), search by run name, issue title, author or algorithm, groups collapse.
- [x] Run panel: grid cell click plays that episode; arrow keys move within the grid and Space toggles play; learning curve shown only with 2+ checkpoints.
- [x] Issue page: one line per run, a dashed line for runs without steps (baseline), the table shows only config keys whose values differ.
- [x] No caption or subtitle lines added; ko-ui-text check on the new strings.
- [x] ui-evidence, 1600x900 and 390x844, run view and issue page: overflow none, no console errors.
- [x] README passes ko-writing `check.py` and `readme_check.py`.

## Current State
- Done. All Done Criteria are met; the user asked for merge and deploy ("머지 배포까지 진행해", 2026-11-11). The untracked test folders under `published/` were deleted before the PR; the synthetic and short local runs remain only in this worktree's gitignored `runs/`.
- After merge: check that https://flytracker-ewk.pages.dev/ shows the grouped sidebar and `?issue=22`; post the result on #27.

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

### feat: 실행 목록에 checkpoint별 요약 넣기 (#27)
> why: the sidebar sparkline and the learning curves need per-checkpoint numbers without downloading every episode file
#### Scope
- `viewer/vite.config.js` only.
#### Changes
- `checkpointsOf(manifest)`: groups `episodes.json` summaries by tag → `{tag, step, episodes, captured, meanReturn, meanCaptureTime}`; `step` from `step_N` (`initial` = 0, other tags such as `baseline` = null); sorted by step, null first; means rounded to 4 decimals, `meanCaptureTime` over captured episodes only (null when none).
- Build and dev index entries carry `checkpoints`. In dev, a run in both `runs/` and `published/` keeps the local entry and files but takes `issue` and `author` from the published `run.json`.
#### Verification
- `npm run build`: the baseline entry has one checkpoint `{baseline, step null, 5 episodes, 5 captured, meanReturn −13.7137, meanCaptureTime 3.528}`, matching the recorder's printed summary (−13.71, 3.53 s).
- A Python recount from `episodes.json` (scratchpad `recount.py`) matches every checkpoint of the build index and of the dev index (baseline, two 12-checkpoint PPO runs, one DQN run still training): 0 mismatches.
- Dev index with the two PPO runs also published locally under `--issue 27`: both show issue 27 and author `lhk0721`; the DQN run (local only) has neither.
#### Notes
- PPO evaluates at multiples of its 2,048-step rollout, so `--eval-every 3000` gave 12 checkpoints (0, 3,000 … 30,720).
- The locally published PPO runs are test data and are not committed.

### feat: viewer에 issue별 실행 목록, 실행 패널, issue 비교 화면 넣기 (#27)
> why: steps 1–4 of the plan on the screen side; one commit because all four share `App.jsx` and `styles.css` and were written together after the session that started them was interrupted
#### Scope
- New: `viewer/src/route.js`, `viewer/src/data/runs.js`, `viewer/src/components/{CurveChart,RunPanel,IssuePage}.jsx`.
- Changed: `viewer/src/App.jsx`, `components/Sidebar.jsx`, `components/LineChart.jsx` (helpers exported), `data/api.js`, `data/labels.js`, `styles.css`, `ui-text.glossary.md`.
#### Changes
- URL state (`useRoute`): `?run=<id>&tag=<tag>&ep=<n, 1-based>` or `?issue=<number|none>`. Clicks push; arrow-key moves and address corrections replace. An unknown run or issue opens the newest run; an unknown tag or ep opens the last episode of the last checkpoint.
- Sidebar: search field (run name, issue title, `#N`, author, algorithm), groups by issue (group of the newest run first, "issue 없음" last), disclosure button per group, group title opens the issue page. A run row shows the last checkpoint's capture rate and a sparkline when the run has 2+ stepped checkpoints. The episode list left the sidebar.
- Run panel (300 px column between sidebar and stage): numbers of the selected checkpoint (not the last one, as first written in Scope — the heading names the checkpoint and it follows the grid selection), learning curve with a capture-rate / mean-reward switch (only with 2+ stepped checkpoints; click picks that checkpoint), episode grid (rows = checkpoints in training order, columns = evaluation episode; filled dot = capture, darker = faster; × = timeout). Arrow keys move the selection and play it, Space toggles play.
- Toolbar shows the selected episode (checkpoint, episode number, outcome, return).
- Issue page: overlaid learning curves (8 categorical colours as CSS variables, assigned in creation order), a dashed horizontal line for a run without steps, a table with one row per run (last checkpoint numbers) plus one column per config key whose value differs among the runs that have the key; the run name opens the run. Toolbar links to the GitHub issue.
- Layout: stage stacks at ≤1360 px (was 1080) because of the new column; at ≤1080 px the run panel stacks above the stage.
- Glossary: 포획률, 평균 보상, 포획 시간, 학습 곡선, checkpoint, 올린 사람, issue 없음.
#### Verification
- `npm run build`: passes.
- Series palette, dataviz `validate_palette.js`: light on `#ffffff` and dark on `#1c1c1e` both ALL CHECKS PASS; light slots 3–5 are below 3:1 against the surface (WARN), relieved by the table under the chart.
- Test data (uncommitted): the two real 30,000-step PPO runs and the DQN run (0 captures everywhere), plus two synthetic entries made by a scratchpad script — `demo-learns` (PPO run copy whose episode summaries were rewritten so captures appear from checkpoint 4; `reward.angle` 0.1; author `teammate`) and `baseline-copy` (the baseline under issue 27). Episode files were not changed.
- Interaction script run as an async ui-evidence probe at 1600x900 on `?run=…demo-learns&tag=step_0018000&ep=2`, all as expected: the address opens that cell; cell click pushes one history entry; ArrowRight/ArrowUp move, keep focus on the selected cell and add no history entry; ArrowRight at the last column stays; Space toggles 일시정지 → 재생; a click at the left end of the curve selects 학습 전; group title opens `?issue=27` with 4 table rows; Back returns to the episode, Forward to the issue; a run name in the table opens that run; search by name / author / algorithm / issue title / `#27` each returns the expected runs; no match shows the empty note; collapsing the first group hides its 4 rows; group order is #27, #22, issue 없음.
- ui-evidence (dev server on 5180 checked to serve this worktree, Chrome 156, 1600x900 and 390x844), 6 addresses × 2 viewports:

| address | result |
| --- | --- |
| `?run=nope&tag=x&ep=99` | corrected to the newest run, last checkpoint, last episode |
| `?issue=999` | same fallback |
| `?run=…baseline` | 5 cells, no learning curve (one checkpoint) |
| `?issue=22` | 1 row, no curve, no config columns |
| `?issue=27` | 1 curve chart, 1 dashed line, 4 rows, config columns `env.camera.fov_v_deg`, `env.reward.angle` |
| `?run=…demo-learns&tag=step_0018000&ep=2` | 36 cells, curve shown |

  Page-level horizontal scroll: none in all 12 shots (`scrollWidth <= innerWidth`). The script flags the run table at 390 px on the two issue pages; the table is wider than the phone by design and scrolls inside its own `overflow-x: auto` card. Console: only the existing `favicon.ico` 404 and three.js deprecation warnings. PNGs looked at for the run view and issue 27 at both widths (dark scheme); they stay in the session scratchpad, not committed.
- No caption or subtitle element added: `figcaption` count is 2 on the run view (the two existing per-episode charts) and 0 on the issue page.
#### Notes
- Not checked: light colour scheme by screenshot (the palette was validated numerically only); Firefox and Safari.
- With more than 8 runs in one issue the line colours repeat.
- Runs with equal values overlap on the curve (the two 0% PPO runs draw as one line); the table tells them apart.

### docs: README에 issue 번호로 올리는 법과 viewer 새 화면 넣기 (#27)
> why: publishing now needs `--issue`, and the viewer section described the old two-list sidebar
#### Scope
- `README.md` only.
#### Changes
- 실행 올리기: the example uses `--issue 22`; what `--issue` records, the `gh` login it needs, the `training` label and its warning; `run.json` described with `issue` and `author`.
- viewer: one paragraph replaced by five subsections (실행 목록, 실행 패널, 재생 화면, issue 화면, 링크) with the URL table.
- "체크포인트" → "checkpoint" (4 places) to match the glossary entry added in the previous commit.
#### Verification
- ko-writing `check.py README.md`: no banned pattern, endings uniform (해라체), no paragraph over 6 sentences, no heading finding; remaining warnings are older lines (116, dates at 48 and 250, 104).
- `readme_check.py README.md`: 0 fail, 0 warn (URLs not probed).
- `uv run pytest -q`: 33 passed. `npm run build` passed in the previous commit; no viewer file changed since.
#### Notes
- The `gh` link (cli.github.com) was not probed online.

### chore: #27 pointer 줄 지우고 문서 상태를 done으로 (#27)
> why: last commit on the branch before the PR, per the post-PR cleanup gate
#### Scope
- `AGENTS.md`, `docs/issues/README.md`, this document.
#### Changes
- Pointer line removed, registry row and Status set to done, Current State rewritten.
#### Verification
- `git status --short` after deleting the four untracked `published/` test folders: clean before this commit.
#### Notes
- (none)

## Management Notes
### Follow-up Candidates
- `train.py --issue N` so local runs group by issue before publishing.
- Cross-issue comparison (multi-select in the sidebar).
- Phone navigation stack.
### References
- Eval seeds: `scripts/train.py` `RecordEvalCallback._record` uses `seed + i` at every checkpoint, so column i of the grid is the same start condition throughout a run.
