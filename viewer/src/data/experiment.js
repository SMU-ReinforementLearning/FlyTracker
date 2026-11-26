// issue 화면에 보일 초파리, 조준기, 환경을 실행들의 config.json 에서 뽑고, 비교 대상과 견준다.
// 줄마다 주인이 있다. 초파리의 비행과 감각은 초파리, 조준기의 몸과 화면은 조준기, 양쪽에 똑같이 적용되는 규칙은 환경이다.
// 실행에 남지 않는 것(실험 단계, 실험 이유, 학습한 모델의 버전 번호, 비교 대상 issue)은 published/issues/<번호>.json 에서 온다.
// 버전 번호는 README 의 대전표 규칙을 따른다. 사람이 짠 규칙인 규칙 초파리와 기준선이 v0 이다.
import { algoLabel, zoomLabel } from './labels.js'

const LEARNED = new Set(['sac', 'td3', 'ppo', 'dqn'])

const FLY = {
  rule: {
    name: '규칙 초파리',
    version: 'v0',
    text: '실제 초파리처럼 곧게 날다가 갑자기 방향을 튼다. 조준기 쪽으로 빠르게 다가가거나 아주 가까워지면 반대쪽으로 피하고, 조준기가 자기를 겨누는지는 모른다.',
  },
  neural: {
    name: '신경 초파리',
    text: '신경 회로 모델이 내는 신호로 날갯짓 힘을 계산해서 난다. 실제 초파리와 얼마나 비슷한지는 아직 확인하지 않았다.',
  },
  learned: {
    name: '학습한 초파리',
    text: '평소에는 규칙 초파리처럼 날고, 언제 어느 쪽으로 얼마나 빨리 피할지는 스스로 정한다. 조준 방향으로 나가는 초록 레이저를 보고 피한다.',
  },
}

const AIMER = {
  baseline: {
    name: '기준선',
    version: 'v0',
    text: '사람이 짠 규칙으로 움직이는 조준기다. 초파리가 보이면 따라 돌고, 놓치면 마지막으로 본 쪽부터 넓혀 가며 찾는다.',
  },
  learned: {
    name: '학습한 조준기',
    text: '자기 화면에 보이는 것만 보고 어느 쪽으로 돌릴지 스스로 정한다. 초파리를 빨리 포획할수록 보상을 많이 받도록 학습했다.',
  },
  none: {
    name: '조준기 없음',
    text: '조준기 없이 초파리가 나는 모습만 기록했다.',
  },
}

/** 화면에 적는 수. 1,000 이상의 정수는 자릿수를 끊고, 나머지는 소수 셋째 자리까지만 둔다. */
function fmtNum(v) {
  if (Number.isInteger(v) && Math.abs(v) >= 1000) return v.toLocaleString('ko-KR')
  return String(Number(v.toFixed(3)))
}

/** 줄에 들어갈 값 하나. num 과 unit 이 있으면 비교 대상과의 차이를 셀 수 있다. */
const item = (text, num = null, unit = '') => ({ text, num, unit })
const qty = (num, unit, prefix = '') => item(`${prefix}${fmtNum(num)}${unit}`, num, unit)

/**
 * 실행마다 하나씩 받은 값을 줄 하나로 만든다. 값이 다르면 쉼표로 나란히 적고, 숫자면 작은 것부터 둔다.
 * delta 가 false 인 줄(학습 seed 처럼 크기를 견줄 뜻이 없는 값)은 차이를 세지 않는다.
 * src 는 이 줄의 값이 config.json 의 어디에서 오는지다. 그 값을 바꾼 issue 를 찾는 데 쓴다(history.js).
 */
function makeRow(label, src, items, { delta = true } = {}) {
  const seen = new Map()
  for (const it of items) if (it && !seen.has(it.text)) seen.set(it.text, it)
  const list = [...seen.values()]
  if (list.length === 0) return null
  if (list.every((it) => typeof it.num === 'number')) list.sort((a, b) => a.num - b.num)
  const one = delta && list.length === 1 && typeof list[0].num === 'number' ? list[0] : null
  return { label, src, value: list.map((it) => it.text).join(', '), one }
}

/** 실행 하나의 초파리와 조준기. 학습한 쪽이면 학습 설정도 함께 돌려준다. */
function sidesOf(cfg) {
  const algo = cfg.algo ?? {}
  const name = algo.name ?? cfg.policy ?? cfg.mode ?? null
  const ruleFly = { kind: cfg.env?.fly_model === 'neural' ? 'neural' : 'rule' }
  // 기준선은 #45(환경 버전 4)부터 초파리 방향의 각속도에 맞춰 돈다. 그 전에는 조준 오차만 보고 돌았다.
  // 환경 버전 6(#69)부터 조준기가 쏜다. 기준선은 어림한 빔까지 거리가 포획 범위 안이면 쏜다.
  const baseline = { kind: 'baseline', tracking: (cfg.envVersion ?? 1) >= 4, fireRadius: (cfg.envVersion ?? 1) >= 6 ? (cfg.env?.capture_radius ?? null) : null }
  if (LEARNED.has(name)) {
    const self = {
      kind: 'learned',
      algo: name,
      steps: algo.steps,
      seed: algo.seed,
      frameStack: algo.frameStack,
      assist: algo.assist, // 초파리가 보이는 동안 기준선의 추적 행동에 더하는 정책 행동의 배율(#51). 0 이면 정책 혼자 조준한다
      model: algo.model, // 이미 학습한 모델을 다른 환경에서 돌린 실행(#44)이면 그 모델의 실행 id
      trainedEnv: algo.trainedEnvVersion,
      fire: algo.fire, // 쏠지를 누가 정하나(#72). 'rule' 이면 조준만 학습한 모델에 기준선의 쏘는 규칙을 붙인 것이다
      control: algo.control, // 정책의 돌리는 행동이 뜻하는 것(#88). 'rate' 는 각속도, 'accel' 은 각가속도. 그 전 실행에는 없고 각속도다
      aim: algo.aim, // 발사만 학습한 모델(#88)이면 조준을 맡은 모델의 실행 id
      firePrior: algo.firePrior, // 발사만 학습한 모델의 발사 값이 어디서 시작하나(#88). 'rule' 이면 기준선의 규칙
    }
    const opponent = algo.opponent
    if (algo.side === 'fly') {
      return { fly: self, aimer: !opponent || opponent === 'baseline' ? baseline : { kind: 'learned', model: opponent } }
    }
    return { fly: !opponent || opponent === 'rule' ? ruleFly : { kind: 'learned', model: opponent }, aimer: self }
  }
  if (name === 'rule-baseline') return { fly: ruleFly, aimer: baseline }
  if (name === 'free-flight') return { fly: ruleFly, aimer: { kind: 'none' } }
  return { fly: ruleFly, aimer: { kind: 'other', name: name ? algoLabel(name) : '알 수 없음' } }
}

const has = (v) => v !== undefined && v !== null

/** 같은 종류끼리 묶어 카드 한 장으로 만든다. */
function cardsOf(side, sides, table, versionLabel) {
  const groups = new Map()
  for (const s of sides) {
    const key = s.kind === 'other' ? `other:${s.name}` : s.kind
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(s)
  }
  return [...groups.entries()].map(([key, list]) => {
    const first = list[0]
    const base = table[first.kind] ?? { name: first.name }
    let rows = []
    if (first.kind === 'learned') {
      rows = [
        makeRow('알고리즘', 'algo.name', list.map((s) => (has(s.algo) ? item(algoLabel(s.algo)) : null))),
        makeRow('학습 길이', 'algo.steps', list.map((s) => (has(s.steps) ? qty(s.steps, ' step') : null))),
        makeRow('학습 seed', 'algo.seed', list.map((s) => (has(s.seed) ? item(String(s.seed), s.seed) : null)), { delta: false }),
        makeRow('함께 보는 최근 관측', 'algo.frameStack', list.map((s) => (has(s.frameStack) ? qty(s.frameStack, '개') : null))),
        makeRow('추적 보조', 'algo.assist', list.map((s) => (has(s.assist) ? item(s.assist > 0 ? `기준선 추적 + 행동 × ${fmtNum(s.assist)}` : '없음') : null))),
        makeRow('학습한 환경 버전', 'algo.trainedEnvVersion', list.map((s) => (has(s.trainedEnv) ? item(String(s.trainedEnv)) : null))),
        makeRow('돌리는 행동', 'algo.control', list.map((s) => (has(s.control) && !has(s.aim) ? item(s.control === 'accel' ? '각가속도' : '각속도') : null))), // 발사만 학습한 모델은 돌리지 않는다
        makeRow('쏘는 방식', 'algo.fire', list.map((s) => (has(s.fire) ? item(s.fire === 'rule' ? '기준선의 규칙' : s.firePrior === 'rule' ? '정책이 정함, 기준선의 규칙에서 시작' : '정책이 정함') : null))),
        makeRow('조준을 맡은 모델', 'algo.aim', list.map((s) => (has(s.aim) ? item(s.aim) : null))),
        makeRow('모델', 'algo.model', list.map((s) => (has(s.model) ? item(s.model) : null))),
      ].filter(Boolean)
    } else if (first.kind === 'baseline') {
      rows = [
        makeRow('따라가는 방식', 'baseline.tracking', list.map((s) => item(s.tracking ? '초파리 각속도에 맞춰 돌림' : '조준 오차만 보고 돌림'))),
        makeRow('쏘는 기준', 'baseline.fire', list.map((s) => (has(s.fireRadius) ? within(qty(s.fireRadius * 1000, 'mm', '빔까지 ')) : null))),
      ].filter(Boolean)
    }
    return {
      key,
      src: `${side}.${first.kind}`,
      name: base.name,
      version: base.version ?? (first.kind === 'learned' ? versionLabel : null) ?? null,
      text: base.text ?? null,
      rows,
    }
  })
}

function captureRangeOf(env) {
  if (env.capture_enabled === false) return item('포획 없음')
  if (has(env.capture_radius)) return qty(env.capture_radius * 1000, 'mm', '빔까지 ')
  if (has(env.capture_angle_deg)) return qty(env.capture_angle_deg, '°', '조준 방향 ')
  return null
}

/** '빔까지 1.25mm' 를 '빔까지 1.25mm 안' 으로. 수가 없는 값('포획 없음')은 그대로 둔다. */
const within = (it) => (it && it.num !== null ? { ...it, text: `${it.text} 안` } : it)

function turretOf(pos) {
  if (!Array.isArray(pos) || pos.length !== 3) return null
  const [x, y, z] = pos
  if (x === 0 && z === 0) return item(`바닥 가운데, 높이 ${fmtNum(y)}m`)
  return item(`x ${fmtNum(x)}m, 높이 ${fmtNum(y)}m, z ${fmtNum(z)}m`)
}

const ms = (sec, prefix = '') => qty(Number((sec * 1000).toFixed(3)), 'ms', prefix)

/** 환경 줄. 초파리와 조준기에 똑같이 적용되는 규칙이다. 실행마다 값이 다르면 쉼표로 나란히 적는다. */
function environmentOf(configs) {
  const envs = configs.map((c) => c.env ?? {})
  return [
    makeRow('환경 버전', 'envVersion', configs.map((c) => item(String(c.envVersion ?? 1)))),
    makeRow('방', 'env.room', envs.map((e) => (e.room ? item(`가로 ${fmtNum(e.room.width)}m, 높이 ${fmtNum(e.room.height)}m, 깊이 ${fmtNum(e.room.depth)}m`) : null))),
    makeRow('에피소드 길이', 'env.max_seconds', envs.map((e) => (has(e.max_seconds) ? qty(e.max_seconds, '초', '최대 ') : null))),
    makeRow('포획 범위', 'env.capture_radius', envs.map((e) => within(captureRangeOf(e)))),
    // 환경 버전 6부터 이 값은 한 발의 길이이고 조준기 줄에 나온다(aimerSettingsOf)
    makeRow('포획 유지 시간', 'env.capture_hold', configs.map((c) => ((c.envVersion ?? 1) < 6 && c.env?.capture_enabled !== false && has(c.env?.capture_hold) ? qty(c.env.capture_hold, '초') : null))),
    makeRow('포획 거리', 'env.capture_range', envs.map((e) => (has(e.capture_range) ? within(qty(e.capture_range, 'm')) : null))),
    makeRow('초파리 시작 거리', 'env.min_start_distance', envs.map((e) => (has(e.min_start_distance) ? item(`조준기에서 ${fmtNum(e.min_start_distance)}m 이상`, e.min_start_distance, 'm') : null))),
  ].filter(Boolean)
}

/** 조준기 줄. 조준기의 자리, 화면, 돌 수 있는 빠르기다. 기준선이든 학습한 조준기든 같은 값을 쓴다. */
function aimerSettingsOf(configs) {
  const envs = configs.map((c) => c.env ?? {})
  return [
    makeRow('조준기 자리', 'env.turret_pos', envs.map((e) => turretOf(e.turret_pos))),
    makeRow('시야각', 'env.camera.fov_v_deg', envs.map((e) => (has(e.camera?.fov_v_deg) ? qty(e.camera.fov_v_deg, '°', '세로 ') : null))),
    // 확대 화면은 조준기 화면의 가운데를 시야각 ÷ fine_error_deg 배로 키운 것이다(#45, 환경 버전 4부터)
    makeRow('확대 화면', 'env.fine_error_deg', envs.map((e) => (has(e.fine_error_deg) && has(e.camera?.fov_v_deg) ? item(zoomLabel(e.camera.fov_v_deg / e.fine_error_deg), e.camera.fov_v_deg / e.fine_error_deg, '배') : null))),
    makeRow('좌우 회전 속도', 'env.aimer.max_yaw_rate_deg', envs.map((e) => (has(e.aimer?.max_yaw_rate_deg) ? qty(e.aimer.max_yaw_rate_deg, '°/s', '최대 ') : null))),
    makeRow('위아래 회전 속도', 'env.aimer.max_pitch_rate_deg', envs.map((e) => (has(e.aimer?.max_pitch_rate_deg) ? qty(e.aimer.max_pitch_rate_deg, '°/s', '최대 ') : null))),
    makeRow('각가속도', 'env.aimer.max_ang_accel_deg', envs.map((e) => (has(e.aimer?.max_ang_accel_deg) ? qty(e.aimer.max_ang_accel_deg, '°/s²', '최대 ') : null))),
    makeRow('위아래 조준 한계', 'env.aimer.max_pitch_deg', envs.map((e) => (has(e.aimer?.max_pitch_deg) ? qty(e.aimer.max_pitch_deg, '°', '±') : null))),
    // 한 발의 길이. 레이저 장치의 값이라 조준기 줄에 둔다. config.json 에서는 env.capture_hold 에 있다(#69, #72)
    makeRow('한 발 길이', 'env.aimer.shot', configs.map((c) => ((c.envVersion ?? 1) >= 6 && c.env?.capture_enabled !== false && has(c.env?.capture_hold) ? qty(c.env.capture_hold, '초') : null))),
    makeRow('시작 방향', 'env.start_facing_fly', envs.map((e) => (has(e.start_facing_fly) ? item(e.start_facing_fly ? '초파리 쪽' : '방 가운데 쪽') : null))),
  ].filter(Boolean)
}

/**
 * 초파리 줄. 초파리 종류에 따라 쓰는 값이 달라서, 그 종류가 있는 실행에서만 뽑는다.
 * 규칙 초파리와 학습한 초파리는 같은 비행 값을 쓰고, 언제 피할지를 정하는 값은 규칙 초파리만 쓴다.
 * 신경 초파리는 비행 값을 쓰지 않고, 조준기가 겨눌 때 보여 주는 가상 자극의 값을 쓴다.
 */
function flySettingsOf(configs, sides) {
  const envOf = (...kinds) => configs.map((c, i) => (kinds.includes(sides[i].fly.kind) ? (c.env ?? {}) : null))
  const flight = envOf('rule', 'learned').map((e) => e?.fly ?? null)
  const rule = envOf('rule').map((e) => e?.fly ?? null)
  const learned = envOf('learned')
  const neural = envOf('neural')
  const stim = neural.map((e) => (e?.stimulus?.enabled ? e.stimulus : null))
  const profiles = { original: '기존 계수', 'zenodo29193-candidate13-experimental': '실측 보정 후보' }
  const weights = { original: '원래 가중치', baseline: '원래 가중치', final: '학습 가중치 후보' }
  return [
    makeRow('비행 속도', 'env.fly.speed', flight.map((f) => (f && has(f.speed_short) && has(f.speed_long) ? item(`평균 ${fmtNum(f.speed_short)}~${fmtNum(f.speed_long)}m/s`) : null))),
    makeRow('급선회 각도', 'env.fly.saccade_mean_deg', flight.map((f) => (f && has(f.saccade_mean_deg) ? qty(f.saccade_mean_deg, '°', '평균 ') : null))),
    makeRow('급선회 시간', 'env.fly.saccade_duration_mean', flight.map((f) => (f && has(f.saccade_duration_mean) ? ms(f.saccade_duration_mean, '평균 ') : null))),
    makeRow('위협을 느끼는 거리', 'env.fly.evade_radius', rule.map((f) => (f && has(f.evade_radius) ? within(qty(f.evade_radius, 'm')) : null))),
    makeRow('무조건 피하는 거리', 'env.fly.evade_proximity', rule.map((f) => (f && has(f.evade_proximity) ? within(qty(f.evade_proximity, 'm')) : null))),
    makeRow('반응 지연', 'env.fly.evade_reaction', rule.map((f) => (f && has(f.evade_reaction) ? ms(f.evade_reaction) : null))),
    makeRow('피할 때 속도', 'env.fly.evade_speed_gain', flight.map((f) => (f && has(f.evade_speed_gain) ? qty(f.evade_speed_gain, '배', '최대 ') : null))),
    makeRow('관측 지연', 'env.fly_reaction_delay', learned.map((e) => (e && has(e.fly_reaction_delay) ? ms(e.fly_reaction_delay) : null))),
    makeRow('비행계수', 'env.neural.profile_id', neural.map((e) => {
      const label = profiles[e?.neural?.profile_id]
      return label ? item(label) : null
    })),
    makeRow('신경 가중치', 'evaluation.flyWeights', configs.map((c, i) => {
      const label = neural[i] && weights[c.evaluation?.flyWeights]
      return label ? item(label) : null
    })),
    makeRow('자극', 'env.stimulus.enabled', neural.map((e) => (e?.stimulus && has(e.stimulus.enabled) ? item(e.stimulus.enabled ? '켬' : '끔') : null))),
    makeRow('자극을 주는 조준 오차', 'env.stimulus.align_deg', stim.map((t) => (t && has(t.align_deg) ? within(qty(t.align_deg, '°')) : null))),
    makeRow('자극 전 조준 시간', 'env.stimulus.charge_ms', stim.map((t) => (t && has(t.charge_ms) ? qty(t.charge_ms, 'ms') : null))),
    makeRow('자극 길이', 'env.stimulus.pulse_ms', stim.map((t) => (t && has(t.pulse_ms) ? qty(t.pulse_ms, 'ms') : null))),
    makeRow('자극 사이 쉬는 시간', 'env.stimulus.cooldown_ms', stim.map((t) => (t && has(t.cooldown_ms) ? qty(t.cooldown_ms, 'ms') : null))),
    makeRow('자극 횟수', 'env.stimulus.max_events', stim.map((t) => (t && has(t.max_events) ? qty(t.max_events, '회', '최대 ') : null))),
  ].filter(Boolean)
}

// 조준기 보상의 가중치. config.json 의 env.reward 에 있는 항목이고, 뜻은 flytracker/env.py 의 RewardWeights 주석에 있다.
const AIMER_REWARD = [
  ['time', '시간 벌점', ''],
  ['beam', '빔까지 거리 벌점', ''],
  ['beam_far', '빔 벌점이 가장 큰 거리', 'm'],
  ['angle', '조준 오차 벌점', ''],
  ['lost', '놓쳤을 때 벌점', ''],
  ['action_change', '행동 변화 벌점', ''],
  ['capture', '포획 보상', ''],
  ['misfire', '오발 벌점', ''], // 오발 한 발마다 한 번 뺀다. 기본값은 0 이다(#88)
]

// 학습한 초파리 보상의 가중치. env.fly_reward 에 있고, 조준기 보상의 부호를 뒤집은 값이라 벌점이 보상으로 바뀐다(FlyRewardWeights).
const FLY_REWARD = [
  ['time', '버틴 시간 보상', ''],
  ['beam', '빔까지 거리 보상', ''],
  ['angle', '조준 오차 보상', ''],
  ['lost', '조준기가 놓쳤을 때 보상', ''],
  ['capture', '포획 벌점', ''],
]

/** 보상 가중치 줄. 아는 항목은 table 순서로, 모르는 항목은 key 그대로 뒤에 둔다. weights 에서 null 인 실행은 건너뛴다. */
function rewardsOf(weights, table, src) {
  const known = new Set(table.map(([k]) => k))
  const extra = [...new Set(weights.flatMap((w) => Object.keys(w ?? {})))].filter((k) => !known.has(k)).map((k) => [k, k, ''])
  return [...table, ...extra]
    .map(([key, label, unit]) => makeRow(label, `${src}.${key}`, weights.map((w) => (w && typeof w[key] === 'number' ? qty(w[key], unit) : null))))
    .filter(Boolean)
}

/**
 * issue 화면의 초파리 칸, 조준기 칸, 환경 줄.
 * runs 는 index.json 의 실행, configs 는 같은 순서의 config.json(못 읽은 실행은 null), info 는 issue 설명 파일(없으면 null).
 * 칸마다 종류별 카드(cards), 설정 줄(settings), 보상 줄(rewards)이 있다. 초파리 보상은 학습한 초파리가 있는 실행에서만,
 * 조준기 설정과 보상은 조준기가 있는 실행에서만 뽑는다. 규칙 초파리와 신경 초파리는 보상을 쓰지 않는다.
 * environment 는 비교 대상과 견주는 줄이고, facts 는 이 issue 에만 있는 사실(기록 수, 설명 파일의 notes)이라 견주지 않는다.
 * envVersion 은 실행들의 환경 버전 가운데 가장 큰 값이다. 줄의 값을 바꾼 issue 를 찾을 때 쓴다.
 */
export function experimentOf(runs, configs, info) {
  const cfgs = configs.filter(Boolean)
  const sides = cfgs.map(sidesOf)
  const episodes = runs.reduce((sum, r) => sum + (r.episodeCount ?? 0), 0)
  const record = episodes ? `실행 ${runs.length}개, 에피소드 ${fmtNum(episodes)}개` : `실행 ${runs.length}개`
  const notes = (info?.notes ?? []).filter((n) => n && n.label && n.value).map((n) => ({ label: n.label, value: n.value }))
  const withAimer = cfgs.filter((_, i) => sides[i].aimer.kind !== 'none')
  return {
    envVersion: Math.max(1, ...cfgs.map((c) => c.envVersion ?? 1)),
    fly: {
      cards: cardsOf('fly', sides.map((s) => s.fly), FLY, info?.fly),
      settings: flySettingsOf(cfgs, sides),
      rewards: rewardsOf(cfgs.map((c, i) => (sides[i].fly.kind === 'learned' ? (c.env?.fly_reward ?? null) : null)), FLY_REWARD, 'env.fly_reward'),
    },
    aimer: {
      cards: cardsOf('aimer', sides.map((s) => s.aimer), AIMER, info?.aimer),
      settings: aimerSettingsOf(withAimer),
      rewards: rewardsOf(withAimer.map((c) => c.env?.reward ?? null), AIMER_REWARD, 'env.reward'),
    },
    environment: environmentOf(cfgs),
    facts: [{ label: '기록', value: record }, ...notes],
  }
}

export const cardTitle = (card) => (card.version ? `${card.name} ${card.version}` : card.name)

/** 비교 대상의 값과 지금 값의 차이. 둘 다 같은 단위의 수일 때만 센다. */
function deltaOf(prev, cur) {
  if (!prev.one || !cur.one || prev.one.unit !== cur.one.unit) return null
  const d = Number((cur.one.num - prev.one.num).toFixed(6))
  if (d === 0) return null
  return `${d > 0 ? '+' : '−'}${fmtNum(Math.abs(d))}${cur.one.unit}`
}

/** 줄마다 비교 대상의 값(prev)과 차이(delta)를 붙인다. 비교 대상에 없던 줄과 지금 없어진 줄은 '없음'으로 적는다. */
function diffRows(rows, prevRows) {
  const prevBy = new Map(prevRows.map((r) => [r.label, r]))
  const out = rows.map((r) => {
    const p = prevBy.get(r.label)
    if (!p) return { ...r, prev: '없음' }
    return p.value === r.value ? r : { ...r, prev: p.value, delta: deltaOf(p, r) }
  })
  for (const p of prevRows) if (!rows.some((r) => r.label === p.label)) out.push({ label: p.label, value: '없음', prev: p.value })
  return out
}

/**
 * 설정 줄과 보상 줄을 견준다. 한쪽에 그 칸이 아예 없으면 견주지 않는다.
 * 규칙 초파리끼리 견주다가 학습한 초파리가 나오면 보상 줄이 모두 '없음 → 값'이 되는데, 그것은 값이 바뀐 것이 아니다.
 */
const diffSection = (rows, prevRows) => (rows.length && prevRows.length ? diffRows(rows, prevRows) : rows)

/**
 * 카드마다 비교 대상과 견준 결과를 붙인다.
 * was 는 '비교 대상' 줄에 적을 값이다. 종류나 버전이 바뀌었으면 비교 대상 카드 이름, 다 같으면 '같음',
 * 종류는 같고 설정만 바뀌었으면 null(바뀐 줄이 저마다 비교 대상의 값을 보여 준다).
 */
function diffCards(cards, prevCards) {
  const prevTitles = prevCards.map(cardTitle).join(', ') || '없음'
  return cards.map((c) => {
    const p = prevCards.find((x) => x.key === c.key)
    if (!p) return { ...c, was: prevTitles, changed: true }
    const rows = diffRows(c.rows, p.rows)
    if ((p.version ?? '') !== (c.version ?? '')) return { ...c, rows, was: cardTitle(p), changed: true }
    const changed = rows.some((r) => r.prev !== undefined)
    return { ...c, rows, was: changed ? null : '같음', changed }
  })
}

/** key 순서와 상관없이 같은 값이면 같은 글이 되도록 JSON 으로 적는다. */
function stableJson(v) {
  if (Array.isArray(v)) return `[${v.map(stableJson).join(',')}]`
  if (v && typeof v === 'object') return `{${Object.keys(v).sort().map((k) => `${JSON.stringify(k)}:${stableJson(v[k])}`).join(',')}}`
  return JSON.stringify(v)
}

/**
 * 학습 seed 를 뺀 config. 이 값이 같은 실행끼리 한 조합이다. 학습 seed 만 다른 실행은 같은 설정을 되풀이한 것이다.
 * 이미 학습한 모델을 다시 돌린 실행의 모델 id(algo.model)도 뺀다. 학습 seed 만 다른 모델은 id 만 다르다.
 */
function signatureOf(cfg) {
  const { algo = {}, ...rest } = cfg
  const { seed: _seed, model: _model, ...algoRest } = algo
  return stableJson({ ...rest, algo: algoRest })
}

const SIDE_NAME = { fly: '초파리', aimer: '조준기' }

/** 화면에 나오는 값을 '자리 + 이름' key 로 편다. 조합끼리 무엇이 다른지 찾는 데 쓴다. */
function shownValues(exp) {
  const out = new Map()
  for (const side of ['fly', 'aimer']) {
    out.set(`${side}|${SIDE_NAME[side]}`, exp[side].cards.map(cardTitle).join(', '))
    for (const card of exp[side].cards) for (const r of card.rows) if (r.label !== '학습 seed') out.set(`${side}|${r.label}`, r.value)
    for (const r of exp[side].settings) out.set(`${side} 설정|${r.label}`, r.value)
    for (const r of exp[side].rewards) out.set(`${side} 보상|${r.label}`, r.value)
  }
  for (const r of exp.environment) out.set(`환경|${r.label}`, r.value)
  return out
}

const NONE = '없음'

// 조합 표의 칸마다 그 칸에 드는 줄의 key 머리. 초파리와 조준기는 카드의 줄, 설정, 보상이고 환경은 환경 줄이다.
const COLUMNS = [
  { key: 'fly', title: 'fly|초파리', prefixes: ['fly|', 'fly 설정|', 'fly 보상|'] },
  { key: 'aimer', title: 'aimer|조준기', prefixes: ['aimer|', 'aimer 설정|', 'aimer 보상|'] },
  { key: 'environment', title: '환경|환경 버전', prefixes: ['환경|'] },
]

/**
 * issue 안의 조합. 학습 seed 만 다른 실행끼리 한 조합으로 묶고, 조합마다 초파리, 조준기, 환경을 늘 같은 칸에 적는다.
 * 돌려주는 것: [{ key, letter, fly, aimer, environment, runs }]. 설정을 읽은 실행이 없으면 빈 목록이다.
 * letter 는 표에서 그 줄을 부르는 글자다(A, B, C). 줄 순서대로 붙이므로 실행이 새로 올라오면 바뀔 수 있다.
 * fly, aimer, environment 는 { title, details: [{ label, value }] } 이다. title 은 종류와 버전이고(규칙 초파리 v0, 학습한 조준기 v1, 버전 6),
 * details 는 title 이 같은 조합끼리 값이 다른 줄이다(자극 켬과 끔, 돌리는 행동). 다른 조합과 같은 줄은 적지 않는다.
 * 한쪽에만 있는 줄(자극을 껐을 때 사라지는 자극 길이)은 값이 서로 다른 줄이 따로 있으면 적지 않는다. 그 줄이 이미 둘을 가른다.
 * runs 는 [{ id, seed }] 이고, seed 는 조합 안에서 실행을 가르는 학습 seed 다. 학습 seed 로 가를 수 없으면 null 이다.
 * 순서는 조준기, 초파리, 환경의 글자 순서다. 기준선이 학습한 조준기보다, 규칙 초파리가 신경 초파리보다 앞에 온다.
 */
export function combinationsOf(runs, configs, info) {
  const groups = new Map()
  runs.forEach((run, i) => {
    const cfg = configs[i]
    if (!cfg) return
    const sig = signatureOf(cfg)
    if (!groups.has(sig)) groups.set(sig, { runs: [], configs: [] })
    groups.get(sig).runs.push(run)
    groups.get(sig).configs.push(cfg)
  })
  const list = [...groups.values()]
  const shown = list.map((g) => shownValues(experimentOf(g.runs, g.configs, info)))
  const keys = [...new Set(shown.flatMap((m) => [...m.keys()]))]
  // 줄이 없는 것과 값이 '없음'인 것(추적 보조 없음)은 다르다. 없는 줄은 undefined 로 두고, 적을 때만 '없음'으로 바꾼다.
  const valueOf = (i, k) => shown[i].get(k)

  const cellOf = (i, col) => {
    const same = list.map((_, j) => j).filter((j) => valueOf(j, col.title) === valueOf(i, col.title))
    // 모델 id 는 학습 seed 처럼 조합 안의 실행을 가르는 값이라 뺀다(signatureOf)
    const mine = keys.filter((k) => k !== col.title && k !== 'aimer|모델' && k !== 'fly|모델' && col.prefixes.some((p) => k.startsWith(p)))
    const real = (k) => new Set(same.map((j) => valueOf(j, k)).filter((v) => v !== undefined))
    const differing = mine.filter((k) => new Set(same.map((j) => valueOf(j, k))).size > 1)
    const valued = differing.filter((k) => real(k).size > 1)
    const details = (valued.length ? valued : differing).map((k) => ({ label: k.split('|')[1], value: valueOf(i, k) ?? NONE }))
    const title = col.key === 'environment' ? `버전 ${valueOf(i, col.title)}` : (valueOf(i, col.title) ?? NONE)
    return { title, details }
  }

  const rows = list.map((g, i) => {
    const seeds = g.configs.map((c) => c.algo?.seed ?? null)
    const named = g.runs.length > 1 && seeds.every((s) => s !== null) && new Set(seeds).size === g.runs.length
    const cells = Object.fromEntries(COLUMNS.map((col) => [col.key, cellOf(i, col)]))
    return { key: g.runs[0].id, ...cells, runs: g.runs.map((r, k) => ({ id: r.id, seed: named ? seeds[k] : null })) }
  })
  const order = (row) => [row.aimer, row.fly, row.environment].map(cellText).join(' | ')
  rows.sort((a, b) => order(a).localeCompare(order(b), 'ko', { numeric: true }))
  return rows.map((row, i) => ({ ...row, letter: letterOf(i) }))
}

/** 표에서 줄을 부르는 글자. 0 은 A, 25 는 Z, 26 은 AA 다. 숫자는 학습 seed 나 버전과 헷갈려서 쓰지 않는다. */
function letterOf(i) {
  let s = ''
  for (let n = i; n >= 0; n = Math.floor(n / 26) - 1) s = String.fromCharCode(65 + (n % 26)) + s
  return s
}

/** 조합 안에서 실행을 부르는 이름. 학습 seed 로 가를 수 있으면 '학습 seed 0', 아니면 null 이다. */
export const seedLabel = (seed) => (seed === null || seed === undefined ? null : `학습 seed ${seed}`)

/** 조합의 칸 하나를 한 줄 글로. '신경 초파리, 자극 켬' 처럼 종류 뒤에 다른 줄을 쉼표로 잇는다. */
export const cellText = (cell) => [cell.title, ...cell.details.map((d) => `${d.label} ${d.value}`)].join(', ')

/** 지금 실험(exp)을 비교 대상(prev)과 견준다. prev 가 없으면 exp 를 그대로 돌려준다. */
export function compareExperiments(exp, prev) {
  if (!prev) return exp
  const side = (cur, old) => ({
    cards: diffCards(cur.cards, old.cards),
    settings: diffSection(cur.settings, old.settings),
    rewards: diffSection(cur.rewards, old.rewards),
  })
  return {
    ...exp,
    fly: side(exp.fly, prev.fly),
    aimer: side(exp.aimer, prev.aimer),
    environment: diffRows(exp.environment, prev.environment),
  }
}
