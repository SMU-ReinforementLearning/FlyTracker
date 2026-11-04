# 1 강화학습 환경과 에피소드 viewer 뼈대

## Document Relations
- Issue: #1
- Branch: `1-feature-env-viewer-skeleton`
- Umbrella: (none) — no umbrella issue exists yet
- Status: done

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
- [x] The viewer lists runs and episodes and replays one episode in both views, with the recorded `uv` point over the first-person view (2026-11-04 11:08)
- [x] Viewer design follows `ui-text.config.md` (Apple style, no filler subtitles or captions); screenshots as evidence (2026-11-04 11:08)

## Current State
- Python side and the viewer are both in place; every Done Criteria item is ticked.
- Baseline capture rate, 40 episodes each, seeds 0-39: moving aimer free 28/40, evade 13/40; fixed aimer (aim-only capture) 32/40 in both modes, because the fly reacts only within 1 m and a fixed aimer captures from farther.
- Next: user review of the viewer commit, then the `AGENTS.md` pointer removal as the branch's last commit before the PR.

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

### feat: 에피소드 viewer (#1)
> why: the second half of the skeleton — replay what Python recorded, in both views, with no game rules in JavaScript
#### Scope
- `viewer/` (Vite 8, React 19, React Three Fiber 9, drei 10, three 0.187), `ui-evidence.config.json`, `ui-text.glossary.md`, README viewer section, `.gitignore`.
#### Changes
- `vite.config.js`: dev-server middleware serves `../runs` at `/runs` (JSON only), port 5180; no backend.
- `src/data/`: `api.js` fetches `runs/index.json`, `<run>/episodes.json` and episode files; `episode.js` turns columnar frames into typed arrays, cumulative return and `sample(ep, t)` interpolation; `labels.js` maps codes to the glossary wording.
- `src/playback/clock.js`: module-level playback clock driven by rAF; `useClock(hz)` re-renders text at 15-20 Hz, scene objects read the clock inside `useFrame`.
- `src/scene/`: `Room` (wireframe box, floor grid, axes), `FlyMarker` (point + trail, evade colour), `AimerRig` (body, frustum drawn to the capture range, aim line clipped at the room wall), `ThirdPersonView` (OrbitControls), `FirstPersonView` (camera follows the recorded pose; the recorded `uv` is drawn as a focus square over the 3D fly; capture ring sized from `capture_angle_deg`), `FrameCounter` (`window.__frames` for screenshot readiness).
- `src/components/`: `Sidebar` (runs, episodes grouped by tag), `Transport` (play/pause, frame step, scrubber, speed), `Readouts` (state, aim error, distance, capture progress, fly state, frame), `LineChart` (single series, crosshair tooltip, click to seek, keyboard).
- `styles.css`: Apple-style tokens for light and dark, Pretendard; stacked layout under 1080 px and 760 px.
- Keyboard: space toggles playback, arrow keys step one frame.
#### Verification
- `npm run build --prefix viewer`: builds; one 1.17 MB chunk (three.js), size warning only.
- `uv run pytest`: 21 passed (Python unchanged, re-run).
- ko-writing `check.py README.md`: nothing in sections 1-8.
- dataviz `validate_palette.js`: light `#0071e3,#eb6834,#1baf7a` on `#f5f5f7` PASS with a contrast WARN relieved by the `Readouts` text; dark `#3987e5,#d95926,#199e70` on `#1c1c1e` PASS.
- UI evidence: `node .claude/skills/ui-evidence/scripts/shot.mjs --name after` with `ui-evidence.config.json`.
  - Commit: dd84acc (dirty, this change) · Chrome: 156.0.8078.74
  - Ready: `window.__frames > 10 && document.fonts.status === 'loaded'`, settle 800 ms, reduced motion on, SwiftShader flags

| page | viewport | file | overflow | probes | console |
| --- | --- | --- | --- | --- | --- |
| / | 1600x900 | `.ui-evidence/after-1600x900.png` | none | body font "Pretendard Variable"; canvases 2; title baseline-evade | 1 error (favicon 404), THREE.Clock deprecation warning from R3F |
| / | 390x844 (mobile, dpr 2) | `.ui-evidence/after-390x844.png` | none | same | 0 errors, THREE.Clock warning |

  - Desktop: sidebar with four runs and five baseline episodes; third-person room with aimer frustum, aim line and fly trail; first-person view with the recorded focus square sitting on the 3D fly; readouts; transport; two charts. Dark scheme (headless default).
  - Phone: sidebar stacks on top at 40vh and scrolls, then the toolbar and the scene; no horizontal overflow.
  - Captures stay in `.ui-evidence/` (ignored); the table is the durable record.
#### Notes
- The first capture showed the aim line running 6 m past the room; it is now clipped at the wall (`distanceToWall`).
- Vite binds `localhost` only, so the evidence config uses `http://localhost:5180` rather than `127.0.0.1`.
- The favicon 404 is a missing icon, left for a later issue.

### chore: 작업 마무리와 AGENTS.md 포인터 제거 (#1)
> why: the branch's last commit before the PR; `main` takes PRs only, so the pointer must go now
#### Scope
- `AGENTS.md`, this doc's Status, the registry row.
#### Changes
- `AGENTS.md` Recent Active Context: pointer line removed, `- (none)` placeholder restored.
- Status: in progress → done, here and in `docs/issues/README.md`.
#### Verification
- `grep -c 1-feature-env-viewer-skeleton AGENTS.md` prints 0.
#### Notes
- The user confirmed the scene holds one fly and one aimer, so no second-aimer issue follows from this one.

## Management Notes
### Follow-up Candidates
- Episode comparison mode in the viewer.
- Image observations through `P = K[R|t]`.
- Per-member umbrella issues once teammates join.
### References
- RackTracker world convention: `rack-tracker-forked/docs/etc/rig-server/rack-anchor-design.md` §0 (sibling repo).
- RackTracker frustum drawing: `rack-tracker-forked/frontend/src/method/scene/CameraRig.js` (sibling repo).
