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
3. Training: 4 conditions x 3 seeds x 1,000,000 steps on a rented vast.ai instance (the user's instruction, 2026-11-15).
4. Evaluation, verdicts, published runs, README (training options, results), a Korean result note if the results need more room than the README.

## Out Of Scope
- Tuning reward weights, the assist scale or SAC hyper-parameters after seeing results (a new gate).
- The fly side; detection noise and latency (#13).

## Done Criteria
- [ ] Tracking assist implemented and tested; a model trained with it is loaded with the same assist by `load_opponent`.
- [ ] Gate document complete above "Verdict" and committed before the first training run starts.
- [ ] 12 runs reach 1,000,000 steps.
- [ ] Each candidate evaluated on seeds 20000-20199; bootstrap output and verdicts written into `gate.md`.
- [ ] Runs published under issue #51; `viewer/dist/runs/index.json` lists them.
- [ ] README updated; `uv run python -m pytest -q` and `npm run build --prefix viewer` pass.

## Current State
2026-11-16 00:25 KST: the 12 runs are training on vast.ai instance 60797094 (ssh target in `runs/_ops/ssh_target.txt`, `root@175.143.181.143 -p 60362`), started 2026-11-15 15:17 UTC, about 49 steps/s per run, so they end around 2026-11-15 21:00 UTC (06:00 KST). The instance costs about $0.14 per hour and keeps billing until it is destroyed.

The remote job (`/root/ft/remote_train.sh`, a copy of `runs/_ops/remote_train.sh`) needs no laptop: after training it evaluates the 12 models on seeds 20000-20199, averages per condition, packs `/root/gate_out.tgz` and `/root/runs-g51.tgz` with `/root/manifest.sha256`, and writes `/root/ft/state/RESULTS_READY` (or `state/FAILED`).

Next, in order: (1) `bash runs/_ops/fetch.sh` — downloads, verifies sha256, extracts runs to `runs/g51/` and CSVs to the gate folder, destroys the instance only when every check passed; (2) `bash runs/_ops/run_gate.sh boot > .../gate/bootstrap-output.md` and write the verdicts into `gate.md`; (3) publish the 12 runs with `publish_run.py --runs-dir runs/g51/<name> --issue 51`; (4) README results, work log, pointer removal, PR, merge (the user asked for the merge).

Trap: a vast `python:3.11-bookworm` instance forces tmux on ssh and runs no command unless `/root/.no_auto_tmux` exists; create the instance with `--onstart-cmd "touch /root/.no_auto_tmux"`. Parallel `train.py` runs need separate `--runs-dir`.

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

### feat: 정책 행동에 기준선 추적을 더하는 assist (#51)
> why: one training condition lets the policy correct the baseline's tracker instead of steering alone; SAC's exploration noise is far larger than the 0.13 % action precision a hit needs
#### Scope
`flytracker/baseline.py`, `wrappers.py`, `players.py`, `scripts/train.py`, `tests/test_assist.py`.
#### Changes
- `RuleAimer.track(obs)` (the tracking law, stateless) and `assisted(obs, action, scale)`: tracking + scale x policy action while visible, the policy's action otherwise.
- `wrappers.TrackingAssist`, `make_env(assist=)`, `train.py --assist`, `algo.assist` in `config.json`; `PolicyPlayer` / `load_opponent` apply the same assist. `baseline_player` passes the camera and rate limits of the config.
#### Verification
- `uv run python -m pytest -q`: 126 passed, 45 skipped. New `tests/test_assist.py`: the action reaching the env is tracking + 0.2 x policy while visible and the policy's own otherwise; a zero policy with assist captures a fly it starts facing; a `PolicyPlayer` with assist reproduces the wrapper's actions and observations step by step; discrete actions are refused.
- Smoke: `train.py --algo sac --steps 6000 --assist 0.2` runs and saves; `evaluate_gate.py model` loads it (0/5 on 5 seeds, untrained).
#### Notes
- Throughput on this machine is about 50 steps/s per run (6,000 steps in about 2 minutes, with or without `OMP_NUM_THREADS=1`).

### docs: SAC 학습 판정 기준을 학습 전에 적기 (#51)
> why: the comparison rules have to exist before any candidate is measured
#### Scope
`docs/issues/feature/51-feature-sac-laser-training/gate.md`, `evaluate_gate.py`, `gate/baseline.csv`, `gate/truth.csv`.
#### Changes
- Gate: four candidates (2 rewards x policy alone / tracking assist 0.2), 3 training seeds, 500,000 steps, time to capture on seeds 20000-20199, paired bootstrap P ≥ 0.90, capture-rate exclusion 0.97, per-seed exclusion, no selection among candidates.
- `evaluate_gate.py`: as in #35, but models are loaded with `load_opponent` so the assist is rebuilt.
- Baseline frozen: 198/200, mean time 4.858 s, sha256 `6ac2f0bd…`.
#### Verification
- `sha256sum` of both files matches `gate.md`. No training run of this issue had started when this was committed.
#### Notes
- 500,000 steps instead of #35's 1,000,000 because of local throughput; stated in the gate as part of the candidate.

### docs: 판정 기준을 100만 step과 인스턴스 학습으로 고치기 (#51)
> why: the user asked for 1,000,000 steps on a rented instance; the gate has to say so before any candidate is measured
#### Scope
`51-feature-sac-laser-training/gate.md`, this doc, `README.md` (the `--assist` option).
#### Changes
- Gate: steps 500,000 → 1,000,000, platform and device lines, an amendment note with what existed at that time.
- README: `--assist` in the training options.
- Current State rewritten as a resume note: instance, timing, the remote job's markers, the next steps in order.
#### Verification
- On the instance: setup log shows torch 2.15.0+cu132, env version 5, 38 tests passed (`test_env`, `test_reward`, `test_assist`, `test_players`); 12 `train.py` processes alive; throughput check cpu 88 s vs cuda 107 s.
- Local runs: 24 python processes stopped, `runs/g51/` deleted before anything was evaluated.
#### Notes
- The first instance (60796025) was destroyed after a few minutes: ssh ran no command because of the forced tmux login.

### docs: SAC 네 조건의 판정 결과 적기 (#51)
> why: the 12 runs finished; the verdicts go into the gate exactly as the pre-written rules say
#### Scope
`51-feature-sac-laser-training/gate.md` (Verdict), `gate/*.csv` (16 prediction files), `gate/*-gate.json`, `gate/bootstrap-output.md`. Also the merge of `origin/main` (#47) into the branch just before.
#### Changes
- Verdict: `sac-beam-assist` adopt (2.941 s vs 4.858 s, P = 1.000 pooled and per seed, 585/600 captured); `sac-beam` (21/600), `sac-angle` (3/600), `sac-angle-assist` (127/600) reject. One of four passed.
- Unedited bootstrap output with every file's sha256.
#### Verification
- 12 `model.zip` and 12 `step_1000000.zip` present; remote marker `training ended with 12 models` (2026-11-15T21:06:48Z).
- `fetch.sh`: `sha256sum -c` OK for both archives, 16 CSVs of 201 lines; instance 60797094 destroyed afterwards, `vastai show instances` lists none.
- Baseline and truth sha256 in the output equal the frozen ones.
#### Notes
- The prediction files were produced on the instance (as the gate says); they were not re-evaluated locally.

### feat: SAC 실행 12개 올리고 viewer에 추적 보조 보여 주기 (#51)
> why: every condition is published separately so they can be compared in the viewer (the user's request); without an assist row two conditions looked identical on the issue page
#### Scope
`published/2026-11-15_151701_sac-*` (12 runs), `published/issues/51.json`, `viewer/src/data/experiment.js`, `ui-text.glossary.md`, `README.md`.
#### Changes
- 12 runs published with `publish_run.py --runs-dir runs/g51/<name> --issue 51` (55 MB; 63 episodes each: 21 checkpoints x seeds 10000-10002).
- `published/issues/51.json`: phase, purpose with the results, compare 49. No `aimer` version label: three of the four conditions failed and the label would apply to all cards.
- Viewer: learned-aimer card gains a "추적 보조" row from `algo.assist` ("없음" / "기준선 추적 + 행동 × 0.2"); glossary row added.
- README: results table for the four conditions next to the baseline, link to the gate.
#### Verification
- `uv run python -m pytest -q`: 139 passed, 45 skipped (includes the issue-info file check from #47).
- `npm run build --prefix viewer` passes; `viewer/dist/runs/index.json` lists 26 runs, 12 with issue 51; `dist/runs/issues/51.json` present.
- `variationsOf` on the 12 published configs gives four variations labelled by 추적 보조, 빔까지 거리 벌점, 조준 오차 벌점.
- `ko-writing` `check.py README.md`: no new finding in the added paragraph.
#### Notes
- The page was not opened in a browser; the variation labels (for example "없음, 0.1, 0") are correct but terse.

## Management Notes
### Follow-up Candidates
### References
- `docs/issues/feature/35-feature-sac-aimer-training/gate.md` (the gate this one follows).
- `docs/issues/feature/49-feature-laser-beam-reward.md`, `docs/issues/feature/45-feature-laser-tracking-baseline.md`.
