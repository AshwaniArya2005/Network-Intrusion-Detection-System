# Task 2.7 Step 1 (ZERO-SHOT): re-tuning on block-grouped validation, official test, mean +/- std over seeds 42-46

Primary metric `det95_test_fpr` (threshold at 95% detection chosen on block-grouped validation). `earlier_tuned_*` = the Task 2a search on random validation (40 and 48 features only); `blockval_tuned_*` = the 40-trial search on block-grouped validation with the regularised space. Verdict = the declared rule against `default` on the same seeds.

## 40f

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

## 45f

| method | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|
| default | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.248 +/- 0.012 | 0.264 +/- 0.016 | 0.943 +/- 0.002 | 0.116 +/- 0.009 | 0.353 +/- 0.045 |
| blockval_tuned_auc | 0.726 +/- 0.007 | 0.700 +/- 0.003 | 0.310 +/- 0.013 | 0.258 +/- 0.012 | 0.265 +/- 0.016 | 0.947 +/- 0.002 | 0.093 +/- 0.010 | 0.529 +/- 0.050 |
| blockval_tuned_f1 | 0.747 +/- 0.006 | 0.708 +/- 0.002 | 0.269 +/- 0.014 | 0.255 +/- 0.012 | 0.258 +/- 0.009 | 0.948 +/- 0.003 | 0.072 +/- 0.008 | 0.493 +/- 0.040 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| blockval_tuned_auc | +0.0096 | 0 of 5 | +0.0041 | no |
| blockval_tuned_f1 | +0.0064 | 1 of 5 | +0.0058 | no |

## 48f

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

