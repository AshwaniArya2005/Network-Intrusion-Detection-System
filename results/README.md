# results/

Everything the report and a teammate need, and nothing else. XGBoost is the only model with results here.

## For the report
| file | content |
|---|---|
| `01_protocol_and_headline.md` | headline (official split against the optimistic pooled split, 5 seeds), tuning, bootstrap intervals, accuracy ceiling, per-class headline metrics, label schemes and class overlap, the earlier single-seed run, shift diagnostics |
| `02_novelty1_open_set.md` | open-set / zero-day detection and its boosts |
| `03_novelty2_explanations.md` | explanation faithfulness, narrative audit, class-relative narratives, false-positive explanations |
| `04_novelty3_feature_tiers.md` | feature tiers and explanation stability |
| `05_novelty4_cross_dataset.md` | cross-dataset generalisation (UNSW-NB15 and CICIDS2017) |
| `06_fpr_and_adaptation.md` | why the false-positive rate stays high, what labels do, neighbour-leakage checks, what did not help |
| `NUMBERS_LEDGER.md` | every headline number the documents quote, with the file, section and cell it comes from (checked by program) |
| `plots/xgboost/` | the figures: confusion matrix and ROC (40 features), open-set sweep, explanation stability, feature-set metrics, adaptation curves (40 and 48 features), dashboard screenshot |
| `metrics/xgboost/xai_audit_40f_narratives.csv`, `xai_audit_40f_example_failures.csv`, `narrative_test_40f_narratives.csv` | narrative samples (1,000 audited narratives; ten example failures; the sample the A/B sheet is built from) |
| `task_5_5_ab_sheet.csv`, `task_5_5_ab_key.csv`, `task_5_5_ab_instructions.md`; `task_5_human_audit_sheet.csv`, `task_5_human_audit_key.csv`, `task_5_human_audit_instructions.md` | the two blank rating sheets with their keys and instructions (no ratings collected yet) |

Each numbered file holds the original conclusion, table and protocol files of its area unchanged, one `Source: <original file name>` section each (headings demoted two levels), followed by tables rendered from small CSV files that were removed. The file names mentioned inside them are those `Source:` sections.

## For handing over
| file | content |
|---|---|
| `PROTOCOL.md` | one page: the shared rules every model follows, and the commands |
| `REFERENCE_XGBOOST.csv` | the XGBoost headline, tier and stability numbers to compare with (`not computed` / `not applicable` where a value does not exist in the XGBoost tables) |
| `TEMPLATE_model_results.csv` | the same columns, blank: one row per (model, pool, tier, split, protocol) |
| `../ONBOARDING.md` | how to add a model and run steps A-E (section "Reference results and how to compare") |
| `feature_ranking_mutual_info*.csv` (+ `.meta.json`) | the shared feature rankings that define the tiers; read by the pipelines, never regenerate |
| `metrics/xgboost/shap_importance_xgboost_<N>f.csv`, `shap_boot_xgboost_<N>f.npz` | the XGBoost SHAP files used by the cross-model agreement step |

Outputs of any model go to `results/metrics/<model.type>/`; plots to `results/plots/<model.type>/` (written by the pipelines, hence not moved).

## Data version
All numbers are on the 42-feature UNSW-NB15 training and testing sets (257,673 rows, 162,745 after exact deduplication). `_48f` in a name: the 48-feature pool; no suffix: the 40-feature pool on the same rows and splits. Figures in older documents (78% F1, 67-75% zero-day detection, 0.97 ROC-AUC) are withdrawn. `feature_ranking_mutual_info.csv` was regenerated on the 42-feature data (commit `70a845d`); results produced before that commit are tied to the older ranking.

## What was removed, and where to recover it
Per-seed, per-run and per-flow result files, per-trial lists, per-tier plots, scratch diagnostics, duplicate and superseded files, and the standalone copies of everything that now lives in the numbered files (the conclusion, table and protocol files, and about 50 small CSV and JSON files rendered into tables). Nothing quoted was dropped; the numbers that now exist only as markdown tables are listed in `NUMBERS_LEDGER.md`.
- Git tag `pre-lean-2026-10`: the state before the last consolidation (`git show pre-lean-2026-10:<path>`).
- Git tag `pre-cleanup-2026-10`: the state before the first cleanup, with the per-seed and per-flow files.
- Backup zip `D:\Github Projects\_backups\xai-ids-results-pre-cleanup.zip`: the whole `results/` folder (including untracked scratch) at that time.
- The manifests of both cleanups are in git history: `results/CLEANUP_MANIFEST.md` (last version at commit `6b92da7`) and `results/LEAN_MANIFEST.md` (commit `b2387f1`; it lists every removed file and the reason). `git log --diff-filter=D --name-only -- results/` shows where each file was deleted.

The scripts that summarise runs (`scripts/*_summary.py`, `tier_summary.py`, ...) read the per-run files of their pipeline; they need that pipeline run first.
