# Onboarding: adding your own model

This project is built so each teammate can plug in a different classifier
(Logistic Regression, Random Forest, LightGBM, an MLP, ...) by touching **one new
file + one config line**. This doc is the result of an end-to-end audit of the
codebase for that claim — what's genuinely swappable today, what wasn't (and has
now been fixed), and exactly which files you need to touch vs. leave alone.

## TL;DR: what to do

1. Create `src/models/your_model.py` with a class implementing `BaseModel`
   (`src/models/base_model.py`) — `fit`, `predict`, `predict_proba`,
   `get_feature_importance`, `save`, `load`, `underlying_model`. Copy
   `src/models/sklearn_model.py` as a starting point if your model has a
   scikit-learn-compatible API (LightGBM, MLPClassifier, SVC, etc. all do).
2. Register it in `src/models/model_factory.py` — one `elif` branch.
3. Set `model.type: "your_model"` and your hyperparameters under `model.params`
   in `configs/config.yaml`.
4. Run `python pipelines/run_all_experiments.py` (or `train_pipeline.py`).

That's it. **Nothing else needs to change** — training, evaluation, SHAP
explanations, the open-set wrapper, and the dashboard all pick your model up
automatically. This was verified, not assumed: see the "what was actually
broken" section below.

## Where the team's models stand

| Model | State in this repo |
|---|---|
| XGBoost | reference model; full experiment suite run (see README "Key findings") |
| Random Forest, Logistic Regression | supported via `model.type` (`src/models/sklearn_model.py`); **no comparison results have been run yet** |
| LightGBM | not implemented; the worked example at the end of this file is the starting point |
| MLP | not implemented; `MLPClassifier` works through `SklearnModel`, but SHAP falls back to the slow `KernelExplainer` |

To get a comparable result for your model: set `model.type`, run `python pipelines/run_all_experiments.py`,
and read `results/metrics/<model.type>/` (outputs are namespaced by model type, so they never overwrite
another model's). The feature ranking (`results/rankings/feature_ranking_mutual_info_48f.csv` for the primary pool 48) is model-independent mutual
information, so all models are compared on the same feature sets. Note that every result in the README is
XGBoost-specific, and `model.params` is shared across tiers (no per-tier re-tuning).

## Files you will touch

| File | What you do |
|---|---|
| `src/models/your_model.py` (new) | Implement `BaseModel` for your classifier |
| `src/models/model_factory.py` | Add one `elif model_type == "your_model": return YourModel(params)` in `create_model` |
| `configs/config.yaml` | `model.type: "your_model"`, your hyperparameters under `model.params` |

## Files you will NOT need to touch

`pipelines/train_pipeline.py`, `pipelines/evaluate_pipeline.py`,
`pipelines/run_all_experiments.py`, `src/models/open_set_wrapper.py`,
`src/xai/shap_explainer.py`, `src/xai/narrative_generator.py`,
`src/evaluation/*.py`, `dashboard/backend/*.py`, `src/preprocessing.py`. All of
these talk to your model only through the `BaseModel` interface, `predict_proba`'s
`(n_samples, n_classes)` shape, and `model.underlying_model` — nothing in them
names a specific model type.

## What the audit found — pass/fail per area

### 1. Model interface — PASS
`BaseModel` (abstract: `fit`/`predict`/`predict_proba`/`get_feature_importance`/
`save`/`load`/`underlying_model`) is the only contract every pipeline file uses.
Traced every import of `XGBoostModel` across the repo — training, evaluation,
SHAP, open-set, dashboard — all of it goes through `create_model()` and the
`BaseModel` interface, never `XGBoostModel` directly. No `.get_booster()` or
other XGBoost-specific calls exist outside `src/models/xgboost_model.py` itself.

### 2. Config-driven model selection — PASS, one real gap fixed
`model.type` + `model.params` in `configs/config.yaml` fully control model
selection with no code changes. **Gap found and fixed**: `dashboard.model_path`/
`preprocessor_path` used to be separate hardcoded string literals independent of
`model.type` — switching `model.type` and retraining would silently leave the
dashboard loading the *old* model's file (or worse, unpickling the wrong object
type into the wrong wrapper class). Fixed by deriving both paths from
`model.type` + `dashboard.feature_set` in one place
(`src.utils.config_loader.get_dashboard_paths`) — there's now nothing to
duplicate or forget to update.

(A model type can also be wrapped as a two-stage `HierarchicalModel` when `data.label_scheme` is
`hierarchical`; `src.models.model_factory.create_scheme_model` is the one place that decides, and
`SHAPExplainer` explains such a model stage by stage.)

Serialization is already correctly abstracted per model type: `XGBoostModel`
uses XGBoost's native `save_model`/`load_model` (JSON, not pickle — portable
across xgboost versions); `SklearnModel` (Random Forest, Logistic Regression,
and your new sklearn-API model) uses `joblib`, which is standard for sklearn
estimators. `BaseModel.save(path)`/`load(path)` takes a generic path string in
both cases — each subclass decides internally how to use it. Artifact names follow
the model: XGBoost saves `.json` (and refuses any other suffix rather than silently
renaming it), every other model saves `.pkl`; `src.utils.config_loader.artifact_suffix`
is the one place that mapping lives — add your model there if it isn't a joblib pickle. You don't need to
do anything for this; `joblib.dump`/`joblib.load` in `SklearnModel` already
works for any sklearn-compatible estimator, LightGBM's sklearn wrapper included.

### 3. SHAP / explainability compatibility — was a real gap, now fixed
This was exactly the breakage point predicted: `SHAPExplainer` used to hardcode
`shap.TreeExplainer(model.underlying_model)`, which raises for non-tree models.
A teammate plugging in Logistic Regression or an MLP would have hit a crash the
first time SHAP explanations were requested.

**Fixed**: `SHAPExplainer` now auto-detects the right explainer from the fitted
model itself, in order:
1. **TreeExplainer** — tries this first; it natively covers XGBoost, LightGBM,
   CatBoost, and sklearn tree ensembles (Random Forest, Gradient Boosting) all
   in one branch, no per-library special-casing needed.
2. **LinearExplainer** — used if the model exposes `.coef_` (Logistic
   Regression, and any other sklearn linear model).
3. **KernelExplainer** — universal fallback for anything else (MLP, SVM, KNN,
   ...). Much slower (sampling-based) — expect noticeably longer SHAP compute
   times if your model lands here. This is inherent to Kernel SHAP, not
   something to optimize away.

All three paths were empirically tested (not just read as code) with real
sklearn estimators — Random Forest → TreeExplainer, Logistic Regression →
LinearExplainer, an actual `MLPClassifier` → KernelExplainer — all producing
valid SHAP values with no code changes beyond instantiating the model.

One caveat worth knowing: for non-tree models, the SHAP "background" reference
sample is built lazily from whatever data first reaches the explainer. If your
first call is `local_explanation()` on a single row rather than
`global_importance()`/`compute_shap_values()` on a batch, your background
sample will be that one row — a warning is logged when this happens, but for
best explanation quality, call `global_importance(X_train)` once during setup
before requesting per-row explanations.

`src/xai/narrative_generator.py` was already model-agnostic — confirmed it
operates purely on the `pd.Series` SHAP value array and feature names, no
model-specific field access anywhere.

### 4. Open-set / threshold logic — PASS
`OpenSetWrapper` only calls `model.fit(...)` and `model.predict_proba(X)`, then
does plain `numpy.argmax`/`max` on the returned `(n_samples, n_classes)` array.
Fully model-agnostic already, no changes needed.

### 5. Tests — mostly generalize, noted where they don't
`tests/test_model.py::test_model_factory_implements_base_model_interface` is
already parametrized across `["xgboost", "random_forest", "logistic_regression"]`
and asserts against the `BaseModel` interface only — this is the right pattern;
add your model type to that list to get the same interface-conformance check for
free. The save/load-roundtrip and open-set-wrapper tests use `create_model("xgboost", ...)`
as a concrete stand-in to test generic wrapper behavior (not testing anything
XGBoost-specific) — you don't need to duplicate these for a new model type
unless you want extra confidence in your own serialization path.
Beyond these, the suite now has pipeline tests (a synthetic end-to-end run for every label scheme), dashboard
API tests, cross-dataset, feature-selection, overlap-analysis and hierarchical-model tests (140 in total);
`pytest tests -q` should stay green when you add your model.
`tests/test_xai.py`'s SHAP tests were XGBoost-only before this audit; the
underlying `SHAPExplainer` is now verified model-agnostic (see section 3), so
these don't need duplication either, but nothing stops you from adding a
parametrized variant if you want CI coverage for your specific model's SHAP path.

### 6. Deliverable
This file. The two real gaps found (SHAP explainer hardcoded to trees;
dashboard path duplicated instead of derived) were fixed, not just documented —
see `src/xai/shap_explainer.py` and `src/utils/config_loader.get_dashboard_paths`.
At the time of those fixes the XGBoost pipeline was checked before/after: same predictions,
same F1 (0.7781 — a historical figure from the old pooled split before duplicates were removed; current numbers are in results/metrics/), same SHAP values and narratives on a fixed set of real test
rows, byte-for-byte identical to before the refactor (a one-off check of that refactor, not a statement about the current pipeline or its results).

## Reproducing the feature-tier and explanation-stability study for your own model

XGBoost's feature-tier and explanation-stability study (feature tiers, SHAP stability, cross-model agreement) is committed. Each teammate runs the **same** study for their own model
so the numbers are comparable. The shared rules are on one page in `results/PROTOCOL.md` (read it first); the full declared protocol is inside `results/04_novelty3_feature_tiers.md` (section `Source: feature_tiers_protocol.md`). The rules that make runs comparable:

- **Zero-shot, official split, scheme `current`.** Nothing is tuned on the official test file.
- **Block-grouped validation.** Training / validation are rebuilt from contiguous blocks of the training file (`tier_study.block_size` / `tier_study.buffer` in
  `configs/config.yaml`) because a random validation split shares neighbouring flows with its training rows. The runner does this for you
  (`pipelines/train_pipeline.block_validation_splits`). Do not report a random-validation number as "validation".
- **Shared rankings.** The mutual-information rankings of the primary pool 48 are committed (`results/rankings/feature_ranking_mutual_info_48f.csv` for the headline run and `feature_ranking_mutual_info_blockval_48f.csv` for the tier study, each with its `.meta.json` sidecar, which stops a committed ranking from being regenerated), so every model sees the same tiers. The rankings of the comparison pools 40 and 45 are not committed: the tier study regenerates them on its first run for that pool (`--pools base full_no_ttl`; `run_all_experiments.py` or `train_pipeline.py --write-ranking` for the plain pool-40 ranking), so a rerun may differ slightly from the committed comparison numbers. Any other study on pool 40 or 45 (headline seeds, FPR, open-set, narrative and similar) raises `FileNotFoundError` until that first run has happened.
  The runner only regenerates a ranking if the file is missing or the training data changed; if it rewrites a tracked ranking file, stop and ask.
- **Same seeds and explained rows.** `tier_study.seeds` (42-46), `tier_study.shap_rows` and `tier_study.bootstrap` must be the same for every model, otherwise the
  cross-model agreement is not a paired comparison. Leave them alone.

### Steps
1. Make your model available as a `model.type` (see "TL;DR" above: `src/models/your_model.py` + one branch in `src/models/model_factory.py`).
2. Declare its parameters (no tuning on test) in `configs/config.yaml`:
   ```yaml
   tier_study:
     model_params:
       your_model: {n_estimators: 200, max_depth: 8}     # whatever your model takes; random_state is set per seed by the runner
   ```
   The runner raises an error naming this key if it is missing.
3. Run the tier grid (3 pools x tiers x 5 seeds; each fit also gives the SHAP importance of that same model):
   ```bash
   python pipelines/run_tier_study.py --model your_model                       # writes results/metrics/your_model/
   python pipelines/run_tier_study.py --model your_model --out-dir results/_local_scratch   # local-only copy (gitignored)
   ```
4. Summaries (add `--in-dir results/_local_scratch` if you used `--out-dir`):
   ```bash
   python scripts/tier_summary.py --model your_model                           # tier table, shrinking-claim test
   python scripts/explanation_stability_tiers.py --model your_model            # tier agreement vs same-tier/different-seed floor
   python scripts/cross_model_agreement.py --models xgboost your_model         # agreement with XGBoost (needs XGBoost's committed SHAP files)
   ```
   Random-subset / worst-N baselines and the pooled-split column are XGBoost-only runs (`--parts baselines`, `--parts pooled`); they are optional for other models.
5. Commit only your own `results/metrics/<your_model>/` files and code; never edit another model's files.

### Things that differ by model family
- **SHAP explainer** is chosen from the fitted model: `TreeExplainer` for XGBoost / random forest / other tree ensembles, `LinearExplainer` for anything with `.coef_`
  (logistic regression), and the slow `KernelExplainer` fallback for MLPs / SVMs. For a Kernel-explained model, expect the SHAP part to dominate the runtime.
- **Logistic regression** gets the same scaled numeric matrix and label-encoded categorical columns as the trees, so `proto` / `service` / `state` enter as numbers,
  not one-hot. It can emit lbfgs convergence warnings at the declared `max_iter`; that is expected and not an error. Class weights (balanced ** 0.5) are passed as `sample_weight` for every model.
- **Random forest** uses `n_jobs: -1`. At the declared settings the SHAP step takes several times longer than the fit (it grows with trees x depth), so keep the declared size; for logistic regression the fit dominates and SHAP is negligible.
- Outputs of a model whose parameters you change are not comparable with the declared settings: say so in your write-up.
- Tests that exercise all of this on synthetic data: `python -m pytest tests/test_pipelines.py -k "tier or cross_model or explainer_type"`.

## Reference results and how to compare

What to compare with, all under `results/`:

| file | what it is |
|---|---|
| `PROTOCOL.md` | the one-page shared rules (official split primary, duplicate removal, block-grouped validation, seeds 42-46, tier grid, zero-shot, the pooled split labelled as optimistic) |
| `REFERENCE_XGBOOST.csv` | the XGBoost headline, tier and explanation-stability numbers (mean and std over 5 seeds; the `role` column marks pool 48 as `primary` and pools 40 and 45 as comparison); a cell reads `not computed` where the XGBoost tables have no such number and `not applicable` where the quantity does not exist |
| `TEMPLATE_model_results.csv` | blank, one row per (model, pool, tier, split, protocol), with the same columns: fill it and compare row by row |
| `rankings/feature_ranking_mutual_info_48f.csv`, `rankings/feature_ranking_mutual_info_blockval_48f.csv` (+ `.meta.json`) | the shared rankings of the primary pool 48 that define the tiers (rankings of pools 40 and 45 are regenerated on their first run into the same folder) |
| `metrics/xgboost/shap_importance_xgboost_<N>f.csv`, `shap_boot_xgboost_<N>f.npz` | the XGBoost SHAP files that step D needs |
| `rating/` | the blank A/B rating sheet, its key and its instructions |
| `01_...` to `06_...md` | XGBoost conclusions, tables and the declared protocols by research area (protocol and headline, open-set, explanations, feature tiers, cross-dataset, false-positive rate and adaptation); `NUMBERS_LEDGER.md` lists every quoted number with its source |

**Primary pool.** Pool 48 (the full official 42-column feature set plus 6 engineered features) is the primary pool: compare your model with the `primary` rows of `REFERENCE_XGBOOST.csv` first. Pools 40 and 45 are comparison pools (their XGBoost rows stay in the reference). Pool 48 needs the full official files; a download with fewer columns only supports pool 40. The XGBoost pool-48 results are slightly worse than pool 40 on FPR at the argmax decision (0.2933 against 0.2853) and ECE (0.1093 against 0.0876); its higher open-set detection depends on the window-count `ct_*` columns (a within-capture effect), and its lower FPR at 95% detection is shared between those and the TTL columns, so do not expect either on another network. Every pipeline and script that takes `--pools` now defaults to the primary pool 48 only (`full`), so a plain run generates no pool-40 or pool-45 files; the comparison pools are produced only when asked for with `--pools base` (40), `--pools full_no_ttl` (45) or both. `run_all_experiments.py` and `train_pipeline.py` pick the pool from the data (`feature_selection.pool: auto`): pool 48 whenever the full official files are present. The comparison tools `scripts/compare_pools.py` and `scripts/final_table.py` still read pools 40 and 48 on purpose and need the comparison runs first.

Steps (run from the repository root; `<type>` is your `model.type`):

| step | command | writes | what a new model needs |
|---|---|---|---|
| A. headline metrics, 5 seeds, official split and the pooled split (best case, optimistic) | set `model.type: <type>` (and its `model.params`) in `configs/config.yaml`, then `python pipelines/run_headline_seeds.py --pools full` (add `base` for the comparison pool 40) | `results/metrics/<type>/headline_*` | a branch in `src/models/model_factory.py` (`elif model_type == "<type>": ...`); the declared parameters in `model.params` |
| B. feature-tier study (primary pool 48: tiers 48 / 40 / 30 / 20 / 15; `--pools base full_no_ttl full` adds the comparison pools 40 and 45) | `python pipelines/run_tier_study.py --model <type>`, then `python scripts/tier_summary.py --model <type>` | `tier_study_<type>_<N>f_runs.csv`, `shap_importance_<type>_<N>f.csv`, `shap_boot_<type>_<N>f.npz`, `tier_summary_<type>*` | `tier_study.model_params.<type>` in `configs/config.yaml` (the runner stops with an error naming the key if it is missing), and the same `model_factory` branch |
| C. explanation stability across tiers | `python scripts/explanation_stability_tiers.py --model <type>` | `stability_<type>_<N>f.csv`, `stability_<type>.md` | step B finished |
| D. cross-model SHAP agreement, once two models have finished step B | `python scripts/cross_model_agreement.py --models xgboost <type>` | `results/metrics/cross_model/` | the XGBoost SHAP files above and your own from step B |
| E. optional: open-set and explanation checks (XGBoost only for now) | `python pipelines/run_open_set_study.py --step scores`, `python pipelines/run_xai_study.py --part faithfulness` | `results/metrics/xgboost/` | not implemented for other models yet |

Add `--out-dir results/_local_scratch` (step B) and `--in-dir results/_local_scratch` (steps B-D) to keep your runs local and untracked, as described above.

**Plots for your model.** The tier run (step B) also writes, for the primary pool 48 (and for the comparison pools 40 and 45 when you ask for them with `--pools`) and every tier of that pool, one confusion-matrix PNG and one ROC PNG of the seed-42 model, into `results/plots/<model.type>/`, named `confusion_matrix_<T>f.png` and `roc_curve_<T>f.png` for pool 48 (for example `confusion_matrix_30f.png` for the 30-feature tier); a comparison pool N adds its size, `confusion_matrix_pool40_30f.png`, because the same tier number in another pool is another feature set. The confusion matrix is grouped by the label scheme; the ROC figure draws one bold attack-versus-normal curve (score 1 - P(Normal)) and one thin one-vs-rest curve per class, and its title gives both AUCs. No extra training is needed: the plots come from the models the tier run trains anyway; `--no-plots` turns them off. To make only the plots (for example for a model whose tier run already finished), run `python pipelines/run_tier_study.py --model <type> --parts plots`: it reuses a model saved in `models_saved/<type>/` for that pool and tier and trains and saves the missing ones (about 15 seconds per tier for XGBoost). The generated plots are git-ignored (`.gitignore`), so they do not fill `results/`; only the two headline plots `confusion_matrix_48f.png` and `roc_curve_48f.png` of XGBoost (primary pool, full tier) are tracked.

**The repository is trimmed.** Per-seed, per-flow and per-trial result files were removed from `results/metrics/xgboost/` (they are in git tag `pre-cleanup-2026-10`). The summary scripts (`scripts/*_summary.py`, `tier_summary.py`, `final_table.py`, `leakage_table.py`, `accuracy_table.py`, `compare_pools.py`, `compare_tuned.py`, ...) read the outputs of their pipeline, so they will not run on the XGBoost side of the trimmed repository until that pipeline has been run first; for your own model they work as described because you run the pipeline yourself. Do not treat a missing XGBoost file as an error in your run: compare with `REFERENCE_XGBOOST.csv`.

## A concrete example

```python
# src/models/lightgbm_model.py
from src.models.sklearn_model import SklearnModel
import lightgbm as lgb

def lightgbm_classifier(params: dict) -> SklearnModel:
    return SklearnModel(lgb.LGBMClassifier(**params))
```

```python
# src/models/model_factory.py — add one branch
elif model_type == "lightgbm":
    from src.models.lightgbm_model import lightgbm_classifier
    return lightgbm_classifier(params)
```

```yaml
# configs/config.yaml
model:
  type: "lightgbm"
  params:
    n_estimators: 400
    max_depth: 8
    learning_rate: 0.08
    random_state: 42
```

Run `python pipelines/run_all_experiments.py`. LightGBM is tree-based, so
`SHAPExplainer` picks `TreeExplainer` automatically — same fast path as
XGBoost and Random Forest, no extra work.
