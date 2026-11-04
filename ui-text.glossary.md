# UI 용어집

같은 개념은 전 화면에서 아래 표기로 통일한다. "더 자연스러운 표기"보다 이 표가 우선이다.
viewer 코드에서는 `viewer/src/data/labels.js`가 이 표를 따른다.

| 개념 | 확정 표기 | 쓰지 않을 말 | 비고 |
|---|---|---|---|
| run (기록 또는 학습 한 번) | 실행 | 런, 세션 | 왼쪽 목록 제목 |
| episode | 에피소드 | 회차 | |
| capture | 포획 | 캡처, 잡음 | 에피소드가 끝난 이유이자 상태 |
| timeout | 시간 초과 | 타임아웃 | 에피소드가 끝난 이유 |
| fly inside the view | 보임 | 가시, 감지 | 반대는 안 보임 |
| capture hold in progress | 포획 중 | 포획 진행 중 | 상태 |
| fly evading | 회피 중 | 도망 중 | 반대는 비행 중 |
| rule-based aimer | 기준선 | 베이스라인, 룰 기반 | 에피소드 그룹 이름 |
| evaluation before training | 학습 전 | 초기 | 평가 tag `initial` |
| aim error | 조준 오차 | 각도 오차, 에러 | 그래프 제목 |
| cumulative reward | 누적 보상 | 리턴, 리워드 | 그래프 제목 |
| fly mode free / evade | 자유비행 / 회피 | 프리, 이베이드 | 실행 목록 부제 |

## 상태값 매핑
코드 상태값과 화면 표기의 대응. 영어 대문자는 화면에 나오지 않는다.

| 코드 | 화면 표기 |
|---|---|
| `result: capture` | 포획 |
| `result: timeout` | 시간 초과 |
| `visible: 1` / `0` | 보임 / 안 보임 |
| `captureProgress > 0` | 포획 중 |
| `evading: 1` / `0` | 회피 중 / 비행 중 |
| tag `baseline` | 기준선 |
| tag `initial` | 학습 전 |
| tag `step_N` | N step |
| algo `rule-baseline` | 기준선 |
| fly mode `free` / `evade` | 자유비행 / 회피 |

## 갱신 이력
- 2026-11-04: 최초 작성. viewer 용어 12개
