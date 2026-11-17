# 72 SAC 조준기를 환경 버전 6에 세우고 조준기 v1로 정하기

## Document Relations
- Issue: #72
- Branch: `72-feature-aimer-v1-sac-rule-trigger`
- Umbrella: (none)
- Status: done

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
- [x] Published runs and `published/issues/72.json`. (2026-11-18 01:20)
- [x] README and viewer name v0 / v1 per the verdict; firing shown as the aimer's. (2026-11-18 01:15)
- [x] Full test suite passes; viewer builds. (2026-11-18 01:10, 211 passed)
- [x] PR merged; `AGENTS.md` pointer removed in the branch's last commit. (pointer removed in this commit; merge follows)

## Current State
2026-11-18 01:30. Done. Verdict: adopt. Aimer v0 = rule aimer (fixed yardstick), aimer v1 = #51 `sac-beam-assist` models steering + the baseline's firing rule.

| Fly | Seeds | v0 | v1 (three models) |
|---|---|---|---|
| rule | 20000-20199 | 198/200, 4.894 s, 0.50 misfires/ep | 584/600, 3.026 s, 0.60 misfires/ep |
| neural, stimulus off | 20000-20059 | 59/60, 5.110 s, 0.62 | 155/180, 4.258 s, 1.94 |
| neural, stimulus on | 20000-20059 | 59/60, 5.397 s, 1.93 | 164/180, 4.058 s, 2.04 |

- Gate and verdict: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate.md`. Raw rows and re-run commands: `.../data/README.md`.
- v1's weakness is the neural fly: faster on average, loses many more flies. It does not decide when to fire.
- To use v1: `load_opponent("runs/2026-11-15_151701_sac-beam-assist-s<k>", "aimer", cfg)`; the model folders are not in the repository.
- Next (not started): aimer v2 that learns to fire, after the detector (#13).

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

### feat: 조준기 v0과 v1을 README와 issue 화면에 올리기 (#72)
> why: the verdict adopts v1, and the user pointed out that firing is the aimer's, not the environment's
#### Scope
`README.md`, viewer issue-page data (`experiment.js`, `history.js`, one CSS rule), `ui-text.glossary.md`, one sentence of `published/issues/69.json`. No package code.
#### Changes
- README: new section "조준기 v0과 v1" (what each is, the six-row table for the three fly settings, the gate in two sentences, links to `gate.md` and `data/README.md`, the two commands); firing stated as the aimer's with the env only judging hits; `record_match.py` listed among the scripts; `match.py`'s version rule now mentions the version 5 exception.
- Issue page: learned-aimer card row `쏘는 방식` (`algo.fire`), baseline card row `쏘는 기준` (env version 6 and later), aimer settings row `한 발 길이` (the value of `env.capture_hold` for version 6 and later; the environment row `포획 유지 시간` is shown for earlier versions only), fly settings row `자극` (켬 / 끔). `history.js` entries for each, and issue 72.
- Variations: runs that differ only in the re-run model id are one variation (as runs that differ only in training seed already were), and variations of the same kinds get the first differing row appended to their name. #72 goes from 12 buttons to 6, #61 from 8 to 4. The button row scrolls inside itself when wider than the screen.
- `69.json`: "환경을 바꾸고" reworded so that the aimer fires and the environment judges.
#### Verification
- `uv run pytest -q`: 211 passed (209 + the issue-72 cases of the published-run tests). `npm run build` in `viewer`: built.
- `scripts/match.py --aimer baseline --aimer runs/2026-11-15_151701_sac-beam-assist-s0 --episodes 3`, as documented in README: prints `baseline 3/3, 4.79초` and `…sac-beam-assist-s0+rule-fire 3/3, 2.49초`.
- ui-evidence on the built site (`vite preview`, port 4972), tree: uncommitted on d695ddb, Chrome 157, serve check `document.title === 'FlyTracker'`, ready when fonts are loaded and more than 10 rows exist. Probes: the new rows' values and the variation button names.

| page | viewport | overflow | new rows | variation buttons |
| --- | --- | --- | --- | --- |
| /?issue=72 | 1600x2600 | none | 쏘는 방식 기준선의 규칙; 쏘는 기준 빔까지 1.25mm 안; 한 발 길이 0.15초; no 포획 유지 시간 | 전체, 규칙 초파리 v0 + 기준선 v0, 규칙 초파리 v0 + 학습한 조준기 v1, 신경 초파리 x (기준선 v0, 학습한 조준기 v1) x (자극 끔, 자극 켬) |
| /?issue=72 | 390x4200 (mobile, dpr 2) | page does not scroll; one button of the variation row ends 18 px past the edge inside the row's own scroll | same | same |
| /?issue=69 | 1600x2600, 390x4200 | none | 쏘는 기준 없음→빔까지 1.25mm 안; 한 발 길이 없음→0.15초; 포획 유지 시간 0.15초→없음 (vs #61) | none |
| /?issue=61 | 1600x2600, 390x4200 | none (390 px overflowed before this change: scrollWidth 522) | | 전체, 기준선 v0 x (자극 끔, 자극 켬), 학습한 조준기 x (자극 끔, 자극 켬) |
| /?issue=51 | 1600x2600, 390x4200 | none | 포획 유지 시간 0.15초; no 한 발 길이 | unchanged (4 conditions) |
| /?issue=35 | 1600x2600, 390x4200 | none | | unchanged (1개, 4개) |

  Console: favicon 404 only (present on main). Captures are in the session scratchpad, not committed. Looked at: #72 desktop (text, v0 and v1 cards with the new rows, `한 발 길이` under the aimer's settings).
- Not verified: the light colour scheme; the popover text of the new rows was read from the DOM, not hovered.
#### Notes
- Decided by the agent, reported to the user: the config key `capture_hold` stays in `EnvConfig` (see Out Of Scope). Only where it is shown and how it is described changed.
- The variation grouping change was not in the plan; the #72 page was unusable without it (12 buttons, 9 of them sharing three names).

### chore: 조준기 v0과 v1 에피소드 올리기 (#72)
> why: the issue page needs episodes of v1 under the shot rule next to v0's
#### Scope
`published/`: twelve runs and `published/issues/72.json`.
#### Changes
- `scripts/record_match.py <aimer> [fly flags]` for `baseline` and the three models against the rule fly, the neural fly with the stimulus off, and with it on; seeds 10000-10002; then `scripts/publish_run.py <run> --issue 72`.
- Captured 35 of 36 episodes. Mean time of the captured ones per run (s): rule fly v0 4.79, v1 2.49 / 4.78 / 1.68; neural, stimulus off v0 5.24, v1 5.17 / 2.81 (2 of 3) / 4.16; neural, stimulus on v0 5.26, v1 2.73 / 4.93 / 2.26.
- `72.json` (Korean, screen text): what v0 and v1 are, the gate numbers, the weakness against the neural fly, what the twelve runs are. `aimer: v1`, `compare: 69`.
#### Verification
- Each SAC run's `config.json` has `algo.fire: "rule"`, `trainedEnvVersion: 5`, `model`. Episodes carry `firing`, `shots`, `misfires`.
- The viewer build and the captures of the previous section include these runs.
#### Notes
- `publish_run.py` warned that #72 has no `training` label: expected, nothing was trained.
- The three baseline runs repeat #69's (same seeds, same code) so that the #72 page shows v0 and v1 side by side.

### chore: #72 마무리 (#72)
> why: last commit before the PR
#### Scope
Status done, registry row done, `AGENTS.md` pointer removed, Current State.
#### Changes
- This document, `docs/issues/README.md` (#72 row -> done), `AGENTS.md` (pointer removed).
#### Verification
- `uv run pytest -q`: 211 passed, no code changed after that run. `git status` clean after this commit.
#### Notes
- The preview server on port 4972 was stopped. `runs/` of this worktree (models and recorded runs) is not committed.
- The user approved the chain on 2026-11-18 ("끝나면 머지까지 진행해").

## Management Notes
### Follow-up Candidates
- Aimer v2: SAC that learns to fire, on observations with the detector's error (#13); decide the misfire term of the reward there.
- Move the shot length from `EnvConfig.capture_hold` to the aimer's settings once the teammate's branch can take a config key change.
### References
- #51 SAC under the laser rule (the models), #61 SAC vs neural fly under version 5, #69 fire action and misfires (env version 6), #13 detector.
