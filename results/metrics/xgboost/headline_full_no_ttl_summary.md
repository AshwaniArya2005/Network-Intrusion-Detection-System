# Headline metrics, mean +/- std over seeds [42, 43, 44, 45, 46] (ddof=1)

A seed changes the model seed and the train/validation split (and the train/test split on the pooled random protocol); the official test file is fixed. Scheme `current`, whole-pool tier.

| metric | full_no_ttl, official | full_no_ttl, pooled_random |
|---|---|---|
| accuracy | 0.7367 +/- 0.0015 | 0.8470 +/- 0.0008 |
| f1 | 0.7075 +/- 0.0010 | 0.7928 +/- 0.0013 |
| detection_rate | 0.9636 +/- 0.0016 | 0.9412 +/- 0.0015 |
| false_positive_rate | 0.2940 +/- 0.0021 | 0.0972 +/- 0.0016 |
| recall_Normal | 0.7060 +/- 0.0021 | 0.9028 +/- 0.0016 |
| normal_to_Fuzzers | 0.2471 +/- 0.0021 | 0.0863 +/- 0.0014 |
| roc_auc_macro | 0.9589 +/- 0.0003 | 0.9759 +/- 0.0003 |
| pr_auc_macro | 0.7459 +/- 0.0012 | 0.8370 +/- 0.0016 |
| roc_auc_attack_vs_normal | 0.9615 +/- 0.0008 | 0.9843 +/- 0.0003 |
| ece | 0.1093 +/- 0.0017 | 0.0128 +/- 0.0022 |
| brier | 0.3481 +/- 0.0008 | 0.2114 +/- 0.0006 |
| fpr_at_95_detection | 0.2523 +/- 0.0067 | 0.1088 +/- 0.0027 |
| unknown_detection_rate | 0.3833 +/- 0.0163 | 0.4494 +/- 0.0136 |
| false_unknown_alarm_rate | 0.0577 +/- 0.0022 | 0.0497 +/- 0.0029 |
| unknown_auroc | 0.8288 +/- 0.0028 | 0.8616 +/- 0.0019 |
