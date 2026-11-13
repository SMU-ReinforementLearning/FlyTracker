import { useEffect, useMemo, useState } from 'react'
import { fetchConfig } from '../../data/api.js'
import { algoLabel, percent, seconds, signed, tagLabel } from '../../data/labels.js'
import { differingKeys, flattenConfig, lastCheckpoint, rateOf, steppedCheckpoints } from '../../data/runs.js'
import { CurveChart } from '../CurveChart/CurveChart.jsx'
import { METRICS, MetricSwitch } from '../RunPanel/RunPanel.jsx'
import { Swatch } from '../Swatch/Swatch.jsx'
import styles from './IssuePage.module.css'

const SERIES_COLORS = 8 // assets/styles/variables.css 의 --color-series-1 … --color-series-8

function useConfigs(runs) {
  const [configs, setConfigs] = useState({})
  useEffect(() => {
    let alive = true
    Promise.all(runs.map((r) => fetchConfig(r.id).then((c) => [r.id, flattenConfig(c)], () => [r.id, {}]))).then((entries) => {
      if (alive) setConfigs(Object.fromEntries(entries))
    })
    return () => {
      alive = false
    }
  }, [runs])
  return configs
}

const cell = (v) => (v === undefined ? '' : typeof v === 'object' ? JSON.stringify(v) : String(v))

/** issue 하나에 올라온 실행들을 비교한다. 학습 곡선을 겹쳐 그리고, 표에는 실행끼리 다른 설정값만 보여 준다. */
export function IssuePage({ group, onSelectRun }) {
  const [metric, setMetric] = useState('rate')
  const m = METRICS[metric]

  // 색은 만든 순서로 준다. 실행이 새로 올라와도 앞선 실행의 색은 바뀌지 않는다.
  const runs = useMemo(() => [...group.runs].sort((a, b) => String(a.createdAt).localeCompare(String(b.createdAt))), [group])
  const colorOf = (i) => `var(--color-series-${(i % SERIES_COLORS) + 1})`

  const series = useMemo(
    () =>
      runs.map((run, i) => {
        const stepped = steppedCheckpoints(run)
        const last = lastCheckpoint(run)
        return {
          id: run.id,
          label: run.name,
          color: colorOf(i),
          points: stepped.map((c) => ({ x: c.step, y: m.value(c) })),
          flat: stepped.length === 0 && last ? m.value(last) : null,
        }
      }),
    [runs, m],
  )
  const hasCurve = new Set(series.flatMap((s) => s.points.map((p) => p.x))).size >= 2

  const configs = useConfigs(runs)
  const loaded = runs.every((r) => configs[r.id])
  const keys = useMemo(() => (loaded && runs.length > 1 ? differingKeys(runs.map((r) => configs[r.id])) : []), [loaded, runs, configs])

  return (
    <div className={styles.page}>
      {hasCurve && (
        <section className={styles.card} aria-label="학습 곡선">
          <MetricSwitch metric={metric} onChange={setMetric} />
          <CurveChart series={series} label={m.label} format={m.format} tickFormat={m.tickFormat} domain={m.domain} height={260} />
        </section>
      )}
      <div className={`${styles.card} ${styles.tableWrap}`}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th scope="col">실행</th>
              <th scope="col">알고리즘</th>
              <th scope="col">올린 사람</th>
              <th scope="col">checkpoint</th>
              <th scope="col" className={styles.num}>포획률</th>
              <th scope="col" className={styles.num}>평균 보상</th>
              <th scope="col" className={styles.num}>포획 시간</th>
              {keys.map((k) => (
                <th key={k} scope="col" className={styles.num}>
                  <code>{k}</code>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {runs.map((run, i) => {
              const last = lastCheckpoint(run)
              return (
                <tr key={run.id}>
                  <th scope="row">
                    <button type="button" className={styles.runLink} onClick={() => onSelectRun(run.id)}>
                      <Swatch color={colorOf(i)} />
                      {run.name}
                    </button>
                  </th>
                  <td>{algoLabel(run.algo)}</td>
                  <td>{run.author ?? ''}</td>
                  <td>{last ? tagLabel(last.tag) : ''}</td>
                  <td className={styles.num}>{last ? percent(rateOf(last)) : ''}</td>
                  <td className={styles.num}>{last ? signed(last.meanReturn, 1) : ''}</td>
                  <td className={styles.num}>{last ? (last.meanCaptureTime === null ? '없음' : seconds(last.meanCaptureTime)) : ''}</td>
                  {keys.map((k) => (
                    <td key={k} className={styles.num}>
                      {cell(configs[run.id]?.[k])}
                    </td>
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
