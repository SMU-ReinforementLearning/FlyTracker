== sha256
b31947f3e8ef7ce7e620a9ae56e264ef7da77b9fe145ff49c43a9260e9dbb196 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv
783c941dbbafa92e5f98d8331f7a447f374e8195d61765bd61e322cdb15f293f *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/baseline/gate.csv
1f9461b88c238ae3a84b2c1da7d88ea7090d9aeebf1951759bc11ccbeed7cc92 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire-neural-fly-nostim.csv
37b1094f3be0f1bdda4a77f9b1a31ae13e0711abf7b1d9309019c49604b25c52 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/sac-beam-assist-s0/gate.csv
5258cc4c4f96eaa828e58ac7dd758ec3fcd53070f912e20845f64e89b4ce734e *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/sac-beam-assist-s1/gate.csv
22ec602c59466e7f3ec9d03e2c2730acd9055cfbe8167a76685956dd95100ea7 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/sac-beam-assist-s2/gate.csv

########## pooled vs baseline: time (reported)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/baseline/gate.csv` (sha256 783c941dbbaf)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire-neural-fly-nostim.csv` (sha256 1f9461b88c23)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 5.1102 | 4.2583 | -0.8519 | -0.8529 | [-1.5584, -0.1141] | 0.989 |
| **macro** | 5.1102 | 4.2583 | -0.8519 | -0.8529 | [-1.5584, -0.1141] | 0.989 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (0.989)

########## pooled vs baseline: capture (value = miss rate; reported)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/baseline/gate.csv` (sha256 783c941dbbaf)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire-neural-fly-nostim.csv` (sha256 1f9461b88c23)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0167 | 0.1389 | +0.1222 | +0.1222 | [+0.0554, +0.1889] | 0.001 |
| **macro** | 0.0167 | 0.1389 | +0.1222 | +0.1222 | [+0.0554, +0.1889] | 0.001 |

########## pooled vs baseline: misfires (reported)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/baseline/gate.csv` (sha256 783c941dbbaf)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire-neural-fly-nostim.csv` (sha256 1f9461b88c23)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6167 | 1.9389 | +1.3222 | +1.3194 | [+0.8389, +1.8222] | 0.000 |
| **macro** | 0.6167 | 1.9389 | +1.3222 | +1.3194 | [+0.8389, +1.8222] | 0.000 |

########## per model: sac-beam-assist-s0 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/baseline/gate.csv` (sha256 783c941dbbaf)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/sac-beam-assist-s0/gate.csv` (sha256 37b1094f3be0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 5.1102 | 5.3513 | +0.2412 | +0.2425 | [-0.7057, +1.2178] | 0.320 |
| **macro** | 5.1102 | 5.3513 | +0.2412 | +0.2425 | [-0.7057, +1.2178] | 0.320 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.320)

########## per model: sac-beam-assist-s1 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/baseline/gate.csv` (sha256 783c941dbbaf)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/sac-beam-assist-s1/gate.csv` (sha256 5258cc4c4f96)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 5.1102 | 3.8712 | -1.2390 | -1.2398 | [-1.9872, -0.4225] | 0.999 |
| **macro** | 5.1102 | 3.8712 | -1.2390 | -1.2398 | [-1.9872, -0.4225] | 0.999 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (0.999)

########## per model: sac-beam-assist-s2 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/baseline/gate.csv` (sha256 783c941dbbaf)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-nostim/sac-beam-assist-s2/gate.csv` (sha256 22ec602c5946)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 5.1102 | 3.5523 | -1.5578 | -1.5614 | [-2.3780, -0.6753] | 1.000 |
| **macro** | 5.1102 | 3.5523 | -1.5578 | -1.5614 | [-2.3780, -0.6753] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)
