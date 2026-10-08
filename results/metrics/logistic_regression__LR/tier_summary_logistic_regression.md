# Feature-tier study Step 1: tier study, logistic_regression (official split, block-grouped validation, mean +/- std over 5 seeds)

Ranked top-N tiers (mutual information on the training split). `det95 FPR` is the 95%-detection operating point chosen on the BLOCK-GROUPED validation split. The pooled random split is a best case: it shares neighbouring flows with its training rows and is optimistic. `noise` / `practical`: macro F1 drop from the full pool within 2 x seed std / within 0.02.

## 48f

| tier | features | macro F1 | accuracy | FPR | det95 FPR | det95 detection | ROC-AUC | ECE | open-set det. | open-set AUROC | pooled macro F1 (best case) | drop F1 | z | noise | practical | ct window / other / TTL cols |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 48 | 48 | 0.5459 +/- 0.0018 | 0.6225 +/- 0.0012 | 0.4072 +/- 0.0025 | 0.3476 +/- 0.0087 | 0.9041 +/- 0.0059 | 0.9036 +/- 0.0015 | 0.1145 +/- 0.0026 | 0.2697 +/- 0.0546 | 0.8538 +/- 0.0075 | 0.6413 +/- 0.0046 | +0.0000 | 0.0 | yes | yes | 7 / 2 / 3 |
| 40 | 40 | 0.5481 +/- 0.0028 | 0.6249 +/- 0.0012 | 0.4067 +/- 0.0009 | 0.3452 +/- 0.0118 | 0.9075 +/- 0.0100 | 0.9049 +/- 0.0020 | 0.1085 +/- 0.0052 | 0.2447 +/- 0.0512 | 0.8507 +/- 0.0064 | 0.6398 +/- 0.0052 | -0.0022 | -1.5 | yes | yes | 7 / 0 / 3 |
| 30 | 30 | 0.5139 +/- 0.0024 | 0.6111 +/- 0.0024 | 0.4171 +/- 0.0036 | 0.3581 +/- 0.0102 | 0.9371 +/- 0.0066 | 0.8688 +/- 0.0045 | 0.0981 +/- 0.0057 | 0.1600 +/- 0.0565 | 0.7896 +/- 0.0067 | 0.6031 +/- 0.0034 | +0.0320 | 24.1 | NO | NO | 2 / 0 / 3 |
| 20 | 20 | 0.4571 +/- 0.0175 | 0.5855 +/- 0.0073 | 0.4219 +/- 0.0087 | 0.3793 +/- 0.0046 | 0.9523 +/- 0.0040 | 0.8610 +/- 0.0051 | 0.0912 +/- 0.0085 | 0.1893 +/- 0.0332 | 0.8177 +/- 0.0049 | 0.4898 +/- 0.0072 | +0.0889 | 11.3 | NO | NO | 0 / 0 / 3 |
| 15 | 15 | 0.4271 +/- 0.0054 | 0.5715 +/- 0.0091 | 0.4252 +/- 0.0146 | 0.3906 +/- 0.0076 | 0.9474 +/- 0.0038 | 0.8221 +/- 0.0048 | 0.0911 +/- 0.0127 | 0.2124 +/- 0.0173 | 0.8152 +/- 0.0053 | 0.4689 +/- 0.0032 | +0.1188 | 46.4 | NO | NO | 0 / 0 / 3 |

