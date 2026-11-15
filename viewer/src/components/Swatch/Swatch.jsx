import styles from './Swatch.module.css'

/** 그래프의 어느 선이 어느 실행인지 알려 주는 색 점 */
export function Swatch({ color }) {
  return <i className={styles.swatch} style={{ background: color }} />
}
