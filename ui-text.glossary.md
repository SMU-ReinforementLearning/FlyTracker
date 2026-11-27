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
| fly alarmed (threat perceived) | 비상시 | 회피 중, 도망 중 | 반대는 평시 |
| rule-based aimer | 기준선 | 베이스라인, 룰 기반 | 에피소드 그룹 이름 |
| evaluation before training | 학습 전 | 초기 | 평가 tag `initial` |
| aim error | 조준 오차 | 각도 오차, 에러 | 그래프 제목 |
| distance from the fly to the laser beam | 빔까지 거리 | 빔 오차, 레이저 거리 | 환경 버전 3부터의 기록에만 나온다. 10cm 아래는 mm, 그 위는 m |
| zoomed centre of the aimer view | 확대 화면 | 줌, 돋보기 | 조준기 화면 바로 아래. 배율은 "80배"처럼 적는다. 포획이 레이저 명중인 기록에만 나온다 |
| cumulative reward | 누적 보상 | 리턴, 리워드 | 그래프 제목 |
| capture rate of a checkpoint | 포획률 | 성공률, 캡처율 | checkpoint의 평가 에피소드 가운데 포획으로 끝난 비율 |
| mean episode return of a checkpoint | 평균 보상 | 평균 리턴 | checkpoint의 평가 에피소드 누적 보상 평균 |
| mean time to capture | 포획 시간 | 소요 시간 | 포획한 에피소드만 평균. 하나도 없으면 "없음" |
| learning curve | 학습 곡선 | 러닝 커브 | 가로축 step, 세로축 포획률 또는 평균 보상 |
| checkpoint | checkpoint | 체크포인트 | 영어 그대로 쓴다 |
| who published the run | 올린 사람 | 작성자, 업로더 | `run.json`의 `author` |
| runs without an issue | issue 없음 | 미분류, 기타 | sidebar 묶음 이름 |
| what an issue's runs test | 실험 | 실험 개요, 개요 | issue 화면 첫 칸 제목 |
| step of the experiment plan | 실험 단계 | phase, 페이즈 | 설명 파일의 `phase`. 예: 조준기 v1 학습 |
| scripted fly | 규칙 초파리 | 룰 초파리, 기본 초파리 | 버전 v0 |
| fly agent | 학습한 초파리 | 초파리 agent, RL 초파리 | 화면 표기. README 본문은 초파리 agent |
| neural-model fly | 신경 초파리 | 뉴럴 초파리 | `fly_model: neural` |
| aimer agent | 학습한 조준기 | 조준기 agent, RL 조준기 | 화면 표기. README 본문은 조준기 agent |
| model version in the alternating schedule | v0, v1 | 버전0, 1세대 | README 대전표의 번호. 환경 버전과 다르다 |
| environment version | 환경 버전 | env 버전 | `config.json`의 `envVersion` |
| frame stack | 함께 보는 최근 관측 | 프레임 스택, 관측 묶음 | 값은 "1개, 4개" |
| tracking assist | 추적 보조 | 어시스트, 보조 제어 | 알고리즘 설정의 `assist`. 값은 "없음" 또는 "기준선 추적 + 행동 × 0.2" |
| rules that apply to both sides | 환경 | 조건, 공통 | issue 화면의 칸 제목. 환경 버전, 방, 포획 조건이 든다 (#62) |
| values of one side that do not depend on its kind | 설정 | 조건, 파라미터, 공통 설정 | 초파리 칸과 조준기 칸의 카드 제목 (#62) |
| reward weights of one side | 보상 | 보상 가중치, 리워드 | 초파리 칸과 조준기 칸의 카드 제목. 조준기 쪽 항목은 벌점, 초파리 쪽 항목은 보상으로 끝난다 (#62) |
| virtual looming stimulus shown to the neural fly | 자극 | 스티뮬러스, 가상 원반 | 신경 초파리 설정의 줄 이름에 쓴다. 예: 자극 횟수 (#62) |
| one laser shot (0.15 s) | 발 | 샷, 사격 | 수치 목록의 "쏜 발". 값은 "3발". 환경 버전 6부터의 기록에만 나온다 (#69) |
| shot during which the beam left the fly | 오발 | 미스, 빗나감 | 상태이자 수치 목록의 줄 이름. 값은 "2발" (#69) |
| misfire during which the beam touched the fly at least once | 스친 발 | 스침, 그레이즈, 빗맞은 발 | 문서와 issue 화면의 글에 쓴다. 화면의 수치 목록에는 아직 없다. 환경 버전 7부터 (#91) |
| misfire during which the beam never touched the fly | 벽에 맞은 발 | 벽 오발, 헛발, 월샷 | 문서와 issue 화면의 글에 쓴다. 화면의 수치 목록에는 아직 없다. 환경 버전 7부터 (#91) |
| shot in progress with the beam on the fly | 맞는 중 | 포획 중, 조사 중 | 상태. 레이저를 쏠 때만 켜는 기록(환경 버전 6부터)에서 "포획 중" 대신 쓴다. 발이 끝나기 전이라 아직 오발이 될 수 있다 (#95) |
| shot that stayed on the fly to its end | 명중 | 히트, 킬, 사살 | 상태(마지막 프레임)이자 재생 막대의 발 표시 이름. 반대는 오발 (#95) |
| laser on | 쏘는 중 | 발사 중, 켜짐 | 수치 목록 "레이저" 줄의 값. 반대는 꺼짐 (#69) |
| who decides when to fire | 쏘는 방식 | 발사 방식, 트리거 | 학습한 조준기 카드의 줄. 값은 "기준선의 규칙", "정책이 정함", "정책이 정함, 기준선의 규칙에서 시작" (#72, #88) |
| what the policy's turning action means | 돌리는 행동 | 제어 방식, 컨트롤, 액션 타입 | 학습한 조준기 카드의 줄. 값은 "각속도" 또는 "각가속도". 발사만 학습한 모델에는 나오지 않는다 (#88) |
| model that aims for a fire-only model | 조준을 맡은 모델 | 조준 모델, aim 모델 | 학습한 조준기 카드의 줄. 값은 그 모델의 실행 id (#88) |
| reward weight per misfire | 오발 벌점 | 미스 페널티, 오발 가중치 | 조준기 보상 카드의 줄 (#88) |
| reward weight per wall shot | 벽에 맞은 발 벌점 | 벽 오발 벌점, 월샷 페널티 | 조준기 보상 카드의 줄. 스친 발에는 주지 않는다 (#101) |
| the baseline's firing rule | 쏘는 기준 | 발사 조건, 트리거 반경 | 기준선 카드의 줄. 값은 "빔까지 1.25mm 안" (#72) |
| length of one shot | 한 발 길이 | 발사 시간, 포획 유지 시간 | 조준기 설정의 줄. 환경 버전 6부터의 실행에 나오고, 그 전 실행에는 환경 칸에 "포획 유지 시간"으로 나온다 (#72) |
| aim stimulus on or off | 자극 켬, 자극 끔 | 자극 있음, 자극 없음 | 신경 초파리 설정의 "자극" 줄의 값이고 조합 표의 초파리 칸에 붙는다 (#72, #92) |
| fly, aimer and environment that a set of runs shares | 조합 | variation, 변형, 매치업 | issue 화면의 표에서 줄 하나. 설명 글에서 쓰는 말이고 화면 제목에는 쓰지 않는다. 학습 seed만 다른 실행은 한 조합이다 (#92) |
| list of an issue's combinations | 실험 목록 | 조합, 조합 표, variation | issue 화면의 표 제목. 칸은 실험, 초파리, 조준기, 환경, 실행 순서다 (#92) |
| letter that names one row of the list | 실험 A | 조합 A, 1번, variation A | 표의 맨 앞 칸과 실행 패널의 "실험" 줄. 글자만 A, B, C로 적는다 (#92) |
| map of issues by area and by what each one builds on | 계보 | 트리, 로드맵, 타임라인 | 첫 화면의 제목이자 사이드바 맨 위 줄 (#77) |
| area an issue mainly changed | 초파리, 조준기, 환경 | 플라이, 에이머, 조건 | 계보의 세로줄 이름이자 사이드바의 구역 제목. 이 순서로 쓴다 (#77, #81) |
| another area an issue also changed | 조준기도 바꿈 | 조준기 포함, + 조준기 | 계보 노드의 아랫줄. 영역 이름 뒤에 "도 바꿈" (#77) |
| version an issue raised, shown on a lineage node | 환경 버전 3, 조준기 v1, 규칙 초파리 | 환경 v3, env 3, 조준기 버전 1 | 계보 노드 맨 위의 표시. 환경은 "환경 버전 N", 조준기는 "조준기 vN", 초파리는 종류 이름이다. 영역 이름 옆의 지금 상태는 "버전 6", "v1", "규칙, 신경"으로 줄인다 (#80) |
| episodes captured out of episodes run, on a lineage node | 포획 5/200 | 5/200 포획, 포획률 2.5% | 계보 노드의 수치 줄에만 쓴다. 문장에서는 "200개 가운데 5개" (#80) |
| whether a run was recorded during training or replays a trained model | 기록 | 종류, 타입, 모드 | 실험 목록의 칸과 실행 패널의 줄. 값은 "학습"(학습하는 동안 checkpoint마다 기록한 실행) 또는 "평가"(학습을 마친 모델을 다시 돌린 실행). 사이드바에서는 둘이 섞인 묶음의 소제목이다. 기준선과 관찰 기록에는 나오지 않는다 (#94) |
| row in which an evaluated model was trained | 모델 실험 B, 모델 #51 실험 B | 학습 실험 B, 출처 B | 평가 실행의 조준기 칸에 붙는 줄. 모델을 학습한 실행이 올라와 있을 때만 나온다. 다른 issue에서 학습했으면 issue 번호가 앞에 오고, 그 issue의 조합이 하나뿐이면 "모델 #35"다. 발사만 학습한 모델의 "조준을 맡은 모델" 줄도 같은 방식으로 적는다 (#94) |
| training seed | 학습 seed | 시드 | 알고리즘 설정의 `seed` |
| seeds of recorded episodes | 에피소드 seed | 평가 시드 | 설명 파일의 `notes`에 적는다 |

## 상태값 매핑
코드 상태값과 화면 표기의 대응. 영어 대문자는 화면에 나오지 않는다.

| 코드 | 화면 표기 |
|---|---|
| `result: capture` | 포획 |
| `result: timeout` | 시간 초과 |
| `visible: 1` / `0` | 보임 / 안 보임 |
| `captureProgress > 0` (`firing` 이 없는 기록) | 포획 중 |
| `firing: true` 이고 `0 < captureProgress < 1` | 맞는 중 |
| `firing: true` 이고 `captureProgress = 1` | 명중 |
| `firing: true` 이고 `captureProgress = 0` | 오발 |
| `firing: true` / `false` | 쏘는 중 / 꺼짐 |
| `alarmed: 1` / `0` | 비상시 / 평시 |
| tag `baseline` | 기준선 |
| tag `initial` | 학습 전 |
| tag `step_N` | N step |
| algo `rule-baseline` | 기준선 |

## 갱신 이력
- 2026-11-04: 최초 작성. viewer 용어 12개
- 2026-11-09: 초파리 상태를 평시와 비상시로 바꾸고 초파리 모드(자유비행, 회피)를 없앰
- 2026-11-11: 실행 패널과 issue 화면 용어 7개 추가 (#27)
- 2026-11-15: 빔까지 거리 추가 (#42)
- 2026-11-15: 확대 화면 추가 (#45)
- 2026-11-16: 추적 보조 추가 (#51)
- 2026-11-15: issue 화면의 실험, 초파리, 조준기, 조건 용어 11개 추가 (#47)
- 2026-11-16: issue 화면의 조건 칸을 환경으로 바꾸고 설정, 보상, 자극 추가 (#62)
- 2026-11-17: 발, 오발, 쏘는 중 추가 (#69)
- 2026-11-18: 쏘는 방식, 쏘는 기준, 한 발 길이 추가 (#72)
- 2026-11-19: 계보 추가 (#77)
- 2026-11-25: 계보 노드의 버전 표시와 수치 표기 추가 (#80)
- 2026-11-25: 영역 이름을 사이드바의 구역 제목으로도 쓴다고 적음 (#81)
- 2026-11-26: 돌리는 행동, 조준을 맡은 모델, 오발 벌점 추가. 쏘는 방식에 값 하나 추가 (#88)
- 2026-11-26: 조합 추가. variation을 조합으로 바꿈 (#92)
- 2026-11-26: 기록(학습, 평가)과 모델 실험 B 추가 (#94)
- 2026-11-26: 맞는 중, 명중 추가. 레이저를 쏠 때만 켜는 기록의 상태에서 포획 중을 대신한다 (#95)
- 2026-11-26: 스친 발, 벽에 맞은 발 추가 (#91)
- 2026-11-27: 벽에 맞은 발 벌점 추가 (#101)
