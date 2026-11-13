import styles from './Segmented.module.css'

/**
 * 여럿 중 하나를 고르는 버튼 묶음. 재생 속도와 학습 곡선 값 고르기에 쓴다.
 * options: [{ value, label }]. className 은 놓이는 자리의 여백처럼 바깥에서 정할 것만 받는다.
 */
export function Segmented({ label, options, value, onChange, className }) {
  return (
    <div className={className ? `${styles.segmented} ${className}` : styles.segmented} role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} type="button" role="radio" aria-checked={value === o.value} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  )
}
