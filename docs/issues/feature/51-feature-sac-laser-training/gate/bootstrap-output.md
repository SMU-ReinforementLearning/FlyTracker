== sha256
6ac2f0bd223aea7cd0d1850ae48e7ed624ccfe8b345f02352d6ade3961e259ae *docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv
fa4c60055ed85bb137ac72eb3160cea52b19b6563e30029526a2ba57636baf48 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle.csv
75cd279289a41dab5fbd2d0ae750c08c59b14dfff99a6e7333c2c5260a5d13b8 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist.csv
cf911b765d1c95fdf136421be8f422644c8a69c87093134371e8a52289794085 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist-s0.csv
31ac61743274882795fd966821796d144356e032a60c0fdbb4f5c62ceca3924d *docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist-s1.csv
fcb99592ae4ceb6f8455950dd1850fc4f7b198591bb0401e563d90ca940c8185 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist-s2.csv
009075a49eef3d9dd7b43c81e81a80363107c957600228ac05cdb89117506dce *docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-s0.csv
14e04e054d9a99b9e2702648ef0ee388ed0e0eb73397ebf387658c28864d7107 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-s1.csv
900885c6fe5eaeb7828946098955c4b03aed98d5ef7a0328d21795f8689ce85e *docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-s2.csv
928d96dc4ace338f36f1d2e57c31f234410206090a45e1977bec72ef34c35741 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam.csv
3647d84876df3a5018a5337107592a4ea21e7b7f5cc3f21850eb8015e2b1aae9 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist.csv
9e2bc608ecccf1dc3d1078c265f072f8f432edaaa0b53bee5c1a8a87228066f4 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist-s0.csv
4bd2a9befc8af35da8ae44686063c3b981b16b5fc1d20c3bb09ee2e142e350f1 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist-s1.csv
2233075631ec7e13bd9d287b1fc1ab1b6afbc184938d3c947b7939d5969360e5 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist-s2.csv
aad5b1100b77de18f03b9583dac0606c9fa8bba4b2119b6a4f0adb89aa986b8b *docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-s0.csv
dec7a27ac1f75d4d58727b3f82ca8c8fe93b9f756ec5343c195f0748963a87f7 *docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-s1.csv
3e83a32b504873ab34666a5a843eb5de0831a44d7283668296f258c64b0d1e7b *docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-s2.csv
630ec5b311a118169c3d0a5872638c13680f0a02d3f509cf98f52238aad98089 *docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv

########## GATE sac-beam vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam.csv` (sha256 928d96dc4ace)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.1 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.9191 | +5.0613 | +5.0607 | [+4.8528, +5.2649] | 0.000 |
| **macro** | 4.8579 | 9.9191 | +5.0613 | +5.0607 | [+4.8528, +5.2649] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## sac-beam vs baseline: capture (reported; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam.csv` (sha256 928d96dc4ace)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.9650 | +0.9550 | +0.9549 | [+0.9267, +0.9783] | 0.000 |
| **macro** | 0.0100 | 0.9650 | +0.9550 | +0.9549 | [+0.9267, +0.9783] | 0.000 |

########## per training seed: sac-beam-s0 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-s0.csv` (sha256 aad5b1100b77)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.9179 | +5.0600 | +5.0592 | [+4.8489, +5.2647] | 0.000 |
| **macro** | 4.8579 | 9.9179 | +5.0600 | +5.0592 | [+4.8489, +5.2647] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: sac-beam-s1 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-s1.csv` (sha256 dec7a27ac1f7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.8911 | +5.0332 | +5.0327 | [+4.8012, +5.2509] | 0.000 |
| **macro** | 4.8579 | 9.8911 | +5.0332 | +5.0327 | [+4.8012, +5.2509] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: sac-beam-s2 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-s2.csv` (sha256 3e83a32b5048)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.9484 | +5.0905 | +5.0901 | [+4.8890, +5.2892] | 0.000 |
| **macro** | 4.8579 | 9.9484 | +5.0905 | +5.0901 | [+4.8890, +5.2892] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## GATE sac-angle vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle.csv` (sha256 fa4c60055ed8)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.9813 | +5.1234 | +5.1228 | [+4.9253, +5.3181] | 0.000 |
| **macro** | 4.8579 | 9.9813 | +5.1234 | +5.1228 | [+4.9253, +5.3181] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## sac-angle vs baseline: capture (reported; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle.csv` (sha256 fa4c60055ed8)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.9950 | +0.9850 | +0.9849 | [+0.9683, +0.9983] | 0.000 |
| **macro** | 0.0100 | 0.9950 | +0.9850 | +0.9849 | [+0.9683, +0.9983] | 0.000 |

########## per training seed: sac-angle-s0 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-s0.csv` (sha256 009075a49eef)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.9773 | +5.1194 | +5.1189 | [+4.9173, +5.3170] | 0.000 |
| **macro** | 4.8579 | 9.9773 | +5.1194 | +5.1189 | [+4.9173, +5.3170] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: sac-angle-s1 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-s1.csv` (sha256 14e04e054d9a)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 10.0000 | +5.1421 | +5.1414 | [+4.9469, +5.3340] | 0.000 |
| **macro** | 4.8579 | 10.0000 | +5.1421 | +5.1414 | [+4.9469, +5.3340] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: sac-angle-s2 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-s2.csv` (sha256 900885c6fe5e)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.9665 | +5.1087 | +5.1082 | [+4.9040, +5.3087] | 0.000 |
| **macro** | 4.8579 | 9.9665 | +5.1087 | +5.1082 | [+4.9040, +5.3087] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## GATE sac-beam-assist vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist.csv` (sha256 3647d84876df)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 2.9413 | -1.9165 | -1.9164 | [-2.2022, -1.6140] | 1.000 |
| **macro** | 4.8579 | 2.9413 | -1.9165 | -1.9164 | [-2.2022, -1.6140] | 1.000 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (1.000)

########## sac-beam-assist vs baseline: capture (reported; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist.csv` (sha256 3647d84876df)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.0250 | +0.0150 | +0.0149 | [-0.0067, +0.0350] | 0.089 |
| **macro** | 0.0100 | 0.0250 | +0.0150 | +0.0149 | [-0.0067, +0.0350] | 0.089 |

########## per training seed: sac-beam-assist-s0 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist-s0.csv` (sha256 9e2bc608eccc)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 2.9947 | -1.8631 | -1.8630 | [-2.1952, -1.5068] | 1.000 |
| **macro** | 4.8579 | 2.9947 | -1.8631 | -1.8630 | [-2.1952, -1.5068] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: sac-beam-assist-s1 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist-s1.csv` (sha256 4bd2a9befc8a)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 3.1988 | -1.6591 | -1.6590 | [-2.0068, -1.2897] | 1.000 |
| **macro** | 4.8579 | 3.1988 | -1.6591 | -1.6590 | [-2.0068, -1.2897] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per training seed: sac-beam-assist-s2 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist-s2.csv` (sha256 2233075631ec)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 2.6305 | -2.2273 | -2.2272 | [-2.5507, -1.8920] | 1.000 |
| **macro** | 4.8579 | 2.6305 | -2.2273 | -2.2272 | [-2.5507, -1.8920] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## GATE sac-angle-assist vs baseline: time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist.csv` (sha256 75cd279289a4)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 8.9764 | +4.1185 | +4.1179 | [+3.8679, +4.3689] | 0.000 |
| **macro** | 4.8579 | 8.9764 | +4.1185 | +4.1179 | [+3.8679, +4.3689] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## sac-angle-assist vs baseline: capture (reported; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist.csv` (sha256 75cd279289a4)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.7883 | +0.7783 | +0.7783 | [+0.7433, +0.8117] | 0.000 |
| **macro** | 0.0100 | 0.7883 | +0.7783 | +0.7783 | [+0.7433, +0.8117] | 0.000 |

########## per training seed: sac-angle-assist-s0 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist-s0.csv` (sha256 cf911b765d1c)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.2720 | +4.4142 | +4.4135 | [+4.0935, +4.7208] | 0.000 |
| **macro** | 4.8579 | 9.2720 | +4.4142 | +4.4135 | [+4.0935, +4.7208] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: sac-angle-assist-s1 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist-s1.csv` (sha256 31ac61743274)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 8.3628 | +3.5049 | +3.5053 | [+3.0813, +3.9167] | 0.000 |
| **macro** | 4.8579 | 8.3628 | +3.5049 | +3.5053 | [+3.0813, +3.9167] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed: sac-angle-assist-s2 vs baseline, time (exclusion if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/baseline.csv` (sha256 6ac2f0bd223a)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist-s2.csv` (sha256 fcb99592ae4c)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8579 | 9.2944 | +4.4366 | +4.4350 | [+4.1167, +4.7422] | 0.000 |
| **macro** | 4.8579 | 9.2944 | +4.4366 | +4.4350 | [+4.1167, +4.7422] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## descriptive: sac-beam (B) vs sac-angle (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle.csv` (sha256 fa4c60055ed8)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam.csv` (sha256 928d96dc4ace)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.1 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 9.9813 | 9.9191 | -0.0621 | -0.0622 | [-0.1113, -0.0217] | 1.000 |
| **macro** | 9.9813 | 9.9191 | -0.0621 | -0.0622 | [-0.1113, -0.0217] | 1.000 |

########## descriptive: sac-beam (B) vs sac-angle (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle.csv` (sha256 fa4c60055ed8)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam.csv` (sha256 928d96dc4ace)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.1 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.9950 | 0.9650 | -0.0300 | -0.0300 | [-0.0517, -0.0117] | 1.000 |
| **macro** | 0.9950 | 0.9650 | -0.0300 | -0.0300 | [-0.0517, -0.0117] | 1.000 |

########## descriptive: sac-beam-assist (B) vs sac-angle-assist (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist.csv` (sha256 75cd279289a4)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist.csv` (sha256 3647d84876df)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.1 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 8.9764 | 2.9413 | -6.0351 | -6.0343 | [-6.2682, -5.7908] | 1.000 |
| **macro** | 8.9764 | 2.9413 | -6.0351 | -6.0343 | [-6.2682, -5.7908] | 1.000 |

########## descriptive: sac-beam-assist (B) vs sac-angle-assist (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist.csv` (sha256 75cd279289a4)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist.csv` (sha256 3647d84876df)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.7883 | 0.0250 | -0.7633 | -0.7634 | [-0.7983, -0.7283] | 1.000 |
| **macro** | 0.7883 | 0.0250 | -0.7633 | -0.7634 | [-0.7983, -0.7283] | 1.000 |

########## descriptive: sac-beam-assist (B) vs sac-beam (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam.csv` (sha256 928d96dc4ace)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist.csv` (sha256 3647d84876df)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 9.9191 | 2.9413 | -6.9778 | -6.9771 | [-7.1649, -6.7774] | 1.000 |
| **macro** | 9.9191 | 2.9413 | -6.9778 | -6.9771 | [-7.1649, -6.7774] | 1.000 |

########## descriptive: sac-beam-assist (B) vs sac-beam (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam.csv` (sha256 928d96dc4ace)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-beam-assist.csv` (sha256 3647d84876df)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.9650 | 0.0250 | -0.9400 | -0.9400 | [-0.9633, -0.9133] | 1.000 |
| **macro** | 0.9650 | 0.0250 | -0.9400 | -0.9400 | [-0.9633, -0.9133] | 1.000 |

########## descriptive: sac-angle-assist (B) vs sac-angle (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle.csv` (sha256 fa4c60055ed8)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist.csv` (sha256 75cd279289a4)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 9.9813 | 8.9764 | -1.0049 | -1.0049 | [-1.1946, -0.8287] | 1.000 |
| **macro** | 9.9813 | 8.9764 | -1.0049 | -1.0049 | [-1.1946, -0.8287] | 1.000 |

########## descriptive: sac-angle-assist (B) vs sac-angle (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/51-feature-sac-laser-training/gate/truth.csv` (sha256 630ec5b311a1) · N = 200
- A (baseline): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle.csv` (sha256 fa4c60055ed8)
- B (candidate): `docs/issues/feature/51-feature-sac-laser-training/gate/sac-angle-assist.csv` (sha256 75cd279289a4)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.09 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.9950 | 0.7883 | -0.2067 | -0.2066 | [-0.2400, -0.1733] | 1.000 |
| **macro** | 0.9950 | 0.7883 | -0.2067 | -0.2066 | [-0.2400, -0.1733] | 1.000 |
