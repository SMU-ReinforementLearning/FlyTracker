== sha256
0f577c4c706f728dccaa660ab6c7640e4eeb69c84e112ddcc29d8396d5f3669b *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv
9996b2a30098ff52da88c1821e114f02d3bbe0bbf8c255d31800c78f7a091e38 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv
f01bd04023165f91a9fb262f709f4308c9499fd9ad8385ec14758743addc2faf *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv
edda5bc82512b1f9a63747e26b20dec0ff29ca04d7ea3b7062986addaae5d37b *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv
611fba486eac086105354cb9d0e94a14d4ddfdc514f624d7edcb45aaf1d44629 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv
70a62ab3d45dc31d10524a514587e59edec48bed0e217f0d3cb32b9559808b1c *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv
949f5e39c066333052ef02cc9d82fc26d57d89f6c55defaff41f877744782b58 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv
eb61decfccab40c0f76dd862d76f2ca16bf9833a80471e7e39b4880bc04167f2 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv
b720fc475fc74e834177264f7e528714d12ac060578f710697c5fbcfabb35511 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv
3185afe22a27bc5d4b8a9778dcf96660ab826666c3a421c8a7677910f0515ea8 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv
0440222f838bdec50aa50eed86968580e284057d3c1b82321ed2edd16cb857c6 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv
1789d3ffe2a421e829a308b805d63c8cc494ed0e818d9240fbd6c87c7ce4abdc *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s0/gate.csv
490f7d98ce338f572bf76f37d4e8f292b2fc77dfd7e7550e506c68ec58441ba7 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s1/gate.csv
849ea03d725631b27b1b392f904f9e4b110a48dc87f824b9f456d5fbf5ceb937 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s2/gate.csv
77b0c347d088d5c606a7d4a299bae642a15f187aef13240a06839062256f969e *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s0/gate.csv
12e2d0a8738486d7071b85ef117a86bcbc3ad8db9151ffe198a76a9cd16d6fca *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s1/gate.csv
60e2b43b0425505648f92abaf1830a63602b1d1628b0a5d77fc66546ce244a8e *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s2/gate.csv
e3d35956aa961b790ab7bc8e4d04f52613c2214d2456efbc46bbd83dc9551d9d *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s0/gate.csv
f4a6149d6c1d626aab10c639c6c8e807725306d5ef5900abcf1e649f5fcf4f9e *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s1/gate.csv
77ee9e0bbef8981e77e15e5add5e8fc4180d92268a30e0b3d311c1e620e1179c *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s2/gate.csv
fed52ba8156f2a37c3e884ee639ecbb792e706e0077be72ca5e398c7fe767eb6 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s0/gate.csv
d7a9e60e67b0ae8f0bed60fa3e67f448f62ba5a27716f5cb9316449d22f1bca4 *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s1/gate.csv
646131ed4816f074b545e08f003bc8bbfb2a72df68fbc01d1537fc8ef09da87c *docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s2/gate.csv

########## GATE fire-m1 vs accel-pen-rule (rule fire): time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.6114 | 2.6760 | +0.0646 | +0.0646 | [+0.0411, +0.0926] | 0.000 |
| **macro** | 2.6114 | 2.6760 | +0.0646 | +0.0646 | [+0.0411, +0.0926] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## fire-m1 vs accel-pen-rule: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0183 | 0.0200 | +0.0017 | +0.0017 | [+0.0000, +0.0050] | 0.179 |
| **macro** | 0.0183 | 0.0200 | +0.0017 | +0.0017 | [+0.0000, +0.0050] | 0.179 |

########## fire-m1 vs accel-pen-rule: misfires (undecided if pooled above the baseline's; declared case needs P >= 0.90)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.4717 | 1.0600 | +0.5883 | +0.5882 | [+0.4367, +0.7533] | 0.000 |
| **macro** | 0.4717 | 1.0600 | +0.5883 | +0.5882 | [+0.4367, +0.7533] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## per training seed: fire-m1-s0 vs accel-pen-rule-s0 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s0/gate.csv` (sha256 1789d3ffe2a4)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.8514 | 2.9376 | +0.0861 | +0.0862 | [+0.0345, +0.1546] | 0.000 |
| **macro** | 2.8514 | 2.9376 | +0.0861 | +0.0862 | [+0.0345, +0.1546] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed, descriptive: fire-m1-s0 vs accel-pen-rule-s0, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s0/gate.csv` (sha256 1789d3ffe2a4)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.3200 | 0.6400 | +0.3200 | +0.3195 | [+0.1949, +0.4700] | 0.000 |
| **macro** | 0.3200 | 0.6400 | +0.3200 | +0.3195 | [+0.1949, +0.4700] | 0.000 |

########## per training seed: fire-m1-s1 vs accel-pen-rule-s1 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s1/gate.csv` (sha256 490f7d98ce33)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.5742 | 2.6351 | +0.0609 | +0.0610 | [+0.0192, +0.1053] | 0.003 |
| **macro** | 2.5742 | 2.6351 | +0.0609 | +0.0610 | [+0.0192, +0.1053] | 0.003 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.003)

########## per training seed, descriptive: fire-m1-s1 vs accel-pen-rule-s1, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s1/gate.csv` (sha256 490f7d98ce33)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6500 | 1.4700 | +0.8200 | +0.8187 | [+0.5050, +1.1500] | 0.000 |
| **macro** | 0.6500 | 1.4700 | +0.8200 | +0.8187 | [+0.5050, +1.1500] | 0.000 |

########## per training seed: fire-m1-s2 vs accel-pen-rule-s2 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s2/gate.csv` (sha256 849ea03d7256)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.4085 | 2.4554 | +0.0469 | +0.0467 | [+0.0260, +0.0708] | 0.000 |
| **macro** | 2.4085 | 2.4554 | +0.0469 | +0.0467 | [+0.0260, +0.0708] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed, descriptive: fire-m1-s2 vs accel-pen-rule-s2, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m1-s2/gate.csv` (sha256 849ea03d7256)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.4450 | 1.0700 | +0.6250 | +0.6264 | [+0.4200, +0.8700] | 0.000 |
| **macro** | 0.4450 | 1.0700 | +0.6250 | +0.6264 | [+0.4200, +0.8700] | 0.000 |

########## GATE fire-m5 vs accel-pen-rule (rule fire): time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.6114 | 2.8394 | +0.2280 | +0.2279 | [+0.1616, +0.3020] | 0.000 |
| **macro** | 2.6114 | 2.8394 | +0.2280 | +0.2279 | [+0.1616, +0.3020] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## fire-m5 vs accel-pen-rule: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0183 | 0.0200 | +0.0017 | +0.0017 | [+0.0000, +0.0050] | 0.182 |
| **macro** | 0.0183 | 0.0200 | +0.0017 | +0.0017 | [+0.0000, +0.0050] | 0.182 |

########## fire-m5 vs accel-pen-rule: misfires (undecided if pooled above the baseline's; declared case needs P >= 0.90)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.4717 | 0.3783 | -0.0933 | -0.0929 | [-0.1783, -0.0117] | 0.987 |
| **macro** | 0.4717 | 0.3783 | -0.0933 | -0.0929 | [-0.1783, -0.0117] | 0.987 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (0.987)

########## per training seed: fire-m5-s0 vs accel-pen-rule-s0 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s0/gate.csv` (sha256 77b0c347d088)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.8514 | 3.0271 | +0.1757 | +0.1759 | [+0.0942, +0.2787] | 0.000 |
| **macro** | 2.8514 | 3.0271 | +0.1757 | +0.1759 | [+0.0942, +0.2787] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed, descriptive: fire-m5-s0 vs accel-pen-rule-s0, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s0/gate.csv` (sha256 77b0c347d088)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.3200 | 0.3500 | +0.0300 | +0.0308 | [-0.0600, +0.1300] | 0.272 |
| **macro** | 0.3200 | 0.3500 | +0.0300 | +0.0308 | [-0.0600, +0.1300] | 0.272 |

########## per training seed: fire-m5-s1 vs accel-pen-rule-s1 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s1/gate.csv` (sha256 12e2d0a87384)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.5742 | 2.9348 | +0.3606 | +0.3600 | [+0.2094, +0.5368] | 0.000 |
| **macro** | 2.5742 | 2.9348 | +0.3606 | +0.3600 | [+0.2094, +0.5368] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed, descriptive: fire-m5-s1 vs accel-pen-rule-s1, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s1/gate.csv` (sha256 12e2d0a87384)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6500 | 0.4400 | -0.2100 | -0.2097 | [-0.4200, -0.0300] | 0.989 |
| **macro** | 0.6500 | 0.4400 | -0.2100 | -0.2097 | [-0.4200, -0.0300] | 0.989 |

########## per training seed: fire-m5-s2 vs accel-pen-rule-s2 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s2/gate.csv` (sha256 60e2b43b0425)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.4085 | 2.5562 | +0.1477 | +0.1478 | [+0.0680, +0.2479] | 0.000 |
| **macro** | 2.4085 | 2.5562 | +0.1477 | +0.1478 | [+0.0680, +0.2479] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed, descriptive: fire-m5-s2 vs accel-pen-rule-s2, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-m5-s2/gate.csv` (sha256 60e2b43b0425)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.4450 | 0.3450 | -0.1000 | -0.0998 | [-0.2050, +0.0100] | 0.967 |
| **macro** | 0.4450 | 0.3450 | -0.1000 | -0.0998 | [-0.2050, +0.0100] | 0.967 |

########## GATE fire-prior-m1 vs accel-pen-rule (rule fire): time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.6114 | 2.6584 | +0.0470 | +0.0470 | [+0.0193, +0.0835] | 0.000 |
| **macro** | 2.6114 | 2.6584 | +0.0470 | +0.0470 | [+0.0193, +0.0835] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## fire-prior-m1 vs accel-pen-rule: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0183 | 0.0217 | +0.0033 | +0.0034 | [+0.0000, +0.0083] | 0.066 |
| **macro** | 0.0183 | 0.0217 | +0.0033 | +0.0034 | [+0.0000, +0.0083] | 0.066 |

########## fire-prior-m1 vs accel-pen-rule: misfires (undecided if pooled above the baseline's; declared case needs P >= 0.90)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.4717 | 0.6167 | +0.1450 | +0.1451 | [+0.0617, +0.2317] | 0.000 |
| **macro** | 0.4717 | 0.6167 | +0.1450 | +0.1451 | [+0.0617, +0.2317] | 0.000 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.000)

########## per training seed: fire-prior-m1-s0 vs accel-pen-rule-s0 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s0/gate.csv` (sha256 e3d35956aa96)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.8514 | 2.8962 | +0.0448 | +0.0451 | [+0.0074, +0.0965] | 0.000 |
| **macro** | 2.8514 | 2.8962 | +0.0448 | +0.0451 | [+0.0074, +0.0965] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed, descriptive: fire-prior-m1-s0 vs accel-pen-rule-s0, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s0/gate.csv` (sha256 e3d35956aa96)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.3200 | 0.4050 | +0.0850 | +0.0857 | [+0.0150, +0.1900] | 0.005 |
| **macro** | 0.3200 | 0.4050 | +0.0850 | +0.0857 | [+0.0150, +0.1900] | 0.005 |

########## per training seed: fire-prior-m1-s1 vs accel-pen-rule-s1 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s1/gate.csv` (sha256 f4a6149d6c1d)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.5742 | 2.6488 | +0.0745 | +0.0739 | [+0.0074, +0.1722] | 0.000 |
| **macro** | 2.5742 | 2.6488 | +0.0745 | +0.0739 | [+0.0074, +0.1722] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed, descriptive: fire-prior-m1-s1 vs accel-pen-rule-s1, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s1/gate.csv` (sha256 f4a6149d6c1d)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6500 | 0.8750 | +0.2250 | +0.2238 | [+0.0300, +0.4000] | 0.012 |
| **macro** | 0.6500 | 0.8750 | +0.2250 | +0.2238 | [+0.0300, +0.4000] | 0.012 |

########## per training seed: fire-prior-m1-s2 vs accel-pen-rule-s2 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s2/gate.csv` (sha256 77ee9e0bbef8)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.4085 | 2.4302 | +0.0217 | +0.0221 | [+0.0020, +0.0519] | 0.002 |
| **macro** | 2.4085 | 2.4302 | +0.0217 | +0.0221 | [+0.0020, +0.0519] | 0.002 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.002)

########## per training seed, descriptive: fire-prior-m1-s2 vs accel-pen-rule-s2, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m1-s2/gate.csv` (sha256 77ee9e0bbef8)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.4450 | 0.5700 | +0.1250 | +0.1258 | [+0.0150, +0.2550] | 0.009 |
| **macro** | 0.4450 | 0.5700 | +0.1250 | +0.1258 | [+0.0150, +0.2550] | 0.009 |

########## GATE fire-prior-m5 vs accel-pen-rule (rule fire): time (gated)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.6114 | 2.6359 | +0.0245 | +0.0247 | [+0.0087, +0.0437] | 0.001 |
| **macro** | 2.6114 | 2.6359 | +0.0245 | +0.0247 | [+0.0087, +0.0437] | 0.001 |

Threshold P(B better) ≥ 0.90 on macro: **FAIL** (0.001)

########## fire-prior-m5 vs accel-pen-rule: capture (value = miss rate; exclusion if pooled capture < 0.97)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0183 | 0.0183 | +0.0000 | +0.0000 | [+0.0000, +0.0000] | 0.500 |
| **macro** | 0.0183 | 0.0183 | +0.0000 | +0.0000 | [+0.0000, +0.0000] | 0.500 |

########## fire-prior-m5 vs accel-pen-rule: misfires (undecided if pooled above the baseline's; declared case needs P >= 0.90)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/accel-pen-rule.csv` (sha256 9996b2a30098)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.4717 | 0.4250 | -0.0467 | -0.0467 | [-0.1133, +0.0117] | 0.936 |
| **macro** | 0.4717 | 0.4250 | -0.0467 | -0.0467 | [-0.1133, +0.0117] | 0.936 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (0.936)

########## per training seed: fire-prior-m5-s0 vs accel-pen-rule-s0 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s0/gate.csv` (sha256 fed52ba8156f)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.8514 | 2.8925 | +0.0410 | +0.0414 | [+0.0076, +0.0859] | 0.001 |
| **macro** | 2.8514 | 2.8925 | +0.0410 | +0.0414 | [+0.0076, +0.0859] | 0.001 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.001)

########## per training seed, descriptive: fire-prior-m5-s0 vs accel-pen-rule-s0, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s0/gate.csv` (sha256 f01bd0402316)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s0/gate.csv` (sha256 fed52ba8156f)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.3200 | 0.3850 | +0.0650 | +0.0656 | [-0.0150, +0.1650] | 0.058 |
| **macro** | 0.3200 | 0.3850 | +0.0650 | +0.0656 | [-0.0150, +0.1650] | 0.058 |

########## per training seed: fire-prior-m5-s1 vs accel-pen-rule-s1 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s1/gate.csv` (sha256 d7a9e60e67b0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.5742 | 2.5889 | +0.0147 | +0.0147 | [-0.0107, +0.0433] | 0.137 |
| **macro** | 2.5742 | 2.5889 | +0.0147 | +0.0147 | [-0.0107, +0.0433] | 0.137 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.137)

########## per training seed, descriptive: fire-prior-m5-s1 vs accel-pen-rule-s1, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s1/gate.csv` (sha256 edda5bc82512)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s1/gate.csv` (sha256 d7a9e60e67b0)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6500 | 0.4800 | -0.1700 | -0.1705 | [-0.3500, -0.0400] | 0.998 |
| **macro** | 0.6500 | 0.4800 | -0.1700 | -0.1705 | [-0.3500, -0.0400] | 0.998 |

########## per training seed: fire-prior-m5-s2 vs accel-pen-rule-s2 (rule fire), time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s2/gate.csv` (sha256 646131ed4816)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.4085 | 2.4263 | +0.0178 | +0.0179 | [+0.0018, +0.0441] | 0.000 |
| **macro** | 2.4085 | 2.4263 | +0.0178 | +0.0179 | [+0.0018, +0.0441] | 0.000 |

Threshold P(B better) ≥ 0.50 on macro: **FAIL** (0.000)

########## per training seed, descriptive: fire-prior-m5-s2 vs accel-pen-rule-s2, misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/accel-pen-rule-s2/gate.csv` (sha256 611fba486eac)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/data/fire-prior-m5-s2/gate.csv` (sha256 646131ed4816)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.4450 | 0.4100 | -0.0350 | -0.0351 | [-0.0750, +0.0000] | 0.977 |
| **macro** | 0.4450 | 0.4100 | -0.0350 | -0.0351 | [-0.0750, +0.0000] | 0.977 |

########## descriptive: fire-prior-m1 (B) vs fire-m1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.6760 | 2.6584 | -0.0176 | -0.0176 | [-0.0566, +0.0252] | 0.801 |
| **macro** | 2.6760 | 2.6584 | -0.0176 | -0.0176 | [-0.0566, +0.0252] | 0.801 |

########## descriptive: fire-prior-m1 (B) vs fire-m1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0200 | 0.0217 | +0.0017 | +0.0017 | [-0.0033, +0.0083] | 0.236 |
| **macro** | 0.0200 | 0.0217 | +0.0017 | +0.0017 | [-0.0033, +0.0083] | 0.236 |

########## descriptive: fire-prior-m1 (B) vs fire-m1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 1.0600 | 0.6167 | -0.4433 | -0.4432 | [-0.5733, -0.3200] | 1.000 |
| **macro** | 1.0600 | 0.6167 | -0.4433 | -0.4432 | [-0.5733, -0.3200] | 1.000 |

########## descriptive: fire-prior-m5 (B) vs fire-m5 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.8394 | 2.6359 | -0.2035 | -0.2032 | [-0.2785, -0.1366] | 1.000 |
| **macro** | 2.8394 | 2.6359 | -0.2035 | -0.2032 | [-0.2785, -0.1366] | 1.000 |

########## descriptive: fire-prior-m5 (B) vs fire-m5 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0200 | 0.0183 | -0.0017 | -0.0017 | [-0.0050, +0.0000] | 0.818 |
| **macro** | 0.0200 | 0.0183 | -0.0017 | -0.0017 | [-0.0050, +0.0000] | 0.818 |

########## descriptive: fire-prior-m5 (B) vs fire-m5 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.3783 | 0.4250 | +0.0467 | +0.0462 | [-0.0150, +0.1050] | 0.065 |
| **macro** | 0.3783 | 0.4250 | +0.0467 | +0.0462 | [-0.0150, +0.1050] | 0.065 |

########## descriptive: fire-m5 (B) vs fire-m1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.6760 | 2.8394 | +0.1634 | +0.1633 | [+0.0934, +0.2403] | 0.000 |
| **macro** | 2.6760 | 2.8394 | +0.1634 | +0.1633 | [+0.0934, +0.2403] | 0.000 |

########## descriptive: fire-m5 (B) vs fire-m1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0200 | 0.0200 | +0.0000 | +0.0000 | [-0.0050, +0.0050] | 0.414 |
| **macro** | 0.0200 | 0.0200 | +0.0000 | +0.0000 | [-0.0050, +0.0050] | 0.414 |

########## descriptive: fire-m5 (B) vs fire-m1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 1.0600 | 0.3783 | -0.6817 | -0.6811 | [-0.8517, -0.5267] | 1.000 |
| **macro** | 1.0600 | 0.3783 | -0.6817 | -0.6811 | [-0.8517, -0.5267] | 1.000 |

########## descriptive: fire-prior-m5 (B) vs fire-prior-m1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 2.6584 | 2.6359 | -0.0225 | -0.0223 | [-0.0632, +0.0119] | 0.884 |
| **macro** | 2.6584 | 2.6359 | -0.0225 | -0.0223 | [-0.0632, +0.0119] | 0.884 |

########## descriptive: fire-prior-m5 (B) vs fire-prior-m1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0217 | 0.0183 | -0.0033 | -0.0034 | [-0.0083, +0.0000] | 0.934 |
| **macro** | 0.0217 | 0.0183 | -0.0033 | -0.0034 | [-0.0083, +0.0000] | 0.934 |

########## descriptive: fire-prior-m5 (B) vs fire-prior-m1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6167 | 0.4250 | -0.1917 | -0.1917 | [-0.2783, -0.1150] | 1.000 |
| **macro** | 0.6167 | 0.4250 | -0.1917 | -0.1917 | [-0.2783, -0.1150] | 1.000 |

########## descriptive: fire-m1 (B) vs v0 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.6760 | -2.2183 | -2.2179 | [-2.4724, -1.9608] | 1.000 |
| **macro** | 4.8943 | 2.6760 | -2.2183 | -2.2179 | [-2.4724, -1.9608] | 1.000 |

########## descriptive: fire-m1 (B) vs v0 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.0200 | +0.0100 | +0.0099 | [-0.0100, +0.0300] | 0.183 |
| **macro** | 0.0100 | 0.0200 | +0.0100 | +0.0099 | [-0.0100, +0.0300] | 0.183 |

########## descriptive: fire-m1 (B) vs v0 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 1.0600 | +0.5600 | +0.5598 | [+0.3300, +0.7900] | 0.000 |
| **macro** | 0.5000 | 1.0600 | +0.5600 | +0.5598 | [+0.3300, +0.7900] | 0.000 |

########## descriptive: fire-m5 (B) vs v0 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.8394 | -2.0549 | -2.0546 | [-2.3114, -1.7889] | 1.000 |
| **macro** | 4.8943 | 2.8394 | -2.0549 | -2.0546 | [-2.3114, -1.7889] | 1.000 |

########## descriptive: fire-m5 (B) vs v0 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.0200 | +0.0100 | +0.0099 | [-0.0100, +0.0300] | 0.186 |
| **macro** | 0.0100 | 0.0200 | +0.0100 | +0.0099 | [-0.0100, +0.0300] | 0.186 |

########## descriptive: fire-m5 (B) vs v0 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 0.3783 | -0.1217 | -0.1213 | [-0.2900, +0.0283] | 0.941 |
| **macro** | 0.5000 | 0.3783 | -0.1217 | -0.1213 | [-0.2900, +0.0283] | 0.941 |

########## descriptive: fire-prior-m1 (B) vs v0 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.6584 | -2.2359 | -2.2355 | [-2.4901, -1.9728] | 1.000 |
| **macro** | 4.8943 | 2.6584 | -2.2359 | -2.2355 | [-2.4901, -1.9728] | 1.000 |

########## descriptive: fire-prior-m1 (B) vs v0 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.0217 | +0.0117 | +0.0116 | [-0.0100, +0.0317] | 0.152 |
| **macro** | 0.0100 | 0.0217 | +0.0117 | +0.0116 | [-0.0100, +0.0317] | 0.152 |

########## descriptive: fire-prior-m1 (B) vs v0 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 0.6167 | +0.1167 | +0.1166 | [-0.0633, +0.2883] | 0.103 |
| **macro** | 0.5000 | 0.6167 | +0.1167 | +0.1166 | [-0.0633, +0.2883] | 0.103 |

########## descriptive: fire-prior-m5 (B) vs v0 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 4.8943 | 2.6359 | -2.2584 | -2.2578 | [-2.5123, -1.9957] | 1.000 |
| **macro** | 4.8943 | 2.6359 | -2.2584 | -2.2578 | [-2.5123, -1.9957] | 1.000 |

########## descriptive: fire-prior-m5 (B) vs v0 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0100 | 0.0183 | +0.0083 | +0.0083 | [-0.0117, +0.0267] | 0.222 |
| **macro** | 0.0100 | 0.0183 | +0.0083 | +0.0083 | [-0.0117, +0.0267] | 0.222 |

########## descriptive: fire-prior-m5 (B) vs v0 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/baseline.csv` (sha256 70a62ab3d45d)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.5000 | 0.4250 | -0.0750 | -0.0751 | [-0.2383, +0.0750] | 0.828 |
| **macro** | 0.5000 | 0.4250 | -0.0750 | -0.0751 | [-0.2383, +0.0750] | 0.828 |

########## descriptive: fire-m1 (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 2.6760 | -0.3496 | -0.3495 | [-0.5146, -0.1894] | 1.000 |
| **macro** | 3.0256 | 2.6760 | -0.3496 | -0.3495 | [-0.5146, -0.1894] | 1.000 |

########## descriptive: fire-m1 (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 0.0200 | -0.0067 | -0.0066 | [-0.0233, +0.0083] | 0.812 |
| **macro** | 0.0267 | 0.0200 | -0.0067 | -0.0066 | [-0.0233, +0.0083] | 0.812 |

########## descriptive: fire-m1 (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m1.csv` (sha256 eb61decfccab)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 1.0600 | +0.4600 | +0.4595 | [+0.2850, +0.6433] | 0.000 |
| **macro** | 0.6000 | 1.0600 | +0.4600 | +0.4595 | [+0.2850, +0.6433] | 0.000 |

########## descriptive: fire-m5 (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 2.8394 | -0.1862 | -0.1862 | [-0.3608, -0.0124] | 0.983 |
| **macro** | 3.0256 | 2.8394 | -0.1862 | -0.1862 | [-0.3608, -0.0124] | 0.983 |

########## descriptive: fire-m5 (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 0.0200 | -0.0067 | -0.0066 | [-0.0233, +0.0100] | 0.786 |
| **macro** | 0.0267 | 0.0200 | -0.0067 | -0.0066 | [-0.0233, +0.0100] | 0.786 |

########## descriptive: fire-m5 (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-m5.csv` (sha256 b720fc475fc7)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 0.3783 | -0.2217 | -0.2216 | [-0.3317, -0.1133] | 1.000 |
| **macro** | 0.6000 | 0.3783 | -0.2217 | -0.2216 | [-0.3317, -0.1133] | 1.000 |

########## descriptive: fire-prior-m1 (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 2.6584 | -0.3672 | -0.3671 | [-0.5365, -0.2005] | 1.000 |
| **macro** | 3.0256 | 2.6584 | -0.3672 | -0.3671 | [-0.5365, -0.2005] | 1.000 |

########## descriptive: fire-prior-m1 (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.07 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 0.0217 | -0.0050 | -0.0049 | [-0.0217, +0.0117] | 0.725 |
| **macro** | 0.0267 | 0.0217 | -0.0050 | -0.0049 | [-0.0217, +0.0117] | 0.725 |

########## descriptive: fire-prior-m1 (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m1.csv` (sha256 3185afe22a27)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 0.6167 | +0.0167 | +0.0164 | [-0.1083, +0.1467] | 0.406 |
| **macro** | 0.6000 | 0.6167 | +0.0167 | +0.0164 | [-0.1083, +0.1467] | 0.406 |

########## descriptive: fire-prior-m5 (B) vs v1 (A), time
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 3.0256 | 2.6359 | -0.3897 | -0.3894 | [-0.5520, -0.2329] | 1.000 |
| **macro** | 3.0256 | 2.6359 | -0.3897 | -0.3894 | [-0.5520, -0.2329] | 1.000 |

########## descriptive: fire-prior-m5 (B) vs v1 (A), capture
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0267 | 0.0183 | -0.0083 | -0.0083 | [-0.0250, +0.0067] | 0.869 |
| **macro** | 0.0267 | 0.0183 | -0.0083 | -0.0083 | [-0.0250, +0.0067] | 0.869 |

########## descriptive: fire-prior-m5 (B) vs v1 (A), misfires
# paired bootstrap — B vs A

- truth: `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/truth.csv` (sha256 0f577c4c706f) · N = 200
- A (baseline): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/v1.csv` (sha256 949f5e39c066)
- B (candidate): `docs/issues/feature/88-feature-aimer-accel-action-sac-fire/gate/fire-prior-m5.csv` (sha256 0440222f838b)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.08 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 0.6000 | 0.4250 | -0.1750 | -0.1753 | [-0.2900, -0.0633] | 0.999 |
| **macro** | 0.6000 | 0.4250 | -0.1750 | -0.1753 | [-0.2900, -0.0633] | 0.999 |
