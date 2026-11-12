# 34 조준기와 초파리를 번갈아 학습하는 환경 만들기

## Document Relations
- Issue: #34
- Branch: `34-feature-fly-vs-aimer-env`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #31 (connectome fly model; the plan agreed there is the source of this issue's scope, https://github.com/SMU-ReinforementLearning/FlyTracker/issues/31#issuecomment-6823169259), #9 (fly flight model and its limits), #7 (fixed turret)
- Status: in progress

## Summary
Prepares the environment so the aimer and a learned fly can be trained in turns, each against a frozen version of the other. The aimer side is the repo owner's work; the fly side (a connectome-shaped network trained to evade, #31) is a teammate's. This issue does the shared environment work the #31 plan listed under "먼저 바꿀 환경", before the first aimer is trained.

## Goal
- Pitch limit 80° → 89°, so the cone straight above the turret (elevation > 83°) is no longer uncapturable. 90° is not allowed: `camera_basis` degenerates there.
- The fly's escape decision can come either from the current rule (fly v0) or from a policy: the policy decides when to escape, which way to turn, and how fast to go, within the current `FlyParams` limits. Normal flight (segments and saccades) stays rule-based.
- The fly sees the aim line (green laser assumption) and receives its observation 3 steps (0.06 s) late, matching the rule fly's reaction delay.
- A fly-side Gymnasium environment where the aimer slot holds the rule baseline or a frozen aimer model.
- A match script: aimer versions × fly versions, same seeds, capture rate and mean time to capture.
- An environment version number written to every run's `config.json`; the match script refuses to compare models from different environment versions.

## Scope
- `flytracker/aimer.py`, `flytracker/baseline.py`: pitch limit.
- `flytracker/fly.py`: external escape commands next to the rule escape; the rule path keeps its RNG sequence.
- `flytracker/env.py`: shared step core, fly observation with delay, fly policy slot, fly-side environment, environment version.
- `flytracker/players.py` (new): loading an aimer or fly opponent from `baseline` / `rule` / a run folder / a checkpoint.
- `flytracker/record.py`: `envVersion` in `config.json`.
- `scripts/train.py`: `--side aimer|fly` and `--opponent`.
- `scripts/match.py` (new).
- `tests/`, `README.md`.

## Out Of Scope
- The connectome network itself, its inputs and outputs, and the final fly reward (teammate, #31). This issue ships starting defaults only.
- Training an aimer or a fly beyond the few steps needed to test loading.
- Mixing several opponents in one training run (plan step 3; later issue).
- Viewer changes (the frame format does not change).
- The detection model (#13).

## Done Criteria
- [ ] Rule fly v0 flies the same path as before for the same seed (checked against `origin/main` on 50 seeds).
- [x] A fly directly above the turret can be captured; pitch stops at 89°. (2026-11-12)
- [ ] Fly observation at step k equals the undelayed observation at step k−3; an escape command turns and speeds the fly within the limits and respects the cooldown.
- [ ] `check_env` passes for both sides; SB3 trains a few steps on each side and the saved models load back as opponents.
- [ ] `scripts/match.py` prints the table for baseline × rule and for small saved models, and refuses a model from another environment version.
- [x] Baseline re-measured on seeds 10000–10199 with the 89° limit; README updated. (2026-11-12)
- [ ] `uv run pytest` passes.

## Current State
- Issue, branch and worktree created from `origin/main` @ 0cda845.
- Fly-side starting defaults approved by the user (2026-11-12) and announced on #31 (https://github.com/SMU-ReinforementLearning/FlyTracker/issues/31#issuecomment-6823604205): observation 17 dims delayed 0.06 s (turret direction and distance, nearest point on the laser beam, aim error, speed and climb, room position, heading, escape ready); action 4 dims (escape or not, turn relative to heading ±180°, climb, speed gain 1–1.6); reward = sign-flipped aimer reward without the action-change term. README must document the fly-side observation, action and reward (user request).
- Commit plan: (1) this doc; (2) pitch 89°, env version, baseline re-measure; (3) fly escape slot, fly-side env, `train.py --side/--opponent`; (4) `scripts/match.py`; (5) README.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 조준기와 초파리를 번갈아 학습하는 환경 만들기 (#34)
> why: the #31 plan assigned the shared environment changes to the repo owner; they asked for the work to be done
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- This document filled from the #31 plan (comment linked above) and the conversation: pitch 89°, green laser, 0.06 s reaction delay, fly escape chosen by a policy within `FlyParams` limits, alternating training, version table.
#### Verification
- `issue-start`: issue #34, branch from `origin/main` @ 0cda845.
#### Notes
- No umbrella issue exists, so `--parent` was not passed.

### feat: 조준기 pitch 제한을 89°로 올리고 환경 버전 기록하기 (#34)
> why: with an 80° limit a fly straight above the turret (elevation > 83°) could never be captured; a learned fly would camp there. Runs also need a version number so models trained under different assumptions are not compared.
#### Scope
- `flytracker/aimer.py`, `flytracker/baseline.py`, `flytracker/env.py`, `flytracker/record.py`, `flytracker/__init__.py`, `tests/test_env.py`, `tests/test_record_and_baseline.py`, `README.md`.
#### Changes
- `AimerLimits.max_pitch_deg` 80 → 89 (90 degenerates `camera_basis`). `RuleAimer` default follows; its sweep bands now also stop once a band's top edge reaches the zenith, so the bands stay 10°/45°/80° instead of gaining a useless 89° band.
- `ENV_VERSION = 2` in `env.py` with a per-version history comment; `RunStore.create_run` writes `envVersion` into every `config.json` (the viewer's comparison table shows it as a column when runs differ).
- README: 89° in the observation and action text, baseline table re-measured, environment version paragraph.
#### Verification
- `uv run pytest`: 37 passed (new: overhead fly captured at 89°, not at 80°; `envVersion` in `config.json`; sweep bands unchanged).
- `scripts/record_baseline.py --episodes 200 --seed 10000 --no-save`: before 200/200, 4.21 s, 18 %, −19.22; after 200/200, 4.20 s, 18 %, −19.21.
- Rule fly paths for seeds 0–49 (zero aimer action, 25,050 frames) saved from the pre-change code in the session scratchpad, for the next unit's refactor check.
#### Notes
- The published baseline run (`published/2026-11-11_133858_baseline`) has no `envVersion`; README states that means version 1.

## Management Notes
### Follow-up Candidates
- Opponent mixing for aimer v2 (train against fly v1 and v0 together).
### References
- #31 plan comment: https://github.com/SMU-ReinforementLearning/FlyTracker/issues/31#issuecomment-6823169259
