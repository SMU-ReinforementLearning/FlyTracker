import { useMemo } from 'react'
import { frameAt } from '../../data/episode.js'
import { useClock } from '../../playback/clock.js'
import { SCENE } from '../../theme.js'
import styles from './Readouts.module.css'

/** 지금 프레임의 상태. 3D 장면의 색이 뜻하는 상태를 글자로도 보여 준다. */
export function Readouts({ ep, scheme }) {
  const c = useClock(15)
  const i = useMemo(() => frameAt(ep, c.t), [ep, c.t])
  const colors = SCENE[scheme]
  const visible = ep.visible[i] === 1
  const capture = ep.capture[i]
  const alarmed = ep.alarmed[i] === 1

  const state = capture > 0 ? ['포획 중', colors.capture] : visible ? ['보임', colors.visible] : ['안 보임', colors.idle]
  const rows = [
    ['상태', state[0], state[1]],
    ['조준 오차', `${ep.angle[i].toFixed(1)}°`],
    ['거리', `${ep.distance[i].toFixed(2)}m`],
    ['포획 진행', `${Math.round(capture * 100)}%`],
    ['초파리', alarmed ? '비상시' : '평시', alarmed ? colors.alarm : null],
    ['프레임', `${i + 1} / ${ep.n}`],
  ]
  return (
    <dl className={styles.readouts}>
      {rows.map(([label, value, dot]) => (
        <div key={label} className={styles.readout}>
          <dt>{label}</dt>
          <dd>
            {dot && <span className={styles.dot} style={{ background: dot }} aria-hidden="true" />}
            {value}
          </dd>
        </div>
      ))}
    </dl>
  )
}
