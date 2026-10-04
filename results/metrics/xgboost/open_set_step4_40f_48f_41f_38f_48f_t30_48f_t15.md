# Task 4 Step 4: does ct_* carry the open-set gain? (XGBoost, official split, threshold at 5% false-Unknown, mean +/- std over 5 seeds)

msp detection: 40f 0.223, 48f 0.333 (gap 0.110); without the 7 window-count ct_* columns 0.172 (drop 0.161). Declared reading: **confirmed**.

| variant | score | unknown AUROC | detection @5% | false-Unknown test |
|---|---|---|---|---|
| 40f | msp | 0.798 +/- 0.004 | 0.223 +/- 0.037 | 0.059 +/- 0.014 |
| 40f | entropy | 0.862 +/- 0.005 | 0.158 +/- 0.047 | 0.025 +/- 0.010 |
| 48f | msp | 0.834 +/- 0.007 | 0.333 +/- 0.044 | 0.050 +/- 0.017 |
| 48f | iforest+entropy:max | 0.810 +/- 0.031 | 0.187 +/- 0.050 | 0.034 +/- 0.013 |
| 41f | msp | 0.764 +/- 0.006 | 0.172 +/- 0.038 | 0.061 +/- 0.012 |
| 41f | margin | 0.743 +/- 0.006 | 0.136 +/- 0.043 | 0.075 +/- 0.018 |
| 38f | msp | 0.762 +/- 0.007 | 0.171 +/- 0.031 | 0.062 +/- 0.014 |
| 38f | margin | 0.740 +/- 0.006 | 0.126 +/- 0.040 | 0.073 +/- 0.017 |
| 48f_t30 | msp | 0.825 +/- 0.005 | 0.340 +/- 0.024 | 0.057 +/- 0.012 |
| 48f_t30 | entropy | 0.870 +/- 0.003 | 0.224 +/- 0.042 | 0.024 +/- 0.008 |
| 48f_t15 | msp | 0.763 +/- 0.010 | 0.193 +/- 0.045 | 0.065 +/- 0.015 |
| 48f_t15 | margin | 0.740 +/- 0.011 | 0.132 +/- 0.051 | 0.075 +/- 0.016 |
