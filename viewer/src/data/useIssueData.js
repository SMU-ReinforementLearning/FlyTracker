// issue 하나의 실행 설정과 설명 파일을 읽는 hook. issue 화면, 사이드바, 실행 패널이 함께 쓴다.
import { useEffect, useMemo, useState } from 'react'
import { fetchConfig, fetchIssueInfo } from './api.js'
import { combinationsOf } from './experiment.js'
import { NO_ISSUE } from './runs.js'

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

/**
 * issue 묶음의 조합(experiment.js 의 combinationsOf). runs 는 그 묶음의 실행이고 key 는 묶음의 key 다.
 * 설정이나 설명 파일을 읽는 중에는 null 을 돌려준다. runs 는 다시 그릴 때마다 같은 배열이어야 한다(useConfigs).
 */
export function useCombinations(runs, key) {
  const configs = useConfigs(runs)
  const info = useIssueInfo(key)
  return useMemo(() => (configs && info !== undefined ? combinationsOf(runs, configs, info) : null), [runs, configs, info])
}
