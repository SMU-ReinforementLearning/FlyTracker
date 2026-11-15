// issue 화면에 보일 초파리, 조준기, 조건을 실행들의 config.json 에서 뽑고, 비교 대상과 견준다.
// 실행에 남지 않는 것(실험 단계, 실험 이유, 학습한 모델의 버전 번호, 비교 대상 issue)은 published/issues/<번호>.json 에서 온다.
// 버전 번호는 README 의 대전표 규칙을 따른다. 사람이 짠 규칙인 규칙 초파리와 기준선이 v0 이다.
import { algoLabel } from './labels.js'

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
    text: '사람이 짠 규칙으로 움직이는 조준기다. 초파리가 보이면 화면 가운데로 오게 돌리고, 놓치면 마지막으로 본 쪽부터 넓혀 가며 찾는다.',
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
 */
function makeRow(label, items, { delta = true } = {}) {
  const seen = new Map()
  for (const it of items) if (it && !seen.has(it.text)) seen.set(it.text, it)
  const list = [...seen.values()]
  if (list.length === 0) return null
  if (list.every((it) => typeof it.num === 'number')) list.sort((a, b) => a.num - b.num)
  const one = delta && list.length === 1 && typeof list[0].num === 'number' ? list[0] : null
  return { label, value: list.map((it) => it.text).join(', '), one }
}

/** 실행 하나의 초파리와 조준기. 학습한 쪽이면 학습 설정도 함께 돌려준다. */
function sidesOf(cfg) {
  const algo = cfg.algo ?? {}
  const name = algo.name ?? cfg.policy ?? cfg.mode ?? null
  const ruleFly = { kind: cfg.env?.fly_model === 'neural' ? 'neural' : 'rule' }
  if (LEARNED.has(name)) {
    const self = { kind: 'learned', algo: name, steps: algo.steps, seed: algo.seed, frameStack: algo.frameStack }
    const opponent = algo.opponent
    if (algo.side === 'fly') {
      return { fly: self, aimer: !opponent || opponent === 'baseline' ? { kind: 'baseline' } : { kind: 'learned', model: opponent } }
    }
    return { fly: !opponent || opponent === 'rule' ? ruleFly : { kind: 'learned', model: opponent }, aimer: self }
  }
  if (name === 'rule-baseline') return { fly: ruleFly, aimer: { kind: 'baseline' } }
  if (name === 'free-flight') return { fly: ruleFly, aimer: { kind: 'none' } }
  return { fly: ruleFly, aimer: { kind: 'other', name: name ? algoLabel(name) : '알 수 없음' } }
}

const has = (v) => v !== undefined && v !== null

/** 같은 종류끼리 묶어 카드 한 장으로 만든다. */
function cardsOf(sides, table, versionLabel) {
  const groups = new Map()
  for (const s of sides) {
    const key = s.kind === 'other' ? `other:${s.name}` : s.kind
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(s)
  }
  return [...groups.entries()].map(([key, list]) => {
    const first = list[0]
    const base = table[first.kind] ?? { name: first.name }
    const rows =
      first.kind === 'learned'
        ? [
            makeRow('알고리즘', list.map((s) => (has(s.algo) ? item(algoLabel(s.algo)) : null))),
            makeRow('학습 길이', list.map((s) => (has(s.steps) ? qty(s.steps, ' step') : null))),
            makeRow('학습 seed', list.map((s) => (has(s.seed) ? item(String(s.seed), s.seed) : null)), { delta: false }),
            makeRow('함께 보는 최근 관측', list.map((s) => (has(s.frameStack) ? qty(s.frameStack, '개') : null))),
            makeRow('모델', list.map((s) => (has(s.model) ? item(s.model) : null))),
          ].filter(Boolean)
        : []
    return {
      key,
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

/** 비교 대상과 견줄 조건 줄. 실행마다 값이 다르면 쉼표로 나란히 적는다. */
function conditionsOf(configs) {
  const envs = configs.map((c) => c.env ?? {})
  return [
    makeRow('환경 버전', configs.map((c) => item(String(c.envVersion ?? 1)))),
    makeRow('포획 범위', envs.map((e) => within(captureRangeOf(e)))),
    makeRow('포획 유지 시간', envs.map((e) => (e.capture_enabled !== false && has(e.capture_hold) ? qty(e.capture_hold, '초') : null))),
    makeRow('포획 거리', envs.map((e) => (has(e.capture_range) ? within(qty(e.capture_range, 'm')) : null))),
    makeRow('에피소드 길이', envs.map((e) => (has(e.max_seconds) ? qty(e.max_seconds, '초', '최대 ') : null))),
    makeRow('방', envs.map((e) => (e.room ? item(`가로 ${fmtNum(e.room.width)}m, 높이 ${fmtNum(e.room.height)}m, 깊이 ${fmtNum(e.room.depth)}m`) : null))),
    makeRow('조준기 자리', envs.map((e) => turretOf(e.turret_pos))),
    makeRow('시야각', envs.map((e) => (has(e.camera?.fov_v_deg) ? qty(e.camera.fov_v_deg, '°', '세로 ') : null))),
    makeRow('위아래 조준 한계', envs.map((e) => (has(e.aimer?.max_pitch_deg) ? qty(e.aimer.max_pitch_deg, '°', '±') : null))),
    makeRow('시작 방향', envs.map((e) => (has(e.start_facing_fly) ? item(e.start_facing_fly ? '초파리 쪽' : '방 가운데 쪽') : null))),
  ].filter(Boolean)
}

/**
 * issue 화면의 초파리 카드, 조준기 카드, 조건 줄.
 * runs 는 index.json 의 실행, configs 는 같은 순서의 config.json(못 읽은 실행은 null), info 는 issue 설명 파일(없으면 null).
 * conditions 는 비교 대상과 견주는 줄이고, facts 는 이 issue 에만 있는 사실(기록 수, 설명 파일의 notes)이라 견주지 않는다.
 */
export function experimentOf(runs, configs, info) {
  const cfgs = configs.filter(Boolean)
  const sides = cfgs.map(sidesOf)
  const episodes = runs.reduce((sum, r) => sum + (r.episodeCount ?? 0), 0)
  const record = episodes ? `실행 ${runs.length}개, 에피소드 ${fmtNum(episodes)}개` : `실행 ${runs.length}개`
  const notes = (info?.notes ?? []).filter((n) => n && n.label && n.value).map((n) => ({ label: n.label, value: n.value }))
  return {
    fly: cardsOf(sides.map((s) => s.fly), FLY, info?.fly),
    aimer: cardsOf(sides.map((s) => s.aimer), AIMER, info?.aimer),
    conditions: conditionsOf(cfgs),
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

/** 학습 seed 를 뺀 config. 이 값이 같은 실행끼리 한 variation 이다. 학습 seed 만 다른 실행은 같은 설정을 되풀이한 것이다. */
function signatureOf(cfg) {
  const { algo = {}, ...rest } = cfg
  const { seed: _seed, ...algoRest } = algo
  return stableJson({ ...rest, algo: algoRest })
}

const SIDE_NAME = { fly: '초파리', aimer: '조준기' }

/** 화면에 나오는 값을 '자리 + 이름' key 로 편다. variation 끼리 무엇이 다른지 찾는 데 쓴다. */
function shownValues(exp) {
  const out = new Map()
  for (const side of ['fly', 'aimer']) {
    out.set(`${side}|${SIDE_NAME[side]}`, exp[side].map(cardTitle).join(', '))
    for (const card of exp[side]) for (const r of card.rows) if (r.label !== '학습 seed') out.set(`${side}|${r.label}`, r.value)
  }
  for (const r of exp.conditions) out.set(`조건|${r.label}`, r.value)
  return out
}

/**
 * issue 안의 variation. 학습 seed 만 다른 실행끼리 묶는다.
 * 돌려주는 것: { label, items: [{ key, label, runIds }] }. label 은 variation 끼리 다른 항목의 이름이고,
 * 항목 label 은 그 값이다(예: '함께 보는 최근 관측' 과 '1개', '4개'). variation 이 하나뿐이면 items 는 빈 목록이다.
 */
export function variationsOf(runs, configs) {
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
  if (list.length < 2) return { label: null, items: [] }
  const shown = list.map((g) => shownValues(experimentOf(g.runs, g.configs, null)))
  const keys = [...new Set(shown.flatMap((m) => [...m.keys()]))]
  const differing = keys.filter((k) => new Set(shown.map((m) => m.get(k) ?? '없음')).size > 1)
  const items = list.map((g, i) => ({
    key: g.runs[0].id,
    label: differing.length ? differing.map((k) => shown[i].get(k) ?? '없음').join(', ') : `설정 ${i + 1}`,
    runIds: g.runs.map((r) => r.id),
  }))
  items.sort((a, b) => a.label.localeCompare(b.label, 'ko', { numeric: true }))
  return { label: differing.length ? differing.map((k) => k.split('|')[1]).join(', ') : '설정', items }
}

/** 지금 실험(exp)을 비교 대상(prev)과 견준다. prev 가 없으면 exp 를 그대로 돌려준다. */
export function compareExperiments(exp, prev) {
  if (!prev) return exp
  return {
    ...exp,
    fly: diffCards(exp.fly, prev.fly),
    aimer: diffCards(exp.aimer, prev.aimer),
    conditions: diffRows(exp.conditions, prev.conditions),
  }
}
