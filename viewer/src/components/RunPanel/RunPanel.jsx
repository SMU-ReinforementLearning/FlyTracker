import { useEffect, useMemo, useRef, useState } from 'react'
import { percent, seconds, signed, tagLabel } from '../../data/labels.js'
import { rateOf, steppedCheckpoints } from '../../data/runs.js'
import { togglePlay } from '../../playback/clock.js'
import { CurveChart } from '../CurveChart/CurveChart.jsx'
import { ListRow, RowList } from '../ListRow/ListRow.jsx'
import { Outcome } from '../Outcome/Outcome.jsx'
import { Segmented } from '../Segmented/Segmented.jsx'
import styles from './RunPanel.module.css'

export const METRICS = {
  rate: { label: '포획률', value: rateOf, format: percent, tickFormat: percent, domain: [0, 1] },
  reward: { label: '평균 보상', value: (c) => c.meanReturn, format: (v) => signed(v, 1), tickFormat: (v) => signed(v, 0) },
}

const METRIC_OPTIONS = Object.entries(METRICS).map(([value, m]) => ({ value, label: m.label }))

export function MetricSwitch({ metric, onChange }) {
  return <Segmented label="학습 곡선 값" options={METRIC_OPTIONS} value={metric} onChange={onChange} />
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
      <h2 className={styles.title}>{tagLabel(checkpoint.tag)}</h2>
      <dl className={styles.stats}>
        {rows.map(([label, value]) => (
          <div key={label} className={styles.stat}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  )
}

function Chevron() {
  return (
    <svg viewBox="0 0 12 12" width="10" height="10" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="m4 2.5 4 3.5-4 3.5" />
    </svg>
  )
}

/**
 * 에피소드 목록. checkpoint 마다 제목 줄이 하나 있고, 펼치면 에피소드가 한 줄에 하나씩 나온다.
 * 에피소드가 아무리 많아도 세로로만 길어진다. 고른 checkpoint 만 펼쳐 두므로 checkpoint 가 많아도 제목 줄만 늘어난다.
 * 위아래 화살표는 앞뒤 에피소드로, 좌우 화살표는 같은 번호(같은 seed)의 앞뒤 checkpoint 로 옮긴다. 스페이스는 재생과 일시정지를 바꾼다.
 */
function EpisodeList({ grid, sel, onSelect }) {
  const root = useRef(null)
  const byKey = useRef(false)
  const selTag = grid[sel.r].tag
  // 제목 줄을 눌러 직접 바꾼 것만 적는다. 적힌 것이 없으면 고른 checkpoint 만 펼친다.
  const [toggled, setToggled] = useState({})
  const isOpen = (tag) => toggled[tag] ?? tag === selTag
  const selOpen = isOpen(selTag)

  const reopen = (tag) => setToggled((prev) => (prev[tag] === false ? { ...prev, [tag]: true } : prev))

  useEffect(() => {
    // 학습 곡선처럼 목록 밖에서 고른 checkpoint 도 펼친다
    reopen(selTag)
  }, [selTag])

  useEffect(() => {
    const row = root.current?.querySelector(`.${CSS.escape(styles.item)}[aria-current="true"]`)
    if (!row) return
    row.scrollIntoView({ block: 'nearest' })
    // 키보드로 옮겼을 때만 focus 를 따라 옮긴다. 목록 밖에 있던 focus 는 건드리지 않는다.
    // 옮기면서 앞 checkpoint 가 접히면 focus 를 쥔 줄이 사라지므로, 지금 focus 가 어디 있는지로는 판단하지 못한다.
    if (byKey.current) row.focus()
    byKey.current = false
  }, [sel.r, sel.k, selOpen])

  const onKey = (e) => {
    if (e.key === ' ') {
      e.preventDefault()
      togglePlay()
      return
    }
    let { r, k } = sel
    if (e.key === 'ArrowUp') {
      if (k > 0) k -= 1
      else if (r > 0) {
        r -= 1
        k = grid[r].items.length - 1
      }
    } else if (e.key === 'ArrowDown') {
      if (k < grid[r].items.length - 1) k += 1
      else if (r < grid.length - 1) {
        r += 1
        k = 0
      }
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      r = Math.min(Math.max(r + (e.key === 'ArrowRight' ? 1 : -1), 0), grid.length - 1)
      k = Math.min(k, grid[r].items.length - 1)
    } else {
      return
    }
    e.preventDefault()
    if (r === sel.r && k === sel.k) return
    byKey.current = true
    reopen(grid[r].tag)
    onSelect(r, k, true)
  }

  return (
    <div className={styles.episodes} ref={root} onKeyDown={onKey}>
      {grid.map((row, r) => {
        const open = isOpen(row.tag)
        const captured = row.items.filter((e) => e.summary.captured).length
        return (
          <section key={row.tag} className={styles.group} aria-label={tagLabel(row.tag)}>
            <button
              type="button"
              className={styles.head}
              aria-expanded={open}
              aria-current={r === sel.r}
              onClick={() => setToggled((prev) => ({ ...prev, [row.tag]: !open }))}
            >
              <Chevron />
              <span className={styles.tag}>{tagLabel(row.tag)}</span>
              <span className={styles.count} aria-label={`포획 ${captured}, 전체 ${row.items.length}`}>
                {captured} / {row.items.length}
              </span>
            </button>
            {open && (
              <RowList>
                {row.items.map((e, k) => (
                  <ListRow key={e.file} current={r === sel.r && k === sel.k} onClick={() => onSelect(r, k, false)} className={styles.item}>
                    <span className={styles.num}>{k + 1}</span>
                    <Outcome captured={e.summary.captured} className={styles.outcome}>
                      {e.summary.captured ? `포획 ${seconds(e.summary.duration)}` : '시간 초과'}
                    </Outcome>
                    <span className={styles.return}>{signed(e.summary.return)}</span>
                  </ListRow>
                ))}
              </RowList>
            )}
          </section>
        )
      })}
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
    <aside className={styles.panel} aria-label="실행 요약과 에피소드">
      {checkpoint && <Stats checkpoint={checkpoint} />}
      {stepped.length >= 2 && (
        <section className={styles.section} aria-label="학습 곡선">
          <MetricSwitch metric={metric} onChange={setMetric} />
          <CurveChart series={series} label={m.label} format={m.format} tickFormat={m.tickFormat} domain={m.domain} marker={checkpoint?.step ?? null} onPick={pickStep} />
        </section>
      )}
      <EpisodeList grid={grid} sel={sel} onSelect={onSelect} />
    </aside>
  )
}
