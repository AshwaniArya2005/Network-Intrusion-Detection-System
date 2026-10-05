# Task 5.5 Step 2: explanations of false-positive flows (official test, 5 seeds, 300 flows per group and model, mean +/- std)

FP-attack = true Normal predicted as an attack; FP-Fuzzers = true Normal predicted as Fuzzers; TN = true Normal predicted Normal; TP-Fuzzers = true Fuzzers predicted Fuzzers.

## 40f

### (a) Deletion faithfulness: probability drop at k = 5, top SHAP minus random removal (median baseline; random-row baseline in brackets)

| group | flows in test | top SHAP drop | random drop | difference (std over seeds) | seeds with interval above 0 and difference >= 0.05 | top: class flips |
|---|---|---|---|---|---|---|
| TN | 24057 | 0.215 +/- 0.030 | 0.031 +/- 0.012 | 0.184 +/- 0.024 (0.386 +/- 0.029) | 5 of 5 | 0.263 +/- 0.086 |
| FP-attack | 9775 | 0.510 +/- 0.053 | 0.161 +/- 0.015 | 0.349 +/- 0.051 (0.336 +/- 0.017) | 5 of 5 | 0.904 +/- 0.063 |
| FP-Fuzzers | 8218 | 0.531 +/- 0.067 | 0.172 +/- 0.028 | 0.359 +/- 0.065 (0.342 +/- 0.034) | 5 of 5 | 0.881 +/- 0.077 |
| TP-Fuzzers | 3658 | 0.615 +/- 0.042 | 0.181 +/- 0.014 | 0.435 +/- 0.042 (0.416 +/- 0.010) | 5 of 5 | 0.893 +/- 0.060 |

### (c) Confidence on these flows

| group | raw confidence | calibrated confidence | raw >= 0.90 | calibrated >= 0.90 | flagged Unknown | features cited (class-relative) | class-atypicality of cited features |
|---|---|---|---|---|---|---|---|
| TN | 0.928 +/- 0.011 | 0.920 +/- 0.013 | 0.826 +/- 0.026 | 0.819 +/- 0.027 | 0.044 +/- 0.010 | 3.12 +/- 0.17 | 0.411 +/- 0.039 |
| FP-attack | 0.675 +/- 0.008 | 0.638 +/- 0.012 | 0.088 +/- 0.026 | 0.043 +/- 0.022 | 0.130 +/- 0.036 | 2.94 +/- 0.14 | 0.457 +/- 0.020 |
| FP-Fuzzers | 0.701 +/- 0.011 | 0.662 +/- 0.010 | 0.105 +/- 0.016 | 0.048 +/- 0.014 | 0.065 +/- 0.034 | 3.02 +/- 0.11 | 0.463 +/- 0.014 |
| TP-Fuzzers | 0.771 +/- 0.011 | 0.734 +/- 0.015 | 0.294 +/- 0.040 | 0.206 +/- 0.031 | 0.051 +/- 0.018 | 2.71 +/- 0.09 | 0.500 +/- 0.042 |

### (c) Does anything separate a false positive from a correct flow? (AUROC; 0.5 = nothing; positive = the false-positive group)

| false positives | compared with | score | AUROC |
|---|---|---|---|
| FP-Fuzzers | TP-Fuzzers | 1 - raw confidence | 0.632 +/- 0.022 |
| FP-Fuzzers | TP-Fuzzers | 1 - calibrated confidence | 0.632 +/- 0.022 |
| FP-Fuzzers | TP-Fuzzers | class-atypicality of the cited features | 0.470 +/- 0.035 |
| FP-attack | TN | 1 - raw confidence | 0.886 +/- 0.019 |
| FP-attack | TN | 1 - calibrated confidence | 0.887 +/- 0.019 |
| FP-attack | TN | class-atypicality of the cited features | 0.553 +/- 0.039 |

### (b) Features the classic narrative cites most often (share of narratives, mean over seeds)

| group | top cited features |
|---|---|
| TN | ackdat (76%), dload (63%), dloss (41%), synack (39%), dbytes (37%) |
| FP-attack | service (76%), dload (75%), avg_pkt_size (52%), sbytes (47%), smean (44%) |
| FP-Fuzzers | dload (88%), service (77%), sbytes (55%), avg_pkt_size (50%), smean (48%) |
| TP-Fuzzers | dload (76%), service (75%), sbytes (70%), smean (42%), dbytes (38%) |

## 48f

### (a) Deletion faithfulness: probability drop at k = 5, top SHAP minus random removal (median baseline; random-row baseline in brackets)

| group | flows in test | top SHAP drop | random drop | difference (std over seeds) | seeds with interval above 0 and difference >= 0.05 | top: class flips |
|---|---|---|---|---|---|---|
| TN | 23754 | 0.748 +/- 0.027 | 0.055 +/- 0.018 | 0.693 +/- 0.038 (0.469 +/- 0.058) | 5 of 5 | 0.848 +/- 0.021 |
| FP-attack | 10078 | 0.594 +/- 0.157 | 0.120 +/- 0.039 | 0.474 +/- 0.122 (0.387 +/- 0.010) | 5 of 5 | 0.891 +/- 0.197 |
| FP-Fuzzers | 8594 | 0.640 +/- 0.192 | 0.131 +/- 0.036 | 0.509 +/- 0.159 (0.404 +/- 0.022) | 5 of 5 | 0.903 +/- 0.218 |
| TP-Fuzzers | 3472 | 0.701 +/- 0.133 | 0.144 +/- 0.033 | 0.558 +/- 0.104 (0.447 +/- 0.022) | 5 of 5 | 0.929 +/- 0.158 |

### (c) Confidence on these flows

| group | raw confidence | calibrated confidence | raw >= 0.90 | calibrated >= 0.90 | flagged Unknown | features cited (class-relative) | class-atypicality of cited features |
|---|---|---|---|---|---|---|---|
| TN | 0.940 +/- 0.010 | 0.932 +/- 0.009 | 0.843 +/- 0.023 | 0.841 +/- 0.023 | 0.026 +/- 0.017 | 2.49 +/- 0.11 | 0.326 +/- 0.031 |
| FP-attack | 0.719 +/- 0.011 | 0.668 +/- 0.015 | 0.128 +/- 0.018 | 0.057 +/- 0.023 | 0.089 +/- 0.052 | 2.88 +/- 0.12 | 0.384 +/- 0.018 |
| FP-Fuzzers | 0.742 +/- 0.023 | 0.692 +/- 0.013 | 0.165 +/- 0.047 | 0.072 +/- 0.019 | 0.044 +/- 0.032 | 3.00 +/- 0.15 | 0.424 +/- 0.024 |
| TP-Fuzzers | 0.778 +/- 0.016 | 0.723 +/- 0.019 | 0.297 +/- 0.047 | 0.157 +/- 0.046 | 0.065 +/- 0.029 | 2.73 +/- 0.10 | 0.414 +/- 0.023 |

### (c) Does anything separate a false positive from a correct flow? (AUROC; 0.5 = nothing; positive = the false-positive group)

| false positives | compared with | score | AUROC |
|---|---|---|---|
| FP-Fuzzers | TP-Fuzzers | 1 - raw confidence | 0.580 +/- 0.051 |
| FP-Fuzzers | TP-Fuzzers | 1 - calibrated confidence | 0.569 +/- 0.052 |
| FP-Fuzzers | TP-Fuzzers | class-atypicality of the cited features | 0.519 +/- 0.031 |
| FP-attack | TN | 1 - raw confidence | 0.892 +/- 0.016 |
| FP-attack | TN | 1 - calibrated confidence | 0.892 +/- 0.017 |
| FP-attack | TN | class-atypicality of the cited features | 0.581 +/- 0.032 |

### (b) Features the classic narrative cites most often (share of narratives, mean over seeds)

| group | top cited features |
|---|---|
| TN | ct_state_ttl (84%), sttl (71%), ct_srv_dst (51%), ct_srv_src (35%), dload (27%) |
| FP-attack | sttl (95%), smean (47%), ct_dst_src_ltm (46%), sbytes (44%), avg_pkt_size (37%) |
| FP-Fuzzers | sttl (100%), smean (52%), sbytes (51%), ct_dst_src_ltm (48%), ct_srv_dst (39%) |
| TP-Fuzzers | sttl (100%), sbytes (62%), smean (38%), dbytes (36%), service (33%) |

