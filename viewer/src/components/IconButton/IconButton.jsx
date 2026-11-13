import styles from './IconButton.module.css'

/**
 * 아이콘만 있는 둥근 버튼. 글자가 없으니 label 이 화면 읽기 프로그램에 읽힐 이름이 된다.
 * href 를 주면 새 탭으로 여는 링크가 된다.
 */
export function IconButton({ label, title, href, onClick, children }) {
  if (href) {
    return (
      <a className={styles.button} href={href} target="_blank" rel="noreferrer" aria-label={label} title={title}>
        {children}
      </a>
    )
  }
  return (
    <button type="button" className={styles.button} aria-label={label} title={title} onClick={onClick}>
      {children}
    </button>
  )
}
