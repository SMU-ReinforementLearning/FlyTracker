"""flybody(TuragaLab) 초파리 몸체 메시를 viewer 용 GLB 한 파일로 만든다.

    git clone --depth 1 https://github.com/TuragaLab/flybody.git <dir>
    uv run --no-project --with mujoco --with trimesh --with fast-simplification \\
        python scripts/build_fly_model.py <dir>/flybody/fruitfly/assets/fruitfly.xml

결과는 viewer/public/models/fruitfly.glb 다. 한 번 만들어 저장소에 넣어 두므로 평소에는 다시 돌릴 필요가 없다.

- MuJoCo 로 기본 자세(qpos0)의 부위별 위치를 계산한다. 이 자세에서 날개는 양옆으로 펼쳐져 있다.
- 부위마다 원래 단위(cm)에서 면 수를 줄인 뒤, 같은 재질의 부위를 한 메시로 합친다 (원본 약 27만 개).
  작은 부위는 줄이지 않는다. 줄인 뒤 재질별 겉넓이가 원본의 몇 % 인지 출력한다.
- 단위를 cm 에서 m 로, 축을 MuJoCo(머리 +x, 위 +z)에서 viewer(머리 −z, 위 +y)로 바꾼다. 원점은 가슴(thorax) 중심이다.

flybody 는 Apache-2.0 이다. 출처와 바꾼 점은 viewer/public/models/fruitfly.NOTICE.txt 에 적는다.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import fast_simplification
import mujoco
import numpy as np
import trimesh

OUT = Path(__file__).resolve().parent.parent / "viewer" / "public" / "models" / "fruitfly.glb"
CM_TO_M = 0.01
# MuJoCo (x 앞, y 왼쪽, z 위) → viewer (앞 −z, 왼쪽 −x, 위 +y)
AXES = np.array([[0.0, -1.0, 0.0], [0.0, 0.0, 1.0], [-1.0, 0.0, 0.0]])


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("xml", help="flybody/fruitfly/assets/fruitfly.xml")
    p.add_argument("--faces", type=int, default=40000, help="줄인 뒤 전체 면 수 목표")
    p.add_argument("--keep-small", type=int, default=2000, help="면이 이보다 적은 부위는 줄이지 않는다")
    p.add_argument("--out", type=Path, default=OUT)
    args = p.parse_args()

    m = mujoco.MjModel.from_xml_path(args.xml)
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)

    # 충돌용 캡슐, 타원체는 그리지 않는다
    mesh_geoms = [g for g in range(m.ngeom) if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH]
    total = sum(int(m.mesh_facenum[m.geom_dataid[g]]) for g in mesh_geoms)
    keep = args.faces / total
    groups: dict[str, dict] = {}
    for g in mesh_geoms:
        mid = m.geom_dataid[g]
        v = m.mesh_vert[m.mesh_vertadr[mid] : m.mesh_vertadr[mid] + m.mesh_vertnum[mid]].astype(float)
        f = m.mesh_face[m.mesh_faceadr[mid] : m.mesh_faceadr[mid] + m.mesh_facenum[mid]].astype(np.int64)
        part = trimesh.Trimesh(v, f, process=True)  # 같은 자리 꼭짓점을 합쳐 면을 잇는다. 안 하면 단순화가 면을 통째로 지운다
        area0 = part.area
        v, f = part.vertices, part.faces
        if len(f) > args.keep_small and keep < 1.0:
            v, f = fast_simplification.simplify(v, f, target_reduction=1.0 - keep)
        world = v @ d.geom_xmat[g].reshape(3, 3).T + d.geom_xpos[g]
        matid = m.geom_matid[g]
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_MATERIAL, matid) if matid >= 0 else "default"
        rgba = m.mat_rgba[matid] if matid >= 0 else m.geom_rgba[g]
        gr = groups.setdefault(name, {"v": [], "f": [], "n": 0, "rgba": rgba, "area0": 0.0, "faces0": 0})
        gr["v"].append(world)
        gr["f"].append(f + gr["n"])
        gr["n"] += len(world)
        gr["area0"] += area0
        gr["faces0"] += int(m.mesh_facenum[mid])

    scene = trimesh.Scene()
    kept = 0
    for name, gr in sorted(groups.items()):
        v = np.concatenate(gr["v"]) @ AXES.T * CM_TO_M
        f = np.concatenate(gr["f"])
        mesh = trimesh.Trimesh(vertices=v, faces=f, process=False)
        area_ratio = mesh.area / (gr["area0"] * CM_TO_M**2)
        # MuJoCo 색은 화면 색(sRGB)이고 glTF baseColorFactor 는 선형 값이라 바꿔 넣는다
        rgba = [srgb_to_linear(float(c)) for c in gr["rgba"][:3]] + [float(gr["rgba"][3])]
        mesh.visual = trimesh.visual.TextureVisuals(
            material=trimesh.visual.material.PBRMaterial(
                name=name,
                baseColorFactor=rgba,
                metallicFactor=0.0,
                roughnessFactor=0.6,
                alphaMode="BLEND" if rgba[3] < 1.0 else "OPAQUE",
                doubleSided=True,
            )
        )
        scene.add_geometry(mesh, node_name=name, geom_name=name)
        kept += len(mesh.faces)
        print(f"{name:14s} {gr['faces0']:7d} -> {len(mesh.faces):6d} faces, area kept {area_ratio:.0%}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(trimesh.exchange.gltf.export_glb(scene))
    lo, hi = scene.bounds
    print(f"faces {total} -> {kept}, size {args.out.stat().st_size / 1024:.0f} KB")
    print(f"bounds (m): x {lo[0]:.4f}~{hi[0]:.4f}, y {lo[1]:.4f}~{hi[1]:.4f}, z {lo[2]:.4f}~{hi[2]:.4f}")


if __name__ == "__main__":
    main()
