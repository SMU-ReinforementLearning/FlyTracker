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
- [ ] Version 5 aimer models load under version 6 with rule firing; tests cover the observation slice, the fire rule and the version check.
- [ ] Gate document written before the candidate is measured on the gate seeds; baseline frozen by sha256.
- [ ] Candidate measured on seeds 20000-20199 (three models) and against the neural fly (60 seeds, stimulus off and on); raw rows committed.
- [ ] Verdict appended to the gate document.
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

## Management Notes
### Follow-up Candidates
- Aimer v2: SAC that learns to fire, on observations with the detector's error (#13); decide the misfire term of the reward there.
- Move the shot length from `EnvConfig.capture_hold` to the aimer's settings once the teammate's branch can take a config key change.
### References
- #51 SAC under the laser rule (the models), #61 SAC vs neural fly under version 5, #69 fire action and misfires (env version 6), #13 detector.
