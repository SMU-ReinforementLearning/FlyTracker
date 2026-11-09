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
- Code, tests, viewer, README and glossary changed in the worktree; awaiting the user's review before the feature commit.
- The fly is now much easier for the baseline: moving aimer 29/40 (old evade 13/40, old free 28/40). Threshold tuning is a follow-up decision for the user.
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

## Management Notes
### Follow-up Candidates
- Tune the threat thresholds so the alarm state matters again for the baseline (e.g. a larger looming radius or a lower looming rate), measured against the 13/40 old-evade figure.
- Projectile capture (#3): pellets are too small and fast to trigger looming, so the alarm state would not react to a shot.
### References
- Design note: `docs/issues/docs/3-docs-aim-point-ballistics/aim-point-and-projectile-speed.md` on branch `3-docs-aim-point-ballistics`.
