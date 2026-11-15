# 44 학습한 조준기로 돌린 버전 3 에피소드 올리기

## Document Relations
- Issue: #44
- Branch: `44-chore-sac-v3-episodes`
- Umbrella: (none)
- Status: done

## Summary
Episodes of the #35 SAC aimer under env version 3, on the same seeds and config as the two #42 baseline runs, published so the viewer shows them next to those runs. The #42 group in the viewer held only rule-baseline runs; the user asked (2026-11-15) for the learned-model version under the same conditions.

## Goal
Two published runs that pair episode by episode with `2026-11-15_201137_baseline` (seeds 10000-10002) and `2026-11-15_201250_baseline` (seeds 10114-10118), played by a trained aimer instead of the rule baseline.

## Scope
- Model: `sac-fs1-s0` final model from #35 (`runs/2026-11-12_131635_sac-fs1-s0/model.zip` in the main checkout, trained under env version 2). Our choice among the 6 adopted models: frame stack 1, training seed 0, and the only one that caught a fly under version 3 in #42's 200-seed measurement.
- `docs/issues/chore/44-chore-sac-v3-episodes/record_model_v3.py`: records a trained aimer under the current env with the default `EnvConfig` (what `record_baseline.py` uses with no flags), skipping the env-version check in `load_opponent` on purpose.
- `published/2026-11-15_220333_sac-fs1-s0-v3/`, `published/2026-11-15_220345_sac-fs1-s0-v3/`, published with `--issue 42` so the viewer groups them with the baseline runs the user is comparing against.

## Out Of Scope
- Training a model under version 3. The user was asked whether the vast.ai instance they mentioned was for that and answered that no instance is to be rented (2026-11-15).
- The other 5 #35 models.
- Changes to `scripts/`, the package or the viewer.

## Done Criteria
- [x] Two runs recorded with the SAC model on seeds 10000-10002 and 10114-10118, env config equal to the paired baseline run's. (2026-11-15 22:05)
- [x] Both published under issue 42 and listed by the viewer build. (2026-11-15 22:10)
- [x] Merged to main (the Cloudflare viewer shows them only after the merge). (2026-11-15, by the PR for this branch)

## Current State
Done 2026-11-15. Runs recorded, published and verified; PR opened and merged at the user's request, and the `AGENTS.md` pointer was removed in the branch's last commit. The merge criterion above is ticked by the PR itself. No aimer trained under version 3 exists yet (see #42 Follow-up Candidates).

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: 학습한 조준기로 돌린 버전 3 에피소드 올리기 (#44)
> why: the #42 group in the viewer had only rule-baseline runs; the user asked for the learned-model version under the same conditions
#### Scope
Management doc, registry row, `AGENTS.md` pointer, `record_model_v3.py`, the two published runs.
#### Changes
- `record_model_v3.py --seed 10000 --episodes 3` and `--seed 10114 --episodes 5` with the `sac-fs1-s0` model: 0/3 and 0/5 captured. Tag `step_1000000`; `config.json` has `algo.model` and `algo.trainedEnvVersion: 2`; `run.json` notes say the model was trained under version 2.
- Both copied with `publish_run.py --issue 42`.
#### Verification
- Baseline reproduces before recording: `record_baseline.py --no-save` gives 0/3 (seed 10000) and 1/5, 2.62 s (seed 10114), as published in #42.
- Published `config.json`: `envVersion` 3 and `env` equal to the paired baseline run's `env`; episode `meta.seed` 10000-10002 and 10114-10118, same as the baseline runs.
- Per episode (min beam distance while visible): 10000 never saw the fly (visible 0 %, return -80.30); 10001 1.22 mm, capture progress peaked at 0.07; 10002 4.91 mm; 10114 5.29 mm; 10115 6.48 mm; 10116 never saw the fly; 10117 5.52 mm; 10118 9.23 mm.
- `npm run build --prefix viewer`: `viewer/dist/runs/index.json` lists the two `sac` runs under issue 42 next to the two baseline runs. `uv run python -m pytest -q`: 109 passed, 45 skipped.
#### Notes
- The viewer page itself was not opened in a browser; only the build index was checked.
- `publish_run.py` warns that #42 has no `training` label, as it did for the baseline runs.
- Seed 10116 is the one episode the baseline captures (2.62 s); the SAC model never gets the fly in view there.
- The user sent "rent a vast.ai instance" mid-task; recording took seconds on the laptop, so they were asked what it was for and chose not to rent.

### chore: #44 마무리 (#44)
> why: last commit before the PR; a protected branch cannot take the pointer removal after the merge
#### Scope
`AGENTS.md`, `docs/issues/README.md`, this doc.
#### Changes
- Pointer line removed, registry row and Status set to done, Current State rewritten.
#### Verification
- No code or data changed since the previous commit (109 passed, 45 skipped there).
#### Notes
- The user approved the commit and asked for the merge (2026-11-15).

## Management Notes
### Follow-up Candidates
### References
