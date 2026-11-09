// 에피소드 JSON 을 재생하기 좋은 typed array 로 바꾸고, 임의 시각의 상태를 보간해 꺼낸다.
// 시간은 frames.t 로 맞춘다. 포획으로 끝난 마지막 프레임은 간격이 짧을 수 있다.

function flat3(rows) {
  const out = new Float32Array(rows.length * 3)
  rows.forEach((r, i) => out.set(r, i * 3))
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
    C: flat3(f.aimerC),
    look: flat3(f.aimerLook),
    uv,
    visible: Uint8Array.from(f.visible, Number),
    alarmed: Uint8Array.from(f.alarmed ?? f.evading, Number), // evading 은 이 필드가 생기기 전 기록
    capture: Float32Array.from(f.captureProgress),
    angle: Float32Array.from(f.angleErrDeg),
    distance: Float32Array.from(f.distance),
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
  return { fly: [0, 0, 0], C: [0, 0, 0], look: [0, 0, -1], i: 0, visible: false, alarmed: false, capture: 0, u: 0, v: 0 }
}
