# Task 6 Step 3: label-free alignment (TRANSDUCTIVE) against the zero-shot baseline (5 seeds, mean +/- std)

## UNSW -> CIC

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| baseline: common_all (ZERO-SHOT, Step 1) | 0.492 +/- 0.036 | 0.485 +/- 0.023 | 0.786 +/- 0.104 | 0.845 +/- 0.069 | 0.926 +/- 0.070 | 0.690 +/- 0.117 | 0 of 5 |
| per_dataset_standardisation | 0.550 +/- 0.044 | 0.785 +/- 0.030 | 0.139 +/- 0.112 | 0.359 +/- 0.253 | 0.410 +/- 0.041 | 0.107 +/- 0.089 | 0 of 5 |
| quantile_mapping | 0.627 +/- 0.040 | 0.720 +/- 0.035 | 0.723 +/- 0.051 | 0.960 +/- 0.045 | 0.683 +/- 0.070 | 0.708 +/- 0.042 | 0 of 5 |
| drop_top3_shifted | 0.500 +/- 0.015 | 0.524 +/- 0.011 | 0.726 +/- 0.065 | 0.802 +/- 0.134 | 0.862 +/- 0.087 | 0.646 +/- 0.061 | 0 of 5 |
| drop_top5_shifted | 0.508 +/- 0.019 | 0.512 +/- 0.030 | 0.651 +/- 0.060 | 0.696 +/- 0.117 | 0.850 +/- 0.052 | 0.601 +/- 0.043 | 0 of 5 |
| quantile_mapping_drop_top3 | 0.628 +/- 0.025 | 0.727 +/- 0.040 | 0.728 +/- 0.059 | 0.976 +/- 0.023 | 0.681 +/- 0.053 | 0.721 +/- 0.044 | 0 of 5 |

## CIC -> UNSW

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| baseline: common_all (ZERO-SHOT, Step 1) | 0.502 | 0.578 +/- 0.019 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.927 +/- 0.064 | 0.003 +/- 0.006 | 4 of 5 |
| per_dataset_standardisation | 0.511 +/- 0.006 | 0.581 +/- 0.039 | 0.005 +/- 0.007 | 0.013 +/- 0.011 | 0.926 +/- 0.063 | 0.025 +/- 0.025 | 2 of 5 |
| quantile_mapping | 0.474 +/- 0.013 | 0.566 +/- 0.032 | 0.054 +/- 0.038 | 0.029 +/- 0.008 | 0.922 +/- 0.021 | 0.070 +/- 0.026 | 0 of 5 |
| drop_top3_shifted | 0.502 | 0.545 +/- 0.020 | 0.000 +/- 0.000 | 0.000 +/- 0.001 | 0.971 +/- 0.035 | 0.004 +/- 0.008 | 4 of 5 |
| drop_top5_shifted | n/a | 0.624 +/- 0.044 | 0.001 +/- 0.003 | 0.003 +/- 0.006 | 0.793 +/- 0.073 | 0.001 +/- 0.002 | 5 of 5 |
| quantile_mapping_drop_top3 | 0.484 +/- 0.025 | 0.553 +/- 0.033 | 0.040 +/- 0.033 | 0.029 +/- 0.004 | 0.937 +/- 0.024 | 0.056 +/- 0.029 | 0 of 5 |

