== sha256
4aec8f8eecf6074d73e37bdd132b6c54b00cd2cd3113e46ed57e2ea36b06b08d *docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv
87157690c9fff6266319ee70bcb64d1bd0ca6d3f173ba6b5b9ce666dfd2e5178 *docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1.csv
3b6869d1b8684a405f0b6f1cfd13e7915fb6cd757ecdf4de76af46030cf7c5ba *docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1-s0.csv
54622a2ee46fed6016ab14be8702e9a1639fef44c4abcdacdade53cd079d19ec *docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1-s1.csv
fcaca01b249d5e226d1dc00f2f01fd0f39447dfecadd5dd642daf9400529a367 *docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1-s2.csv
51ab848c61163b3507533668aa5df97711e201d208a40ebcd82ca95a14455519 *docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4.csv
86c30eecf606c4a95d5118c5699106ee34a837c9c955b5dd520a99021a7dd380 *docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4-s0.csv
dc676f615b401892191cad3ccc9319f45b5afb14b791a366585c30cd6ec3fcca *docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4-s1.csv
02abbc5c6b6867d7da7c5fcca87c7291a892dede4261f9bea8442c35335ad58e *docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4-s2.csv
630ec5b311a118169c3d0a5872638c13680f0a02d3f509cf98f52238aad98089 *docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv

########## GATE sac-fs1 vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1.csv` (sha256 87157690c9ff)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.3 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.1836 | -1.9163 | -1.9150 | [-2.1957, -1.6234] | 1.000 |
| **macro** | 4.0999 | 2.1836 | -1.9163 | -1.9150 | [-2.1957, -1.6234] | 1.000 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (1.000)

########## sac-fs1 vs baseline: capture (reported; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1.csv` (sha256 87157690c9ff)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0050 | 0.0200 | +0.0150 | +0.0151 | [-0.0033, +0.0350] | 0.055 |
| **macro** | 0.0050 | 0.0200 | +0.0150 | +0.0151 | [-0.0033, +0.0350] | 0.055 |

########## per training seed: sac-fs1-s0 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1-s0.csv` (sha256 3b6869d1b868)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.7278 | -1.3721 | -1.3699 | [-1.7742, -0.9515] | 1.000 |
| **macro** | 4.0999 | 2.7278 | -1.3721 | -1.3699 | [-1.7742, -0.9515] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: sac-fs1-s1 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1-s1.csv` (sha256 54622a2ee46f)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.1 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 1.8014 | -2.2985 | -2.2986 | [-2.5776, -2.0079] | 1.000 |
| **macro** | 4.0999 | 1.8014 | -2.2985 | -2.2986 | [-2.5776, -2.0079] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: sac-fs1-s2 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1-s2.csv` (sha256 fcaca01b249d)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.1 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.0217 | -2.0782 | -2.0765 | [-2.3538, -1.7741] | 1.000 |
| **macro** | 4.0999 | 2.0217 | -2.0782 | -2.0765 | [-2.3538, -1.7741] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## GATE sac-fs4 vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4.csv` (sha256 51ab848c6116)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.1232 | -1.9767 | -1.9762 | [-2.2707, -1.6688] | 1.000 |
| **macro** | 4.0999 | 2.1232 | -1.9767 | -1.9762 | [-2.2707, -1.6688] | 1.000 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (1.000)

########## sac-fs4 vs baseline: capture (reported; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4.csv` (sha256 51ab848c6116)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.1 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0050 | 0.0283 | +0.0233 | +0.0233 | [+0.0033, +0.0450] | 0.013 |
| **macro** | 0.0050 | 0.0283 | +0.0233 | +0.0233 | [+0.0033, +0.0450] | 0.013 |

########## per training seed: sac-fs4-s0 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4-s0.csv` (sha256 86c30eecf606)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.1561 | -1.9438 | -1.9444 | [-2.3154, -1.5511] | 1.000 |
| **macro** | 4.0999 | 2.1561 | -1.9438 | -1.9444 | [-2.3154, -1.5511] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: sac-fs4-s1 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4-s1.csv` (sha256 dc676f615b40)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.1523 | -1.9476 | -1.9467 | [-2.2612, -1.6161] | 1.000 |
| **macro** | 4.0999 | 2.1523 | -1.9476 | -1.9467 | [-2.2612, -1.6161] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: sac-fs4-s2 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/baseline.csv` (sha256 4aec8f8eecf6)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4-s2.csv` (sha256 02abbc5c6b68)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.0999 | 2.0612 | -2.0387 | -2.0376 | [-2.3167, -1.7370] | 1.000 |
| **macro** | 4.0999 | 2.0612 | -2.0387 | -2.0376 | [-2.3167, -1.7370] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## descriptive: sac-fs4 (B) vs sac-fs1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1.csv` (sha256 87157690c9ff)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4.csv` (sha256 51ab848c6116)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.1836 | 2.1232 | -0.0604 | -0.0612 | [-0.1851, +0.0642] | 0.832 |
| **macro** | 2.1836 | 2.1232 | -0.0604 | -0.0612 | [-0.1851, +0.0642] | 0.832 |

########## descriptive: sac-fs4 (B) vs sac-fs1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/35-feature-sac-aimer-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs1.csv` (sha256 87157690c9ff)
- B (candidate): `docs/issues/feature/35-feature-sac-aimer-training/gate/sac-fs4.csv` (sha256 51ab848c6116)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0200 | 0.0283 | +0.0083 | +0.0083 | [-0.0050, +0.0233] | 0.118 |
| **macro** | 0.0200 | 0.0283 | +0.0083 | +0.0083 | [-0.0050, +0.0233] | 0.118 |
