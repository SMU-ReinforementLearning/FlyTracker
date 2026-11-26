"""viewer 가 재생 막대에 그리는 발 목록(episode.js 의 shotsOf)을 published/ 의 실제 에피소드로 검사한다. node 가 없으면 건너뛴다."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

CODE = """
import {{ shotsOf }} from "{episode}";
import fs from "node:fs";
let text = '';
for await (const chunk of process.stdin) text += chunk;
const out = [];
for (const file of JSON.parse(text)) {{
  const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
  const shots = shotsOf(raw.frames, raw.summary.captured === true);
  const n = raw.frames.t.length;
  out.push({{
    file,
    firing: Boolean(raw.frames.firing),
    captured: raw.summary.captured === true,
    shots: raw.frames.shots ? raw.frames.shots[n - 1] : null,
    misfires: raw.frames.misfires ? raw.frames.misfires[n - 1] : null,
    found: shots.length,
    hit: shots.filter((s) => s.result === 'hit').length,
    miss: shots.filter((s) => s.result === 'miss').length,
    open: shots.filter((s) => s.result === 'open').length,
    ordered: shots.every((s, k) => s.start <= s.end && (k === 0 || shots[k - 1].end <= s.start)),
    lastIsHit: shots.length > 0 && shots[shots.length - 1].result === 'hit',
    duration: raw.frames.t[n - 1],
  }});
}}
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def rows():
    if not shutil.which("node"):
        pytest.skip("node 가 없다")
    files = sorted(str(p) for p in (ROOT / "published").glob("*/episodes/*/ep_*.json"))
    assert files, "published/ 에 에피소드가 없다"
    code = CODE.format(episode=(ROOT / "viewer/src/data/episode.js").as_uri())
    done = subprocess.run(["node", "--input-type=module", "-e", code], input=json.dumps(files), text=True, encoding="utf-8", check=True, capture_output=True)
    return json.loads(done.stdout)


def test_records_without_firing_have_no_shots(rows):
    """레이저가 늘 켜져 있던 기록(환경 버전 5까지)에는 발 표시가 없다."""
    old = [r for r in rows if not r["firing"]]
    assert old and all(r["found"] == 0 for r in old)


def test_shot_marks_match_the_recorded_counts(rows):
    """발 표시의 수는 기록의 쏜 발 수와 같고, 오발 표시의 수는 오발 수와 같다. 올라온 에피소드 전부에서 그렇다."""
    new = [r for r in rows if r["firing"]]
    assert new
    for r in new:
        assert r["found"] == r["shots"], r
        assert r["miss"] == r["misfires"], r
        assert r["ordered"], r


def test_a_captured_episode_ends_with_one_hit(rows):
    """포획으로 끝난 에피소드는 마지막 발이 명중이고 명중은 그 하나뿐이다. 포획하지 못한 에피소드에는 명중이 없다."""
    for r in rows:
        if not r["firing"]:
            continue
        if r["captured"]:
            assert r["hit"] == 1 and r["lastIsHit"], r
        else:
            assert r["hit"] == 0, r
        assert r["open"] <= 1, r
