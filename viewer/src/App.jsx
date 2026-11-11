import { useEffect, useMemo, useState } from 'react'
import { IssuePage } from './components/IssuePage.jsx'
import { LineChart } from './components/LineChart.jsx'
import { Readouts } from './components/Readouts.jsx'
import { RunPanel } from './components/RunPanel.jsx'
import { groupTitle, Sidebar } from './components/Sidebar.jsx'
import { stepFrame, Transport } from './components/Transport.jsx'
import { fetchEpisode, fetchEpisodes, fetchRuns } from './data/api.js'
import { prepareEpisode } from './data/episode.js'
import { seconds, signed, tagLabel } from './data/labels.js'
import { gridOf, groupByIssue } from './data/runs.js'
import { load, togglePlay, useClock } from './playback/clock.js'
import { useRoute } from './route.js'
import { FirstPersonView } from './scene/FirstPersonView.jsx'
import { ThirdPersonView } from './scene/ThirdPersonView.jsx'
import { useColorScheme } from './theme.js'

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
  return (
    <div className="charts">
      <LineChart ep={ep} values={ep.returns} label="누적 보상" format={(v) => signed(v, 2)} tickFormat={(v) => signed(v, 0)} t={t} zeroBased />
      <LineChart ep={ep} values={ep.angle} label="조준 오차" format={(v) => `${v.toFixed(1)}°`} tickFormat={(v) => `${v}°`} t={t} zeroBased />
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
        setRuns(list)
        setRunsError(false)
      },
      () => setRunsError(true),
    )
  }, [reloadKey])

  // URL 이 가리키는 것. 모르는 issue 나 실행이면 가장 최근 실행을 연다.
  const groups = useMemo(() => (runs ? groupByIssue(runs) : null), [runs])
  const group = groups?.find((g) => g.key === route.issue) ?? null
  const run = group ? null : (runs?.find((r) => r.id === route.run) ?? runs?.[0] ?? null)
  const runId = run?.id ?? null

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

  const title = group ? groupTitle(group) : run ? run.name : 'FlyTracker'
  return (
    <div className="app">
      <Sidebar groups={groups} error={runsError} runId={runId} issueKey={group?.key ?? null} onSelectRun={selectRun} onOpenIssue={openIssue} />
      <main className="main">
        <header className="toolbar">
          <div className="toolbar-lead">
            {group?.issue && <span className="toolbar-num">#{group.issue.number}</span>}
            <h1 className="toolbar-title">{title}</h1>
            {episode && (
              <span className="toolbar-meta">
                <span>{tagLabel(episode.tag)}</span>
                <span>에피소드 {sel.k + 1}</span>
                <span className={episode.summary.captured ? 'outcome outcome-capture' : 'outcome'}>
                  {episode.summary.captured ? `포획 ${seconds(episode.summary.duration)}` : '시간 초과'}
                </span>
                <span>보상 {signed(episode.summary.return)}</span>
              </span>
            )}
          </div>
          <div className="toolbar-actions">
            {group?.issue && (
              <a className="icon-button" href={group.issue.url} target="_blank" rel="noreferrer" aria-label="GitHub에서 issue 열기" title="GitHub에서 issue 열기">
                <ExternalIcon />
              </a>
            )}
            <button type="button" className="icon-button" aria-label="새로고침" title="새로고침" onClick={() => setReloadKey((k) => k + 1)}>
              <ReloadIcon />
            </button>
          </div>
        </header>
        {group ? (
          <IssuePage key={group.key} group={group} onSelectRun={selectRun} />
        ) : (
          <div className="workspace">
            {run && sel && <RunPanel key={run.id} run={run} grid={grid} sel={sel} onSelect={selectEpisode} />}
            {ep ? (
              <div className="stage">
                <div className="scene">
                  <ThirdPersonView key={file} ep={ep} scheme={scheme} />
                </div>
                <aside className="inspector" aria-label="조준기 화면과 현재 상태">
                  <FirstPersonView key={file} ep={ep} />
                  <Readouts ep={ep} scheme={scheme} />
                </aside>
                <div className="dock">
                  <Transport ep={ep} />
                  <Charts ep={ep} />
                </div>
              </div>
            ) : (
              <p className="empty">{list && !sel ? '저장된 에피소드가 없어요.' : ''}</p>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
