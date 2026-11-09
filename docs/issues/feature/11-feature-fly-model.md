# 11 viewer에서 초파리를 실제 모양으로 그리기

## Document Relations
- Issue: #11
- Branch: `11-feature-fly-model`
- Umbrella: (none) — no umbrella issue exists yet
- Related: #9 (fly flight model; its design note gets two evidence upgrades here)
- Status: in progress

## Summary
Replaces the large sphere that stood for the fly in the viewer with a real fruit fly model at real size (body about 3 mm), built from the flybody MuJoCo model (TuragaLab, Apache-2.0). Both views draw the fly at real size; the third-person view relies on the trail to show where it is, as the user asked.

## Goal
- A fly-shaped model (head, eyes, wings, legs, abdomen) facing its flight direction, at real size in both views.
- A small, reproducible asset: one GLB built by a committed script from the upstream meshes, with the Apache-2.0 licence and a notice of changes next to it.
- Python stays the source of truth: the heading is recorded per frame, the viewer only draws it.

## Scope
- `scripts/build_fly_model.py` (mujoco + trimesh + fast-simplification via `uv run --with`, not project dependencies).
- `viewer/public/models/fruitfly.glb`, `fruitfly.LICENSE.txt`, `fruitfly.NOTICE.txt`.
- `flytracker/env.py`, `flytracker/record.py`: frame key `flyHeading`.
- `viewer/src/data/episode.js` (heading, with a fallback from positions for older runs), `viewer/src/scene/FlyMarker.jsx`, `ThirdPersonView.jsx` (camera near plane 0.002 m so the real-size fly can be approached), `FirstPersonView.jsx`.
- `README.md` viewer section.
- #9 design note and a `fly.py` comment: evidence levels upgraded from the sources read after #9 merged.

## Out Of Scope
- Wing flapping, body banking during saccades, leg retraction in flight.
- A location marker in the third-person view (the user asked for none; the trail is enough).
- Any change to the simulation.

## Done Criteria
- [x] The GLB keeps the fly's shape: surface area kept per material is reported by the build script, and a top/side render shows head at -z, legs down, wings spread. (2026-11-09)
- [x] `uv run pytest` and `npm run build --prefix viewer` pass. (2026-11-09)
- [x] UI evidence at 1600x900 and 390x844 shows the model loaded, no sphere, no ring, no overflow. (2026-11-09)

## Current State
- Implemented and verified in the worktree; ready to commit, PR and merge.

## Work Log
<!-- one `### <commit title>` per commit, written BEFORE the commit and staged with it -->

### chore: viewer에서 초파리를 실제 모양으로 그리기 (#11)
> why: issue registered, branch and worktree created, this document seeded
#### Scope
- Management doc, Master Registry row, `AGENTS.md` pointer.
#### Changes
- `docs/issues/feature/11-feature-fly-model.md` filled from the user's requests (real shape instead of a sphere; use flybody; real size in the third-person view too; no location ring).
- `docs/issues/README.md` +1 row; `AGENTS.md` Recent Active Context pointer.
#### Verification
- `issue-start`: issue #11, branch from `origin/main` @ 02d1560.
#### Notes
- No umbrella issue yet, so `--parent` was not passed.

## Management Notes
### Follow-up Candidates
- Wing flapping and banked turns in the viewer (would need Python to record roll).
- A size toggle if the team wants to see the fly's shape in the third-person view without zooming in.
### References
- flybody: https://github.com/TuragaLab/flybody (commit d015e9b); Vaxenburg et al., Nature 643, 1312-1320 (2025).
