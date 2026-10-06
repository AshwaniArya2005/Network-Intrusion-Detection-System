# Task 2.7 tables (XGBoost): re-tuning, calibration and class-prior correction, self-training, few-shot budget, final table

Merged in the Task 7 cleanup from the per-table files named below. Each section is the original file with every line unchanged except that its headings are demoted by two levels; nothing was added to or removed from any table or caveat. The generation scripts still write the original per-table names if re-run.

## Source: fpr_study_tuned_40f_45f_48f.md

### Task 2.7 Step 1 (ZERO-SHOT): re-tuning on block-grouped validation, official test, mean +/- std over seeds 42-46

Primary metric `det95_test_fpr` (threshold at 95% detection chosen on block-grouped validation). `earlier_tuned_*` = the Task 2a search on random validation (40 and 48 features only); `blockval_tuned_*` = the 40-trial search on block-grouped validation with the regularised space. Verdict = the declared rule against `default` on the same seeds.

#### 40f

| method | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|
| default | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.256 +/- 0.010 | 0.255 +/- 0.007 | 0.950 +/- 0.003 | 0.093 +/- 0.008 | 0.237 +/- 0.053 |
| earlier_tuned_auc | 0.761 +/- 0.005 | 0.718 +/- 0.002 | 0.245 +/- 0.011 | 0.252 +/- 0.014 | 0.253 +/- 0.009 | 0.950 +/- 0.005 | 0.058 +/- 0.006 | 0.213 +/- 0.038 |
| earlier_tuned_f1 | 0.750 +/- 0.007 | 0.714 +/- 0.003 | 0.269 +/- 0.012 | 0.254 +/- 0.012 | 0.255 +/- 0.009 | 0.950 +/- 0.005 | 0.068 +/- 0.008 | 0.222 +/- 0.051 |
| blockval_tuned_auc | 0.762 +/- 0.005 | 0.714 +/- 0.002 | 0.239 +/- 0.010 | 0.257 +/- 0.014 | 0.261 +/- 0.008 | 0.948 +/- 0.006 | 0.051 +/- 0.006 | 0.239 +/- 0.058 |
| blockval_tuned_f1 | 0.753 +/- 0.006 | 0.713 +/- 0.002 | 0.258 +/- 0.011 | 0.253 +/- 0.014 | 0.262 +/- 0.009 | 0.947 +/- 0.006 | 0.058 +/- 0.007 | 0.273 +/- 0.061 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| earlier_tuned_auc | -0.0035 | 3 of 5 | -0.0007 | no |
| earlier_tuned_f1 | -0.0020 | 4 of 5 | -0.0004 | no |
| blockval_tuned_auc | +0.0010 | 2 of 5 | -0.0022 | no |
| blockval_tuned_f1 | -0.0024 | 3 of 5 | -0.0037 | no |

#### 45f

| method | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|
| default | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.248 +/- 0.012 | 0.264 +/- 0.016 | 0.943 +/- 0.002 | 0.116 +/- 0.009 | 0.353 +/- 0.045 |
| blockval_tuned_auc | 0.726 +/- 0.007 | 0.700 +/- 0.003 | 0.310 +/- 0.013 | 0.258 +/- 0.012 | 0.265 +/- 0.016 | 0.947 +/- 0.002 | 0.093 +/- 0.010 | 0.529 +/- 0.050 |
| blockval_tuned_f1 | 0.747 +/- 0.006 | 0.708 +/- 0.002 | 0.269 +/- 0.014 | 0.255 +/- 0.012 | 0.258 +/- 0.009 | 0.948 +/- 0.003 | 0.072 +/- 0.008 | 0.493 +/- 0.040 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| blockval_tuned_auc | +0.0096 | 0 of 5 | +0.0041 | no |
| blockval_tuned_f1 | +0.0064 | 1 of 5 | +0.0058 | no |

#### 48f

| method | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|
| default | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.248 +/- 0.011 | 0.246 +/- 0.022 | 0.950 +/- 0.005 | 0.115 +/- 0.010 | 0.344 +/- 0.045 |
| earlier_tuned_auc | 0.755 +/- 0.007 | 0.718 +/- 0.003 | 0.265 +/- 0.013 | 0.249 +/- 0.011 | 0.230 +/- 0.015 | 0.957 +/- 0.004 | 0.085 +/- 0.008 | 0.399 +/- 0.052 |
| earlier_tuned_f1 | 0.755 +/- 0.007 | 0.718 +/- 0.003 | 0.265 +/- 0.013 | 0.249 +/- 0.011 | 0.230 +/- 0.015 | 0.957 +/- 0.004 | 0.085 +/- 0.008 | 0.399 +/- 0.052 |
| blockval_tuned_auc | 0.733 +/- 0.006 | 0.709 +/- 0.003 | 0.307 +/- 0.013 | 0.254 +/- 0.014 | 0.230 +/- 0.011 | 0.961 +/- 0.003 | 0.091 +/- 0.010 | 0.546 +/- 0.047 |
| blockval_tuned_f1 | 0.753 +/- 0.007 | 0.716 +/- 0.004 | 0.267 +/- 0.012 | 0.253 +/- 0.011 | 0.227 +/- 0.011 | 0.961 +/- 0.001 | 0.074 +/- 0.008 | 0.496 +/- 0.038 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| earlier_tuned_auc | +0.0012 | 2 of 5 | +0.0071 | no |
| earlier_tuned_f1 | +0.0012 | 2 of 5 | +0.0071 | no |
| blockval_tuned_auc | +0.0066 | 0 of 5 | +0.0103 | no |
| blockval_tuned_f1 | +0.0049 | 0 of 5 | +0.0111 | no |

## Source: fpr_study_prior_40f_45f_48f.md

### Task 2.7 Step 2: temperature scaling and class-prior correction, official test, mean +/- std over seeds 42-46

`calibrated` and `calibrated_valprior` are ZERO-SHOT; `calibrated_em` is TRANSDUCTIVE (uses the unlabelled test features). The same transformation is applied to validation and test; the det95 threshold is chosen on the transformed validation scores.

#### 40f

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

#### 45f

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

#### 48f

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

## Source: fpr_study_self_40f_45f_48f.md

### Task 2.7 Step 3 (TRANSDUCTIVE): self-training, mean +/- std over seeds 42-46

Two rounds, tau = 0.90, pseudo-labelled rows carry 20% of the sample weight, rounds are not cumulative. Pseudo-labels come from the unlabelled blocks and every metric is on the other blocks (200-row gaps). `validation` rows are the check made before looking at the test file (half of the block-grouped validation blocks treated as unlabelled).

#### 40f

##### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.811 +/- 0.111 | 0.729 +/- 0.065 | 0.210 +/- 0.219 | n/a | n/a | n/a |
| self_round1 | transductive | 0.811 +/- 0.111 | 0.729 +/- 0.064 | 0.209 +/- 0.218 | n/a | n/a | n/a |
| self_round2 | transductive | 0.812 +/- 0.110 | 0.704 +/- 0.077 | 0.207 +/- 0.215 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR -0.0034 (lower in 4 of 5 seeds), macro F1 -0.0245.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): fails.

##### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.726 +/- 0.042 | 0.709 +/- 0.025 | 0.314 +/- 0.071 | 0.283 +/- 0.082 | 0.944 +/- 0.007 | 0.090 +/- 0.017 |
| self_round1 | transductive | 0.721 +/- 0.046 | 0.707 +/- 0.027 | 0.325 +/- 0.080 | 0.283 +/- 0.087 | 0.944 +/- 0.009 | 0.101 +/- 0.020 |
| self_round2 | transductive | 0.722 +/- 0.045 | 0.706 +/- 0.025 | 0.324 +/- 0.079 | 0.282 +/- 0.085 | 0.944 +/- 0.007 | 0.101 +/- 0.020 |

Round 2 minus round 0: argmax FPR +0.0097 (lower in 0 of 5 seeds), macro F1 -0.0022.

##### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13360.800 +/- 1915.084 | 0.034 +/- 0.016 | 0.023 +/- 0.012 | 0.089 +/- 0.040 |
| self_round1 | 13730.400 +/- 1840.486 | 0.043 +/- 0.020 | 0.031 +/- 0.015 | 0.107 +/- 0.045 |

#### 45f

##### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.818 +/- 0.111 | 0.736 +/- 0.064 | 0.208 +/- 0.222 | n/a | n/a | n/a |
| self_round1 | transductive | 0.819 +/- 0.110 | 0.712 +/- 0.074 | 0.207 +/- 0.221 | n/a | n/a | n/a |
| self_round2 | transductive | 0.820 +/- 0.108 | 0.737 +/- 0.064 | 0.205 +/- 0.216 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR -0.0030 (lower in 3 of 5 seeds), macro F1 +0.0009.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): passes.

##### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.719 +/- 0.043 | 0.704 +/- 0.024 | 0.324 +/- 0.075 | 0.271 +/- 0.078 | 0.936 +/- 0.005 | 0.116 +/- 0.023 |
| self_round1 | transductive | 0.718 +/- 0.046 | 0.703 +/- 0.026 | 0.332 +/- 0.080 | 0.275 +/- 0.084 | 0.947 +/- 0.010 | 0.123 +/- 0.025 |
| self_round2 | transductive | 0.721 +/- 0.047 | 0.706 +/- 0.027 | 0.331 +/- 0.082 | 0.274 +/- 0.082 | 0.953 +/- 0.009 | 0.124 +/- 0.025 |

Round 2 minus round 0: argmax FPR +0.0070 (lower in 0 of 5 seeds), macro F1 +0.0022.

##### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13599.200 +/- 1789.848 | 0.054 +/- 0.026 | 0.041 +/- 0.020 | 0.144 +/- 0.055 |
| self_round1 | 14234.200 +/- 1653.202 | 0.073 +/- 0.034 | 0.057 +/- 0.027 | 0.176 +/- 0.064 |

#### 48f

##### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.822 +/- 0.111 | 0.717 +/- 0.076 | 0.207 +/- 0.220 | n/a | n/a | n/a |
| self_round1 | transductive | 0.821 +/- 0.111 | 0.716 +/- 0.074 | 0.209 +/- 0.223 | n/a | n/a | n/a |
| self_round2 | transductive | 0.820 +/- 0.111 | 0.716 +/- 0.072 | 0.209 +/- 0.222 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR +0.0022 (lower in 1 of 5 seeds), macro F1 -0.0013.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): passes.

##### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.723 +/- 0.044 | 0.710 +/- 0.025 | 0.323 +/- 0.074 | 0.272 +/- 0.080 | 0.944 +/- 0.007 | 0.114 +/- 0.022 |
| self_round1 | transductive | 0.722 +/- 0.047 | 0.710 +/- 0.027 | 0.332 +/- 0.081 | 0.274 +/- 0.080 | 0.956 +/- 0.008 | 0.123 +/- 0.025 |
| self_round2 | transductive | 0.726 +/- 0.046 | 0.714 +/- 0.027 | 0.329 +/- 0.080 | 0.271 +/- 0.080 | 0.961 +/- 0.008 | 0.122 +/- 0.025 |

Round 2 minus round 0: argmax FPR +0.0054 (lower in 0 of 5 seeds), macro F1 +0.0039.

##### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13770.600 +/- 1753.373 | 0.054 +/- 0.026 | 0.041 +/- 0.020 | 0.140 +/- 0.055 |
| self_round1 | 14412.600 +/- 1622.903 | 0.073 +/- 0.034 | 0.058 +/- 0.028 | 0.172 +/- 0.063 |

## Source: fpr_study_fewshot_48f_45f_41f.md

### Task 2.7 Step 4 (FEW-SHOT): label budget and selection strategy, mean +/- std over 5 runs

Half of the k labelled rows retrain the model (weight fraction 0.5), the other half chooses the 95%-detection threshold. Candidates and evaluation rows come from different time blocks (200-row gaps); every method is scored on the same evaluation rows as the zero-shot baseline. Two FPRs are shown: `det95 FPR` at the threshold chosen on the held-out labelled half (its test detection is in the next column and is often below 95%, which flatters the FPR) and the threshold-free FPR at exactly 95% detection. Smallest k with mean FPR <= 0.15 is stated per strategy for both.

#### 48f

Zero-shot baseline on the same rows: det95 FPR 0.255 +/- 0.049, threshold-free FPR at 95% detection 0.251 +/- 0.055, detection 0.950 +/- 0.009, argmax FPR 0.304 +/- 0.049.

| strategy | k | det95 FPR | detection | FPR at exactly 95% detection | argmax FPR | accuracy | macro F1 | ECE | held-out half FPR | labelled attack share |
|---|---|---|---|---|---|---|---|---|---|---|
| random | 100 | 0.306 +/- 0.052 | 0.967 +/- 0.022 | 0.249 +/- 0.045 | 0.302 +/- 0.049 | 0.731 +/- 0.030 | 0.702 +/- 0.015 | 0.121 +/- 0.019 | 0.325 +/- 0.119 | 0.362 +/- 0.100 |
| entropy | 100 | 0.212 +/- 0.059 | 0.936 +/- 0.025 | 0.241 +/- 0.049 | 0.307 +/- 0.048 | 0.730 +/- 0.030 | 0.704 +/- 0.017 | 0.120 +/- 0.017 | 0.883 +/- 0.162 | 0.882 +/- 0.036 |
| diverse | 100 | 0.214 +/- 0.076 | 0.923 +/- 0.031 | 0.258 +/- 0.043 | 0.305 +/- 0.049 | 0.728 +/- 0.031 | 0.699 +/- 0.018 | 0.125 +/- 0.020 | 0.273 +/- 0.085 | 0.422 +/- 0.066 |
| mix | 100 | 0.224 +/- 0.042 | 0.942 +/- 0.007 | 0.244 +/- 0.052 | 0.305 +/- 0.049 | 0.730 +/- 0.031 | 0.704 +/- 0.017 | 0.123 +/- 0.021 | 0.307 +/- 0.100 | 0.638 +/- 0.044 |
| random | 250 | 0.209 +/- 0.056 | 0.944 +/- 0.026 | 0.214 +/- 0.047 | 0.298 +/- 0.049 | 0.735 +/- 0.030 | 0.703 +/- 0.020 | 0.123 +/- 0.021 | 0.191 +/- 0.087 | 0.402 +/- 0.083 |
| entropy | 250 | 0.160 +/- 0.026 | 0.926 +/- 0.017 | 0.214 +/- 0.053 | 0.307 +/- 0.048 | 0.731 +/- 0.029 | 0.703 +/- 0.015 | 0.121 +/- 0.019 | 0.378 +/- 0.132 | 0.846 +/- 0.056 |
| diverse | 250 | 0.160 +/- 0.097 | 0.908 +/- 0.042 | 0.247 +/- 0.032 | 0.301 +/- 0.048 | 0.731 +/- 0.029 | 0.703 +/- 0.017 | 0.126 +/- 0.020 | 0.181 +/- 0.123 | 0.422 +/- 0.067 |
| mix | 250 | 0.216 +/- 0.066 | 0.942 +/- 0.023 | 0.229 +/- 0.042 | 0.304 +/- 0.048 | 0.731 +/- 0.030 | 0.702 +/- 0.019 | 0.122 +/- 0.020 | 0.257 +/- 0.047 | 0.646 +/- 0.049 |
| random | 500 | 0.201 +/- 0.062 | 0.949 +/- 0.011 | 0.199 +/- 0.039 | 0.294 +/- 0.047 | 0.740 +/- 0.030 | 0.708 +/- 0.017 | 0.120 +/- 0.019 | 0.160 +/- 0.057 | 0.366 +/- 0.058 |
| entropy | 500 | 0.168 +/- 0.042 | 0.930 +/- 0.036 | 0.201 +/- 0.045 | 0.305 +/- 0.049 | 0.733 +/- 0.030 | 0.706 +/- 0.018 | 0.121 +/- 0.020 | 0.301 +/- 0.105 | 0.802 +/- 0.056 |
| diverse | 500 | 0.126 +/- 0.062 | 0.887 +/- 0.053 | 0.216 +/- 0.036 | 0.295 +/- 0.048 | 0.737 +/- 0.028 | 0.705 +/- 0.014 | 0.122 +/- 0.018 | 0.126 +/- 0.062 | 0.420 +/- 0.079 |
| mix | 500 | 0.160 +/- 0.044 | 0.934 +/- 0.020 | 0.193 +/- 0.049 | 0.303 +/- 0.048 | 0.735 +/- 0.030 | 0.706 +/- 0.016 | 0.122 +/- 0.016 | 0.192 +/- 0.047 | 0.628 +/- 0.053 |
| random | 1000 | 0.164 +/- 0.046 | 0.941 +/- 0.008 | 0.185 +/- 0.047 | 0.286 +/- 0.048 | 0.745 +/- 0.031 | 0.711 +/- 0.019 | 0.118 +/- 0.020 | 0.138 +/- 0.049 | 0.381 +/- 0.068 |
| entropy | 1000 | 0.144 +/- 0.060 | 0.924 +/- 0.035 | 0.191 +/- 0.036 | 0.295 +/- 0.048 | 0.739 +/- 0.030 | 0.709 +/- 0.019 | 0.121 +/- 0.020 | 0.159 +/- 0.069 | 0.709 +/- 0.089 |
| diverse | 1000 | 0.138 +/- 0.031 | 0.923 +/- 0.016 | 0.200 +/- 0.058 | 0.287 +/- 0.048 | 0.742 +/- 0.031 | 0.707 +/- 0.018 | 0.119 +/- 0.020 | 0.127 +/- 0.060 | 0.411 +/- 0.066 |
| mix | 1000 | 0.159 +/- 0.038 | 0.936 +/- 0.028 | 0.182 +/- 0.036 | 0.295 +/- 0.051 | 0.739 +/- 0.031 | 0.708 +/- 0.017 | 0.119 +/- 0.020 | 0.186 +/- 0.082 | 0.602 +/- 0.059 |
| random | 2500 | 0.126 +/- 0.020 | 0.938 +/- 0.018 | 0.152 +/- 0.036 | 0.268 +/- 0.045 | 0.757 +/- 0.027 | 0.718 +/- 0.013 | 0.107 +/- 0.016 | 0.103 +/- 0.040 | 0.375 +/- 0.069 |
| entropy | 2500 | 0.164 +/- 0.039 | 0.947 +/- 0.020 | 0.167 +/- 0.042 | 0.272 +/- 0.044 | 0.753 +/- 0.027 | 0.717 +/- 0.017 | 0.112 +/- 0.018 | 0.135 +/- 0.027 | 0.578 +/- 0.064 |
| diverse | 2500 | 0.099 +/- 0.014 | 0.926 +/- 0.010 | 0.148 +/- 0.035 | 0.270 +/- 0.046 | 0.756 +/- 0.029 | 0.718 +/- 0.019 | 0.109 +/- 0.017 | 0.070 +/- 0.024 | 0.394 +/- 0.065 |
| mix | 2500 | 0.127 +/- 0.032 | 0.938 +/- 0.021 | 0.152 +/- 0.046 | 0.272 +/- 0.048 | 0.754 +/- 0.030 | 0.717 +/- 0.018 | 0.107 +/- 0.020 | 0.120 +/- 0.050 | 0.532 +/- 0.074 |
| random | 5000 | 0.089 +/- 0.003 | 0.935 +/- 0.015 | 0.122 +/- 0.032 | 0.248 +/- 0.052 | 0.769 +/- 0.033 | 0.723 +/- 0.020 | 0.095 +/- 0.022 | 0.052 +/- 0.017 | 0.373 +/- 0.060 |
| entropy | 5000 | 0.154 +/- 0.031 | 0.964 +/- 0.013 | 0.113 +/- 0.026 | 0.212 +/- 0.046 | 0.790 +/- 0.030 | 0.734 +/- 0.019 | 0.082 +/- 0.021 | 0.118 +/- 0.056 | 0.470 +/- 0.063 |
| diverse | 5000 | 0.091 +/- 0.016 | 0.933 +/- 0.016 | 0.130 +/- 0.035 | 0.248 +/- 0.050 | 0.769 +/- 0.031 | 0.722 +/- 0.019 | 0.096 +/- 0.020 | 0.056 +/- 0.022 | 0.383 +/- 0.065 |
| mix | 5000 | 0.120 +/- 0.014 | 0.945 +/- 0.015 | 0.132 +/- 0.035 | 0.248 +/- 0.047 | 0.769 +/- 0.029 | 0.724 +/- 0.018 | 0.096 +/- 0.019 | 0.088 +/- 0.029 | 0.470 +/- 0.058 |

| strategy | smallest k with mean det95 FPR <= 0.15 | smallest k with mean FPR at exactly 95% detection <= 0.15 |
|---|---|---|
| random | 2500 | 5000 |
| entropy | 1000 | 5000 |
| diverse | 500 | 2500 |
| mix | 2500 | 5000 |

#### 45f

Zero-shot baseline on the same rows: det95 FPR 0.255 +/- 0.047, threshold-free FPR at 95% detection 0.269 +/- 0.053, detection 0.942 +/- 0.009, argmax FPR 0.304 +/- 0.048.

| strategy | k | det95 FPR | detection | FPR at exactly 95% detection | argmax FPR | accuracy | macro F1 | ECE | held-out half FPR | labelled attack share |
|---|---|---|---|---|---|---|---|---|---|---|
| random | 100 | 0.305 +/- 0.070 | 0.962 +/- 0.026 | 0.267 +/- 0.052 | 0.303 +/- 0.049 | 0.726 +/- 0.031 | 0.695 +/- 0.015 | 0.122 +/- 0.020 | 0.307 +/- 0.131 | 0.362 +/- 0.100 |
| entropy | 100 | 0.208 +/- 0.059 | 0.926 +/- 0.026 | 0.261 +/- 0.053 | 0.308 +/- 0.047 | 0.726 +/- 0.030 | 0.698 +/- 0.017 | 0.122 +/- 0.018 | 0.545 +/- 0.161 | 0.836 +/- 0.051 |
| diverse | 100 | 0.166 +/- 0.133 | 0.864 +/- 0.145 | 0.271 +/- 0.047 | 0.303 +/- 0.049 | 0.726 +/- 0.031 | 0.696 +/- 0.016 | 0.125 +/- 0.019 | 0.215 +/- 0.160 | 0.396 +/- 0.074 |
| mix | 100 | 0.221 +/- 0.047 | 0.931 +/- 0.028 | 0.253 +/- 0.041 | 0.305 +/- 0.050 | 0.727 +/- 0.031 | 0.698 +/- 0.017 | 0.123 +/- 0.020 | 0.369 +/- 0.110 | 0.622 +/- 0.075 |
| random | 250 | 0.254 +/- 0.036 | 0.958 +/- 0.022 | 0.228 +/- 0.044 | 0.298 +/- 0.048 | 0.732 +/- 0.030 | 0.697 +/- 0.021 | 0.123 +/- 0.020 | 0.263 +/- 0.112 | 0.402 +/- 0.083 |
| entropy | 250 | 0.209 +/- 0.056 | 0.939 +/- 0.013 | 0.240 +/- 0.058 | 0.309 +/- 0.048 | 0.727 +/- 0.032 | 0.698 +/- 0.019 | 0.121 +/- 0.019 | 0.488 +/- 0.130 | 0.826 +/- 0.059 |
| diverse | 250 | 0.176 +/- 0.143 | 0.889 +/- 0.081 | 0.262 +/- 0.060 | 0.299 +/- 0.048 | 0.728 +/- 0.031 | 0.693 +/- 0.020 | 0.125 +/- 0.019 | 0.188 +/- 0.122 | 0.410 +/- 0.072 |
| mix | 250 | 0.202 +/- 0.048 | 0.931 +/- 0.015 | 0.243 +/- 0.061 | 0.305 +/- 0.050 | 0.728 +/- 0.033 | 0.697 +/- 0.021 | 0.123 +/- 0.021 | 0.257 +/- 0.048 | 0.620 +/- 0.038 |
| random | 500 | 0.226 +/- 0.046 | 0.955 +/- 0.012 | 0.215 +/- 0.038 | 0.294 +/- 0.048 | 0.737 +/- 0.031 | 0.702 +/- 0.018 | 0.121 +/- 0.020 | 0.182 +/- 0.096 | 0.366 +/- 0.058 |
| entropy | 500 | 0.157 +/- 0.057 | 0.915 +/- 0.031 | 0.225 +/- 0.047 | 0.306 +/- 0.049 | 0.729 +/- 0.030 | 0.698 +/- 0.017 | 0.124 +/- 0.019 | 0.262 +/- 0.076 | 0.787 +/- 0.059 |
| diverse | 500 | 0.169 +/- 0.073 | 0.900 +/- 0.052 | 0.251 +/- 0.052 | 0.293 +/- 0.045 | 0.732 +/- 0.029 | 0.696 +/- 0.018 | 0.123 +/- 0.018 | 0.168 +/- 0.048 | 0.406 +/- 0.077 |
| mix | 500 | 0.169 +/- 0.049 | 0.926 +/- 0.021 | 0.222 +/- 0.046 | 0.302 +/- 0.050 | 0.732 +/- 0.031 | 0.701 +/- 0.018 | 0.123 +/- 0.019 | 0.238 +/- 0.075 | 0.610 +/- 0.049 |
| random | 1000 | 0.182 +/- 0.043 | 0.942 +/- 0.010 | 0.198 +/- 0.046 | 0.286 +/- 0.048 | 0.742 +/- 0.031 | 0.705 +/- 0.019 | 0.119 +/- 0.020 | 0.150 +/- 0.040 | 0.381 +/- 0.068 |
| entropy | 1000 | 0.188 +/- 0.076 | 0.932 +/- 0.041 | 0.213 +/- 0.045 | 0.296 +/- 0.047 | 0.735 +/- 0.030 | 0.701 +/- 0.020 | 0.120 +/- 0.020 | 0.224 +/- 0.125 | 0.695 +/- 0.095 |
| diverse | 1000 | 0.126 +/- 0.050 | 0.907 +/- 0.030 | 0.198 +/- 0.047 | 0.287 +/- 0.049 | 0.741 +/- 0.030 | 0.706 +/- 0.017 | 0.118 +/- 0.019 | 0.115 +/- 0.040 | 0.405 +/- 0.067 |
| mix | 1000 | 0.189 +/- 0.050 | 0.943 +/- 0.020 | 0.203 +/- 0.045 | 0.296 +/- 0.049 | 0.735 +/- 0.031 | 0.699 +/- 0.021 | 0.120 +/- 0.019 | 0.208 +/- 0.080 | 0.581 +/- 0.058 |
| random | 2500 | 0.132 +/- 0.030 | 0.935 +/- 0.025 | 0.164 +/- 0.042 | 0.268 +/- 0.045 | 0.754 +/- 0.028 | 0.713 +/- 0.014 | 0.107 +/- 0.016 | 0.107 +/- 0.040 | 0.375 +/- 0.069 |
| entropy | 2500 | 0.172 +/- 0.037 | 0.945 +/- 0.027 | 0.181 +/- 0.049 | 0.277 +/- 0.046 | 0.747 +/- 0.029 | 0.711 +/- 0.017 | 0.116 +/- 0.018 | 0.134 +/- 0.050 | 0.579 +/- 0.065 |
| diverse | 2500 | 0.104 +/- 0.017 | 0.924 +/- 0.014 | 0.160 +/- 0.037 | 0.270 +/- 0.045 | 0.753 +/- 0.028 | 0.712 +/- 0.020 | 0.111 +/- 0.017 | 0.075 +/- 0.029 | 0.391 +/- 0.067 |
| mix | 2500 | 0.143 +/- 0.033 | 0.939 +/- 0.021 | 0.167 +/- 0.041 | 0.277 +/- 0.045 | 0.747 +/- 0.028 | 0.708 +/- 0.018 | 0.112 +/- 0.018 | 0.128 +/- 0.050 | 0.520 +/- 0.075 |
| random | 5000 | 0.100 +/- 0.005 | 0.934 +/- 0.015 | 0.138 +/- 0.038 | 0.249 +/- 0.052 | 0.765 +/- 0.033 | 0.717 +/- 0.019 | 0.095 +/- 0.022 | 0.060 +/- 0.018 | 0.373 +/- 0.060 |
| entropy | 5000 | 0.159 +/- 0.026 | 0.963 +/- 0.013 | 0.127 +/- 0.034 | 0.218 +/- 0.048 | 0.784 +/- 0.030 | 0.727 +/- 0.019 | 0.086 +/- 0.022 | 0.126 +/- 0.051 | 0.479 +/- 0.065 |
| diverse | 5000 | 0.104 +/- 0.009 | 0.935 +/- 0.011 | 0.141 +/- 0.037 | 0.246 +/- 0.048 | 0.767 +/- 0.031 | 0.717 +/- 0.020 | 0.096 +/- 0.021 | 0.066 +/- 0.015 | 0.382 +/- 0.066 |
| mix | 5000 | 0.112 +/- 0.016 | 0.938 +/- 0.019 | 0.139 +/- 0.034 | 0.249 +/- 0.048 | 0.765 +/- 0.030 | 0.717 +/- 0.017 | 0.097 +/- 0.021 | 0.086 +/- 0.026 | 0.470 +/- 0.057 |

| strategy | smallest k with mean det95 FPR <= 0.15 | smallest k with mean FPR at exactly 95% detection <= 0.15 |
|---|---|---|
| random | 2500 | 5000 |
| entropy | none reached | 5000 |
| diverse | 1000 | 5000 |
| mix | 2500 | 5000 |

#### 41f

Zero-shot baseline on the same rows: det95 FPR 0.260 +/- 0.042, threshold-free FPR at 95% detection 0.249 +/- 0.039, detection 0.952 +/- 0.011, argmax FPR 0.302 +/- 0.044.

| strategy | k | det95 FPR | detection | FPR at exactly 95% detection | argmax FPR | accuracy | macro F1 | ECE | held-out half FPR | labelled attack share |
|---|---|---|---|---|---|---|---|---|---|---|
| random | 100 | 0.321 +/- 0.120 | 0.961 +/- 0.045 | 0.256 +/- 0.036 | 0.307 +/- 0.046 | 0.726 +/- 0.028 | 0.700 +/- 0.013 | 0.102 +/- 0.016 | 0.275 +/- 0.155 | 0.362 +/- 0.100 |
| entropy | 100 | 0.262 +/- 0.082 | 0.949 +/- 0.039 | 0.255 +/- 0.039 | 0.307 +/- 0.044 | 0.726 +/- 0.027 | 0.700 +/- 0.015 | 0.102 +/- 0.015 | 0.691 +/- 0.141 | 0.806 +/- 0.044 |
| diverse | 100 | 0.193 +/- 0.087 | 0.913 +/- 0.068 | 0.255 +/- 0.038 | 0.306 +/- 0.046 | 0.727 +/- 0.027 | 0.700 +/- 0.014 | 0.102 +/- 0.015 | 0.229 +/- 0.152 | 0.426 +/- 0.086 |
| mix | 100 | 0.234 +/- 0.081 | 0.940 +/- 0.022 | 0.254 +/- 0.036 | 0.308 +/- 0.044 | 0.725 +/- 0.027 | 0.699 +/- 0.016 | 0.102 +/- 0.015 | 0.370 +/- 0.167 | 0.636 +/- 0.033 |
| random | 250 | 0.265 +/- 0.034 | 0.954 +/- 0.019 | 0.249 +/- 0.039 | 0.298 +/- 0.047 | 0.731 +/- 0.029 | 0.701 +/- 0.017 | 0.099 +/- 0.017 | 0.255 +/- 0.120 | 0.402 +/- 0.083 |
| entropy | 250 | 0.275 +/- 0.070 | 0.956 +/- 0.034 | 0.256 +/- 0.037 | 0.312 +/- 0.046 | 0.722 +/- 0.027 | 0.696 +/- 0.015 | 0.102 +/- 0.016 | 0.654 +/- 0.148 | 0.798 +/- 0.072 |
| diverse | 250 | 0.188 +/- 0.051 | 0.922 +/- 0.027 | 0.254 +/- 0.038 | 0.300 +/- 0.041 | 0.729 +/- 0.026 | 0.700 +/- 0.015 | 0.103 +/- 0.014 | 0.216 +/- 0.086 | 0.414 +/- 0.069 |
| mix | 250 | 0.255 +/- 0.036 | 0.949 +/- 0.025 | 0.261 +/- 0.037 | 0.308 +/- 0.046 | 0.724 +/- 0.028 | 0.698 +/- 0.016 | 0.104 +/- 0.017 | 0.380 +/- 0.139 | 0.635 +/- 0.062 |
| random | 500 | 0.257 +/- 0.126 | 0.939 +/- 0.045 | 0.255 +/- 0.035 | 0.291 +/- 0.049 | 0.734 +/- 0.030 | 0.701 +/- 0.018 | 0.099 +/- 0.016 | 0.224 +/- 0.095 | 0.366 +/- 0.058 |
| entropy | 500 | 0.242 +/- 0.064 | 0.938 +/- 0.031 | 0.258 +/- 0.036 | 0.312 +/- 0.045 | 0.720 +/- 0.026 | 0.691 +/- 0.016 | 0.105 +/- 0.016 | 0.612 +/- 0.108 | 0.808 +/- 0.076 |
| diverse | 500 | 0.267 +/- 0.081 | 0.947 +/- 0.034 | 0.253 +/- 0.038 | 0.294 +/- 0.046 | 0.732 +/- 0.028 | 0.702 +/- 0.016 | 0.100 +/- 0.017 | 0.233 +/- 0.021 | 0.410 +/- 0.071 |
| mix | 500 | 0.228 +/- 0.074 | 0.932 +/- 0.032 | 0.258 +/- 0.032 | 0.304 +/- 0.046 | 0.726 +/- 0.027 | 0.697 +/- 0.016 | 0.101 +/- 0.016 | 0.267 +/- 0.065 | 0.609 +/- 0.062 |
| random | 1000 | 0.264 +/- 0.080 | 0.950 +/- 0.022 | 0.254 +/- 0.034 | 0.275 +/- 0.048 | 0.741 +/- 0.028 | 0.704 +/- 0.013 | 0.093 +/- 0.016 | 0.248 +/- 0.056 | 0.381 +/- 0.068 |
| entropy | 1000 | 0.243 +/- 0.059 | 0.942 +/- 0.029 | 0.254 +/- 0.033 | 0.306 +/- 0.045 | 0.723 +/- 0.028 | 0.692 +/- 0.018 | 0.103 +/- 0.018 | 0.470 +/- 0.079 | 0.756 +/- 0.095 |
| diverse | 1000 | 0.268 +/- 0.054 | 0.953 +/- 0.020 | 0.252 +/- 0.043 | 0.276 +/- 0.045 | 0.741 +/- 0.028 | 0.704 +/- 0.015 | 0.093 +/- 0.018 | 0.261 +/- 0.071 | 0.394 +/- 0.068 |
| mix | 1000 | 0.251 +/- 0.080 | 0.941 +/- 0.032 | 0.256 +/- 0.035 | 0.296 +/- 0.049 | 0.729 +/- 0.028 | 0.695 +/- 0.016 | 0.100 +/- 0.017 | 0.289 +/- 0.093 | 0.601 +/- 0.059 |
| random | 2500 | 0.246 +/- 0.060 | 0.943 +/- 0.018 | 0.260 +/- 0.036 | 0.251 +/- 0.045 | 0.753 +/- 0.027 | 0.709 +/- 0.013 | 0.081 +/- 0.015 | 0.225 +/- 0.058 | 0.375 +/- 0.069 |
| entropy | 2500 | 0.332 +/- 0.047 | 0.981 +/- 0.005 | 0.246 +/- 0.035 | 0.272 +/- 0.045 | 0.742 +/- 0.028 | 0.705 +/- 0.015 | 0.096 +/- 0.017 | 0.397 +/- 0.078 | 0.535 +/- 0.078 |
| diverse | 2500 | 0.268 +/- 0.059 | 0.954 +/- 0.020 | 0.250 +/- 0.038 | 0.260 +/- 0.045 | 0.750 +/- 0.026 | 0.709 +/- 0.013 | 0.087 +/- 0.014 | 0.231 +/- 0.048 | 0.356 +/- 0.065 |
| mix | 2500 | 0.256 +/- 0.074 | 0.949 +/- 0.026 | 0.249 +/- 0.030 | 0.264 +/- 0.046 | 0.747 +/- 0.028 | 0.704 +/- 0.016 | 0.087 +/- 0.015 | 0.272 +/- 0.062 | 0.523 +/- 0.063 |
| random | 5000 | 0.228 +/- 0.066 | 0.940 +/- 0.024 | 0.242 +/- 0.037 | 0.227 +/- 0.054 | 0.766 +/- 0.032 | 0.714 +/- 0.017 | 0.069 +/- 0.020 | 0.178 +/- 0.037 | 0.373 +/- 0.060 |
| entropy | 5000 | 0.310 +/- 0.036 | 0.976 +/- 0.008 | 0.238 +/- 0.035 | 0.208 +/- 0.044 | 0.775 +/- 0.027 | 0.719 +/- 0.016 | 0.071 +/- 0.020 | 0.523 +/- 0.100 | 0.447 +/- 0.061 |
| diverse | 5000 | 0.260 +/- 0.056 | 0.953 +/- 0.017 | 0.245 +/- 0.039 | 0.233 +/- 0.048 | 0.764 +/- 0.029 | 0.714 +/- 0.014 | 0.074 +/- 0.016 | 0.219 +/- 0.051 | 0.371 +/- 0.062 |
| mix | 5000 | 0.273 +/- 0.048 | 0.961 +/- 0.014 | 0.243 +/- 0.036 | 0.234 +/- 0.050 | 0.763 +/- 0.029 | 0.715 +/- 0.015 | 0.074 +/- 0.018 | 0.268 +/- 0.066 | 0.434 +/- 0.059 |

| strategy | smallest k with mean det95 FPR <= 0.15 | smallest k with mean FPR at exactly 95% detection <= 0.15 |
|---|---|---|
| random | none reached | none reached |
| entropy | none reached | none reached |
| diverse | none reached | none reached |
| mix | none reached | none reached |

## Source: fpr_study_final_40f_45f_48f.md

### Task 2.7 Step 5: final table (official split, mean +/- std over seeds 42-46)

#### 40f

##### A. Whole official test file (zero-shot and transductive methods)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default (config.yaml) | zero-shot | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.256 +/- 0.010 | 0.255 +/- 0.007 | 0.950 +/- 0.003 | 0.093 +/- 0.008 | 0.237 +/- 0.053 |
| earlier tuned, random validation (auc) | zero-shot | 0.761 +/- 0.005 | 0.718 +/- 0.002 | 0.245 +/- 0.011 | 0.252 +/- 0.014 | 0.253 +/- 0.009 | 0.950 +/- 0.005 | 0.058 +/- 0.006 | 0.213 +/- 0.038 |
| tuned on block-grouped validation (auc) | zero-shot | 0.762 +/- 0.005 | 0.714 +/- 0.002 | 0.239 +/- 0.010 | 0.257 +/- 0.014 | 0.261 +/- 0.008 | 0.948 +/- 0.006 | 0.051 +/- 0.006 | 0.239 +/- 0.058 |
| tuned on block-grouped validation (macro F1) | zero-shot | 0.753 +/- 0.006 | 0.713 +/- 0.002 | 0.258 +/- 0.011 | 0.253 +/- 0.014 | 0.262 +/- 0.009 | 0.947 +/- 0.006 | 0.058 +/- 0.007 | 0.273 +/- 0.061 |
| temperature scaling | zero-shot | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.259 +/- 0.010 | 0.256 +/- 0.007 | 0.951 +/- 0.003 | 0.070 +/- 0.006 | 0.237 +/- 0.052 |
| temperature scaling + validation class prior (control) | zero-shot | 0.766 +/- 0.060 | 0.718 +/- 0.022 | 0.230 +/- 0.123 | 0.256 +/- 0.011 | 0.253 +/- 0.007 | 0.951 +/- 0.003 | 0.060 +/- 0.060 | 0.241 +/- 0.118 |
| temperature scaling + EM prior correction | transductive | 0.775 +/- 0.023 | 0.680 +/- 0.030 | 0.196 +/- 0.038 | 0.249 +/- 0.008 | 0.245 +/- 0.008 | 0.952 +/- 0.004 | 0.044 +/- 0.015 | 0.037 +/- 0.028 |
| declared combination (tuned if validation AUC >= default, temperature, EM if its gate passes) | zero-shot / transductive | 0.764 +/- 0.025 | 0.698 +/- 0.024 | 0.226 +/- 0.055 | 0.254 +/- 0.015 | 0.253 +/- 0.013 | 0.951 +/- 0.005 | 0.050 +/- 0.019 | 0.106 +/- 0.085 |

##### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.726 +/- 0.042 | 0.709 +/- 0.025 | 0.314 +/- 0.071 | 0.283 +/- 0.082 | 0.296 +/- 0.083 | 0.944 +/- 0.007 | 0.090 +/- 0.017 | 0.237 +/- 0.053 |
| self-training, round 2 | transductive | 0.722 +/- 0.045 | 0.706 +/- 0.025 | 0.324 +/- 0.079 | 0.282 +/- 0.085 | 0.296 +/- 0.086 | 0.944 +/- 0.007 | 0.101 +/- 0.020 | 0.231 +/- 0.041 |

#### 45f

##### A. Whole official test file (zero-shot and transductive methods)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default (config.yaml) | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.248 +/- 0.012 | 0.264 +/- 0.016 | 0.943 +/- 0.002 | 0.116 +/- 0.009 | 0.353 +/- 0.045 |
| tuned on block-grouped validation (auc) | zero-shot | 0.726 +/- 0.007 | 0.700 +/- 0.003 | 0.310 +/- 0.013 | 0.258 +/- 0.012 | 0.265 +/- 0.016 | 0.947 +/- 0.002 | 0.093 +/- 0.010 | 0.529 +/- 0.050 |
| tuned on block-grouped validation (macro F1) | zero-shot | 0.747 +/- 0.006 | 0.708 +/- 0.002 | 0.269 +/- 0.014 | 0.255 +/- 0.012 | 0.258 +/- 0.009 | 0.948 +/- 0.003 | 0.072 +/- 0.008 | 0.493 +/- 0.040 |
| temperature scaling | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.251 +/- 0.013 | 0.261 +/- 0.018 | 0.946 +/- 0.002 | 0.086 +/- 0.003 | 0.366 +/- 0.050 |
| temperature scaling + validation class prior (control) | zero-shot | 0.753 +/- 0.052 | 0.706 +/- 0.019 | 0.249 +/- 0.108 | 0.249 +/- 0.012 | 0.259 +/- 0.017 | 0.945 +/- 0.003 | 0.074 +/- 0.057 | 0.309 +/- 0.114 |
| temperature scaling + EM prior correction | transductive | 0.759 +/- 0.017 | 0.682 +/- 0.033 | 0.228 +/- 0.030 | 0.244 +/- 0.010 | 0.259 +/- 0.014 | 0.943 +/- 0.003 | 0.065 +/- 0.011 | 0.120 +/- 0.084 |
| declared combination (tuned if validation AUC >= default, temperature, EM if its gate passes) | zero-shot / transductive | 0.751 +/- 0.023 | 0.698 +/- 0.025 | 0.254 +/- 0.052 | 0.249 +/- 0.013 | 0.262 +/- 0.015 | 0.944 +/- 0.003 | 0.072 +/- 0.015 | 0.243 +/- 0.123 |

##### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.719 +/- 0.043 | 0.704 +/- 0.024 | 0.324 +/- 0.075 | 0.271 +/- 0.078 | 0.304 +/- 0.092 | 0.936 +/- 0.005 | 0.116 +/- 0.023 | 0.353 +/- 0.045 |
| self-training, round 2 | transductive | 0.721 +/- 0.047 | 0.706 +/- 0.027 | 0.331 +/- 0.082 | 0.274 +/- 0.082 | 0.266 +/- 0.093 | 0.953 +/- 0.009 | 0.124 +/- 0.025 | 0.371 +/- 0.044 |
| zero-shot baseline (few-shot evaluation rows) | zero-shot | 0.726 +/- 0.031 | 0.697 +/- 0.017 | 0.304 +/- 0.048 | 0.255 +/- 0.047 | 0.269 +/- 0.053 | 0.942 +/- 0.009 | 0.121 +/- 0.019 | 0.353 +/- 0.045 |
| few-shot, diverse selection, k = 1000 | few-shot | 0.741 +/- 0.030 | 0.706 +/- 0.017 | 0.287 +/- 0.049 | 0.126 +/- 0.050 | 0.198 +/- 0.047 | 0.907 +/- 0.030 | 0.118 +/- 0.019 | 0.374 +/- 0.065 |
| few-shot, diverse selection, k = 5000 | few-shot | 0.767 +/- 0.031 | 0.717 +/- 0.020 | 0.246 +/- 0.048 | 0.104 +/- 0.009 | 0.141 +/- 0.037 | 0.935 +/- 0.011 | 0.096 +/- 0.021 | 0.364 +/- 0.046 |

Few-shot strategy chosen by the declared rule (lowest held-out-half FPR at k = 1,000): **diverse**.

#### 48f

##### A. Whole official test file (zero-shot and transductive methods)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default (config.yaml) | zero-shot | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.248 +/- 0.011 | 0.246 +/- 0.022 | 0.950 +/- 0.005 | 0.115 +/- 0.010 | 0.344 +/- 0.045 |
| earlier tuned, random validation (auc) | zero-shot | 0.755 +/- 0.007 | 0.718 +/- 0.003 | 0.265 +/- 0.013 | 0.249 +/- 0.011 | 0.230 +/- 0.015 | 0.957 +/- 0.004 | 0.085 +/- 0.008 | 0.399 +/- 0.052 |
| tuned on block-grouped validation (auc) | zero-shot | 0.733 +/- 0.006 | 0.709 +/- 0.003 | 0.307 +/- 0.013 | 0.254 +/- 0.014 | 0.230 +/- 0.011 | 0.961 +/- 0.003 | 0.091 +/- 0.010 | 0.546 +/- 0.047 |
| tuned on block-grouped validation (macro F1) | zero-shot | 0.753 +/- 0.007 | 0.716 +/- 0.004 | 0.267 +/- 0.012 | 0.253 +/- 0.011 | 0.227 +/- 0.011 | 0.961 +/- 0.001 | 0.074 +/- 0.008 | 0.496 +/- 0.038 |
| temperature scaling | zero-shot | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.249 +/- 0.012 | 0.242 +/- 0.023 | 0.952 +/- 0.005 | 0.086 +/- 0.002 | 0.357 +/- 0.047 |
| temperature scaling + validation class prior (control) | zero-shot | 0.757 +/- 0.053 | 0.712 +/- 0.020 | 0.249 +/- 0.108 | 0.248 +/- 0.012 | 0.241 +/- 0.024 | 0.952 +/- 0.006 | 0.074 +/- 0.060 | 0.290 +/- 0.131 |
| temperature scaling + EM prior correction | transductive | 0.762 +/- 0.018 | 0.691 +/- 0.030 | 0.230 +/- 0.032 | 0.244 +/- 0.010 | 0.241 +/- 0.020 | 0.951 +/- 0.005 | 0.065 +/- 0.012 | 0.113 +/- 0.082 |
| declared combination (tuned if validation AUC >= default, temperature, EM if its gate passes) | zero-shot / transductive | 0.755 +/- 0.024 | 0.706 +/- 0.022 | 0.254 +/- 0.053 | 0.247 +/- 0.013 | 0.240 +/- 0.020 | 0.953 +/- 0.006 | 0.071 +/- 0.016 | 0.216 +/- 0.123 |

##### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.723 +/- 0.044 | 0.710 +/- 0.025 | 0.323 +/- 0.074 | 0.272 +/- 0.080 | 0.285 +/- 0.091 | 0.944 +/- 0.007 | 0.114 +/- 0.022 | 0.344 +/- 0.045 |
| self-training, round 2 | transductive | 0.726 +/- 0.046 | 0.714 +/- 0.027 | 0.329 +/- 0.080 | 0.271 +/- 0.080 | 0.242 +/- 0.091 | 0.961 +/- 0.008 | 0.122 +/- 0.025 | 0.354 +/- 0.054 |
| zero-shot baseline (few-shot evaluation rows) | zero-shot | 0.729 +/- 0.031 | 0.702 +/- 0.017 | 0.304 +/- 0.049 | 0.255 +/- 0.049 | 0.251 +/- 0.055 | 0.950 +/- 0.009 | 0.121 +/- 0.019 | 0.344 +/- 0.045 |
| few-shot, diverse selection, k = 1000 | few-shot | 0.742 +/- 0.031 | 0.707 +/- 0.018 | 0.287 +/- 0.048 | 0.138 +/- 0.031 | 0.200 +/- 0.058 | 0.923 +/- 0.016 | 0.119 +/- 0.020 | 0.355 +/- 0.060 |
| few-shot, diverse selection, k = 5000 | few-shot | 0.769 +/- 0.031 | 0.722 +/- 0.019 | 0.248 +/- 0.050 | 0.091 +/- 0.016 | 0.130 +/- 0.035 | 0.933 +/- 0.016 | 0.096 +/- 0.020 | 0.355 +/- 0.054 |

Few-shot strategy chosen by the declared rule (lowest held-out-half FPR at k = 1,000): **diverse**.

