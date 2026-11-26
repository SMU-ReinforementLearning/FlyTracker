## 1. Deterministic, seeds 20000-20199, steps where a new shot can start

| model | value at 0-0.5 mm | value at 0.5-1.25 mm | value at 1.25-3 mm | value over 3 mm | value, not visible | rule says fire, policy holds | shots the rule would not take | hit rate of shots the rule would take | hit rate of shots the rule would not take |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fire-m1-s0 | -0.04 | -0.09 | -0.42 | -0.80 | -0.53 | 59.4 % | 32.1 % | 75.6 % | 27.2 % |
| fire-m1-s1 | -0.05 | -0.08 | -0.49 | -0.84 | -0.50 | 58.8 % | 51.0 % | 70.5 % | 11.2 % |
| fire-m1-s2 | +0.62 | +0.00 | -0.41 | -0.82 | -0.66 | 44.6 % | 43.7 % | 73.7 % | 15.0 % |
| fire-m5-s0 | -0.19 | -0.21 | -0.69 | -0.72 | -0.65 | 82.7 % | 4.6 % | 74.9 % | 41.7 % |
| fire-m5-s1 | -0.24 | -0.45 | -0.84 | -0.71 | -0.58 | 90.0 % | 9.5 % | 73.6 % | 25.9 % |
| fire-m5-s2 | -0.14 | -0.23 | -0.56 | -0.62 | -0.54 | 81.3 % | 4.9 % | 76.0 % | 38.5 % |
| fire-prior-m1-s0 | -0.59 | -0.16 | -0.25 | -0.56 | -0.38 | 48.0 % | 5.9 % | 74.3 % | 6.2 % |
| fire-prior-m1-s1 | -0.53 | -0.20 | -0.32 | -0.43 | -0.52 | 39.5 % | 20.4 % | 64.2 % | 9.2 % |
| fire-prior-m1-s2 | +0.17 | -0.08 | -0.11 | -0.49 | -0.30 | 32.0 % | 14.7 % | 72.9 % | 8.7 % |
| fire-prior-m5-s0 | -0.55 | -0.24 | -0.27 | -0.40 | -0.30 | 37.6 % | 1.1 % | 72.3 % | 0.0 % |
| fire-prior-m5-s1 | -0.73 | -0.33 | -0.42 | -0.39 | -0.26 | 49.4 % | 2.0 % | 68.8 % | 0.0 % |
| fire-prior-m5-s2 | -0.63 | -0.02 | -0.09 | -0.29 | -0.37 | 40.7 % | 0.7 % | 71.2 % | 0.0 % |

Value = the policy's output after tanh (median). A hit is a shot that captured; the rest are misfires.

## 2. Sampled actions (as in training), seeds 20000-20049

| model | captures of 50 | shots per episode | misfires per episode | fire sd (median) | share of free steps fired |
| --- | --- | --- | --- | --- | --- |
| fire-m1-s0 | 47 | 1.86 | 0.92 | 0.187 | 1.3 % |
| fire-m1-s1 | 50 | 2.28 | 1.28 | 0.198 | 2.2 % |
| fire-m1-s2 | 50 | 1.98 | 0.98 | 0.232 | 2.0 % |
| fire-m5-s0 | 47 | 1.44 | 0.50 | 0.203 | 1.0 % |
| fire-m5-s1 | 50 | 1.24 | 0.24 | 0.185 | 1.1 % |
| fire-m5-s2 | 50 | 1.42 | 0.42 | 0.170 | 1.4 % |
| fire-prior-m1-s0 | 47 | 1.34 | 0.40 | 0.166 | 0.9 % |
| fire-prior-m1-s1 | 50 | 1.66 | 0.66 | 0.180 | 1.5 % |
| fire-prior-m1-s2 | 50 | 1.40 | 0.40 | 0.175 | 1.4 % |
| fire-prior-m5-s0 | 47 | 1.30 | 0.36 | 0.147 | 0.9 % |
| fire-prior-m5-s1 | 50 | 1.34 | 0.34 | 0.158 | 1.2 % |
| fire-prior-m5-s2 | 50 | 1.44 | 0.44 | 0.187 | 1.4 % |
