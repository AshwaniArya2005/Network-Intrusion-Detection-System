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

## Updates since the tables below were written (Tasks 1-4; read these first)

The tables further down were written for the 34-feature data and a single seed. What has since been established (details in `results/metrics/xgboost/`; every headline number of the bullets below is listed with its source file and column in `results/NUMBERS_LEDGER.md`; the conclusions, tables and declared protocols by research area are the numbered files `results/01_protocol_and_headline.md` to `results/06_fpr_and_adaptation.md`):

- **Data and pools.** The loader now uses the 42-feature UNSW-NB15 training/testing files (257,673 rows, 162,745 after exact deduplication) and two pools: 40 features (34 raw + 6 engineered)
  and 48 features (42 raw + 6 engineered). Official split, 5 seeds, XGBoost, scheme `current`: accuracy 0.743 / 0.740, FPR 0.285 / 0.293 (40 / 48 features).
- **Random splits are optimistic.** Consecutive rows of the official files are not shuffled: neighbouring flows share sliding-window `ct_*` values and often a class. A random validation split or the pooled
  random split therefore shares neighbours with its training rows. The pooled-split figures quoted below (and the random-validation FPR) are best cases. A validation set built from contiguous blocks
  predicts the test FPR to within 0.03-0.05 at the 95%-detection point; the random validation under-predicts it by 0.15-0.17 (`results/06_fpr_and_adaptation.md` (section `Source: task_2_6_conclusion.md`), `results/04_novelty3_feature_tiers.md` (section `Source: task_3_conclusion.md`)).
- **The train-vs-test shift is real but smaller than first reported.** A classifier separating train-Normal from official-test-Normal reaches AUC 0.81-0.84 with block-grouped cross-validation
  (0.90-0.93 with random cross-validation, which is inflated by neighbours). What the shift is made of is undetermined; removing the three TTL columns does not reduce the Normal -> Fuzzers errors.
- **Zero-shot FPR is about 0.24-0.25** at 95% detection for every method that uses no target labels (hierarchical scheme, tuning, importance weighting). The few-shot result (FPR about 0.09 at 48 features with
  ~5,000 labelled test rows) is **within-capture adaptation**: it holds with adaptation rows from other row-order blocks, but it relies on the window-count `ct_*` columns and was not tested on another capture.
- **Task 2.7 (XGBoost): the zero-shot FPR could not be lowered.** Re-tuning on block-grouped validation, temperature scaling, EM class-prior correction (transductive), self-training (transductive; it raises the
  FPR) and their declared combination all leave the FPR at about 0.25 for a 95%-detection operating point (every change within 0.007, below the declared 0.02). With labels, the FPR at *exactly* 95% detection reaches 0.15
  at about 2,500-5,000 labelled rows from the same capture (48 and 45 features; the "about 0.09" above is read at a test detection of 0.93, 0.12-0.13 at exactly 95%), the choice of which rows to label matters little,
  and it never reaches 0.15 without the window-count `ct_*` columns (`results/06_fpr_and_adaptation.md` (section `Source: task_2_7_conclusion.md`)).
- **Feature-set size (Task 3, XGBoost).** Down to 30 features, macro F1 is within 0.003 of the full pool and the SHAP explanations are as stable as retraining makes them; 20 / 15 features cost 0.006-0.014 macro F1 and
  about half of the open-set detection (`results/04_novelty3_feature_tiers.md` (section `Source: task_3_conclusion.md`)).
- **Open-set / zero-day detection (Task 4, XGBoost, zero-shot).** Thresholds come from known block-grouped validation at a 5% false-Unknown target; no zero-day flow is used for any choice
  (`results/02_novelty1_open_set.md` (section `Source: task_4_protocol.md`), `results/02_novelty1_open_set.md` (section `Source: task_4_conclusion.md`)). Max-softmax flags 0.22 (40 features) / 0.33 (48 features) of the Worms + Shellcode flows (AUROC 0.80 / 0.83); the
  nine-class leave-one-class-out mean is detection 0.21-0.23, AUROC 0.77, with Worms, Exploits and Fuzzers the hardest. Entropy ranks better (AUROC 0.86-0.88) and is the best score over the rotation at 40 features
  (0.81 / 0.27), but flags fewer Worms + Shellcode flows; margin, conformal, a Normal-trained isolation forest and their combinations are no better than max-softmax. The 40 -> 48-feature gain disappears
  without the window-count `ct_*` columns. 94-99% of zero-day flows are already flagged or called an attack, so flagging 22% instead of 4% of them adds only 1.6 points of catch (40 features), and the review queue barely lowers the alert FPR
  (0.289 -> 0.254 at 5%) because 88-92% of the false alerts on shifted Normal flows are confidently wrong. The earlier "67-75% detection at 26-28% false alarms" is withdrawn (threshold tuned on the zero-day flows).
- **Task 4.5 (zero-shot, tried to improve it).** Temperature scaling, per-class thresholds, ensemble disagreement, kNN / Mahalanobis distance, pseudo-unknown training and a rank-average were compared on the same nine-class rotation. The best result
  is a rank-average of ensemble mutual information and an Unknown-class probability: rotation-mean detection 0.27 / 0.34 (40 / 48 features) against 0.13 / 0.21 for max-softmax in the same, smaller setting (two known classes removed), only 0.02-0.07 above entropy, and it
  loses on Shellcode. In the full known set only temperature-scaled entropy on 48 features clearly beats max-softmax (0.304 against 0.234). Distance scores fail because Shellcode sits inside the training data, and the review queue still does not lower the alert FPR
  (`results/02_novelty1_open_set.md` (section `Source: task_4_conclusion.md`)).
- **Explanations and narratives (Task 5, XGBoost).** SHAP values reproduce the model's raw output to within 1.4e-5. Removing the top-5 SHAP features lowers the predicted-class probability 0.50-0.55 more than removing random ones on the whole pools (0.33-0.34 with 15 features),
  in every seed and class, and as much on shifted test flows as on validation flows. The dashboard narratives passed every mechanical check on 2,000 audited flows (label, confidence, cited features, cues in the right units, category names, action) and match the pipeline exactly. They
  are weaker as explanations: 36-47% of cited features read "typical" and the cue direction agrees with the model's general use of the feature in 72-76% of cases (36-49% for Overlap-Group-1); the confidence quoted is the uncalibrated probability. Human ratings were not collected (the blank 30-narrative rating template was removed from the repository; `python scripts/make_human_audit_sheet.py` rebuilds it from `results/metrics/xgboost/xai_audit_40f_narratives.csv`). `scripts/check_explainability.py` had the double-standardisation defect and is fixed (`results/03_novelty2_explanations.md` (section `Source: task_5_conclusion.md`)).
- **Task 5.5 (class-relative narrative, false-positive explanations).** `narrative.style: class_relative` (classic stays the default) drops features that read "typical" and places the others among all training flows and the predicted class's flows, with a calibrated confidence next to the raw one:
  on a fresh official-test sample the "typical" share falls from 45% / 37% to 0, cited features per narrative from 4.1 / 4.0 to 2.6 / 2.7, all checks stay at 1.000, the cue-direction agreement is unchanged (0.78 / 0.73) and ECE falls 0.093 -> 0.070 and 0.115 -> 0.086. The explanations of false-positive Normal flows are as faithful
  to the model as those of true attacks (top-minus-random 0.35-0.51), but they cite the same features as true Fuzzers and are no more atypical for the predicted class, so a narrative alone gives no reason to doubt a false alarm (only a weak confidence difference). Faithful to the model, not the truth; confidence still
  not calibrated on this split; no human study (blank A/B sheet `results/task_5_5_ab_sheet.csv`).
- **Task 6 (cross-dataset, UNSW-NB15 <-> CICIDS2017, leak-free).** Under block-disjoint splits with a 200-row gap on BOTH datasets (CIC streamed in file order, i.e. its day structure), zero-shot transfer still fails on the 14 common features: UNSW -> CIC AUROC 0.49 (69% of flows flagged), CIC -> UNSW AUROC 0.58
  and degenerate (0.3% flagged); the leak-free within-dataset references are 0.975 (CIC) and 0.896 (UNSW) balanced accuracy, so the earlier references were only slightly optimistic. 11 of the 14 features are near 0.5 in at least one dataset and 7 point opposite ways. The SHAP-selected "stable" set is not better than random
  subsets of its size (better in 2 of 5 seeds). Per-dataset standardisation (label-free) lifts UNSW -> CIC to AUROC 0.79 but not the operating point and does nothing for CIC -> UNSW. Few-shot: about 1,000 labelled CIC flows reach FPR 0.10 at 95% detection (target-only); UNSW never gets below FPR 0.22 on these features (its own
  ceiling is 0.21); the source data does not help beyond about 100 labelled rows. These are within-capture results (`results/05_novelty4_cross_dataset.md` (section `Source: task_6_conclusion.md`)); the older "Cross-dataset results" section below predates this protocol.
- The 0.912 / 0.921 best-possible accuracy is an empirical feature-space ceiling (rows sharing a feature vector can only get one label), not a Bayes ceiling.

## Key findings (current results, XGBoost, 40 features, official UNSW-NB15 split)

These are the numbers to quote; every row is reproducible with `python pipelines/run_all_experiments.py`
(details and caveats in the sections below).

| Topic | Result |
|---|---|
| Closed-set classification | macro F1 **0.685**, accuracy 0.742 on the deduplicated official test set (0.760 / 0.836 on a pooled random split, an optimistic best case that shares neighbouring flows with its training rows). About 44% of UNSW rows were exact duplicates (257,673 → 145,222) and are removed. |
| Attack vs. normal | detection rate 0.955, false-positive rate **0.276** (0.112 on the optimistic pooled split); FPR 0.167 / 0.264 / 0.374 at 90 / 95 / 99% detection. Most of the gap to the pooled split is train/test shift plus dedup, not the model. |
| Analysis / Backdoor / DoS | indistinguishable at flow level: 77–85% of their rows have an exact feature twin in another class on the tracked partition (pooled, duplicates kept: `results/01_protocol_and_headline.md` (section `Source: overlap/pooled_34f/summary.md`), `results/01_protocol_and_headline.md` (section `Source: overlap/pooled_42f/summary.md`); Analysis 77.0%, Backdoor 84.9%, DoS 77.4–77.8%); an earlier deduplicated 34-feature run gave 72–80% (output not committed). Merged into `Overlap-Group-1` (recall into the group 0.83 / 0.94 / 0.50, `results/01_protocol_and_headline.md` (section `Source: experiment_results.csv`), rendered table). Restoring the 8 columns missing from the local data does not resolve this. Exploits is the closest other class. |
| Open-set (zero-day) | validation-chosen threshold ≈ 0.49: **~25% zero-day detection at ~6.4% false "Unknown"**, AUROC 0.80 (0.75–0.80 across tiers). Weak. The old fixed 0.65 gives 67% / 26% but was tuned on the reported zero-day samples. |
| Feature-set size | tiers 40 → 15 change macro F1 by only ~0.015 (0.672–0.687). The mutual-information ranking beats random subsets significantly only at 30 features; at 20 and 15 it does not. Worst-N subsets are far worse (0.466 at 15). |
| Explanation stability | nested-tier SHAP rank correlation 0.83–0.99 (mean 0.92), vs. 0.98–0.99 for the same set retrained with other seeds. |
| Cross-dataset transfer | **does not transfer**: UNSW→CIC macro F1 0.38–0.43 (balanced accuracy 0.41–0.47, below chance); CIC→UNSW is degenerate (predicts almost no attacks). Within-dataset reference: 0.90 / 0.97. No feature-selection strategy, including "stable", is shown to help. |
| Label schemes | on scheme-independent metrics (40 features, official split): `wide` (merge + Exploits) has the best fine-grained recall (0.859, `results/01_protocol_and_headline.md` (section `Source: label_scheme_summary.md`)) but lumps 48% of attack rows into one class; `hierarchical` has the lowest false-positive rate (0.214) and the lowest detection (0.935) (5-seed result of the zero-shot method comparison, `results/01_protocol_and_headline.md` (section `Source: methods_zero_shot_b1_40f_summary.csv`), rendered table, method `hier_default`). The choice is the team's (`label_scheme_summary.md`; table in the Label schemes section). |

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
results/             the six numbered area files (01-06: conclusions, tables, protocols), PROTOCOL.md, REFERENCE_XGBOOST.csv, TEMPLATE_model_results.csv, NUMBERS_LEDGER.md, charts (plots/<model.type>/), the shared feature rankings, the XGBoost SHAP files and the rating sheets — committed; logs and results/diagnostics/ are gitignored
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

Per-class counts before/after dedup and per final split are in `split_summary.csv` (written by the pipeline; the committed copy is the rendered table `results/01_protocol_and_headline.md` (section `Source: split_summary.csv`)).
Dedup removes most Generic rows (train file 40,000 → 1,800; test 18,871 → 1,257) and most DoS
(test 4,089 → 1,504), so some classes have only ~1–2k training rows. Dedup removes the easiest,
most recurring rows and reshapes the class mix, so the deduplicated official test set is harder
than the raw one. `split_comparison.csv` (committed as the rendered table `results/01_protocol_and_headline.md` (section `Source: split_comparison.csv`)) is written on every run (when
`experiments.report_pooled_split` is on, the default) and puts the official split next to a pooled
random split (`use_official_split: false`) per feature tier, with the per-class train/test row counts
as columns. For 40 features:

| | official split | pooled random split (optimistic: shares neighbouring flows) |
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
class (77–85% on the tracked pooled partition, 72–80% in an earlier deduplicated 34-feature run), so no classifier on these columns can separate them
reliably. Medians alone would not show that; exact twins do. Restoring the 8 columns missing from
the `data/raw` copy (the official release has them) does **not** remove the overlap; it mainly helps
Fuzzers and Reconnaissance. Two sets of figures exist and they are different runs:

- **Tracked** (`results/01_protocol_and_headline.md` (section `Source: overlap/pooled_34f/summary.md`) and `results/01_protocol_and_headline.md` (section `Source: overlap/pooled_42f/summary.md`); pooled partition, duplicates kept, 255,988 known-class rows; share of a class's rows with an exact twin in another class, 34 → 42 features): Analysis 77.0 → 77.0%, Backdoor 84.9 → 84.9%, DoS 77.8 → 77.4%, Fuzzers 23.9 → 14.9%, Reconnaissance 33.8 → 16.1%, Overlap-Group-1 78.4 → 78.2%.
- **Earlier 34-feature result** (deduplicated data; the output was never committed and is not regenerated here): Analysis 72.0 → 72.0%, Backdoor 78.9 → 76.7%, DoS 79.7 → 79.5%, Fuzzers 21.1 → 11.4%, Reconnaissance 35.4 → 18.0%, and Exploits as the class sharing the most vectors with the merged group (78% of the group's rows have an exact twin in Exploits, 77% in Fuzzers, 72% in Reconnaissance, 33% in Generic, 0.1% in Normal). The split by partner class is not in any tracked file.

Coarser labels raise the
best-possible accuracy mechanically (8 classes 0.905, current merge 0.912, wide 0.969), so that number
measures what a merge discards, not which merge is right.

`python pipelines/run_label_scheme_comparison.py` trains the 40-feature model once per scheme and writes
`label_scheme_comparison.csv` (official split), `label_scheme_comparison_pooled.csv` and `label_scheme_summary.md` (committed: `results/01_protocol_and_headline.md` (section `Source: label_scheme_summary.md`))
under `results/metrics/<model.type>/`. Compare schemes on the scheme-independent columns:
attack-vs-normal detection / false-positive rate, `fine_recall_<class>` for all 8 original classes and their mean
`fine_recall_macro` (the share of each class's rows predicted as the label that contains it), and
`group_size_share` (attack rows inside a merged group). Macro F1 is kept only as
`macro_f1_not_comparable_across_schemes` (it averages over 6 / 8 / 5 / 8 classes). Official split, 40 features:

| scheme | fine-recall macro | false-positive rate | attack detection | group share |
|---|---|---|---|---|
| current | 0.786 | 0.286 | 0.961 | 0.119 |
| none (8 classes) | 0.633 | 0.290 | 0.962 | 0 |
| wide | 0.859 | 0.290 | 0.960 | 0.485 |
| hierarchical | 0.628 | 0.214 | 0.935 | 0 |

Sources: the `current`, `none` and `wide` rows are one run on the 42-feature data, 40-feature pool: `results/01_protocol_and_headline.md` (section `Source: label_scheme_summary.md`) (the 48-feature pool is `results/01_protocol_and_headline.md` (section `Source: label_scheme_summary_48f.md`)). The `hierarchical` row is the 5-seed result of the zero-shot method comparison, same pool and split: `results/01_protocol_and_headline.md` (section `Source: methods_zero_shot_b1_40f_summary.csv`) (rendered table), method `hier_default`, metrics `fine_recall_macro`, `false_positive_rate`, `detection_rate`, `group_size_share` (its stage-1-tuned variant: 0.628 / 0.212 / 0.933 / 0; the flat default in the same file, 0.786 / 0.285 / 0.959 / 0.119, reproduces the `current` row). The two sources differ in protocol (one run against the mean of 5 seeds), so differences of about 0.001-0.002 between them are not meaningful. The table that stood here before (0.756 / 0.276 / 0.955 / 0.12 for `current`, hierarchical FPR 0.208) came from an earlier 34-feature run that is not tracked and is replaced by the figures above.

The comparison reports; it does not choose a scheme. `python scripts/overlap_analysis.py [--partition
pooled|train|test] [--features all|base34]` reproduces the twin / near-twin / best-possible-accuracy numbers
into `results/metrics/overlap/<partition>_<n>f/` on demand (methods in `src/evaluation/overlap.py`). Only the `summary.md` of the pooled partition at 34 and 42 features is committed (inside `results/01_protocol_and_headline.md`, sections `Source: overlap/pooled_34f/summary.md` and `Source: overlap/pooled_42f/summary.md`); the per-class twin tables and `best_possible_accuracy.csv` were removed in the cleanup and the command regenerates them.

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
feature subsets and the worst-N features of the ranking (written to `feature_selection_baselines.csv`, one row per
draw with a `ranking` column = ranked/random/worst; only `feature_selection_baselines_summary.csv` is committed, as the rendered table `results/01_protocol_and_headline.md` (section `Source: feature_selection_baselines_summary.csv`): the
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
attacks on UNSW. `cross_dataset_feature_shift.csv` (rendered table `results/05_novelty4_cross_dataset.md` (section `Source: cross_dataset_feature_shift.csv`)) shows why: the flows are different populations
(Kolmogorov-Smirnov statistic up to 0.72 for `smean`, 0.69 for `sbytes`, 0.64 for `total_pkts`; median CIC flow
≈ 2 packets / 62 bytes vs. UNSW ≈ 10 / 1012). An earlier run reported "stable" as the worst UNSW→CIC strategy
(F1 0.43 vs 0.56 for all features) with separately scaled datasets; that result does not survive the fixes, and
neither does any strategy ranking.

## Reported metrics

`experiment_results.csv` (committed as the rendered table `results/01_protocol_and_headline.md`, section `Source: experiment_results.csv`) has, per model: macro accuracy/precision/recall/F1 on the active label
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
`open_set_sweep_40.csv` (committed as the rendered table `results/01_protocol_and_headline.md` (section `Source: open_set_sweep_40.csv`)) lists detection / false-alarm rates at every threshold (only the active tier gets one
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

328 tests: preprocessing, models (incl. the two-stage hierarchical model), XAI (batched SHAP, hierarchical
class mapping, faithfulness, narrative audit, class-relative narratives), the pipelines (small synthetic end-to-end run for
every label scheme and for the leakage, few-shot, open-set, FPR, faithfulness, narrative and cross-dataset runners and their
summary scripts), the cross-dataset study (degenerate detection, feature shift, the CIC loader), feature selection, the
overlap analysis (hand-computed cases) and the `/predict` endpoint (FastAPI `TestClient`, incl. missing-column and
oversize cases).

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
