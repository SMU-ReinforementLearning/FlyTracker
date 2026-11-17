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

### feat: 레이저를 한 발씩 쏘게 하고 오발을 세기 (#69)
> why: the laser was implicitly always on, so a beam pointed away from the fly cost nothing and "fire only when sure" could not be expressed or measured
#### Scope
Env version 6: action, shot rule, counts, observation, baseline trigger, recorder fields, tests, README, measuring script. No viewer change, no training.
#### Changes
- `env.py`: `step` starts a shot when `fire > 0` and none is running; `_advance_shot` runs once per physics step after the vision update, marks the shot a misfire the first time the beam is off the fly, and returns capture when a clean shot ends. `captureProgress` is now the clean fraction of the running shot (0 when not firing or after a miss, 1 on capture). `info` gains `firing`, `shots`, `misfires`; the observation gains `shot` (remaining fraction of the running shot), so 18 dims.
- `baseline.py`: `beam_distance(obs)` = distance x sin(angle from `uv_fine`); the rule fires when it is within `fire_radius` (default: the capture radius). `track()` and `assisted()` never fire on their own, so with the tracking assist the policy's `fire` value decides.
- `wrappers.py`: discrete action 5 is `fire`. A shot lasts 7.5 action steps and turning is allowed during it, so one discrete action per step is enough.
- `record.py`: frame key `firing`, summary `shots` / `misfires`. `free_flight.py` passes a third action value 0 and writes `firing: false`.
- `measure_fire.py`: prints the table below; with `--out DIR` it also writes `episodes.csv`, `shots.csv` and `meta.json` (the raw rows are committed in the next commit, measured at this one).
- Reward: the action-change penalty averages the two turning values only. With the third value included, the same turning sequence would have been penalised two thirds as much, which changed a pinned rule-fly rollout (`test_default_rule_matches_prechange_rollout`).
- Tests: 2-dim actions widened to 3; capture tests fire; four new or rewritten shot tests in `tests/test_env.py`. In the teammate's tests: `[0,0]` -> `[0,0,1]` where capture is expected, `OBS_DIM == 18`, one unused `env._capture_timer = 0.` line removed, and `test_capture_at_pulse_onset_has_zero_delivered_exposure` uses `capture_hold=.12` instead of `.13` (the old timer counted the reset's vision update as one tick; a shot fired on the first step ends at 0.12 s only if it is 12 steps long).
#### Verification
- `uv run pytest -q`: 205 passed (203 before, plus 2 net new).
- Baseline against the rule fly, seeds 20000-20199, `measure_fire.py --fire-radius-mm always 2.5 1.25 0.9 0.6 0.3`:

| Trigger | Captured | Mean time (miss = 10 s) | Shots / ep | Misfires / ep | Episodes with no misfire | Hit rate |
|---|---|---|---|---|---|---|
| always firing | 198/200 | 4.965 s | 31.10 | 30.11 | 0/200 | 0.032 |
| 2.5 mm | 198/200 | 4.949 s | 2.19 | 1.20 | 67/200 | 0.452 |
| 1.25 mm (default) | 198/200 | 4.894 s | 1.49 | 0.50 | 138/200 | 0.664 |
| 0.9 mm | 198/200 | 4.901 s | 1.41 | 0.42 | 147/200 | 0.702 |
| 0.6 mm | 198/200 | 4.919 s | 1.31 | 0.33 | 155/200 | 0.753 |
| 0.3 mm | 198/200 | 4.971 s | 1.24 | 0.25 | 166/200 | 0.798 |

  Under env version 5 the baseline took 4.86 s on these seeds (198/200, #51). The same two episodes are missed at every trigger.
- README table seeds (10000-10199), default trigger: 200/200, 4.99 s (version 5: 4.95 s), 1.54 shots and 0.55 misfires per episode, 134/200 with no misfire. `scripts/record_baseline.py --episodes 200 --seed 10000 --no-save` prints the same capture count and time.
- Baseline against the neural fly, stimulus off, seeds 20000-20019 (`measure_fire.py --fire-radius-mm always 1.25 --fly-model neural --no-stimulus --episodes 20`): always firing 20/20, 5.062 s, 31.70 shots and 30.70 misfires per episode; default trigger 20/20, 4.920 s, 1.80 shots and 0.80 misfires per episode, 10/20 episodes with no misfire. Twenty seeds only.
- `scripts/train.py --algo sac --steps 300 --assist 0.2` runs end to end with the 3-dim action (smoke test, scratch folder).
- `npm run build --prefix viewer`: built. The viewer ignores the new fields for now.
- Not run: lint (`ruff` is not installed in this environment).
#### Notes
- Read of the numbers: the trigger radius trades misfires for time only weakly; from 2.5 mm to 0.3 mm misfires fall from 1.20 to 0.25 per episode while the mean time moves by 0.08 s. Most of an episode is search, so waiting for a better lock is cheap. One in three default-trigger episodes still has a misfire: a single observation does not tell whether the lock will hold for 0.15 s.
- "Always firing" is not the old rule: shots restart every 0.15 s, so a 0.15 s on-target window that straddles two shots does not capture. It costs 0.1 s on average here.
- Episodes recorded before version 6 have no `firing`, `shots`, `misfires`; readers must treat them as absent.

### chore: 기준선 측정 원자료 올리기 (#69)
> why: the user asked (2026-11-17) that the results be reproducible and usable for later analysis; the tables above were only printed
#### Scope
`docs/issues/feature/69-feature-aimer-fire-action-misfire/data/`: raw rows of both measurements and a README with commands and columns. No code change.
#### Changes
- `data/rule-fly/` (seeds 20000-20199, six triggers: 1,200 episode rows, 7,749 shot rows) and `data/neural-fly-nostim/` (seeds 20000-20019, two triggers: 40 episode rows, 670 shot rows). Each has `episodes.csv`, `shots.csv`, `meta.json`.
- `data/README.md`: the exact command per folder, setup, every column, a loading example, limits.
#### Verification
- Both runs were made at commit 55cc905 with a clean tree (`gitCommit`, `gitDirty: false` in each `meta.json`). No local path is in either `meta.json`.
- The printed tables equal the ones in the previous section, row for row (rule fly: 198/200, 4.894 s, 1.49 shots, 0.50 misfires at 1.25 mm; neural: 20/20, 4.920 s, 1.80, 0.80).
- From `shots.csv`, default trigger (script: stdlib `csv`, medians):

| Fly | Outcome | Shots | Beam distance at trigger | Fly's angular rate at trigger | Aimer-fly distance |
|---|---|---|---|---|---|
| rule | hit | 198 | 0.84 mm | 7.4 deg/s | 1.88 m |
| rule | misfire | 100 | 0.89 mm | 8.6 deg/s | 1.96 m |
| neural | hit | 20 | 0.73 mm | 11.5 deg/s | 2.06 m |
| neural | misfire | 16 | 1.12 mm | 11.0 deg/s | 2.05 m |

  Rule fly: 60 of 100 misfires leave the fly within 40 ms of the trigger, 18 after 100 ms or more. Misfires per episode: 0 in 138, 1 in 41, 2 in 11, 3 in 7, 4 in 2, 8 in 1. From first sight of the fly to capture: median 1.35 s; the fly is first seen at 3.43 s on average.
#### Notes
- `est_beam_mm` equals `true_beam_mm` in every row: the observation carries no error yet, so the baseline knows the beam distance exactly at the trigger and still misses one shot in three. What it lacks is not the present position but the next 0.15 s. This is the number to compare against once the detector (#13) adds error.
- Against the rule fly, hits and misfires look alike at the trigger (0.84 vs 0.89 mm, 7.4 vs 8.6 deg/s), so a tighter radius or a rate threshold on one observation cannot separate them well; this agrees with the weak effect of the trigger radius.
- The neural rows are 36 shots; the 0.73 vs 1.12 mm gap there is not established.

### feat: viewer에 레이저 발사와 오발 보여 주기 (#69)
> why: recorded episodes carried `firing` but the viewer drew the aim line as if the laser were always on, and a misfire could not be seen
#### Scope
Viewer (aim line, zoom circle, readouts, issue-page history), two more frame keys, glossary. No change to env behaviour.
#### Changes
- `env.py` snapshot and `record.py` `FRAME_KEYS`: cumulative `shots` and `misfires` per frame, so the viewer and later analysis do not have to reconstruct them from `firing` (back-to-back shots have no falling edge). `free_flight.py` writes zeros. README `frames` table gains the row and a link to `data/README.md`.
- `viewer/src/data/episode.js`: `firing`, `shots`, `misfires` (null for records before version 6); a sample has `firing` (true for old records: the laser was always on) and `missed` (firing and `captureProgress` 0).
- `AimerRig.jsx`: in version 6 records the aim line is faint (opacity 0.15) while not firing and solid (0.95) while firing; a missed shot is drawn in the new `misfire` colour (`theme.js`). Old records are drawn as before (0.35).
- `FirstPersonView.jsx` / `.module.css`: the zoom view's beam circle is dim while not firing, red on a missed shot, green on a clean one.
- `Readouts.jsx`: state `오발` while a missed shot is still running; rows `레이저` (`쏘는 중` / `꺼짐`), `쏜 발`, `오발`, only for records that have `firing`.
- `history.js`: issue 69 (env 6), an `envVersion` line and a `env.capture_hold` line (value unchanged, meaning now "length of one shot").
- `ui-text.glossary.md`: 발, 오발, 쏘는 중.
#### Verification
- `uv run pytest -q`: 205 passed. `npm run build` in `viewer`: built.
- ui-evidence on the built site (`vite preview`, port 4969), tree: uncommitted on 9fe7215, Chrome 157, 1600x900, serve check `document.title === 'FlyTracker'`. Ready = playback ended, then N `ArrowLeft` key events to reach the frame. Probe = the readout rows and the zoom circle's `data-firing/data-missed`.

| state | run, episode, frame | overflow | readouts | zoom circle |
| --- | --- | --- | --- | --- |
| missed shot | `2026-11-17_231813_neural-nostim-baseline` ep 3, 214/255 | none | 상태 오발, 포획 진행 0%, 레이저 쏘는 중, 쏜 발 1발, 오발 1발 | true/true |
| clean shot | `2026-11-17_231802_rule-baseline` ep 1, 255/259 | none | 상태 포획 중, 포획 진행 53%, 레이저 쏘는 중, 쏜 발 1발, 오발 0발 | true/false |
| not firing | same episode, 241/259 | none | 상태 보임, 레이저 꺼짐, 쏜 발 0발, 오발 0발 | false/false |
| record before version 6 | `2026-11-17_201228_neural-nostim-baseline` ep 1, 201/265 | none | no 레이저 / 쏜 발 / 오발 rows | true/false |

  Console: favicon 404 and `THREE.Clock` deprecation warnings only (both present on main). Captures are in the session scratchpad, not committed. Looked at: missed shot (red solid aim line from the aimer through the fly's position, red zoom circle, red dot next to 오발) and not firing (aim line barely visible, dim zoom circle).
- Not verified: phone width (no layout change; three readout rows added to an existing list), light colour scheme (the capture ran in dark), the clean-shot PNG was checked by probe only.
#### Notes
- The first two capture attempts failed in the helper script (playback auto-starts, so stepping forward from frame 0 did not land on the frame; then a regex lost its backslashes). Not a viewer fault.

### chore: 환경 버전 6 기준선 에피소드 올리기 (#69)
> why: the issue page needs episodes to watch; no published run was recorded under the shot rule
#### Scope
`published/`: three runs and `published/issues/69.json`. No code change.
#### Changes
- Recorded with #61's `record_match.py baseline` (default seeds 10000-10002) at 4f73d3c's code, then `scripts/publish_run.py <run> --issue 69`:

| Run | Fly | Flags | Captured | Time (s) | Shots / misfires per episode |
|---|---|---|---|---|---|
| `2026-11-17_231802_rule-baseline` | rule | (none) | 3/3 | 5.15, 5.05, 4.17 | 1/0, 1/0, 1/0 |
| `2026-11-17_231813_neural-nostim-baseline` | neural | `--fly-model neural --no-stimulus` | 3/3 | 5.29, 5.37, 5.07 | 1/0, 1/0, 5/4 |
| `2026-11-17_231839_neural-stim-baseline` | neural | `--fly-model neural` | 3/3 | 5.35, 5.53, 4.91 | 2/1, 2/1, 4/3 |

- `published/issues/69.json` (Korean, screen text): the rule, what the three runs show, the 200-seed and 20-seed numbers, where the raw rows are, why no learned aimer exists yet. `compare` is 61 (the same baseline against the same flies under version 5).
#### Verification
- Each published episode has `firing`, `shots`, `misfires` in `frames` and `shots` / `misfires` in `summary`; the counts above were read back from the published files.
- `npm run build` in `viewer` with the three runs and `69.json` present: built; the captures in the previous section were taken from this build.
- `publish_run.py` warned that #69 has no `training` label: expected, nothing was trained.
#### Notes
- Under version 5 the baseline took 4.89-5.45 s on these seeds against the neural fly (#61); the times here are in the same range.
- Three seeds per run: these are for watching, not for rates. Rates are in `data/`.

## Management Notes
### Follow-up Candidates
- Train an aimer under env version 6 once the detector's error model exists (#13); decide the misfire term of the reward there.
- A trigger that looks at more than one observation (for example, lock held for N steps) if the misfire rate matters before training.
### References
- #42 laser capture condition (1.25 mm, 0.15 s), #45 baseline tracking, #51 SAC under the laser rule, #13 detector on the aimer's view, #61 episodes against the neural fly.
