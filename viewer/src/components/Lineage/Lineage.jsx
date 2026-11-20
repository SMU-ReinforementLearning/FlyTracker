import { useLayoutEffect, useMemo, useRef, useState } from 'react'
import { LANES, lineageOf } from '../../data/lineage.js'
import styles from './Lineage.module.css'

const CORNER = 8 // 선이 꺾이는 곳의 둥글기(px)
const SPREAD = 6 // 같은 틈을 타는 선끼리 겹치지 않게 이어받은 issue 마다 옆으로 비키는 거리(px)
const ARROW = 7 // 화살촉의 길이와 폭(px)
const SIDE = 9 // 같은 영역에서 사이의 노드를 건너뛰는 선이 노드 왼쪽으로 비켜 가는 거리(px)

/** 가로세로로만 가는 꺾은선을 모서리가 둥근 path 로 적는다. */
function pathOf(pts) {
  let d = `M${pts[0][0]},${pts[0][1]}`
  for (let i = 1; i < pts.length - 1; i++) {
    const [x0, y0] = pts[i - 1]
    const [x1, y1] = pts[i]
    const [x2, y2] = pts[i + 1]
    const r = Math.min(CORNER, Math.hypot(x1 - x0, y1 - y0) / 2, Math.hypot(x2 - x1, y2 - y1) / 2)
    const ax = x1 - Math.sign(x1 - x0) * r
    const ay = y1 - Math.sign(y1 - y0) * r
    const bx = x1 + Math.sign(x2 - x1) * r
    const by = y1 + Math.sign(y2 - y1) * r
    d += `L${ax},${ay}Q${x1},${y1} ${bx},${by}`
  }
  const [xe, ye] = pts.at(-1)
  return `${d}L${xe},${ye}`
}

/**
 * 이어받은 issue(p)에서 이어진 issue(c)로 가는 선. 끝점이 c 의 테두리라서 화살촉이 c 를 가리킨다.
 * 같은 영역의 바로 다음 노드면 아래로 곧게 긋는다. 사이에 다른 노드가 있으면 노드 왼쪽으로 비켜 간다.
 * 영역이 다르면 p 의 옆에서 나와 c 가 있는 영역 바로 앞의 틈을 타고 내려가 c 의 옆으로 들어간다.
 */
function edgePath(p, c, direct, lanes, shift) {
  const pcy = p.top + p.height / 2
  const ccy = c.top + c.height / 2
  if (p.lane === c.lane) {
    const x = p.left + p.width / 2
    if (direct) return pathOf([[x, p.top + p.height], [x, c.top]])
    const side = Math.min(p.left, c.left) - SIDE
    return pathOf([[p.left, pcy], [side, pcy], [side, ccy], [c.left, ccy]])
  }
  if (c.lane > p.lane) {
    const gutter = (lanes[c.lane - 1].right + lanes[c.lane].left) / 2 + shift
    return pathOf([[p.left + p.width, pcy], [gutter, pcy], [gutter, ccy], [c.left, ccy]])
  }
  const gutter = (lanes[c.lane].right + lanes[c.lane + 1].left) / 2 + shift
  return pathOf([[p.left, pcy], [gutter, pcy], [gutter, ccy], [c.left + c.width, ccy]])
}

function ExternalIcon() {
  return (
    <svg className={styles.external} viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M14 5h5v5" />
      <path d="M19 5 10.5 13.5" />
      <path d="M18 14v4a1.5 1.5 0 0 1-1.5 1.5h-10A1.5 1.5 0 0 1 5 18V8a1.5 1.5 0 0 1 1.5-1.5H10" />
    </svg>
  )
}

/**
 * 계보. issue 를 영역(초파리, 조준기, 환경)별 세로줄에 시간 순서로 놓고, 이어받은 issue 와 선으로 잇는다.
 * 실행이 올라온 issue 는 누르면 issue 화면이 열린다. 실행이 없는 issue 는 흐리게 그리고, 누르면 GitHub 의 issue 가 새 창으로 열린다.
 */
export function Lineage({ groups, onOpenIssue }) {
  const { nodes, edges, rows } = useMemo(lineageOf, [])
  const withRuns = useMemo(() => new Set((groups ?? []).map((g) => g.key)), [groups])
  const [active, setActive] = useState(null)
  const [geom, setGeom] = useState(null) // { width, height, nodes: Map(number → 상자), lanes: [{ left, right }] }
  const mapRef = useRef(null)
  const nodeRefs = useRef(new Map())
  const laneRefs = useRef([])

  // 선은 노드가 실제로 놓인 자리를 재서 긋는다. 폭이 바뀌면 글이 다시 흘러 자리가 달라지므로 다시 잰다.
  useLayoutEffect(() => {
    const map = mapRef.current
    const measure = () => {
      const boxes = new Map()
      for (const n of nodes) {
        const el = nodeRefs.current.get(n.number)
        if (el) boxes.set(n.number, { lane: n.lane, left: el.offsetLeft, top: el.offsetTop, width: el.offsetWidth, height: el.offsetHeight })
      }
      const lanes = laneRefs.current.map((el) => ({ left: el.offsetLeft, right: el.offsetLeft + el.offsetWidth }))
      setGeom({ width: map.offsetWidth, height: map.offsetHeight, nodes: boxes, lanes })
    }
    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(map)
    return () => observer.disconnect()
  }, [nodes])

  // 같은 영역에서 두 노드 사이에 다른 노드가 없으면 곧은 선으로 잇는다
  const isDirect = (from, to) => {
    const a = nodes.find((n) => n.number === from)
    const b = nodes.find((n) => n.number === to)
    return a.lane === b.lane && !nodes.some((n) => n.lane === a.lane && n.row > a.row && n.row < b.row)
  }

  const related = useMemo(() => {
    if (active == null) return null
    const set = new Set([active])
    for (const e of edges) {
      if (e.from === active) set.add(e.to)
      if (e.to === active) set.add(e.from)
    }
    return set
  }, [active, edges])

  return (
    <div className={styles.page}>
      <div className={styles.frame}>
        <div className={styles.map} ref={mapRef}>
          {LANES.map((lane, i) => (
            <div key={lane.key} className={styles.lane} style={{ gridColumn: i + 1, gridRow: `1 / span ${rows + 1}` }} ref={(el) => (laneRefs.current[i] = el)} />
          ))}
          {LANES.map((lane, i) => (
            <h2 key={lane.key} className={styles.laneName} style={{ gridColumn: i + 1 }}>
              {lane.name}
            </h2>
          ))}
          {geom && (
            <svg className={styles.edges} width={geom.width} height={geom.height} aria-hidden="true">
              {/* 화살촉은 이어진 issue 쪽 끝에 붙는다. 선이 먼저 한 일에서 나중에 한 일로 간다는 것을 보여 준다. */}
              <defs>
                {[['lineage-arrow', styles.arrow], ['lineage-arrow-on', styles.arrowOn]].map(([id, cls]) => (
                  <marker key={id} id={id} className={cls} markerUnits="userSpaceOnUse" markerWidth={ARROW} markerHeight={ARROW} viewBox={`0 0 ${ARROW} ${ARROW}`} refX={ARROW} refY={ARROW / 2} orient="auto">
                    <path d={`M0,0L${ARROW},${ARROW / 2}L0,${ARROW}Z`} />
                  </marker>
                ))}
              </defs>
              {edges.map((e) => {
                const p = geom.nodes.get(e.from)
                const c = geom.nodes.get(e.to)
                if (!p || !c) return null
                const on = active === e.from || active === e.to
                return <path key={`${e.from}-${e.to}`} className={on ? `${styles.edge} ${styles.edgeOn}` : styles.edge} markerEnd={`url(#${on ? 'lineage-arrow-on' : 'lineage-arrow'})`} d={edgePath(p, c, isDirect(e.from, e.to), geom.lanes, ((e.from % 3) - 1) * SPREAD)} />
              })}
            </svg>
          )}
          {nodes.map((n) => {
            const open = withRuns.has(String(n.number))
            const cls = [styles.node, !open && styles.ghost, related && !related.has(n.number) && styles.dim].filter(Boolean).join(' ')
            const meta = [n.author, n.date, n.also.length ? `${n.also.join(', ')}도 바꿈` : null].filter(Boolean).join(' · ')
            const shared = {
              className: cls,
              style: { gridColumn: n.lane + 1, gridRow: n.row + 2 },
              title: n.title,
              ref: (el) => {
                if (el) nodeRefs.current.set(n.number, el)
                else nodeRefs.current.delete(n.number)
              },
              onMouseEnter: () => setActive(n.number),
              onMouseLeave: () => setActive(null),
              onFocus: () => setActive(n.number),
              onBlur: () => setActive(null),
            }
            const body = (
              <>
                <span className={styles.head}>
                  <span className={styles.num}>#{n.number}</span>
                  {n.envVersion != null && <span className={styles.badge}>환경 버전 {n.envVersion}</span>}
                  {!open && <ExternalIcon />}
                </span>
                <span className={styles.name}>{n.name}</span>
                <span className={styles.result}>{n.result}</span>
                <span className={styles.meta}>{meta}</span>
              </>
            )
            return open ? (
              <button key={n.number} type="button" {...shared} onClick={() => onOpenIssue(String(n.number))}>
                {body}
              </button>
            ) : (
              <a key={n.number} {...shared} href={n.url} target="_blank" rel="noreferrer" aria-label={`#${n.number} ${n.name}, GitHub에서 issue 열기`}>
                {body}
              </a>
            )
          })}
        </div>
      </div>
    </div>
  )
}
