# Cleanup manifest (Task 7): what was removed, merged and kept, and why

**Status: the proposal was approved with six edits and applied on branch `cleanup/prune-results` (not merged).** Commits: `77286b8` ledger and manifest, `8536e7a` merges, `1e7ab35` outputs removed, then the documentation commit. Branch from `research/novelty-results` (HEAD `e8b58e4`). Recovery tag: `pre-cleanup-2026-10` on that commit; a zip of the whole `results/` folder (including the untracked folders) is at `D:\Github Projects\_backups\xai-ids-results-pre-cleanup.zip`.

Approved edits: (1) keep one small Task 5 audit narrative sample (`xai_audit_40f_narratives.csv`) and add ten example failures (`xai_audit_40f_example_failures.csv`, four of the "reduced average packet size" style); (2) also delete `cross_dataset_generalization.png`; (3) keep the three notebooks and `normal_fpr_floor_40f_48f.csv`; (4) back up `results/` first; (5) do the 7 merges and verify every source line; (6) fix the Task 6 Spearman rounding, "140 tests" -> 327 and the README label-scheme table, and label the twin shares by origin. The rest of this file is the original classification; where it says "proposed" read "done".

Rule used throughout: delete only what no quoted number, declared protocol, kept script or test, or the dashboard depends on; if the purpose is unclear the file is KEPT and listed under UNSURE. Nothing under `data/raw`, `models_saved`, `results/_local_scratch` or any other gitignored path is touched (they are not tracked). No teammate file is touched (none is tracked: `results/_local_scratch/` is ignored).

| | files | size |
|---|---|---|
| tracked before the cleanup | 575 | 30.00 MB |
| KEEP | 341 | 5.23 MB |
| MERGE (into 7 files; content kept verbatim) | 37 -> 7 | 0.25 MB |
| DELETE | 198 | 24.52 MB |
| UNSURE items, decided: kept (counted in KEEP above) | 4 | 18.5 KB |
| **after the cleanup** (350 tracked files, including the ledger, this manifest, the 7 merged files and the example-failures file) | **350** | **5.63 MB** (before 30.00 MB; DELETE below counts 198 files, 24.52 MB, after the `cross_dataset_generalization.png` edit) |

Code, tests, configs, dashboard, notebooks, data samples and root documents: **no deletions** (details in section 5).

## 1. DELETE: by family

| family | files | size | why it is safe |
|---|---|---|---|
| Confusion-matrix CSVs of the non-default `none` / `wide` label schemes | 16 | 5.8 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| Duplicates / superseded single files | 4 | 4.4 KB | subset of bootstrap_ci_40f_48f_45f.csv (same rows plus the 45-feature pool) |
| Overlap twin tables (4 label schemes; summary.md and best_possible_accuracy.csv kept) | 16 | 5.6 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| Plots: per-tier (15 / 20 / 30 features) and the stale cross-dataset plot | 7 | 0.61 MB | per-tier plot not planned for the report (headline tier 40 kept) |
| Scratch diagnostic: normal_fuzzers_diagnostic/ (Task 2 investigation) | 8 | 16.2 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |
| Task 1 headline / operating point: per-seed rows | 7 | 36.2 KB | per-seed rows; the kept headline_*_summary.csv/.md has mean/std/min/max over the same 5 seeds |
| Task 2.7: per-seed rows (fpr_study_*_runs.csv) | 15 | 0.20 MB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| Task 3 / older tier study: per-seed and per-draw rows | 7 | 33.0 KB | per-draw rows; tier_baselines_summary_xgboost_<N>f.csv (kept) has mean/std/z |
| Task 4.5: per-run, curve, composition, diagnostics and per-seed check rows | 44 | 1.62 MB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| Task 4: per-run, per-flow and curve rows (open_set_*) | 32 | 5.28 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| Task 5.5: narrative texts and failure lists (test / validation) | 5 | 3.17 MB | list of every failing cited feature; the audit summaries (kept) hold the counts per check |
| Task 5: per-sample / per-flow faithfulness rows, audit failure lists, other narrative texts | 13 | 12.87 MB | per-sample / per-flow rows (3.5 MB per pool); xai_faithfulness_40f_45f_48f.md (kept/merged) holds the summary and intervals |
| Task 6: per-run rows (zero-shot, alignment, few-shot, block mix, types) | 6 | 0.52 MB | per-run rows; cross_dataset_step*.md (kept/merged) holds the Task 6 tables |
| Tasks 2.5 / 2.6: per-seed / per-run rows (methods, adaptation, leakage) | 18 | 0.15 MB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |

Every file, with the reason it is safe (the kept summary that carries its numbers or the file that supersedes it):

### Confusion-matrix CSVs of the non-default `none` / `wide` label schemes

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/confusion_matrix_40_official_none.csv` | 0.4 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_40_official_rownorm_none.csv` | 0.6 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_40_official_rownorm_wide.csv` | 0.3 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_40_official_wide.csv` | 0.2 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_40_pooled_random_none_pooled.csv` | 0.4 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_40_pooled_random_rownorm_none_pooled.csv` | 0.6 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_40_pooled_random_rownorm_wide_pooled.csv` | 0.3 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_40_pooled_random_wide_pooled.csv` | 0.2 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_48_official_none_48f.csv` | 0.4 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_48_official_rownorm_none_48f.csv` | 0.6 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_48_official_rownorm_wide_48f.csv` | 0.3 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_48_official_wide_48f.csv` | 0.2 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_48_pooled_random_none_pooled_48f.csv` | 0.4 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_48_pooled_random_rownorm_none_pooled_48f.csv` | 0.6 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_48_pooled_random_rownorm_wide_pooled_48f.csv` | 0.3 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |
| `results/metrics/xgboost/confusion_matrix_48_pooled_random_wide_pooled_48f.csv` | 0.2 KB | confusion matrix of the non-default `none` / `wide` scheme; the default-scheme matrices are kept; scheme comparison is in label_scheme_summary.md |

### Duplicates / superseded single files

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/bootstrap_ci_40f_48f.csv` | 0.5 KB | subset of bootstrap_ci_40f_48f_45f.csv (same rows plus the 45-feature pool) |
| `results/metrics/xgboost/bootstrap_paired_diff_40f_48f.csv` | 0.4 KB | subset of bootstrap_paired_diff_40f_48f_45f.csv (same rows plus the 45-feature pool) |
| `results/metrics/xgboost/evaluation_results.csv` | 1.0 KB | one-row copy of the 40/official row of split_comparison.csv (single seed, superseded by headline_summary) |
| `results/metrics/xgboost/pooled_split_results.csv` | 2.5 KB | per-tier pooled rows, already the pooled_random rows of split_comparison.csv (single seed) |

### Overlap twin tables (4 label schemes; summary.md and best_possible_accuracy.csv kept)

| file | size | reason |
|---|---|---|
| `results/metrics/overlap/pooled_34f/twin_rows_pct_binary.csv` | 0.0 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_34f/twin_rows_pct_current.csv` | 0.3 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_34f/twin_rows_pct_none.csv` | 0.5 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_34f/twin_rows_pct_original.csv` | 0.5 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_34f/twin_vectors_pct_binary.csv` | 0.0 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_34f/twin_vectors_pct_current.csv` | 0.3 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_34f/twin_vectors_pct_none.csv` | 0.5 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_34f/twin_vectors_pct_original.csv` | 0.5 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_42f/twin_rows_pct_binary.csv` | 0.0 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_42f/twin_rows_pct_current.csv` | 0.3 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_42f/twin_rows_pct_none.csv` | 0.5 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_42f/twin_rows_pct_original.csv` | 0.5 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_42f/twin_vectors_pct_binary.csv` | 0.0 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_42f/twin_vectors_pct_current.csv` | 0.3 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_42f/twin_vectors_pct_none.csv` | 0.5 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |
| `results/metrics/overlap/pooled_42f/twin_vectors_pct_original.csv` | 0.5 KB | per-class twin tables for 4 label schemes; `none` and `original` are byte-identical; summary.md (kept) holds the shares |

### Plots: per-tier (15 / 20 / 30 features) and the stale cross-dataset plot

| file | size | reason |
|---|---|---|
| `results/plots/xgboost/confusion_matrix_15.png` | 85.6 KB | per-tier plot not planned for the report (headline tier 40 kept) |
| `results/plots/xgboost/confusion_matrix_20.png` | 86.2 KB | per-tier plot not planned for the report (headline tier 40 kept) |
| `results/plots/xgboost/confusion_matrix_30.png` | 86.5 KB | per-tier plot not planned for the report (headline tier 40 kept) |
| `results/plots/xgboost/cross_dataset_generalization.png` | 35.1 KB | stale: plots the pre-Task-6 random-split run that Task 6 contradicts (approved edit 2) |
| `results/plots/xgboost/roc_curve_15.png` | 0.11 MB | per-tier plot not planned for the report (headline tier 40 kept) |
| `results/plots/xgboost/roc_curve_20.png` | 0.11 MB | per-tier plot not planned for the report (headline tier 40 kept) |
| `results/plots/xgboost/roc_curve_30.png` | 0.10 MB | per-tier plot not planned for the report (headline tier 40 kept) |

### Scratch diagnostic: normal_fuzzers_diagnostic/ (Task 2 investigation)

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/normal_fuzzers_diagnostic/feature_distributions.csv` | 3.6 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |
| `results/metrics/xgboost/normal_fuzzers_diagnostic/feature_distributions_48f.csv` | 4.1 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |
| `results/metrics/xgboost/normal_fuzzers_diagnostic/split_shift_ks.csv` | 1.0 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |
| `results/metrics/xgboost/normal_fuzzers_diagnostic/split_shift_ks_48f.csv` | 1.2 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |
| `results/metrics/xgboost/normal_fuzzers_diagnostic/summary.csv` | 2.3 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |
| `results/metrics/xgboost/normal_fuzzers_diagnostic/summary_48f.csv` | 2.3 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |
| `results/metrics/xgboost/normal_fuzzers_diagnostic/ttl_signature.csv` | 0.8 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |
| `results/metrics/xgboost/normal_fuzzers_diagnostic/ttl_signature_48f.csv` | 0.8 KB | Task 2 investigation tables (feature distributions, TTL signature, KS); no document quotes them; scripts/diagnose_normal_fuzzers.py stays (imported by characterize_shift.py and run_leakage_checks.py) |

### Task 1 headline / operating point: per-seed rows

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/headline_full_no_ttl_seeds.csv` | 6.9 KB | per-seed rows; the kept headline_*_summary.csv/.md has mean/std/min/max over the same 5 seeds |
| `results/metrics/xgboost/headline_seeds.csv` | 12.3 KB | per-seed rows; the kept headline_*_summary.csv/.md has mean/std/min/max over the same 5 seeds |
| `results/metrics/xgboost/headline_tuned_auc_official_seeds.csv` | 6.9 KB | per-seed rows; the kept headline_*_summary.csv/.md has mean/std/min/max over the same 5 seeds |
| `results/metrics/xgboost/headline_tuned_f1_official_seeds.csv` | 6.9 KB | per-seed rows; the kept headline_*_summary.csv/.md has mean/std/min/max over the same 5 seeds |
| `results/metrics/xgboost/operating_point_seeds_40f.csv` | 1.0 KB | per-seed rows; operating_point_summary_<N>f.csv (kept) has mean/std |
| `results/metrics/xgboost/operating_point_seeds_45f.csv` | 1.1 KB | per-seed rows; operating_point_summary_<N>f.csv (kept) has mean/std |
| `results/metrics/xgboost/operating_point_seeds_48f.csv` | 1.0 KB | per-seed rows; operating_point_summary_<N>f.csv (kept) has mean/std |

### Task 2.7: per-seed rows (fpr_study_*_runs.csv)

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/fpr_study_combined_40f_runs.csv` | 3.2 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_combined_45f_runs.csv` | 3.2 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_combined_48f_runs.csv` | 3.2 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_fewshot_41f_runs.csv` | 41.4 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_fewshot_45f_runs.csv` | 41.5 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_fewshot_48f_runs.csv` | 41.4 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_prior_40f_runs.csv` | 8.1 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_prior_45f_runs.csv` | 8.1 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_prior_48f_runs.csv` | 8.1 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_self_40f_runs.csv` | 7.7 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_self_45f_runs.csv` | 7.7 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_self_48f_runs.csv` | 7.7 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_tuned_40f_runs.csv` | 7.0 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_tuned_45f_runs.csv` | 4.3 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |
| `results/metrics/xgboost/fpr_study_tuned_48f_runs.csv` | 7.0 KB | per-seed rows; the Task 2.7 tables (fpr_study_*.md, kept/merged) hold mean/std and paired differences |

### Task 3 / older tier study: per-seed and per-draw rows

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/feature_selection_baselines.csv` | 13.7 KB | per-draw rows (ranked / 10 random / worst-N); feature_selection_baselines_summary.csv (kept) has mean/std/z |
| `results/metrics/xgboost/tier_baselines_xgboost_40f.csv` | 1.1 KB | per-draw rows; tier_baselines_summary_xgboost_<N>f.csv (kept) has mean/std/z |
| `results/metrics/xgboost/tier_baselines_xgboost_45f.csv` | 1.1 KB | per-draw rows; tier_baselines_summary_xgboost_<N>f.csv (kept) has mean/std/z |
| `results/metrics/xgboost/tier_baselines_xgboost_48f.csv` | 1.1 KB | per-draw rows; tier_baselines_summary_xgboost_<N>f.csv (kept) has mean/std/z |
| `results/metrics/xgboost/tier_study_xgboost_40f_runs_pooled.csv` | 4.0 KB | per-seed rows; tier_summary_xgboost_<N>f.csv / tier_summary_xgboost.md (kept) hold mean/std, drop, Welch z |
| `results/metrics/xgboost/tier_study_xgboost_45f_runs_pooled.csv` | 5.8 KB | per-seed rows; tier_summary_xgboost_<N>f.csv / tier_summary_xgboost.md (kept) hold mean/std, drop, Welch z |
| `results/metrics/xgboost/tier_study_xgboost_48f_runs_pooled.csv` | 6.1 KB | per-seed rows; tier_summary_xgboost_<N>f.csv / tier_summary_xgboost.md (kept) hold mean/std, drop, Welch z |

### Task 4.5: per-run, curve, composition, diagnostics and per-seed check rows

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/open_set_boost_calibration_40f_composition.csv` | 15.6 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_calibration_40f_curve.csv` | 47.2 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_calibration_40f_diagnostics.csv` | 4.3 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_calibration_40f_runs.csv` | 57.9 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_calibration_48f_composition.csv` | 15.5 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_calibration_48f_curve.csv` | 47.2 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_calibration_48f_diagnostics.csv` | 4.3 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_calibration_48f_runs.csv` | 57.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_combo_40f_composition.csv` | 15.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_combo_40f_curve.csv` | 58.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_combo_40f_diagnostics.csv` | 6.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_combo_40f_runs.csv` | 77.5 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_combo_48f_composition.csv` | 15.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_combo_48f_curve.csv` | 58.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_combo_48f_diagnostics.csv` | 6.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_combo_48f_runs.csv` | 77.0 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_distance_40f_composition.csv` | 15.1 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_distance_40f_curve.csv` | 46.3 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_distance_40f_runs.csv` | 56.8 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_distance_48f_composition.csv` | 15.0 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_distance_48f_curve.csv` | 46.5 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_distance_48f_runs.csv` | 56.3 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_ensemble_40f_composition.csv` | 19.3 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_ensemble_40f_curve.csv` | 58.8 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_ensemble_40f_runs.csv` | 71.7 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_ensemble_48f_composition.csv` | 19.1 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_ensemble_48f_curve.csv` | 58.7 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_ensemble_48f_runs.csv` | 70.9 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_iforest_40f_checks.csv` | 15.9 KB | per-seed percentiles; open_set_boost_iforest_40f_48f.md (kept/merged) holds every number quoted |
| `results/metrics/xgboost/open_set_boost_iforest_48f_checks.csv` | 15.9 KB | per-seed percentiles; open_set_boost_iforest_40f_48f.md (kept/merged) holds every number quoted |
| `results/metrics/xgboost/open_set_boost_oe_40f_composition.csv` | 12.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_oe_40f_curve.csv` | 47.0 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_oe_40f_diagnostics.csv` | 6.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_oe_40f_runs.csv` | 62.5 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_oe_48f_composition.csv` | 12.3 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_oe_48f_curve.csv` | 47.0 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_oe_48f_diagnostics.csv` | 6.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_oe_48f_runs.csv` | 62.1 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_perclass_40f_composition.csv` | 15.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_perclass_40f_curve.csv` | 44.3 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_perclass_40f_runs.csv` | 56.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_perclass_48f_composition.csv` | 15.4 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_perclass_48f_curve.csv` | 44.2 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |
| `results/metrics/xgboost/open_set_boost_perclass_48f_runs.csv` | 55.6 KB | per-run / curve / composition rows; open_set_boost_<idea>_40f_48f.md (kept/merged) holds the Task 4.5 tables |

### Task 4: per-run, per-flow and curve rows (open_set_*)

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/open_set_curve_38f.csv` | 0.15 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_curve_40f.csv` | 0.15 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_curve_41f.csv` | 0.15 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_curve_45f.csv` | 0.16 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_curve_48f.csv` | 0.15 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_curve_48f_t15.csv` | 0.16 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_curve_48f_t30.csv` | 0.16 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_rotation_40f_runs.csv` | 0.12 MB | per-run / per-flow rotation rows; open_set_step2*.md (kept) holds the nine-class table |
| `results/metrics/xgboost/open_set_rotation_40f_sources.csv` | 1.43 MB | per-run / per-flow rotation rows; open_set_step2*.md (kept) holds the nine-class table |
| `results/metrics/xgboost/open_set_rotation_48f_runs.csv` | 0.12 MB | per-run / per-flow rotation rows; open_set_step2*.md (kept) holds the nine-class table |
| `results/metrics/xgboost/open_set_rotation_48f_sources.csv` | 1.42 MB | per-run / per-flow rotation rows; open_set_step2*.md (kept) holds the nine-class table |
| `results/metrics/xgboost/open_set_runs_38f.csv` | 30.0 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_runs_40f.csv` | 30.5 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_runs_41f.csv` | 29.7 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_runs_45f.csv` | 29.7 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_runs_48f.csv` | 29.6 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_runs_48f_t15.csv` | 30.8 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_runs_48f_t30.csv` | 30.6 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_selection_38f.csv` | 7.5 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_selection_40f.csv` | 7.5 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_selection_41f.csv` | 7.5 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_selection_45f.csv` | 7.5 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_selection_48f.csv` | 7.5 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_selection_48f_t15.csv` | 8.0 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_selection_48f_t30.csv` | 8.0 KB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_sources_38f.csv` | 0.12 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_sources_40f.csv` | 0.12 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_sources_41f.csv` | 0.12 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_sources_45f.csv` | 0.12 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_sources_48f.csv` | 0.12 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_sources_48f_t15.csv` | 0.13 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |
| `results/metrics/xgboost/open_set_sources_48f_t30.csv` | 0.13 MB | per-run / per-flow rows; open_set_step*.md/.csv (kept) hold the Task 4 tables |

### Task 5.5: narrative texts and failure lists (test / validation)

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/narrative_test_40f_failures.csv` | 0.56 MB | list of every failing cited feature; the audit summaries (kept) hold the counts per check |
| `results/metrics/xgboost/narrative_test_48f_failures.csv` | 0.88 MB | list of every failing cited feature; the audit summaries (kept) hold the counts per check |
| `results/metrics/xgboost/narrative_test_48f_narratives.csv` | 1.37 MB | 2,000 / 1,150 narrative texts per file; summaries (kept) hold every check; not read by any kept script |
| `results/metrics/xgboost/narrative_validation_40f_failures.csv` | 0.10 MB | list of every failing cited feature; the audit summaries (kept) hold the counts per check |
| `results/metrics/xgboost/narrative_validation_40f_narratives.csv` | 0.26 MB | 2,000 / 1,150 narrative texts per file; summaries (kept) hold every check; not read by any kept script |

### Task 5: per-sample / per-flow faithfulness rows, audit failure lists, other narrative texts

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/xai_audit_40f_failures.csv` | 0.20 MB | list of every failing cited feature; the audit summaries (kept) hold the counts per check |
| `results/metrics/xgboost/xai_audit_48f_failures.csv` | 0.32 MB | list of every failing cited feature; the audit summaries (kept) hold the counts per check |
| `results/metrics/xgboost/xai_audit_48f_narratives.csv` | 0.43 MB | 2,000 / 1,150 narrative texts per file; summaries (kept) hold every check; not read by any kept script |
| `results/metrics/xgboost/xai_audit_validation_40f_failures.csv` | 0.18 MB | list of every failing cited feature; the audit summaries (kept) hold the counts per check |
| `results/metrics/xgboost/xai_audit_validation_40f_narratives.csv` | 0.42 MB | 2,000 / 1,150 narrative texts per file; summaries (kept) hold every check; not read by any kept script |
| `results/metrics/xgboost/xai_audit_validation_48f_failures.csv` | 0.30 MB | list of every failing cited feature; the audit summaries (kept) hold the counts per check |
| `results/metrics/xgboost/xai_audit_validation_48f_narratives.csv` | 0.43 MB | 2,000 / 1,150 narrative texts per file; summaries (kept) hold every check; not read by any kept script |
| `results/metrics/xgboost/xai_faithfulness_40f_flowdiffs.csv` | 2.57 MB | per-sample / per-flow rows (3.5 MB per pool); xai_faithfulness_40f_45f_48f.md (kept/merged) holds the summary and intervals |
| `results/metrics/xgboost/xai_faithfulness_40f_runs.csv` | 0.96 MB | per-sample / per-flow rows (3.5 MB per pool); xai_faithfulness_40f_45f_48f.md (kept/merged) holds the summary and intervals |
| `results/metrics/xgboost/xai_faithfulness_45f_flowdiffs.csv` | 2.57 MB | per-sample / per-flow rows (3.5 MB per pool); xai_faithfulness_40f_45f_48f.md (kept/merged) holds the summary and intervals |
| `results/metrics/xgboost/xai_faithfulness_45f_runs.csv` | 0.96 MB | per-sample / per-flow rows (3.5 MB per pool); xai_faithfulness_40f_45f_48f.md (kept/merged) holds the summary and intervals |
| `results/metrics/xgboost/xai_faithfulness_48f_flowdiffs.csv` | 2.57 MB | per-sample / per-flow rows (3.5 MB per pool); xai_faithfulness_40f_45f_48f.md (kept/merged) holds the summary and intervals |
| `results/metrics/xgboost/xai_faithfulness_48f_runs.csv` | 0.96 MB | per-sample / per-flow rows (3.5 MB per pool); xai_faithfulness_40f_45f_48f.md (kept/merged) holds the summary and intervals |

### Task 6: per-run rows (zero-shot, alignment, few-shot, block mix, types)

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/cross_dataset_align_runs.csv` | 12.7 KB | per-run rows; cross_dataset_step*.md (kept/merged) holds the Task 6 tables |
| `results/metrics/xgboost/cross_dataset_fewshot_CIC_to_UNSW_runs.csv` | 0.17 MB | per-run rows; cross_dataset_step*.md (kept/merged) holds the Task 6 tables |
| `results/metrics/xgboost/cross_dataset_fewshot_UNSW_to_CIC_runs.csv` | 0.17 MB | per-run rows; cross_dataset_step*.md (kept/merged) holds the Task 6 tables |
| `results/metrics/xgboost/cross_dataset_zero_shot_block_mix.csv` | 98.1 KB | per-run rows; cross_dataset_step*.md (kept/merged) holds the Task 6 tables |
| `results/metrics/xgboost/cross_dataset_zero_shot_runs.csv` | 36.6 KB | per-run rows; cross_dataset_step*.md (kept/merged) holds the Task 6 tables |
| `results/metrics/xgboost/cross_dataset_zero_shot_types.csv` | 37.3 KB | per-run rows; cross_dataset_step*.md (kept/merged) holds the Task 6 tables |

### Tasks 2.5 / 2.6: per-seed / per-run rows (methods, adaptation, leakage)

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/adaptation_38f_split_runs.csv` | 2.7 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/adaptation_40f_domain5_runs.csv` | 2.4 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/adaptation_40f_runs.csv` | 18.9 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/adaptation_40f_split_runs.csv` | 4.8 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/adaptation_41f_split_runs.csv` | 2.7 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/adaptation_45f_split_runs.csv` | 2.6 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/adaptation_48f_domain20_runs.csv` | 2.4 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/adaptation_48f_runs.csv` | 18.9 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/adaptation_48f_split_runs.csv` | 4.8 KB | per-run rows; adaptation_*_summary.csv (kept, read by final_table.py / leakage_table.py) has mean/std |
| `results/metrics/xgboost/leakage_40f_runs.csv` | 13.2 KB | per-run rows; leakage_<N>f_summary.csv (kept) has mean/std |
| `results/metrics/xgboost/leakage_48f_runs.csv` | 13.2 KB | per-run rows; leakage_<N>f_summary.csv (kept) has mean/std |
| `results/metrics/xgboost/methods_leak_zero_38f_seeds.csv` | 4.7 KB | per-seed rows; methods_*_summary.csv (kept, read by scripts/final_table.py) has mean/std |
| `results/metrics/xgboost/methods_leak_zero_41f_seeds.csv` | 4.7 KB | per-seed rows; methods_*_summary.csv (kept, read by scripts/final_table.py) has mean/std |
| `results/metrics/xgboost/methods_leak_zero_45f_seeds.csv` | 4.6 KB | per-seed rows; methods_*_summary.csv (kept, read by scripts/final_table.py) has mean/std |
| `results/metrics/xgboost/methods_transductive_b3_40f_seeds.csv` | 14.0 KB | per-seed rows; methods_*_summary.csv (kept, read by scripts/final_table.py) has mean/std |
| `results/metrics/xgboost/methods_transductive_b3_48f_seeds.csv` | 14.0 KB | per-seed rows; methods_*_summary.csv (kept, read by scripts/final_table.py) has mean/std |
| `results/metrics/xgboost/methods_zero_shot_b1_40f_seeds.csv` | 11.7 KB | per-seed rows; methods_*_summary.csv (kept, read by scripts/final_table.py) has mean/std |
| `results/metrics/xgboost/methods_zero_shot_b1_48f_seeds.csv` | 11.7 KB | per-seed rows; methods_*_summary.csv (kept, read by scripts/final_table.py) has mean/std |

## 2. MERGE: tables folded into one file per task (verbatim, one section per source file, headings demoted two levels; no number or caveat dropped)

Each merged file keeps every source line unchanged under a heading `Source: <original file name>`. Step 4 checks that every non-empty source line appears in its target. References in README, PROJECT_PLAN and the conclusions are re-pointed to the new names. The generation scripts still write the original per-table names if re-run; `results/README.md` will say so.

| target (new file in `results/metrics/xgboost/`) | sources | size |
|---|---|---|
| `task_2_7_tables.md` | `fpr_study_tuned_40f_45f_48f.md`, `fpr_study_prior_40f_45f_48f.md`, `fpr_study_self_40f_45f_48f.md`, `fpr_study_fewshot_48f_45f_41f.md`, `fpr_study_final_40f_45f_48f.md` | 40.3 KB |
| `task_3_tables.md` | `tier_summary_xgboost.md`, `stability_xgboost.md` | 10.9 KB |
| `task_4_tables.md` | `open_set_step1_40f_45f_48f.md`, `open_set_step2_40f_48f.md`, `open_set_step2_sources_40f_45f_48f.md`, `open_set_step3_40f_45f_48f.md`, `open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.md` | 33.2 KB |
| `task_4_5_tables.md` | `open_set_boost_calibration_40f_48f.md`, `open_set_boost_perclass_40f_48f.md`, `open_set_boost_ensemble_40f_48f.md`, `open_set_boost_distance_40f_48f.md`, `open_set_boost_oe_40f_48f.md`, `open_set_boost_combo_40f_48f.md`, `open_set_boost_iforest_40f_48f.md` | 0.11 MB |
| `task_5_tables.md` | `xai_faithfulness_40f_45f_48f.md`, `xai_audit_40f_48f.md`, `narrative_test_40f_48f.md`, `narrative_falsepos_40f_48f.md` | 24.2 KB |
| `task_6_tables.md` | `cross_dataset_step1_zero_shot.md`, `cross_dataset_step2_diagnostic.md`, `cross_dataset_step3_align.md`, `cross_dataset_step4_fewshot.md` | 16.3 KB |
| `headline_tables.md` | `headline_summary.md`, `headline_full_no_ttl_summary.md`, `headline_tuned_auc_official_summary.md`, `headline_tuned_f1_official_summary.md`, `operating_point_summary.md`, `accuracy_three_numbers_40f_48f_45f.md`, `accuracy_three_numbers_40f_48f_tuned_f1_auc.md`, `pool_comparison_40f_48f_45f_official.md`, `pool_comparison_40f_48f_45f_pooled_random.md`, `tuned_vs_default.md` | 13.2 KB |

## 3. Decisions on the UNSURE items (approved)

- Kept: `normal_fpr_floor_40f_48f.csv` (edit 3); the three notebooks (edit 3); the three `tier_study_xgboost_<N>f_runs.csv` (read by `run_tier_study.py --parts baselines`); `open_set_detection.png`; the small per-table CSVs next to the markdown tables (`open_set_step*.csv`, `cross_dataset_diagnostic_*.csv`, `narrative_falsepos_*_{faithfulness,features,groups,separation}.csv`); the older single-seed outputs quoted by README `Key findings` (`experiment_results.csv`, `split_comparison.csv`, `split_summary.csv`, `feature_selection_baselines_summary.csv`, `explanation_stability.csv`, `open_set_sweep_40.csv`, `overlap_diagnostic_40.csv`, `cross_dataset_results.csv`, `cross_dataset_feature_shift.csv`).
- Deleted (edit 2): `results/plots/xgboost/cross_dataset_generalization.png`, stale (plots the pre-Task-6 random-split run).
- Added (edit 1): `xai_audit_40f_example_failures.csv`, ten rows taken verbatim from the audit failure list (check f) plus the columns `feature`, `cue` and `shap_trend_on_training_rows`; the failure-list `reason` text always says "falls as the value rises" (a wording defect of the template in `pipelines/run_xai_study.py`), so that column states the real sign. The figures of the 2,000 audited narratives remain in `xai_audit_*_summary.csv`.

## 4. KEEP (compact)

| group | files | size |
|---|---|---|
| repository root | 5 | 68.4 KB |
| configs | 2 | 19.1 KB |
| dashboard | 16 | 76.6 KB |
| data | 6 | 14.2 KB |
| models_saved | 1 | 0.0 KB |
| notebooks | 3 | 5.4 KB |
| pipelines | 19 | 0.27 MB |
| results/ protocols, sheets, rankings, README | 27 | 0.11 MB |
| results/ metrics/overlap | 4 | 6.5 KB |
| results/ metrics/xgboost | 159 | 3.27 MB |
| results/ plots | 9 | 0.74 MB |
| scripts | 25 | 0.19 MB |
| src | 33 | 0.21 MB |
| tests | 32 | 0.25 MB |

<details><summary>results/ protocols, sheets, rankings, README: 27 files</summary>

- `results\.gitkeep` (0.0 KB): placeholder
- `results\README.md` (2.3 KB): results guide (edit after cleanup)
- `results\feature_ranking_mutual_info.csv` (1.2 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info.meta.json` (0.0 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info_48f.csv` (1.4 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info_48f.meta.json` (0.0 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info_blockval_40f.csv` (1.2 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info_blockval_40f.meta.json` (0.0 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info_blockval_45f.csv` (1.3 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info_blockval_45f.meta.json` (0.0 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info_blockval_48f.csv` (1.4 KB): input of the pipelines (shared rankings)
- `results\feature_ranking_mutual_info_blockval_48f.meta.json` (0.0 KB): input of the pipelines (shared rankings)
- `results\task_2_5_protocol.md` (3.0 KB): declared protocol
- `results\task_2_6_protocol.md` (4.4 KB): declared protocol
- `results\task_2_7_protocol.md` (8.2 KB): declared protocol
- `results\task_3_protocol.md` (6.4 KB): declared protocol
- `results\task_4_5_protocol.md` (6.8 KB): declared protocol
- `results\task_4_protocol.md` (6.4 KB): declared protocol
- `results\task_5_5_ab_instructions.md` (1.4 KB): blank rating sheet / key / instructions
- `results\task_5_5_ab_key.csv` (1.1 KB): blank rating sheet / key / instructions
- `results\task_5_5_ab_sheet.csv` (29.5 KB): blank rating sheet / key / instructions
- `results\task_5_5_protocol.md` (7.2 KB): declared protocol
- `results\task_5_human_audit_instructions.md` (1.3 KB): blank rating sheet / key / instructions
- `results\task_5_human_audit_key.csv` (0.7 KB): blank rating sheet / key / instructions
- `results\task_5_human_audit_sheet.csv` (11.4 KB): blank rating sheet / key / instructions
- `results\task_5_protocol.md` (8.1 KB): declared protocol
- `results\task_6_protocol.md` (9.0 KB): declared protocol

</details>

<details><summary>results/ metrics/overlap: 4 files</summary>

- `results\metrics\overlap\pooled_34f\best_possible_accuracy.csv` (0.2 KB): backs quoted numbers; twin shares / best-possible accuracy quoted in README and PROJECT_PLAN
- `results\metrics\overlap\pooled_34f\summary.md` (3.0 KB): backs quoted numbers; twin shares / best-possible accuracy quoted in README and PROJECT_PLAN
- `results\metrics\overlap\pooled_42f\best_possible_accuracy.csv` (0.2 KB): backs quoted numbers; twin shares / best-possible accuracy quoted in README and PROJECT_PLAN
- `results\metrics\overlap\pooled_42f\summary.md` (3.1 KB): backs quoted numbers; twin shares / best-possible accuracy quoted in README and PROJECT_PLAN

</details>

<details><summary>results/ metrics/xgboost: 159 files</summary>

- `results\metrics\xgboost\accuracy_three_numbers_40f_48f_45f.csv` (0.3 KB): backs quoted numbers
- `results\metrics\xgboost\accuracy_three_numbers_40f_48f_tuned_f1_auc.csv` (0.5 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_38f_split_summary.csv` (2.8 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_40f_domain5_summary.csv` (3.0 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_40f_split_summary.csv` (4.9 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_40f_summary.csv` (21.6 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_41f_split_summary.csv` (2.9 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_45f_split_summary.csv` (2.7 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_48f_domain20_summary.csv` (3.0 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_48f_split_summary.csv` (4.9 KB): backs quoted numbers
- `results\metrics\xgboost\adaptation_48f_summary.csv` (21.6 KB): backs quoted numbers
- `results\metrics\xgboost\bootstrap_ci_40f_48f_45f.csv` (0.8 KB): backs quoted numbers
- `results\metrics\xgboost\bootstrap_paired_diff_40f_48f_45f.csv` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\confusion_matrix_40_official.csv` (0.3 KB): backs quoted numbers
- `results\metrics\xgboost\confusion_matrix_40_official_rownorm.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\confusion_matrix_40_pooled_random_pooled.csv` (0.3 KB): backs quoted numbers
- `results\metrics\xgboost\confusion_matrix_40_pooled_random_rownorm_pooled.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\confusion_matrix_48_official_48f.csv` (0.3 KB): backs quoted numbers
- `results\metrics\xgboost\confusion_matrix_48_official_rownorm_48f.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\confusion_matrix_48_pooled_random_pooled_48f.csv` (0.3 KB): backs quoted numbers
- `results\metrics\xgboost\confusion_matrix_48_pooled_random_rownorm_pooled_48f.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\cross_dataset_diagnostic_importance_agreement.csv` (1.3 KB): backs quoted numbers
- `results\metrics\xgboost\cross_dataset_diagnostic_univariate.csv` (0.9 KB): backs quoted numbers
- `results\metrics\xgboost\cross_dataset_feature_shift.csv` (0.6 KB): backs quoted numbers
- `results\metrics\xgboost\cross_dataset_results.csv` (0.6 KB): backs quoted numbers
- `results\metrics\xgboost\cross_dataset_zero_shot_eval_mix.csv` (3.1 KB): backs quoted numbers; evaluation rows per attack type (basis of the 'too few rows for a per-type recall' statement); 3 KB
- `results\metrics\xgboost\dashboard_end_to_end_40f.csv` (45.5 KB): backs quoted numbers
- `results\metrics\xgboost\experiment_results.csv` (3.8 KB): backs quoted numbers
- `results\metrics\xgboost\explanation_stability.csv` (1.1 KB): backs quoted numbers
- `results\metrics\xgboost\feature_selection_baselines_summary.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\headline_full_no_ttl_summary.csv` (10.1 KB): backs quoted numbers
- `results\metrics\xgboost\headline_summary.csv` (18.3 KB): backs quoted numbers
- `results\metrics\xgboost\headline_tuned_auc_official_summary.csv` (8.8 KB): backs quoted numbers
- `results\metrics\xgboost\headline_tuned_f1_official_summary.csv` (8.8 KB): backs quoted numbers
- `results\metrics\xgboost\hyperparameter_search_40f.csv` (3.3 KB): backs quoted numbers
- `results\metrics\xgboost\hyperparameter_search_48f.csv` (3.3 KB): backs quoted numbers
- `results\metrics\xgboost\hyperparameter_search_blockval_40f.csv` (3.4 KB): backs quoted numbers
- `results\metrics\xgboost\hyperparameter_search_blockval_45f.csv` (3.4 KB): backs quoted numbers
- `results\metrics\xgboost\hyperparameter_search_blockval_48f.csv` (3.4 KB): backs quoted numbers
- `results\metrics\xgboost\hyperparameter_search_stage1_40f.csv` (3.3 KB): backs quoted numbers
- `results\metrics\xgboost\hyperparameter_search_stage1_48f.csv` (3.3 KB): backs quoted numbers
- `results\metrics\xgboost\label_scheme_comparison.csv` (1.2 KB): backs quoted numbers
- `results\metrics\xgboost\label_scheme_comparison_48f.csv` (1.2 KB): backs quoted numbers
- `results\metrics\xgboost\label_scheme_comparison_pooled.csv` (1.2 KB): backs quoted numbers
- `results\metrics\xgboost\label_scheme_comparison_pooled_48f.csv` (1.2 KB): backs quoted numbers
- `results\metrics\xgboost\label_scheme_summary.md` (3.7 KB): backs quoted numbers
- `results\metrics\xgboost\label_scheme_summary_48f.md` (3.7 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_40f_shift_auc.csv` (0.1 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_40f_summary.csv` (10.8 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_40f_validation_blocks.csv` (0.9 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_40f_validation_blocks_b200.csv` (0.9 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_45f_shift_auc.csv` (0.1 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_48f_shift_auc.csv` (0.1 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_48f_summary.csv` (10.8 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_48f_validation_blocks.csv` (0.9 KB): backs quoted numbers
- `results\metrics\xgboost\leakage_48f_validation_blocks_b200.csv` (0.9 KB): backs quoted numbers
- `results\metrics\xgboost\methods_leak_zero_38f_summary.csv` (6.8 KB): backs quoted numbers
- `results\metrics\xgboost\methods_leak_zero_41f_summary.csv` (7.0 KB): backs quoted numbers
- `results\metrics\xgboost\methods_leak_zero_45f_summary.csv` (6.5 KB): backs quoted numbers
- `results\metrics\xgboost\methods_transductive_b3_40f_summary.csv` (27.0 KB): backs quoted numbers
- `results\metrics\xgboost\methods_transductive_b3_48f_summary.csv` (27.0 KB): backs quoted numbers
- `results\metrics\xgboost\methods_zero_shot_b1_40f_summary.csv` (21.1 KB): backs quoted numbers
- `results\metrics\xgboost\methods_zero_shot_b1_48f_summary.csv` (21.1 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_falsepos_40f_faithfulness.csv` (6.6 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_falsepos_40f_features.csv` (21.1 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_falsepos_40f_groups.csv` (3.1 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_falsepos_40f_separation.csv` (2.2 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_falsepos_48f_faithfulness.csv` (6.5 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_falsepos_48f_features.csv` (20.7 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_falsepos_48f_groups.csv` (3.2 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_falsepos_48f_separation.csv` (2.2 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_test_40f_calibration.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_test_40f_narratives.csv` (1.31 MB): provenance of a kept sheet; input of scripts/make_human_audit_sheet.py / make_ab_sheet.py (provenance of the blank rating sheets)
- `results\metrics\xgboost\narrative_test_40f_summary.csv` (14.8 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_test_48f_calibration.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_test_48f_summary.csv` (14.3 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_validation_40f_calibration.csv` (0.1 KB): backs quoted numbers
- `results\metrics\xgboost\narrative_validation_40f_summary.csv` (3.3 KB): backs quoted numbers
- `results\metrics\xgboost\normal_fpr_floor_40f_48f.csv` (0.3 KB): approved: keep; two-row exact-twin floor of the Normal FPR (Task 2.7 diagnostic); no document quotes it
- `results\metrics\xgboost\open_set_boost_selection_40f_scores.csv` (5.0 KB): backs quoted numbers
- `results\metrics\xgboost\open_set_boost_selection_48f_scores.csv` (5.0 KB): backs quoted numbers
- `results\metrics\xgboost\open_set_step1_40f.csv` (4.7 KB): backs quoted numbers
- `results\metrics\xgboost\open_set_step1_45f.csv` (4.7 KB): backs quoted numbers
- `results\metrics\xgboost\open_set_step1_48f.csv` (4.6 KB): backs quoted numbers
- `results\metrics\xgboost\open_set_step2_40f.csv` (5.1 KB): backs quoted numbers
- `results\metrics\xgboost\open_set_step2_48f.csv` (5.2 KB): backs quoted numbers
- `results\metrics\xgboost\open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv` (1.8 KB): backs quoted numbers
- `results\metrics\xgboost\open_set_sweep_40.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\operating_point_summary_40f.csv` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\operating_point_summary_45f.csv` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\operating_point_summary_48f.csv` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\overlap_diagnostic_40.csv` (0.2 KB): backs quoted numbers
- `results\metrics\xgboost\pool_comparison_40f_48f_45f_official.csv` (1.1 KB): backs quoted numbers
- `results\metrics\xgboost\pool_comparison_40f_48f_45f_pooled_random.csv` (1.1 KB): backs quoted numbers
- `results\metrics\xgboost\pooled_reference_composition.csv` (0.5 KB): backs quoted numbers
- `results\metrics\xgboost\shap_boot_xgboost_40f.npz` (0.19 MB): backs quoted numbers
- `results\metrics\xgboost\shap_boot_xgboost_45f.npz` (0.27 MB): backs quoted numbers
- `results\metrics\xgboost\shap_boot_xgboost_48f.npz` (0.28 MB): backs quoted numbers
- `results\metrics\xgboost\shap_importance_xgboost_40f.csv` (22.8 KB): backs quoted numbers
- `results\metrics\xgboost\shap_importance_xgboost_45f.csv` (38.0 KB): backs quoted numbers
- `results\metrics\xgboost\shap_importance_xgboost_48f.csv` (33.4 KB): backs quoted numbers
- `results\metrics\xgboost\shift_conclusion_40f_45f_48f.md` (3.8 KB): backs quoted numbers
- `results\metrics\xgboost\shift_group_ablation_40f.csv` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\shift_group_ablation_48f.csv` (1.1 KB): backs quoted numbers
- `results\metrics\xgboost\shift_nf_groups_40f.csv` (0.7 KB): backs quoted numbers
- `results\metrics\xgboost\shift_nf_groups_45f.csv` (0.7 KB): backs quoted numbers
- `results\metrics\xgboost\shift_nf_groups_48f.csv` (0.7 KB): backs quoted numbers
- `results\metrics\xgboost\shift_normal_features_40f.csv` (2.1 KB): backs quoted numbers
- `results\metrics\xgboost\shift_normal_features_45f.csv` (2.4 KB): backs quoted numbers
- `results\metrics\xgboost\shift_normal_features_48f.csv` (2.5 KB): backs quoted numbers
- `results\metrics\xgboost\shift_normal_summary_40f.csv` (0.3 KB): backs quoted numbers
- `results\metrics\xgboost\shift_normal_summary_45f.csv` (0.3 KB): backs quoted numbers
- `results\metrics\xgboost\shift_normal_summary_48f.csv` (0.3 KB): backs quoted numbers
- `results\metrics\xgboost\shift_ranking_stability_40f_45f_48f.csv` (0.2 KB): backs quoted numbers
- `results\metrics\xgboost\split_comparison.csv` (2.7 KB): backs quoted numbers
- `results\metrics\xgboost\split_summary.csv` (0.6 KB): backs quoted numbers
- `results\metrics\xgboost\stability_xgboost_40f.csv` (0.8 KB): backs quoted numbers
- `results\metrics\xgboost\stability_xgboost_45f.csv` (1.1 KB): backs quoted numbers
- `results\metrics\xgboost\stability_xgboost_48f.csv` (1.1 KB): backs quoted numbers
- `results\metrics\xgboost\task_2_5_conclusion.md` (4.9 KB): backs quoted numbers
- `results\metrics\xgboost\task_2_5_final_table_40f_48f.csv` (12.0 KB): backs quoted numbers
- `results\metrics\xgboost\task_2_5_final_table_40f_48f.md` (12.0 KB): backs quoted numbers
- `results\metrics\xgboost\task_2_6_conclusion.md` (6.6 KB): backs quoted numbers
- `results\metrics\xgboost\task_2_6_table_40f_48f_45f_41f_38f.csv` (7.3 KB): backs quoted numbers
- `results\metrics\xgboost\task_2_6_table_40f_48f_45f_41f_38f.md` (8.4 KB): backs quoted numbers
- `results\metrics\xgboost\task_2_7_conclusion.md` (9.1 KB): backs quoted numbers
- `results\metrics\xgboost\task_3_conclusion.md` (7.9 KB): backs quoted numbers
- `results\metrics\xgboost\task_4_conclusion.md` (21.6 KB): backs quoted numbers
- `results\metrics\xgboost\task_5_conclusion.md` (20.3 KB): backs quoted numbers
- `results\metrics\xgboost\task_6_conclusion.md` (12.0 KB): backs quoted numbers
- `results\metrics\xgboost\tier_baselines_summary_accuracy_xgboost_40f.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\tier_baselines_summary_accuracy_xgboost_45f.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\tier_baselines_summary_accuracy_xgboost_48f.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\tier_baselines_summary_xgboost_40f.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\tier_baselines_summary_xgboost_45f.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\tier_baselines_summary_xgboost_48f.csv` (0.4 KB): backs quoted numbers
- `results\metrics\xgboost\tier_study_xgboost_40f_runs.csv` (4.7 KB): approved: keep; per-seed tier rows (18 KB for the 3 pools): `pipelines/run_tier_study.py --parts baselines` reads them, and they are the per-seed source of the Task 3 macro F1
- `results\metrics\xgboost\tier_study_xgboost_45f_runs.csv` (6.6 KB): approved: keep; per-seed tier rows (18 KB for the 3 pools): `pipelines/run_tier_study.py --parts baselines` reads them, and they are the per-seed source of the Task 3 macro F1
- `results\metrics\xgboost\tier_study_xgboost_48f_runs.csv` (6.9 KB): approved: keep; per-seed tier rows (18 KB for the 3 pools): `pipelines/run_tier_study.py --parts baselines` reads them, and they are the per-seed source of the Task 3 macro F1
- `results\metrics\xgboost\tier_summary_xgboost_40f.csv` (1.4 KB): backs quoted numbers
- `results\metrics\xgboost\tier_summary_xgboost_45f.csv` (1.7 KB): backs quoted numbers
- `results\metrics\xgboost\tier_summary_xgboost_48f.csv` (1.8 KB): backs quoted numbers
- `results\metrics\xgboost\tuned_params_40f.json` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\tuned_params_48f.json` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\tuned_params_blockval_40f.json` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\tuned_params_blockval_45f.json` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\tuned_params_blockval_48f.json` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\tuned_params_stage1_40f.json` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\tuned_params_stage1_48f.json` (1.0 KB): backs quoted numbers
- `results\metrics\xgboost\tuned_vs_default.csv` (1.7 KB): backs quoted numbers
- `results\metrics\xgboost\xai_additivity_40f.csv` (2.3 KB): backs quoted numbers
- `results\metrics\xgboost\xai_additivity_45f.csv` (2.3 KB): backs quoted numbers
- `results\metrics\xgboost\xai_additivity_48f.csv` (2.3 KB): backs quoted numbers
- `results\metrics\xgboost\xai_audit_40f_narratives.csv` (0.41 MB): provenance of a kept sheet; input of scripts/make_human_audit_sheet.py / make_ab_sheet.py (provenance of the blank rating sheets)
- `results\metrics\xgboost\xai_audit_40f_summary.csv` (4.9 KB): backs quoted numbers
- `results\metrics\xgboost\xai_audit_48f_summary.csv` (4.8 KB): backs quoted numbers
- `results\metrics\xgboost\xai_audit_validation_40f_summary.csv` (4.8 KB): backs quoted numbers
- `results\metrics\xgboost\xai_audit_validation_48f_summary.csv` (4.8 KB): backs quoted numbers
- `results\metrics\xgboost\xai_audit_40f_example_failures.csv` (5.7 KB): added (approved edit 1); ten example audit failures extracted from xai_audit_40f_failures.csv (four of the 'reduced average packet size' style) with the real SHAP trend column

</details>

<details><summary>results/ plots: 9 files</summary>

- `results\plots\xgboost\adaptation_curve_40f.png` (65.6 KB): planned report figure
- `results\plots\xgboost\adaptation_curve_48f.png` (76.7 KB): planned report figure
- `results\plots\xgboost\confusion_matrix_40.png` (86.3 KB): planned report figure
- `results\plots\xgboost\dashboard_prediction_explanation_view.png` (0.21 MB): planned report figure
- `results\plots\xgboost\explanation_stability.png` (36.8 KB): planned report figure
- `results\plots\xgboost\feature_set_metrics.png` (37.9 KB): planned report figure
- `results\plots\xgboost\open_set_detection.png` (33.2 KB): planned report figure
- `results\plots\xgboost\open_set_sweep.png` (85.5 KB): planned report figure
- `results\plots\xgboost\roc_curve_40.png` (0.10 MB): planned report figure

</details>

## 5. Code, tests, configs: no deletions

Import graph of every tracked module (checked with `ast`): every file in `src/`, `pipelines/`, `scripts/` and `dashboard/` is imported by a kept script, a kept test or the dashboard, or is an entry point named in README / ONBOARDING / a protocol. The only candidates were:

- `scripts/compare_pools.py` (+ one test in `tests/test_pipelines.py`): writes `pool_comparison_*` which are KEPT (the three-pool official / pooled table is a natural report table), so the script stays.
- `scripts/diagnose_normal_fuzzers.py` (+ `tests/test_diagnostics.py`): its outputs (`normal_fuzzers_diagnostic/`) were removed, but the module is imported by `scripts/characterize_shift.py` and `pipelines/run_leakage_checks.py` (`CV_PARAMS`, `codes`, `distance`, `load_splits`), so it stays.
- `scripts/normal_fpr_floor.py` (no test; helper `normal_overlap_floor` is tested in `tests/test_overlap.py`): its single output `normal_fpr_floor_40f_48f.csv` is UNSURE (kept), so the script stays.
- The summary scripts (`scripts/*_summary.py`, `tier_summary.py`, ...) read per-seed files that were removed. They stay because they produce the kept tables; to re-run one, re-run the pipeline named in its docstring first (hours for the large studies). The two sheet makers read `xai_audit_40f_narratives.csv` and `narrative_test_40f_narratives.csv`, which are KEPT for that reason.
- Config keys: nothing is removed; every key in `configs/config.yaml` is still read by kept code (the pooled-split and baseline CSV names are still written by `run_all_experiments.py`).
- Test suite: 327 tests at HEAD; no test is removed, so the count must stay 327 after the cleanup.

## 6. Documents edited so that no kept document points at a removed file or command

- `results/README.md`: rewritten (merged files, removed families and how to recover them, new file names).
- `README.md`: pointer to the ledger; twin shares labelled by origin (tracked 77-85% against the earlier untracked 72-80%); label-scheme table replaced by the tracked figures with named sources (hierarchical row from the Task 2.5 B1 summary); `feature_selection_baselines.csv` and the overlap-folder sentences; "140 tests" -> 327.
- `PROJECT_PLAN.md`: same twin-share and label-scheme corrections; "140" -> 327; pointer to the ledger.
- `ONBOARDING.md`: no reference to a removed file (checked); unchanged.
- Conclusions (`task_2_7` ... `task_6`): `Tables:` lines re-pointed to the merged files; Task 6 Spearman corrected to +/- 0.05; Task 5 names the example-failures file and the template wording defect.
- `results/NUMBERS_LEDGER.md`: regenerated (316 entries) with the merged file names; all verified.
- Protocols (`results/task_*_protocol.md`): not edited.

## 7. Coverage check (why deleting these files loses no quoted number)

For every conclusion and for README / PROJECT_PLAN, each quoted number with two or more decimals (and each count of 1,000 or more) was looked up in the kept files of its task. Result (a number counts as found when the same digits occur in a kept file of that task, after rounding):

| document | numbers quoted | found in a kept file | only in files proposed for deletion | in neither (derived: differences, ranges, round counts) |
|---|---|---|---|---|
| `task_2_5_conclusion.md` | 63 | 63 | 0 | 0 |
| `task_2_6_conclusion.md` | 60 | 58 | 0 | 2 |
| `task_2_7_conclusion.md` | 111 | 111 | 0 | 0 |
| `task_3_conclusion.md` | 124 | 122 | 0 | 2 |
| `task_4_conclusion.md` | 277 | 273 | 2 | 2 |
| `task_5_conclusion.md` | 126 | 125 | 0 | 1 |
| `task_6_conclusion.md` | 170 | 169 | 0 | 1 |
| `shift_conclusion_40f_45f_48f.md` | 43 | 42 | 0 | 1 |
| `README.md` | 134 | 131 | 0 | 3 |
| `PROJECT_PLAN.md` | 98 | 96 | 0 | 2 |

The few numbers flagged "only in a file proposed for deletion" are artefacts of the checker, each checked by hand: comma formatting (1,627 is in the kept `open_set_step1_40f_45f_48f.md`); round-half-up against the checker's round-half-even (0.768, 0.789 and 0.773 are 0.7675, 0.7885 / 0.7895 and 0.7725 in the kept `tier_summary_xgboost.md`); and a mean recomputed from a kept file (0.815 is the mean of `open_set_boost_selection_40f_scores.csv`). The stronger check is the ledger (`results/NUMBERS_LEDGER.md`): 280 headline numbers, each verified against a cell of a KEEP or MERGE file.
