# 61 신경망 초파리와 SAC 조준기 대결 에피소드 올리기

## Document Relations
- Issue: #61
- Branch: `61-chore-neural-fly-sac-episodes`
- Umbrella: (none)
- Status: done

## Summary
Record and publish episodes of the adopted SAC aimer (`sac-beam-assist`, #51) and the rule baseline against the neural fly (#31) under env version 5. The aimers were trained and tuned against the rule fly only, so these episodes show how they do against a fly they have never seen. Nothing is trained here.

## Goal
Eight published runs the viewer can play, grouped under issue #61: four aimers x two stimulus settings x three seeds.

| Axis | Values |
|---|---|
| Aimer | `sac-beam-assist-s0`, `-s1`, `-s2` (final models of #51), rule baseline |
| Fly | neural, gaze-contingent stimulus on (defaults: 2.5 deg, 120 ms charge, at most 3 events) / off (`--no-stimulus`) |
| Seeds | 10000, 10001, 10002 (those of the runs published so far) |
| Everything else | default `EnvConfig` of env version 5 (10 s limit, laser capture 1.25 mm for 0.15 s), no lesion |

The stimulus-off setting is the fair comparison: with the stimulus on, the fly's path depends on what the aimer does, so two aimers do not meet the same fly on the same seed (#31 doc).

## Scope
- `docs/issues/chore/61-chore-neural-fly-sac-episodes/record_match.py`: records one aimer under any env setting, building the aimer with `load_opponent` so the tracking assist is applied.
- The eight runs under `published/`, with local paths removed the way #56 did it.
- `published/issues/61.json` (required per issue since #47).

## Out Of Scope
- Training against the neural fly (the teammate's #58 / #59).
- Lesion settings, other stimulus parameters, other seeds, the three SAC conditions that lost to the baseline in #51.
- Viewer changes. (The gap noted at registration is gone: since #62 the experiment card reads `env.fly_model`.)
- A capture-rate claim. Three seeds per run is a viewing sample, not a measurement.

## Done Criteria
- [x] `record_match.py` reproduces known results against the rule fly on this machine. (2026-11-16 19:08)
- [x] Eight runs recorded on one machine that has the flysim project, all with env version 5. (2026-11-17 20:18, the user's laptop, bundled assets of #64)
- [x] Published copies contain no local path (`grep` for the flysim location and the user folder returns nothing). (2026-11-17)
- [x] `published/issues/61.json` written; `npm run build --prefix viewer` lists the eight runs under issue 61. (2026-11-17)
- [x] PR merged; `AGENTS.md` pointer removed in the branch's last commit. (2026-11-17, pointer removed in the commit below; merge follows it)

## Current State
2026-11-17 20:40. The teammate's PR #65 (#64, flysim code and neural data bundled under `flytracker/neural_assets/`) was merged on 2026-11-16; `origin/main` is merged into this branch. The eight runs are recorded on the user's laptop, copied to `published/` and described in `published/issues/61.json`. The user approved commit, push, PR and squash merge on 2026-11-17.

Next: nothing in this issue once the PR is merged. The fly's behaviour (wall input driving escape, flying along the far wall on seed 10002) was passed to the teammate by the user and is not touched here.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 신경망 초파리와 SAC 조준기 대결 에피소드 올리기 (#61)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, `AGENTS.md` pointer.
#### Changes
- Doc filled from the conversation: the combination is the one the user approved on 2026-11-16 (four aimers x stimulus on/off x seeds 10000-10002).
#### Verification
- `issue-start.mjs` created issue #61, branch from `origin/main` @ 7bd3ea5, worktree `FlyTracker-61`.
#### Notes
- No umbrella: the open umbrella #58 is the teammate's workstream.

### chore: 조준기 하나를 임의의 환경 설정으로 녹화하는 스크립트 (#61)
> why: `record_baseline.py` records only the rule aimer and `match.py` saves no episodes; #44's `record_model_v3.py` calls `model.predict` directly, which would drop the tracking assist `sac-beam-assist` was trained with
#### Scope
`docs/issues/chore/61-chore-neural-fly-sac-episodes/record_match.py`. No change to `scripts/`, the package or the viewer.
#### Changes
- `record_match.py <baseline | run folder>` plus the env flags of `record_baseline.py`. The aimer comes from `load_opponent` and sees the raw observation, as in `matchup.play_cell`. Defaults: seeds 10000-10002. Run name `<rule | neural-stim | neural-nostim>-<aimer name>`; episodes tagged `step_<steps>` for a model, `baseline` for the rule aimer.
- `config.json` of a model run keeps the model's `algo` block and adds `model` and `trainedEnvVersion` (as #44 did). `algo.opponent` stays the fly the model was trained against; the fly of the run is `env.fly_model`.
#### Verification
All against the rule fly, seeds 10000-10002, on the user's laptop (torch 2.15.0+cpu, SB3 2.9.2):
- Baseline: 5.13 / 5.03 / 4.16 s, 3/3 captured, mean return -22.58, visible 26%. `scripts/record_baseline.py --seed 10000 --episodes 3 --no-save` prints the same summary line.
- `sac-beam-assist-s0/s1/s2`: 3.03, 2.73, 1.63 / 3.02, 2.59, 5.37 / 1.29, 1.19, 2.40 s, 9/9 captured. The training-time path (`make_env(assist=0.2)` + `model.predict`) gives the same nine durations and visible ratios on this machine.
- Against the runs published in #51 (recorded on the vast.ai instance): five of nine durations equal, four differ by 0.01-0.12 s (s0 seed 10001 2.73 vs 2.69; s2 1.29 / 1.19 / 2.40 vs 1.32 / 1.20 / 2.28). Since both paths agree here, the difference is between machines, not between the script and training.
- Saving: a saved rule-fly run of `sac-beam-assist-s0` has `envVersion` 5, the model's `algo` block plus `model` / `trainedEnvVersion`, and three episodes under `step_1000000` (written to a scratch folder outside the repo).
- `--fly-model neural` without the flysim project stops with `Neural flight requires neural.source_root / --neural-source / FLYTRACKER_NEURAL_SOURCE` and leaves no run folder (the run is created after the first episode).
- Not run: the full pytest suite (no package code changed), anything with the neural fly.
#### Notes
- Episodes are not bit-reproducible across machines, so all eight runs must be recorded on the same machine, the baseline included.
- `--neural-source` puts the local path into `config.json`; use `FLYTRACKER_NEURAL_SOURCE`. Episode files still carry `resolved_source_root` / `resolved_data_dir` (`NeuralFly.provenance`) and must be stripped before publishing.

### chore: 신경 초파리와 겨룬 조준기 실행 8개 올리기 (#61)
> why: the neural fly became runnable here once #64 put the flysim code and data in the repo
#### Scope
Eight run folders under `published/`, `published/issues/61.json`, this document. No code change.
#### Changes
- Merged `origin/main` (67c6750) into the branch first; the only conflict was the registry table in `docs/issues/README.md` (rows added on both sides, both kept).
- Recorded with `record_match.py <aimer> --fly-model neural [--no-stimulus]`, default seeds, no `--neural-source` and no env var (bundled assets), then `scripts/publish_run.py <run> --issue 61` for each.
- `61.json`: `compare` 51, purpose in four paragraphs, four notes. One note says the stimulus-off runs still show escape phases: wall approach feeds the same LPLC2 inputs (`flytracker/neuromechanics.py`), so "stimulus off" is not "no escape".
#### Verification
Durations in seconds for seeds 10000 / 10001 / 10002, all env version 5, user's laptop:

| Aimer | Stimulus on | Stimulus off |
|---|---|---|
| baseline | 5.32 / 5.45 / 4.89 | 5.28 / 5.36 / 5.01 |
| sac-beam-assist-s0 | 2.81 / 3.00 / 2.27 | 2.67 / 2.95 / 9.71 |
| sac-beam-assist-s1 | 2.89 / 2.70 / 8.84 | 2.88 / 2.71 / not captured (10.0) |
| sac-beam-assist-s2 | 1.22 / 1.20 / 3.35 | 1.21 / 1.20 / 9.81 |

- 23 of 24 captured. Baseline, stimulus on, seed 10000 = 5.32 s, the figure in the teammate's PR #65 from their machine.
- `grep -rIl -i` for the user folder name, `Users` and drive-letter paths over the eight published folders: no hit. `config.json` has `neural.source_root` and `data_dir` null.
- `npm run build --prefix viewer` (after `npm ci` in this worktree): built; `viewer/dist/runs/index.json` has 37 runs, 8 with issue 61.
- `uv run pytest -q` after the merge: 203 passed.
- Not done: the built page was not opened in a browser.
#### Notes
- `load_opponent` warns that the env differs from training (`fly_model`); expected here.
- Seed 10002 with the stimulus off is slow or missed for all three SAC models (9.71, 10.0, 9.81 s) while the baseline takes 5.01 s. One seed; no claim made. Worth a look if the measured comparison below is done.

### chore: #61 pointer 지우고 문서 닫기 (#61)
> why: the protected base branch cannot take this edit after the merge
#### Scope
`AGENTS.md` pointer line, registry row status, this document's status.
#### Changes
- Pointer line removed; registry row and `Status` set to done.
#### Verification
- `git show origin/main:AGENTS.md` has an empty pointer slot; this branch's slot is empty again after the edit.
#### Notes
- Follow-up outside this issue, raised by the user on 2026-11-17: a fire action for the aimer with a cost for firing (the laser is implicitly always on today). Not decided; needs its own issue.

## Management Notes
### Follow-up Candidates
- A measured comparison (200 seeds, gate) of the aimers against the neural fly, if the team wants a number.
### References
- #31 neural fly, #51 SAC under the laser rule, #44 `record_model_v3.py`, #47 `published/issues/<n>.json`, #56 published neural runs without paths.
