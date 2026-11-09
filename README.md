# FlyTracker

방 안을 나는 초파리를 시야각이 제한된 조준기가 겨누는 강화학습 환경이다. 조준기는 방공포처럼 정해진 자리에서 조준 방향만 돌리는 카메라이고, 자기 화면에 들어온 것만 안다. 학습 결과는 viewer에서 3인칭 시점과 조준기 1인칭 시점으로 재생한다.

## 팀원 시작하기

```sh
git clone https://github.com/lhk0721/FlyTracker.git
cd FlyTracker
claude
```

Claude Code에서 `run onboarding`이라고 입력하면 hook 설정과 필요한 도구 확인을 안내한다.

## 설치

Python 3.10 이상과 [uv](https://docs.astral.sh/uv/)가 필요하다.

```sh
uv sync --extra train --extra dev
uv run pytest
```

`train` extra는 Stable-Baselines3와 TensorBoard를 설치한다. 환경만 쓸 때는 `uv sync`로 충분하다.

## 실행

규칙 기반 조준기(기준선)로 에피소드를 만든다. 결과는 `runs/`에 쌓인다. 기준선은 초파리를 놓치면 마지막으로 본 방향 둘레를 8자로 넓혀 가며 찾고, 그래도 없으면 고도 띠를 바꿔 가며 360°를 훑는다. 이 탐색은 학습 결과를 견줄 비교 대상일 뿐이고, 환경의 관측, 보상, 행동에는 들어 있지 않다. 강화학습 agent는 찾는 법도 스스로 배운다.

```sh
uv run python scripts/record_baseline.py --episodes 5
```

학습은 `scripts/train.py`로 한다. `--algo`는 `sac`, `td3`, `ppo`, `dqn` 중 하나다. DQN은 이산 행동 5개, 나머지는 연속 행동 2차원으로 학습한다. `--eval-every` step마다 같은 seed로 평가 에피소드를 저장하므로 체크포인트끼리 같은 상황에서 비교할 수 있다.

```sh
uv run python scripts/train.py --algo sac --steps 200000 --eval-every 20000
uv run tensorboard --logdir runs
```

두 스크립트가 같이 받는 환경 옵션은 다음과 같다.

| 옵션 | 뜻 |
|---|---|
| `--turret-pos X Y Z` | 조준기 자리(m). 기본 `0 0.1 0`(바닥 정가운데, 회전축 높이 0.1m) |
| `--fov` | 세로 시야각(도). 기본 40 |
| `--capture-range` | 포획 거리(m). 주지 않으면 거리 조건이 없다 |
| `--start-facing-fly` | 시작할 때 초파리를 바라보게 한다. 주지 않으면 방 가운데 쪽을 수평으로 바라본다(바닥 가운데에 있으면 −z) |

## 환경

좌표는 RackTracker 리그 규약을 따른다. x 오른쪽, y 위, z 정면인 오른손 좌표이고 단위는 m, 원점은 바닥 중심이다. 방은 가로 4m, 높이 2.5m, 깊이 3m가 기본이다. three.js도 같은 축을 쓰므로 viewer는 좌표를 변환하지 않는다.

| 항목 | 내용 |
|---|---|
| 조준기 | 설정한 자리에 고정된 포대다. 기본 자리는 바닥 정가운데다. 자리를 옮기지 않고 yaw와 pitch만 돌린다 |
| 행동 | −1~1 범위 2차원. yaw, pitch 각속도. 실제 각속도는 각가속도 제한 안에서 따라간다 |
| 관측 | 13차원. 초파리가 보이는지, 화면 좌표, 거리, 마지막으로 본 방향, 놓친 뒤 지난 시간, 조준기의 방향과 각속도 |
| 초파리 | 실제 초파리 자유비행 측정값을 따른다. 직선 구간과 급선회를 번갈아 하고, 직선 구간은 짧은 것이 잦고 긴 것이 드물다. 속도는 평균 약 0.3m/s이고, 급선회는 평균 93°를 약 50ms에 돈다. 1m 안에서 조준기와의 거리가 빠르게 줄거나 0.35m 안에 들어오면 비상시로 바뀌어, 60ms 뒤 위협 반대쪽으로 빠르게 돌며 잠깐 빨라진다. 조준선이 자기를 겨누는지는 모른다 |
| 포획 | 초파리가 조준 중심 3° 안에 0.2초 머무르면 성공하고 에피소드가 끝난다. 거리 조건은 기본으로 없다 |
| 보상 | step마다 시간 벌점, 보일 때는 조준 오차 벌점, 놓쳤을 때 고정 벌점, 행동 변화 벌점, 포획 보상 10 |
| 시간 | 물리 step 10ms, 행동 하나를 2 step 유지, 에피소드 최대 10초 |

보상 가중치는 출발점으로 잡은 값이다. 초파리 비행 값에는 문헌에서 가져온 값과 가정한 값이 섞여 있고, 값마다 출처는 [초파리 비행 모델과 기준선 탐색](docs/issues/feature/9-feature-fly-realism-search/fly-flight-and-search-model.md)에 있다. 각각 `flytracker/env.py`의 `RewardWeights`, `flytracker/fly.py`의 `FlyParams`에서 바꾼다.

## viewer

Node 20 이상이 필요하다. 개발 서버가 `runs/`를 그대로 읽으므로 따로 백엔드가 없다.

```sh
npm install --prefix viewer
npm run dev --prefix viewer
```

브라우저에서 http://localhost:5180 을 연다. 왼쪽에서 실행과 에피소드를 고르면 3인칭 장면, 조준기 화면, 현재 상태, 누적 보상과 조준 오차 그래프가 나온다. 스페이스로 재생하고 멈추며, 화살표 키로 한 프레임씩 옮긴다. 그래프를 누르면 그 시각으로 간다.

조준기 화면 위의 사각형은 Python이 기록한 화면 좌표다. 3D로 그린 초파리와 사각형이 어긋나면 Python의 투영 계산과 viewer 중 한쪽이 틀린 것이다.

## 폴더

| 경로 | 내용 |
|---|---|
| `flytracker/` | 환경, 카메라 모델, 조준기, 초파리, wrapper, 기록 저장, 기준선 |
| `scripts/` | 기준선 기록, 학습 |
| `tests/` | pytest |
| `viewer/` | 에피소드 viewer. Vite, React, React Three Fiber |
| `runs/` | 실행 결과. git에 올리지 않는다 |
