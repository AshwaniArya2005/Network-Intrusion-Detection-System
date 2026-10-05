# Task 5 Steps 1-2: SHAP additivity and faithfulness (XGBoost, official split, 5 seeds)

Sample: 300 flows per predicted class + 200 flagged-Unknown flows per model and source (official test = known + zero-day flows; validation = block-grouped validation flows).

## Step 1: SHAP additivity (sum of SHAP values + expected value against the raw margin of the predicted class)

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

## Primary metric: probability drop at k = 5, top-SHAP removal minus random removal (median baseline), official-test flows

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

## Deletion curve, whole pools, official-test flows, baseline = training median (probability drop; flip rate)

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

## Deletion curve, whole pools, official-test flows, baseline = a random training row (probability drop; flip rate)

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

## Insertion and sufficiency at k = 5, whole pools, official-test flows, median baseline

Comprehensiveness = the deletion drop; sufficiency = the original probability minus the probability with ONLY the chosen features on the baseline vector (lower = the chosen features alone nearly reproduce the prediction).

| pool | comprehensiveness: top / random | sufficiency: top / random |
|---|---|---|
| 40f | 0.619 +/- 0.011 / 0.182 +/- 0.083 | 0.163 +/- 0.029 / 0.559 +/- 0.045 |
| 45f | 0.598 +/- 0.023 / 0.173 +/- 0.079 | 0.217 +/- 0.056 / 0.569 +/- 0.059 |
| 48f | 0.635 +/- 0.016 / 0.175 +/- 0.093 | 0.200 +/- 0.034 / 0.562 +/- 0.046 |

## Primary metric per predicted class (whole pools, official-test flows; mean +/- std over seeds)

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

## Shift check: the primary metric on official-test flows against block-grouped validation flows (flows pooled over the 5 seeds; two-sample bootstrap)

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
