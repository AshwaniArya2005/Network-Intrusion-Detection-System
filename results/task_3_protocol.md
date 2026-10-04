# Task 3 protocol (declared before any Task 3 result was produced)

Novelty 3: feature selection and explanation consistency. Everything is ZERO-SHOT (training data only), official split, scheme `current`.

## Design
- **Block-grouped validation.** The training / validation split of every run is built from contiguous blocks of the training file
  (block size 1,000 rows, 200-row gap on each side of every boundary, `data.val_size` = 15% of the blocks;
  `pipelines/train_pipeline.block_validation_splits`). A random validation split shares neighbouring flows with the training rows and is
  optimistic (Task 2.6); it is used only for comparison. The validation-chosen 95%-detection operating point (`det95`) is therefore chosen
  on the block-grouped validation split; the random-validation counterpart is quoted from the earlier headline / operating-point files for
  the full pools (40 / 48 features; the 45-feature pool is run once with `run_operating_point.py`).
- **Seeds 42-46** change the model seed and the block draw (which blocks are validation); the official test file is fixed.
- **Feature rankings:** mutual information with the target on the seed-42 block-grouped TRAINING split (20,000-row sample, seed 42), one ranking
  per pool, shared by all seeds and all three model types (so the tiers are the same feature sets for every model). Files:
  `results/feature_ranking_mutual_info_blockval[_40f|_45f|_48f].csv`. Tiers: 48 pool: 48 / 40 / 30 / 20 / 15; 45 pool: 45 / 40 / 30 / 20 / 15;
  40 pool: 40 / 30 / 20 / 15.
- **Pools:** 40 (34 raw + 6 engineered), 45 (48 minus sttl, dttl, ct_state_ttl), 48 (42 raw + 6 engineered).
- **Which extra official columns survive** is reported for every tier: the seven window-count ct_* columns, the other ct_* columns
  (ct_state_ttl, ct_flw_http_mthd, ct_ftp_cmd) and the TTL columns (sttl, dttl, ct_state_ttl).

## Step 1 (XGBoost tier study)
- Primary metric: **macro F1** on the official test split (mean and std over the 5 seeds). Also accuracy, detection, FPR (argmax and block-validated
  det95), attack-vs-normal ROC-AUC, ECE, open-set detection and AUROC. The pooled random split is shown as a labelled best-case column
  (it shares neighbouring flows with its training rows and is optimistic).
- Claim tested: shrinking the feature set to 15 costs no more than retraining noise. Criterion A (noise): the mean macro F1 drop from the full pool
  is at most 2 x the seed-to-seed std of the full pool. Criterion B (practical): the drop is at most 0.02 macro F1. Both are reported for every tier;
  a tier failing A is reported as significantly worse (with the Welch z of the difference).
- Ranked tier vs 10 random subsets vs the worst-N features, for tiers 30 / 20 / 15 of each pool (macro F1; z-score and percentile of the ranked mean
  among the random draws, as in the earlier study). Random draws: model seed 42 on the seed-42 split, subset seed 42 + draw.

## Step 2 (explanation stability, XGBoost)
- Global SHAP importance = mean |SHAP| over classes, on 1,000 random training rows (the earlier study used 2,000; reduced so the same rows can be
  explained for every model type in Step 4). Pairwise definitions kept from `src/xai/explanation_stability.py`: Spearman rank correlation,
  cosine similarity and top-10 Jaccard overlap over the common features. Tier agreement = pairs of tiers of the same seed; noise floor = the same
  tier under different seeds (all 10 pairs of the 5 seeds). Protocol change from the earlier study: the earlier noise floor kept the training rows
  fixed and changed only the model seed; here a seed also changes the block draw, so the floor includes training-subset variation.
- Descriptive bands (no threshold test): high >= 0.9, moderate 0.7-0.9, low < 0.7.

## Step 3 (logistic regression, random forest)
Same grid, metrics and stability study. Declared settings (no tuning): random forest 150 trees, max depth 10, min leaf 5; logistic regression
`max_iter` 300 (lbfgs, balanced ** 0.5 sample weights as for XGBoost); inputs are the same scaled numeric / label-encoded categorical matrix
(logistic regression sees categorical codes as numbers, which XGBoost and the forest handle by splits). SHAP explainer: TreeExplainer for the forest,
LinearExplainer for logistic regression (background 100 rows). Random subsets / worst-N are run for XGBoost only. FPR on the official split is
reported for every model; nothing is tuned on test.

## Step 4 (cross-model agreement)
For every pool, tier and seed, XGBoost vs logistic regression vs random forest global SHAP importance (Spearman, cosine, top-10 Jaccard), with
95% percentile intervals from 100 paired bootstrap resamples of the explained rows (the same 1,000 rows and the same resample indices for all
three models), averaged over the seeds. Whether agreement drops for the smaller tiers is read from these numbers.

## Not claimed
Stability is evidence about the explanations, not about the cause of the official-split shift, which remains undetermined.
