# results/

Committed CSV metrics (`metrics/<model.type>/`), charts (`plots/<model.type>/`) and the feature rankings.

## File naming
- `_48f` suffix: the 48-feature pool (42 raw official columns + 6 engineered). No suffix: the 40-feature pool
  (34 raw + 6 engineered) run on the SAME deduplicated rows and splits (`feature_selection.pool: base`).
- `_wide`, `_none`, `_pooled`: label scheme / pooled random split variants (see `config.yaml`).
- `confusion_matrix_<tier>_<official|pooled_random>[_rownorm].csv`: test confusion matrix, rows = true class.
- `normal_fuzzers_diagnostic/`: why Normal flows are called Fuzzers on the official split (`scripts/diagnose_normal_fuzzers.py`).
- `overlap/`: exact/near-twin and best-possible-accuracy analysis (`scripts/overlap_analysis.py`).

## Data version
All numbers here are on the 42-feature UNSW-NB15 training/testing sets (`data/raw`, 257,673 rows, 162,745 after exact
deduplication). Figures in older documents (78 % F1, 67-75 % zero-day detection, 0.97 ROC-AUC) are withdrawn.

## Feature rankings were regenerated
`feature_ranking_mutual_info.csv` (40-feature pool) was regenerated on the 42-feature data, because deduplication over
42 columns keeps ~17,500 more rows than over 34 and the ranking depends on the training rows. **Its order and top-15 set
differ from the ranking behind the older 34-feature results** (committed at `af809d2`); results produced before
commit `70a845d` are tied to the old ranking. The 48-feature ranking is `feature_ranking_mutual_info_48f.csv`.
