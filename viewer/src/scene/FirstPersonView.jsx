import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { useCallback, useEffect, useMemo, useRef } from 'react'
import { newSample, sample } from '../data/episode.js'
import { clock, useAnimationFrame } from '../playback/clock.js'
import { VIEWFINDER } from '../theme.js'
import { FlyMarker } from './FlyMarker.jsx'
import { FrameCounter } from './FrameCounter.jsx'
import { Room } from './Room.jsx'
import styles from './FirstPersonView.module.css'

function FollowAimer({ ep }) {
  const camera = useThree((st) => st.camera)
  const s = useMemo(newSample, [])
  useEffect(() => {
    camera.fov = ep.meta.fovV
    camera.near = 0.02
    camera.far = 50
    camera.updateProjectionMatrix()
  }, [camera, ep])
  useFrame(() => {
    sample(ep, clock.t, s)
    camera.position.set(s.C[0], s.C[1], s.C[2])
    camera.lookAt(s.C[0] + s.look[0], s.C[1] + s.look[1], s.C[2] + s.look[2])
  })
  return null
}

/**
 * 조준기 카메라 화면. 3D 로 그린 초파리 위에 Python 이 기록한 화면 좌표(uv)를 초점 사각형으로 겹친다.
 * 두 위치가 어긋나면 Python 의 투영 계산과 viewer 중 한쪽이 틀린 것이다.
 * 가운데 십자는 빔이 지나는 자리다. 빔 지름 2.5mm 는 화면에서 화소 하나보다 작아서 범위를 원으로 그리지 않는다.
 * 포획을 각도로 판정하던 기록(captureAngleDeg 가 있다)은 그 각도 범위를 원으로 그린다.
 * 초파리는 실제 크기로 그린다. 멀리 있으면 화소 하나보다 작아서, 위치는 초점 사각형으로 본다.
 */
export function FirstPersonView({ ep }) {
  const focus = useRef(null)
  const s = useMemo(newSample, [])
  const halfV = (ep.meta.fovV * Math.PI) / 360
  const byAngle = ep.meta.captureAngleDeg != null
  const ringPct = byAngle ? (Math.tan((ep.meta.captureAngleDeg * Math.PI) / 180) / Math.tan(halfV)) * 100 : 0

  const update = useCallback(() => {
    const el = focus.current
    if (!el) return
    sample(ep, clock.t, s)
    el.style.opacity = s.visible ? '1' : '0'
    el.style.left = `${((s.u + 1) / 2) * 100}%`
    el.style.top = `${((1 - s.v) / 2) * 100}%`
    el.dataset.capture = s.capture > 0 ? 'true' : 'false'
  }, [ep, s])
  useAnimationFrame(update)

  const vf = VIEWFINDER
  return (
    <div className={styles.viewfinder} style={{ aspectRatio: String(ep.meta.aspect) }}>
      <Canvas dpr={[1, 2]} camera={{ fov: ep.meta.fovV }}>
        <color attach="background" args={[vf.background]} />
        <Room size={ep.meta.room} colors={{ grid: vf.grid, room: vf.room }} showAxes={false} />
        <FlyMarker ep={ep} />
        <FollowAimer ep={ep} />
        <FrameCounter />
      </Canvas>
      {ep.meta.captureEnabled !== false && (byAngle
        ? <div className={styles.ring} style={{ height: `${ringPct}%` }} aria-hidden="true" />
        : <div className={styles.cross} aria-hidden="true" />)}
      <div ref={focus} className={styles.focus} aria-hidden="true" />
    </div>
  )
}
