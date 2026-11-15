# 49 레이저 명중에 맞춰 조준기 보상 바꾸기

## Document Relations
- Issue: #49
- Branch: `49-feature-laser-beam-reward`
- Umbrella: (none)
- Status: in progress

## Summary
Replace the aimer's aim-error penalty, which is linear in angle and nearly flat below 1°, by a penalty on the log-scaled distance from the fly to the beam, so that the reward still changes over the last millimetres before a laser hit (capture radius 1.25 mm). `ENV_VERSION` 4 → 5; the old penalty stays available through reward weights so runs under both rewards can be compared.

## Goal
- A dense reward term that keeps a usable gradient from about 1 m down to the capture radius.
- The previous reward remains selectable per run (`--reward beam=0 angle=0.05`), because the next issue trains SAC under several conditions and compares them.

## Scope
1. `RewardWeights`: new `beam` (0.1) and `beam_far` (1.0 m); `angle` default 0.05 → 0. Penalty while visible: `beam * min(log1p(d / capture_radius) / log1p(beam_far / capture_radius), 1) + angle * (aim error / half FOV)`.
2. `FlyRewardWeights` mirrors it (`beam` 0.1, `angle` 0), keeping the fly's reward the sign-flipped aimer reward as the README states.
3. `--reward item=value ...` in the shared env options (`train.py`, `record_baseline.py`).
4. Tests, README (aimer R, fly R, training options, baseline return, version), one published version-5 baseline run for side-by-side viewing with later training runs.

## Out Of Scope
- Training. Whether SAC learns under this reward is not tested here; it is the next issue, with a pre-registered gate and several conditions (old reward, new reward, residual on the baseline tracker).
- Positive shaping (a bonus while on the beam): not added, because on-off-on farming becomes possible; all dense terms stay penalties.
- The fly side's own reward design beyond mirroring.

## Done Criteria
- [x] Reward computed as specified; tests cover the values at 0, 1.25, 12.5 and 125 mm, the cap at `beam_far`, visible always better than lost, the old reward by weights, the option parser, and the fly mirror. (2026-11-15)
- [x] `ENV_VERSION` 5 with the version comment. (2026-11-15)
- [x] `uv run python -m pytest -q` passes; the teammate's fixed rollout sum in `tests/test_neural_fly.py` (skipped here) still holds. (2026-11-15: 122 passed, 45 skipped; rollout sum recomputed by a local script, −4.99468802723724 for both seeds, the fly is never visible in those 30 steps)
- [x] Baseline re-measured on seeds 10000-10199 and README updated. (2026-11-15: 200/200, 4.95 s, mean return −23.13)
- [x] One version-5 baseline run published. (2026-11-15)

## Current State
2026-11-15: implemented and verified in the working tree; committing, then PR and merge at the user's request (they asked for the reward issue to be done and merged, then SAC training).

The weights are starting values chosen by reasoning, not by experiment: `beam` 0.1 keeps the visible penalty below `lost` (0.15) and makes one decade of distance worth about 0.034 per step against the 0.01 time penalty.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 레이저 명중에 맞춰 조준기 보상 바꾸기 (#49)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
`docs/issues/feature/49-feature-laser-beam-reward.md`, `docs/issues/README.md`, `AGENTS.md`.
#### Changes
- Management doc filled, registry row and `AGENTS.md` pointer added by `issue-start`.
#### Verification
- `issue-start` real run: issue #49, branch from `origin/main` @ d38e931 (contains #45 and #44).
#### Notes
- None.

### feat: 보일 때의 벌점을 빔까지 거리의 log 눈금으로 (#49)
> why: the aim-error penalty differs by 0.0024 per step between 1° and a hit, a quarter of the time penalty, so nothing but the sparse capture reward rewards closing the last millimetres
#### Scope
`flytracker/env.py`, `scripts/_common.py`, `tests/test_reward.py`.
#### Changes
- `RewardWeights.beam` 0.1, `beam_far` 1.0 m, `angle` 0.05 → 0; `_beam_ratio()`; `FlyRewardWeights` mirrors `beam` and `angle`. `ENV_VERSION` 5.
- `--reward item=value ...` (shared env options) builds `RewardWeights`; unknown items stop with a message.
#### Verification
- `uv run python -m pytest -q`: 122 passed, 45 skipped. New `tests/test_reward.py` (10 cases).
- `runs/_ops/check_rollout.py` (local): the rollout that `tests/test_neural_fly.py::test_default_rule_matches_prechange_rollout` pins gives −4.99468802723724 for seeds 0 and 123, unchanged, because the fly is not visible in those steps.
- `scripts/record_baseline.py --episodes 200 --seed 10000 --no-save`: 200/200, mean return −23.13, visible 30 %, 4.95 s. With `--reward beam=0 angle=0.05`, seed 10000 returns −23.57, the version-4 value.
#### Notes
- Penalty values: 0 on the beam, 0.010 at 1.25 mm, 0.036 at 12.5 mm, 0.069 at 125 mm, 0.1 from 1 m.

### feat: 버전 5 기준선 실행 올리기 (#49)
> why: episode files store per-step rewards, so the version-4 baseline run cannot sit next to version-5 training runs in the viewer
#### Scope
`published/2026-11-15_223016_baseline/`.
#### Changes
- `record_baseline.py --episodes 5 --seed 10000` (5/5, mean return −23.24, 4.87 s), published with `publish_run.py --issue 49`.
#### Verification
- `npm run build --prefix viewer`; `viewer/dist/runs/index.json` lists the run under issue 49.
#### Notes
- None.

## Management Notes
### Follow-up Candidates
- SAC training under version 5 with several conditions and a pre-registered gate (next issue).
- Tuning `beam` / `beam_far` if training shows the term is too weak or too strong.
### References
- `docs/issues/feature/45-feature-laser-tracking-baseline.md` (observation and baseline this builds on).
- `docs/issues/feature/42-feature-laser-hit-capture/laser-capture-condition.md` (capture rule).
