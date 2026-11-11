import json

import pytest

from flytracker import RunStore
from flytracker.record import publish_run


def fake_episode(i):
    return {"format": "flytracker.episode/1", "meta": {"seed": i}, "summary": {"frames": 1, "captured": False}, "frames": {"t": [0.0]}}


def make_run(root):
    store = RunStore(root)
    run = store.create_run("test", "sac", "continuous", {"env": {}, "algo": {"name": "sac"}}, notes="메모")
    for tag in ("step_0000000", "step_0020000"):
        for i in range(2):
            run.save_episode(fake_episode(i), tag)
    # 학습이 같은 폴더에 남기는 것들. 복사되면 안 된다.
    (run.dir / "checkpoints").mkdir()
    (run.dir / "checkpoints" / "step_0020000.zip").write_bytes(b"model")
    (run.dir / "model.zip").write_bytes(b"model")
    (run.dir / "tb").mkdir()
    (run.dir / "tb" / "events.out").write_bytes(b"tb")
    return run


def tree(path):
    return sorted(p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file())


def test_publish_copies_json_only(tmp_path):
    run = make_run(tmp_path / "runs")
    files = publish_run(tmp_path / "runs", run.id, tmp_path / "published")

    dest = tmp_path / "published" / run.id
    assert tree(dest) == [
        "config.json",
        "episodes.json",
        "episodes/step_0000000/ep_000.json",
        "episodes/step_0000000/ep_001.json",
        "episodes/step_0020000/ep_000.json",
        "episodes/step_0020000/ep_001.json",
        "run.json",
    ]
    assert sorted(files) == sorted(dest / f for f in tree(dest))
    assert tree(tmp_path / "published") == [f"{run.id}/{f}" for f in tree(dest)]  # 임시 폴더가 남지 않는다

    # episodes.json 의 경로는 runs/ 기준 그대로라 published/ 에서도 맞는다
    manifest = json.loads((dest / "episodes.json").read_text(encoding="utf-8"))
    for ep in manifest["episodes"]:
        assert (tmp_path / "published" / ep["file"]).is_file()


def test_run_json_is_the_index_entry(tmp_path):
    run = make_run(tmp_path / "runs")
    publish_run(tmp_path / "runs", run.id, tmp_path / "published")

    index = json.loads((tmp_path / "runs" / "index.json").read_text(encoding="utf-8"))
    entry = json.loads((tmp_path / "published" / run.id / "run.json").read_text(encoding="utf-8"))
    assert entry == index["runs"][0]
    assert entry["episodeCount"] == 4
    assert entry["notes"] == "메모"


def test_extra_fields_go_into_run_json(tmp_path):
    run = make_run(tmp_path / "runs")
    issue = {"number": 31, "title": "보상에 각도 항 넣기", "url": "https://github.com/o/r/issues/31"}
    publish_run(tmp_path / "runs", run.id, tmp_path / "published", extra={"issue": issue, "author": "kim", "episodeCount": 99})

    entry = json.loads((tmp_path / "published" / run.id / "run.json").read_text(encoding="utf-8"))
    assert entry["issue"] == issue
    assert entry["author"] == "kim"
    assert entry["id"] == run.id
    assert entry["episodeCount"] == 4  # 세어서 적는 값은 extra 가 덮지 못한다
    # runs/index.json 은 그대로다
    index = json.loads((tmp_path / "runs" / "index.json").read_text(encoding="utf-8"))
    assert "issue" not in index["runs"][0]


def test_refuses_existing_unless_overwrite(tmp_path):
    run = make_run(tmp_path / "runs")
    publish_run(tmp_path / "runs", run.id, tmp_path / "published")
    stale = tmp_path / "published" / run.id / "episodes" / "old" / "ep_000.json"
    stale.parent.mkdir(parents=True)
    stale.write_text("{}", encoding="utf-8")

    with pytest.raises(FileExistsError):
        publish_run(tmp_path / "runs", run.id, tmp_path / "published")
    assert stale.exists()

    publish_run(tmp_path / "runs", run.id, tmp_path / "published", overwrite=True)
    assert not stale.exists()


def test_unknown_or_broken_run_writes_nothing(tmp_path):
    run = make_run(tmp_path / "runs")
    with pytest.raises(FileNotFoundError):
        publish_run(tmp_path / "runs", "no-such-run", tmp_path / "published")

    (run.dir / "episodes" / "step_0020000" / "ep_001.json").unlink()
    with pytest.raises(FileNotFoundError, match="ep_001.json"):
        publish_run(tmp_path / "runs", run.id, tmp_path / "published")
    assert not (tmp_path / "published").exists()
