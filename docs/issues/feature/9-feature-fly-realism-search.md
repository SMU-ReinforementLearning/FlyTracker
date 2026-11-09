# 9 초파리 비행을 문헌값에 맞추고 조준기 탐색 넣기

## Document Relations
- Issue: #9
- Branch: `9-feature-fly-realism-search`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #4 (fly states), #7 (fixed turret)
- Status: done

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
- Committed and PR opened; the `AGENTS.md` pointer was removed in the branch's last commit.
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

### feat: 초파리 비행을 문헌값에 맞추고 조준기 탐색 넣기 (#9)
> why: the fly moved at a constant 0.5 m/s with uniform 60-120° turns once a second; the user wanted it to fly like a real fruit fly, the turret at the floor centre, and a published search pattern when the baseline loses the fly
#### Scope
- `flytracker/fly.py`, `flytracker/env.py`, `flytracker/baseline.py`, `scripts/_common.py`, `tests/test_env.py`, `tests/test_fly.py`, `tests/test_record_and_baseline.py`, `tests/test_baseline_search.py` (new), this doc.
#### Changes
- `fly.py`: straight segments with power-law length (exponent 1.3, 0.01-2 m) counted only between turns; per-segment speed N(0.285 or 0.356, 0.19) m/s clipped to 0.05-1.0, approached with a 0.1 s time constant; saccades 93 ± 27° (20-180°) over 49 ± 18 ms with a bell-shaped angular-velocity profile; 25% speed dip while turning; 0.8 probability of keeping the previous turn direction; escape turn 25 ms after a 60 ms delay. `FlyParams.hovering()` for tests; `Fly.turning`.
- `env.py`: `turret_pos` default `(0, 0.1, 0)`; the start aim faces -z when the turret is directly under the room centre.
- `baseline.py`: local search (slew to the last-seen direction, then a figure-eight Lissajous 1:2 around it, period 1.6 s, yaw amplitude 15° growing 15° per cycle to 45°) and global search (yaw at 90% of max rate, pitch bands from the floor up spaced by the vertical FOV minus 5° overlap: 10°, 45°, 80°); `reset()` per episode; `scripts/_common.py` calls it.
- Tests: hovering fly via `FlyParams.hovering()`; new search tests.
#### Verification
- `uv run pytest`: 28 passed (26 before + 2 search tests).
- `fly_stats.py` (200 flies × 10 s, no threat): speed 0.273 ± 0.164 m/s; 1.53 saccades/s; 98 ± 31°; 55 ± 18 ms; peak yaw rate median 3,670°/s; inter-saccade distance slope -1.23 over 10-100 mm; same-direction runs mean 3.2. Literature targets in the design note.
- Baseline vs the old spin search, seeds 0-39, turret at the floor centre (scratchpad script): new 40/40, first sight 3.69 s, capture 4.37 s, visible 18%; old 0/40, never saw the fly. 0 alarm onsets in both.
#### Notes
- A first version ordered the bands by the fly's elevation distribution (50°, 80°, 20°; first sight 1.41 s). The user pointed out that this uses simulator knowledge the agent does not have; the bands are now geometry-only.
- The user confirmed the search stays in the baseline only; the environment gives the agent no search help.

### docs: 초파리 비행과 기준선 탐색 근거 문서 (#9)
> why: teammates need to see which fly values come from papers, which are secondary or assumed, and that the baseline search is not part of the environment
#### Scope
- `docs/issues/feature/9-feature-fly-realism-search/fly-flight-and-search-model.md`, `docs/issues/feature/9-feature-fly-realism-search/fly_stats.py`, `README.md`, this doc.
#### Changes
- Design note (Korean): parameter table with source and evidence level (original text / secondary / assumed), model-vs-literature table, baseline search description and comparison, limits, references.
- `fly_stats.py`: measures the fly model's flight statistics.
- README: fly row rewritten, turret default `0 0.1 0`, baseline search sentence that states the environment has no search, link to the note.
#### Verification
- ko-writing `check.py` on the note and README: sections 1-8 clean.
- Every number in the note's model column matches the `fly_stats.py` output above.
#### Notes
- Sources actually read: Reynolds & Frye 2007 (PMC full text) and Muijres et al. 2015 (PDF text). Muijres 2014, Censi 2013 Results and the escape numbers come from secondary sources and are labelled so.

### chore: 작업 마무리와 AGENTS.md 포인터 제거 (#9)
> why: the branch's last commit before the PR; `main` takes PRs only, so the pointer must go now
#### Scope
- `AGENTS.md`, this doc's Status and Current State, the registry row.
#### Changes
- `AGENTS.md` Recent Active Context: pointer line removed, `- (none)` placeholder restored.
- Status: in progress → done, here and in `docs/issues/README.md`.
#### Verification
- `grep -c 9-feature-fly-realism-search AGENTS.md` prints 0.
#### Notes
- The user asked earlier to merge when work is done and show a local preview.

## Management Notes
### Follow-up Candidates
- Threat rule a fly could perceive from a fixed turret.
- Read Muijres 2014 and Censi 2013 full texts to replace the secondary-source values.
- 3-D banked saccades and altitude statistics if a source is found.
### References
- See the design note's reference list.
