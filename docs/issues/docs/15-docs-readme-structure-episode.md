# 15 README에 저장소 구성과 에피소드 기록 설명 넣기

## Document Relations
- Issue: #15
- Branch: `15-docs-readme-structure-episode`
- Umbrella: (none)
- Status: in progress

## Summary
Adds plain-language README sections that explain how the repo's parts connect, what the environment takes from Gymnasium, and what one episode is and what it leaves on disk. The user asked for these after a Q&A session (2026-11-09) in which the same three questions had no answer in the README.

## Goal
- A teammate who just cloned the repo can tell, from the README alone: which parts exist and how data flows between them; which Gymnasium pieces the environment uses and which parts are hand-written; how an episode starts, runs and ends, which files a run writes, what each episode field means, and what is not recorded.

## Scope
- `README.md` only: a new structure section, a Gymnasium paragraph and table in the environment section, a new episode-and-record section, and a link from the folder table's `runs/` row.

## Out Of Scope
- Any code change (`flytracker/`, `scripts/`, `viewer/`).
- Recording observations or actions in episode files (see Follow-up Candidates).
- A full README overhaul through `readme-upkeep` (trending layout comparison, badges, CHANGELOG).

## Done Criteria
- [ ] Every fact in the new sections is checked against the source (`flytracker/env.py`, `wrappers.py`, `record.py`, `scripts/train.py`, `scripts/record_baseline.py`, `scripts/_common.py`, `tests/test_env.py`) or a real file under `runs/`.
- [ ] ko-writing `check.py` on `README.md` shows nothing in the new sections except known false positives.
- [ ] `readme-upkeep` `scripts/readme_check.py` passes (links and anchors).
- [ ] The user approved the README text.

## Current State
- Issue, branch and worktree created from `origin/main` @ 25b05d1; this document seeded.
- README sections drafted in the worktree; waiting for the user's review.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: README에 저장소 구성과 에피소드 기록 설명 넣기 (#15)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management document, Master Registry row, `AGENTS.md` pointer line.
#### Changes
- Seeded by `issue-start`; Summary, Goal, Scope, Out Of Scope, Done Criteria filled from the conversation.
#### Verification
- `issue-start` dry run and real run both reported base `origin/main` @ 25b05d1.
#### Notes
- No umbrella issue exists in this repo yet, so no `--parent`.

## Management Notes
### Follow-up Candidates
- Episode files do not record the agent's observation vector or its action. When #13 adds a detection model, the observation will differ from the true state, so decide then whether `EpisodeRecorder` should record both.
### References
- `flytracker/record.py` (episode file format), `flytracker/wrappers.py` (`make_env`), `flytracker/env.py` (`FlyChaseEnv`).
