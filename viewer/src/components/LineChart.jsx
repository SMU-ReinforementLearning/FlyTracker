import { useEffect, useMemo, useRef, useState } from 'react'
import { frameAt } from '../data/episode.js'
import { clock, seek } from '../playback/clock.js'

const H = 112
const M = { top: 26, right: 12, bottom: 20, left: 40 }

export function niceStep(span, count) {
  const raw = span / Math.max(count, 1)
  const mag = 10 ** Math.floor(Math.log10(raw || 1))
  const n = raw / mag
  return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * mag
}

export function ticks(lo, hi, count) {
  const step = niceStep(hi - lo, count)
  const start = Math.ceil(lo / step) * step
  const out = []
  for (let v = start; v <= hi + step * 1e-6; v += step) out.push(Number(v.toFixed(10)))
  return { out, step }
}

export function useWidth(ref) {
  const [w, setW] = useState(0)
  useEffect(() => {
    const ro = new ResizeObserver(([entry]) => setW(Math.floor(entry.contentRect.width)))
    ro.observe(ref.current)
    return () => ro.disconnect()
  }, [ref])
  return w
}

/**
 * 시리즈 하나짜리 선 그래프. 제목이 시리즈 이름이라 범례는 없다.
 * 마우스를 올리면 가장 가까운 프레임에 십자선과 값이 뜨고, 누르면 그 시각으로 이동한다.
 */
export function LineChart({ ep, values, label, format, tickFormat = format, t, zeroBased = false }) {
  const box = useRef(null)
  const width = useWidth(box)
  const [hover, setHover] = useState(null)

  const geo = useMemo(() => {
    if (!width) return null
    let lo = Infinity
    let hi = -Infinity
    for (const v of values) {
      if (v < lo) lo = v
      if (v > hi) hi = v
    }
    if (zeroBased) lo = Math.min(lo, 0)
    if (hi - lo < 1e-9) hi = lo + 1
    const step = niceStep(hi - lo, 3)
    lo = Math.floor(lo / step) * step // 축 끝을 눈금에 맞춘다
    hi = Math.ceil(hi / step) * step
    const yt = ticks(lo, hi, Math.round((hi - lo) / step))
    const iw = width - M.left - M.right
    const ih = H - M.top - M.bottom
    const x = (time) => M.left + (time / (ep.duration || 1)) * iw
    const y = (v) => M.top + (1 - (v - lo) / (hi - lo)) * ih
    let d = ''
    for (let i = 0; i < ep.n; i++) d += `${i ? 'L' : 'M'}${x(ep.t[i]).toFixed(1)},${y(values[i]).toFixed(1)}`
    const xt = ticks(0, ep.duration, Math.max(2, Math.floor(iw / 90)))
    return { x, y, d, yTicks: yt.out, xTicks: xt.out, iw, ih }
  }, [width, values, ep, zeroBased])

  const indexAt = (clientX) => {
    const rect = box.current.getBoundingClientRect()
    const frac = (clientX - rect.left - M.left) / geo.iw
    return frameAt(ep, Math.min(Math.max(frac, 0), 1) * ep.duration + 1e-9)
  }

  const onKey = (e) => {
    const cur = hover ?? frameAt(ep, clock.t)
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault()
      e.stopPropagation()
      setHover(Math.min(Math.max(cur + (e.key === 'ArrowRight' ? 1 : -1), 0), ep.n - 1))
    } else if (e.key === 'Enter') {
      seek(ep.t[cur])
    }
  }

  const last = values[ep.n - 1]
  const aria = `${label} 그래프. 마지막 값 ${format(last)}.`
  return (
    <figure className="chart" ref={box}>
      <figcaption className="chart-label">{label}</figcaption>
      {geo && (
        <svg
          width={width}
          height={H}
          role="img"
          aria-label={aria}
          tabIndex={0}
          onPointerMove={(e) => setHover(indexAt(e.clientX))}
          onPointerLeave={() => setHover(null)}
          onFocus={() => setHover(frameAt(ep, clock.t))}
          onBlur={() => setHover(null)}
          onKeyDown={onKey}
          onClick={(e) => seek(ep.t[indexAt(e.clientX)])}
        >
          {geo.yTicks.map((v) => (
            <g key={`y${v}`}>
              <line className="grid" x1={M.left} x2={M.left + geo.iw} y1={geo.y(v)} y2={geo.y(v)} />
              <text className="tick" x={M.left - 8} y={geo.y(v)} textAnchor="end" dominantBaseline="middle">
                {tickFormat(v)}
              </text>
            </g>
          ))}
          {geo.xTicks.map((v) => (
            <text key={`x${v}`} className="tick" x={geo.x(v)} y={H - 4} textAnchor="middle">
              {v}초
            </text>
          ))}
          <path className="series" d={geo.d} />
          <line className="playhead" x1={geo.x(t)} x2={geo.x(t)} y1={M.top} y2={M.top + geo.ih} />
          {hover !== null && (
            <g className="crosshair">
              <line x1={geo.x(ep.t[hover])} x2={geo.x(ep.t[hover])} y1={M.top} y2={M.top + geo.ih} />
              <circle cx={geo.x(ep.t[hover])} cy={geo.y(values[hover])} r={4} />
            </g>
          )}
        </svg>
      )}
      {geo && hover !== null && (
        <div
          className="tooltip"
          style={{ left: Math.min(Math.max(geo.x(ep.t[hover]), 60), width - 60), top: M.top - 6 }}
          role="status"
        >
          <strong>{format(values[hover])}</strong>
          <span>{ep.t[hover].toFixed(2)}초</span>
        </div>
      )}
    </figure>
  )
}
