# Lean consolidation manifest (Task 8, Step 1): PROPOSAL. Nothing has been deleted.

Branch `cleanup/lean` from `main` (`9550c9d`, which contains the merged Task 7 cleanup and the audit-wording fix). Recovery tag `pre-lean-2026-10`. The pre-Task-7 state is tag `pre-cleanup-2026-10`; the backup zip `D:\Github Projects\_backups\xai-ids-results-pre-cleanup.zip` is intact (578 files, CRC test clean). Baseline tests: **328 passed** (170 s). Only tracked files under `results/` are touched; nothing gitignored or untracked (`data/raw`, `models_saved`, `results/_local_scratch`, `results/diagnostics`, `results/pipeline.log`), and no code, test, config, dashboard or notebook is edited.

## 1. Totals

| | files | size |
|---|---|---|
| tracked in `results/` now | 208 | 4.55 MB |
| KEEP | 15 | 1.24 MB |
| MERGE->FINDINGS | 17 | 0.15 MB |
| MERGE->TABLES | 13 | 0.29 MB |
| RENDER->TABLES, DELETE | 50 | 64.5 KB |
| KEEP? | 19 | 0.86 MB |
| DELETE | 94 | 1.94 MB |
| **after, as the brief specifies** (kept files + FINDINGS, TABLES, PROTOCOL, REFERENCE_XGBOOST, TEMPLATE) | **20** | about 1.94 MB |
| **after, with my recommended exception: the 3 human-audit files** | **23** | about 1.95 MB |
| after, if you also keep the 16 rankings and SHAP files (see section 6) | 39 | about 2.80 MB |

Size after includes an estimate of 0.7 MB for the new FINDINGS.md (about 0.17 MB), TABLES.md (about 0.4 MB with the rendered appendix tables) and the small hand-off files; the exact numbers are reported after Step 2.

## 2. Target layout of `results/` and what feeds it

| file | content | built from |
|---|---|---|
| `FINDINGS.md` | the 8 conclusion files verbatim, one `Source:` section each, in task order (2.5, shift Step A, 2.6, 2.7, 3, 4 with 4.5, 5 with 5.5, 6), then **Appendix: the 9 declared protocols verbatim** | task_2_5_conclusion.md, shift_conclusion_40f_45f_48f.md, task_2_6_conclusion.md, task_2_7_conclusion.md, task_3_conclusion.md, task_4_conclusion.md, task_5_conclusion.md, task_6_conclusion.md; task_2_5_protocol.md, task_2_6_protocol.md, task_2_7_protocol.md, task_3_protocol.md, task_4_protocol.md, task_4_5_protocol.md, task_5_protocol.md, task_5_5_protocol.md, task_6_protocol.md |
| `TABLES.md` | all per-task tables verbatim (one `Source:` section per original table, headings demoted), then **Appendix B: small CSVs rendered losslessly as markdown tables** (section 4) | headline_tables.md, label_scheme_summary.md, label_scheme_summary_48f.md, task_2_5_final_table_40f_48f.md, task_2_6_table_40f_48f_45f_41f_38f.md, task_2_7_tables.md, task_3_tables.md, task_4_tables.md, task_4_5_tables.md, task_5_tables.md, task_6_tables.md; the two overlap `summary.md`; the CSVs in section 4 |
| `NUMBERS_LEDGER.md` | kept; every entry re-pointed to a cell of TABLES.md or a line of FINDINGS.md (section 5) | |
| `PROTOCOL.md` | ONE page: the shared rules every model follows and the commands (outline in section 7) | distilled from the 9 protocols, `configs/config.yaml` and ONBOARDING; every sentence checked against them |
| `REFERENCE_XGBOOST.csv` | tidy file of the XGBoost headline (40 / 48 features, 45 as the TTL ablation; official and pooled), tier and stability numbers | parsed only from tables in TABLES.md; verified value by value against the ledger |
| `TEMPLATE_model_results.csv` | blank template, one row per (model, pool, tier, split), same columns as the reference | the reference columns |
| `README.md` | short index of the above plus 'what was removed and where to recover it' (tags `pre-lean-2026-10`, `pre-cleanup-2026-10`, the backup zip, the old manifests in git history) | |
| `plots/xgboost/` (8 files) | adaptation_curve_40f.png, adaptation_curve_48f.png, confusion_matrix_40.png, roc_curve_40.png, open_set_sweep.png, explanation_stability.png, feature_set_metrics.png, dashboard_prediction_explanation_view.png | the Task 6 cross-dataset figure does not exist (the stale one was deleted in Task 7), so there is none to keep |
| narratives and sheets | `xai_audit_40f_example_failures.csv`, `xai_audit_40f_narratives.csv`, `task_5_5_ab_sheet.csv`, `task_5_5_ab_key.csv`, `task_5_5_ab_instructions.md` | kept as they are |

The plots stay in `results/plots/xgboost/` (not moved to `results/plots/`) because `src/evaluation/plots.py` and `train_pipeline.py` write to `results/plots/<model.type>/`; moving them would need a code change. `ONBOARDING.md` (repository root) gets the new section 'Reference results and how to compare'.

## 3. Action for every tracked file in `results/`

| action | files | size | meaning |
|---|---|---|---|
| DELETE | 74 | 1.76 MB | detail not housed |
| DELETE | 14 | 29.9 KB | fully housed |
| DELETE | 1 | 73.3 KB | old manifest |
| DELETE | 3 | 47.7 KB | other |
| DELETE | 1 | 0.0 KB | placeholder |
| DELETE | 1 | 33.2 KB | plots |
| KEEP | 8 | 0.70 MB | plots |
| KEEP | 7 | 0.54 MB | report / hand-off |
| KEEP? | 19 | 0.86 MB | exception, needs your OK |
| MERGE->FINDINGS | 8 | 87.4 KB | conclusions |
| MERGE->FINDINGS | 9 | 60.1 KB | protocols (appendix) |
| MERGE->TABLES | 13 | 0.29 MB | tables |
| RENDER->TABLES, DELETE | 9 | 10.4 KB | B1 earlier single-seed run (README Key findings) |
| RENDER->TABLES, DELETE | 8 | 2.6 KB | B2 confusion matrices (counts and row-normalised) |
| RENDER->TABLES, DELETE | 2 | 1.8 KB | B3 bootstrap intervals |
| RENDER->TABLES, DELETE | 21 | 16.9 KB | B4 Step A shift and Task 2.6 leakage evidence |
| RENDER->TABLES, DELETE | 2 | 4.4 KB | B5 Task 6 small tables |
| RENDER->TABLES, DELETE | 7 | 7.3 KB | B6 tuned hyperparameters (the JSON files) |
| RENDER->TABLES, DELETE | 1 | 21.1 KB | B7 hierarchical / flat label-scheme metrics (subset of the Task 2.5 B1 summary) |

Per file:

<details><summary>DELETE: detail not housed (74 files, 1.76 MB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/adaptation_38f_split_summary.csv` | 2.8 KB | 81 of 102 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/adaptation_40f_domain5_summary.csv` | 3.0 KB | 89 of 102 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/adaptation_40f_split_summary.csv` | 4.9 KB | 180 of 204 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/adaptation_40f_summary.csv` | 21.6 KB | 835 of 1020 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/adaptation_41f_split_summary.csv` | 2.9 KB | 83 of 102 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/adaptation_45f_split_summary.csv` | 2.7 KB | 76 of 102 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/adaptation_48f_domain20_summary.csv` | 3.0 KB | 90 of 102 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/adaptation_48f_split_summary.csv` | 4.9 KB | 181 of 204 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/adaptation_48f_summary.csv` | 21.6 KB | 817 of 1020 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/headline_full_no_ttl_summary.csv` | 10.1 KB | 103 of 550 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/headline_summary.csv` | 18.3 KB | 257 of 1101 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/headline_tuned_auc_official_summary.csv` | 8.8 KB | 125 of 552 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/headline_tuned_f1_official_summary.csv` | 8.8 KB | 139 of 550 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/hyperparameter_search_40f.csv` | 3.3 KB | 42 of 374 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/hyperparameter_search_48f.csv` | 3.3 KB | 40 of 372 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/hyperparameter_search_blockval_40f.csv` | 3.4 KB | 73 of 386 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/hyperparameter_search_blockval_45f.csv` | 3.4 KB | 59 of 385 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/hyperparameter_search_blockval_48f.csv` | 3.4 KB | 56 of 384 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/hyperparameter_search_stage1_40f.csv` | 3.3 KB | 44 of 374 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/hyperparameter_search_stage1_48f.csv` | 3.3 KB | 41 of 374 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/label_scheme_comparison.csv` | 1.2 KB | 55 of 66 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/label_scheme_comparison_48f.csv` | 1.2 KB | 55 of 66 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/label_scheme_comparison_pooled.csv` | 1.2 KB | 56 of 66 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/label_scheme_comparison_pooled_48f.csv` | 1.2 KB | 55 of 66 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/leakage_40f_summary.csv` | 10.8 KB | 279 of 356 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/leakage_48f_summary.csv` | 10.8 KB | 288 of 356 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/methods_leak_zero_38f_summary.csv` | 6.8 KB | 112 of 302 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/methods_leak_zero_41f_summary.csv` | 7.0 KB | 110 of 304 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/methods_leak_zero_45f_summary.csv` | 6.5 KB | 101 of 302 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/methods_transductive_b3_40f_summary.csv` | 27.0 KB | 454 of 1212 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/methods_transductive_b3_48f_summary.csv` | 27.0 KB | 435 of 1212 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/methods_zero_shot_b1_48f_summary.csv` | 21.1 KB | 346 of 958 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_falsepos_40f_faithfulness.csv` | 6.6 KB | 83 of 360 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_falsepos_40f_features.csv` | 21.1 KB | 384 of 1133 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_falsepos_40f_groups.csv` | 3.1 KB | 50 of 200 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_falsepos_40f_separation.csv` | 2.2 KB | 3 of 30 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_falsepos_48f_faithfulness.csv` | 6.5 KB | 83 of 352 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_falsepos_48f_features.csv` | 20.7 KB | 394 of 1088 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_falsepos_48f_groups.csv` | 3.2 KB | 52 of 200 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_falsepos_48f_separation.csv` | 2.2 KB | 3 of 30 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_test_40f_calibration.csv` | 0.4 KB | 2 of 15 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_test_40f_narratives.csv` | 1.31 MB | 388 of 4598 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_test_40f_summary.csv` | 14.8 KB | 98 of 560 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_test_48f_calibration.csv` | 0.4 KB | 2 of 15 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_test_48f_summary.csv` | 14.3 KB | 92 of 523 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_validation_40f_calibration.csv` | 0.1 KB | 0 of 3 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/narrative_validation_40f_summary.csv` | 3.3 KB | 13 of 109 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/open_set_boost_selection_40f_scores.csv` | 5.0 KB | 99 of 200 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/open_set_boost_selection_48f_scores.csv` | 5.0 KB | 107 of 200 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/open_set_step2_40f.csv` | 5.1 KB | 226 of 238 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/open_set_step2_48f.csv` | 5.2 KB | 230 of 238 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/operating_point_summary_40f.csv` | 1.0 KB | 39 of 79 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/operating_point_summary_45f.csv` | 1.0 KB | 12 of 78 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/operating_point_summary_48f.csv` | 1.0 KB | 40 of 78 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/task_2_5_final_table_40f_48f.csv` | 12.0 KB | 1222 of 1392 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_baselines_summary_accuracy_xgboost_40f.csv` | 0.4 KB | 7 of 22 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_baselines_summary_accuracy_xgboost_45f.csv` | 0.4 KB | 9 of 22 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_baselines_summary_accuracy_xgboost_48f.csv` | 0.4 KB | 6 of 22 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_baselines_summary_xgboost_40f.csv` | 0.4 KB | 19 of 22 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_baselines_summary_xgboost_45f.csv` | 0.4 KB | 18 of 21 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_baselines_summary_xgboost_48f.csv` | 0.4 KB | 19 of 22 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_study_xgboost_40f_runs.csv` | 4.7 KB | 80 of 420 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_study_xgboost_45f_runs.csv` | 6.6 KB | 71 of 525 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_study_xgboost_48f_runs.csv` | 6.9 KB | 77 of 525 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_summary_xgboost_40f.csv` | 1.4 KB | 80 of 89 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_summary_xgboost_45f.csv` | 1.7 KB | 99 of 112 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/tier_summary_xgboost_48f.csv` | 1.8 KB | 99 of 112 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/xai_additivity_40f.csv` | 2.3 KB | 60 of 90 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/xai_additivity_45f.csv` | 2.3 KB | 60 of 90 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/xai_additivity_48f.csv` | 2.3 KB | 60 of 90 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/xai_audit_40f_summary.csv` | 4.9 KB | 12 of 143 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/xai_audit_48f_summary.csv` | 4.8 KB | 11 of 136 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/xai_audit_validation_40f_summary.csv` | 4.8 KB | 13 of 146 numeric cells appear in the home tables; the rest are listed in section 4 |
| `results/metrics/xgboost/xai_audit_validation_48f_summary.csv` | 4.8 KB | 13 of 137 numeric cells appear in the home tables; the rest are listed in section 4 |

</details>

<details><summary>DELETE: fully housed (14 files, 29.9 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/overlap/pooled_34f/best_possible_accuracy.csv` | 0.2 KB | all 8 numeric cells appear in headline_full_no_ttl_summary.md, headline_summary.md |
| `results/metrics/overlap/pooled_42f/best_possible_accuracy.csv` | 0.2 KB | all 8 numeric cells appear in headline_full_no_ttl_summary.md, headline_summary.md |
| `results/metrics/xgboost/accuracy_three_numbers_40f_48f_45f.csv` | 0.3 KB | all 21 numeric cells appear in accuracy_three_numbers_40f_48f_45f.md, accuracy_three_numbers_40f_48f_tuned_f1_auc.md |
| `results/metrics/xgboost/accuracy_three_numbers_40f_48f_tuned_f1_auc.csv` | 0.5 KB | all 30 numeric cells appear in accuracy_three_numbers_40f_48f_45f.md, accuracy_three_numbers_40f_48f_tuned_f1_auc.md |
| `results/metrics/xgboost/cross_dataset_diagnostic_univariate.csv` | 0.9 KB | all 28 numeric cells appear in cross_dataset_step1_zero_shot.md, cross_dataset_step2_diagnostic.md |
| `results/metrics/xgboost/open_set_step1_40f.csv` | 4.7 KB | all 191 numeric cells appear in open_set_step1_40f_45f_48f.md |
| `results/metrics/xgboost/open_set_step1_45f.csv` | 4.7 KB | all 191 numeric cells appear in open_set_step1_40f_45f_48f.md |
| `results/metrics/xgboost/open_set_step1_48f.csv` | 4.6 KB | all 189 numeric cells appear in open_set_step1_40f_45f_48f.md |
| `results/metrics/xgboost/open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv` | 1.8 KB | all 72 numeric cells appear in open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.md |
| `results/metrics/xgboost/stability_xgboost_40f.csv` | 0.8 KB | all 49 numeric cells appear in stability_xgboost.md |
| `results/metrics/xgboost/stability_xgboost_45f.csv` | 1.1 KB | all 87 numeric cells appear in stability_xgboost.md |
| `results/metrics/xgboost/stability_xgboost_48f.csv` | 1.1 KB | all 90 numeric cells appear in stability_xgboost.md |
| `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.csv` | 7.3 KB | all 438 numeric cells appear in task_2_6_table_40f_48f_45f_41f_38f.md |
| `results/metrics/xgboost/tuned_vs_default.csv` | 1.7 KB | all 144 numeric cells appear in tuned_vs_default.md |

</details>

<details><summary>DELETE: old manifest (1 files, 73.3 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/CLEANUP_MANIFEST.md` | 73.3 KB | you asked for it to be deleted; stays in git history (commit 6b92da7) |

</details>

<details><summary>DELETE: other (3 files, 47.7 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/dashboard_end_to_end_40f.csv` | 45.5 KB |  |
| `results/metrics/xgboost/pool_comparison_40f_48f_45f_official.csv` | 1.1 KB |  |
| `results/metrics/xgboost/pool_comparison_40f_48f_45f_pooled_random.csv` | 1.1 KB |  |

</details>

<details><summary>DELETE: placeholder (1 files, 0.0 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/.gitkeep` | 0.0 KB | the folder is not empty |

</details>

<details><summary>DELETE: plots (1 files, 33.2 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/plots/xgboost/open_set_detection.png` | 33.2 KB | not in the list of report figures (aggregate over tiers) |

</details>

<details><summary>KEEP: plots (8 files, 0.70 MB)</summary>

| file | size | reason |
|---|---|---|
| `results/plots/xgboost/adaptation_curve_40f.png` | 65.6 KB | figure the report uses |
| `results/plots/xgboost/adaptation_curve_48f.png` | 76.7 KB | figure the report uses |
| `results/plots/xgboost/confusion_matrix_40.png` | 86.3 KB | figure the report uses |
| `results/plots/xgboost/dashboard_prediction_explanation_view.png` | 0.21 MB | figure the report uses |
| `results/plots/xgboost/explanation_stability.png` | 36.8 KB | figure the report uses |
| `results/plots/xgboost/feature_set_metrics.png` | 37.9 KB | figure the report uses |
| `results/plots/xgboost/open_set_sweep.png` | 85.5 KB | figure the report uses |
| `results/plots/xgboost/roc_curve_40.png` | 0.10 MB | figure the report uses |

</details>

<details><summary>KEEP: report / hand-off (7 files, 0.54 MB)</summary>

| file | size | reason |
|---|---|---|
| `results/NUMBERS_LEDGER.md` | 85.7 KB | kept; every entry re-pointed |
| `results/README.md` | 4.6 KB | kept; rewritten as the index |
| `results/metrics/xgboost/xai_audit_40f_example_failures.csv` | 5.7 KB | example narratives and failures (explanation section) |
| `results/metrics/xgboost/xai_audit_40f_narratives.csv` | 0.41 MB | 1,000 audited narratives (explanation section) |
| `results/task_5_5_ab_instructions.md` | 1.4 KB | A/B instructions (go with the sheet) |
| `results/task_5_5_ab_key.csv` | 1.1 KB | A/B key |
| `results/task_5_5_ab_sheet.csv` | 29.5 KB | A/B sheet (blank ratings) |

</details>

<details><summary>KEEP?: exception, needs your OK (19 files, 0.86 MB)</summary>

| file | size | reason |
|---|---|---|
| `results/feature_ranking_mutual_info.csv` | 1.2 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info.meta.json` | 0.0 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info_48f.csv` | 1.4 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info_48f.meta.json` | 0.0 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info_blockval_40f.csv` | 1.2 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info_blockval_40f.meta.json` | 0.0 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info_blockval_45f.csv` | 1.3 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info_blockval_45f.meta.json` | 0.0 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info_blockval_48f.csv` | 1.4 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/feature_ranking_mutual_info_blockval_48f.meta.json` | 0.0 KB | feature rankings (read by src/utils/config_loader.py on every pipeline run; ONBOARDING requires the shared committed rankings) |
| `results/metrics/xgboost/shap_boot_xgboost_40f.npz` | 0.19 MB | XGBoost SHAP importance and bootstrap (read by scripts/cross_model_agreement.py and explanation_stability_tiers.py; ONBOARDING step 4) |
| `results/metrics/xgboost/shap_boot_xgboost_45f.npz` | 0.27 MB | XGBoost SHAP importance and bootstrap (read by scripts/cross_model_agreement.py and explanation_stability_tiers.py; ONBOARDING step 4) |
| `results/metrics/xgboost/shap_boot_xgboost_48f.npz` | 0.28 MB | XGBoost SHAP importance and bootstrap (read by scripts/cross_model_agreement.py and explanation_stability_tiers.py; ONBOARDING step 4) |
| `results/metrics/xgboost/shap_importance_xgboost_40f.csv` | 22.8 KB | XGBoost SHAP importance and bootstrap (read by scripts/cross_model_agreement.py and explanation_stability_tiers.py; ONBOARDING step 4) |
| `results/metrics/xgboost/shap_importance_xgboost_45f.csv` | 38.0 KB | XGBoost SHAP importance and bootstrap (read by scripts/cross_model_agreement.py and explanation_stability_tiers.py; ONBOARDING step 4) |
| `results/metrics/xgboost/shap_importance_xgboost_48f.csv` | 33.4 KB | XGBoost SHAP importance and bootstrap (read by scripts/cross_model_agreement.py and explanation_stability_tiers.py; ONBOARDING step 4) |
| `results/task_5_human_audit_instructions.md` | 1.3 KB | Task 5 human audit sheet, key and instructions (blank rating template, same kind of deliverable as the A/B sheet) |
| `results/task_5_human_audit_key.csv` | 0.7 KB | Task 5 human audit sheet, key and instructions (blank rating template, same kind of deliverable as the A/B sheet) |
| `results/task_5_human_audit_sheet.csv` | 11.4 KB | Task 5 human audit sheet, key and instructions (blank rating template, same kind of deliverable as the A/B sheet) |

</details>

<details><summary>MERGE->FINDINGS: conclusions (8 files, 87.4 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/shift_conclusion_40f_45f_48f.md` | 3.8 KB | verbatim, task order |
| `results/metrics/xgboost/task_2_5_conclusion.md` | 4.9 KB | verbatim, task order |
| `results/metrics/xgboost/task_2_6_conclusion.md` | 6.6 KB | verbatim, task order |
| `results/metrics/xgboost/task_2_7_conclusion.md` | 9.2 KB | verbatim, task order |
| `results/metrics/xgboost/task_3_conclusion.md` | 8.0 KB | verbatim, task order |
| `results/metrics/xgboost/task_4_conclusion.md` | 22.1 KB | verbatim, task order |
| `results/metrics/xgboost/task_5_conclusion.md` | 20.9 KB | verbatim, task order |
| `results/metrics/xgboost/task_6_conclusion.md` | 12.0 KB | verbatim, task order |

</details>

<details><summary>MERGE->FINDINGS: protocols (appendix) (9 files, 60.1 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/task_2_5_protocol.md` | 3.0 KB | verbatim in the appendix; distilled into PROTOCOL.md |
| `results/task_2_6_protocol.md` | 4.5 KB | verbatim in the appendix; distilled into PROTOCOL.md |
| `results/task_2_7_protocol.md` | 8.2 KB | verbatim in the appendix; distilled into PROTOCOL.md |
| `results/task_3_protocol.md` | 6.5 KB | verbatim in the appendix; distilled into PROTOCOL.md |
| `results/task_4_5_protocol.md` | 6.8 KB | verbatim in the appendix; distilled into PROTOCOL.md |
| `results/task_4_protocol.md` | 6.5 KB | verbatim in the appendix; distilled into PROTOCOL.md |
| `results/task_5_5_protocol.md` | 7.3 KB | verbatim in the appendix; distilled into PROTOCOL.md |
| `results/task_5_protocol.md` | 8.1 KB | verbatim in the appendix; distilled into PROTOCOL.md |
| `results/task_6_protocol.md` | 9.1 KB | verbatim in the appendix; distilled into PROTOCOL.md |

</details>

<details><summary>MERGE->TABLES: tables (13 files, 0.29 MB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/overlap/pooled_34f/summary.md` | 3.0 KB | verbatim |
| `results/metrics/overlap/pooled_42f/summary.md` | 3.1 KB | verbatim |
| `results/metrics/xgboost/headline_tables.md` | 14.2 KB | verbatim |
| `results/metrics/xgboost/label_scheme_summary.md` | 3.7 KB | verbatim |
| `results/metrics/xgboost/label_scheme_summary_48f.md` | 3.7 KB | verbatim |
| `results/metrics/xgboost/task_2_5_final_table_40f_48f.md` | 12.0 KB | verbatim |
| `results/metrics/xgboost/task_2_6_table_40f_48f_45f_41f_38f.md` | 8.4 KB | verbatim |
| `results/metrics/xgboost/task_2_7_tables.md` | 41.0 KB | verbatim |
| `results/metrics/xgboost/task_3_tables.md` | 11.4 KB | verbatim |
| `results/metrics/xgboost/task_4_5_tables.md` | 0.11 MB | verbatim |
| `results/metrics/xgboost/task_4_tables.md` | 34.0 KB | verbatim |
| `results/metrics/xgboost/task_5_tables.md` | 24.9 KB | verbatim |
| `results/metrics/xgboost/task_6_tables.md` | 16.9 KB | verbatim |

</details>

<details><summary>RENDER->TABLES, DELETE: B1 earlier single-seed run (README Key findings) (9 files, 10.4 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/cross_dataset_feature_shift.csv` | 0.6 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/cross_dataset_results.csv` | 0.6 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/experiment_results.csv` | 3.8 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/explanation_stability.csv` | 1.1 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/feature_selection_baselines_summary.csv` | 0.4 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/open_set_sweep_40.csv` | 0.4 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/overlap_diagnostic_40.csv` | 0.2 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/split_comparison.csv` | 2.7 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/split_summary.csv` | 0.6 KB | values rendered into TABLES.md first (they have no markdown home) |

</details>

<details><summary>RENDER->TABLES, DELETE: B2 confusion matrices (counts and row-normalised) (8 files, 2.6 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/confusion_matrix_40_official.csv` | 0.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/confusion_matrix_40_official_rownorm.csv` | 0.4 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/confusion_matrix_40_pooled_random_pooled.csv` | 0.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/confusion_matrix_40_pooled_random_rownorm_pooled.csv` | 0.4 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/confusion_matrix_48_official_48f.csv` | 0.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/confusion_matrix_48_official_rownorm_48f.csv` | 0.4 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/confusion_matrix_48_pooled_random_pooled_48f.csv` | 0.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/confusion_matrix_48_pooled_random_rownorm_pooled_48f.csv` | 0.4 KB | values rendered into TABLES.md first (they have no markdown home) |

</details>

<details><summary>RENDER->TABLES, DELETE: B3 bootstrap intervals (2 files, 1.8 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/bootstrap_ci_40f_48f_45f.csv` | 0.8 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/bootstrap_paired_diff_40f_48f_45f.csv` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |

</details>

<details><summary>RENDER->TABLES, DELETE: B4 Step A shift and Task 2.6 leakage evidence (21 files, 16.9 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/leakage_40f_shift_auc.csv` | 0.1 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/leakage_40f_validation_blocks.csv` | 0.9 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/leakage_40f_validation_blocks_b200.csv` | 0.9 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/leakage_45f_shift_auc.csv` | 0.1 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/leakage_48f_shift_auc.csv` | 0.1 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/leakage_48f_validation_blocks.csv` | 0.9 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/leakage_48f_validation_blocks_b200.csv` | 0.9 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/normal_fpr_floor_40f_48f.csv` | 0.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/pooled_reference_composition.csv` | 0.5 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_group_ablation_40f.csv` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_group_ablation_48f.csv` | 1.1 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_nf_groups_40f.csv` | 0.7 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_nf_groups_45f.csv` | 0.7 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_nf_groups_48f.csv` | 0.7 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_normal_features_40f.csv` | 2.1 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_normal_features_45f.csv` | 2.4 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_normal_features_48f.csv` | 2.5 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_normal_summary_40f.csv` | 0.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_normal_summary_45f.csv` | 0.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_normal_summary_48f.csv` | 0.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/shift_ranking_stability_40f_45f_48f.csv` | 0.2 KB | values rendered into TABLES.md first (they have no markdown home) |

</details>

<details><summary>RENDER->TABLES, DELETE: B5 Task 6 small tables (2 files, 4.4 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/cross_dataset_diagnostic_importance_agreement.csv` | 1.3 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/cross_dataset_zero_shot_eval_mix.csv` | 3.1 KB | values rendered into TABLES.md first (they have no markdown home) |

</details>

<details><summary>RENDER->TABLES, DELETE: B6 tuned hyperparameters (the JSON files) (7 files, 7.3 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/tuned_params_40f.json` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/tuned_params_48f.json` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/tuned_params_blockval_40f.json` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/tuned_params_blockval_45f.json` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/tuned_params_blockval_48f.json` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/tuned_params_stage1_40f.json` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |
| `results/metrics/xgboost/tuned_params_stage1_48f.json` | 1.0 KB | values rendered into TABLES.md first (they have no markdown home) |

</details>

<details><summary>RENDER->TABLES, DELETE: B7 hierarchical / flat label-scheme metrics (subset of the Task 2.5 B1 summary) (1 files, 21.1 KB)</summary>

| file | size | reason |
|---|---|---|
| `results/metrics/xgboost/methods_zero_shot_b1_40f_summary.csv` | 21.1 KB | values rendered into TABLES.md first (they have no markdown home) |

</details>

## 4. Value coverage of every CSV and JSON proposed for deletion

For each file, every numeric cell (trivial 0 / 1 / small integers excluded) was looked up, at the displayed precision, in the markdown section that would be its home (its table twin, or the conclusion that quotes it). **Found** = present in that section; the remainder is listed. 'Rendered' files are first written into TABLES.md Appendix B, so nothing in them is lost.

**A. Fully housed (14 files): every value is already in a table or conclusion that is kept.** `best_possible_accuracy.csv`, `best_possible_accuracy.csv`, `accuracy_three_numbers_40f_48f_45f.csv`, `accuracy_three_numbers_40f_48f_tuned_f1_auc.csv`, `cross_dataset_diagnostic_univariate.csv`, `open_set_step1_40f.csv`, `open_set_step1_45f.csv`, `open_set_step1_48f.csv`, `open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv`, `stability_xgboost_40f.csv`, `stability_xgboost_45f.csv`, `stability_xgboost_48f.csv`, `task_2_6_table_40f_48f_45f_41f_38f.csv`, `tuned_vs_default.csv`

**B. Rendered into TABLES.md Appendix B before deletion (no value lost):**

- **B1 earlier single-seed run (README Key findings)** (9 files, 10.4 KB): `cross_dataset_feature_shift.csv`, `cross_dataset_results.csv`, `experiment_results.csv`, `explanation_stability.csv`, `feature_selection_baselines_summary.csv`, `open_set_sweep_40.csv`, `overlap_diagnostic_40.csv`, `split_comparison.csv`, `split_summary.csv`
- **B2 confusion matrices (counts and row-normalised)** (8 files, 2.6 KB): `confusion_matrix_40_official.csv`, `confusion_matrix_40_official_rownorm.csv`, `confusion_matrix_40_pooled_random_pooled.csv`, `confusion_matrix_40_pooled_random_rownorm_pooled.csv`, `confusion_matrix_48_official_48f.csv`, `confusion_matrix_48_official_rownorm_48f.csv`, `confusion_matrix_48_pooled_random_pooled_48f.csv`, `confusion_matrix_48_pooled_random_rownorm_pooled_48f.csv`
- **B3 bootstrap intervals** (2 files, 1.8 KB): `bootstrap_ci_40f_48f_45f.csv`, `bootstrap_paired_diff_40f_48f_45f.csv`
- **B4 Step A shift and Task 2.6 leakage evidence** (21 files, 16.9 KB): `leakage_40f_shift_auc.csv`, `leakage_40f_validation_blocks.csv`, `leakage_40f_validation_blocks_b200.csv`, `leakage_45f_shift_auc.csv`, `leakage_48f_shift_auc.csv`, `leakage_48f_validation_blocks.csv`, `leakage_48f_validation_blocks_b200.csv`, `normal_fpr_floor_40f_48f.csv`, `pooled_reference_composition.csv`, `shift_group_ablation_40f.csv`, `shift_group_ablation_48f.csv`, `shift_nf_groups_40f.csv`, `shift_nf_groups_45f.csv`, `shift_nf_groups_48f.csv`, `shift_normal_features_40f.csv`, `shift_normal_features_45f.csv`, `shift_normal_features_48f.csv`, `shift_normal_summary_40f.csv`, `shift_normal_summary_45f.csv`, `shift_normal_summary_48f.csv`, `shift_ranking_stability_40f_45f_48f.csv`
- **B5 Task 6 small tables** (2 files, 4.4 KB): `cross_dataset_diagnostic_importance_agreement.csv`, `cross_dataset_zero_shot_eval_mix.csv`
- **B6 tuned hyperparameters (the JSON files)** (7 files, 7.3 KB): `tuned_params_40f.json`, `tuned_params_48f.json`, `tuned_params_blockval_40f.json`, `tuned_params_blockval_45f.json`, `tuned_params_blockval_48f.json`, `tuned_params_stage1_40f.json`, `tuned_params_stage1_48f.json`
- **B7 hierarchical / flat label-scheme metrics (subset of the Task 2.5 B1 summary)** (1 files, 21.1 KB): `methods_zero_shot_b1_40f_summary.csv` (only the hierarchical / flat / current rows of the metrics fine_recall_macro, false_positive_rate, detection_rate, group_size_share are rendered; the remaining columns of this file are listed under C)

**C1. Deleted; the missing values are per-seed rows, per-trial lists, per-flow text and rank / bookkeeping columns** (the means over seeds of these quantities are in the tables that are kept, and every quoted number is housed, see section 5):

| file | numeric cells | found | not found | columns with most of the missing values |
|---|---|---|---|---|
| `narrative_test_40f_narratives.csv` | 4598 | 388 | 4210 | flow (2298), confidence (1912) |
| `narrative_falsepos_40f_features.csv` | 1133 | 384 | 749 | n_in_test (320), share (256), narratives_citing (173) |
| `narrative_falsepos_48f_features.csv` | 1088 | 394 | 694 | n_in_test (320), share (250), narratives_citing (124) |
| `narrative_test_40f_summary.csv` | 560 | 98 | 462 | f_consistent_of_determined (84), cited_numeric_per_narrative (84), mean_failures_per_narrative (78), cited_features_per_narrative (76) |
| `tier_study_xgboost_45f_runs.csv` | 525 | 71 | 454 | f1 (25), recall_Normal (25), ece (25), fpr_at_90_detection (25) |
| `tier_study_xgboost_48f_runs.csv` | 525 | 77 | 448 | det95_threshold (25), det95_fpr_gap (25), ece (24), fpr_at_90_detection (24) |
| `narrative_test_48f_summary.csv` | 523 | 92 | 431 | f_consistent_of_determined (78), cited_features_per_narrative (77), cited_numeric_per_narrative (76), mean_failures_per_narrative (74) |
| `tier_study_xgboost_40f_runs.csv` | 420 | 80 | 340 | ece (20), fpr_at_90_detection (20), false_unknown_alarm_rate (20), det95_threshold (20) |
| `hyperparameter_search_stage1_48f.csv` | 374 | 41 | 333 | val_macro_f1 (41), val_attack_auc (41), colsample_bytree (40), best_iteration (40) |
| `hyperparameter_search_40f.csv` | 374 | 42 | 332 | val_attack_auc (41), colsample_bytree (40), best_iteration (40), reg_lambda (39) |
| `hyperparameter_search_48f.csv` | 372 | 40 | 332 | val_macro_f1 (41), val_attack_auc (41), colsample_bytree (40), best_iteration (40) |
| `hyperparameter_search_stage1_40f.csv` | 374 | 44 | 330 | val_macro_f1 (41), val_attack_auc (41), colsample_bytree (40), reg_lambda (39) |
| `hyperparameter_search_blockval_48f.csv` | 384 | 56 | 328 | reg_lambda (41), best_iteration (41), colsample_bytree (40), subsample (38) |
| `hyperparameter_search_blockval_45f.csv` | 385 | 59 | 326 | reg_lambda (41), best_iteration (41), colsample_bytree (40), val_attack_auc (39) |
| `hyperparameter_search_blockval_40f.csv` | 386 | 73 | 313 | reg_lambda (41), best_iteration (41), colsample_bytree (40), seconds (39) |
| `narrative_falsepos_40f_faithfulness.csv` | 360 | 83 | 277 | n_in_test (40), ci_high (38), top_flip_k5 (36), top_drop_k5 (34) |
| `narrative_falsepos_48f_faithfulness.csv` | 352 | 83 | 269 | n_in_test (40), top_drop_k5 (37), ci_low (35), difference (34) |
| `narrative_falsepos_40f_groups.csv` | 200 | 50 | 150 | n_in_test (20), mean_cited_features_class_relative (20), atypicality_mean (20), atypicality_defined (20) |
| `narrative_falsepos_48f_groups.csv` | 200 | 52 | 148 | n_in_test (20), mean_cited_features_class_relative (20), atypicality_defined (20), calibrated_confidence_mean (19) |
| `xai_audit_validation_40f_summary.csv` | 146 | 13 | 133 | f_share_typical_cue (40), mean_failures_per_narrative (36), f_consistent_of_determined (35), f_share_no_monotone_relation (22) |
| `xai_audit_40f_summary.csv` | 143 | 12 | 131 | f_share_typical_cue (40), f_consistent_of_determined (34), mean_failures_per_narrative (33), f_share_no_monotone_relation (24) |
| `xai_audit_48f_summary.csv` | 136 | 11 | 125 | f_share_typical_cue (40), f_consistent_of_determined (35), mean_failures_per_narrative (34), f_share_no_monotone_relation (16) |
| `xai_audit_validation_48f_summary.csv` | 137 | 13 | 124 | f_share_typical_cue (39), f_consistent_of_determined (36), mean_failures_per_narrative (34), f_share_no_monotone_relation (15) |
| `open_set_boost_selection_40f_scores.csv` | 200 | 99 | 101 | n_pseudo (80), pseudo_auroc (21) |
| `narrative_validation_40f_summary.csv` | 109 | 13 | 96 | f_consistent_of_determined (16), mean_failures_per_narrative (16), cited_features_per_narrative (16), cited_numeric_per_narrative (15) |
| `open_set_boost_selection_48f_scores.csv` | 200 | 107 | 93 | n_pseudo (80), pseudo_auroc (13) |
| `xai_additivity_40f.csv` | 90 | 60 | 30 | n (30) |
| `xai_additivity_45f.csv` | 90 | 60 | 30 | n (30) |
| `xai_additivity_48f.csv` | 90 | 60 | 30 | n (30) |
| `narrative_falsepos_40f_separation.csv` | 30 | 3 | 27 | auroc (27) |
| `narrative_falsepos_48f_separation.csv` | 30 | 3 | 27 | auroc (27) |
| `narrative_test_40f_calibration.csv` | 15 | 2 | 13 | temperature (5), ece_calibrated (5), ece_raw (3) |
| `narrative_test_48f_calibration.csv` | 15 | 2 | 13 | temperature (5), ece_raw (5), ece_calibrated (3) |
| `open_set_step2_40f.csv` | 238 | 226 | 12 | exact_twin_share (12) |
| `label_scheme_comparison.csv` | 66 | 55 | 11 | accuracy (3), macro_f1_not_comparable_across_schemes (3), best_possible_accuracy_pairs_deduped (3), recall_Overlap-Group-1 (1) |
| `label_scheme_comparison_48f.csv` | 66 | 55 | 11 | accuracy (3), macro_f1_not_comparable_across_schemes (3), best_possible_accuracy_pairs_deduped (3), recall_Overlap-Group-1 (1) |
| `label_scheme_comparison_pooled_48f.csv` | 66 | 55 | 11 | accuracy (3), macro_f1_not_comparable_across_schemes (3), best_possible_accuracy_pairs_deduped (3), recall_Overlap-Group-1 (1) |
| `label_scheme_comparison_pooled.csv` | 66 | 56 | 10 | accuracy (3), best_possible_accuracy_pairs_deduped (3), macro_f1_not_comparable_across_schemes (2), recall_Overlap-Group-1 (1) |
| `open_set_step2_48f.csv` | 238 | 230 | 8 | exact_twin_share (8) |
| `narrative_validation_40f_calibration.csv` | 3 | 0 | 3 | temperature (1), ece_raw (1), ece_calibrated (1) |
| `tier_baselines_summary_xgboost_40f.csv` | 22 | 19 | 3 | random_f1_max (3) |
| `tier_baselines_summary_xgboost_45f.csv` | 21 | 18 | 3 | random_f1_max (3) |
| `tier_baselines_summary_xgboost_48f.csv` | 22 | 19 | 3 | random_f1_max (3) |

**C2. Deleted, but these summary files hold MEAN values that no kept table shows** (not quoted by any document, hence not in the ledger; they are metrics outside the displayed subset: per-class precision / recall / F1 of the headline runs, the full metric grids of the Task 2.5 / 2.6 methods and adaptation runs, the ablation pools' other metrics, the 45-feature operating points). **This is the list to veto**: tell me any file you want rendered into TABLES.md instead (about 10 KB of markdown per 10 KB of CSV).

| file | size | numeric cells | mean values without a home | all cells without a home |
|---|---|---|---|---|
| `methods_transductive_b3_40f_summary.csv` | 27.0 KB | 1212 | 229 | 758 |
| `methods_transductive_b3_48f_summary.csv` | 27.0 KB | 1212 | 224 | 777 |
| `headline_summary.csv` | 18.3 KB | 1101 | 197 | 844 |
| `adaptation_48f_summary.csv` | 21.6 KB | 1020 | 182 | 203 |
| `methods_zero_shot_b1_48f_summary.csv` | 21.1 KB | 958 | 180 | 612 |
| `adaptation_40f_summary.csv` | 21.6 KB | 1020 | 174 | 185 |
| `task_2_5_final_table_40f_48f.csv` | 12.0 KB | 1392 | 145 | 170 |
| `headline_tuned_auc_official_summary.csv` | 8.8 KB | 552 | 103 | 427 |
| `headline_full_no_ttl_summary.csv` | 10.1 KB | 550 | 102 | 447 |
| `headline_tuned_f1_official_summary.csv` | 8.8 KB | 550 | 100 | 411 |
| `methods_leak_zero_45f_summary.csv` | 6.5 KB | 302 | 67 | 201 |
| `methods_leak_zero_41f_summary.csv` | 7.0 KB | 304 | 62 | 194 |
| `methods_leak_zero_38f_summary.csv` | 6.8 KB | 302 | 58 | 190 |
| `leakage_40f_summary.csv` | 10.8 KB | 356 | 45 | 77 |
| `leakage_48f_summary.csv` | 10.8 KB | 356 | 38 | 68 |
| `adaptation_40f_split_summary.csv` | 4.9 KB | 204 | 23 | 24 |
| `adaptation_45f_split_summary.csv` | 2.7 KB | 102 | 22 | 26 |
| `adaptation_48f_split_summary.csv` | 4.9 KB | 204 | 21 | 23 |
| `adaptation_38f_split_summary.csv` | 2.8 KB | 102 | 20 | 21 |
| `operating_point_summary_45f.csv` | 1.0 KB | 78 | 18 | 66 |
| `adaptation_41f_split_summary.csv` | 2.9 KB | 102 | 17 | 19 |
| `adaptation_40f_domain5_summary.csv` | 3.0 KB | 102 | 12 | 13 |
| `adaptation_48f_domain20_summary.csv` | 3.0 KB | 102 | 11 | 12 |
| `tier_summary_xgboost_45f.csv` | 1.7 KB | 112 | 5 | 13 |
| `tier_summary_xgboost_48f.csv` | 1.8 KB | 112 | 4 | 13 |
| `operating_point_summary_40f.csv` | 1.0 KB | 79 | 3 | 40 |
| `tier_baselines_summary_accuracy_xgboost_40f.csv` | 0.4 KB | 22 | 3 | 15 |
| `tier_baselines_summary_accuracy_xgboost_48f.csv` | 0.4 KB | 22 | 3 | 16 |
| `tier_summary_xgboost_40f.csv` | 1.4 KB | 89 | 3 | 9 |
| `tier_baselines_summary_accuracy_xgboost_45f.csv` | 0.4 KB | 22 | 2 | 13 |
| `operating_point_summary_48f.csv` | 1.0 KB | 78 | 1 | 38 |

Files whose full content is lost (not rendered, not housed): `narrative_test_40f_narratives.csv` (1.3 MB, 1,150 narrative texts of the Task 5.5 sample; the A/B sheet built from it stays) and `dashboard_end_to_end_40f.csv` (64 per-flow comparisons; the conclusion states all 64 match on every field). Everything is recoverable from the tags and the zip.

## 5. Ledger entries that must be re-pointed

All 316 entries change file, because TABLES.md and FINDINGS.md replace every current source. Destination by source:

| current source | entries | destination in the new layout |
|---|---|---|
| `headline_summary.csv` | 24 | TABLES.md, `Source: headline_summary.md` (table cell) |
| `headline_full_no_ttl_summary.csv` | 1 | TABLES.md, `Source: headline_full_no_ttl_summary.md` (table cell) |
| `accuracy_three_numbers_40f_48f_45f.csv` | 2 | TABLES.md, `Source: accuracy_three_numbers_40f_48f_45f.md`, `Source: accuracy_three_numbers_40f_48f_tuned_f1_auc.md` (table cell) |
| `tuned_vs_default.csv` | 3 | TABLES.md, `Source: tuned_vs_default.md` (table cell) |
| `operating_point_summary_40f.csv` | 2 | TABLES.md, `Source: operating_point_summary.md` (table cell) |
| `operating_point_summary_48f.csv` | 1 | TABLES.md, `Source: operating_point_summary.md` (table cell) |
| `task_2_5_final_table_40f_48f.csv` | 15 | TABLES.md, `Source: task_2_5_conclusion.md`, `Source: task_2_5_final_table_40f_48f.md`, `Source: task_2_6_conclusion.md`, `Source: task_2_6_table_40f_48f_45f_41f_38f.md` (table cell) |
| `task_2_6_table_40f_48f_45f_41f_38f.csv` | 12 | TABLES.md, `Source: task_2_6_table_40f_48f_45f_41f_38f.md` (table cell) |
| `leakage_40f_shift_auc.csv` | 2 | TABLES.md Appendix B4 (Step A shift and Task 2.6 leakage evidence); rendered from this file first |
| `leakage_45f_shift_auc.csv` | 2 | TABLES.md Appendix B4 (Step A shift and Task 2.6 leakage evidence); rendered from this file first |
| `leakage_48f_shift_auc.csv` | 2 | TABLES.md Appendix B4 (Step A shift and Task 2.6 leakage evidence); rendered from this file first |
| `leakage_40f_validation_blocks.csv` | 2 | TABLES.md Appendix B4 (Step A shift and Task 2.6 leakage evidence); rendered from this file first |
| `pooled_reference_composition.csv` | 3 | TABLES.md Appendix B4 (Step A shift and Task 2.6 leakage evidence); rendered from this file first |
| `shift_normal_summary_40f.csv` | 2 | TABLES.md Appendix B4 (Step A shift and Task 2.6 leakage evidence); rendered from this file first |
| `shift_normal_summary_45f.csv` | 1 | TABLES.md Appendix B4 (Step A shift and Task 2.6 leakage evidence); rendered from this file first |
| `shift_normal_summary_48f.csv` | 1 | TABLES.md Appendix B4 (Step A shift and Task 2.6 leakage evidence); rendered from this file first |
| `task_2_7_tables.md` | 19 | TABLES.md, same section, i.e. `Source: fpr_study_fewshot_48f_45f_41f.md`, `Source: fpr_study_final_40f_45f_48f.md` |
| `tier_summary_xgboost_40f.csv` | 7 | TABLES.md, `Source: task_3_conclusion.md`, `Source: tier_summary_xgboost.md` (table cell); 1 of 7 values appear there only at a coarser precision or in the conclusion text (re-pointed to the displayed value) |
| `tier_summary_xgboost_45f.csv` | 4 | TABLES.md, `Source: task_3_conclusion.md`, `Source: tier_summary_xgboost.md` (table cell) |
| `tier_summary_xgboost_48f.csv` | 4 | TABLES.md, `Source: task_3_conclusion.md`, `Source: tier_summary_xgboost.md` (table cell) |
| `stability_xgboost_48f.csv` | 4 | TABLES.md, `Source: stability_xgboost.md` (table cell) |
| `open_set_step1_40f.csv` | 7 | TABLES.md, `Source: open_set_step1_40f_45f_48f.md` (table cell) |
| `open_set_step1_45f.csv` | 2 | TABLES.md, `Source: open_set_step1_40f_45f_48f.md` (table cell) |
| `open_set_step1_48f.csv` | 6 | TABLES.md, `Source: open_set_step1_40f_45f_48f.md` (table cell) |
| `open_set_step2_40f.csv` | 7 | TABLES.md, `Source: open_set_step2_40f_48f.md`, `Source: open_set_step2_sources_40f_45f_48f.md` (table cell); 1 of 7 values appear there only at a coarser precision or in the conclusion text (re-pointed to the displayed value) |
| `task_4_tables.md` | 8 | TABLES.md, same section, i.e. `Source: open_set_step3_40f_45f_48f.md` |
| `open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.csv` | 4 | TABLES.md, `Source: open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.md` (table cell) |
| `task_4_conclusion.md` | 1 | FINDINGS.md, `Source: task_4_conclusion.md` (text statement) |
| `task_4_5_tables.md` | 17 | TABLES.md, same section, i.e. `Source: open_set_boost_calibration_40f_48f.md`, `Source: open_set_boost_combo_40f_48f.md`, `Source: open_set_boost_iforest_40f_48f.md` |
| `open_set_boost_selection_40f_scores.csv` | 2 | TABLES.md, `Source: open_set_boost_calibration_40f_48f.md`, `Source: open_set_boost_combo_40f_48f.md`, `Source: open_set_boost_distance_40f_48f.md`, `Source: open_set_boost_ensemble_40f_48f.md`, `Source: open_set_boost_iforest_40f_48f.md`, `Source: open_set_boost_oe_40f_48f.md`, `Source: open_set_boost_perclass_40f_48f.md`, `Source: task_4_conclusion.md` (table cell) |
| `open_set_boost_selection_48f_scores.csv` | 2 | TABLES.md, `Source: open_set_boost_calibration_40f_48f.md`, `Source: open_set_boost_combo_40f_48f.md`, `Source: open_set_boost_distance_40f_48f.md`, `Source: open_set_boost_ensemble_40f_48f.md`, `Source: open_set_boost_iforest_40f_48f.md`, `Source: open_set_boost_oe_40f_48f.md`, `Source: open_set_boost_perclass_40f_48f.md`, `Source: task_4_conclusion.md` (table cell) |
| `task_5_tables.md` | 37 | TABLES.md, same section, i.e. `Source: narrative_falsepos_40f_48f.md`, `Source: narrative_test_40f_48f.md`, `Source: xai_audit_40f_48f.md`, `Source: xai_faithfulness_40f_45f_48f.md` |
| `task_5_conclusion.md` | 1 | FINDINGS.md, `Source: task_5_conclusion.md` (text statement) |
| `task_6_tables.md` | 24 | TABLES.md, same section, i.e. `Source: cross_dataset_step1_zero_shot.md`, `Source: cross_dataset_step2_diagnostic.md`, `Source: cross_dataset_step3_align.md`, `Source: cross_dataset_step4_fewshot.md` |
| `cross_dataset_diagnostic_importance_agreement.csv` | 1 | TABLES.md Appendix B5 (Task 6 small tables); rendered from this file first |
| `split_comparison.csv` | 15 | TABLES.md Appendix B1 (earlier single-seed run (README Key findings)); rendered from this file first |
| `experiment_results.csv` | 11 | TABLES.md Appendix B1 (earlier single-seed run (README Key findings)); rendered from this file first |
| `feature_selection_baselines_summary.csv` | 8 | TABLES.md Appendix B1 (earlier single-seed run (README Key findings)); rendered from this file first |
| `explanation_stability.csv` | 3 | TABLES.md Appendix B1 (earlier single-seed run (README Key findings)); rendered from this file first |
| `split_summary.csv` | 3 | TABLES.md Appendix B1 (earlier single-seed run (README Key findings)); rendered from this file first |
| `README.md` | 1 | stays in README.md (text statement; README is kept) |
| `cross_dataset_results.csv` | 4 | TABLES.md Appendix B1 (earlier single-seed run (README Key findings)); rendered from this file first |
| `cross_dataset_feature_shift.csv` | 3 | TABLES.md Appendix B1 (earlier single-seed run (README Key findings)); rendered from this file first |
| `label_scheme_comparison.csv` | 12 | TABLES.md, `Source: label_scheme_summary.md`, `Source: label_scheme_summary_48f.md` (table cell) |
| `methods_zero_shot_b1_40f_summary.csv` | 12 | TABLES.md Appendix B7 (hierarchical / flat label-scheme metrics (subset of the Task 2.5 B1 summary)); rendered from this file first |
| `pooled_34f/summary.md` | 6 | TABLES.md, `Source: pooled_34f/summary.md` (text block) |
| `pooled_42f/summary.md` | 6 | TABLES.md, `Source: pooled_42f/summary.md` (text block) |

Entries whose value is shown at a coarser precision than the ledger quotes (for example Welch z 8.8552 shown as 8.9, an exact-twin share 0.777 shown as 0.78) are re-pointed with the displayed value and the precision is stated in the entry. Entries re-pointed to rendered tables (`B1`-`B7`) are exactly the 75 that had no markdown home. Two entries of Task 4 and the Task 6 Spearman mean come from conclusion text or rendered tables as listed.

## 6. Files that scripts, tests or documents read (reported, not edited)

**Code that loads a results file** (found by `read_csv` / `json.load` / `np.load` in `src/`, `pipelines/`, `scripts/`, `dashboard/`; tests use temporary directories and read no committed result):

| file(s) proposed for deletion | read by | consequence if deleted |
|---|---|---|
| `feature_ranking_*.csv` + `.meta.json` (exception, 10 files) | `src/utils/config_loader.py:59` on every run; `pipelines/train_pipeline.py` (`ensure_feature_ranking`) | the tiers cannot be built, or the ranking is regenerated and may differ, breaking comparability with the committed 30 / 20 / 15 tiers. **Recommend KEEP.** |
| `shap_importance_xgboost_*.csv`, `shap_boot_xgboost_*.npz` (exception, 6 files) | `scripts/cross_model_agreement.py:61`, `scripts/explanation_stability_tiers.py:78`, `scripts/characterize_shift.py:224` | ONBOARDING step 4 ('needs XGBoost's committed SHAP files') stops working. **Recommend KEEP.** |
| `tuned_params_*.json` (rendered as B6) | `pipelines/tune_xgboost.py:141`, and the `--tuned` / stage-1 / block-validation paths of `run_headline_seeds.py`, `run_methods.py`, `run_fpr_study.py` | those reruns fail until `tune_xgboost.py` is run again (a long job). Not needed by teammates. |
| `headline_summary.csv` | `pipelines/run_adaptation.py:194` (pooled-random FPR reference for the adaptation plot), `scripts/accuracy_table.py`, `compare_pools.py`, `compare_tuned.py`, `final_table.py` | those scripts cannot be re-run without rerunning `run_headline_seeds.py` |
| `methods_*_summary.csv`, `adaptation_*_summary.csv`, `task_2_5_final_table_*.csv`, `leakage_*_summary.csv` | `scripts/final_table.py`, `scripts/leakage_table.py` | the Task 2.5 / 2.6 tables cannot be re-rendered without the pipelines |
| `open_set_step*.csv`, `open_set_boost_selection_*_scores.csv` | `pipelines/run_openset_boost.py:395,402` (reuses the stored pseudo-unknown selection), `scripts/open_set_summary.py` | a Task 4.5 rerun recomputes the selection instead of reading it |
| `tier_study_xgboost_*_runs.csv`, `tier_baselines_summary_*.csv` | `pipelines/run_tier_study.py:208` (`--parts baselines`), `scripts/tier_summary.py` | the baselines part and the tier table need the tiers part run first |
| `cross_dataset_diagnostic_*.csv`, `cross_dataset_zero_shot_eval_mix.csv` | `scripts/cross_dataset_summary.py:168` | the Task 6 tables cannot be re-rendered without the study |
| `narrative_*` and `xai_*` summary CSVs, `xai_additivity_*.csv` | `scripts/narrative_summary.py`, `scripts/xai_summary.py` | tables cannot be re-rendered without the runs |
| `narrative_test_40f_narratives.csv` | `scripts/make_ab_sheet.py:58` | the A/B sheet (kept) cannot be regenerated; `xai_audit_40f_narratives.csv`, read by `make_human_audit_sheet.py`, is kept |
| `open_set_sweep_40.csv` | `src/evaluation/plots.py:119` (reads the file the same run wrote) | none; the run rewrites it |
| config keys `experiments.baselines_summary_csv`, `split_summary_csv`, `baselines_csv`, `pooled_split_csv`, `paths.feature_ranking` | `configs/config.yaml` (read by `run_all_experiments.py`, which rewrites those files) | none, except the ranking above |

Tests: `tests/` never reads a committed result (all use `tmp_path`); the suite is unaffected, expected 328 before and after.

**Documents that name a removed or merged file** (to be re-pointed in Step 2): in the table below.

| document | removed or merged files it names | how |
|---|---|---|
| `README.md` | 21: `cross_dataset_feature_shift.csv`, `experiment_results.csv`, `feature_ranking_mutual_info.csv`, `feature_selection_baselines_summary.csv`, `headline_tables.md`, `label_scheme_comparison.csv`, `label_scheme_comparison_48f.csv`, `label_scheme_comparison_pooled.csv`, `label_scheme_summary.md`, `methods_zero_shot_b1_40f_summary.csv`, `open_set_sweep_40.csv`, `split_comparison.csv`, `split_summary.csv`, `task_2_6_conclusion.md` ... | re-point to FINDINGS.md / TABLES.md sections |
| `PROJECT_PLAN.md` | 9: `label_scheme_comparison.csv`, `label_scheme_summary.md`, `methods_zero_shot_b1_40f_summary.csv`, `task_2_7_conclusion.md`, `task_3_conclusion.md`, `task_4_conclusion.md`, `task_5_conclusion.md`, `task_5_human_audit_sheet.csv`, `task_6_conclusion.md` | re-point to FINDINGS.md / TABLES.md sections |
| `ONBOARDING.md` | 2: `feature_ranking_mutual_info.csv`, `task_3_protocol.md` | re-point to FINDINGS.md / TABLES.md sections |
| `results/README.md` | 14: `CLEANUP_MANIFEST.md`, `bootstrap_ci_40f_48f_45f.csv`, `bootstrap_paired_diff_40f_48f_45f.csv`, `feature_ranking_mutual_info.csv`, `feature_ranking_mutual_info_48f.csv`, `headline_tables.md`, `narrative_test_40f_narratives.csv`, `shift_conclusion_40f_45f_48f.md`, `task_2_7_tables.md`, `task_3_tables.md`, `task_4_5_tables.md`, `task_4_tables.md`, `task_5_tables.md`, `task_6_tables.md` | rewritten as the index |
| the merged conclusions, tables and protocols themselves | file names inside them (for example `task_6_tables.md`, `xai_audit_40f_example_failures.csv`, `results/task_5_protocol.md`) | left verbatim as you asked; a one-paragraph note at the top of FINDINGS.md and TABLES.md says that these names are the `Source:` sections of the two files and that removed CSVs are in the tags |
## 7. The new hand-off files (outline; written in Step 2 after approval)

- **PROTOCOL.md** (one page): (1) official UNSW-NB15 split is primary, the pooled random split is reported only as an optimistic best case that shares neighbouring flows with training; (2) exact deduplication before splitting; label scheme `current` (Analysis / Backdoor / DoS merged into Overlap-Group-1); (3) block-grouped validation, blocks of `tier_study.block_size` = 1,000 rows with a `tier_study.buffer` = 200-row gap (the values will be read from `configs/config.yaml`, not from memory); (4) seeds 42-46, mean +/- std (ddof 1); (5) pools 40 / 45 / 48 features, tiers full / 30 / 20 / 15 from the committed rankings; (6) zero-shot: nothing tuned on the official test file, declared parameters in `tier_study.model_params`; (7) metric definitions: FPR at exactly 95% detection, det95 FPR with the threshold chosen on block-grouped validation, ECE (15 bins), open-set at 5% false-Unknown; (8) commands: `run_tier_study.py --model`, `tier_summary.py`, `explanation_stability_tiers.py`, `cross_model_agreement.py`, the test command. Every rule is cross-checked against the nine protocols; the protocols themselves stay verbatim in the FINDINGS.md appendix, so no declared rule is lost.
- **REFERENCE_XGBOOST.csv**: columns `model, pool, tier, split, n_seeds, accuracy_mean/std, macro_f1_mean/std, detection_rate_mean/std, false_positive_rate_mean/std, fpr_at_95_detection_mean/std, det95_fpr_mean/std, roc_auc_attack_vs_normal_mean/std, ece_mean/std`, plus `source` (the TABLES.md section and table). Rows: whole-pool 40 and 48 (official and pooled random) and 45 (official, pooled), and the 30 / 20 / 15 tiers of each pool (official; pooled macro F1 only, as in the table). **A value that is not in TABLES.md is left blank, not filled from a CSV**: the Task 3 tier table has no argmax detection rate, and has `det95 FPR` (threshold on block-grouped validation) but not the threshold-free FPR at 95% detection, which exists only for the whole pools in the headline table. The two FPR-at-95 variants therefore get separate columns, so a teammate compares like with like. The stability numbers (tier-pair Spearman / cosine / top-10 Jaccard, noise floor) go in a second block of rows of the same file with `split = stability` and their own columns.
- **TEMPLATE_model_results.csv**: the same columns, blank, one row per (model, pool, tier, split) for the 12 pool-tier cells x {official, pooled_random}, with `model` empty and a `notes` column.

## 8. Questions for you

1. **Exceptions.** The brief's layout leaves out three things that code or hand-off needs: the 10 feature-ranking files (read on every run), the 6 XGBoost SHAP files (the ONBOARDING comparison step), and the 3 human-audit files (a blank rating template, like the A/B sheet that you keep). I recommend keeping all three groups (19 files, 0.85 MB). Strictly following the brief gives 20 files; keeping only the 3 human-audit files gives 23.
2. **Rendering the small CSVs (section 4B, 50 files, about 0.1 MB of markdown)** so that no finding or ledger value loses its home. The alternative is to delete them and accept 75 ledger entries without a source (section 5). I recommend rendering. **And look at section 4 C2**: the summary files listed there hold mean values that no kept table shows; they are deleted unless you name them.
3. **Test count:** the brief says 328; it is 328 (the audit-wording fix raised it from 327).
