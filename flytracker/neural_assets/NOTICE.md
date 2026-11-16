# 신경 실행 코드와 자료 고지

이 폴더는 FlyTracker가 기본으로 사용하는 신경 실행 구현과 자료다. 사용자 작성 코드와 외부 자료의 권리는 구분한다. 외부 경로 지정 없이 실행할 수 있으며 계산 동역학은 기존 #31 모델과 같다.

## 사용자 작성 코드

flysim/core.py, neural.py, neural_state.py, physics.py, behavior.py는 사용자가 외부 신경 모델 및 자료를 참고해 Codex로 작성했다고 확인한 코드다. 2026-11-16 작성자의 직접 요청으로 FlyTracker 안에 원본 바이트 그대로 포함했다. 외부 프로젝트의 MIT를 이 코드 전체의 독립 라이선스로 자동 적용하지 않는다. 별도의 포괄 라이선스를 임의로 부여하지 않았으며 작성자의 팀 실행 및 개발 요청에 따른 포함이다.

## 외부 연결 자료

Connectivity_783.parquet의 직접 확보처는 [philshiu/Drosophila_brain_model의 고정 버전](https://github.com/philshiu/Drosophila_brain_model/tree/91bdd1e7dcf193f3e7ca5a8933497fcef63b7960)이다. 로컬 파일과 upstream Git blob 해시 d386555d1a5f40ebfa1380bcb05b1fab044855fd가 같다. 해당 저장소의 [MIT 저작권 및 허가 고지](data/raw/Drosophila_brain_model/LICENSE)를 변경 없이 동봉했다. 고지의 저작권자는 Philip Shiu 및 Nico Spiller(2023)다.

[Zenodo 10676866](https://zenodo.org/records/10676866)은 관련 FlyWire 연결 자료의 별도 출처이고 CC BY 4.0이다. 이 record에 현재 Parquet 파일은 없으므로 직접 다운로드 출처로 표시하지 않는다. Parquet의 Excitatory 부호는 참고 모델의 해석이며 수용체 수준 실측 부호와 구분한다.

## 주석과 가공물

주석 TSV는 [a83b2776d60d5764cef36b927f5f9679c16c47a2](https://github.com/flyconnectome/flywire_annotations/tree/a83b2776d60d5764cef36b927f5f9679c16c47a2)의 원본이다. 이 버전의 README는 해당 자료를 v783 공개 자료로 설명한다. [FlyWire 공식 공개 및 인용 안내](https://flywire.ai/guidelines)는 v783 공개 자료와 주석에 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.ko)을 명시한다. 이 안내와 자료 범위 설명을 근거로 주석과 주석 기반 가공물을 저작자표시 및 비영리 조건부 자료로 함께 배포한다. 원저작자, 출처와 라이선스 링크를 보존하고, 가공 및 추가 변경을 표시해야 한다. 비영리 조건을 제거한 자료로 표시하지 않는다.

고정 저장소에는 개별 LICENSE가 없고 이 TSV는 2024 논문에 직접 첨부된 TSV와 다른 2026 갱신본이다. 이번 조건 판단은 공식 v783 안내와 저장소 설명에 근거한 적용이며, 개별 파일에 별도 라이선스 문구를 새로 발견했다고 주장하지 않는다. 2024 논문의 CC BY 4.0을 이 갱신본의 조건으로 대신 쓰지 않는다.

neurons.csv는 TSV의 root_id, cell_type, side, top_nt, top_nt_conf를 선택하고 선별 표시 및 제외 연결 수를 추가한 273개 뉴런 가공물이다. edges.csv는 Parquet의 Presynaptic_ID, Postsynaptic_ID, Connectivity, Excitatory에서 9,495개 연결을 선별했다. 대상 뉴런 선정에는 주석을 사용했다. selection.json에는 선별 규칙과 집계, manifest.json에는 원자료 확보 기록이 있다. 현재 실행은 원자료에서 회로를 547개 뉴런과 16,344개 연결로 확장하므로 CSV만으로 원자료를 대체할 수 없다. 실제 추출과 감각 및 운동 변환의 공학적 가정을 생물학적 실측으로 표시하지 않는다.

## 인용

- Shiu 등, A Drosophila computational brain model reveals sensorimotor processing. [Nature 2024](https://doi.org/10.1038/s41586-024-07763-9).
- Schlegel 등, Whole-brain annotation and multi-connectome cell typing of Drosophila. [Nature 2024](https://doi.org/10.1038/s41586-024-07686-5).
- Dorkenwald 등, Neuronal wiring diagram of an adult brain. [Nature 2024](https://doi.org/10.1038/s41586-024-07558-y).
- Matsliah 등, Neuronal parts list and wiring diagram for a visual system. [Nature 2024](https://doi.org/10.1038/s41586-024-07981-1).
- Berg 등, Sexual dimorphism in the complete Drosophila male central nervous system connectome. [Cell 2026](https://doi.org/10.1016/j.cell.2026.08.015).
- Tastekin 등, The complete gustatory connectome of adult Drosophila reveals how taste guides feeding, foraging, and social behavior. [Cell 2026](https://doi.org/10.1016/j.cell.2026.08.016).

## 크기와 무결성

MANIFEST.json에 포함한 원본 13개의 파일별 크기, SHA-256과 공개 에피소드 해시 일치 여부가 있다. 원본 합계는 132,992,496 bytes다. Parquet는 100,804,642 bytes, 즉 96.135MiB이며 GitHub의 100MiB 차단 기준 이내다. .gitattributes는 이 폴더의 바이트를 줄바꿈 자동 변환에서 제외한다. 기존 공개 에피소드의 해시를 맞추려고 원본을 고치지 않았다.
