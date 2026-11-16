# 64 신경 비행 코드와 자료를 저장소에 포함

## Document Relations
- Issue: [#64](https://github.com/SMU-ReinforementLearning/FlyTracker/issues/64)
- Branch: `64-feature-bundled-neural-flight`
- Umbrella: [#58](https://github.com/SMU-ReinforementLearning/FlyTracker/issues/58)
- Related: #61, #31, #59
- Base: upstream/main@31d64cb
- Status: 완료(구현 및 검증). PR #65의 사용자 승인에 따른 병합 준비 완료.

## Summary

사용자가 직접 작성한 flysim 코드와 필요한 신경 자료를 FlyTracker 패키지에 포함해 외부 프로젝트 및 환경 변수 없이 신경 초파리를 실행한다. 원본 파일은 바이트 그대로 보존하며 비행 동역학을 변경하지 않는다.

## Goal

- 새 폴더에서 uv sync --extra neural --extra dev 후 신경 기준선을 실행한다.
- 기본 입력은 동봉 자료, 명시적 경로와 환경 변수는 기존과 같은 선택적 override로 둔다.
- 동봉 실행의 기록 및 설정에 컴퓨터별 절대 경로를 저장하지 않는다.
- 원본 자료와 기존 공개 에피소드의 SHA-256을 대조하고 권리와 인용을 함께 기록한다.

## Scope

- flytracker/neural_assets 아래에 코드 5개, CSV 2개, 회로 확장 원자료 2개와 출처 메타데이터 및 고지를 포함한다.
- 기본 자료 선택, 기록용 경로 표시와 현재 관측 및 포획 계약의 테스트를 정리한다.
- 원본 바이트의 줄바꿈 변환을 막는 Git 속성을 적용한다.
- 사용자 재지시로 코드와 자료의 포함 및 필요한 구현을 진행하되 커밋, push, PR은 최종 변경 검토 후 별도 승인을 받는다.

## Out Of Scope

신경 동역학 변경, 새로운 보정, #61의 에피소드 녹화, 학습, GPU 대여는 수행하지 않는다. #59의 진행 중 변경과 기존 결과물, 원본 프로젝트를 변경하거나 덮어쓰지 않는다.

## Rights Decision

사용자는 flysim이 자신의 작성물임을 재확인하고 이를 FlyTracker로 옮기도록 명시했다. 이 작성 확인과 포함 지시를 코드 공개의 근거로 기록한다. 코드 전체에 외부 프로젝트의 MIT를 자동 적용하거나 새 독립 라이선스를 임의 부여하지 않는다.

FlyWire 공식 가이드는 v783 공개 자료에 CC BY-NC 4.0을 명시하며 공개 범위에 주석과 후속 주석도 포함한다. 고정 주석 README는 해당 저장소를 v783 공개 자료로 설명한다. 이 두 근거로 주석 및 주석에서 선별한 가공물을 비영리 조건부 자료로 포함한다. 개별 TSV에 별도 LICENSE가 없고 2024 논문 부속 파일과 다른 갱신본이라는 사실도 명시한다. 논문의 CC BY 4.0으로 갱신본의 조건을 대체하지 않는다. 앞선 조사에서 LICENSE 파일 부재를 이유로 공식 공개 자료 조건의 적용까지 배제했던 판단을 정정한다.

Parquet의 직접 확보처는 philshiu/Drosophila_brain_model의 고정 commit이다. Git blob 해시가 로컬과 일치한다. MIT 원문을 보존하고, Zenodo 10676866은 관련 FlyWire 원자료의 참고 출처로 구분한다. 이 record의 파일 목록에 현재 Parquet는 없다.

## Done Criteria

- [x] 입력 후보 13개의 원본 및 공개 에피소드 해시 일치와 크기를 기록한다.
- [x] 기본 동봉 및 명시적 override 경로를 검증한다.
- [x] 기록 및 config에 동봉 절대 경로가 남지 않는지 검증한다.
- [x] 환경 변수가 없는 전체 pytest 결과를 기록한다.
- [x] 독립 새 폴더에서 요청한 설치 및 no-save 실행 명령을 확인한다.
- [x] 권리, 출처, 인용, README와 원본 확보 문서를 갱신한다.
- [x] 최종 변경을 제시하고 커밋 승인을 받는다.
- [x] push 및 PR 생성 전에 별도 승인을 받는다.
- [x] 병합 승인을 받고 진행 중 포인터를 제거하며 완료 상태를 기록한다.

## Current State

구현과 검증을 완료하고 사용자 승인에 따라 개인 Fork에 push한 뒤 [PR #65](https://github.com/SMU-ReinforementLearning/FlyTracker/pull/65)를 만들었다. 사용자가 병합도 승인했다. 이 마감 커밋에서 AGENTS의 #64 진행 중 포인터를 제거하고 완료 상태를 기록한다. 마감 커밋 push 뒤 검증한 Head를 지정해 squash 병합한다. 환경 변수 없는 전체 검사는 199개 통과, 2개 건너뜀이며 독립 새 폴더 실행은 exit 0이다. 원본 13개의 해시는 기존 공개 에피소드와 모두 일치한다. 원본과 #59 작업은 보존하며 브랜치와 worktree 삭제는 하지 않는다.

## Work Log

### feature: 신경 비행 코드와 자료를 저장소에 포함 (#64)

- 승인: 파일별 크기와 권리 조건, 변경 목록, 검증 결과를 보고한 뒤 사용자가 ‘진행해’라고 승인했다. 이번 승인 범위는 로컬 커밋이다.
- 변경: 사용자 작성 flysim 코드 5개와 계산 및 출처 기록에 필요한 자료를 포함한다. 환경 변수 없는 기본 경로와 기록용 상대 식별자를 추가하고 기존 외부 경로 옵션을 보존한다. NOTICE, MANIFEST, README와 원본 확보 안내를 갱신한다.
- 테스트: 환경 변수 없이 전체 pytest 199개 통과, 0개 실패, 2개 건너뜀. 핵심 조건 검사 13개 통과. 기존 실패 4개는 현재 관측 및 포획 조건에 맞게 수정했다.
- 독립 실행: 새 폴더와 가상환경에서 `uv sync --extra neural --extra dev`와 요청한 신경 기준선 `--no-save` 실행이 모두 exit 0이다. 포획 1/1, 평균 보상 -24.88, 보인 비율 28%, 포획까지 평균 5.32초다.
- 무결성: 포함한 원본 13개의 SHA-256이 원본 프로젝트 및 공개 에피소드와 일치한다. `.gitattributes`에 따른 Git 저장 바이트도 13개 모두 확인했다. 원본, 기준선, 공개 에피소드 및 #59 작업을 보존한다.
- 범위: 신경 동역학 변경, 녹화, 학습, GPU 대여는 하지 않는다. push 및 PR은 별도 승인 대상이다.

### docs: 신경 비행 포함 작업의 병합 준비 마감 (#64)

- 승인: 사용자가 커밋, push와 PR 생성에 이어 ‘머지까지 해’라고 명시했다. 병합 절차에 필요한 문서 마감을 수행한다.
- 변경: AGENTS의 #64 진행 중 포인터를 제거하고 이 문서의 완료 상태, PR 주소와 승인 기록을 갱신한다. 코드와 자료에는 변경이 없다.
- 검증: PR #65의 Head가 7b52017이며 main 대상 MERGEABLE/CLEAN 상태임을 확인했다. 등록된 리뷰와 CI 검사는 없고 squash 병합을 허용한다. 구현 검증은 199개 통과, 2개 건너뜀 결과를 유지한다. 마감 변경에는 Git hook과 공백 검사를 적용한다.
- 병합: 이 마감 커밋을 push한 뒤 해당 Head를 일치 조건으로 지정해 PR을 squash 병합한다. 관리자 우회, 강제 push, 브랜치 및 worktree 삭제는 수행하지 않는다. 병합 결과와 이슈 종료는 GitHub에서 확인하고 post-pr-cleanup은 dry-run만 실행한다.

## Management Notes

### 파일별 포함 판단

경로는 `flytracker/neural_assets` 기준이다. ‘해시만’은 계산에 사용하지 않는다는 뜻이며 MIT LICENSE는 배포 조건 때문에 함께 보존한다.

| 파일 | bytes | 실제 사용 | 권리 판단과 필요한 고지 |
|---|---:|---|---|
| flysim/core.py | 2,936 | 실행 코드 | 올려도 됨: 작성자의 직접 포함 지시. 외부 MIT를 전체 코드에 자동 적용하지 않음 |
| flysim/neural.py | 4,946 | 실행 코드 | 올려도 됨: 위와 같음 |
| flysim/neural_state.py | 4,374 | 실행 코드 | 올려도 됨: 위와 같음 |
| flysim/physics.py | 3,963 | 실행 코드 | 올려도 됨: 위와 같음 |
| flysim/behavior.py | 11,818 | 실행 코드 | 올려도 됨: 위와 같음 |
| data/stage2/neurons.csv | 22,842 | 기본 회로 계산 | 조건부: 주석의 출처, 선별 가공 사실, 저작자표시 및 비영리 조건 |
| data/stage2/edges.csv | 408,743 | 기본 회로 계산 | 조건부: MIT 고지와 주석 기반 선별의 비영리 조건 |
| data/stage2/selection.json | 4,035 | 해시만 | 조건부: 주석 기반 선별 집계로 같은 조건 적용 |
| data/stage2/zenodo_licenses.json | 95 | 해시만 | 올려도 됨: 출처 라이선스 식별자 기록. 다른 파일의 허가를 대신하지 않음 |
| data/raw/manifest.json | 2,719 | 해시만 | 올려도 됨: 확보 URL, commit 및 해시 기록 |
| data/raw/Drosophila_brain_model/LICENSE | 1,085 | 해시만, 필수 고지 | 조건부: MIT 원문 보존 |
| data/raw/Drosophila_brain_model/Connectivity_783.parquet | 100,804,642 | 확장 회로 계산 | 조건부: 고정 Shiu 저장소의 MIT 원문 동봉 |
| data/raw/flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv | 31,720,298 | 확장 회로 계산 | 조건부: v783 공식 안내에 근거한 CC BY-NC 4.0 및 인용 |

코드 5개와 CSV 2개는 `load_backend`가 읽는다. 두 원자료는 이어서 `expand_flight_network`가 읽는다. CSV의 273개 뉴런과 9,495개 연결을 현재 모델의 547개 뉴런과 16,344개 연결로 확장하므로 두 원자료는 필수다. 전체 연결을 다른 형식으로 다시 가공하거나 모델을 축소하는 변경은 이번 범위에서 하지 않았다.

원본 13개의 합계는 132,992,496 bytes다. 최대 파일은 십진 단위로 100.805MB지만 96.135MiB이므로 [GitHub의 실제 차단 기준인 100MiB](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) 이내다. 50MiB 경고 대상이며 저장소 다운로드 용량은 증가한다. LFS나 외부 다운로드를 요구하지 않는다. 파일별 전체 SHA-256과 공개 에피소드의 대응 키는 [MANIFEST.json](../../../flytracker/neural_assets/MANIFEST.json)에 있다. 13개 모두 원본 및 공개 포획 에피소드와 일치한다.

뉴런 CSV의 `id`는 TSV의 `root_id`에서 오며 `cell_type, side, top_nt, top_nt_conf`를 보존한다. `selection, excluded_in_synapses, excluded_out_synapses`는 선별 및 연결 집계로 추가한다. 연결 CSV의 `pre, post, synapse_count, source_model_sign`은 Parquet의 `Presynaptic_ID, Postsynaptic_ID, Connectivity, Excitatory`에서 온다. 대상 뉴런 선정에 주석을 쓰므로 연결 CSV에도 주석의 조건을 보수적으로 유지한다.

### 변경 범위

- `flytracker/neural_assets/`: 원본 13개와 NOTICE, MANIFEST를 직접 포함한다. 원본의 코드와 자료를 수정하지 않는다.
- `flytracker/neural_fly.py`: 기본 동봉 경로, 명시적 경로 우선순위와 기록용 상대 식별자를 추가한다. 신경 계산, 감각, 운동 및 비행 수식은 변경하지 않는다.
- `flytracker/env.py`: 신경 설정을 직렬화할 때 내부 절대 경로를 제거한다.
- `scripts/_common.py`: 경로 옵션의 도움말을 갱신한다.
- `.gitattributes`: 동봉 파일의 Git 줄바꿈 변환을 막는다. 대표 코드, CSV, Parquet 모두 `text: unset`을 확인했다.
- 기존 신경 테스트 6개 파일에서 외부 경로 부재에 따른 건너뜀을 제거한다.
- `tests/test_neural_fly.py`, `tests/test_neuromechanics.py`: 현재 관측 및 포획 조건에 맞춰 4개 오래된 테스트를 고친다.
- `tests/conftest.py`: 시간 순서 시험 전용 정답 조준 fixture를 추가한다. 실제 초파리는 비행하며 조준기만 5ms마다 맞춘다. 정책 성능 시험으로 해석하지 않는다.
- `tests/test_bundled_neural_assets.py`: 기본 경로, 외부 override, Windows 경로, 잘못된 경로, 파일 해시, 기록과 설정의 절대 경로 제거, 외부 복사본과의 계산 동등성을 검사한다.
- README, #31의 원본 확보 문서, 이 문서와 관리 색인을 갱신한다. AGENTS에는 새 작업의 포인터 한 줄만 추가한다.

### 검증 결과

2026-11-16 Windows, CPython 3.12.16, NumPy 2.5.4, Gymnasium 1.4.0, PyArrow 26.0.1, pytest 9.2.0에서 확인했다. 작업 전 기준은 upstream/main@31d64cb이며, 이전 main에서 늘어난 viewer 테스트도 포함한다.

| 조건 | 통과 | 실패 | 건너뜀 | 실행 시간 |
|---|---:|---:|---:|---:|
| 작업 전, 외부 원본 환경 변수 없음 | 145 | 0 | 47 | 14.38초 |
| 작업 전, 기존 외부 원본 지정 | 186 | 4 | 2 | 88.78초 |
| 수정 후 핵심 조건 검사 | 13 | 0 | 0 | 11.05초 |
| 수정 후 전체 검사, 환경 변수 없음 | 199 | 0 | 2 | 88.24초 |

전체 명령은 `uv run python -m pytest -q`이다. pytest 임시 파일은 작업별 ignored runs 경로에 두고 cacheprovider를 끈 상태에서 실행했다. 남은 2개 건너뜀은 `tests/test_players.py`의 Stable-Baselines3 선택 의존성 검사다. 신경 원본 부재를 이유로 건너뛴 시험은 없다. 4개 기존 실패는 13차원 관측 기대 1개와 과거 포획 조건 기대 3개였으며 동작을 바꾸거나 실패를 숨기는 건너뜀을 추가하지 않았다.

핵심 검사에는 저장된 config 및 에피소드의 모든 문자열을 순회하는 절대 경로 검사와 설정 복원이 포함된다. 동봉 폴더 전체를 독립 경로에 복사해 같은 seed 17로 초기화하고 50ms 비행한 결과, 위치, 방향, 속도, quaternion, 각속도와 신경 전압, 시냅스 상태, 지연 큐, 발화 계수 및 RNG 상태가 정확히 일치했다. 원본 보존 검사는 파일 크기와 수정 시각도 확인한다.

최초 추가 테스트에서 Windows 경로 문자열에 역슬래시를 두 번 넣은 시험 입력 오류를 발견해 실제 단일 역슬래시 경로로 고쳤다. 최종 13개 핵심 검사와 전체 회귀 검사는 그 수정 뒤의 결과다.

### 새 폴더 실행

추적 파일과 새 포함 파일 1,603개를 독립 임시 폴더에 복사했다. 원본 프로젝트와 기존 가상환경은 공유하지 않았다. `FLYTRACKER_NEURAL_SOURCE`, `PYTHONPATH`, `VIRTUAL_ENV`, uv 환경 경로 설정을 제거하고 새 가상환경을 만들었다. import 위치도 새 폴더의 `flytracker/__init__.py`임을 확인했다. 검사 당시 미커밋 상태였으므로 원격 clone 검사는 아니며, 검토 대상 파일을 별도 새 폴더에 받은 조건의 검사다.

```powershell
uv sync --extra neural --extra dev
uv run python scripts/record_baseline.py --fly-model neural --episodes 1 --seed 10000 --no-save
```

두 명령 모두 exit 0이다. 첫 명령의 출력은 아래와 같으며, 컴퓨터별 임시 절대 경로만 `<새 폴더>`로 바꿔 적었다.

```text
Using CPython 3.12.16
Creating virtual environment at: .venv
Resolved 76 packages in 1ms
   Building flytracker @ file:///<새 폴더>
      Built flytracker @ file:///<새 폴더>
Prepared 1 package in 1.91s
Installed 13 packages in 749ms
 + cloudpickle==3.1.2
 + colorama==0.4.6
 + farama-notifications==0.0.6
 + flytracker==0.1.0 (from file:///<새 폴더>)
 + gymnasium==1.4.0
 + iniconfig==2.3.1
 + numpy==2.5.4
 + packaging==26.3
 + pluggy==1.7.0
 + pyarrow==26.0.1
 + pygments==2.21.0
 + pytest==9.2.0
 + typing-extensions==4.16.0
```

두 번째 명령의 실제 표준 출력이다.

```text
포획 1/1, 평균 보상 -24.88, 보인 비율 28%, 포획까지 평균 5.32초
```

현재 빔 거리 1.25mm, 유지 0.15초 조건에서 오류 없이 종료했다. `--no-save`이므로 새 에피소드는 저장하지 않았다. #61의 실제 녹화, SAC 평가, 학습 및 GPU 대여는 수행하지 않았다. 원본 출력 로그는 ignored `runs/bundle-audit-09f3301c/`에 보관하며 commit 대상에서 제외한다.

### 남은 사항

사용자 승인에 따라 커밋 7b52017을 개인 Fork에 push하고 PR #65를 생성했다. 병합 승인도 받아 마감 문서 반영 뒤 squash 병합한다. 원격 push는 성공했으며 96.13MiB Parquet에 대한 GitHub 권장 크기 경고가 있었다. 큰 자료 때문에 clone 비용이 늘며 향후 자료 변경도 이력을 증가시킨다. 주석 저장소의 개별 LICENSE 부재와 공식 v783 조건을 적용한 근거는 NOTICE에 명시했다. 상업적 사용 허가나 모든 코드의 독립 MIT 라이선스를 확인한 것으로 표시하지 않는다.

생물 행동 일치, 신경 가중치 학습, 장시간 안정성 및 성능 향상은 이번 포함 작업의 검증 범위가 아니다. 기존 원본 프로젝트, 공개 에피소드, 기준선과 #59의 미커밋 작업은 변경하지 않았다.


### References
- [FlyWire 공개 자료 및 인용 안내](https://flywire.ai/guidelines)
- [주석 고정 버전](https://github.com/flyconnectome/flywire_annotations/tree/a83b2776d60d5764cef36b927f5f9679c16c47a2)
- [Shiu 모델 고정 버전](https://github.com/philshiu/Drosophila_brain_model/tree/91bdd1e7dcf193f3e7ca5a8933497fcef63b7960)
- [Zenodo 연결 자료](https://zenodo.org/records/10676866)
