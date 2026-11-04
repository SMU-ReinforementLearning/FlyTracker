import { useFrame } from '@react-three/fiber'
import { useMemo } from 'react'
import * as THREE from 'three'
import { newSample, sample } from '../data/episode.js'
import { clock } from '../playback/clock.js'

const UP = new THREE.Vector3(0, 1, 0)

/** 조준기 위치 C 에서 방향 f 로 나갔을 때 방 벽에 닿는 거리. 조준선을 방 안에서만 그린다. */
function distanceToWall(C, f, [w, h, d]) {
  const lo = [-w / 2, 0, -d / 2]
  const hi = [w / 2, h, d / 2]
  let best = Infinity
  for (let i = 0; i < 3; i++) {
    const dir = f.getComponent(i)
    if (Math.abs(dir) < 1e-9) continue
    const t = ((dir > 0 ? hi[i] : lo[i]) - C.getComponent(i)) / dir
    if (t > 0 && t < best) best = t
  }
  return Number.isFinite(best) ? best : 0
}

/**
 * 조준기 몸체, 시야 frustum, 조준선.
 * 카메라 축은 Python 의 camera_basis 와 같다. 오른쪽 r = f × up, 위 u = r × f, 굴림 없음.
 * frustum 은 depth 까지 그린다. 움직이는 조준기는 포획 거리와 같아서 끝면이 포획 범위를 보여 준다.
 * 색은 포획 조건 안이면 capture, 보이면 visible, 아니면 idle 이다.
 */
export function AimerRig({ ep, colors, depth, bodyColor }) {
  const s = useMemo(newSample, [])
  const tanV = Math.tan((ep.meta.fovV * Math.PI) / 360)
  const tanH = tanV * ep.meta.aspect

  const parts = useMemo(() => {
    const frustumGeo = new THREE.BufferGeometry()
    frustumGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(16 * 3), 3))
    const frustum = new THREE.LineSegments(frustumGeo, new THREE.LineBasicMaterial())
    const boreGeo = new THREE.BufferGeometry()
    boreGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(2 * 3), 3))
    const bore = new THREE.LineSegments(boreGeo, new THREE.LineBasicMaterial({ transparent: true, opacity: 0.35 }))
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.06, 0.07), new THREE.MeshBasicMaterial())
    for (const o of [frustum, bore]) o.frustumCulled = false
    return { frustum, bore, body }
  }, [])

  const v = useMemo(
    () => ({ C: new THREE.Vector3(), f: new THREE.Vector3(), r: new THREE.Vector3(), u: new THREE.Vector3(), m: new THREE.Matrix4(), back: new THREE.Vector3() }),
    [],
  )

  useFrame(() => {
    sample(ep, clock.t, s)
    v.C.fromArray(s.C)
    v.f.fromArray(s.look)
    v.r.crossVectors(v.f, UP).normalize()
    v.u.crossVectors(v.r, v.f)

    const corners = [
      [-1, 1],
      [1, 1],
      [1, -1],
      [-1, -1],
    ].map(([sx, sy]) =>
      v.C.clone()
        .addScaledVector(v.f, depth)
        .addScaledVector(v.r, sx * depth * tanH)
        .addScaledVector(v.u, sy * depth * tanV),
    )
    const pos = parts.frustum.geometry.attributes.position.array
    let k = 0
    const put = (p) => {
      pos[k++] = p.x
      pos[k++] = p.y
      pos[k++] = p.z
    }
    for (const c of corners) {
      put(v.C)
      put(c)
    }
    for (let i = 0; i < 4; i++) {
      put(corners[i])
      put(corners[(i + 1) % 4])
    }
    parts.frustum.geometry.attributes.position.needsUpdate = true

    const bpos = parts.bore.geometry.attributes.position.array
    const end = v.C.clone().addScaledVector(v.f, distanceToWall(v.C, v.f, ep.meta.room))
    bpos.set([v.C.x, v.C.y, v.C.z, end.x, end.y, end.z])
    parts.bore.geometry.attributes.position.needsUpdate = true

    v.back.copy(v.f).negate()
    v.m.makeBasis(v.r, v.u, v.back)
    parts.body.quaternion.setFromRotationMatrix(v.m)
    parts.body.position.copy(v.C)

    const color = s.capture > 0 ? colors.capture : s.visible ? colors.visible : colors.idle
    parts.frustum.material.color.set(color)
    parts.bore.material.color.set(color)
    parts.body.material.color.set(bodyColor)
  })

  return (
    <group>
      <primitive object={parts.frustum} />
      <primitive object={parts.bore} />
      <primitive object={parts.body} />
    </group>
  )
}
