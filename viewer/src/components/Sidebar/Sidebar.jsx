import { useEffect, useMemo, useState } from 'react'
import { variationsOf } from '../../data/experiment.js'
import { algoLabel, percent, shortDate } from '../../data/labels.js'
import { issueName } from '../../data/lineage.js'
import { byCreatedAt, lastCheckpoint, matchesQuery, NO_ISSUE, rateOf, steppedCheckpoints } from '../../data/runs.js'
import { useConfigs, useIssueInfo } from '../../data/useIssueData.js'
import { ListRow, RowList } from '../ListRow/ListRow.jsx'
import styles from './Sidebar.module.css'

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
    <svg className={styles.spark} width={SPARK_W} height={SPARK_H} aria-hidden="true">
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

/** label 은 variation 안에서 실행을 가르는 이름(학습 seed)이다. 없으면 실행 이름을 적는다. */
function RunRow({ run, label, selected, onSelect }) {
  const last = lastCheckpoint(run)
  const rate = rateOf(last)
  const meta = [algoLabel(run.algo), run.author].filter(Boolean).join(' · ')
  return (
    <ListRow current={selected} onClick={() => onSelect(run.id)} className={styles.row} title={label ? run.name : undefined}>
      <span className={styles.line}>
        <span className={styles.title}>{label ?? run.name}</span>
        <span className={`${styles.aside} ${styles.rate}`}>
          {!['free-flight', 'tracking-observation'].includes(run.algo) && <Sparkline run={run} />}
          {!['free-flight', 'tracking-observation'].includes(run.algo) && rate !== null && <span aria-label={`포획률 ${percent(rate)}`}>{percent(rate)}</span>}
        </span>
      </span>
      <span className={`${styles.line} ${styles.sub}`}>
        <span className={styles.meta}>{meta}</span>
        <span>{shortDate(run.createdAt)}</span>
      </span>
    </ListRow>
  )
}

/** 묶음의 이름. issue 제목이 아니라 그 issue 에서 바뀐 것을 적은 짧은 이름이다(lineage.js). */
export const groupTitle = (group) => (group.key === NO_ISSUE ? 'issue 없음' : issueName(group.issue))

/**
 * 펼친 issue 의 실행 목록. 설정이 다른 실행끼리 variation 으로 나누고, variation 마다 무엇이 다른지를 이름과 값 줄로 적는다.
 * 그 아래의 실행은 학습 seed 만 다르므로 학습 seed 로 부른다. 설정을 다 읽기 전이거나 variation 이 하나뿐이면 실행 이름 그대로 늘어놓는다.
 * group.runs 는 검색으로 걸러진 것일 수 있다. variation 은 걸러진 실행만으로 나눈다.
 */
function Runs({ group, runId, onSelectRun }) {
  const runs = useMemo(() => [...group.runs].sort(byCreatedAt), [group.runs])
  const configs = useConfigs(runs)
  const info = useIssueInfo(group.key)
  const blocks = useMemo(() => {
    if (!configs || info === undefined) return null
    const { items } = variationsOf(runs, configs, info)
    if (items.length === 0) return null
    const seedOf = new Map(runs.map((r, i) => [r.id, configs[i]?.algo?.seed ?? null]))
    const byId = new Map(runs.map((r) => [r.id, r]))
    const placed = new Set(items.flatMap((v) => v.runIds))
    const rest = runs.filter((r) => !placed.has(r.id)) // 설정을 못 읽은 실행
    return [
      ...items.map((v) => {
        const list = v.runIds.map((id) => byId.get(id))
        const seeds = list.map((r) => seedOf.get(r.id))
        const named = list.length > 1 && seeds.every((x) => x !== null) && new Set(seeds).size === list.length
        return { key: v.key, parts: v.parts, runs: list.map((run, i) => ({ run, label: named ? `학습 seed ${seeds[i]}` : null })) }
      }),
      ...(rest.length ? [{ key: 'rest', parts: [], runs: rest.map((run) => ({ run, label: null })) }] : []),
    ]
  }, [runs, configs, info])

  if (!blocks) {
    return (
      <RowList>
        {group.runs.map((run) => (
          <RunRow key={run.id} run={run} selected={run.id === runId} onSelect={onSelectRun} />
        ))}
      </RowList>
    )
  }
  return blocks.map((b) => (
    <div key={b.key} className={styles.variation}>
      {b.parts.length > 0 && (
        <dl className={styles.parts}>
          {b.parts.map((part) => (
            <div key={part.label} className={styles.part}>
              <dt>{part.label}</dt>
              <dd>{part.value}</dd>
            </div>
          ))}
        </dl>
      )}
      <RowList>
        {b.runs.map(({ run, label }) => (
          <RunRow key={run.id} run={run} label={label} selected={run.id === runId} onSelect={onSelectRun} />
        ))}
      </RowList>
    </div>
  ))
}

function Group({ group, open, onToggle, runId, issueKey, onSelectRun, onOpenIssue }) {
  const title = groupTitle(group)
  return (
    <section className={styles.group} aria-label={title}>
      <div className={styles.groupHead}>
        <button type="button" className={styles.disclosure} aria-expanded={open} aria-label={`${title} ${open ? '접기' : '펼치기'}`} onClick={onToggle}>
          <Chevron />
        </button>
        <button type="button" className={styles.groupName} aria-current={issueKey === group.key} title={group.key === NO_ISSUE ? undefined : group.issue.title} onClick={() => onOpenIssue(group.key)}>
          {group.key !== NO_ISSUE && <span className={styles.groupNum}>#{group.issue.number}</span>}
          <span className={styles.groupText}>{title}</span>
        </button>
      </div>
      {open && <Runs group={group} runId={runId} onSelectRun={onSelectRun} />}
    </section>
  )
}

export function Sidebar({ groups, error, runId, issueKey, home, onSelectRun, onOpenIssue, onOpenLineage }) {
  const [query, setQuery] = useState('')
  // 묶음은 처음에 모두 접혀 있다. issue 이름을 누르면 그 묶음이 펼쳐진다.
  const [opened, setOpened] = useState(() => new Set())

  // 계보의 노드나 주소로 issue 화면에 들어오면 그 묶음을 펼친다
  useEffect(() => {
    if (issueKey != null) setOpened((prev) => (prev.has(issueKey) ? prev : new Set(prev).add(issueKey)))
  }, [issueKey])

  const toggle = (key) =>
    setOpened((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })

  const openIssue = (key) => {
    setOpened((prev) => (prev.has(key) ? prev : new Set(prev).add(key)))
    onOpenIssue(key)
  }

  // 검색으로 거른 묶음. 다시 그릴 때마다 새 목록을 만들면 펼친 묶음이 설정을 다시 읽으므로 기억해 둔다.
  const shown = useMemo(
    () => (groups ?? []).map((g) => ({ ...g, runs: g.runs.filter((r) => matchesQuery(r, query)) })).filter((g) => g.runs.length > 0),
    [groups, query],
  )

  let body
  if (error) {
    body = <p className={styles.note}>runs 폴더를 읽지 못했어요. 저장소의 viewer 폴더에서 npm run dev로 실행했는지 확인해 주세요.</p>
  } else if (!groups) {
    body = <p className={styles.note}>불러오는 중</p>
  } else if (groups.length === 0) {
    body = (
      <p className={styles.note}>
        기록된 실행이 없어요. <code>scripts/record_baseline.py</code>로 에피소드를 만들어 주세요.
      </p>
    )
  } else {
    const searching = query.trim() !== ''
    body =
      shown.length === 0 ? (
        <p className={styles.note}>맞는 실행이 없어요. 검색어를 바꿔 주세요.</p>
      ) : (
        shown.map((g) => (
          <Group
            key={g.key}
            group={g}
            open={searching || opened.has(g.key)}
            onToggle={() => toggle(g.key)}
            runId={runId}
            issueKey={issueKey}
            onSelectRun={onSelectRun}
            onOpenIssue={openIssue}
          />
        ))
      )
  }

  return (
    <nav className={styles.sidebar} aria-label="실행">
      <button type="button" className={styles.home} aria-current={home} onClick={onOpenLineage}>
        계보
      </button>
      <input className={styles.search} type="search" placeholder="실행 검색" aria-label="실행 검색" value={query} onChange={(e) => setQuery(e.target.value)} />
      {body}
    </nav>
  )
}
