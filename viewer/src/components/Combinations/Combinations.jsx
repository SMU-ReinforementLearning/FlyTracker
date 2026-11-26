import { seedLabel } from '../../data/experiment.js'
import { lastCheckpoint } from '../../data/runs.js'
import styles from './Combinations.module.css'

const OBSERVING = new Set(['free-flight', 'tracking-observation'])

/** 칸 하나. 종류와 버전이 윗줄이고, 다른 조합과 값이 다른 줄이 그 아래에 이름과 값으로 온다. */
export function CombinationCell({ cell }) {
  return (
    <>
      <span className={styles.kind}>{cell.title}</span>
      {cell.details.length > 0 && (
        <dl className={styles.details}>
          {cell.details.map((d) => (
            <div key={d.label}>
              <dt>{d.label}</dt>
              <dd>{d.value}</dd>
            </div>
          ))}
        </dl>
      )}
    </>
  )
}

/** 실행 하나로 가는 버튼. 이름 옆에 마지막 checkpoint 의 포획 수를 적는다. 관찰 기록은 에피소드 수를 적는다. */
function RunLink({ run, label, onOpen }) {
  const last = lastCheckpoint(run)
  const observing = OBSERVING.has(run.algo)
  return (
    <button
      type="button"
      className={styles.run}
      title={label ? run.name : undefined}
      onClick={(e) => {
        e.stopPropagation()
        onOpen(run.id)
      }}
    >
      <span>{label ?? run.name}</span>
      {last?.episodes > 0 && (
        <span className={styles.count} aria-label={observing ? `에피소드 ${last.episodes}개` : `포획 ${last.captured}, 전체 ${last.episodes}`}>
          {observing ? `${last.episodes}개` : `${last.captured}/${last.episodes}`}
        </span>
      )}
    </button>
  )
}

/**
 * issue 안의 조합 표. 줄 하나가 조합 하나이고, 초파리, 조준기, 환경이 늘 같은 칸에 온다(experiment.js 의 combinationsOf).
 * 맨 앞 칸은 그 줄을 부르는 글자다(A, B, C). 실행 패널도 같은 글자로 조합을 부른다.
 * 조합이 둘 이상이면 줄을 눌러 고른다. 고른 줄을 다시 누르면 전체로 돌아간다. 고른 조합은 selected(조합의 key)로 받는다.
 * 마지막 칸의 실행 버튼은 그 실행의 화면으로 간다. runs 는 이 issue 의 실행 목록이다.
 */
export function Combinations({ rows, runs, selected, onSelect, onOpenRun }) {
  const byId = new Map(runs.map((r) => [r.id, r]))
  const selectable = rows.length > 1
  const toggle = (key) => onSelect(key === selected ? null : key)
  return (
    <div className={styles.scroll}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th scope="col">실험</th>
            <th scope="col">초파리</th>
            <th scope="col">조준기</th>
            <th scope="col">환경</th>
            <th scope="col">실행</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.key}
              className={selectable ? styles.selectable : undefined}
              aria-selected={selectable ? row.key === selected : undefined}
              tabIndex={selectable ? 0 : undefined}
              onClick={selectable ? () => toggle(row.key) : undefined}
              onKeyDown={
                selectable
                  ? (e) => {
                      if (e.target !== e.currentTarget || (e.key !== 'Enter' && e.key !== ' ')) return
                      e.preventDefault()
                      toggle(row.key)
                    }
                  : undefined
              }
            >
              <th scope="row" className={styles.letter}>
                {row.letter}
              </th>
              <td>
                <CombinationCell cell={row.fly} />
              </td>
              <td>
                <CombinationCell cell={row.aimer} />
              </td>
              <td>
                <CombinationCell cell={row.environment} />
              </td>
              <td>
                <div className={styles.runs}>
                  {row.runs.map(({ id, seed }) => (
                    <RunLink key={id} run={byId.get(id)} label={seedLabel(seed)} onOpen={onOpenRun} />
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
