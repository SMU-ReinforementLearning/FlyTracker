"""viewer 의 계보 자료(lineage.js)를 published/ 의 실제 issue 와 맞춰 본다. node 가 없으면 건너뛴다."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "published"

CODE = """
import {{ lineageOf, LANES }} from "{lineage}";
console.log(JSON.stringify({{ ...lineageOf(), lanes: LANES.length }}));
"""


@pytest.fixture(scope="module")
def lineage():
    if not shutil.which("node"):
        pytest.skip("node 가 없다")
    code = CODE.format(lineage=(ROOT / "viewer/src/data/lineage.js").as_uri())
    done = subprocess.run(["node", "--input-type=module", "-e", code], text=True, encoding="utf-8", check=True, capture_output=True)
    return json.loads(done.stdout)


def _issues_with_runs() -> set[int]:
    numbers = set()
    for run_json in PUBLISHED.glob("*/run.json"):
        issue = json.loads(run_json.read_text(encoding="utf-8")).get("issue")
        if issue and issue.get("number") is not None:
            numbers.add(int(issue["number"]))
    return numbers


def test_every_issue_with_published_runs_is_a_node(lineage):
    """실행을 올린 issue 는 계보에 있어야 첫 화면에서 그 issue 화면으로 갈 수 있다. 실행을 올리고 lineage.js 를 잊으면 여기서 걸린다."""
    numbers = {n["number"] for n in lineage["nodes"]}
    assert _issues_with_runs() - numbers == set()


def test_node_names_are_short_and_distinct(lineage):
    """이름은 노드, 사이드바, issue 화면 제목에 함께 쓴다. 길면 사이드바에서 잘리고, 같으면 두 issue 를 가를 수 없다."""
    names = [n["name"] for n in lineage["nodes"]]
    assert [x for x in names if len(x) > 15] == []
    assert len(names) == len(set(names))
    assert [n["number"] for n in lineage["nodes"] if n["name"] == n["title"]] == []


def test_every_node_is_complete(lineage):
    for n in lineage["nodes"]:
        assert 0 <= n["lane"] < lineage["lanes"], n
        assert all(isinstance(n[k], str) and n[k].strip() for k in ("name", "result", "title", "author", "date", "url")), n


def test_edges_only_go_down_and_cells_hold_one_node(lineage):
    by = {n["number"]: n for n in lineage["nodes"]}
    for e in lineage["edges"]:
        assert e["from"] in by and by[e["from"]]["row"] < by[e["to"]]["row"], e
    cells = [(n["lane"], n["row"]) for n in lineage["nodes"]]
    assert len(cells) == len(set(cells))
    assert max(n["row"] for n in lineage["nodes"]) == lineage["rows"] - 1


def test_environment_versions_run_without_a_gap(lineage):
    """환경 버전은 1부터 하나씩 오른다. 버전을 올린 issue 에 envVersion 을 빠뜨리면 계보에서 버전이 건너뛴다."""
    versions = sorted(n["envVersion"] for n in lineage["nodes"] if n["envVersion"] is not None)
    assert versions == list(range(1, len(versions) + 1))
    assert lineage["current"][-1] == f"버전 {versions[-1]}"


def test_a_version_mark_sits_in_an_empty_cell_of_its_own_lane(lineage):
    """다른 영역의 노드가 올린 버전은 제 영역의 같은 줄에 표식으로 놓인다. 그 칸에 노드가 있으면 둘이 겹친다."""
    by = {n["number"]: n for n in lineage["nodes"]}
    taken = {(n["lane"], n["row"]) for n in lineage["nodes"]}
    for m in lineage["marks"]:
        assert m["lane"] != by[m["number"]]["lane"] and m["row"] == by[m["number"]]["row"], m
        assert (m["lane"], m["row"]) not in taken, m
    cells = [(m["lane"], m["row"]) for m in lineage["marks"]]
    assert len(cells) == len(set(cells))


def test_change_and_metric_are_filled_or_absent(lineage):
    """change 는 후(to)가 있어야 하고, 전(from)이 있으면 후와 달라야 한다. 버전을 올린 노드만 크게 그린다."""
    for n in lineage["nodes"]:
        change = n["change"]
        if change is not None:
            assert change["what"].strip() and change["to"].strip(), n
            assert change.get("from") != change["to"], n
        assert n["metric"] is None or n["metric"].strip(), n
        assert n["major"] == bool(n["badges"]), n


def test_a_line_between_lanes_does_not_cross_a_node(lineage):
    """영역이 다른 issue 를 잇는 선은 이어받은 issue 의 줄에서 옆으로 나간다. 그 줄의 사이 영역에 노드가 있으면 선이 노드를 지난다."""
    by = {n["number"]: n for n in lineage["nodes"]}
    taken = {(n["lane"], n["row"]) for n in lineage["nodes"]}
    crossed = []
    for e in lineage["edges"]:
        p, c = by[e["from"]], by[e["to"]]
        lo, hi = sorted((p["lane"], c["lane"]))
        crossed += [e for lane in range(lo + 1, hi) if (lane, p["row"]) in taken]
    assert crossed == []
