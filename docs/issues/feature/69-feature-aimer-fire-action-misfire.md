# 69 조준기에 레이저 발사 행동과 오발 측정 넣기

## Document Relations
- Issue: #69
- Branch: `69-feature-aimer-fire-action-misfire`
- Umbrella: (none)
- Status: in progress

## Summary
Give the aimer a fire action so the laser is on only when it shoots, and count the shots that miss. Until env version 5 the laser was implicitly always on: capture was "beam within 1.25 mm for 0.15 s" and a beam pointed anywhere else cost nothing. The user's point (2026-11-17): a real laser must not be left on; it should be fired briefly, when the aimer is sure of the kill.

## Goal
Env version 6 with the shot rule, a baseline that follows it, and two numbers per episode: capture time and misfires.

The rule, as agreed with the user on 2026-11-17:

| Item | Rule |
|---|---|
| Action | `[yaw_rate, pitch_rate, fire]`. `fire > 0` pulls the trigger |
| One shot | Lasts `capture_hold` (0.15 s). Cannot be stopped. A trigger pulled during a shot is ignored |
| Capture | The beam stays within `capture_radius` (1.25 mm) of the fly for the whole shot |
| Misfire | A shot during which the beam left the fly at least once. The fly lives |
| Limits | None. A new shot can start as soon as the last one ends |
| Turning | Allowed during a shot |

Why a fixed-length shot and not a free on/off switch: with a switch the aimer turns the beam on only while it is on the fly, misfires stay near zero and there is nothing to decide. With a shot, the aimer must judge at the trigger whether it can stay on the fly for the next 0.15 s.

Why not an energy or shot budget: the user rejected it as unintuitive (a laser can fire as long as it has power). The cost of a bad shot is that the beam lands on something that is not the fly, so that is what is counted.

Premise for later (#13, detector on the aimer's view): capture and misfire are judged by the env from true positions; the aimer decides from its observation only. A misfire is "beam on, not on a fly", so a shot at a false detection is counted by the same number. No artificial trigger delay is added now; detector noise and latency will make the decision hard on their own.

## Scope
- `flytracker/aimer.py`, `env.py`: third action, shot state, capture by shot, `shots` / `misfires`, observation field `shot`, `ENV_VERSION = 6`.
- `flytracker/baseline.py`, `players.py`: the baseline fires when the beam distance estimated from its observation is within `fire_radius`.
- `flytracker/wrappers.py`: sixth discrete action `fire`; the tracking assist leaves firing to the policy.
- `flytracker/record.py`, `free_flight.py`: frame key `firing`, summary `shots` / `misfires`.
- Tests, `README.md`, `scripts/train.py` docstring.
- `docs/issues/feature/69-feature-aimer-fire-action-misfire/measure_fire.py`: baseline numbers under the rule.
- Viewer: show firing and misfires (second unit, not started).

## Out Of Scope
- Retraining SAC. Decided with the user: train once, after the detector's error is known, on observations with that error. Until then no learned aimer exists for env version 6 (`load_opponent` refuses version 5 models).
- A misfire term in the reward. Belongs to the training issue; today's reward is unchanged except that the action-change penalty looks at the two turning values only.
- The fly's side: stimulus trigger, `FLY_OBS_FIELDS`, fly reward. The fly still sees the aim line as before (the teammate's area; the user decided not to touch it).
- A failure condition on misfires. Measure first, then decide.

## Done Criteria
- [x] Shot rule in the env with tests for: no capture without firing, 15 physics steps to capture, a shot that leaves the fly is a misfire and the next shot can capture, a shot cannot be stopped. (2026-11-17 21:50)
- [x] Full test suite passes. (2026-11-17 21:50, 205 passed)
- [x] Baseline measured over 200 seeds against the rule fly: capture rate, mean time, shots, misfires. (2026-11-17 21:55)
- [x] Baseline measured against the neural fly. (2026-11-17 22:10, 20 seeds, stimulus off)
- [ ] Viewer shows when the laser fires and the shot / misfire counts.
- [ ] Published baseline runs under env version 6 and `published/issues/69.json`.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-17 22:00. Env, baseline, tests, README and the measuring script are written and verified; nothing is committed yet (waiting at the review gate, two commits: registration, then the rule).

Next: commit after approval -> viewer unit (beam drawn only while firing, misfire readout, `history.js` entry for env version 6; needs `ko-ui-text` and screenshot evidence) -> record and publish baseline runs under version 6 with `published/issues/69.json` -> PR.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 조준기에 레이저 발사 행동과 오발 측정 넣기 (#69)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, `AGENTS.md` pointer.
#### Changes
- Doc filled from the 2026-11-17 conversation: the shot rule, why not a budget, the detector premise, training deferred.
#### Verification
- `issue-start.mjs` created issue #69 (Type Feature, label enhancement, assignee the user, Priority Medium), branch from `origin/main` @ fdbb86e, worktree `FlyTracker-69`.
#### Notes
- Priority Medium was proposed by the agent, not stated by the user: nothing waits on this, and the detector issue (#13) comes after it.
- No umbrella: the only open umbrella (#58) is the teammate's workstream.

## Management Notes
### Follow-up Candidates
- Train an aimer under env version 6 once the detector's error model exists (#13); decide the misfire term of the reward there.
- A trigger that looks at more than one observation (for example, lock held for N steps) if the misfire rate matters before training.
### References
- #42 laser capture condition (1.25 mm, 0.15 s), #45 baseline tracking, #51 SAC under the laser rule, #13 detector on the aimer's view, #61 episodes against the neural fly.
