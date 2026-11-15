import { useEffect, useMemo, useState } from 'react'
import { fetchConfig, fetchIssueInfo } from '../../data/api.js'
import { compareExperiments, experimentOf, variationsOf } from '../../data/experiment.js'
import { byCreatedAt, compareGroup, lastCheckpoint, NO_ISSUE, steppedCheckpoints } from '../../data/runs.js'
import { CurveChart } from '../CurveChart/CurveChart.jsx'
import { METRICS, MetricSwitch } from '../RunPanel/RunPanel.jsx'
import { Segmented } from '../Segmented/Segmented.jsx'
import { Swatch } from '../Swatch/Swatch.jsx'
import styles from './IssuePage.module.css'

const SERIES_COLORS = 8 // assets/styles/variables.css 의 --color-series-1 … --color-series-8
const NO_RUNS = []
const ALL = 'all'

/** runs 와 같은 순서의 config.json. 못 읽은 실행은 null, 다 읽기 전에는 null 을 돌려준다. */
function useConfigs(runs) {
  const [state, setState] = useState(null) // { runs, configs }
  useEffect(() => {
    let alive = true
    Promise.all(runs.map((r) => fetchConfig(r.id).catch(() => null))).then((configs) => {
      if (alive) setState({ runs, configs })
    })
    return () => {
      alive = false
    }
  }, [runs])
  if (runs.length === 0) return NO_RUNS
  return state?.runs === runs ? state.configs : null
}

/** issue 설명 파일. 읽는 중에는 undefined, 없으면 null. key 가 null 이거나 issue 없음 묶음이면 늘 null. */
function useIssueInfo(key) {
  const none = key == null || key === NO_ISSUE
  const [state, setState] = useState(null) // { key, info }
  useEffect(() => {
    if (none) return
    let alive = true
    fetchIssueInfo(key).then((info) => {
      if (alive) setState({ key, info })
    })
    return () => {
      alive = false
    }
  }, [key, none])
  if (none) return null
  return state?.key === key ? state.info : undefined
}

const paragraphs = (value) => (Array.isArray(value) ? value : value ? [value] : []).filter(Boolean)

function Section({ title, children }) {
  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>{title}</h2>
      {children}
    </section>
  )
}

/** 이름과 값 줄. 비교 대상과 다른 줄은 '비교 대상의 값 → 지금 값'과 차이를 보여 준다. */
function Rows({ rows }) {
  return (
    <dl className={styles.rows}>
      {rows.map((r) => {
        const changed = r.prev !== undefined || r.changed
        return (
          <div key={r.label} className={changed ? `${styles.row} ${styles.changed}` : styles.row}>
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
            </dd>
          </div>
        )
      })}
    </dl>
  )
}

function AgentCard({ card }) {
  const rows = card.was ? [{ label: '비교 대상', value: card.was, changed: card.was !== '같음' }, ...card.rows] : card.rows
  return (
    <article className={styles.card}>
      <div className={styles.agentHead}>
        <h3 className={styles.agentName}>{card.name}</h3>
        {card.version && <span className={styles.version}>{card.version}</span>}
      </div>
      {card.text && <p className={styles.text}>{card.text}</p>}
      {rows.length > 0 && <Rows rows={rows} />}
    </article>
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
                  #{target.issue.number} {target.issue.title}
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

/** issue 하나가 어떤 실험인지 보여 준다. 실험 이유, variation, 초파리, 조준기, 조건, 보상, 학습 곡선 순서다. */
export function IssuePage({ group, groups, onOpenIssue }) {
  const [metric, setMetric] = useState('rate')
  const [variation, setVariation] = useState(ALL)
  const m = METRICS[metric]

  // 색은 만든 순서로 준다. 실행이 새로 올라와도 앞선 실행의 색은 바뀌지 않는다.
  const runs = useMemo(() => [...group.runs].sort(byCreatedAt), [group])
  const colorOf = (i) => `var(--color-series-${(i % SERIES_COLORS) + 1})`

  const configs = useConfigs(runs)
  const info = useIssueInfo(group.key)
  const variations = useMemo(() => (configs && info !== undefined ? variationsOf(runs, configs, info) : { label: null, items: [] }), [runs, configs, info])
  const picked = variations.items.find((v) => v.key === variation) ?? null
  const shownIds = useMemo(() => (picked ? new Set(picked.runIds) : null), [picked])

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

  const options = [{ value: ALL, label: '전체' }, ...variations.items.map((v) => ({ value: v.key, label: v.label }))]

  return (
    <div className={styles.page}>
      <div className={styles.column}>
        {group.key !== NO_ISSUE && (
          <Section title="실험">
            <Purpose issueKey={group.key} info={info} target={target} onOpenIssue={onOpenIssue} />
          </Section>
        )}
        {variations.items.length > 0 && (
          <div className={styles.variationBar}>
            <span className={styles.variationLabel}>{variations.label}</span>
            <Segmented label={variations.label} options={options} value={picked ? picked.key : ALL} onChange={setVariation} className={styles.variationSwitch} />
          </div>
        )}
        {(exp.fly.length > 0 || exp.aimer.length > 0) && (
          <div className={styles.pair}>
            <Section title="초파리">
              {exp.fly.map((card) => (
                <AgentCard key={card.key} card={card} />
              ))}
            </Section>
            <Section title="조준기">
              {exp.aimer.map((card) => (
                <AgentCard key={card.key} card={card} />
              ))}
            </Section>
          </div>
        )}
        <Section title="조건">
          <div className={styles.card}>
            <Rows rows={[...exp.conditions, ...exp.facts]} />
          </div>
        </Section>
        {exp.rewards.length > 0 && (
          <Section title="보상">
            <div className={styles.card}>
              <Rows rows={exp.rewards} />
            </div>
          </Section>
        )}
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
