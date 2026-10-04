# Task 2.7 Step 5: final table (official split, mean +/- std over seeds 42-46)

## 40f

### A. Whole official test file (zero-shot and transductive methods)

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

### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.726 +/- 0.042 | 0.709 +/- 0.025 | 0.314 +/- 0.071 | 0.283 +/- 0.082 | 0.296 +/- 0.083 | 0.944 +/- 0.007 | 0.090 +/- 0.017 | 0.237 +/- 0.053 |
| self-training, round 2 | transductive | 0.722 +/- 0.045 | 0.706 +/- 0.025 | 0.324 +/- 0.079 | 0.282 +/- 0.085 | 0.296 +/- 0.086 | 0.944 +/- 0.007 | 0.101 +/- 0.020 | 0.231 +/- 0.041 |

## 45f

### A. Whole official test file (zero-shot and transductive methods)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default (config.yaml) | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.248 +/- 0.012 | 0.264 +/- 0.016 | 0.943 +/- 0.002 | 0.116 +/- 0.009 | 0.353 +/- 0.045 |
| tuned on block-grouped validation (auc) | zero-shot | 0.726 +/- 0.007 | 0.700 +/- 0.003 | 0.310 +/- 0.013 | 0.258 +/- 0.012 | 0.265 +/- 0.016 | 0.947 +/- 0.002 | 0.093 +/- 0.010 | 0.529 +/- 0.050 |
| tuned on block-grouped validation (macro F1) | zero-shot | 0.747 +/- 0.006 | 0.708 +/- 0.002 | 0.269 +/- 0.014 | 0.255 +/- 0.012 | 0.258 +/- 0.009 | 0.948 +/- 0.003 | 0.072 +/- 0.008 | 0.493 +/- 0.040 |
| temperature scaling | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.251 +/- 0.013 | 0.261 +/- 0.018 | 0.946 +/- 0.002 | 0.086 +/- 0.003 | 0.366 +/- 0.050 |
| temperature scaling + validation class prior (control) | zero-shot | 0.753 +/- 0.052 | 0.706 +/- 0.019 | 0.249 +/- 0.108 | 0.249 +/- 0.012 | 0.259 +/- 0.017 | 0.945 +/- 0.003 | 0.074 +/- 0.057 | 0.309 +/- 0.114 |
| temperature scaling + EM prior correction | transductive | 0.759 +/- 0.017 | 0.682 +/- 0.033 | 0.228 +/- 0.030 | 0.244 +/- 0.010 | 0.259 +/- 0.014 | 0.943 +/- 0.003 | 0.065 +/- 0.011 | 0.120 +/- 0.084 |
| declared combination (tuned if validation AUC >= default, temperature, EM if its gate passes) | zero-shot / transductive | 0.751 +/- 0.023 | 0.698 +/- 0.025 | 0.254 +/- 0.052 | 0.249 +/- 0.013 | 0.262 +/- 0.015 | 0.944 +/- 0.003 | 0.072 +/- 0.015 | 0.243 +/- 0.123 |

### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.719 +/- 0.043 | 0.704 +/- 0.024 | 0.324 +/- 0.075 | 0.271 +/- 0.078 | 0.304 +/- 0.092 | 0.936 +/- 0.005 | 0.116 +/- 0.023 | 0.353 +/- 0.045 |
| self-training, round 2 | transductive | 0.721 +/- 0.047 | 0.706 +/- 0.027 | 0.331 +/- 0.082 | 0.274 +/- 0.082 | 0.266 +/- 0.093 | 0.953 +/- 0.009 | 0.124 +/- 0.025 | 0.371 +/- 0.044 |
| zero-shot baseline (few-shot evaluation rows) | zero-shot | 0.726 +/- 0.031 | 0.697 +/- 0.017 | 0.304 +/- 0.048 | 0.255 +/- 0.047 | 0.269 +/- 0.053 | 0.942 +/- 0.009 | 0.121 +/- 0.019 | 0.353 +/- 0.045 |
| few-shot, diverse selection, k = 1000 | few-shot | 0.741 +/- 0.030 | 0.706 +/- 0.017 | 0.287 +/- 0.049 | 0.126 +/- 0.050 | 0.198 +/- 0.047 | 0.907 +/- 0.030 | 0.118 +/- 0.019 | 0.374 +/- 0.065 |
| few-shot, diverse selection, k = 5000 | few-shot | 0.767 +/- 0.031 | 0.717 +/- 0.020 | 0.246 +/- 0.048 | 0.104 +/- 0.009 | 0.141 +/- 0.037 | 0.935 +/- 0.011 | 0.096 +/- 0.021 | 0.364 +/- 0.046 |

Few-shot strategy chosen by the declared rule (lowest held-out-half FPR at k = 1,000): **diverse**.

## 48f

### A. Whole official test file (zero-shot and transductive methods)

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

### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.723 +/- 0.044 | 0.710 +/- 0.025 | 0.323 +/- 0.074 | 0.272 +/- 0.080 | 0.285 +/- 0.091 | 0.944 +/- 0.007 | 0.114 +/- 0.022 | 0.344 +/- 0.045 |
| self-training, round 2 | transductive | 0.726 +/- 0.046 | 0.714 +/- 0.027 | 0.329 +/- 0.080 | 0.271 +/- 0.080 | 0.242 +/- 0.091 | 0.961 +/- 0.008 | 0.122 +/- 0.025 | 0.354 +/- 0.054 |
| zero-shot baseline (few-shot evaluation rows) | zero-shot | 0.729 +/- 0.031 | 0.702 +/- 0.017 | 0.304 +/- 0.049 | 0.255 +/- 0.049 | 0.251 +/- 0.055 | 0.950 +/- 0.009 | 0.121 +/- 0.019 | 0.344 +/- 0.045 |
| few-shot, diverse selection, k = 1000 | few-shot | 0.742 +/- 0.031 | 0.707 +/- 0.018 | 0.287 +/- 0.048 | 0.138 +/- 0.031 | 0.200 +/- 0.058 | 0.923 +/- 0.016 | 0.119 +/- 0.020 | 0.355 +/- 0.060 |
| few-shot, diverse selection, k = 5000 | few-shot | 0.769 +/- 0.031 | 0.722 +/- 0.019 | 0.248 +/- 0.050 | 0.091 +/- 0.016 | 0.130 +/- 0.035 | 0.933 +/- 0.016 | 0.096 +/- 0.020 | 0.355 +/- 0.054 |

Few-shot strategy chosen by the declared rule (lowest held-out-half FPR at k = 1,000): **diverse**.
