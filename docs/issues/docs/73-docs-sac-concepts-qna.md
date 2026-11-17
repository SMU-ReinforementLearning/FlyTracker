# 73 SAC 개념을 쉬운 문답으로 정리하기

## Document Relations
- Issue: #73
- Branch: `73-docs-sac-concepts-qna`
- Umbrella: (none)
- Status: done

## Summary
A formula-free question-and-answer explainer of the SAC networks used for the aimer, written from the questions the user asked while studying it on 2026-11-17. It is the easy companion to the formula-level `docs/issues/feature/35-feature-sac-aimer-training/sac.md` and links to it.

## Goal
- A teammate who knows DQN but not SAC can read what the actor outputs, how an action is sampled from the mean and the standard deviation, what the critic's Q value predicts and how it is learned, why there are two critics, and why target networks exist.
- Keep the user's own questions as the section openers, so the document answers what a first reader actually asks.

## Scope
- New file `docs/issues/docs/73-docs-sac-concepts-qna/sac-concepts.md` (Korean, document style `~한다`).
- This management doc, the Master Registry row, the AGENTS.md pointer.

## Out Of Scope
- Editing `sac.md` of #35. It still says the observation is 13-dim (true for #35, env version 1); the new document states its own version instead.
- Loss formulas, hyperparameter tables, reparameterization: already in `sac.md`.
- README changes, code changes.

## Done Criteria
- [x] The document exists and its relative link to `sac.md` resolves. (2026-11-18 00:11)
- [x] Every project number in it is traceable: 17-dim observation / 2-dim action to env version 5 (#45, #51), 18 / 3 to env version 6 (`flytracker/env.py` `OBS_FIELDS`, `flytracker/aimer.py` `ACTION_NAMES`), hidden layers 256, 256, γ 0.99 and τ 0.005 to the Stable-Baselines3 defaults listed in `sac.md` (`scripts/train.py` passes no `policy_kwargs`). (2026-11-18 00:11)
- [x] Worked numbers are arithmetically right (tanh values, 68% / 95%). (2026-11-18 00:11)
- [x] `ko-writing` `check.py` run; remaining warnings judged one by one. (2026-11-18 00:11)
- [x] Cold-reader pass by a subagent that saw only the file; every item fixed or answered. Two passes run. (2026-11-18 00:11)
- [x] User approved the text. (2026-11-18, "머지까지 해")

## Current State
Document committed and approved by the user. Nothing is left on this issue; the one open item is under Follow-up Candidates.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: SAC 개념을 쉬운 문답으로 정리하기 (#73)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Seed only: this document, the Master Registry row, the AGENTS.md pointer.
#### Changes
- `docs/issues/docs/73-docs-sac-concepts-qna.md` created and filled.
- `docs/issues/README.md` +1 row; `AGENTS.md` +1 pointer line.
#### Verification
None needed; no behaviour or rendered page changed.
#### Notes
Branch cut from `origin/main` @ 61d2b6b. Priority Low: a study aid, nothing waits on it. `uv sync` not run in this worktree; the work is documentation only.

### docs: SAC 개념을 쉬운 문답으로 정리하기 (#73)
> why: the user asked to document the SAC concepts they had worked through by question and answer on 2026-11-17
#### Scope
`docs/issues/docs/73-docs-sac-concepts-qna/sac-concepts.md` only.
#### Changes
- Intro: what SAC, the aimer, capture, a step and the env version are; the sizes are those of env version 5 (17 / 2) and how env version 6 differs (18 / 3, fire).
- Nine sections, each opened by the question it answers: network layout, the actor's role, mean and standard deviation, the sampling computation with a worked table, the critic's Q value and its target, how the actor learns, what goes into the critic, why two critics, why target networks.
- The chat explanation "networks tend to err high" was wrong and is not in the document; it says the errors go both ways and the actor's selection picks the high ones.
- Example predictions for the two-critic section changed from the chat's 4.0 / 5.2 / 6.5 to 3.6 / 4.9 / 6.5 so the errors average to zero as the text claims.
#### Verification
- tanh(0.63) = 0.558, tanh(0.48) = 0.446, tanh(0.60) = 0.537 computed with Python; the table rounds them to 0.56, 0.45, 0.54.
- `OBS_FIELDS` on this branch sums to 18 with `shot`, 17 without; `ACTION_NAMES` has 3 entries with `fire`.
- `check.py`: no forbidden patterns, endings uniform, no long paragraphs. Left as is: one heading of 16 characters (`target network의 역할`) and three headings flagged for a relative clause; they name topics, not claims.
- Cold reader, pass 1: 9 stuck points, 8 terms used before definition, 6 naming wobbles, 8 mismatches. All fixed by a rewrite except the `target critic` alias (kept: other material uses that name).
- Cold reader, pass 2 (fresh subagent): 8 stuck points, 4 naming wobbles, 4 mismatches, its summary matched the intended one. Fixed with 20 replacements. Not changed: `log std` appears in the layout table before its section (a pointer follows the table); "행동을 뽑는다" is kept as the name of the whole computation. No third pass was run.
#### Notes
The README's aimer state section lists 18 items (env version 6); the document says so and says which 17 it means.

### chore: #73 마무리 (#73)
> why: last commit before the PR
#### Scope
Status and pointer only.
#### Changes
- Status done here and in the Master Registry; AGENTS.md pointer removed.
#### Verification
None needed.
#### Notes

## Management Notes
### Follow-up Candidates
- `sac.md` (#35) describes the 13-dim observation and the angle-based capture of env version 1. A dated note at its top, like the one in `detection-model.md`, would tell readers the current sizes.
### References
- `docs/issues/feature/35-feature-sac-aimer-training/sac.md`
- `flytracker/env.py` (`OBS_FIELDS`, `ENV_VERSION`), `flytracker/aimer.py` (`ACTION_NAMES`), `scripts/train.py`
