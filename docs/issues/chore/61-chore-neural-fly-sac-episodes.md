# 61 신경망 초파리와 SAC 조준기 대결 에피소드 올리기

## Document Relations
- Issue: #61
- Branch: `61-chore-neural-fly-sac-episodes`
- Umbrella: (none)
- Status: in progress

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
- Fixing the four neural tests that fail on main since the capture rule changed (#31 doc, 2026-11-16 note).
- Viewer changes. Known gap: the issue page's experiment card derives the fly from `algo.opponent` and will call these flies "rule"; the episode readout itself shows the neural model.
- A capture-rate claim. Three seeds per run is a viewing sample, not a measurement.

## Done Criteria
- [x] `record_match.py` reproduces known results against the rule fly on this machine. (2026-11-16 19:08)
- [ ] Eight runs recorded on one machine that has the flysim project, all with env version 5.
- [ ] Published copies contain no local path (`grep` for the flysim location and the user folder returns nothing).
- [ ] `published/issues/61.json` written; `npm run build --prefix viewer` lists the eight runs under issue 61.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-16 19:08. The script is written and checked against the rule fly. The neural fly cannot run on the user's machine: the flysim project and `neurons.csv` / `edges.csv` are not there (`FLYTRACKER_NEURAL_SOURCE` unset, nothing found under Documents, Desktop, Downloads). The user decided (2026-11-16) to ask the teammate who owns #31 to merge the flysim code and neural data into the repo, with a per-file redistribution check first (the repo is public); the prompt for their Codex was handed over. This issue waits for that PR.

Next, in order: teammate's PR merged -> merge `origin/main` into this branch -> copy the three model folders (`model.zip` + `config.json`) from the #51 worktree's `runs/g51/` into `runs/` (not in git) -> one `--no-save` neural run to see it works under the laser rule -> record the eight runs here -> strip local paths if any remain -> `publish_run.py --issue 61` -> write `published/issues/61.json` -> viewer build check -> PR.

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

## Management Notes
### Follow-up Candidates
- Viewer: show the neural fly on the issue page's experiment card (`viewer/src/data/experiment.js` reads only `algo.opponent`).
- A measured comparison (200 seeds, gate) of the aimers against the neural fly, if the team wants a number.
### References
- #31 neural fly, #51 SAC under the laser rule, #44 `record_model_v3.py`, #47 `published/issues/<n>.json`, #56 published neural runs without paths.
