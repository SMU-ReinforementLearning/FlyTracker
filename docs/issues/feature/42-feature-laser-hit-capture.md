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
- [ ] Capture is decided by distance to the beam (1.25 mm) and hold time (0.15 s); the 3° angle condition is gone from code, recordings, viewer and README.
- [ ] `ENV_VERSION` is 3 with a version-table line.
- [ ] Tests cover: on-beam for 15 physics steps captures; 14 steps does not; 1.3 mm off does not; a fly behind the turret does not; full test suite passes.
- [ ] The design note records evidence, power choice and safety limits; #3 doc states the laser decision and its date.
- [ ] Baseline and #35 SAC capture counts on 200 seeds under version 3 are reported in this doc, whatever they are.
- [ ] Viewer shows the new condition; screenshot evidence at desktop and 390px.

## Current State
Seeded 2026-11-15. No code changed yet. Values fixed with the user on 2026-11-15: radius 1.25 mm, hold 0.15 s (500 mW assumption). Next: design note and #3 doc, then `env.py` and tests.

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

## Management Notes
### Follow-up Candidates
- Reward shaping or radius curriculum for sub-0.1° aiming, if version 3 measurements show no captures.
### References
- https://www.nature.com/articles/srep20936
- https://www.nature.com/articles/s41598-020-71824-y
- https://www.nature.com/articles/s41598-024-57804-6
- https://www.seibersdorf-laboratories.at/fileadmin/user_upload/docs/le/las/publ/whitepaper_iec-60825-1.pdf
- https://blog.ansi.org/ansi/laser-class-safety-1-1c-1m-2-2m-3r-3b-4/
