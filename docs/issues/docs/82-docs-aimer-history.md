# 82 조준기 변천사 문서로 정리하기

## Document Relations
- Issue: #82
- Branch: `82-docs-aimer-history`
- Umbrella: (none)
- Related: #1, #7, #9, #34, #35, #42, #45, #49, #51, #69, #72 (the aimer changes this document retells; nothing in them is changed)
- Status: in progress

## Summary
Writes one Korean document that tells how the aimer changed from issue #1 to #72: action, observation, reward, capture condition, baseline and training results, each with the reason for the change and the numbers measured at the time. The user asked for it on 2026-11-25 after a Q&A about the aimer's history ("나중에 발표에 쓸만한 내용들이네. 앞선 변천사부터 싹 문서화해"), as material for the team's presentation.

## Goal
- A teammate who knows reinforcement learning but did not follow the aimer work can read the document alone and prepare the aimer part of the presentation.
- The two points the user asked about in the conversation are answered in the document: how the observation dimension changed (19 → 13 → 17 → 18) and why the reward uses a logarithm of the beam distance.
- Every number has its sample (episode seeds, which time metric) next to it and a source in this repository.

## Scope
- `docs/issues/docs/82-docs-aimer-history/aimer-history.md` — the document (Korean, 문서체).
- `docs/issues/docs/82-docs-aimer-history/aimer-history.terms.md`, `aimer-history.facts.md` — the glossary and fact ledger the ko-writing skill asks for; they record where each number comes from.
- This management doc, the registry row, the `AGENTS.md` pointer.

## Out Of Scope
- Any code, README or viewer change. The README stays the source of truth for the current values; the document links to it.
- New measurements. Every number is taken from existing documents, except five values computed in the document from those (listed in the fact ledger).
- Figures and slides. The document has tables only.
- The fly's side beyond what the aimer's results need (rule fly, neural fly as opponents).

## Done Criteria
- [x] The document covers every aimer change from #1 to #72 in time order, with the reason and the measured result. (2026-11-25)
- [x] Every number in the document is in the fact ledger with its source; the ones computed here are marked as computed. (2026-11-25)
- [x] ko-writing `check.py` with the glossary and ledger: no banned pattern, endings consistent; remaining warnings judged one by one. (2026-11-25)
- [x] Cold-reader review by a fresh subagent that read only the document; every returned item fixed or answered. (2026-11-25, two passes; no third pass after the second round of fixes)
- [x] Relative links in the document resolve. (2026-11-25)
- [ ] PR merged; `AGENTS.md` pointer removed in the branch's last commit.

## Current State
2026-11-25. Document, glossary and fact ledger written and reviewed by cold readers. The user approved at the review gate with "머지해" (commit, push, PR and squash merge for this branch). Registration commit and docs commit made; the pointer removal is the last commit before the PR.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 조준기 변천사 문서로 정리하기 (#82)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Management doc, registry row, `AGENTS.md` pointer.
#### Changes
- Doc filled from the 2026-11-25 conversation: reader, the two questions the user asked, what is out of scope.
#### Verification
- `issue-start.mjs` created issue #82 (Type Task, label documentation, assignee the user, Priority Medium), branch from `origin/main` @ ee4c5a1, worktree `FlyTracker-82`.
#### Notes
- Priority Medium was proposed by the agent, not stated by the user: the presentation date is not known and nothing else waits on this.
- No umbrella: the only open umbrella (#58) is the teammate's workstream.
- The main checkout's local `main` was at 61d2b6b, four commits behind `origin/main`. The first answer in the conversation was read from it and missed #72 (aimer v1 under env version 6); the document is written from `origin/main`.

### docs: 조준기 변천사 문서 쓰기 (#82)
> why: the user wants the aimer's history, with the reasons and numbers, kept as one document the team can use for the presentation
#### Scope
`docs/issues/docs/82-docs-aimer-history/aimer-history.md`, `aimer-history.terms.md`, `aimer-history.facts.md`, this doc.
#### Changes
- `aimer-history.md` (Korean): overview with three turning points; how things are measured (two capture conditions, two time metrics, four episode-seed sets, the gate); per-version tables (settings, observation, reward, baseline results on seeds 10000-10199); ten change sections from the moving aimer (#1) to aimer v0 / v1 (#72); rejected options; limits; links.
- Chapter "학습과 추적의 구조" (added after the first review round): the order of one training run in `train.py` and what Stable-Baselines3 does; the 0.01 s / 0.02 s intervals; the rule tracker's computation step by step; what gain means and why 25 /s alone lags by about 12 mm at 2 m; how the tracking assist combines actions (residual RL); the rule trigger and why it still misfires; which of search / tracking / firing aimer v1 learned; which reward values have a recorded reason and which were compared; a table of questions expected at the presentation. Two items added to "한계" (four → six); Stable-Baselines3 defined at its first use; a link to the SAC Q&A document (#73).
- The two questions from the conversation are answered in it: the observation tables (19 → 13 → 17 → 18 and the current 18 items) and the section on the beam-distance penalty (both formulas, a table of both penalties at the same distances, why a logarithm, what each part of the formula does).
- `aimer-history.terms.md`: 31 terms with the section each is defined in; shared terms copied from `ui-text.glossary.md`.
- `aimer-history.facts.md`: every number with sample, condition and source; a table of the values computed here.
#### Verification
- Sources read on `origin/main` @ ee4c5a1: README (aimer state, R, baseline, v0 / v1), management docs of #1, #7, #9, #34, #35, #42, #45, #49, #51, #69, #72, gate documents of #35 and #51, `flytracker/env.py` version comment, `flytracker/baseline.py` (the search starts with the sweep when the fly was never seen).
- ko-writing `check.py --glossary --facts`: no banned pattern, 233 sentences all in 해라체, no paragraph over 6 sentences, no heading over 15 characters. Warnings left, judged: the title and the three overview items use section names before their sections define them (each item explains itself in the same line); "발" inside "발사" is a substring match; ledger "same value" and "mixed sample" lines are small integers shared by different rows; settings values live in the ledger's second table, which the script does not read.
- Cold reader, pass 1 (fresh subagent, document only): about 50 items. Fixed: camera, screen coordinates, tracking vs search were never introduced; the reward's items were nowhere; 6 state dimensions listed as 5; "탐색" used for SAC exploration too; "놓치다" used for both losing sight and failing to capture; three names for each capture condition and for the dense penalty; a 60-episode seed set missing from the table; the old spin search not introduced.
- Cold reader, pass 2 (another fresh subagent): about 45 items, smaller. Fixed: what the rule fly reacts to; what an episode seed fixes; room size and the 2 m reference; the angle-penalty problem was a prediction, not an observation; which search step runs before the first sighting; the stimulus; "실패한 시도" renamed "기각한 안" because two rows were never tried; a sentence that put version 5 and version 6 results side by side removed.
- Both readers' three-sentence summaries match the intended conclusion.
- Arithmetic recomputed: penalties at 125 / 12.5 / 1.25 mm for both formulas, 3° ÷ 0.036° = 83, 0.50 ÷ 1.49 = 0.34, 4.858 − 2.941 = 1.917.
- Relative links: all 7 targets exist.
- Added on 2026-11-25 from a second Q&A in another session (the user: "발표용으로 지금까지 내용 정리해줘 ... 작성한 문서에 덧붙여 문서화해"): chapter "학습과 추적의 구조" before "기각한 안". Checked against code on this branch (`scripts/train.py`, `flytracker/env.py`, `wrappers.py`, `baseline.py`, `players.py`), README and the management docs of #45, #49, #51, #69, #72. `check.py` after the addition: no banned pattern, 355 sentences in 해라체, no long paragraph or heading; the heading "쏘는 규칙의 계산" is flagged for its modifier and kept because "쏘는 규칙" is the document's term. One cold-reader pass on the new chapter (fresh subagent, document only): about 35 items. Fixed: "판정" used for both the gate and the 0.01 s computation (the latter is now "계산 간격"); 1,000,000 updates against "from step 100"; 0.25 s holds for yaw only; DQN listed as a drop-in although it needs discrete actions; "임시 실험" unexplained; v2 and #85 used before being introduced; a teammate's remark quoted without context; two lists of what is hand-made that differed; the reward table's "no positive reward" row next to the capture reward; a −23.16 with no claim attached (removed); the limits list missing the second unmeasured item and #85. No second pass was run after these fixes.
#### Notes
- No third cold-reader pass was run after the second round of fixes.
- The added chapter states as unrecorded or unmeasured: why the action interval is twice the judgment interval; any comparison of gain 25 /s, assist scale 0.2 or the reward values against other values; whether aimer v1's speed-up comes from search or from the correction; which of three mechanisms causes misfires. It points to #85 (in progress, no result) for why the unassisted SAC aimers fail.
- The first answers of that second conversation were also read from the stale local `main` and said no learned aimer runs under env version 6; the chapter follows `origin/main` (aimer v1, #72).
- Not fixed, with reasons: the first SAC section states its result before the version 2 change that preceded it (conclusion first); the tracking assist is defined one sentence after the four candidates are first mentioned.
- Stated as unknown in the document because no record explains them: why the old spin search never saw the fly; why the correction hurts with the angle penalty; the differences between stimulus on and off.
- The reason for capping the penalty at 1 m is not recorded anywhere; the document says 1 m and 0.1 are starting values. An earlier chat answer gave a reason for the cap that was the agent's own reading, and it is not in the document.

## Management Notes
### Follow-up Candidates
- Figures for the presentation (baseline capture by env version, the two penalty curves, the four SAC conditions), through the `report-figures` skill.
### References
- `README.md` sections "조준기의 state와 action", "조준기의 R", "기준선과 비교", "조준기 v0과 v1".
- Gate documents of #35, #51, #72.
