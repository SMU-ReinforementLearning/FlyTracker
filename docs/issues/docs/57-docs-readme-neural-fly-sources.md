# 57 README에 신경 초파리 출처 적기

## Document Relations
- Issue: #57
- Branch: `57-docs-readme-neural-fly-sources`
- Umbrella: (none)
- Status: in progress

## Summary
README gains a `### 신경 초파리` section that says what the neural fly is, that it cannot run from this repository alone, and where each of its four parts comes from. Until now the neural fly (#31) appeared nowhere in the README; its sources were only in the #31 management doc and in `flytracker/neural_fly.py`.

## Goal
- A reader of the README learns that a third fly model exists, how to select it, what it needs that the repo does not ship, and the origin of each part.
- Record the fact the user relayed on 2026-11-16: the local `flysim` code was written by the teammate with Codex, on top of the Shiu model and the FlyWire annotations. The #31 doc still says its author is unknown.

## Scope
- `README.md`: one new subsection between `### 초파리` and `### 에피소드` with a four-row source table (the table the teammate sent, plus links and a "shipped in the repo?" column), and a pointer to the three published neural runs.
- `docs/issues/feature/31-feature-neural-flight/flysim-source.md`: the two sentences that said the author of `flysim` was not confirmed. Added to scope on 2026-11-16 after PR #56 merged, because the README links to this file and the two would contradict each other.

## Out Of Scope
- The rest of `flysim-source.md` and the #31 management doc, including their "rights unresolved" passages. The user decided on 2026-11-16 that the flysim licence is not a concern (team-internal code, same project) and that the derived CSVs need no redistribution check while they stay out of the repo; the README therefore makes no rights claim. The older passages are left as the teammate wrote them.
- The `환경 옵션` table (does not list `--fly-model`, `--neural-source`, `--neural-data`).
- Deciding the licence of `flysim` or of the derived CSVs.
- Any code or test change.

## Done Criteria
- [x] README has the section; every link in it resolves (`readme_check.py --online`). (2026-11-16)
- [x] Every fact in the section is traceable: option names to `scripts/_common.py`, extra name to `pyproject.toml`, neuron/edge counts and URLs to the #31 doc and its rights file, flysim authorship to the user's statement. (2026-11-16)
- [x] The teammate's local path (`D:\...`) is not in the repo. (2026-11-16)
- [x] User approved the text. (2026-11-16, "머지해")

## Current State
PR #56 was squash-merged at the user's instruction (main @ 7bd0ac8) and this branch was fast-forwarded onto it. README section and the `flysim-source.md` fix are written, uncommitted, waiting at the pre-commit review gate. Nothing pushed.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: README에 신경 초파리 출처 적기 (#57)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
Seed only: this document, the Master Registry row, the AGENTS.md pointer.
#### Changes
- `docs/issues/docs/57-docs-readme-neural-fly-sources.md` created and filled.
- `docs/issues/README.md` +1 row; `AGENTS.md` +1 pointer line.
#### Verification
None needed; no behaviour or rendered page changed.
#### Notes
Branch cut from `origin/main` @ f542106. The local `main` of the main checkout was 6 commits behind and was not used.

### docs: README에 신경 초파리 출처 적기 (#57)
> why: the teammate sent a four-row source table and the user asked for it in the README; the user also relayed that the teammate wrote `flysim` with Codex
#### Scope
`README.md` and two sentences of `flysim-source.md`.
#### Changes
- New `### 신경 초파리` after `### 초파리`: what the model computes (547 neurons, 16,344 connections, spikes to wing force), that connectivity is measured but neuron selection and the spike-to-force mapping are assumptions, that it is not trained and not validated against real flies.
- How to select it (`--fly-model neural`, `--neural-source` / `FLYTRACKER_NEURAL_SOURCE`, `uv sync --extra neural`) and that the rule fly and the fly agent need none of it.
- Source table: Shiu et al. Drosophila_brain_model (MIT, pinned commit) with the Zenodo connectivity record; FlyWire neuron annotations (pinned commit) with the FlyWire terms; flysim = local project the teammate wrote with Codex; `neuromechanics.py` and `neural_fly.py` from #31. Third column says whether the repo ships it.
- Closing paragraphs: the three published neural runs open at `https://flytracker-ewk.pages.dev/?issue=31`, replay needs no flysim, and they were recorded on 2026-11-12 under the old capture rule (3° for 0.2 s); links to `flysim-source.md` and the #31 doc. No statement about redistribution rights (user decision, see Out Of Scope).
- `flysim-source.md`, section "코드 확보 경위": "author, first distribution address and release number not confirmed" → flysim is team-internal code the teammate wrote with Codex on top of the external material, never distributed; "ask the user about provenance and sharing rights" → get the code bundle from the teammate who wrote it.
#### Verification
- `python .claude/skills/readme-upkeep/scripts/readme_check.py README.md --online` and the same on `flysim-source.md` → `2 file(s): 0 fail, 0 warn` (external URLs and relative links answered).
- Deployed site after the #56 merge: `https://flytracker-ewk.pages.dev/runs/index.json` lists 29 runs, the three `2026-11-12_18*` runs carry issue 31, and each of their episode files answers 200.
- `python .claude/skills/ko-writing/scripts/check.py README.md --from "### 신경 초파리" --to "### 에피소드"` → no failures; warnings read and kept (one date, which is the "as of" of an undecided fact).
- `grep -n "D:" README.md` → no local path.
- `uv run --extra dev python -m pytest -q` → 139 passed, 47 skipped (after `npm ci --prefix viewer`; without `viewer/node_modules` one viewer test fails in a fresh worktree).
- Not verified: flysim authorship. It is the user's relay of the teammate's statement; no file in this repo can confirm it. Not run: the neural fly itself — this machine has no flysim source.
#### Notes
- `### 초파리` still opens its second paragraph with "피하는 법은 두 가지다" (rule fly, fly agent). Left as is: the neural fly is opt-in and described in its own section.

## Management Notes
### Follow-up Candidates
- PR #56's body reports 4 neural integration tests failing on `main` f542106 when the flysim source is supplied (13- vs 17-dim observation; angle-based capture expectations vs the beam rule). Not reproducible here. The neural fly has not been brought up to env v3–v5.
- `환경 옵션` table lacks `--fly-model`, `--neural-source`, `--neural-data`.
- The three published neural runs predate the laser capture rule; none has been re-recorded under env v5.
### References
