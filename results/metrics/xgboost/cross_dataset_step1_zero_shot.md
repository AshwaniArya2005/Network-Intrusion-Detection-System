# Task 6 Step 1: leak-free zero-shot baseline (5 seeds, mean +/- std; target = the evaluation blocks, 200-row gaps)

## UNSW -> CIC

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| within_dataset_reference | 0.975 +/- 0.005 | 0.997 +/- 0.002 | 0.006 +/- 0.005 | 0.915 +/- 0.032 | 0.014 +/- 0.001 | 0.198 +/- 0.008 | 0 of 5 |
| common_all | 0.492 +/- 0.036 | 0.485 +/- 0.023 | 0.786 +/- 0.104 | 0.845 +/- 0.069 | 0.926 +/- 0.070 | 0.690 +/- 0.117 | 0 of 5 |
| source_only | 0.521 +/- 0.037 | 0.466 +/- 0.041 | 0.795 +/- 0.167 | 0.817 +/- 0.220 | 0.933 +/- 0.046 | 0.745 +/- 0.155 | 0 of 5 |
| stable | 0.502 +/- 0.058 | 0.499 +/- 0.051 | 0.750 +/- 0.150 | 0.771 +/- 0.216 | 0.935 +/- 0.062 | 0.691 +/- 0.128 | 0 of 5 |
| random (10 subsets x 5 seeds) | 0.487 +/- 0.054 | 0.482 +/- 0.068 | 0.710 +/- 0.108 | 0.697 +/- 0.182 | 0.899 +/- 0.072 | 0.642 +/- 0.103 | 0 of 50 |

Stable against random subsets of the same size (AUROC): better in 2 of 5 seeds, mean difference +0.017 (95% interval -0.064, +0.097); spread of the random subsets 0.068; **stable beats random: no**.
Stable against random subsets of the same size (FPR at exactly 95% detection): better in 2 of 5 seeds, mean difference +0.036 (95% interval -0.035, +0.107); spread of the random subsets 0.072; **stable beats random: no**.

## CIC -> UNSW

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| within_dataset_reference | 0.896 +/- 0.011 | 0.972 +/- 0.006 | 0.159 +/- 0.035 | 0.947 +/- 0.016 | 0.163 +/- 0.036 | 0.454 +/- 0.043 | 0 of 5 |
| common_all | 0.502 | 0.578 +/- 0.019 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.927 +/- 0.064 | 0.003 +/- 0.006 | 4 of 5 |
| source_only | n/a | 0.551 +/- 0.046 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.957 +/- 0.026 | 0.001 +/- 0.002 | 5 of 5 |
| stable | n/a | 0.521 +/- 0.044 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.968 +/- 0.017 | 0.001 +/- 0.001 | 5 of 5 |
| random (10 subsets x 5 seeds) | 0.531 +/- 0.056 | 0.541 +/- 0.075 | 0.001 +/- 0.006 | 0.007 +/- 0.045 | 0.926 +/- 0.071 | 0.005 +/- 0.023 | 46 of 50 |

Stable against random subsets of the same size (AUROC): better in 2 of 5 seeds, mean difference -0.020 (95% interval -0.080, +0.041); spread of the random subsets 0.075; **stable beats random: no**.
Stable against random subsets of the same size (FPR at exactly 95% detection): better in 1 of 5 seeds, mean difference +0.042 (95% interval -0.011, +0.095); spread of the random subsets 0.071; **stable beats random: no**.

## Recall per attack type at the argmax (mean over seeds; types with at least 100 evaluation rows)

### UNSW -> CIC

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

### CIC -> UNSW

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

## Block class mix (1,000-row blocks in file order)

| dataset | blocks | pure normal | mixed | pure attack | most frequent dominant attack types (blocks) |
|---|---|---|---|---|---|
| CIC | 2831 | 1523 | 1198 | 110 | DoS Hulk (255), SSH-Patator (218), PortScan (187), DoS GoldenEye (181), DDoS (152) |
| UNSW | 163 | 78 | 38 | 47 | Exploits (60), Fuzzers (13), Generic (12) |

Evaluation rows per attack type (mean over seeds, minimum over seeds): types with fewer than 100 rows in some seed are not reported per type: CIC Heartbleed (min 10), CIC Infiltration (min 7), CIC Web Attack - Sql Injection (min 4), UNSW Worms (min 44).

