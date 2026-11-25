# 조준기 변천사 사실 대장

`aimer-history.md`에 쓴 숫자와 그 출처다. 재료 위치는 이 저장소의 문서이고, `docs/issues/` 아래 경로는 앞부분을 줄였다.

표본이 다른 값은 본문에서 바로 견주지 않는다. 에피소드 seed가 0~39, 10000~10199, 20000~20199 세 가지이고, 시간도 포획 시간과 평균 시간 두 가지다.

| 대상 | 지표 | 값 | 표본 | 조건 | 재료 위치 |
|---|---|---|---|---|---|
| 이동하는 조준기 기준선 | 포획 | 28/40 | 에피소드 seed 0~39 | #1, 초파리 자유비행 | feature/1 Current State |
| 이동하는 조준기 기준선 | 포획 | 13/40 | 에피소드 seed 0~39 | #1, 초파리 회피 | feature/1 Current State |
| 고정 포대 기준선 | 포획 | 40/40 | 에피소드 seed 0~39 | #7, 벽 앞 높이 1.2m | feature/7 Current State |
| 고정 포대 기준선 | 포획 시간 | 1.92초 | 에피소드 seed 0~39 | #7 | feature/7 Current State |
| 새 탐색 기준선 | 포획 | 40/40 | 에피소드 seed 0~39 | #9, 바닥 중앙 | feature/9 work log |
| 새 탐색 기준선 | 포획 시간 | 4.37초 | 에피소드 seed 0~39 | #9 | feature/9 work log |
| 새 탐색 기준선 | 처음 볼 때까지 | 3.69초 | 에피소드 seed 0~39 | #9 | feature/9 work log |
| 제자리 회전 탐색 | 포획 | 0/40 | 에피소드 seed 0~39 | #9, 바닥 중앙 | feature/9 work log |
| 버전 2 기준선 | 포획 | 200/200 | 에피소드 seed 10000~10199 | 포획 시간 4.20초 | README 기준선과 비교 |
| 버전 2 기준선 | 포획 | 199/200 | 에피소드 seed 20000~20199 | 평균 시간 4.10초 | feature/35 gate.md |
| 버전 2 SAC, frame stack 1개 | 평균 시간 | 2.18초 | 에피소드 seed 20000~20199 | 모델 3개 평균, 포획률 98.0% | feature/35 gate.md |
| 버전 2 SAC, frame stack 4개 | 평균 시간 | 2.12초 | 에피소드 seed 20000~20199 | 모델 3개 평균, 포획률 97.2% | feature/35 gate.md |
| 버전 3 기준선 | 포획 | 5/200 | 에피소드 seed 10000~10199 | 화면 좌표에만 비례해 회전 | feature/42 Current State |
| 버전 3 기준선 | 빔이 1.25mm 안에 든 에피소드 | 39/200 | 에피소드 seed 10000~10199 | 0.05초 이상 머문 것은 9개 | feature/42 Current State |
| 버전 2 SAC 모델 6개 | 버전 3 포획 | 1/1200 | 에피소드 seed 10000~10199 | 버전 검사를 건너뛴 임시 스크립트 | feature/42 work log |
| 버전 4 기준선 | 포획 | 200/200 | 에피소드 seed 10000~10199 | 포획 시간 4.95초 | feature/45 work log |
| 버전 5 기준선 | 포획 | 198/200 | 에피소드 seed 20000~20199 | 평균 시간 4.86초 | feature/51 gate.md |
| SAC 빔 거리 | 포획 | 21/600 | 에피소드 seed 20000~20199 | 평균 시간 9.92초 | feature/51 gate.md |
| SAC 조준 오차 | 포획 | 3/600 | 에피소드 seed 20000~20199 | 평균 시간 9.98초 | feature/51 gate.md |
| SAC 빔 거리 + 추적 보조 | 포획 | 585/600 | 에피소드 seed 20000~20199 | 평균 시간 2.94초, P 1.000 | feature/51 gate.md |
| SAC 조준 오차 + 추적 보조 | 포획 | 127/600 | 에피소드 seed 20000~20199 | 평균 시간 8.98초 | feature/51 gate.md |
| 버전 6 기준선 | 포획 | 198/200 | 에피소드 seed 20000~20199 | 평균 시간 4.89초, 오발 0.50발 | feature/69 Current State |
| 버전 6 기준선 | 오발 없는 에피소드 | 138/200 | 에피소드 seed 20000~20199 | 쏘는 기준 1.25mm | feature/69 work log |
| 늘 쏘는 기준선 | 쏜 발 | 31.10발 | 에피소드 seed 20000~20199 | 에피소드마다, 오발 30.11발 | feature/69 work log |
| 쏘는 기준 2.5mm | 오발 | 1.20발 | 에피소드 seed 20000~20199 | 평균 시간 4.95초 | feature/69 work log |
| 쏘는 기준 0.3mm | 오발 | 0.25발 | 에피소드 seed 20000~20199 | 평균 시간 4.97초 | feature/69 work log |
| 조준기 v0, 규칙 초파리 | 포획 | 198/200 | 에피소드 seed 20000~20199 | 평균 시간 4.89초, 오발 0.50발 | README 조준기 v0과 v1 |
| 조준기 v1, 규칙 초파리 | 포획 | 584/600 | 에피소드 seed 20000~20199 | 평균 시간 3.03초, 오발 0.60발 | README 조준기 v0과 v1 |
| 조준기 v0, 신경 초파리 자극 끔 | 포획 | 59/60 | 에피소드 seed 20000~20059 | 평균 시간 5.11초, 오발 0.62발 | README 조준기 v0과 v1 |
| 조준기 v1, 신경 초파리 자극 끔 | 포획 | 155/180 | 에피소드 seed 20000~20059 | 평균 시간 4.26초, 오발 1.94발 | README 조준기 v0과 v1 |
| 조준기 v0, 신경 초파리 자극 켬 | 포획 | 59/60 | 에피소드 seed 20000~20059 | 평균 시간 5.40초, 오발 1.93발 | README 조준기 v0과 v1 |
| 조준기 v1, 신경 초파리 자극 켬 | 포획 | 164/180 | 에피소드 seed 20000~20059 | 평균 시간 4.06초, 오발 2.04발 | README 조준기 v0과 v1 |

## 설정값

| 대상 | 값 | 재료 위치 |
|---|---|---|
| 관측 차원 | 19(#1), 13(#7), 17(버전 4), 18(버전 6) | feature/1, feature/7, feature/45 work log, README |
| 행동 차원 | 5(#1), 2(#7), 3(버전 6) | feature/1, feature/7, feature/69 |
| 이산 행동 수 | 11(#1), 5(#7), 6(버전 6) | feature/1, feature/7, README |
| pitch 한계 | 80°(버전 1), 89°(버전 2), 90°(버전 4) | `flytracker/env.py` 버전 주석 |
| 포획 조건 | 3°와 0.5m 안에 0.2초(#1), 3° 안에 0.2초(#7), 1.25mm 안에 0.15초(버전 3), 한 발 0.15초 내내 1.25mm 안(버전 6) | feature/1, feature/7, feature/42, feature/69 |
| 레이저 가정 | 빔 지름 2.5mm, 출력 500mW, 치사 에너지 74mJ | feature/42 work log |
| 1.25mm의 각도 | 2m 거리에서 0.036° | feature/42 work log |
| 3°의 반경 | 2m 거리에서 약 10cm | feature/42 Summary |
| 조준기 최고 각속도 | yaw 180°/s, pitch 120°/s | README 조준기의 state와 action |
| 기준선 추적 식 | 초파리 방향의 각속도 + 25/s × 조준 오차 | feature/45 work log |
| 추적 보조 | 기준선 추적 행동 + 0.2 × agent의 행동 | feature/51 gate.md |
| 보상 가중치 | 시간 0.01, 놓침 0.15, 빔까지 거리 0~0.1, 행동 변화 0.01, 포획 10 | README 조준기의 R |
| 이전 조준 오차 벌점 | 0.05 × 조준 오차 ÷ 20° | README, `flytracker/env.py` |
| 판정 기준 | P 0.90 이상, 포획률 97% 이상, 모델마다 P 0.50 이상. #72는 오발이 v0의 두 배 이하 | feature/35 gate.md, feature/51 gate.md, feature/72 |
| 학습량 | 조건마다 학습 seed 3개, 1,000,000 step | feature/35 gate.md, feature/51 gate.md |
| SAC 설정 | 학습률 0.0003, replay buffer 1,000,000, batch 256, gamma 0.99, tau 0.005, 처음 100 step 뒤부터 step마다 갱신 한 번, entropy 계수 자동, 256 유닛 2층 MLP | `scripts/train.py`가 기본값을 그대로 씀. 값은 Stable-Baselines3 2.9.2의 `SAC.__init__`에서 확인 |
| 녹화 에피소드 | 학습 시작과 50,000 step마다 checkpoint 21개, checkpoint마다 3개, 학습 한 번에 63개 | `published/` 아래 #35와 #51 학습 18개의 `episodes.json` |
| 녹화 에피소드의 에피소드 seed | 10000~10002, 잡음 없는 행동 | `scripts/train.py`의 `--eval-seed` 기본값, `scripts/_common.py`의 `run_episode`, `published/issues/51.json` |
| 뷰어가 먼저 여는 에피소드 | 마지막 checkpoint의 마지막 에피소드 | `viewer/src/App.jsx` |

| 시간 간격 | 계산 0.01초, 행동 0.02초(계산 두 번), 에피소드 500 step, 한 발은 계산 15번이고 여덟째 step의 가운데에서 끝남 | `flytracker/env.py`의 `dt`, `frame_skip`, `_shot_steps`. README 에피소드 |
| 조준기 각가속도 제한 | 720°/s², 멈춘 상태에서 최고 각속도까지 0.25초 | README 조준기의 state와 action |
| 초파리 방향의 각속도 예 | 2m 거리에서 0.3m/s로 나는 초파리가 약 8.6°/s | README 조준기의 state와 action |
| gain 25/s의 출처 | 새 추적 식을 따로 시험한 스크립트에서 200/200, 버전 3 | feature/45 Scope 3번 |
| 추적 계산 순서 | 화면 좌표에서 초파리 방향을 구해 조준 오차를 내고 각속도를 더한다 | `flytracker/baseline.py`의 `RuleAimer.track` |
| 추적 보조의 계산 | 보이면 추적 행동 + 0.2 × agent의 행동을 −1~1로 자름, 안 보이면 agent의 행동 | `flytracker/baseline.py`의 `assisted`, `flytracker/wrappers.py`의 `TrackingAssist` |
| 쏘는 규칙 | 보이고, 초파리까지의 거리 × sin(조준 오차)가 1.25mm 안이면 쏜다 | `flytracker/baseline.py`의 `wants_fire`, `beam_distance` |
| v1의 발사 | 모델에 17차원을 주고 발사 값은 쏘는 규칙이 정한다 | `flytracker/players.py`의 `PolicyPlayer`(`rule_fire`) |
| 학습 순서 | 환경 설정, 상대, 환경, `SAC("MlpPolicy")`, `learn`, `RecordEvalCallback` | `scripts/train.py` |
| 진행 중인 원인 측정 | #85, 결과 없음 | GitHub issue #85 |

## 이 문서에서 계산한 값

| 값 | 계산 |
|---|---|
| gain 표 2.5°/s, 25°/s, 100°/s | 25/s × 0.1°, 1°, 4° |
| 추적 예 35°/s | 10°/s + 25/s × 1° |
| 행동 한 번에 오차의 절반 | 25/s × 0.02초 = 0.5. 각가속도 제한이 없을 때 |
| 뒤처지는 각 0.34°, 약 12mm | 8.6°/s ÷ 25/s = 0.344°, 2,000mm × tan(0.344°) = 12.0mm |
| 추적 보조의 폭 yaw 36°/s, pitch 24°/s | 0.2 × 180°/s, 0.2 × 120°/s |
| 10초 내내 안 보일 때 누적 보상 −80 | (0.01 + 0.15) × 500 step. 행동 변화 벌점은 뺐다 |
| 빔까지 거리 벌점 0.069, 0.036, 0.010 | 0.1 × log(1 + d ÷ 1.25mm) ÷ log(801), d = 125mm, 12.5mm, 1.25mm. README 값과 같다 |
| 조준 오차 벌점 0.0090, 0.00090, 0.00009 | 2m 거리에서 d = 125mm, 12.5mm, 1.25mm의 각도 3.58°, 0.358°, 0.0358°에 0.05 ÷ 20°를 곱했다 |
| 요구 정밀도 약 80배 | 3° ÷ 0.036° = 83 |
| 이전 벌점이 0.0008 줄고 지금 벌점이 0.026 준다 | 0.00090 − 0.00009, 0.036 − 0.010 |
| 채택 조건이 평균 1.9초 빠르다 | 4.858 − 2.941. feature/51 gate.md |
| v1이 놓친 25개 | 180 − 155 |
| 세 발 가운데 한 발이 오발 | 0.50 ÷ 1.49 = 0.34 |

## 본문에만 나오는 값

| 값 | 출처 |
|---|---|
| 버전 6 기준선 200개 중 200개, 포획 시간 4.99초, 오발 0.55발 | 에피소드 seed 10000~10199. README 기준선과 비교 |
| 버전 2 SAC 모델의 버전 2 포획 약 97~98% | 에피소드 seed 10000~10199. feature/42 work log |
| 채택 조건의 포획률 97.5%, 기준선 99.0% | 585/600, 198/200. feature/51 gate.md |
| v1 포획률 97.3% | 584/600. README 조준기 v0과 v1 |
| 화면 좌표 0.002, 확대한 조준 오차 0.07 | README 조준기의 state와 action |
| frame stack 비교 P 0.832 | feature/35 gate.md |
| 레이저 논문의 실험 범위 45ms | feature/42 work log |
| 초파리를 처음 볼 때까지 1.41초 | 고도 분포로 순서를 정한 첫 판. feature/9 work log |
| 초파리가 보인 step의 비율 18%(버전 2), 31%(버전 6) | 에피소드 seed 10000~10199. feature/34 work log, README 기준선과 비교 |
| 조준기 v1의 모델별 P 1.000 | feature/72 work log |
| 방 가로 4m, 높이 2.5m, 깊이 3m | README 방과 좌표 |
