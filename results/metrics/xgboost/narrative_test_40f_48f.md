# Task 5.5 Step 1: classic against class-relative narratives (test flows, 5 seeds, mean +/- std)

## 40f

| metric | classic | class-relative |
|---|---|---|
| narratives | 230 +/- 0 | 230 +/- 0 |
| cited numeric features read "typical" | 0.452 +/- 0.016 | 0.000 +/- 0.000 |
| features cited per narrative | 4.108 +/- 0.061 | 2.558 +/- 0.056 |
| numeric features cited per narrative | 3.430 +/- 0.076 | 1.880 +/- 0.081 |
| narratives citing no numeric feature | 0.004 +/- 0.008 | 0.073 +/- 0.011 |
| (a) cited features are positive top-5 SHAP features | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (b) cue exact vs training z-score | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (c) categorical named | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (d) action matches the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (e) no false statement about the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (f) cue direction agrees with the SHAP trend | 0.780 +/- 0.016 | 0.780 +/- 0.016 |
| (g) clauses equal an independent computation | n/a | 1.000 +/- 0.000 |
| calibrated number = temperature-scaled probability | n/a | 1.000 +/- 0.000 |

### 40f per predicted class

| predicted class (stratum) | flows per seed | "typical" share: classic -> class-relative | features cited: classic -> class-relative | (f): classic -> class-relative |
|---|---|---|---|---|
| Exploits | 25 | 0.462 +/- 0.035 -> 0.000 +/- 0.000 | 4.368 +/- 0.137 -> 2.640 +/- 0.075 | 0.693 +/- 0.059 -> 0.693 +/- 0.059 |
| FP-Normal | 30 | 0.369 +/- 0.025 -> 0.000 +/- 0.000 | 4.320 +/- 0.159 -> 2.993 +/- 0.182 | 0.823 +/- 0.026 -> 0.823 +/- 0.026 |
| Fuzzers | 25 | 0.409 +/- 0.053 -> 0.000 +/- 0.000 | 4.200 +/- 0.075 -> 2.816 +/- 0.254 | 0.876 +/- 0.038 -> 0.876 +/- 0.038 |
| Generic | 25 | 0.611 +/- 0.056 -> 0.000 +/- 0.000 | 4.200 +/- 0.113 -> 2.136 +/- 0.185 | 0.656 +/- 0.175 -> 0.656 +/- 0.175 |
| Normal | 25 | 0.321 +/- 0.045 -> 0.000 +/- 0.000 | 4.464 +/- 0.092 -> 3.216 +/- 0.236 | 0.895 +/- 0.073 -> 0.895 +/- 0.073 |
| Overlap-Group-1 | 25 | 0.519 +/- 0.046 -> 0.000 +/- 0.000 | 4.024 +/- 0.197 -> 2.368 +/- 0.214 | 0.437 +/- 0.094 -> 0.437 +/- 0.094 |
| Reconnaissance | 25 | 0.416 +/- 0.109 -> 0.000 +/- 0.000 | 4.816 +/- 0.036 -> 2.928 +/- 0.512 | 0.976 +/- 0.024 -> 0.976 +/- 0.024 |
| Unknown | 50 | 0.528 +/- 0.025 -> 0.000 +/- 0.000 | 3.268 +/- 0.129 -> 1.920 +/- 0.141 | 0.688 +/- 0.063 -> 0.688 +/- 0.063 |

## 48f

| metric | classic | class-relative |
|---|---|---|
| narratives | 230 +/- 0 | 230 +/- 0 |
| cited numeric features read "typical" | 0.365 +/- 0.036 | 0.000 +/- 0.000 |
| features cited per narrative | 4.018 +/- 0.037 | 2.714 +/- 0.140 |
| numeric features cited per narrative | 3.568 +/- 0.097 | 2.263 +/- 0.130 |
| narratives citing no numeric feature | 0.001 +/- 0.002 | 0.040 +/- 0.014 |
| (a) cited features are positive top-5 SHAP features | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (b) cue exact vs training z-score | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (c) categorical named | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (d) action matches the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (e) no false statement about the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (f) cue direction agrees with the SHAP trend | 0.733 +/- 0.019 | 0.733 +/- 0.019 |
| (g) clauses equal an independent computation | n/a | 1.000 +/- 0.000 |
| calibrated number = temperature-scaled probability | n/a | 1.000 +/- 0.000 |

### 48f per predicted class

| predicted class (stratum) | flows per seed | "typical" share: classic -> class-relative | features cited: classic -> class-relative | (f): classic -> class-relative |
|---|---|---|---|---|
| Exploits | 25 | 0.303 +/- 0.055 -> 0.000 +/- 0.000 | 4.544 +/- 0.176 -> 3.312 +/- 0.270 | 0.722 +/- 0.055 -> 0.722 +/- 0.055 |
| FP-Normal | 30 | 0.321 +/- 0.030 -> 0.000 +/- 0.000 | 4.380 +/- 0.150 -> 3.120 +/- 0.227 | 0.675 +/- 0.032 -> 0.675 +/- 0.032 |
| Fuzzers | 25 | 0.403 +/- 0.039 -> 0.000 +/- 0.000 | 4.192 +/- 0.134 -> 2.680 +/- 0.080 | 0.830 +/- 0.089 -> 0.830 +/- 0.089 |
| Generic | 25 | 0.607 +/- 0.031 -> 0.000 +/- 0.000 | 4.232 +/- 0.158 -> 2.232 +/- 0.087 | 0.262 +/- 0.172 -> 0.262 +/- 0.172 |
| Normal | 25 | 0.247 +/- 0.074 -> 0.000 +/- 0.000 | 3.280 +/- 0.102 -> 2.480 +/- 0.172 | 0.909 +/- 0.053 -> 0.909 +/- 0.053 |
| Overlap-Group-1 | 25 | 0.303 +/- 0.042 -> 0.000 +/- 0.000 | 3.960 +/- 0.188 -> 2.976 +/- 0.218 | 0.550 +/- 0.043 -> 0.550 +/- 0.043 |
| Reconnaissance | 25 | 0.372 +/- 0.088 -> 0.000 +/- 0.000 | 4.896 +/- 0.061 -> 3.176 +/- 0.419 | 0.991 +/- 0.008 -> 0.991 +/- 0.008 |
| Unknown | 50 | 0.382 +/- 0.023 -> 0.000 +/- 0.000 | 3.304 +/- 0.151 -> 2.184 +/- 0.123 | 0.681 +/- 0.043 -> 0.681 +/- 0.043 |

## Calibration (temperature fitted on block-grouped validation; ECE of the known official-test flows, 15 bins)

| pool | temperature | ECE raw | ECE calibrated |
|---|---|---|---|
| 40f | 1.18 +/- 0.09 | 0.093 +/- 0.008 | 0.070 +/- 0.006 |
| 48f | 1.26 +/- 0.10 | 0.115 +/- 0.010 | 0.086 +/- 0.002 |

## Failures

| style | f_direction |
|---|---|
| class_relative | 1112 |
| classic | 1112 |

Failures other than the cue-direction check (f): 0.
