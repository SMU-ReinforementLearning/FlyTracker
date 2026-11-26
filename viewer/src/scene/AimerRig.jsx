import { useFrame } from '@react-three/fiber'
import { useMemo } from 'react'
import * as THREE from 'three'
import { newSample, sample } from '../data/episode.js'
import { clock } from '../playback/clock.js'

const UP = new THREE.Vector3(0, 1, 0)
const FORWARD = new THREE.Vector3(0, 0, 1) // 고리(TorusGeometry)가 처음에 바라보는 쪽

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
 * 카메라 축은 Python 의 aim_basis 와 같다. 오른쪽 r 은 yaw 로 정하고, 위 u = r × f, 굴림 없음.
 * yaw 가 없는 기록(환경 버전 3까지)은 r = f × up 으로 만든다.
 * frustum 은 depth 까지 그린다. 움직이는 조준기는 포획 거리와 같아서 끝면이 포획 범위를 보여 준다.
 * 색은 포획 조건 안이면 capture, 보이면 visible, 아니면 idle 이다.
 * 레이저를 쏠 때만 켜는 기록(ep.firing 이 있다)은 조준선과 빔을 따로 그린다. 조준선은 늘 옅은 선이고 포획이나 오발의 색을 띠지 않는다.
 * 빔은 쏘는 동안에만 나타나는 굵은 막대다. 초파리 위에 있으면 capture 색으로 초파리까지, 벗어났으면 misfire 색으로 벽까지 그린다.
 * 실제 빔 지름 2.5mm 는 방 전체를 보는 화면에서 보이지 않아서 굵기를 키워 그린다(BEAM_RADIUS). 정확한 범위는 확대 화면이 보여 준다.
 * 빔이 초파리에 닿아 있는 동안에는 닿은 자리에 점을 그리고, 그 발이 끝까지 맞아 포획이 되면 점이 고리로 커진다.
 */
const BEAM_RADIUS = 0.004 // m. 화면에 보이게 키운 값이다
const GLOW_RADIUS = 0.014
const HIT_RADIUS = 0.018
const KILL_RADIUS = 0.07

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
    // 빔과 그 둘레의 옅은 빛. 길이 1, 반지름 1 인 원기둥을 프레임마다 늘리고 돌린다
    const rod = new THREE.CylinderGeometry(1, 1, 1, 16, 1, true)
    const beam = new THREE.Mesh(rod, new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.95 }))
    const glow = new THREE.Mesh(rod, new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.22, depthWrite: false, side: THREE.DoubleSide }))
    const hit = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.9 }))
    const kill = new THREE.Mesh(new THREE.TorusGeometry(1, 0.06, 8, 48), new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.9 }))
    for (const o of [frustum, bore, beam, glow, hit, kill]) o.frustumCulled = false
    for (const o of [beam, glow, hit, kill]) o.visible = false
    return { frustum, bore, body, beam, glow, hit, kill }
  }, [])

  const v = useMemo(
    () => ({ C: new THREE.Vector3(), f: new THREE.Vector3(), r: new THREE.Vector3(), u: new THREE.Vector3(), m: new THREE.Matrix4(), back: new THREE.Vector3(), fly: new THREE.Vector3(), mid: new THREE.Vector3(), q: new THREE.Quaternion() }),
    [],
  )

  useFrame(() => {
    sample(ep, clock.t, s)
    v.C.fromArray(s.C)
    v.f.fromArray(s.look)
    if (s.hasAngles) v.r.set(Math.cos(s.yaw), 0, -Math.sin(s.yaw)) // 바로 위를 볼 때도 정해진다 (Python 의 aim_basis)
    else v.r.crossVectors(v.f, UP).normalize()
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

    const stimulating = ep.meta.stimulus?.mode === 'beam' && ep.events.some((e) => e.onset_ms <= clock.t*1000 && e.end_ms > clock.t*1000 && e.exposure_ms > 0)
    const color = stimulating ? colors.alarm : s.capture > 0 ? colors.capture : s.visible ? colors.visible : colors.idle
    const shots = ep.firing !== null // 레이저를 쏠 때만 켜는 기록
    const shooting = shots && s.firing
    const onFly = shooting && s.capture > 0
    parts.bore.material.opacity = stimulating ? .95 : shots ? .2 : .35
    parts.frustum.material.color.set(color)
    parts.bore.material.color.set(stimulating || !shots ? color : s.visible ? colors.visible : colors.idle)
    parts.body.material.color.set(bodyColor)

    // 빔. 초파리 위에 있으면 초파리까지, 아니면 벽까지 간다
    const wall = distanceToWall(v.C, v.f, ep.meta.room)
    const reach = onFly ? Math.min(v.fly.fromArray(s.fly).sub(v.C).dot(v.f), wall) : wall
    for (const o of [parts.beam, parts.glow]) o.visible = shooting && reach > 0
    if (shooting && reach > 0) {
      const beamColor = onFly ? colors.capture : colors.misfire
      v.mid.copy(v.C).addScaledVector(v.f, reach / 2)
      v.q.setFromUnitVectors(UP, v.f)
      for (const [o, radius] of [[parts.beam, BEAM_RADIUS], [parts.glow, GLOW_RADIUS]]) {
        o.position.copy(v.mid)
        o.quaternion.copy(v.q)
        o.scale.set(radius, reach, radius)
        o.material.color.set(beamColor)
      }
    }
    // 닿은 자리의 점과, 포획이 된 순간의 고리. 고리는 빔에 수직으로 둔다
    const killed = onFly && s.capture >= 1
    parts.hit.visible = onFly
    parts.kill.visible = killed
    if (onFly) {
      v.mid.copy(v.C).addScaledVector(v.f, reach)
      parts.hit.position.copy(v.mid)
      parts.hit.scale.setScalar(HIT_RADIUS)
      parts.hit.material.color.set(colors.capture)
      if (killed) {
        parts.kill.position.copy(v.mid)
        parts.kill.quaternion.setFromUnitVectors(FORWARD, v.f)
        parts.kill.scale.setScalar(KILL_RADIUS)
        parts.kill.material.color.set(colors.capture)
      }
    }
  })

  return (
    <group>
      <primitive object={parts.frustum} />
      <primitive object={parts.bore} />
      <primitive object={parts.body} />
      <primitive object={parts.glow} />
      <primitive object={parts.beam} />
      <primitive object={parts.hit} />
      <primitive object={parts.kill} />
    </group>
  )
}
