# results/

Everything the report and a teammate need, and nothing else. XGBoost is the only model with results here.

## Layout
`results/` holds the six numbered files, `PROTOCOL.md`, `NUMBERS_LEDGER.md`, `REFERENCE_XGBOOST.csv`, `TEMPLATE_model_results.csv` and this file, plus four folders: `metrics/` (per-model CSVs; XGBoost: SHAP files and narrative samples), `plots/` (figures, one folder per model type), `rankings/` (the pool-48 feature rankings) and `rating/` (blank rating sheets and keys).

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
| `plots/xgboost/` | the figures: confusion matrix and ROC of the headline tier (`confusion_matrix_pool48_tier48.png`, `roc_curve_pool48_tier48.png`; primary pool 48, full tier; the ROC has a bold attack-vs-normal curve and one thin one-vs-rest curve per class), open-set sweep, explanation stability, feature-set metrics, adaptation curves (40 and 48 features). The dashboard screenshot was removed and nothing generates one (no script, pipeline or test writes a screenshot; `.gitignore` ignores `results/plots/*/dashboard_*.png`). The pipeline writes one confusion matrix and one ROC figure for every tier of every pool of every model (`confusion_matrix_pool<N>_tier<T>.png`, `roc_curve_pool<N>_tier<T>.png`, into `plots/<model.type>/`); those are git-ignored (pool 40 and 45 plots stay local), only the two headline plots are tracked |
| `metrics/xgboost/xai_audit_40f_narratives.csv`, `xai_audit_40f_example_failures.csv`, `narrative_test_40f_narratives.csv` | narrative samples (1,000 audited narratives; ten example failures; the sample the A/B sheet is built from) |
| `rating/narratives_ab_sheet.csv`, `rating/narratives_ab_key.csv`, `rating/narratives_ab_instructions.md` | the blank A/B rating sheet with its key and instructions (no ratings collected yet). The separate 30-narrative human-audit template was removed; `scripts/make_human_audit_sheet.py` rebuilds it from `xai_audit_40f_narratives.csv`, and tag `pre-lean-2026-10` holds the old copy |

Each numbered file holds the original conclusion, table and protocol files of its area unchanged, one `Source: <original file name>` section each (headings demoted two levels), followed by tables rendered from small CSV files that were removed. The file names mentioned inside them are those `Source:` sections.

## For handing over
| file | content |
|---|---|
| `PROTOCOL.md` | one page: the shared rules every model follows, and the commands |
| `REFERENCE_XGBOOST.csv` | the XGBoost headline, tier and stability numbers to compare with; the `role` column marks pool 48 as the primary reference and pools 40 and 45 as comparison rows (`not computed` / `not applicable` where a value does not exist in the XGBoost tables) |
| `TEMPLATE_model_results.csv` | the same columns, blank: one row per (model, pool, tier, split, protocol) |
| `../ONBOARDING.md` | how to add a model and run steps A-E (section "Reference results and how to compare") |
| `rankings/feature_ranking_mutual_info_48f.csv`, `rankings/feature_ranking_mutual_info_blockval_48f.csv` (+ `.meta.json`) | the shared feature rankings of the primary pool 48 that define the tiers; read by the pipelines (`paths.feature_ranking`), never regenerate; the sidecars stop a committed ranking from being rewritten. The rankings of pools 40 and 45 are not committed: they are regenerated into the same folder on the first tier run (or `run_all_experiments.py` / `train_pipeline.py --write-ranking` for pool 40), so a rerun may differ slightly from the committed comparison numbers, and other studies on those pools raise `FileNotFoundError` until then |
| `metrics/xgboost/shap_importance_xgboost_<N>f.csv`, `shap_boot_xgboost_<N>f.npz` | the XGBoost SHAP files used by the cross-model agreement step |

Outputs of any model go to `results/metrics/<model.type>/`; plots to `results/plots/<model.type>/` (written by the pipelines, hence not moved).

## Other models
The numbered files, the ledger and `REFERENCE_XGBOOST.csv` describe XGBoost only: they are the reference, and a teammate's results are not added to them. A model's own results go to `metrics/<model.type>/` (the same scripts write that model's tables there, for example `tier_summary_<type>.md` and `stability_<type>.md`) and its plots to `plots/<model.type>/`. To compare, run steps A to C of `../ONBOARDING.md` for the model, fill `TEMPLATE_model_results.csv` from those outputs (a script that fills it automatically does not exist yet) and read it next to `REFERENCE_XGBOOST.csv`, row by row. The shared rules are in `PROTOCOL.md`. A write-up for another model should be its own file (for example `metrics/<type>/README.md`), not an edit of the numbered files.

## Primary pool
The primary pool is 48: the full official feature set (42 raw columns + 6 engineered features), which needs the full official files (a download with fewer columns only supports pool 40). Pools 40 (34 raw + 6 engineered) and 45 (pool 48 without the three TTL columns) are comparison pools whose numbers stay in the tables, the ledger and the reference file. Pool 48 is slightly worse than pool 40 on FPR at the argmax decision (0.2933 against 0.2853) and ECE (0.1093 against 0.0876); its higher open-set detection depends on the window-count `ct_*` columns, a within-capture effect shown by the leakage check, and its lower FPR at 95% detection is shared between those columns and the TTL columns, so do not expect either on another network.

## Data version
All numbers are on the 42-feature UNSW-NB15 training and testing sets (257,673 rows, 162,745 after exact deduplication). `_48f` in a name: the 48-feature pool; no suffix: the 40-feature pool on the same rows and splits. Figures in older documents (78% F1, 67-75% zero-day detection, 0.97 ROC-AUC) are withdrawn. The 40-feature pool's ranking (`feature_ranking_mutual_info.csv`, no longer committed) was regenerated on the 42-feature data (commit `70a845d`); results produced before that commit are tied to the older ranking. The committed ranking files are in the tags `pre-lean-2026-10` and `pre-cleanup-2026-10`.

## What was removed, and where to recover it
Per-seed, per-run and per-flow result files, per-trial lists, per-tier plots, scratch diagnostics, duplicate and superseded files, and the standalone copies of everything that now lives in the numbered files (the conclusion, table and protocol files, and about 50 small CSV and JSON files rendered into tables). Nothing quoted was dropped; the numbers that now exist only as markdown tables are listed in `NUMBERS_LEDGER.md`.
- Git tag `pre-lean-2026-10`: the state before the last consolidation (`git show pre-lean-2026-10:<path>`).
- Git tag `pre-cleanup-2026-10`: the state before the first cleanup, with the per-seed and per-flow files.
- Backup zip `D:\Github Projects\_backups\xai-ids-results-pre-cleanup.zip`: the whole `results/` folder (including untracked scratch) at that time.
- The manifests of both cleanups are in git history: `results/CLEANUP_MANIFEST.md` (last version at commit `6b92da7`) and `results/LEAN_MANIFEST.md` (commit `b2387f1`; it lists every removed file and the reason). `git log --diff-filter=D --name-only -- results/` shows where each file was deleted.

The scripts that summarise runs (`scripts/*_summary.py`, `tier_summary.py`, ...) read the per-run files of their pipeline; they need that pipeline run first.
