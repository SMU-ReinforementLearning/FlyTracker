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
- [ ] 6 SAC runs (frame stack 1 and 4 × seeds 0, 1, 2) finish 1,000,000 steps each; run folders and final models copied back.
- [ ] Final models evaluated on seeds 20000-20199; paired bootstrap verdict appended to the gate document.
- [x] SAC explainer written, passed `check.py` and a cold-reader review. (2026-11-12 22:40)
- [ ] `uv run pytest` passes (no code changes expected; re-run before the last commit).

## Current State
Read only this block to take over. As of 2026-11-13 00:00 KST. The user went to sleep and will check in the morning; they asked that the results be fetched, backed up, and the instance destroyed when training ends.

### Fallback that is certain
Nothing ships from this issue. The rule baseline is the reference aimer: `gate/baseline.csv`, sha256 `4aec8f8e…` (199/200 captures, 4.100 s mean on seeds 20000-20199, env v2). Branch `35-feature-sac-aimer-training` @ 20ae755 (local, not pushed) holds the gate, the explainer and env v2. If the instance and its results were lost, the runs are reproducible from `gate.md` (6 × 1M steps, about 2.3 h and $0.5 on a 7900X).

### Running now
| job | where | started | ETA | log path | how to check | survives a dropped session |
| --- | --- | --- | --- | --- | --- | --- |
| 6 SAC runs (`sac-fs{1,4}-s{0,1,2}`, 1M steps) | vast.ai instance 60356096, `ssh -p 28112 root@ssh1.vast.ai`, `/root/ft/runs/` | 22:16 KST | about 00:45 KST | `/root/ft/logs/*.log` (block-buffered, mostly empty) | `ssh -p 28112 root@ssh1.vast.ai '/root/ft/.venv/bin/python /root/progress.py'` | yes (nohup on the instance) |
| auto-eval: waits for 6 `model.zip` and no `train.py`, runs `remote_eval.sh` (gate CSVs, tarballs, `manifest.sha256`), then touches `/root/RESULTS_READY` | same instance, `setsid nohup bash /root/remote_autorun.sh` | 23:55 KST | about 00:50 KST | `/root/autorun.log`, `/root/eval.log` | `ssh -p 28112 root@ssh1.vast.ai 'cat /root/autorun.log; ls /root/RESULTS_READY'` | yes |
| local waiter: polls for `RESULTS_READY`, then runs `runs/_ops/fetch_and_release.sh` | this laptop, background task of the session that wrote this | 23:58 KST | about 01:00 KST | session task output | `ls runs/_download/RELEASED` in the worktree | no |
| progress watch (`runs/_ops/watch_runs.sh`) | this laptop, Monitor of the same session | 23:30 KST | until done | session events | — | no |

The instance costs $0.167/h while it runs (about $1.5 overnight). It cannot stop itself (no per-instance API key; the account key is not copied there). Destroying deletes its disk; stopping keeps the disk at $0.20/GB/month but a restart needs the host free, so download first, then destroy.

### Confirmed so far
- Baseline (env v2), seeds 20000-20199: 199/200 captures, 4.100 s mean time — `gate.md`.
- Env v2 = code part of #34's f8cfa78; `uv run pytest` 37 passed locally and on the instance; baseline byte-identical with branch 34 HEAD 50c05b7 — work log, `feat:` section.
- Throughput: laptop 41 steps/s (1 thread); instance 109-118 steps/s per run with 6 in parallel — this block.
- At 14:48 UTC (23:48 KST) all 6 runs were between 601k and 648k steps, no stall, no traceback.
- Commits 629a967, 8050472, 20ae755 made with the user's approval. Uncommitted, awaiting approval: the LF fix (`evaluate_gate.py`, both gate CSVs, `gate.md` hashes, work-log section `fix: 판정 기준 CSV 줄바꿈을 LF로 고정 (#35)`).

### Next steps in order
1. Check whether the release already happened: `ls runs/_download/RELEASED` (worktree root). If it is missing, run `bash runs/_ops/fetch_and_release.sh` in Git Bash from the worktree root. It downloads `runs-full.tgz` (checkpoints included), `gate_out.tgz`, `manifest.sha256`, verifies sha256, extracts to `runs/` and `runs/_download/gate_out/`, copies the tarballs to `C:/Users/neighbor/Documents/Code/Github/FlyTracker/runs/_backup-issue35/` and verifies them there, and only then runs `vastai destroy instance 60356096 -y`. If it prints `FAIL: results are not packed yet`, check the auto-eval row above; if `/root/autorun.log` says `eval FAILED`, read `/root/eval.log`, fix, and run `bash /root/remote_eval.sh` on the instance.
2. Copy `runs/_download/gate_out/sac-fs{1,4}.csv` and `sac-fs{1,4}-s{0,1,2}.csv` to `docs/issues/feature/35-feature-sac-aimer-training/gate/`, record their sha256 in `gate.md`.
3. Gate, as written in `gate.md` (from the worktree root, D = `docs/issues/feature/35-feature-sac-aimer-training`): `python .claude/skills/experiment-gate/scripts/paired_bootstrap.py --truth $D/gate/truth.csv --a $D/gate/baseline.csv --b $D/gate/sac-fs1.csv --targets time --metric mae --lower-is-better --resamples 10000 --seed 42 --threshold 0.90 --json $D/gate/sac-fs1-gate.json`; same for `sac-fs4`, for each `-s0/-s1/-s2` file (exclusion: any P < 0.50 → undecided), `--targets capture --metric mae --lower-is-better` for capture rate (mae against truth 1 is 1 − capture rate; exclusion: pooled capture < 0.97 → not adopted), and `--a sac-fs1.csv --b sac-fs4.csv` descriptively.
4. Paste the tables under `## Verdict` in `gate.md`, decide adopt / reject / undecided by the pre-written rule, update this block and the Done Criteria, write the work-log section, show the user the changed files and wait for commit approval.
5. Ask the user the open decisions below.

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

### Open decisions for the user
- Commit the LF fix (`fix: 판정 기준 CSV 줄바꿈을 LF로 고정 (#35)`)? Asked 2026-11-12 23:50, not answered yet.
- Publish runs to `published/` for the Cloudflare viewer (`scripts/publish_run.py <run> --issue 35`; issue #35 then needs the `training` label, and the copy goes in through a PR)? Which runs: all 6, or one per candidate?
- Push the branch and open a PR once the verdict is in?

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

## Management Notes
### Follow-up Candidates
- DQN with a 5×5 joint discrete action set as a comparison (the current 5 actions turn one axis per step).
### References
- Haarnoja et al., 2018, "Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor" (ICML).
- Haarnoja et al., 2018, "Soft Actor-Critic Algorithms and Applications" (arXiv:1812.05905) — automatic entropy temperature.
