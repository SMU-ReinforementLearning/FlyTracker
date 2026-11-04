import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// 저장소 루트의 runs/ 를 /runs 로 연다. Python 이 쓴 파일을 서버 없이 그대로 읽기 위해서다.
const RUNS_DIR = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..', 'runs')

function serveRuns() {
  const handler = async (req, res, next) => {
    const rel = decodeURIComponent((req.url || '/').split('?')[0])
    const file = path.resolve(RUNS_DIR, '.' + rel)
    if (!file.startsWith(RUNS_DIR + path.sep) || !file.endsWith('.json')) {
      res.statusCode = 404
      return res.end()
    }
    try {
      const body = await readFile(file)
      res.setHeader('Content-Type', 'application/json; charset=utf-8')
      res.setHeader('Cache-Control', 'no-store')
      res.end(body)
    } catch {
      res.statusCode = 404
      res.end()
    }
  }
  return {
    name: 'serve-runs',
    configureServer(server) {
      server.middlewares.use('/runs', handler)
    },
    configurePreviewServer(server) {
      server.middlewares.use('/runs', handler)
    },
  }
}

export default defineConfig({
  plugins: [react(), serveRuns()],
  server: { port: 5180 },
})
