== sha256
b31947f3e8ef7ce7e620a9ae56e264ef7da77b9fe145ff49c43a9260e9dbb196 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv
ec2a2a7cca18dea40d5d16058032b840469a8b5fcb0ef5bd8e55e8d11c3afdbf *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/baseline/gate.csv
2e456728e9526d86687b0988ed9cdef4e5c9d80aa75c2f7463e57f3aa7f1ec3b *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire-neural-fly-stim.csv
d7ea0a9b3cd302d6d88aad9452061018c1ff744e4f8d62e5a66d1ffd3a78fa05 *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/sac-beam-assist-s0/gate.csv
07318a2327d9a456ccd1cb504bee109c1768c766cb146df6dd54c5eec3eb9bff *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/sac-beam-assist-s1/gate.csv
14b401530bf56b312f7752ad36f6bdbd398048db28af75d9ea817b34b11496cf *docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/sac-beam-assist-s2/gate.csv

########## pooled vs baseline: time (reported)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/baseline/gate.csv` (sha256 ec2a2a7cca18)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire-neural-fly-stim.csv` (sha256 2e456728e952)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 5.3965 | 4.0576 | -1.3389 | -1.3421 | [-1.9455, -0.7120] | 1.000 |
| **macro** | 5.3965 | 4.0576 | -1.3389 | -1.3421 | [-1.9455, -0.7120] | 1.000 |

Threshold P(B better) ≥ 0.90 on macro: **PASS** (1.000)

########## pooled vs baseline: capture (value = miss rate; reported)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/baseline/gate.csv` (sha256 ec2a2a7cca18)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire-neural-fly-stim.csv` (sha256 2e456728e952)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: capture

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| capture | 0.0167 | 0.0889 | +0.0722 | +0.0718 | [+0.0111, +0.1222] | 0.012 |
| **macro** | 0.0167 | 0.0889 | +0.0722 | +0.0718 | [+0.0111, +0.1222] | 0.012 |

########## pooled vs baseline: misfires (reported)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/baseline/gate.csv` (sha256 ec2a2a7cca18)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/sac-beam-assist-rule-fire-neural-fly-stim.csv` (sha256 2e456728e952)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: misfires

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| misfires | 1.9333 | 2.0389 | +0.1056 | +0.1031 | [-0.6111, +0.7944] | 0.388 |
| **macro** | 1.9333 | 2.0389 | +0.1056 | +0.1031 | [-0.6111, +0.7944] | 0.388 |

########## per model: sac-beam-assist-s0 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/baseline/gate.csv` (sha256 ec2a2a7cca18)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/sac-beam-assist-s0/gate.csv` (sha256 d7ea0a9b3cd3)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 5.3965 | 4.8095 | -0.5870 | -0.5876 | [-1.4211, +0.2868] | 0.908 |
| **macro** | 5.3965 | 4.8095 | -0.5870 | -0.5876 | [-1.4211, +0.2868] | 0.908 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (0.908)

########## per model: sac-beam-assist-s1 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/baseline/gate.csv` (sha256 ec2a2a7cca18)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/sac-beam-assist-s1/gate.csv` (sha256 07318a2327d9)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 5.3965 | 3.6705 | -1.7260 | -1.7292 | [-2.3382, -1.0757] | 1.000 |
| **macro** | 5.3965 | 3.6705 | -1.7260 | -1.7292 | [-2.3382, -1.0757] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)

########## per model: sac-beam-assist-s2 vs baseline, time (undecided if P < 0.50)
# paired bootstrap — B vs A

- truth: `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/gate/truth-neural.csv` (sha256 b31947f3e8ef) · N = 60
- A (baseline): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/baseline/gate.csv` (sha256 ec2a2a7cca18)
- B (candidate): `docs/issues/feature/72-feature-aimer-v1-sac-rule-trigger/data/neural-fly-stim/sac-beam-assist-s2/gate.csv` (sha256 14b401530bf5)
- metric: mae · round none · no clip · lower is better
- resamples 10000 · seed 42 · engine numpy · 0.04 s
- targets: time

| target | A | B | Δ (B−A) | boot mean Δ | 95% CI | P(B better) |
| --- | --- | --- | --- | --- | --- | --- |
| time | 5.3965 | 3.6927 | -1.7038 | -1.7096 | [-2.5138, -0.8658] | 1.000 |
| **macro** | 5.3965 | 3.6927 | -1.7038 | -1.7096 | [-2.5138, -0.8658] | 1.000 |

Threshold P(B better) ≥ 0.50 on macro: **PASS** (1.000)
