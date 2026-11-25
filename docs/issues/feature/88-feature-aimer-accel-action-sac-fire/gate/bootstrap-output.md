== sha256
0f577c4c706f728dccaa660ab6c7640e4eeb69c84e112ddcc29d8396d5f3669b *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv
70a62ab3d45dc31d10524a514587e59edec48bed0e217f0d3cb32b9559808b1c *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv
447e5ccceec3cbff72c28f07fcc1c715752857c6abbe66f360f5052ae1919063 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv
3aa5986a6a010444e164d9e338b6e990a21faa1b88806489f7d9a3151a8d4271 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv
9996b2a30098ff52da88c1821e114f02d3bbe0bbf8c255d31800c78f7a091e38 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv
643920978d802e2582c930866fcee5829708ecefc733340164549042aec3428e *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv
835c488be6c0cb10cf8c6cfaeaaa26c53ac9a591351d33e4f745da506a44875f *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv
144cf7221dc9a6e052ef2aa11b002ca3d38b1aa69522befcea86c11fedd9e9e9 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/rate-rule-s0/gate.csv
9ab739087daac839e8a72da667b505d20eb89aca738f2236bc41c93559c950c3 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/rate-rule-s1/gate.csv
869ce881f98bf51acc6beb3dfa65f38f348bb835066e288491c2d99b6a7ea64e *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/rate-rule-s2/gate.csv
5f8a72d6d94cca424da60a40614d8a5fad06652bcb9a9bebc80038a684338a60 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-rule-s0/gate.csv
5d3c604c85005521c590e2bbfb39ad3aef2804e5746cf478f4e0048129385dac *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-rule-s1/gate.csv
0062db4a65ba73fd060a8fe75233e8d980cb98e94f1e849877c484b824482713 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-rule-s2/gate.csv
f01bd04023165f91a9fb262f709f4308c9499fd9ad8385ec14758743addc2faf *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv
edda5bc82512b1f9a63747e26b20dec0ff29ca04d7ea3b7062986addaae5d37b *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv
611fba486eac086105354cb9d0e94a14d4ddfdc514f624d7edcb45aaf1d44629 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv
4427073cc4f230917b1966fc18ca86a64b763a529dabe6b604bd055fbae92679 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m03-s0/gate.csv
d0f1e10673ebbbe91c940192cd6f4bc4084c3f4424e052d9c8f2236cd4d724b6 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m03-s1/gate.csv
580247d18697d3d4587a3436deeb92b54f3cdad42b36d15de5f3aa9fe7977e84 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m03-s2/gate.csv
b1d2e4e9bcfd6f305d38b7a1141b9eba24247da4d138a788017572ccf9b9e97b *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m10-s0/gate.csv
7f9379493696a82cd0f5030a59d577f48f098eab8977456c8e229269eb392e2c *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m10-s1/gate.csv
0ad5c9f2f14efff798fd3f4ed779d6838c13a4bd673b0a670a94ce26e1d5dafb *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m10-s2/gate.csv
949f5e39c066333052ef02cc9d82fc26d57d89f6c55defaff41f877744782b58 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv

########## GATE rate-rule vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 9.9675 | +5.0732 | +5.0723 | [+4.8696, +5.2718] | 0.000 |
| **macro** | 4.8943 | 9.9675 | +5.0732 | +5.0723 | [+4.8696, +5.2718] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## rate-rule vs baseline: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.9800 | +0.9700 | +0.9698 | [+0.9417, +0.9900] | 0.000 |
| **macro** | 0.0100 | 0.9800 | +0.9700 | +0.9698 | [+0.9417, +0.9900] | 0.000 |

########## rate-rule vs baseline: misfires (undecided if pooled misfires per episode > 1.00)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 19.5783 | +19.0783 | +19.0726 | [+18.2600, +19.8717] | 0.000 |
| **macro** | 0.5000 | 19.5783 | +19.0783 | +19.0726 | [+18.2600, +19.8717] | 0.000 |

########## per training seed: rate-rule-s0 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/rate-rule-s0/gate.csv` (sha256 144cf7221dc9)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 9.9385 | +5.0442 | +5.0433 | [+4.8353, +5.2492] | 0.000 |
| **macro** | 4.8943 | 9.9385 | +5.0442 | +5.0433 | [+4.8353, +5.2492] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: rate-rule-s1 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/rate-rule-s1/gate.csv` (sha256 9ab739087daa)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 9.9760 | +5.0817 | +5.0809 | [+4.8754, +5.2823] | 0.000 |
| **macro** | 4.8943 | 9.9760 | +5.0817 | +5.0809 | [+4.8754, +5.2823] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: rate-rule-s2 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/rate-rule-s2/gate.csv` (sha256 869ce881f98b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 9.9879 | +5.0936 | +5.0928 | [+4.8958, +5.2891] | 0.000 |
| **macro** | 4.8943 | 9.9879 | +5.0936 | +5.0928 | [+4.8958, +5.2891] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## GATE accel-rule vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 3.0215 | -1.8728 | -1.8714 | [-2.1370, -1.5912] | 1.000 |
| **macro** | 4.8943 | 3.0215 | -1.8728 | -1.8714 | [-2.1370, -1.5912] | 1.000 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (1.000)

########## accel-rule vs baseline: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.0350 | +0.0250 | +0.0250 | [+0.0083, +0.0433] | 0.002 |
| **macro** | 0.0100 | 0.0350 | +0.0250 | +0.0250 | [+0.0083, +0.0433] | 0.002 |

########## accel-rule vs baseline: misfires (undecided if pooled misfires per episode > 1.00)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 0.6867 | +0.1867 | +0.1866 | [-0.0067, +0.3717] | 0.030 |
| **macro** | 0.5000 | 0.6867 | +0.1867 | +0.1866 | [-0.0067, +0.3717] | 0.030 |

########## per training seed: accel-rule-s0 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-rule-s0/gate.csv` (sha256 5f8a72d6d94c)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 3.0304 | -1.8639 | -1.8634 | [-2.1770, -1.5231] | 1.000 |
| **macro** | 4.8943 | 3.0304 | -1.8639 | -1.8634 | [-2.1770, -1.5231] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: accel-rule-s1 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-rule-s1/gate.csv` (sha256 5d3c604c8500)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 3.0471 | -1.8473 | -1.8446 | [-2.1687, -1.4971] | 1.000 |
| **macro** | 4.8943 | 3.0471 | -1.8473 | -1.8446 | [-2.1687, -1.4971] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: accel-rule-s2 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-rule-s2/gate.csv` (sha256 0062db4a65ba)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.9869 | -1.9074 | -1.9062 | [-2.2568, -1.5393] | 1.000 |
| **macro** | 4.8943 | 2.9869 | -1.9074 | -1.9062 | [-2.2568, -1.5393] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## GATE accel-pen-rule vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.6114 | -2.2829 | -2.2825 | [-2.5372, -2.0240] | 1.000 |
| **macro** | 4.8943 | 2.6114 | -2.2829 | -2.2825 | [-2.5372, -2.0240] | 1.000 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (1.000)

########## accel-pen-rule vs baseline: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.0183 | +0.0083 | +0.0083 | [-0.0117, +0.0267] | 0.222 |
| **macro** | 0.0100 | 0.0183 | +0.0083 | +0.0083 | [-0.0117, +0.0267] | 0.222 |

########## accel-pen-rule vs baseline: misfires (undecided if pooled misfires per episode > 1.00)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 0.4717 | -0.0283 | -0.0284 | [-0.1984, +0.1333] | 0.631 |
| **macro** | 0.5000 | 0.4717 | -0.0283 | -0.0284 | [-0.1984, +0.1333] | 0.631 |

########## per training seed: accel-pen-rule-s0 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.8514 | -2.0429 | -2.0419 | [-2.3762, -1.6978] | 1.000 |
| **macro** | 4.8943 | 2.8514 | -2.0429 | -2.0419 | [-2.3762, -1.6978] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: accel-pen-rule-s1 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.5742 | -2.3201 | -2.3208 | [-2.6326, -2.0015] | 1.000 |
| **macro** | 4.8943 | 2.5742 | -2.3201 | -2.3208 | [-2.6326, -2.0015] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: accel-pen-rule-s2 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.4085 | -2.4858 | -2.4847 | [-2.7221, -2.2362] | 1.000 |
| **macro** | 4.8943 | 2.4085 | -2.4858 | -2.4847 | [-2.7221, -2.2362] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## GATE accel-fire-m03 vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |
| **macro** | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## accel-fire-m03 vs baseline: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 1.0000 | +0.9900 | +0.9899 | [+0.9750, +1.0000] | 0.000 |
| **macro** | 0.0100 | 1.0000 | +0.9900 | +0.9899 | [+0.9750, +1.0000] | 0.000 |

########## accel-fire-m03 vs baseline: misfires (undecided if pooled misfires per episode > 1.00)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 0.0067 | -0.4933 | -0.4935 | [-0.6400, -0.3650] | 1.000 |
| **macro** | 0.5000 | 0.0067 | -0.4933 | -0.4935 | [-0.6400, -0.3650] | 1.000 |

########## per training seed: accel-fire-m03-s0 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m03-s0/gate.csv` (sha256 4427073cc4f2)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |
| **macro** | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: accel-fire-m03-s1 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m03-s1/gate.csv` (sha256 d0f1e10673eb)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |
| **macro** | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: accel-fire-m03-s2 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m03-s2/gate.csv` (sha256 580247d18697)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |
| **macro** | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## GATE accel-fire-m10 vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |
| **macro** | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## accel-fire-m10 vs baseline: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 1.0000 | +0.9900 | +0.9899 | [+0.9750, +1.0000] | 0.000 |
| **macro** | 0.0100 | 1.0000 | +0.9900 | +0.9899 | [+0.9750, +1.0000] | 0.000 |

########## accel-fire-m10 vs baseline: misfires (undecided if pooled misfires per episode > 1.00)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 0.0067 | -0.4933 | -0.4935 | [-0.6400, -0.3667] | 1.000 |
| **macro** | 0.5000 | 0.0067 | -0.4933 | -0.4935 | [-0.6400, -0.3667] | 1.000 |

########## per training seed: accel-fire-m10-s0 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m10-s0/gate.csv` (sha256 b1d2e4e9bcfd)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |
| **macro** | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: accel-fire-m10-s1 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m10-s1/gate.csv` (sha256 7f9379493696)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |
| **macro** | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: accel-fire-m10-s2 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-fire-m10-s2/gate.csv` (sha256 0ad5c9f2f14e)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |
| **macro** | 4.8943 | 10.0000 | +5.1057 | +5.1050 | [+4.9094, +5.2978] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## descriptive: accel-rule (B) vs rate-rule (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 9.9675 | 3.0215 | -6.9460 | -6.9438 | [-7.1655, -6.7047] | 1.000 |
| **macro** | 9.9675 | 3.0215 | -6.9460 | -6.9438 | [-7.1655, -6.7047] | 1.000 |

########## descriptive: accel-rule (B) vs rate-rule (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.9800 | 0.0350 | -0.9450 | -0.9448 | [-0.9683, -0.9183] | 1.000 |
| **macro** | 0.9800 | 0.0350 | -0.9450 | -0.9448 | [-0.9683, -0.9183] | 1.000 |

########## descriptive: accel-rule (B) vs rate-rule (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 19.5783 | 0.6867 | -18.8917 | -18.8860 | [-19.6750, -18.0850] | 1.000 |
| **macro** | 19.5783 | 0.6867 | -18.8917 | -18.8860 | [-19.6750, -18.0850] | 1.000 |

########## descriptive: accel-pen-rule (B) vs accel-rule (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0215 | 2.6114 | -0.4101 | -0.4111 | [-0.5877, -0.2446] | 1.000 |
| **macro** | 3.0215 | 2.6114 | -0.4101 | -0.4111 | [-0.5877, -0.2446] | 1.000 |

########## descriptive: accel-pen-rule (B) vs accel-rule (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0350 | 0.0183 | -0.0167 | -0.0168 | [-0.0333, -0.0017] | 0.984 |
| **macro** | 0.0350 | 0.0183 | -0.0167 | -0.0168 | [-0.0333, -0.0017] | 0.984 |

########## descriptive: accel-pen-rule (B) vs accel-rule (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6867 | 0.4717 | -0.2150 | -0.2150 | [-0.3383, -0.0983] | 1.000 |
| **macro** | 0.6867 | 0.4717 | -0.2150 | -0.2150 | [-0.3383, -0.0983] | 1.000 |

########## descriptive: accel-fire-m03 (B) vs accel-rule (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0215 | 10.0000 | +6.9785 | +6.9764 | [+6.7406, +7.1923] | 0.000 |
| **macro** | 3.0215 | 10.0000 | +6.9785 | +6.9764 | [+6.7406, +7.1923] | 0.000 |

########## descriptive: accel-fire-m03 (B) vs accel-rule (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0350 | 1.0000 | +0.9650 | +0.9649 | [+0.9467, +0.9800] | 0.000 |
| **macro** | 0.0350 | 1.0000 | +0.9650 | +0.9649 | [+0.9467, +0.9800] | 0.000 |

########## descriptive: accel-fire-m03 (B) vs accel-rule (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6867 | 0.0067 | -0.6800 | -0.6801 | [-0.8150, -0.5583] | 1.000 |
| **macro** | 0.6867 | 0.0067 | -0.6800 | -0.6801 | [-0.8150, -0.5583] | 1.000 |

########## descriptive: accel-fire-m10 (B) vs accel-rule (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0215 | 10.0000 | +6.9785 | +6.9764 | [+6.7406, +7.1923] | 0.000 |
| **macro** | 3.0215 | 10.0000 | +6.9785 | +6.9764 | [+6.7406, +7.1923] | 0.000 |

########## descriptive: accel-fire-m10 (B) vs accel-rule (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0350 | 1.0000 | +0.9650 | +0.9649 | [+0.9467, +0.9800] | 0.000 |
| **macro** | 0.0350 | 1.0000 | +0.9650 | +0.9649 | [+0.9467, +0.9800] | 0.000 |

########## descriptive: accel-fire-m10 (B) vs accel-rule (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6867 | 0.0067 | -0.6800 | -0.6801 | [-0.8150, -0.5600] | 1.000 |
| **macro** | 0.6867 | 0.0067 | -0.6800 | -0.6801 | [-0.8150, -0.5600] | 1.000 |

########## descriptive: accel-fire-m10 (B) vs accel-fire-m03 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 10.0000 | 10.0000 | +0.0000 | +0.0000 | [+0.0000, +0.0000] | 0.500 |
| **macro** | 10.0000 | 10.0000 | +0.0000 | +0.0000 | [+0.0000, +0.0000] | 0.500 |

########## descriptive: accel-fire-m10 (B) vs accel-fire-m03 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 1.0000 | 1.0000 | +0.0000 | +0.0000 | [+0.0000, +0.0000] | 0.500 |
| **macro** | 1.0000 | 1.0000 | +0.0000 | +0.0000 | [+0.0000, +0.0000] | 0.500 |

########## descriptive: accel-fire-m10 (B) vs accel-fire-m03 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.0067 | 0.0067 | -0.0000 | -0.0000 | [-0.0133, +0.0100] | 0.509 |
| **macro** | 0.0067 | 0.0067 | -0.0000 | -0.0000 | [-0.0133, +0.0100] | 0.509 |

########## descriptive: rate-rule (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 9.9675 | +6.9418 | +6.9407 | [+6.7390, +7.1298] | 0.000 |
| **macro** | 3.0256 | 9.9675 | +6.9418 | +6.9407 | [+6.7390, +7.1298] | 0.000 |

########## descriptive: rate-rule (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 0.9800 | +0.9533 | +0.9533 | [+0.9317, +0.9733] | 0.000 |
| **macro** | 0.0267 | 0.9800 | +0.9533 | +0.9533 | [+0.9317, +0.9733] | 0.000 |

########## descriptive: rate-rule (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/rate-rule.csv` (sha256 447e5ccceec3)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 19.5783 | +18.9783 | +18.9723 | [+18.1816, +19.7600] | 0.000 |
| **macro** | 0.6000 | 19.5783 | +18.9783 | +18.9723 | [+18.1816, +19.7600] | 0.000 |

########## descriptive: accel-rule (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 3.0215 | -0.0042 | -0.0030 | [-0.1977, +0.1973] | 0.514 |
| **macro** | 3.0256 | 3.0215 | -0.0042 | -0.0030 | [-0.1977, +0.1973] | 0.514 |

########## descriptive: accel-rule (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 0.0350 | +0.0083 | +0.0085 | [-0.0083, +0.0250] | 0.173 |
| **macro** | 0.0267 | 0.0350 | +0.0083 | +0.0085 | [-0.0083, +0.0250] | 0.173 |

########## descriptive: accel-rule (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-rule.csv` (sha256 3aa5986a6a01)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 0.6867 | +0.0867 | +0.0863 | [-0.0517, +0.2267] | 0.108 |
| **macro** | 0.6000 | 0.6867 | +0.0867 | +0.0863 | [-0.0517, +0.2267] | 0.108 |

########## descriptive: accel-pen-rule (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 2.6114 | -0.4142 | -0.4141 | [-0.5755, -0.2573] | 1.000 |
| **macro** | 3.0256 | 2.6114 | -0.4142 | -0.4141 | [-0.5755, -0.2573] | 1.000 |

########## descriptive: accel-pen-rule (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 0.0183 | -0.0083 | -0.0083 | [-0.0250, +0.0067] | 0.869 |
| **macro** | 0.0267 | 0.0183 | -0.0083 | -0.0083 | [-0.0250, +0.0067] | 0.869 |

########## descriptive: accel-pen-rule (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 0.4717 | -0.1283 | -0.1287 | [-0.2533, +0.0000] | 0.975 |
| **macro** | 0.6000 | 0.4717 | -0.1283 | -0.1287 | [-0.2533, +0.0000] | 0.975 |

########## descriptive: accel-fire-m03 (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 10.0000 | +6.9744 | +6.9734 | [+6.7751, +7.1577] | 0.000 |
| **macro** | 3.0256 | 10.0000 | +6.9744 | +6.9734 | [+6.7751, +7.1577] | 0.000 |

########## descriptive: accel-fire-m03 (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 1.0000 | +0.9733 | +0.9733 | [+0.9567, +0.9867] | 0.000 |
| **macro** | 0.0267 | 1.0000 | +0.9733 | +0.9733 | [+0.9567, +0.9867] | 0.000 |

########## descriptive: accel-fire-m03 (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m03.csv` (sha256 643920978d80)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 0.0067 | -0.5933 | -0.5937 | [-0.6967, -0.4967] | 1.000 |
| **macro** | 0.6000 | 0.0067 | -0.5933 | -0.5937 | [-0.6967, -0.4967] | 1.000 |

########## descriptive: accel-fire-m10 (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 10.0000 | +6.9744 | +6.9734 | [+6.7751, +7.1577] | 0.000 |
| **macro** | 3.0256 | 10.0000 | +6.9744 | +6.9734 | [+6.7751, +7.1577] | 0.000 |

########## descriptive: accel-fire-m10 (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 1.0000 | +0.9733 | +0.9733 | [+0.9567, +0.9867] | 0.000 |
| **macro** | 0.0267 | 1.0000 | +0.9733 | +0.9733 | [+0.9567, +0.9867] | 0.000 |

########## descriptive: accel-fire-m10 (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-fire-m10.csv` (sha256 835c488be6c0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 0.0067 | -0.5933 | -0.5938 | [-0.6950, -0.4967] | 1.000 |
| **macro** | 0.6000 | 0.0067 | -0.5933 | -0.5938 | [-0.6950, -0.4967] | 1.000 |
