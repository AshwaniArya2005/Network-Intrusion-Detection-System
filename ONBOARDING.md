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
another model's). The feature ranking (`results/feature_ranking_mutual_info.csv`) is model-independent mutual
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
