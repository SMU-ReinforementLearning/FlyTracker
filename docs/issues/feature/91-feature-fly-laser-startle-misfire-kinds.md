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
2026-11-26: issue registered, worktree created from `origin/main` @ ca60b27 (the merge of #88), this document filled. Nothing implemented or committed yet; the first commit waits for the user's approval of the seeded files.

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

## Management Notes
### Follow-up Candidates
- Fire learning under version 7 (joint with zero penalty as control and with a wall-shot penalty; fire-only on a fixed aim; fine-tuning if the joint run never fires), evaluated on the rule fly and the calibrated neural fly.
- The neural fly's reaction to the beam (teammate).
- Several flies seeing each other's flashes.
- Moving #59's training script from `algo.fireMode` to `algo.fire` (teammate).
- #85's diagnosis documents are still unpushed.
### References
- #88: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate-fire.md` (why time alone left nothing to win), `conditions.md`.
