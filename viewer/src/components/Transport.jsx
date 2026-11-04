import { frameAt } from '../data/episode.js'
import { clock, seek, setSpeed, togglePlay, useClock } from '../playback/clock.js'

const SPEEDS = [0.25, 0.5, 1, 2]

export function stepFrame(ep, delta) {
  const i = frameAt(ep, clock.t + 1e-9)
  const j = Math.min(Math.max(i + delta, 0), ep.n - 1)
  clock.playing = false
  seek(ep.t[j])
}

function Icon({ name }) {
  const paths = {
    play: <path d="M8 5.5v13l11-6.5z" />,
    pause: (
      <>
        <rect x="6.5" y="5" width="4" height="14" rx="1.2" />
        <rect x="13.5" y="5" width="4" height="14" rx="1.2" />
      </>
    ),
    prev: <path d="M15.5 6 9.5 12l6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />,
    next: <path d="m8.5 6 6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />,
  }
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
      {paths[name]}
    </svg>
  )
}

export function Transport({ ep }) {
  const c = useClock(20)
  const progress = c.duration > 0 ? (c.t / c.duration) * 100 : 0
  return (
    <div className="transport">
      <div className="transport-buttons">
        <button type="button" className="icon-button" aria-label="이전 프레임" onClick={() => stepFrame(ep, -1)}>
          <Icon name="prev" />
        </button>
        <button type="button" className="play-button" aria-label={c.playing ? '일시정지' : '재생'} onClick={togglePlay}>
          <Icon name={c.playing ? 'pause' : 'play'} />
        </button>
        <button type="button" className="icon-button" aria-label="다음 프레임" onClick={() => stepFrame(ep, 1)}>
          <Icon name="next" />
        </button>
      </div>
      <input
        className="scrubber"
        type="range"
        min={0}
        max={c.duration}
        step={0.001}
        value={c.t}
        style={{ '--progress': `${progress}%` }}
        aria-label="재생 위치"
        onChange={(e) => seek(Number(e.target.value))}
      />
      <span className="time">
        {c.t.toFixed(2)} / {c.duration.toFixed(2)}초
      </span>
      <div className="segmented" role="radiogroup" aria-label="재생 속도">
        {SPEEDS.map((s) => (
          <button key={s} type="button" role="radio" aria-checked={c.speed === s} onClick={() => setSpeed(s)}>
            {s}×
          </button>
        ))}
      </div>
    </div>
  )
}
