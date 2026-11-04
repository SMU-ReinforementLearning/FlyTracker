// runs/ 아래 JSON 을 읽는다. 파일 형식은 flytracker/record.py 가 정한다.

async function getJson(path) {
  const res = await fetch(`/runs/${path}`, { cache: 'no-store' })
  if (!res.ok) throw new Error(`${res.status} ${path}`)
  return res.json()
}

export async function fetchRuns() {
  try {
    const index = await getJson('index.json')
    return [...index.runs].reverse() // 최근 실행이 위로
  } catch (err) {
    if (String(err.message).startsWith('404')) return []
    throw err
  }
}

export async function fetchEpisodes(runId) {
  const manifest = await getJson(`${runId}/episodes.json`)
  return manifest.episodes
}

export async function fetchEpisode(file) {
  return getJson(file)
}
