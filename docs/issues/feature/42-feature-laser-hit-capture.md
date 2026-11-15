# 42 포획 조건을 레이저 명중으로 바꾸기

## Document Relations
- Issue: #42
- Branch: `42-feature-laser-hit-capture`
- Umbrella: (none)
- Status: in progress

## Summary
Capture changes from "fly within 3° of the aim direction for 0.2 s" to "laser beam on the fly's body centre for the lethal exposure time". The team decided (2026-11-15, user) to catch the fly with a laser, so the aim line is the beam itself and a 3° cone (about 10 cm radius at 2 m) no longer means a hit.

## Goal
Make the capture condition match a laser hit, with values taken from published in-flight laser insect control work, and re-measure the existing aimers under the new condition.

## Scope
- `flytracker/env.py`: capture = perpendicular distance from the fly centre to the beam ≤ capture radius, held for `capture_hold`. The beam leaves the turret forward only (same geometry the fly observation already uses for `laser_dist`).
  - capture radius 1.25 mm (beam diameter 2.5 mm), replaces `capture_angle_deg`.
  - `capture_hold` 0.15 s: the time a 500 mW beam (top of Class 3B, chosen for indoor use) needs to deliver the published lethal energy of 74 mJ. Stays a config value.
  - `ENV_VERSION` 2 → 3.
- Everything that reads the old condition: recording meta (`captureAngleDeg`), viewer display of the capture angle, CLI flags, fly observation comment, tests.
- Design note for teammates (Korean) next to this doc: `42-feature-laser-hit-capture/laser-capture-condition.md` with the evidence, the power choice and the safety limits.
- `docs/issues/docs/3-docs-aim-point-ballistics/aim-point-and-projectile-speed.md`: it excludes the laser (fire, eye damage) and keeps salt grains as the projectile. Record the new decision there first, then the dependent docs.
- README: episode, R, fly state sections, recording format, CLI table.
- Re-measure under env version 3: rule baseline and the adopted #35 SAC checkpoint, seeds 10000–10199 via `match.py`.

## Out Of Scope
- Reward redesign or a radius curriculum. The aim-error penalty is normalised by half the FOV (20°), so it is nearly flat below 0.1°; whether that blocks learning is measured here and handled in a follow-up issue.
- Retraining SAC under the new condition.
- Detection noise (#13) and the neural fly model's own behaviour (#31).
- Real hardware laser safety.

## Done Criteria
- [x] Capture is decided by distance to the beam (1.25 mm) and hold time (0.15 s); the 3° angle condition is gone from code, recordings, viewer and README. (2026-11-15) The viewer keeps the ring for version-2 recordings, and the README names the old rule once as history.
- [x] `ENV_VERSION` is 3 with a version-table line. (2026-11-15)
- [x] Tests cover: on-beam for 15 physics steps captures; 14 steps does not; 1.3 mm off does not; a fly behind the turret does not; full test suite passes. (2026-11-15)
- [x] The design note records evidence, power choice and safety limits; #3 doc states the laser decision and its date. (2026-11-15)
- [x] Baseline and #35 SAC capture counts on 200 seeds under version 3 are reported in this doc, whatever they are. (2026-11-15) Baseline 5/200, SAC 1/1200.
- [x] Viewer shows the new condition; screenshot evidence at desktop and 390px. (2026-11-15)

## Current State
2026-11-15. Committed: seed, design note + #3 note, capture change with tests, viewer, two published version-3 baseline runs. Values: radius 1.25 mm, hold 0.15 s (500 mW assumption).

Measured under version 3 (seeds 10000-10199, rule fly): baseline 5/200, the 6 #35 SAC models 1/1200 in total. The existing aimers do not work under the new rule; reward design and retraining are a follow-up issue.

The user asked (2026-11-15) to go through to the merge so that version-3 episodes can be watched in the viewer. Left: README, close (pointer removal), push, PR, merge.

Two vast.ai instances were created and destroyed on 2026-11-15 without running anything (first image had no sshd; the local measurement finished before the second came up). `vastai show instances` is empty.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 포획 조건을 레이저 명중으로 바꾸기 (#42)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, AGENTS.md pointer.
#### Changes
- Filled Summary, Goal, Scope, Out Of Scope, Done Criteria from the conversation.
#### Verification
- None needed; no code changed.
#### Notes
- Evidence for the values (Keller et al. 2016, 2020, Scientific Reports):
  - Baseline lethal setting: 532 nm, 3 W, 25 ms pulse, 2.5 mm spot. LD90 about 1.6–1.8 J/cm² (74 mJ at 2.3 mm, 25 ms).
  - Target point: mid-thorax, the body centroid in flight.
  - In-flight tracking acceptance at 2 m: mean 2 px, max 3 px during the pulse, 1 px ≈ 250 µm → 0.5 mm mean, 0.75 mm max (the multiplication is ours).
  - Mortality dropped at 50 ms and 100 ms pulses, and tracking accuracy dropped with it.
  - Spots under 2 mm were judged impractical for a deployable system.
  - These are mosquito numbers. The 2020 paper also tried spotted-wing drosophila; its numbers were not verified. No Drosophila melanogaster dose was read.
- 1.25 mm is our choice between the paper's 0.75 mm tracking limit and "beam touches any part of the body" (about 2.75 mm).
- Hold time and laser power trade off at fixed energy: 74 mJ is 25 ms at 3 W, about 75 ms at 1 W, about 150 ms at 0.5 W.
- A fly at 0.3 m/s moves 3 mm per physics step, more than the 2.5 mm beam diameter, so a fly merely crossing the beam is inside it for at most one step.
- Power decision (user, 2026-11-15): the device is for indoor use, so a 3 W beam is not acceptable. No eye-safe power kills a fly (Class 2 at 1 mW would need 74 s, Class 3R at 5 mW 15 s, and heat leaks away over seconds), so the power is lowered only to the top of Class 3B, 500 mW, where fire, skin and diffuse-reflection hazards are normally absent; the eye hazard is left to interlocks. 74 mJ / 0.5 W = 0.148 s → 0.15 s.
- 0.15 s is an extrapolation: the papers varied pulse length only up to 45 ms for dose, and in-flight mortality fell at 50–100 ms. Class limits were checked against secondary sources (Seibersdorf white paper, Lasermet, ANSI blog), not the IEC 60825-1 text.

### docs: 레이저 포획 조건의 근거 문서 (#42)
> why: the user asked for the evidence behind the new capture values to be kept and documented; the #3 note still said the laser was excluded
#### Scope
`docs/issues/feature/42-feature-laser-hit-capture/laser-capture-condition.md` (new, Korean, for teammates), the #3 design note, this doc.
#### Changes
- New design note: scope, terms, values taken from Keller 2016 / 2020, the 1.25 mm choice among three candidates, power class table and the 500 mW / 0.15 s choice, what a fly crossing the beam does, safety limits, values put into the environment, references.
- #3 note: a dated line at the top says the laser decision replaces its salt-pellet choice and links the new note. The rest is kept as a record.
#### Verification
- ko-writing `check.py`: no hits in sections 1-7; remaining warnings are heading heuristics (noun phrases with a modifier) and two dated lines kept on purpose.
- One cold-reader pass by a fresh subagent that read only the note. Fixed: undefined terms (Class 3B, 벗초파리, Photonic Fence, R), "머무는 시간" / "판정 거리" used for both the measured value and the limit, "논문" without a year, the 45 ms figure missing from the table, eye-limit comparison at 25 ms only, missing Lasermet reference.
- Arithmetic rechecked by script: 1.25 mm at 1 / 2 / 3 m = 0.072° / 0.036° / 0.024°; 74 mJ over a 2.3 mm spot = 1.78 J/cm²; 1.6 J/cm² over a 2.5 mm spot = 79 mJ, 0.157 s at 0.5 W.
#### Notes
- The cold reader caught that 74 mJ was measured with a 2.3 mm spot while the note assumes 2.5 mm. At 2.5 mm the same fluence is 79 mJ, i.e. 0.16 s at 500 mW. 0.15 s is kept (the value the user approved) and the note says so; the mosquito-to-fruit-fly gap is larger than this difference (our estimate).
- The eye exposure limits in the note (about 0.1 mJ/cm² at 25 ms, 0.4 mJ/cm² at 0.15 s) come from the 1.8·t^0.75 mJ/cm² formula as remembered; a web search did not confirm it against the standard, and the note says it is unchecked.
- No second cold-reader pass was run after the fixes.

### feat: 포획 판정을 빔까지 거리로 바꾸기 (#42)
> why: capture has to mean a laser hit; values from the design note
#### Scope
`flytracker/env.py`, `flytracker/record.py`, `flytracker/free_flight.py`, `flytracker/aimer.py` (comment), `tests/test_env.py`, `tests/test_neural_demo_suite.py`, this doc.
#### Changes
- `EnvConfig`: `capture_angle_deg` removed, `capture_radius` 0.00125 m added, `capture_hold` 0.2 to 0.15 s. `ENV_VERSION` 3.
- Capture test in `_update_vision`: distance from the fly centre to the beam (`_to_beam`, forward-only, now shared with the fly observation) at most `capture_radius`; still requires `visible` and `capture_range`.
- `info["beam_dist"]` (m) and frame key `beamDistMm` (mm, because frames are rounded to 4 decimals).
- Recording meta: `captureAngleDeg` replaced by `captureRadius` and `captureHold`.
- Tests: 15 physics steps capture and 14 do not; 1.2 mm captures, 1.3 mm and 52 mm (3° at 1 m) do not; the timer restarts after leaving the beam; a fly behind the turret is not hit; a fly straight above the turret is no longer capturable.
#### Verification
- `uv run python -m pytest -q`: 109 passed, 45 skipped (the skips need the local neural source).
- Rule baseline under version 3, seeds 10000-10199, rule fly: 5/200 captured, mean 6.21 s over the captured ones (`scripts/match.py`). Under version 2 it was 200/200.
- The 6 #35 SAC models (trained under version 2) under version 3, same seeds, rule fly, measured on the laptop with a scratch script that skips the version check in `load_opponent`: `sac-fs1-s0` 1/200 (9.91 s); `sac-fs1-s1`, `sac-fs1-s2`, `sac-fs4-s0`, `sac-fs4-s1`, `sac-fs4-s2` 0/200 each. Total 1/1200. Under version 2 they caught about 97-98 %.
#### Notes
- Blind cone: pitch stops at 89°, so a fly within 1° of straight up cannot be hit (33 mm off the beam at 1.9 m). Under the 3° rule the 89° limit covered the zenith; `test_fly_straight_above_turret_is_capturable_only_with_89_deg_limit` is replaced by a test that states the new behaviour.
- `EnvConfig.from_dict` ignores unknown keys, so a version-2 config (`capture_angle_deg: 3.0`, `capture_hold: 0.2`) loads as radius 1.25 mm with hold 0.2 s. `test_capture_demos_keep_published_baseline_contract` now asserts exactly that for the #31 demo specs. Whether the neural demos should use 0.15 s is the #31 owner's call.
- The first test runs in this worktree used the main checkout's pytest (`VIRTUAL_ENV` pointed there) and so tested the old code; fixed with `uv sync --all-extras` and `uv run python -m pytest`. Results above are from the worktree's own environment.
- Viewer still reads `captureAngleDeg`; new recordings have no such key until the viewer commit on this branch.

### feat: viewer에 빔 자리와 빔까지 거리 넣기 (#42)
> why: new recordings have no `captureAngleDeg`, so the capture ring had no size; a 0.036° target cannot be read from an aim error shown to 0.1°
#### Scope
`viewer/src/scene/FirstPersonView.jsx` + its CSS module, `viewer/src/components/Readouts/Readouts.jsx`, `viewer/src/data/episode.js`, `viewer/src/data/labels.js`, `viewer/src/App.jsx`, `ui-text.glossary.md`, captures, this doc.
#### Changes
- Aimer view: recordings without `captureAngleDeg` get a small centre crosshair (the beam path; a 2.5 mm beam is under one pixel, so no ring). Recordings with `captureAngleDeg` keep the ring.
- Readouts: new row "빔까지 거리" (mm under 10 cm, m above) when the recording has `beamDistMm`; aim error shown to 0.01° for those recordings, also in the chart tooltip.
- Glossary: "빔까지 거리" added.
#### Verification
- `npm run build --prefix viewer` passes. `uv run python -m pytest -q`: 109 passed, 45 skipped (includes the viewer attitude test, which needs `viewer/node_modules`).
- ui-evidence, dev server from this worktree on port 5180 (port was free before start), commit c22f18d + working tree, Chrome 157.0.8103.52, ready `window.__frames > 10 && document.fonts.status === 'loaded'`, settle 800 ms, reduced motion on:

| page | viewport | file | overflow | probes |
| --- | --- | --- | --- | --- |
| version-3 episode (`?run=2026-11-15_201137_baseline&tag=baseline&ep=1`) | 1600x900 | `42-feature-laser-hit-capture/captures/v3-1600x900.png` | none | 1 cross / 0 ring; rows: 상태, 조준 오차, 빔까지 거리, 거리, 포획 진행, 초파리, 프레임 |
| version-3 episode | 390x844 (mobile, dpr 2) | `42-feature-laser-hit-capture/captures/v3-390x844.png` | none | same |
| version-2 episode (`?run=2026-11-11_133858_baseline&tag=baseline&ep=1`) | 1600x900 | `42-feature-laser-hit-capture/captures/v2-1600x900.png` | none | 0 cross / 1 ring; rows: 상태, 조준 오차, 거리, 포획 진행, 초파리, 프레임 |
| version-2 episode | 390x844 (mobile, dpr 2) | `42-feature-laser-hit-capture/captures/v2-390x844.png` | none | same |

- Looked at the three 1600x900 / 390x844 PNGs opened: crosshair centred in the aimer view, "빔까지 거리 0.63m" row present, old episode unchanged with its ring. The phone capture shows the run list and panel above the fold; the aimer view is below it and was checked by probe only.
- Console: one 404 for `/favicon.ico` and the existing `THREE.Clock` deprecation warnings; nothing from the changed code.
#### Notes
- The first capture run wrote both pages to the same file names (same path `/`), so the version-3 page was captured again into its own folder.
- The aim-error chart still spans 0-180° and cannot show the last 0.1°. A beam-distance chart is a follow-up candidate.

### feat: 새 포획 조건으로 돌린 기준선 실행 올리기 (#42)
> why: the user asked to be able to watch version-3 episodes in the viewer after the merge
#### Scope
`published/2026-11-15_201137_baseline/`, `published/2026-11-15_201250_baseline/`, this doc.
#### Changes
- `record_baseline.py --episodes 3 --seed 10000` (the seeds the training evaluation uses): 0/3 captured.
- `record_baseline.py --episodes 5 --seed 10114`: 1/5 captured (seed 10116 at 2.62 s). Chosen so that one capture can be watched; 5 episodes around a known capture overstate the rate, which is 5/200.
- Both copied with `publish_run.py --issue 42`.
#### Verification
- Captured episode (`ep_002.json`, seed 10116): last frames have `beamDistMm` 1.21 → 0.32 while `captureProgress` goes 0.07 → 1.0 over 8 frames; meta has `captureRadius` 0.00125, `captureHold` 0.15, no `captureAngleDeg`.
- Per-seed baseline run on seeds 10000-10199 (`runs/_ops/eval_v3.py`, local only): 5 captures (seeds 10031, 10069, 10116, 10164, 10196); the beam came within 1.25 mm at least once in 39 episodes, stayed for 0.05 s or more in 9; median of the closest approach 2.51 mm.
#### Notes
- `publish_run.py` warns when the issue has no `training` label; #42 is not a training issue.

### docs: README를 레이저 포획 조건에 맞추기 (#42)
> why: the README still described capture as 3° for 0.2 s and reported the version-2 baseline
#### Scope
`README.md`, this doc.
#### Changes
- Episode: capture is the fly centre within 1.25 mm of the beam for 0.15 s, with a short paragraph on what the values mean, a link to the design note, and the date the rule changed.
- Aimer action: the 89° pitch limit now leaves a 1° cone above the turret that the beam cannot reach.
- Fly state: the aim error entry no longer states the capture rule.
- Baseline comparison: version-3 numbers on seeds 10000-10199 (5/200, 6.21 s over the captured ones, visible 64 %, mean return −32.26), what the baseline fails at, and the version-2 numbers kept as history with the SAC result (1/1200).
- Match table example, recording format (`captureRadius`, `captureHold`, `beamDistMm`), playback screen (crosshair, beam distance).
#### Verification
- `uv run python scripts/record_baseline.py --episodes 200 --seed 10000 --no-save`: 포획 5/200, 평균 보상 -32.26, 보인 비율 64%, 포획까지 평균 6.21초.
- `readme_check.py README.md`: 0 fail, 0 warn (URLs not probed). ko-writing `check.py`: no forbidden patterns; the two heading-length hits were there before.
#### Notes
- The visible ratio rose from 18 % to 64 % only because episodes no longer end early: the baseline keeps the fly in view and never finishes.
- No cold-reader pass was run on the README change.

## Management Notes
### Follow-up Candidates
- Reward shaping or radius curriculum for sub-0.1° aiming, if version 3 measurements show no captures.
### References
- https://www.nature.com/articles/srep20936
- https://www.nature.com/articles/s41598-020-71824-y
- https://www.nature.com/articles/s41598-024-57804-6
- https://www.seibersdorf-laboratories.at/fileadmin/user_upload/docs/le/las/publ/whitepaper_iec-60825-1.pdf
- https://blog.ansi.org/ansi/laser-class-safety-1-1c-1m-2-2m-3r-3b-4/
