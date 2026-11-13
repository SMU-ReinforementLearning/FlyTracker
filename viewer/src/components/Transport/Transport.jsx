import { frameAt } from '../../data/episode.js'
import { clock, seek, setSpeed, togglePlay, useClock } from '../../playback/clock.js'
import { IconButton } from '../IconButton/IconButton.jsx'
import { Segmented } from '../Segmented/Segmented.jsx'
import styles from './Transport.module.css'

// 숫자와 × 를 따로 둔다. 한 문자열로 합치면 글자 폭이 1/64px 달라진다.
const SPEEDS = [0.25, 0.5, 1, 2].map((s) => ({ value: s, label: <>{s}×</> }))

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
    <div className={styles.transport}>
      <div className={styles.buttons}>
        <IconButton label="이전 프레임" onClick={() => stepFrame(ep, -1)}>
          <Icon name="prev" />
        </IconButton>
        <button type="button" className={styles.playButton} aria-label={c.playing ? '일시정지' : '재생'} onClick={togglePlay}>
          <Icon name={c.playing ? 'pause' : 'play'} />
        </button>
        <IconButton label="다음 프레임" onClick={() => stepFrame(ep, 1)}>
          <Icon name="next" />
        </IconButton>
      </div>
      <input
        className={styles.scrubber}
        type="range"
        min={0}
        max={c.duration}
        step={0.001}
        value={c.t}
        style={{ '--progress': `${progress}%` }}
        aria-label="재생 위치"
        onChange={(e) => seek(Number(e.target.value))}
      />
      <span className={styles.time}>
        {c.t.toFixed(2)} / {c.duration.toFixed(2)}초
      </span>
      <Segmented label="재생 속도" options={SPEEDS} value={c.speed} onChange={setSpeed} className={styles.speeds} />
    </div>
  )
}
