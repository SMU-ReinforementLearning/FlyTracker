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
- Gate: does SAC catch the fly faster than the rule baseline (mean time to capture, misses counted as 10 s) on 200 held-out evaluation seeds? Written before any candidate number is seen.
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
- [x] 6 SAC runs (frame stack 1 and 4 × seeds 0, 1, 2) finish 1,000,000 steps each; run folders and final models copied back. (2026-11-13 00:52)
- [x] Final models evaluated on seeds 20000-20199; paired bootstrap verdict appended to the gate document. (2026-11-13 01:03)
- [x] SAC explainer written, passed `check.py` and a cold-reader review. (2026-11-12 22:40)
- [ ] `uv run pytest` passes (no code changes expected; re-run before the last commit).

## Current State
Read only this block to take over. As of 2026-11-13 01:05 KST. Training, evaluation and the gate are done; the instance is destroyed. What is left is publishing the runs, the PR, and reporting to the user (asleep; approved publishing, push and PR on 2026-11-13).

### Fallback that is certain
Nothing ships from this issue. Local results: `runs/2026-11-12_131635_sac-fs{1,4}-s{0,1,2}/` in this worktree (final `model.zip`, 21 checkpoints, episodes, TensorBoard). Backup, independent of this worktree: `C:/Users/neighbor/Documents/Code/Github/FlyTracker/runs/_backup-issue35/runs-full.tgz` (sha256 `491888f4a4bb…`, 350 MB) and `gate_out.tgz` (`0bcb10c60926…`), verified after the copy. Restore: `tar -xzf runs-full.tgz -C <worktree>`.

### Running now
Nothing. vast.ai instance 60356096 destroyed at 00:52 KST by `runs/_ops/fetch_and_release.sh` after every check passed; `vastai show instances` lists none.

### Confirmed so far
- Gate (`gate.md` Verdict, raw output `gate/bootstrap-output.md`): both candidates PASS on mean time to capture, P 1.000 vs threshold 0.90. sac-fs1 2.18 s, sac-fs4 2.12 s, baseline 4.10 s. No exclusion fired; sac-fs4's capture rate 0.9717 was 0.0017 above the 0.97 floor. Decision: adopt; no choice between fs1 and fs4.
- SAC misses more flies than the baseline (2.0 % and 2.8 % vs 0.5 %); seed 20112 is missed by all 6 SAC models. Training-rollout episode length is flat from 500k steps on.
- Env v2 = code part of #34's f8cfa78; `uv run pytest` 37 passed locally and on the instance; baseline byte-identical with branch 34 HEAD 50c05b7.
- Commits so far: 629a967, 8050472, 20ae755, 060b28a, 6c1d084 (all with the user's approval).

### Next steps in order
1. Commit the verdict (`docs: SAC 판정 결과 (#35)`): `gate.md`, `gate/*.csv`, `gate/*-gate.json`, `gate/bootstrap-output.md`, this doc.
2. Publish all 6 runs (all 6 so the viewer shows the seed spread; about 15 MB of episode JSON, models excluded): from the worktree root, for each run id `uv run python scripts/publish_run.py <run_id> --issue 35` (issue #35 has the `training` label). Commit `published/` with its own work-log section.
3. `uv run pytest`; remove this branch's pointer from `AGENTS.md` as the last commit; `git push -u origin 35-feature-sac-aimer-training`; open the PR (`Closes #35`); report to the user with the PR URL.

### Today's traps
- PyPI download of the CUDA torch wheel stalled at ~120 KB/s on the instance → the host's PyPI path was slow, download.pytorch.org was 3 MB/s → install torch 2.15.0+cpu from download.pytorch.org (`runs/_ops/remote_launch2.sh`).
- `uv run` on the instance re-syncs the env to `uv.lock` (CUDA torch) → call `/root/ft/.venv/bin/python` directly.
- Bash calls naming the worktree path together with variables, `$(...)` or pipelines into scp/ssh are refused by the worktree-isolation guard → put the command in a script file and run `bash <file>`; plain `cd <worktree> && git ...` works.
- `EnterWorktree` refuses this sibling worktree from a session started in another worktree → work with absolute paths, `cd` inside each command.
- Python `csv` writes CRLF; git stores LF, so a recorded sha256 breaks after checkout → `lineterminator="\n"` (fixed, uncommitted).
- `train.py` stdout is block-buffered into the log, so logs look empty for a long time → read progress from TensorBoard events (`progress.py`).
- Monitor watches expire every 30 min → re-arm `watch_runs.sh`.

### Tools
| script | path | what it does | copied from scratchpad on |
| --- | --- | --- | --- |
| `fetch_and_release.sh` | `runs/_ops/` (gitignored) | download, verify, extract, back up, then destroy the instance | written there 2026-11-12 |
| `progress.py` | `runs/_ops/` and `/root/progress.py` | one line per run: step, fps, record age | 2026-11-12 |
| `watch_runs.sh` | `runs/_ops/` | Monitor loop: progress, stall, crash, death, all done | 2026-11-12 |
| `remote_eval.sh`, `remote_autorun.sh` | `runs/_ops/` and `/root/` | gate evaluation on the instance, auto-start after training | 2026-11-12 |
| `remote_launch2.sh` | `runs/_ops/` | instance setup with CPU torch and the 6 launches (rough; instance-specific) | 2026-11-12 |
| `katex-check/check.js` | `runs/_ops/katex-check/` | renders every formula of an md file with KaTeX strict; `npm install katex markdown-it @vscode/markdown-it-katex` first | 2026-11-12 |
| `evaluate_gate.py` | `docs/issues/feature/35-feature-sac-aimer-training/` | gate CSVs for baseline / model / mean | was already in the repo |
| `run_gate.sh` | `runs/_ops/` | copies the candidate CSVs into `gate/` and runs every bootstrap call of `gate.md` | written there 2026-11-13 |
| `gate_details.py` | `runs/_ops/` | missed seeds, time percentiles, learning curve from TensorBoard | written there 2026-11-13 |

### Open decisions for the user
- None open. Answered 2026-11-13 ("3개 다 진행해"): LF fix committed (060b28a, plus 6c1d084 pinning gate CSVs to LF in `.gitattributes`); publish runs (all 6 chosen; label `training` added to #35); push and open the PR once the verdict is in.

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

### docs: SAC 설명과 학습 판정 기준 (#35)
> why: the user asked for a plain Korean explanation of SAC in the issue docs; the comparison with the baseline is pre-registered before any candidate exists
#### Scope
- `docs/issues/feature/35-feature-sac-aimer-training/` — `sac.md`, `gate.md`, `evaluate_gate.py`, `gate/truth.csv`, `gate/baseline.csv` (all new); this doc.
#### Changes
- `sac.md` (Korean): the aimer as the learner (step, capture, 13-dim observation, 2-dim action), actor and critic, entropy bonus and automatic α with target entropy −2, the DQN-family parts (replay buffer, soft target update, two critics), the loss functions, the training settings table marking which values are SB3 defaults.
- Formulas in KaTeX syntax (`$...$`, `$$...$$`; `\mid` instead of `|` so table cells do not split), each followed by a table of what every term means: entropy, the max-entropy objective, critic target and loss, actor loss with the reparameterised sample and the tanh log-prob correction, α loss, soft target update. The update order is explained as critic → actor → α; SB3 computes the α loss first but uses the pre-update α in both other losses, so the result is the same.
- `gate.md`: question, baseline (frozen sha256), two candidates (`sac-fs1`, `sac-fs4`, 3 training seeds each, final model only), metric = mean time to capture with misses counted as 10 s, 200 seeds 20000-20199, threshold P ≥ 0.90, exclusions (capture < 0.97; a training seed with P < 0.50; unfinished run), decision rule.
- `evaluate_gate.py`: one row per seed (`id`, `capture`, `time`) for the baseline or a saved SAC model, deterministic policy, default `EnvConfig`; `mean` averages the three training seeds.
#### Verification
- Baseline (env v2): 199/200 captures, 4.100 s mean time. Env v1, before the switch: 198/200, 4.127 s (replaced before any candidate existed).
- SB3 2.9.2 SAC defaults read from the installed source (`inspect.signature`, `SACPolicy`, `_setup_model`): lr 3e-4, buffer 1e6, learning_starts 100, batch 256, tau 0.005, gamma 0.99, train_freq 1, gradient_steps 1, ent_coef auto, target_entropy = −dim(A), net_arch [256, 256], n_critics 2.
- Loss formulas checked against the installed SB3 source (`SAC.train`, `SquashedDiagGaussianDistribution.log_prob`, `ReplayBuffer.add`): min over target critics minus α·logπ for the target, `0.5 * sum(mse)` critic loss, `(α·logπ − min Q).mean()` actor loss, `−(log α · (logπ + target_entropy)).mean()` α loss, tanh correction `−Σ log(1 − a² + ε)`, α starts at 1.0, time-limit truncations stored as not-done (`handle_timeout_termination=True`).
- KaTeX 0.19.1 (`throwOnError`, `strict: "error"`): 9 display and 121 inline formulas, 0 errors; markdown-it 15 + `@vscode/markdown-it-katex` HTML: 0 `katex-error`, 10 tables intact. Rendered page screenshotted with headless Chrome and looked at.
- ko-writing `check.py` on `sac.md`: one sentence ending, no heading or demonstrative warnings; the 2 semicolon hits are `\mathcal{N}(u;\, …)` inside formulas.
- Six cold-reader reviews by fresh subagents, findings fixed after each: undefined aimer/yaw/pitch, "점수" ambiguous, two critics appearing unannounced, α direction, "기본값 그대로" vs "바꾼 것", "목표값" clashing with target network, actor "outputs an action" vs "outputs a distribution", "상태" vs "관측", 13-dim breakdown, screen motion caused by the aimer's own rotation; after the formulas: ε used for both ε-greedy and the Gaussian noise (noise renamed ξ), SAC's Q including the entropy bonus, α's initial value, $a'$ vs $\tilde a$, $\bar\theta$ undefined, list order vs section order, "first term" pointing at the wrong term of the actor loss, no term table for the tanh correction, gradient step vs environment step. Left as is: tanh, off-policy, Double DQN, discount γ, TensorBoard (course material for the readers), "issue #35" (the doc sits in that issue's folder), "목표" in 목표 각속도 / 목표 entropy / 목표값 (each is the standard term).
#### Notes
- Capture rate was planned as the gate metric; the baseline's 0.99 left no room, so the metric is time to capture. The change was made after seeing the baseline only.

### fix: 판정 기준 CSV 줄바꿈을 LF로 고정 (#35)
> why: the gate CSVs were written with CRLF (Python `csv` default) but git stores them as LF, so the sha256 in `gate.md` would not match after a checkout
#### Scope
- `evaluate_gate.py`, `gate/baseline.csv`, `gate/truth.csv`, `gate.md`, this doc.
#### Changes
- `evaluate_gate.py` writes with `lineterminator="\n"`.
- Both CSVs re-written; `gate.md` carries the new hashes and a note on the first ones.
#### Verification
- Old and new files compared after stripping `\r`: identical line by line for both.
- New sha256 (baseline `4aec8f8e…`, truth `630ec5b3…`) equal `git show HEAD:<path> | sha256sum` of the blobs committed in 20ae755.
- The instance's copy of `evaluate_gate.py` replaced before any candidate CSV was written.
#### Notes
- No candidate had been measured, so this is still the first gate.

### fix: 판정 CSV를 checkout에서도 LF로 두기 (#35)
> why: with `core.autocrlf=true` (this laptop) a Windows checkout turns the LF blobs back into CRLF, so the hashes in `gate.md` would still break there
#### Scope
- `.gitattributes`, this doc.
#### Changes
- `docs/issues/**/gate/*.csv text eol=lf`, next to the existing `.githooks/** text eol=lf` line.
#### Verification
- Fresh clone of this branch with `core.autocrlf=true`: `sha256sum` of both gate CSVs equals the hashes in `gate.md` (see the commit body for the output).
#### Notes
- The rule covers every issue's `gate/` folder, so later gates get the same guarantee.

### docs: SAC 판정 결과 (#35)
> why: the 6 runs finished; the pre-registered gate decides whether SAC beats the rule baseline
#### Scope
- `gate.md` (candidate hashes, Verdict), `gate/sac-fs{1,4}.csv`, `gate/sac-fs{1,4}-s{0,1,2}.csv`, `gate/sac-fs{1,4}-gate.json`, `gate/bootstrap-output.md` (all new except `gate.md`), this doc.
#### Changes
- Verdict: both `sac-fs1` (2.1836 s, Δ −1.9163 s, CI [−2.1957, −1.6234]) and `sac-fs4` (2.1232 s, Δ −1.9767 s, CI [−2.2707, −1.6688]) beat the baseline's 4.0999 s with P 1.000; every training seed P 1.000; no exclusion fired (sac-fs4 capture 0.9717 vs the 0.97 floor). Decision adopt, no choice between the two settings.
- Written down with it: SAC's miss rate 2.0 % / 2.8 % vs 0.5 % (significant for fs4, CI [+0.0033, +0.0450]); seed 20112 missed by all 6 models; 5 seeds where the baseline is faster than every model; learning curves flat from 500k steps.
- Current State refreshed: instance destroyed, results and backup locations, remaining steps.
#### Verification
- 6 runs reached 1,000,000 steps (`[step_1000000]` lines in each training log, 21 checkpoints each); auto-eval on the instance 15:51:01-15:51:19 UTC.
- `fetch_and_release.sh`: `sha256sum -c` OK for both tarballs after download and again after the backup copy; 6 `model.zip`; 8 gate CSVs with 201 lines each; instance destroyed, `vastai show instances` empty.
- Gate commands run as written in `gate.md` (`runs/_ops/run_gate.sh`); output pasted unedited into `gate/bootstrap-output.md`.
#### Notes
- On the instance, `remote_eval.sh` copied the training logs into `gate_out/` under the same file names as the evaluation logs, so the per-model evaluation logs in `gate_out.tgz` are training logs; the evaluation output itself is in `eval.log` (kept in the backup folder).
- The in-training evaluation (seeds 10000-10002, 3 episodes per checkpoint) printed 3/3 captures at 1M steps for `sac-fs1-s2` before the gate ran; it is not gate data.

### feat: SAC 학습 실행 6개를 viewer에 올리기 (#35)
> why: the user approved publishing the runs for the Cloudflare viewer; all 6 so the seed spread is visible
#### Scope
- `published/2026-11-12_131635_sac-fs{1,4}-s{0,1,2}/` (new), this doc.
#### Changes
- `scripts/publish_run.py <run_id> --issue 35` for each run: config, `episodes.json`, 63 episodes per run (21 checkpoints × 3 in-training evaluation episodes), `run.json` with issue #35 and author. Models, checkpoints and TensorBoard files are not copied. 66 files and 0.9-2.4 MB per run; `published/` is 9.5 MB in total.
- Issue #35 got the `training` label that `publish_run.py` expects.
#### Verification
- Every `run.json` has the same keys as the existing baseline's; issue 35, 63 episodes each.
- `viewer`: `npm ci`, `npm run build` succeed; `dist/runs/index.json` lists 7 runs, the 6 SAC runs under issue 35 with 21 checkpoints each. `vite preview` screenshot at 1440 × 1000: the sidebar shows the "#35 SAC로 조준기 학습하기" group with the 6 runs, the capture-rate curve over checkpoints, and episode playback.
#### Notes
- `sac-fs1-s0` was missing from the local `runs/index.json`: the 6 parallel `train.py` processes started in the same second, and `RunStore.create_run` reads and rewrites `index.json` without a lock, so one append was lost. The run folder itself was complete. The entry was rebuilt in the siblings' shape from the folder's own files (`runs/_ops/restore_index_entry.py`, local only), then published. The race is listed under Follow-up Candidates; no library change here.

## Management Notes
### Follow-up Candidates
- Seed 20112: missed by all 6 SAC models, caught by the baseline. Replay it in the viewer and find what the policy does there (the published runs do not contain gate episodes; record one with `EpisodeRecorder` and seed 20112).
- SAC's miss rate (2.0-2.8 % vs the baseline's 0.5 %): a reward or observation change aimed at it would be a new gate.
- `sac-fs1` vs `sac-fs4` on fresh seeds, if a single reference setting is needed (this gate made no choice).
- DQN with a 5×5 joint discrete action set as a comparison (the current 5 actions turn one axis per step).
- `RunStore.create_run` / `_update_run` lose entries of `runs/index.json` when several `train.py` processes share one `runs/` (read-modify-write without a lock; seen here with 6 runs started in the same second). Fix with a file lock, or give each process its own `--runs-dir`.
### References
- Haarnoja et al., 2018, "Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor" (ICML).
- Haarnoja et al., 2018, "Soft Actor-Critic Algorithms and Applications" (arXiv:1812.05905) — automatic entropy temperature.
