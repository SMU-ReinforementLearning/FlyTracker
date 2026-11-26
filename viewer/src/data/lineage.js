// 계보 화면의 자료. issue 가 어느 영역의 일이고 어느 issue 에서 이어졌는지를 손으로 적는다.
// 실행을 올리지 않은 issue(#1, #7 처럼 코드만 바꾼 것)도 흐름에 들어가야 해서 published/issues 가 아니라 여기에 둔다.
// 흐름에 넣을 issue 를 merge 할 때 한 줄을 더한다. 제목, 올린 사람, merge 날짜는 history.js 의 ISSUES 에서 온다.
import { issueOf } from './history.js'

export const LANES = [
  { key: 'fly', name: '초파리' },
  { key: 'aimer', name: '조준기' },
  { key: 'environment', name: '환경' },
]

// lane 은 그 issue 가 주로 바꾼 영역, also 는 함께 바꾼 다른 영역이다.
// parents 는 이어받은 issue 다. 설명 파일의 compare(견줄 대상)와는 뜻이 다르다.
// name 은 그 issue 에서 무엇이 어떻게 바뀌었는지를 적은 짧은 이름이다. 15자 안쪽으로 쓴다.
// 계보의 노드, 사이드바의 묶음, issue 화면의 제목이 모두 이 이름을 쓴다. GitHub 의 issue 제목은 마우스를 올리면 나온다.
// 설명 파일의 phase(실험 단계)와는 다른 것이다. phase 는 실험 계획에서의 자리이고 name 은 바뀐 내용이다.
// result 는 그 issue 에서 달라진 것이나 잰 결과 한두 문장이다. 한다체로 쓴다.
// 그 문장은 노드에 마우스를 올리면 나온다. 노드에 늘 보이는 것은 아래 버전, change, metric 이다.
// envVersion 은 그 issue 가 환경 버전을 올렸을 때만 적는다.
// aimerVersion 은 그 issue 에서 조준기 버전이 정해졌을 때만 적는다. v0 은 기준선이고, 지금의 기준선 동작이 나온 #45 에 적는다.
// fly 는 그 issue 에서 초파리 종류가 계보에 처음 나올 때만 적는다. 값은 용어집의 표기다(규칙 초파리, 신경 초파리).
// 셋 가운데 하나라도 있는 노드는 크게 그린다.
// change 는 바뀐 값 하나다. { what: 무엇이, from: 전(없으면 뺀다), to: 후 }. 값이 바뀌지 않은 issue 에는 적지 않는다.
// metric 은 그 issue 에서 잰 수치다. result 에 있는 숫자만 옮긴다. 포획 5/200 은 에피소드 200개 가운데 5개를 포획했다는 뜻이다.
const NODES = {
  59: {
    lane: 'fly',
    also: ['aimer'],
    parents: [31, 64, 72],
    name: '실측 보정과 신경 학습',
    result: '실측 자료로 비행계수를 보정하고, 학습용 조준기를 고정해 신경회로를 학습했다. 배율 후보는 바닥 보정이 늘어 채택하지 않았다.',
  },

  1: {
    lane: 'environment',
    parents: [],
    name: '첫 환경과 viewer',
    result: '초파리와 조준기가 겨루는 방과 에피소드 기록을 처음 만들었다.',
    envVersion: 1,
  },
  4: {
    lane: 'fly',
    parents: [1],
    name: '다가올 때만 회피',
    result: '조준 방향에 반응하던 것을 빼고, 다가오는 것만 피하게 했다.',
    fly: '규칙 초파리',
    change: { what: '회피', from: '조준 방향에도 반응', to: '다가올 때만 반응' },
  },
  7: {
    lane: 'aimer',
    parents: [1],
    name: '위치 고정, 방향만 회전',
    result: '조준기가 자리를 옮기지 못하고 방향만 돌리게 했다.',
    change: { what: '조준기 자리', from: '날아다님', to: '고정' },
  },
  9: {
    lane: 'fly',
    also: ['aimer'],
    parents: [4],
    name: '문헌값 속도와 급선회',
    result: '속도와 급선회를 실제 초파리 측정값에 맞췄다. 기준선에는 놓친 초파리를 찾는 동작을 넣었다.',
    change: { what: '비행', to: '직선 285~356mm/s, 급선회 93°' },
  },
  22: {
    lane: 'aimer',
    parents: [7],
    name: '기준선 기록 첫 공개',
    result: '기준선 에피소드 5개를 저장소에 처음 올렸다.',
  },
  34: {
    lane: 'environment',
    also: ['fly'],
    parents: [1],
    name: '초파리 학습 자리 추가',
    result: '학습한 초파리가 들어갈 자리를 만들고, 위아래 조준 한계를 89°로 늘렸다.',
    envVersion: 2,
    change: { what: '위아래 조준 한계', from: '80°', to: '89°' },
  },
  35: {
    lane: 'aimer',
    parents: [22, 34],
    name: 'SAC 조준기 첫 학습',
    result: 'SAC로 학습한 조준기가 기준선보다 두 배쯤 빨리 포획했다. 평균 2.18초와 2.12초이고 기준선은 4.10초다.',
    metric: '평균 2.18초, 2.12초 · 기준선 4.10초',
  },
  31: {
    lane: 'fly',
    parents: [],
    name: '신경 초파리 추가',
    result: '신경 회로가 날개 힘을 내는 초파리를 더하고, 관찰 기록 셋을 올렸다.',
    fly: '신경 초파리',
  },
  42: {
    lane: 'environment',
    parents: [34],
    name: '포획을 레이저 명중으로',
    result: '포획을 빔까지 1.25mm 안에 0.15초로 바꿨다. 기준선은 200개 가운데 5개만 포획했다.',
    envVersion: 3,
    change: { what: '포획 조건', from: '조준 오차 3° 안 0.2초', to: '빔까지 1.25mm 안 0.15초' },
    metric: '기준선 포획 5/200',
  },
  44: {
    lane: 'aimer',
    parents: [35, 42],
    name: '레이저 포획에서 SAC 실패',
    result: '환경 버전 2에서 학습한 모델은 8개 가운데 하나도 포획하지 못했다. 실행은 #42에 함께 있다.',
    metric: '포획 0/8',
  },
  45: {
    lane: 'aimer',
    parents: [42],
    name: '기준선을 각속도 추적으로',
    result: '초파리 방향의 각속도에 맞춰 돌게 했다. 200개를 모두 포획했고 평균 4.95초다.',
    envVersion: 4,
    aimerVersion: 'v0',
    change: { what: '기준선 회전', from: '조준 오차만큼', to: '초파리 각속도를 더해' },
    metric: '포획 200/200 · 평균 4.95초',
  },
  49: {
    lane: 'aimer',
    parents: [45],
    name: '벌점을 빔까지 거리로',
    result: '초파리가 보일 때 받는 벌점을 조준 오차에서 빔까지 거리로 바꿨다. 이 보상으로 학습한 조준기는 아직 없었다.',
    envVersion: 5,
    change: { what: '보일 때 벌점', from: '조준 오차', to: '빔까지 거리' },
  },
  51: {
    lane: 'aimer',
    parents: [49],
    name: '추적 보조로 SAC 재학습',
    result: '빔까지 거리 벌점에 추적 보조를 붙인 조건만 기준선보다 빨랐다. 평균 2.94초이고 기준선은 4.86초다.',
    metric: '평균 2.94초 · 기준선 4.86초',
  },
  64: {
    lane: 'fly',
    parents: [31],
    name: '신경 초파리 코드 포함',
    result: '신경 초파리를 돌리는 코드와 신경 자료를 저장소에 넣었다.',
  },
  61: {
    lane: 'aimer',
    parents: [51, 64],
    name: '신경 초파리와 SAC 대결',
    result: '에피소드 24개 가운데 23개를 포획했다. seed가 3개뿐이라 견줄 근거는 되지 않는다.',
    metric: '포획 23/24',
  },
  69: {
    lane: 'environment',
    also: ['aimer'],
    parents: [42],
    name: '레이저 한 발씩 쏘기',
    result: '쏠 때만 레이저를 켜고 오발을 센다. 기준선은 200개 가운데 198개를 잡았고, 에피소드마다 0.50발이 오발이다.',
    envVersion: 6,
    change: { what: '레이저', from: '늘 켜짐', to: '쏠 때만 켜짐' },
    metric: '기준선 포획 198/200 · 오발 0.50발',
  },
  72: {
    lane: 'aimer',
    parents: [61, 69],
    name: '조준은 SAC, 쏘기는 규칙',
    result: 'SAC 모델이 조준하고 기준선의 규칙이 쏘는 조준기를 v1로 정했다. 평균 3.03초이고 기준선은 4.89초다.',
    aimerVersion: 'v1',
    metric: '평균 3.03초 · 기준선 4.89초',
  },
  88: {
    lane: 'aimer',
    parents: [72],
    name: '정책 행동을 각가속도로',
    result: '정책이 각가속도를 내게 하자 추적 보조 없이도 조준했다. 쏘기는 규칙에 맡겼고 평균 2.61초다. 쏘는 것까지 학습한 조건은 규칙보다 빠르지 않았다.',
    change: { what: '정책의 돌리는 행동', from: '각속도', to: '각가속도' },
    metric: '평균 2.61초 · 기준선 4.89초',
  },
}

/** issue 를 화면에서 부르는 이름. 계보에 없는 issue 는 GitHub 의 issue 제목으로 부른다. issue 는 { number, title } 이다. */
export const issueName = (issue) => NODES[issue.number]?.name ?? issue.title

/** issue 가 주로 바꾼 영역의 key. 계보에 없는 issue 는 null. */
export const laneOf = (number) => NODES[number]?.lane ?? null

const laneName = (key) => LANES.find((l) => l.key === key)?.name ?? key

/** '2026-11-15' 를 '11월 15일' 로. */
const dayLabel = (iso) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return iso
  const [, m, d] = iso.split('-').map(Number)
  return `${m}월 ${d}일`
}

/** 노드에 붙는 버전 표시. 그 노드의 영역 것이 맨 앞에 온다. */
function badgesOf(node) {
  const badges = [
    node.fly && { lane: 'fly', text: node.fly },
    node.aimerVersion && { lane: 'aimer', text: `조준기 ${node.aimerVersion}` },
    node.envVersion != null && { lane: 'environment', text: `환경 버전 ${node.envVersion}` },
  ].filter(Boolean)
  return badges.sort((a, b) => (b.lane === node.lane) - (a.lane === node.lane))
}

/**
 * 계보에 그릴 노드와 선.
 * 노드: { number, lane(0부터), row(0부터), name, result, title, author, date, url, envVersion, also: [영역 이름], parents,
 *         badges: [{ lane(영역 key), text }], major(버전 표시가 있다), change: { what, from, to } | null, metric | null }.
 * 선: { from, to } (issue 번호). 표에 없는 issue 를 가리키는 parents 는 버린다.
 * marks: 다른 영역의 노드가 올린 버전을 제 영역의 줄에 놓는 표식. { lane(0부터), row, text, number(올린 issue) }.
 *        #45 는 조준기 영역이지만 환경 버전 4 를 올렸으므로, 환경 영역의 같은 줄에 "환경 버전 4" 가 놓인다. 영역만 내려 읽어도 버전이 이어진다.
 * current: 영역마다 지금 상태. LANES 와 같은 순서다. 환경은 가장 높은 환경 버전, 조준기는 마지막 조준기 버전, 초파리는 종류들이다.
 *
 * 줄은 위에서 아래로 시간 순서다. 늦게 merge 된 issue 는 먼저 merge 된 issue 보다 위에 오지 않고,
 * 이어받은 issue 와 같은 영역의 앞 issue 보다는 늘 아래에 온다. 그래서 선은 아래로만 간다.
 * 영역이 다르고 이어받은 사이가 아니면 날짜가 달라도 같은 줄에 설 수 있다. 줄 수를 줄여 한 화면에 들어오게 하려는 것이다.
 */
export function lineageOf() {
  const all = Object.entries(NODES)
    .map(([key, node]) => ({ number: Number(key), node, meta: issueOf(Number(key)) }))
    .filter((n) => n.meta)
  const known = new Set(all.map((n) => n.number))
  const dates = [...new Set(all.map((n) => n.meta.merged))].sort()

  const rowOf = new Map()
  const lastInLane = new Map()
  let floor = 0
  for (const date of dates) {
    const waiting = all.filter((n) => n.meta.merged === date).sort((a, b) => a.number - b.number)
    while (waiting.length) {
      // 이어받은 issue 가 같은 날짜에 있으면 그것부터 놓는다. 번호가 뒤여도 먼저 merge 된 것이다(#64 와 #61).
      let i = waiting.findIndex((n) => n.node.parents.every((p) => !known.has(p) || rowOf.has(p)))
      if (i < 0) i = 0
      const [n] = waiting.splice(i, 1)
      const after = [...n.node.parents.map((p) => rowOf.get(p) ?? -1), lastInLane.get(n.node.lane) ?? -1]
      const row = Math.max(floor, ...after.map((r) => r + 1))
      rowOf.set(n.number, row)
      lastInLane.set(n.node.lane, row)
    }
    floor = Math.max(...rowOf.values())
  }

  const nodes = all
    .map(({ number, node, meta }) => ({
      number,
      lane: LANES.findIndex((l) => l.key === node.lane),
      row: rowOf.get(number),
      name: node.name,
      result: node.result,
      title: meta.title,
      author: meta.author,
      date: dayLabel(meta.merged),
      url: meta.url,
      envVersion: node.envVersion ?? null,
      badges: badgesOf(node),
      major: badgesOf(node).length > 0,
      change: node.change ?? null,
      metric: node.metric ?? null,
      also: (node.also ?? []).map(laneName),
      parents: node.parents.filter((p) => known.has(p)),
    }))
    .sort((a, b) => a.row - b.row || a.lane - b.lane)
  const edges = nodes.flatMap((n) => n.parents.map((p) => ({ from: p, to: n.number })))
  const marks = nodes.flatMap((n) =>
    n.badges
      .filter((b) => b.lane !== LANES[n.lane].key)
      .map((b) => ({ lane: LANES.findIndex((l) => l.key === b.lane), row: n.row, text: b.text, number: n.number })),
  )
  const versions = nodes.map((n) => n.envVersion).filter((v) => v != null)
  const aimers = nodes.map((n) => NODES[n.number].aimerVersion).filter(Boolean)
  const kinds = nodes.map((n) => NODES[n.number].fly).filter(Boolean).map((k) => k.replace(' 초파리', ''))
  const current = LANES.map((l) => {
    if (l.key === 'environment') return versions.length ? `버전 ${Math.max(...versions)}` : null
    if (l.key === 'aimer') return aimers.at(-1) ?? null
    return kinds.length ? kinds.join(', ') : null
  })
  return { nodes, edges, rows: floor + 1, marks, current }
}
