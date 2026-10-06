# Onboarding: run your own model

Everything a teammate needs to get comparable results for one model. You edit **two config values**, run **one command**, and read your results in folders named after your model. Nothing of another model is touched.

## 1. Install

```bash
git clone <repo> && cd "XAI Network IDS System"
python -m venv .venv && .venv\Scripts\activate          # Windows; on Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests -q                                # should end green (synthetic data only, writes nothing outside a temp folder)
```

`scripts/setup.sh` does the same for Linux/macOS and also installs the dashboard's frontend.

## 2. Data files

Put the official UNSW-NB15 training and testing CSVs in `data/raw/` (`unsw_nb15_train.csv`, `unsw_nb15_test.csv`; `python scripts/download_datasets.py` prints where to get them). **Pool 48 (the primary pool) needs the full official files with all 42 feature columns; the older 36-column download only supports pool 40.** The workflow checks this before it starts and says which pools your files allow. If the files are missing it stops, unless you pass `--allow-synthetic` (generated data for a smoke test; the log then says loudly that the numbers are not results).

## 3. Set your model

Edit `configs/config.yaml` (or a copy):

```yaml
model:
  type: "random_forest"        # any registered type: xgboost | random_forest | logistic_regression | yours (section 7)
  params:                      # the ONE place for hyperparameters; every step uses it
    n_estimators: 200
    max_depth: 10
    n_jobs: -1
```

Do not edit anything else (seeds, tier lists, block sizes and the shared rankings are part of the protocol, see section 8).
`tier_study.model_params.<type>` is only used for a *different* model family named with `--model` in the tier study; for your configured `model.type` the tier study takes `model.params` (the log says so).

## 4. Run the one command

```bash
python pipelines/run_model.py                              # steps A, B, C for the configured model, pool 48
python pipelines/run_model.py --config my_config.yaml      # a copy of the config instead of configs/config.yaml
python pipelines/run_model.py --steps A B                  # only some steps
python pipelines/run_model.py --run-name deep              # folders <type>__deep, to try several hyperparameter sets side by side
python pipelines/run_model.py --pool 40                    # a comparison pool (pool 40 or 45); default is the primary pool 48
python pipelines/run_model.py --out-dir results/_local_scratch/mine   # keep everything local and untracked
```

| step | what | reuses |
|---|---|---|
| A | headline metrics: five seeds, official split, and the pooled random split (labelled the optimistic best case) | `pipelines/run_headline_seeds.py` |
| B | feature-tier study (top 48 / 40 / 30 / 20 / 15 features by the shared ranking) with SHAP, confusion matrices and ROC curves, saved models; then the summary tables | `pipelines/run_tier_study.py`, `scripts/tier_summary.py` |
| C | explanation stability across the tiers | `scripts/explanation_stability_tiers.py` |

A filled copy of `results/TEMPLATE_model_results.csv` is written at the end (`scripts/fill_model_template.py`). The command first runs a pre-flight check (model type buildable, data files present, which pools the files allow) and **stops instead of overwriting** if the model's folders already hold results; use `--run-name NAME` for new folders or `--overwrite` to replace them. `--config` or the environment variable `XAI_IDS_CONFIG` (for any other script) replaces `configs/config.yaml`; the file that was loaded is logged. Expect roughly 20-40 minutes for XGBoost on the real data; a random forest takes longer (its SHAP step grows with trees x depth), logistic regression is fast.

## 5. Where everything appears

| folder | content |
|---|---|
| `results/metrics/<model.type>/` | all tables (`headline_full_*`, `tier_study_*`, `tier_summary_*`, `shap_importance_*`, `stability_*`), `run_config.yaml` (the settings used), and `model_results_<model.type>.csv` (the filled template) |
| `results/plots/<model.type>/` | `confusion_matrix_<T>f.png` and `roc_curve_<T>f.png` for each tier T of pool 48 (a comparison pool N adds `pool<N>_`, e.g. `confusion_matrix_pool40_30f.png`); the ROC figure has a bold attack-vs-normal curve and one thin curve per class |
| `models_saved/<model.type>/` | the saved model and preprocessor of every tier (git-ignored) |

With `--run-name NAME` every folder is `<model.type>__NAME`. Commit only your own `results/metrics/<your model>/` files and plots; never edit another model's files. The XGBoost pool-48 plots are tracked as the reference; plots of other models are git-ignored unless you add them on purpose.

## 6. Compare with the reference

| file (under `results/`) | what it is |
|---|---|
| `PROTOCOL.md` | the one-page shared rules |
| `REFERENCE_XGBOOST.csv` | XGBoost headline, tier and explanation-stability numbers (mean and std over 5 seeds); the `role` column marks pool 48 as `primary`, pools 40 and 45 as comparison; `not computed` = the XGBoost tables have no such number, `not applicable` = the quantity does not exist |
| `TEMPLATE_model_results.csv` | the same columns, blank; your filled copy is `metrics/<model>/model_results_<model>.csv` |
| `rankings/` | the two shared pool-48 rankings (`feature_ranking_mutual_info_48f.csv`, `feature_ranking_mutual_info_blockval_48f.csv`, each with a `.meta.json` sidecar) |
| `01_...` to `06_...md`, `NUMBERS_LEDGER.md` | XGBoost conclusions by research area, and every quoted number with its source |

Compare your filled table with the `primary` rows of `REFERENCE_XGBOOST.csv` row by row (same pool, tier, split, protocol). The XGBoost pool-48 numbers are slightly worse than pool 40 on FPR at the argmax decision (0.2933 against 0.2853) and ECE (0.1093 against 0.0876); its higher open-set detection depends on the window-count `ct_*` columns (a within-capture effect), so do not expect it on another network.

Separate commands after your own run:
- **D. Cross-model SHAP agreement** (needs two models' tier studies): `python scripts/cross_model_agreement.py --models xgboost <type>`.
- **E. Open-set and explanation studies** are XGBoost-only research runs (`pipelines/run_open_set_study.py`, `run_xai_study.py`, ...); they stop with a clear message unless `model.type: xgboost`.

## 7. Adding a model that is not registered

1. Create `src/models/your_model.py` with a class implementing `BaseModel` (`src/models/base_model.py`: `fit`, `predict`, `predict_proba`, `get_feature_importance`, `save`, `load`, `underlying_model`). A scikit-learn-compatible classifier needs no new class: wrap it in `SklearnModel` (`src/models/sklearn_model.py`).
2. Register it in `src/models/model_factory.py`: one `elif model_type == "your_model":` branch.
3. If it does not save as a joblib pickle, add its suffix in `src.utils.config_loader._ARTIFACT_SUFFIX` (XGBoost is `.json`, everything else `.pkl`).
4. Set `model.type` and `model.params`, then section 4. Add the type to `MODEL_TYPES` in `tests/conftest.py` for the interface tests.

```python
# src/models/model_factory.py
elif model_type == "lightgbm":
    from src.models.sklearn_model import SklearnModel
    import lightgbm as lgb
    return SklearnModel(lgb.LGBMClassifier(**params))
```

SHAP needs nothing: `SHAPExplainer` picks `TreeExplainer` for tree ensembles (XGBoost, LightGBM, random forest), `LinearExplainer` for anything with `.coef_`, and the slow `KernelExplainer` for the rest (MLP, SVM); the log names the explainer and warns when the slow one is used. Training, evaluation, the open-set wrapper and the dashboard only use the `BaseModel` interface.

## 8. Rules that make runs comparable

- **Zero-shot, official split, scheme `current`.** Nothing is tuned on the official test file.
- **Block-grouped validation** (`tier_study.block_size` / `buffer`): a random validation split shares neighbouring flows with its training rows and is optimistic. The pooled random split is reported only as that best case.
- **Shared rankings.** The pool-48 rankings are committed and never regenerated; the comparison pools 40 and 45 regenerate theirs on first use, so a rerun there may differ slightly from the committed comparison numbers.
- **Same seeds and explained rows** (`tier_study.seeds` 42-46, `shap_rows`, `bootstrap`): leave them alone, otherwise the cross-model agreement is not a paired comparison.
- Outputs of a model whose parameters differ from the declared ones are not comparable with the declared settings: say so in your write-up.
- **Model families:** logistic regression gets the same scaled numeric matrix and label-encoded categorical columns as the trees and may print lbfgs convergence warnings (expected). Random forest uses `n_jobs: -1` and its SHAP step takes several times longer than its fit. Class weights (balanced ** 0.5) are passed as `sample_weight` for every model.

## 9. Troubleshooting

| symptom | cause and fix |
|---|---|
| `Missing data file(s)` | the UNSW-NB15 CSVs are not in `data/raw/`; `python scripts/download_datasets.py` shows where to get them |
| `Pool 48 needs the full official files` | your CSVs have the older 36 columns; run with `--pool 40` or get the full 42-column files |
| `These folders already contain results` | the model's folders are not empty; `--run-name NAME` for new folders, `--overwrite` to replace |
| `SYNTHETIC DATA` in the log | the real files were not found and generated data is used; the numbers are not results |
| `<study> is an XGBoost-only study` | the open-set, explanation, FPR and cross-dataset studies train XGBoost; set `model.type: xgboost` (they would otherwise write XGBoost numbers into your model's folder) |
| `FileNotFoundError: Feature ranking ...` on pool 40 or 45 | those rankings are not committed; run the tier study for that pool first (`run_model.py --pool 40`) |
| `--help` starts a run | 11 scripts have no command-line parser (`run_all_experiments.py`, `evaluate_pipeline.py`, `check_explainability.py`, `download_datasets.py`, `final_table.py`, `leakage_table.py`, `normal_fpr_floor.py`, `pooled_reference_composition.py`, `cross_dataset_summary.py`, `make_ab_sheet.py`, `make_human_audit_sheet.py`): they run when called with any argument, including `--help`. Read their docstring instead. |
| a summary script reports a missing XGBoost file | the repository is trimmed (per-seed files are in git tag `pre-cleanup-2026-10`); compare with `REFERENCE_XGBOOST.csv`, or run the pipeline first |
| notebooks do not start | `notebook` is in `requirements.txt`; the notebooks in `notebooks/` are exploratory and read `configs/` and `src/` only |
