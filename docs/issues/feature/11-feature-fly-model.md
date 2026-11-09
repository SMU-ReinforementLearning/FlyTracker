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

### feat: viewer에서 초파리를 실제 모양으로 그리기 (#11)
> why: the fly was a large sphere; the user wanted the real shape, from flybody, at real size in both views, with only the trail to locate it
#### Scope
- `scripts/build_fly_model.py`, `viewer/public/models/` (GLB, licence, notice), `flytracker/env.py`, `flytracker/record.py`, `viewer/src/data/episode.js`, `viewer/src/scene/FlyMarker.jsx`, `ThirdPersonView.jsx`, `FirstPersonView.jsx`, `README.md`, this doc.
#### Changes
- Build script: loads flybody `fruitfly.xml` with MuJoCo at qpos0 (wings spread), welds each visual mesh, simplifies parts over 2,000 faces to ~15% in cm units, merges by material, converts cm → m, MuJoCo axes → viewer axes (head -z, up +y), sRGB → linear colours, writes a 1.6 MB GLB (272,550 → 90,983 faces).
- Python: `snapshot()` and `FRAME_KEYS` gain `flyHeading`.
- Viewer: `FlyMarker` draws the GLB at real size facing the heading, with lights; trail unchanged; the sphere and its alarm colour are gone; older runs derive the heading from positions. Third-person near plane 0.05 → 0.002 m.
- README: viewer section explains the real-size model, its source, and that the trail shows the position.
#### Verification
- Build script output, area kept per material: body 100%, red (eyes) 95%, ocelli 101%, lower 100%, membrane 100%, black 68%, bristle-brown 67%, brown 54% (thin bristles and claws). A first attempt without welding kept only 11-15% and the wings vanished; welding fixed it.
- Top/side matplotlib render of the GLB (scratchpad): head with red eyes at -z, six legs below, translucent veined wings spread sideways, abdomen at +z.
- `uv run pytest`: 28 passed. `npm run build --prefix viewer`: builds.
- `scripts/record_baseline.py --episodes 3`: frames contain `flyHeading`.
- UI evidence: `node .claude/skills/ui-evidence/scripts/shot.mjs --name after` (repo overlay, `http://localhost:5180` served from this worktree; the server was started only for the capture and stopped right after because free memory was low).
  - Commit: 02d1560 (dirty, this change) · Chrome: 156.0.8078.74
  - Serve check: `document.title === 'FlyTracker' && document.body.innerText.includes('12:56')` (this worktree's only run)

| page | viewport | file | overflow | probes | console |
| --- | --- | --- | --- | --- | --- |
| / | 1600x900 | `after-1600x900.png` (scratchpad) | none | `fruitfly.glb` loaded: true | favicon 404, THREE.Clock deprecation, GL ReadPixels perf warnings |
| / | 390x844 (mobile, dpr 2) | `after-390x844.png` (scratchpad) | none | `fruitfly.glb` loaded: true | THREE.Clock deprecation only |

  - Desktop: no sphere and no ring; the trail shows where the fly is; the real-size fly is below one pixel at room scale, as intended.
#### Notes
- Two intermediate versions were dropped at the user's request: a 20x / 40 px enlarged fly, then a fixed-pixel location ring.

## Management Notes
### Follow-up Candidates
- Wing flapping and banked turns in the viewer (would need Python to record roll).
- A size toggle if the team wants to see the fly's shape in the third-person view without zooming in.
### References
- flybody: https://github.com/TuragaLab/flybody (commit d015e9b); Vaxenburg et al., Nature 643, 1312-1320 (2025).
