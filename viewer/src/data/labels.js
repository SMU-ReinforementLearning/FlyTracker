// 화면 표기. ui-text.glossary.md 와 같은 표기를 쓴다.

const ALGO = { sac: 'SAC', td3: 'TD3', ppo: 'PPO', dqn: 'DQN', 'rule-baseline': '기준선', 'free-flight': '비행 관찰', 'tracking-observation': '추적 관찰', 'neural-tracking': '신경 초파리 추적' }

export const algoLabel = (algo) => ALGO[algo] ?? algo

export function tagLabel(tag) {
  if (tag === 'free-flight') return '비행 관찰'
  if (tag === 'tracking-observation') return '추적 관찰'
  if (tag === 'neural-tracking') return '신경 초파리 추적'
  if (tag === 'baseline') return '기준선'
  const m = /^step_(\d+)$/.exec(tag)
  if (!m) return tag
  const step = Number(m[1])
  return step === 0 ? '학습 전' : `${step.toLocaleString('ko-KR')} step`
}

export const seconds = (s, digits = 1) => `${s.toFixed(digits)}초`

export function signed(x, digits = 1) {
  const v = x.toFixed(digits)
  return x < 0 ? `−${v.slice(1)}` : v
}

export function shortDate(iso) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${d.getMonth() + 1}월 ${d.getDate()}일 ${hh}:${mm}`
}

export const percent = (ratio) => `${Math.round(ratio * 100)}%`

export const stepLabel = (step) => step.toLocaleString('ko-KR')
