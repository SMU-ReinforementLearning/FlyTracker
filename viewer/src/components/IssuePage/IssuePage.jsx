import { useId, useMemo, useState } from 'react'
import { combinationsOf, compareExperiments, experimentOf } from '../../data/experiment.js'
import { changeOf } from '../../data/history.js'
import { issueName } from '../../data/lineage.js'
import { byCreatedAt, compareGroup, lastCheckpoint, NO_ISSUE, steppedCheckpoints } from '../../data/runs.js'
import { NO_RUNS, useConfigs, useIssueInfo, useOrigins } from '../../data/useIssueData.js'
import { Combinations } from '../Combinations/Combinations.jsx'
import { CurveChart } from '../CurveChart/CurveChart.jsx'
import { METRICS, MetricSwitch } from '../RunPanel/RunPanel.jsx'
import { Swatch } from '../Swatch/Swatch.jsx'
import styles from './IssuePage.module.css'

const SERIES_COLORS = 8 // assets/styles/variables.css 의 --color-series-1 … --color-series-8
const NO_COMBINATIONS = []

const paragraphs = (value) => (Array.isArray(value) ? value : value ? [value] : []).filter(Boolean)

function Section({ title, children }) {
  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>{title}</h2>
      {children}
    </section>
  )
}

/**
 * 줄이나 카드 이름에 붙는 출처. 그 값을 정한 issue 를 마우스를 올리면 상자로 보여 주고, 누르면 GitHub 에서 새 창으로 연다.
 * 링크는 글자가 없고 ::after 로 부모(position: relative)를 덮는다. 그래서 줄 어디를 눌러도 열린다.
 */
function Source({ label, change }) {
  const id = useId()
  if (!change) return null
  const { issue } = change
  return (
    <>
      <a className={styles.source} href={issue.url} target="_blank" rel="noreferrer" aria-label={`${label}, #${issue.number} ${issueName(issue)}`} aria-describedby={id} />
      <span id={id} role="tooltip" className={styles.pop}>
        <strong className={styles.popTitle}>
          #{issue.number} {issueName(issue)}
        </strong>
        <span className={styles.popMeta}>
          {issue.author} · {issue.merged}
        </span>
        <span className={styles.popWhy}>{change.why}</span>
      </span>
    </>
  )
}

/** 이름과 값 줄. 비교 대상과 다른 줄은 '비교 대상의 값 → 지금 값'과 차이를 보여 준다. 값을 정한 issue 를 아는 줄은 출처가 붙는다. */
function Rows({ rows, envVersion }) {
  return (
    <dl className={styles.rows}>
      {rows.map((r) => {
        const changed = r.prev !== undefined || r.changed
        const change = r.src ? changeOf(r.src, envVersion) : null
        const cls = [styles.row, changed && styles.changed, change && styles.sourced].filter(Boolean).join(' ')
        return (
          <div key={r.label} className={cls}>
            <dt>{r.label}</dt>
            <dd>
              {r.prev !== undefined && (
                <>
                  <span className={styles.prev}>{r.prev}</span>
                  <span className={styles.arrow} aria-hidden="true">
                    →
                  </span>
                </>
              )}
              <span>{r.value}</span>
              {r.delta && <span className={styles.delta}>{r.delta}</span>}
              <Source label={r.label} change={change} />
            </dd>
          </div>
        )
      })}
    </dl>
  )
}

function AgentCard({ card, envVersion }) {
  const rows = card.was ? [{ label: '비교 대상', value: card.was, changed: card.was !== '같음' }, ...card.rows] : card.rows
  const change = card.src ? changeOf(card.src, envVersion) : null
  return (
    <article className={styles.card}>
      <div className={change ? `${styles.agentHead} ${styles.sourced}` : styles.agentHead}>
        <h3 className={styles.agentName}>{card.name}</h3>
        {card.version && <span className={styles.version}>{card.version}</span>}
        <Source label={card.name} change={change} />
      </div>
      {card.text && <p className={styles.text}>{card.text}</p>}
      {rows.length > 0 && <Rows rows={rows} envVersion={envVersion} />}
    </article>
  )
}

/** 종류와 상관없이 그 칸 전체에 걸리는 줄. 설정과 보상이 여기에 든다. */
function RowsCard({ title, rows, envVersion }) {
  if (rows.length === 0) return null
  return (
    <article className={styles.card}>
      <h3 className={styles.agentName}>{title}</h3>
      <Rows rows={rows} envVersion={envVersion} />
    </article>
  )
}

/** 초파리 칸 또는 조준기 칸. 종류별 카드, 설정, 보상 순서다. */
function Side({ title, side, envVersion }) {
  return (
    <Section title={title}>
      {side.cards.map((card) => (
        <AgentCard key={card.key} card={card} envVersion={envVersion} />
      ))}
      <RowsCard title="설정" rows={side.settings} envVersion={envVersion} />
      <RowsCard title="보상" rows={side.rewards} envVersion={envVersion} />
    </Section>
  )
}

function Purpose({ issueKey, info, target, onOpenIssue }) {
  return (
    <div className={styles.card}>
      {info ? (
        <>
          {info.phase && <h3 className={styles.phase}>{info.phase}</h3>}
          {paragraphs(info.purpose).map((p, i) => (
            <p key={i} className={styles.text}>
              {p}
            </p>
          ))}
        </>
      ) : (
        <p className={styles.empty}>
          실험 설명이 아직 없다. <code>published/issues/{issueKey}.json</code>에 실험 단계와 이유를 쓰면 여기에 나온다.
        </p>
      )}
      {info?.compare != null && (
        <dl className={styles.rows}>
          <div className={styles.row}>
            <dt>비교 대상</dt>
            <dd>
              {target ? (
                <button type="button" className={styles.issueLink} onClick={() => onOpenIssue(target.key)}>
                  #{target.issue.number} {issueName(target.issue)}
                </button>
              ) : (
                `#${info.compare}에는 올라온 실행이 없다`
              )}
            </dd>
          </div>
        </dl>
      )}
    </div>
  )
}

/**
 * issue 하나가 어떤 실험인지 보여 준다. 실험 이유, 조합 표, 초파리와 조준기, 환경, 학습 곡선 순서다.
 * 조합 표에서 줄을 고르면 그 아래의 칸과 학습 곡선이 그 조합의 실행만 보여 준다. 고르지 않으면 실행 전체다.
 */
export function IssuePage({ group, groups, onOpenIssue, onSelectRun }) {
  const [metric, setMetric] = useState('rate')
  const [combination, setCombination] = useState(null)
  const m = METRICS[metric]

  // 색은 만든 순서로 준다. 실행이 새로 올라와도 앞선 실행의 색은 바뀌지 않는다.
  const runs = useMemo(() => [...group.runs].sort(byCreatedAt), [group])
  const colorOf = (i) => `var(--color-series-${(i % SERIES_COLORS) + 1})`

  const configs = useConfigs(runs)
  const info = useIssueInfo(group.key)
  const origins = useOrigins(runs, configs)
  const combinations = useMemo(() => (configs && info !== undefined && origins ? combinationsOf(runs, configs, info, origins) : NO_COMBINATIONS), [runs, configs, info, origins])
  const picked = (combinations.length > 1 && combinations.find((c) => c.key === combination)) || null
  const shownIds = useMemo(() => (picked ? new Set(picked.runs.map((r) => r.id)) : null), [picked])

  // 비교 대상은 설명 파일의 compare 가 정한다. 그 issue 의 실행 전체와 견준다.
  const target = info ? compareGroup(groups, group, info.compare) : null
  const targetRuns = useMemo(() => (target ? [...target.runs].sort(byCreatedAt) : NO_RUNS), [target])
  const targetConfigs = useConfigs(targetRuns)
  const targetInfo = useIssueInfo(target?.key ?? null)

  const exp = useMemo(() => {
    if (!configs || info === undefined || !targetConfigs || targetInfo === undefined) return null
    const keep = (_, i) => !shownIds || shownIds.has(runs[i].id)
    const cur = experimentOf(runs.filter(keep), configs.filter(keep), info)
    return compareExperiments(cur, target ? experimentOf(targetRuns, targetConfigs, targetInfo) : null)
  }, [runs, configs, info, shownIds, target, targetRuns, targetConfigs, targetInfo])

  const series = useMemo(
    () =>
      runs
        .map((run, i) => {
          const stepped = steppedCheckpoints(run)
          const last = lastCheckpoint(run)
          return {
            id: run.id,
            label: run.name,
            color: colorOf(i),
            points: stepped.map((c) => ({ x: c.step, y: m.value(c) })),
            flat: stepped.length === 0 && last ? m.value(last) : null,
          }
        })
        .filter((s) => !shownIds || shownIds.has(s.id)),
    [runs, m, shownIds],
  )
  const hasCurve = new Set(series.flatMap((s) => s.points.map((p) => p.x))).size >= 2

  if (!exp) return <div className={styles.page} />

  return (
    <div className={styles.page}>
      <div className={styles.column}>
        {group.key !== NO_ISSUE && (
          <Section title="실험">
            <Purpose issueKey={group.key} info={info} target={target} onOpenIssue={onOpenIssue} />
          </Section>
        )}
        {combinations.length > 0 && (
          <Section title="실험 목록">
            <div className={styles.card}>
              <Combinations rows={combinations} runs={runs} selected={picked?.key ?? null} onSelect={setCombination} onOpenRun={onSelectRun} />
            </div>
          </Section>
        )}
        {(exp.fly.cards.length > 0 || exp.aimer.cards.length > 0) && (
          <div className={styles.pair}>
            <Side title="초파리" side={exp.fly} envVersion={exp.envVersion} />
            <Side title="조준기" side={exp.aimer} envVersion={exp.envVersion} />
          </div>
        )}
        <Section title="환경">
          <div className={styles.card}>
            <Rows rows={[...exp.environment, ...exp.facts]} envVersion={exp.envVersion} />
          </div>
        </Section>
        {hasCurve && (
          <Section title="학습 곡선">
            <div className={`${styles.card} ${styles.curveCard}`}>
              <MetricSwitch metric={metric} onChange={setMetric} />
              <CurveChart series={series} label={m.label} format={m.format} tickFormat={m.tickFormat} domain={m.domain} height={260} />
              {series.length > 1 && (
                <ul className={styles.legend}>
                  {series.map((s) => (
                    <li key={s.id}>
                      <Swatch color={s.color} />
                      {s.label}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </Section>
        )}
      </div>
    </div>
  )
}
