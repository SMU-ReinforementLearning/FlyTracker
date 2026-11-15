import { useMemo, useRef, useState } from 'react'
import { stepLabel } from '../../data/labels.js'
import { niceStep, ticks, useWidth } from '../LineChart/LineChart.jsx'
import { Swatch } from '../Swatch/Swatch.jsx'
import { Tooltip, TooltipRow } from '../Tooltip/Tooltip.jsx'
import styles from './CurveChart.module.css'

const M = { top: 10, right: 14, bottom: 22, left: 40 }

/**
 * 학습 곡선. 가로축은 학습 step, 세로축은 checkpoint 별 값이다.
 * series: [{ id, label, color, points: [{ x, y }], flat }]
 *   points 는 step 이 있는 checkpoint. flat 은 step 이 없는 실행(기준선)의 값이고 점선 가로줄로 그린다.
 * 시리즈가 여럿일 때 어느 선이 어느 실행인지는 아래 표의 색 표시가 알려 준다.
 */
export function CurveChart({ series, label, format, tickFormat = format, domain, marker = null, onPick, height = 150 }) {
  const box = useRef(null)
  const width = useWidth(box)
  const [hover, setHover] = useState(null)

  const geo = useMemo(() => {
    if (!width) return null
    const xs = [...new Set(series.flatMap((s) => s.points.map((p) => p.x)))].sort((a, b) => a - b)
    if (xs.length < 2) return null
    const ys = series.flatMap((s) => [...s.points.map((p) => p.y), ...(s.flat != null ? [s.flat] : [])])
    let [lo, hi] = domain ?? [Math.min(...ys), Math.max(...ys)]
    let count = 2
    if (!domain) {
      if (hi - lo < 1e-9) hi = lo + 1
      const step = niceStep(hi - lo, 3)
      lo = Math.floor(lo / step) * step // 축 끝을 눈금에 맞춘다
      hi = Math.ceil(hi / step) * step
      count = Math.round((hi - lo) / step)
    }
    const iw = width - M.left - M.right
    const ih = height - M.top - M.bottom
    const x0 = xs[0]
    const x1 = xs.at(-1)
    const x = (v) => M.left + ((v - x0) / (x1 - x0)) * iw
    const y = (v) => M.top + (1 - (v - lo) / (hi - lo)) * ih
    const paths = series.map((s) => s.points.map((p, i) => `${i ? 'L' : 'M'}${x(p.x).toFixed(1)},${y(p.y).toFixed(1)}`).join(''))
    return { xs, x, y, paths, iw, ih, yTicks: ticks(lo, hi, count).out, xTicks: ticks(x0, x1, Math.max(2, Math.floor(iw / 80))).out }
  }, [width, height, series, domain])

  if (series.length === 0) return null

  const nearest = (clientX) => {
    const px = clientX - box.current.getBoundingClientRect().left
    return geo.xs.reduce((best, v) => (Math.abs(geo.x(v) - px) < Math.abs(geo.x(best) - px) ? v : best), geo.xs[0])
  }

  const onKey = (e) => {
    const cur = geo.xs.indexOf(hover ?? marker ?? geo.xs.at(-1))
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault()
      const next = Math.min(Math.max(cur + (e.key === 'ArrowRight' ? 1 : -1), 0), geo.xs.length - 1)
      setHover(geo.xs[next])
    } else if (e.key === 'Enter' && onPick) {
      onPick(geo.xs[Math.max(cur, 0)])
    }
  }

  const valueAt = (s, v) => s.points.find((p) => p.x === v)?.y ?? s.flat ?? null
  const rows = hover === null ? [] : series.map((s) => ({ s, y: valueAt(s, hover) })).filter((r) => r.y !== null)
  const lastOf = (s) => s.points.at(-1)?.y ?? s.flat
  const aria = `${label} 학습 곡선. ${series.map((s) => `${s.label} 마지막 값 ${format(lastOf(s))}`).join(', ')}.`

  return (
    <div className={styles.curve} ref={box}>
      {geo && (
        <svg
          width={width}
          height={height}
          role="img"
          aria-label={aria}
          tabIndex={0}
          data-pickable={onPick ? 'true' : undefined}
          onPointerMove={(e) => setHover(nearest(e.clientX))}
          onPointerLeave={() => setHover(null)}
          onFocus={() => setHover(marker ?? geo.xs.at(-1))}
          onBlur={() => setHover(null)}
          onKeyDown={onKey}
          onClick={(e) => onPick?.(nearest(e.clientX))}
        >
          {geo.yTicks.map((v) => (
            <g key={`y${v}`}>
              <line className={styles.grid} x1={M.left} x2={M.left + geo.iw} y1={geo.y(v)} y2={geo.y(v)} />
              <text className={styles.tick} x={M.left - 8} y={geo.y(v)} textAnchor="end" dominantBaseline="middle">
                {tickFormat(v)}
              </text>
            </g>
          ))}
          {geo.xTicks.map((v) => (
            <text key={`x${v}`} className={styles.tick} x={geo.x(v)} y={height - 4} textAnchor="middle">
              {stepLabel(v)}
            </text>
          ))}
          {hover !== null && <line className={styles.crosshair} x1={geo.x(hover)} x2={geo.x(hover)} y1={M.top} y2={M.top + geo.ih} />}
          {series.map((s, k) => (
            <g key={s.id} style={s.color ? { '--series': s.color } : undefined}>
              {s.flat != null && <line className={styles.flat} x1={M.left} x2={M.left + geo.iw} y1={geo.y(s.flat)} y2={geo.y(s.flat)} />}
              <path className={styles.series} d={geo.paths[k]} />
              {s.points.map((p) => (
                <circle key={p.x} className={styles.point} cx={geo.x(p.x)} cy={geo.y(p.y)} r={p.x === hover ? 4 : 2.5} />
              ))}
              {k === 0 && s.points.filter((p) => p.x === marker).map((p) => <circle key="marker" className={styles.marker} cx={geo.x(p.x)} cy={geo.y(p.y)} r={5} />)}
            </g>
          ))}
        </svg>
      )}
      {geo && rows.length > 0 && (
        <Tooltip side flip={geo.x(hover) > width / 2} style={{ left: geo.x(hover), top: M.top }}>
          <span>{stepLabel(hover)} step</span>
          {rows.map(({ s, y }) => (
            <TooltipRow key={s.id}>
              {series.length > 1 && <Swatch color={s.color} />}
              {series.length > 1 && <span>{s.label}</span>}
              <strong>{format(y)}</strong>
            </TooltipRow>
          ))}
        </Tooltip>
      )}
    </div>
  )
}
