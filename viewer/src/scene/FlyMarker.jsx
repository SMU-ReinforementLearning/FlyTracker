import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { Suspense, useEffect, useMemo, useRef } from 'react'
import * as THREE from 'three'
import { frameAt, newSample, sample } from '../data/episode.js'
import { clock } from '../playback/clock.js'

// flybody(TuragaLab, Apache-2.0) 메시를 줄여 만든 모델. 실제 크기(몸 길이 약 3mm), 단위 m, 머리가 −z, 위가 +y.
// 만드는 법은 scripts/build_fly_model.py, 출처는 public/models/fruitfly.NOTICE.txt
const MODEL_URL = `${import.meta.env.BASE_URL}models/fruitfly.glb`
useGLTF.preload(MODEL_URL)

/** 실제 크기 초파리 모델. 진행 방향(heading)을 바라보게 돌린다. */
function FlyBody({ ep }) {
  const { scene } = useGLTF(MODEL_URL)
  const group = useRef()
  const s = useMemo(newSample, [])
  const root = useMemo(() => scene.clone(true), [scene])

  useFrame(() => {
    sample(ep, clock.t, s)
    const g = group.current
    g.position.set(s.fly[0], s.fly[1], s.fly[2])
    const [hx, hy, hz] = s.heading
    g.rotation.set(Math.asin(Math.max(-1, Math.min(1, hy))), Math.atan2(-hx, -hz), 0, 'YXZ')
  })

  return (
    <group ref={group}>
      <primitive object={root} />
    </group>
  )
}

/**
 * 초파리와 지나온 궤적. 초파리는 늘 실제 크기로 그린다.
 * 실제 크기로는 방 전체를 보는 화면에서 보이지 않으므로, 그런 화면은 trailColor 를 주어 궤적으로 위치를 보인다.
 */
export function FlyMarker({ ep, trailColor, trailSeconds = 1.5 }) {
  const s = useMemo(newSample, [])
  const maxPts = Math.ceil(trailSeconds / (ep.meta.frameDt || 0.02)) + 3

  const trail = useMemo(() => {
    if (!trailColor) return null
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(maxPts * 3), 3))
    const line = new THREE.Line(g, new THREE.LineBasicMaterial({ transparent: true, opacity: 0.7 }))
    line.frustumCulled = false
    return line
  }, [maxPts, trailColor])

  useEffect(() => {
    if (trail) trail.material.color.set(trailColor)
  }, [trail, trailColor])

  useFrame(() => {
    if (!trail) return
    sample(ep, clock.t, s)
    const pos = trail.geometry.attributes.position.array
    const start = Math.max(frameAt(ep, clock.t - trailSeconds), s.i - (maxPts - 2))
    let k = 0
    for (let i = start; i <= s.i; i++, k++) {
      pos[k * 3] = ep.fly[i * 3]
      pos[k * 3 + 1] = ep.fly[i * 3 + 1]
      pos[k * 3 + 2] = ep.fly[i * 3 + 2]
    }
    pos.set(s.fly, k * 3)
    trail.geometry.setDrawRange(0, k + 1)
    trail.geometry.attributes.position.needsUpdate = true
  })

  return (
    <group>
      <hemisphereLight args={['#ffffff', '#3a3a3c', 2.2]} />
      <directionalLight position={[2, 4, 3]} intensity={1.6} />
      <Suspense fallback={null}>
        <FlyBody ep={ep} />
      </Suspense>
      {trail && <primitive object={trail} />}
    </group>
  )
}
