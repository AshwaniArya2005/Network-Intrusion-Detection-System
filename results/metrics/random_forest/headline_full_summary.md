# Headline metrics, mean +/- std over seeds [42, 43, 44, 45, 46] (ddof=1)

A seed changes the model seed and the train/validation split (and the train/test split on the pooled random protocol); the official test file is fixed. Scheme `current`, whole-pool tier.

| metric | 48 features, official | 48 features, pooled_random |
|---|---|---|
| accuracy | 0.7640 +/- 0.0007 | 0.8500 +/- 0.0012 |
| f1 | 0.7226 +/- 0.0018 | 0.7896 +/- 0.0017 |
| detection_rate | 0.9678 +/- 0.0008 | 0.9088 +/- 0.0020 |
| false_positive_rate | 0.2507 +/- 0.0010 | 0.0654 +/- 0.0013 |
| recall_Normal | 0.7493 +/- 0.0010 | 0.9346 +/- 0.0013 |
| normal_to_Fuzzers | 0.2167 +/- 0.0009 | 0.0572 +/- 0.0014 |
| roc_auc_macro | 0.9615 +/- 0.0001 | 0.9753 +/- 0.0004 |
| pr_auc_macro | 0.7535 +/- 0.0004 | 0.8305 +/- 0.0018 |
| roc_auc_attack_vs_normal | 0.9711 +/- 0.0003 | 0.9831 +/- 0.0004 |
| ece | 0.0414 +/- 0.0016 | 0.0249 +/- 0.0015 |
| brier | 0.2925 +/- 0.0001 | 0.2100 +/- 0.0012 |
| fpr_at_95_detection | 0.1873 +/- 0.0037 | 0.1147 +/- 0.0025 |
| unknown_detection_rate | 0.5733 +/- 0.0127 | 0.6070 +/- 0.0139 |
| false_unknown_alarm_rate | 0.0646 +/- 0.0023 | 0.0500 +/- 0.0020 |
| unknown_auroc | 0.8645 +/- 0.0033 | 0.9008 +/- 0.0016 |
