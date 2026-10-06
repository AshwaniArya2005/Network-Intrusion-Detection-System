# Headline tables (XGBoost): 5-seed official and pooled metrics, operating points, accuracy against the ceiling, pools side by side, tuned against default

Merged in the Task 7 cleanup from the per-table files named below. Each section is the original file with every line unchanged except that its headings are demoted by two levels; nothing was added to or removed from any table or caveat. The generation scripts still write the original per-table names if re-run.

## Source: headline_summary.md

### Headline metrics, mean +/- std over seeds [42, 43, 44, 45, 46] (ddof=1)

A seed changes the model seed and the train/validation split (and the train/test split on the pooled random protocol); the official test file is fixed. Scheme `current`, whole-pool tier.

| metric | 40 features, official | 40 features, pooled_random | 48 features, official | 48 features, pooled_random |
|---|---|---|---|---|
| accuracy | 0.7427 +/- 0.0009 | 0.8305 +/- 0.0009 | 0.7401 +/- 0.0020 | 0.8493 +/- 0.0010 |
| f1 | 0.7125 +/- 0.0012 | 0.7816 +/- 0.0010 | 0.7130 +/- 0.0016 | 0.7982 +/- 0.0014 |
| detection_rate | 0.9594 +/- 0.0007 | 0.9343 +/- 0.0012 | 0.9681 +/- 0.0025 | 0.9423 +/- 0.0020 |
| false_positive_rate | 0.2853 +/- 0.0013 | 0.1198 +/- 0.0016 | 0.2933 +/- 0.0024 | 0.0981 +/- 0.0011 |
| recall_Normal | 0.7147 +/- 0.0013 | 0.8802 +/- 0.0016 | 0.7067 +/- 0.0024 | 0.9019 +/- 0.0011 |
| normal_to_Fuzzers | 0.2355 +/- 0.0014 | 0.1069 +/- 0.0013 | 0.2475 +/- 0.0021 | 0.0875 +/- 0.0007 |
| roc_auc_macro | 0.9615 +/- 0.0002 | 0.9725 +/- 0.0003 | 0.9606 +/- 0.0006 | 0.9769 +/- 0.0003 |
| pr_auc_macro | 0.7676 +/- 0.0018 | 0.8256 +/- 0.0020 | 0.7528 +/- 0.0021 | 0.8442 +/- 0.0020 |
| roc_auc_attack_vs_normal | 0.9627 +/- 0.0002 | 0.9789 +/- 0.0004 | 0.9642 +/- 0.0009 | 0.9846 +/- 0.0003 |
| ece | 0.0876 +/- 0.0009 | 0.0159 +/- 0.0011 | 0.1093 +/- 0.0024 | 0.0127 +/- 0.0018 |
| brier | 0.3241 +/- 0.0007 | 0.2287 +/- 0.0009 | 0.3438 +/- 0.0011 | 0.2077 +/- 0.0009 |
| fpr_at_95_detection | 0.2588 +/- 0.0019 | 0.1405 +/- 0.0026 | 0.2375 +/- 0.0076 | 0.1085 +/- 0.0042 |
| unknown_detection_rate | 0.2585 +/- 0.0140 | 0.4430 +/- 0.0297 | 0.3770 +/- 0.0104 | 0.4594 +/- 0.0270 |
| false_unknown_alarm_rate | 0.0691 +/- 0.0027 | 0.0507 +/- 0.0020 | 0.0566 +/- 0.0021 | 0.0489 +/- 0.0022 |
| unknown_auroc | 0.7992 +/- 0.0039 | 0.8661 +/- 0.0026 | 0.8358 +/- 0.0032 | 0.8668 +/- 0.0048 |

## Source: headline_full_no_ttl_summary.md

### Headline metrics, mean +/- std over seeds [42, 43, 44, 45, 46] (ddof=1)

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

## Source: headline_tuned_auc_official_summary.md

### Headline metrics, mean +/- std over seeds [42, 43, 44, 45, 46] (ddof=1)

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

## Source: headline_tuned_f1_official_summary.md

### Headline metrics, mean +/- std over seeds [42, 43, 44, 45, 46] (ddof=1)

A seed changes the model seed and the train/validation split (and the train/test split on the pooled random protocol); the official test file is fixed. Scheme `current`, whole-pool tier.

| metric | 40 features, official | 48 features, official |
|---|---|---|
| accuracy | 0.7514 +/- 0.0019 | 0.7591 +/- 0.0012 |
| f1 | 0.7141 +/- 0.0012 | 0.7209 +/- 0.0013 |
| detection_rate | 0.9533 +/- 0.0004 | 0.9618 +/- 0.0010 |
| false_positive_rate | 0.2659 +/- 0.0029 | 0.2591 +/- 0.0019 |
| recall_Normal | 0.7341 +/- 0.0029 | 0.7409 +/- 0.0019 |
| normal_to_Fuzzers | 0.2207 +/- 0.0021 | 0.2193 +/- 0.0014 |
| roc_auc_macro | 0.9614 +/- 0.0001 | 0.9613 +/- 0.0004 |
| pr_auc_macro | 0.7658 +/- 0.0011 | 0.7549 +/- 0.0024 |
| roc_auc_attack_vs_normal | 0.9630 +/- 0.0001 | 0.9663 +/- 0.0007 |
| ece | 0.0644 +/- 0.0013 | 0.0778 +/- 0.0017 |
| brier | 0.3095 +/- 0.0007 | 0.3147 +/- 0.0009 |
| fpr_at_95_detection | 0.2554 +/- 0.0026 | 0.2188 +/- 0.0056 |
| unknown_detection_rate | 0.2590 +/- 0.0159 | 0.4117 +/- 0.0093 |
| false_unknown_alarm_rate | 0.0712 +/- 0.0020 | 0.0511 +/- 0.0015 |
| unknown_auroc | 0.7965 +/- 0.0047 | 0.8368 +/- 0.0044 |

## Source: operating_point_summary.md

### Attack-vs-normal operating points chosen on validation, official test split (mean +/- std over seeds [42, 43, 44, 45, 46])

Thresholds on 1 - P(Normal) are fixed on the validation split (drawn from the training file) and never adjusted; `fpr_gap` = test FPR - validation FPR is the cost of the train/test shift.

| pool | rule | threshold | val detection | val FPR | test detection | test FPR | FPR gap (test - val) |
|---|---|---|---|---|---|---|---|
| 40f | argmax | n/a | 0.9637 +/- 0.0009 | 0.1198 +/- 0.0018 | 0.9594 +/- 0.0007 | 0.2853 +/- 0.0013 | 0.1654 +/- 0.0024 |
| 40f | det95 | 0.5966 +/- 0.0060 | 0.9501 +/- 0.0000 | 0.0999 +/- 0.0013 | 0.9465 +/- 0.0017 | 0.2496 +/- 0.0025 | 0.1497 +/- 0.0025 |
| 40f | fpr10 | 0.5961 +/- 0.0057 | 0.9502 +/- 0.0010 | 0.0998 +/- 0.0001 | 0.9466 +/- 0.0016 | 0.2498 +/- 0.0035 | 0.1500 +/- 0.0035 |
| 48f | argmax | n/a | 0.9691 +/- 0.0007 | 0.0996 +/- 0.0025 | 0.9681 +/- 0.0025 | 0.2933 +/- 0.0024 | 0.1937 +/- 0.0037 |
| 48f | det95 | 0.6168 +/- 0.0114 | 0.9501 +/- 0.0000 | 0.0744 +/- 0.0036 | 0.9526 +/- 0.0015 | 0.2442 +/- 0.0068 | 0.1698 +/- 0.0056 |
| 48f | fpr10 | 0.5169 +/- 0.0095 | 0.9692 +/- 0.0018 | 0.0999 +/- 0.0000 | 0.9710 +/- 0.0025 | 0.2986 +/- 0.0055 | 0.1986 +/- 0.0055 |

## Source: accuracy_three_numbers_40f_48f_45f.md

### Accuracy: official split, pooled split and the best-possible ceiling

Scheme `current`, whole-pool tier; mean +/- std over seeds. The ceiling is what ANY classifier could reach on the pool's raw columns (rows with identical feature vectors can only get one label); it is not a target for the model.

| pool | hyperparameters | official split | pooled random split | ceiling | official - ceiling | pooled - ceiling |
|---|---|---|---|---|---|---|
| 40f | default | 0.7427 +/- 0.0009 | 0.8305 +/- 0.0009 | 0.9117 | -0.1690 | -0.0812 |
| 48f | default | 0.7401 +/- 0.0020 | 0.8493 +/- 0.0010 | 0.9212 | -0.1811 | -0.0719 |
| 45f | default | 0.7367 +/- 0.0015 | 0.8470 +/- 0.0008 | 0.9212 | -0.1845 | -0.0742 |

## Source: accuracy_three_numbers_40f_48f_tuned_f1_auc.md

### Accuracy: official split, pooled split and the best-possible ceiling

Scheme `current`, whole-pool tier; mean +/- std over seeds. The ceiling is what ANY classifier could reach on the pool's raw columns (rows with identical feature vectors can only get one label); it is not a target for the model.

| pool | hyperparameters | official split | pooled random split | ceiling | official - ceiling | pooled - ceiling |
|---|---|---|---|---|---|---|
| 40f | default | 0.7427 +/- 0.0009 | 0.8305 +/- 0.0009 | 0.9117 | -0.1690 | -0.0812 |
| 40f | tuned_f1 | 0.7514 +/- 0.0019 | n/a | 0.9117 | -0.1603 | n/a |
| 40f | tuned_auc | 0.7647 +/- 0.0010 | n/a | 0.9117 | -0.1470 | n/a |
| 48f | default | 0.7401 +/- 0.0020 | 0.8493 +/- 0.0010 | 0.9212 | -0.1811 | -0.0719 |
| 48f | tuned_f1 | 0.7591 +/- 0.0012 | n/a | 0.9212 | -0.1621 | n/a |
| 48f | tuned_auc | 0.7591 +/- 0.0012 | n/a | 0.9212 | -0.1621 | n/a |

## Source: pool_comparison_40f_48f_45f_official.md

### Pools side by side, official split (mean +/- std over seeds)

| metric | 40f | 48f | 45f |
|---|---|---|---|
| accuracy | 0.7427 +/- 0.0009 | 0.7401 +/- 0.0020 | 0.7367 +/- 0.0015 |
| f1 | 0.7125 +/- 0.0012 | 0.7130 +/- 0.0016 | 0.7075 +/- 0.0010 |
| detection_rate | 0.9594 +/- 0.0007 | 0.9681 +/- 0.0025 | 0.9636 +/- 0.0016 |
| false_positive_rate | 0.2853 +/- 0.0013 | 0.2933 +/- 0.0024 | 0.2940 +/- 0.0021 |
| recall_Normal | 0.7147 +/- 0.0013 | 0.7067 +/- 0.0024 | 0.7060 +/- 0.0021 |
| normal_to_Fuzzers | 0.2355 +/- 0.0014 | 0.2475 +/- 0.0021 | 0.2471 +/- 0.0021 |
| roc_auc_macro | 0.9615 +/- 0.0002 | 0.9606 +/- 0.0006 | 0.9589 +/- 0.0003 |
| pr_auc_macro | 0.7676 +/- 0.0018 | 0.7528 +/- 0.0021 | 0.7459 +/- 0.0012 |
| roc_auc_attack_vs_normal | 0.9627 +/- 0.0002 | 0.9642 +/- 0.0009 | 0.9615 +/- 0.0008 |
| ece | 0.0876 +/- 0.0009 | 0.1093 +/- 0.0024 | 0.1093 +/- 0.0017 |
| brier | 0.3241 +/- 0.0007 | 0.3438 +/- 0.0011 | 0.3481 +/- 0.0008 |
| fpr_at_95_detection | 0.2588 +/- 0.0019 | 0.2375 +/- 0.0076 | 0.2523 +/- 0.0067 |
| unknown_detection_rate | 0.2585 +/- 0.0140 | 0.3770 +/- 0.0104 | 0.3833 +/- 0.0163 |
| false_unknown_alarm_rate | 0.0691 +/- 0.0027 | 0.0566 +/- 0.0021 | 0.0577 +/- 0.0022 |
| unknown_auroc | 0.7992 +/- 0.0039 | 0.8358 +/- 0.0032 | 0.8288 +/- 0.0028 |

## Source: pool_comparison_40f_48f_45f_pooled_random.md

### Pools side by side, pooled_random split (mean +/- std over seeds)

| metric | 40f | 48f | 45f |
|---|---|---|---|
| accuracy | 0.8305 +/- 0.0009 | 0.8493 +/- 0.0010 | 0.8470 +/- 0.0008 |
| f1 | 0.7816 +/- 0.0010 | 0.7982 +/- 0.0014 | 0.7928 +/- 0.0013 |
| detection_rate | 0.9343 +/- 0.0012 | 0.9423 +/- 0.0020 | 0.9412 +/- 0.0015 |
| false_positive_rate | 0.1198 +/- 0.0016 | 0.0981 +/- 0.0011 | 0.0972 +/- 0.0016 |
| recall_Normal | 0.8802 +/- 0.0016 | 0.9019 +/- 0.0011 | 0.9028 +/- 0.0016 |
| normal_to_Fuzzers | 0.1069 +/- 0.0013 | 0.0875 +/- 0.0007 | 0.0863 +/- 0.0014 |
| roc_auc_macro | 0.9725 +/- 0.0003 | 0.9769 +/- 0.0003 | 0.9759 +/- 0.0003 |
| pr_auc_macro | 0.8256 +/- 0.0020 | 0.8442 +/- 0.0020 | 0.8370 +/- 0.0016 |
| roc_auc_attack_vs_normal | 0.9789 +/- 0.0004 | 0.9846 +/- 0.0003 | 0.9843 +/- 0.0003 |
| ece | 0.0159 +/- 0.0011 | 0.0127 +/- 0.0018 | 0.0128 +/- 0.0022 |
| brier | 0.2287 +/- 0.0009 | 0.2077 +/- 0.0009 | 0.2114 +/- 0.0006 |
| fpr_at_95_detection | 0.1405 +/- 0.0026 | 0.1085 +/- 0.0042 | 0.1088 +/- 0.0027 |
| unknown_detection_rate | 0.4430 +/- 0.0297 | 0.4594 +/- 0.0270 | 0.4494 +/- 0.0136 |
| false_unknown_alarm_rate | 0.0507 +/- 0.0020 | 0.0489 +/- 0.0022 | 0.0497 +/- 0.0029 |
| unknown_auroc | 0.8661 +/- 0.0026 | 0.8668 +/- 0.0048 | 0.8616 +/- 0.0019 |

## Source: tuned_vs_default.md

### Tuned vs default hyperparameters, official split (mean +/- std over seeds)

Hyperparameters and the class-weight exponent were chosen on the validation split only (pipelines/tune_xgboost.py). `vs default` is the tuned mean minus the default mean.

| pool | hyperparameters | accuracy | f1 | detection_rate | false_positive_rate | normal_to_Fuzzers | roc_auc_attack_vs_normal | ece | unknown_detection_rate | unknown_auroc |
|---|---|---|---|---|---|---|---|---|---|---|
| base | default | 0.7427 +/- 0.0009 | 0.7125 +/- 0.0012 | 0.9594 +/- 0.0007 | 0.2853 +/- 0.0013 | 0.2355 +/- 0.0014 | 0.9627 +/- 0.0002 | 0.0876 +/- 0.0009 | 0.2585 +/- 0.0140 | 0.7992 +/- 0.0039 |
| base | tuned_f1 | 0.7514 +/- 0.0019 (+0.0087) | 0.7141 +/- 0.0012 (+0.0016) | 0.9533 +/- 0.0004 (-0.0061) | 0.2659 +/- 0.0029 (-0.0194) | 0.2207 +/- 0.0021 (-0.0148) | 0.9630 +/- 0.0001 (+0.0003) | 0.0644 +/- 0.0013 (-0.0232) | 0.2590 +/- 0.0159 (+0.0005) | 0.7965 +/- 0.0047 (-0.0027) |
| base | tuned_auc | 0.7647 +/- 0.0010 (+0.0220) | 0.7192 +/- 0.0008 (+0.0067) | 0.9452 +/- 0.0016 (-0.0142) | 0.2395 +/- 0.0016 (-0.0458) | 0.2007 +/- 0.0010 (-0.0348) | 0.9633 +/- 0.0004 (+0.0006) | 0.0521 +/- 0.0010 (-0.0355) | 0.2589 +/- 0.0170 (+0.0004) | 0.7991 +/- 0.0056 (-0.0001) |
| full | default | 0.7401 +/- 0.0020 | 0.7130 +/- 0.0016 | 0.9681 +/- 0.0025 | 0.2933 +/- 0.0024 | 0.2475 +/- 0.0021 | 0.9642 +/- 0.0009 | 0.1093 +/- 0.0024 | 0.3770 +/- 0.0104 | 0.8358 +/- 0.0032 |
| full | tuned_f1 | 0.7591 +/- 0.0012 (+0.0190) | 0.7209 +/- 0.0013 (+0.0079) | 0.9618 +/- 0.0010 (-0.0063) | 0.2591 +/- 0.0019 (-0.0342) | 0.2193 +/- 0.0014 (-0.0282) | 0.9663 +/- 0.0007 (+0.0021) | 0.0778 +/- 0.0017 (-0.0315) | 0.4117 +/- 0.0093 (+0.0347) | 0.8368 +/- 0.0044 (+0.0010) |
| full | tuned_auc | 0.7591 +/- 0.0012 (+0.0190) | 0.7209 +/- 0.0013 (+0.0079) | 0.9618 +/- 0.0010 (-0.0063) | 0.2591 +/- 0.0019 (-0.0342) | 0.2193 +/- 0.0014 (-0.0282) | 0.9663 +/- 0.0007 (+0.0021) | 0.0778 +/- 0.0017 (-0.0315) | 0.4117 +/- 0.0093 (+0.0347) | 0.8368 +/- 0.0044 (+0.0010) |

