# XIDS Capstone — Project Plan (updated to match the repository)

> This revises the earlier plan so that its findings, numbers and open items match what the code and
> `results/` currently show. Numbers are XGBoost, 40 features, official UNSW-NB15 train/test split,
> duplicates removed, single seed unless stated. Reproduce with `python pipelines/run_all_experiments.py`.
> Items that cannot be derived from the repository (team progress, review dates) are left as they were and marked.

## Corrections since this plan was written (Tasks 1-3)

- The repository now runs on the 42-feature UNSW-NB15 files (40- and 48-feature pools); the "obtain the official files with all 42 features" open item is done. Numbers below that say 34 raw features / 0.742 / 0.685 are the earlier single-seed figures.
  Current official-split figures (XGBoost, 5 seeds): accuracy 0.743 / 0.740 and FPR 0.285 / 0.293 for 40 / 48 features.
- **Random splits leak through neighbouring flows** (the official files are in capture order; `ct_*` window counts and class labels are shared by consecutive rows). The pooled-split and random-validation figures in this document are
  best cases; block-grouped validation is used for any new selection.
- **Train-vs-test shift:** block-grouped AUC 0.81-0.84 (not 0.90-0.93). Its cause is undetermined; the TTL columns do not explain the Normal -> Fuzzers errors.
- **Few-shot result:** the 48-feature FPR of about 0.09 at 95% detection with ~5,000 labelled test rows is within-capture adaptation that relies on the window-count `ct_*` columns; zero-shot FPR stays 0.24-0.25.
- **Task 2.7 (XGBoost):** re-tuning on block-grouped validation, temperature scaling, EM class-prior correction, self-training and their combination do not lower the zero-shot FPR (all within 0.007 of the default at about 95% detection);
  with labels, 0.15 at exactly 95% detection takes about 2,500-5,000 labelled rows (48 and 45 features) and is never reached without the window-count `ct_*` columns; the earlier 0.09 was read at a test detection of 0.93
  (`results/metrics/xgboost/task_2_7_conclusion.md`).
- **Novelty 3 (Task 3, XGBoost):** no measurable cost down to 30 features; 20 / 15 features cost 0.006-0.014 macro F1 and about half the open-set detection; explanation stability stays near the retraining floor
  (`results/metrics/xgboost/task_3_conclusion.md`). Other model families are left to their owners (`pipelines/run_tier_study.py --model <type>`, `scripts/cross_model_agreement.py`).
- **Novelty 1 (Task 4, XGBoost, zero-shot):** under thresholds fixed on known block-grouped validation at 5% false-Unknown, max-softmax flags 0.22 (40 features) / 0.33 (48) of the Worms + Shellcode flows and a nine-class
  leave-one-class-out mean of 0.21-0.23 (AUROC 0.77; hardest: Worms, Exploits, Fuzzers). Entropy ranks better but is not reliably better at the threshold; margin, conformal, an isolation forest and combinations are no better.
  The 48-feature gain depends on window-count `ct_*` columns. 94-99% of zero-day flows are already called an attack, and the review queue barely lowers the alert FPR (0.289 -> 0.254) because the false alerts are confidently wrong
  (`results/metrics/xgboost/task_4_conclusion.md`).
- **Novelty 1, Task 4.5:** six ideas to improve it (calibration, per-class thresholds, ensemble disagreement, distance, pseudo-unknown training, a rank-average chosen on pseudo-unknown validation) leave the picture much the same: the best combination reaches rotation-mean detection
  0.27 / 0.34 (40 / 48 features) in a setting that removes two known classes, only 0.02-0.07 above entropy; in the full known set only calibrated entropy on 48 features clearly beats max-softmax (0.304 against 0.234); distance scores fail and the review queue does not lower the alert FPR.
- **Novelty 2 (Task 5, XGBoost):** the SHAP explanations are faithful (SHAP additivity error 1.4e-5; removing the top-5 SHAP features lowers the predicted-class probability 0.50-0.55 more than removing random ones on the whole pools, 0.33-0.34 at 15 features; unchanged on shifted test flows) and the
  narratives pass every mechanical check on 2,000 audited flows (label, confidence, cited features, cues in the right units, categories, action) and match the dashboard exactly; they are weaker as explanations (36-47% of cited features read "typical", cue direction agrees with the model's general behaviour in 72-76% of cases)
  and quote an uncalibrated confidence. The pipeline's own `check_explainability.py` standardised twice and was fixed. Human ratings are not collected (blank sheet `results/task_5_human_audit_sheet.csv`) (`results/metrics/xgboost/task_5_conclusion.md`).
  **Task 5.5:** a `class_relative` narrative style (config switch, classic is the default) removes the "typical" reasons (45% / 37% of cited numeric features, now 0), cites about 2.6 instead of 4.1 features, adds a calibrated confidence (ECE 0.093 -> 0.070, 0.115 -> 0.086) and keeps every correctness check at 1.000; the cue-direction agreement
  is unchanged (0.78 / 0.73). The explanations of false-positive Normal flows are faithful to the model (top-minus-random 0.35-0.51) but look like those of true attacks, so a narrative alone gives no reason to doubt a false alarm. No human study yet (blank A/B sheet `results/task_5_5_ab_sheet.csv`).
- **Novelty 4 (Task 6, XGBoost, leak-free on both datasets):** zero-shot transfer between UNSW-NB15 and CICIDS2017 fails in both directions on the 14 common features (AUROC 0.49 UNSW -> CIC, 0.58 CIC -> UNSW and degenerate; leak-free references 0.975 and 0.896 balanced accuracy); 11 of 14 features are near 0.5 in at least one
  dataset and 7 point opposite ways; the SHAP-selected "stable" set is not better than random subsets of its size; per-dataset standardisation helps ranking in one direction only (AUROC 0.79). Transfer takes labelled target flows: about 1,000 for CIC (FPR 0.10 at 95% detection), 1,000-5,000 for UNSW to match its own ceiling (FPR 0.21), and the
  source data does not help beyond about 100 labelled rows. Within-capture results (`results/metrics/xgboost/task_6_conclusion.md`).
- 0.912 / 0.921 is an empirical feature-space ceiling, not a Bayes ceiling.

## Overview

XIDS (Explainable AI-Based Network Intrusion Detection System) classifies network flows into normal and
attack categories and generates a plain-language, SHAP-based explanation for every prediction instead of a
black-box label.

The core problem: existing intrusion detection systems report strong accuracy but give analysts no
interpretable reasoning. XIDS closes that gap, and it also surfaces a real limitation of the data: some UNSW-NB15
attack categories are indistinguishable at the flow-feature level, which shaped the taxonomy. This revision is
equally candid about what did *not* work (zero-day detection, cross-dataset transfer, feature selection).

**Team:** Ashwani, Anjali, Anshu, Ashika, Samiksha Tiwari

## Objectives and Research Novelties

1. **Open-Set / Zero-Day Attack Detection** — confidence-based thresholding on the max softmax probability.
   *Outcome: works only weakly (about a quarter of zero-day flows detected at ~6% false alarms; 0.04-0.41 depending on the held-out class; no alternative score reliably better; see Task 4 above).*
2. **Human-Centered Actionable Explanations** — SHAP-driven plain-language narratives per prediction, checked
   against real data. *Outcome: implemented; two bugs found and fixed through real-data checks (below).*
3. **Feature-Selection + Explanation Consistency Study** — does shrinking the feature set change accuracy and the
   stability of the explanations? *Outcome: accuracy barely changes; explanations stay stable.*
4. **Cross-Dataset Transfer (UNSW-NB15 → CICIDS2017)** — originally "with stable features". *Outcome: negative —
   the models do not transfer, and no feature-selection strategy helps.*

## Datasets

- **UNSW-NB15** — primary dataset for closed-set classification, taxonomy analysis and feature-tier experiments.
  The copy in `data/raw` has 34 of the 42 official feature columns (both the train and test files lack `sttl, dttl,
  ct_state_ttl, ct_srv_src, ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm`). About **44% of its rows are exact
  duplicates** (257,673 → 145,222), which are now removed before splitting.
- **CICIDS2017** — used only for the cross-dataset study (stratified-subsampled to 200k rows).

## System Architecture

Preprocessing → Classification engine → (Explainability module + Open-set detection) → Dashboard
(FastAPI backend + React/Vite frontend). The repo is config-driven; the classification engine is swappable across
model types without touching other modules (`src/models/model_factory.py`). Evaluation uses one shared function
for the experiment grid and for re-evaluating saved models.

## Model Comparison Plan

| Model | Owner | Status in the repository |
|---|---|---|
| XGBoost | Ashwani | Done. Macro F1 **0.685** (accuracy 0.742) on the official test split; 0.760 / 0.836 on a pooled random split (an optimistic best case: it shares neighbouring flows with its training rows). The earlier "0.97 macro ROC-AUC" is not reproduced (ROC curves are plotted, AUC is not in the result CSVs). |
| Logistic Regression | Samiksha Tiwari | Supported via `model.type: logistic_regression`; no comparison results in the repo (the earlier 64% F1 is not reproduced here). |
| Random Forest | Anjali | Supported via `model.type: random_forest`; no results in the repo. |
| LightGBM | Anshu | Not implemented; worked example in `ONBOARDING.md`. |
| MLP | Ashika | Not implemented; `MLPClassifier` would work through `SklearnModel` but SHAP falls back to the slow KernelExplainer. |

## Key Findings

**Data hygiene changed the headline numbers.** Removing exact duplicates and using the official train/test split
lowers macro F1 from ~0.78 to **0.685**. The attack-vs-normal false-positive rate is **0.276** on the official
split vs. 0.112 on a pooled random split, which is optimistic because it shares neighbouring flows with its training rows (FPR at 90 / 95 / 99% detection: 0.167 / 0.264 / 0.374); most of the gap is
train/test shift plus dedup (dedup removes recurring easy rows and reshapes the class mix: Generic 18,871 → 1,257
test rows, DoS 4,089 → 1,504), not the model.

**Taxonomy.** Analysis, Backdoor and DoS cannot be reliably separated from the flow features: **72–80% of their rows
have an exact feature-vector twin in another class**. (The earlier justification — identical medians, extra features
absent — was incomplete: the official release does have the 8 missing columns, and restoring them does *not* remove the
overlap: twin share Analysis 72.0 → 72.0%, Backdoor 78.9 → 76.7%, DoS 79.7 → 79.5%.) They are merged into
`Overlap-Group-1`; recall into the group is 0.83 (Analysis), 0.94 (Backdoor), 0.50 (DoS). Exploits is the class
sharing the most vectors with the group (78% of the group's rows have an Exploits twin). Label schemes compared
(`current`, `none` 8-class, `wide` = merge + Exploits, `hierarchical`): `wide` has the best fine-grained recall (0.83)
but lumps 56% of attack rows into one class; `hierarchical` has the lowest false-positive rate (0.208) and the lowest
detection (0.925). Best-possible accuracy rises mechanically with coarser labels (0.905 / 0.912 / 0.969), so it measures
what a merge discards, not which merge is right. The choice of scheme is a team decision.

**Feature tiers.** Tier size (40 → 15) changes macro F1 by only about 0.015 (0.672–0.687). Against 10 random subsets per
tier, the mutual-information ranking is significantly better only at 30 features (0.687 vs 0.677 ± 0.004); at 20 it is
indistinguishable from random (0.6717 vs 0.6722) and at 15 it is within the spread (0.675 vs 0.659 ± 0.024). The worst-N
features are much worse (0.466 at 15), so which features matter is real, but the ranking does not reliably pick
better-than-random sets. Removing redundant (correlated) features from the ranking did not help.

**Explanation stability.** SHAP importance rank correlation across tiers is 0.83–0.99 (mean 0.92); retraining the same
feature set with a different seed gives 0.98–0.99, which is the noise floor.

**Explainability validation (real data).** Two bugs found and fixed: categorical features (proto, service, state)
produced nonsensical "extremely high" narratives from an undefined z-score; and the dashboard z-scored
already-standardised values a second time, making nearly every flow read "typical". Both now have regression tests.

**Cross-dataset transfer.** Trained on UNSW and tested on CIC the models are *below chance* (macro F1 0.38–0.43, balanced
accuracy 0.41–0.47); trained on CIC and tested on UNSW they predict almost no attacks (degenerate). Within-dataset
references are 0.90 (UNSW) and 0.97 (CIC). The two datasets are different populations (largest Kolmogorov–Smirnov
distances: `smean` 0.72, `sbytes` 0.69, `total_pkts` 0.64). The earlier claims — "stable" features underperform
UNSW→CIC but are strongest CIC→UNSW — came from unfixed experiments (separately scaled datasets, an unweighted
constant-prediction model) and are withdrawn: no strategy ranking is supportable.

**Open-set detection.** With the threshold chosen on known validation data (target 5% false "Unknown"; threshold ≈ 0.49)
the system detects about **25%** of the held-out zero-day classes (Worms, Shellcode) at **~6.4%** false "Unknown" on
known test traffic; AUROC 0.80 (0.75–0.80 across tiers). The earlier "67–75% detection at 26–28% false alarms" was the
0.65 threshold tuned against the reported zero-day samples; that point is still one point of the sweep (67% / 26%), but
it is not an honest operating point. Where the false alarms concentrate (previously Overlap-Group-1) was not re-checked.

## Validation and Rigor Methodology

- Duplicate removal before splitting; official train/test split; validation set used only to choose the open-set threshold
- Scaler fitted on the training dataset only (cross-dataset study)
- Random-feature-set and worst-N baselines (10 draws per tier) with a significance statement; same-set/different-seed noise floor
- Per-class precision/recall, attack-vs-normal view at several operating points, fine-grained recall under every label scheme
- Exact-twin and best-possible-accuracy analysis of class overlap (`scripts/overlap_analysis.py`)
- Real-data explainability spot checks (`scripts/check_explainability.py`) plus 140 automated tests

## Remaining Work / Open Items

- [ ] Run the model comparison (Logistic Regression, Random Forest) through `run_all_experiments.py`; implement LightGBM and MLP
- [ ] Multi-seed runs with error bars for the headline numbers (everything outside the random-subset draws is single-seed)
- [ ] Open-set: per-class or calibrated thresholds; check where false alarms concentrate; weak detection (~25%) is the main open problem
- [ ] Decide the label scheme (`current` vs `wide` vs `hierarchical`) using `results/metrics/xgboost/label_scheme_summary.md`
- [ ] Obtain the official UNSW-NB15 files with all 42 features and rerun (the pipeline switches to a 48-feature pool automatically); the official test file was not compared with the local one
- [ ] Cross-dataset: the negative result stands unless a shared-feature set that actually overlaps in distribution is found
- [ ] Dashboard: run end to end against the latest artifacts (implemented and API-tested, not re-run in the browser)
- [x] Migrate XGBoost artifacts to native serialization (`.json`); stale pickles removed
- [x] Deep-dive on the Overlap-Group-1 ↔ Exploits boundary (exact/near-twin analysis, `wide` scheme)

## Timeline / Phased Plan

*(Not derivable from the repository — carried over unchanged.)*
Review 1: data preprocessing, baseline XGBoost, taxonomy validation — Completed
Review 2: multi-model comparison, explainability validation, open-set threshold tuning — In progress
Review 3: dashboard integration, cross-dataset analysis, final evaluation + report — Planned

## Team Roles

| Member | Area |
| --- | --- |
| Ashwani | Core pipeline, XGBoost, taxonomy redesign, explainability, open-set detection |
| Anjali | Random Forest |
| Anshu | LightGBM |
| Ashika | MLP |
| Samiksha Tiwari | Logistic Regression |

## References

1. Moustafa, N., & Slay, J. (2015). UNSW-NB15: A comprehensive data set for network intrusion detection systems. *MilCIS*, IEEE.
2. Moustafa, N., & Slay, J. (2016). The evaluation of Network Anomaly Detection Systems. *Information Security Journal*, 25(1-3), 18-31.
3. Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization. *ICISSP*, 1, 108-116.
4. Lundberg, S. M., & Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. *NeurIPS*, 30.
5. Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *KDD*, 785-794.
6. Ke, G., et al. (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. *NeurIPS*, 30.
7. Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5-32.
8. [UNSW-NB15 class-overlap literature — verify exact citation before final submission]
