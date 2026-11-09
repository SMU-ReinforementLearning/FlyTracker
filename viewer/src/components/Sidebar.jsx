import { algoLabel, seconds, shortDate, signed, tagLabel } from '../data/labels.js'

function RunList({ runs, error, selectedId, onSelect }) {
  if (error) {
    return <p className="sidebar-note">runs 폴더를 읽지 못했어요. 저장소의 viewer 폴더에서 npm run dev로 실행했는지 확인해 주세요.</p>
  }
  if (!runs) return <p className="sidebar-note">불러오는 중</p>
  if (runs.length === 0) {
    return (
      <p className="sidebar-note">
        기록된 실행이 없어요. <code>scripts/record_baseline.py</code>로 에피소드를 만들어 주세요.
      </p>
    )
  }
  return (
    <ul className="source-list">
      {runs.map((run) => (
        <li key={run.id}>
          <button type="button" className="row" aria-current={run.id === selectedId} onClick={() => onSelect(run.id)}>
            <span className="row-line">
              <span className="row-title">{run.name}</span>
              <span className="row-aside">{shortDate(run.createdAt)}</span>
            </span>
            <span className="row-line row-sub">
              <span>{algoLabel(run.algo)}</span>
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}

function groupByTag(episodes) {
  const groups = new Map()
  episodes.forEach((e) => {
    if (!groups.has(e.tag)) groups.set(e.tag, [])
    groups.get(e.tag).push(e)
  })
  return [...groups.entries()].reverse() // 최근 체크포인트가 위로
}

function EpisodeList({ episodes, selectedFile, onSelect }) {
  if (!episodes) return null
  if (episodes.length === 0) return <p className="sidebar-note">저장된 에피소드가 없어요.</p>
  return groupByTag(episodes).map(([tag, items]) => (
    <section key={tag} className="episode-group" aria-label={tagLabel(tag)}>
      <h3 className="group-title">{tagLabel(tag)}</h3>
      <ul className="source-list">
        {items.map((e, k) => (
          <li key={e.file}>
            <button type="button" className="row" aria-current={e.file === selectedFile} onClick={() => onSelect(e.file)}>
              <span className="row-line">
                <span className="row-title">에피소드 {k + 1}</span>
                <span className="row-aside">{seconds(e.summary.duration)}</span>
              </span>
              <span className="row-line row-sub">
                <span className={e.summary.captured ? 'outcome outcome-capture' : 'outcome'}>
                  {e.summary.captured ? '포획' : '시간 초과'}
                </span>
                <span>보상 {signed(e.summary.return)}</span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  ))
}

export function Sidebar({ runs, runsError, runId, onSelectRun, episodes, file, onSelectEpisode }) {
  return (
    <nav className="sidebar" aria-label="실행과 에피소드">
      <h2 className="sidebar-title">실행</h2>
      <RunList runs={runs} error={runsError} selectedId={runId} onSelect={onSelectRun} />
      {runId && (
        <>
          <h2 className="sidebar-title">에피소드</h2>
          <EpisodeList episodes={episodes} selectedFile={file} onSelect={onSelectEpisode} />
        </>
      )}
    </nav>
  )
}
