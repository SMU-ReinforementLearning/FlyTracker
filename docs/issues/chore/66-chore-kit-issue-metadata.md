# 66 issue에 type, label, 담당자를 채우도록 agent-workflow-kit 올리기

## Document Relations
- Issue: #66
- Branch: `66-chore-kit-issue-metadata`
- Umbrella: (none)
- Status: in progress

## Summary
Update the installed agent-workflow-kit so that `issue-start` registers an issue with its sidebar filled in (Type, label, assignee, Priority, sub-issue link) and checks the title, and give the issues registered before this their Type and label.

## Goal
The issue list was hard to scan: 30 of 33 issues read "No type, No labels, No one
assigned". New issues must carry that information from the moment they are created, and
the old ones, closed ones included, must get it afterwards.

## Scope
- Rerun the kit installer from the kit branch `issue-start-metadata` (kit PR #37):
  `.claude/skills/issue-start/` (script, new `issue-backfill.mjs`, tests, `SKILL.md`),
  `docs/agent-workflow/{git-rules,skills,templates}.md`, `agent-system.lock.json`.
- Backfill on GitHub: Type, type label and (for the user's own issues) assignee on the
  existing issues.

## Out Of Scope
- Issues #58, #59, #64 (a teammate's umbrella and its sub-issues): no management document
  or branch names their type, so the backfill left them alone. Their owner decides.
- Priority on old issues, milestones, projects: nothing exists to derive them from, and
  the repo has no milestone.
- Assigning a teammate to #31: it would notify them.

## Done Criteria
- [x] `issue-start` creates an issue with Type, label, assignee and Priority set — #66 itself was created by the new script: Task, `chore`, lhk0721, Medium (2026-11-16 KST)
- [x] Every issue whose type the repo records carries a Type and its label — 30 issues updated, rerun plans nothing (2026-11-16 KST)
- [x] Installed copy passes its own tests: `issue-start.test` 27 cases (2026-11-16 KST)
- [x] Kit PR #37 merged, so the installed files match a kit commit on `main` — squash commit `68c22ae` (2026-11-16 KST)

## Current State
Installer rerun and backfill done. The installed files equal kit `main` at `68c22ae`
(kit PR #37). Open: types for #58, #59, #64 (see Follow-up Candidates).

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: issue에 type, label, 담당자를 채우도록 agent-workflow-kit 올리기 (#66)
> why: the issue list could not be scanned or filtered — issues were registered with a title only
#### Scope
Kit update (system-owned files only) plus this document, the registry row and the pointer.
#### Changes
- `.claude/skills/issue-start/scripts/issue-start.mjs`: title check (`team_language`, no
  type prefix), sidebar plan checked against the repo before the issue is created, Type /
  Priority / sub-issue link set after `gh issue create`.
- `.claude/skills/issue-start/scripts/issue-backfill.mjs` (new): Type and label for
  existing issues, read from the management document or branch name.
- `docs/agent-workflow/git-rules.md`: new section "Registering the issue".
- `agent-system.lock.json`: new hashes; eight stale `__pycache__` entries dropped.
#### Verification
- `node .claude/skills/issue-start/scripts/issue-start.test.mjs` → 27 cases passed.
- `node .githooks/checks/doctor.mjs` → 26 OK, 0 FAIL, 2 WARN (guard ask tier off,
  `PYTHONUTF8` unset — both machine settings that predate this change).
- GitHub after the backfill: 16 Feature, 11 Task, 2 Bug with label and assignee; #31
  Feature + `enhancement` without assignee; #58, #59, #64 untouched.
- Labels `chore`, `refactor` were created in the repo by the scripts.
#### Notes
- Mapping: `feature` → Feature + `enhancement`; `fix` → Bug + `bug`; `docs` → Task +
  `documentation`; `chore` / `refactor` → Task + a label of the same name.

## Management Notes
### Follow-up Candidates
- Ask the owner of #58, #59, #64 for their types, then
  `issue-backfill.mjs --apply --set <n>=<type>`.
### References
- Kit PR: https://github.com/lhk0721/agent-workflow-kit/pull/37
