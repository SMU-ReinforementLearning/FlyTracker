# 51 레이저 명중 조건에서 SAC로 조준기 다시 학습하기

## Document Relations
- Issue: #51
- Branch: `51-feature-sac-laser-training`
- Umbrella: (none)
- Status: in progress

## Summary
Train SAC aimers under environment version 5 (laser-hit capture, 17-dim observation, log-scaled beam-distance penalty) in four conditions — new or previous dense reward, policy alone or correcting the baseline's tracker — and gate each against the rule baseline with rules written before training. Models from before version 4 cannot be loaded, and under the laser rule #35's models caught 1/1200.

## Goal
- Learn whether SAC can catch the fly under the laser rule at all, and whether it is faster than the rule baseline (200 evaluation seeds, pre-registered gate).
- Make the conditions comparable: the same seeds, steps and settings, differing only in reward and control, each published as its own runs (the user asked for several conditions that can be compared with the earlier phase, each uploaded separately).

## Scope
1. Tracking assist: `RuleAimer.track` / `assisted`, `wrappers.TrackingAssist`, `make_env(assist=)`, `train.py --assist`, `PolicyPlayer` and `load_opponent` rebuild it from `config.json` (`algo.assist`). Not an environment change; `ENV_VERSION` stays 5.
2. Gate: `51-feature-sac-laser-training/gate.md`, `evaluate_gate.py`, frozen baseline and truth files.
3. Training: 4 conditions x 3 seeds x 500,000 steps on the local machine.
4. Evaluation, verdicts, published runs, README (training options, results), a Korean result note if the results need more room than the README.

## Out Of Scope
- Tuning reward weights, the assist scale or SAC hyper-parameters after seeing results (a new gate).
- The fly side; detection noise and latency (#13).

## Done Criteria
- [ ] Tracking assist implemented and tested; a model trained with it is loaded with the same assist by `load_opponent`.
- [ ] Gate document complete above "Verdict" and committed before the first training run starts.
- [ ] 12 runs reach 500,000 steps.
- [ ] Each candidate evaluated on seeds 20000-20199; bootstrap output and verdicts written into `gate.md`.
- [ ] Runs published under issue #51; `viewer/dist/runs/index.json` lists them.
- [ ] README updated; `uv run python -m pytest -q` and `npm run build --prefix viewer` pass.

## Current State
2026-11-15: tracking assist implemented (tests pass), gate written, baseline frozen (198/200, 4.858 s on seeds 20000-20199). Next: commit seed, assist and gate, then launch the 12 runs with `runs/_ops/launch.sh` (local, gitignored). Logs go to `runs/_ops/logs/<name>.log`.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 레이저 명중 조건에서 SAC로 조준기 다시 학습하기 (#51)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
`docs/issues/feature/51-feature-sac-laser-training.md`, `docs/issues/README.md`, `AGENTS.md`.
#### Changes
- Management doc filled, registry row and `AGENTS.md` pointer added by `issue-start`; issue labelled `training`.
#### Verification
- `issue-start` real run: issue #51, branch from `origin/main` @ c4dd7e1 (contains #45 and #49).
#### Notes
- None.

## Management Notes
### Follow-up Candidates
### References
- `docs/issues/feature/35-feature-sac-aimer-training/gate.md` (the gate this one follows).
- `docs/issues/feature/49-feature-laser-beam-reward.md`, `docs/issues/feature/45-feature-laser-tracking-baseline.md`.
