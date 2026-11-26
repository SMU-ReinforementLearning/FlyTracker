# 59 실측 보정 적용과 신경 비행 검증

## Document Relations

- Issue: [#59](https://github.com/SMU-ReinforementLearning/FlyTracker/issues/59)
- Branch: `59-feature-neural-fly-learning`
- Umbrella: [#58](https://github.com/SMU-ReinforementLearning/FlyTracker/issues/58)
- Base: `upstream/main@ad6e9c6e3d0e6ea661ef7e04c7f98947d015de2e`
- Status: done
- 상세 문서: [이번 비행 이론 점검](59-feature-neural-fly-learning/flight-theory-audit.md), [사전 계획](59-feature-neural-fly-learning/flight-theory-audit-plan.md), [용어](59-feature-neural-fly-learning/flight-theory-audit-terms.md), [사실 대장](59-feature-neural-fly-learning/flight-theory-audit-facts.md).
- 학습 재개: [2026-11-23 조건과 결과](59-feature-neural-fly-learning/vast-calibrated-training-20261123.md).
- 이전 근거: [실측 보정](59-feature-neural-fly-learning/normal-flight-calibration-gate.md), [분포 진단](59-feature-neural-fly-learning/normal-flight-diagnosis.md), [순차 학습 계획](59-feature-neural-fly-learning/calibrated-learning-gate.md).

## Summary

공개 실측으로 구한 candidate-13을 새 신경 비행 실행의 기본 실험 프로필로 선택한다. 기본 rule 모델은 유지한다. original을 선택하거나 보정 정보가 없는 과거 설정을 읽으면 원래 계수로 실행한다. 일반 실행에 연결되지 않고 별도 학습 함수에만 연결돼 있던 누락을 수정했다.

이 후보는 기존 독립 평가에서 평균 정규화 분포 오차가 0.367910에서 0.352007로 줄었으나 P=0.879로 사전 문턱 0.90에 미달했다. 이번 적용은 사용자의 명시적 요청에 따른 실험 설정이며 기존 미채택 판정을 바꾸지 않는다. 기록에는 계수, 자료 해시와 통계적 미채택 상태를 남긴다.

현재 모델은 실측 부분 뇌 회로와 감각, 근육 및 공력 가정을 결합한 혼합 모델이다. 회로 개입 실험에는 사용할 수 있지만 실제 초파리의 자연 비행과 회피를 재현했다고 판정할 단계는 아니다. 회로 밖 PD 자세 안정화, 초기 양력 trim과 미검증 운동 해독 및 좁은 비행 분포가 남아 있다. PD는 자세 변화의 내부 추정치와 각속도로 복원 토크를 계산하는 비례 및 미분 제어다. trim은 기준 발화에서 중량을 지탱하도록 날개 진폭을 정하는 평형 가정이다.

## Scope

| 파일 | 이번 역할 또는 유지 범위 |
|---|---|
| flytracker/flight_profiles.py | 네 계수의 공통 정의, 프로필 선택과 실측 출처 및 미검증 상태 |
| flytracker/neural_fly.py | 새 기본 보정 적용, 과거 설정 보존, 실제 물리 설정과 경고 기록 |
| flytracker/env.py | neural 항목 자체가 없는 과거 신경 설정도 원래 계수로 읽는다. |
| flytracker/neuromechanics.py | 각속도 경고를 5ms마다 기록한다. 신체 계산식은 이번에 변경하지 않았다. |
| flytracker/neural_training.py | 중복 계수 정의를 공통 프로필로 옮기고 체크포인트 계약에 해당 소스 해시를 포함한다. |
| scripts/_common.py, scripts/record_free_flight.py | 일반 및 자유비행 CLI에서 --neural-profile을 선택한다. |
| scripts/calibrate_free_flight.py, scripts/validate_neuromechanics.py | 기존 기준선 계산은 original을 명시해 새 기본값에 영향받지 않게 한다. |
| scripts/audit_neural_flight.py | 포획 없는 30초 실행의 신경, 신체, 감각 및 보조 제어 진단 |
| flytracker/aimer_training_env.py, flytracker/players.py, tests/test_current_neural_aimer.py | 현재 관측의 조준 학습과 규칙 발사, 기존 v5 및 새 v6 정책 재생과 동등 행동·보상 검사 |
| tests/test_neural_flight_profiles.py | 새 API와 CLI, 과거 설정, 프로필 오표기 거부와 각속도 경고 reset 검사 |
| flight_calibration.py, fetch_flight_dataset.py, diagnose_free_flight.py와 기존 관련 테스트 | 이전 보정 및 진단 도구를 유지한다. |
| docs/issues/README.md, pyproject.toml, uv.lock, viewer/src/data/history.js와 lineage.js | 이전 미커밋 이슈 색인, 분석 의존성과 #59 미병합 계보를 보존한다. |

## Current State

2026-11-25 PR 범위는 실측 기반 비행계수 보정, 보정 초파리 상대 SAC 조준기 및 고정 조준기 상대 81개 그룹 신경 학습이다. viewer에서 재생할 쌍별 에피소드와 검증 요약을 published/에 싣는다. 조직 브랜치의 Cloudflare Pages 미리보기에서 먼저 확인하고, 운영 사이트는 main 병합으로 갱신된다.

2026-11-21과 11-22에 원격 main을 fetch했고 두 번 모두 현재 HEAD와 같은 ee4c5a1이었다. 새 main 커밋이 없어 병합은 필요하지 않았다. #59는 OPEN이며 기존 worktree에서 작업했다. 원래 FlyTracker checkout의 chore/publish-neural-demos 브랜치와 원본 프로젝트는 변경하지 않았다. PR 직전에는 최신 main의 #80, #81 변경 두 개를 기존 Issue #59 브랜치에 반영하고 같은 worktree에서 다시 검증했다.

변경 전 파일 24개와 patch는 runs/issue59-flight-audit-20261121/before/, before.patch와 before-manifest.json에 보존했다. 더 이전 정리의 bundle, patch와 제외한 코드 및 실행은 runs/issue59-main-refresh-backup-20261120-201250에 유지한다. 기존 실측 원자료와 결과, published는 그대로다.

새 프로필은 zenodo29193-candidate13-experimental이다. 환경 v6의 관측 18차원, yaw/pitch/fire 행동과 포획 조건은 유지한다. 기존 조준기 정책을 사용할 때도 상대 신경 프로필이 같은지 확인해야 한다. 같은 seed라도 시선 연동 정책이 달라지면 자극과 궤적이 달라진다.

2026-11-23에 학습을 재개하려고 main과 #59 OPEN 상태를 확인했다. 잔액은 $4.87868352637, 대여 인스턴스는 0개였다. 현재 코드와 공개 동봉 자료 및 고지 50개를 108,479,461바이트 압축본으로 선별했다. SHA-256은 15242f2a39834ecf037266a8948a8242084daf149e28f3a0a1e4c6052f7c3f30이다.

자동 승인 심사가 정확한 50개 파일과 Vast.ai 목적지의 명시적 전송 승인이 부족하다고 판단했다. 대여·전송 명령은 실행되지 않았고 이후 자원 조회도 0개였다. 사용자에게 전송 목록과 예산 및 중단 조건을 제시해 승인을 요청했고, 다음 메시지에서 진행 승인을 받았다. 이후 인스턴스 62188296을 시간당 $0.09에 대여했다. 진행 기록은 runs/issue59-vast-calibrated-20261123/controller.log이며 승인된 전송 묶음은 변경하지 않았다. 개인 API/SSH 키, 실측 H5, .env, .git과 기존 결과는 압축본에 없다.

2026-11-24 순차 학습을 완료했다. 첫 인스턴스 62188296은 시작 시간 초과, 두 번째 62190154는 대용량 SCP 전송 시간 초과로 반납했다. 로컬 감시기에 후보 선택과 --public-assets를 추가했다. 세 번째 62191297에서는 코드 등 48개를 전송하고 공개 main 고정 커밋에서 동일한 원자료 2개를 받아 승인된 SHA-256으로 확인했다. 계산에 쓰는 50개 파일의 내용은 그대로다.

SAC는 300,000 step을 완료했고 actor 가중치가 바뀌었다. 고정 조준기 상대 신경 배율 학습은 16세대와 81개 그룹 갱신을 완료했다. 무자극 및 시선 연동 조건의 생존시간은 늘었지만 자유비행 seed 60001에서 바닥 경계 보정이 0회에서 66회로 늘어 채택하지 않는다. 학습된 조준기는 개발 4회 중 2회 포획해 회피 학습용 상대의 선행 조건을 충족했고 실제 16세대 학습에 사용했다. 규칙 조준기 대비 우세 확률 미달은 보조 진단 결과이며 상대 준비 실패를 뜻하지 않는다. 사용자 목적에 대한 이전 보고의 해석을 바로잡았다. 학습 배율은 기본값에 적용하지 않는다.

최종 결과는 runs/issue59-vast-calibrated-20261124-public/artifacts/training-neural, 요약 및 파일 해시는 같은 audit 폴더의 analysis-results.json이다. model.zip과 weights-selected.npz는 실험 산출물로 보존한다. 세 인스턴스의 반납과 최종 인스턴스 0개를 확인했다. 전체 관측 잔액 차이는 $0.2337419915이며 후행 정산 가능성을 남긴다.

로컬 감시 기록에 약 67분의 공백이 있어 원격 종료 후 반납이 약 41분 늦었다. 공백의 원인은 확정하지 못했다. 5% 미만 조건은 발생하지 않았으며 이 구간의 연속 감시를 보장했다고 보고하지 않는다. 다음 유료 실행 전에 서버 측 heartbeat 만료 중단과 종료 후 유휴 중단을 보강해야 한다. 현재 2시간 자체 중단 장치는 결과 회수 즉시 반납을 보장하지 않는다.

## Published Recordings

#59 viewer에는 보정 전후 조준기 없는 자유비행, 규칙과 SAC 조준기 비교, 고정 SAC 상대의 원래 배율 및 81개 그룹 학습 후보 비교, 경계 보정 실패의 재현을 올린다. 조건별 앞 세 seed를 재생용으로 고정한다. 별도 경계 검사는 이전에 실패한 seed 60001의 원래 배율과 학습 후보를 함께 올린 진단 기록이다. 전체 평가 통계와 재생용 표본의 범위를 구분한다.

보정 자료는 Zenodo 29193(CC BY 4.0)이다. 원자료와 조준기 모델 파일은 기존 산출물로 관리하고, 공개 기록에는 에피소드·환경 설정·모델과 배율 해시만 싣는다. 실행에 쓰인 신경 자료의 출처와 조건은 flytracker/neural_assets/NOTICE.md에 기록돼 있다.

record_issue59.py는 승인된 로컬 학습 산출물의 해시를 검사한 뒤 표준 EpisodeRecorder와 publish_run으로 재생 JSON을 생성한다. 공개 에피소드는 같은 모델과 seed의 Windows 재실행이다. 포획 여부, 종료 시각과 경계 보정 횟수를 이전 Linux 평가와 비교한다. 차이가 있을 수 있으며 원격 평가는 성능 비교의 기준으로 유지한다.

## Verification

PR 기준 최종 회귀는 250개 통과, 실패·건너뜀 0개(118.79초)다. 공개 빌드와 화면 검증은 아래 작업 로그에 정리했다.

전송 경로 보완 후 최종 회귀는 255 passed, 실패와 건너뜀 0개, 116.77초다. runs/issue59-final-transport-regression-20261124.xml에 기록했다. 원격 사전 검사도 20 passed, 4.57초다. 회수한 모델의 로컬 로딩과 신경 배율 해시 검사를 통과했다.

2026-11-23 학습 준비 후 최종 회귀는 255 passed, 실패와 건너뜀 0개, 60.26초다. runs/issue59-final-pre-vast-regression-20261123.xml에 기록했다. 현재 관측 18개를 유지하는 SAC 조준 및 규칙 발사의 학습·평가·재생 행동 변환과 보상이 일치하는 검사를 추가했다. 조준 보조가 fire까지 축소하는 불일치를 수정했다. 별도 32-step CPU smoke에서 실제 actor 가중치 변경을 확인했으며 학습 성과로 표시하지 않는다.

이전 비행 점검의 전체 회귀는 250 passed이며 실패와 건너뜀은 0개다. 기록은 runs/issue59-flight-audit-20261121/pytest-final.xml이다. 환경 일시 정지로 표시 경과시간에 중단 시간이 포함된 6,292.11초는 계산 성능 수치로 사용하지 않는다. 1차 전체 회귀는 249개 통과와 상태 이름 기대값 1개 실패였으며 새 검증 상태와 미채택 플래그를 함께 검사하도록 고쳤다.

고정 조건 방 비행은 seed 0,1,2에서 원래 계수 무자극, 보정 후보 무자극, 보정 후보 시선 연동을 각각 30초 실행했다. 총 270초, 54,000회 신체 갱신에서 비유한 상태, 방 이탈, 접촉 보정과 속도 및 각속도 경고는 모두 0이었다. quaternion 최대 오차는 2.22e-16이다. 세 조건의 날개 출력 포화는 각각 2,096회, 2,330회, 2,213회였다. 각 조건의 분모는 18,000회다. 실행 길이를 넘는 안정성은 주장하지 않는다.

시선 연동 자극은 seed마다 3회 제시됐다. 감각 입력이 없거나 무자극 대조와 같은 phase 전환도 확인했다. escape/recovery 표시만으로 조준 자극 도피를 세지 않는다. phase는 발화율 문턱과 지속시간으로 붙인 표시이며 비행의 방향성 있는 회피 성공과 다르다. 상세 수치, 예산 소진과 생물학적 한계는 별도 점검 문서에 남겼다.

일반 기준선 CLI를 새 기본 프로필로 seed 10000에서 실행해 포획 1/1, 5.39초로 정상 종료했다. 성능 평가용 표본이 아니다. 이전 32-step 학습 smoke와 245개 회귀 기록은 과거 상태의 검사로 보존한다. 이후 SAC와 신경 배율 순차 학습은 2026-11-24 완료했고 별도 문서에 결과를 기록했다. 양쪽 교대 학습은 하지 않았다.

## Execution and Next Steps

```powershell
uv sync --extra neural --extra research --extra dev
uv run python scripts/record_baseline.py --fly-model neural --episodes 1 --seed 10000 --no-save
uv run python scripts/record_baseline.py --fly-model neural --neural-profile original --episodes 1 --seed 10000 --no-save
uv run python scripts/record_free_flight.py --fly-model neural --no-aim --seconds 30 --no-save
uv run python scripts/audit_neural_flight.py --output runs/new-flight-audit --seconds 30 --workers 3
```

결과 폴더를 재사용하면 오류로 중단하므로 새 이름을 사용한다. 먼저 감각 입력, 신경 반응과 운동 변화의 대조를 분리하고 좌우 DNg02 및 VNC-근육 변환과 자세 제어를 검증한다. VNC는 날개 운동 회로를 포함하는 배쪽신경삭이다. 속도 확대나 임의 회전으로 눈에 띄게 만드는 보정은 추가하지 않는다.

이후 학습을 재개할 경우 총 $3와 Codex 잔여 한도 5% 미만 중단 조건을 유지한다. GPU 사용률은 중단 조건이 아니다. 로컬 사용량 기록을 확인할 수 없을 때도 중단한다. 대여 전에 현재 코드의 전송 목록과 사용자 승인, 잔액 및 자원을 다시 확인한다. 이번 비행 판단은 그 승인을 대신하지 않는다.

## Work Log

### feature: 실측 비행 보정과 신경회로 학습 기록 (#59)

- Zenodo 29193 기반 비행계수 네 개를 실험 프로필에 적용했다. `original`과 보정 정보가 없는 기존 설정에서 원래 계수를 재현한다.
- 관측 18개를 쓰는 환경에서 조준을 SAC로 학습하고 규칙으로 발사했다. 고정된 SAC를 상대로 신경회로 시냅스 81개 그룹의 배율을 진화 전략(ES)으로 학습했다.
- 단계별 회로 확대 실험과 전용 클라우드 실행 도구를 이번 범위에서 빼고, 관련 작업 사본은 로컬 `runs/issue59-pr-excluded-20261125/`에 보관했다.
- `published/`에 12개 실행과 에피소드 32개를 추가했다. 자유비행 보정 전후, 규칙과 SAC 조준기, 무자극 및 시선 자극의 배율 후보, 경계 진단을 재생할 수 있다. 기존 공개 기록과 신경회로 자료는 유지했다.
- Windows 재실행의 포획 시각 네 개가 Linux 평가와 0.02~0.28초 차이 났다. 포획 여부와 경계 횟수는 해당 비교에서 일치했다. 재생 기록에 대응하는 원격 수치를 남겼고 전체 성능 수치는 Linux의 자극 조건별 12회 평가에서 인용한다.
- 바닥 보정이 0회에서 66회로 늘어 배율 후보를 채택하지 않았다. 모델·가중치 바이너리와 실측 원자료는 커밋에 포함하지 않는다.

| 검증 | 결과 |
|---|---|
| 전체 Python 회귀 | 250개 통과, 실패·건너뜀 0개 (118.79초) |
| viewer 운영 빌드와 재생 데이터 읽기 | 성공. 12개 실행, 32개 에피소드, 경계 보정 0회와 66회 확인 |
| Chrome 158 · 1600×900 | #59 요약과 진단 에피소드 재생 확인. 기존 favicon 누락과 그래픽 경고 관찰 |
| Chrome 158 · 390×844 | 요약과 진단 에피소드 재생 확인. 실행 선택 줄을 가로로 밀면 마지막 선택지까지 표시 |

전체 회귀 XML과 화면 검증 원본은 로컬 `runs/issue59-pr-ad6e9c6-*` 및 `runs/issue59-pr-mobile-scroll/`에 있다.

### docs: 신경 학습 병합 표기 정리 (#59)

PR #86의 코드와 재생 기록 검토를 마쳐 관리 문서와 이슈 색인을 완료로 표시하고, viewer에는 병합일을 기록한다. 최신 main의 조준기 변천사 문서를 포함한 병합을 시뮬레이션해 충돌이 없는지 확인했다.

표기 수정 후 viewer와 기록 관련 테스트 45개가 통과했다. 운영용 viewer 빌드에서 실행 12개와 에피소드 32개의 로드를 확인했다.
