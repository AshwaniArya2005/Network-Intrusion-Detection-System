# Shared protocol: the rules every model follows

One page. These rules make results of different models comparable with the XGBoost reference (`REFERENCE_XGBOOST.csv`). The full declared protocols are kept verbatim inside the numbered files `01` to `06` (under their `Source:` headings); nothing declared there is dropped, this page only distils the rules that apply to every model.

## Data and splits
1. **Official split is primary.** Train on `unsw_nb15_train.csv`, test on `unsw_nb15_test.csv` (`data.use_official_split: true`). The 42-column files are used (257,673 rows, 162,745 after step 2).
2. **Exact duplicate rows are removed before splitting** (done by the loader). Label scheme `current`: Analysis, Backdoor and DoS are one class, `Overlap-Group-1`. Worms and Shellcode are held out of training and validation and used only as the zero-day flows of the open-set checks.
3. **The pooled random split is a best case.** It mixes both files and shares neighbouring flows (window counts and labels of consecutive rows) with its training rows, so it is optimistic. Always label it "pooled random (optimistic)"; never report it as the result.
4. **Block-grouped validation for every selection.** Training and validation are built from contiguous blocks of the training file: `tier_study.block_size: 1000` rows, `tier_study.buffer: 200` rows of gap on each side of a block boundary, 15% of the blocks as validation (`data.val_size`), through `pipelines/train_pipeline.block_validation_splits`. A random validation split under-predicts the test false-positive rate and must not be used to choose a threshold, an operating point or a hyperparameter.
5. **The official test labels never choose a method, a threshold or a hyperparameter.** Everything is zero-shot: the model sees only training data.

## Seeds, pools and tiers
6. **Seeds 42, 43, 44, 45, 46** (`tier_study.seeds`, `experiments.headline_seeds`). A seed changes the model seed and the block draw; the test file is fixed. Report mean and standard deviation (ddof = 1) over the five seeds.
7. **Pools:** 40 features (34 raw + 6 engineered), 45 (the 48-feature pool without `sttl`, `dttl`, `ct_state_ttl`), 48 (42 raw + 6 engineered).
8. **Tier grid:** the top-N of the committed mutual-information rankings (`results/feature_ranking_mutual_info_blockval*.csv`, shared by all models, never regenerated). Pool 48: 48 / 40 / 30 / 20 / 15; pool 45: 45 / 40 / 30 / 20 / 15; pool 40: 40 / 30 / 20 / 15. If a runner would rewrite a tracked ranking file, stop and ask.
9. **Do not change** `tier_study.seeds`, `tier_study.shap_rows` (1,000 explained rows), `tier_study.bootstrap` (100 resamples) or `evaluation.ece_bins` (15): otherwise the cross-model comparison is not paired.
10. **Hyperparameters are declared, not tuned:** `model.params` for the headline run and `tier_study.model_params.<model type>` for the tier study (random forest: 150 trees, depth 10, min leaf 5; logistic regression: `max_iter` 300). A model run with other settings is not comparable; say so.

## Metrics (all on the official test split unless the split column says otherwise)
- accuracy, macro F1, attack detection rate and false-positive rate at the argmax decision (a Normal flow called any attack counts as a false positive);
- **FPR at 95% detection**, threshold-free (the false-positive rate at the point of the ROC curve where 95% of attacks are detected) and **det95 FPR**, the test FPR at the threshold chosen on block-grouped validation for 95% detection (reported with the detection reached);
- attack-versus-normal ROC AUC (1 - P(Normal) as the score), expected calibration error with 15 equal-width bins;
- open-set: the max-softmax threshold is the quantile that flags 5% of KNOWN validation flows as Unknown (`open_set.target_false_unknown_rate: 0.05`); report detection and AUROC on the held-out zero-day flows and the false-Unknown rate on known test flows. Never tune the threshold on the zero-day flows.

## Where results go
Outputs of a model go to `results/metrics/<model.type>/` only; never edit or overwrite another model's files (XGBoost's are committed under `metrics/xgboost/`). Every new function needs a test. Report in `TEMPLATE_model_results.csv` format (same columns as the reference).

## Commands (details and the config key for a new model: `ONBOARDING.md`)
| step | command |
|---|---|
| A headline, 5 seeds, official and pooled | `python pipelines/run_headline_seeds.py` (with `model.type` set to your model) |
| B tier study | `python pipelines/run_tier_study.py --model <type>` then `python scripts/tier_summary.py --model <type>` |
| C explanation stability across tiers | `python scripts/explanation_stability_tiers.py --model <type>` |
| D cross-model SHAP agreement (after two models finished) | `python scripts/cross_model_agreement.py --models xgboost <type>` |
| E open-set and explanation checks (XGBoost only for now) | `python pipelines/run_open_set_study.py --step scores`, `python pipelines/run_xai_study.py --part faithfulness` |
| tests | `python -m pytest tests -q` |
