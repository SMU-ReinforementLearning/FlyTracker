# flysim 출처와 실행

## 코드 확보 경위

FlyTracker의 신경 초파리는 사용자가 제공한 별도 로컬 프로젝트의 `flysim` 코드와 신경 자료를 읽는다. `flysim`은 팀원이 아래 외부 자료를 바탕으로 Codex로 작성한 팀 내부 코드다(2026-11-16 팀원 확인). 외부에 배포한 적이 없어서 다운로드 주소와 릴리스 번호가 없고, 로컬 프로젝트에 `.git`도 없다.

아래 외부 주소는 로컬 자료의 출처 기록에서 확인한 참고 모델과 데이터의 주소다. `philshiu/Drosophila_brain_model`을 내려받는 것만으로 현재 필요한 로컬 `flysim` 프로젝트가 설치되는 것은 아니다. 재실행하려는 팀원은 `flysim`을 작성한 팀원에게 코드 묶음을 받는다.

## 외부 자료 출처

| 구분 | 로컬 기록에서 확인한 주소와 버전 | 사용 범위와 확인 한계 |
|---|---|---|
| 신경 모델 참고 코드 | [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model/tree/91bdd1e7dcf193f3e7ca5a8933497fcef63b7960), commit `91bdd1e7dcf193f3e7ca5a8933497fcef63b7960` | LIF 모델과 연결 자료의 참고 출처다. 로컬에 있는 해당 외부 프로젝트의 LICENSE는 MIT이며, 저작권 고지는 2023 Philip Shiu 및 Nico Spiller다. 로컬 `flysim` 전체의 허가를 뜻하지 않는다. |
| 연결 자료 | [Zenodo record 10676866](https://zenodo.org/records/10676866) | 현재 로컬 `Connectivity_783.parquet`의 출처로 기록되어 있다. 로컬 라이선스 조회 파일에는 record의 `cc-by-4.0` 식별자가 있으나, 주석과 가공 CSV를 포함한 모든 자료의 조건을 확정한 것은 아니다. |
| 뉴런 주석 | [flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations/tree/a83b2776d60d5764cef36b927f5f9679c16c47a2), commit `a83b2776d60d5764cef36b927f5f9679c16c47a2` | `supplemental_files/Supplemental_file1_neuron_annotations.tsv`를 사용한다. 정확한 주석 파일과 가공물의 재배포 조건은 미확정이다. |
| 이용 조건 | [FlyWire 이용 조건](https://flywire.ai/tos) | 이용자가 별도로 확인해야 할 조건이다. 공개 주소의 존재를 재배포 허가로 해석하지 않는다. |

이 표는 로컬 `data/raw/manifest.json`, `data/stage2/zenodo_licenses.json`과 이미 조사한 [권리 구분](rights-status-neuromechanics-20261112.json)을 근거로 한다. 이번 작업에서 원격 자료를 새로 내려받거나 재배포 조건을 확정하지 않았다. 사용자가 제공한 코드와 외부 코드의 저작권은 별도로 확인해야 한다.

## 로컬 실행에 필요한 파일

권한을 확보한 원본 프로젝트 루트를 기준으로 다음 파일이 필요하다.

```text
flysim/core.py
flysim/neural.py
flysim/neural_state.py
flysim/physics.py
flysim/behavior.py
data/stage2/neurons.csv
data/stage2/edges.csv
data/raw/Drosophila_brain_model/Connectivity_783.parquet
data/raw/flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv
```

`selection.json`, `zenodo_licenses.json`, 원자료 manifest와 외부 LICENSE는 있으면 추가로 해시를 기록한다. 가공 CSV의 경로는 `--neural-data`로 바꿀 수 있다. 공개 참고 저장소에서 현재의 가공 CSV까지 자동 생성하는 절차는 이 저장소에서 제공하지 않는다.

파일별 버전은 공개 에피소드의 `meta.neural.sha256`에 남긴 SHA-256으로 확인한다. 원자료 해시는 `raw_connectivity`, `raw_annotations`로 구분한다. FlyTracker 통합 코드의 기록 당시 해시는 `meta.neural.integration_sha256`에 있다. 해시가 다르면 동일한 입력 버전으로 간주하지 않는다. 해시는 원본 확보나 사용 허가를 대신하지 않는다.

## 환경 설정과 실행

저장소 루트의 PowerShell에서 실행한다. 아래 경로 자리에는 각자가 권한을 확보한 프로젝트 위치를 넣는다. `FLYTRACKER_NEURAL_SOURCE`는 로컬 Python 코드를 신뢰하고 실행하도록 지정하는 설정이다.

```powershell
uv sync --extra dev --extra neural
$env:FLYTRACKER_NEURAL_SOURCE = '<권한을 확보한 로컬 flysim 프로젝트 경로>'
$env:PYTHONDONTWRITEBYTECODE = '1'

# 무조준 30초
.\.venv\Scripts\python.exe -B -m scripts.record_free_flight --no-aim --seconds 30 --seed 0

# 4초 조준과 4초 해제 반복, 포획 종료 없이 30초
.\.venv\Scripts\python.exe -B -m scripts.record_free_flight --seconds 30 --seed 0

# 기존 관측 기반 조준기, 포획 시 종료
.\.venv\Scripts\python.exe -B scripts/record_baseline.py --fly-model neural --episodes 1 --seed 0
```

현재 신경 계산에는 NumPy, Gymnasium과 PyArrow가 필요하다. 원본 경로나 필수 자료가 없으면 신경 모델은 오류로 알린다. 기존 `rule` 모델은 원본 없이 동작한다. 위 명령은 새 실행을 생성하며 아래 공개 기록의 생성 시각이나 파일명을 재현하는 명령은 아니다. 원본 내용과 의존성이 달라지면 궤적도 달라질 수 있다.

## 공개 실행 3개

`published/`에는 기존 로컬 기록의 공개용 사본을 추가한다. 기존 기준선과 `runs/` 원본은 변경하지 않는다. 공개 사본에는 설정, 궤적, 신경 진단과 자극 사건을 담으며 `flysim` 코드, CSV, Parquet, TSV, 모델 체크포인트는 포함하지 않는다.

| 실행 | 길이 | 조건과 해석 |
|---|---:|---|
| [2026-11-12_180641_01-30](../../../../published/2026-11-12_180641_01-30/run.json) | 30초 | 무조준, 가상 자극 없음. 벽 감각은 유지한다. |
| [2026-11-12_180710_02-30](../../../../published/2026-11-12_180710_02-30/run.json) | 30초 | 4초 조준과 4초 해제 반복, 포획 종료 없음, 자극 13회. 정답 기하를 쓰는 관찰 장치이며 학습 정책 성능 평가가 아니다. |
| [2026-11-12_180717_03](../../../../published/2026-11-12_180717_03/run.json) | 6.08초 | 기존 관측 기반 조준기의 포획 종료. 자극 15ms 노출 후 종료됐으며 신경 도피 phase는 발생하지 않았다. |

공개 사본에서 삭제한 값은 에피소드의 `meta.neural.resolved_source_root`와 `meta.neural.resolved_data_dir`다. 설정의 `source_root`, `data_dir`는 원래부터 `null`이다. viewer가 파일을 찾는 상대 경로, 공개 출처 URL과 해시는 유지한다. 각 `run.json`의 `publication`에 삭제한 필드 이름, 원본 에피소드 해시와 이 문서의 위치를 남긴다.

기록은 2026-11-12에 생성되었다. 이후 정리한 현재 구현으로 전체 재실행했을 때 활성 계산과 기록이 일치한 내용은 [관리 문서](../31-feature-neural-flight.md)에 있다. 원래 기록에 남은 미사용 운동 설정이나 과거 통합 코드 해시는 생성 당시의 메타데이터이며 현재 계산에 쓰인다는 뜻이 아니다. 공개 과정에서 이러한 이력이나 실제 수치를 현재 값처럼 고쳐 쓰지 않는다.

viewer에서 저장된 결과를 재생할 때는 로컬 `flysim`이나 신경 원자료가 필요 없다. 로컬 서버는 `runs/`를 먼저 읽으므로, 공개 사본만 확인하려면 production 빌드와 preview를 사용한다.

```powershell
npm.cmd --prefix viewer ci
npm.cmd --prefix viewer run build
npm.cmd --prefix viewer run preview -- --host 127.0.0.1
```

최초 구현 PR #39는 main에 병합되었고 Issue #31은 닫혔다. 이번 후속 PR은 사용자의 예외 지시에 따라 새 이슈와 worktree 없이 최신 main을 대상으로 공개 기록과 이 문서만 추가한다. PR 생성과 실제 main 기반 배포 반영은 별도 단계다.

공개 기록은 13차원 조준기 관측과 3도 정렬, 0.2초 유지의 이전 포획 조건에서 생성한 자료다. 현재 main의 17차원 관측 및 빔 거리 기반 포획 조건으로 재생성하지 않았다. 위 실행 명령을 현재 main에서 실행하면 현재 환경 조건을 사용하므로 공개 기록과 같은 궤적이나 포획 시각을 보장하지 않는다.

## 권리와 미완료 사항

로컬 경로 제거는 개인정보와 실행 환경 정보의 노출을 줄이는 조치다. 외부 코드나 데이터의 재배포 권리를 새로 부여하지 않는다. 이번 공개 후보는 시뮬레이션 결과이며, 원자료 행과 개별 뉴런 ID 및 연결 목록을 복사하지 않았다. 기록에는 세포 유형별 집계와 모델 출력이 포함되므로 결과물과 집계에 적용되는 추가 조건도 별도 확인 대상이다.

로컬 `flysim`과 가공 CSV의 최초 확보 경위, 공유 권한, 정확한 주석 및 파생물의 조건은 미해결이다. 실제 초파리 행동과의 독립 검증, 발화에서 날개로의 변환 보정과 장시간 학습도 미완료다. 공개 기록의 존재를 생물학적 재현성이나 권리 확인의 완료로 해석하지 않는다.
