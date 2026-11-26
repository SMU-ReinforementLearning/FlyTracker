# 91 레이저에 맞은 초파리가 놀라게 하고 오발을 종류별로 세기

## Document Relations
- Issue: #91
- Branch: `91-feature-fly-laser-startle-misfire-kinds`
- Umbrella: (none)
- Status: in progress
- Follows: #88 (acceleration action; fire learning not faster than the rule), #69 (shots and misfires), #4 (the fly's threat response)

## Summary
Environment version 7: a rule fly touched by the laser beam is startled and escapes, and misfires are counted in two kinds (grazing shots and wall shots), so that a misfire has a consequence inside the environment; then the existing aimers are measured again under it. In version 6 a misfire only blocks the trigger for the rest of the shot (at most 0.15 s), so there was nothing for a learned fire decision to win (#88, `gate-fire.md`). The user's reasons for reducing misfires are safety and damage to walls and furniture, and that a fly hit without being killed would react.

## Goal
- A misfire costs something in the environment, in a way a real fly and a real room would make it cost.
- Numbers for the existing aimers under the new rule, including how many shots land on the wall, so that the user can set the price of a wall shot for the fire-learning issue that follows.
- A pre-registered answer to "is `accel-pen-rule` better than v1" under version 7 (aimer v2 or not).

## Scope
1. Rule fly reaction (`flytracker/fly.py`, `flytracker/env.py`): while a shot is on and the beam is on the fly (the capture condition of that physics step holds), the fly is startled. It uses the existing threat response unchanged: reaction delay 0.06 s, escape turn 0.025 s, speed boost 1.6x for 0.3 s, then 0.4 s during which it cannot be startled again. The reaction starts from the first contact, also in a shot that would have captured (the user, 2026-11-26: "빔이 닿는 순간이지").
2. Misfire kinds (`flytracker/env.py`): a misfire is a **grazing shot** when the beam was on the fly for at least one physics step of that shot, a **wall shot** when it never was. Counted when the shot ends; `misfires` stays the total. Exposed in `info`, the snapshot and the episode summary.
3. `ENV_VERSION` 6 -> 7. Models trained under version 6 stay loadable (same observation and action; only the rule fly's reaction differs), recorded with their trained version, as version 5 aimer models already are (#72). The neural fly and the learned fly do not react to the beam in this issue; with the neural fly the environment behaves as in version 6.
4. Tests for 1-3; the pinned baseline numbers move to version 7.
5. Measurement on seeds 20000-20199, rule fly: v0, v1 (3 models), `accel-pen-rule` (3 models), with shots, grazing shots and wall shots per episode. A gate written before measuring: `accel-pen-rule` against v1 (time, P >= 0.90; capture exclusion stated in the gate). Neural fly (calibrated profile): reported, not gated, on fewer episodes.
6. README (fly behaviour, shots and misfires, environment version table, baseline numbers), `history.js` / `lineage.js`, glossary for the two new terms; published runs and `published/issues/91.json`.

## Out Of Scope
- The neural fly's reaction to the beam: to be agreed with the teammate who owns it. Until then it does not react.
- A "being hit" value in the learned fly's observation.
- A reward weight for wall shots and any training (aim or fire): the next issue, after the user has seen item 5's numbers and set what a wall shot may cost in time.
- Several flies; a cooldown of the laser.
- Showing the two misfire kinds in the viewer's readouts beyond what the issue page needs (decide when the numbers exist).

## Done Criteria
- [ ] Rule fly startled by beam contact during a shot; tested (reaction delay, no second startle inside the cooldown, no reaction without a shot, none for the neural fly).
- [ ] Grazing and wall shots counted and exposed; `misfires` equals their sum for finished shots; tested.
- [ ] Version 7; version 6 and version 5 aimer models load and play; tested.
- [ ] Gate document complete above "Verdict" and committed before any aimer is measured under version 7.
- [ ] v0, v1, `accel-pen-rule` measured on seeds 20000-20199; verdict written; numbers reported to the user with the wall-shot counts.
- [ ] README, viewer data, glossary, published runs and `published/issues/91.json` updated.
- [ ] `uv run pytest -q` and the viewer build pass.
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-26: issue registered and first commit made (9735310) after the user's go-ahead. Scope 1-4 implemented and tested (272 passed), gate document and measuring script written; the user reviewed the report of both and said "진행해. vast.ai에서 진행해", which approves these two commits, the gate as written and measuring on vast.ai. Review-free commits for the rest of the issue were asked about and not answered: later commits still go through the review gate, except the mechanical freeze of `gate/v1.csv` that the approved gate itself requires between the two measuring steps. The environment change is commit d3b95b2, the gate b967875, the frozen baseline 6e40c1c. Measured the same day on vast.ai (instance destroyed, none left): verdict **adopt** (`accel-pen-rule` faster than v1, P 1.000; capture 0.843 against 0.780). The verdict text and `gate/accel-pen-rule.csv` are written but NOT committed: they wait for the user's review. Full outputs (21 runs: episodes, shots, meta) are only in `runs/_ops91/dl/all/` (gitignored) until they are published. Reported to the user with the wall-shot counts (0.24 to 0.37 per episode; about 95% of misfires are grazes) and with the caveat that the rule aimer v0 captures more (0.960) than both learned aimers under version 7. Next: the user's review and the price of a wall shot; then README, viewer data, glossary, published runs, `published/issues/91.json`.

Decisions already made by the user (2026-11-26): the fly reacts from the moment the beam touches it; version goes up to 7 and version 6 models stay loadable; the neural fly is changed only after talking to the teammate; the misfire penalty is kept, to be given to wall shots, with a zero-penalty condition as control, in the next issue; the price of a wall shot is set after seeing this issue's numbers.

Agent's defaults, to confirm at the first review: the startle reuses the fly's existing escape parameters (no new numbers); "touch" is the capture radius (1.25 mm) during a shot; the escape direction is the existing one (sideways and away from the turret).

Where things are:
- Models for the measurement live only in `C:\Users\neighbor\Documents\Code\Github\FlyTracker-88\runs\g88\` (`accel-pen-rule-s<k>`) and the #51 worktree's `runs/g51` (v1); both gitignored. Do not remove those worktrees.
- Trap: sessions bound to another worktree cannot `EnterWorktree` here; work by absolute path and put multi-step shell work into script files.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 레이저에 맞은 초파리가 놀라게 하고 오발을 종류별로 세기 (#91)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
This document, the registry row in `docs/issues/README.md`, the pointer line in `AGENTS.md`.
#### Changes
- Summary, goal, scope, out of scope and done criteria filled from the conversation of 2026-11-26.
#### Verification
- `issue-start` summary: issue #91 (Feature, label enhancement, Priority High, assigned), branch from `origin/main` @ ca60b27.
#### Notes
- No code yet.

### feat: 쏘는 빔에 닿은 규칙 초파리가 놀라게 하고 오발을 두 종류로 세기 (#91)
> why: Scope 1-4 — the environment change itself, before anything is measured under it
#### Scope
`flytracker/env.py`, `fly.py`, `players.py`, `record.py`, `tests/test_env.py`, `tests/test_players.py`, this doc.
#### Changes
- `Fly.startle()`: sets the existing reaction delay when the fly can react (not while waiting to react, not during the cooldown, not for a learned fly). `FlyParams.evade_laser` (default on) switches it.
- `FlyChaseEnv._advance_shot`: on every physics step of a shot with the beam on the fly, marks the shot as touched and startles a rule fly; when a missed shot ends it is counted in `grazes` (touched) or `wall_shots` (never touched). `info` carries both; the episode summary carries `grazes` and `wallShots`.
- `ENV_VERSION` 7 with the comment line; `players.SAME_SPACES_VERSIONS = (6, 7)`: version 6 models load with their trained version recorded; version 5 aimer models as before; others refused.
#### Verification
- `uv run pytest -q`: 272 passed (267 of main + 5 new: misfire kinds, startle timing and cooldown, no startle on a miss or with the option off, learned fly ignores it, version 6 loads). The first run failed 2: `tests/test_viewer_attitude.py` needed `npm ci` in `viewer/` (fresh worktree), and the new startle test asserted on the heading, which a hovering fly changes by itself; it now asserts on the reaction timer.
- Neural fly: `startle` is called only for `Fly` instances (`isinstance`), so the neural path is untouched; its existing tests pass.
#### Notes
- The user's decisions are in Current State. Agent's defaults used: touch = the capture condition of that physics step during a shot; escape parameters and direction unchanged.
- Smoke only (not a result): the rule aimer on seeds 10000-10002 under version 7 captured 3/3 in 6.26 s with 6.67 misfires per episode, all grazes (version 6 on seeds 10000-10199: 4.99 s, 0.55). The fly escapes in the middle of a shot, as expected.

### docs: 환경 버전 7에서 조준기를 견줄 판정 기준을 재기 전에 적기 (#91)
> why: the comparison rules have to exist before v1 or the candidate is measured under version 7
#### Scope
`docs/issues/feature/91-feature-fly-laser-startle-misfire-kinds/gate.md`, `measure_v7.py`, this doc.
#### Changes
- Gate: `accel-pen-rule` (3 models) against v1 (3 models) on seeds 20000-20199, time, P >= 0.90; capture exclusion relative to v1 (P(candidate misses fewer) < 0.10 -> not adopted); per-model and "neither captures half" conditions -> undecided; misfire kinds reported, not gated.
- `measure_v7.py`: #72's `run_episode` plus `grazes` and `wall_shots` per episode and in `gate.csv`; `mean` over models; no local paths in `meta.json`; the commit is read from `FLYTRACKER_COMMIT` when set (a code bundle on a rented instance has no `.git`).
- `gate/truth.csv` written (ids 20000-20199), sha256 in the gate.
- Where: one vast.ai instance, baseline first, `gate/v1.csv` frozen in a commit, then the candidate (the user, 2026-11-26: "vast.ai에서 진행해").
#### Verification
- `measure_v7.py baseline --episodes 3 --seed 10000`: runs, writes the six columns.
- `uv run pytest -q`: 272 passed (rerun after the script edit).
#### Notes
- The capture exclusion is the agent's proposal (the fixed 0.97 floor of #72 cannot be assumed under version 7); the user approved the gate as written ("진행해", 2026-11-26) before anything was measured.

### docs: 후보를 재기 전에 버전 7의 v1 측정값을 고정하기 (#91)
> why: the gate requires `gate/v1.csv` to be frozen by sha256 before the candidate is measured
#### Scope
`gate/v0.csv`, `gate/v1.csv`, `gate.md` (Baseline section), this doc.
#### Changes
- v0 and v1 (3 models) measured on vast.ai instance 62693179 (32 cores; torch 2.15.0+cpu, sb3 2.9.2, gymnasium 1.4.0, numpy 2.4.6) from the bundle of commit b967875, seeds 20000-20199, rule fly.
- sha256 of both files written into the gate.
#### Verification
- Instance setup: `tests/test_env.py` and `tests/test_players.py` 32 passed, `ENV_VERSION` 7, six models present.
- sha256 of the downloaded files equals the instance's `state/P1_GATE_SHA256`.
- v0: capture 0.960, 6.037 s, misfires 5.010 (grazes 4.770, wall shots 0.240). v1 per model: s0 0.715 / 5.976 s, s1 0.730 / 5.979 s, s2 0.895 / 4.372 s; pooled 0.780, 5.442 s, 6.408 (6.013, 0.372).
#### Notes
- Committed without the review gate: a mechanical step the approved gate itself orders between the two measuring steps. The candidate had not been measured when this was committed.
- Two rented instances failed before this one (no sshd after 15 min; `docker_build() error`), and a third refused the key (`bad ownership or modes for file /root/.ssh/authorized_keys`); fixed by an onstart command that sets owner and modes of `/root/.ssh`. Scripts are in `runs/_ops91/` (gitignored).

### docs: 환경 버전 7에서 각가속도 조준기를 v2로 정한 판정 적기 (#91)
> why: the candidate was measured; the verdict goes under the gate that was written first
#### Scope
`gate.md` (Verdict), `gate/accel-pen-rule.csv`, this doc.
#### Changes
- Verdict: adopt. Time P 1.000 (4.851 s against 5.442 s), capture exclusion not fired (P 0.998; 506 against 468 of 600), per model P 1.000 / 0.957 / 0.999.
- Caveats written into the verdict: both learned aimers got worse than under version 6; v0 captures most (192/200); about 95% of misfires are grazes; wall shots 0.24-0.37 per episode.
- Neural fly table (60 episodes, reported only).
#### Verification
- `paired_bootstrap.py` output pasted from the run of 2026-11-26 (10,000 resamples, seed 42); sha256 of `accel-pen-rule.csv` equals the instance's `state/P2_GATE_SHA256`; the downloaded archive passed its sha256 and held 21 complete runs (7 x 200 rule episodes, 14 x 60 neural episodes) before the instance was destroyed.
- Neural pooled values are means of the three per-model summary lines, computed by hand from the logs.
#### Notes
- The user approved on 2026-11-26 ("그래. 다 문서화하고 머지해"): this commit, the documentation commit, push, PR and squash merge.
- The user set the price of a wall shot for the next issue: 1 s as the main condition, with 0 s (control) and 3 s beside it.
- Full per-episode outputs stay in `runs/_ops91/dl/all/` (gitignored); only the gate CSVs are in the repo.

## Management Notes
### Follow-up Candidates
- Fire learning under version 7 (joint with zero penalty as control and with a wall-shot penalty; fire-only on a fixed aim; fine-tuning if the joint run never fires), evaluated on the rule fly and the calibrated neural fly.
- The neural fly's reaction to the beam (teammate).
- Several flies seeing each other's flashes.
- Moving #59's training script from `algo.fireMode` to `algo.fire` (teammate).
- #85's diagnosis documents are still unpushed.
### References
- #88: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate-fire.md` (why time alone left nothing to win), `conditions.md`.
