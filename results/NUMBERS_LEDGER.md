# Numbers ledger

One line per headline number that the README, PROJECT_PLAN, the per-task conclusions or the Phase-I report quote: the value, what it measures and under which setting, and the file and column (or table row) it comes from. Built in Task 7 Step 1 on branch `cleanup/prune-results` (recovery tag `pre-cleanup-2026-10`). **All 280 entries were checked by a program against their source cell** (CSV cells selected by the row filter shown, means over seeds, or markdown-table cells selected by row text and column header), rounded to the precision the documents quote. No experiment was run and no result was regenerated.

## How to read it

- *Pools:* `base` / `40f` = 40 features (34 raw + 6 engineered); `full` / `48f` = 48 features; `full_no_ttl` / `45f` = 48 minus `sttl`, `dttl`, `ct_state_ttl`; `41f` = 48 minus the 7 window-count `ct_*` columns; `38f` = 48 minus every `ct_*` column. *Splits:* `official` = official UNSW-NB15 train/test files; `pooled_random` = optimistic pooled random split (shares neighbouring flows with its training rows).
- *Seeds:* every `mean` is over seeds 42-46 unless the setting says single seed. Access levels are written as in the conclusions: ZERO-SHOT / TRANSDUCTIVE / FEW-SHOT.
- *Paths* are relative to the repository root. Markdown-table sources that the manifest proposes to merge into one per-task tables file keep their current name here until the merge is applied; Step 3 rewrites this column to the merged file (the section keeps the original table's file name) and Step 4 re-verifies every entry.
- Per-seed rows that were behind these means were removed in the cleanup (list: `results/CLEANUP_MANIFEST.md`); they are recoverable from tag `pre-cleanup-2026-10` or by re-running the pipeline named in the conclusion.

## Headline

### Headline (5 seeds)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 1 | **0.7427** | accuracy, 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=accuracy |
| 2 | **0.7401** | accuracy, 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=accuracy |
| 3 | **0.8305** | accuracy, 40 features, pooled random split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=pooled_random, metric=accuracy |
| 4 | **0.8493** | accuracy, 48 features, pooled random split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=pooled_random, metric=accuracy |
| 5 | **0.7125** | macro F1, 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=f1 |
| 6 | **0.7130** | macro F1, 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=f1 |
| 7 | **0.7816** | macro F1, 40 features, pooled random split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=pooled_random, metric=f1 |
| 8 | **0.7982** | macro F1, 48 features, pooled random split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=pooled_random, metric=f1 |
| 9 | **0.2853** | attack-vs-normal FPR (argmax), 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=false_positive_rate |
| 10 | **0.2933** | attack-vs-normal FPR (argmax), 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=false_positive_rate |
| 11 | **0.1198** | attack-vs-normal FPR (argmax), 40 features, pooled random split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=pooled_random, metric=false_positive_rate |
| 12 | **0.0981** | attack-vs-normal FPR (argmax), 48 features, pooled random split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=pooled_random, metric=false_positive_rate |
| 13 | **0.9594** | attack detection rate, 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=detection_rate |
| 14 | **0.9681** | attack detection rate, 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=detection_rate |
| 15 | **0.9627** | attack-vs-normal ROC AUC, 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=roc_auc_attack_vs_normal |
| 16 | **0.9642** | attack-vs-normal ROC AUC, 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=roc_auc_attack_vs_normal |
| 17 | **0.0876** | ECE, 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=ece |
| 18 | **0.1093** | ECE, 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=ece |
| 19 | **0.2588** | FPR at 95% detection (threshold-free), 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=fpr_at_95_detection |
| 20 | **0.2375** | FPR at 95% detection (threshold-free), 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=fpr_at_95_detection |
| 21 | **0.2585** | open-set detection (Worms + Shellcode, max-softmax), 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=unknown_detection_rate |
| 22 | **0.3770** | open-set detection (Worms + Shellcode, max-softmax), 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=unknown_detection_rate |
| 23 | **0.7992** | open-set AUROC, 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=base, split=official, metric=unknown_auroc |
| 24 | **0.8358** | open-set AUROC, 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/headline_summary.csv` | column `mean`; row: pool=full, split=official, metric=unknown_auroc |
| 25 | **0.7367** | accuracy, 45 features (48 minus TTL), official split | `results/metrics/xgboost/headline_full_no_ttl_summary.csv` | column `mean`; row: pool=full_no_ttl, split=official, metric=accuracy |
| 26 | **0.9117** | best-possible accuracy (empirical feature-space ceiling), 40 features | `results/metrics/xgboost/accuracy_three_numbers_40f_48f_45f.csv` | column `ceiling`; row: pool=40f, hyperparameters=default |
| 27 | **0.9212** | best-possible accuracy, 48 features | `results/metrics/xgboost/accuracy_three_numbers_40f_48f_45f.csv` | column `ceiling`; row: pool=48f, hyperparameters=default |
| 28 | **0.7514** | accuracy with hyperparameters tuned for macro F1 (random validation), 40 features | `results/metrics/xgboost/tuned_vs_default.csv` | column `accuracy_mean`; row: pool=base, hyperparameters=tuned_f1 |
| 29 | **0.7647** | accuracy with hyperparameters tuned for attack AUC, 40 features | `results/metrics/xgboost/tuned_vs_default.csv` | column `accuracy_mean`; row: pool=base, hyperparameters=tuned_auc |
| 30 | **0.7591** | accuracy with tuned hyperparameters, 48 features | `results/metrics/xgboost/tuned_vs_default.csv` | column `accuracy_mean`; row: pool=full, hyperparameters=tuned_f1 |

## Operating point

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 31 | **0.2496** | test FPR at the validation-chosen 95%-detection threshold, 40 features (random validation) | `results/metrics/xgboost/operating_point_summary_40f.csv` | column `mean`; row: rule=det95, metric=test_fpr |
| 32 | **0.1497** | FPR gap test - validation at that threshold, 40 features (random validation) | `results/metrics/xgboost/operating_point_summary_40f.csv` | column `mean`; row: rule=det95, metric=fpr_gap |
| 33 | **0.2442** | test FPR at the validation-chosen 95%-detection threshold, 48 features (random validation) | `results/metrics/xgboost/operating_point_summary_48f.csv` | column `mean`; row: rule=det95, metric=test_fpr |

## Task 2.5

### Task 2.5 FPR (det95, test)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 34 | **0.2496** | zero-shot flat default, 40 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_fpr_mean`; row: pool=40f, method=flat_default, k_labelled=0 |
| 35 | **0.2442** | zero-shot flat default, 48 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_fpr_mean`; row: pool=48f, method=flat_default, k_labelled=0 |
| 36 | **0.2434** | zero-shot hierarchical, stage 1 tuned, 40 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_fpr_mean`; row: pool=40f, method=hier_stage1_tuned, k_labelled=0 |
| 37 | **0.2466** | zero-shot hierarchical, stage 1 tuned, 48 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_fpr_mean`; row: pool=48f, method=hier_stage1_tuned, k_labelled=0 |
| 38 | **0.0940** | few-shot k=5000 (half fit, half threshold), 48 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_fpr_mean`; row: pool=48f, method=retrain_split_f0.5, k_labelled=5000 |
| 39 | **0.1578** | few-shot k=1000, 48 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_fpr_mean`; row: pool=48f, method=retrain_split_f0.5, k_labelled=1000 |
| 40 | **0.2318** | few-shot k=5000, 40 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_fpr_mean`; row: pool=40f, method=retrain_split_f0.5, k_labelled=5000 |
| 41 | **0.2666** | few-shot k=1000, 40 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_fpr_mean`; row: pool=40f, method=retrain_split_f0.5, k_labelled=1000 |
| 42 | **0.9523** | detection reached by the 48-feature k=5000 few-shot run (the 0.094 is read at 0.952, not 0.95) | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `det95_test_detection_mean`; row: pool=48f, method=retrain_split_f0.5, k_labelled=5000 |

### Task 2.5 side effects

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 43 | **0.071** | ECE after few-shot adaptation (k=5000 split), 48 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `ece_mean`; row: pool=48f, method=retrain_split_f0.5, k_labelled=5000 |
| 44 | **0.109** | ECE of the default model, 48 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `ece_mean`; row: pool=48f, method=flat_default, k_labelled=0 |
| 45 | **0.796** | accuracy after few-shot adaptation (k=5000 split), 48 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `accuracy_mean`; row: pool=48f, method=retrain_split_f0.5, k_labelled=5000 |
| 46 | **0.375** | open-set detection after few-shot adaptation, 48 features | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `unknown_detection_rate_mean`; row: pool=48f, method=retrain_split_f0.5, k_labelled=5000 |
| 47 | **0.214** | argmax FPR of the hierarchical scheme, 40 features (flat default 0.285) | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `false_positive_rate_mean`; row: pool=40f, method=hier_default, k_labelled=0 |
| 48 | **0.03** | open-set detection of the hierarchical scheme, 40 features (flat 0.26) | `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | column `unknown_detection_rate_mean`; row: pool=40f, method=hier_default, k_labelled=0 |

## Task 2.6

### Task 2.6 leakage check (det95 FPR)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 49 | **0.2442** | zero-shot on the same rows, 48 features, k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=48f, k_labelled=5000, row=twins: all evaluation rows (reproduction) - zero-shot |
| 50 | **0.0958** | few-shot, evaluation rows with no near twin, 48 features, k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=48f, k_labelled=5000, row=twins: rows with NO near twin (<= 0.1) in the adaptation set |
| 51 | **0.0854** | few-shot, adaptation rows from OTHER row-order blocks (200-row gaps), 48 features, k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=48f, k_labelled=5000, row=blocks: adaptation rows from other blocks (neighbourhood-disjoint) |
| 52 | **0.0851** | few-shot, adaptation rows from the evaluation blocks, 48 features, k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=48f, k_labelled=5000, row=blocks: adaptation rows from the evaluation blocks (within-file) |
| 53 | **0.1587** | few-shot, no near twin, 48 features, k=1000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=48f, k_labelled=1000, row=twins: rows with NO near twin (<= 0.1) in the adaptation set |
| 54 | **0.1528** | few-shot, other blocks, 48 features, k=1000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=48f, k_labelled=1000, row=blocks: adaptation rows from other blocks (neighbourhood-disjoint) |
| 55 | **0.2427** | few-shot, other blocks, 40 features, k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=40f, k_labelled=5000, row=blocks: adaptation rows from other blocks (neighbourhood-disjoint) |
| 56 | **0.2025** | few-shot, adaptation rows inside the evaluation blocks, 40 features, k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=40f, k_labelled=5000, row=blocks: adaptation rows from the evaluation blocks (within-file) |
| 57 | **0.1109** | few-shot without the 3 TTL columns (45 features), k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=45f, k_labelled=5000, row=ablation: retrain_split_f0.5, random adaptation rows |
| 58 | **0.2308** | few-shot without the 7 window-count ct_* columns (41 features), k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=41f, k_labelled=5000, row=ablation: retrain_split_f0.5, random adaptation rows |
| 59 | **0.2281** | few-shot without every ct_* column (38 features), k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_fpr_mean`; row: pool=38f, k_labelled=5000, row=ablation: retrain_split_f0.5, random adaptation rows |
| 60 | **0.9318** | detection reached in the other-blocks condition (so FPR at exactly 95% would be higher), 48 features, k=5000 | `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | column `det95_test_detection_mean`; row: pool=48f, k_labelled=5000, row=blocks: adaptation rows from other blocks (neighbourhood-disjoint) |

### Task 2.6 shift AUC (seed 42)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 61 | **0.8987** | train-Normal vs test-Normal classifier AUC, random 5-fold CV, 40f | `results/metrics/xgboost/leakage_40f_shift_auc.csv` | column `auc_random_cv`; row:  |
| 62 | **0.814** | same, CV grouped by 1,000-row blocks, 40f | `results/metrics/xgboost/leakage_40f_shift_auc.csv` | column `auc_block_cv`; row:  |
| 63 | **0.9291** | train-Normal vs test-Normal classifier AUC, random 5-fold CV, 45f | `results/metrics/xgboost/leakage_45f_shift_auc.csv` | column `auc_random_cv`; row:  |
| 64 | **0.8356** | same, CV grouped by 1,000-row blocks, 45f | `results/metrics/xgboost/leakage_45f_shift_auc.csv` | column `auc_block_cv`; row:  |
| 65 | **0.9296** | train-Normal vs test-Normal classifier AUC, random 5-fold CV, 48f | `results/metrics/xgboost/leakage_48f_shift_auc.csv` | column `auc_random_cv`; row:  |
| 66 | **0.8371** | same, CV grouped by 1,000-row blocks, 48f | `results/metrics/xgboost/leakage_48f_shift_auc.csv` | column `auc_block_cv`; row:  |

### Task 2.6 validation vs test

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 67 | **0.1198** | validation FPR at argmax, RANDOM validation (mean of 5 seeds), 40 features | `results/metrics/xgboost/leakage_40f_validation_blocks.csv` | mean of column `val_fpr` over rows: validation=random_validation |
| 68 | **0.2507** | validation FPR, BLOCK-built validation (1,000-row blocks; mean of 5 seeds), 40 features | `results/metrics/xgboost/leakage_40f_validation_blocks.csv` | mean of column `val_fpr` over rows: validation=block_validation |

### Task 2.6 pooled reference

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 69 | **37013** | official-test rows inside the pooled random split's training set | `results/metrics/xgboost/pooled_reference_composition.csv` | column `rows`; row: protocol=pooled_random, part=train, source_file=test |

## Shift diagnostics

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 70 | **0.8994** | AUC separating train-Normal from official-test-Normal (random CV, 5 seeds), 40f | `results/metrics/xgboost/shift_normal_summary_40f.csv` | column `value`; row: metric=auc_mean |
| 71 | **0.9293** | AUC separating train-Normal from official-test-Normal (random CV, 5 seeds), 45f | `results/metrics/xgboost/shift_normal_summary_45f.csv` | column `value`; row: metric=auc_mean |
| 72 | **0.9301** | AUC separating train-Normal from official-test-Normal (random CV, 5 seeds), 48f | `results/metrics/xgboost/shift_normal_summary_48f.csv` | column `value`; row: metric=auc_mean |
| 73 | **0.9709** | SHAP importance rank correlation across seeds, 40 features | `results/metrics/xgboost/shift_normal_summary_40f.csv` | column `value`; row: metric=shap_rank_spearman_across_seeds |

## Task 2.7

### Task 2.7 zero-shot (det95 FPR)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 74 | **0.256** | default (config.yaml), 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `default (config.yaml)`, column `det95_test_fpr` (section `## 40f`) |
| 75 | **0.257** | tuned on block-grouped validation (auc), 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `tuned on block-grouped validation (auc)`, column `det95_test_fpr` (section `## 40f`) |
| 76 | **0.249** | temperature scaling + EM prior correction, 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `temperature scaling + EM prior correction`, column `det95_test_fpr` (section `## 40f`) |
| 77 | **0.254** | declared combination, 40 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `declared combination`, column `det95_test_fpr` (section `## 40f`) |
| 78 | **0.248** | default (config.yaml), 45 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `default (config.yaml)`, column `det95_test_fpr` (section `## 45f`) |
| 79 | **0.258** | tuned on block-grouped validation (auc), 45 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `tuned on block-grouped validation (auc)`, column `det95_test_fpr` (section `## 45f`) |
| 80 | **0.244** | temperature scaling + EM prior correction, 45 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `temperature scaling + EM prior correction`, column `det95_test_fpr` (section `## 45f`) |
| 81 | **0.249** | declared combination, 45 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `declared combination`, column `det95_test_fpr` (section `## 45f`) |
| 82 | **0.248** | default (config.yaml), 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `default (config.yaml)`, column `det95_test_fpr` (section `## 48f`) |
| 83 | **0.244** | temperature scaling + EM prior correction, 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `temperature scaling + EM prior correction`, column `det95_test_fpr` (section `## 48f`) |
| 84 | **0.247** | declared combination, 48 features, official split (mean of seeds 42-46) | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `declared combination`, column `det95_test_fpr` (section `## 48f`) |
| 85 | **0.196** | argmax FPR with EM prior correction, 40 features | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `temperature scaling + EM prior correction`, column `argmax_fpr` (section `## 40f`) |
| 86 | **0.289** | argmax FPR, default, 40 features | `results/metrics/xgboost/fpr_study_final_40f_45f_48f.md` | table row containing `default (config.yaml)`, column `argmax_fpr` (section `## 40f`) |

### Task 2.7 few-shot (FPR at exactly 95% detection)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 87 | **0.152** | random selection, k=2,500, 48 features | `results/metrics/xgboost/fpr_study_fewshot_48f_45f_41f.md` | table row containing `random` + `2500`, column `FPR at exactly 95%` (section `## 48f`) |
| 88 | **0.148** | diverse (k-means) selection, k=2,500, 48 features | `results/metrics/xgboost/fpr_study_fewshot_48f_45f_41f.md` | table row containing `diverse` + `2500`, column `FPR at exactly 95%` (section `## 48f`) |
| 89 | **0.122** | random selection, k=5,000, 48 features | `results/metrics/xgboost/fpr_study_fewshot_48f_45f_41f.md` | table row containing `random` + `5000`, column `FPR at exactly 95%` (section `## 48f`) |
| 90 | **0.138** | random selection, k=5,000, 45 features | `results/metrics/xgboost/fpr_study_fewshot_48f_45f_41f.md` | table row containing `random` + `5000`, column `FPR at exactly 95%` (section `## 45f`) |
| 91 | **0.199** | random selection, k=500, 48 features | `results/metrics/xgboost/fpr_study_fewshot_48f_45f_41f.md` | table row containing `random` + `500`, column `FPR at exactly 95%` (section `## 48f`) |

### Task 2.7 few-shot (det95 FPR, threshold on held-out half)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 92 | **0.089** | random selection, k=5,000, 48 features (the 'about 0.09'; read at a test detection of 0.935) | `results/metrics/xgboost/fpr_study_fewshot_48f_45f_41f.md` | table row containing `random` + `5000`, column `det95 FPR` (section `## 48f`) |

## Task 3

### Task 3 tiers

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 93 | **0.7113** | macro F1, 40-feature pool, 40-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_40f.csv` | column `f1_mean`; row: tier=40 |
| 94 | **0.7141** | macro F1, 40-feature pool, 30-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_40f.csv` | column `f1_mean`; row: tier=30 |
| 95 | **0.6973** | macro F1, 40-feature pool, 20-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_40f.csv` | column `f1_mean`; row: tier=20 |
| 96 | **0.6986** | macro F1, 40-feature pool, 15-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_40f.csv` | column `f1_mean`; row: tier=15 |
| 97 | **0.7065** | macro F1, 45-feature pool, 45-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_45f.csv` | column `f1_mean`; row: tier=45 |
| 98 | **0.7057** | macro F1, 45-feature pool, 30-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_45f.csv` | column `f1_mean`; row: tier=30 |
| 99 | **0.6976** | macro F1, 45-feature pool, 20-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_45f.csv` | column `f1_mean`; row: tier=20 |
| 100 | **0.6972** | macro F1, 45-feature pool, 15-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_45f.csv` | column `f1_mean`; row: tier=15 |
| 101 | **0.7126** | macro F1, 48-feature pool, 48-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_48f.csv` | column `f1_mean`; row: tier=48 |
| 102 | **0.7129** | macro F1, 48-feature pool, 30-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_48f.csv` | column `f1_mean`; row: tier=30 |
| 103 | **0.7063** | macro F1, 48-feature pool, 20-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_48f.csv` | column `f1_mean`; row: tier=20 |
| 104 | **0.7067** | macro F1, 48-feature pool, 15-feature tier (official split, block-grouped validation) | `results/metrics/xgboost/tier_summary_xgboost_48f.csv` | column `f1_mean`; row: tier=15 |
| 105 | **8.8552** | Welch z of the macro-F1 drop, 40-pool 20-feature tier vs full | `results/metrics/xgboost/tier_summary_xgboost_40f.csv` | column `welch_z_f1`; row: tier=20 |
| 106 | **0.1866** | open-set detection, 40-pool 20-feature tier | `results/metrics/xgboost/tier_summary_xgboost_40f.csv` | column `unknown_detection_rate_mean`; row: tier=20 |
| 107 | **0.2311** | open-set detection, 40-pool full tier | `results/metrics/xgboost/tier_summary_xgboost_40f.csv` | column `unknown_detection_rate_mean`; row: tier=40 |

### Task 3 stability

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 108 | **0.9739** | SHAP rank correlation, 48-feature tier vs 30-feature tier (same seed) | `results/metrics/xgboost/stability_xgboost_48f.csv` | column `rank_correlation_mean`; row: comparison=tier_pair, a=48, b=30 |
| 109 | **0.9164** | SHAP rank correlation, 48-feature tier vs 15-feature tier | `results/metrics/xgboost/stability_xgboost_48f.csv` | column `rank_correlation_mean`; row: comparison=tier_pair, a=48, b=15 |
| 110 | **0.9746** | noise floor: same 48-feature tier retrained under another seed | `results/metrics/xgboost/stability_xgboost_48f.csv` | column `rank_correlation_mean`; row: comparison=same_tier_seeds, a=48, b=48 |
| 111 | **0.9772** | SHAP rank correlation, 40-feature tier vs 30-feature tier within the 48-feature pool | `results/metrics/xgboost/stability_xgboost_48f.csv` | column `rank_correlation_mean`; row: comparison=tier_pair, a=40, b=30 |

## Task 4

### Task 4 open-set (Worms + Shellcode, zero-shot)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 112 | **0.2235** | max-softmax detection of Worms + Shellcode at 5% false-Unknown, 40 features, 5 seeds | `results/metrics/xgboost/open_set_step1_40f.csv` | column `detection_mean`; row: score=msp |
| 113 | **0.7977** | max-softmax unknown AUROC (Worms + Shellcode), 40 features, 5 seeds | `results/metrics/xgboost/open_set_step1_40f.csv` | column `unknown_auroc_mean`; row: score=msp |
| 114 | **0.862** | entropy unknown AUROC, 40 features, 5 seeds | `results/metrics/xgboost/open_set_step1_40f.csv` | column `unknown_auroc_mean`; row: score=entropy |
| 115 | **0.158** | entropy detection (stricter transferred threshold), 40 features, 5 seeds | `results/metrics/xgboost/open_set_step1_40f.csv` | column `detection_mean`; row: score=entropy |
| 116 | **0.0591** | max-softmax realised false-Unknown on the official test (target 0.05), 40 features, 5 seeds | `results/metrics/xgboost/open_set_step1_40f.csv` | column `false_unknown_test_mean`; row: score=msp |
| 117 | **0.436** | isolation forest alone, unknown AUROC (below chance), 40 features, 5 seeds | `results/metrics/xgboost/open_set_step1_40f.csv` | column `unknown_auroc_mean`; row: score=iforest |
| 118 | **0.7444** | max-softmax pseudo-unknown validation AUROC, 40 features, 5 seeds | `results/metrics/xgboost/open_set_step1_40f.csv` | column `pseudo_unknown_auroc`; row: score=msp |
| 119 | **0.343** | max-softmax detection, 45 features, 5 seeds | `results/metrics/xgboost/open_set_step1_45f.csv` | column `detection_mean`; row: score=msp |
| 120 | **0.829** | max-softmax unknown AUROC, 45 features, 5 seeds | `results/metrics/xgboost/open_set_step1_45f.csv` | column `unknown_auroc_mean`; row: score=msp |
| 121 | **0.333** | max-softmax detection, 48 features, 5 seeds | `results/metrics/xgboost/open_set_step1_48f.csv` | column `detection_mean`; row: score=msp |
| 122 | **0.834** | max-softmax unknown AUROC, 48 features, 5 seeds | `results/metrics/xgboost/open_set_step1_48f.csv` | column `unknown_auroc_mean`; row: score=msp |
| 123 | **0.881** | entropy unknown AUROC, 48 features, 5 seeds | `results/metrics/xgboost/open_set_step1_48f.csv` | column `unknown_auroc_mean`; row: score=entropy |
| 124 | **0.302** | entropy detection, 48 features, 5 seeds | `results/metrics/xgboost/open_set_step1_48f.csv` | column `detection_mean`; row: score=entropy |
| 125 | **0.187** | validation-selected iforest+entropy:max detection, 48 features, 5 seeds | `results/metrics/xgboost/open_set_step1_48f.csv` | column `detection_mean`; row: score=iforest+entropy:max |
| 126 | **0.810** | validation-selected iforest+entropy:max unknown AUROC, 48 features, 5 seeds | `results/metrics/xgboost/open_set_step1_48f.csv` | column `unknown_auroc_mean`; row: score=iforest+entropy:max |

### Task 4 leave-one-class-out (40 features, max-softmax)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 127 | **0.041** | Worms held out: detection (hardest class) | `results/metrics/xgboost/open_set_step2_40f.csv` | column `detection_mean`; row: held_out=Worms, score=msp |
| 128 | **0.632** | Worms held out: AUROC | `results/metrics/xgboost/open_set_step2_40f.csv` | column `unknown_auroc_mean`; row: held_out=Worms, score=msp |
| 129 | **0.262** | Fuzzers held out: share flagged or called an attack | `results/metrics/xgboost/open_set_step2_40f.csv` | column `flagged_or_attack_mean`; row: held_out=Fuzzers, score=msp |
| 130 | **0.123** | Exploits held out: detection | `results/metrics/xgboost/open_set_step2_40f.csv` | column `detection_mean`; row: held_out=Exploits, score=msp |
| 131 | **0.400** | Generic held out: detection (easiest) | `results/metrics/xgboost/open_set_step2_40f.csv` | column `detection_mean`; row: held_out=Generic, score=msp |
| 132 | **0.374** | Overlap-Group-1 (trio) held out: detection | `results/metrics/xgboost/open_set_step2_40f.csv` | column `detection_mean`; row: held_out=Overlap-Group-1 (all three), score=msp |
| 133 | **0.777** | Analysis: share of rows with an exact twin in the known data | `results/metrics/xgboost/open_set_step2_40f.csv` | column `exact_twin_share`; row: held_out=Analysis, score=msp |

### Task 4 alert FPR and review queue (5% target)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 134 | **0.289** | alert FPR OFF, max-softmax, 40 features, Worms + Shellcode held out | `results/metrics/xgboost/open_set_step3_40f_45f_48f.md` | table row containing `| 5.0% |`, column `alert FPR OFF` (section `## 40f: msp`) |
| 135 | **0.311** | alert FPR ON, max-softmax, 40 features, Worms + Shellcode held out | `results/metrics/xgboost/open_set_step3_40f_45f_48f.md` | table row containing `| 5.0% |`, column `alert FPR ON` (section `## 40f: msp`) |
| 136 | **0.254** | confident-alert FPR, max-softmax, 40 features, Worms + Shellcode held out | `results/metrics/xgboost/open_set_step3_40f_45f_48f.md` | table row containing `| 5.0% |`, column `confident-alert FPR` (section `## 40f: msp`) |
| 137 | **0.057** | review rate on Normal, max-softmax, 40 features, Worms + Shellcode held out | `results/metrics/xgboost/open_set_step3_40f_45f_48f.md` | table row containing `| 5.0% |`, column `review rate on Normal` (section `## 40f: msp`) |
| 138 | **0.878** | false alerts that skip review, max-softmax, 40 features, Worms + Shellcode held out | `results/metrics/xgboost/open_set_step3_40f_45f_48f.md` | table row containing `| 5.0% |`, column `false alerts that skip review` (section `## 40f: msp`) |
| 139 | **0.955** | zero-day catch, max-softmax, 40 features, Worms + Shellcode held out | `results/metrics/xgboost/open_set_step3_40f_45f_48f.md` | table row containing `| 5.0% |`, column `zero-day catch` (section `## 40f: msp`) |
| 140 | **0.223** | zero-day flagged Unknown, max-softmax, 40 features, Worms + Shellcode held out | `results/metrics/xgboost/open_set_step3_40f_45f_48f.md` | table row containing `| 5.0% |`, column `zero-day flagged Unknown` (section `## 40f: msp`) |
| 141 | **0.121** | confident-alert FPR at the 30% target (entropy, 40 features): the cost of halving it | `results/metrics/xgboost/open_set_step3_40f_45f_48f.md` | table row containing `| 30.0% |`, column `confident-alert FPR` (section `## 40f: entropy`) |

### Task 4 where the 40 -> 48 gain comes from

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 142 | **0.172** | max-softmax detection without the 7 window-count ct_* columns (41 features) | `results/metrics/xgboost/open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv` | column `detection_mean`; row: label=41f, score=msp |
| 143 | **0.171** | same without every ct_* column (38 features) | `results/metrics/xgboost/open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv` | column `detection_mean`; row: label=38f, score=msp |
| 144 | **0.340** | 48-pool 30-feature tier (keeps two window columns) | `results/metrics/xgboost/open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv` | column `detection_mean`; row: label=48f_t30, score=msp |
| 145 | **0.193** | 48-pool 15-feature tier (no window column) | `results/metrics/xgboost/open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv` | column `detection_mean`; row: label=48f_t15, score=msp |

### Task 4 zero-day set

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 146 | **1,627** | Zero-day flows after deduplication = Shellcode 1,456 + Worms 171 | `results/metrics/xgboost/task_4_conclusion.md` | stated in the running text ("1,627 = Shellcode 1,456") |

## Task 4.5

### Task 4.5 calibration (rotation means)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 147 | **0.213** | max-softmax rotation-mean detection, 40 features (baseline) | `results/metrics/xgboost/open_set_boost_calibration_40f_48f.md` | table row containing `| msp |`, column `rotation mean detection` (section `## calibration (40f`) |
| 148 | **0.266** | entropy rotation-mean detection, 40 features | `results/metrics/xgboost/open_set_boost_calibration_40f_48f.md` | table row containing `| entropy |`, column `rotation mean detection` (section `## calibration (40f`) |
| 149 | **0.276** | temperature-scaled entropy rotation-mean detection, 40 features | `results/metrics/xgboost/open_set_boost_calibration_40f_48f.md` | table row containing `| entropy_cal |`, column `rotation mean detection` (section `## calibration (40f`) |
| 150 | **0.234** | max-softmax rotation-mean detection, 48 features (baseline) | `results/metrics/xgboost/open_set_boost_calibration_40f_48f.md` | table row containing `| msp |`, column `rotation mean detection` (section `## calibration (48f`) |
| 151 | **0.304** | temperature-scaled entropy rotation-mean detection, 48 features (the one clear gain in the full known set) | `results/metrics/xgboost/open_set_boost_calibration_40f_48f.md` | table row containing `| entropy_cal |`, column `rotation mean detection` (section `## calibration (48f`) |
| 152 | **yes** | calibrated entropy clearly beats max-softmax under the declared rule, 48 features | `results/metrics/xgboost/open_set_boost_calibration_40f_48f.md` | table row containing `| entropy_cal |`, column `clearly beats` (section `## calibration (48f`) |

### Task 4.5 outlier exposure + combination

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 153 | **0.128** | max-softmax of the model trained without two classes, rotation-mean detection, 40 features (baseline in this setting) | `results/metrics/xgboost/open_set_boost_combo_40f_48f.md` | table row containing `| noP_msp |`, column `rotation mean detection` (section `## combo (40f`) |
| 154 | **0.268** | rank-average of ensemble MI and P(Unknown), rotation-mean detection, 40 features | `results/metrics/xgboost/open_set_boost_combo_40f_48f.md` | table row containing `| combo |`, column `rotation mean detection` (section `## combo (40f`) |
| 155 | **0.209** | max-softmax of the model trained without two classes, 48 features (baseline) | `results/metrics/xgboost/open_set_boost_combo_40f_48f.md` | table row containing `| noP_msp |`, column `rotation mean detection` (section `## combo (48f`) |
| 156 | **0.335** | rank-average of ensemble MI and P(Unknown), 48 features | `results/metrics/xgboost/open_set_boost_combo_40f_48f.md` | table row containing `| combo |`, column `rotation mean detection` (section `## combo (48f`) |
| 157 | **0.842** | P(Unknown) rotation-mean AUROC, 40 features (best AUROC of any score) | `results/metrics/xgboost/open_set_boost_combo_40f_48f.md` | table row containing `| oe_pu |`, column `rotation mean AUROC` (section `## combo (40f`) |
| 158 | **0.200** | entropy of the model trained without the two classes, rotation-mean detection, 40 features | `results/metrics/xgboost/open_set_boost_combo_40f_48f.md` | table row containing `| noP_entropy |`, column `rotation mean detection` (section `## combo (40f`) |

### Task 4.5 isolation-forest sign check

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 159 | **0.672** | isolation-forest AUROC, known attacks vs Normal (official test), 40 features | `results/metrics/xgboost/open_set_boost_iforest_40f_48f.md` | table row containing `| iforest |`, column `known attacks vs Normal` (section `(40f`) |
| 160 | **0.724** | same, 48 features | `results/metrics/xgboost/open_set_boost_iforest_40f_48f.md` | table row containing `| iforest |`, column `known attacks vs Normal` (section `(48f`) |
| 161 | **0.407** | Shellcode mean percentile among known test flows (looks like an inlier), 40 features | `results/metrics/xgboost/open_set_boost_iforest_40f_48f.md` | table row containing `| iforest |`, column `Shellcode` (section `(40f`) |
| 162 | **0.684** | Worms mean percentile, 40 features | `results/metrics/xgboost/open_set_boost_iforest_40f_48f.md` | table row containing `| iforest |`, column `Worms` (section `(40f`) |
| 163 | **0.411** | Mahalanobis AUROC, known attacks vs Normal, 40 features (ranks attacks below Normal) | `results/metrics/xgboost/open_set_boost_iforest_40f_48f.md` | table row containing `| maha |`, column `known attacks vs Normal` (section `(40f`) |

### Task 4.5 pseudo-unknown selection

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 164 | **0.818** | ensemble MI: mean pseudo-unknown validation AUROC over seeds and inner classes, 40 features | `results/metrics/xgboost/open_set_boost_selection_40f_scores.csv` | mean of column `pseudo_auroc` over rows: score=ens_mi |
| 165 | **0.815** | P(Unknown): mean pseudo-unknown validation AUROC, 40 features | `results/metrics/xgboost/open_set_boost_selection_40f_scores.csv` | mean of column `pseudo_auroc` over rows: score=oe_pu |
| 166 | **0.841** | ensemble MI, 48 features | `results/metrics/xgboost/open_set_boost_selection_48f_scores.csv` | mean of column `pseudo_auroc` over rows: score=ens_mi |
| 167 | **0.869** | P(Unknown), 48 features | `results/metrics/xgboost/open_set_boost_selection_48f_scores.csv` | mean of column `pseudo_auroc` over rows: score=oe_pu |

## Task 5

### Task 5 SHAP additivity

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 168 | **1.39e-05** | largest SHAP additivity error over about 179,000 flows (45-feature pool, whole tier); every flow within 1e-3 | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 45f | 45 |`, column `maximum error` (section `Step 1`) |

### Task 5 faithfulness (top-5 SHAP minus random removal, probability drop)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 169 | **0.512** | 40-feature pool, 40-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 40f | 40 | 40 |`, column `difference` (section `Primary metric: probability drop`) |
| 170 | **0.501** | 45-feature pool, 45-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 45f | 45 | 45 |`, column `difference` (section `Primary metric: probability drop`) |
| 171 | **0.553** | 48-feature pool, 48-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 48f | 48 | 48 |`, column `difference` (section `Primary metric: probability drop`) |
| 172 | **0.466** | 40-feature pool, 30-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 40f | 30 | 30 |`, column `difference` (section `Primary metric: probability drop`) |
| 173 | **0.429** | 45-feature pool, 30-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 45f | 30 | 30 |`, column `difference` (section `Primary metric: probability drop`) |
| 174 | **0.489** | 48-feature pool, 30-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 48f | 30 | 30 |`, column `difference` (section `Primary metric: probability drop`) |
| 175 | **0.333** | 40-feature pool, 15-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 40f | 15 | 15 |`, column `difference` (section `Primary metric: probability drop`) |
| 176 | **0.344** | 45-feature pool, 15-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 45f | 15 | 15 |`, column `difference` (section `Primary metric: probability drop`) |
| 177 | **0.340** | 48-feature pool, 15-feature tier, official-test flows (mean of 5 seeds) | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 48f | 15 | 15 |`, column `difference` (section `Primary metric: probability drop`) |

### Task 5 faithfulness (deletion curve, 40 features, k = 5, median baseline)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 178 | **0.619** | removing the top-5 SHAP features lowers the predicted-class probability by | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 40f | 5 |`, column `top SHAP` (section `baseline = training median`) |
| 179 | **0.182** | removing 5 random features lowers it by | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 40f | 5 |`, column `random` (section `baseline = training median`) |
| 180 | **0.022** | removing the 5 least important lowers it by | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 40f | 5 |`, column `least important` (section `baseline = training median`) |
| 181 | **0.860** | share of flows whose predicted class flips after removing the top 5 SHAP features | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 40f | 5 |`, column `top: class flips` (section `baseline = training median`) |
| 182 | **0.280** | same after removing 5 random features | `results/metrics/xgboost/xai_faithfulness_40f_45f_48f.md` | table row containing `| 40f | 5 |`, column `random: class flips` (section `baseline = training median`) |

### Task 5 narrative audit

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 183 | **0.757** | (f) cue direction agrees with the SHAP-vs-value trend on training flows, 40 features | `results/metrics/xgboost/xai_audit_40f_48f.md` | table row containing `(f) cue direction agrees`, column `40f` |
| 184 | **0.722** | (f) same, 48 features | `results/metrics/xgboost/xai_audit_40f_48f.md` | table row containing `(f) cue direction agrees`, column `48f` |
| 185 | **1.000** | (a)-(e) correctness checks, each, 40 and 48 features (2,000 audited narratives) | `results/metrics/xgboost/xai_audit_40f_48f.md` | table row containing `(e) no false statement`, column `40f` |
| 186 | **46.9%** | cited numeric features that read 'typical', 40 features | `results/metrics/xgboost/xai_audit_40f_48f.md` | stated in the running text ("of the cited numeric features 46.9% carry the cue") |
| 187 | **35.7%** | cited numeric features that read 'typical', 48 features | `results/metrics/xgboost/xai_audit_40f_48f.md` | stated in the running text ("of the cited numeric features 35.7% carry the cue") |

### Task 5 dashboard end to end

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 188 | **64** | flows of sample_flows.csv for which the API output equals an independent computation on every field | `results/metrics/xgboost/task_5_conclusion.md` | stated in the running text ("matches an independent computation") |

## Task 5.5

### Task 5.5 class-relative narrative

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 189 | **0.452** | cited numeric features that read 'typical', classic narrative, 40 features (held-out official-test sample) | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `cited numeric features read "typical"`, column `classic` (section `## 40f`) |
| 190 | **0.000** | same, class-relative narrative, 40 features (held-out official-test sample) | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `cited numeric features read "typical"`, column `class-relative` (section `## 40f`) |
| 191 | **0.365** | same, classic, 48 features, 48 features (held-out official-test sample) | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `cited numeric features read "typical"`, column `classic` (section `## 48f`) |
| 192 | **0.000** | same, class-relative, 48 features, 48 features (held-out official-test sample) | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `cited numeric features read "typical"`, column `class-relative` (section `## 48f`) |
| 193 | **4.108** | features cited per narrative, classic, 40 features | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `features cited per narrative`, column `classic` (section `## 40f`) |
| 194 | **2.558** | features cited per narrative, class-relative, 40 features | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `features cited per narrative`, column `class-relative` (section `## 40f`) |
| 195 | **4.018** | features cited per narrative, classic, 48 features, 48 features | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `features cited per narrative`, column `classic` (section `## 48f`) |
| 196 | **2.714** | features cited per narrative, class-relative, 48 features, 48 features | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `features cited per narrative`, column `class-relative` (section `## 48f`) |
| 197 | **0.780** | (f) cue-direction agreement (unchanged by the new wording), 40 features | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `(f) cue direction`, column `class-relative` (section `## 40f`) |
| 198 | **0.733** | (f) cue-direction agreement, 48 features | `results/metrics/xgboost/narrative_test_40f_48f.md` | table row containing `(f) cue direction`, column `class-relative` (section `## 48f`) |

### Task 5.5 false-positive explanations

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 199 | **0.184** | faithfulness difference (top SHAP minus random, k = 5), correctly predicted Normal (TN), 40 features | `results/metrics/xgboost/narrative_falsepos_40f_48f.md` | table row containing `| TN |`, column `difference` (section `## 40f`) |
| 200 | **0.349** | same, false-positive Normal predicted as an attack (FP-attack), 40 features | `results/metrics/xgboost/narrative_falsepos_40f_48f.md` | table row containing `| FP-attack |`, column `difference` (section `## 40f`) |
| 201 | **0.359** | same, FP-Fuzzers, 40 features | `results/metrics/xgboost/narrative_falsepos_40f_48f.md` | table row containing `| FP-Fuzzers |`, column `difference` (section `## 40f`) |
| 202 | **0.435** | same, true Fuzzers (TP-Fuzzers), 40 features | `results/metrics/xgboost/narrative_falsepos_40f_48f.md` | table row containing `| TP-Fuzzers |`, column `difference` (section `## 40f`) |
| 203 | **0.701** | raw confidence on FP-Fuzzers flows, 40 features | `results/metrics/xgboost/narrative_falsepos_40f_48f.md` | table row containing `| FP-Fuzzers |`, column `raw confidence` (section `## 40f`) |
| 204 | **0.771** | raw confidence on true Fuzzers, 40 features | `results/metrics/xgboost/narrative_falsepos_40f_48f.md` | table row containing `| TP-Fuzzers |`, column `raw confidence` (section `## 40f`) |
| 205 | **0.632** | AUROC of 1 - raw confidence for FP-Fuzzers vs TP-Fuzzers, 40 features (weak separation) | `results/metrics/xgboost/narrative_falsepos_40f_48f.md` | table row containing `1 - raw confidence`, column `AUROC` (section `## 40f`) |

## Task 6

### Task 6 zero-shot (leak-free)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 206 | **0.485** | UNSW -> CIC AUROC, 14 common features, ZERO-SHOT | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| common_all |`, column `AUROC` (section `## UNSW -> CIC`) |
| 207 | **0.578** | CIC -> UNSW AUROC (degenerate in 4 of 5 runs) | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| common_all |`, column `AUROC` (section `## CIC -> UNSW`) |
| 208 | **0.975** | within-dataset reference balanced accuracy, CIC (leak-free) | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| within_dataset_reference |`, column `balanced accuracy` (section `## UNSW -> CIC`) |
| 209 | **0.896** | within-dataset reference balanced accuracy, UNSW (leak-free) | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| within_dataset_reference |`, column `balanced accuracy` (section `## CIC -> UNSW`) |
| 210 | **0.786** | UNSW -> CIC FPR at the source 95%-detection threshold | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| common_all |`, column `FPR at the 95%-detection threshold` (section `## UNSW -> CIC`) |
| 211 | **0.926** | UNSW -> CIC FPR at exactly 95% detection | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| common_all |`, column `FPR at exactly 95% detection` (section `## UNSW -> CIC`) |
| 212 | **0.690** | UNSW -> CIC predicted attack share (CIC is 80% benign) | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| common_all |`, column `predicted attack share` (section `## UNSW -> CIC`) |
| 213 | **0.003** | CIC -> UNSW predicted attack share | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| common_all |`, column `predicted attack share` (section `## CIC -> UNSW`) |
| 214 | **+0.017** | stable minus random subsets, AUROC, UNSW -> CIC: better in 2 of 5 seeds; 95% interval -0.064, +0.097 | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | stated in the running text ("Stable against random subsets of the same size (AUROC): better in 2 of...") |
| 215 | **2831** | CIC blocks of 1,000 consecutive rows in file order | `results/metrics/xgboost/cross_dataset_step1_zero_shot.md` | table row containing `| CIC |`, column `blocks` (section `Block class mix`) |

### Task 6 diagnostic

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 216 | **0.52 +/- 0.05** | SHAP importance rank agreement, UNSW-trained vs CIC-trained model, Spearman over 5 seeds (the conclusion prints +/- 0.06: rounding slip, raw std 0.0548) | `results/metrics/xgboost/cross_dataset_step2_diagnostic.md` | stated in the running text ("Spearman 0.52 +/- 0.05 over 5 seeds") |
| 217 | **0.518** | same, mean of the five per-seed Spearman values | `results/metrics/xgboost/cross_dataset_diagnostic_importance_agreement.csv` | mean of column `spearman_importance` |
| 218 | **7 point the same way** | common features whose attack-vs-normal AUROC points the same way in both datasets (7 of 14; 11 of 14 are near 0.5 in at least one) | `results/metrics/xgboost/cross_dataset_step2_diagnostic.md` | stated in the running text ("Of 14 features: 7 point the same way, 7 do not, 11 are absent") |

### Task 6 alignment (TRANSDUCTIVE)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 219 | **0.785** | UNSW -> CIC AUROC after per-dataset standardisation (baseline 0.485) | `results/metrics/xgboost/cross_dataset_step3_align.md` | table row containing `| per_dataset_standardisation |`, column `AUROC` (section `## UNSW -> CIC`) |
| 220 | **0.410** | UNSW -> CIC FPR at exactly 95% detection after standardisation (baseline 0.926) | `results/metrics/xgboost/cross_dataset_step3_align.md` | table row containing `| per_dataset_standardisation |`, column `FPR at exactly 95% detection` (section `## UNSW -> CIC`) |
| 221 | **0.359** | detection at the source threshold after standardisation (the threshold no longer transfers) | `results/metrics/xgboost/cross_dataset_step3_align.md` | table row containing `| per_dataset_standardisation |`, column `detection at that threshold` (section `## UNSW -> CIC`) |
| 222 | **0.720** | UNSW -> CIC AUROC after quantile mapping | `results/metrics/xgboost/cross_dataset_step3_align.md` | table row containing `| quantile_mapping |`, column `AUROC` (section `## UNSW -> CIC`) |

### Task 6 few-shot, UNSW -> CIC (random selection, 25 runs per cell)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 223 | **0.508** | target-only FPR at k=100 | `results/metrics/xgboost/cross_dataset_step4_fewshot.md` | table row containing `| random |` + `| 100 |` + `| target_only |`, column `FPR at threshold` (section `## UNSW -> CIC`) |
| 224 | **0.169** | target-only FPR at k=500 | `results/metrics/xgboost/cross_dataset_step4_fewshot.md` | table row containing `| random |` + `| 500 |` + `| target_only |`, column `FPR at threshold` (section `## UNSW -> CIC`) |
| 225 | **0.096** | target-only FPR at k=1,000 (FPR <= 0.15 at detection 0.945) | `results/metrics/xgboost/cross_dataset_step4_fewshot.md` | table row containing `| random |` + `| 1000 |` + `| target_only |`, column `FPR at threshold` (section `## UNSW -> CIC`) |
| 226 | **0.187** | source+target FPR at k=1,000 (the source data does not help) | `results/metrics/xgboost/cross_dataset_step4_fewshot.md` | table row containing `| random |` + `| 1000 |` + `| source+target |`, column `FPR at threshold` (section `## UNSW -> CIC`) |
| 227 | **0.022** | target-only FPR at k=5,000 | `results/metrics/xgboost/cross_dataset_step4_fewshot.md` | table row containing `| random |` + `| 5000 |` + `| target_only |`, column `FPR at threshold` (section `## UNSW -> CIC`) |
| 228 | **0.981** | target-only AUROC at k=1,000 | `results/metrics/xgboost/cross_dataset_step4_fewshot.md` | table row containing `| random |` + `| 1000 |` + `| target_only |`, column `AUROC` (section `## UNSW -> CIC`) |

### Task 6 few-shot, CIC -> UNSW (random selection, 25 runs per cell)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 229 | **0.292** | source+target FPR at k=1,000 (UNSW never reaches 0.15) | `results/metrics/xgboost/cross_dataset_step4_fewshot.md` | table row containing `| random |` + `| 1000 |` + `| source+target |`, column `FPR at threshold` (section `## CIC -> UNSW`) |
| 230 | **0.224** | FPR at k=10,000 (best of the curve; the leak-free reference itself is 0.210) | `results/metrics/xgboost/cross_dataset_step4_fewshot.md` | table row containing `| random |` + `| 10000 |` + `| target_only |`, column `FPR at threshold` (section `## CIC -> UNSW`) |

## Older single-seed table

### Older single-seed table (README Key findings)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 231 | **0.742** | accuracy, 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `accuracy`; row: feature_set=40, split=official |
| 232 | **0.685** | macro F1, 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `f1`; row: feature_set=40, split=official |
| 233 | **0.955** | attack detection rate, 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `detection_rate`; row: feature_set=40, split=official |
| 234 | **0.276** | attack-vs-normal false-positive rate (argmax), 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `false_positive_rate`; row: feature_set=40, split=official |
| 235 | **0.167** | FPR at 90% detection, 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `fpr_at_90_detection`; row: feature_set=40, split=official |
| 236 | **0.264** | FPR at 95% detection, 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `fpr_at_95_detection`; row: feature_set=40, split=official |
| 237 | **0.374** | FPR at 99% detection, 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `fpr_at_99_detection`; row: feature_set=40, split=official |
| 238 | **0.724** | Normal recall, 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `recall_Normal`; row: feature_set=40, split=official |
| 239 | **0.308** | Fuzzers precision, 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `precision_Fuzzers`; row: feature_set=40, split=official |
| 240 | **0.836** | accuracy (pooled random split: optimistic, shares neighbouring flows), 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `accuracy`; row: feature_set=40, split=pooled_random |
| 241 | **0.760** | macro F1 (pooled random split), 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `f1`; row: feature_set=40, split=pooled_random |
| 242 | **0.112** | FPR (pooled random split), 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `false_positive_rate`; row: feature_set=40, split=pooled_random |
| 243 | **0.134** | FPR at 95% detection (pooled random split), 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `fpr_at_95_detection`; row: feature_set=40, split=pooled_random |
| 244 | **0.889** | Normal recall (pooled random split), 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `recall_Normal`; row: feature_set=40, split=pooled_random |
| 245 | **0.598** | Fuzzers precision (pooled random split), 40 features, official/pooled split as stated, single seed | `results/metrics/xgboost/split_comparison.csv` | column `precision_Fuzzers`; row: feature_set=40, split=pooled_random |
| 246 | **0.83** | recall_Analysis_as_Overlap-Group-1: recall into the merged group (40 features, official split) | `results/metrics/xgboost/experiment_results.csv` | column `recall_Analysis_as_Overlap-Group-1`; row: feature_set=40, open_set=True |
| 247 | **0.94** | recall_Backdoor_as_Overlap-Group-1: recall into the merged group (40 features, official split) | `results/metrics/xgboost/experiment_results.csv` | column `recall_Backdoor_as_Overlap-Group-1`; row: feature_set=40, open_set=True |
| 248 | **0.50** | recall_DoS_as_Overlap-Group-1: recall into the merged group (40 features, official split) | `results/metrics/xgboost/experiment_results.csv` | column `recall_DoS_as_Overlap-Group-1`; row: feature_set=40, open_set=True |
| 249 | **0.685** | macro F1 of the 40-feature tier (official split, single seed) | `results/metrics/xgboost/experiment_results.csv` | column `f1`; row: feature_set=40, open_set=True |
| 250 | **0.687** | macro F1 of the 30-feature tier (official split, single seed) | `results/metrics/xgboost/experiment_results.csv` | column `f1`; row: feature_set=30, open_set=True |
| 251 | **0.672** | macro F1 of the 20-feature tier (official split, single seed) | `results/metrics/xgboost/experiment_results.csv` | column `f1`; row: feature_set=20, open_set=True |
| 252 | **0.675** | macro F1 of the 15-feature tier (official split, single seed) | `results/metrics/xgboost/experiment_results.csv` | column `f1`; row: feature_set=15, open_set=True |
| 253 | **0.494** | open-set threshold chosen on validation (max-softmax; target 5% false-Unknown on validation) | `results/metrics/xgboost/experiment_results.csv` | column `open_set_threshold`; row: feature_set=40, open_set=True |
| 254 | **0.247** | open-set (zero-day) detection at that threshold, 40 features (README: about 25%) | `results/metrics/xgboost/experiment_results.csv` | column `unknown_detection_rate`; row: feature_set=40, open_set=True |
| 255 | **0.064** | false 'Unknown' on known test traffic | `results/metrics/xgboost/experiment_results.csv` | column `false_unknown_alarm_rate`; row: feature_set=40, open_set=True |
| 256 | **0.800** | open-set AUROC, 40 features (README: 0.80; 0.75-0.80 across tiers) | `results/metrics/xgboost/experiment_results.csv` | column `unknown_auroc`; row: feature_set=40, open_set=True |
| 257 | **0.687** | feature-set size study, ranked top-30 macro F1 (single seed, 10 random draws) | `results/metrics/xgboost/feature_selection_baselines_summary.csv` | column `ranked_f1`; row: feature_set=30 |
| 258 | **0.677** | feature-set size study, mean of 10 random 30-feature subsets (single seed, 10 random draws) | `results/metrics/xgboost/feature_selection_baselines_summary.csv` | column `random_f1_mean`; row: feature_set=30 |
| 259 | **2.41** | feature-set size study, z of the ranked set against the random subsets (single seed, 10 random draws) | `results/metrics/xgboost/feature_selection_baselines_summary.csv` | column `ranked_z_vs_random`; row: feature_set=30 |
| 260 | **0.672** | feature-set size study, ranked top-20 macro F1 (single seed, 10 random draws) | `results/metrics/xgboost/feature_selection_baselines_summary.csv` | column `ranked_f1`; row: feature_set=20 |
| 261 | **0.672** | feature-set size study, random 20-feature subsets (ranking indistinguishable) (single seed, 10 random draws) | `results/metrics/xgboost/feature_selection_baselines_summary.csv` | column `random_f1_mean`; row: feature_set=20 |
| 262 | **0.659** | feature-set size study, random 15-feature subsets (single seed, 10 random draws) | `results/metrics/xgboost/feature_selection_baselines_summary.csv` | column `random_f1_mean`; row: feature_set=15 |
| 263 | **0.024** | feature-set size study, spread of random 15-feature subsets (single seed, 10 random draws) | `results/metrics/xgboost/feature_selection_baselines_summary.csv` | column `random_f1_std`; row: feature_set=15 |
| 264 | **0.466** | feature-set size study, worst-15 subset (far worse than the ranking) (single seed, 10 random draws) | `results/metrics/xgboost/feature_selection_baselines_summary.csv` | column `worst_f1`; row: feature_set=15 |
| 265 | **0.8321** | lowest nested-tier SHAP rank correlation (20 vs 15 features); README quotes 0.83-0.99 | `results/metrics/xgboost/explanation_stability.csv` | column `rank_correlation`; row: comparison=nested_feature_sets, config_a=xgboost_20, config_b=xgboost_15 |
| 266 | **0.9969** | highest nested-tier SHAP rank correlation (40 vs 30 features) | `results/metrics/xgboost/explanation_stability.csv` | column `rank_correlation`; row: comparison=nested_feature_sets, config_a=xgboost_40, config_b=xgboost_30 |
| 267 | **0.9942** | same set, different seed (noise floor); README quotes 0.98-0.99 | `results/metrics/xgboost/explanation_stability.csv` | column `rank_correlation`; row: comparison=same_set_different_seed, config_a=xgboost_40, config_b=xgboost_40_seed43 |

## Data

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 268 | **1800** | Generic rows in the train file after exact deduplication (raw 40,000) | `results/metrics/xgboost/split_summary.csv` | column `dedup_train_file`; row: attack_cat=Generic |
| 269 | **1257** | Generic rows in the test file after deduplication (raw 18,871) | `results/metrics/xgboost/split_summary.csv` | column `dedup_test_file`; row: attack_cat=Generic |
| 270 | **1504** | DoS rows in the test file after deduplication (raw 4,089) | `results/metrics/xgboost/split_summary.csv` | column `dedup_test_file`; row: attack_cat=DoS |
| 271 | **162,745** | rows of the 42-feature UNSW-NB15 files after exact deduplication (257,673 before) = 90,543 + 15,979 + 54,596 official train/val/test rows + 1,627 zero-day flows | `README.md` | stated in the running text ("162,745 after exact deduplication") |
| 272 | **54596** | official-test rows used (known classes) in the 42-feature runs | `results/metrics/xgboost/pooled_reference_composition.csv` | column `rows`; row: protocol=official, part=test, source_file=test |
| 273 | **90543** | official training rows (85% of the train file) in the 42-feature runs | `results/metrics/xgboost/pooled_reference_composition.csv` | column `rows`; row: protocol=official, part=train, source_file=train |

## Older cross-dataset run

### Older cross-dataset run (superseded by Task 6)

| # | value | metric and setting | source file | where in the file |
|---|---|---|---|---|
| 274 | **0.38** | UNSW -> CIC macro F1, common_all, with the earlier random-split protocol | `results/metrics/xgboost/cross_dataset_results.csv` | column `f1`; row: strategy=common_all, train=UNSW, test=CIC |
| 275 | **0.41** | UNSW -> CIC balanced accuracy, common_all | `results/metrics/xgboost/cross_dataset_results.csv` | column `balanced_accuracy`; row: strategy=common_all, train=UNSW, test=CIC |
| 276 | **0.90** | within-dataset reference, UNSW (macro F1) | `results/metrics/xgboost/cross_dataset_results.csv` | column `f1`; row: strategy=within_dataset, train=UNSW, test=UNSW |
| 277 | **0.97** | within-dataset reference, CIC (macro F1) | `results/metrics/xgboost/cross_dataset_results.csv` | column `f1`; row: strategy=within_dataset, train=CIC, test=CIC |
| 278 | **0.72** | Kolmogorov-Smirnov statistic of smean between the datasets | `results/metrics/xgboost/cross_dataset_feature_shift.csv` | column `ks_statistic`; row: feature=smean |
| 279 | **0.69** | KS statistic of sbytes | `results/metrics/xgboost/cross_dataset_feature_shift.csv` | column `ks_statistic`; row: feature=sbytes |
| 280 | **0.64** | KS statistic of total_pkts | `results/metrics/xgboost/cross_dataset_feature_shift.csv` | column `ks_statistic`; row: feature=total_pkts |

## Gaps and corrections found while building the ledger (nothing was changed or regenerated for these)

1. **`task_6_conclusion.md` prints Spearman 0.52 +/- 0.06; the data say 0.52 +/- 0.05.** The five per-seed values (`cross_dataset_diagnostic_importance_agreement.csv`, column `spearman_importance`) have mean 0.518 and standard deviation 0.0548, which `cross_dataset_step2_diagnostic.md` prints as 0.05. A rounding slip in the conclusion; it is corrected in Step 3 if approved.
2. **README `Label schemes` table (and the matching sentences in PROJECT_PLAN `Key Findings`) are not backed by any tracked file.** README: current 0.756 / 0.276 / 0.955 / 0.12, none 0.611, wide 0.832 / 0.284 / 0.957 / 0.56, hierarchical 0.609 / 0.208 / 0.925 (fine-recall macro / FPR / detection / group share). The tracked `label_scheme_comparison.csv` and `label_scheme_summary.md` hold a later 42-feature run (commit `70a845d`) with three schemes and different values: current 0.7859 / 0.2860 / 0.9607 / 0.1193, none 0.6327 / 0.2895 / 0.9622 / 0, wide 0.8590 / 0.2895 / 0.9598 / 0.4848, and no hierarchical row. The hierarchical row survives only in git history (commit `af809d2`). Left as is; the report should quote the tracked file or the table should be regenerated by its owner (not in this task).
3. **README and PROJECT_PLAN twin shares (Analysis / Backdoor / DoS 72-80%; "34 -> 42 features": 72.0 -> 72.0, 78.9 -> 76.7, 79.7 -> 79.5, Fuzzers 21.1 -> 11.4, Reconnaissance 35.4 -> 18.0; Overlap-Group-1 twins in Exploits 78% / Fuzzers 77% / Reconnaissance 72% / Generic 33% / Normal 0.1%) are not in the tracked overlap summaries.** `results/metrics/overlap/pooled_34f/` and `pooled_42f/` are the pooled partition with duplicates kept (Analysis 76.99%, Backdoor 84.89%, DoS 77.4-77.8% at both widths), so the quoted figures came from another partition whose output was never committed. README also says the overlap output folder "is not kept in the repo", but these two folders are tracked. `scripts/overlap_analysis.py --partition train|test` regenerates them; not done here.
4. **Test counts in README ("140 tests") and PROJECT_PLAN ("140 automated tests") are out of date** (the suite has 327 tests at HEAD); corrected in Step 3 if approved.
5. Numbers that now live only in running text of a kept document (their per-run source is proposed for deletion): the zero-day flow count 1,627 (Shellcode 1,456 + Worms 171) is also in `open_set_step1_40f_45f_48f.md`; the 2,831 / 1,308 CIC block counts are in the `Block class mix` table of `cross_dataset_step1_zero_shot.md` (1,198 mixed + 110 pure-attack = 1,308); the per-class sample counts of Task 5.5 are in `narrative_falsepos_*_groups.csv`. No quoted number depends solely on a file proposed for deletion (checked mechanically, conclusion by conclusion: see `results/CLEANUP_MANIFEST.md`, section Coverage check).
