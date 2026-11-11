import { useCallback, useEffect, useState } from 'react'

// 무엇을 골랐는지는 URL 이 갖는다. 새로고침과 뒤로 가기가 그대로 동작하고, 링크를 보내면 같은 에피소드가 열린다.
//   ?run=<실행 id>&tag=<checkpoint tag>&ep=<에피소드 번호, 1부터>
//   ?issue=<issue 번호 | none>
const KEYS = ['run', 'tag', 'ep', 'issue']

function read() {
  const params = new URLSearchParams(window.location.search)
  const route = {}
  for (const k of KEYS) if (params.has(k)) route[k] = params.get(k)
  return route
}

function searchOf(route) {
  const params = new URLSearchParams()
  for (const k of KEYS) if (route[k] != null) params.set(k, String(route[k]))
  const s = params.toString()
  return s ? `?${s}` : ''
}

export function useRoute() {
  const [route, setRoute] = useState(read)

  useEffect(() => {
    const onPop = () => setRoute(read())
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])

  /** replace 는 주소만 바로잡을 때 쓴다. 뒤로 가기 기록을 늘리지 않는다. */
  const navigate = useCallback((next, replace = false) => {
    const search = searchOf(next)
    if (search === window.location.search) return
    const url = search || window.location.pathname
    if (replace) window.history.replaceState(null, '', url)
    else window.history.pushState(null, '', url)
    setRoute(read())
  }, [])

  return [route, navigate]
}
