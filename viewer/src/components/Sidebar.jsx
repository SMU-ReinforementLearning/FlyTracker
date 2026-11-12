import { useState } from 'react'
import { algoLabel, percent, shortDate } from '../data/labels.js'
import { lastCheckpoint, matchesQuery, NO_ISSUE, rateOf, steppedCheckpoints } from '../data/runs.js'

const SPARK_W = 40
const SPARK_H = 14

/** checkpoint 별 포획률을 이은 작은 선. 값은 옆의 숫자가 말하고, 이 선은 오르내림만 보여 준다. */
function Sparkline({ run }) {
  const points = steppedCheckpoints(run)
  if (points.length < 2) return null
  const x0 = points[0].step
  const span = points.at(-1).step - x0 || 1
  const d = points
    .map((c, i) => {
      const x = 1 + ((c.step - x0) / span) * (SPARK_W - 2)
      const y = 1 + (1 - rateOf(c)) * (SPARK_H - 2)
      return `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join('')
  return (
    <svg className="spark" width={SPARK_W} height={SPARK_H} aria-hidden="true">
      <path d={d} />
    </svg>
  )
}

function Chevron() {
  return (
    <svg viewBox="0 0 12 12" width="10" height="10" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="m4 2.5 4 3.5-4 3.5" />
    </svg>
  )
}

function RunRow({ run, selected, onSelect }) {
  const last = lastCheckpoint(run)
  const rate = rateOf(last)
  const meta = [algoLabel(run.algo), run.author].filter(Boolean).join(' · ')
  return (
    <li>
      <button type="button" className="row" aria-current={selected} onClick={() => onSelect(run.id)}>
        <span className="row-line">
          <span className="row-title">{run.name}</span>
          <span className="row-aside row-rate">
            {!['free-flight', 'tracking-observation'].includes(run.algo) && <Sparkline run={run} />}
            {!['free-flight', 'tracking-observation'].includes(run.algo) && rate !== null && <span aria-label={`포획률 ${percent(rate)}`}>{percent(rate)}</span>}
          </span>
        </span>
        <span className="row-line row-sub">
          <span className="row-meta">{meta}</span>
          <span>{shortDate(run.createdAt)}</span>
        </span>
      </button>
    </li>
  )
}

export const groupTitle = (group) => (group.key === NO_ISSUE ? 'issue 없음' : group.issue.title)

function Group({ group, open, onToggle, runId, issueKey, onSelectRun, onOpenIssue }) {
  const title = groupTitle(group)
  return (
    <section className="group" aria-label={title}>
      <div className="group-head">
        <button type="button" className="disclosure" aria-expanded={open} aria-label={`${title} ${open ? '접기' : '펼치기'}`} onClick={onToggle}>
          <Chevron />
        </button>
        <button type="button" className="group-name" aria-current={issueKey === group.key} title={title} onClick={() => onOpenIssue(group.key)}>
          {group.key !== NO_ISSUE && <span className="group-num">#{group.issue.number}</span>}
          <span className="group-text">{title}</span>
        </button>
      </div>
      {open && (
        <ul className="source-list">
          {group.runs.map((run) => (
            <RunRow key={run.id} run={run} selected={run.id === runId} onSelect={onSelectRun} />
          ))}
        </ul>
      )}
    </section>
  )
}

export function Sidebar({ groups, error, runId, issueKey, onSelectRun, onOpenIssue }) {
  const [query, setQuery] = useState('')
  const [closed, setClosed] = useState(() => new Set())

  const toggle = (key) =>
    setClosed((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })

  let body
  if (error) {
    body = <p className="sidebar-note">runs 폴더를 읽지 못했어요. 저장소의 viewer 폴더에서 npm run dev로 실행했는지 확인해 주세요.</p>
  } else if (!groups) {
    body = <p className="sidebar-note">불러오는 중</p>
  } else if (groups.length === 0) {
    body = (
      <p className="sidebar-note">
        기록된 실행이 없어요. <code>scripts/record_baseline.py</code>로 에피소드를 만들어 주세요.
      </p>
    )
  } else {
    const searching = query.trim() !== ''
    const shown = groups
      .map((g) => ({ ...g, runs: g.runs.filter((r) => matchesQuery(r, query)) }))
      .filter((g) => g.runs.length > 0)
    body =
      shown.length === 0 ? (
        <p className="sidebar-note">맞는 실행이 없어요. 검색어를 바꿔 주세요.</p>
      ) : (
        shown.map((g) => (
          <Group
            key={g.key}
            group={g}
            open={searching || !closed.has(g.key)}
            onToggle={() => toggle(g.key)}
            runId={runId}
            issueKey={issueKey}
            onSelectRun={onSelectRun}
            onOpenIssue={onOpenIssue}
          />
        ))
      )
  }

  return (
    <nav className="sidebar" aria-label="실행">
      <input className="search" type="search" placeholder="실행 검색" aria-label="실행 검색" value={query} onChange={(e) => setQuery(e.target.value)} />
      {body}
    </nav>
  )
}
