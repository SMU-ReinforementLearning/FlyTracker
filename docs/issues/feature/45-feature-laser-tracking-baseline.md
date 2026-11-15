# 45 레이저 포획 조건에서 통하는 조준기 기준선 만들기

## Document Relations
- Issue: #45
- Branch: `45-feature-laser-tracking-baseline`
- Umbrella: (none)
- Status: in progress

## Summary
Make an aimer that works under the laser capture rule of env version 3 (fly centre within 1.25 mm of the beam for 0.15 s): a rule baseline with velocity feed-forward tracking, the observation it needs, no blind cone above the turret, and a zoomed aimer view in the viewer. Under version 3 the current rule baseline catches 5/200 and the six #35 SAC models 1/1200 (seeds 10000-10199, measured in #42).

## Goal
- A rule baseline that captures under version 3 from the aimer observation alone, so that later learned aimers have a working reference and a tracker to build on.
- An observation in which the last 0.1° is visible to a policy: the fly's angular velocity and a fine (zoomed) aim error.
- The beam can reach every direction in the upper hemisphere, including straight up.
- A person watching an episode can see whether the beam is on the fly: a zoomed aimer view.

## Scope
1. Pitch limit 89° → 90°. `camera_basis` takes its right axis from `cross(forward, UP)`, which is zero at 90°; the right axis has to come from yaw instead so the camera frame stays defined and continuous.
2. Aimer observation gains the fly's angular velocity seen from the turret (ground truth, same assumption as the exact screen position today) and a fine aim error that magnifies the centre. `ENV_VERSION` 3 → 4.
3. Rule baseline: keep the search, replace the P-only tracking law by `rate command = fly angular rate + kp * angle error`. Feasibility was shown in #42's scratch script (200/200, mean 4.96 s, kp 25 /s, angular rate from finite differences).
4. Viewer: a zoomed aimer view around the beam, readable at the 1.25 mm scale. Recording format gains what that view needs, if anything.
5. Docs: README sections that state the observation, the pitch limit, the baseline and its numbers; a dated note on #13's design doc that latency compensation and prediction (the anti-aircraft "predicted impact point" reduced to system latency for a laser) belong to the detection-tracking pipeline, and that the ground-truth angular velocity becomes an estimate there.
6. Published baseline runs under version 4 so the deployed viewer shows them.

## Out Of Scope
- Reward redesign (log-scale beam distance) and SAC retraining: next issue, with a pre-registered gate.
- System latency, detection noise, velocity estimation from noisy detections: #13.
- The #31 neural demo specs and the fly side.
- #44 (publishing learned-aimer episodes under version 3) runs in another worktree; this branch does not touch its runs.

## Done Criteria
- [x] Pitch reaches 90°; a test shows a fly straight above the turret is captured, and the camera frame is continuous through 90°. (2026-11-15)
- [x] Observation has the fly's angular velocity and the fine aim error; `ENV_VERSION` is 4 and loaders refuse version-3 models; tests cover both new entries. (2026-11-15; the refusal is the existing `load_opponent` version check, covered by `tests/test_players.py`)
- [x] New rule baseline captures at least 190/200 on seeds 10000-10199 against the rule fly, using the observation only. The number, mean time over captures and the failed seeds are reported as measured. (2026-11-15: 200/200, 4.95 s, no failed seed)
- [x] Viewer shows the zoomed aimer view; ui-evidence captures at 1600x900 and 390x844 with no overflow; older recordings still render. (2026-11-15)
- [x] `uv run python -m pytest -q` and `npm run build --prefix viewer` pass. (2026-11-15: 112 passed, 45 skipped)
- [x] README and the #13 note updated; Korean text checked with ko-writing `check.py`. (2026-11-15)
- [x] Version-4 baseline runs published and listed in `viewer/dist/runs/index.json`. (2026-11-15)

## Current State
2026-11-15: all scope items are implemented in the working tree and verified; commits wait for the user's approval (review gate). Planned commits: seed, env version 4 with the new baseline, viewer, published runs, README and #13 note, then the `AGENTS.md` pointer removal before the PR.

Measured under version 4, seeds 10000-10199, rule fly: baseline 200/200, mean 4.95 s over captures, visible 30 %, mean return −19.95 (version 3 baseline: 5/200). One episode (seed 10027) reaches pitch 90°. Per-seed numbers come from `runs/_ops/eval_v4.py` (local, gitignored).

Design choices made here: the fly's angular rate is a finite difference of the true direction over one physics step, given in action units and only while visible; `uv_fine` is the angular offset divided by `fine_error_deg` (0.5°); the zoomed view is a second 3D camera with a 0.5° vertical field (80x) in its own card under the aimer view, not a schematic; recordings gain `aimerAngles` because `aimerLook` loses yaw when looking straight up.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 레이저 포획 조건에서 통하는 조준기 기준선 만들기 (#45)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
`docs/issues/feature/45-feature-laser-tracking-baseline.md`, `docs/issues/README.md`, `AGENTS.md`.
#### Changes
- Management doc filled (summary, goal, scope, out of scope, done criteria), registry row and `AGENTS.md` pointer added by `issue-start`.
#### Verification
- `issue-start` dry run, then the real run: issue #45, branch from `origin/main` @ 7a81d0a.
#### Notes
- Open issue #44 (`44-chore-sac-v3-episodes`, another worktree) is unrelated work on version-3 episodes.

## Management Notes
### Follow-up Candidates
- Reward that has a gradient below 0.1° (log-scale beam distance) and SAC retraining under version 4, possibly as a residual policy on top of the feed-forward tracker; fallback: learned search + rule tracking (191/200, 3.24 s in the #42 scratch run).
### References
- `docs/issues/feature/42-feature-laser-hit-capture.md` and its design note `42-feature-laser-hit-capture/laser-capture-condition.md`.
