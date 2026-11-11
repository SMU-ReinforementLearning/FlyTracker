"""runs/ 의 실행 하나를 저장소에 올릴 수 있게 published/ 로 복사한다.

예: python scripts/publish_run.py 2026-11-09_130439_baseline --issue 31
    python scripts/publish_run.py runs/2026-11-09_130439_baseline --issue 31 --force

설정과 에피소드 JSON 만 복사한다. 모델 파일(checkpoints/, model.zip)과 TensorBoard 기록(tb/)은 빠진다.
--issue 로 받은 GitHub issue 의 번호, 제목, 주소와 올린 사람(git config user.name)을 run.json 에 적는다.
viewer 는 이 issue 로 실행을 묶는다. issue 정보는 gh 로 읽으므로 gh 에 로그인돼 있어야 한다.
학습 결과를 올리는 issue 에는 training label 을 붙인다. 없으면 경고만 하고 복사는 한다.
복사한 폴더를 commit 해 PR 로 올리면, main 에 merge 된 뒤 Cloudflare 의 viewer 에 나온다.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from flytracker.record import publish_run

TRAINING_LABEL = "training"

# Windows 콘솔이 cp949 여도 한국어 출력이 깨지지 않게 한다
for stream in (sys.stdout, sys.stderr):  # 오류 문구는 stderr 로 나간다
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def read_issue(number: int) -> tuple[dict, list[str]]:
    """gh 로 issue 를 읽어 run.json 에 적을 값과 label 이름을 돌려준다."""
    try:
        raw = json.loads(_run(["gh", "issue", "view", str(number), "--json", "number,title,url,labels"]))
    except FileNotFoundError:
        sys.exit("issue 정보를 읽지 못했다: gh 가 없다. GitHub CLI 를 설치하고 gh auth login 으로 로그인한다")
    except subprocess.CalledProcessError as err:
        sys.exit(f"issue #{number} 정보를 읽지 못했다: {err.stderr.strip() or err}")
    issue = {"number": raw["number"], "title": raw["title"], "url": raw["url"]}
    return issue, [label["name"] for label in raw.get("labels", [])]


def git_author() -> str:
    try:
        return _run(["git", "config", "user.name"]).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run", help="실행 id 또는 실행 폴더 경로 (예: runs/2026-11-09_130439_baseline)")
    p.add_argument("--issue", type=int, required=True, help="이 실행이 속한 GitHub issue 번호")
    p.add_argument("--runs-dir", default="runs")
    p.add_argument("--dest", default="published", help="복사할 곳. viewer 가 build 할 때 이 폴더를 읽는다")
    p.add_argument("--force", action="store_true", help="이미 올린 실행을 덮어쓴다")
    args = p.parse_args()

    issue, labels = read_issue(args.issue)
    if TRAINING_LABEL not in labels:
        print(
            f"경고: issue #{issue['number']} 에 {TRAINING_LABEL} label 이 없다. 학습 결과를 올리는 issue 면 label 을 붙인다.",
            file=sys.stderr,
        )
    extra = {"issue": issue, "author": git_author()}

    run_id = Path(args.run).name
    try:
        files = publish_run(args.runs_dir, run_id, args.dest, overwrite=args.force, extra=extra)
    except FileExistsError:
        sys.exit(f"복사하지 못했다: {Path(args.dest) / run_id} 가 이미 있다. 덮어쓰려면 --force 를 붙인다")
    except (FileNotFoundError, ValueError) as err:
        sys.exit(f"복사하지 못했다: {err}")
    size = sum(f.stat().st_size for f in files)
    dest = Path(args.dest) / run_id
    print(f"{dest} 에 파일 {len(files)}개, {size / 1024:.0f} KB 를 복사했다.")
    print(f"issue #{issue['number']} {issue['title']}")
    print(f"다음: git add {dest.as_posix()} 로 commit 하고 PR 을 연다.")


if __name__ == "__main__":
    main()
