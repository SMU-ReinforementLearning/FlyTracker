// 에피소드 JSON 을 재생하기 좋은 typed array 로 바꾸고, 임의 시각의 상태를 보간해 꺼낸다.
// 시간은 frames.t 로 맞춘다. 포획으로 끝난 마지막 프레임은 간격이 짧을 수 있다.

function flat3(rows) {
  const out = new Float32Array(rows.length * 3)
  rows.forEach((r, i) => out.set(r, i * 3))
  return out
}

// 기록은 native 몸 축(+X 앞,+Z 위)에서 tracker 월드로 가는 wxyz 자세다.
// 메시에는 이미 같은 좌표 변환 A가 적용되어 있어 q_world * inverse(A)를 쓴다.
export function meshQuaternion(q, out = [0, 0, 0, 1]) {
  const [w, x, y, z] = q
  out[0] = .5 * (w + x - y + z)
  out[1] = .5 * (-w + x + y + z)
  out[2] = .5 * (-w - x - y + z)
  out[3] = .5 * (w - x + y + z)
  return out
}

function attitudes(frames, n) {
  if (!frames.neuralDiagnostics) return null
  const values = new Float64Array(n * 4)
  frames.neuralDiagnostics.forEach((d, i) => {
    const q = d.quaternion
    if (!q || q.length !== 4 || !q.every(Number.isFinite) || Math.abs(Math.hypot(...q) - 1) > 1e-6)
      throw new Error('신경 기록의 자세 값이 올바르지 않습니다.')
    values.set(q, i * 4)
  })
  if (frames.neuralDiagnostics.length !== n) throw new Error('신경 자세와 프레임 수가 다릅니다.')
  return values
}

/** 초파리 진행 방향. 기록에 없으면(flyHeading 이 생기기 전 기록) 위치 차이로 만든다. */
function headings(f) {
  if (f.flyHeading) return flat3(f.flyHeading)
  const n = f.fly.length
  const out = new Float32Array(n * 3)
  let prev = [0, 0, -1]
  for (let i = 0; i < n; i++) {
    const a = f.fly[Math.max(i - 1, 0)]
    const b = f.fly[Math.min(i + 1, n - 1)]
    const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
    const len = Math.hypot(d[0], d[1], d[2])
    if (len > 1e-6) prev = [d[0] / len, d[1] / len, d[2] / len]
    out.set(prev, i * 3)
  }
  return out
}

export function prepareEpisode(raw) {
  const f = raw.frames
  const n = f.t.length
  const returns = new Float32Array(n)
  let acc = 0
  for (let i = 0; i < n; i++) {
    acc += f.reward[i]
    returns[i] = acc
  }
  const uv = new Float32Array(n * 2)
  f.uv.forEach((r, i) => uv.set(r, i * 2))
  return {
    meta: raw.meta,
    summary: raw.summary,
    n,
    duration: f.t[n - 1],
    t: Float64Array.from(f.t),
    fly: flat3(f.fly),
    heading: headings(f),
    attitude: attitudes(f, n),
    C: flat3(f.aimerC),
    look: flat3(f.aimerLook),
    uv,
    visible: Uint8Array.from(f.visible, Number),
    alarmed: Uint8Array.from(f.alarmed ?? f.evading, Number), // evading 은 이 필드가 생기기 전 기록
    capture: Float32Array.from(f.captureProgress),
    angle: Float32Array.from(f.angleErrDeg),
    distance: Float32Array.from(f.distance),
    speed: f.flySpeed ? Float32Array.from(f.flySpeed) : null,
    events: raw.diagnostics?.stimulus?.events ?? [],
    aimCommanded: f.aimCommanded ? Uint8Array.from(f.aimCommanded, Number) : null,
    phase: f.neuralPhase ?? null,
    normalRate: f.neuralDiagnostics ? Float32Array.from(f.neuralDiagnostics, (d) => d.normal_rate_hz) : null,
    escapeRate: f.neuralDiagnostics ? Float32Array.from(f.neuralDiagnostics, (d) => Math.max(d.dnp06_left_hz, d.dnp06_right_hz,
      d.extended_rates?.dnp03_left_hz ?? 0, d.extended_rates?.dnp03_right_hz ?? 0)) : null,
    saccadeRate: f.neuralDiagnostics?.some((d) => d.extended_rates) ? Float32Array.from(f.neuralDiagnostics,
      (d) => Math.max(d.extended_rates?.sgu_left_hz ?? 0, d.extended_rates?.sgu_right_hz ?? 0)) : null,
    wallInput: f.neuralDiagnostics?.some((d) => d.wall_sensory) ? Float32Array.from(f.neuralDiagnostics,
      (d) => Math.max(d.wall_sensory?.left ?? 0, d.wall_sensory?.right ?? 0)) : null,
    threatInput: f.neuralDiagnostics ? Float32Array.from(f.neuralDiagnostics, (d) => Math.max(d.left_input_hz, d.right_input_hz)) : null,
    returns,
  }
}

/** t 이하인 마지막 프레임 번호. */
export function frameAt(ep, t) {
  const ts = ep.t
  if (t <= ts[0]) return 0
  if (t >= ts[ep.n - 1]) return ep.n - 1
  let lo = 0
  let hi = ep.n - 1
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1
    if (ts[mid] <= t) lo = mid
    else hi = mid
  }
  return lo
}

function lerp3(arr, i, j, s, out) {
  for (let k = 0; k < 3; k++) out[k] = arr[i * 3 + k] + (arr[j * 3 + k] - arr[i * 3 + k]) * s
  return out
}

/** 위치와 방향은 보간하고, 상태 값은 직전 프레임 값을 쓴다. out 을 재사용해 프레임마다 메모리를 만들지 않는다. */
export function sample(ep, t, out) {
  const i = frameAt(ep, t)
  const j = Math.min(i + 1, ep.n - 1)
  const span = ep.t[j] - ep.t[i]
  const s = span > 0 ? Math.min(Math.max((t - ep.t[i]) / span, 0), 1) : 0
  lerp3(ep.fly, i, j, s, out.fly)
  lerp3(ep.heading, i, j, s, out.heading)
  const hl = Math.hypot(out.heading[0], out.heading[1], out.heading[2]) || 1
  out.heading[0] /= hl
  out.heading[1] /= hl
  out.heading[2] /= hl
  out.hasAttitude = ep.attitude !== null
  if (out.hasAttitude) {
    const a = ep.attitude
    let dot = 0
    for (let k = 0; k < 4; k++) dot += a[i * 4 + k] * a[j * 4 + k]
    const sign = dot < 0 ? -1 : 1
    const angle = Math.acos(Math.min(1, Math.abs(dot)))
    const sin = Math.sin(angle)
    const wa = sin > 1e-8 ? Math.sin((1 - s) * angle) / sin : 1 - s
    const wb = sin > 1e-8 ? Math.sin(s * angle) / sin : s
    for (let k = 0; k < 4; k++) out.attitude[k] = wa * a[i * 4 + k] + wb * sign * a[j * 4 + k]
    const norm = Math.hypot(...out.attitude)
    for (let k = 0; k < 4; k++) out.attitude[k] /= norm
    meshQuaternion(out.attitude, out.meshQuaternion)
  }
  lerp3(ep.C, i, j, s, out.C)
  lerp3(ep.look, i, j, s, out.look)
  const len = Math.hypot(out.look[0], out.look[1], out.look[2]) || 1
  out.look[0] /= len
  out.look[1] /= len
  out.look[2] /= len
  out.i = i
  out.visible = ep.visible[i] === 1
  out.alarmed = ep.alarmed[i] === 1
  out.capture = ep.capture[i]
  out.u = ep.uv[i * 2]
  out.v = ep.uv[i * 2 + 1]
  return out
}

export function newSample() {
  return { fly: [0, 0, 0], heading: [0, 0, -1], C: [0, 0, 0], look: [0, 0, -1],
    hasAttitude: false, attitude: [1, 0, 0, 0], meshQuaternion: [0, 0, 0, 1],
    i: 0, visible: false, alarmed: false, capture: 0, u: 0, v: 0 }
}
