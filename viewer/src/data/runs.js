// 실행 목록(index.json)과 에피소드 목록(episodes.json)을 화면이 쓰는 모양으로 바꾼다.
import { algoLabel } from './labels.js'

export const NO_ISSUE = 'none'

/** checkpoint 의 포획률(0~1). 에피소드가 없으면 null. */
export const rateOf = (c) => (c && c.episodes ? c.captured / c.episodes : null)

export const lastCheckpoint = (run) => run.checkpoints?.at(-1) ?? null

/** 학습 step 이 있는 checkpoint 만. 기준선처럼 step 이 없는 것은 곡선에 점으로 찍지 못한다. */
export const steppedCheckpoints = (run) => (run.checkpoints ?? []).filter((c) => c.step !== null)

export const issueKeyOf = (run) => (run.issue?.number != null ? String(run.issue.number) : NO_ISSUE)

/** runs 는 최근순. 묶음도 가장 최근 실행이 있는 것이 위로 오고, issue 가 없는 묶음은 맨 아래다. */
export function groupByIssue(runs) {
  const groups = new Map()
  for (const run of runs) {
    const key = issueKeyOf(run)
    if (!groups.has(key)) groups.set(key, { key, issue: run.issue ?? null, runs: [] })
    groups.get(key).runs.push(run)
  }
  const list = [...groups.values()]
  return [...list.filter((g) => g.key !== NO_ISSUE), ...list.filter((g) => g.key === NO_ISSUE)]
}

export function matchesQuery(run, query) {
  const q = query.trim().toLowerCase()
  if (!q) return true
  const fields = [run.name, run.author, run.algo, algoLabel(run.algo), run.issue?.title, run.issue ? `#${run.issue.number}` : '']
  return fields.some((f) => f && String(f).toLowerCase().includes(q))
}

/** 에피소드를 checkpoint(tag) 별 행으로 묶는다. 행은 기록된 순서, 곧 학습이 진행된 순서다. */
export function gridOf(episodes) {
  const rows = new Map()
  for (const e of episodes ?? []) {
    if (!rows.has(e.tag)) rows.set(e.tag, { tag: e.tag, items: [] })
    rows.get(e.tag).items.push(e)
  }
  return [...rows.values()]
}

/** config.json 을 `env.camera.fov_v_deg` 같은 한 줄 key 로 편다. 배열은 값 하나로 본다. */
export function flattenConfig(value, prefix = '', out = {}) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    for (const [k, v] of Object.entries(value)) flattenConfig(v, prefix ? `${prefix}.${k}` : k, out)
  } else if (prefix) {
    out[prefix] = value
  }
  return out
}

const SKIP_KEYS = new Set(['algo.name']) // 알고리즘은 표에 따로 열이 있다

/**
 * 실행끼리 값이 다른 config key. 그 key 가 있는 실행들 사이에서만 비교한다.
 * 기준선에는 algo.steps 같은 key 가 아예 없는데, 그것만으로 열이 생기면 표가 같은 값으로 채워지기 때문이다.
 */
export function differingKeys(flatConfigs) {
  const keys = new Set(flatConfigs.flatMap((c) => Object.keys(c)))
  const distinct = (k) => new Set(flatConfigs.filter((c) => k in c).map((c) => JSON.stringify(c[k]))).size
  return [...keys].filter((k) => !SKIP_KEYS.has(k) && distinct(k) > 1).sort()
}
