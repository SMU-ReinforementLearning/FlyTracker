import { useEffect, useMemo, useState } from 'react'
import { cellText, recordLabel, seedLabel } from '../../data/experiment.js'
import { percent, shortDate } from '../../data/labels.js'
import { issueName } from '../../data/lineage.js'
import { byCreatedAt, lastCheckpoint, matchesQuery, NO_ISSUE, rateOf, sectionsByLane, steppedCheckpoints } from '../../data/runs.js'
import { useCombinations } from '../../data/useIssueData.js'
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

/**
 * 실행 줄. 실행을 가르는 짧은 이름만 적는다. 초파리와 조준기가 무엇인지는 issue 화면의 표에서 같은 글자의 줄을 본다.
 * 조합이 둘 이상인 묶음이면 그 조합을 부르는 글자(A, B, C)가 앞에 온다. 그 뒤는 표의 실행 칸에 나오는 이름이다.
 * 조합 안에 학습 seed 만 다른 실행이 여럿이면 학습 seed, 아니면 실행 이름이다. combo 가 없으면(설정을 읽기 전이거나 못 읽은 실행) 실행 이름이다.
 * 초파리, 조준기, 환경, 실행 이름, 올린 사람, 만든 때는 마우스를 올리면 나온다.
 */
function RunRow({ run, combo, seed, lettered, selected, onSelect }) {
  const last = lastCheckpoint(run)
  const rate = rateOf(last)
  const observing = ['free-flight', 'tracking-observation'].includes(run.algo)
  const letter = lettered && combo ? combo.letter : null
  const name = seedLabel(seed) ?? run.name // issue 화면의 표에서 실행 칸의 버튼에 적는 이름과 같다
  const hint = [combo && `${cellText(combo.fly)} / ${cellText(combo.aimer)} / 환경 ${cellText(combo.environment)}`, run.name, run.author, shortDate(run.createdAt)].filter(Boolean).join('\n')
  return (
    <ListRow current={selected} onClick={() => onSelect(run.id)} className={styles.row} title={hint}>
      <span className={styles.line}>
        <span className={styles.title}>
          {letter && (
            <span className={styles.letter} aria-label={`실험 ${letter}`}>
              {letter}
            </span>
          )}
          {name}
        </span>
        <span className={`${styles.aside} ${styles.rate}`}>
          {!observing && <Sparkline run={run} />}
          {!observing && rate !== null && <span aria-label={`포획률 ${percent(rate)}`}>{percent(rate)}</span>}
        </span>
      </span>
    </ListRow>
  )
}

/** 묶음의 이름. issue 제목이 아니라 그 issue 에서 바뀐 것을 적은 짧은 이름이다(lineage.js). */
export const groupTitle = (group) => (group.key === NO_ISSUE ? 'issue 없음' : issueName(group.issue))

/**
 * 펼친 issue 의 실행 목록. issue 화면의 표와 같은 순서로 늘어놓는다. 설정을 다 읽기 전에는 실행 이름만 늘어놓는다.
 * 학습 실행과 평가 실행이 섞인 묶음은 기록의 종류(학습, 평가)를 소제목으로 적어 둘로 나눈다. 줄 이름인 학습 seed 만으로는 둘을 가를 수 없다.
 * group.runs 는 검색으로 걸러진 것일 수 있다. 조합은 걸러지기 전의 실행(group.all)으로 나눈다. 그래야 글자가 issue 화면의 표와 같다.
 */
function Runs({ group, runId, onSelectRun }) {
  const all = useMemo(() => [...(group.all ?? group.runs)].sort(byCreatedAt), [group.all, group.runs])
  const combos = useCombinations(all, group.key)
  const rows = useMemo(() => {
    const shown = new Set(group.runs.map((r) => r.id))
    const runs = all.filter((r) => shown.has(r.id))
    if (!combos) return runs.map((run) => ({ run, combo: null, seed: null }))
    const byId = new Map(runs.map((r) => [r.id, r]))
    const placed = combos.flatMap((combo) => combo.runs.filter(({ id }) => byId.has(id)).map(({ id, seed }) => ({ run: byId.get(id), combo, seed })))
    const seen = new Set(placed.map((p) => p.run.id))
    return [...placed, ...runs.filter((r) => !seen.has(r.id)).map((run) => ({ run, combo: null, seed: null }))] // 뒤는 설정을 못 읽은 실행
  }, [all, group.runs, combos])
  const lettered = (combos?.length ?? 0) > 1
  const mixed = new Set((combos ?? []).map((c) => c.record).filter(Boolean)).size > 1
  const list = (items) => (
    <RowList>
      {items.map(({ run, combo, seed }) => (
        <RunRow key={run.id} run={run} combo={combo} seed={seed} lettered={lettered} selected={run.id === runId} onSelect={onSelectRun} />
      ))}
    </RowList>
  )
  if (!mixed) return list(rows)
  // 종류가 없는 실행(기준선)은 소제목 없이 맨 앞에 둔다
  const parts = [null, 'training', 'evaluation'].map((kind) => ({ kind, items: rows.filter((r) => (r.combo?.record ?? null) === kind) })).filter((p) => p.items.length > 0)
  return parts.map(({ kind, items }) => (
    <section key={kind ?? 'none'} aria-label={recordLabel(kind) ?? undefined}>
      {kind && <h3 className={styles.record}>{recordLabel(kind)}</h3>}
      {list(items)}
    </section>
  ))
}

/**
 * issue 묶음. 이름 줄 하나가 묶음을 펼치고 접는다. 따로 둔 화살표 버튼은 없다.
 * 접힌 이름을 누르면 묶음이 펼쳐지고 issue 화면이 열린다. 그 issue 화면을 보는 중에 다시 누르면 접힌다.
 * 펼쳐져 있지만 다른 화면(그 묶음의 실행)을 보는 중이면 접지 않고 issue 화면으로 간다.
 */
function Group({ group, open, current, onPress, runId, onSelectRun }) {
  const title = groupTitle(group)
  return (
    <section className={styles.group} aria-label={title}>
      <button type="button" className={styles.groupName} aria-expanded={open} aria-current={current} title={group.key === NO_ISSUE ? undefined : group.issue.title} onClick={onPress}>
        <span className={styles.chevron}>
          <Chevron />
        </span>
        {group.key !== NO_ISSUE && <span className={styles.groupNum}>#{group.issue.number}</span>}
        <span className={styles.groupText}>{title}</span>
      </button>
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

  // 이름 줄을 눌렀을 때. 펼쳐진 묶음의 issue 화면을 보는 중이면 접고, 아니면 펼치면서 issue 화면을 연다.
  const press = (key) => {
    if (opened.has(key) && issueKey === key) {
      setOpened((prev) => {
        const next = new Set(prev)
        next.delete(key)
        return next
      })
      return
    }
    setOpened((prev) => (prev.has(key) ? prev : new Set(prev).add(key)))
    onOpenIssue(key)
  }

  // 검색으로 거른 묶음. 걸러지기 전의 실행은 all 에 둔다(조합의 글자를 정하는 데 쓴다). 다시 그릴 때마다 새 목록을 만들면 펼친 묶음이 설정을 다시 읽으므로 기억해 둔다.
  const shown = useMemo(
    () => (groups ?? []).map((g) => ({ ...g, all: g.runs, runs: g.runs.filter((r) => matchesQuery(r, query)) })).filter((g) => g.runs.length > 0),
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
        sectionsByLane(shown).map((s) => (
          <section key={s.key} className={styles.lane} aria-label={s.name ?? undefined}>
            {s.name && <h2 className={styles.laneName}>{s.name}</h2>}
            {s.groups.map((g) => (
              <Group
                key={g.key}
                group={g}
                open={searching || opened.has(g.key)}
                current={issueKey === g.key}
                onPress={() => press(g.key)}
                runId={runId}
                onSelectRun={onSelectRun}
              />
            ))}
          </section>
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
