# 94 각가속도 조준기(#88)의 학습 실행 15개를 올리고 viewer에서 학습 실행과 평가 실행 구분하기

## Document Relations
- Issue: #94
- Branch: `94-feature-publish-training-runs-mark-eval`
- Umbrella: (none)
- Status: in progress

## Summary
Publish the 15 stage-1 training runs of #88 so the viewer can replay how the aim developed during training, and make the viewer say which runs were recorded during training and which are a finished model played again. #88 published only replays of the final models (3 episodes each, tag `step_1000000`), so the user, looking at #88's row A, found one checkpoint and nothing that says the run is an evaluation (2026-11-26: "100만 스텝 것 밖에 없는데, 그건 왜그래? 평가라 그래?", "평가랑 학습 구분이 없네?").

## Goal
- The training runs of #88 (first stage: 5 conditions x training seeds 0, 1, 2, 21 checkpoints x 3 episodes each; second stage: 4 fire-only conditions x 3 seeds, 11 checkpoints x 3 episodes) are in `published/` under issue #88 and play in the viewer.
- In the viewer a reader can tell a training run from a replay of a trained model without opening the run: in the issue page's table, in the sidebar and in the run panel.

## Scope
1. `published/`: 15 runs copied with `scripts/publish_run.py --issue 88` from `FlyTracker-88/runs/g88/<condition>-s<k>/` (the user chose all 15, 2026-11-26; about 68 MB). They are filed under #88 because they are that experiment's runs; the viewer groups by the issue in `run.json`.
2. `published/issues/88.json`: the paragraph that counts the published runs, and a note that explains the two kinds.
3. `viewer/src/data/experiment.js`: the kind of record of a run, derived from `config.json` (a learned side with `algo.model` is a replay of a trained model; a learned side without it was recorded during its training); combinations never mix the two kinds.
4. Viewer screens: the kind shown in the issue page's table, the sidebar run rows and the run panel. The wording and placement are proposed with screenshots and decided by the user.
5. `ui-text.glossary.md`, README (viewer section) for the new term; tests for the kind and the combinations.
6. Added 2026-11-26 after the user saw the first screens ("88 이슈 말고도 다른 이슈들도 다 이렇게 작업해놔"), read by the agent as: everything that can be done for the other runs too. (a) The 12 stage-2 (fire-only) training runs of #88 from `FlyTracker-88/runs/g88f` are published as well (27 training runs in all). (b) An evaluation row names the row its model was trained in even when that is another issue (#42 -> #35, #61 and #72 -> #51): `combinationsOf(..., origins)`, `useOrigins` in `useIssueData.js`. (c) Fire-only conditions are one row each (`algo.aim` differs per training seed and is no longer part of the signature) and name the row of their aim model. The label 학습 / 평가 itself is code and already applied to every issue.

## Out Of Scope
- Training runs of #59's aimer model (`issue59-sac-300000`): the teammate's, not on this machine.
- Re-recording or re-measuring anything; no model is run in this issue.
- Changing `publish_run.py` or the run format; the kind is derived from what `config.json` already holds.
- #79 (choosing which episodes to replay from the 200-seed measurements).

## Done Criteria
- [x] 27 training runs in `published/` (15 with 63 episodes, 12 with 33) and `run.json` naming issue #88; pytest passes.
- [x] The viewer shows the kind for every run of #88 and the kinds are right for all published issues (checked over every published run, not a sample).
- [x] Screenshots (desktop and 390 px) of the issue page, sidebar and run panel shown to the user; wording approved.
- [x] Viewer build passes; viewer tests pass.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-27. The user said "다 머지해" (2026-11-26) after seeing the screens of #94, #95 and #96: commit, push, PR and squash merge. Everything in Scope 1-6 is committed; the pointer line is removed in the last commit.

Earlier notes:
2026-11-26 22:00 KST. All of Scope 1-5 is in the working tree, nothing committed: waiting at the Pre-Commit Review Gate for the user's approval of the screens (kind column "기록" with 학습 / 평가, sidebar sub-headings, "모델 실험 B" on evaluation rows, no reward lines on evaluation rows). Planned commits: the seed commit, the 15 runs with `88.json`, the viewer change with README, glossary and tests. Verified in the working tree: 274 passed, 1 skipped; `npm run build` passes; screenshots in `.ui-evidence/` (gitignored). After the first screens the user asked for the same on the other issues; Scope 6 was added and is also in the working tree (viewer tests pass; full pytest and build not re-run since). Letters of #88 changed: the old row A (replay of `accel-pen-rule`) is now J, its training runs are B; #88 has 9 training rows and 7 evaluation rows.

Traps: `uv run pytest` here picks a pytest outside this worktree and imports the stale main checkout's `flytracker`; use `env -u VIRTUAL_ENV -u PYTHONPATH uv run --extra neural --extra train --with pytest python -m pytest -q`. A dev server for this worktree may still run on port 5194.

Open question from the user (2026-11-26), not in this issue: a first-shot kill looks like the old aim-hold capture in the viewer. The agent proposed a separate issue (beam drawn only while firing, shot ticks on the transport bar, a hit marker at the end); no answer yet.

Earlier: This session could not `EnterWorktree` into `FlyTracker-94` (same trap as #88: the tool only accepts worktrees under `.claude/worktrees`); it works here by absolute path and with `git -C`.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 각가속도 조준기(#88)의 학습 실행 15개를 올리고 viewer에서 학습 실행과 평가 실행 구분하기 (#94)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, `AGENTS.md` pointer.
#### Changes
- Doc filled from the 2026-11-26 conversation: which runs (all 15 stage-1 runs) and one issue for both parts were the user's choices.
#### Verification
- `issue-start.mjs` created issue #94 (Type Feature, labels enhancement and training, assignee the user, Priority Medium), branch from `origin/main` @ dcce349, worktree `FlyTracker-94`.
#### Notes
- Priority Medium was chosen by the agent: ordinary planned work, nothing waits on it.
- Filing the runs under #88 instead of #94 is the agent's choice (reason in Scope 1); tell the user at the review gate.

### feat: #88의 학습 실행 27개를 올리기 (#94)
> why: the user asked for the training runs next to the replays of the final models
#### Scope
`published/2026-11-25_1310*` (15 runs), `published/2026-11-26_030258_fire-*` (12 runs), `published/issues/88.json`.
#### Changes
- 15 stage-1 runs (5 conditions x training seeds 0, 1, 2; 21 checkpoints x 3 episodes) and 12 stage-2 fire-only runs (4 conditions x 3 seeds; 11 checkpoints x 3 episodes), copied with `scripts/publish_run.py --issue 88` from `FlyTracker-88/runs/g88` and `runs/g88f`.
- `88.json`: the last paragraph counts 40 runs and says which are recorded during training and which replay a finished model; the episode-seed note covers both.
#### Verification
- `publish_run.py` reported 66 files for each stage-1 run and 36 for each stage-2 run, no failure. All 945 stage-1 episode files carry seeds 10000-10002 (read from every file).
- Full pytest on the final tree: 275 passed, 1 skipped.
#### Notes
- The stage-2 runs were added after the user's "다른 이슈들도 다 이렇게 작업해놔"; their first choice had been the 15 stage-1 runs.
- About 75 MB of JSON; the viewer build output was 184 MB with the first 15 runs (not measured before or after the 12 more).
- Committed as 1,422 new files under `published/` (15 x 66 + 12 x 36) and the edit to `88.json`.

### feat: viewer에서 학습 실행과 평가 실행을 가르고 평가 줄에 모델을 학습한 줄 적기 (#94)
> why: a replay of a final model and a run recorded during training looked the same, and a replay showed the reward weights of the replay environment as if the model had been trained with them
#### Scope
`viewer/src/data/experiment.js`, `useIssueData.js`, `App.jsx`, `Combinations`, `RunPanel`, `Sidebar`, `IssuePage`, `README.md`, `ui-text.glossary.md`, `tests/test_viewer_combinations.py`.
#### Changes
- `recordKindOf`: a learned side with `algo.model` is an evaluation, without it a training record; runs without a learned side have no kind. `combinationsOf` never mixes the kinds, puts training rows first, orders a row's runs by training seed, drops reward lines from evaluation rows and no longer splits fire-only conditions by `algo.aim`.
- References: an evaluation row names the row its model was trained in ("모델 실험 B"), a fire-only row the row of its aim model; `origins` (`useOrigins`) resolves models trained in another issue ("모델 #51 실험 B").
- Screens: a "기록" column (학습 / 평가) in the issue page's table, a "기록" row in the run panel, sub-headings 학습 / 평가 in the sidebar for groups that hold both.
#### Verification
- Full pytest: 275 passed, 1 skipped (4 new tests over the published runs). `npm run build`: built.
- Kinds printed for every published run of every issue match the episode counts (63 or 33 for training, 3 or 5 for evaluation); letters of #42, #59, #61, #72 unchanged.
- ui-evidence on this worktree's dev server (port 5194): `/?issue=88` at 1600 and 390 px, a training run, an evaluation run, `/?issue=72` (rows B, D, F read "모델 #51 실험 B"). At 390 px the table is wider than the page and scrolls inside its own box, as before.
#### Notes
- The first version put the kind after the run name in the sidebar ("학습 seed 0 학습"); replaced by sub-headings before the user saw it.
- The sidebar and run panel were captured for #88 only; the stage-2 rows and the final 16-row table of #88 were checked by the printed combinations and the tests, not by a new screenshot.
- Letters of #88 changed: the replay of `accel-pen-rule` was A and is J.
- "평가" also names the episodes a training run records at each checkpoint (glossary: 평가 에피소드); told to the user, who kept the words.
- Committed with the full pytest and the build re-run on the final tree (275 passed, 1 skipped; built).

### chore: #94 포인터를 지우고 완료로 표시하기 (#94)
> why: the pointer line has to go in the branch's last commit; a protected branch cannot take that edit after the merge
#### Scope
`AGENTS.md`, `docs/issues/README.md`, this doc.
#### Changes
- Pointer line removed, registry row and Status set to done.
#### Verification
- `git diff origin/main -- AGENTS.md` is empty after this commit.
#### Notes
- The PR merged box is ticked here because the doc cannot be edited after the merge.

## Management Notes
### Follow-up Candidates
- Stage-2 training runs (`runs/g88f`, 12 runs) are not published.
### References
- #88 management doc: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire.md` (where the models and archives are).
- #92: the combinations table this issue extends.
