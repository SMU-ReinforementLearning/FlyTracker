# 3 조준점 계산과 탄속 가정 정리

## Document Relations
- Issue: #3
- Branch: `3-docs-aim-point-ballistics`
- Umbrella: (none) — no umbrella issue exists yet
- Status: done

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
- [x] The note states the defaults, the intercept procedure and the best-aim-point rule, with estimates marked as estimates. (2026-11-09)
- [x] `ballistics_table.py` reproduces every table value in the note. (2026-11-09)
- [x] ko-writing `check.py` shows nothing in sections 1-8 except known false positives, and a cold-reader review has been applied. (2026-11-09)

## Current State
- Note and script committed.
- The user decided (2026-11-09) that the fly cannot know where the aim line points, so its behaviour splits into two states, normal and alarm (threat perceived), with no free mode. The note records the decision; the code change is issue #4 (`4-feature-fly-alarm-state`).
- The user corrected the aimer model (2026-11-09): a turret at a user-set position that only turns, like an AA gun. The note now says so; the 1 m range and the fly's threat rule are to be revisited after the turret change.
- PR opened; the `AGENTS.md` pointer was removed in the branch's last commit.

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

### docs: 조준점 계산과 탄속 가정 문서 (#3)
> why: keep the projectile and aim-point assumptions from the design discussion where teammates can find them, with numbers that can be recomputed
#### Scope
- `docs/issues/docs/3-docs-aim-point-ballistics/aim-point-and-projectile-speed.md`, `docs/issues/docs/3-docs-aim-point-ballistics/ballistics_table.py`, this doc.
#### Changes
- Design note (Korean, for teammates): terms, projectile choice (shot pellets over a single BB), drag decay length and flight-time table, intercept iteration, best aim point as the hit-probability maximum, what the environment must change, default values, safety.
- `ballistics_table.py`: stdlib-only; decay length per projectile, horizontal flight time / drop / arrival speed at 1 m and 2 m by numerical integration, pellets needed for 63% / 90% hit, salt grain count per 0.1 g.
#### Verification
- `python docs/issues/docs/3-docs-aim-point-ballistics/ballistics_table.py`: every number in the note's tables matches the output (salt 50 m/s: 28 ms / 0.3 cm / 25.7 m/s at 1 m, 84 ms / 2.4 cm / 13.2 m/s at 2 m; R 3 cm needs 565 / 1,302 pellets).
- ko-writing `check.py`: sections 1-8 clean; section 9 flags "이 메모" self-references only.
- Cold-reader review (fresh subagent, note only): 30-odd findings applied (undefined terms before use, aim point vs intercept point naming, L 1.5 m basis, BB comparison distance, latency ratio, mosquito-raindrop condition mismatch, 1 m range basis). A second pass was stopped at the user's request.
#### Notes
- All numbers are calculations; system latency, salt C_d, real muzzle speed and lethal arrival speed are unmeasured.
- Fly mass (~1 mg), fly speed and the Korean toy-gun energy limit were not checked against sources.

### docs: 초파리 평시와 비상시 결정 기록 (#3)
> why: the user decided the fly cannot sense the aim line, and corrected the aimer model: a fixed turret (like an AA gun) that only turns
#### Scope
- `docs/issues/docs/3-docs-aim-point-ballistics/aim-point-and-projectile-speed.md` (scope, range and current-environment sections), this doc's Current State.
#### Changes
- Scope: the aimer is a turret at a user-set position that only turns; the code at writing time wrongly flies it, to be fixed separately.
- Range: a fixed turret can fire only when the fly comes within 1 m; whether 1 m is enough in a 4 m x 3 m room is revisited once the turret position is set.
- Current environment: free/evade described as the state at writing time; the decision (normal and alarm states, aim-line trigger and free mode removed) points to issue #4; a fixed turret never approaches, so the approach trigger rarely fires and the threat rule is re-decided after the turret work.
- The list of environment changes needed for projectile capture drops the evade item (now decided) and keeps two.
#### Verification
- ko-writing `check.py` on the note: sections 1-8 clean (the first draft had an 8-sentence paragraph; split in two).
#### Notes
- Cold-reader review not re-run for these paragraphs (the user stopped the review loop).

### chore: 작업 마무리와 AGENTS.md 포인터 제거 (#3)
> why: the branch's last commit before the PR; `main` takes PRs only, so the pointer must go now
#### Scope
- `AGENTS.md`, this doc's Status and Current State, the registry row.
#### Changes
- `AGENTS.md` Recent Active Context: pointer line removed, `- (none)` placeholder restored.
- Status: in progress → done, here and in `docs/issues/README.md`.
#### Verification
- `grep -c 3-docs-aim-point-ballistics AGENTS.md` prints 0.
#### Notes
- The registry row will conflict with #4's row if both PRs are squash-merged in turn; resolve by keeping both rows.

## Management Notes
### Follow-up Candidates
- Lead aim line in the viewer: draw the trajectory from the aimer to the intercept point instead of the straight look line.
- Fly velocity in the observation, or a tracking filter, before any lead-based capture.
- Capture by hit: a fire action, projectile flight in the simulation, reward redesign.
### References
- Design discussion with the user, 2026-11-04 to 2026-11-09 (chat).
