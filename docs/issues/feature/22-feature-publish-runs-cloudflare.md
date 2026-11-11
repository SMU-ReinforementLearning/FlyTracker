# 22 학습 결과를 저장소에 올려 Cloudflare viewer에서 재생하기

## Document Relations
- Issue: #22
- Branch: `22-feature-publish-runs-cloudflare`
- Umbrella: (none)
- Status: in progress

## Summary
Lets a teammate copy a finished run into a tracked folder, open a PR, and after merge replay it on the viewer that Cloudflare Pages builds from `main`. The user asked for this in a Q&A (2026-11-11) and chose the default answers: training stays on each member's PC (not GitHub Actions), and the Cloudflare dashboard connection is done by the user after the repo side lands.

## Goal
- `python scripts/publish_run.py <run_id>` copies the run's JSON (no model files, no TensorBoard logs) into `published/<run_id>/`.
- `npm run build` in `viewer/` ships every published run inside `dist/`, so a static host serves `/runs/...` exactly as the dev server does today.
- Two PRs that each add a run never conflict: no shared list file is committed.

## Scope
- `flytracker/record.py`: `publish_run()`; writes `published/<run_id>/run.json` (the run's entry from `runs/index.json`) next to `config.json`, `episodes.json`, `episodes/<tag>/ep_NNN.json`.
- `scripts/publish_run.py`: thin CLI over `publish_run()`; refuses to overwrite without `--force`.
- `viewer/vite.config.js`:
  - build: emit `published/**` JSON into `dist/runs/` and generate `dist/runs/index.json` from the `run.json` files.
  - dev server: serve `runs/` and `published/` together under `/runs` (index merged, deduped by run id).
  - preview server: drop the `/runs` middleware so `npm run preview` shows exactly what Cloudflare will serve.
- `tests/`: pytest for `publish_run()`.
- `published/`: one fresh baseline run (5 episodes) as the first content, so the site is not empty and the build has something to check.
- `README.md`: `runs/` vs `published/`, the publish → PR → merge flow, the Cloudflare Pages settings. Kept to the sections it touches because #21 (README rewrite) is open.

## Out Of Scope
- Training on GitHub Actions.
- The Cloudflare dashboard itself (project creation, GitHub App on the org). The user does it; settings go in the README.
- Marking published vs local runs in the viewer UI.
- Changing the episode or run format, recording observations/actions, checkpoint evaluation.

## Done Criteria
- [ ] pytest: `publish_run()` copies only the listed JSON files, writes `run.json`, skips `checkpoints/`, `model.zip`, `tb/`, refuses an existing destination without overwrite.
- [ ] Full pytest suite passes.
- [ ] `npm run build` puts every published run plus a generated `index.json` under `dist/runs/`; nothing named `index.json` is committed under `published/`.
- [ ] `npm run preview` (dist only): the run list shows the published run and an episode plays. Screenshot evidence via ui-evidence.
- [ ] `npm run dev`: local runs and published runs show together; a run present in both shows once.
- [ ] README passes ko-writing `check.py` and `readme_check.py`.
- [ ] After the user connects Cloudflare Pages and the PR merges: the production URL lists the published run and plays it. (Recorded here once checked; may land after the merge.)

## Current State
- Issue, branch and worktree created from `origin/main` @ fc67f84; this document filled. Next: first commit, then `publish_run()` + tests.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 학습 결과를 저장소에 올려 Cloudflare viewer에서 재생하기 (#22)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, AGENTS.md pointer.
#### Changes
- Seeded by `issue-start.mjs`; Summary, Goal, Scope, Out Of Scope, Done Criteria filled from the 2026-11-11 Q&A.
#### Verification
- `git diff --stat` shows only the three seeded files.
#### Notes
- #21 (README rewrite) is open in `FlyTracker-21` with no commits yet; whichever merges second rebases README.

### feat: 실행을 published 폴더로 복사하는 스크립트 (#22)
> why: runs/ is gitignored and holds model files; a run needs a JSON-only copy that can go into git without a shared list file
#### Scope
- `flytracker/record.py`, `scripts/publish_run.py`, `tests/test_publish.py`.
#### Changes
- `publish_run(runs_root, run_id, dest_root, overwrite=False)`: copies `config.json`, `episodes.json` and every episode file listed in it; writes `run.json` = the run's entry from `runs/index.json` with `episodeCount` recomputed. Checks every source first, writes into `.<run_id>.tmp`, then swaps it in. Raises `FileExistsError` unless `overwrite`.
- `scripts/publish_run.py <run id or runs/<id>> [--runs-dir] [--dest published] [--force]`; stdout and stderr forced to UTF-8 so errors are readable in a cp949 console.
- Module docstring of `record.py` describes `published/`.
#### Verification
- `uv run pytest -q`: 32 passed (4 new: JSON-only copy with checkpoints/model.zip/tb present, run.json equals index entry, refuse then overwrite removes stale files, unknown id and missing episode write nothing).
- CLI by hand on a fresh `record_baseline.py --episodes 5` run with `--dest` in the scratchpad: 8 files, 128 KB; second call exits 1 with the `--force` hint; `--force` succeeds; unknown id exits 1. Messages render in Korean (they were garbled before stderr was reconfigured).
#### Notes
- Episode paths in `episodes.json` stay `<run_id>/episodes/...`, relative to whichever root serves `/runs`, so the viewer needs no path rewrite.

### feat: viewer build에 published 실행 넣기 (#22)
> why: a static host has no `/runs` middleware, so the build itself must carry the published runs and their list
#### Scope
- `viewer/vite.config.js` only. Screen code still reads `/runs/...`; nothing in `viewer/src` changes.
#### Changes
- build (`generateBundle`): emits every JSON under `published/<run_id>/` to `dist/runs/<run_id>/` and a generated `dist/runs/index.json` built from the `run.json` files, sorted by `createdAt`. Files at the top of `published/` and dot-folders (publish temp dirs) are skipped.
- dev server: `/runs/index.json` = `runs/index.json` entries + published entries whose id is not local; a file is looked up in `runs/` first, then `published/`. Path check kept per root (only `.json` inside the root).
- preview server: the `/runs` middleware is gone, so `npm run preview` serves `dist/` exactly as Cloudflare will.
#### Verification
- `npm run build --prefix viewer`: `dist/runs/` holds the published run's 8 files plus `index.json` listing only that run; `ep_003.json` byte-identical to the source (`cmp`). The >500 kB chunk warning is the existing three.js bundle.
- dev server (port 5191), `runs/` = {baseline (also published), local-only}: index lists both, baseline once; local-only file 200; `..%2Fpyproject.toml`, `..%2Fviewer%2Fpackage.json`, unknown run → 404. With `runs/` moved away: index lists the published run only and its episode file is 200.
- preview server (port 5192): index lists only the published run; the local-only run's `episodes.json` is not served (HTML fallback, as on Cloudflare).
- ui-evidence (commit 589c20b + this uncommitted change, Chrome 156.0.8078.74), captures kept in the session scratchpad, not committed:

| page | viewport | overflow | probes | console |
| --- | --- | --- | --- | --- |
| preview `/` | 1600x900 | none | run rows = 1 (`baseline 11월 11일 13:38`), episode rows = 5 | favicon.ico 404 (no favicon in the repo), THREE.Clock deprecation, GL ReadPixels stall |
| preview `/` | 390x844 mobile | none | run rows = 1, episode rows = 5 | THREE.Clock deprecation only |
| dev `/` | 1600x900 | none | run rows = 2 (`local-only`, `baseline`) | same as preview |

  - preview 1600x900: published baseline run selected, episode 5 playing at 2.92 / 4.26 s, frame 146 / 214, both views and both charts drawn.
  - dev 1600x900: local-only run on top, published baseline below it, episode 2 playing.
#### Notes
- On Cloudflare a missing file returns the SPA `index.html` with 200, not 404. `index.json` is always emitted, so the run list never hits that case.

### chore: 기준선 실행 하나를 published에 올리기 (#22)
> why: the deployed viewer should not open empty, and the build needs real content to check
#### Scope
- `published/2026-11-11_133858_baseline/` (8 files, 128 KB).
#### Changes
- Made with `python scripts/record_baseline.py --episodes 5` on this branch (env defaults, seeds 0–4), then `python scripts/publish_run.py 2026-11-11_133858_baseline`.
#### Verification
- Summary printed by the recorder: 포획 5/5, 평균 보상 −13.71, 보인 비율 24%, 포획까지 평균 3.53초.
- This is the run shown in the preview capture above.
#### Notes
- None.

## Management Notes
### Follow-up Candidates
- Optional GitHub Actions workflow that trains, publishes and opens the PR (user chose local training for now).
- Badge or filter in the viewer for published vs local runs.
### References
- Cloudflare Pages build configuration: https://developers.cloudflare.com/pages/configuration/build-configuration/ (Vite preset: `npm run build`, output `dist`; `NODE_VERSION` env var pins Node).
