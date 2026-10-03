# Headline metrics, mean +/- std over seeds [42, 43, 44, 45, 46] (ddof=1)

A seed changes the model seed and the train/validation split (and the train/test split on the pooled random protocol); the official test file is fixed. Scheme `current`, whole-pool tier.

| metric | 40 features, official | 48 features, official |
|---|---|---|
| accuracy | 0.7647 +/- 0.0010 | 0.7591 +/- 0.0012 |
| f1 | 0.7192 +/- 0.0008 | 0.7209 +/- 0.0013 |
| detection_rate | 0.9452 +/- 0.0016 | 0.9618 +/- 0.0010 |
| false_positive_rate | 0.2395 +/- 0.0016 | 0.2591 +/- 0.0019 |
| recall_Normal | 0.7605 +/- 0.0016 | 0.7409 +/- 0.0019 |
| normal_to_Fuzzers | 0.2007 +/- 0.0010 | 0.2193 +/- 0.0014 |
| roc_auc_macro | 0.9614 +/- 0.0003 | 0.9613 +/- 0.0004 |
| pr_auc_macro | 0.7662 +/- 0.0021 | 0.7549 +/- 0.0024 |
| roc_auc_attack_vs_normal | 0.9633 +/- 0.0004 | 0.9663 +/- 0.0007 |
| ece | 0.0521 +/- 0.0010 | 0.0778 +/- 0.0017 |
| brier | 0.2980 +/- 0.0005 | 0.3147 +/- 0.0009 |
| fpr_at_95_detection | 0.2532 +/- 0.0022 | 0.2188 +/- 0.0056 |
| unknown_detection_rate | 0.2589 +/- 0.0170 | 0.4117 +/- 0.0093 |
| false_unknown_alarm_rate | 0.0697 +/- 0.0034 | 0.0511 +/- 0.0015 |
| unknown_auroc | 0.7991 +/- 0.0056 | 0.8368 +/- 0.0044 |
