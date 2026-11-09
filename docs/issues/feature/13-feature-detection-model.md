# 13 조준기 관측에 초파리 검출 모델 넣기

## Document Relations
- Issue: #13
- Branch: `13-feature-detection-model`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #3 (aim point; may need distance later), #9 (fly flight model, baseline search), #11 (real-size fly model used for the body length)
- Status: in progress

## Summary
Replaces the environment's perfect fly detection with a detection model: each frame the fly is detected with a probability set by its size on screen, and a detected position carries a small pixel error. Today any fly inside the camera frustum is known exactly, although a 3 mm fly is only 1-9 px on a 1080 px image at room distances.

## Goal
- A detection model that needs no rendering: size on screen `s = f × L / z`, detection probability from the TTPF curve with the Johnson detection criterion (N50 = 1 cycle = 2 px), Gaussian centroid error of 0.5 px. All starting values are assumptions to be replaced by a later measurement issue.
- Observation follows the detection model: `visible` renamed to `detected`, `uv` noisy, `distance` removed (13 → 12 dims), `last_seen_dir` and `time_since_seen` from detections.
- Reward and capture stay on ground truth.

## Scope
- Design note (Korean) and `detection_curve.py` under `docs/issues/feature/13-feature-detection-model/`.
- `flytracker/detection.py` (new), `flytracker/env.py` (`DetectionParams` in `EnvConfig`, separate RNG, observation, record key `detected`), `flytracker/baseline.py` (`detected`), tests.
- Viewer: first-person focus box and third-person sight-line colour follow detection; the status readout shows a miss.
- `README.md` observation row.

## Out Of Scope
- Rendering images and running a real detector to measure the detection curve (next issue; motion detector first, deep-learning detector as a comparison candidate).
- False positives, correlated misses, pose and wing size, motion blur, slow-fly misses (listed as limits in the note).
- Any change to fly flight, aimer actions, reward weights or the capture rule.
- Changing the baseline's search logic, unless the comparison shows it breaks; that decision goes back to the user.

## Done Criteria
- [ ] Design note committed with sources and evidence levels.
- [ ] `uv run pytest` passes, with tests for: P = 0.5 at 2 px; empirical detection rate matches the curve; out-of-frame never detected; `perfect=True` reproduces the old in-frame judgement with exact `uv`; same seed gives the same fly path with `perfect` on and off; observation is 12-dim.
- [ ] Baseline on seeds 0-39, `perfect` vs detection model: captures, time to first detection, time to capture, detected-frame ratio recorded in the note.
- [ ] Viewer shows detection state; README observation row updated.

## Current State
- Issue, branch and worktree created from `origin/main` @ 3f3a7e2. The user approved the recommended plan (2026-11-09): 1080 px height, drop distance from the observation, split the work into this issue (model) and a later measurement issue, documentation first.
- Next: user review of the design note, then implementation.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 조준기 관측에 초파리 검출 모델 넣기 (#13)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/feature/13-feature-detection-model.md` filled from the conversation: the environment treats in-frame flies as perfectly detected; the user asked whether edge detection applies, accepted the recommended detection model, and asked for documentation first.
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start`: issue #13, branch from `origin/main` @ 3f3a7e2.
#### Notes
- No umbrella issue yet, so `--parent` was not passed.
- The measurement issue is not opened yet; it is listed under Follow-up Candidates and will be opened when this one is done.

## Management Notes
### Follow-up Candidates
- Measurement issue: render the turret view at 1440 × 1080 with the real-size fly model, run a rotation-compensated motion detector (and a deep-learning detector as a comparison), fit `n50_cycles` and `noise_px`.
- Baseline: keep tracking for a few frames after a miss, if the comparison shows frequent track/search switching.
### References
- See the design note's reference list.
