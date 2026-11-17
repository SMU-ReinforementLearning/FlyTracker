# 72 SAC 조준기를 환경 버전 6에 세우고 조준기 v1로 정하기

## Document Relations
- Issue: #72
- Branch: `72-feature-aimer-v1-sac-rule-trigger`
- Umbrella: (none)
- Status: in progress

## Summary
Stand the #51 SAC aimer up under env version 6 and decide whether it becomes aimer v1, with the rule aimer kept as v0. Since #51 the SAC aimer (`sac-beam-assist`) has been faster than the rule aimer (2.94 s vs 4.86 s under version 5), yet #61 and #69 kept reporting only the rule aimer; #69's fire action made the version 5 models unloadable. The user (2026-11-18): "it is the aimer's next generation; time for the aimer baseline to move on", then agreed to the order below.

## Goal
Agreed order (2026-11-18):
1. Run the version 5 SAC models under version 6: the model steers as trained, the baseline's rule decides when to fire. No training.
2. Measure v0 and the candidate on the same 200 seeds (capture, time, misfires), and against the neural fly on more seeds than #61's three.
3. Decide by a pre-registered gate (`72-feature-aimer-v1-sac-rule-trigger/gate.md`) whether the candidate is v1; if so README and the issue page show v0 and v1 side by side.
4. A SAC that also learns to fire is v2, after the detector's error is known (#13). Not here.

Two roles, kept apart: the rule aimer is the fixed yardstick (no training, runs under any env version); v1 is the best aimer so far and the opponent a learned fly would face.

Also from the same conversation: firing belongs to the aimer, not the environment. The decision to fire is the policy's, the length of a shot is a property of the laser, and only the hit / misfire judgement is the environment's. #69's text and the viewer present all of it as "environment".

## Scope
- `flytracker/players.py`, `baseline.py`: `load_opponent` accepts an env version 5 aimer model and gives it the baseline's firing rule (`RuleAimer.wants_fire`); `Opponent.fire` says who fires; label suffix `+rule-fire`.
- `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/`: `measure_aimers.py`, `gate.md`, `gate/`, `data/` (raw rows per aimer and fly).
- Published runs of the candidate under version 6 and `published/issues/72.json`.
- Viewer / README: v0 and v1 naming, who fires, shot settings shown on the aimer's side.

## Out Of Scope
- Training anything. A SAC that learns to fire (v2) waits for the detector (#13).
- Tuning the trigger (radius, multi-step lock) for the SAC aimer. One fixed rule, the baseline's.
- Moving the config key `capture_hold` out of `EnvConfig`. Decided by the agent while working, not by the user: the teammate's in-flight training (#58/#59) and tests construct `EnvConfig(capture_hold=...)`; renaming the key would break their branch for no change in behaviour. Presentation and wording are changed instead; the key move is a follow-up candidate.
- The fly's side.

## Done Criteria
- [x] Version 5 aimer models load under version 6 with rule firing; tests cover the observation slice, the fire rule and the version check. (2026-11-17 23:50)
- [x] Gate document written before the candidate is measured on the gate seeds; baseline frozen by sha256. (2026-11-17 23:55; committed together with the results)
- [x] Candidate measured on seeds 20000-20199 (three models) and against the neural fly (60 seeds, stimulus off and on); raw rows committed. (2026-11-18 00:40)
- [x] Verdict appended to the gate document. (2026-11-18 00:50, adopt)
- [ ] Published runs and `published/issues/72.json`.
- [ ] README and viewer name v0 / v1 per the verdict; firing shown as the aimer's.
- [ ] Full test suite passes; viewer builds.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-18. Adapter and tests written; gate document written; baseline frozen (4.894 s, 198/200, 0.50 misfires per episode). Candidate measurements running. Nothing committed yet.

Gate: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate.md`.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: SAC 조준기를 환경 버전 6에 세우고 조준기 v1로 정하기 (#72)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, `AGENTS.md` pointer.
#### Changes
- Doc filled from the 2026-11-18 conversation: two roles (yardstick v0, best-so-far v1), the agreed order, firing as the aimer's area.
#### Verification
- `issue-start.mjs` created issue #72 (Type Feature, label enhancement, assignee the user, Priority Medium), branch from `origin/main` @ 61d2b6b, worktree `FlyTracker-72`.
#### Notes
- Priority Medium was proposed by the agent.
- The main checkout's local `main` was fast-forwarded to `origin/main` first (it was at 7bd0ac8 and its copy of `issue-start.mjs` predated `--priority`).
- Open issue #70 (README date of the aimer state) also edits `README.md`; it is not part of this work.

### feat: 환경 버전 5 조준기 모델을 쏘는 규칙과 함께 불러오기 (#72)
> why: #69's fire action made every trained aimer unloadable, so only the rule aimer could be measured under env version 6
#### Scope
`flytracker/players.py`, `baseline.py`, `scripts/record_match.py`, `tests/test_players.py`. No env change, no training.
#### Changes
- `RuleAimer.wants_fire(obs)`: the firing rule as one method (visible and estimated beam distance within `fire_radius`); `act` uses it.
- `PolicyPlayer(rule_fire=True)`: the policy gets the observation without `shot` (the last field), its two outputs are padded to three, the tracking assist is applied as trained, then `fire` is set by `tracker.wants_fire`. Continuous-action policies only.
- `load_opponent`: an aimer model with `envVersion` in `RULE_FIRE_VERSIONS` (5) is loaded that way instead of being refused. Version 5 differs from 6 for the aimer only in that field and that action; other versions and fly models are refused as before. `Opponent.fire` is `"rule"` or `"policy"`, and the label gets `+rule-fire`.
- `scripts/record_match.py`: moved from `docs/issues/chore/61-chore-neural-fly-sac-episodes/` (third issue to use it); writes `algo.fire` into the run's config and says so in the notes.
#### Verification
- `uv run pytest -q`: 209 passed (205 before, 2 new tests here; the suite was first run before `npm ci`, where `test_viewer_attitude` failed for lack of `node_modules`, and passed after it).
- New tests: the policy sees the observation minus `shot`, the action is 3 values, `fire` equals the baseline rule over a 40-step chase that both fires and does not; a version 5 PPO stub (17-dim observation, 2-dim action) loads with `fire == "rule"` and plays an episode; version 4 is refused.
- On seeds 10000-10002 (rule fly) the three `sac-beam-assist` models capture 9/9 in 3.07, 2.75, 1.65 / 3.03, 2.61, 8.71 / 1.31, 1.33, 2.41 s; under version 5 on this machine they took 3.03, 2.73, 1.63 / 3.02, 2.59, 5.37 / 1.29, 1.19, 2.40 s (#61). Eight of nine are within one shot length of the version 5 time; s1 on seed 10002 misfires 8 times.
#### Notes
- The steering cannot be compared frame by frame with the published version 5 episodes: those were recorded on the vast.ai instance and differ from this machine by up to 0.04 rad within an episode (float differences that grow along a trajectory).
- The file move of `record_match.py` (rename only) went into the registration commit b7641f4 by mistake: it was already staged by `git mv` when that commit was made. Its content edits are in this commit.
- A side effect worth knowing: `train.py --opponent <version 5 aimer run>` for the fly now works under version 6 too, since it also goes through `load_opponent`.

### chore: 조준기 v0과 v1 후보를 재고 판정하기 (#72)
> why: whether the SAC aimer becomes v1 was to be decided by a rule written before measuring, and the rows kept for later analysis
#### Scope
`docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/`: `gate.md` (pre-registration and verdict), `gate/`, `data/`, `measure_aimers.py`, `run_gate.py`. No package code.
#### Changes
- `measure_aimers.py`: one aimer per call (`baseline` or a model run), writes `episodes.csv`, `shots.csv`, `gate.csv`, `meta.json`; `mean` pools the three models per seed. `run_gate.py`: every bootstrap named in the gate, output to `gate/bootstrap-<fly>.md`.
- `gate.md`: question, frozen baseline (sha256), candidate, metric, threshold 0.90 on time, exclusions (capture below 0.97, a model below 0.50, misfires above twice v0's), the neural fly as reported-only, then the verdict.
- `data/`: 12 folders (3 fly settings x 4 aimers), 200 seeds for the rule fly and 60 for the neural fly, and a README with re-run commands.
#### Verification
- Verdict: **adopt**. Rule fly, 200 seeds: v0 4.894 s, 198/200, 0.50 misfires per episode; candidate 3.026 s, 584/600 (0.973), 0.60 misfires; P(faster) 1.000 pooled and for each model; no exclusion fired (capture by two episodes of 600).
- Neural fly, 60 seeds, reported only: stimulus off v0 5.110 s, 59/60, 0.62 misfires vs candidate 4.258 s, 155/180 (0.861), 1.94 misfires; stimulus on v0 5.397 s, 59/60, 1.93 misfires vs candidate 4.058 s, 164/180 (0.911), 2.04 misfires. Faster on average, loses many more flies; one model (s0, stimulus off) is slower than v0.
- The baseline's rule-fly rows equal #69's (`198/200, 4.894 s, 1.49 shots, 0.50 misfires`).
- `paired_bootstrap.py`: 10,000 resamples, seed 42; unedited output with file hashes in `gate/bootstrap-*.md`.
#### Notes
- Deviations are listed at the end of `gate.md`: the gate text was written before measuring but not committed before it; every `meta.json` has `gitDirty: true` (code as in a4a6c12); the `+rule-fire` label suffix appears in the stimulus-on `meta.json` files only.
- The misfire rule in the gate was written after seeing 9 pilot episodes on non-gate seeds (12 misfires, 8 in one episode); the gate says so.
- `run_gate.py` first crashed printing the tables to a cp949 console after the file had been written; it now prints the path only.

## Management Notes
### Follow-up Candidates
- Aimer v2: SAC that learns to fire, on observations with the detector's error (#13); decide the misfire term of the reward there.
- Move the shot length from `EnvConfig.capture_hold` to the aimer's settings once the teammate's branch can take a config key change.
### References
- #51 SAC under the laser rule (the models), #61 SAC vs neural fly under version 5, #69 fire action and misfires (env version 6), #13 detector.
