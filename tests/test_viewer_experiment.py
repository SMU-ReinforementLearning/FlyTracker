"""viewer 의 issue 화면 데이터(experiment.js, history.js)를 published/ 의 실제 실행으로 검사한다. node 가 없으면 건너뛴다."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

CODE = """
import {{ experimentOf, compareExperiments }} from "{experiment}";
import {{ changeOf }} from "{history}";
let text = '';
for await (const chunk of process.stdin) text += chunk;
const groups = JSON.parse(text);
const out = {{}};
for (const [key, configs] of Object.entries(groups)) {{
  const runs = configs.map((_, i) => ({{ id: String(i), episodeCount: 1 }}));
  const exp = experimentOf(runs, configs, null);
  const rows = [
    ...exp.environment,
    ...['fly', 'aimer'].flatMap((s) => [...exp[s].settings, ...exp[s].rewards, ...exp[s].cards.flatMap((c) => c.rows)]),
  ];
  const cards = ['fly', 'aimer'].flatMap((s) => exp[s].cards);
  out[key] = {{
    envVersion: exp.envVersion,
    labels: {{
      environment: exp.environment.map((r) => r.label),
      flySettings: exp.fly.settings.map((r) => r.label),
      flyRewards: exp.fly.rewards.map((r) => r.label),
      aimerSettings: exp.aimer.settings.map((r) => r.label),
      aimerRewards: exp.aimer.rewards.map((r) => r.label),
    }},
    cards: cards.map((c) => c.src),
    unsourced: [...rows.filter((r) => !changeOf(r.src, exp.envVersion)).map((r) => r.src), ...cards.filter((c) => !changeOf(c.src, exp.envVersion)).map((c) => c.src)],
    issues: Object.fromEntries(rows.map((r) => [r.src, changeOf(r.src, exp.envVersion)?.issue.number ?? null])),
    selfDiff: JSON.stringify(compareExperiments(exp, exp)).includes('"prev"'),
  }};
}}
console.log(JSON.stringify(out));
"""


def _groups():
    """issue 번호별 config.json 목록."""
    groups = {}
    for run in sorted((ROOT / "published").glob("*/run.json")):
        meta = json.loads(run.read_text(encoding="utf-8"))
        number = (meta.get("issue") or {}).get("number")
        if number is None:
            continue
        groups.setdefault(str(number), []).append(json.loads((run.parent / "config.json").read_text(encoding="utf-8")))
    return groups


@pytest.fixture(scope="module")
def result():
    if not shutil.which("node"):
        pytest.skip("node 가 없다")
    groups = _groups()
    assert groups, "published/ 에 issue 가 붙은 실행이 없다"
    code = CODE.format(
        experiment=(ROOT / "viewer/src/data/experiment.js").as_uri(),
        history=(ROOT / "viewer/src/data/history.js").as_uri(),
    )
    done = subprocess.run(["node", "--input-type=module", "-e", code], input=json.dumps(groups), text=True, encoding="utf-8", check=True, capture_output=True)
    return json.loads(done.stdout)


def test_every_shown_row_and_card_names_the_issue_that_set_it(result):
    """화면에 나오는 줄과 카드 이름은 모두 값을 정한 issue 를 안다. 줄을 더하고 history.js 를 잊으면 여기서 걸린다.

    aimer.other 는 viewer 가 종류를 모르는 조준기라서 뺀다.
    """
    missing = {key: [s for s in r["unsourced"] if s != "aimer.other"] for key, r in result.items()}
    assert {key: v for key, v in missing.items() if v} == {}


def test_rows_are_split_by_owner(result):
    """포획 규칙은 환경, 조준기의 몸과 화면은 조준기, 비행 값은 초파리에 든다."""
    for key, r in result.items():
        labels = r["labels"]
        assert "포획 범위" in labels["environment"], key
        assert "환경 버전" in labels["environment"], key
        assert "시야각" not in labels["environment"], key
        if "aimer.none" not in r["cards"]:
            assert "시야각" in labels["aimerSettings"], key
            assert "포획 보상" in labels["aimerRewards"], key


def test_fly_reward_is_hidden_without_a_learned_fly(result):
    """규칙 초파리와 신경 초파리는 보상을 쓰지 않는다. published/ 에는 아직 학습한 초파리가 없다."""
    for key, r in result.items():
        if "fly.learned" not in r["cards"]:
            assert r["labels"]["flyRewards"] == [], key


def test_neural_fly_shows_stimulus_instead_of_flight_values(result):
    r = result["31"]
    assert "자극 횟수" in r["labels"]["flySettings"]
    assert "비행 속도" not in r["labels"]["flySettings"]
    assert "비행 속도" in result["51"]["labels"]["flySettings"]


def test_issue_is_picked_by_env_version(result):
    """같은 줄이라도 환경 버전에 따라 값을 정한 issue 가 다르다."""
    assert result["35"]["envVersion"] == 2
    assert result["35"]["issues"]["env.capture_radius"] == 1
    assert result["42"]["issues"]["env.capture_radius"] == 42
    assert result["35"]["issues"]["env.aimer.max_pitch_deg"] == 34
    assert result["51"]["issues"]["env.aimer.max_pitch_deg"] == 45
    assert result["51"]["issues"]["env.reward.beam"] == 49


def test_comparing_an_experiment_with_itself_changes_nothing(result):
    assert not any(r["selfDiff"] for r in result.values())
