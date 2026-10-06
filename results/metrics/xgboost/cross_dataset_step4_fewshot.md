# Task 6 Step 4: few-shot curve, both directions (25 runs per cell = 5 seeds x 5 draws; mean +/- std)

k labelled target rows: half retrain the model (together with the source data for source+target), half choose the threshold; evaluation on target rows from other blocks. Success level: FPR at the held-out-half threshold <= 0.15 with detection >= 0.90, or balanced accuracy within 0.05 of the leak-free reference.

## UNSW -> CIC

Zero-shot baseline on the same evaluation rows (k = 0): FPR 0.786 +/- 0.095, detection 0.838 +/- 0.068, AUROC 0.492 +/- 0.035, balanced accuracy 0.495 +/- 0.035. Leak-free reference (trained on all candidate blocks): FPR 0.019 +/- 0.031, detection 0.938 +/- 0.055, AUROC 0.997 +/- 0.001, balanced accuracy 0.976 +/- 0.005.

| strategy | k | model | FPR at threshold | detection | balanced accuracy | AUROC | FPR at exactly 95% detection | degenerate runs |
|---|---|---|---|---|---|---|---|---|
| random | 100 | source+target | 0.604 +/- 0.306 | 0.893 +/- 0.097 | 0.750 +/- 0.072 | 0.801 +/- 0.100 | 0.743 +/- 0.185 | 0 of 25 |
| random | 100 | target_only | 0.508 +/- 0.230 | 0.936 +/- 0.093 | 0.700 +/- 0.079 | 0.822 +/- 0.069 | 0.530 +/- 0.221 | 0 of 25 |
| random | 500 | source+target | 0.326 +/- 0.233 | 0.937 +/- 0.039 | 0.896 +/- 0.026 | 0.948 +/- 0.023 | 0.352 +/- 0.157 | 0 of 25 |
| random | 500 | target_only | 0.169 +/- 0.130 | 0.941 +/- 0.040 | 0.905 +/- 0.033 | 0.968 +/- 0.013 | 0.163 +/- 0.095 | 0 of 25 |
| random | 1000 | source+target | 0.187 +/- 0.117 | 0.946 +/- 0.027 | 0.923 +/- 0.014 | 0.971 +/- 0.008 | 0.196 +/- 0.075 | 0 of 25 |
| random | 1000 | target_only | 0.096 +/- 0.078 | 0.945 +/- 0.024 | 0.935 +/- 0.015 | 0.981 +/- 0.006 | 0.090 +/- 0.054 | 0 of 25 |
| random | 5000 | source+target | 0.030 +/- 0.009 | 0.948 +/- 0.014 | 0.959 +/- 0.006 | 0.991 +/- 0.002 | 0.036 +/- 0.014 | 0 of 25 |
| random | 5000 | target_only | 0.022 +/- 0.006 | 0.946 +/- 0.016 | 0.963 +/- 0.006 | 0.994 +/- 0.001 | 0.024 +/- 0.006 | 0 of 25 |
| random | 10000 | source+target | 0.021 +/- 0.002 | 0.952 +/- 0.010 | 0.966 +/- 0.004 | 0.994 +/- 0.001 | 0.023 +/- 0.007 | 0 of 25 |
| random | 10000 | target_only | 0.017 +/- 0.002 | 0.952 +/- 0.009 | 0.969 +/- 0.004 | 0.995 +/- 0.001 | 0.018 +/- 0.002 | 0 of 25 |
| diverse | 100 | source+target | 0.580 +/- 0.328 | 0.880 +/- 0.116 | 0.772 +/- 0.048 | 0.823 +/- 0.097 | 0.706 +/- 0.223 | 0 of 25 |
| diverse | 100 | target_only | 0.491 +/- 0.216 | 0.970 +/- 0.046 | 0.738 +/- 0.042 | 0.869 +/- 0.034 | 0.399 +/- 0.166 | 0 of 25 |
| diverse | 500 | source+target | 0.220 +/- 0.218 | 0.896 +/- 0.044 | 0.902 +/- 0.017 | 0.940 +/- 0.027 | 0.456 +/- 0.218 | 0 of 25 |
| diverse | 500 | target_only | 0.199 +/- 0.173 | 0.937 +/- 0.047 | 0.910 +/- 0.020 | 0.970 +/- 0.009 | 0.163 +/- 0.062 | 0 of 25 |
| diverse | 1000 | source+target | 0.178 +/- 0.136 | 0.928 +/- 0.028 | 0.922 +/- 0.017 | 0.964 +/- 0.013 | 0.269 +/- 0.148 | 0 of 25 |
| diverse | 1000 | target_only | 0.108 +/- 0.093 | 0.947 +/- 0.026 | 0.929 +/- 0.020 | 0.980 +/- 0.005 | 0.099 +/- 0.050 | 0 of 25 |
| diverse | 5000 | source+target | 0.032 +/- 0.016 | 0.932 +/- 0.024 | 0.951 +/- 0.011 | 0.990 +/- 0.003 | 0.048 +/- 0.026 | 0 of 25 |
| diverse | 5000 | target_only | 0.023 +/- 0.013 | 0.944 +/- 0.027 | 0.959 +/- 0.012 | 0.993 +/- 0.002 | 0.023 +/- 0.007 | 0 of 25 |
| diverse | 10000 | source+target | 0.015 +/- 0.007 | 0.925 +/- 0.023 | 0.962 +/- 0.008 | 0.994 +/- 0.002 | 0.029 +/- 0.011 | 0 of 25 |
| diverse | 10000 | target_only | 0.013 +/- 0.006 | 0.931 +/- 0.030 | 0.969 +/- 0.007 | 0.995 +/- 0.001 | 0.019 +/- 0.005 | 0 of 25 |

| strategy | model | smallest k: FPR <= 0.15 with detection >= 0.90 | smallest k: balanced accuracy within 0.05 of the reference | source data helps? (source+target minus target-only, FPR, by k) |
|---|---|---|---|---|
| diverse | source+target | 5000 | 5000 | k=100: +0.088 (no); k=500: +0.021 (no); k=1000: +0.069 (no); k=5000: +0.008 (no); k=10000: +0.002 (no) |
| diverse | target_only | 1000 | 1000 |  |
| random | source+target | 5000 | 5000 | k=100: +0.095 (no); k=500: +0.158 (no); k=1000: +0.091 (no); k=5000: +0.009 (no); k=10000: +0.003 (no) |
| random | target_only | 1000 | 1000 |  |

## CIC -> UNSW

Zero-shot baseline on the same evaluation rows (k = 0): FPR 0.000 +/- 0.000, detection 0.000 +/- 0.000, AUROC 0.574 +/- 0.025, balanced accuracy 0.501 +/- 0.001. Leak-free reference (trained on all candidate blocks): FPR 0.210 +/- 0.035, detection 0.951 +/- 0.012, AUROC 0.960 +/- 0.007, balanced accuracy 0.876 +/- 0.013.

| strategy | k | model | FPR at threshold | detection | balanced accuracy | AUROC | FPR at exactly 95% detection | degenerate runs |
|---|---|---|---|---|---|---|---|---|
| random | 100 | source+target | 0.554 +/- 0.144 | 0.938 +/- 0.047 | 0.667 +/- 0.027 | 0.814 +/- 0.026 | 0.540 +/- 0.096 | 0 of 25 |
| random | 100 | target_only | 0.575 +/- 0.162 | 0.939 +/- 0.055 | 0.687 +/- 0.028 | 0.748 +/- 0.030 | 0.582 +/- 0.108 | 0 of 25 |
| random | 500 | source+target | 0.345 +/- 0.054 | 0.949 +/- 0.019 | 0.762 +/- 0.026 | 0.888 +/- 0.019 | 0.340 +/- 0.042 | 0 of 25 |
| random | 500 | target_only | 0.356 +/- 0.055 | 0.946 +/- 0.022 | 0.801 +/- 0.024 | 0.892 +/- 0.018 | 0.358 +/- 0.034 | 0 of 25 |
| random | 1000 | source+target | 0.292 +/- 0.033 | 0.948 +/- 0.013 | 0.803 +/- 0.016 | 0.906 +/- 0.017 | 0.293 +/- 0.028 | 0 of 25 |
| random | 1000 | target_only | 0.296 +/- 0.035 | 0.946 +/- 0.015 | 0.830 +/- 0.014 | 0.918 +/- 0.013 | 0.298 +/- 0.028 | 0 of 25 |
| random | 5000 | source+target | 0.245 +/- 0.032 | 0.945 +/- 0.008 | 0.850 +/- 0.011 | 0.941 +/- 0.009 | 0.252 +/- 0.029 | 0 of 25 |
| random | 5000 | target_only | 0.235 +/- 0.035 | 0.945 +/- 0.009 | 0.858 +/- 0.012 | 0.947 +/- 0.008 | 0.242 +/- 0.029 | 0 of 25 |
| random | 10000 | source+target | 0.232 +/- 0.032 | 0.947 +/- 0.006 | 0.861 +/- 0.012 | 0.950 +/- 0.008 | 0.236 +/- 0.030 | 0 of 25 |
| random | 10000 | target_only | 0.224 +/- 0.030 | 0.946 +/- 0.006 | 0.865 +/- 0.012 | 0.954 +/- 0.007 | 0.230 +/- 0.030 | 0 of 25 |
| diverse | 100 | source+target | 0.512 +/- 0.141 | 0.927 +/- 0.062 | 0.653 +/- 0.054 | 0.807 +/- 0.036 | 0.519 +/- 0.085 | 0 of 25 |
| diverse | 100 | target_only | 0.591 +/- 0.139 | 0.942 +/- 0.051 | 0.684 +/- 0.055 | 0.731 +/- 0.040 | 0.592 +/- 0.118 | 0 of 25 |
| diverse | 500 | source+target | 0.340 +/- 0.052 | 0.959 +/- 0.019 | 0.780 +/- 0.022 | 0.885 +/- 0.021 | 0.320 +/- 0.039 | 0 of 25 |
| diverse | 500 | target_only | 0.348 +/- 0.045 | 0.948 +/- 0.020 | 0.804 +/- 0.019 | 0.887 +/- 0.023 | 0.347 +/- 0.038 | 0 of 25 |
| diverse | 1000 | source+target | 0.294 +/- 0.032 | 0.952 +/- 0.013 | 0.814 +/- 0.016 | 0.907 +/- 0.015 | 0.290 +/- 0.028 | 0 of 25 |
| diverse | 1000 | target_only | 0.293 +/- 0.040 | 0.946 +/- 0.015 | 0.831 +/- 0.013 | 0.914 +/- 0.012 | 0.296 +/- 0.028 | 0 of 25 |
| diverse | 5000 | source+target | 0.254 +/- 0.034 | 0.954 +/- 0.007 | 0.855 +/- 0.011 | 0.942 +/- 0.010 | 0.247 +/- 0.031 | 0 of 25 |
| diverse | 5000 | target_only | 0.244 +/- 0.033 | 0.950 +/- 0.007 | 0.859 +/- 0.012 | 0.946 +/- 0.009 | 0.244 +/- 0.029 | 0 of 25 |
| diverse | 10000 | source+target | 0.242 +/- 0.033 | 0.956 +/- 0.005 | 0.863 +/- 0.011 | 0.950 +/- 0.008 | 0.233 +/- 0.029 | 0 of 25 |
| diverse | 10000 | target_only | 0.234 +/- 0.034 | 0.955 +/- 0.005 | 0.866 +/- 0.012 | 0.953 +/- 0.007 | 0.225 +/- 0.029 | 0 of 25 |

| strategy | model | smallest k: FPR <= 0.15 with detection >= 0.90 | smallest k: balanced accuracy within 0.05 of the reference | source data helps? (source+target minus target-only, FPR, by k) |
|---|---|---|---|---|
| diverse | source+target | not reached | 5000 | k=100: -0.079 (yes); k=500: -0.008 (no); k=1000: +0.001 (no); k=5000: +0.010 (no); k=10000: +0.008 (no) |
| diverse | target_only | not reached | 1000 |  |
| random | source+target | not reached | 5000 | k=100: -0.021 (no); k=500: -0.011 (no); k=1000: -0.004 (no); k=5000: +0.010 (no); k=10000: +0.008 (no) |
| random | target_only | not reached | 1000 |  |

