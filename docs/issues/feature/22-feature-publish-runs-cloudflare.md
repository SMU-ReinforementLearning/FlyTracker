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

## Management Notes
### Follow-up Candidates
- Optional GitHub Actions workflow that trains, publishes and opens the PR (user chose local training for now).
- Badge or filter in the viewer for published vs local runs.
### References
- Cloudflare Pages build configuration: https://developers.cloudflare.com/pages/configuration/build-configuration/ (Vite preset: `npm run build`, output `dist`; `NODE_VERSION` env var pins Node).
