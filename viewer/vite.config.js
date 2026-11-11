import { readdir, readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// 화면 코드는 에피소드를 늘 /runs 주소로 읽는다. 그 주소에 무엇을 내줄지는 여기서 정한다.
//   개발 서버: runs/(내 컴퓨터에서 만든 실행)와 published/(저장소에 올라온 실행)를 함께 내준다.
//   build: published/ 만 dist/runs/ 에 넣는다. Cloudflare 에 올라가는 것은 이것뿐이다.
// published/ 에는 index.json 이 없다. 실행마다 있는 run.json 을 모아 목록을 만든다(flytracker/record.py).
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

async function publishedRuns() {
  const runs = []
  for (const d of await dirents(PUBLISHED_DIR)) {
    if (!d.isDirectory() || d.name.startsWith('.')) continue
    const entry = await readJson(path.join(PUBLISHED_DIR, d.name, 'run.json'), null)
    if (entry) runs.push(entry)
  }
  return runs
}

const byCreatedAt = (a, b) => String(a.createdAt).localeCompare(String(b.createdAt))

/** 같은 id 가 양쪽에 있으면 runs/ 쪽을 쓴다. 파일도 runs/ 에서 먼저 찾는다. */
async function devIndex() {
  const local = (await readJson(path.join(RUNS_DIR, 'index.json'), { runs: [] })).runs
  const seen = new Set(local.map((r) => r.id))
  const runs = [...local, ...(await publishedRuns()).filter((r) => !seen.has(r.id))]
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
