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
- [x] Every fact in the new sections is checked against the source (`flytracker/env.py`, `wrappers.py`, `record.py`, `scripts/train.py`, `scripts/record_baseline.py`, `scripts/_common.py`, `tests/test_env.py`) or a real file under `runs/`. (2026-11-09)
- [x] ko-writing `check.py` on `README.md` shows nothing in the new sections except known false positives. (2026-11-09)
- [x] `readme-upkeep` `scripts/readme_check.py` passes (links and anchors). (2026-11-09)
- [x] The user approved the README text. (2026-11-09, "머지해")

## Current State
- README sections committed; a cold-reader review was applied to the new sections.
- Next: remove the `AGENTS.md` pointer as the last commit, open the PR and squash-merge it (the user asked to merge).

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

### docs: README에 저장소 구성과 에피소드 기록 설명 넣기 (#15)
> why: the user asked for the Q&A answers on structure, Gymnasium use and episode records to live in the README in plain words
#### Scope
- `README.md`, this doc.
#### Changes
- New `## 구성`: the three parts (`flytracker/`, `scripts/`, `viewer/`) and that they meet only through JSON files under `runs/`; defines step (0.02 s) and 기준선 on first use.
- `## 환경`: the time row now names the 10 ms interval and the 20 ms step instead of two meanings of "step"; new `### Gymnasium` with a table of the seven Gymnasium pieces used and where, plus what is hand-written (no physics engine, no `render`, no `gym.register`).
- New `## 에피소드와 기록`: how an episode starts, steps and ends (max 500 steps, 501 frames); `### 실행 폴더` tree and tag meaning (eval seeds 10000-10002); `### 에피소드 파일` with `meta`, `summary` and every `frames` key; observations and actions are not recorded.
- `## 폴더`: the `runs/` row links to the new section.
#### Verification
- Same seed, three policies (rule baseline, still, constant spin), seeds 3, 5, 10000: fly positions identical over the common frames. The README claim that the fly path depends only on the seed rests on this.
- Rule baseline seed 3 run twice: identical frames, and the summary matches `runs/2026-11-09_130439_baseline/episodes/baseline/ep_003.json` (69 frames, 1.36 s, captured).
- Timeout episodes have 501 frames; `make_env(frame_stack=4)` observation shape is `(4, 13)`.
- ko-writing `check.py README.md`: sections 1-8 clean; one section-9 warning on the pre-existing line 36 ("이 탐색은"), a false positive.
- `readme_check.py README.md`: 0 fail, 0 warn.
- Cold-reader subagent (README only): fixed step's two meanings, frame count 500 vs 501, eval seeds, 기준선 used before its definition, how the dev server hands files to the viewer, `aimerC`, frame-stack shape.
#### Notes
- Cold-reader items in pre-existing README text were left alone (out of scope): the screen rectangle introduced without a lead-in, `hook` and `RackTracker` undefined, "위협" and "평시" undefined, the `−z` default facing next to "z 정면", the "각각" mapping in the reward/fly paragraph, the heading `## 실행` versus the glossary term 실행 (= run). Listed under Follow-up Candidates.

## Management Notes
### Follow-up Candidates
- Episode files do not record the agent's observation vector or its action. When #13 adds a detection model, the observation will differ from the true state, so decide then whether `EpisodeRecorder` should record both.
- README text that predates this issue and tripped the cold reader: the screen rectangle in `## viewer` has no lead-in; `hook`, `RackTracker`, "위협" and "평시" are undefined; the default `−z` facing sits next to "z 정면" without explanation; "각각" in the reward/fly paragraph needs the reader to match order; the heading `## 실행` clashes with the glossary term 실행 (= run).
### References
- `flytracker/record.py` (episode file format), `flytracker/wrappers.py` (`make_env`), `flytracker/env.py` (`FlyChaseEnv`).
