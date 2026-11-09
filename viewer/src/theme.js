import { useEffect, useState } from 'react'

// 3D 장면 색. 화면 요소 색은 styles.css 의 CSS 변수가 맡는다.
// 상태 색 세 가지(보임, 포획 중, 회피 중)는 dataviz 검사 스크립트로 두 모드 모두 확인했다.
// 밝은 모드의 주황과 초록은 바탕 대비 3:1 미만이라, 같은 상태를 오른쪽 수치 목록이 글자로도 보여 준다.
export const SCENE = {
  light: {
    background: '#f5f5f7',
    grid: '#dcdce1',
    gridCenter: '#c7c7cc',
    room: '#aeaeb2',
    fly: '#1d1d1f',
    trail: '#8e8e93',
    idle: '#8e8e93',
    visible: '#0071e3',
    capture: '#1baf7a',
    alarm: '#eb6834',
  },
  dark: {
    background: '#1c1c1e',
    grid: '#2c2c2e',
    gridCenter: '#3a3a3c',
    room: '#636366',
    fly: '#f5f5f7',
    trail: '#8e8e93',
    idle: '#8e8e93',
    visible: '#3987e5',
    capture: '#199e70',
    alarm: '#d95926',
  },
}

// 1인칭 화면은 두 모드 모두 카메라 뷰파인더처럼 어둡게 둔다.
export const VIEWFINDER = {
  background: '#000000',
  grid: '#1f1f21',
  room: '#48484a',
  fly: '#ffffff',
  focus: '#ffd60a',
  capture: '#30d158',
}

export function useColorScheme() {
  const query = '(prefers-color-scheme: dark)'
  const [dark, setDark] = useState(() => window.matchMedia(query).matches)
  useEffect(() => {
    const mq = window.matchMedia(query)
    const onChange = (e) => setDark(e.matches)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])
  return dark ? 'dark' : 'light'
}
