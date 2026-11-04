import { useEffect, useState } from 'react'

// 재생 시각은 React state 밖에 둔다. 3D 장면과 오버레이는 프레임마다 clock.t 를 직접 읽고,
// 화면 글자(시간, 그래프 커서, 수치)는 useClock 으로 초당 몇 번만 다시 그린다.
export const clock = { t: 0, duration: 0, playing: false, speed: 1 }

let last = null
function tick(now) {
  if (clock.playing && last !== null) {
    clock.t += ((now - last) / 1000) * clock.speed
    if (clock.t >= clock.duration) {
      clock.t = clock.duration
      clock.playing = false
    }
  }
  last = now
  requestAnimationFrame(tick)
}
requestAnimationFrame(tick)

export function load(duration) {
  clock.duration = duration
  clock.t = 0
  clock.playing = true
}

export function togglePlay() {
  if (!clock.playing && clock.t >= clock.duration) clock.t = 0
  clock.playing = !clock.playing
}

export function seek(t) {
  clock.t = Math.min(Math.max(t, 0), clock.duration)
}

export function setSpeed(speed) {
  clock.speed = speed
}

/** clock 의 사본을 hz 주기로 갱신한다. */
export function useClock(hz = 15) {
  const [snap, setSnap] = useState(() => ({ ...clock }))
  useEffect(() => {
    const id = setInterval(() => {
      setSnap((prev) =>
        prev.t === clock.t && prev.playing === clock.playing && prev.speed === clock.speed && prev.duration === clock.duration
          ? prev
          : { ...clock },
      )
    }, 1000 / hz)
    return () => clearInterval(id)
  }, [hz])
  return snap
}

/** 브라우저 프레임마다 콜백을 부른다. Canvas 밖의 오버레이용. */
export function useAnimationFrame(callback) {
  useEffect(() => {
    let id
    const loop = () => {
      callback()
      id = requestAnimationFrame(loop)
    }
    id = requestAnimationFrame(loop)
    return () => cancelAnimationFrame(id)
  }, [callback])
}
