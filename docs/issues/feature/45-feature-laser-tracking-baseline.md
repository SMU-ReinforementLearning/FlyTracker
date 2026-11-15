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

### feat: 환경 버전 4와 속도 맞춤 기준선 (#45)
> why: under the laser capture rule the P-only baseline lags a moving fly and catches 5/200; the fix needs the fly's angular rate in the observation, and the 1° blind cone above the turret had no reason to stay
#### Scope
`flytracker/geometry.py`, `camera.py`, `aimer.py`, `env.py`, `baseline.py`, `record.py`, `free_flight.py`, `tests/test_env.py`.
#### Changes
- `geometry.aim_basis(yaw, pitch)`: camera axes with the right axis taken from yaw, defined at pitch ±90°. `Aimer.basis` uses it; `project` takes an optional `basis`; the env passes it everywhere it projected with `look` alone.
- `AimerLimits.max_pitch_deg` 89 → 90.
- Observation 13 → 17: `target_rate` (fly direction's yaw/pitch rate over the last physics step, in action units, only while visible) and `uv_fine` (angular offset from the centre / `fine_error_deg` 0.5°). `ENV_VERSION` 4.
- `RuleAimer`: tracking law is `target_rate + track_gain * angle error` (`track_gain` 25 /s replaces `turn_gain`); search unchanged.
- Recording: frame key `aimerAngles` (yaw, pitch in rad); free-flight writes a placeholder.
#### Verification
- `uv run python -m pytest -q`: 112 passed, 45 skipped (skips need the local neural source). New tests: fly straight above is captured at pitch 90°; screen coordinates continuous between 89.9° and 90°; `target_rate` and `uv_fine` values for a known offset and motion, zero when not visible; baseline captures at least 4 of seeds 0-4.
- `runs/_ops/eval_v4.py` (local), seeds 10000-10199, rule fly: 200/200, mean 4.95 s, no failed seed; one episode (seed 10027) reaches pitch 90°. `scripts/record_baseline.py --episodes 200 --seed 10000 --no-save`: 200/200, mean return −19.95, visible 30 %, 4.95 s.
#### Notes
- Near straight up the fly direction's yaw rate grows without bound; `target_rate` clips at ±1 and the turret's yaw rate limit applies. No failed seed came from this in the 200.

### feat: viewer에 확대 화면 넣기 (#45)
> why: a 2.5 mm beam is smaller than a pixel in the 40° aimer view, so a viewer cannot see whether the beam is on the fly
#### Scope
`viewer/src/scene/FirstPersonView.jsx` + `.module.css`, `AimerRig.jsx`, `viewer/src/App.jsx`, `viewer/src/data/episode.js`, `labels.js`, `ui-text.glossary.md`, captures.
#### Changes
- `ZoomView`: a second 3D camera on the aimer with a 0.5° vertical field (80x), in its own 2:1 card under the aimer view. A circle shows the beam's extent at the fly's distance and turns green while hitting. Shown for recordings with `captureRadius` (version 3 and later).
- The aimer camera and the third-person rig use `aimerAngles` when present (yaw is lost in `aimerLook` when looking straight up); older recordings use `lookAt` as before.
- Glossary: "확대 화면".
#### Verification
- `npm run build --prefix viewer` passes.
- ui-evidence, dev server from this worktree on port 5185 (`--strictPort`), working tree on 7a81d0a, Chrome 157.0.8103.52, each page sought to its last frame by the ready expression, settle 800 ms, reduced motion on. Files in `45-feature-laser-tracking-baseline/captures/`.

| page | viewport | file | overflow | probes |
| --- | --- | --- | --- | --- |
| version-4 episode (seed 10000) | 1600x900 | `v4-1600x900.png` | none | 3 canvases, zoom label 80배, beam circle 20.1 % of height |
| version-4 episode | 390x844 (mobile, dpr 2) | `v4-390x844.png` | none | same |
| version-3 episode (seed 10116) | 1600x900 | `v3-1600x900.png` | none | 3 canvases, zoom label 80배 |
| version-3 episode | 390x844 (mobile, dpr 2) | `v3-390x844.png` | none | same |
| version-2 episode | 1600x900 | `v2-1600x900.png` | none | 2 canvases, no zoom view |
| version-2 episode | 390x844 (mobile, dpr 2) | `v2-390x844.png` | none | same |

- Looked at `v4-1600x900.png`: the fly model sits inside the green beam circle; the inspector column fits without scrolling.
#### Notes
- First attempt put the zoom view as an inset inside the aimer view (34 % wide, 1° field); the fly was about 8 px, so it moved to its own card with a 0.5° field.
- The phone captures show only the top of the page, so the zoom view itself is not in them; they establish no horizontal overflow.

## Management Notes
### Follow-up Candidates
- Reward that has a gradient below 0.1° (log-scale beam distance) and SAC retraining under version 4, possibly as a residual policy on top of the feed-forward tracker; fallback: learned search + rule tracking (191/200, 3.24 s in the #42 scratch run).
### References
- `docs/issues/feature/42-feature-laser-hit-capture.md` and its design note `42-feature-laser-hit-capture/laser-capture-condition.md`.
