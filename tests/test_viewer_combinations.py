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
  const runs = configs.map((c, i) => ({{ id: c.__id ?? String(i), episodeCount: 1 }}));
  out[key] = combinationsOf(runs, configs.map(({{ __id, ...c }}) => c), null).map((row) => ({{  // __id 는 실행 id 를 넘기는 자리일 뿐이다
    letter: row.letter,
    record: row.record,
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


def test_training_and_evaluation_runs_are_separate_rows(result):
    """#88 에는 학습하는 동안 기록한 실행 27개(1단계 다섯 조건, 발사만 학습한 네 조건)와 학습을 마친 모델을 다시 돌린 실행 13개(일곱 조합)가 있다.

    둘은 한 줄에 섞이지 않고, 학습 실행의 줄이 앞에 온다.
    """
    rows = result["88"]
    kinds = [row["record"] for row in rows]
    assert kinds == ["training"] * 9 + ["evaluation"] * 7
    assert [len(row["runs"]) for row in rows if row["record"] == "training"] == [3] * 9
    assert sum(len(row["runs"]) for row in rows if row["record"] == "evaluation") == 13


def test_runs_without_a_learned_side_have_no_record_kind(result):
    """기준선과 관찰 기록은 학습도 평가도 아니다."""
    assert all(row["record"] is None for row in result["69"])
    assert {row["record"] for row in result["72"]} == {None, "evaluation"}
    assert {row["record"] for row in result["51"]} == {"training"}


def test_evaluation_rows_name_the_row_their_model_was_trained_in():
    """평가 실행의 줄은 모델을 학습한 실행이 같은 issue 에 있으면 그 줄의 글자를 적고, 보상 줄은 적지 않는다.

    평가 실행의 보상 값은 다시 돌린 환경의 값이다. 적으면 행동 변화 벌점 1.0 으로 학습한 모델이 0.01 로 학습한 것처럼 읽힌다.
    """
    if not shutil.which("node"):
        pytest.skip("node 가 없다")
    configs = []
    for run in sorted((ROOT / "published").glob("*/run.json")):
        meta = json.loads(run.read_text(encoding="utf-8"))
        if (meta.get("issue") or {}).get("number") == 88:
            configs.append({**json.loads((run.parent / "config.json").read_text(encoding="utf-8")), "__id": meta["id"]})
    code = CODE.format(experiment=(ROOT / "viewer/src/data/experiment.js").as_uri())
    done = subprocess.run(["node", "--input-type=module", "-e", code], input=json.dumps({"88": configs}), text=True, encoding="utf-8", check=True, capture_output=True)
    rows = json.loads(done.stdout)["88"]
    trained = {row["letter"]: row for row in rows if row["record"] == "training"}
    pen = next(letter for letter, row in trained.items() if "행동 변화 벌점 1," in row["aimer"] + ",")
    evaluated = [row for row in rows if row["record"] == "evaluation"]
    assert all("벌점" not in row["aimer"] for row in evaluated)
    named = [row for row in evaluated if "모델 실험" in row["aimer"]]
    assert len(named) == 7
    # 발사만 학습한 모델은 학습 seed 마다 조준 모델의 id 가 다르다. 그래도 조건 하나가 한 줄이고, 조준 모델은 행동 변화 벌점 조건의 줄을 가리킨다
    fire_only = [row for row in rows if "조준을 맡은 모델" in row["aimer"]]
    assert len(fire_only) == 6 and all(f"조준을 맡은 모델 실험 {pen}" in row["aimer"] for row in fire_only)
    assert sum(f"모델 실험 {pen}" in row["aimer"].split(", ") for row in named) == 3  # 규칙 초파리, 신경 초파리 자극 끔과 켬
    # 학습 seed 로 가르는 줄은 학습 seed 순서다
    for row in rows:
        seeds = [run["seed"] for run in row["runs"] if run["seed"] is not None]
        assert seeds == sorted(seeds)


ORIGINS_CODE = """
import {{ combinationsOf, cellText }} from "{experiment}";
let text = '';
for await (const chunk of process.stdin) text += chunk;
const {{ source, target }} = JSON.parse(text);
const runsOf = (configs) => configs.map((c) => ({{ id: c.__id, episodeCount: 1 }}));
const strip = (configs) => configs.map(({{ __id, ...c }}) => c);
const origins = new Map();
for (const row of combinationsOf(runsOf(source), strip(source), null))
  if (row.record === 'training') for (const r of row.runs) origins.set(r.id, `#51 실험 ${{row.letter}}`);
console.log(JSON.stringify(combinationsOf(runsOf(target), strip(target), null, origins).map((row) => cellText(row.aimer))));
"""


def test_evaluation_rows_name_a_model_trained_in_another_issue():
    """#72 의 모델은 #51 에서 학습했다. 그 issue 의 줄을 부르는 글(origins)을 주면 평가 줄이 '모델 #51 실험 B' 로 적는다."""
    if not shutil.which("node"):
        pytest.skip("node 가 없다")

    def configs(number):
        found = []
        for run in sorted((ROOT / "published").glob("*/run.json")):
            meta = json.loads(run.read_text(encoding="utf-8"))
            if (meta.get("issue") or {}).get("number") == number:
                found.append({**json.loads((run.parent / "config.json").read_text(encoding="utf-8")), "__id": meta["id"]})
        return found

    code = ORIGINS_CODE.format(experiment=(ROOT / "viewer/src/data/experiment.js").as_uri())
    done = subprocess.run(["node", "--input-type=module", "-e", code], input=json.dumps({"source": configs(51), "target": configs(72)}), text=True, encoding="utf-8", check=True, capture_output=True)
    aimers = json.loads(done.stdout)
    learned = [a for a in aimers if a.startswith("학습한 조준기")]
    assert len(learned) == 3 and all("모델 #51 실험 B" in a for a in learned), aimers
