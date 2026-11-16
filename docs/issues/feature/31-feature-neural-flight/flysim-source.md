# flysim 출처와 실행

## 코드 확보와 직접 포함

flysim은 사용자가 외부 신경 모델과 자료를 바탕으로 Codex로 작성한 팀 코드다. 작성자가 이 내용을 FlyTracker 안으로 옮기라고 재확인해 #64에서 필요한 코드와 자료를 패키지의 [neural_assets](../../../../flytracker/neural_assets)에 직접 포함했다. 별도 flysim 프로젝트의 설치나 외부 경로 연결은 기본 실행에 필요하지 않다. 외부 프로젝트에 .git과 배포 릴리스가 없다는 사실을 코드 작성자나 이번 포함 요청이 불명확하다는 의미로 해석하지 않는다.

기존 규칙 초파리는 기본값이다. --fly-model neural을 선택하면 동봉한 신경 코드를 사용한다. --neural-source 또는 FLYTRACKER_NEURAL_SOURCE를 명시하면 해당 외부 경로가 우선하며, --neural-data로 가공 CSV 경로를 따로 지정할 수도 있다. 선택한 외부 Python 코드는 신뢰하고 실행하는 입력이다.

## 출처와 권리

| 대상 | 직접 출처 및 버전 | 포함 조건 |
|---|---|---|
| flysim 코드 5개 | 사용자 작성 코드. 2026-11-16 작성자가 직접 포함 지시 | 작성자의 요청에 따른 포함이며 외부 MIT를 전체 코드에 자동 적용하지 않는다. |
| Connectivity_783.parquet | [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model/tree/91bdd1e7dcf193f3e7ca5a8933497fcef63b7960) | 해당 저장소의 MIT 고지를 원문 그대로 동봉한다. 로컬과 upstream Git blob 해시가 같다. |
| 관련 FlyWire 연결 자료 | [Zenodo 10676866](https://zenodo.org/records/10676866) | CC BY 4.0. feather 4개와 npy 1개를 배포하며 현재 Parquet의 직접 다운로드 출처는 아니다. |
| 뉴런 주석 TSV | [flywire_annotations 고정 버전](https://github.com/flyconnectome/flywire_annotations/tree/a83b2776d60d5764cef36b927f5f9679c16c47a2) | v783 공개 자료 설명과 [공식 안내](https://flywire.ai/guidelines)에 근거해 CC BY-NC 4.0의 저작자표시 및 비영리 조건을 보존한다. |
| neurons.csv, edges.csv와 선별 집계 | 위 연결 및 주석 자료의 가공물 | 열 출처와 선별 가공 사실을 기록하고 주석의 비영리 조건을 제거하지 않는다. |

개별 주석 저장소에는 LICENSE가 없으며 고정 TSV는 2026 갱신본이다. 2024 논문에 직접 첨부된 TSV와 크기 및 해시가 다르므로 그 논문의 CC BY 4.0을 갱신본에 대신 적용하지 않는다. 이번 판단의 근거는 공식 v783 공개 자료 안내와 고정 저장소의 자료 범위 설명이다. 전체 출처, 인용 문헌과 적용 범위는 [고지](../../../../flytracker/neural_assets/NOTICE.md)에 있다. 이전에 이 코드 전체의 작성자와 공유 경위를 불명확하다고 기록했던 내용은 사용자 확인과 이번 직접 포함 지시에 따라 정정했다.

## 포함 파일과 실제 의존성

다음 경로는 flytracker/neural_assets 기준이다.

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

load_backend는 코드 5개와 CSV 2개를 읽는다. 이어서 생성자의 expand_flight_network가 Parquet와 TSV를 읽어 회로를 확장하므로 두 원자료도 계산에 필수다. selection.json, zenodo_licenses.json, 원자료 manifest.json과 외부 LICENSE는 계산에는 사용하지 않고 있으면 해시를 기록한다. MIT 고지는 배포 조건에 따라 별도로 보존한다.

기존 가공 CSV는 273개 뉴런과 9,495개 연결이며, 현재 실행은 원자료를 사용해 547개 뉴런과 16,344개 연결로 확장한다. 원자료를 빼고 CSV만 동봉하면 같은 신경 모델이 실행되지 않는다. 데이터 해시가 달라지면 같은 입력 버전으로 취급하지 않는다.

13개 원본 파일은 바이트 그대로 복사했으며 기존 공개 포획 에피소드의 meta.neural.sha256과 모두 일치한다. 파일별 크기와 전체 해시는 [MANIFEST.json](../../../../flytracker/neural_assets/MANIFEST.json)에 있다. Parquet는 96.135MiB로 GitHub의 실제 100MiB 차단 한도 이내다. 저장소의 줄바꿈 설정은 동봉 파일의 바이트를 보존한다.

## 환경 변수 없는 실행

새로 받은 저장소의 루트에서 실행한다. 외부 원본 폴더가 필요하지 않다.

```powershell
uv sync --extra neural --extra dev
uv run python scripts/record_baseline.py --fly-model neural --episodes 1 --seed 10000 --no-save
```

--no-save는 실행 결과를 요약하고 에피소드 파일은 저장하지 않는다. #61의 실제 녹화와 SAC 조준기 평가 실행은 이 파일 포함 작업에서 수행하지 않는다. 현재 포획은 빔 거리 1.25mm와 0.15초 유지 조건이다.

외부 원본을 의도적으로 검사할 때만 다음 옵션을 사용한다. 명시적 옵션, 환경 변수, 동봉 기본값 순서다. 지정한 외부 경로에 파일이 없으면 오류를 알리고 동봉 자료로 조용히 바꾸지 않는다.

```powershell
uv run python scripts/record_baseline.py --fly-model neural --neural-source '<외부 프로젝트 루트>' --episodes 1 --seed 10000 --no-save
```

## 기록과 기존 공개 실행

동봉 자료를 사용할 때 resolved_source_root는 flytracker/neural_assets, resolved_data_dir는 flytracker/neural_assets/data/stage2로 기록한다. 설정의 기본 source_root와 data_dir는 null이며, 내부 자료를 절대 경로로 명시한 경우에도 직렬화에서는 패키지 기준 경로로 바꾼다. 외부 override의 경로 기록은 기존처럼 유지한다.

[무조준 30초](../../../../published/2026-11-12_180641_01-30/run.json), [반복 조준 30초](../../../../published/2026-11-12_180710_02-30/run.json), [포획 종료](../../../../published/2026-11-12_180717_03/run.json)는 2026-11-12의 기존 기록이다. 13차원 조준기 관측, 3도 정렬과 0.2초 유지의 과거 포획 조건에서 생성했다. 현재 코드로 같은 포획 시각을 재현한다고 표시하지 않는다. 기존 공개 파일과 runs 및 원본 프로젝트는 변경하지 않았다.

실제 생물 행동 일치, 발화에서 날개로의 변환 보정과 장시간 안정성 및 학습은 여전히 별도 검증 대상이다. 코드와 자료의 직접 포함은 이러한 검증을 완료했다는 뜻이 아니다. 이번 파일 포함과 검사 기록은 [#64 관리 문서](../64-feature-bundled-neural-flight.md)에 있다.
