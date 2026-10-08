# Headline metrics, mean +/- std over seeds [42, 43, 44, 45, 46] (ddof=1)

A seed changes the model seed and the train/validation split (and the train/test split on the pooled random protocol); the official test file is fixed. Scheme `current`, whole-pool tier.

| metric | 48 features, official | 48 features, pooled_random |
|---|---|---|
| accuracy | 0.6226 +/- 0.0014 | 0.7138 +/- 0.0029 |
| f1 | 0.5462 +/- 0.0023 | 0.6428 +/- 0.0043 |
| detection_rate | 0.9753 +/- 0.0013 | 0.9782 +/- 0.0016 |
| false_positive_rate | 0.4089 +/- 0.0008 | 0.2645 +/- 0.0032 |
| recall_Normal | 0.5911 +/- 0.0008 | 0.7355 +/- 0.0032 |
| normal_to_Fuzzers | 0.2872 +/- 0.0008 | 0.1923 +/- 0.0017 |
| roc_auc_macro | 0.9059 +/- 0.0008 | 0.9305 +/- 0.0013 |
| pr_auc_macro | 0.5684 +/- 0.0033 | 0.6602 +/- 0.0043 |
| roc_auc_attack_vs_normal | 0.9038 +/- 0.0004 | 0.9496 +/- 0.0008 |
| ece | 0.1123 +/- 0.0020 | 0.0288 +/- 0.0018 |
| brier | 0.4511 +/- 0.0014 | 0.3476 +/- 0.0023 |
| fpr_at_95_detection | 0.3894 +/- 0.0018 | 0.2188 +/- 0.0020 |
| unknown_detection_rate | 0.2994 +/- 0.0326 | 0.3014 +/- 0.0163 |
| false_unknown_alarm_rate | 0.0480 +/- 0.0027 | 0.0497 +/- 0.0015 |
| unknown_auroc | 0.8548 +/- 0.0046 | 0.8406 +/- 0.0038 |
