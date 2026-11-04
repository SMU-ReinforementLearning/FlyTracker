import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { useCallback, useEffect, useMemo, useRef } from 'react'
import { newSample, sample } from '../data/episode.js'
import { clock, useAnimationFrame } from '../playback/clock.js'
import { VIEWFINDER } from '../theme.js'
import { FlyMarker } from './FlyMarker.jsx'
import { FrameCounter } from './FrameCounter.jsx'
import { Room } from './Room.jsx'

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
 * 가운데 원은 포획 각도 범위다.
 */
export function FirstPersonView({ ep }) {
  const focus = useRef(null)
  const s = useMemo(newSample, [])
  const halfV = (ep.meta.fovV * Math.PI) / 360
  const ringPct = (Math.tan((ep.meta.captureAngleDeg * Math.PI) / 180) / Math.tan(halfV)) * 100

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
    <div className="viewfinder" style={{ aspectRatio: String(ep.meta.aspect) }}>
      <Canvas dpr={[1, 2]} camera={{ fov: ep.meta.fovV }}>
        <color attach="background" args={[vf.background]} />
        <Room size={ep.meta.room} colors={{ grid: vf.grid, room: vf.room }} showAxes={false} />
        <FlyMarker ep={ep} color={vf.fly} evadeColor={vf.fly} radius={0.012} />
        <FollowAimer ep={ep} />
        <FrameCounter />
      </Canvas>
      <div className="vf-ring" style={{ height: `${ringPct}%` }} aria-hidden="true" />
      <div ref={focus} className="vf-focus" aria-hidden="true" />
    </div>
  )
}
