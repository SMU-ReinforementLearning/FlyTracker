import styles from './Tooltip.module.css'

/**
 * 그래프 위에 뜨는 값 상자. 기본은 가리키는 점 위 가운데에 뜬다.
 * side 면 점 오른쪽에 세로로 쌓이고, flip 이면 점 왼쪽으로 넘어간다.
 */
export function Tooltip({ side = false, flip, style, children }) {
  return (
    <div className={side ? `${styles.tooltip} ${styles.side}` : styles.tooltip} data-flip={side ? flip : undefined} style={style} role="status">
      {children}
    </div>
  )
}

/** side 값 상자의 한 줄. 값(strong)은 오른쪽 끝에 붙는다. */
export function TooltipRow({ children }) {
  return <span className={styles.row}>{children}</span>
}
