import { useMemo } from 'react'
import { frameAt } from '../data/episode.js'
import { useClock } from '../playback/clock.js'
import { SCENE } from '../theme.js'

/** 지금 프레임의 상태. 3D 장면의 색이 뜻하는 상태를 글자로도 보여 준다. */
export function Readouts({ ep, scheme }) {
  const c = useClock(15)
  const i = useMemo(() => frameAt(ep, c.t), [ep, c.t])
  const colors = SCENE[scheme]
  const visible = ep.visible[i] === 1
  const capture = ep.capture[i]
  const alarmed = ep.alarmed[i] === 1
  const events = ep.events.filter((event) => event.onset_ms <= c.t * 1000)
  const stimulating = events.some((event) => event.end_ms > c.t * 1000 && event.exposure_ms > 0)
  const phase = ep.phase?.[i]
  const phaseLabel = phase === 'escape' ? '도피 중' : phase === 'recovery' ? '회복 중' : '평상 비행'
  const flightLabel = ep.meta.flyModel === 'neural' ? '신경 날개 (실험)' : '규칙 기반'
  const escapeLabel = '도피 회로 출력'

  const state = capture > 0 ? ['포획 중', colors.capture] : visible ? ['보임', colors.visible] : ['안 보임', colors.idle]
  const rows = ep.meta.mode === 'free-flight' ? [
    ['비행 모델', ep.meta.flyModel === 'neural' ? '신경 기반' : '규칙 기반'],
    ...(ep.meta.flyModel === 'neural' ? [['비행 설정', flightLabel]] : []),
    ['비행 속도', `${ep.speed[i].toFixed(2)}m/s`],
    ['높이', `${ep.fly[i * 3 + 1].toFixed(2)}m`],
    ['운동 상태', phase ? phaseLabel : alarmed ? '비상시' : '평시', alarmed ? colors.alarm : null],
    ...(ep.normalRate ? [['DNg02 출력', `${ep.normalRate[i].toFixed(1)}Hz`],
      [escapeLabel, `${ep.escapeRate[i].toFixed(1)}Hz`]] : []),
    ...(ep.saccadeRate ? [['급선회 출력', `${ep.saccadeRate[i].toFixed(1)}Hz`]] : []),
    ...(ep.wallInput ? [['벽 감각 입력', `${ep.wallInput[i].toFixed(1)}Hz`]] : []),
    ['프레임', `${i + 1} / ${ep.n}`],
  ] : ep.meta.mode === 'tracking-observation' ? [
    ['비행 설정', flightLabel],
    ...(ep.aimCommanded ? [['조준 구간', ep.aimCommanded[i] ? '유지' : '해제']] : []),
    ['상태', state[0], state[1]],
    ['비행 속도', `${ep.speed[i].toFixed(2)}m/s`],
    ['가상 자극', stimulating ? '제시 중' : '대기'],
    ['자극 횟수', `${events.length}회`],
    ...(ep.threatInput ? [['감각 입력', `${ep.threatInput[i].toFixed(1)}Hz`],
      ['DNg02 출력', `${ep.normalRate[i].toFixed(1)}Hz`],
      [escapeLabel, `${ep.escapeRate[i].toFixed(1)}Hz`]] : []),
    ...(ep.saccadeRate ? [['급선회 출력', `${ep.saccadeRate[i].toFixed(1)}Hz`]] : []),
    ...(ep.wallInput ? [['벽 감각 입력', `${ep.wallInput[i].toFixed(1)}Hz`]] : []),
    ['운동 상태', phase ? phaseLabel : alarmed ? '비상시' : '평시', alarmed ? colors.alarm : null],
    ...(ep.meta.neural?.connections != null ? [['회로 연결', `${ep.meta.neural.effective_connections}개`]] : []),
  ] : [
    ...(ep.meta.flyModel === 'neural' ? [['비행 설정', flightLabel]] : []),
    ['상태', state[0], state[1]],
    ['조준 오차', `${ep.angle[i].toFixed(1)}°`],
    ['거리', `${ep.distance[i].toFixed(2)}m`],
    ['포획 진행', `${Math.round(capture * 100)}%`],
    ['초파리', alarmed ? '비상시' : '평시', alarmed ? colors.alarm : null],
    ...(ep.normalRate ? [['DNg02 출력', `${ep.normalRate[i].toFixed(1)}Hz`],
      [escapeLabel, `${ep.escapeRate[i].toFixed(1)}Hz`],
      ['운동 상태', phaseLabel, alarmed ? colors.alarm : null]] : []),
    ['프레임', `${i + 1} / ${ep.n}`],
  ]
  return (
    <dl className="readouts">
      {rows.map(([label, value, dot]) => (
        <div key={label} className="readout">
          <dt>{label}</dt>
          <dd>
            {dot && <span className="dot" style={{ background: dot }} aria-hidden="true" />}
            {value}
          </dd>
        </div>
      ))}
    </dl>
  )
}
