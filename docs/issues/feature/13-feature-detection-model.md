# 13 조준기 관측에 초파리 검출 모델 넣기

## Document Relations
- Issue: #13
- Branch: `13-feature-detection-model`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #3 (aim point; may need distance later), #9 (fly flight model, baseline search), #11 (real-size fly model used for the body length)
- Status: paused — design merged; implementation waits for the team meeting

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
- [x] Design note committed with sources and evidence levels. (2026-11-09 22:29)
- [ ] `uv run pytest` passes, with tests for: P = 0.5 at 2 px; empirical detection rate matches the curve; out-of-frame never detected; `perfect=True` reproduces the old in-frame judgement with exact `uv`; same seed gives the same fly path with `perfect` on and off; observation is 12-dim.
- [ ] Baseline on seeds 0-39, `perfect` vs detection model: captures, time to first detection, time to capture, detected-frame ratio recorded in the note.
- [ ] Viewer shows detection state; README observation row updated.

## Current State
- Issue, branch and worktree created from `origin/main` @ 3f3a7e2. The user approved the recommended plan (2026-11-09): 1080 px height, drop distance from the observation, split the work into this issue (model) and a later measurement issue, documentation first.
- Design note committed: `docs/issues/feature/13-feature-detection-model/detection-model.md`, numbers from `detection_curve.py` in the same folder.
- The user decided (2026-11-09) to merge the design note now and to decide the implementation with the team in a meeting. Issue #13 stays open; the PR references it without closing it.
- To resume: after the meeting, run `issue-start --issue 13` to cut a new branch and worktree from `origin/main`, then continue from the open Done Criteria (implementation, baseline comparison, viewer, README). If the team drops or changes the plan, update the design note first.

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

### docs: 초파리 검출 모델 설계 문서 (#13)
> why: the user asked for documentation before implementation; teammates need the model, its starting values and their evidence levels in one place
#### Scope
- `docs/issues/feature/13-feature-detection-model/detection-model.md` (new), `docs/issues/feature/13-feature-detection-model/detection_curve.py` (new), this doc.
#### Changes
- Design note (Korean): environment summary, current judgement, apparent size `s = f × L / z` (1440 × 1080 px, f = 1483.6 px, L = 3.0 mm), detection probability from the TTPF with N50 = 1 cycle = 2 px, centroid error 0.5 px, observation table (13 → 12 dims, `visible` → `detected`, `distance` removed), reward and capture on ground truth, record and viewer, `DetectionParams`, separate RNG, planned baseline comparison, measurement plan for the next issue, limits, references.
- `detection_curve.py`: depth → size → detection probability table, and the fly's distance from the turret over 200 flies × 10 s.
#### Verification
- `detection_curve.py` output: 50% depth 2.23 m; farthest corner 3.47 m; distance median 1.85 m, 90th percentile 2.27 m; 13.7% of time beyond 2.23 m; mean per-frame detection probability 0.668 when aimed at the fly. Every number in the note matches this output.
- Body length 3.01 mm and wingspan 6.11 mm measured from `viewer/public/models/fruitfly.glb` with trimesh.
- ko-writing `check.py` with a glossary and fact ledger: sections 1-11 clean; the remaining section 12 warnings are false positives (angles and counts read as room sizes).
- Three cold-reader reviews by fresh subagents; findings fixed after each. A fourth was not run; the third round's findings were mostly minor.
#### Notes
- Johnson criterion (1.0 cycle) and the TTPF formula were confirmed only from web search summaries, not the original texts; the note labels both "검색 요약". The criterion comes from human observers, so its fit to an automated detector is an assumption.
- Earlier in the conversation the per-distance pixel table used a 2.5 mm body and listed 5.6 m (room diagonal); the note uses 3.0 mm and the real farthest distance from the turret, 3.47 m.

### chore: 설계 문서 merge와 AGENTS.md 포인터 제거 (#13)
> why: the user asked to merge the design note now and decide the implementation with the team; `main` takes PRs only, so the pointer goes in the branch's last commit
#### Scope
- `AGENTS.md`, `docs/issues/README.md`, this doc's Status and Current State.
#### Changes
- `AGENTS.md` Recent Active Context: pointer line removed, `- (none)` restored.
- Status: in progress → paused, here and in the registry row. Issue #13 stays open as the record of the pending implementation.
#### Verification
- `grep -c 13-feature-detection-model AGENTS.md` prints 0.
#### Notes
- The PR body uses `Refs #13`, not `Closes #13`, so the merge does not close the issue.

## Management Notes
### Follow-up Candidates
- Measurement issue: render the turret view at 1440 × 1080 with the real-size fly model, run a rotation-compensated motion detector (and a deep-learning detector as a comparison), fit `n50_cycles` and `noise_px`.
- Baseline: keep tracking for a few frames after a miss, if the comparison shows frequent track/search switching.
### References
- See the design note's reference list.
