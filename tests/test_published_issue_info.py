"""published/issues/<번호>.json 이 viewer 의 issue 화면이 읽는 모양인지 본다.

실행을 올린 issue 마다 설명 파일이 하나 있어야 한다. 없으면 issue 화면에 실험 단계와 이유가 빠진다.
"""

import json
from pathlib import Path

import pytest

from flytracker.record import issue_info_path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "published"


def _issues_with_runs() -> set[int]:
    numbers = set()
    for run_json in PUBLISHED.glob("*/run.json"):
        issue = json.loads(run_json.read_text(encoding="utf-8")).get("issue")
        if issue and issue.get("number") is not None:
            numbers.add(int(issue["number"]))
    return numbers


def _info_files() -> list[Path]:
    return sorted((PUBLISHED / "issues").glob("*.json"))


def test_issue_info_path_is_where_the_viewer_reads(tmp_path):
    # viewer 는 /runs/issues/<번호>.json 을 읽고, build 는 published/ 를 dist/runs/ 로 옮긴다
    assert issue_info_path(tmp_path, 35) == tmp_path / "issues" / "35.json"


@pytest.mark.parametrize("number", sorted(_issues_with_runs()))
def test_every_issue_with_published_runs_has_an_info_file(number):
    assert issue_info_path(PUBLISHED, number).is_file(), f"published/issues/{number}.json 이 없다"


KEYS = {"phase", "purpose", "fly", "aimer", "compare", "notes"}


@pytest.mark.parametrize("path", _info_files(), ids=lambda p: p.name)
def test_info_file_shape(path):
    info = json.loads(path.read_text(encoding="utf-8"))
    assert path.stem.isdigit(), "파일 이름은 issue 번호다"
    assert set(info) <= KEYS, f"모르는 항목: {set(info) - KEYS}"
    if "compare" in info:
        # 비교 대상은 실행이 올라온 다른 issue 여야 viewer 가 견줄 수 있다
        assert isinstance(info["compare"], int) and info["compare"] != int(path.stem)
        assert info["compare"] in _issues_with_runs(), f"#{info['compare']} 에 올라온 실행이 없다"
    assert isinstance(info.get("phase"), str) and info["phase"].strip()
    assert isinstance(info.get("purpose"), list) and info["purpose"]
    assert all(isinstance(p, str) and p.strip() for p in info["purpose"])
    for key in ("fly", "aimer"):
        if key in info:
            assert isinstance(info[key], str) and info[key].strip()
    for note in info.get("notes", []):
        assert set(note) == {"label", "value"}
        assert all(isinstance(note[k], str) and note[k].strip() for k in ("label", "value"))
