# Task 6 tables (XGBoost): cross-dataset zero-shot, diagnostic, alignment, few-shot curve

Merged in the Task 7 cleanup from the per-table files named below. Each section is the original file with every line unchanged except that its headings are demoted by two levels; nothing was added to or removed from any table or caveat. The generation scripts still write the original per-table names if re-run.

## Source: cross_dataset_step1_zero_shot.md

### Task 6 Step 1: leak-free zero-shot baseline (5 seeds, mean +/- std; target = the evaluation blocks, 200-row gaps)

#### UNSW -> CIC

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| within_dataset_reference | 0.975 +/- 0.005 | 0.997 +/- 0.002 | 0.006 +/- 0.005 | 0.915 +/- 0.032 | 0.014 +/- 0.001 | 0.198 +/- 0.008 | 0 of 5 |
| common_all | 0.492 +/- 0.036 | 0.485 +/- 0.023 | 0.786 +/- 0.104 | 0.845 +/- 0.069 | 0.926 +/- 0.070 | 0.690 +/- 0.117 | 0 of 5 |
| source_only | 0.521 +/- 0.037 | 0.466 +/- 0.041 | 0.795 +/- 0.167 | 0.817 +/- 0.220 | 0.933 +/- 0.046 | 0.745 +/- 0.155 | 0 of 5 |
| stable | 0.502 +/- 0.058 | 0.499 +/- 0.051 | 0.750 +/- 0.150 | 0.771 +/- 0.216 | 0.935 +/- 0.062 | 0.691 +/- 0.128 | 0 of 5 |
| random (10 subsets x 5 seeds) | 0.487 +/- 0.054 | 0.482 +/- 0.068 | 0.710 +/- 0.108 | 0.697 +/- 0.182 | 0.899 +/- 0.072 | 0.642 +/- 0.103 | 0 of 50 |

Stable against random subsets of the same size (AUROC): better in 2 of 5 seeds, mean difference +0.017 (95% interval -0.064, +0.097); spread of the random subsets 0.068; **stable beats random: no**.
Stable against random subsets of the same size (FPR at exactly 95% detection): better in 2 of 5 seeds, mean difference +0.036 (95% interval -0.035, +0.107); spread of the random subsets 0.072; **stable beats random: no**.

#### CIC -> UNSW

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| within_dataset_reference | 0.896 +/- 0.011 | 0.972 +/- 0.006 | 0.159 +/- 0.035 | 0.947 +/- 0.016 | 0.163 +/- 0.036 | 0.454 +/- 0.043 | 0 of 5 |
| common_all | 0.502 | 0.578 +/- 0.019 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.927 +/- 0.064 | 0.003 +/- 0.006 | 4 of 5 |
| source_only | n/a | 0.551 +/- 0.046 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.957 +/- 0.026 | 0.001 +/- 0.002 | 5 of 5 |
| stable | n/a | 0.521 +/- 0.044 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.968 +/- 0.017 | 0.001 +/- 0.001 | 5 of 5 |
| random (10 subsets x 5 seeds) | 0.531 +/- 0.056 | 0.541 +/- 0.075 | 0.001 +/- 0.006 | 0.007 +/- 0.045 | 0.926 +/- 0.071 | 0.005 +/- 0.023 | 46 of 50 |

Stable against random subsets of the same size (AUROC): better in 2 of 5 seeds, mean difference -0.020 (95% interval -0.080, +0.041); spread of the random subsets 0.075; **stable beats random: no**.
Stable against random subsets of the same size (FPR at exactly 95% detection): better in 1 of 5 seeds, mean difference +0.042 (95% interval -0.011, +0.095); spread of the random subsets 0.071; **stable beats random: no**.

#### Recall per attack type at the argmax (mean over seeds; types with at least 100 evaluation rows)

##### UNSW -> CIC

| attack type | evaluation rows | zero-shot (common_all) | leak-free reference |
|---|---|---|---|
| Bot | 660 | 0.537 | 0.372 |
| DDoS | 38482 | 0.650 | 0.997 |
| DoS GoldenEye | 3058 | 0.692 | 0.893 |
| DoS Hulk | 67302 | 0.824 | 0.967 |
| DoS Slowhttptest | 1310 | 0.384 | 0.456 |
| DoS slowloris | 1409 | 0.385 | 0.695 |
| FTP-Patator | 2821 | 0.568 | 0.981 |
| PortScan | 48166 | 0.534 | 0.998 |
| SSH-Patator | 1596 | 0.525 | 0.494 |
| Web Attack - Brute Force | 400 | 0.139 | 0.060 |
| Web Attack - XSS | 244 | 0.047 | 0.011 |

##### CIC -> UNSW

| attack type | evaluation rows | zero-shot (common_all) | leak-free reference |
|---|---|---|---|
| Analysis | 601 | 0.000 | 0.809 |
| Backdoor | 517 | 0.000 | 0.983 |
| DoS | 1525 | 0.001 | 0.955 |
| Exploits | 7659 | 0.001 | 0.968 |
| Fuzzers | 6060 | 0.009 | 0.702 |
| Generic | 2352 | 0.004 | 0.991 |
| Reconnaissance | 2857 | 0.000 | 0.992 |
| Shellcode | 412 | 0.004 | 0.859 |

#### Block class mix (1,000-row blocks in file order)

| dataset | blocks | pure normal | mixed | pure attack | most frequent dominant attack types (blocks) |
|---|---|---|---|---|---|
| CIC | 2831 | 1523 | 1198 | 110 | DoS Hulk (255), SSH-Patator (218), PortScan (187), DoS GoldenEye (181), DDoS (152) |
| UNSW | 163 | 78 | 38 | 47 | Exploits (60), Fuzzers (13), Generic (12) |

Evaluation rows per attack type (mean over seeds, minimum over seeds): types with fewer than 100 rows in some seed are not reported per type: CIC Heartbleed (min 10), CIC Infiltration (min 7), CIC Web Attack - Sql Injection (min 4), UNSW Worms (min 44).

## Source: cross_dataset_step2_diagnostic.md

### Task 6 Step 2: why zero-shot fails (diagnostic)

AUROC of each common feature alone for attack against normal (all rows of each dataset; above 0.5 = attack flows have higher values). `absent` = |AUROC - 0.5| < 0.05 in at least one dataset.

| feature | UNSW | CIC | same direction | absent in either dataset | flipped (clear and opposite) |
|---|---|---|---|---|---|
| avg_pkt_size | 0.445 | 0.521 | no | yes | no |
| byte_ratio | 0.470 | 0.278 | yes | yes | no |
| dbytes | 0.362 | 0.543 | no | yes | no |
| dmean | 0.302 | 0.561 | no | no | yes |
| dpkts | 0.367 | 0.489 | yes | yes | no |
| dur | 0.560 | 0.542 | yes | yes | no |
| duration_log | 0.560 | 0.542 | yes | yes | no |
| pkt_ratio | 0.499 | 0.429 | yes | yes | no |
| rate | 0.441 | 0.440 | yes | no | no |
| sbytes | 0.416 | 0.363 | yes | no | no |
| smean | 0.526 | 0.343 | no | yes | no |
| spkts | 0.404 | 0.547 | no | yes | no |
| total_bytes | 0.398 | 0.509 | no | yes | no |
| total_pkts | 0.382 | 0.525 | no | yes | no |

Of 14 features: 7 point the same way, 7 do not, 11 are absent (near 0.5) in at least one dataset and 1 are clearly flipped. SHAP importance rank agreement between a UNSW-trained and a CIC-trained model on the common features: Spearman 0.52 +/- 0.05 over 5 seeds.

Zero-shot AUROC of the common_all model: CIC -> UNSW 0.578 +/- 0.019; UNSW -> CIC 0.485 +/- 0.023.

## Source: cross_dataset_step3_align.md

### Task 6 Step 3: label-free alignment (TRANSDUCTIVE) against the zero-shot baseline (5 seeds, mean +/- std)

#### UNSW -> CIC

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| baseline: common_all (ZERO-SHOT, Step 1) | 0.492 +/- 0.036 | 0.485 +/- 0.023 | 0.786 +/- 0.104 | 0.845 +/- 0.069 | 0.926 +/- 0.070 | 0.690 +/- 0.117 | 0 of 5 |
| per_dataset_standardisation | 0.550 +/- 0.044 | 0.785 +/- 0.030 | 0.139 +/- 0.112 | 0.359 +/- 0.253 | 0.410 +/- 0.041 | 0.107 +/- 0.089 | 0 of 5 |
| quantile_mapping | 0.627 +/- 0.040 | 0.720 +/- 0.035 | 0.723 +/- 0.051 | 0.960 +/- 0.045 | 0.683 +/- 0.070 | 0.708 +/- 0.042 | 0 of 5 |
| drop_top3_shifted | 0.500 +/- 0.015 | 0.524 +/- 0.011 | 0.726 +/- 0.065 | 0.802 +/- 0.134 | 0.862 +/- 0.087 | 0.646 +/- 0.061 | 0 of 5 |
| drop_top5_shifted | 0.508 +/- 0.019 | 0.512 +/- 0.030 | 0.651 +/- 0.060 | 0.696 +/- 0.117 | 0.850 +/- 0.052 | 0.601 +/- 0.043 | 0 of 5 |
| quantile_mapping_drop_top3 | 0.628 +/- 0.025 | 0.727 +/- 0.040 | 0.728 +/- 0.059 | 0.976 +/- 0.023 | 0.681 +/- 0.053 | 0.721 +/- 0.044 | 0 of 5 |

#### CIC -> UNSW

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| baseline: common_all (ZERO-SHOT, Step 1) | 0.502 | 0.578 +/- 0.019 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.927 +/- 0.064 | 0.003 +/- 0.006 | 4 of 5 |
| per_dataset_standardisation | 0.511 +/- 0.006 | 0.581 +/- 0.039 | 0.005 +/- 0.007 | 0.013 +/- 0.011 | 0.926 +/- 0.063 | 0.025 +/- 0.025 | 2 of 5 |
| quantile_mapping | 0.474 +/- 0.013 | 0.566 +/- 0.032 | 0.054 +/- 0.038 | 0.029 +/- 0.008 | 0.922 +/- 0.021 | 0.070 +/- 0.026 | 0 of 5 |
| drop_top3_shifted | 0.502 | 0.545 +/- 0.020 | 0.000 +/- 0.000 | 0.000 +/- 0.001 | 0.971 +/- 0.035 | 0.004 +/- 0.008 | 4 of 5 |
| drop_top5_shifted | n/a | 0.624 +/- 0.044 | 0.001 +/- 0.003 | 0.003 +/- 0.006 | 0.793 +/- 0.073 | 0.001 +/- 0.002 | 5 of 5 |
| quantile_mapping_drop_top3 | 0.484 +/- 0.025 | 0.553 +/- 0.033 | 0.040 +/- 0.033 | 0.029 +/- 0.004 | 0.937 +/- 0.024 | 0.056 +/- 0.029 | 0 of 5 |

## Source: cross_dataset_step4_fewshot.md

### Task 6 Step 4: few-shot curve, both directions (25 runs per cell = 5 seeds x 5 draws; mean +/- std)

k labelled target rows: half retrain the model (together with the source data for source+target), half choose the threshold; evaluation on target rows from other blocks. Success level: FPR at the held-out-half threshold <= 0.15 with detection >= 0.90, or balanced accuracy within 0.05 of the leak-free reference.

#### UNSW -> CIC

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

#### CIC -> UNSW

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

