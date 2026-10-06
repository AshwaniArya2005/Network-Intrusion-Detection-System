# Task 2.6: is the few-shot result adaptation or neighbour leakage? (official split, mean +/- std over 5 runs)

Few-shot = k labelled test rows (half retrain, half choose the 95%-detection threshold), evaluated on rows not used for adaptation. Zero-shot rows use the validation-chosen threshold.

| pool | k | row | access | FPR at ~95% detection | detection | accuracy | ECE |
|---|---|---|---|---|---|---|---|
| 40f | 1000 | original Task 2.5 result (retrain_split_f0.5, random adaptation rows) | few-shot | 0.2666 +/- 0.0378 | 0.9541 +/- 0.0143 | 0.7515 +/- 0.0013 | 0.0858 +/- 0.0013 |
| 40f | 1000 | twins: all evaluation rows (reproduction) | few-shot | 0.2666 +/- 0.0378 | 0.9541 +/- 0.0143 | 0.7515 +/- 0.0013 | 0.0858 +/- 0.0013 |
| 40f | 1000 | twins: all evaluation rows (reproduction) - zero-shot | zero-shot | 0.2498 +/- 0.0024 | 0.9464 +/- 0.0017 | 0.7425 +/- 0.0009 | 0.0878 +/- 0.0010 |
| 40f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set | few-shot | 0.3563 +/- 0.0525 | 0.9510 +/- 0.0157 | 0.7038 +/- 0.0012 | 0.0988 +/- 0.0017 |
| 40f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set - zero-shot | zero-shot | 0.3258 +/- 0.0046 | 0.9402 +/- 0.0013 | 0.6944 +/- 0.0023 | 0.1022 +/- 0.0025 |
| 40f | 1000 | twins: rows WITH a near twin (<= 0.1) | few-shot | 0.0658 +/- 0.0105 | 0.9743 +/- 0.0095 | 0.9019 +/- 0.0055 | 0.0446 +/- 0.0052 |
| 40f | 1000 | twins: rows WITH a near twin (<= 0.1) - zero-shot | zero-shot | 0.0796 +/- 0.0076 | 0.9878 +/- 0.0022 | 0.8942 +/- 0.0079 | 0.0449 +/- 0.0046 |
| 40f | 1000 | blocks: adaptation rows from the evaluation blocks (within-file) | few-shot | 0.2519 +/- 0.0649 | 0.9457 +/- 0.0293 | 0.7497 +/- 0.0253 | 0.0851 +/- 0.0104 |
| 40f | 1000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) | few-shot | 0.3045 +/- 0.0812 | 0.9622 +/- 0.0232 | 0.7472 +/- 0.0285 | 0.0862 +/- 0.0134 |
| 40f | 1000 | blocks: same rows - zero-shot | zero-shot | 0.2508 +/- 0.0411 | 0.9456 +/- 0.0103 | 0.7388 +/- 0.0298 | 0.0879 +/- 0.0132 |
| 40f | 5000 | original Task 2.5 result (retrain_split_f0.5, random adaptation rows) | few-shot | 0.2318 +/- 0.0108 | 0.9513 +/- 0.0032 | 0.7801 +/- 0.0021 | 0.0600 +/- 0.0019 |
| 40f | 5000 | twins: all evaluation rows (reproduction) | few-shot | 0.2318 +/- 0.0108 | 0.9513 +/- 0.0032 | 0.7801 +/- 0.0021 | 0.0600 +/- 0.0019 |
| 40f | 5000 | twins: all evaluation rows (reproduction) - zero-shot | zero-shot | 0.2497 +/- 0.0033 | 0.9466 +/- 0.0012 | 0.7424 +/- 0.0010 | 0.0877 +/- 0.0011 |
| 40f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set | few-shot | 0.3493 +/- 0.0185 | 0.9457 +/- 0.0050 | 0.7236 +/- 0.0035 | 0.0671 +/- 0.0031 |
| 40f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set - zero-shot | zero-shot | 0.3671 +/- 0.0056 | 0.9356 +/- 0.0014 | 0.6724 +/- 0.0026 | 0.1080 +/- 0.0029 |
| 40f | 5000 | twins: rows WITH a near twin (<= 0.1) | few-shot | 0.0824 +/- 0.0040 | 0.9696 +/- 0.0069 | 0.8791 +/- 0.0030 | 0.0482 +/- 0.0051 |
| 40f | 5000 | twins: rows WITH a near twin (<= 0.1) - zero-shot | zero-shot | 0.1002 +/- 0.0020 | 0.9817 +/- 0.0020 | 0.8651 +/- 0.0018 | 0.0530 +/- 0.0026 |
| 40f | 5000 | blocks: adaptation rows from the evaluation blocks (within-file) | few-shot | 0.2025 +/- 0.0481 | 0.9398 +/- 0.0114 | 0.7809 +/- 0.0175 | 0.0571 +/- 0.0057 |
| 40f | 5000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) | few-shot | 0.2427 +/- 0.0468 | 0.9449 +/- 0.0191 | 0.7666 +/- 0.0296 | 0.0703 +/- 0.0137 |
| 40f | 5000 | blocks: same rows - zero-shot | zero-shot | 0.2508 +/- 0.0411 | 0.9456 +/- 0.0103 | 0.7388 +/- 0.0298 | 0.0879 +/- 0.0132 |
| 48f | 1000 | original Task 2.5 result (retrain_split_f0.5, random adaptation rows) | few-shot | 0.1578 +/- 0.0374 | 0.9472 +/- 0.0164 | 0.7598 +/- 0.0015 | 0.1033 +/- 0.0017 |
| 48f | 1000 | twins: all evaluation rows (reproduction) | few-shot | 0.1578 +/- 0.0374 | 0.9472 +/- 0.0164 | 0.7598 +/- 0.0015 | 0.1033 +/- 0.0017 |
| 48f | 1000 | twins: all evaluation rows (reproduction) - zero-shot | zero-shot | 0.2444 +/- 0.0068 | 0.9525 +/- 0.0013 | 0.7400 +/- 0.0021 | 0.1093 +/- 0.0026 |
| 48f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set | few-shot | 0.1587 +/- 0.0376 | 0.9463 +/- 0.0168 | 0.7600 +/- 0.0013 | 0.1024 +/- 0.0016 |
| 48f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set - zero-shot | zero-shot | 0.2454 +/- 0.0069 | 0.9517 +/- 0.0013 | 0.7397 +/- 0.0021 | 0.1096 +/- 0.0025 |
| 48f | 1000 | twins: rows WITH a near twin (<= 0.1) | few-shot | 0.0289 +/- 0.0078 | 0.9957 +/- 0.0024 | 0.7342 +/- 0.0392 | 0.1887 +/- 0.0231 |
| 48f | 1000 | twins: rows WITH a near twin (<= 0.1) - zero-shot | zero-shot | 0.0997 +/- 0.0154 | 0.9950 +/- 0.0035 | 0.7607 +/- 0.0269 | 0.0916 +/- 0.0124 |
| 48f | 1000 | blocks: adaptation rows from the evaluation blocks (within-file) | few-shot | 0.1395 +/- 0.0442 | 0.9337 +/- 0.0227 | 0.7574 +/- 0.0266 | 0.1028 +/- 0.0129 |
| 48f | 1000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) | few-shot | 0.1528 +/- 0.0466 | 0.9362 +/- 0.0284 | 0.7521 +/- 0.0279 | 0.1084 +/- 0.0151 |
| 48f | 1000 | blocks: same rows - zero-shot | zero-shot | 0.2463 +/- 0.0400 | 0.9511 +/- 0.0086 | 0.7348 +/- 0.0304 | 0.1123 +/- 0.0160 |
| 48f | 5000 | original Task 2.5 result (retrain_split_f0.5, random adaptation rows) | few-shot | 0.0940 +/- 0.0156 | 0.9523 +/- 0.0076 | 0.7957 +/- 0.0031 | 0.0708 +/- 0.0028 |
| 48f | 5000 | twins: all evaluation rows (reproduction) | few-shot | 0.0940 +/- 0.0156 | 0.9523 +/- 0.0076 | 0.7957 +/- 0.0031 | 0.0708 +/- 0.0028 |
| 48f | 5000 | twins: all evaluation rows (reproduction) - zero-shot | zero-shot | 0.2442 +/- 0.0074 | 0.9527 +/- 0.0017 | 0.7398 +/- 0.0023 | 0.1094 +/- 0.0027 |
| 48f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set | few-shot | 0.0958 +/- 0.0159 | 0.9492 +/- 0.0082 | 0.7990 +/- 0.0033 | 0.0656 +/- 0.0028 |
| 48f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set - zero-shot | zero-shot | 0.2478 +/- 0.0078 | 0.9494 +/- 0.0019 | 0.7394 +/- 0.0025 | 0.1103 +/- 0.0028 |
| 48f | 5000 | twins: rows WITH a near twin (<= 0.1) | few-shot | 0.0311 +/- 0.0079 | 0.9920 +/- 0.0012 | 0.7251 +/- 0.0085 | 0.1843 +/- 0.0100 |
| 48f | 5000 | twins: rows WITH a near twin (<= 0.1) - zero-shot | zero-shot | 0.1142 +/- 0.0073 | 0.9934 +/- 0.0013 | 0.7480 +/- 0.0055 | 0.0910 +/- 0.0058 |
| 48f | 5000 | blocks: adaptation rows from the evaluation blocks (within-file) | few-shot | 0.0851 +/- 0.0333 | 0.9446 +/- 0.0089 | 0.7987 +/- 0.0191 | 0.0660 +/- 0.0051 |
| 48f | 5000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) | few-shot | 0.0854 +/- 0.0162 | 0.9318 +/- 0.0167 | 0.7732 +/- 0.0315 | 0.0905 +/- 0.0184 |
| 48f | 5000 | blocks: same rows - zero-shot | zero-shot | 0.2463 +/- 0.0400 | 0.9511 +/- 0.0086 | 0.7348 +/- 0.0304 | 0.1123 +/- 0.0160 |
| 45f | 1000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.1742 +/- 0.0430 | 0.9477 +/- 0.0174 | 0.7563 +/- 0.0011 | 0.1036 +/- 0.0011 |
| 45f | 5000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.1109 +/- 0.0188 | 0.9557 +/- 0.0086 | 0.7925 +/- 0.0033 | 0.0711 +/- 0.0030 |
| 45f | 0 | ablation: zero-shot (validation-chosen det95) | zero-shot | 0.2455 +/- 0.0074 | 0.9473 +/- 0.0015 | 0.7367 +/- 0.0015 | 0.1093 +/- 0.0017 |
| 41f | 1000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.2549 +/- 0.0452 | 0.9516 +/- 0.0165 | 0.7535 +/- 0.0043 | 0.0812 +/- 0.0044 |
| 41f | 5000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.2308 +/- 0.0106 | 0.9542 +/- 0.0033 | 0.7836 +/- 0.0014 | 0.0533 +/- 0.0011 |
| 41f | 0 | ablation: zero-shot (validation-chosen det95) | zero-shot | 0.2475 +/- 0.0007 | 0.9511 +/- 0.0012 | 0.7390 +/- 0.0013 | 0.0900 +/- 0.0012 |
| 38f | 1000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.2704 +/- 0.0534 | 0.9571 +/- 0.0184 | 0.7529 +/- 0.0043 | 0.0815 +/- 0.0042 |
| 38f | 5000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.2281 +/- 0.0125 | 0.9527 +/- 0.0036 | 0.7837 +/- 0.0027 | 0.0528 +/- 0.0025 |
| 38f | 0 | ablation: zero-shot (validation-chosen det95) | zero-shot | 0.2473 +/- 0.0026 | 0.9518 +/- 0.0011 | 0.7381 +/- 0.0014 | 0.0908 +/- 0.0012 |
