# Protocol and headline results

Headline (official split against the optimistic pooled split, 5 seeds), tuning, bootstrap intervals, the accuracy ceiling, per-class headline metrics, label schemes and class overlap, the earlier single-seed run, the shift diagnostics. The declared protocols sit inside the file of the study they declare; the shared rules for every model are in `PROTOCOL.md`. The leakage notes (validation against test, shift AUC with random against block-grouped folds) are in `06_fpr_and_adaptation.md`.

File names mentioned inside this file (for example `task_6_tables.md`, `results/task_5_protocol.md` or `xai_audit_40f_example_failures.csv`) are the `Source:` sections of this file or of one of the other numbered files, or files that were removed in the cleanup and are recoverable from the git tags `pre-cleanup-2026-10` and `pre-lean-2026-10`. Text under a `Source:` heading is the original file, unchanged except that its headings are demoted two levels. Two kinds of file moved after the originals were written: the feature rankings are now in `results/rankings/` and the A/B rating sheet, key and instructions in `results/rating/`.

## Source: shift_conclusion_40f_45f_48f.md

> **Update after Task 2.6.** The shift AUCs below (0.8994 / 0.9293 / 0.9301) use random 5-fold cross-validation. Because neighbouring rows of a file share window values, they
> are inflated: with cross-validation grouped by contiguous row blocks they are 0.814 / 0.836 / 0.837 (seed 42, `leakage_*_shift_auc.csv`). The shift is real (control 0.50) but smaller
> than first reported; the per-group AUC changes of the ablation used random CV and were not re-run. Normal -> Fuzzers results on the official test split are unaffected.

### Step A: what the official-split shift is made of (XGBoost, official split, scheme `current`)

Sources: `shift_normal_*`, `shift_ranking_stability_40f_45f_48f.csv`, `shift_nf_groups_*`, `shift_group_ablation_*`
(`scripts/characterize_shift.py`). NF = Normal flows the default model calls Fuzzers, NN = correctly predicted Normal,
TF = true Fuzzers, all on the official test split.

#### Evidence
1. **The shift is detectable in every pool, and its ranking is stable.** A classifier separating train-Normal from
   official-test-Normal reaches AUC 0.8994 (40 features), 0.9293 (45) and 0.9301 (48), std <= 0.0002 over 5 seeds. SHAP
   importance rankings agree across seeds (Spearman 0.971 / 0.983 / 0.985) and across pools (0.958-0.978). The KS ranking
   is a fixed statistic of the data, so it agrees exactly on shared features; SHAP and KS rankings agree only moderately
   (Spearman 0.67 / 0.55 / 0.50), i.e. the classifier uses feature combinations, not just marginal shifts.
2. **The extra columns add shift.** 40 -> 45/48 features raises the AUC by 0.03. Without the three TTL columns it is
   unchanged (0.9293 vs 0.9301); the connection-count group takes over the top of the SHAP ranking (`ct_dst_src_ltm`).
3. **NF flows resemble Fuzzers on most groups.** Using one group at a time, AUC(NF vs NN) is 0.81-0.98 but AUC(NF vs TF)
   only 0.51-0.74 for volume_size, rate_load, timing, tcp_window_loss, protocol_state and ttl (ttl: 0.945 vs 0.506). The
   exception is connection_counts in the 45/48 pools, where NF differs from BOTH classes (0.905 vs NN, 0.937 vs TF); on
   the 40-feature pool the two connection-count features carry no signal (0.58 / 0.58).
4. **No single group is necessary for the sink.** Removing one group at a time (3 seeds) never lowers the
   Normal -> Fuzzers rate by more than 0.006 (protocol_state, 40 features: 0.2363 -> 0.2300; every other change is within
   +/- 0.002 or an increase). Removing volume_size RAISES it (+0.018 / +0.013) and the FPR (0.286 -> 0.333 / 0.294 -> 0.324).
   The train-vs-test AUC falls only when volume_size (-0.050 / -0.035), timing (-0.034 / -0.020) or connection_counts
   (-0.003 / -0.034) is removed, and stays at 0.85-0.93; rate_load, tcp_window_loss, protocol_state and ttl change it by
   <= 0.003. Groups that turn out to be irrelevant to the shift AUC: rate_load, tcp_window_loss, protocol_state, ttl.

#### What the shift is made of (one paragraph)
The shift between training and official-test Normal traffic is real (AUC 0.90-0.93, controls 0.50) and is spread over
several feature groups at once: size/volume, timing and (when present) connection counts each carry part of it, and
removing one group leaves a classifier that still separates the two Normal populations at AUC 0.85-0.93, so the shift is
encoded redundantly. The Normal flows that are called Fuzzers look like Fuzzers on most groups simultaneously, so no single
group, and in particular not the TTL columns, explains the Normal -> Fuzzers errors: removing any one group does not reduce
them. The cause of the shift (for example a different capture period or host mix in the test file) is **undetermined**: the
data do not identify it, and no feature is named as the cause on correlation alone.

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

## Source: label_scheme_summary.md

### Label scheme comparison (report only; the choice of scheme is the team's)

Compare schemes on the scheme-independent columns below. Macro F1 is NOT comparable across schemes
(it averages over 6, 8, 5 classes for current, none, wide), and
`best_possible_accuracy` rises mechanically with coarser labels: it measures what a merge discards,
not which merge is right. `group_size_share` is the share of attack rows inside a merged group, so a
high value means the scheme lumps most attack traffic together. Ranks: 1 = best.

#### Official train/test split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9607               0.2860             0.7859            0.1193                       2                         1                            0.9117
        none          8          0.9622               0.2895             0.6327            0.0000                       3                         2                            0.9052
        wide          5          0.9598               0.2895             0.8590            0.4848                       1                         2                            0.9690
```

Recall of each ORIGINAL class under each scheme (share of its rows predicted as the label that contains it):
```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.8721                0.9449           0.5437                0.8221               0.7538               0.8596                      0.7768              0.7140
        none                0.3699                0.5072           0.2591                0.8236               0.7553               0.8575                      0.7785              0.7105
        wide                0.9749                0.9710           0.9044                0.9141               0.7476               0.8675                      0.7821              0.7105
```

#### Pooled random split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9320               0.1197             0.7898            0.1248                       2                         2                            0.9117
        none          8          0.9330               0.1204             0.6060            0.0000                       3                         3                            0.9052
        wide          5          0.9375               0.1180             0.8548            0.4887                       1                         1                            0.9690
```

```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.8325                0.9005           0.5264                0.8234               0.7142               0.8993                      0.7417              0.8803
        none                0.2759                0.2793           0.2545                0.8152               0.7109               0.8888                      0.7437              0.8796
        wide                0.8515                0.9449           0.8897                0.9132               0.7188               0.8895                      0.7487              0.8820
```

## Source: label_scheme_summary_48f.md

### Label scheme comparison (report only; the choice of scheme is the team's)

Compare schemes on the scheme-independent columns below. Macro F1 is NOT comparable across schemes
(it averages over 6, 8, 5 classes for current, none, wide), and
`best_possible_accuracy` rises mechanically with coarser labels: it measures what a merge discards,
not which merge is right. `group_size_share` is the share of attack rows inside a merged group, so a
high value means the scheme lumps most attack traffic together. Ranks: 1 = best.

#### Official train/test split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9674               0.2947             0.7645            0.1193                       2                         1                            0.9212
        none          8          0.9688               0.3013             0.6291            0.0000                       3                         3                            0.9134
        wide          5          0.9677               0.2947             0.8521            0.4848                       1                         1                            0.9764
```

Recall of each ORIGINAL class under each scheme (share of its rows predicted as the label that contains it):
```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.7785                0.8319           0.5691                0.8544               0.7343               0.8628                      0.7797              0.7053
        none                0.3539                0.4551           0.3081                0.8518               0.7204               0.8631                      0.7821              0.6987
        wide                0.9315                0.9449           0.9333                0.9410               0.7198               0.8631                      0.7780              0.7053
```

#### Pooled random split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9428               0.0961             0.8061            0.1248                       2                         1                            0.9212
        none          8          0.9407               0.0992             0.5947            0.0000                       3                         3                            0.9134
        wide          5          0.9448               0.0972             0.8586            0.4887                       1                         2                            0.9764
```

```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.8300                0.9084           0.5855                0.8467               0.7281               0.9026                      0.7437              0.9039
        none                0.1429                0.1968           0.3100                0.8376               0.7266               0.8895                      0.7533              0.9008
        wide                0.8144                0.9284           0.9253                0.9272               0.7278               0.8908                      0.7523              0.9028
```

## Source: overlap/pooled_34f/summary.md

### Overlap analysis

Partition: pooled; 255988 known-class rows (duplicates kept); 34 features (base 34): dur, proto, service, state, spkts, dpkts, sbytes, dbytes, rate, sload, dload, sloss, dloss, sinpkt, dinpkt, sjit, djit, swin, dwin, stcpb, dtcpb, tcprtt, synack, ackdat, smean, dmean, trans_depth, response_body_len, ct_src_dport_ltm, ct_dst_sport_ltm, is_ftp_login, ct_ftp_cmd, ct_flw_http_mthd, is_sm_ips_ports.

#### Best-possible accuracy

```
label_scheme  n_classes  best_possible_accuracy_dups_kept  best_possible_accuracy_pairs_deduped
    original          8                            0.9052                                0.9565
     current          6                            0.9117                                0.9702
        none          8                            0.9052                                0.9565
      binary          2                            0.9903                                0.9971
```

#### Exact twins, label set 'original' (% of rows / % of distinct vectors with a twin in another class)

```
                rows_pct  vectors_pct
Analysis           76.99        69.56
Backdoor           84.89        74.80
DoS                77.75        27.03
Exploits           37.14         5.25
Fuzzers            23.93         8.85
Generic             0.71         8.86
Normal              4.23         0.51
Reconnaissance     33.78        13.39
```

Largest multi-label vector ('original'): label counts {'Analysis': 95, 'Backdoor': 84, 'DoS': 637, 'Exploits': 803, 'Fuzzers': 97, 'Generic': 21, 'Reconnaissance': 104}

#### Exact twins, label set 'current' (% of rows / % of distinct vectors with a twin in another class)

```
                 rows_pct  vectors_pct
Exploits            37.14         5.25
Fuzzers             23.93         8.85
Generic              0.71         8.86
Normal               4.23         0.51
Overlap-Group-1     78.42        23.39
Reconnaissance      33.78        13.39
```

Largest multi-label vector ('current'): label counts {'Exploits': 803, 'Fuzzers': 97, 'Generic': 21, 'Overlap-Group-1': 816, 'Reconnaissance': 104}

#### Exact twins, label set 'none' (% of rows / % of distinct vectors with a twin in another class)

```
                rows_pct  vectors_pct
Analysis           76.99        69.56
Backdoor           84.89        74.80
DoS                77.75        27.03
Exploits           37.14         5.25
Fuzzers            23.93         8.85
Generic             0.71         8.86
Normal              4.23         0.51
Reconnaissance     33.78        13.39
```

Largest multi-label vector ('none'): label counts {'Analysis': 95, 'Backdoor': 84, 'DoS': 637, 'Exploits': 803, 'Fuzzers': 97, 'Generic': 21, 'Reconnaissance': 104}

#### Exact twins, label set 'binary' (% of rows / % of distinct vectors with a twin in another class)

```
   rows_pct  vectors_pct
0      4.23         0.51
1      3.22         0.70
```

Largest multi-label vector ('binary'): label counts {0: 2, 1: 1179}

## Source: overlap/pooled_42f/summary.md

### Overlap analysis

Partition: pooled; 255988 known-class rows (duplicates kept); 42 features (all loaded): dur, proto, service, state, spkts, dpkts, sbytes, dbytes, rate, sttl, dttl, sload, dload, sloss, dloss, sinpkt, dinpkt, sjit, djit, swin, dwin, stcpb, dtcpb, tcprtt, synack, ackdat, smean, dmean, trans_depth, response_body_len, ct_srv_src, ct_state_ttl, ct_dst_ltm, ct_src_dport_ltm, ct_dst_sport_ltm, ct_dst_src_ltm, is_ftp_login, ct_ftp_cmd, ct_flw_http_mthd, ct_src_ltm, ct_srv_dst, is_sm_ips_ports.

#### Best-possible accuracy

```
label_scheme  n_classes  best_possible_accuracy_dups_kept  best_possible_accuracy_pairs_deduped
    original          8                            0.9134                                0.9439
     current          6                            0.9212                                0.9624
        none          8                            0.9134                                0.9439
      binary          2                            0.9974                                0.9973
```

#### Exact twins, label set 'original' (% of rows / % of distinct vectors with a twin in another class)

```
                rows_pct  vectors_pct
Analysis           76.99        77.85
Backdoor           84.89        81.38
DoS                77.41        34.04
Exploits           37.04         7.18
Fuzzers            14.92        10.55
Generic             0.63         4.15
Normal              1.00         0.48
Reconnaissance     16.06        15.73
```

Largest multi-label vector ('original'): label counts {'Analysis': 10, 'Backdoor': 10, 'DoS': 66, 'Exploits': 76, 'Fuzzers': 10, 'Generic': 6, 'Reconnaissance': 10}

#### Exact twins, label set 'current' (% of rows / % of distinct vectors with a twin in another class)

```
                 rows_pct  vectors_pct
Exploits            37.04         7.18
Fuzzers             14.92        10.55
Generic              0.63         4.15
Normal               1.00         0.48
Overlap-Group-1     78.16        29.82
Reconnaissance      16.06        15.73
```

Largest multi-label vector ('current'): label counts {'Exploits': 76, 'Fuzzers': 10, 'Generic': 6, 'Overlap-Group-1': 86, 'Reconnaissance': 10}

#### Exact twins, label set 'none' (% of rows / % of distinct vectors with a twin in another class)

```
                rows_pct  vectors_pct
Analysis           76.99        77.85
Backdoor           84.89        81.38
DoS                77.41        34.04
Exploits           37.04         7.18
Fuzzers            14.92        10.55
Generic             0.63         4.15
Normal              1.00         0.48
Reconnaissance     16.06        15.73
```

Largest multi-label vector ('none'): label counts {'Analysis': 10, 'Backdoor': 10, 'DoS': 66, 'Exploits': 76, 'Fuzzers': 10, 'Generic': 6, 'Reconnaissance': 10}

#### Exact twins, label set 'binary' (% of rows / % of distinct vectors with a twin in another class)

```
   rows_pct  vectors_pct
0      1.00         0.48
1      0.51         0.62
```

Largest multi-label vector ('binary'): label counts {0: 14, 1: 20}

## Source: headline_summary.csv (rendered table: per-class and per-group metrics, official split, 40 and 48 features)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed. `base` = 40 features, `full` = 48 features; five seeds (42-46); the aggregate metrics of the same runs are in the headline tables above.

**The other full metric grids were removed in the cleanup**: the complete headline summaries (all metrics, pooled split, tuned runs, 45-feature ablation), the full method grids of the zero-shot, transductive and leakage-ablation runs, and the full few-shot adaptation grids. Their rows that the documents quote are in the tables of this and the other numbered files; the complete files are in git tag `pre-lean-2026-10` (and `pre-cleanup-2026-10`).

| pool | metric | mean | std | min | max | n_seeds |
|---|---|---|---|---|---|---|
| base | precision_Exploits | 0.7587 | 0.0038 | 0.7537 | 0.7628 | 5 |
| full | precision_Exploits | 0.7488 | 0.0024 | 0.7461 | 0.7518 | 5 |
| base | recall_Exploits | 0.8263 | 0.0018 | 0.8232 | 0.8275 | 5 |
| full | recall_Exploits | 0.8547 | 0.0022 | 0.8526 | 0.858 | 5 |
| base | f1_Exploits | 0.7911 | 0.0015 | 0.7889 | 0.7929 | 5 |
| full | f1_Exploits | 0.7982 | 0.0011 | 0.7969 | 0.7992 | 5 |
| base | precision_Fuzzers | 0.2996 | 0.0008 | 0.2983 | 0.3005 | 5 |
| full | precision_Fuzzers | 0.287 | 0.0044 | 0.2794 | 0.2906 | 5 |
| base | recall_Fuzzers | 0.7479 | 0.0038 | 0.7424 | 0.753 | 5 |
| full | recall_Fuzzers | 0.7317 | 0.0143 | 0.7094 | 0.7482 | 5 |
| base | f1_Fuzzers | 0.4279 | 0.001 | 0.4266 | 0.4289 | 5 |
| full | f1_Fuzzers | 0.4122 | 0.0067 | 0.4009 | 0.4186 | 5 |
| base | precision_Generic | 0.9732 | 0.0023 | 0.9707 | 0.977 | 5 |
| full | precision_Generic | 0.9817 | 0.003 | 0.9784 | 0.9863 | 5 |
| base | recall_Generic | 0.8611 | 0.0027 | 0.8578 | 0.8637 | 5 |
| full | recall_Generic | 0.864 | 0.0019 | 0.8616 | 0.8666 | 5 |
| base | f1_Generic | 0.9137 | 0.0012 | 0.9115 | 0.9145 | 5 |
| full | f1_Generic | 0.9191 | 0.001 | 0.9173 | 0.9199 | 5 |
| base | precision_Normal | 0.9663 | 0.0005 | 0.9655 | 0.9668 | 5 |
| full | precision_Normal | 0.9731 | 0.0021 | 0.9697 | 0.9752 | 5 |
| base | recall_Normal | 0.7147 | 0.0013 | 0.7129 | 0.7162 | 5 |
| full | recall_Normal | 0.7067 | 0.0024 | 0.7045 | 0.7106 | 5 |
| base | f1_Normal | 0.8217 | 0.0008 | 0.8206 | 0.8226 | 5 |
| full | f1_Normal | 0.8188 | 0.002 | 0.8161 | 0.8216 | 5 |
| base | precision_Overlap-Group-1 | 0.4005 | 0.0054 | 0.3924 | 0.4057 | 5 |
| full | precision_Overlap-Group-1 | 0.4132 | 0.0037 | 0.408 | 0.4185 | 5 |
| base | recall_Overlap-Group-1 | 0.656 | 0.0024 | 0.6524 | 0.6585 | 5 |
| full | recall_Overlap-Group-1 | 0.6461 | 0.0043 | 0.6399 | 0.6508 | 5 |
| base | f1_Overlap-Group-1 | 0.4973 | 0.0042 | 0.4911 | 0.5021 | 5 |
| full | f1_Overlap-Group-1 | 0.504 | 0.0038 | 0.4983 | 0.5089 | 5 |
| base | precision_Reconnaissance | 0.8705 | 0.0039 | 0.8673 | 0.8759 | 5 |
| full | precision_Reconnaissance | 0.8728 | 0.0044 | 0.8679 | 0.8773 | 5 |
| base | recall_Reconnaissance | 0.7814 | 0.0029 | 0.778 | 0.7857 | 5 |
| full | recall_Reconnaissance | 0.7833 | 0.0032 | 0.778 | 0.7861 | 5 |
| base | f1_Reconnaissance | 0.8235 | 0.002 | 0.8202 | 0.8252 | 5 |
| full | f1_Reconnaissance | 0.8256 | 0.0033 | 0.8206 | 0.8286 | 5 |
| base | roc_auc_Exploits | 0.9753 | 0.0002 | 0.9751 | 0.9755 | 5 |
| full | roc_auc_Exploits | 0.9786 | 0 | 0.9785 | 0.9786 | 5 |
| base | pr_auc_Exploits | 0.8821 | 0.0006 | 0.8813 | 0.8829 | 5 |
| full | pr_auc_Exploits | 0.8947 | 0.0005 | 0.894 | 0.8955 | 5 |
| base | roc_auc_Fuzzers | 0.8968 | 0.0004 | 0.8962 | 0.8974 | 5 |
| full | roc_auc_Fuzzers | 0.8815 | 0.0028 | 0.8774 | 0.8845 | 5 |
| base | pr_auc_Fuzzers | 0.4388 | 0.0028 | 0.435 | 0.4425 | 5 |
| full | pr_auc_Fuzzers | 0.3473 | 0.0106 | 0.3328 | 0.3581 | 5 |
| base | roc_auc_Generic | 0.9937 | 0.0002 | 0.9935 | 0.9941 | 5 |
| full | roc_auc_Generic | 0.9948 | 0.0002 | 0.9945 | 0.9951 | 5 |
| base | pr_auc_Generic | 0.9624 | 0.0005 | 0.9616 | 0.9629 | 5 |
| full | pr_auc_Generic | 0.9664 | 0.0006 | 0.9656 | 0.967 | 5 |
| base | roc_auc_Normal | 0.9627 | 0.0002 | 0.9624 | 0.963 | 5 |
| full | roc_auc_Normal | 0.9642 | 0.0009 | 0.9628 | 0.965 | 5 |
| base | pr_auc_Normal | 0.976 | 0.0002 | 0.9758 | 0.9762 | 5 |
| full | pr_auc_Normal | 0.9772 | 0.0006 | 0.9762 | 0.9777 | 5 |
| base | roc_auc_Overlap-Group-1 | 0.9511 | 0.0006 | 0.9501 | 0.9518 | 5 |
| full | roc_auc_Overlap-Group-1 | 0.9536 | 0.0004 | 0.9532 | 0.954 | 5 |
| base | pr_auc_Overlap-Group-1 | 0.4539 | 0.0078 | 0.442 | 0.4622 | 5 |
| full | pr_auc_Overlap-Group-1 | 0.4333 | 0.0042 | 0.4273 | 0.4375 | 5 |
| base | roc_auc_Reconnaissance | 0.9894 | 0.0001 | 0.9893 | 0.9896 | 5 |
| full | roc_auc_Reconnaissance | 0.9905 | 0.0002 | 0.9902 | 0.9906 | 5 |
| base | pr_auc_Reconnaissance | 0.8925 | 0.0009 | 0.8909 | 0.8931 | 5 |
| full | pr_auc_Reconnaissance | 0.898 | 0.0008 | 0.897 | 0.8989 | 5 |
| base | recall_Analysis_as_Overlap-Group-1 | 0.8717 | 0.0019 | 0.8699 | 0.8744 | 5 |
| full | recall_Analysis_as_Overlap-Group-1 | 0.7968 | 0.0116 | 0.7808 | 0.8082 | 5 |
| base | recall_Backdoor_as_Overlap-Group-1 | 0.9455 | 0.0103 | 0.9304 | 0.9536 | 5 |
| full | recall_Backdoor_as_Overlap-Group-1 | 0.8586 | 0.0147 | 0.8377 | 0.8725 | 5 |
| base | recall_DoS_as_Overlap-Group-1 | 0.5412 | 0.0018 | 0.539 | 0.5437 | 5 |
| full | recall_DoS_as_Overlap-Group-1 | 0.5639 | 0.0051 | 0.559 | 0.5726 | 5 |
| base | fine_recall_Analysis | 0.8717 | 0.0019 | 0.8699 | 0.8744 | 5 |
| full | fine_recall_Analysis | 0.7968 | 0.0116 | 0.7808 | 0.8082 | 5 |
| base | fine_recall_Backdoor | 0.9455 | 0.0103 | 0.9304 | 0.9536 | 5 |
| full | fine_recall_Backdoor | 0.8586 | 0.0147 | 0.8377 | 0.8725 | 5 |
| base | fine_recall_DoS | 0.5412 | 0.0018 | 0.539 | 0.5437 | 5 |
| full | fine_recall_DoS | 0.5639 | 0.0051 | 0.559 | 0.5726 | 5 |
| base | fine_recall_Exploits | 0.8263 | 0.0018 | 0.8232 | 0.8275 | 5 |
| full | fine_recall_Exploits | 0.8547 | 0.0022 | 0.8526 | 0.858 | 5 |
| base | fine_recall_Fuzzers | 0.7479 | 0.0038 | 0.7424 | 0.753 | 5 |
| full | fine_recall_Fuzzers | 0.7317 | 0.0143 | 0.7094 | 0.7482 | 5 |
| base | fine_recall_Generic | 0.8611 | 0.0027 | 0.8578 | 0.8637 | 5 |
| full | fine_recall_Generic | 0.864 | 0.0019 | 0.8616 | 0.8666 | 5 |
| base | fine_recall_Reconnaissance | 0.7814 | 0.0029 | 0.778 | 0.7857 | 5 |
| full | fine_recall_Reconnaissance | 0.7833 | 0.0032 | 0.778 | 0.7861 | 5 |
| base | fine_recall_Normal | 0.7147 | 0.0013 | 0.7129 | 0.7162 | 5 |
| full | fine_recall_Normal | 0.7067 | 0.0024 | 0.7045 | 0.7106 | 5 |
| base | fine_recall_macro | 0.7862 | 0.0015 | 0.7846 | 0.7879 | 5 |
| full | fine_recall_macro | 0.77 | 0.0035 | 0.7644 | 0.7739 | 5 |
| base | group_size_share | 0.1193 | 0 | 0.1193 | 0.1193 | 5 |
| full | group_size_share | 0.1193 | 0 | 0.1193 | 0.1193 | 5 |
| base | normal_to_Exploits | 0.0199 | 0.0011 | 0.0187 | 0.0211 | 5 |
| full | normal_to_Exploits | 0.0198 | 0.0007 | 0.0187 | 0.0204 | 5 |
| base | normal_to_Fuzzers | 0.2355 | 0.0014 | 0.2337 | 0.2371 | 5 |
| full | normal_to_Fuzzers | 0.2475 | 0.0021 | 0.2443 | 0.2498 | 5 |
| base | normal_to_Generic | 0.0008 | 0.0001 | 0.0006 | 0.0009 | 5 |
| full | normal_to_Generic | 0.0002 | 0 | 0.0002 | 0.0002 | 5 |
| base | normal_to_Normal | 0.7147 | 0.0013 | 0.7129 | 0.7162 | 5 |
| full | normal_to_Normal | 0.7067 | 0.0024 | 0.7045 | 0.7106 | 5 |
| base | normal_to_Overlap-Group-1 | 0.0288 | 0.0014 | 0.0272 | 0.0308 | 5 |
| full | normal_to_Overlap-Group-1 | 0.0256 | 0.0009 | 0.0245 | 0.0269 | 5 |
| base | normal_to_Reconnaissance | 0.0002 | 0.0001 | 0.0002 | 0.0004 | 5 |
| full | normal_to_Reconnaissance | 0.0002 | 0.0001 | 0.0001 | 0.0002 | 5 |

## Source: methods_zero_shot_b1_40f_summary.csv (rendered table: label-scheme metrics of the flat and hierarchical models, 40 features, official split)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed. Only the rows and metrics that the label-scheme comparison quotes are rendered (flat default, hierarchical default, hierarchical with stage 1 tuned; fine-recall macro, false-positive rate, detection rate, group size share); five seeds (42-46). The full method grids were removed (see above).

| method | access | metric | mean | std | min | max | n_seeds |
|---|---|---|---|---|---|---|---|
| flat_default | zero-shot | detection_rate | 0.9594 | 0.0007 | 0.9584 | 0.96 | 5 |
| hier_default | zero-shot | detection_rate | 0.9351 | 0.0005 | 0.9343 | 0.9356 | 5 |
| hier_stage1_tuned | zero-shot | detection_rate | 0.9332 | 0.0008 | 0.9318 | 0.9339 | 5 |
| flat_default | zero-shot | false_positive_rate | 0.2853 | 0.0013 | 0.2838 | 0.2871 | 5 |
| hier_default | zero-shot | false_positive_rate | 0.2137 | 0.0021 | 0.2115 | 0.2168 | 5 |
| hier_stage1_tuned | zero-shot | false_positive_rate | 0.2124 | 0.0021 | 0.2088 | 0.2138 | 5 |
| flat_default | zero-shot | fine_recall_macro | 0.7862 | 0.0015 | 0.7846 | 0.7879 | 5 |
| hier_default | zero-shot | fine_recall_macro | 0.6284 | 0.0034 | 0.6241 | 0.6314 | 5 |
| hier_stage1_tuned | zero-shot | fine_recall_macro | 0.6279 | 0.0036 | 0.6231 | 0.6316 | 5 |
| flat_default | zero-shot | group_size_share | 0.1193 | 0 | 0.1193 | 0.1193 | 5 |
| hier_default | zero-shot | group_size_share | 0 | 0 | 0 | 0 | 5 |
| hier_stage1_tuned | zero-shot | group_size_share | 0 | 0 | 0 | 0 | 5 |

## Source: bootstrap_ci_40f_48f_45f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| model | metric | estimate | ci_low | ci_high |
|---|---|---|---|---|
| 40f | accuracy | 0.7413 | 0.7377 | 0.7448 |
| 40f | f1 | 0.7111 | 0.7069 | 0.7155 |
| 40f | detection_rate | 0.9597 | 0.957 | 0.9622 |
| 40f | false_positive_rate | 0.2871 | 0.2828 | 0.2916 |
| 40f | normal_to_Fuzzers | 0.2367 | 0.2325 | 0.241 |
| 40f | unknown_detection_rate | 0.2508 | 0.2299 | 0.2735 |
| 48f | accuracy | 0.7397 | 0.7359 | 0.7431 |
| 48f | f1 | 0.7111 | 0.7069 | 0.7156 |
| 48f | detection_rate | 0.9675 | 0.9648 | 0.9699 |
| 48f | false_positive_rate | 0.2926 | 0.2878 | 0.2972 |
| 48f | normal_to_Fuzzers | 0.2467 | 0.2423 | 0.2512 |
| 48f | unknown_detection_rate | 0.3878 | 0.3657 | 0.4118 |
| 45f | accuracy | 0.7372 | 0.7337 | 0.7408 |
| 45f | f1 | 0.7081 | 0.7034 | 0.7127 |
| 45f | detection_rate | 0.9619 | 0.9592 | 0.9644 |
| 45f | false_positive_rate | 0.2932 | 0.2884 | 0.2978 |
| 45f | normal_to_Fuzzers | 0.2458 | 0.2416 | 0.2501 |
| 45f | unknown_detection_rate | 0.3792 | 0.3565 | 0.402 |

## Source: bootstrap_paired_diff_40f_48f_45f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| comparison | metric | difference | ci_low | ci_high | excludes_zero |
|---|---|---|---|---|---|
| 48f - 40f | accuracy | -0.0016 | -0.004 | 0.0007 | False |
| 48f - 40f | f1 | 0 | -0.0028 | 0.0028 | False |
| 48f - 40f | detection_rate | 0.0079 | 0.0052 | 0.0104 | True |
| 48f - 40f | false_positive_rate | 0.0055 | 0.0025 | 0.0085 | True |
| 48f - 40f | normal_to_Fuzzers | 0.01 | 0.0074 | 0.0127 | True |
| 48f - 40f | unknown_detection_rate | 0.1371 | 0.1063 | 0.1672 | True |
| 45f - 40f | accuracy | -0.0041 | -0.0062 | -0.0017 | True |
| 45f - 40f | f1 | -0.0029 | -0.0052 | -0.0004 | True |
| 45f - 40f | detection_rate | 0.0022 | -0.0003 | 0.0048 | False |
| 45f - 40f | false_positive_rate | 0.0061 | 0.0032 | 0.0089 | True |
| 45f - 40f | normal_to_Fuzzers | 0.0092 | 0.0066 | 0.0118 | True |
| 45f - 40f | unknown_detection_rate | 0.1285 | 0.0965 | 0.1592 | True |
| 45f - 48f | accuracy | -0.0025 | -0.0041 | -0.0009 | True |
| 45f - 48f | f1 | -0.003 | -0.0051 | -0.0008 | True |
| 45f - 48f | detection_rate | -0.0056 | -0.0074 | -0.004 | True |
| 45f - 48f | false_positive_rate | 0.0006 | -0.0012 | 0.0023 | False |
| 45f - 48f | normal_to_Fuzzers | -0.0009 | -0.0025 | 0.0007 | False |
| 45f - 48f | unknown_detection_rate | -0.0086 | -0.0264 | 0.0104 | False |

## Source: experiment_results.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed. Each original column is a row here; each original row is a column.

| metric | 40 / False | 40 / True | 30 / False | 30 / True | 20 / False | 20 / True | 15 / False | 15 / True |
|---|---|---|---|---|---|---|---|---|
| model_type | xgboost | xgboost | xgboost | xgboost | xgboost | xgboost | xgboost | xgboost |
| feature_pool | base | base | base | base | base | base | base | base |
| label_scheme | current | current | current | current | current | current | current | current |
| n_features | 40 | 40 | 30 | 30 | 20 | 20 | 15 | 15 |
| n_train | 81383 | 81383 | 81383 | 81383 | 81383 | 81383 | 81383 | 81383 |
| n_val | 14362 | 14362 | 14362 | 14362 | 14362 | 14362 | 14362 | 14362 |
| n_test | 48055 | 48055 | 48055 | 48055 | 48055 | 48055 | 48055 | 48055 |
| accuracy | 0.7415 | 0.7415 | 0.74 | 0.74 | 0.729 | 0.729 | 0.7292 | 0.7292 |
| precision | 0.6941 | 0.6941 | 0.6934 | 0.6934 | 0.6672 | 0.6672 | 0.6682 | 0.6682 |
| recall | 0.7304 | 0.7304 | 0.7361 | 0.7361 | 0.7328 | 0.7328 | 0.7394 | 0.7394 |
| f1 | 0.6851 | 0.6851 | 0.687 | 0.687 | 0.6717 | 0.6717 | 0.675 | 0.675 |
| precision_Exploits | 0.7621 | 0.7621 | 0.7704 | 0.7704 | 0.7428 | 0.7428 | 0.7483 | 0.7483 |
| recall_Exploits | 0.8399 | 0.8399 | 0.8381 | 0.8381 | 0.8292 | 0.8292 | 0.8268 | 0.8268 |
| f1_Exploits | 0.7991 | 0.7991 | 0.8028 | 0.8028 | 0.7837 | 0.7837 | 0.7856 | 0.7856 |
| precision_Fuzzers | 0.308 | 0.308 | 0.3071 | 0.3071 | 0.3049 | 0.3049 | 0.3044 | 0.3044 |
| recall_Fuzzers | 0.7691 | 0.7691 | 0.7684 | 0.7684 | 0.762 | 0.762 | 0.77 | 0.77 |
| f1_Fuzzers | 0.4398 | 0.4398 | 0.4388 | 0.4388 | 0.4355 | 0.4355 | 0.4363 | 0.4363 |
| precision_Generic | 0.9003 | 0.9003 | 0.8961 | 0.8961 | 0.8904 | 0.8904 | 0.8875 | 0.8875 |
| recall_Generic | 0.6539 | 0.6539 | 0.6722 | 0.6722 | 0.6786 | 0.6786 | 0.6969 | 0.6969 |
| f1_Generic | 0.7576 | 0.7576 | 0.7682 | 0.7682 | 0.7702 | 0.7702 | 0.7807 | 0.7807 |
| precision_Normal | 0.9673 | 0.9673 | 0.9676 | 0.9676 | 0.9733 | 0.9733 | 0.9759 | 0.9759 |
| recall_Normal | 0.7239 | 0.7239 | 0.7199 | 0.7199 | 0.7054 | 0.7054 | 0.7032 | 0.7032 |
| f1_Normal | 0.8281 | 0.8281 | 0.8256 | 0.8256 | 0.8179 | 0.8179 | 0.8174 | 0.8174 |
| precision_Overlap-Group-1 | 0.3874 | 0.3874 | 0.3783 | 0.3783 | 0.3664 | 0.3664 | 0.3731 | 0.3731 |
| recall_Overlap-Group-1 | 0.6095 | 0.6095 | 0.6291 | 0.6291 | 0.6162 | 0.6162 | 0.6344 | 0.6344 |
| f1_Overlap-Group-1 | 0.4738 | 0.4738 | 0.4725 | 0.4725 | 0.4596 | 0.4596 | 0.4699 | 0.4699 |
| precision_Reconnaissance | 0.8397 | 0.8397 | 0.841 | 0.841 | 0.7252 | 0.7252 | 0.7197 | 0.7197 |
| recall_Reconnaissance | 0.7863 | 0.7863 | 0.7888 | 0.7888 | 0.8052 | 0.8052 | 0.8052 | 0.8052 |
| f1_Reconnaissance | 0.8121 | 0.8121 | 0.8141 | 0.8141 | 0.7631 | 0.7631 | 0.76 | 0.76 |
| detection_rate | 0.9552 | 0.9552 | 0.956 | 0.956 | 0.9646 | 0.9646 | 0.9683 | 0.9683 |
| false_positive_rate | 0.2761 | 0.2761 | 0.2801 | 0.2801 | 0.2946 | 0.2946 | 0.2968 | 0.2968 |
| fpr_at_90_detection | 0.1668 | 0.1668 | 0.1615 | 0.1615 | 0.1648 | 0.1648 | 0.1599 | 0.1599 |
| fpr_at_95_detection | 0.2641 | 0.2641 | 0.2644 | 0.2644 | 0.2547 | 0.2547 | 0.2517 | 0.2517 |
| fpr_at_99_detection | 0.3736 | 0.3736 | 0.3712 | 0.3712 | 0.3692 | 0.3692 | 0.3652 | 0.3652 |
| recall_Analysis_as_Overlap-Group-1 | 0.8266 | 0.8266 | 0.839 | 0.839 | 0.9164 | 0.9164 | 0.935 | 0.935 |
| recall_Backdoor_as_Overlap-Group-1 | 0.9403 | 0.9403 | 0.9366 | 0.9366 | 0.9328 | 0.9328 | 0.9291 | 0.9291 |
| recall_DoS_as_Overlap-Group-1 | 0.504 | 0.504 | 0.5293 | 0.5293 | 0.4953 | 0.4953 | 0.5173 | 0.5173 |
| fine_recall_Analysis | 0.8266 | 0.8266 | 0.839 | 0.839 | 0.9164 | 0.9164 | 0.935 | 0.935 |
| fine_recall_Backdoor | 0.9403 | 0.9403 | 0.9366 | 0.9366 | 0.9328 | 0.9328 | 0.9291 | 0.9291 |
| fine_recall_DoS | 0.504 | 0.504 | 0.5293 | 0.5293 | 0.4953 | 0.4953 | 0.5173 | 0.5173 |
| fine_recall_Exploits | 0.8399 | 0.8399 | 0.8381 | 0.8381 | 0.8292 | 0.8292 | 0.8268 | 0.8268 |
| fine_recall_Fuzzers | 0.7691 | 0.7691 | 0.7684 | 0.7684 | 0.762 | 0.762 | 0.77 | 0.77 |
| fine_recall_Generic | 0.6539 | 0.6539 | 0.6722 | 0.6722 | 0.6786 | 0.6786 | 0.6969 | 0.6969 |
| fine_recall_Reconnaissance | 0.7863 | 0.7863 | 0.7888 | 0.7888 | 0.8052 | 0.8052 | 0.8052 | 0.8052 |
| fine_recall_Normal | 0.7239 | 0.7239 | 0.7199 | 0.7199 | 0.7054 | 0.7054 | 0.7032 | 0.7032 |
| fine_recall_macro | 0.7555 | 0.7555 | 0.7615 | 0.7615 | 0.7656 | 0.7656 | 0.7729 | 0.7729 |
| group_size_share | 0.1234 | 0.1234 | 0.1234 | 0.1234 | 0.1234 | 0.1234 | 0.1234 | 0.1234 |
| open_set_threshold |  | 0.494 |  | 0.494 |  | 0.4888 |  | 0.4877 |
| target_false_unknown_rate |  | 0.05 |  | 0.05 |  | 0.05 |  | 0.05 |
| false_unknown_alarm_rate_val |  | 0.0501 |  | 0.0501 |  | 0.0501 |  | 0.0501 |
| unknown_detection_rate |  | 0.2468 |  | 0.2581 |  | 0.1702 |  | 0.1695 |
| false_unknown_alarm_rate |  | 0.0644 |  | 0.0634 |  | 0.0663 |  | 0.0682 |
| n_zero_day_samples |  | 1422 |  | 1422 |  | 1422 |  | 1422 |
| unknown_auroc |  | 0.7999 |  | 0.7932 |  | 0.7561 |  | 0.7531 |

## Source: split_comparison.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed. Each original column is a row here; each original row is a column.

| metric | 40 / official | 40 / pooled_random | 30 / official | 30 / pooled_random | 20 / official | 20 / pooled_random | 15 / official | 15 / pooled_random |
|---|---|---|---|---|---|---|---|---|
| n_train | 81383 | 97784 | 81383 | 97784 | 81383 | 97784 | 81383 | 97784 |
| n_test | 48055 | 28760 | 48055 | 28760 | 48055 | 28760 | 48055 | 28760 |
| accuracy | 0.7415 | 0.8357 | 0.74 | 0.8372 | 0.729 | 0.8241 | 0.7292 | 0.8243 |
| precision | 0.6941 | 0.7569 | 0.6934 | 0.7579 | 0.6672 | 0.736 | 0.6682 | 0.7377 |
| recall | 0.7304 | 0.766 | 0.7361 | 0.7746 | 0.7328 | 0.7612 | 0.7394 | 0.7649 |
| f1 | 0.6851 | 0.7595 | 0.687 | 0.7643 | 0.6717 | 0.7464 | 0.675 | 0.7486 |
| precision_Exploits | 0.7621 | 0.8424 | 0.7704 | 0.8507 | 0.7428 | 0.8226 | 0.7483 | 0.8268 |
| recall_Exploits | 0.8399 | 0.8411 | 0.8381 | 0.8383 | 0.8292 | 0.8284 | 0.8268 | 0.8262 |
| precision_Fuzzers | 0.308 | 0.5982 | 0.3071 | 0.5999 | 0.3049 | 0.5859 | 0.3044 | 0.583 |
| recall_Fuzzers | 0.7691 | 0.7327 | 0.7684 | 0.7387 | 0.762 | 0.7305 | 0.77 | 0.7357 |
| precision_Generic | 0.9003 | 0.7968 | 0.8961 | 0.7963 | 0.8904 | 0.774 | 0.8875 | 0.7819 |
| recall_Generic | 0.6539 | 0.7447 | 0.6722 | 0.7676 | 0.6786 | 0.7512 | 0.6969 | 0.7512 |
| precision_Normal | 0.9673 | 0.9412 | 0.9676 | 0.9424 | 0.9733 | 0.9433 | 0.9759 | 0.9453 |
| recall_Normal | 0.7239 | 0.8885 | 0.7199 | 0.8871 | 0.7054 | 0.8725 | 0.7032 | 0.8703 |
| precision_Overlap-Group-1 | 0.3874 | 0.5387 | 0.3783 | 0.5405 | 0.3664 | 0.5234 | 0.3731 | 0.5268 |
| recall_Overlap-Group-1 | 0.6095 | 0.6145 | 0.6291 | 0.6275 | 0.6162 | 0.6171 | 0.6344 | 0.6379 |
| precision_Reconnaissance | 0.8397 | 0.824 | 0.841 | 0.8175 | 0.7252 | 0.7667 | 0.7197 | 0.7626 |
| recall_Reconnaissance | 0.7863 | 0.7747 | 0.7888 | 0.7884 | 0.8052 | 0.7672 | 0.8052 | 0.7678 |
| detection_rate | 0.9552 | 0.9305 | 0.956 | 0.9321 | 0.9646 | 0.9344 | 0.9683 | 0.9369 |
| false_positive_rate | 0.2761 | 0.1115 | 0.2801 | 0.1129 | 0.2946 | 0.1275 | 0.2968 | 0.1297 |
| fpr_at_90_detection | 0.1668 | 0.0795 | 0.1615 | 0.08 | 0.1648 | 0.093 | 0.1599 | 0.0899 |
| fpr_at_95_detection | 0.2641 | 0.1343 | 0.2644 | 0.1353 | 0.2547 | 0.1473 | 0.2517 | 0.1473 |
| fpr_at_99_detection | 0.3736 | 0.2245 | 0.3712 | 0.2257 | 0.3692 | 0.2328 | 0.3652 | 0.2355 |
| train_rows_Normal | 41560 | 54376 | 41560 | 54376 | 41560 | 54376 | 41560 | 54376 |
| train_rows_Exploits | 16456 | 18189 | 16456 | 18189 | 16456 | 18189 | 16456 | 18189 |
| train_rows_Fuzzers | 11970 | 12452 | 11970 | 12452 | 11970 | 12452 | 11970 | 12452 |
| train_rows_Reconnaissance | 5100 | 5449 | 5100 | 5449 | 5100 | 5449 | 5100 | 5449 |
| train_rows_DoS | 2863 | 3313 | 2863 | 3313 | 2863 | 3313 | 2863 | 3313 |
| train_rows_Generic | 1530 | 2079 | 1530 | 2079 | 1530 | 2079 | 1530 | 2079 |
| train_rows_Analysis | 961 | 986 | 961 | 986 | 961 | 986 | 961 | 986 |
| train_rows_Backdoor | 943 | 940 | 943 | 940 | 943 | 940 | 943 | 940 |
| test_rows_Normal | 31071 | 15993 | 31071 | 15993 | 31071 | 15993 | 31071 | 15993 |
| test_rows_Exploits | 7389 | 5350 | 7389 | 5350 | 7389 | 5350 | 7389 | 5350 |
| test_rows_Fuzzers | 4231 | 3663 | 4231 | 3663 | 4231 | 3663 | 4231 | 3663 |
| test_rows_Reconnaissance | 2012 | 1602 | 2012 | 1602 | 2012 | 1602 | 2012 | 1602 |
| test_rows_DoS | 1504 | 977 | 1504 | 977 | 1504 | 977 | 1504 | 977 |
| test_rows_Generic | 1257 | 611 | 1257 | 611 | 1257 | 611 | 1257 | 611 |
| test_rows_Analysis | 323 | 281 | 323 | 281 | 323 | 281 | 323 | 281 |
| test_rows_Backdoor | 268 | 283 | 268 | 283 | 268 | 283 | 268 | 283 |

## Source: split_summary.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| attack_cat | raw_train_file | raw_test_file | dedup_train_file | dedup_test_file | n_train | n_val | n_test | n_unknown |
|---|---|---|---|---|---|---|---|---|
| Analysis | 2000 | 677 | 1119 | 323 | 961 | 158 | 323 | 0 |
| Backdoor | 1746 | 583 | 1121 | 268 | 943 | 178 | 268 | 0 |
| DoS | 12264 | 4089 | 3369 | 1504 | 2863 | 506 | 1504 | 0 |
| Exploits | 33393 | 11132 | 19360 | 7389 | 16456 | 2904 | 7389 | 0 |
| Fuzzers | 18184 | 6062 | 14082 | 4231 | 11970 | 2112 | 4231 | 0 |
| Generic | 40000 | 18871 | 1800 | 1257 | 1530 | 270 | 1257 | 0 |
| Normal | 56000 | 37000 | 48894 | 31071 | 41560 | 7334 | 31071 | 0 |
| Reconnaissance | 10491 | 3496 | 6000 | 2012 | 5100 | 900 | 2012 | 0 |
| Shellcode | 1133 | 378 | 954 | 303 | 0 | 0 | 0 | 1257 |
| Worms | 130 | 44 | 123 | 42 | 0 | 0 | 0 | 165 |

## Source: feature_selection_baselines_summary.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| feature_set | n_features | ranked_f1 | worst_f1 | random_f1_mean | random_f1_std | random_f1_min | random_f1_max | n_random_draws | ranked_percentile_in_random | ranked_rank_among_draws | ranked_z_vs_random | ranked_beats_random_mean_plus_2std |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 30 | 30 | 0.687 | 0.6184 | 0.6773 | 0.004 | 0.673 | 0.6837 | 10 | 100 | 1 | 2.41 | True |
| 20 | 20 | 0.6717 | 0.5757 | 0.6722 | 0.0052 | 0.6625 | 0.6799 | 10 | 40 | 7 | -0.09 | False |
| 15 | 15 | 0.675 | 0.466 | 0.6587 | 0.024 | 0.5946 | 0.676 | 10 | 80 | 3 | 0.68 | False |

## Source: explanation_stability.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| comparison | config_a | config_b | n_common_features | rank_correlation | cosine_similarity | topk_overlap |
|---|---|---|---|---|---|---|
| nested_feature_sets | xgboost_40 | xgboost_30 | 30 | 0.9969 | 0.9988 | 1 |
| nested_feature_sets | xgboost_40 | xgboost_20 | 20 | 0.9684 | 0.9928 | 0.8182 |
| nested_feature_sets | xgboost_40 | xgboost_15 | 15 | 0.8857 | 0.965 | 1 |
| nested_feature_sets | xgboost_30 | xgboost_20 | 20 | 0.9639 | 0.9908 | 0.8182 |
| nested_feature_sets | xgboost_30 | xgboost_15 | 15 | 0.8821 | 0.9631 | 1 |
| nested_feature_sets | xgboost_20 | xgboost_15 | 15 | 0.8321 | 0.9738 | 0.8182 |
| same_set_different_seed | xgboost_40 | xgboost_40_seed43 | 40 | 0.9942 | 0.9993 | 1 |
| same_set_different_seed | xgboost_40 | xgboost_40_seed44 | 40 | 0.9942 | 0.9993 | 1 |
| same_set_different_seed | xgboost_30 | xgboost_30_seed43 | 30 | 0.9938 | 0.999 | 0.8182 |
| same_set_different_seed | xgboost_30 | xgboost_30_seed44 | 30 | 0.9929 | 0.9991 | 0.8182 |
| same_set_different_seed | xgboost_20 | xgboost_20_seed43 | 20 | 0.994 | 0.9988 | 1 |
| same_set_different_seed | xgboost_20 | xgboost_20_seed44 | 20 | 0.994 | 0.9994 | 1 |
| same_set_different_seed | xgboost_15 | xgboost_15_seed43 | 15 | 0.9821 | 0.9996 | 1 |
| same_set_different_seed | xgboost_15 | xgboost_15_seed44 | 15 | 0.9857 | 0.9994 | 1 |

## Source: open_set_sweep_40.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| threshold | detection_rate | false_alarm_rate |
|---|---|---|
| 0.05 | 0 | 0 |
| 0.1 | 0 | 0 |
| 0.15 | 0 | 0 |
| 0.2 | 0 | 0 |
| 0.25 | 0 | 0 |
| 0.3 | 0.0049 | 0.0004 |
| 0.35 | 0.0218 | 0.0038 |
| 0.4 | 0.0738 | 0.0171 |
| 0.45 | 0.1477 | 0.0376 |
| 0.494 | 0.2468 | 0.0644 |
| 0.5 | 0.2637 | 0.0707 |
| 0.55 | 0.398 | 0.1389 |
| 0.6 | 0.5401 | 0.2063 |
| 0.65 | 0.6723 | 0.2633 |
| 0.7 | 0.7616 | 0.3108 |
| 0.75 | 0.8347 | 0.3516 |
| 0.8 | 0.8812 | 0.3877 |
| 0.85 | 0.9107 | 0.4221 |
| 0.9 | 0.9473 | 0.4602 |
| 0.95 | 0.9817 | 0.5071 |

## Source: overlap_diagnostic_40.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true_fine_grained | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Analysis | 0.1455 | 0 | 0 | 0.0279 | 0.8266 | 0 |
| Backdoor | 0.0448 | 0.0037 | 0 | 0.0112 | 0.9403 | 0 |
| DoS | 0.391 | 0.0605 | 0.0073 | 0.0193 | 0.504 | 0.018 |

## Source: confusion_matrix_40_official.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Exploits | 6240 | 255 | 28 | 147 | 684 | 236 |
| Fuzzers | 97 | 3626 | 9 | 585 | 480 | 13 |
| Generic | 309 | 88 | 2938 | 17 | 65 | 1 |
| Normal | 632 | 7990 | 24 | 24155 | 1024 | 7 |
| Overlap-Group-1 | 676 | 96 | 12 | 36 | 1629 | 28 |
| Reconnaissance | 231 | 33 | 2 | 30 | 255 | 1918 |

## Source: confusion_matrix_40_official_rownorm.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Exploits | 0.8221 | 0.0336 | 0.0037 | 0.0194 | 0.0901 | 0.0311 |
| Fuzzers | 0.0202 | 0.7538 | 0.0019 | 0.1216 | 0.0998 | 0.0027 |
| Generic | 0.0904 | 0.0257 | 0.8596 | 0.005 | 0.019 | 0.0003 |
| Normal | 0.0187 | 0.2362 | 0.0007 | 0.714 | 0.0303 | 0.0002 |
| Overlap-Group-1 | 0.2729 | 0.0388 | 0.0048 | 0.0145 | 0.6577 | 0.0113 |
| Reconnaissance | 0.0936 | 0.0134 | 0.0008 | 0.0122 | 0.1033 | 0.7768 |

## Source: confusion_matrix_40_pooled_random_pooled.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Exploits | 4518 | 150 | 31 | 171 | 458 | 159 |
| Fuzzers | 62 | 2994 | 21 | 732 | 376 | 7 |
| Generic | 67 | 13 | 1367 | 4 | 66 | 3 |
| Normal | 146 | 1844 | 14 | 15093 | 32 | 16 |
| Overlap-Group-1 | 386 | 59 | 20 | 108 | 1256 | 53 |
| Reconnaissance | 159 | 12 | 1 | 10 | 334 | 1482 |

## Source: confusion_matrix_40_pooled_random_rownorm_pooled.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Exploits | 0.8234 | 0.0273 | 0.0056 | 0.0312 | 0.0835 | 0.029 |
| Fuzzers | 0.0148 | 0.7142 | 0.005 | 0.1746 | 0.0897 | 0.0017 |
| Generic | 0.0441 | 0.0086 | 0.8993 | 0.0026 | 0.0434 | 0.002 |
| Normal | 0.0085 | 0.1076 | 0.0008 | 0.8803 | 0.0019 | 0.0009 |
| Overlap-Group-1 | 0.2051 | 0.0313 | 0.0106 | 0.0574 | 0.6674 | 0.0282 |
| Reconnaissance | 0.0796 | 0.006 | 0.0005 | 0.005 | 0.1672 | 0.7417 |

## Source: confusion_matrix_48_official_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Exploits | 6485 | 164 | 28 | 61 | 614 | 238 |
| Fuzzers | 236 | 3532 | 12 | 576 | 443 | 11 |
| Generic | 334 | 35 | 2949 | 7 | 90 | 3 |
| Normal | 637 | 8379 | 6 | 23863 | 942 | 5 |
| Overlap-Group-1 | 644 | 157 | 9 | 25 | 1592 | 50 |
| Reconnaissance | 262 | 20 | 2 | 7 | 253 | 1925 |

## Source: confusion_matrix_48_official_rownorm_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Exploits | 0.8544 | 0.0216 | 0.0037 | 0.008 | 0.0809 | 0.0314 |
| Fuzzers | 0.0491 | 0.7343 | 0.0025 | 0.1198 | 0.0921 | 0.0023 |
| Generic | 0.0977 | 0.0102 | 0.8628 | 0.002 | 0.0263 | 0.0009 |
| Normal | 0.0188 | 0.2477 | 0.0002 | 0.7053 | 0.0278 | 0.0001 |
| Overlap-Group-1 | 0.26 | 0.0634 | 0.0036 | 0.0101 | 0.6427 | 0.0202 |
| Reconnaissance | 0.1061 | 0.0081 | 0.0008 | 0.0028 | 0.1025 | 0.7797 |

## Source: confusion_matrix_48_pooled_random_pooled_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Exploits | 4646 | 90 | 31 | 102 | 458 | 160 |
| Fuzzers | 56 | 3052 | 7 | 694 | 376 | 7 |
| Generic | 65 | 6 | 1372 | 1 | 72 | 4 |
| Normal | 122 | 1477 | 2 | 15498 | 36 | 10 |
| Overlap-Group-1 | 385 | 38 | 20 | 64 | 1323 | 52 |
| Reconnaissance | 167 | 13 | 1 | 2 | 329 | 1486 |

## Source: confusion_matrix_48_pooled_random_rownorm_pooled_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| true | Exploits | Fuzzers | Generic | Normal | Overlap-Group-1 | Reconnaissance |
|---|---|---|---|---|---|---|
| Exploits | 0.8467 | 0.0164 | 0.0056 | 0.0186 | 0.0835 | 0.0292 |
| Fuzzers | 0.0134 | 0.7281 | 0.0017 | 0.1656 | 0.0897 | 0.0017 |
| Generic | 0.0428 | 0.0039 | 0.9026 | 0.0007 | 0.0474 | 0.0026 |
| Normal | 0.0071 | 0.0861 | 0.0001 | 0.9039 | 0.0021 | 0.0006 |
| Overlap-Group-1 | 0.2046 | 0.0202 | 0.0106 | 0.034 | 0.703 | 0.0276 |
| Reconnaissance | 0.0836 | 0.0065 | 0.0005 | 0.001 | 0.1647 | 0.7437 |

## Source: shift_group_ablation_40f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| removed_group | n_removed | n_kept | shift_auc | normal_to_Fuzzers_mean | fpr_mean | accuracy_mean | f1_mean | detection_mean | normal_to_Fuzzers_std | fpr_std | accuracy_std | f1_std | detection_std | shift_auc_vs_all | normal_to_Fuzzers_vs_all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none_removed | 0 | 40 | 0.8993 | 0.2363 | 0.2858 | 0.7424 | 0.7126 | 0.9593 | 0.0009 | 0.0013 | 0.001 | 0.0014 | 0.0008 | 0 | 0 |
| volume_size | 12 | 28 | 0.8489 | 0.2543 | 0.3331 | 0.6982 | 0.6539 | 0.9611 | 0.0014 | 0.0015 | 0 | 0.002 | 0.0008 | -0.0504 | 0.018 |
| rate_load | 3 | 37 | 0.8986 | 0.2355 | 0.2851 | 0.7426 | 0.7122 | 0.9585 | 0.0007 | 0.0023 | 0.0018 | 0.0016 | 0.0005 | -0.0007 | -0.0008 |
| timing | 9 | 31 | 0.8654 | 0.2395 | 0.2925 | 0.7402 | 0.713 | 0.9631 | 0.0007 | 0.0021 | 0.0016 | 0.0017 | 0.0003 | -0.0339 | 0.0032 |
| tcp_window_loss | 6 | 34 | 0.8996 | 0.2377 | 0.2889 | 0.7413 | 0.7127 | 0.9613 | 0.0006 | 0.0013 | 0.0011 | 0.0014 | 0.0003 | 0.0003 | 0.0014 |
| protocol_state | 8 | 32 | 0.8963 | 0.23 | 0.2951 | 0.7359 | 0.701 | 0.9624 | 0.0008 | 0.0006 | 0.0006 | 0.0015 | 0.0008 | -0.003 | -0.0063 |
| connection_counts | 2 | 38 | 0.8961 | 0.2492 | 0.2962 | 0.7346 | 0.7086 | 0.9622 | 0.0016 | 0.0001 | 0.0007 | 0.0009 | 0.0002 | -0.0032 | 0.0129 |

## Source: shift_group_ablation_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| removed_group | n_removed | n_kept | shift_auc | normal_to_Fuzzers_mean | fpr_mean | accuracy_mean | f1_mean | detection_mean | normal_to_Fuzzers_std | fpr_std | accuracy_std | f1_std | detection_std | shift_auc_vs_all | normal_to_Fuzzers_vs_all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none_removed | 0 | 48 | 0.9299 | 0.2483 | 0.2941 | 0.7393 | 0.7122 | 0.9675 | 0.0016 | 0.0015 | 0.0017 | 0.0014 | 0.0033 | 0 | 0 |
| volume_size | 12 | 36 | 0.8948 | 0.2614 | 0.3238 | 0.7035 | 0.6592 | 0.9665 | 0.0017 | 0.0003 | 0.0009 | 0.0017 | 0.0021 | -0.0351 | 0.0131 |
| rate_load | 3 | 45 | 0.9302 | 0.2478 | 0.2941 | 0.7398 | 0.7131 | 0.9678 | 0.0006 | 0.001 | 0.0008 | 0.0005 | 0.0018 | 0.0003 | -0.0005 |
| timing | 9 | 39 | 0.9101 | 0.2524 | 0.2995 | 0.7353 | 0.7101 | 0.9653 | 0.0017 | 0.0018 | 0.001 | 0.0003 | 0.0014 | -0.0198 | 0.0041 |
| tcp_window_loss | 6 | 42 | 0.9305 | 0.2503 | 0.2969 | 0.7375 | 0.7111 | 0.9677 | 0.0002 | 0.0002 | 0.0011 | 0.0016 | 0.0023 | 0.0006 | 0.002 |
| protocol_state | 8 | 40 | 0.9301 | 0.2478 | 0.2985 | 0.7353 | 0.7069 | 0.9653 | 0.0004 | 0.0008 | 0.0007 | 0.0013 | 0.0009 | 0.0002 | -0.0005 |
| ttl | 3 | 45 | 0.9296 | 0.2478 | 0.2947 | 0.7362 | 0.7071 | 0.9628 | 0.0025 | 0.0021 | 0.0017 | 0.0011 | 0.0017 | -0.0003 | -0.0005 |
| connection_counts | 7 | 41 | 0.8963 | 0.2498 | 0.2952 | 0.7384 | 0.7151 | 0.9651 | 0.0021 | 0.0007 | 0.0006 | 0.0004 | 0.0001 | -0.0336 | 0.0015 |

## Source: shift_nf_groups_40f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| feature_set | n_features | auc_NF_vs_NN | auc_NF_vs_TF | resemblance | mean_ks_NF_vs_NN | mean_ks_NF_vs_TF | n_NF | n_NN | n_TF |
|---|---|---|---|---|---|---|---|---|---|
| volume_size | 12 | 0.9749 | 0.7355 | 0.2394 | 0.3658 | 0.0956 | 8007 | 24120 | 4810 |
| rate_load | 3 | 0.964 | 0.7277 | 0.2363 | 0.4542 | 0.1152 | 8007 | 24120 | 4810 |
| timing | 9 | 0.9429 | 0.6679 | 0.275 | 0.4119 | 0.0952 | 8007 | 24120 | 4810 |
| tcp_window_loss | 6 | 0.8417 | 0.5933 | 0.2484 | 0.1272 | 0.0526 | 8007 | 24120 | 4810 |
| protocol_state | 8 | 0.8128 | 0.597 | 0.2157 | 0.1024 | 0.0248 | 8007 | 24120 | 4810 |
| connection_counts | 2 | 0.5813 | 0.5844 | -0.0031 | 0.0402 | 0.1014 | 8007 | 24120 | 4810 |
| all_features | 40 | 0.9926 | 0.8057 | 0.1869 | 0.2781 | 0.0766 | 8007 | 24120 | 4810 |
| top10_shift_ranked | 10 | 0.9833 | 0.7893 | 0.1941 | 0.3986 | 0.1018 | 8007 | 24120 | 4810 |

## Source: shift_nf_groups_45f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| feature_set | n_features | auc_NF_vs_NN | auc_NF_vs_TF | resemblance | mean_ks_NF_vs_NN | mean_ks_NF_vs_TF | n_NF | n_NN | n_TF |
|---|---|---|---|---|---|---|---|---|---|
| volume_size | 12 | 0.9756 | 0.7401 | 0.2355 | 0.3718 | 0.0997 | 8317 | 23913 | 4810 |
| rate_load | 3 | 0.9652 | 0.7284 | 0.2369 | 0.4532 | 0.1113 | 8317 | 23913 | 4810 |
| timing | 9 | 0.9462 | 0.6549 | 0.2913 | 0.4026 | 0.0831 | 8317 | 23913 | 4810 |
| tcp_window_loss | 6 | 0.8472 | 0.5927 | 0.2545 | 0.1397 | 0.0504 | 8317 | 23913 | 4810 |
| protocol_state | 8 | 0.8212 | 0.5996 | 0.2216 | 0.1087 | 0.0246 | 8317 | 23913 | 4810 |
| connection_counts | 7 | 0.9041 | 0.9373 | -0.0332 | 0.1864 | 0.1465 | 8317 | 23913 | 4810 |
| all_features | 45 | 0.9936 | 0.9688 | 0.0248 | 0.2768 | 0.0845 | 8317 | 23913 | 4810 |
| top10_shift_ranked | 10 | 0.9882 | 0.9553 | 0.0329 | 0.4081 | 0.1344 | 8317 | 23913 | 4810 |

## Source: shift_nf_groups_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| feature_set | n_features | auc_NF_vs_NN | auc_NF_vs_TF | resemblance | mean_ks_NF_vs_NN | mean_ks_NF_vs_TF | n_NF | n_NN | n_TF |
|---|---|---|---|---|---|---|---|---|---|
| volume_size | 12 | 0.9762 | 0.7392 | 0.237 | 0.3716 | 0.0997 | 8347 | 23933 | 4810 |
| rate_load | 3 | 0.9646 | 0.7239 | 0.2407 | 0.4537 | 0.1118 | 8347 | 23933 | 4810 |
| timing | 9 | 0.9459 | 0.6515 | 0.2944 | 0.4041 | 0.0839 | 8347 | 23933 | 4810 |
| tcp_window_loss | 6 | 0.8466 | 0.5927 | 0.2538 | 0.1382 | 0.0507 | 8347 | 23933 | 4810 |
| protocol_state | 8 | 0.8209 | 0.5997 | 0.2212 | 0.1078 | 0.0243 | 8347 | 23933 | 4810 |
| ttl | 3 | 0.945 | 0.506 | 0.439 | 0.6663 | 0.0125 | 8347 | 23933 | 4810 |
| connection_counts | 7 | 0.9054 | 0.9374 | -0.032 | 0.1865 | 0.1482 | 8347 | 23933 | 4810 |
| all_features | 48 | 0.9936 | 0.968 | 0.0256 | 0.3011 | 0.0804 | 8347 | 23933 | 4810 |
| top10_shift_ranked | 10 | 0.9898 | 0.9593 | 0.0305 | 0.3776 | 0.1081 | 8347 | 23933 | 4810 |

## Source: shift_normal_features_40f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| feature | group | ks_or_tvd | shap_mean | shap_std | rank_shap | rank_ks |
|---|---|---|---|---|---|---|
| ackdat | timing | 0.2526 | 0.4006 | 0.01957 | 1 | 1 |
| dbytes | volume_size | 0.1868 | 0.37342 | 0.04147 | 2 | 6 |
| service | protocol_state | 0.1053 | 0.25687 | 0.01277 | 3 | 24 |
| byte_ratio | volume_size | 0.1261 | 0.18926 | 0.01233 | 4 | 22 |
| total_bytes | volume_size | 0.1677 | 0.17583 | 0.02586 | 5 | 8 |
| sbytes | volume_size | 0.1293 | 0.16438 | 0.01556 | 6 | 20 |
| sinpkt | timing | 0.1579 | 0.15169 | 0.00845 | 7 | 13 |
| dmean | volume_size | 0.2132 | 0.12958 | 0.0051 | 8 | 3 |
| dinpkt | timing | 0.1463 | 0.1062 | 0.0073 | 9 | 15 |
| smean | volume_size | 0.0763 | 0.09593 | 0.00609 | 10 | 26 |
| dload | rate_load | 0.2442 | 0.09265 | 0.01031 | 11 | 2 |
| tcprtt | timing | 0.2121 | 0.08888 | 0.00483 | 12 | 4 |
| avg_pkt_size | volume_size | 0.111 | 0.087 | 0.00874 | 13 | 23 |
| sload | rate_load | 0.1371 | 0.07165 | 0.00453 | 14 | 16 |
| synack | timing | 0.2113 | 0.06546 | 0.01083 | 15 | 5 |
| ct_src_dport_ltm | connection_counts | 0.0441 | 0.06449 | 0.00424 | 16 | 30 |
| state | protocol_state | 0.0498 | 0.06203 | 0.01352 | 17 | 27 |
| dloss | tcp_window_loss | 0.1638 | 0.06029 | 0.01132 | 18 | 11 |
| pkt_ratio | volume_size | 0.1712 | 0.05713 | 0.01247 | 19 | 7 |
| total_pkts | volume_size | 0.1522 | 0.05508 | 0.01534 | 20 | 14 |
| dpkts | volume_size | 0.1584 | 0.05202 | 0.00681 | 21 | 12 |
| response_body_len | volume_size | 0.0252 | 0.05127 | 0.00276 | 22 | 34 |
| spkts | volume_size | 0.1356 | 0.05112 | 0.02447 | 23 | 19 |
| dur | timing | 0.1368 | 0.04596 | 0.00969 | 24 | 17 |
| djit | timing | 0.096 | 0.03505 | 0.00126 | 25 | 25 |
| dtcpb | tcp_window_loss | 0.0269 | 0.03461 | 0.00424 | 26 | 31 |
| rate | rate_load | 0.1663 | 0.03449 | 0.00365 | 27 | 9 |
| sloss | tcp_window_loss | 0.1264 | 0.03174 | 0.01204 | 28 | 21 |
| sjit | timing | 0.1641 | 0.03052 | 0.00294 | 29 | 10 |
| swin | tcp_window_loss | 0.048 | 0.01638 | 0.00525 | 30 | 29 |
| duration_log | timing | 0.1368 | 0.0138 | 0.00389 | 31 | 17 |
| trans_depth | protocol_state | 0.0154 | 0.01161 | 0.00127 | 32 | 35 |
| stcpb | tcp_window_loss | 0.0269 | 0.0112 | 0.0017 | 33 | 31 |
| proto | protocol_state | 0.0483 | 0.00965 | 0.00158 | 34 | 28 |
| is_ftp_login | protocol_state | 0.0075 | 0.00878 | 0.0014 | 35 | 38 |
| ct_dst_sport_ltm | connection_counts | 0.0085 | 0.00409 | 0.00057 | 36 | 37 |
| is_sm_ips_ports | protocol_state | 0.0074 | 0.00208 | 0.00096 | 37 | 40 |
| ct_flw_http_mthd | protocol_state | 0.0154 | 0.00099 | 0.00036 | 38 | 35 |
| dwin | tcp_window_loss | 0.0264 | 0.00006 | 0.00006 | 39 | 33 |
| ct_ftp_cmd | protocol_state | 0.0075 | 0 | 0 | 40 | 38 |

## Source: shift_normal_features_45f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| feature | group | ks_or_tvd | shap_mean | shap_std | rank_shap | rank_ks |
|---|---|---|---|---|---|---|
| ct_dst_src_ltm | connection_counts | 0.0847 | 0.66653 | 0.00656 | 1 | 28 |
| ackdat | timing | 0.2526 | 0.49874 | 0.00927 | 2 | 1 |
| dbytes | volume_size | 0.1868 | 0.36663 | 0.02072 | 3 | 6 |
| dload | rate_load | 0.2442 | 0.21494 | 0.01804 | 4 | 2 |
| ct_dst_ltm | connection_counts | 0.1054 | 0.1988 | 0.00657 | 5 | 24 |
| byte_ratio | volume_size | 0.1261 | 0.19541 | 0.01862 | 6 | 22 |
| sbytes | volume_size | 0.1293 | 0.16649 | 0.00844 | 7 | 20 |
| ct_srv_src | connection_counts | 0.0268 | 0.15431 | 0.00586 | 8 | 37 |
| total_bytes | volume_size | 0.1677 | 0.14314 | 0.0115 | 9 | 8 |
| dmean | volume_size | 0.2132 | 0.13654 | 0.01319 | 10 | 3 |
| sinpkt | timing | 0.1579 | 0.13455 | 0.00413 | 11 | 13 |
| ct_src_ltm | connection_counts | 0.0997 | 0.13197 | 0.00864 | 12 | 26 |
| ct_srv_dst | connection_counts | 0.0286 | 0.1216 | 0.00427 | 13 | 34 |
| smean | volume_size | 0.0763 | 0.11527 | 0.01103 | 14 | 29 |
| dinpkt | timing | 0.1463 | 0.09863 | 0.00436 | 15 | 15 |
| sload | rate_load | 0.1371 | 0.09593 | 0.00613 | 16 | 16 |
| service | protocol_state | 0.1053 | 0.08723 | 0.00464 | 17 | 25 |
| avg_pkt_size | volume_size | 0.111 | 0.07234 | 0.0083 | 18 | 23 |
| tcprtt | timing | 0.2121 | 0.06682 | 0.00799 | 19 | 4 |
| dpkts | volume_size | 0.1584 | 0.05289 | 0.01007 | 20 | 12 |
| synack | timing | 0.2113 | 0.05196 | 0.00362 | 21 | 5 |
| ct_src_dport_ltm | connection_counts | 0.0441 | 0.05117 | 0.00198 | 22 | 33 |
| pkt_ratio | volume_size | 0.1712 | 0.04885 | 0.00971 | 23 | 7 |
| response_body_len | volume_size | 0.0252 | 0.04589 | 0.00506 | 24 | 39 |
| spkts | volume_size | 0.1356 | 0.04541 | 0.01534 | 25 | 19 |
| dloss | tcp_window_loss | 0.1638 | 0.0448 | 0.00859 | 26 | 11 |
| total_pkts | volume_size | 0.1522 | 0.03993 | 0.00971 | 27 | 14 |
| state | protocol_state | 0.0498 | 0.03864 | 0.0108 | 28 | 30 |
| sloss | tcp_window_loss | 0.1264 | 0.0336 | 0.00865 | 29 | 21 |
| rate | rate_load | 0.1663 | 0.02539 | 0.00205 | 30 | 9 |
| sjit | timing | 0.1641 | 0.02465 | 0.00442 | 31 | 10 |
| djit | timing | 0.096 | 0.02414 | 0.00305 | 32 | 27 |
| dur | timing | 0.1368 | 0.02292 | 0.00462 | 33 | 17 |
| swin | tcp_window_loss | 0.048 | 0.01803 | 0.00397 | 34 | 32 |
| dtcpb | tcp_window_loss | 0.0269 | 0.01591 | 0.00363 | 35 | 35 |
| trans_depth | protocol_state | 0.0154 | 0.00954 | 0.0044 | 36 | 40 |
| duration_log | timing | 0.1368 | 0.00918 | 0.00122 | 37 | 17 |
| is_sm_ips_ports | protocol_state | 0.0074 | 0.00854 | 0.00218 | 38 | 45 |
| stcpb | tcp_window_loss | 0.0269 | 0.00787 | 0.00276 | 39 | 35 |
| ct_flw_http_mthd | protocol_state | 0.0154 | 0.00345 | 0.0006 | 40 | 40 |
| is_ftp_login | protocol_state | 0.0075 | 0.00294 | 0.00096 | 41 | 43 |
| proto | protocol_state | 0.0483 | 0.00281 | 0.00074 | 42 | 31 |
| ct_dst_sport_ltm | connection_counts | 0.0085 | 0.00227 | 0.00029 | 43 | 42 |
| dwin | tcp_window_loss | 0.0264 | 0.00005 | 0.00007 | 44 | 38 |
| ct_ftp_cmd | protocol_state | 0.0075 | 0 | 0 | 45 | 43 |

## Source: shift_normal_features_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| feature | group | ks_or_tvd | shap_mean | shap_std | rank_shap | rank_ks |
|---|---|---|---|---|---|---|
| ct_dst_src_ltm | connection_counts | 0.0847 | 0.68493 | 0.01222 | 1 | 31 |
| sttl | ttl | 0.271 | 0.49825 | 0.02466 | 2 | 1 |
| ackdat | timing | 0.2526 | 0.31833 | 0.01512 | 3 | 3 |
| dbytes | volume_size | 0.1868 | 0.30822 | 0.02958 | 4 | 9 |
| ct_dst_ltm | connection_counts | 0.1054 | 0.23974 | 0.00501 | 5 | 27 |
| byte_ratio | volume_size | 0.1261 | 0.16867 | 0.02282 | 6 | 25 |
| sbytes | volume_size | 0.1293 | 0.16619 | 0.01055 | 7 | 23 |
| ct_srv_src | connection_counts | 0.0268 | 0.15272 | 0.00958 | 8 | 40 |
| ct_src_ltm | connection_counts | 0.0997 | 0.14652 | 0.00609 | 9 | 29 |
| sinpkt | timing | 0.1579 | 0.13524 | 0.00521 | 10 | 16 |
| dmean | volume_size | 0.2132 | 0.13321 | 0.01365 | 11 | 6 |
| dload | rate_load | 0.2442 | 0.13109 | 0.00956 | 12 | 4 |
| ct_srv_dst | connection_counts | 0.0286 | 0.12845 | 0.00793 | 13 | 37 |
| total_bytes | volume_size | 0.1677 | 0.12749 | 0.01123 | 14 | 11 |
| smean | volume_size | 0.0763 | 0.10476 | 0.00924 | 15 | 32 |
| dinpkt | timing | 0.1463 | 0.09622 | 0.00597 | 16 | 18 |
| tcprtt | timing | 0.2121 | 0.08117 | 0.01245 | 17 | 7 |
| service | protocol_state | 0.1053 | 0.07243 | 0.01292 | 18 | 28 |
| avg_pkt_size | volume_size | 0.111 | 0.06249 | 0.00285 | 19 | 26 |
| ct_state_ttl | ttl | 0.2649 | 0.06134 | 0.01129 | 20 | 2 |
| ct_src_dport_ltm | connection_counts | 0.0441 | 0.05958 | 0.00413 | 21 | 36 |
| dpkts | volume_size | 0.1584 | 0.05361 | 0.00943 | 22 | 15 |
| synack | timing | 0.2113 | 0.04987 | 0.00811 | 23 | 8 |
| total_pkts | volume_size | 0.1522 | 0.04973 | 0.00395 | 24 | 17 |
| pkt_ratio | volume_size | 0.1712 | 0.04456 | 0.01169 | 25 | 10 |
| response_body_len | volume_size | 0.0252 | 0.04323 | 0.00383 | 26 | 42 |
| spkts | volume_size | 0.1356 | 0.03982 | 0.00508 | 27 | 22 |
| sload | rate_load | 0.1371 | 0.03869 | 0.00724 | 28 | 19 |
| dloss | tcp_window_loss | 0.1638 | 0.03768 | 0.00744 | 29 | 14 |
| sloss | tcp_window_loss | 0.1264 | 0.03132 | 0.01081 | 30 | 24 |
| state | protocol_state | 0.0498 | 0.02849 | 0.00586 | 31 | 33 |
| rate | rate_load | 0.1663 | 0.02843 | 0.00302 | 32 | 12 |
| dur | timing | 0.1368 | 0.02579 | 0.00397 | 33 | 20 |
| djit | timing | 0.096 | 0.02404 | 0.00391 | 34 | 30 |
| sjit | timing | 0.1641 | 0.02273 | 0.00161 | 35 | 13 |
| dtcpb | tcp_window_loss | 0.0269 | 0.02201 | 0.00375 | 36 | 38 |
| dttl | ttl | 0.2159 | 0.01271 | 0.00692 | 37 | 5 |
| duration_log | timing | 0.1368 | 0.01208 | 0.00248 | 38 | 20 |
| trans_depth | protocol_state | 0.0154 | 0.00711 | 0.00261 | 39 | 43 |
| stcpb | tcp_window_loss | 0.0269 | 0.00693 | 0.00138 | 40 | 38 |
| is_sm_ips_ports | protocol_state | 0.0074 | 0.00672 | 0.00097 | 41 | 48 |
| is_ftp_login | protocol_state | 0.0075 | 0.00343 | 0.00151 | 42 | 46 |
| ct_flw_http_mthd | protocol_state | 0.0154 | 0.00341 | 0.00084 | 43 | 43 |
| proto | protocol_state | 0.0483 | 0.00215 | 0.00104 | 44 | 34 |
| ct_dst_sport_ltm | connection_counts | 0.0085 | 0.00205 | 0.00036 | 45 | 45 |
| swin | tcp_window_loss | 0.048 | 0.00086 | 0.00087 | 46 | 35 |
| dwin | tcp_window_loss | 0.0264 | 0.00002 | 0.00005 | 47 | 41 |
| ct_ftp_cmd | protocol_state | 0.0075 | 0 | 0 | 48 | 46 |

## Source: shift_normal_summary_40f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| metric | value |
|---|---|
| pool | 40f |
| n_features | 40 |
| n_seeds | 5 |
| auc_mean | 0.8994 |
| auc_std | 0.0001 |
| shap_rank_spearman_across_seeds | 0.9709 |
| shap_top10_jaccard_across_seeds | 0.8212 |
| shap_vs_ks_rank_spearman | 0.6659 |
| top5_shap_features | ackdat, dbytes, service, byte_ratio, total_bytes |
| top5_ks_features | ackdat, dload, dmean, tcprtt, synack |

## Source: shift_normal_summary_45f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| metric | value |
|---|---|
| pool | 45f |
| n_features | 45 |
| n_seeds | 5 |
| auc_mean | 0.9293 |
| auc_std | 0.0002 |
| shap_rank_spearman_across_seeds | 0.9831 |
| shap_top10_jaccard_across_seeds | 0.7909 |
| shap_vs_ks_rank_spearman | 0.552 |
| top5_shap_features | ct_dst_src_ltm, ackdat, dbytes, dload, ct_dst_ltm |
| top5_ks_features | ackdat, dload, dmean, tcprtt, synack |

## Source: shift_normal_summary_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| metric | value |
|---|---|
| pool | 48f |
| n_features | 48 |
| n_seeds | 5 |
| auc_mean | 0.9301 |
| auc_std | 0.0002 |
| shap_rank_spearman_across_seeds | 0.9846 |
| shap_top10_jaccard_across_seeds | 0.7909 |
| shap_vs_ks_rank_spearman | 0.5022 |
| top5_shap_features | ct_dst_src_ltm, sttl, ackdat, dbytes, ct_dst_ltm |
| top5_ks_features | sttl, ct_state_ttl, ackdat, dload, dttl |

## Source: shift_ranking_stability_40f_45f_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| a | b | n_shared_features | spearman | top10_jaccard | importance |
|---|---|---|---|---|---|
| 40f | 45f | 40 | 0.9645 | 0.8182 | shap |
| 40f | 48f | 40 | 0.9578 | 0.8182 | shap |
| 45f | 48f | 45 | 0.9776 | 0.6667 | shap |
| 40f | 45f | 40 | 1 | 1 | ks |
| 40f | 48f | 40 | 1 | 1 | ks |
| 45f | 48f | 45 | 1 | 1 | ks |

## Source: tuned_params_40f.json (rendered table)

Rendered from the JSON file of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); every key and value is listed.

| key | value |
|---|---|
| pool | base |
| n_features | 40 |
| n_trials | 40 |
| seed | 42 |
| early_stopping | 30 rounds on validation mlogloss, max 1000 trees |
| default_reference.best_iteration | 275 |
| default_reference.val_macro_f1 | 0.7966 |
| default_reference.val_attack_auc | 0.984 |
| f1.params.max_depth | 10 |
| f1.params.learning_rate | 0.0327 |
| f1.params.min_child_weight | 1 |
| f1.params.subsample | 0.7484 |
| f1.params.colsample_bytree | 0.9149 |
| f1.params.reg_lambda | 9.8591 |
| f1.params.reg_alpha | 1 |
| f1.params.n_estimators | 456 |
| f1.class_weight_power | 0.3171 |
| f1.val_macro_f1 | 0.7981 |
| f1.val_attack_auc | 0.9841 |
| f1.trial | 26 |
| auc.params.max_depth | 9 |
| auc.params.learning_rate | 0.17187 |
| auc.params.min_child_weight | 10 |
| auc.params.subsample | 0.9883 |
| auc.params.colsample_bytree | 0.9466 |
| auc.params.reg_lambda | 8.83054 |
| auc.params.reg_alpha | 0.1 |
| auc.params.n_estimators | 148 |
| auc.class_weight_power | 0.1946 |
| auc.val_macro_f1 | 0.7953 |
| auc.val_attack_auc | 0.9842 |
| auc.trial | 4 |

## Source: tuned_params_48f.json (rendered table)

Rendered from the JSON file of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); every key and value is listed.

| key | value |
|---|---|
| pool | full |
| n_features | 48 |
| n_trials | 40 |
| seed | 42 |
| early_stopping | 30 rounds on validation mlogloss, max 1000 trees |
| default_reference.best_iteration | 272 |
| default_reference.val_macro_f1 | 0.8123 |
| default_reference.val_attack_auc | 0.9875 |
| f1.params.max_depth | 9 |
| f1.params.learning_rate | 0.17187 |
| f1.params.min_child_weight | 10 |
| f1.params.subsample | 0.9883 |
| f1.params.colsample_bytree | 0.9466 |
| f1.params.reg_lambda | 8.83054 |
| f1.params.reg_alpha | 0.1 |
| f1.params.n_estimators | 161 |
| f1.class_weight_power | 0.1946 |
| f1.val_macro_f1 | 0.8137 |
| f1.val_attack_auc | 0.9879 |
| f1.trial | 4 |
| auc.params.max_depth | 9 |
| auc.params.learning_rate | 0.17187 |
| auc.params.min_child_weight | 10 |
| auc.params.subsample | 0.9883 |
| auc.params.colsample_bytree | 0.9466 |
| auc.params.reg_lambda | 8.83054 |
| auc.params.reg_alpha | 0.1 |
| auc.params.n_estimators | 161 |
| auc.class_weight_power | 0.1946 |
| auc.val_macro_f1 | 0.8137 |
| auc.val_attack_auc | 0.9879 |
| auc.trial | 4 |

## Source: tuned_params_blockval_40f.json (rendered table)

Rendered from the JSON file of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); every key and value is listed.

| key | value |
|---|---|
| pool | base |
| n_features | 40 |
| n_trials | 40 |
| seed | 42 |
| early_stopping | 30 rounds on validation mlogloss, max 1000 trees |
| default_reference.best_iteration | 177 |
| default_reference.val_macro_f1 | 0.758 |
| default_reference.val_attack_auc | 0.9624 |
| f1.params.max_depth | 3 |
| f1.params.learning_rate | 0.13694 |
| f1.params.min_child_weight | 10 |
| f1.params.subsample | 0.8908 |
| f1.params.colsample_bytree | 0.8843 |
| f1.params.reg_lambda | 3.04845 |
| f1.params.reg_alpha | 1 |
| f1.params.n_estimators | 904 |
| f1.class_weight_power | 0.2302 |
| f1.val_macro_f1 | 0.7614 |
| f1.val_attack_auc | 0.9627 |
| f1.trial | 25 |
| auc.params.max_depth | 6 |
| auc.params.learning_rate | 0.13867 |
| auc.params.min_child_weight | 50 |
| auc.params.subsample | 0.8821 |
| auc.params.colsample_bytree | 0.8904 |
| auc.params.reg_lambda | 12.04243 |
| auc.params.reg_alpha | 1 |
| auc.params.n_estimators | 367 |
| auc.class_weight_power | 0.1398 |
| auc.val_macro_f1 | 0.7583 |
| auc.val_attack_auc | 0.963 |
| auc.trial | 9 |

## Source: tuned_params_blockval_45f.json (rendered table)

Rendered from the JSON file of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); every key and value is listed.

| key | value |
|---|---|
| pool | full_no_ttl |
| n_features | 45 |
| n_trials | 40 |
| seed | 42 |
| early_stopping | 30 rounds on validation mlogloss, max 1000 trees |
| default_reference.best_iteration | 175 |
| default_reference.val_macro_f1 | 0.7653 |
| default_reference.val_attack_auc | 0.9688 |
| f1.params.max_depth | 7 |
| f1.params.learning_rate | 0.17187 |
| f1.params.min_child_weight | 50 |
| f1.params.subsample | 0.9883 |
| f1.params.colsample_bytree | 0.9466 |
| f1.params.reg_lambda | 42.02234 |
| f1.params.reg_alpha | 0.1 |
| f1.params.n_estimators | 189 |
| f1.class_weight_power | 0.1946 |
| f1.val_macro_f1 | 0.7677 |
| f1.val_attack_auc | 0.9688 |
| f1.trial | 4 |
| auc.params.max_depth | 5 |
| auc.params.learning_rate | 0.08114 |
| auc.params.min_child_weight | 50 |
| auc.params.subsample | 0.8509 |
| auc.params.colsample_bytree | 0.792 |
| auc.params.reg_lambda | 25.41557 |
| auc.params.reg_alpha | 1 |
| auc.params.n_estimators | 544 |
| auc.class_weight_power | 0.4158 |
| auc.val_macro_f1 | 0.7633 |
| auc.val_attack_auc | 0.9689 |
| auc.trial | 19 |

## Source: tuned_params_blockval_48f.json (rendered table)

Rendered from the JSON file of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); every key and value is listed.

| key | value |
|---|---|
| pool | full |
| n_features | 48 |
| n_trials | 40 |
| seed | 42 |
| early_stopping | 30 rounds on validation mlogloss, max 1000 trees |
| default_reference.best_iteration | 175 |
| default_reference.val_macro_f1 | 0.7694 |
| default_reference.val_attack_auc | 0.9688 |
| f1.params.max_depth | 7 |
| f1.params.learning_rate | 0.17187 |
| f1.params.min_child_weight | 50 |
| f1.params.subsample | 0.9883 |
| f1.params.colsample_bytree | 0.9466 |
| f1.params.reg_lambda | 42.02234 |
| f1.params.reg_alpha | 0.1 |
| f1.params.n_estimators | 244 |
| f1.class_weight_power | 0.1946 |
| f1.val_macro_f1 | 0.7709 |
| f1.val_attack_auc | 0.9689 |
| f1.trial | 4 |
| auc.params.max_depth | 5 |
| auc.params.learning_rate | 0.08114 |
| auc.params.min_child_weight | 50 |
| auc.params.subsample | 0.8509 |
| auc.params.colsample_bytree | 0.792 |
| auc.params.reg_lambda | 25.41557 |
| auc.params.reg_alpha | 1 |
| auc.params.n_estimators | 580 |
| auc.class_weight_power | 0.4158 |
| auc.val_macro_f1 | 0.7657 |
| auc.val_attack_auc | 0.9696 |
| auc.trial | 19 |

## Source: tuned_params_stage1_40f.json (rendered table)

Rendered from the JSON file of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); every key and value is listed.

| key | value |
|---|---|
| pool | base |
| n_features | 40 |
| n_trials | 40 |
| seed | 42 |
| early_stopping | 30 rounds on validation mlogloss, max 1000 trees |
| default_reference.best_iteration | 267 |
| default_reference.val_macro_f1 | 0.9258 |
| default_reference.val_attack_auc | 0.9841 |
| f1.params.max_depth | 10 |
| f1.params.learning_rate | 0.04781 |
| f1.params.min_child_weight | 10 |
| f1.params.subsample | 0.8317 |
| f1.params.colsample_bytree | 0.5884 |
| f1.params.reg_lambda | 11.78467 |
| f1.params.reg_alpha | 0.1 |
| f1.params.n_estimators | 488 |
| f1.class_weight_power | 0.7585 |
| f1.val_macro_f1 | 0.9263 |
| f1.val_attack_auc | 0.9842 |
| f1.trial | 18 |
| auc.params.max_depth | 10 |
| auc.params.learning_rate | 0.04781 |
| auc.params.min_child_weight | 10 |
| auc.params.subsample | 0.8317 |
| auc.params.colsample_bytree | 0.5884 |
| auc.params.reg_lambda | 11.78467 |
| auc.params.reg_alpha | 0.1 |
| auc.params.n_estimators | 488 |
| auc.class_weight_power | 0.7585 |
| auc.val_macro_f1 | 0.9263 |
| auc.val_attack_auc | 0.9842 |
| auc.trial | 18 |

## Source: tuned_params_stage1_48f.json (rendered table)

Rendered from the JSON file of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); every key and value is listed.

| key | value |
|---|---|
| pool | full |
| n_features | 48 |
| n_trials | 40 |
| seed | 42 |
| early_stopping | 30 rounds on validation mlogloss, max 1000 trees |
| default_reference.best_iteration | 409 |
| default_reference.val_macro_f1 | 0.9378 |
| default_reference.val_attack_auc | 0.9881 |
| f1.params.max_depth | 10 |
| f1.params.learning_rate | 0.0704 |
| f1.params.min_child_weight | 1 |
| f1.params.subsample | 0.6758 |
| f1.params.colsample_bytree | 0.565 |
| f1.params.reg_lambda | 2.8912 |
| f1.params.reg_alpha | 0.1 |
| f1.params.n_estimators | 278 |
| f1.class_weight_power | 0.2269 |
| f1.val_macro_f1 | 0.9366 |
| f1.val_attack_auc | 0.9878 |
| f1.trial | 6 |
| auc.params.max_depth | 10 |
| auc.params.learning_rate | 0.0704 |
| auc.params.min_child_weight | 1 |
| auc.params.subsample | 0.6758 |
| auc.params.colsample_bytree | 0.565 |
| auc.params.reg_lambda | 2.8912 |
| auc.params.reg_alpha | 0.1 |
| auc.params.n_estimators | 278 |
| auc.class_weight_power | 0.2269 |
| auc.val_macro_f1 | 0.9366 |
| auc.val_attack_auc | 0.9878 |
| auc.trial | 6 |
