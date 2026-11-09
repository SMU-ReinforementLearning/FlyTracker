# 9 초파리 비행을 문헌값에 맞추고 조준기 탐색 넣기

## Document Relations
- Issue: #9
- Branch: `9-feature-fly-realism-search`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #4 (fly states), #7 (fixed turret)
- Status: in progress

## Summary
Makes the fly move like a real fruit fly using published free-flight measurements, moves the turret to the floor centre, and gives the rule-based baseline a search pattern for when it has lost the fly. The search lives only in the baseline; the environment's observation, reward and action are unchanged, so the RL agent still has to learn its own search.

## Goal
- Fly flight statistics (speed, saccade angle and duration, inter-saccade distance, turn persistence) close to literature values, each value tagged with its source and evidence level.
- Turret default at the floor centre, `(0, 0.1, 0)`.
- Baseline search from published patterns: a datum-centred, growing figure-eight (Lissajous 1:2; IAMSAR expanding-square / sector idea) and a 360° band sweep (Koopman parallel search), using only observations and camera geometry.

## Scope
- `flytracker/fly.py`, `flytracker/env.py` (turret default, start yaw at the room centre), `flytracker/baseline.py`, `scripts/_common.py` (help text, `policy.reset()`), tests, `README.md`.
- Design note and stats script under `docs/issues/feature/9-feature-fly-realism-search/`.

## Out Of Scope
- The fly's threat rule for a fixed turret (still deferred; 0 alarm onsets in the baseline run).
- Any change to the environment's observation, reward or action; any search help for the RL agent (the user decided search must be learned).
- Reading the paywalled or blocked full texts (Muijres 2014, Tammero & Dickinson 2002, Censi 2013 Results).

## Done Criteria
- [x] `fly_stats.py` shows the model near the literature values it cites. (2026-11-09)
- [x] `uv run pytest` passes, including search tests (sweep covers every band; figure-eight reacquires a fly pushed 55° out of view without falling back to the sweep). (2026-11-09)
- [x] Baseline compared with the old spin search on seeds 0-39 at the new turret position. (2026-11-09)

## Current State
- Code, tests, README and design note done in the worktree.
- The user decided (2026-11-09) that the search stays in the baseline only, and that band order must not use the simulator's knowledge of where flies are (geometry-only bands 10°, 45°, 80°).

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 초파리 비행을 문헌값에 맞추고 조준기 탐색 넣기 (#9)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/feature/9-feature-fly-realism-search.md` filled from the user's requests (realistic fly from papers; turret at floor centre; search pattern from papers when the fly is lost).
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start`: issue #9, branch from `origin/main` @ a43d1d8.
#### Notes
- No umbrella issue yet, so `--parent` was not passed.

## Management Notes
### Follow-up Candidates
- Threat rule a fly could perceive from a fixed turret.
- Read Muijres 2014 and Censi 2013 full texts to replace the secondary-source values.
- 3-D banked saccades and altitude statistics if a source is found.
### References
- See the design note's reference list.
