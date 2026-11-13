import styles from './ListRow.module.css'

/** 고를 수 있는 줄의 목록. 사이드바의 실행 목록과 실행 패널의 에피소드 목록에서 쓴다. */
export function RowList({ children }) {
  return <ul className={styles.list}>{children}</ul>
}

/**
 * 목록의 줄 하나. 고른 줄은 강조색 바탕이 된다.
 * 줄 안의 배치는 쓰는 쪽이 정하므로 className 으로 받는다. 이 모양보다 앞서야 하는 규칙은 쓰는 쪽에서 선택자를 한 단계 더 써서 이긴다.
 */
export function ListRow({ current, onClick, className, children }) {
  return (
    <li>
      <button type="button" className={className ? `${styles.row} ${className}` : styles.row} aria-current={current} onClick={onClick}>
        {children}
      </button>
    </li>
  )
}
