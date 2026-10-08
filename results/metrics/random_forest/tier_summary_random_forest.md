# Feature-tier study Step 1: tier study, random_forest (official split, block-grouped validation, mean +/- std over 5 seeds)

Ranked top-N tiers (mutual information on the training split). `det95 FPR` is the 95%-detection operating point chosen on the BLOCK-GROUPED validation split. The pooled random split is a best case: it shares neighbouring flows with its training rows and is optimistic. `noise` / `practical`: macro F1 drop from the full pool within 2 x seed std / within 0.02.

## 48f

| tier | features | macro F1 | accuracy | FPR | det95 FPR | det95 detection | ROC-AUC | ECE | open-set det. | open-set AUROC | pooled macro F1 (best case) | drop F1 | z | noise | practical | ct window / other / TTL cols |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 48 | 48 | 0.7219 +/- 0.0024 | 0.7623 +/- 0.0053 | 0.2541 +/- 0.0117 | 0.2451 +/- 0.0132 | 0.9724 +/- 0.0014 | 0.9705 +/- 0.0013 | 0.0424 +/- 0.0054 | 0.5352 +/- 0.0556 | 0.8636 +/- 0.0069 | 0.7902 +/- 0.0020 | +0.0000 | 0.0 | yes | yes | 7 / 2 / 3 |
| 40 | 40 | 0.7234 +/- 0.0020 | 0.7633 +/- 0.0055 | 0.2529 +/- 0.0117 | 0.2452 +/- 0.0142 | 0.9728 +/- 0.0009 | 0.9706 +/- 0.0016 | 0.0444 +/- 0.0058 | 0.5000 +/- 0.0494 | 0.8590 +/- 0.0076 | 0.7913 +/- 0.0020 | -0.0015 | -1.1 | yes | yes | 7 / 0 / 3 |
| 30 | 30 | 0.7217 +/- 0.0036 | 0.7633 +/- 0.0058 | 0.2480 +/- 0.0107 | 0.2490 +/- 0.0127 | 0.9498 +/- 0.0045 | 0.9610 +/- 0.0019 | 0.0433 +/- 0.0054 | 0.4711 +/- 0.0555 | 0.8585 +/- 0.0045 | 0.7810 +/- 0.0023 | +0.0001 | 0.1 | yes | yes | 2 / 0 / 3 |
| 20 | 20 | 0.7205 +/- 0.0024 | 0.7686 +/- 0.0050 | 0.2359 +/- 0.0105 | 0.2535 +/- 0.0136 | 0.9569 +/- 0.0033 | 0.9623 +/- 0.0015 | 0.0336 +/- 0.0051 | 0.2398 +/- 0.0510 | 0.7805 +/- 0.0053 | 0.7699 +/- 0.0023 | +0.0013 | 0.9 | yes | yes | 0 / 0 / 3 |
| 15 | 15 | 0.7246 +/- 0.0030 | 0.7723 +/- 0.0070 | 0.2328 +/- 0.0149 | 0.2509 +/- 0.0138 | 0.9576 +/- 0.0032 | 0.9635 +/- 0.0017 | 0.0296 +/- 0.0053 | 0.2071 +/- 0.0602 | 0.7784 +/- 0.0071 | 0.7743 +/- 0.0019 | -0.0027 | -1.6 | yes | yes | 0 / 0 / 3 |

