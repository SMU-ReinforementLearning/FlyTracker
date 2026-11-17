== sha256
0f577c4c706f728dccaa660ab6c7640e4eeb69c84e112ddcc29d8396d5f3669b *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth.csv
70a62ab3d45dc31d10524a514587e59edec48bed0e217f0d3cb32b9559808b1c *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/baseline.csv
949f5e39c066333052ef02cc9d82fc26d57d89f6c55defaff41f877744782b58 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire.csv
0db1f1b35e0ad782fa0622a46015012b45215471f8c7de68b31a78b74b911e42 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/rule-fly/sac-beam-assist-s0/gate.csv
b214ad7548e04ade5c35bf991ae526c41941e9e938812ccef390ed36cd20fd0a *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/rule-fly/sac-beam-assist-s1/gate.csv
393a7638c63f0df1031125059d6befc199ff27870d037af0c78270e507dee352 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/rule-fly/sac-beam-assist-s2/gate.csv

########## pooled vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire.csv` (sha256 949f5e39c066)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.12 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 3.0256 | -1.8687 | -1.8684 | [-2.1606, -1.5598] | 1.000 |
| **macro** | 4.8943 | 3.0256 | -1.8687 | -1.8684 | [-2.1606, -1.5598] | 1.000 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (1.000)

########## pooled vs baseline: capture (value = miss rate; reported)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire.csv` (sha256 949f5e39c066)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.11 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.0267 | +0.0167 | +0.0165 | [-0.0050, +0.0367] | 0.072 |
| **macro** | 0.0100 | 0.0267 | +0.0167 | +0.0165 | [-0.0050, +0.0367] | 0.072 |

########## pooled vs baseline: misfires (reported)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire.csv` (sha256 949f5e39c066)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.11 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 0.6000 | +0.1000 | +0.1003 | [-0.0683, +0.2617] | 0.122 |
| **macro** | 0.5000 | 0.6000 | +0.1000 | +0.1003 | [-0.0683, +0.2617] | 0.122 |

########## per model: sac-beam-assist-s0 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/rule-fly/sac-beam-assist-s0/gate.csv` (sha256 0db1f1b35e0a)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.12 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 3.0343 | -1.8600 | -1.8597 | [-2.1894, -1.5056] | 1.000 |
| **macro** | 4.8943 | 3.0343 | -1.8600 | -1.8597 | [-2.1894, -1.5056] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per model: sac-beam-assist-s1 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/rule-fly/sac-beam-assist-s1/gate.csv` (sha256 b214ad7548e0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.11 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 3.3563 | -1.5381 | -1.5375 | [-1.9016, -1.1521] | 1.000 |
| **macro** | 4.8943 | 3.3563 | -1.5381 | -1.5375 | [-1.9016, -1.1521] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per model: sac-beam-assist-s2 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/rule-fly/sac-beam-assist-s2/gate.csv` (sha256 393a7638c63f)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.12 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.6863 | -2.2080 | -2.2079 | [-2.5408, -1.8582] | 1.000 |
| **macro** | 4.8943 | 2.6863 | -2.2080 | -2.2079 | [-2.5408, -1.8582] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)
