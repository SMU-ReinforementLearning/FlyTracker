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
- [x] `uv run pytest` passes (camera projection, aimer kinematics, env checker, recording, baseline) (2026-11-04 10:52)
- [x] `scripts/record_baseline.py` writes episodes under `runs/` with `index.json` and a per-run manifest (2026-11-04 10:52)
- [x] `scripts/train.py` finishes a short SAC and DQN smoke run and records evaluation episodes (2026-11-04 10:52)
- [ ] The viewer lists runs and episodes and replays one episode in both views, with the recorded `uv` point over the first-person view
- [ ] Viewer design follows `ui-text.config.md` (Apple style, no filler subtitles or captions); screenshots as evidence

## Current State
- Python side is complete for this issue (environment, baseline, recording, training script, tests, README).
- Baseline capture rate, 40 episodes each, seeds 0-39: moving aimer free 28/40, evade 13/40; fixed aimer (aim-only capture) 32/40 in both modes, because the fly reacts only within 1 m and a fixed aimer captures from farther.
- Next: the React viewer under `viewer/`, reading `runs/` from the Vite dev server.

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

### feat: 조준기 추적 환경, 기준선, 학습 스크립트 (#1)
> why: the Python half of the skeleton — everything the viewer will replay comes from here
#### Scope
- `flytracker/` package, `scripts/`, `tests/`, `pyproject.toml` + `uv.lock`, README run instructions.
#### Changes
- `world.py`, `geometry.py`, `camera.py`: room box in the RackTracker convention, look direction from yaw/pitch (yaw 0 looks along -z like a three.js camera), pinhole projection to NDC-style `uv`, plus `K`, OpenCV `R, t` and pixel projection.
- `aimer.py`: 5-D action, velocity and angular-rate targets followed under acceleration limits, wall clamp reports collision, `can_move=False` for a turret.
- `fly.py`: free flight with random saccades and wall avoidance; evade mode reacts (after 60 ms) when the aim line points within 10 deg, when looming rate exceeds 1/s, or when closer than 0.35 m.
- `env.py`: `FlyChaseEnv`, 19-D observation (`OBS` slices), shaped reward with all tracking terms negative so delaying capture never pays, capture = 3 deg / 0.5 m held 0.2 s, `snapshot()` for recording only.
- `wrappers.py`: `DiscreteActions` (11 one-axis actions), `make_env` with optional frame stack.
- `record.py`: `EpisodeRecorder` wrapper (columnar frames per agent step), `RunStore` writing `runs/index.json`, `<run>/config.json`, `<run>/episodes.json`; atomic writes with a retry for Windows file locks.
- `baseline.py`: `RuleAimer` working from observations only.
- `scripts/record_baseline.py`, `scripts/train.py` (SB3 SAC/TD3/PPO/DQN, evaluation episodes with fixed seeds at start, every N steps and at the end, checkpoints, TensorBoard when installed).
#### Verification
- `uv run pytest`: 21 passed.
- Baseline, 40 episodes per row: moving free 28/40, moving evade 13/40, fixed free 32/40, fixed evade 32/40.
- `train.py --algo sac --steps 3000` and `--algo dqn --steps 3000 --fly-mode evade`: both finish and save 3 evaluation sets of 2 episodes plus checkpoints; no captures, as expected for 3k steps.
#### Notes
- Fly flight parameters (0.5 m/s, 60-120 deg saccades in 50 ms) are starting values, not checked against literature.

## Management Notes
### Follow-up Candidates
- Episode comparison mode in the viewer.
- Image observations through `P = K[R|t]`.
- Per-member umbrella issues once teammates join.
### References
- RackTracker world convention: `rack-tracker-forked/docs/etc/rig-server/rack-anchor-design.md` §0 (sibling repo).
- RackTracker frustum drawing: `rack-tracker-forked/frontend/src/method/scene/CameraRig.js` (sibling repo).
