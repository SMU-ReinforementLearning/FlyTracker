"""조준기 버전과 초파리 버전을 맞붙여 대전표를 출력한다.

예: python scripts/match.py
    python scripts/match.py --aimer baseline --aimer runs/<조준기 실행 id> --fly rule --fly runs/<초파리 실행 id>

--aimer 와 --fly 는 여러 번 줄 수 있다. 조준기 v0 은 baseline(기준선), 초파리 v0 은 rule(규칙 초파리)이고, 둘 다 기본값이다.
실행 폴더(그 안의 model.zip 을 쓴다)나 checkpoint 파일(.zip)을 주면 그 모델을 쓴다.
칸마다 같은 seed 로 에피소드를 돌려 포획 수와 포획까지 평균 시간을 적는다.
환경 버전이 지금과 다른 모델은 불러오지 않는다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import add_env_args, config_from_args

from flytracker import ENV_VERSION, load_opponent
from flytracker.matchup import format_table, play_table


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_env_args(p)
    p.add_argument("--aimer", action="append", default=None, help="조준기. 여러 번 줄 수 있다. 기본 baseline")
    p.add_argument("--fly", action="append", default=None, help="초파리. 여러 번 줄 수 있다. 기본 rule")
    p.add_argument("--episodes", type=int, default=200, help="칸마다 돌릴 에피소드 수")
    p.add_argument("--seed", type=int, default=10_000, help="에피소드 i 는 seed + i 로 시작한다. 기본은 학습 중 평가와 같은 10000")
    p.add_argument("--json", default=None, help="결과를 이 JSON 파일에도 쓴다")
    args = p.parse_args()

    cfg = config_from_args(args)
    try:
        aimers = [load_opponent(s, "aimer", cfg) for s in args.aimer or ["baseline"]]
        flies = [load_opponent(s, "fly", cfg) for s in args.fly or ["rule"]]
    except (ValueError, FileNotFoundError) as e:
        p.error(str(e))

    seeds = range(args.seed, args.seed + args.episodes)
    cells = play_table(cfg, aimers, flies, seeds)
    print(f"환경 버전 {ENV_VERSION}, seed {seeds.start}~{seeds.stop - 1} (칸마다 에피소드 {len(seeds)}개)\n")
    print(format_table(aimers, flies, cells))

    if args.json:
        result = {
            "envVersion": ENV_VERSION,
            "seed": args.seed,
            "episodes": args.episodes,
            "env": cfg.to_dict(),
            "aimers": [a.label for a in aimers],
            "flies": [f.label for f in flies],
            "cells": [[c.to_dict() for c in row] for row in cells],
        }
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n저장 위치: {args.json}")


if __name__ == "__main__":
    main()
