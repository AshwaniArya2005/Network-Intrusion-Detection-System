# Task 5 / 5.5 tables (XGBoost): faithfulness, narrative audit, class-relative narrative, false-positive explanations

Merged in the Task 7 cleanup from the per-table files named below. Each section is the original file with every line unchanged except that its headings are demoted by two levels; nothing was added to or removed from any table or caveat. The generation scripts still write the original per-table names if re-run.

## Source: xai_faithfulness_40f_45f_48f.md

### Task 5 Steps 1-2: SHAP additivity and faithfulness (XGBoost, official split, 5 seeds)

Sample: 300 flows per predicted class + 200 flagged-Unknown flows per model and source (official test = known + zero-day flows; validation = block-grouped validation flows).

#### Step 1: SHAP additivity (sum of SHAP values + expected value against the raw margin of the predicted class)

| pool | tier | flows checked | maximum error | flows over 1e-3 |
|---|---|---|---|---|
| 40f | 40 | 19868 | 1.19e-05 | 0 |
| 40f | 30 | 19867 | 1.07e-05 | 0 |
| 40f | 15 | 19869 | 9.95e-06 | 0 |
| 45f | 45 | 19863 | 1.39e-05 | 0 |
| 45f | 30 | 19857 | 1.21e-05 | 0 |
| 45f | 15 | 19870 | 1.32e-05 | 0 |
| 48f | 48 | 19865 | 1.08e-05 | 0 |
| 48f | 30 | 19860 | 1.08e-05 | 0 |
| 48f | 15 | 19873 | 1.02e-05 | 0 |

#### Primary metric: probability drop at k = 5, top-SHAP removal minus random removal (median baseline), official-test flows

| pool | tier | features | difference (mean +/- std over seeds) | seeds with interval above 0 and difference >= 0.05 | faithful (declared reading) |
|---|---|---|---|---|---|
| 40f | 40 | 40 | 0.512 +/- 0.012 | 5 of 5 | yes |
| 40f | 30 | 30 | 0.466 +/- 0.011 | 5 of 5 | yes |
| 40f | 15 | 15 | 0.333 +/- 0.011 | 5 of 5 | yes |
| 45f | 45 | 45 | 0.501 +/- 0.023 | 5 of 5 | yes |
| 45f | 30 | 30 | 0.429 +/- 0.014 | 5 of 5 | yes |
| 45f | 15 | 15 | 0.344 +/- 0.012 | 5 of 5 | yes |
| 48f | 48 | 48 | 0.553 +/- 0.011 | 5 of 5 | yes |
| 48f | 30 | 30 | 0.489 +/- 0.007 | 5 of 5 | yes |
| 48f | 15 | 15 | 0.340 +/- 0.026 | 5 of 5 | yes |

#### Deletion curve, whole pools, official-test flows, baseline = training median (probability drop; flip rate)

| pool | k | top SHAP | random | least important | top: class flips | random: class flips | least: class flips |
|---|---|---|---|---|---|---|---|
| 40f | 1 | 0.273 +/- 0.050 | 0.035 +/- 0.018 | 0.003 +/- 0.002 | 0.342 +/- 0.087 | 0.075 +/- 0.034 | 0.018 +/- 0.014 |
| 40f | 3 | 0.547 +/- 0.018 | 0.109 +/- 0.053 | 0.011 +/- 0.011 | 0.790 +/- 0.033 | 0.186 +/- 0.075 | 0.047 +/- 0.038 |
| 40f | 5 | 0.619 +/- 0.011 | 0.182 +/- 0.083 | 0.022 +/- 0.022 | 0.860 +/- 0.018 | 0.280 +/- 0.111 | 0.074 +/- 0.055 |
| 40f | 10 | 0.668 +/- 0.013 | 0.344 +/- 0.121 | 0.074 +/- 0.076 | 0.883 +/- 0.029 | 0.485 +/- 0.166 | 0.167 +/- 0.116 |
| 45f | 1 | 0.234 +/- 0.031 | 0.032 +/- 0.015 | 0.003 +/- 0.003 | 0.295 +/- 0.052 | 0.068 +/- 0.029 | 0.017 +/- 0.014 |
| 45f | 3 | 0.513 +/- 0.025 | 0.102 +/- 0.047 | 0.012 +/- 0.010 | 0.713 +/- 0.040 | 0.172 +/- 0.064 | 0.046 +/- 0.037 |
| 45f | 5 | 0.598 +/- 0.023 | 0.173 +/- 0.079 | 0.025 +/- 0.021 | 0.814 +/- 0.041 | 0.263 +/- 0.104 | 0.070 +/- 0.055 |
| 45f | 10 | 0.670 +/- 0.011 | 0.330 +/- 0.126 | 0.075 +/- 0.070 | 0.893 +/- 0.023 | 0.464 +/- 0.167 | 0.151 +/- 0.109 |
| 48f | 1 | 0.314 +/- 0.053 | 0.035 +/- 0.020 | 0.000 +/- 0.001 | 0.375 +/- 0.094 | 0.071 +/- 0.038 | 0.013 +/- 0.013 |
| 48f | 3 | 0.594 +/- 0.022 | 0.106 +/- 0.059 | 0.001 +/- 0.004 | 0.796 +/- 0.042 | 0.174 +/- 0.088 | 0.029 +/- 0.022 |
| 48f | 5 | 0.635 +/- 0.016 | 0.175 +/- 0.093 | 0.014 +/- 0.022 | 0.836 +/- 0.033 | 0.262 +/- 0.130 | 0.058 +/- 0.047 |
| 48f | 10 | 0.685 +/- 0.027 | 0.321 +/- 0.140 | 0.079 +/- 0.101 | 0.900 +/- 0.035 | 0.439 +/- 0.187 | 0.162 +/- 0.151 |

#### Deletion curve, whole pools, official-test flows, baseline = a random training row (probability drop; flip rate)

| pool | k | top SHAP | random | least important | top: class flips | random: class flips | least: class flips |
|---|---|---|---|---|---|---|---|
| 40f | 1 | 0.240 +/- 0.036 | 0.038 +/- 0.018 | 0.005 +/- 0.006 | 0.311 +/- 0.062 | 0.083 +/- 0.033 | 0.023 +/- 0.019 |
| 40f | 3 | 0.517 +/- 0.014 | 0.117 +/- 0.055 | 0.020 +/- 0.022 | 0.726 +/- 0.024 | 0.200 +/- 0.076 | 0.058 +/- 0.048 |
| 40f | 5 | 0.603 +/- 0.008 | 0.195 +/- 0.088 | 0.041 +/- 0.046 | 0.818 +/- 0.013 | 0.303 +/- 0.112 | 0.096 +/- 0.077 |
| 40f | 10 | 0.656 +/- 0.015 | 0.361 +/- 0.125 | 0.124 +/- 0.129 | 0.870 +/- 0.013 | 0.509 +/- 0.164 | 0.226 +/- 0.169 |
| 45f | 1 | 0.223 +/- 0.035 | 0.038 +/- 0.018 | 0.006 +/- 0.006 | 0.286 +/- 0.054 | 0.080 +/- 0.033 | 0.026 +/- 0.023 |
| 45f | 3 | 0.497 +/- 0.023 | 0.115 +/- 0.054 | 0.021 +/- 0.020 | 0.686 +/- 0.039 | 0.194 +/- 0.076 | 0.060 +/- 0.050 |
| 45f | 5 | 0.588 +/- 0.014 | 0.195 +/- 0.089 | 0.042 +/- 0.041 | 0.792 +/- 0.027 | 0.298 +/- 0.119 | 0.094 +/- 0.073 |
| 45f | 10 | 0.657 +/- 0.018 | 0.359 +/- 0.133 | 0.128 +/- 0.125 | 0.863 +/- 0.010 | 0.505 +/- 0.177 | 0.223 +/- 0.173 |
| 48f | 1 | 0.285 +/- 0.028 | 0.040 +/- 0.021 | 0.003 +/- 0.004 | 0.358 +/- 0.052 | 0.082 +/- 0.038 | 0.019 +/- 0.017 |
| 48f | 3 | 0.556 +/- 0.017 | 0.125 +/- 0.062 | 0.016 +/- 0.017 | 0.741 +/- 0.032 | 0.204 +/- 0.087 | 0.058 +/- 0.049 |
| 48f | 5 | 0.619 +/- 0.013 | 0.201 +/- 0.094 | 0.042 +/- 0.046 | 0.812 +/- 0.023 | 0.303 +/- 0.127 | 0.099 +/- 0.079 |
| 48f | 10 | 0.666 +/- 0.013 | 0.356 +/- 0.128 | 0.118 +/- 0.121 | 0.867 +/- 0.012 | 0.496 +/- 0.170 | 0.210 +/- 0.161 |

#### Insertion and sufficiency at k = 5, whole pools, official-test flows, median baseline

Comprehensiveness = the deletion drop; sufficiency = the original probability minus the probability with ONLY the chosen features on the baseline vector (lower = the chosen features alone nearly reproduce the prediction).

| pool | comprehensiveness: top / random | sufficiency: top / random |
|---|---|---|
| 40f | 0.619 +/- 0.011 / 0.182 +/- 0.083 | 0.163 +/- 0.029 / 0.559 +/- 0.045 |
| 45f | 0.598 +/- 0.023 / 0.173 +/- 0.079 | 0.217 +/- 0.056 / 0.569 +/- 0.059 |
| 48f | 0.635 +/- 0.016 / 0.175 +/- 0.093 | 0.200 +/- 0.034 / 0.562 +/- 0.046 |

#### Primary metric per predicted class (whole pools, official-test flows; mean +/- std over seeds)

| pool | stratum | flows per seed | difference | interval above 0 in |
|---|---|---|---|---|
| 40f | Exploits | 300 | 0.519 +/- 0.081 | 15 of 15 |
| 40f | Fuzzers | 300 | 0.304 +/- 0.099 | 15 of 15 |
| 40f | Generic | 300 | 0.776 +/- 0.111 | 15 of 15 |
| 40f | Normal | 300 | 0.182 +/- 0.025 | 15 of 15 |
| 40f | Overlap-Group-1 | 300 | 0.382 +/- 0.091 | 15 of 15 |
| 40f | Reconnaissance | 300 | 0.590 +/- 0.149 | 15 of 15 |
| 40f | Unknown | 200 | 0.238 +/- 0.034 | 15 of 15 |
| 45f | Exploits | 300 | 0.404 +/- 0.132 | 15 of 15 |
| 45f | Fuzzers | 300 | 0.264 +/- 0.075 | 15 of 15 |
| 45f | Generic | 300 | 0.760 +/- 0.108 | 15 of 15 |
| 45f | Normal | 300 | 0.263 +/- 0.140 | 15 of 15 |
| 45f | Overlap-Group-1 | 300 | 0.391 +/- 0.091 | 15 of 15 |
| 45f | Reconnaissance | 300 | 0.593 +/- 0.174 | 15 of 15 |
| 45f | Unknown | 200 | 0.235 +/- 0.047 | 15 of 15 |
| 48f | Exploits | 300 | 0.290 +/- 0.039 | 15 of 15 |
| 48f | Fuzzers | 300 | 0.392 +/- 0.172 | 15 of 15 |
| 48f | Generic | 300 | 0.785 +/- 0.106 | 15 of 15 |
| 48f | Normal | 300 | 0.650 +/- 0.063 | 15 of 15 |
| 48f | Overlap-Group-1 | 300 | 0.258 +/- 0.122 | 15 of 15 |
| 48f | Reconnaissance | 300 | 0.551 +/- 0.188 | 15 of 15 |
| 48f | Unknown | 200 | 0.217 +/- 0.052 | 15 of 15 |

#### Shift check: the primary metric on official-test flows against block-grouped validation flows (flows pooled over the 5 seeds; two-sample bootstrap)

| pool | tier | official test | validation | test minus validation (95% interval) | faithfulness lost under the shift (declared reading) |
|---|---|---|---|---|---|
| 40f | 40 | 0.512 | 0.513 | -0.001 (-0.010, +0.009) | no |
| 40f | 30 | 0.466 | 0.470 | -0.004 (-0.013, +0.006) | no |
| 40f | 15 | 0.333 | 0.334 | -0.001 (-0.010, +0.008) | no |
| 45f | 45 | 0.501 | 0.495 | +0.006 (-0.004, +0.015) | no |
| 45f | 30 | 0.429 | 0.436 | -0.007 (-0.017, +0.002) | no |
| 45f | 15 | 0.344 | 0.349 | -0.005 (-0.014, +0.004) | no |
| 48f | 48 | 0.553 | 0.540 | +0.013 (+0.003, +0.023) | no |
| 48f | 30 | 0.489 | 0.486 | +0.002 (-0.008, +0.013) | no |
| 48f | 15 | 0.340 | 0.340 | +0.000 (-0.009, +0.011) | no |

## Source: xai_audit_40f_48f.md

### Task 5 Steps 1 and 3: narrative audit through the dashboard path (XGBoost, official split, 5 seeds x 200 flows per pool)

| check | 40f | 48f |
|---|---|---|
| quoted confidence = model probability | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| JSON confidence = model probability | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (a) cited features are positive top-5 SHAP features | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (b) cue exact vs training z-score (per cited feature) | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (b) cue direction (per cited feature) | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (c) categorical named by category (per cited feature) | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (d) action matches the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (e) no false statement about the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (f) cue direction agrees with the SHAP-vs-value relation (determined cases) | 0.757 +/- 0.018 | 0.722 +/- 0.013 |

40f: of the cited numeric features 46.9% carry the cue "typical" (no direction claimed), 4.5% have no monotone SHAP-vs-value relation, and in 7.5% of the narratives no cited numeric feature carries a direction at all; 0.0% of narratives say the decision was diffuse.

48f: of the cited numeric features 35.7% carry the cue "typical" (no direction claimed), 1.7% have no monotone SHAP-vs-value relation, and in 2.7% of the narratives no cited numeric feature carries a direction at all; 0.0% of narratives say the decision was diffuse.

#### Per predicted class (mean over seeds; all deterministic checks a-e must be 1.000)

| pool | stratum | narratives | (a) | (b) exact | (d) | (e) | (f) consistent |
|---|---|---|---|---|---|---|---|
| 40f | Exploits | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.719 |
| 40f | Fuzzers | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.846 |
| 40f | Generic | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.611 |
| 40f | Normal | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.891 |
| 40f | Overlap-Group-1 | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.361 |
| 40f | Reconnaissance | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.993 |
| 40f | Unknown | 250 | 1.000 | 1.000 | 1.000 | 1.000 | 0.692 |
| 48f | Exploits | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.718 |
| 48f | Fuzzers | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.753 |
| 48f | Generic | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.253 |
| 48f | Normal | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.892 |
| 48f | Overlap-Group-1 | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.489 |
| 48f | Reconnaissance | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 48f | Unknown | 250 | 1.000 | 1.000 | 1.000 | 1.000 | 0.676 |

#### Failures

| pool | f_direction |
|---|---|
| 40f | 403 |
| 48f | 622 |

Most frequent reasons:

- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.44 on training rows) (54)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.55 on training rows) (32)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.47 on training rows) (32)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.46 on training rows) (32)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.49 on training rows) (31)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.51 on training rows) (30)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.43 on training rows) (28)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.45 on training rows) (26)

#### Audit rates on official-test flows against validation flows (the shift check)

| check | pool | official test | validation | test minus validation |
|---|---|---|---|---|
| (a) cited features in the SHAP top 5 | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (a) cited features in the SHAP top 5 | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (b) cue exact | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (b) cue exact | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (c) categorical named | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (c) categorical named | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (d) action | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (d) action | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (e) label statement | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (e) label statement | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (f) directional consistency | 40f | 0.757 +/- 0.018 | 0.788 +/- 0.017 | -0.030 |
| (f) directional consistency | 48f | 0.722 +/- 0.013 | 0.731 +/- 0.029 | -0.009 |
| share of cited features read "typical" | 40f | 0.469 +/- 0.017 | 0.479 +/- 0.034 | -0.010 |
| share of cited features read "typical" | 48f | 0.357 +/- 0.031 | 0.363 +/- 0.030 | -0.005 |
| share with no monotone SHAP-vs-value relation | 40f | 0.045 +/- 0.013 | 0.034 +/- 0.013 | +0.011 |
| share with no monotone SHAP-vs-value relation | 48f | 0.017 +/- 0.010 | 0.016 +/- 0.009 | +0.000 |

## Source: narrative_test_40f_48f.md

### Task 5.5 Step 1: classic against class-relative narratives (test flows, 5 seeds, mean +/- std)

#### 40f

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

##### 40f per predicted class

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

#### 48f

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

##### 48f per predicted class

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

#### Calibration (temperature fitted on block-grouped validation; ECE of the known official-test flows, 15 bins)

| pool | temperature | ECE raw | ECE calibrated |
|---|---|---|---|
| 40f | 1.18 +/- 0.09 | 0.093 +/- 0.008 | 0.070 +/- 0.006 |
| 48f | 1.26 +/- 0.10 | 0.115 +/- 0.010 | 0.086 +/- 0.002 |

#### Failures

| style | f_direction |
|---|---|
| class_relative | 1112 |
| classic | 1112 |

Failures other than the cue-direction check (f): 0.

## Source: narrative_falsepos_40f_48f.md

### Task 5.5 Step 2: explanations of false-positive flows (official test, 5 seeds, 300 flows per group and model, mean +/- std)

FP-attack = true Normal predicted as an attack; FP-Fuzzers = true Normal predicted as Fuzzers; TN = true Normal predicted Normal; TP-Fuzzers = true Fuzzers predicted Fuzzers.

#### 40f

##### (a) Deletion faithfulness: probability drop at k = 5, top SHAP minus random removal (median baseline; random-row baseline in brackets)

| group | flows in test | top SHAP drop | random drop | difference (std over seeds) | seeds with interval above 0 and difference >= 0.05 | top: class flips |
|---|---|---|---|---|---|---|
| TN | 24057 | 0.215 +/- 0.030 | 0.031 +/- 0.012 | 0.184 +/- 0.024 (0.386 +/- 0.029) | 5 of 5 | 0.263 +/- 0.086 |
| FP-attack | 9775 | 0.510 +/- 0.053 | 0.161 +/- 0.015 | 0.349 +/- 0.051 (0.336 +/- 0.017) | 5 of 5 | 0.904 +/- 0.063 |
| FP-Fuzzers | 8218 | 0.531 +/- 0.067 | 0.172 +/- 0.028 | 0.359 +/- 0.065 (0.342 +/- 0.034) | 5 of 5 | 0.881 +/- 0.077 |
| TP-Fuzzers | 3658 | 0.615 +/- 0.042 | 0.181 +/- 0.014 | 0.435 +/- 0.042 (0.416 +/- 0.010) | 5 of 5 | 0.893 +/- 0.060 |

##### (c) Confidence on these flows

| group | raw confidence | calibrated confidence | raw >= 0.90 | calibrated >= 0.90 | flagged Unknown | features cited (class-relative) | class-atypicality of cited features |
|---|---|---|---|---|---|---|---|
| TN | 0.928 +/- 0.011 | 0.920 +/- 0.013 | 0.826 +/- 0.026 | 0.819 +/- 0.027 | 0.044 +/- 0.010 | 3.12 +/- 0.17 | 0.411 +/- 0.039 |
| FP-attack | 0.675 +/- 0.008 | 0.638 +/- 0.012 | 0.088 +/- 0.026 | 0.043 +/- 0.022 | 0.130 +/- 0.036 | 2.94 +/- 0.14 | 0.457 +/- 0.020 |
| FP-Fuzzers | 0.701 +/- 0.011 | 0.662 +/- 0.010 | 0.105 +/- 0.016 | 0.048 +/- 0.014 | 0.065 +/- 0.034 | 3.02 +/- 0.11 | 0.463 +/- 0.014 |
| TP-Fuzzers | 0.771 +/- 0.011 | 0.734 +/- 0.015 | 0.294 +/- 0.040 | 0.206 +/- 0.031 | 0.051 +/- 0.018 | 2.71 +/- 0.09 | 0.500 +/- 0.042 |

##### (c) Does anything separate a false positive from a correct flow? (AUROC; 0.5 = nothing; positive = the false-positive group)

| false positives | compared with | score | AUROC |
|---|---|---|---|
| FP-Fuzzers | TP-Fuzzers | 1 - raw confidence | 0.632 +/- 0.022 |
| FP-Fuzzers | TP-Fuzzers | 1 - calibrated confidence | 0.632 +/- 0.022 |
| FP-Fuzzers | TP-Fuzzers | class-atypicality of the cited features | 0.470 +/- 0.035 |
| FP-attack | TN | 1 - raw confidence | 0.886 +/- 0.019 |
| FP-attack | TN | 1 - calibrated confidence | 0.887 +/- 0.019 |
| FP-attack | TN | class-atypicality of the cited features | 0.553 +/- 0.039 |

##### (b) Features the classic narrative cites most often (share of narratives, mean over seeds)

| group | top cited features |
|---|---|
| TN | ackdat (76%), dload (63%), dloss (41%), synack (39%), dbytes (37%) |
| FP-attack | service (76%), dload (75%), avg_pkt_size (52%), sbytes (47%), smean (44%) |
| FP-Fuzzers | dload (88%), service (77%), sbytes (55%), avg_pkt_size (50%), smean (48%) |
| TP-Fuzzers | dload (76%), service (75%), sbytes (70%), smean (42%), dbytes (38%) |

#### 48f

##### (a) Deletion faithfulness: probability drop at k = 5, top SHAP minus random removal (median baseline; random-row baseline in brackets)

| group | flows in test | top SHAP drop | random drop | difference (std over seeds) | seeds with interval above 0 and difference >= 0.05 | top: class flips |
|---|---|---|---|---|---|---|
| TN | 23754 | 0.748 +/- 0.027 | 0.055 +/- 0.018 | 0.693 +/- 0.038 (0.469 +/- 0.058) | 5 of 5 | 0.848 +/- 0.021 |
| FP-attack | 10078 | 0.594 +/- 0.157 | 0.120 +/- 0.039 | 0.474 +/- 0.122 (0.387 +/- 0.010) | 5 of 5 | 0.891 +/- 0.197 |
| FP-Fuzzers | 8594 | 0.640 +/- 0.192 | 0.131 +/- 0.036 | 0.509 +/- 0.159 (0.404 +/- 0.022) | 5 of 5 | 0.903 +/- 0.218 |
| TP-Fuzzers | 3472 | 0.701 +/- 0.133 | 0.144 +/- 0.033 | 0.558 +/- 0.104 (0.447 +/- 0.022) | 5 of 5 | 0.929 +/- 0.158 |

##### (c) Confidence on these flows

| group | raw confidence | calibrated confidence | raw >= 0.90 | calibrated >= 0.90 | flagged Unknown | features cited (class-relative) | class-atypicality of cited features |
|---|---|---|---|---|---|---|---|
| TN | 0.940 +/- 0.010 | 0.932 +/- 0.009 | 0.843 +/- 0.023 | 0.841 +/- 0.023 | 0.026 +/- 0.017 | 2.49 +/- 0.11 | 0.326 +/- 0.031 |
| FP-attack | 0.719 +/- 0.011 | 0.668 +/- 0.015 | 0.128 +/- 0.018 | 0.057 +/- 0.023 | 0.089 +/- 0.052 | 2.88 +/- 0.12 | 0.384 +/- 0.018 |
| FP-Fuzzers | 0.742 +/- 0.023 | 0.692 +/- 0.013 | 0.165 +/- 0.047 | 0.072 +/- 0.019 | 0.044 +/- 0.032 | 3.00 +/- 0.15 | 0.424 +/- 0.024 |
| TP-Fuzzers | 0.778 +/- 0.016 | 0.723 +/- 0.019 | 0.297 +/- 0.047 | 0.157 +/- 0.046 | 0.065 +/- 0.029 | 2.73 +/- 0.10 | 0.414 +/- 0.023 |

##### (c) Does anything separate a false positive from a correct flow? (AUROC; 0.5 = nothing; positive = the false-positive group)

| false positives | compared with | score | AUROC |
|---|---|---|---|
| FP-Fuzzers | TP-Fuzzers | 1 - raw confidence | 0.580 +/- 0.051 |
| FP-Fuzzers | TP-Fuzzers | 1 - calibrated confidence | 0.569 +/- 0.052 |
| FP-Fuzzers | TP-Fuzzers | class-atypicality of the cited features | 0.519 +/- 0.031 |
| FP-attack | TN | 1 - raw confidence | 0.892 +/- 0.016 |
| FP-attack | TN | 1 - calibrated confidence | 0.892 +/- 0.017 |
| FP-attack | TN | class-atypicality of the cited features | 0.581 +/- 0.032 |

##### (b) Features the classic narrative cites most often (share of narratives, mean over seeds)

| group | top cited features |
|---|---|
| TN | ct_state_ttl (84%), sttl (71%), ct_srv_dst (51%), ct_srv_src (35%), dload (27%) |
| FP-attack | sttl (95%), smean (47%), ct_dst_src_ltm (46%), sbytes (44%), avg_pkt_size (37%) |
| FP-Fuzzers | sttl (100%), smean (52%), sbytes (51%), ct_dst_src_ltm (48%), ct_srv_dst (39%) |
| TP-Fuzzers | sttl (100%), sbytes (62%), smean (38%), dbytes (36%), service (33%) |

