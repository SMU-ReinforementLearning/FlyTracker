import { readdir, readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// 화면 코드는 에피소드를 늘 /runs 주소로 읽는다. 그 주소에 무엇을 내줄지는 여기서 정한다.
//   개발 서버: runs/(내 컴퓨터에서 만든 실행)와 published/(저장소에 올라온 실행)를 함께 내준다.
//   build: published/ 만 dist/runs/ 에 넣는다. Cloudflare 에 올라가는 것은 이것뿐이다.
// published/ 에는 index.json 이 없다. 실행마다 있는 run.json 을 모아 목록을 만든다(flytracker/record.py).
// 목록의 실행마다 checkpoint 별 요약(checkpoints)을 붙인다. 화면이 에피소드 파일을 다 받지 않고 학습 곡선을 그리게 하려는 것이다.
const ROOT = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..')
const RUNS_DIR = path.join(ROOT, 'runs')
const PUBLISHED_DIR = path.join(ROOT, 'published')
const INDEX_FORMAT = 'flytracker.runs/1'

async function readJson(file, fallback) {
  try {
    return JSON.parse(await readFile(file, 'utf8'))
  } catch (err) {
    if (err.code === 'ENOENT') return fallback
    throw err
  }
}

async function dirents(dir) {
  try {
    return await readdir(dir, { withFileTypes: true })
  } catch (err) {
    if (err.code === 'ENOENT') return []
    throw err
  }
}

/** dir 아래 JSON 파일의 상대 경로(/ 구분). 점으로 시작하는 것(복사 중인 임시 폴더)은 건너뛴다. */
async function listJson(dir, prefix = '') {
  const out = []
  for (const d of await dirents(dir)) {
    if (d.name.startsWith('.')) continue
    const rel = prefix + d.name
    if (d.isDirectory()) out.push(...(await listJson(path.join(dir, d.name), rel + '/')))
    else if (d.name.endsWith('.json')) out.push(rel)
  }
  return out
}

/** tag 이름의 학습 step. 기준선처럼 step 이 없는 tag 는 null. */
function stepOf(tag) {
  if (tag === 'initial') return 0
  const m = /^step_(\d+)$/.exec(tag)
  return m ? Number(m[1]) : null
}

const round4 = (v) => Math.round(v * 1e4) / 1e4
const mean = (xs) => (xs.length ? round4(xs.reduce((a, b) => a + b, 0) / xs.length) : null)

/** episodes.json 의 에피소드 요약을 tag 별로 모은다. step 순서이고, step 이 없는 tag 가 앞에 온다. */
export function checkpointsOf(manifest) {
  const byTag = new Map()
  for (const e of manifest?.episodes ?? []) {
    if (!byTag.has(e.tag)) byTag.set(e.tag, [])
    byTag.get(e.tag).push(e.summary ?? {})
  }
  return [...byTag]
    .map(([tag, list]) => {
      const caught = list.filter((s) => s.captured)
      return {
        tag,
        step: stepOf(tag),
        episodes: list.length,
        captured: caught.length,
        meanReturn: mean(list.map((s) => s.return ?? 0)),
        meanCaptureTime: mean(caught.map((s) => s.duration ?? 0)),
      }
    })
    .sort((a, b) => (a.step ?? -1) - (b.step ?? -1))
}

async function withCheckpoints(entry, root) {
  const manifest = await readJson(path.join(root, entry.id, 'episodes.json'), null)
  return { ...entry, checkpoints: checkpointsOf(manifest) }
}

async function publishedRuns() {
  const runs = []
  for (const d of await dirents(PUBLISHED_DIR)) {
    if (!d.isDirectory() || d.name.startsWith('.')) continue
    const entry = await readJson(path.join(PUBLISHED_DIR, d.name, 'run.json'), null)
    if (entry) runs.push(await withCheckpoints(entry, PUBLISHED_DIR))
  }
  return runs
}

const byCreatedAt = (a, b) => String(a.createdAt).localeCompare(String(b.createdAt))

/**
 * 같은 id 가 양쪽에 있으면 runs/ 쪽 목록과 파일을 쓰되, issue 와 올린 사람은 published/ 의 run.json 에서 가져온다.
 * runs/index.json 에는 그 둘이 없기 때문이다. 파일도 runs/ 에서 먼저 찾는다.
 */
async function devIndex() {
  const published = await publishedRuns()
  const pub = new Map(published.map((r) => [r.id, r]))
  const local = []
  for (const r of (await readJson(path.join(RUNS_DIR, 'index.json'), { runs: [] })).runs) {
    const { issue, author } = pub.get(r.id) ?? {}
    local.push(await withCheckpoints({ ...r, ...(issue && { issue }), ...(author !== undefined && { author }) }, RUNS_DIR))
  }
  const seen = new Set(local.map((r) => r.id))
  const runs = [...local, ...published.filter((r) => !seen.has(r.id))]
  return { format: INDEX_FORMAT, runs: runs.sort(byCreatedAt) }
}

function sendJson(res, body) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8')
  res.setHeader('Cache-Control', 'no-store')
  res.end(body)
}

function serveRuns() {
  const handler = async (req, res) => {
    const rel = decodeURIComponent((req.url || '/').split('?')[0])
    if (rel === '/index.json') return sendJson(res, JSON.stringify(await devIndex()))
    for (const root of [RUNS_DIR, PUBLISHED_DIR]) {
      const file = path.resolve(root, '.' + rel)
      if (!file.startsWith(root + path.sep) || !file.endsWith('.json')) break
      try {
        return sendJson(res, await readFile(file))
      } catch {
        // 다음 폴더에서 찾는다
      }
    }
    res.statusCode = 404
    res.end()
  }
  return {
    name: 'serve-runs',
    configureServer(server) {
      server.middlewares.use('/runs', handler)
    },
    async generateBundle() {
      for (const rel of await listJson(PUBLISHED_DIR)) {
        if (!rel.includes('/')) continue // 실행 폴더 밖의 파일. index.json 은 아래에서 만든다
        this.emitFile({ type: 'asset', fileName: `runs/${rel}`, source: await readFile(path.join(PUBLISHED_DIR, rel)) })
      }
      const index = { format: INDEX_FORMAT, runs: (await publishedRuns()).sort(byCreatedAt) }
      this.emitFile({ type: 'asset', fileName: 'runs/index.json', source: JSON.stringify(index) })
    },
  }
}

export default defineConfig({
  plugins: [react(), serveRuns()],
  server: { port: 5180 },
})
