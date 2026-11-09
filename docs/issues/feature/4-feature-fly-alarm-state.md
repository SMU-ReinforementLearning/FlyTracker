# 4 초파리 행동을 평시와 비상시로 나누기

## Document Relations
- Issue: #4
- Branch: `4-feature-fly-alarm-state`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #3 (design note that raised the aim-line question)
- Status: in progress

## Summary
Splits the fly's behaviour into two states, normal and alarm, and drops the aim-line trigger because a real fly cannot know where the aimer points. The fly now enters the alarm state only on what it can sense (a fast approach within 1 m, or the aimer closer than 0.35 m), and the free/evade mode switch is removed so every fly can be alarmed.

## Goal
- The fly reacts only to stimuli it could perceive: looming (closing speed / distance) and proximity.
- One fly behaviour for every episode; no `--fly-mode`.
- The alarm state is recorded per frame and shown in the viewer under the glossary terms 평시 / 비상시.

## Scope
- `flytracker/fly.py`: remove `mode`, `FLY_MODES`, `evade_aim_angle_deg` and the aim-line check; `Fly.step` no longer takes the aimer's look direction; `Fly.alarmed` replaces `Fly.evading` and covers the reaction delay plus the escape boost.
- `flytracker/env.py`, `flytracker/record.py`: frame key `evading` → `alarmed`, info key `fly_evading` → `fly_alarmed`, `flyMode` dropped from episode meta and the run index.
- `scripts/`: `--fly-mode` removed; default run names `baseline` and `<algo>`.
- `tests/`: new `test_fly.py`; tests that set `mode="evade"` updated.
- `viewer/`: `alarmed` field (falls back to `evading` for runs recorded before this change), readout 평시 / 비상시, theme token `evade` → `alarm`, run subtitle without the fly mode.
- `README.md`, `ui-text.glossary.md`.

## Out Of Scope
- Retuning the threat thresholds (`evade_radius` 1 m, `evade_looming_rate` 1/s, `evade_proximity` 0.35 m) or the escape (60 ms, ×1.6 for 0.3 s).
- Projectile capture and lead aiming (#3).
- Renaming the `evade_*` parameters; they still describe the escape action.

## Done Criteria
- [x] `uv run pytest` passes, including tests that a still aimer inside 1 m does not alarm the fly and a fast approach or a 0.3 m aimer does. (2026-11-09)
- [x] Baseline capture rate re-measured on seeds 0-39 for the moving and the fixed aimer. (2026-11-09)
- [x] `npm run build --prefix viewer` builds; UI evidence at 1600x900 and 390x844 shows the new readout and run subtitle without overflow. (2026-11-09)

## Current State
- Feature committed: two states, aim-line trigger and free mode removed.
- The fly is now much easier for the moving-aimer baseline: 29/40 (old evade 13/40, old free 28/40).
- The user corrected the aimer model (2026-11-09): a turret at a user-set position that only turns. A turret never approaches the fly, so the approach trigger rarely fires (fixed aimer: 0 alarm onsets in 40 episodes). The user chose to keep this change and re-decide the threat rule after the turret work.
- Before a PR: remove the `AGENTS.md` pointer as the branch's last commit.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 초파리 행동을 평시와 비상시로 나누기 (#4)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/feature/4-feature-fly-alarm-state.md` filled from the user's decision (no aim-line knowledge, two states, free mode removed).
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start` dry run, then the real run: issue #4, branch from `origin/main` @ 46e141e.
#### Notes
- No umbrella issue yet, so `--parent` was not passed.

### feat: 초파리 평시와 비상시 상태 (#4)
> why: a real fly cannot know where the aimer points; the fly should react only to what it can sense, and every fly should be able to react
#### Scope
- `flytracker/fly.py`, `flytracker/env.py`, `flytracker/record.py`, `scripts/_common.py`, `scripts/record_baseline.py`, `scripts/train.py`, `tests/test_fly.py` (new), `tests/test_env.py`, `tests/test_record_and_baseline.py`, `viewer/src/` (episode, labels, Readouts, Sidebar, FlyMarker, both views, theme), `README.md`, `ui-text.glossary.md`, this doc.
#### Changes
- `fly.py`: `mode`, `FLY_MODES`, `evade_aim_angle_deg` and the aim-line check removed; `step(dt, room, aimer_pos)`; `_update_threat` alarms on looming (closing / distance > 1/s within 1 m) or distance < 0.35 m; `alarmed` is true from the perceived threat through the reaction delay and the escape boost.
- `env.py`: snapshot key `alarmed`, info key `fly_alarmed`. `record.py`: frame key `alarmed`; `flyMode` dropped from episode meta and the run index.
- Scripts: `--fly-mode` removed; default run names `baseline` and `<algo>`.
- Tests: `test_fly.py` (still aimer at 0.8 m does not alarm; 1.5 m/s approach alarms and returns to normal; aimer at 0.3 m alarms); `mode="evade"` uses replaced.
- Viewer: `alarmed` per frame with a fallback to `evading` for older runs; readout 초파리 평시 / 비상시; colour token `evade` → `alarm`; run subtitle shows the algorithm only. Glossary: 비상시 / 평시 replaces 회피 중 / 비행 중; fly-mode rows removed.
- README: `--fly-mode` row and example removed; environment table gains a 초파리 row.
#### Verification
- `uv run pytest`: 24 passed (21 before + 3 new). Before the change: 21 passed.
- Baseline capture, `RuleAimer`, seeds 0-39 (scratchpad script, same seeds as #1):

| aimer | old free | old evade | this change |
| --- | --- | --- | --- |
| moving | 28/40 | 13/40 | 29/40 (74 alarm onsets) |
| fixed | 32/40 | 32/40 | 32/40 (0 alarm onsets) |

- `npm run build --prefix viewer`: builds (chunk-size warning only, as before).
- ko-writing `check.py README.md`: sections 1-8 clean.
- UI evidence: `node .claude/skills/ui-evidence/scripts/shot.mjs --base http://localhost:5181 --name after` with the repo overlay (port 5180 was held by another node process, PID 41864, not started here).
  - Commit: 46e141e (dirty, this change) · Chrome: 156.0.8078.74
  - Serve check: `document.title === 'FlyTracker' && /평시|비상시/.test(document.body.innerText)`; the served `runs/index.json` listed only this worktree's `baseline` run.

| page | viewport | file | overflow | probes | console |
| --- | --- | --- | --- | --- | --- |
| / | 1600x900 | `after-1600x900.png` (scratchpad) | none | readouts: 상태 보임 \| 조준 오차 1.4° \| 거리 1.22m \| 포획 진행 0% \| 초파리 평시 \| 프레임 120 / 215; run subtitle: 기준선 | favicon 404, THREE.Clock deprecation, GL ReadPixels perf warnings |
| / | 390x844 (mobile, dpr 2) | `after-390x844.png` (scratchpad) | none | readouts: … 초파리 평시 …; run subtitle: 기준선 | THREE.Clock deprecation only |

  - Desktop: run row shows 기준선 only; readouts show 초파리 평시. Phone: sidebar stacks above the scene, no horizontal overflow.
  - The recorded episodes contain alarm frames (18-54 of 215-469 per episode), so the 비상시 colour path has data.
#### Notes
- Dropping the aim-line trigger made the fly about as easy as the old free mode for the moving baseline; most of the old evade difficulty came from the aim-line trigger.
- Older `runs/` still carry `evading` and `flyMode`; the viewer reads `evading` as a fallback and ignores `flyMode`.

## Management Notes
### Follow-up Candidates
- Tune the threat thresholds so the alarm state matters again for the baseline (e.g. a larger looming radius or a lower looming rate), measured against the 13/40 old-evade figure.
- Projectile capture (#3): pellets are too small and fast to trigger looming, so the alarm state would not react to a shot.
### References
- Design note: `docs/issues/docs/3-docs-aim-point-ballistics/aim-point-and-projectile-speed.md` on branch `3-docs-aim-point-ballistics`.
