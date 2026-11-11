"""runs/ 의 실행 하나를 저장소에 올릴 수 있게 published/ 로 복사한다.

예: python scripts/publish_run.py 2026-11-09_130439_baseline
    python scripts/publish_run.py runs/2026-11-09_130439_baseline --force

설정과 에피소드 JSON 만 복사한다. 모델 파일(checkpoints/, model.zip)과 TensorBoard 기록(tb/)은 빠진다.
복사한 폴더를 commit 해 PR 로 올리면, main 에 merge 된 뒤 Cloudflare 의 viewer 에 나온다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flytracker.record import publish_run

# Windows 콘솔이 cp949 여도 한국어 출력이 깨지지 않게 한다
for stream in (sys.stdout, sys.stderr):  # 오류 문구는 stderr 로 나간다
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run", help="실행 id 또는 실행 폴더 경로 (예: runs/2026-11-09_130439_baseline)")
    p.add_argument("--runs-dir", default="runs")
    p.add_argument("--dest", default="published", help="복사할 곳. viewer 가 build 할 때 이 폴더를 읽는다")
    p.add_argument("--force", action="store_true", help="이미 올린 실행을 덮어쓴다")
    args = p.parse_args()

    run_id = Path(args.run).name
    try:
        files = publish_run(args.runs_dir, run_id, args.dest, overwrite=args.force)
    except FileExistsError:
        sys.exit(f"복사하지 못했다: {Path(args.dest) / run_id} 가 이미 있다. 덮어쓰려면 --force 를 붙인다")
    except (FileNotFoundError, ValueError) as err:
        sys.exit(f"복사하지 못했다: {err}")
    size = sum(f.stat().st_size for f in files)
    dest = Path(args.dest) / run_id
    print(f"{dest} 에 파일 {len(files)}개, {size / 1024:.0f} KB 를 복사했다.")
    print(f"다음: git add {dest.as_posix()} 로 commit 하고 PR 을 연다.")


if __name__ == "__main__":
    main()
