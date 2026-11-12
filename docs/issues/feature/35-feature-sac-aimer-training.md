# 35 SAC로 조준기 학습하기

## Document Relations
- Issue: #35
- Branch: `35-feature-sac-aimer-training`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #34 (alternate training of aimer and fly; this issue trains the aimer alone against the scripted fly), #13 (detection model, not implemented — the aimer still sees the fly perfectly inside the frame)
- Status: in progress

## Summary
First reinforcement-learning run for the aimer: train SAC with `scripts/train.py` on the current environment and compare the trained aimer with the rule baseline on a pre-registered gate. Until now the repo has only baseline runs; nobody has trained an agent yet.

## Goal
- SAC (Stable-Baselines3 defaults) trained on the default `EnvConfig`, environment version 2, 3 training seeds, two observation settings: frame stack 1 and 4.
- Gate: does SAC capture the fly more often than the rule baseline on 200 held-out evaluation seeds? Written before any candidate number is seen.
- A short Korean explainer of SAC for the team, in this issue's folder.

## Scope
- Environment version 2: the code part of #34's commit f8cfa78 (`flytracker/{__init__,aimer,baseline,env,record}.py`, `tests/test_env.py`, `tests/test_record_and_baseline.py`) applied unchanged. The user asked to train on version 2 before #34 merges. The hunks are identical to #34's, so whichever branch merges second sees them already present; the `ENV_VERSION` history comment may need a one-line conflict resolution because #34 extended it later.
- `docs/issues/feature/35-feature-sac-aimer-training/` — SAC explainer (Korean), gate document, evaluation script, baseline and candidate per-seed CSVs.
- Training runs on a rented vast.ai instance (the user allowed it); run folders copied back to the local `runs/`.

## Out Of Scope
- Changes to the environment, reward weights, action space or the baseline.
- Hyper-parameter tuning beyond the two pre-registered frame-stack settings.
- DQN with a wider discrete action set (discussed with the user; a separate issue if wanted).
- Publishing runs to `published/` — asked of the user once the results are in.

## Done Criteria
- [x] Gate document with frozen baseline CSV (sha256) written before training starts. (2026-11-12 22:10)
- [ ] 6 SAC runs (frame stack 1 and 4 × seeds 0, 1, 2) finish 1,000,000 steps each; run folders and final models copied back.
- [ ] Final models evaluated on seeds 20000-20199; paired bootstrap verdict appended to the gate document.
- [x] SAC explainer written, passed `check.py` and a cold-reader review. (2026-11-12 22:40)
- [ ] `uv run pytest` passes (no code changes expected; re-run before the last commit).

## Current State
- Issue #35, branch and worktree created from `origin/main` @ 0cda845. `uv sync --extra train --extra dev` done in the worktree; `uv run pytest`: 33 passed.
- Local throughput is too low for 1M-step runs: SAC learns at 41 steps/s on one thread, 68 steps/s on four (laptop CPU; one 256×256 MLP update takes 2.9 ms). The user allowed a vast.ai instance; account has $15.27 credit.
- The user asked to train on environment version 2. f8cfa78's code part applied; `uv run pytest`: 37 passed. Gate written: `docs/issues/feature/35-feature-sac-aimer-training/gate.md`; baseline re-frozen on version 2 (199/200 captures, 4.100 s mean) and cross-checked byte-identical against branch 34 HEAD 50c05b7.
- vast.ai instance 60356096 (Ryzen 9 7900X, 24 cores, 61 GB, $0.157/h, label `flytracker-35-sac`, `ssh -p 28112 root@ssh1.vast.ai`) rented 2026-11-12 21:43 KST; destroy it when the runs are copied back.
- Instance setup: PyPI's CUDA torch download stalled at ~120 KB/s, so the venv was rebuilt with torch 2.15.0+cpu from download.pytorch.org and every other package at its `uv.lock` version (`uv export` minus torch/nvidia); `pytest` there: 37 passed. Runs use `/root/ft/.venv/bin/python`, not `uv run` (which would re-sync to the CUDA wheel).
- 6 runs started 2026-11-12 22:15 KST under `/root/ft/runs/` (logs `/root/ft/logs/sac-fs{1,4}-s{0,1,2}.log`, progress `python /root/progress.py`): about 120 steps/s each, so about 2.3 h; expected end around 00:40 KST.
- Next: when all 6 `model.zip` exist, run `evaluate_gate.py model` for each on the instance, `evaluate_gate.py mean` per candidate, copy `runs/` (without checkpoints) and the CSVs back, destroy the instance, run `paired_bootstrap.py` as written in `gate.md`, append the verdict.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: SAC로 조준기 학습하기 (#35)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/feature/35-feature-sac-aimer-training.md` filled from the conversation: the user asked which RL algorithm suits the aimer and whether DQN's discrete actions are a problem; the recommendation was SAC on the native 2-D continuous action, with DQN needing a wider action set; the user asked to open an issue, train, and document SAC in plain Korean.
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start`: issue #35, branch from `origin/main` @ 0cda845.
#### Notes
- No umbrella issue exists, so `--parent` was not passed.

### feat: 환경 버전 2(pitch 89°) 가져오기 (#35)
> why: the user asked to train on environment version 2, which lives on #34's unmerged branch
#### Scope
- `flytracker/__init__.py`, `flytracker/aimer.py`, `flytracker/baseline.py`, `flytracker/env.py`, `flytracker/record.py`, `tests/test_env.py`, `tests/test_record_and_baseline.py`.
#### Changes
- The code part of #34's commit f8cfa78, applied unchanged with `git diff c998454 f8cfa78 -- flytracker tests | git apply` (c998454 is its parent; both branches start at `origin/main` @ 0cda845): `AimerLimits.max_pitch_deg` 80 → 89, `RuleAimer` stops adding sweep bands once the zenith is in view, `ENV_VERSION = 2`, `RunStore.create_run` writes `envVersion` into `config.json`, tests for both.
- README and #34's management doc from that commit are not taken; they belong to #34.
#### Verification
- `uv run pytest`: 37 passed (f8cfa78's own record: 37 passed).
- Gate baseline on seeds 20000-20199 with this code and with branch 34 HEAD 50c05b7's `flytracker` package (learned-fly slot added): byte-identical CSVs, so the aimer's environment against the rule fly is the same in both.
#### Notes
- When #34 merges first, rebasing this branch may stop on the `ENV_VERSION` history comment, which #34 extended after f8cfa78; take #34's line.

## Management Notes
### Follow-up Candidates
- DQN with a 5×5 joint discrete action set as a comparison (the current 5 actions turn one axis per step).
### References
- Haarnoja et al., 2018, "Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor" (ICML).
- Haarnoja et al., 2018, "Soft Actor-Critic Algorithms and Applications" (arXiv:1812.05905) — automatic entropy temperature.
