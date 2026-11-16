# 62 issue 화면을 초파리, 조준기, 환경으로 나누고 항목마다 바꾼 issue 보여 주기

## Document Relations
- Issue: #62
- Branch: `62-feature-issue-page-owner-split-provenance`
- Umbrella: (none)
- Status: done

## Summary
The viewer's issue page now groups every value by its owner (fly, aimer, environment) and shows, on hover, which issue set each value. Before, one "조건" card mixed environment rules with aimer hardware and held no fly value at all, and the "보상" card showed only the aimer reward although every run also stores the fly reward. Each row and card name is now a link: hovering shows the issue number and title, who opened the PR, the merge date and the reason; clicking opens that GitHub issue in a new window.

## Goal
- A reader can tell at a glance whose value a row is: the fly's flight and senses, the aimer's body and view, or a rule that binds both.
- The fly reward is visible when a learned fly is present, with labels that say reward where the aimer's say penalty.
- A reader who wonders "who decided this, when, and why" gets the answer without leaving the page, and one click away from the issue.

## Scope
- `viewer/src/data/experiment.js`: `experimentOf` returns `fly` / `aimer` as `{ cards, settings, rewards }`, plus `environment`, `facts`, `envVersion`. New fly rows (flight values, rule-fly threat values, learned-fly observation delay, neural-fly stimulus values), new aimer rows (yaw/pitch rate, angular acceleration), new environment row (fly start distance). Every row carries `src`, the config path it comes from.
- `viewer/src/data/history.js` (new): hand-written table `src → [issue, reason]`, issue metadata (title, PR author, merge date, lowest env version that contains the change), and `changeOf(src, envVersion)`.
- `viewer/src/components/IssuePage/`: `Side`, `RowsCard`, `Source`; hover/focus popover; the "조건" and "보상" sections become "환경" plus per-side "설정" / "보상" cards.
- `tests/test_viewer_experiment.py` (new): runs both modules in node against every published issue.
- `README.md` issue-page section, `ui-text.glossary.md`.

## Out Of Scope
- Fetching issue data from the GitHub API at run time (60 unauthenticated calls per hour, and the page must work offline). The table is static and must be extended by hand.
- Provenance for run-specific overrides (a run that passes `--reward beam=0`): the popover names the issue that set the default or last changed the meaning, not the run that overrode it.
- The run panel and the replay screen.
- `aimer.other` cards (policies the viewer does not recognise) have no provenance.

## Done Criteria
- [x] Fly, aimer and environment values are in separate places; no aimer hardware row is left under environment. (2026-11-16)
- [x] Fly reward rows appear only when a learned fly is present; aimer settings and reward are hidden when no run has an aimer. (2026-11-16; no published run has a learned fly, so the visible case is covered by code path only)
- [x] Every row and card name shown for every published issue resolves to an issue in `history.js` (test). (2026-11-16)
- [x] Hover and keyboard focus show the popover; the link opens `…/issues/<n>` with `target="_blank"`. (2026-11-16, probes)
- [x] No horizontal overflow at 1600 px and 390 px. (2026-11-16)
- [x] User approved the layout and the popover text. (2026-11-16, "머지해", after two rounds on the popover position)

## Current State
Done and committed. When an issue changes a default value or what a value means, add one line to `viewer/src/data/history.js`; open items are under Follow-up Candidates.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: issue 화면을 초파리, 조준기, 환경으로 나누고 항목마다 바꾼 issue 보여 주기 (#62)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Seed only: this document, the Master Registry row, the AGENTS.md pointer.
#### Changes
- This document created and filled; `docs/issues/README.md` +1 row; `AGENTS.md` +1 pointer line.
#### Verification
None needed.
#### Notes
Branch cut from `origin/main` @ 7bd3ea5.

### feat: issue 화면을 초파리, 조준기, 환경으로 나누고 항목마다 바꾼 issue 보여 주기 (#62)
> why: the user asked whether the reward should be split per side and how the conditions should be split, chose the "merge into the side columns" option, and asked for a hover popover (who, when, why, which issue) that opens the GitHub issue in a new window on click
#### Scope
See Scope above. One commit: the split and the provenance touch the same functions and rows.
#### Changes
- Split by owner. Environment: env version, room, episode length, capture range / hold / distance, fly start distance, record count, notes. Aimer "설정": position, FOV, zoom, yaw and pitch rate, angular acceleration, pitch limit, start direction. Aimer "보상": `env.reward`. Fly "설정": depends on the fly kinds present — flight values for rule and learned flies, threat values for the rule fly only, observation delay for the learned fly only, stimulus values for the neural fly (only where `stimulus.enabled`). Fly "보상": `env.fly_reward`, only from runs with a learned fly.
- Fly reward labels flip the aimer's wording (시간 벌점 → 버틴 시간 보상, 포획 보상 → 포획 벌점) because `FlyRewardWeights` is the aimer reward with the sign flipped.
- Comparison: settings and reward lists are diffed only when both sides have them (`diffSection`); otherwise a newly appearing card would mark every row as changed from "없음".
- Provenance: `history.js` holds 12 issues and 54 keys. `changeOf` returns the last entry whose issue's `env` is ≤ the page's highest env version, so the same row names #1 on a version-2 page and #42 on a version-3 page. Issues that only added a comment to a value are not listed.
- UI: the link has no text and covers its row through `::after`; the popover is a sibling `role="tooltip"` shown on `:hover` and `:focus-within`, anchored at the row's bottom-right corner, at most 34rem wide and never wider than the row, and `display: none` when hidden (does not extend the scroll area). The first version spanned the row's full width directly under it; the user found it covered everything below ("바로 아래 걸 다 가려버리니까", 2026-11-16), so it was narrowed and moved to the right end. Re-captured at 1600 px and 390 px with "확대 화면" focused: overflow none. In the half-width fly and aimer cards that still covered the values of the two or three rows below, and the user chose to move it out of the card ("카드 밖으로 빼줘. 다른 표는 가려도 되니까"). Final rule: while the fly and aimer columns sit side by side (container query on `.column`, ≥ 680 px), a fly row's popover opens to the right over the aimer column and an aimer row's opens to the left over the fly column, top-aligned with the row; in the full-width environment card and in the single-column layout it stays at the row's bottom-right corner. Re-captured with "확대 화면" (aimer), "급선회 각도" (fly) and "포획 범위" (environment) focused at 1600, 1000 and 390 px: overflow none in all nine; looked at the aimer capture at 1600 px (popover over the fly card, aimer table fully visible).
#### Verification
- `uv run --extra dev python -m pytest -q` → 145 passed, 47 skipped (139 before; 6 new in `tests/test_viewer_experiment.py`).
- `npm run build --prefix viewer` → built.
- `readme_check.py README.md` → 0 fail, 0 warn.
- ui-evidence on the built site (`npm run preview`, port 4962), commit: uncommitted tree on 7bd3ea5, serve check `document.title === 'FlyTracker'`, ready when more than 5 source links exist:

| page | viewport | overflow | source links | console |
| --- | --- | --- | --- | --- |
| /?issue=51 | 1600x2300 | none | 35 | favicon 404 only (present on main) |
| /?issue=51 | 390x3400 (mobile, dpr 2) | none | 35 | clean |
| /?issue=31 | 1600x2300 | none | 25 | favicon 404 only |
| /?issue=31 | 390x3400 (mobile, dpr 2) | none | 25 | clean |
| /?issue=42 | 1600x2300 | none | 35 | favicon 404 only |
| /?issue=42 | 390x3400 (mobile, dpr 2) | none | 35 | clean |
| /?issue=51, "포획 범위" focused | 1600x2300, 390x3400 | none | popover `display: flex`; label "포획 범위, #42 포획 조건을 레이저 명중으로 바꾸기"; href `…/issues/42`, target `_blank` | — |

  Captures are in `.ui-evidence/` (gitignored), not committed. Looked at: #51 desktop with popover (three sections, popover under the row), #31 desktop (stimulus rows, no fly reward, three aimer cards), #51 phone (single column, no clipping).
- Not verified: real mouse hover and a real click (the popover was shown through keyboard focus, which uses the same CSS rule; the click target was read from the link's `href`/`target`). The fly-reward card with a learned fly present — no published run has one. #22, #35, #45, #49 pages were covered by the test, not by captures.
#### Notes
- Provenance facts came from a read-only sub-agent pass over `git log -S`, the squash commits and the management docs; its unresolved points: the reasons for #1's initial values are not recorded anywhere (the popover says so), and `ENV_VERSION`'s comment says "#33 까지" where #33 is a PR number.
- The published neural runs have no `envVersion` (counted as 1) although #31 merged during version 2, so #31's `env` is 1 in the table.
- Row order inside environment changed (capture rows now follow room and episode length).

### chore: #62 마무리 (#62)
> why: last commit before the PR
#### Scope
Status done, AGENTS.md pointer removed, registry row set to done.
#### Changes
- This document: Status, Current State, follow-up candidates. `docs/issues/README.md`: #62 row → done. `AGENTS.md`: pointer line removed.
#### Verification
None needed.
#### Notes
The user said "머지해" on 2026-11-16; taken as approval to commit, push, open the PR and merge it, as for #57.

## Management Notes
### Follow-up Candidates
- Real mouse hover and click were not exercised by the captures (keyboard focus was). The user was asked to try them on the preview.
- The reasons for #1's initial values (room size, FOV, turn rates, reward weights) are recorded nowhere; the popover says so. Fill them in if the team lead supplies them.
- The fly reward card has not been seen with real data: no published run has a learned fly.
- Popover text for a run that overrides a default (`--reward beam=0`) names the issue that set the default, not the run's own issue.
### References
