# FlyTracker

방 안을 나는 초파리를 시야각이 제한된 조준기가 겨누는 강화학습 환경이다. 조준기는 방공포처럼 정해진 자리에서 조준 방향만 돌리는 카메라이고, 자기 화면에 들어온 것만 안다. 학습 결과는 viewer에서 3인칭 시점과 조준기 1인칭 시점으로 재생한다.

## 팀원 시작하기

```sh
git clone https://github.com/lhk0721/FlyTracker.git
cd FlyTracker
claude
```

Claude Code에서 `run onboarding`이라고 입력하면 hook 설정과 필요한 도구 확인을 안내한다.

## 구성

Python 쪽이 에피소드를 만들고, viewer가 그것을 재생한다. 둘은 서로를 부르지 않고 `runs/` 폴더의 JSON 파일로만 이어진다.

1. `flytracker/`의 환경이 초파리와 조준기를 움직인다. agent가 행동을 하나 고르면 0.02초를 진행하고 관측과 보상을 돌려준다. 이 한 번을 step이라고 부른다.
2. `scripts/`의 스크립트가 환경에서 에피소드를 돌리고 결과를 `runs/`에 저장한다. 에피소드는 JSON 파일로 남는다. 규칙 기반 조준기(기준선)로 돌리는 것이 `record_baseline.py`, 학습하면서 돌리는 것이 `train.py`다.
3. `viewer/`는 `runs/`의 에피소드를 3D로 재생하는 웹 페이지다. 로컬에서 띄우는 viewer 개발 서버가 `runs/`의 파일을 `/runs` 주소로 내주고, 브라우저의 viewer가 그 파일을 받아 그린다.

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
| 시간 | 계산 간격 10ms. 행동 하나를 두 간격(20ms) 유지하고, 이것이 step 하나다. 에피소드 최대 10초 |

보상 가중치는 출발점으로 잡은 값이다. 초파리 비행 값에는 문헌에서 가져온 값과 가정한 값이 섞여 있고, 값마다 출처는 [초파리 비행 모델과 기준선 탐색](docs/issues/feature/9-feature-fly-realism-search/fly-flight-and-search-model.md)에 있다. 각각 `flytracker/env.py`의 `RewardWeights`, `flytracker/fly.py`의 `FlyParams`에서 바꾼다.

### Gymnasium

환경은 [Gymnasium](https://gymnasium.farama.org/) 규격을 따른다. Gymnasium에서는 규격과 wrapper만 가져다 썼고, 초파리 비행, 조준기 회전, 초파리가 화면에 보이는지 계산하는 부분은 numpy로 직접 짰다. MuJoCo 같은 물리 엔진은 쓰지 않는다. Stable-Baselines3는 이 규격을 따르는 환경을 그대로 받으므로, `train.py`에서 알고리즘을 바꿔도 환경 코드는 바뀌지 않는다.

| 가져다 쓴 것 | 쓰는 곳 |
|---|---|
| `gym.Env` | `FlyChaseEnv`(`flytracker/env.py`)가 상속한다. `reset(seed)`은 초파리와 조준기를 처음 자리에 놓고 첫 관측을 돌려준다. `step(action)`은 `(관측, 보상, terminated, truncated, info)`를 돌려준다. 포획하면 `terminated`, 시간 초과면 `truncated`다 |
| `np_random` | `reset`에 넘긴 seed로 만든 난수 생성기다. 초파리 시작 위치와 비행이 이것을 쓴다. 초파리는 조준기가 어디를 겨누는지 모르므로, seed가 같으면 정책이 달라도 초파리는 같은 경로로 난다 |
| `spaces.Box`, `spaces.Discrete` | 행동과 관측의 모양과 범위를 선언한다. 행동은 2차원(−1~1), 관측은 13차원이다. DQN용 이산 행동은 `Discrete(5)`다 |
| `gym.ActionWrapper` | `DiscreteActions`(`flytracker/wrappers.py`)가 DQN이 고른 행동 번호 0~4를 연속 행동으로 바꾼다. 차례로 정지, yaw 왼쪽, yaw 오른쪽, pitch 위, pitch 아래다 |
| `gym.wrappers.FrameStackObservation` | `train.py --frame-stack`이 N(2 이상)이면 최근 관측 N개를 쌓아 (N, 13) 모양으로 넘긴다 |
| `gym.Wrapper` | `EpisodeRecorder`(`flytracker/record.py`)가 step마다 상태를 받아 적고, 에피소드가 끝나면 파일에 쓸 내용을 만든다 |
| `check_env` | `tests/test_env.py`가 환경이 규격에 맞는지 검사한다 |

`render`는 구현하지 않았다. 그림은 viewer가 그린다. `gym.register`로 등록하지 않았으므로 `gym.make`로는 만들 수 없고, `flytracker/wrappers.py`의 `make_env()`가 환경과 wrapper를 직접 조립한다.

## 에피소드와 기록

에피소드 하나는 추격 한 판이다. `reset`으로 시작해서 포획하거나 시간 초과로 끝난다.

1. 시작: 초파리를 방 안 무작위 위치에 놓는다. 조준기에서 1.5m 이상 떨어진 곳이다. 조준기는 기본으로 방 가운데 쪽을 수평으로 바라본다.
2. step: agent가 행동을 하나 고르면, 환경은 그 행동을 유지한 채 0.01초씩 두 번 움직인다. 이 0.02초가 step 하나이고, 기록에는 step마다 프레임 하나가 남는다.
3. 끝: 초파리가 조준 중심 3° 안에 0.2초 머물면 포획이다. 10초가 지나면 시간 초과다. 그래서 에피소드 하나는 길어야 500 step이고, `reset` 직후 프레임까지 더해 프레임은 최대 501개다.

### 실행 폴더

실행 한 번마다 `runs/` 아래에 폴더 하나가 생긴다.

```
runs/
  index.json                    실행 목록
  <실행 id>/                    예: 2026-11-09_130439_baseline
    config.json                 환경 설정 전체와 알고리즘 설정
    episodes.json               에피소드 목록과 각 요약
    episodes/<tag>/ep_000.json  에피소드 하나
    checkpoints/<tag>.zip       평가 시점마다 저장한 모델 (학습만)
    model.zip                   마지막 모델 (학습만)
    tb/                         TensorBoard 기록 (학습만)
```

`<tag>`는 에피소드 묶음 이름이다. 기준선이면 `baseline`이고, 학습이면 평가한 시점까지의 step 수다(`step_0020000` 형식). 평가 한 번에 에피소드 3개(`--eval-episodes`)를 저장하고, seed는 매번 10000, 10001, 10002다. 초파리 경로는 seed로 정해지므로 체크포인트끼리 같은 초파리를 상대로 비교된다.

### 에피소드 파일

에피소드 파일 하나는 세 부분으로 되어 있다.

| 부분 | 내용 |
|---|---|
| `meta` | 방 크기, 단위와 좌표축, 프레임 간격(0.02초), 시야각, 화면 비율, 포획 각도와 거리, seed, 정책 이름. 학습 중 저장했으면 몇 step째 모델인지도 들어간다 |
| `summary` | 프레임 수, 걸린 시간, 포획 여부, 누적 보상, 초파리가 보인 프레임 비율 |
| `frames` | 프레임마다의 상태 |

`frames`는 항목마다 배열 하나로 저장한다. 프레임마다 객체를 하나씩 두는 것보다 파일이 작다. 첫 프레임은 `reset` 직후 상태이고, 이때 보상은 0이다.

| 항목 | 뜻 |
|---|---|
| `t` | 시각(초) |
| `fly`, `flyHeading` | 초파리 위치, 나는 방향 |
| `aimerC`, `aimerLook` | 조준기 위치(C는 카메라 중심), 바라보는 방향 |
| `visible`, `uv` | 초파리가 시야 안에 있는지(보임), 화면 어디에 있는지(가로세로 −1~1, x 오른쪽, y 위) |
| `angleErrDeg`, `distance` | 조준 오차(도), 초파리까지 거리(m) |
| `alarmed` | 초파리가 비상시인지 |
| `captureProgress` | 포획 조건을 채운 정도(0~1) |
| `reward` | 그 step에서 받은 보상 |

agent가 받은 관측(13차원)과 고른 행동은 기록하지 않는다. 파일에 남는 것은 환경이 아는 실제 상태다. 그래서 viewer에서는 agent가 무엇을 보고 그렇게 움직였는지 바로 볼 수 없다.

## viewer

Node 20 이상이 필요하다. 개발 서버가 `runs/`를 그대로 읽으므로 따로 백엔드가 없다.

```sh
npm install --prefix viewer
npm run dev --prefix viewer
```

브라우저에서 http://localhost:5180 을 연다. 왼쪽에서 실행과 에피소드를 고르면 3인칭 장면, 조준기 화면, 현재 상태, 누적 보상과 조준 오차 그래프가 나온다. 스페이스로 재생하고 멈추며, 화살표 키로 한 프레임씩 옮긴다. 그래프를 누르면 그 시각으로 간다.

초파리는 두 화면 모두 실제 모양과 크기(몸 길이 약 3mm)로 그린다. 모델은 [flybody](https://github.com/TuragaLab/flybody)(Apache-2.0)의 메시를 줄여 만들었고, 만드는 법은 `scripts/build_fly_model.py`, 출처는 `viewer/public/models/fruitfly.NOTICE.txt`에 있다. 실제 크기로는 화소 하나보다 작아서, 3인칭 장면에서는 지나온 궤적으로 위치를 본다.

조준기 화면 위의 사각형은 Python이 기록한 화면 좌표다. 초파리가 멀리 있으면 보이지 않으므로 위치는 이 사각형으로 본다. 3D로 그린 초파리와 사각형이 어긋나면 Python의 투영 계산과 viewer 중 한쪽이 틀린 것이다.

## 폴더

| 경로 | 내용 |
|---|---|
| `flytracker/` | 환경, 카메라 모델, 조준기, 초파리, wrapper, 기록 저장, 기준선 |
| `scripts/` | 기준선 기록, 학습 |
| `tests/` | pytest |
| `viewer/` | 에피소드 viewer. Vite, React, React Three Fiber |
| `runs/` | 실행 결과. git에 올리지 않는다. 형식은 [에피소드와 기록](#에피소드와-기록) |
