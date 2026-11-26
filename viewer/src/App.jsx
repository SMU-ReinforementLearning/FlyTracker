import { useEffect, useMemo, useState } from 'react'
import { IconButton } from './components/IconButton/IconButton.jsx'
import { IssuePage } from './components/IssuePage/IssuePage.jsx'
import { LineChart } from './components/LineChart/LineChart.jsx'
import { Lineage } from './components/Lineage/Lineage.jsx'
import { Outcome } from './components/Outcome/Outcome.jsx'
import { Readouts } from './components/Readouts/Readouts.jsx'
import { RunPanel } from './components/RunPanel/RunPanel.jsx'
import { groupTitle, Sidebar } from './components/Sidebar/Sidebar.jsx'
import { stepFrame, Transport } from './components/Transport/Transport.jsx'
import { fetchEpisode, fetchEpisodes, fetchRuns } from './data/api.js'
import { prepareEpisode } from './data/episode.js'
import { seconds, signed, tagLabel } from './data/labels.js'
import { gridOf, groupByIssue } from './data/runs.js'
import { setAllRuns } from './data/useIssueData.js'
import { load, togglePlay, useClock } from './playback/clock.js'
import { useRoute } from './route.js'
import { FirstPersonView, ZoomView } from './scene/FirstPersonView.jsx'
import { ThirdPersonView } from './scene/ThirdPersonView.jsx'
import { useColorScheme } from './theme.js'
import styles from './App.module.css'

function ReloadIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3" />
      <path d="M19.5 4.5v4h-4" />
    </svg>
  )
}

function ExternalIcon() {
  return (
    <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M14 5h5v5" />
      <path d="M19 5 10.5 13.5" />
      <path d="M18 14v4a1.5 1.5 0 0 1-1.5 1.5h-10A1.5 1.5 0 0 1 5 18V8a1.5 1.5 0 0 1 1.5-1.5H10" />
    </svg>
  )
}

function Charts({ ep }) {
  const { t } = useClock(15)
  if (ep.meta.mode === 'free-flight') {
    return (
      <div className={`${styles.charts} ${styles.chartsFlight}`}>
        <LineChart ep={ep} values={ep.speed} label="비행 속도" format={(v) => `${v.toFixed(2)}m/s`} tickFormat={(v) => v.toFixed(1)} t={t} zeroBased />
      </div>
    )
  }
  return (
    <div className={styles.charts}>
      {ep.meta.mode === 'tracking-observation'
        ? <LineChart ep={ep} values={ep.speed} label="비행 속도" format={(v) => `${v.toFixed(2)}m/s`} tickFormat={(v) => v.toFixed(1)} t={t} zeroBased />
        : <LineChart ep={ep} values={ep.returns} label="누적 보상" format={(v) => signed(v, 2)} tickFormat={(v) => signed(v, 0)} t={t} zeroBased />}
      <LineChart ep={ep} values={ep.angle} label="조준 오차" format={(v) => `${v.toFixed(ep.beam ? 2 : 1)}°`} tickFormat={(v) => `${v}°`} t={t} zeroBased />
      {ep.meta.mode === 'tracking-observation' && ep.normalRate && <>
        <LineChart ep={ep} values={ep.normalRate} label="평상 회로 출력" format={(v) => `${v.toFixed(1)}Hz`} tickFormat={(v) => v.toFixed(0)} t={t} zeroBased />
        <LineChart ep={ep} values={ep.escapeRate} label="도피 회로 출력" format={(v) => `${v.toFixed(1)}Hz`} tickFormat={(v) => v.toFixed(0)} t={t} zeroBased />
      </>}
    </div>
  )
}

export default function App() {
  const scheme = useColorScheme()
  const [route, navigate] = useRoute()
  const [runs, setRuns] = useState(null)
  const [runsError, setRunsError] = useState(false)
  const [episodes, setEpisodes] = useState(null) // { runId, list }
  const [loaded, setLoaded] = useState(null) // { file, ep }
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    fetchRuns().then(
      (list) => {
        setAllRuns(list) // 다른 issue 에서 학습한 모델을 찾는 데 쓴다
        setRuns(list)
        setRunsError(false)
      },
      () => setRunsError(true),
    )
  }, [reloadKey])

  // URL 이 가리키는 것. issue 도 실행도 가리키지 않거나 모르는 것을 가리키면 계보를 연다.
  const groups = useMemo(() => (runs ? groupByIssue(runs) : null), [runs])
  const group = groups?.find((g) => g.key === route.issue) ?? null
  const run = group ? null : (runs?.find((r) => r.id === route.run) ?? null)
  const runId = run?.id ?? null
  // 고른 실행이 든 issue 묶음. 실행 패널이 같은 묶음의 실행과 견주어 조합을 적는 데 쓴다.
  const runGroup = useMemo(() => (runId ? (groups?.find((g) => g.runs.some((r) => r.id === runId)) ?? null) : null), [groups, runId])

  useEffect(() => {
    if (!runId) return
    let alive = true
    fetchEpisodes(runId).then(
      (list) => alive && setEpisodes({ runId, list }),
      () => alive && setEpisodes({ runId, list: [] }),
    )
    return () => {
      alive = false
    }
  }, [runId, reloadKey])

  const list = episodes?.runId === runId ? episodes.list : null
  const grid = useMemo(() => gridOf(list), [list])

  // 고른 칸. URL 의 tag 와 ep 가 맞지 않으면 마지막 checkpoint 의 마지막 에피소드다.
  const sel = useMemo(() => {
    if (grid.length === 0) return null
    let r = grid.findIndex((row) => row.tag === route.tag)
    let k = Number(route.ep) - 1
    if (r < 0) r = grid.length - 1
    if (!Number.isInteger(k) || k < 0 || k >= grid[r].items.length) k = grid[r].items.length - 1
    return { r, k }
  }, [grid, route.tag, route.ep])
  const episode = sel ? grid[sel.r].items[sel.k] : null
  const file = episode?.file ?? null

  // 주소를 지금 보이는 것에 맞춘다
  useEffect(() => {
    if (!runs || group) return
    if (!runId) navigate({}, true)
    else if (list && !sel) navigate({ run: runId }, true)
    else if (sel) navigate({ run: runId, tag: grid[sel.r].tag, ep: sel.k + 1 }, true)
  }, [runs, group, runId, list, sel, grid, navigate])

  useEffect(() => {
    if (!file) return
    let alive = true
    fetchEpisode(file).then((raw) => {
      if (!alive) return
      const prepared = prepareEpisode(raw)
      setLoaded({ file, ep: prepared })
      load(prepared.duration)
    })
    return () => {
      alive = false
    }
  }, [file])
  const ep = loaded?.file === file ? loaded.ep : null

  useEffect(() => {
    const onKey = (e) => {
      if (!ep || e.target.closest('input, button, [tabindex]')) return
      if (e.key === ' ') {
        e.preventDefault()
        togglePlay()
      } else if (e.key === 'ArrowLeft') stepFrame(ep, -1)
      else if (e.key === 'ArrowRight') stepFrame(ep, 1)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [ep])

  const selectRun = (id) => navigate({ run: id })
  const selectEpisode = (r, k, replace) => navigate({ run: runId, tag: grid[r].tag, ep: k + 1 }, replace)
  const openIssue = (key) => navigate({ issue: key })
  const openLineage = () => navigate({})
  // 실행 목록을 읽기 전에는 주소가 아무것도 가리키지 않을 때만 계보다. 실행을 가리키는 주소로 들어왔으면 그 실행을 기다린다.
  const home = !group && !run && (runs != null || (!route.run && !route.issue))

  const title = group ? groupTitle(group) : run ? run.name : '계보'
  return (
    <div className={styles.app}>
      <Sidebar groups={groups} error={runsError} runId={runId} issueKey={group?.key ?? null} home={home} onSelectRun={selectRun} onOpenIssue={openIssue} onOpenLineage={openLineage} />
      <main className={styles.main}>
        <header className={styles.toolbar}>
          <div className={styles.toolbarLead}>
            {group?.issue && <span className={styles.toolbarNum}>#{group.issue.number}</span>}
            <h1 className={styles.toolbarTitle}>{title}</h1>
            {episode && (
              <span className={styles.toolbarMeta}>
                <span>{tagLabel(episode.tag)}</span>
                <span>에피소드 {sel.k + 1}</span>
                <Outcome captured={episode.summary.captured}>
                  {episode.summary.result === 'observation_complete' ? `관찰 ${seconds(episode.summary.duration)}` : episode.summary.captured ? `포획 ${seconds(episode.summary.duration)}` : '시간 초과'}
                </Outcome>
                {episode.summary.result !== 'observation_complete' && <span>보상 {signed(episode.summary.return)}</span>}
              </span>
            )}
          </div>
          <div className={styles.toolbarActions}>
            {group?.issue && (
              <IconButton href={group.issue.url} label="GitHub에서 issue 열기" title="GitHub에서 issue 열기">
                <ExternalIcon />
              </IconButton>
            )}
            <IconButton label="새로고침" title="새로고침" onClick={() => setReloadKey((k) => k + 1)}>
              <ReloadIcon />
            </IconButton>
          </div>
        </header>
        {group ? (
          <IssuePage key={group.key} group={group} groups={groups} onOpenIssue={openIssue} onSelectRun={selectRun} />
        ) : home ? (
          <Lineage groups={groups} onOpenIssue={openIssue} />
        ) : (
          <div className={styles.workspace}>
            {run && sel && <RunPanel key={run.id} run={run} group={runGroup} grid={grid} sel={sel} onSelect={selectEpisode} />}
            {ep ? (
              <div className={styles.stage}>
                <div className={styles.scene}>
                  <ThirdPersonView key={file} ep={ep} scheme={scheme} />
                </div>
                <aside className={styles.inspector} aria-label={ep.meta.mode === 'free-flight' ? '초파리 비행 상태' : '조준기 화면과 현재 상태'}>
                  {ep.meta.aimerEnabled !== false && <FirstPersonView key={file} ep={ep} />}
                  {ep.meta.aimerEnabled !== false && ep.meta.captureEnabled !== false && ep.meta.captureRadius != null && (
                    <ZoomView key={`zoom-${file}`} ep={ep} />
                  )}
                  <Readouts ep={ep} scheme={scheme} />
                </aside>
                <div className={styles.dock}>
                  <Transport ep={ep} />
                  <Charts ep={ep} />
                </div>
              </div>
            ) : (
              <p className={styles.empty}>{list && !sel ? '저장된 에피소드가 없어요.' : ''}</p>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
