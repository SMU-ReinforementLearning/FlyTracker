import { useEffect, useMemo, useRef, useState } from 'react'
import { percent, seconds, signed, tagLabel } from '../data/labels.js'
import { rateOf, steppedCheckpoints } from '../data/runs.js'
import { togglePlay } from '../playback/clock.js'
import { CurveChart } from './CurveChart.jsx'

export const METRICS = {
  rate: { label: '포획률', value: rateOf, format: percent, tickFormat: percent, domain: [0, 1] },
  reward: { label: '평균 보상', value: (c) => c.meanReturn, format: (v) => signed(v, 1), tickFormat: (v) => signed(v, 0) },
}

export function MetricSwitch({ metric, onChange }) {
  return (
    <div className="segmented" role="radiogroup" aria-label="학습 곡선 값">
      {Object.entries(METRICS).map(([key, m]) => (
        <button key={key} type="button" role="radio" aria-checked={metric === key} onClick={() => onChange(key)}>
          {m.label}
        </button>
      ))}
    </div>
  )
}

/** 고른 checkpoint 의 수치. 어느 checkpoint 인지는 제목이 말한다. */
function Stats({ checkpoint }) {
  const rows = [
    ['포획률', percent(rateOf(checkpoint))],
    ['평균 보상', signed(checkpoint.meanReturn, 1)],
    ['포획 시간', checkpoint.meanCaptureTime === null ? '없음' : seconds(checkpoint.meanCaptureTime)],
  ]
  return (
    <section aria-label={tagLabel(checkpoint.tag)}>
      <h2 className="panel-title">{tagLabel(checkpoint.tag)}</h2>
      <dl className="stats">
        {rows.map(([label, value]) => (
          <div key={label} className="stat">
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  )
}

/**
 * 에피소드 격자. 행은 checkpoint, 열은 평가 에피소드 번호다.
 * 학습은 checkpoint 마다 같은 seed 로 평가하므로, 한 열을 위에서 아래로 읽으면 같은 시작 조건에서 결과가 어떻게 바뀌었는지 보인다.
 * 화살표 키로 칸을 옮기면 그 에피소드가 바로 재생되고, 스페이스는 재생과 일시정지를 바꾼다.
 */
function EpisodeGrid({ grid, sel, onSelect }) {
  const root = useRef(null)
  const cols = Math.max(...grid.map((row) => row.items.length))
  const longest = Math.max(...grid.flatMap((row) => row.items.map((e) => e.summary.duration)))

  useEffect(() => {
    // 키보드로 옮겼을 때만 focus 를 따라 옮긴다. 격자 밖에 있던 focus 는 건드리지 않는다.
    if (root.current?.contains(document.activeElement)) root.current.querySelector('[aria-selected="true"]')?.focus()
  }, [sel.r, sel.k])

  const onKey = (e) => {
    if (e.key === ' ') {
      e.preventDefault()
      togglePlay()
      return
    }
    const move = { ArrowLeft: [0, -1], ArrowRight: [0, 1], ArrowUp: [-1, 0], ArrowDown: [1, 0] }[e.key]
    if (!move) return
    e.preventDefault()
    const r = Math.min(Math.max(sel.r + move[0], 0), grid.length - 1)
    const k = Math.min(Math.max(sel.k + move[1], 0), grid[r].items.length - 1)
    if (r !== sel.r || k !== sel.k) onSelect(r, k, true)
  }

  return (
    <div className="ep-grid" role="grid" aria-label="에피소드" ref={root} onKeyDown={onKey} style={{ '--cols': cols }}>
      <div className="ep-row ep-head" role="row">
        <span role="columnheader" />
        {Array.from({ length: cols }, (_, k) => (
          <span key={k} role="columnheader" aria-label={`에피소드 ${k + 1}`}>
            {k + 1}
          </span>
        ))}
      </div>
      {grid.map((row, r) => (
        <div key={row.tag} className="ep-row" role="row" aria-current={r === sel.r}>
          <span className="ep-tag" role="rowheader">
            {tagLabel(row.tag)}
          </span>
          {row.items.map((e, k) => {
            const { captured, duration } = e.summary
            const selected = r === sel.r && k === sel.k
            const outcome = captured ? `포획 ${seconds(duration)}` : '시간 초과'
            const text = `${tagLabel(row.tag)}, 에피소드 ${k + 1}, ${outcome}`
            return (
              <button
                key={e.file}
                type="button"
                role="gridcell"
                className="ep-cell"
                aria-selected={selected}
                aria-label={text}
                title={text}
                tabIndex={selected ? 0 : -1}
                onClick={() => onSelect(r, k, false)}
              >
                {captured ? (
                  // 빨리 잡았을수록 진하다
                  <span className="ep-dot" style={{ opacity: 0.4 + 0.6 * (1 - duration / (longest || 1)) }} />
                ) : (
                  <span className="ep-miss" aria-hidden="true">
                    ×
                  </span>
                )}
              </button>
            )
          })}
        </div>
      ))}
    </div>
  )
}

export function RunPanel({ run, grid, sel, onSelect }) {
  const [metric, setMetric] = useState('rate')
  const m = METRICS[metric]
  const stepped = useMemo(() => steppedCheckpoints(run), [run])
  const series = useMemo(
    () => [{ id: run.id, label: run.name, points: stepped.map((c) => ({ x: c.step, y: m.value(c) })) }],
    [run, stepped, m],
  )
  const tag = grid[sel.r].tag
  const checkpoint = run.checkpoints?.find((c) => c.tag === tag)

  const pickStep = (step) => {
    const picked = stepped.find((c) => c.step === step)
    const r = grid.findIndex((row) => row.tag === picked?.tag)
    if (r >= 0) onSelect(r, Math.min(sel.k, grid[r].items.length - 1), false)
  }

  return (
    <aside className="run-panel" aria-label="실행 요약과 에피소드">
      {checkpoint && <Stats checkpoint={checkpoint} />}
      {stepped.length >= 2 && (
        <section className="panel-section" aria-label="학습 곡선">
          <MetricSwitch metric={metric} onChange={setMetric} />
          <CurveChart series={series} label={m.label} format={m.format} tickFormat={m.tickFormat} domain={m.domain} marker={checkpoint?.step ?? null} onPick={pickStep} />
        </section>
      )}
      <EpisodeGrid grid={grid} sel={sel} onSelect={onSelect} />
    </aside>
  )
}
