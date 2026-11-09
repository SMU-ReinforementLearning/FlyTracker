# 3 조준점 계산과 탄속 가정 정리

## Document Relations
- Issue: #3
- Branch: `3-docs-aim-point-ballistics`
- Umbrella: (none) — no umbrella issue exists yet
- Status: in progress

## Summary
Records, as a design note, where the aimer should point if it ever fires a real projectile at the fly: projectile choice, an assumed muzzle speed, the intercept calculation, and why the best aim point is the one that maximises hit probability rather than the mean predicted position. Firing is not implemented; the environment still captures by holding the aim (3 deg, 0.5 m, 0.2 s).

## Goal
- Fix the default assumptions (shot pellets, 50 m/s, 1 m range, decay length 1.5 m) so a later aim-line or capture-by-hit change starts from agreed numbers.
- Keep every number reproducible from a script next to the note.
- Note what the current environment would have to change to support a projectile.

## Scope
- `docs/issues/docs/3-docs-aim-point-ballistics/aim-point-and-projectile-speed.md` (Korean design note for teammates).
- `docs/issues/docs/3-docs-aim-point-ballistics/ballistics_table.py` (stdlib-only calculation behind the note's tables).

## Out Of Scope
- Any code change in `flytracker/` or `viewer/`: no projectile, no lead aim line, no change to capture or reward.
- Measuring real system latency or real salt-pellet speed.
- Checking fly flight parameters or the Korean toy-gun energy limit against primary sources.

## Done Criteria
- [ ] The note states the defaults, the intercept procedure and the best-aim-point rule, with estimates marked as estimates.
- [ ] `ballistics_table.py` reproduces every table value in the note.
- [ ] ko-writing `check.py` shows nothing in sections 1-8 except known false positives, and a cold-reader review has been applied.

## Current State
- Note and script written; awaiting the user's review before the docs commit.
- Next: commit the note, then decide whether to open a PR (the `AGENTS.md` pointer must be removed as the branch's last commit before it).

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 조준점 계산과 탄속 가정 정리 (#3)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/docs/3-docs-aim-point-ballistics.md` filled from the design discussion.
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start` dry run, then the real run: issue #3, branch from `origin/main` @ 46e141e.
#### Notes
- No umbrella issue yet, so `--parent` was not passed (same as #1).

## Management Notes
### Follow-up Candidates
- Lead aim line in the viewer: draw the trajectory from the aimer to the intercept point instead of the straight look line.
- Fly velocity in the observation, or a tracking filter, before any lead-based capture.
- Capture by hit: a fire action, projectile flight in the simulation, reward redesign.
### References
- Design discussion with the user, 2026-11-04 to 2026-11-09 (chat).
