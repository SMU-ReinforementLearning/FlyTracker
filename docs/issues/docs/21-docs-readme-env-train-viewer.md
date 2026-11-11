# 21 README를 환경, 학습 코드, viewer로 나눠 다시 쓰기

## Document Relations
- Issue: #21
- Branch: `21-docs-readme-env-train-viewer`
- Umbrella: (none)
- Status: in progress

## Summary
Rewrites `README.md` so that it reads in three parts — environment, training code, viewer — instead of the current nine sections that grew one issue at a time (#1, #15, #19). The user asked for it on 2026-11-11 right after the repository moved to the team organization: "readme 쉽고 읽히게 다시 써줘. 환경, 학습코드, viewer로 나누어서". Facts stay; the order, the depth-first-then-detail flow and the clone URL change.

## Goal
- A teammate who clones the repository for the first time gets to a rendered episode in the viewer by following the first screen of the README, then finds the part they will work on (environment, training code, viewer) under its own heading.
- Every fact kept from the old README is re-checked against the source or re-measured; nothing is restated from memory.

## Scope
- `README.md`: new outline — intro, quick start, `## 환경`, `## 학습 코드`, `## viewer`, folder table. Clone URL changes to `SMU-ReinforementLearning/FlyTracker`.
- Reference tables that most readers never need (episode file fields, Gymnasium mapping) move below the main path of their part or into a folded block.

## Out Of Scope
- Code changes of any kind.
- New figures (no plotting script exists; adding one is a separate decision).
- `CHANGELOG.md` / release notes — the project has no versioned releases yet.
- Fixing the org name typo (`ReinforementLearning`) — that is a GitHub setting, not a repo file.

## Done Criteria
- [ ] The README has exactly the three parts the user named, each starting with what a reader does, followed by what they need to know.
- [ ] Every number and name in the README is in the facts ledger with its source; measured values (baseline over 200 episodes) are re-run on this branch.
- [ ] `ko-writing` `check.py` with glossary and facts ledger reports nothing except known false positives.
- [ ] `readme_check.py` passes (links, anchors).
- [ ] Two cold-reader passes applied (fresh subagent each time).
- [ ] The user approved the text at the review gate.

## Current State
- Issue, branch and worktree created from `origin/main` @ fc67f84; this document seeded.
- #22 (publish runs, Cloudflare viewer) merged to `main` while the draft was being written. The branch was fast-forwarded to `origin/main` @ 8aed060 before its first commit, and the #22 README sections were folded into the new outline.
- README draft written with a glossary and a facts ledger (scratchpad), checked with `check.py` and `readme_check.py`, and reviewed by four cold-reader passes before the #22 merge. The user stopped further passes.
- Next: the user approved the text ("머지해"); commit, remove the pointer, open the PR, squash-merge, run post-PR cleanup.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: README를 환경, 학습 코드, viewer로 나눠 다시 쓰기 (#21)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management document, Master Registry row, `AGENTS.md` pointer line.
#### Changes
- Seeded by `issue-start`; Summary, Goal, Scope, Out Of Scope, Done Criteria filled from the conversation (the user's request right after the repository moved to `SMU-ReinforementLearning/FlyTracker`).
- Registry row inserted before the #22 row that landed meanwhile.
#### Verification
- `issue-start` reported base `origin/main` @ fc67f84; `git merge --ff-only origin/main` then moved the branch to 8aed060 with no local commits to carry.
- `git status` shows only the three seeded files.
#### Notes
- No umbrella issue exists in this repo yet, so no `--parent`.
- The ff-merge was done by restoring the three dirty tracked files from a scratchpad copy, fast-forwarding, and putting the copies back; nothing was stashed.

### docs: README를 환경, 학습 코드, viewer로 나눠 다시 쓰기 (#21)
> why: the user asked for a README that reads easily, split into environment, training code and viewer, right after the repository moved to the team organization
#### Scope
- `README.md` (whole file), this doc.
#### Changes
- New outline: intro (one paragraph + a three-row table of the parts), `## 시작하기` (six commands from clone to a playing episode), `## 환경` (방과 좌표, 조준기, 초파리, 관측과 행동, 에피소드, 보상; Gymnasium table folded), `## 학습 코드` (기준선, 학습, 기준선과 비교, 환경 옵션, 실행 폴더 with the episode-file tables folded, 실행 올리기, 정책의 기억, 학습 시간, 에피소드 파일의 한계), `## viewer` (run and controls, 초파리 3D 모델, 조준기 화면의 사각형, 배포). The old `## 구성`, `## 설치`, `## 실행`, `## 에피소드와 기록`, `## 기준선과 강화학습` and `## 폴더` sections are redistributed into those parts; no fact from them was dropped.
- Clone URL → `https://github.com/SMU-ReinforementLearning/FlyTracker.git`.
- Node requirement 20 → 20.19 (Vite 8 `engines`: `^20.19.0 || >=22.12.0`).
- New facts not in the old README: action 1 = yaw 180°/s, pitch 120°/s, accel limit 720°/s², pitch ±80° (`AimerLimits`); what `--capture-range` means; the alarm trigger stated as "closing within 1 s at the current speed" (looming rate 1/s); the default aim direction stated as −z first, then the rule for a moved turret; the observation as a 13-row-sum table; the comparison that is possible today (3 eval episodes vs `record_baseline.py --episodes 3 --seed 10000`); `turret`/`aimer` naming; `step_0000000` = "학습 전"; `rule-baseline` as the policy name.
- #22 sections folded in: `published/` in the intro and the parts table, `### 실행 올리기` under 학습 코드, dev server reads both folders, `### 배포` under viewer. Text taken from the merged #22 README with the terms of this rewrite.
- Terminology fixed across the file: 조준 방향 (no 조준 중심), 포획 거리 (no 거리 조건), 에피소드 파일 (no 기록 파일), 학습 중 평가, 체크포인트 defined before use, 탐색 vs exploration, 3D 모델 vs 모델.
#### Verification
- Every number re-read from its source on this branch: `pyproject.toml`, `viewer/package.json` + Vite `engines`, `viewer/vite.config.js` (port 5180), `flytracker/world.py`, `env.py` (`EnvConfig`, `RewardWeights`, `OBS_FIELDS`), `camera.py`, `aimer.py` (`AimerLimits`), `fly.py` (`FlyParams`), `wrappers.py`, `record.py`, `baseline.py`, `scripts/train.py --help`, `scripts/record_baseline.py --help`, `scripts/publish_run.py --help`, `viewer/src/data/labels.js`, `viewer/src/playback/clock.js` (an episode starts playing on load).
- Baseline re-measured on this branch, 2026-11-11: `record_baseline.py --episodes 200 --seed 10000 --no-save` → 포획 200/200, 평균 보상 -19.22, 보인 비율 18%, 포획까지 평균 4.21초 (48 s wall clock). Training speeds are kept from the #19 measurement of 2026-11-10 and dated in the text.
- ko-writing `check.py --glossary --facts` (ledgers in the scratchpad): sections 1–8 clean; remaining warnings are false positives — "이 README에서", 탐색 inside a linked document title, 요 in 요약, 기록 in "TensorBoard 기록" and "기록한".
- `readme_check.py README.md`: 0 fail, 0 warn (anchors `#환경`, `#학습-코드`, `#viewer`, `#환경-옵션`, `#시작하기`, `#배포` resolve).
- Cold-reader passes (fresh subagent each, README only): four, all before folding #22 in. All four said the first screen alone gets a new member to a playing episode. A fifth pass on the folded text was started and stopped at the user's request ("콜드 리더 그만 돌려"); the #22 text is the merged, user-approved wording with this rewrite's terms. Fixed from them: 포대 vs 카메라; "위협" undefined; 고도 띠; 체크포인트 used before definition; the claim that no observation is recorded (visible, uv, distance are); "놓친 벌점이 가장 크다" vs capture reward 10; 실행 read as a verb; `run onboarding` without a subject; 조준기 "다가오거나" while the turret is fixed (introduced during a fix, caught by the third pass); 조준 중심/카메라 중심/조준 방향; 거리 조건/포획 거리; 기록 three ways; 모델 two ways; 보이다 two ways; z 정면 vs −z; 포획 거리 undefined; "빠르게" without a threshold; `dev` extra unexplained; 시작하기 run not comparable with training (seed 0).
#### Notes
- Left as is, with reasons: the org name typo in the clone URL (it is the real address); 탐색 in the linked design-note title (a document title); "학습 코드" as the name of `scripts/` although it also holds the baseline and publish scripts (the user's naming); the 200-episode baseline table next to 3 eval episodes (the README says the comparison script does not exist yet).
- Length 10,760 → 12,066 characters; the growth is the #22 content.

## Management Notes
### Follow-up Candidates
### References
