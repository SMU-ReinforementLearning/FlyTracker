import { useFrame } from '@react-three/fiber'
import { useEffect, useMemo, useRef } from 'react'
import * as THREE from 'three'
import { frameAt, newSample, sample } from '../data/episode.js'
import { clock } from '../playback/clock.js'

/** 초파리 점과 지나온 궤적. 비상시면 alarmColor 로 칠한다. */
export function FlyMarker({ ep, color, alarmColor, trailColor, radius = 0.025, trailSeconds = 1.5 }) {
  const mesh = useRef()
  const mat = useRef()
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
    sample(ep, clock.t, s)
    mesh.current.position.set(s.fly[0], s.fly[1], s.fly[2])
    mat.current.color.set(s.alarmed ? alarmColor : color)
    if (!trail) return
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
      <mesh ref={mesh}>
        <sphereGeometry args={[radius, 20, 14]} />
        <meshBasicMaterial ref={mat} color={color} />
      </mesh>
      {trail && <primitive object={trail} />}
    </group>
  )
}
