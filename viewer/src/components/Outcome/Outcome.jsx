import styles from './Outcome.module.css'

/** 에피소드 결과 글자. 포획이면 앞에 초록 점을 붙인다. */
export function Outcome({ captured, className, children }) {
  const cls = [captured && styles.capture, className].filter(Boolean).join(' ')
  return <span className={cls || undefined}>{children}</span>
}
