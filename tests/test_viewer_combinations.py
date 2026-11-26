"""viewer 의 조합 표 데이터(experiment.js 의 combinationsOf)를 published/ 의 실제 실행으로 검사한다. node 가 없으면 건너뛴다."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

CODE = """
import {{ combinationsOf, cellText }} from "{experiment}";
let text = '';
for await (const chunk of process.stdin) text += chunk;
const groups = JSON.parse(text);
const out = {{}};
for (const [key, configs] of Object.entries(groups)) {{
  const runs = configs.map((_, i) => ({{ id: String(i), episodeCount: 1 }}));
  out[key] = combinationsOf(runs, configs, null).map((row) => ({{
    letter: row.letter,
    fly: cellText(row.fly),
    aimer: cellText(row.aimer),
    environment: cellText(row.environment),
    runs: row.runs,
  }}));
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
def groups():
    found = _groups()
    assert found, "published/ 에 issue 가 붙은 실행이 없다"
    return found


@pytest.fixture(scope="module")
def result(groups):
    if not shutil.which("node"):
        pytest.skip("node 가 없다")
    code = CODE.format(experiment=(ROOT / "viewer/src/data/experiment.js").as_uri())
    done = subprocess.run(["node", "--input-type=module", "-e", code], input=json.dumps(groups), text=True, encoding="utf-8", check=True, capture_output=True)
    return json.loads(done.stdout)


def test_every_run_is_in_exactly_one_combination(groups, result):
    """실행은 모두 조합 하나에만 든다. 표에서 빠지거나 두 줄에 나오는 실행이 없다."""
    for key, configs in groups.items():
        placed = sorted(run["id"] for row in result[key] for run in row["runs"])
        assert placed == sorted(str(i) for i in range(len(configs))), key


def test_combinations_of_one_issue_read_differently(result):
    """한 issue 안의 조합은 초파리, 조준기, 환경 칸의 글이 서로 다르다. 같으면 표에서 두 줄을 가를 수 없다.

    #59 는 뺀다. 같은 설정을 두 번 올린 실행이 있다. config.json 의 evaluation.flyWeights 가 한쪽은 original, 한쪽은 baseline 인데 둘 다 원래 가중치다.
    """
    for key, rows in result.items():
        if key == "59":
            continue
        texts = [(row["fly"], row["aimer"], row["environment"]) for row in rows]
        assert len(set(texts)) == len(texts), (key, texts)


def test_aimer_v1_issue_has_six_combinations(result):
    """#72 는 조준기 둘(기준선, 학습한 조준기)과 초파리 셋(규칙, 신경 자극 끔, 신경 자극 켬)의 조합 여섯이다."""
    rows = result["72"]
    assert len(rows) == 6
    assert [row["letter"] for row in rows] == ["A", "B", "C", "D", "E", "F"]
    assert sorted({row["fly"] for row in rows}) == ["규칙 초파리 v0", "신경 초파리, 자극 끔", "신경 초파리, 자극 켬"]
    assert all(row["environment"] == "버전 6" for row in rows)
    # 학습한 조준기 줄에는 학습 seed 가 다른 실행 셋이 있고, 기준선 줄에는 실행 하나가 있다
    assert sorted(len(row["runs"]) for row in rows) == [1, 1, 1, 3, 3, 3]
    assert all(run["seed"] is not None for row in rows if len(row["runs"]) == 3 for run in row["runs"])


def test_missing_row_is_not_confused_with_the_value_none(result):
    """추적 보조 '없음'은 값이다. 줄이 없는 것으로 보고 빼면 #51 의 네 조건이 두 줄씩 같아진다."""
    aimers = [row["aimer"] for row in result["51"]]
    assert sum("추적 보조 없음" in a for a in aimers) == 2
    assert len(set(aimers)) == 4
