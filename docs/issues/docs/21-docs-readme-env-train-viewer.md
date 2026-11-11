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
- README draft written with a glossary and a facts ledger (scratchpad), checked with `check.py` and `readme_check.py`, and reviewed by four cold-reader passes before the #22 merge; one more pass after folding #22 in.
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

## Management Notes
### Follow-up Candidates
### References
