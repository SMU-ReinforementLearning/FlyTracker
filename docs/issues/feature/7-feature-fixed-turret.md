# 7 조준기를 위치가 고정된 포대로 바꾸기

## Document Relations
- Issue: #7
- Branch: `7-feature-fixed-turret`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #1 (built the flying aimer), #3 (projectile note), #4 (fly threat rule)
- Status: in progress

## Summary
Turns the aimer into what the user meant from the start: a turret at a user-set position that only turns its aim, like an anti-aircraft gun. Issue #1 had built a camera that flies around the room; the move axes, the moving-aimer option, the position and velocity observations, and the distance and collision rewards are removed.

## Goal
- The aimer never changes position; the agent controls yaw and pitch rates only.
- The position is one configured value (`EnvConfig.turret_pos`, `--turret-pos`), default `(0, 1.2, 1.4)`: centred in front of the +z wall at 1.2 m, facing into the room.
- Capture has no distance condition by default (a turret cannot close the distance); `--capture-range` can add one.

## Scope
- `flytracker/aimer.py`: 2-D action (`yaw_rate`, `pitch_rate`); `AimerLimits` keeps the angular limits only; `Aimer.step(action, dt)`; no velocity, no wall clamp.
- `flytracker/env.py`: `turret_pos` (checked to be inside the room, list → tuple in `from_dict`); `capture_range: float | None = None`; the fly is placed at least 1.5 m from the turret; the start aim faces the room centre horizontally unless `start_facing_fly`; observation 19-D → 13-D (`closeness` → `distance` / room diagonal; `position`, `velocity` removed); reward drops the distance and collision terms; `collided` removed from info and snapshot.
- `flytracker/wrappers.py`: 5 discrete actions (idle, yaw left/right, pitch up/down).
- `flytracker/baseline.py`: rotate-only rule aimer.
- `flytracker/record.py`: `collided` frame key removed.
- `flytracker/fly.py`: docstring only (with a turret, the distance shrinks only when the fly flies toward it).
- `scripts/`: `--fixed-aimer` removed, `--turret-pos X Y Z` added, `--capture-range` defaults to none; stale "파리 모드" help text in `train.py` fixed.
- `tests/`: `test_aimer.py` rewritten; `test_env.py` updated plus turret-position, out-of-room and no-distance-capture tests.
- `viewer/src/scene/ThirdPersonView.jsx`: frustum depth falls back to 0.8 m when `captureRange` is null.
- `README.md`.

## Out Of Scope
- The fly's threat rule for a turret (the user deferred it until after this change).
- Difficulty: the rule baseline now captures every episode (see Current State).
- Projectile capture (#3).

## Done Criteria
- [x] `uv run pytest` passes, including tests that the turret never moves and stays at the configured position. (2026-11-09)
- [x] Baseline capture rate measured on seeds 0-39 at the default turret position. (2026-11-09)
- [x] `scripts/train.py` finishes short SAC and DQN runs with the new action and observation spaces. (2026-11-09)
- [x] `npm run build --prefix viewer` builds; UI evidence shows the turret at its position without overflow. (2026-11-09)

## Current State
- Change complete in the worktree.
- The task became easy for the rule baseline: 40/40 captures, mean 1.92 s to capture, capture distance 0.71-2.62 m, no alarm onsets. A fixed turret with no distance condition only needs to keep a 0.5 m/s fly inside 3 deg for 0.2 s. How to make it harder (capture by projectile per #3, longer hold, narrower FOV, faster or evasive fly, a turret-appropriate threat rule) is the user's next decision.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 조준기를 위치가 고정된 포대로 바꾸기 (#7)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/feature/7-feature-fixed-turret.md` filled from the user's correction (aimer = fixed turret like an AA gun; flying code removed; position as one configured value).
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start`: issue #7, branch from `origin/main` @ ce79745.
#### Notes
- No umbrella issue yet, so `--parent` was not passed.

## Management Notes
### Follow-up Candidates
- Difficulty for the turret task (see Current State).
- Fly threat rule for a turret: what a fly can sense from a fixed turret (its turning motion, a shot's sound or air flow).
- #3's 1 m range assumption against the default turret position (the farthest corner is about 3.7 m away).
### References
- User correction, 2026-11-09: "방공포는 고정된 위치에서 조준을 움직일 뿐이지 날아다니지 않아."
