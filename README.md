# FlyTracker

시야각이 제한된 조준기가 방 안을 나는 초파리를 겨누는 강화학습 환경이다. 조준기는 정해진 자리에서 조준 방향만 돌리는 카메라이고, 자기 화면에 들어온 것만 안다. 추격 한 판이 에피소드다. 기준선은 사람이 짠 규칙으로 움직이는 조준기다. 학습한 agent는 기준선과 견주고, 결과는 웹 페이지인 viewer에서 3인칭 장면과 조준기 화면으로 재생한다.

저장소는 세 부분으로 되어 있다. Python 쪽(환경, 학습 코드)과 viewer는 서로를 부르지 않는다. 에피소드를 돌리고 재생하는 동안 둘을 잇는 것은 `runs/`와 `published/` 폴더의 에피소드 파일뿐이다. 에피소드 파일은 에피소드 하나를 담은 JSON 파일이다.

| 부분 | 폴더 | 하는 일 |
|---|---|---|
| [환경](#환경) | `flytracker/` | 초파리와 조준기를 움직이고 관측과 보상을 돌려준다. 기준선도 여기 있다 |
| [학습 코드](#학습-코드) | `scripts/` | 기준선이나 학습 중인 agent로 에피소드를 돌려 `runs/`에 저장한다. 실행을 `published/`에 복사하는 스크립트와 viewer의 초파리 3D 모델을 만드는 스크립트도 여기 있다 |
| [viewer](#viewer) | `viewer/` | `runs/`와 `published/`의 에피소드를 3D로 재생한다 |

## 시작하기

Python 3.10 이상, [uv](https://docs.astral.sh/uv/), Node 20.19 이상이 필요하다.

```sh
git clone https://github.com/SMU-ReinforementLearning/FlyTracker.git
cd FlyTracker
uv sync --extra train --extra dev
uv run python scripts/record_baseline.py --episodes 5
npm install --prefix viewer
npm run dev --prefix viewer
```

브라우저에서 http://localhost:5180 을 연다. 왼쪽 목록에 방금 돌린 실행과 저장소에 올라 있는 실행이 보인다. 실행은 스크립트를 한 번 돌려 생긴 결과 전체다. 실행 안의 에피소드를 고르면 바로 재생된다.

`train` extra는 Stable-Baselines3와 TensorBoard를, `dev` extra는 pytest를 설치한다. 기준선만 돌릴 때는 `uv sync`로 충분하다. 테스트는 `uv run pytest`로 돌린다.

팀 작업은 Claude Code로 한다. `claude`를 띄우고 채팅에 `run onboarding`이라고 입력하면, Claude가 저장소의 git hook과 Claude Code hook을 켜고 필요한 도구를 확인한다. 코드만 돌려 볼 때는 건너뛰어도 된다.

## 환경

환경은 `flytracker/env.py`의 `FlyChaseEnv`다. [Gymnasium](https://gymnasium.farama.org/) 규격을 따르고, 초파리 비행, 조준기 회전, 초파리가 화면에 보이는지 계산하는 부분은 numpy로 직접 짰다. 물리 엔진은 쓰지 않는다. agent가 행동을 하나 고르면 환경은 0.02초를 진행하고 관측과 보상을 돌려준다. 이 한 번이 step이다.

### 방과 좌표

방은 가로 4m, 높이 2.5m, 깊이 3m다. 좌표는 x 오른쪽, y 위, z 정면인 오른손 좌표이고 단위는 m, 원점은 바닥 중심이다. three.js도 같은 축을 쓰므로 viewer는 좌표를 변환하지 않는다.

### 조준기

조준기는 방공포처럼 자리가 고정되어 있고, 자리를 옮기지 않고 yaw와 pitch만 돌린다. 기본 자리는 바닥 정가운데이고 회전축 높이는 0.1m다. 세로 시야각은 기본 40°, 화면 비율은 4:3이다. 코드와 스크립트 옵션에서는 `turret`, 에피소드 파일에서는 `aimer`라고 부른다.

### 초파리

초파리는 실제 초파리의 자유비행 측정값을 따라 난다. 직선 구간과 급선회를 번갈아 하고, 직선 구간은 짧은 것이 잦고 긴 것이 드물다. 속도는 평균 약 0.3m/s이고, 급선회는 평균 93°를 약 50ms에 돈다.

초파리에는 평시와 비상시가 있다. 초파리가 조준기에 1m 안에서 지금 속도로 1초 안에 닿을 만큼 빠르게 가까워지거나, 0.35m 안으로 들어가면 조준기를 위협으로 느껴 비상시로 바뀐다. 비상시가 되면 60ms 뒤 조준기 반대쪽으로 빠르게 돌며 잠깐 빨라진다. 조준기가 자기를 겨누는지는 모른다.

비행 값에는 문헌에서 가져온 값과 가정한 값이 섞여 있다. 값마다 출처는 [초파리 비행 모델과 기준선 탐색](docs/issues/feature/9-feature-fly-realism-search/fly-flight-and-search-model.md)에 있고, `flytracker/fly.py`의 `FlyParams`에서 바꾼다.

### 관측과 행동

관측은 13차원이다. 초파리가 안 보일 때 관측이 알려 주는 초파리 정보는 마지막으로 본 방향과 놓친 뒤 지난 시간뿐이다.

| 항목 | 차원 |
|---|---|
| 초파리가 보이는지 | 1 |
| 화면 좌표와 거리. 보일 때만 값이 있고 안 보이면 0 | 3 |
| 마지막으로 본 방향 | 3 |
| 놓친 뒤 지난 시간. 2초에서 더 늘지 않는다 | 1 |
| 조준기의 yaw(sin과 cos)와 pitch | 3 |
| 조준기의 yaw와 pitch 각속도 | 2 |

행동은 −1~1 범위의 2차원이다. yaw와 pitch의 각속도이고, 1이 yaw 180°/s, pitch 120°/s다. 실제 각속도는 각가속도 제한 720°/s² 안에서 따라가고, pitch는 위아래 80°까지 돈다. DQN처럼 이산 행동만 받는 알고리즘을 위해 행동 5개짜리 wrapper가 있다. 차례로 정지, yaw 왼쪽, yaw 오른쪽, pitch 위, pitch 아래다.

### 에피소드

에피소드는 `reset`으로 시작해서 포획하거나 시간 초과로 끝난다.

1. 시작: 초파리를 조준기에서 1.5m 이상 떨어진 무작위 위치에 놓는다. 조준기는 기본 자리에서 −z 쪽을 수평으로 바라보며 시작한다. 자리를 옮기면 그 자리에서 방 가운데 쪽을 본다.
2. step: 환경은 행동을 유지한 채 0.01초씩 두 번, 합쳐 0.02초를 움직인다. 에피소드 파일에는 step마다 프레임 하나가 남는다.
3. 끝: 초파리가 조준 방향에서 3° 안에 0.2초 머물면 포획이다. 10초가 지나면 시간 초과다. 포획 거리를 주면 초파리가 그 거리 안에 있어야 포획이 되는데, 기본으로는 없다.

그래서 에피소드 하나는 길어야 500 step이고, 시작 직후 프레임까지 더해 프레임은 최대 501개다. seed가 같으면 초파리는 같은 경로로 난다. 초파리는 고정된 조준기의 자리에만 반응하고 조준 방향은 모르므로, 정책이 달라도 경로는 같다.

### 보상

포획 보상을 빼면 모두 벌점이다. 조준 오차는 조준 방향과 초파리 방향 사이의 각도이고, 누적 보상은 에피소드 동안 받은 보상의 합이다.

| 항목 | 가중치 |
|---|---|
| 시간 벌점 | step마다 0.01 |
| 놓친 벌점 | 초파리가 안 보이는 step마다 0.15 |
| 조준 오차 벌점 | 초파리가 보이는 step마다 조준 오차에 비례해 0~0.05. 오차가 세로 시야각의 절반(기본 20°) 이상이면 0.05 |
| 행동 변화 벌점 | 직전 행동과 이번 행동의 차이를 yaw와 pitch마다 제곱해 평균한 값 × 0.01 |
| 포획 보상 | 10 |

벌점 가운데 놓친 벌점이 가장 크므로 빨리 찾을수록 누적 보상이 커진다. 초파리가 보이는 동안에도 양(+)의 보상은 없다. 보이는 step마다 양의 보상을 주면, 포획해서 에피소드를 끝내기보다 초파리를 화면에 두고 오래 버티는 편이 누적 보상이 커질 수 있어서다. 가중치는 출발점으로 잡은 값이고, `flytracker/env.py`의 `RewardWeights`에서 바꾼다.

<details>
<summary>Gymnasium에서 가져다 쓴 것</summary>

| 가져다 쓴 것 | 쓰는 곳 |
|---|---|
| `gym.Env` | `FlyChaseEnv`가 상속한다. `reset(seed)`은 첫 관측을, `step(action)`은 `(관측, 보상, terminated, truncated, info)`를 돌려준다. 포획하면 `terminated`, 시간 초과면 `truncated`다 |
| `np_random` | `reset`에 넘긴 seed로 만든 난수 생성기. 초파리 시작 위치와 비행이 이것을 쓴다 |
| `spaces.Box`, `spaces.Discrete` | 행동과 관측의 모양과 범위. 이산 행동은 `Discrete(5)`다 |
| `gym.ActionWrapper` | `DiscreteActions`(`flytracker/wrappers.py`)가 행동 번호 0~4를 연속 행동으로 바꾼다 |
| `gym.wrappers.FrameStackObservation` | 학습 스크립트 `scripts/train.py`의 `--frame-stack N`이 2 이상이면 최근 관측 N개를 쌓아 (N, 13) 모양으로 넘긴다 |
| `gym.Wrapper` | `EpisodeRecorder`(`flytracker/record.py`)가 step마다 상태를 받아 적고, 에피소드가 끝나면 파일에 쓸 내용을 만든다 |
| `check_env` | `tests/test_env.py`가 환경이 규격에 맞는지 검사한다 |

`render`는 구현하지 않았다. 그림은 viewer가 그린다. `gym.register`로 등록하지 않았으므로 `gym.make`로는 만들 수 없고, `flytracker/wrappers.py`의 `make_env()`가 환경과 wrapper를 조립한다.

</details>

## 학습 코드

에피소드를 만드는 스크립트는 `scripts/`에 두 개 있다. `record_baseline.py`는 기준선으로, `train.py`는 학습 중인 agent로 에피소드를 돌려 `runs/`에 저장한다. 둘 다 같은 [환경 옵션](#환경-옵션)을 받는다.

### 기준선

기준선은 agent와 같은 13차원 관측만 받고, 초파리의 실제 위치는 보지 않는다(`flytracker/baseline.py`). 보이면 화면 좌표에 비례해 조준 방향을 돌린다. 놓치면 마지막으로 본 방향 둘레를 8자(숫자 8 모양)로 넓혀 가며 찾는다. 그래도 없으면 yaw를 한 바퀴 돌려 360°를 훑고, 한 바퀴마다 pitch를 세로 시야각보다 조금 좁은 간격으로 옮긴다. 어디까지 찾았는지는 기준선이 내부 상태로 기억한다.

이 README에서 탐색은 놓친 초파리를 찾는 동작을 가리키고, 강화학습의 exploration과는 다르다. 탐색은 기준선의 규칙일 뿐 환경의 관측, 보상, 행동에는 들어 있지 않으므로, agent는 찾는 법도 스스로 배운다.

```sh
uv run python scripts/record_baseline.py --episodes 5
```

에피소드 i의 seed는 `--seed` 값에 i를 더한 것이고, `--seed`의 기본값은 0이다. `--no-save`는 저장하지 않고 요약만 출력한다.

### 학습

`train.py`는 Stable-Baselines3로 agent를 학습한다. `--algo`는 `sac`(기본), `td3`, `ppo`, `dqn` 중 하나다. DQN은 이산 행동 5개, 나머지는 연속 행동 2차원으로 학습한다. 정책은 MLP다. 나머지 옵션은 `--help`로 본다.

```sh
uv run python scripts/train.py --algo sac --steps 200000 --eval-every 20000
uv run tensorboard --logdir runs
```

학습 중 평가는 학습을 시작할 때와 그 뒤 일정 step마다 에피소드 몇 개를 저장하는 것이다. 간격은 `--eval-every`로 기본 20,000 step, 개수는 `--eval-episodes`로 기본 3개다. 체크포인트는 그때마다 저장한 모델이다.

학습 중 평가는 매번 같은 seed를 쓴다. 첫 에피소드가 `--eval-seed`(기본 10000)이고 다음 에피소드부터 하나씩 커진다. 그래서 체크포인트끼리 같은 초파리를 상대로 비교된다. 학습을 시작할 때 저장한 에피소드는 viewer에 "학습 전"으로 나오고, 그 뒤 것은 "20,000 step"처럼 나온다.

### 기준선과 비교

agent가 이겨야 할 기준선 성적은 아래와 같다. 학습 중 평가가 쓰는 seed 10000부터 에피소드 200개를 돌렸고, 환경 옵션과 보상 가중치는 기본값이다.

```sh
uv run python scripts/record_baseline.py --episodes 200 --seed 10000 --no-save
```

| 지표 | 기준선 |
|---|---|
| 포획 | 200개 중 200개 |
| 포획까지 평균 시간 | 4.21초 |
| 초파리가 보인 비율 | 18% |
| 평균 누적 보상 | −19.22 |

기준선은 200개를 모두 포획했으므로, agent가 포획한 에피소드 수로 기준선을 이길 수는 없다. 남은 여지는 포획까지 걸리는 시간과 누적 보상이다. 기준선은 초파리가 보인 비율이 18%뿐이라 시간 대부분을 탐색에 쓴다.

지금 할 수 있는 비교는 학습 중 평가 에피소드 3개를 같은 seed의 기준선 에피소드 3개와 견주는 것이다. 기준선 쪽은 `record_baseline.py --episodes 3 --seed 10000`으로 만든다. seed가 같아야 같은 초파리를 상대로 비교되므로, `--seed`를 주지 않은 기준선(seed 0부터)과는 견주지 않는다. [시작하기](#시작하기)에서 만든 실행이 그 경우다. 에피소드 3개는 위 표의 200개와 바로 견주기에는 적다. 체크포인트를 불러 기준선처럼 수백 개 seed로 돌리는 스크립트는 아직 없다.

### 환경 옵션

두 스크립트가 같이 받는다.

| 옵션 | 뜻 |
|---|---|
| `--turret-pos X Y Z` | 조준기 자리(m). 기본 `0 0.1 0` |
| `--fov` | 세로 시야각(도). 기본 40 |
| `--capture-range` | 포획 거리(m). 주지 않으면 없다 |
| `--max-seconds` | 에피소드 최대 길이(초). 기본 10 |
| `--start-facing-fly` | 시작할 때 초파리를 바라보게 한다. 주지 않으면 방 가운데 쪽(바닥 가운데에 있으면 −z)을 바라본다 |

### 실행 폴더

실행마다 `runs/` 아래에 폴더 하나가 생긴다. `runs/`는 git에 올리지 않는다.

```
runs/
  index.json                    실행 목록
  <실행 id>/                    예: 2026-11-09_130439_baseline
    config.json                 환경 설정 전체와 알고리즘 설정
    episodes.json               에피소드 목록과 각 요약
    episodes/<tag>/ep_000.json  에피소드 하나
    checkpoints/<tag>.zip       체크포인트 (학습만)
    model.zip                   마지막 모델 (학습만)
    tb/                         TensorBoard 기록 (학습만)
```

`<tag>`는 실행 안에서 에피소드를 나누는 이름이다. 기준선이면 `baseline`, 학습이면 평가한 시점까지의 step 수다(`step_0020000` 형식). 학습 시작 때는 `step_0000000`이고, viewer에서는 "학습 전"이다.

<details>
<summary>에피소드 파일 형식</summary>

에피소드 파일 하나는 세 부분으로 되어 있다.

| 부분 | 내용 |
|---|---|
| `meta` | 방 크기, 단위와 좌표축, 프레임 간격(0.02초), 시야각, 화면 비율, 포획 각도(3°)와 포획 거리, seed, 정책 이름(기준선이면 `rule-baseline`, 학습이면 알고리즘 이름). 학습 중 저장했으면 몇 step째 모델인지도 들어간다 |
| `summary` | 프레임 수, 걸린 시간, 포획 여부, 누적 보상, 초파리가 보인 비율 |
| `frames` | 프레임마다의 상태 |

`frames`는 항목마다 배열 하나로 저장한다. 프레임마다 객체를 하나씩 두는 것보다 파일이 작다. 첫 프레임은 `reset` 직후 상태이고, 이때 보상은 0이다.

| 항목 | 뜻 |
|---|---|
| `t` | 시각(초) |
| `fly`, `flyHeading` | 초파리 위치, 나는 방향 |
| `aimerC`, `aimerLook` | 조준기 위치, 조준 방향 |
| `visible`, `uv` | 초파리가 시야 안에 있는지(보임), 화면 어디에 있는지(가로세로 −1~1, x 오른쪽, y 위) |
| `angleErrDeg`, `distance` | 조준 오차(도), 초파리까지 거리(m) |
| `alarmed` | 초파리가 비상시인지 |
| `captureProgress` | 포획 조건을 채운 정도(0~1) |
| `reward` | 그 step에서 받은 보상 |

</details>

### 실행 올리기

팀과 나눌 실행은 `published/`에 복사해 PR로 올린다. 학습한 실행 폴더에는 모델 파일과 TensorBoard 기록이 함께 들어 있어서 `runs/`는 통째로 올리지 않는다. `publish_run.py`는 설정과 에피소드 파일만 복사한다. 이미 올린 실행을 다시 복사하려면 `--force`를 붙인다.

```sh
uv run python scripts/publish_run.py 2026-11-11_133858_baseline
git add published/2026-11-11_133858_baseline
```

`published/`는 `runs/`와 구조가 같다. 다만 `checkpoints/`, `model.zip`, `tb/`가 없고, `index.json` 대신 실행 폴더마다 `run.json`이 있다. `run.json`은 `runs/index.json`에 있던 그 실행의 한 줄이다. viewer를 build할 때 실행마다 있는 `run.json`을 모아 실행 목록을 만든다. 실행 목록을 한 파일에 두지 않으므로, 두 사람이 각자 실행을 올린 PR도 서로 충돌하지 않는다. PR이 main에 merge되면 [배포](#배포)한 viewer에 그 실행이 나온다.

### 정책의 기억

기준선은 탐색 상태를 안에 들고 있다. 8자를 몇 바퀴째 그리는지, yaw를 몇 바퀴 돌았는지 기억한다. MLP 정책은 그런 기억이 없다. 관측에서 지난 일을 알려 주는 항목은 마지막으로 본 방향과 놓친 뒤 지난 시간뿐이고, 놓친 뒤 지난 시간은 2초에서 멈춘다. 그래서 "이 pitch는 이미 훑었다"처럼 몇 초에 걸친 탐색을 배우기 어렵다.

정책에 기억을 주는 방법은 세 가지다.

- frame stack: `train.py --frame-stack N`으로 켠다. 최근 N step(N × 0.02초)의 관측을 함께 본다. 초파리가 움직이는 방향을 아는 데는 쓸 만하지만, 몇 초에 걸친 탐색을 기억하기에는 짧다.
- recurrent 정책(LSTM): Stable-Baselines3 확장 패키지 `sb3-contrib`의 RecurrentPPO가 필요하다. 지금 의존성(`pyproject.toml`)에는 없다.
- 관측에 기억 항목 더하기: 환경을 고치는 일이다.

코드를 고치지 않고 바로 쓸 수 있는 것은 frame stack뿐이다.

### 학습 시간

알고리즘마다 학습 속도가 열 배 넘게 차이 난다. SAC와 TD3는 step마다 신경망을 업데이트해서 느리다. 아래 표의 "실제 1초당 step"은 학습을 돌리는 컴퓨터가 실제 시간 1초에 처리하는 step 수다.

| 알고리즘 | 실제 1초당 step | 200,000 step(`train.py` 기본값)에 드는 시간 |
|---|---|---|
| SAC | 53 | 약 63분 |
| TD3 | 42 | 약 79분 |
| DQN | 611 | 약 5분 |
| PPO | 493 | 약 7분 |

Intel Core i9-13900H CPU에서 GPU 없이(`train.py` 기본값 `--device cpu`) Stable-Baselines3 기본 설정으로 2026-11-10에 잰 값이다. 알고리즘마다 30초~2분 남짓 학습을 돌려 속도를 재고, 그 속도로 200,000 step을 환산했다. 돌린 길이는 SAC와 TD3가 6,000 step, DQN이 20,000 step, PPO가 16,384 step이다. 학습 없이 환경만 돌리면 같은 CPU에서 실제 1초당 약 2,500 step이다. 그러니 학습 시간 대부분은 환경이 아니라 신경망 업데이트에 든다.

### 에피소드 파일의 한계

에피소드 파일에 남는 것은 환경이 아는 실제 상태다. agent가 받은 관측 가운데 마지막으로 본 방향, 놓친 뒤 지난 시간, 조준기 각속도는 남지 않고, agent가 고른 행동도 남지 않는다. 기준선은 어떤 경우에 어떻게 움직이는지가 코드에 규칙으로 적혀 있어서 코드를 읽으면 안다. agent에는 그런 규칙이 없으므로, agent가 이상하게 움직이는 이유를 찾으려면 에피소드 파일의 항목을 늘려야 한다.

## viewer

viewer는 Vite, React, React Three Fiber로 만든 웹 페이지다. 개발 서버가 저장소의 `runs/`와 `published/`를 `/runs` 주소로 내주므로 따로 백엔드가 없다. 같은 실행이 두 폴더에 다 있으면 목록에 한 번만 나온다.

```sh
npm install --prefix viewer
npm run dev --prefix viewer
```

브라우저에서 http://localhost:5180 을 연다. 왼쪽에서 실행과 에피소드를 고르면 3인칭 장면, 조준기 화면, 현재 상태, 누적 보상과 조준 오차 그래프가 나온다. 에피소드는 고르면 바로 재생되고, 스페이스로 멈추거나 다시 재생하며, 화살표 키로 한 프레임씩 옮긴다. 그래프를 누르면 그 시각으로 간다.

### 초파리 3D 모델

초파리는 3인칭 장면과 조준기 화면 모두 실제 모양과 크기(몸 길이 약 3mm)로 그린다. 3D 모델은 [flybody](https://github.com/TuragaLab/flybody)(Apache-2.0)의 메시를 줄여 만들었고, 만드는 법은 `scripts/build_fly_model.py`, 출처는 `viewer/public/models/fruitfly.NOTICE.txt`에 있다. 실제 크기로는 화소 하나보다 작아서, 3인칭 장면에서는 지나온 궤적으로 위치를 본다.

### 조준기 화면의 사각형

조준기 화면 위의 사각형은 Python이 기록한 화면 좌표 자리에 그린 표식이다. 조준기 화면에서는 초파리가 멀면 화소보다 작아 눈에 띄지 않으므로 위치는 이 사각형으로 본다. 3D로 그린 초파리와 사각형이 어긋나면 Python의 투영 계산과 viewer 중 한쪽이 틀린 것이다.

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
