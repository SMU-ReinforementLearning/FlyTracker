import { OrbitControls } from '@react-three/drei'
import { Canvas } from '@react-three/fiber'
import { SCENE } from '../theme.js'
import { AimerRig } from './AimerRig.jsx'
import { FlyMarker } from './FlyMarker.jsx'
import { FrameCounter } from './FrameCounter.jsx'
import { Room } from './Room.jsx'

/** 방 전체를 보는 3인칭 시점. 마우스로 돌리고(왼쪽 버튼) 옮기고(오른쪽 버튼) 확대한다. */
export function ThirdPersonView({ ep, scheme }) {
  const c = SCENE[scheme]
  const [w, h, d] = ep.meta.room
  const depth = Math.min(ep.meta.captureRange, 0.8)
  return (
    <Canvas dpr={[1, 2]} camera={{ position: [w * 0.85, h * 1.25, d * 1.35], fov: 36, near: 0.05, far: 100 }}>
      <color attach="background" args={[c.background]} />
      <Room size={ep.meta.room} colors={c} />
      <FlyMarker ep={ep} color={c.fly} evadeColor={c.evade} trailColor={c.trail} />
      <AimerRig ep={ep} colors={c} depth={depth} bodyColor={c.fly} />
      <OrbitControls makeDefault target={[0, h * 0.4, 0]} enableDamping dampingFactor={0.12} />
      <FrameCounter />
    </Canvas>
  )
}
