# Task 2.7 Step 2: temperature scaling and class-prior correction, official test, mean +/- std over seeds 42-46

`calibrated` and `calibrated_valprior` are ZERO-SHOT; `calibrated_em` is TRANSDUCTIVE (uses the unlabelled test features). The same transformation is applied to validation and test; the det95 threshold is chosen on the transformed validation scores.

## 40f

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default | zero-shot | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.256 +/- 0.010 | 0.255 +/- 0.007 | 0.950 +/- 0.003 | 0.093 +/- 0.008 | 0.237 +/- 0.053 |
| calibrated | zero-shot | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.259 +/- 0.010 | 0.256 +/- 0.007 | 0.951 +/- 0.003 | 0.070 +/- 0.006 | 0.237 +/- 0.052 |
| calibrated_valprior | zero-shot | 0.766 +/- 0.060 | 0.718 +/- 0.022 | 0.230 +/- 0.123 | 0.256 +/- 0.011 | 0.253 +/- 0.007 | 0.951 +/- 0.003 | 0.060 +/- 0.060 | 0.241 +/- 0.118 |
| calibrated_em | transductive | 0.775 +/- 0.023 | 0.680 +/- 0.030 | 0.196 +/- 0.038 | 0.249 +/- 0.008 | 0.245 +/- 0.008 | 0.952 +/- 0.004 | 0.044 +/- 0.015 | 0.037 +/- 0.028 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| calibrated | +0.0029 | 0 of 5 | +0.0008 | no |
| calibrated_valprior | +0.0008 | 2 of 5 | +0.0006 | no |
| calibrated_em | -0.0066 | 5 of 5 | +0.0012 | no |

Temperature (mean) 1.18. Diagnostic only, the true shares never enter a fit: L1 distance to the true test shares: EM estimate 0.233 +/- 0.037, model prior 0.600 +/- 0.035, validation shares 0.452 +/- 0.336. EM validation gate (simulated shifts) passes in 4 of 5 seeds.

| class | estimated share | true share |
|---|---|---|
| Exploits | 0.162 | 0.139 |
| Fuzzers | 0.182 | 0.088 |
| Generic | 0.059 | 0.063 |
| Normal | 0.528 | 0.620 |
| Overlap-Group-1 | 0.028 | 0.045 |
| Reconnaissance | 0.041 | 0.045 |

## 45f

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.248 +/- 0.012 | 0.264 +/- 0.016 | 0.943 +/- 0.002 | 0.116 +/- 0.009 | 0.353 +/- 0.045 |
| calibrated | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.251 +/- 0.013 | 0.261 +/- 0.018 | 0.946 +/- 0.002 | 0.086 +/- 0.003 | 0.366 +/- 0.050 |
| calibrated_valprior | zero-shot | 0.753 +/- 0.052 | 0.706 +/- 0.019 | 0.249 +/- 0.108 | 0.249 +/- 0.012 | 0.259 +/- 0.017 | 0.945 +/- 0.003 | 0.074 +/- 0.057 | 0.309 +/- 0.114 |
| calibrated_em | transductive | 0.759 +/- 0.017 | 0.682 +/- 0.033 | 0.228 +/- 0.030 | 0.244 +/- 0.010 | 0.259 +/- 0.014 | 0.943 +/- 0.003 | 0.065 +/- 0.011 | 0.120 +/- 0.084 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| calibrated | +0.0029 | 0 of 5 | +0.0033 | no |
| calibrated_valprior | +0.0007 | 1 of 5 | +0.0029 | no |
| calibrated_em | -0.0037 | 4 of 5 | +0.0007 | no |

Temperature (mean) 1.25. Diagnostic only, the true shares never enter a fit: L1 distance to the true test shares: EM estimate 0.245 +/- 0.032, model prior 0.600 +/- 0.035, validation shares 0.452 +/- 0.336. EM validation gate (simulated shifts) passes in 4 of 5 seeds.

| class | estimated share | true share |
|---|---|---|
| Exploits | 0.164 | 0.139 |
| Fuzzers | 0.186 | 0.088 |
| Generic | 0.059 | 0.063 |
| Normal | 0.516 | 0.620 |
| Overlap-Group-1 | 0.036 | 0.045 |
| Reconnaissance | 0.040 | 0.045 |

## 48f

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default | zero-shot | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.248 +/- 0.011 | 0.246 +/- 0.022 | 0.950 +/- 0.005 | 0.115 +/- 0.010 | 0.344 +/- 0.045 |
| calibrated | zero-shot | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.249 +/- 0.012 | 0.242 +/- 0.023 | 0.952 +/- 0.005 | 0.086 +/- 0.002 | 0.357 +/- 0.047 |
| calibrated_valprior | zero-shot | 0.757 +/- 0.053 | 0.712 +/- 0.020 | 0.249 +/- 0.108 | 0.248 +/- 0.012 | 0.241 +/- 0.024 | 0.952 +/- 0.006 | 0.074 +/- 0.060 | 0.290 +/- 0.131 |
| calibrated_em | transductive | 0.762 +/- 0.018 | 0.691 +/- 0.030 | 0.230 +/- 0.032 | 0.244 +/- 0.010 | 0.241 +/- 0.020 | 0.951 +/- 0.005 | 0.065 +/- 0.012 | 0.113 +/- 0.082 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| calibrated | +0.0011 | 1 of 5 | +0.0022 | no |
| calibrated_valprior | -0.0002 | 3 of 5 | +0.0022 | no |
| calibrated_em | -0.0039 | 5 of 5 | +0.0006 | no |

Temperature (mean) 1.26. Diagnostic only, the true shares never enter a fit: L1 distance to the true test shares: EM estimate 0.250 +/- 0.033, model prior 0.600 +/- 0.035, validation shares 0.452 +/- 0.336. EM validation gate (simulated shifts) passes in 4 of 5 seeds.

| class | estimated share | true share |
|---|---|---|
| Exploits | 0.166 | 0.139 |
| Fuzzers | 0.186 | 0.088 |
| Generic | 0.059 | 0.063 |
| Normal | 0.513 | 0.620 |
| Overlap-Group-1 | 0.037 | 0.045 |
| Reconnaissance | 0.039 | 0.045 |

