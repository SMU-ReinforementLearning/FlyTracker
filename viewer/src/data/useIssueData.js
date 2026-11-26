// issue 하나의 실행 설정과 설명 파일을 읽는 hook. issue 화면, 사이드바, 실행 패널이 함께 쓴다.
import { useEffect, useMemo, useState } from 'react'
import { fetchConfig, fetchIssueInfo } from './api.js'
import { combinationsOf, referencedRunIds } from './experiment.js'
import { byCreatedAt, issueKeyOf, NO_ISSUE } from './runs.js'

export const NO_RUNS = []

/** runs 와 같은 순서의 config.json. 못 읽은 실행은 null, 다 읽기 전에는 null 을 돌려준다. */
export function useConfigs(runs) {
  const [state, setState] = useState(null) // { runs, configs }
  useEffect(() => {
    let alive = true
    Promise.all(runs.map((r) => fetchConfig(r.id).catch(() => null))).then((configs) => {
      if (alive) setState({ runs, configs })
    })
    return () => {
      alive = false
    }
  }, [runs])
  if (runs.length === 0) return NO_RUNS
  return state?.runs === runs ? state.configs : null
}

/** issue 설명 파일. 읽는 중에는 undefined, 없으면 null. key 가 null 이거나 issue 없음 묶음이면 늘 null. */
export function useIssueInfo(key) {
  const none = key == null || key === NO_ISSUE
  const [state, setState] = useState(null) // { key, info }
  useEffect(() => {
    if (none) return
    let alive = true
    fetchIssueInfo(key).then((info) => {
      if (alive) setState({ key, info })
    })
    return () => {
      alive = false
    }
  }, [key, none])
  if (none) return null
  return state?.key === key ? state.info : undefined
}

// 실행 목록 전체. 다른 issue 에서 학습한 모델을 찾는 데 쓴다. App 이 목록을 읽을 때마다 넣는다.
let allRuns = []
const originCache = new Map() // issue key -> Promise<Map<실행 id, 글>>
const NO_ORIGINS = new Map()

export function setAllRuns(runs) {
  allRuns = runs ?? []
  originCache.clear()
}

/** issue 하나의 학습 실행을 '#51 실험 B' 같은 글로 부르는 Map. 조합이 하나뿐인 issue 는 '#35' 다. */
function originsOfIssue(key) {
  if (!originCache.has(key)) {
    const runs = allRuns.filter((r) => issueKeyOf(r) === key).sort(byCreatedAt)
    const loading = Promise.all([Promise.all(runs.map((r) => fetchConfig(r.id).catch(() => null))), fetchIssueInfo(key)]).then(([configs, info]) => {
      const rows = combinationsOf(runs, configs, info)
      const out = new Map()
      for (const row of rows) if (row.record === 'training') for (const r of row.runs) out.set(r.id, rows.length > 1 ? `#${key} 실험 ${row.letter}` : `#${key}`)
      return out
    })
    originCache.set(key, loading)
  }
  return originCache.get(key)
}

/**
 * 이 실행들이 가리키는 다른 issue 의 학습 실행을 부르는 글(combinationsOf 의 origins). 읽는 중에는 null 이다.
 * 평가 실행의 모델이 다른 issue 에서 학습한 것일 때(#72 의 모델은 #51 에서 학습했다) 그 issue 의 설정을 읽어 줄의 글자를 찾는다.
 */
export function useOrigins(runs, configs) {
  const [state, setState] = useState(null) // { configs, origins }
  const keys = useMemo(() => {
    if (!configs) return null
    const own = new Set(runs.map((r) => r.id))
    const found = new Set()
    for (const id of referencedRunIds(configs)) {
      const src = own.has(id) ? null : allRuns.find((r) => r.id === id)
      if (src && issueKeyOf(src) !== NO_ISSUE) found.add(issueKeyOf(src))
    }
    return [...found]
  }, [runs, configs])
  useEffect(() => {
    if (!keys || keys.length === 0) return
    let alive = true
    Promise.all(keys.map(originsOfIssue)).then((maps) => {
      if (alive) setState({ configs, origins: new Map(maps.flatMap((m) => [...m])) })
    })
    return () => {
      alive = false
    }
  }, [keys, configs])
  if (!keys) return null
  if (keys.length === 0) return NO_ORIGINS
  return state?.configs === configs ? state.origins : null
}

/**
 * issue 묶음의 조합(experiment.js 의 combinationsOf). runs 는 그 묶음의 실행이고 key 는 묶음의 key 다.
 * 설정이나 설명 파일을 읽는 중에는 null 을 돌려준다. runs 는 다시 그릴 때마다 같은 배열이어야 한다(useConfigs).
 */
export function useCombinations(runs, key) {
  const configs = useConfigs(runs)
  const info = useIssueInfo(key)
  const origins = useOrigins(runs, configs)
  return useMemo(() => (configs && info !== undefined && origins ? combinationsOf(runs, configs, info, origins) : null), [runs, configs, info, origins])
}
