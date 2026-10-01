# XAI Network IDS

A modular, config-driven, explainable-AI Network Intrusion Detection System built
around four research novelties:

1. **Open-Set / Zero-Day Attack Detection** — a confidence-threshold wrapper
   (`src/models/open_set_wrapper.py`) flags traffic the model isn't confident about
   as `"Unknown"` instead of forcing it into a known attack category. Measured on the
   held-out Worms/Shellcode classes it detects only about a quarter of them at a ~6%
   false-alarm rate (see [Open-set](#open-set--zero-day-simulation)): a prototype, not a solved problem.
2. **Human-Centered Actionable Explanations** — SHAP values are turned into plain-English
   narratives with a suggested remediation action (`src/xai/narrative_generator.py`).
3. **Feature-Selection + Explanation Consistency Study** — measures how stable SHAP
   explanations stay as the feature set shrinks from 40 → 30 → 20 → 15 features, against
   random-subset and same-set/different-seed references (`src/xai/explanation_stability.py`).
4. **Cross-Dataset Transfer Limits** — trains on UNSW-NB15, tests on CICIDS2017 (and vice
   versa) on the 14 shared features, with within-dataset reference rows and a per-feature
   distribution-shift table (`src/evaluation/cross_dataset.py`). It is a *negative* result: the
   models do not transfer, and no feature-selection strategy is shown to help.

The reference model is **XGBoost**, but every pipeline is written against an
abstract `BaseModel` interface — see [Swapping the model](#swapping-the-model) below.

## Key findings (current results, XGBoost, 40 features, official UNSW-NB15 split)

These are the numbers to quote; every row is reproducible with `python pipelines/run_all_experiments.py`
(details and caveats in the sections below).

| Topic | Result |
|---|---|
| Closed-set classification | macro F1 **0.685**, accuracy 0.742 on the deduplicated official test set (0.760 / 0.836 on a pooled random split). About 44% of UNSW rows were exact duplicates (257,673 → 145,222) and are removed. |
| Attack vs. normal | detection rate 0.955, false-positive rate **0.276** (0.112 pooled); FPR 0.167 / 0.264 / 0.374 at 90 / 95 / 99% detection. Most of the gap to the pooled split is train/test shift plus dedup, not the model. |
| Analysis / Backdoor / DoS | indistinguishable at flow level: 72–80% of their rows have an exact feature twin in another class. Merged into `Overlap-Group-1` (recall into the group 0.83 / 0.94 / 0.50). Restoring the 8 columns missing from the local data does not resolve this. Exploits is the closest other class. |
| Open-set (zero-day) | validation-chosen threshold ≈ 0.49: **~25% zero-day detection at ~6.4% false "Unknown"**, AUROC 0.80 (0.75–0.80 across tiers). Weak. The old fixed 0.65 gives 67% / 26% but was tuned on the reported zero-day samples. |
| Feature-set size | tiers 40 → 15 change macro F1 by only ~0.015 (0.672–0.687). The mutual-information ranking beats random subsets significantly only at 30 features; at 20 and 15 it does not. Worst-N subsets are far worse (0.466 at 15). |
| Explanation stability | nested-tier SHAP rank correlation 0.83–0.99 (mean 0.92), vs. 0.98–0.99 for the same set retrained with other seeds. |
| Cross-dataset transfer | **does not transfer**: UNSW→CIC macro F1 0.38–0.43 (balanced accuracy 0.41–0.47, below chance); CIC→UNSW is degenerate (predicts almost no attacks). Within-dataset reference: 0.90 / 0.97. No feature-selection strategy, including "stable", is shown to help. |
| Label schemes | on scheme-independent metrics: `wide` (merge + Exploits) has the best fine-grained recall (0.83) but lumps 56% of attack rows into one class; `hierarchical` has the lowest false-positive rate (0.208) and lowest detection (0.925). The choice is the team's (`label_scheme_summary.md`). |

**Status and limits.** XGBoost is the only model with full results; Random Forest and Logistic Regression
are supported (`model.type`) but no comparison has been run, and LightGBM / MLP are not implemented (see
ONBOARDING.md). Results are single-seed except where a random-draw spread is stated. The dashboard
is implemented (FastAPI + React) and covered by API tests; it was not re-run end to end after the latest changes.

## Project layout

```
configs/            All hyperparameters, paths, and feature-set definitions (YAML)
data/                Raw/processed data + standalone load/preprocess CLI scripts
src/                 Core library: data loading, preprocessing, models, XAI, evaluation
pipelines/           Training / evaluation / full-experiment-suite entrypoints
dashboard/           FastAPI backend + React/Vite frontend
notebooks/           Exploratory analysis, feature importance, explanation stability
scripts/             Dataset download helper (+ column check), setup script, overlap_analysis.py
tests/               pytest suite: preprocessing, models, XAI, pipelines, cross-dataset, overlap, dashboard API
models_saved/        Trained model artifacts (.json for XGBoost, .pkl otherwise), grouped by model.type — gitignored, generated by pipelines
results/             CSV metrics (metrics/<model.type>/), charts (plots/<model.type>/) and feature_ranking_mutual_info.csv — committed; logs and results/diagnostics/ are gitignored
```

## Installation

Requires Python 3.10+ and Node.js 18+ (for the dashboard UI only).

```bash
bash scripts/setup.sh
```

This creates a virtualenv, installs `requirements.txt`, generates small synthetic
demo datasets (see [Datasets](#datasets)), and installs the frontend's npm packages.

Or manually:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_datasets.py
cd dashboard/frontend && npm install
```

## Datasets

UNSW-NB15 and CICIDS2017 require a manual download from their official portals
(no public direct-download API exists) — `python scripts/download_datasets.py`
prints the links and the exact file paths to place them at
(`data/raw/unsw_nb15_train.csv`, `data/raw/unsw_nb15_test.csv`,
`data/raw/cicids2017_combined.csv`).

The official UNSW-NB15 training/testing set has 42 feature columns. The files this project was developed
on (`data/raw`, both train and test) lack 8 of them (`sttl, dttl, ct_state_ttl, ct_srv_src, ct_dst_ltm,
ct_src_ltm, ct_srv_dst, ct_dst_src_ltm`); `python scripts/download_datasets.py` reports which are missing,
and the loader switches to a 48-feature pool automatically when all 8 are present (see
[Feature sets](#feature-sets)). The local copy's train file matches the official training set row for row
on the shared columns (checked against a third-party mirror); the official test file was not compared.

**Until those files exist, every pipeline in this repo falls back to a small
synthetic, dataset-shaped stand-in** (see `src/data_loader.py`), so the whole
system — training, explanations, dashboard — is runnable immediately for
development/demo purposes. Replace the files with the real datasets before
reporting research results.

## Quick start

```bash
# 1. Train one model using the settings in configs/config.yaml
python pipelines/train_pipeline.py

# 2. Or run the full research suite in one command (about 15-20 minutes on the real data):
#    8 models (4 feature sets x closed/open-set), random/worst feature-set baselines,
#    explanation stability, cross-dataset study, official-vs-pooled split comparison
python pipelines/run_all_experiments.py

# Optional extras
python pipelines/run_label_scheme_comparison.py    # current / none / wide / hierarchical side by side
python scripts/overlap_analysis.py                 # exact/near-twin and best-possible-accuracy analysis
python pipelines/evaluate_pipeline.py              # re-evaluate the saved dashboard model

# 3. Launch the dashboard
uvicorn dashboard.backend.main:app --reload --port 8000   # terminal 1
cd dashboard/frontend && npm run dev                       # terminal 2
# open http://localhost:5173
```

Results land in `results/metrics/<model.type>/*.csv` and `results/plots/<model.type>/*.png`,
trained artifacts in `models_saved/<model.type>/` (`.json` for XGBoost, `.pkl` for the sklearn models).

## Swapping the model

See **[ONBOARDING.md](ONBOARDING.md)** — a full audit of what's actually
swappable (model interface, SHAP explainability, open-set logic, config-driven
selection), which files to touch (3) vs. leave alone, and a worked example
adding LightGBM. Short version: create `src/models/your_model.py` implementing
`BaseModel`, register it in `src/models/model_factory.py`, set `model.type` in
`configs/config.yaml`, run `python pipelines/run_all_experiments.py`.

## Data split

UNSW-NB15 exact duplicate rows are dropped before splitting (the count is logged;
rows present in both official files stay in train). With `data.use_official_split: true`
(default) the model trains on `unsw_nb15_train.csv` and is tested on `unsw_nb15_test.csv`;
set it to `false` to pool both files and split randomly (`data.test_size`). Either way the
zero-day classes (`data.unknown_attack_categories`) are held out of train, validation and
test, and `data.val_size` of the training rows becomes a validation set used only to choose
the open-set threshold. Synthetic fallback data always splits randomly.

Per-class counts before/after dedup and per final split are in `split_summary.csv`.
Dedup removes most Generic rows (train file 40,000 → 1,800; test 18,871 → 1,257) and most DoS
(test 4,089 → 1,504), so some classes have only ~1–2k training rows. Dedup removes the easiest,
most recurring rows and reshapes the class mix, so the deduplicated official test set is harder
than the raw one. `split_comparison.csv` is written on every run (when
`experiments.report_pooled_split` is on, the default) and puts the official split next to a pooled
random split (`use_official_split: false`) per feature tier, with the per-class train/test row counts
as columns. For 40 features:

| | official split | pooled random split |
|---|---|---|
| accuracy / macro F1 | 0.742 / 0.685 | 0.836 / 0.760 |
| attack detection rate / false-positive rate | 0.955 / 0.276 | 0.931 / 0.112 |
| Normal recall | 0.724 | 0.889 |
| Fuzzers precision | 0.308 | 0.598 |
| false-positive rate at 90 / 95 / 99% detection | 0.167 / 0.264 / 0.374 | 0.080 / 0.134 / 0.225 |

Most of the gap is the official train/test shift plus dedup, not the model. The attack-vs-normal
view is reported at two operating points: the argmax decision (`false_positive_rate`) and the false-positive
rate needed to reach 90 / 95 / 99% detection from the score 1 − P(Normal) (`fpr_at_90_detection`, ...).
The default stays the official split.

## Label schemes

`data.label_scheme` picks an entry of `data.label_schemes` (all defined in `configs/config.yaml`,
none hard-coded): `current` (default: Analysis/Backdoor/DoS merged into `Overlap-Group-1`), `none`
(8 classes), `wide` (the current merge plus Exploits → `Overlap-Group-2`) and `hierarchical`
(stage 1 attack vs. normal, stage 2 attack family; `src/models/hierarchical_model.py`). A hierarchical
model is built by `create_scheme_model`, saved as a directory (stage artifacts + `meta.json` with
`normal_index`, `attack_classes`, `n_classes`), loaded by the dashboard, and explained stage by stage by
`SHAPExplainer` (stage 1 for Normal, stage 2 for each attack class, with encoder indexes mapped to stage-2
indexes so they are never mixed). It uses the `sample_weight` it is given, else balanced weights per stage. Outputs of
any scheme other than `current` carry its name in their filenames (`experiment_results_wide.csv`,
`xgboost_40_closed_wide.json`, ...; aggregate plots go to `results/plots/<model.type>/<scheme>/`), so the
default's results are never overwritten. The confusion matrix blocks and title follow the scheme.

**Why Analysis/Backdoor/DoS are merged:** most of their rows have an exact feature twin in another
class (72–80% in the 34-feature data), so no classifier on these columns can separate them
reliably. Medians alone would not show that; exact twins do. Restoring the 8 columns missing from
the `data/raw` copy (the official release has them) does **not** remove the overlap (twin share
34 → 42 features: Analysis 72.0 → 72.0%, Backdoor 78.9 → 76.7%, DoS 79.7 → 79.5%); it mainly helps
Fuzzers (21.1 → 11.4%) and Reconnaissance (35.4 → 18.0%). Exploits shares feature vectors with the
merged group more than any other class (78% of the group's rows have an exact twin in Exploits, 77%
in Fuzzers, 72% in Reconnaissance, 33% in Generic, 0.1% in Normal). Coarser labels raise the
best-possible accuracy mechanically (8 classes 0.905, current merge 0.912, wide 0.969), so that number
measures what a merge discards, not which merge is right.

`python pipelines/run_label_scheme_comparison.py` trains the 40-feature model once per scheme and writes
`label_scheme_comparison.csv` (official split), `label_scheme_comparison_pooled.csv` and `label_scheme_summary.md`
under `results/metrics/<model.type>/`. Compare schemes on the scheme-independent columns:
attack-vs-normal detection / false-positive rate, `fine_recall_<class>` for all 8 original classes and their mean
`fine_recall_macro` (the share of each class's rows predicted as the label that contains it), and
`group_size_share` (attack rows inside a merged group). Macro F1 is kept only as
`macro_f1_not_comparable_across_schemes` (it averages over 6 / 8 / 5 / 8 classes). Official split:

| scheme | fine-recall macro | false-positive rate | attack detection | group share |
|---|---|---|---|---|
| current | 0.756 | 0.276 | 0.955 | 0.12 |
| none (8 classes) | 0.611 | 0.278 | 0.955 | 0 |
| wide | 0.832 | 0.284 | 0.957 | 0.56 |
| hierarchical | 0.609 | 0.208 | 0.925 | 0 |

The comparison reports; it does not choose a scheme. `python scripts/overlap_analysis.py [--partition
pooled|train|test] [--features all|base34]` reproduces the twin / near-twin / best-possible-accuracy numbers
into `results/metrics/overlap/<partition>_<n>f/` on demand (methods in `src/evaluation/overlap.py`; the output
folder is not kept in the repo).

## Feature sets

`configs/feature_sets.yaml` lists the 40-feature pool (the 34 raw UNSW-NB15 columns in this
repo's `data/raw` copy plus 6 engineered ones). The official UNSW-NB15 training/testing set has
42 raw columns; this copy lacks `sttl, dttl, ct_state_ttl, ct_srv_src, ct_dst_ltm, ct_src_ltm,
ct_srv_dst, ct_dst_src_ltm` (see `scripts/download_datasets.py` for the official files). When all 8
are present in the loaded data the 48-feature `feature_pool_full` is used automatically (tiers
`"48"`, `"40"`, … from `experiments.feature_sets_full`), and the pool name is logged and stored in
results and in each saved preprocessor. The tier name equals
`n_features` (`"40"`, `"30"`, `"20"`, `"15"`); the 30/20/15 sets are the top-N of a ranking
chosen by `feature_selection.ranking_source`:

- `mutual_info` (default): mutual information with the target on the training split, with
  proto/service/state estimated as discrete. Written by `run_all_experiments.py` (or
  `python pipelines/train_pipeline.py --write-ranking`) to `results/feature_ranking_mutual_info.csv`.
  A single-model `train_pipeline.py` run never rewrites it, and raises if the file is missing or
  doesn't match the pool. `feature_selection.redundancy_threshold` (e.g. 0.8, off by default)
  pushes features highly correlated with a better-ranked one down the ranking.
- `curated`: the original hand-written order (`feature_curated_rank`), for reproducing the
  curated-vs-worst / noise-floor comparisons. Each source has its own ranking file.

Every saved preprocessor carries `metadata` (feature set, feature list, ranking source).

`run_all_experiments.py` also trains, per tier, `experiments.random_baseline_draws` random
feature subsets and the worst-N features of the ranking (`feature_selection_baselines.csv`,
`ranking` column = ranked/random/worst; `feature_selection_baselines_summary.csv` has the
mean/std/min/max macro F1 of the random draws next to the ranked and worst tiers — a ranking
only counts if its tier beats that spread). The explanation-stability CSV has a `comparison`
column: `nested_feature_sets` rows compare the tiers, `same_set_different_seed` rows compare a
tier with itself retrained under other seeds (`experiments.stability_seeds`) — the agreement
from retraining noise alone, the reference for reading the nested numbers.

**What the study shows (official split, macro F1):** tier size changes F1 by only about 0.01–0.02
(0.672–0.687 across 15–40 features). The mutual-information ranking is not reliably better than
random subsets: `feature_selection_baselines_summary.csv` reports the ranked tier's percentile, rank
and z-score among the 10 random draws plus whether it beats the random mean + 2 std. At 30 features the ranked set
is significantly better (0.687 vs 0.677 ± 0.004, z = 2.4); at 20 it is indistinguishable from random
(0.6717 vs 0.6722 ± 0.0052, z = −0.1); at 15 it is within the random spread (0.675 vs 0.659 ± 0.024,
z = 0.7). The worst-N subsets are clearly worse (down to 0.466 at 15), so *which* features matter is real; the ranking just
does not pick better-than-random sets reliably. The ranked top sets contain many redundant byte
features; the redundancy-aware variant (`feature_selection.redundancy_threshold: 0.8`) did not improve F1
(0.684 / 0.679 / 0.678 / 0.666 for 40 / 30 / 20 / 15 vs 0.685 / 0.687 / 0.672 / 0.675 ranked). It was run once
and its files are not kept; `experiments.run_nonredundant: true` regenerates them as `*_nonredundant` files. proto/service/state are
estimated as discrete variables by the mutual-information ranking (tested).

## Cross-dataset results (read before quoting)

This study measures **how far a model trained on one dataset transfers to the other** on the 14
features they share. The result is negative: it does not transfer, and no feature-selection
strategy is shown to help (in particular, "stable" features are not better).

Setup: each direction fits one preprocessor on the training dataset only and applies it to the test
dataset; CIC `Flow Duration` is converted from microseconds to seconds; CIC is stratified-subsampled
(fixed seed) to `data.cic_max_rows`; models train with balanced weights. Strategies: `common_all` (14
features), `source_only` (top-10 SHAP on the training dataset), `stable` (top-k on both datasets; it looks at
the test dataset's importances, so it is not strict zero-shot). Each row reports `balanced_accuracy`,
`predicted_attack_share` and `degenerate` (under 1% or over 99% of test rows predicted as attack);
degenerate rows have their metrics written as NaN and are not plotted. `within_dataset` rows train and
test on the same dataset's own 70/30 split with the same 14 features, as the upper bound.

Latest run (macro F1 / balanced accuracy):

| | UNSW→CIC | CIC→UNSW |
|---|---|---|
| within-dataset reference | 0.90 / 0.90 (UNSW) | 0.97 / 0.98 (CIC) |
| common_all | 0.38 / 0.41 | degenerate (attack share 0.0%) |
| source_only | 0.42 / 0.46 | degenerate (0.02%) |
| stable | 0.43 / 0.47 | degenerate (0.1%) |

UNSW→CIC is *below chance* (balanced accuracy < 0.5), and the CIC-trained model predicts almost no
attacks on UNSW. `cross_dataset_feature_shift.csv` shows why: the flows are different populations
(Kolmogorov-Smirnov statistic up to 0.72 for `smean`, 0.69 for `sbytes`, 0.64 for `total_pkts`; median CIC flow
≈ 2 packets / 62 bytes vs. UNSW ≈ 10 / 1012). An earlier run reported "stable" as the worst UNSW→CIC strategy
(F1 0.43 vs 0.56 for all features) with separately scaled datasets; that result does not survive the fixes, and
neither does any strategy ranking.

## Reported metrics

`experiment_results.csv` has, per model: macro accuracy/precision/recall/F1 on the active label
scheme's target (by default Analysis/Backdoor/DoS are one `Overlap-Group-1` class); per-class
`precision_*`, `recall_*`, `f1_*`; the attack-vs-normal `detection_rate` and `false_positive_rate` and
the `fpr_at_90/95/99_detection` operating points; `recall_<Analysis|Backdoor|DoS>_as_Overlap-Group-1`;
`fine_recall_<class>` / `fine_recall_macro` for all 8 known classes under the active scheme (so a
merge cannot hide them) and `group_size_share`. `pipelines/evaluate_pipeline.py` uses the same
evaluation function, so a saved model gets the same numbers as its grid row.

## Open-set / zero-day simulation

`data.unknown_attack_categories` (default: `Worms`, `Shellcode`) are withheld entirely from
training, then scored at test time to see whether `OpenSetWrapper` flags them as
`"Unknown"` instead of misclassifying them. The confidence threshold is **not** tuned on
those samples: it is the max-softmax-confidence quantile that flags at most
`open_set.target_false_unknown_rate` of *known validation* flows as Unknown, then frozen.

**Operating point (40 features, official split):** threshold ≈ 0.49, i.e. a 5% target false-alarm
rate on validation, which gives ≈ 6.4% false "Unknown" on known test traffic, ≈ 25% zero-day
detection (15–26% across tiers) and AUROC ≈ 0.80 (0.75–0.80). Zero-day detection is weak at this
operating point; the AUROC says known and zero-day flows overlap heavily in confidence.
The threshold targets 5% false "Unknown" on validation data drawn from the training distribution
(`false_unknown_alarm_rate_val`, 5.0%), and the official test split shows 6.3–6.8% (`false_unknown_alarm_rate`): the
gap is the train→test shift, and a larger one would appear on truly new traffic.
`experiment_results.csv` reports `open_set_threshold`, `target_false_unknown_rate`,
`unknown_detection_rate`, `false_unknown_alarm_rate`, `unknown_auroc`;
`open_set_sweep_40.csv` lists detection / false-alarm rates at every threshold (only the active tier gets one
unless `experiments.save_per_tier_diagnostics: true`) and
`results/plots/<model.type>/open_set_sweep.png` plots them (dot: chosen threshold, square: the
old fixed 0.65). The 0.65 point stays in the sweep: on the current split it gives 67% detection
at 26% false alarms for 40 features, matching the earlier 66% / 26% figures — those numbers came
from choosing the threshold against the reported zero-day samples, which is why the
validation-selected point is the one to quote. The chosen threshold is saved next to the model
(`open_set_<set>.json`) and used by the dashboard; `open_set.confidence_threshold` is only a
fallback for models saved without one.

## Running tests

```bash
pytest tests/ -v
```

140 tests: preprocessing, models (incl. the two-stage hierarchical model), XAI (batched SHAP, hierarchical
class mapping), the pipelines (small synthetic end-to-end run for every label scheme), the cross-dataset
study (degenerate detection, feature shift), feature selection, the overlap analysis (hand-computed cases)
and the `/predict` endpoint (FastAPI `TestClient`, incl. missing-column and oversize cases).

## Configuration highlights

Defaults live in `configs/config.yaml`; the switches most worth knowing:

| key | default | effect |
|---|---|---|
| `data.use_official_split` | `true` | official train/test files vs. a pooled random split |
| `data.label_scheme` | `current` | `current` / `none` / `wide` / `hierarchical` (non-default outputs carry the scheme in filenames) |
| `feature_selection.ranking_source` | `mutual_info` | or `curated` (original hand-written order) |
| `feature_selection.redundancy_threshold` | `null` | e.g. `0.8` pushes correlated features down the ranking |
| `open_set.target_false_unknown_rate` | `0.05` | the threshold is chosen on known validation data to meet this |
| `experiments.random_baseline_draws` | `10` | random feature subsets per tier |
| `experiments.report_pooled_split` | `true` | also run the pooled-split comparison |
| `experiments.run_nonredundant` | `false` | also run the grid with the redundancy-aware ranking |
| `experiments.save_per_tier_diagnostics` | `false` | per-tier sweep / overlap-diagnostic CSVs for every tier, not just the active one |
| `dashboard.max_rows` | `500` | `/predict` rejects larger uploads |

## Dashboard API

- `POST /predict` — multipart file upload (`file`, a `.csv` of flow records, ≤10MB and
  ≤ `dashboard.max_rows` rows; a CSV missing required columns gets a 400 naming them) →
  `{n_rows, predictions: [{flow_id, prediction, confidence, is_unknown, narrative, shap_top_features}]}`
- `GET /health` — liveness check

The dashboard loads whichever model `configs/config.yaml`'s `dashboard.*` keys
point at (defaults to the closed-set, "40"-tier XGBoost model produced by
`run_all_experiments.py`), with the open-set threshold saved next to it (`open_set_<set>.json`).
It works with every label scheme, including `hierarchical`. SHAP is computed in one batch per request
and the narrative uses the already-standardised feature values as z-scores. The frontend's "Analyst View" shows the narrative;
"Technical View" shows the raw SHAP contributions as bars.

## Notes for contributors

- Everything is config-driven — avoid hardcoding paths or hyperparameters in
  code; add a key to `configs/config.yaml` instead.
- All modules use `src/utils/logger.get_logger(__name__)` for structured
  logging — no bare `print()`.
- Type hints are used throughout; keep new code consistent with that.
