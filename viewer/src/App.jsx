import { useCallback, useEffect, useState } from 'react'
import { LineChart } from './components/LineChart.jsx'
import { Readouts } from './components/Readouts.jsx'
import { Sidebar } from './components/Sidebar.jsx'
import { stepFrame, Transport } from './components/Transport.jsx'
import { fetchEpisode, fetchEpisodes, fetchRuns } from './data/api.js'
import { prepareEpisode } from './data/episode.js'
import { signed } from './data/labels.js'
import { load, togglePlay, useClock } from './playback/clock.js'
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
  const [runs, setRuns] = useState(null)
  const [runsError, setRunsError] = useState(false)
  const [runId, setRunId] = useState(null)
  const [episodes, setEpisodes] = useState(null)
  const [file, setFile] = useState(null)
  const [ep, setEp] = useState(null)
  const [reloadKey, setReloadKey] = useState(0)

  const loadRuns = useCallback(async () => {
    try {
      const list = await fetchRuns()
      setRuns(list)
      setRunsError(false)
      setRunId((cur) => (cur && list.some((r) => r.id === cur) ? cur : list[0]?.id ?? null))
    } catch {
      setRunsError(true)
    }
  }, [])

  useEffect(() => {
    loadRuns()
  }, [loadRuns, reloadKey])

  useEffect(() => {
    if (!runId) return
    let alive = true
    fetchEpisodes(runId)
      .then((list) => {
        if (!alive) return
        setEpisodes(list)
        setFile((cur) => (cur && list.some((e) => e.file === cur) ? cur : list.at(-1)?.file ?? null))
      })
      .catch(() => alive && setEpisodes([]))
    return () => {
      alive = false
    }
  }, [runId, reloadKey])

  useEffect(() => {
    if (!file) return
    let alive = true
    fetchEpisode(file).then((raw) => {
      if (!alive) return
      const prepared = prepareEpisode(raw)
      setEp(prepared)
      load(prepared.duration)
    })
    return () => {
      alive = false
    }
  }, [file])

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

  const run = runs?.find((r) => r.id === runId)
  const selectRun = (id) => {
    if (id === runId) return
    setRunId(id)
    setEpisodes(null)
    setFile(null)
    setEp(null)
  }

  return (
    <div className="app">
      <Sidebar
        runs={runs}
        runsError={runsError}
        runId={runId}
        onSelectRun={selectRun}
        episodes={episodes}
        file={file}
        onSelectEpisode={setFile}
      />
      <main className="main">
        <header className="toolbar">
          <h1 className="toolbar-title">{run ? run.name : 'FlyTracker'}</h1>
          <button type="button" className="icon-button" aria-label="새로고침" title="새로고침" onClick={() => setReloadKey((k) => k + 1)}>
            <ReloadIcon />
          </button>
        </header>
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
          <p className="empty">{runs?.length ? '왼쪽 목록에서 에피소드를 골라 주세요.' : ''}</p>
        )}
      </main>
    </div>
  )
}
