# 1 강화학습 환경과 에피소드 viewer 뼈대

## Document Relations
- Issue: #1
- Branch: `1-feature-env-viewer-skeleton`
- Umbrella: (none) — no umbrella issue exists yet
- Status: in progress

## Summary
Builds the first runnable skeleton of the project: a Gymnasium environment in which a limited-FOV aimer chases a fruit fly inside a room, a rule-based baseline aimer, episode recording under `runs/`, a Stable-Baselines3 training script, and a React viewer that replays recorded episodes in third person and from the aimer's own camera.

## Goal
- One source of truth for simulation in Python; the viewer only draws what Python recorded (no game rules in JavaScript).
- World convention borrowed from RackTracker: x right, y up, z front, right-handed, metres, origin at the floor centre. three.js uses the same axes, so positions pass through unchanged.
- The aimer is a pinhole camera (position, look direction, vertical FOV, aspect). Visibility is the projection falling inside the image; `P = K[R|t]` is available for image observations later.
- Continuous 5-D action (forward, right, up, yaw rate, pitch rate) with a discrete 11-action wrapper so DQN and SAC run on the same environment.
- The agent observes only what its camera sees plus its own state; the third-person view is for people.

## Scope
- Python package `flytracker/`: room, camera model, aimer kinematics, fly behaviour (free / evade), environment, wrappers, recorder and run store, rule-based baseline.
- `scripts/record_baseline.py`, `scripts/train.py` (SAC, TD3, PPO, DQN; periodic evaluation episodes saved per checkpoint).
- Tests under `tests/`.
- `viewer/`: Vite + React + React Three Fiber; run list, episode list, third-person and first-person views, timeline, per-episode charts. Serves `runs/` from the dev server, no backend.
- README section on how to run each part.

## Out Of Scope
- Reward and difficulty tuning beyond sane defaults (the user deferred details).
- Image observations, MuJoCo, live streaming over WebSocket, starting training from the viewer.
- Episode comparison mode in the viewer (planned, not in this skeleton).

## Done Criteria
- [ ] `uv run pytest` passes (camera projection, aimer kinematics, env checker, recording, baseline)
- [ ] `scripts/record_baseline.py` writes episodes under `runs/` with `index.json` and a per-run manifest
- [ ] `scripts/train.py` finishes a short SAC and DQN smoke run and records evaluation episodes
- [ ] The viewer lists runs and episodes and replays one episode in both views, with the recorded `uv` point over the first-person view
- [ ] Viewer design follows `ui-text.config.md` (Apple style, no filler subtitles or captions); screenshots as evidence

## Current State
- Python skeleton was drafted in the main checkout before the kit was installed and moved here untracked; 21 tests passed there. Not yet committed.
- Baseline capture rate (40 episodes, moving aimer): free 28/40, evade 29/40 — the evade trigger is still too weak; next step is to add an aim-based trigger.
- Viewer not started.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 강화학습 환경과 에피소드 viewer 뼈대 (#1)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/feature/1-feature-env-viewer-skeleton.md` filled from the design discussion.
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start` dry run, then the real run: issue #1, branch from `origin/main` @ 52f6632.
#### Notes
- No umbrella issue yet, so `--parent` was not passed.

## Management Notes
### Follow-up Candidates
- Episode comparison mode in the viewer.
- Image observations through `P = K[R|t]`.
- Per-member umbrella issues once teammates join.
### References
- RackTracker world convention: `rack-tracker-forked/docs/etc/rig-server/rack-anchor-design.md` §0 (sibling repo).
- RackTracker frustum drawing: `rack-tracker-forked/frontend/src/method/scene/CameraRig.js` (sibling repo).
