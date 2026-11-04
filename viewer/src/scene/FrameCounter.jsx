import { useFrame } from '@react-three/fiber'

/** 그린 프레임 수를 window.__frames 에 센다. 스크린샷 도구가 WebGL 장면이 떴는지 확인하는 데 쓴다. */
export function FrameCounter() {
  useFrame(() => {
    window.__frames = (window.__frames || 0) + 1
  })
  return null
}
