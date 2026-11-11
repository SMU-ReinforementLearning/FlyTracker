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

Python 쪽이 에피소드를 만들고, viewer가 그것을 재생한다. 둘은 서로를 부르지 않고 `runs/`와 `published/` 폴더의 JSON 파일로만 이어진다.

1. `flytracker/`의 환경이 초파리와 조준기를 움직인다. agent가 행동을 하나 고르면 0.02초를 진행하고 관측과 보상을 돌려준다. 이 한 번을 step이라고 부른다.
2. `scripts/`의 스크립트가 환경에서 에피소드를 돌리고 결과를 `runs/`에 저장한다. 에피소드는 JSON 파일로 남는다. 규칙 기반 조준기(기준선)로 돌리는 것이 `record_baseline.py`, 학습하면서 돌리는 것이 `train.py`다.
3. `viewer/`는 에피소드를 3D로 재생하는 웹 페이지다. 로컬에서 띄우는 viewer 개발 서버가 `runs/`와 `published/`의 파일을 `/runs` 주소로 내주고, 브라우저의 viewer가 그 파일을 받아 그린다.
4. 팀과 나눌 실행은 `publish_run.py`로 `published/`에 복사해 PR로 올린다. `runs/`는 git에 올리지 않는다. main에 merge되면 Cloudflare Pages가 viewer를 다시 build해 사이트에 올린다.

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

실행 결과를 팀과 나누려면 `published/`에 복사해 PR로 올린다. 학습한 실행 폴더에는 모델 파일과 TensorBoard 기록이 함께 들어 있어서, `runs/`는 통째로 올리지 않는다. `publish_run.py`는 설정과 에피소드 JSON만 복사한다. 이미 올린 실행을 다시 복사하려면 `--force`를 붙인다.

```sh
uv run python scripts/publish_run.py 2026-11-11_133858_baseline
git add published/2026-11-11_133858_baseline
```

PR이 main에 merge되면 [배포](#배포)한 viewer에 그 실행이 나온다.

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

`published/`는 `runs/`와 구조가 같다. 다만 `checkpoints/`, `model.zip`, `tb/`가 없고, `index.json` 대신 실행 폴더마다 `run.json`이 있다. `run.json`은 `runs/index.json`에 있던 그 실행의 한 줄이다. viewer를 build할 때 실행마다 있는 `run.json`을 모아 실행 목록을 만든다. 실행 목록을 한 파일에 두지 않으므로, 두 사람이 각자 실행을 올린 PR도 서로 충돌하지 않는다.

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

## 기준선과 강화학습

기준선과 강화학습 agent는 같은 환경에서 같은 13차원 관측만 받는다. 기준선도 초파리의 실제 위치처럼 관측에 없는 값은 보지 않는다(`flytracker/baseline.py`). 이 절에서 agent는 강화학습 agent를 가리킨다.

둘은 행동을 고르는 쪽이 다르다. 기준선은 사람이 짠 규칙으로 고르고, 놓친 초파리를 찾는 동안에는 어디까지 찾았는지를 스스로 기억한다. 이 기억도 자기가 받아 온 관측으로 쌓은 것이다. agent는 MLP 정책으로 고르고, 어떤 행동이 좋은지 보상으로만 배운다. 그래서 놓친 초파리를 찾는 방법도 스스로 익혀야 한다. 이 README에서 "탐색"은 놓친 초파리를 찾는 동작을 말하고, 강화학습의 exploration과는 다르다.

`train.py`는 학습을 시작할 때와 `--eval-every` step마다 평가 에피소드를 돌려, 기준선과 같은 형식으로 저장한다. viewer에서는 학습 시작 때(0 step) 저장한 에피소드가 "학습 전"으로 나온다. 그 뒤 것은 "20,000 step"처럼 나온다.

agent를 학습시키면 다섯 가지가 새로 중요해진다. 보상, 기억, 학습 시간, 기준선과 비교, 관측과 행동 기록이다.

### 보상

기준선은 보상을 보지 않고 움직인다. 그래서 지금 보상 가중치가 좋은 행동을 이끄는지는 agent를 학습해 봐야 처음 드러난다. 가중치는 출발점으로 정한 값이고, `flytracker/env.py`의 `RewardWeights`에서 바꾼다.

| 항목 | 값 |
|---|---|
| 시간 벌점 | step마다 0.01 |
| 놓친 벌점 | 초파리가 안 보이는 step마다 0.15 |
| 조준 오차 벌점 | 초파리가 보이는 step마다 조준 오차에 비례해 0~0.05. 오차가 세로 시야각의 절반(기본 20°) 이상이면 0.05다 |
| 행동 변화 벌점 | 직전 행동과 이번 행동의 차이를 yaw와 pitch마다 제곱해 평균한 값 × 0.01 |
| 포획 보상 | 10 |

놓친 벌점이 가장 크므로, 빨리 찾을수록 누적 보상이 커진다. 포획 보상을 빼면 모두 벌점이고, 초파리가 보이는 동안에도 양(+)의 보상은 없다. 포획을 미루지 않게 하려고 이렇게 두었다. 보이는 step마다 양의 보상을 주면, 포획해서 에피소드를 끝내기보다 초파리를 화면에 두고 오래 버티는 편이 누적 보상이 커질 수 있다.

### 기억

기준선은 탐색 상태를 안에 들고 있다. 8자를 몇 바퀴째 그리는지, 몇 번째 고도 띠를 훑는지 기억한다. MLP 정책은 그런 기억이 없다. 관측 가운데 지난 일을 알려 주는 항목은 둘뿐이다. 마지막으로 본 방향, 그리고 놓친 뒤 지난 시간이다. 놓친 뒤 지난 시간은 2초에서 더 늘지 않는다(환경 설정 `EnvConfig.memory_horizon`).

그래서 MLP 정책은 "이 고도는 이미 훑었다"처럼 몇 초에 걸친 탐색을 배우기 어렵다. 정책에 기억을 주는 방법은 아래 세 가지다.

- frame stack: `train.py --frame-stack N`으로 켠다. 최근 N step(N × 0.02초)의 관측을 함께 본다. 초파리가 움직이는 방향을 아는 데는 쓸 만하지만, 몇 초에 걸친 탐색을 기억하기에는 짧다.
- recurrent 정책(LSTM): Stable-Baselines3 확장 패키지 `sb3-contrib`의 RecurrentPPO가 필요하다. 지금 의존성(`pyproject.toml`)에는 없다.
- 관측에 기억 항목을 더한다. 환경을 고치는 일이다.

코드를 고치지 않고 바로 쓸 수 있는 것은 frame stack뿐이다. 긴 탐색을 기억하게 하려면 뒤의 두 방법 가운데 하나가 필요하다.

### 학습 시간

알고리즘마다 학습 속도가 열 배 넘게 차이 난다. SAC와 TD3는 step마다 신경망을 업데이트해서 느리다. 아래 표의 "실제 1초당 step"은 학습을 돌리는 컴퓨터가 실제 시간 1초에 처리하는 step 수다.

| 알고리즘 | 실제 1초당 step | 200,000 step(`train.py` 기본값)에 드는 시간 |
|---|---|---|
| SAC | 53 | 약 63분 |
| TD3 | 42 | 약 79분 |
| DQN | 611 | 약 5분 |
| PPO | 493 | 약 7분 |

Intel Core i9-13900H CPU에서 GPU 없이(`train.py` 기본값 `--device cpu`) Stable-Baselines3 기본 설정으로 잰 값이다. 알고리즘마다 30초~2분 남짓 학습을 돌려 속도를 재고, 그 속도로 200,000 step을 환산했다. 돌린 길이는 SAC와 TD3가 6,000 step, DQN이 20,000 step, PPO가 16,384 step이다.

학습 없이 환경만 돌리면 같은 CPU에서 실제 1초당 약 2,500 step이다. 그러니 학습 시간 대부분은 환경이 아니라 신경망 업데이트에 든다.

### 기준선과 비교

agent가 넘어야 할 기준선 성적은 아래와 같다. 학습 중 평가가 쓰는 seed 10000부터 10199까지 에피소드 200개를 돌렸다. 환경 옵션과 보상 가중치는 모두 기본값이다. `--no-save`는 결과를 `runs/`에 저장하지 않고 요약만 출력한다.

```sh
uv run python scripts/record_baseline.py --episodes 200 --seed 10000 --no-save
```

| 지표 | 기준선 |
|---|---|
| 포획 | 200개 중 200개 |
| 포획까지 평균 시간(에피소드 안의 시간) | 4.21초 |
| 초파리가 보인 비율 | 18% |
| 평균 누적 보상 | −19.22 |

기준선은 200개를 모두 포획했으므로, agent가 포획한 에피소드 수로 기준선을 이길 수는 없다. 남은 여지는 포획까지 걸리는 시간이다. 기준선은 초파리가 안 보이면 늘 탐색을 하는데, 초파리가 보인 시간은 18%뿐이다. 시간 대부분을 탐색에 쓰는 셈이라, agent는 더 빨리 찾아야 이긴다. 비교할 때는 두 가지를 지킨다.

- seed를 맞춘다. seed가 같으면 초파리는 같은 경로로 난다. `record_baseline.py`는 기본으로 seed 0부터 돌리고, `train.py`의 평가는 seed 10000부터 돌린다. 그러니 기준선을 `--seed 10000`으로 돌려야 같은 초파리를 상대로 비교된다.
- 에피소드를 충분히 돌린다. 학습 중 평가는 한 번에 에피소드 3개뿐이라, 위 표의 200개와 견주어 판정하기에는 적다. 저장한 체크포인트를 불러 수백 개 seed로 돌리는 스크립트는 아직 없으므로, 이 비교를 하려면 그 스크립트부터 만들어야 한다.

### 관측과 행동 기록

에피소드 파일에는 기준선이든 agent든 받은 관측과 고른 행동이 남지 않는다([에피소드 파일](#에피소드-파일)). 기준선은 어떤 경우에 어떻게 움직이는지가 규칙으로 코드에 적혀 있어서, 코드를 읽으면 안다. 학습한 MLP 정책에는 그런 규칙이 없다. agent가 이상하게 움직이는 이유를 찾으려면 기록 항목을 늘려야 한다.

## viewer

Node 20 이상이 필요하다. 개발 서버가 `runs/`와 `published/`를 그대로 읽으므로 따로 백엔드가 없다. 같은 실행이 두 폴더에 다 있으면 목록에 한 번만 나온다.

```sh
npm install --prefix viewer
npm run dev --prefix viewer
```

브라우저에서 http://localhost:5180 을 연다. 왼쪽에서 실행과 에피소드를 고르면 3인칭 장면, 조준기 화면, 현재 상태, 누적 보상과 조준 오차 그래프가 나온다. 스페이스로 재생하고 멈추며, 화살표 키로 한 프레임씩 옮긴다. 그래프를 누르면 그 시각으로 간다.

초파리는 두 화면 모두 실제 모양과 크기(몸 길이 약 3mm)로 그린다. 모델은 [flybody](https://github.com/TuragaLab/flybody)(Apache-2.0)의 메시를 줄여 만들었고, 만드는 법은 `scripts/build_fly_model.py`, 출처는 `viewer/public/models/fruitfly.NOTICE.txt`에 있다. 실제 크기로는 화소 하나보다 작아서, 3인칭 장면에서는 지나온 궤적으로 위치를 본다.

조준기 화면 위의 사각형은 Python이 기록한 화면 좌표다. 초파리가 멀리 있으면 보이지 않으므로 위치는 이 사각형으로 본다. 3D로 그린 초파리와 사각형이 어긋나면 Python의 투영 계산과 viewer 중 한쪽이 틀린 것이다.

### 배포

Cloudflare Pages에 저장소를 연결해 두면, main에 merge할 때마다 viewer를 build해 사이트에 올린다. build 결과물(`viewer/dist/`)에는 `published/`의 실행만 들어가고 `runs/`는 들어가지 않는다. PR을 올리면 미리보기 주소가 따로 생기므로, merge 전에 올린 실행을 재생해 볼 수 있다.

사이트에 올라갈 결과물은 내 컴퓨터에서도 미리 볼 수 있다. preview 서버는 개발 서버와 달리 `dist/`만 내준다.

```sh
npm run build --prefix viewer
npm run preview --prefix viewer
```

Cloudflare Pages 프로젝트는 아래처럼 설정한다.

| 항목 | 값 |
|---|---|
| Production branch | `main` |
| Root directory | `viewer` |
| Build command | `npm run build` |
| Build output directory | `dist` |
| 환경 변수 | `NODE_VERSION` = `22` |

## 폴더

| 경로 | 내용 |
|---|---|
| `flytracker/` | 환경, 카메라 모델, 조준기, 초파리, wrapper, 기록 저장, 기준선 |
| `scripts/` | 기준선 기록, 학습, 실행 올리기 |
| `tests/` | pytest |
| `viewer/` | 에피소드 viewer. Vite, React, React Three Fiber |
| `runs/` | 실행 결과. git에 올리지 않는다. 형식은 [에피소드와 기록](#에피소드와-기록) |
| `published/` | 저장소에 올린 실행. 형식은 [실행 폴더](#실행-폴더) |
