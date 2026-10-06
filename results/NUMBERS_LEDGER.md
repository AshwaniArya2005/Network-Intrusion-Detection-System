# Numbers ledger

One line per headline number that the README, PROJECT_PLAN, the conclusions or the Phase-I report quote: the value, what it measures and under which setting, and where it is: the file, the `Source:` section and the table row and column. **All 316 entries are checked by a program against the cell they point to** (markdown table cells located by row text and column header, means over seeds computed from rendered per-seed rows, or a statement in the text), at the precision the documents quote. Where a value appears in a table only at a coarser precision, the entry points to the displayed value and says so.

## How to read it

- *Pools:* `base` / `40f` = 40 features (34 raw + 6 engineered); `full` / `48f` = 48 features; `full_no_ttl` / `45f` = 48 minus `sttl`, `dttl`, `ct_state_ttl`; `41f` = 48 minus the 7 window-count `ct_*` columns; `38f` = 48 minus every `ct_*` column. *Splits:* `official` = official UNSW-NB15 train and test files; `pooled_random` = the optimistic pooled random split (shares neighbouring flows with its training rows).
- *Seeds:* every mean is over seeds 42-46 unless the setting says single seed. Access levels are as in the conclusions: ZERO-SHOT / TRANSDUCTIVE / FEW-SHOT.
- *Files:* all paths are relative to the repository root. The numbered files `results/01_...md` to `06_...md` hold the original table files unchanged under `## Source: <original file name>` headings, plus tables rendered from CSV files that were removed (marked 'rendered table'). The per-seed rows behind the means were removed (recoverable from git tags `pre-cleanup-2026-10` and `pre-lean-2026-10`, or by re-running the pipeline named in the conclusion).

## 01 Protocol and headline

### Headline (5 seeds)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 1 | **0.7427** | accuracy, 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| accuracy |`, column `40 features, official` |
| 2 | **0.7401** | accuracy, 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| accuracy |`, column `48 features, official` |
| 3 | **0.8305** | accuracy, 40 features, pooled random split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| accuracy |`, column `40 features, pooled_random` |
| 4 | **0.8493** | accuracy, 48 features, pooled random split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| accuracy |`, column `48 features, pooled_random` |
| 5 | **0.7125** | macro F1, 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| f1 |`, column `40 features, official` |
| 6 | **0.7130** | macro F1, 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| f1 |`, column `48 features, official` |
| 7 | **0.7816** | macro F1, 40 features, pooled random split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| f1 |`, column `40 features, pooled_random` |
| 8 | **0.7982** | macro F1, 48 features, pooled random split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| f1 |`, column `48 features, pooled_random` |
| 9 | **0.2853** | attack-vs-normal FPR (argmax), 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| false_positive_rate |`, column `40 features, official` |
| 10 | **0.2933** | attack-vs-normal FPR (argmax), 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| false_positive_rate |`, column `48 features, official` |
| 11 | **0.1198** | attack-vs-normal FPR (argmax), 40 features, pooled random split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| false_positive_rate |`, column `40 features, pooled_random` |
| 12 | **0.0981** | attack-vs-normal FPR (argmax), 48 features, pooled random split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| false_positive_rate |`, column `48 features, pooled_random` |
| 13 | **0.9594** | attack detection rate, 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| detection_rate |`, column `40 features, official` |
| 14 | **0.9681** | attack detection rate, 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| detection_rate |`, column `48 features, official` |
| 15 | **0.9627** | attack-vs-normal ROC AUC, 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| roc_auc_attack_vs_normal |`, column `40 features, official` |
| 16 | **0.9642** | attack-vs-normal ROC AUC, 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| roc_auc_attack_vs_normal |`, column `48 features, official` |
| 17 | **0.0876** | ECE, 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| ece |`, column `40 features, official` |
| 18 | **0.1093** | ECE, 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| ece |`, column `48 features, official` |
| 19 | **0.2588** | FPR at 95% detection (threshold-free), 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| fpr_at_95_detection |`, column `40 features, official` |
| 20 | **0.2375** | FPR at 95% detection (threshold-free), 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| fpr_at_95_detection |`, column `48 features, official` |
| 21 | **0.2585** | open-set detection (Worms + Shellcode, max-softmax), 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| unknown_detection_rate |`, column `40 features, official` |
| 22 | **0.3770** | open-set detection (Worms + Shellcode, max-softmax), 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| unknown_detection_rate |`, column `48 features, official` |
| 23 | **0.7992** | open-set AUROC, 40 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| unknown_auroc |`, column `40 features, official` |
| 24 | **0.8358** | open-set AUROC, 48 features, official split (mean of seeds 42-46) | `results/01_protocol_and_headline.md` | section `Source: headline_summary.md`: table row starting `| unknown_auroc |`, column `48 features, official` |
| 25 | **0.7367** | accuracy, 45 features (48 minus TTL), official split | `results/01_protocol_and_headline.md` | section `Source: headline_full_no_ttl_summary.md`: table row starting `| accuracy |`, column `full_no_ttl, official` |
| 26 | **0.9117** | best-possible accuracy (empirical feature-space ceiling), 40 features | `results/01_protocol_and_headline.md` | section `Source: accuracy_three_numbers_40f_48f_45f.md`: table row starting `| 40f |`, column `ceiling` |
| 27 | **0.9212** | best-possible accuracy, 48 features | `results/01_protocol_and_headline.md` | section `Source: accuracy_three_numbers_40f_48f_45f.md`: table row starting `| 48f |`, column `ceiling` |
| 28 | **0.7514** | accuracy with hyperparameters tuned for macro F1 (random validation), 40 features | `results/01_protocol_and_headline.md` | section `Source: tuned_vs_default.md`: table row starting `| base | tuned_f1 |`, column `accuracy` |
| 29 | **0.7647** | accuracy with hyperparameters tuned for attack AUC, 40 features | `results/01_protocol_and_headline.md` | section `Source: tuned_vs_default.md`: table row starting `| base | tuned_auc |`, column `accuracy` |
| 30 | **0.7591** | accuracy with tuned hyperparameters, 48 features | `results/01_protocol_and_headline.md` | section `Source: tuned_vs_default.md`: table row starting `| full | tuned_f1 |`, column `accuracy` |

### Operating point

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 31 | **0.2496** | test FPR at the validation-chosen 95%-detection threshold, 40 features (random validation) | `results/01_protocol_and_headline.md` | section `Source: operating_point_summary.md`: table row starting `| 40f | det95 |`, column `test FPR` |
| 32 | **0.1497** | FPR gap test - validation at that threshold, 40 features (random validation) | `results/01_protocol_and_headline.md` | section `Source: operating_point_summary.md`: table row starting `| 40f | det95 |`, column `FPR gap (test - val)` |
| 33 | **0.2442** | test FPR at the validation-chosen 95%-detection threshold, 48 features (random validation) | `results/01_protocol_and_headline.md` | section `Source: operating_point_summary.md`: table row starting `| 48f | det95 |`, column `test FPR` |

### Shift diagnostics

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 34 | **0.8994** | AUC separating train-Normal from official-test-Normal (random CV, 5 seeds), 40f | `results/01_protocol_and_headline.md` | section `Source: shift_normal_summary_40f.csv` (rendered table): row with metric = auc_mean, column `value` |
| 35 | **0.9293** | AUC separating train-Normal from official-test-Normal (random CV, 5 seeds), 45f | `results/01_protocol_and_headline.md` | section `Source: shift_normal_summary_45f.csv` (rendered table): row with metric = auc_mean, column `value` |
| 36 | **0.9301** | AUC separating train-Normal from official-test-Normal (random CV, 5 seeds), 48f | `results/01_protocol_and_headline.md` | section `Source: shift_normal_summary_48f.csv` (rendered table): row with metric = auc_mean, column `value` |
| 37 | **0.9709** | SHAP importance rank correlation across seeds, 40 features | `results/01_protocol_and_headline.md` | section `Source: shift_normal_summary_40f.csv` (rendered table): row with metric = shap_rank_spearman_across_seeds, column `value` |

### Older single-seed table (README Key findings)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 38 | **0.742** | accuracy, 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `accuracy`, column `40 / official` |
| 39 | **0.685** | macro F1, 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `f1`, column `40 / official` |
| 40 | **0.955** | attack detection rate, 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `detection_rate`, column `40 / official` |
| 41 | **0.276** | attack-vs-normal false-positive rate (argmax), 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `false_positive_rate`, column `40 / official` |
| 42 | **0.167** | FPR at 90% detection, 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `fpr_at_90_detection`, column `40 / official` |
| 43 | **0.264** | FPR at 95% detection, 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `fpr_at_95_detection`, column `40 / official` |
| 44 | **0.374** | FPR at 99% detection, 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `fpr_at_99_detection`, column `40 / official` |
| 45 | **0.724** | Normal recall, 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `recall_Normal`, column `40 / official` |
| 46 | **0.308** | Fuzzers precision, 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `precision_Fuzzers`, column `40 / official` |
| 47 | **0.836** | accuracy (pooled random split: optimistic, shares neighbouring flows), 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `accuracy`, column `40 / pooled_random` |
| 48 | **0.760** | macro F1 (pooled random split), 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `f1`, column `40 / pooled_random` |
| 49 | **0.112** | FPR (pooled random split), 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `false_positive_rate`, column `40 / pooled_random` |
| 50 | **0.134** | FPR at 95% detection (pooled random split), 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `fpr_at_95_detection`, column `40 / pooled_random` |
| 51 | **0.889** | Normal recall (pooled random split), 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `recall_Normal`, column `40 / pooled_random` |
| 52 | **0.598** | Fuzzers precision (pooled random split), 40 features, official/pooled split as stated, single seed | `results/01_protocol_and_headline.md` | section `Source: split_comparison.csv` (rendered table): row `precision_Fuzzers`, column `40 / pooled_random` |
| 53 | **0.83** | recall_Analysis_as_Overlap-Group-1: recall into the merged group (40 features, official split) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `recall_Analysis_as_Overlap-Group-1`, column `40 / True` |
| 54 | **0.94** | recall_Backdoor_as_Overlap-Group-1: recall into the merged group (40 features, official split) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `recall_Backdoor_as_Overlap-Group-1`, column `40 / True` |
| 55 | **0.50** | recall_DoS_as_Overlap-Group-1: recall into the merged group (40 features, official split) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `recall_DoS_as_Overlap-Group-1`, column `40 / True` |
| 56 | **0.685** | macro F1 of the 40-feature tier (official split, single seed) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `f1`, column `40 / True` |
| 57 | **0.687** | macro F1 of the 30-feature tier (official split, single seed) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `f1`, column `30 / True` |
| 58 | **0.672** | macro F1 of the 20-feature tier (official split, single seed) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `f1`, column `20 / True` |
| 59 | **0.675** | macro F1 of the 15-feature tier (official split, single seed) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `f1`, column `15 / True` |
| 60 | **0.494** | open-set threshold chosen on validation (max-softmax; target 5% false-Unknown on validation) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `open_set_threshold`, column `40 / True` |
| 61 | **0.247** | open-set (zero-day) detection at that threshold, 40 features (README: about 25%) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `unknown_detection_rate`, column `40 / True` |
| 62 | **0.064** | false 'Unknown' on known test traffic | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `false_unknown_alarm_rate`, column `40 / True` |
| 63 | **0.800** | open-set AUROC, 40 features (README: 0.80; 0.75-0.80 across tiers) | `results/01_protocol_and_headline.md` | section `Source: experiment_results.csv` (rendered table): row `unknown_auroc`, column `40 / True` |
| 64 | **0.687** | feature-set size study, ranked top-30 macro F1 (single seed, 10 random draws) | `results/01_protocol_and_headline.md` | section `Source: feature_selection_baselines_summary.csv` (rendered table): row with feature_set = 30, column `ranked_f1` |
| 65 | **0.677** | feature-set size study, mean of 10 random 30-feature subsets (single seed, 10 random draws) | `results/01_protocol_and_headline.md` | section `Source: feature_selection_baselines_summary.csv` (rendered table): row with feature_set = 30, column `random_f1_mean` |
| 66 | **2.41** | feature-set size study, z of the ranked set against the random subsets (single seed, 10 random draws) | `results/01_protocol_and_headline.md` | section `Source: feature_selection_baselines_summary.csv` (rendered table): row with feature_set = 30, column `ranked_z_vs_random` |
| 67 | **0.672** | feature-set size study, ranked top-20 macro F1 (single seed, 10 random draws) | `results/01_protocol_and_headline.md` | section `Source: feature_selection_baselines_summary.csv` (rendered table): row with feature_set = 20, column `ranked_f1` |
| 68 | **0.672** | feature-set size study, random 20-feature subsets (ranking indistinguishable) (single seed, 10 random draws) | `results/01_protocol_and_headline.md` | section `Source: feature_selection_baselines_summary.csv` (rendered table): row with feature_set = 20, column `random_f1_mean` |
| 69 | **0.659** | feature-set size study, random 15-feature subsets (single seed, 10 random draws) | `results/01_protocol_and_headline.md` | section `Source: feature_selection_baselines_summary.csv` (rendered table): row with feature_set = 15, column `random_f1_mean` |
| 70 | **0.024** | feature-set size study, spread of random 15-feature subsets (single seed, 10 random draws) | `results/01_protocol_and_headline.md` | section `Source: feature_selection_baselines_summary.csv` (rendered table): row with feature_set = 15, column `random_f1_std` |
| 71 | **0.466** | feature-set size study, worst-15 subset (far worse than the ranking) (single seed, 10 random draws) | `results/01_protocol_and_headline.md` | section `Source: feature_selection_baselines_summary.csv` (rendered table): row with feature_set = 15, column `worst_f1` |
| 72 | **0.8321** | lowest nested-tier SHAP rank correlation (20 vs 15 features); README quotes 0.83-0.99 | `results/01_protocol_and_headline.md` | section `Source: explanation_stability.csv` (rendered table): row with comparison = nested_feature_sets, config_a = xgboost_20, config_b = xgboost_15, column `rank_correlation` |
| 73 | **0.9969** | highest nested-tier SHAP rank correlation (40 vs 30 features) | `results/01_protocol_and_headline.md` | section `Source: explanation_stability.csv` (rendered table): row with comparison = nested_feature_sets, config_a = xgboost_40, config_b = xgboost_30, column `rank_correlation` |
| 74 | **0.9942** | same set, different seed (noise floor); README quotes 0.98-0.99 | `results/01_protocol_and_headline.md` | section `Source: explanation_stability.csv` (rendered table): row with comparison = same_set_different_seed, config_a = xgboost_40, config_b = xgboost_40_seed43, column `rank_correlation` |

### Data

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 75 | **1800** | Generic rows in the train file after exact deduplication (raw 40,000) | `results/01_protocol_and_headline.md` | section `Source: split_summary.csv` (rendered table): row with attack_cat = Generic, column `dedup_train_file` |
| 76 | **1257** | Generic rows in the test file after deduplication (raw 18,871) | `results/01_protocol_and_headline.md` | section `Source: split_summary.csv` (rendered table): row with attack_cat = Generic, column `dedup_test_file` |
| 77 | **1504** | DoS rows in the test file after deduplication (raw 4,089) | `results/01_protocol_and_headline.md` | section `Source: split_summary.csv` (rendered table): row with attack_cat = DoS, column `dedup_test_file` |

### Label schemes (README table; 40 features, official split, one run)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 78 | **0.786** | fine-recall macro, scheme `current` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `current`, column `fine_recall_macro` |
| 79 | **0.286** | false-positive rate, scheme `current` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `current`, column `false_positive_rate` |
| 80 | **0.961** | attack detection, scheme `current` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `current`, column `detection_rate` |
| 81 | **0.119** | group share (attack rows inside a merged group), scheme `current` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `current`, column `group_size_share` |
| 82 | **0.633** | fine-recall macro, scheme `none` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `none`, column `fine_recall_macro` |
| 83 | **0.290** | false-positive rate, scheme `none` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `none`, column `false_positive_rate` |
| 84 | **0.962** | attack detection, scheme `none` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `none`, column `detection_rate` |
| 85 | **0.000** | group share (attack rows inside a merged group), scheme `none` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `none`, column `group_size_share` |
| 86 | **0.859** | fine-recall macro, scheme `wide` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `wide`, column `fine_recall_macro` |
| 87 | **0.290** | false-positive rate, scheme `wide` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `wide`, column `false_positive_rate` |
| 88 | **0.960** | attack detection, scheme `wide` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `wide`, column `detection_rate` |
| 89 | **0.485** | group share (attack rows inside a merged group), scheme `wide` | `results/01_protocol_and_headline.md` | section `Source: label_scheme_summary.md`: the text block under `Official train/test split`, row `wide`, column `group_size_share` |

### Label schemes: hierarchical row (5-seed method summary, mean of 5 seeds, 40 features, official split)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 90 | **0.628** | fine-recall macro, method `hier_default` | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = hier_default, metric = fine_recall_macro, column `mean` |
| 91 | **0.214** | false-positive rate, method `hier_default` | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = hier_default, metric = false_positive_rate, column `mean` |
| 92 | **0.935** | attack detection, method `hier_default` | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = hier_default, metric = detection_rate, column `mean` |
| 93 | **0.000** | group share, method `hier_default` | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = hier_default, metric = group_size_share, column `mean` |
| 94 | **0.628** | fine-recall macro, method `hier_stage1_tuned` | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = hier_stage1_tuned, metric = fine_recall_macro, column `mean` |
| 95 | **0.212** | false-positive rate, method `hier_stage1_tuned` | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = hier_stage1_tuned, metric = false_positive_rate, column `mean` |
| 96 | **0.933** | attack detection, method `hier_stage1_tuned` | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = hier_stage1_tuned, metric = detection_rate, column `mean` |
| 97 | **0.000** | group share, method `hier_stage1_tuned` | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = hier_stage1_tuned, metric = group_size_share, column `mean` |
| 98 | **0.786** | fine-recall macro, method `flat_default` (the flat default, which reproduces the `current` row above) | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = flat_default, metric = fine_recall_macro, column `mean` |
| 99 | **0.285** | false-positive rate, method `flat_default` (the flat default, which reproduces the `current` row above) | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = flat_default, metric = false_positive_rate, column `mean` |
| 100 | **0.959** | attack detection, method `flat_default` (the flat default, which reproduces the `current` row above) | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = flat_default, metric = detection_rate, column `mean` |
| 101 | **0.119** | group share, method `flat_default` (the flat default, which reproduces the `current` row above) | `results/01_protocol_and_headline.md` | section `Source: methods_zero_shot_b1_40f_summary.csv` (rendered table): row with method = flat_default, metric = group_size_share, column `mean` |

### Twin shares (tracked pooled partition, duplicates kept; README: 77-85% etc.)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 102 | **76.99%** | share of Analysis rows with an exact twin in another class (label set `original`), 34 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_34f/summary.md`: stated in the text ("Analysis           76.99") |
| 103 | **76.99%** | share of Analysis rows with an exact twin in another class (label set `original`), 42 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_42f/summary.md`: stated in the text ("Analysis           76.99") |
| 104 | **84.89%** | share of Backdoor rows with an exact twin in another class (label set `original`), 34 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_34f/summary.md`: stated in the text ("Backdoor           84.89") |
| 105 | **84.89%** | share of Backdoor rows with an exact twin in another class (label set `original`), 42 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_42f/summary.md`: stated in the text ("Backdoor           84.89") |
| 106 | **77.75%** | share of DoS rows with an exact twin in another class (label set `original`), 34 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_34f/summary.md`: stated in the text ("DoS                77.75") |
| 107 | **77.41%** | share of DoS rows with an exact twin in another class (label set `original`), 42 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_42f/summary.md`: stated in the text ("DoS                77.41") |
| 108 | **23.93%** | share of Fuzzers rows with an exact twin in another class (label set `original`), 34 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_34f/summary.md`: stated in the text ("Fuzzers            23.93") |
| 109 | **14.92%** | share of Fuzzers rows with an exact twin in another class (label set `original`), 42 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_42f/summary.md`: stated in the text ("Fuzzers            14.92") |
| 110 | **33.78%** | share of Reconnaissance rows with an exact twin in another class (label set `original`), 34 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_34f/summary.md`: stated in the text ("Reconnaissance     33.78") |
| 111 | **16.06%** | share of Reconnaissance rows with an exact twin in another class (label set `original`), 42 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_42f/summary.md`: stated in the text ("Reconnaissance     16.06") |
| 112 | **78.42%** | share of Overlap-Group-1 rows with an exact twin in another class (label set `current`), 34 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_34f/summary.md`: stated in the text ("Overlap-Group-1     78.42") |
| 113 | **78.16%** | share of Overlap-Group-1 rows with an exact twin in another class (label set `current`), 42 raw features | `results/01_protocol_and_headline.md` | section `Source: overlap/pooled_42f/summary.md`: stated in the text ("Overlap-Group-1     78.16") |

## 02 Open-set detection

### Open-set: open-set (Worms + Shellcode, zero-shot)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 114 | **0.223** | max-softmax detection of Worms + Shellcode at 5% false-Unknown, 40 features, 5 seeds (shown at 3 decimals in the table) | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| msp |`, column `detection @5%` |
| 115 | **0.798** | max-softmax unknown AUROC (Worms + Shellcode), 40 features, 5 seeds (shown at 3 decimals in the table) | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| msp |`, column `unknown AUROC` |
| 116 | **0.862** | entropy unknown AUROC, 40 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| entropy*+ |`, column `unknown AUROC` |
| 117 | **0.158** | entropy detection (stricter transferred threshold), 40 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| entropy*+ |`, column `detection @5%` |
| 118 | **0.059** | max-softmax realised false-Unknown on the official test (target 0.05), 40 features, 5 seeds (shown at 3 decimals in the table) | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| msp |`, column `test` |
| 119 | **0.436** | isolation forest alone, unknown AUROC (below chance), 40 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| iforest |`, column `unknown AUROC` |
| 120 | **0.744** | max-softmax pseudo-unknown validation AUROC, 40 features, 5 seeds (shown at 3 decimals in the table) | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| msp |`, column `pseudo-unknown AUROC` |
| 121 | **0.343** | max-softmax detection, 45 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| msp |`, column `detection @5%` |
| 122 | **0.829** | max-softmax unknown AUROC, 45 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| msp |`, column `unknown AUROC` |
| 123 | **0.333** | max-softmax detection, 48 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| msp |`, column `detection @5%` |
| 124 | **0.834** | max-softmax unknown AUROC, 48 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| msp |`, column `unknown AUROC` |
| 125 | **0.881** | entropy unknown AUROC, 48 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| entropy+ |`, column `unknown AUROC` |
| 126 | **0.302** | entropy detection, 48 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| entropy+ |`, column `detection @5%` |
| 127 | **0.187** | validation-selected iforest+entropy:max detection, 48 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| iforest+entropy:max* |`, column `detection @5%` |
| 128 | **0.810** | validation-selected iforest+entropy:max unknown AUROC, 48 features, 5 seeds | `results/02_novelty1_open_set.md` | section `Source: open_set_step1_40f_45f_48f.md`: table row starting `| iforest+entropy:max* |`, column `unknown AUROC` |

### Open-set: leave-one-class-out (40 features, max-softmax)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 129 | **0.041** | Worms held out: detection (hardest class) | `results/02_novelty1_open_set.md` | section `Source: open_set_step2_40f_48f.md`: table row starting `| Worms | 171 | 0.08 | msp |`, column `detection @5%` |
| 130 | **0.632** | Worms held out: AUROC | `results/02_novelty1_open_set.md` | section `Source: open_set_step2_40f_48f.md`: table row starting `| Worms | 171 | 0.08 | msp |`, column `AUROC` |
| 131 | **0.262** | Fuzzers held out: share flagged or called an attack | `results/02_novelty1_open_set.md` | section `Source: open_set_step2_40f_48f.md`: table row starting `| Fuzzers | 20960 | 0.19 | msp |`, column `flagged or called attack` |
| 132 | **0.123** | Exploits held out: detection | `results/02_novelty1_open_set.md` | section `Source: open_set_step2_40f_48f.md`: table row starting `| Exploits | 27434 | 0.07 | msp |`, column `detection @5%` |
| 133 | **0.400** | Generic held out: detection (easiest) | `results/02_novelty1_open_set.md` | section `Source: open_set_step2_40f_48f.md`: table row starting `| Generic | 7599 | 0.05 | msp |`, column `detection @5%` |
| 134 | **0.374** | Overlap-Group-1 (trio) held out: detection | `results/02_novelty1_open_set.md` | section `Source: open_set_step2_40f_48f.md`: table row starting `| Overlap-Group-1 (all three) | 9412 | 0.53 | msp |`, column `detection @5%` |
| 135 | **0.78** | Analysis: share of rows with an exact twin in the known data (shown at 2 decimals in the table) | `results/02_novelty1_open_set.md` | section `Source: open_set_step2_40f_48f.md`: table row starting `| Analysis | 2032 | 0.78 | msp |`, column `exact twin share` |

### Open-set: alert FPR and review queue (5% target)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 136 | **0.289** | alert FPR OFF, max-softmax, 40 features, Worms + Shellcode held out | `results/02_novelty1_open_set.md` | section `Source: open_set_step3_40f_45f_48f.md`: table row containing `| 5.0% |`, column `alert FPR OFF` (heading `## 40f: msp`) |
| 137 | **0.311** | alert FPR ON, max-softmax, 40 features, Worms + Shellcode held out | `results/02_novelty1_open_set.md` | section `Source: open_set_step3_40f_45f_48f.md`: table row containing `| 5.0% |`, column `alert FPR ON` (heading `## 40f: msp`) |
| 138 | **0.254** | confident-alert FPR, max-softmax, 40 features, Worms + Shellcode held out | `results/02_novelty1_open_set.md` | section `Source: open_set_step3_40f_45f_48f.md`: table row containing `| 5.0% |`, column `confident-alert FPR` (heading `## 40f: msp`) |
| 139 | **0.057** | review rate on Normal, max-softmax, 40 features, Worms + Shellcode held out | `results/02_novelty1_open_set.md` | section `Source: open_set_step3_40f_45f_48f.md`: table row containing `| 5.0% |`, column `review rate on Normal` (heading `## 40f: msp`) |
| 140 | **0.878** | false alerts that skip review, max-softmax, 40 features, Worms + Shellcode held out | `results/02_novelty1_open_set.md` | section `Source: open_set_step3_40f_45f_48f.md`: table row containing `| 5.0% |`, column `false alerts that skip review` (heading `## 40f: msp`) |
| 141 | **0.955** | zero-day catch, max-softmax, 40 features, Worms + Shellcode held out | `results/02_novelty1_open_set.md` | section `Source: open_set_step3_40f_45f_48f.md`: table row containing `| 5.0% |`, column `zero-day catch` (heading `## 40f: msp`) |
| 142 | **0.223** | zero-day flagged Unknown, max-softmax, 40 features, Worms + Shellcode held out | `results/02_novelty1_open_set.md` | section `Source: open_set_step3_40f_45f_48f.md`: table row containing `| 5.0% |`, column `zero-day flagged Unknown` (heading `## 40f: msp`) |
| 143 | **0.121** | confident-alert FPR at the 30% target (entropy, 40 features): the cost of halving it | `results/02_novelty1_open_set.md` | section `Source: open_set_step3_40f_45f_48f.md`: table row containing `| 30.0% |`, column `confident-alert FPR` (heading `## 40f: entropy`) |

### Open-set: where the 40 -> 48 gain comes from

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 144 | **0.172** | max-softmax detection without the 7 window-count ct_* columns (41 features) | `results/02_novelty1_open_set.md` | section `Source: open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.md`: table row starting `| 41f | msp |`, column `detection @5%` |
| 145 | **0.171** | same without every ct_* column (38 features) | `results/02_novelty1_open_set.md` | section `Source: open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.md`: table row starting `| 38f | msp |`, column `detection @5%` |
| 146 | **0.340** | 48-pool 30-feature tier (keeps two window columns) | `results/02_novelty1_open_set.md` | section `Source: open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.md`: table row starting `| 48f_t30 | msp |`, column `detection @5%` |
| 147 | **0.193** | 48-pool 15-feature tier (no window column) | `results/02_novelty1_open_set.md` | section `Source: open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.md`: table row starting `| 48f_t15 | msp |`, column `detection @5%` |

### Open-set: zero-day set

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 148 | **1,627** | Zero-day flows after deduplication = Shellcode 1,456 + Worms 171 | `results/02_novelty1_open_set.md` | section `Source: task_4_conclusion.md`: stated in the text ("1,627 = Shellcode 1,456") |

### Open-set boosts: calibration (rotation means)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 149 | **0.213** | max-softmax rotation-mean detection, 40 features (baseline) | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_calibration_40f_48f.md`: table row containing `| msp |`, column `rotation mean detection` (heading `## calibration (40f`) |
| 150 | **0.266** | entropy rotation-mean detection, 40 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_calibration_40f_48f.md`: table row containing `| entropy |`, column `rotation mean detection` (heading `## calibration (40f`) |
| 151 | **0.276** | temperature-scaled entropy rotation-mean detection, 40 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_calibration_40f_48f.md`: table row containing `| entropy_cal |`, column `rotation mean detection` (heading `## calibration (40f`) |
| 152 | **0.234** | max-softmax rotation-mean detection, 48 features (baseline) | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_calibration_40f_48f.md`: table row containing `| msp |`, column `rotation mean detection` (heading `## calibration (48f`) |
| 153 | **0.304** | temperature-scaled entropy rotation-mean detection, 48 features (the one clear gain in the full known set) | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_calibration_40f_48f.md`: table row containing `| entropy_cal |`, column `rotation mean detection` (heading `## calibration (48f`) |
| 154 | **yes** | calibrated entropy clearly beats max-softmax under the declared rule, 48 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_calibration_40f_48f.md`: table row containing `| entropy_cal |`, column `clearly beats` (heading `## calibration (48f`) |

### Open-set boosts: outlier exposure + combination

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 155 | **0.128** | max-softmax of the model trained without two classes, rotation-mean detection, 40 features (baseline in this setting) | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_combo_40f_48f.md`: table row containing `| noP_msp |`, column `rotation mean detection` (heading `## combo (40f`) |
| 156 | **0.268** | rank-average of ensemble MI and P(Unknown), rotation-mean detection, 40 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_combo_40f_48f.md`: table row containing `| combo |`, column `rotation mean detection` (heading `## combo (40f`) |
| 157 | **0.209** | max-softmax of the model trained without two classes, 48 features (baseline) | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_combo_40f_48f.md`: table row containing `| noP_msp |`, column `rotation mean detection` (heading `## combo (48f`) |
| 158 | **0.335** | rank-average of ensemble MI and P(Unknown), 48 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_combo_40f_48f.md`: table row containing `| combo |`, column `rotation mean detection` (heading `## combo (48f`) |
| 159 | **0.842** | P(Unknown) rotation-mean AUROC, 40 features (best AUROC of any score) | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_combo_40f_48f.md`: table row containing `| oe_pu |`, column `rotation mean AUROC` (heading `## combo (40f`) |
| 160 | **0.200** | entropy of the model trained without the two classes, rotation-mean detection, 40 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_combo_40f_48f.md`: table row containing `| noP_entropy |`, column `rotation mean detection` (heading `## combo (40f`) |

### Open-set boosts: isolation-forest sign check

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 161 | **0.672** | isolation-forest AUROC, known attacks vs Normal (official test), 40 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_iforest_40f_48f.md`: table row containing `| iforest |`, column `known attacks vs Normal` (heading `(40f`) |
| 162 | **0.724** | same, 48 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_iforest_40f_48f.md`: table row containing `| iforest |`, column `known attacks vs Normal` (heading `(48f`) |
| 163 | **0.407** | Shellcode mean percentile among known test flows (looks like an inlier), 40 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_iforest_40f_48f.md`: table row containing `| iforest |`, column `Shellcode` (heading `(40f`) |
| 164 | **0.684** | Worms mean percentile, 40 features | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_iforest_40f_48f.md`: table row containing `| iforest |`, column `Worms` (heading `(40f`) |
| 165 | **0.411** | Mahalanobis AUROC, known attacks vs Normal, 40 features (ranks attacks below Normal) | `results/02_novelty1_open_set.md` | section `Source: open_set_boost_iforest_40f_48f.md`: table row containing `| maha |`, column `known attacks vs Normal` (heading `(40f`) |

### Open-set boosts: pseudo-unknown selection

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 166 | **0.818** | ensemble MI: mean pseudo-unknown validation AUROC over seeds and inner classes, 40 features | `results/02_novelty1_open_set.md` | section `Source: task_4_conclusion.md`: stated in the text ("0.818 / 0.815 at 40 features") |
| 167 | **0.815** | P(Unknown): mean pseudo-unknown validation AUROC, 40 features | `results/02_novelty1_open_set.md` | section `Source: task_4_conclusion.md`: stated in the text ("0.818 / 0.815 at 40 features") |
| 168 | **0.841** | ensemble MI, 48 features | `results/02_novelty1_open_set.md` | section `Source: task_4_conclusion.md`: stated in the text ("0.841 / 0.869 at 48") |
| 169 | **0.869** | P(Unknown), 48 features | `results/02_novelty1_open_set.md` | section `Source: task_4_conclusion.md`: stated in the text ("0.841 / 0.869 at 48") |

## 03 Explanations and narratives

### Explanations: SHAP additivity

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 170 | **1.39e-05** | largest SHAP additivity error over about 179,000 flows (45-feature pool, whole tier); every flow within 1e-3 | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 45f | 45 |`, column `maximum error` (heading `Step 1`) |

### Explanations: faithfulness (top-5 SHAP minus random removal, probability drop)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 171 | **0.512** | 40-feature pool, 40-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 40f | 40 | 40 |`, column `difference` (heading `Primary metric: probability drop`) |
| 172 | **0.501** | 45-feature pool, 45-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 45f | 45 | 45 |`, column `difference` (heading `Primary metric: probability drop`) |
| 173 | **0.553** | 48-feature pool, 48-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 48f | 48 | 48 |`, column `difference` (heading `Primary metric: probability drop`) |
| 174 | **0.466** | 40-feature pool, 30-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 40f | 30 | 30 |`, column `difference` (heading `Primary metric: probability drop`) |
| 175 | **0.429** | 45-feature pool, 30-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 45f | 30 | 30 |`, column `difference` (heading `Primary metric: probability drop`) |
| 176 | **0.489** | 48-feature pool, 30-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 48f | 30 | 30 |`, column `difference` (heading `Primary metric: probability drop`) |
| 177 | **0.333** | 40-feature pool, 15-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 40f | 15 | 15 |`, column `difference` (heading `Primary metric: probability drop`) |
| 178 | **0.344** | 45-feature pool, 15-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 45f | 15 | 15 |`, column `difference` (heading `Primary metric: probability drop`) |
| 179 | **0.340** | 48-feature pool, 15-feature tier, official-test flows (mean of 5 seeds) | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 48f | 15 | 15 |`, column `difference` (heading `Primary metric: probability drop`) |

### Explanations: faithfulness (deletion curve, 40 features, k = 5, median baseline)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 180 | **0.619** | removing the top-5 SHAP features lowers the predicted-class probability by | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 40f | 5 |`, column `top SHAP` (heading `baseline = training median`) |
| 181 | **0.182** | removing 5 random features lowers it by | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 40f | 5 |`, column `random` (heading `baseline = training median`) |
| 182 | **0.022** | removing the 5 least important lowers it by | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 40f | 5 |`, column `least important` (heading `baseline = training median`) |
| 183 | **0.860** | share of flows whose predicted class flips after removing the top 5 SHAP features | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 40f | 5 |`, column `top: class flips` (heading `baseline = training median`) |
| 184 | **0.280** | same after removing 5 random features | `results/03_novelty2_explanations.md` | section `Source: xai_faithfulness_40f_45f_48f.md`: table row containing `| 40f | 5 |`, column `random: class flips` (heading `baseline = training median`) |

### Explanations: narrative audit

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 185 | **0.757** | (f) cue direction agrees with the SHAP-vs-value trend on training flows, 40 features | `results/03_novelty2_explanations.md` | section `Source: xai_audit_40f_48f.md`: table row containing `(f) cue direction agrees`, column `40f` |
| 186 | **0.722** | (f) same, 48 features | `results/03_novelty2_explanations.md` | section `Source: xai_audit_40f_48f.md`: table row containing `(f) cue direction agrees`, column `48f` |
| 187 | **1.000** | (a)-(e) correctness checks, each, 40 and 48 features (2,000 audited narratives) | `results/03_novelty2_explanations.md` | section `Source: xai_audit_40f_48f.md`: table row containing `(e) no false statement`, column `40f` |
| 188 | **46.9%** | cited numeric features that read 'typical', 40 features | `results/03_novelty2_explanations.md` | section `Source: xai_audit_40f_48f.md`: stated in the text ("of the cited numeric features 46.9% carry the cue") |
| 189 | **35.7%** | cited numeric features that read 'typical', 48 features | `results/03_novelty2_explanations.md` | section `Source: xai_audit_40f_48f.md`: stated in the text ("of the cited numeric features 35.7% carry the cue") |

### Explanations: dashboard end to end

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 190 | **64** | flows of sample_flows.csv for which the API output equals an independent computation on every field | `results/03_novelty2_explanations.md` | section `Source: task_5_conclusion.md`: stated in the text ("matches an independent computation") |

### Narratives and false positives: class-relative narrative

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 191 | **0.452** | cited numeric features that read 'typical', classic narrative, 40 features (held-out official-test sample) | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `cited numeric features read "typical"`, column `classic` (heading `## 40f`) |
| 192 | **0.000** | same, class-relative narrative, 40 features (held-out official-test sample) | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `cited numeric features read "typical"`, column `class-relative` (heading `## 40f`) |
| 193 | **0.365** | same, classic, 48 features, 48 features (held-out official-test sample) | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `cited numeric features read "typical"`, column `classic` (heading `## 48f`) |
| 194 | **0.000** | same, class-relative, 48 features, 48 features (held-out official-test sample) | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `cited numeric features read "typical"`, column `class-relative` (heading `## 48f`) |
| 195 | **4.108** | features cited per narrative, classic, 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `features cited per narrative`, column `classic` (heading `## 40f`) |
| 196 | **2.558** | features cited per narrative, class-relative, 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `features cited per narrative`, column `class-relative` (heading `## 40f`) |
| 197 | **4.018** | features cited per narrative, classic, 48 features, 48 features | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `features cited per narrative`, column `classic` (heading `## 48f`) |
| 198 | **2.714** | features cited per narrative, class-relative, 48 features, 48 features | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `features cited per narrative`, column `class-relative` (heading `## 48f`) |
| 199 | **0.780** | (f) cue-direction agreement (unchanged by the new wording), 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `(f) cue direction`, column `class-relative` (heading `## 40f`) |
| 200 | **0.733** | (f) cue-direction agreement, 48 features | `results/03_novelty2_explanations.md` | section `Source: narrative_test_40f_48f.md`: table row containing `(f) cue direction`, column `class-relative` (heading `## 48f`) |

### Narratives and false positives: false-positive explanations

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 201 | **0.184** | faithfulness difference (top SHAP minus random, k = 5), correctly predicted Normal (TN), 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_falsepos_40f_48f.md`: table row containing `| TN |`, column `difference` (heading `## 40f`) |
| 202 | **0.349** | same, false-positive Normal predicted as an attack (FP-attack), 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_falsepos_40f_48f.md`: table row containing `| FP-attack |`, column `difference` (heading `## 40f`) |
| 203 | **0.359** | same, FP-Fuzzers, 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_falsepos_40f_48f.md`: table row containing `| FP-Fuzzers |`, column `difference` (heading `## 40f`) |
| 204 | **0.435** | same, true Fuzzers (TP-Fuzzers), 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_falsepos_40f_48f.md`: table row containing `| TP-Fuzzers |`, column `difference` (heading `## 40f`) |
| 205 | **0.701** | raw confidence on FP-Fuzzers flows, 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_falsepos_40f_48f.md`: table row containing `| FP-Fuzzers |`, column `raw confidence` (heading `## 40f`) |
| 206 | **0.771** | raw confidence on true Fuzzers, 40 features | `results/03_novelty2_explanations.md` | section `Source: narrative_falsepos_40f_48f.md`: table row containing `| TP-Fuzzers |`, column `raw confidence` (heading `## 40f`) |
| 207 | **0.632** | AUROC of 1 - raw confidence for FP-Fuzzers vs TP-Fuzzers, 40 features (weak separation) | `results/03_novelty2_explanations.md` | section `Source: narrative_falsepos_40f_48f.md`: table row containing `1 - raw confidence`, column `AUROC` (heading `## 40f`) |

## 04 Feature tiers and stability

### Feature tiers: tiers

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 208 | **0.7113** | macro F1, 40-feature pool, 40-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 40 |`, column `macro F1` |
| 209 | **0.7141** | macro F1, 40-feature pool, 30-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 30 |`, column `macro F1` |
| 210 | **0.6973** | macro F1, 40-feature pool, 20-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 20 |`, column `macro F1` |
| 211 | **0.6986** | macro F1, 40-feature pool, 15-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 15 |`, column `macro F1` |
| 212 | **0.7065** | macro F1, 45-feature pool, 45-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 45 |`, column `macro F1` |
| 213 | **0.7057** | macro F1, 45-feature pool, 30-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 30 |`, column `macro F1` |
| 214 | **0.6976** | macro F1, 45-feature pool, 20-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 20 |`, column `macro F1` |
| 215 | **0.6972** | macro F1, 45-feature pool, 15-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 15 |`, column `macro F1` |
| 216 | **0.7126** | macro F1, 48-feature pool, 48-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 48 |`, column `macro F1` |
| 217 | **0.7129** | macro F1, 48-feature pool, 30-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 30 |`, column `macro F1` |
| 218 | **0.7063** | macro F1, 48-feature pool, 20-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 20 |`, column `macro F1` |
| 219 | **0.7067** | macro F1, 48-feature pool, 15-feature tier (official split, block-grouped validation) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 15 |`, column `macro F1` |
| 220 | **8.9** | Welch z of the macro-F1 drop, 40-pool 20-feature tier vs full (shown at 1 decimal in the table) | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 20 |`, column `z` |
| 221 | **0.1866** | open-set detection, 40-pool 20-feature tier | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 20 |`, column `open-set det.` |
| 222 | **0.2311** | open-set detection, 40-pool full tier | `results/04_novelty3_feature_tiers.md` | section `Source: tier_summary_xgboost.md`: table row starting `| 40 |`, column `open-set det.` |

### Feature tiers: stability

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 223 | **0.974** | SHAP rank correlation, 48-feature tier vs 30-feature tier (same seed) (shown at 3 decimals in the table) | `results/04_novelty3_feature_tiers.md` | section `Source: stability_xgboost.md`: table row starting `| tier_pair | 48 | 30 |`, column `Spearman` |
| 224 | **0.916** | SHAP rank correlation, 48-feature tier vs 15-feature tier (shown at 3 decimals in the table) | `results/04_novelty3_feature_tiers.md` | section `Source: stability_xgboost.md`: table row starting `| tier_pair | 48 | 15 |`, column `Spearman` |
| 225 | **0.975** | noise floor: same 48-feature tier retrained under another seed (shown at 3 decimals in the table) | `results/04_novelty3_feature_tiers.md` | section `Source: stability_xgboost.md`: table row starting `| same_tier_seeds | 48 |`, column `Spearman` |
| 226 | **0.977** | SHAP rank correlation, 40-feature tier vs 30-feature tier within the 48-feature pool (shown at 3 decimals in the table) | `results/04_novelty3_feature_tiers.md` | section `Source: stability_xgboost.md`: table row starting `| tier_pair | 40 | 30 |`, column `Spearman` |

## 05 Cross-dataset

### Cross-dataset: zero-shot (leak-free)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 227 | **0.485** | UNSW -> CIC AUROC, 14 common features, ZERO-SHOT | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| common_all |`, column `AUROC` (heading `## UNSW -> CIC`) |
| 228 | **0.578** | CIC -> UNSW AUROC (degenerate in 4 of 5 runs) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| common_all |`, column `AUROC` (heading `## CIC -> UNSW`) |
| 229 | **0.975** | within-dataset reference balanced accuracy, CIC (leak-free) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| within_dataset_reference |`, column `balanced accuracy` (heading `## UNSW -> CIC`) |
| 230 | **0.896** | within-dataset reference balanced accuracy, UNSW (leak-free) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| within_dataset_reference |`, column `balanced accuracy` (heading `## CIC -> UNSW`) |
| 231 | **0.786** | UNSW -> CIC FPR at the source 95%-detection threshold | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| common_all |`, column `FPR at the 95%-detection threshold` (heading `## UNSW -> CIC`) |
| 232 | **0.926** | UNSW -> CIC FPR at exactly 95% detection | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| common_all |`, column `FPR at exactly 95% detection` (heading `## UNSW -> CIC`) |
| 233 | **0.690** | UNSW -> CIC predicted attack share (CIC is 80% benign) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| common_all |`, column `predicted attack share` (heading `## UNSW -> CIC`) |
| 234 | **0.003** | CIC -> UNSW predicted attack share | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| common_all |`, column `predicted attack share` (heading `## CIC -> UNSW`) |
| 235 | **+0.017** | stable minus random subsets, AUROC, UNSW -> CIC: better in 2 of 5 seeds; 95% interval -0.064, +0.097 | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: stated in the text ("Stable against random subsets of the same size (AUROC): bett...") |
| 236 | **2831** | CIC blocks of 1,000 consecutive rows in file order | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step1_zero_shot.md`: table row containing `| CIC |`, column `blocks` (heading `Block class mix`) |

### Cross-dataset: diagnostic

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 237 | **0.52 +/- 0.05** | SHAP importance rank agreement, UNSW-trained vs CIC-trained model, Spearman over 5 seeds (the conclusion prints +/- 0.06: rounding slip, raw std 0.0548) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step2_diagnostic.md`: stated in the text ("Spearman 0.52 +/- 0.05 over 5 seeds") |
| 238 | **0.518** | same, mean of the five per-seed Spearman values | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_diagnostic_importance_agreement.csv` (rendered table): mean of the row `spearman_importance` over the seeds |
| 239 | **7 point the same way** | common features whose attack-vs-normal AUROC points the same way in both datasets (7 of 14; 11 of 14 are near 0.5 in at least one) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step2_diagnostic.md`: stated in the text ("Of 14 features: 7 point the same way, 7 do not, 11 are absen...") |

### Cross-dataset: alignment (TRANSDUCTIVE)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 240 | **0.785** | UNSW -> CIC AUROC after per-dataset standardisation (baseline 0.485) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step3_align.md`: table row containing `| per_dataset_standardisation |`, column `AUROC` (heading `## UNSW -> CIC`) |
| 241 | **0.410** | UNSW -> CIC FPR at exactly 95% detection after standardisation (baseline 0.926) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step3_align.md`: table row containing `| per_dataset_standardisation |`, column `FPR at exactly 95% detection` (heading `## UNSW -> CIC`) |
| 242 | **0.359** | detection at the source threshold after standardisation (the threshold no longer transfers) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step3_align.md`: table row containing `| per_dataset_standardisation |`, column `detection at that threshold` (heading `## UNSW -> CIC`) |
| 243 | **0.720** | UNSW -> CIC AUROC after quantile mapping | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step3_align.md`: table row containing `| quantile_mapping |`, column `AUROC` (heading `## UNSW -> CIC`) |

### Cross-dataset: few-shot, UNSW -> CIC (random selection, 25 runs per cell)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 244 | **0.508** | target-only FPR at k=100 | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step4_fewshot.md`: table row containing `| random |` + `| 100 |` + `| target_only |`, column `FPR at threshold` (heading `## UNSW -> CIC`) |
| 245 | **0.169** | target-only FPR at k=500 | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step4_fewshot.md`: table row containing `| random |` + `| 500 |` + `| target_only |`, column `FPR at threshold` (heading `## UNSW -> CIC`) |
| 246 | **0.096** | target-only FPR at k=1,000 (FPR <= 0.15 at detection 0.945) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step4_fewshot.md`: table row containing `| random |` + `| 1000 |` + `| target_only |`, column `FPR at threshold` (heading `## UNSW -> CIC`) |
| 247 | **0.187** | source+target FPR at k=1,000 (the source data does not help) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step4_fewshot.md`: table row containing `| random |` + `| 1000 |` + `| source+target |`, column `FPR at threshold` (heading `## UNSW -> CIC`) |
| 248 | **0.022** | target-only FPR at k=5,000 | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step4_fewshot.md`: table row containing `| random |` + `| 5000 |` + `| target_only |`, column `FPR at threshold` (heading `## UNSW -> CIC`) |
| 249 | **0.981** | target-only AUROC at k=1,000 | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step4_fewshot.md`: table row containing `| random |` + `| 1000 |` + `| target_only |`, column `AUROC` (heading `## UNSW -> CIC`) |

### Cross-dataset: few-shot, CIC -> UNSW (random selection, 25 runs per cell)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 250 | **0.292** | source+target FPR at k=1,000 (UNSW never reaches 0.15) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step4_fewshot.md`: table row containing `| random |` + `| 1000 |` + `| source+target |`, column `FPR at threshold` (heading `## CIC -> UNSW`) |
| 251 | **0.224** | FPR at k=10,000 (best of the curve; the leak-free reference itself is 0.210) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_step4_fewshot.md`: table row containing `| random |` + `| 10000 |` + `| target_only |`, column `FPR at threshold` (heading `## CIC -> UNSW`) |

### Older cross-dataset run (superseded by the leak-free study)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 252 | **0.38** | UNSW -> CIC macro F1, common_all, with the earlier random-split protocol | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_results.csv` (rendered table): row with strategy = common_all, train = UNSW, test = CIC, column `f1` |
| 253 | **0.41** | UNSW -> CIC balanced accuracy, common_all | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_results.csv` (rendered table): row with strategy = common_all, train = UNSW, test = CIC, column `balanced_accuracy` |
| 254 | **0.90** | within-dataset reference, UNSW (macro F1) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_results.csv` (rendered table): row with strategy = within_dataset, train = UNSW, test = UNSW, column `f1` |
| 255 | **0.97** | within-dataset reference, CIC (macro F1) | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_results.csv` (rendered table): row with strategy = within_dataset, train = CIC, test = CIC, column `f1` |
| 256 | **0.72** | Kolmogorov-Smirnov statistic of smean between the datasets | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_feature_shift.csv` (rendered table): row with feature = smean, column `ks_statistic` |
| 257 | **0.69** | KS statistic of sbytes | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_feature_shift.csv` (rendered table): row with feature = sbytes, column `ks_statistic` |
| 258 | **0.64** | KS statistic of total_pkts | `results/05_novelty4_cross_dataset.md` | section `Source: cross_dataset_feature_shift.csv` (rendered table): row with feature = total_pkts, column `ks_statistic` |

## 06 False-positive rate and adaptation

### FPR and adaptation: FPR (det95, test)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 259 | **0.2496** | zero-shot flat default, 40 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| flat_default |`, column `det95_test_fpr` |
| 260 | **0.2442** | zero-shot flat default, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| flat_default |`, column `det95_test_fpr` |
| 261 | **0.2434** | zero-shot hierarchical, stage 1 tuned, 40 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| hier_stage1_tuned |`, column `det95_test_fpr` |
| 262 | **0.2466** | zero-shot hierarchical, stage 1 tuned, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| hier_stage1_tuned |`, column `det95_test_fpr` |
| 263 | **0.0940** | few-shot k=5000 (half fit, half threshold), 48 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| retrain_split_f0.5 | few-shot | 5000 |`, column `det95_test_fpr` |
| 264 | **0.1578** | few-shot k=1000, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| retrain_split_f0.5 | few-shot | 1000 |`, column `det95_test_fpr` |
| 265 | **0.2318** | few-shot k=5000, 40 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| retrain_split_f0.5 | few-shot | 5000 |`, column `det95_test_fpr` |
| 266 | **0.2666** | few-shot k=1000, 40 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| retrain_split_f0.5 | few-shot | 1000 |`, column `det95_test_fpr` |
| 267 | **0.9523** | detection reached by the 48-feature k=5000 few-shot run (the 0.094 is read at 0.952, not 0.95) | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| retrain_split_f0.5 | few-shot | 5000 |`, column `det95_test_detection` |

### FPR and adaptation: leakage check (det95 FPR)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 268 | **0.2442** | zero-shot on the same rows, 48 features, k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 48f | 5000 | twins: all evaluation rows (reproduction) - zero-shot |`, column `FPR at ~95% detection` |
| 269 | **0.0958** | few-shot, evaluation rows with no near twin, 48 features, k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 48f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set |`, column `FPR at ~95% detection` |
| 270 | **0.0854** | few-shot, adaptation rows from OTHER row-order blocks (200-row gaps), 48 features, k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 48f | 5000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) |`, column `FPR at ~95% detection` |
| 271 | **0.0851** | few-shot, adaptation rows from the evaluation blocks, 48 features, k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 48f | 5000 | blocks: adaptation rows from the evaluation blocks (within-file) |`, column `FPR at ~95% detection` |
| 272 | **0.1587** | few-shot, no near twin, 48 features, k=1000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 48f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set |`, column `FPR at ~95% detection` |
| 273 | **0.1528** | few-shot, other blocks, 48 features, k=1000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 48f | 1000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) |`, column `FPR at ~95% detection` |
| 274 | **0.2427** | few-shot, other blocks, 40 features, k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 40f | 5000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) |`, column `FPR at ~95% detection` |
| 275 | **0.2025** | few-shot, adaptation rows inside the evaluation blocks, 40 features, k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 40f | 5000 | blocks: adaptation rows from the evaluation blocks (within-file) |`, column `FPR at ~95% detection` |
| 276 | **0.1109** | few-shot without the 3 TTL columns (45 features), k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 45f | 5000 |`, column `FPR at ~95% detection` |
| 277 | **0.2308** | few-shot without the 7 window-count ct_* columns (41 features), k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 41f | 5000 |`, column `FPR at ~95% detection` |
| 278 | **0.2281** | few-shot without every ct_* column (38 features), k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 38f | 5000 |`, column `FPR at ~95% detection` |
| 279 | **0.9318** | detection reached in the other-blocks condition (so FPR at exactly 95% would be higher), 48 features, k=5000 | `results/06_fpr_and_adaptation.md` | section `Source: task_2_6_table_40f_48f_45f_41f_38f.md`: table row starting `| 48f | 5000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) |`, column `detection` |

### FPR and adaptation: shift AUC (seed 42)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 280 | **0.8987** | train-Normal vs test-Normal classifier AUC, random 5-fold CV, 40f | `results/06_fpr_and_adaptation.md` | section `Source: leakage_40f_shift_auc.csv` (rendered table): row with , column `auc_random_cv` |
| 281 | **0.814** | same, CV grouped by 1,000-row blocks, 40f | `results/06_fpr_and_adaptation.md` | section `Source: leakage_40f_shift_auc.csv` (rendered table): row with , column `auc_block_cv` |
| 282 | **0.9291** | train-Normal vs test-Normal classifier AUC, random 5-fold CV, 45f | `results/06_fpr_and_adaptation.md` | section `Source: leakage_45f_shift_auc.csv` (rendered table): row with , column `auc_random_cv` |
| 283 | **0.8356** | same, CV grouped by 1,000-row blocks, 45f | `results/06_fpr_and_adaptation.md` | section `Source: leakage_45f_shift_auc.csv` (rendered table): row with , column `auc_block_cv` |
| 284 | **0.9296** | train-Normal vs test-Normal classifier AUC, random 5-fold CV, 48f | `results/06_fpr_and_adaptation.md` | section `Source: leakage_48f_shift_auc.csv` (rendered table): row with , column `auc_random_cv` |
| 285 | **0.8371** | same, CV grouped by 1,000-row blocks, 48f | `results/06_fpr_and_adaptation.md` | section `Source: leakage_48f_shift_auc.csv` (rendered table): row with , column `auc_block_cv` |

### FPR and adaptation: validation vs test

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 286 | **0.1198** | validation FPR at argmax, RANDOM validation (mean of 5 seeds), 40 features | `results/06_fpr_and_adaptation.md` | section `Source: leakage_40f_validation_blocks.csv` (rendered table): mean of column `val_fpr` over the rows with validation = random_validation |
| 287 | **0.2507** | validation FPR, BLOCK-built validation (1,000-row blocks; mean of 5 seeds), 40 features | `results/06_fpr_and_adaptation.md` | section `Source: leakage_40f_validation_blocks.csv` (rendered table): mean of column `val_fpr` over the rows with validation = block_validation |

### FPR and adaptation: pooled reference

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 288 | **37013** | official-test rows inside the pooled random split's training set | `results/06_fpr_and_adaptation.md` | section `Source: pooled_reference_composition.csv` (rendered table): row with protocol = pooled_random, part = train, source_file = test, column `rows` |

### FPR and adaptation: zero-shot (det95 FPR)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 289 | **0.256** | default (config.yaml), 40 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `default (config.yaml)`, column `det95_test_fpr` (heading `## 40f`) |
| 290 | **0.257** | tuned on block-grouped validation (auc), 40 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `tuned on block-grouped validation (auc)`, column `det95_test_fpr` (heading `## 40f`) |
| 291 | **0.249** | temperature scaling + EM prior correction, 40 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `temperature scaling + EM prior correction`, column `det95_test_fpr` (heading `## 40f`) |
| 292 | **0.254** | declared combination, 40 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `declared combination`, column `det95_test_fpr` (heading `## 40f`) |
| 293 | **0.248** | default (config.yaml), 45 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `default (config.yaml)`, column `det95_test_fpr` (heading `## 45f`) |
| 294 | **0.258** | tuned on block-grouped validation (auc), 45 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `tuned on block-grouped validation (auc)`, column `det95_test_fpr` (heading `## 45f`) |
| 295 | **0.244** | temperature scaling + EM prior correction, 45 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `temperature scaling + EM prior correction`, column `det95_test_fpr` (heading `## 45f`) |
| 296 | **0.249** | declared combination, 45 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `declared combination`, column `det95_test_fpr` (heading `## 45f`) |
| 297 | **0.248** | default (config.yaml), 48 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `default (config.yaml)`, column `det95_test_fpr` (heading `## 48f`) |
| 298 | **0.244** | temperature scaling + EM prior correction, 48 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `temperature scaling + EM prior correction`, column `det95_test_fpr` (heading `## 48f`) |
| 299 | **0.247** | declared combination, 48 features, official split (mean of seeds 42-46) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `declared combination`, column `det95_test_fpr` (heading `## 48f`) |
| 300 | **0.196** | argmax FPR with EM prior correction, 40 features | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `temperature scaling + EM prior correction`, column `argmax_fpr` (heading `## 40f`) |
| 301 | **0.289** | argmax FPR, default, 40 features | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_final_40f_45f_48f.md`: table row containing `default (config.yaml)`, column `argmax_fpr` (heading `## 40f`) |

### FPR and adaptation: few-shot (FPR at exactly 95% detection)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 302 | **0.152** | random selection, k=2,500, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_fewshot_48f_45f_41f.md`: table row containing `random` + `2500`, column `FPR at exactly 95%` (heading `## 48f`) |
| 303 | **0.148** | diverse (k-means) selection, k=2,500, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_fewshot_48f_45f_41f.md`: table row containing `diverse` + `2500`, column `FPR at exactly 95%` (heading `## 48f`) |
| 304 | **0.122** | random selection, k=5,000, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_fewshot_48f_45f_41f.md`: table row containing `random` + `5000`, column `FPR at exactly 95%` (heading `## 48f`) |
| 305 | **0.138** | random selection, k=5,000, 45 features | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_fewshot_48f_45f_41f.md`: table row containing `random` + `5000`, column `FPR at exactly 95%` (heading `## 45f`) |
| 306 | **0.199** | random selection, k=500, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_fewshot_48f_45f_41f.md`: table row containing `random` + `500`, column `FPR at exactly 95%` (heading `## 48f`) |

### FPR and adaptation: few-shot (det95 FPR, threshold on held-out half)

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 307 | **0.089** | random selection, k=5,000, 48 features (the 'about 0.09'; read at a test detection of 0.935) | `results/06_fpr_and_adaptation.md` | section `Source: fpr_study_fewshot_48f_45f_41f.md`: table row containing `random` + `5000`, column `det95 FPR` (heading `## 48f`) |

### FPR and adaptation: side effects

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 308 | **0.071** | ECE after few-shot adaptation (k=5000 split), 48 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| retrain_split_f0.5 | few-shot | 5000 |`, column `ece` |
| 309 | **0.109** | ECE of the default model, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| flat_default |`, column `ece` |
| 310 | **0.796** | accuracy after few-shot adaptation (k=5000 split), 48 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| retrain_split_f0.5 | few-shot | 5000 |`, column `accuracy` |
| 311 | **0.375** | open-set detection after few-shot adaptation, 48 features | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| retrain_split_f0.5 | few-shot | 5000 |`, column `unknown_detection_rate` |
| 312 | **0.214** | argmax FPR of the hierarchical scheme, 40 features (flat default 0.285) | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| hier_default |`, column `false_positive_rate` |
| 313 | **0.03** | open-set detection of the hierarchical scheme, 40 features (flat 0.26) | `results/06_fpr_and_adaptation.md` | section `Source: task_2_5_final_table_40f_48f.md`: table row starting `| hier_default |`, column `unknown_detection_rate` |

### Data

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 314 | **54596** | official-test rows used (known classes) in the 42-feature runs | `results/06_fpr_and_adaptation.md` | section `Source: pooled_reference_composition.csv` (rendered table): row with protocol = official, part = test, source_file = test, column `rows` |
| 315 | **90543** | official training rows (85% of the train file) in the 42-feature runs | `results/06_fpr_and_adaptation.md` | section `Source: pooled_reference_composition.csv` (rendered table): row with protocol = official, part = train, source_file = train, column `rows` |

## Statements in README.md

### Data

| # | value | metric and setting | file | where in the file |
|---|---|---|---|---|
| 316 | **162,745** | rows of the 42-feature UNSW-NB15 files after exact deduplication (257,673 before) = 90,543 + 15,979 + 54,596 official train/val/test rows + 1,627 zero-day flows | `README.md` | the running text: stated in the text ("162,745 after exact deduplication") |

## Where the numbers live now, and what was corrected

**Numbers that now exist only as markdown.** 196 of the 316 entries were backed by a CSV that no longer exists; their values are table cells (or means of rendered per-seed rows) in the numbered files. The removed CSVs were: `accuracy_three_numbers_40f_48f_45f.csv`, `cross_dataset_diagnostic_importance_agreement.csv`, `cross_dataset_feature_shift.csv`, `cross_dataset_results.csv`, `experiment_results.csv`, `explanation_stability.csv`, `feature_selection_baselines_summary.csv`, `headline_full_no_ttl_summary.csv`, `headline_summary.csv`, `label_scheme_comparison.csv`, `leakage_40f_shift_auc.csv`, `leakage_40f_validation_blocks.csv`, `leakage_45f_shift_auc.csv`, `leakage_48f_shift_auc.csv`, `methods_zero_shot_b1_40f_summary.csv`, `open_set_boost_selection_40f_scores.csv`, `open_set_boost_selection_48f_scores.csv`, `open_set_step1_40f.csv`, `open_set_step1_45f.csv`, `open_set_step1_48f.csv`, `open_set_step2_40f.csv`, `open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv`, `operating_point_summary_40f.csv`, `operating_point_summary_48f.csv`, `pooled_reference_composition.csv`, `shift_normal_summary_40f.csv`, `shift_normal_summary_45f.csv`, `shift_normal_summary_48f.csv`, `split_comparison.csv`, `split_summary.csv`, `stability_xgboost_48f.csv`, `task_2_5_final_table_40f_48f.csv`, `task_2_6_table_40f_48f_45f_41f_38f.csv`, `tier_summary_xgboost_40f.csv`, `tier_summary_xgboost_45f.csv`, `tier_summary_xgboost_48f.csv`, `tuned_vs_default.csv`. In addition the 49 small CSV and JSON files rendered into the numbered files (confusion matrices, bootstrap intervals, shift and leakage diagnostics, the earlier single-seed run, tuned hyperparameters and others) exist only as markdown tables.

**Corrected earlier (approved):**

1. The Spearman rank agreement of the UNSW-trained and CIC-trained models was printed as 0.52 +/- 0.06; the data say 0.52 +/- 0.05 (five per-seed values, mean 0.518, std 0.0548). Corrected in the conclusion.
2. The README label-scheme table and the matching PROJECT_PLAN sentences quoted figures with no tracked source. They now quote the tracked figures (`current`, `none`, `wide` from the label-scheme summary; `hierarchical` from the 5-seed method summary) and name their sources; the entries above verify every value.
3. Twin shares in README and PROJECT_PLAN are labelled by origin: the tracked pooled partition (Analysis / Backdoor / DoS 77-85%) against an earlier deduplicated 34-feature run (72-80%, the 34 to 42 feature changes and the partner-class split of the merged group) whose output was never committed. Nothing was regenerated.
4. Test counts in README and PROJECT_PLAN corrected (now 328).

**Still open (not changed, not regenerated):**

- The earlier-run twin figures and the partner-class split in item 3 have no tracked file. `scripts/overlap_analysis.py --partition train|test` would regenerate comparable tables if the owner wants them.
- The failure-list template in `pipelines/run_xai_study.py` used to write 'SHAP ... falls as the value rises' whatever the sign of rho. Fixed in the code (`shap_trend_phrase` in `src/xai/narrative_audit.py`, with a regression test); the committed example file `metrics/xgboost/xai_audit_40f_example_failures.csv` keeps the old `reason` wording, so read its `shap_trend_on_training_rows` column.
- Numbers that live only in running text: the zero-day flow count 1,627 (Shellcode 1,456 + Worms 171) is also in the open-set tables; the CIC block counts 2,831 / 1,308 are in the `Block class mix` table of the cross-dataset tables (1,198 mixed + 110 pure-attack = 1,308).
