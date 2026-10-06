# False-positive rate, few-shot labels, leakage checks and what did not help

Why the official-split false-positive rate stays high, what lowers it (labels), the neighbour-leakage checks of the few-shot result and of the earlier validation and shift numbers, and every method that did not help: conclusions, tables and the declared protocols.

File names mentioned inside this file (for example `task_6_tables.md`, `results/task_5_protocol.md` or `xai_audit_40f_example_failures.csv`) are the `Source:` sections of this file or of one of the other numbered files, or files that were removed in the cleanup and are recoverable from the git tags `pre-cleanup-2026-10` and `pre-lean-2026-10`. Text under a `Source:` heading is the original file, unchanged except that its headings are demoted two levels. Two kinds of file moved after the originals were written: the feature rankings are now in `results/rankings/` and the A/B rating sheet, key and instructions in `results/rating/`.

## Source: task_2_5_conclusion.md

> **Update after Task 2.6 (`task_2_6_conclusion.md`).** The few-shot result below (48 features, FPR 0.094 at ~95% detection with 5,000 labelled rows) was checked
> for neighbour leakage and holds (0.085-0.096 with no near twins and with adaptation rows from other row-order blocks), but it relies on the window-count `ct_*`
> columns and is within-capture adaptation, not transfer to a new deployment; on 40 features the small gain is partly neighbour-dependent. The "pooled-split reference
> of 0.109" is not a like-for-like comparison (that model trains on 68% of the test file). The validation-vs-test gap and the train-vs-test shift AUC quoted from earlier
> tasks are partly neighbour artefacts: block-built validation gives FPR 0.19-0.25 instead of 0.10-0.12, and block-grouped cross-validation gives shift AUC 0.81-0.84
> instead of 0.90-0.93.

### Task 2.5 conclusion: the official-split shift and the Normal false-positive rate

Numbers: `task_2_5_final_table_40f_48f.md` (all methods, access levels, 5 seeds/runs), `shift_conclusion_40f_45f_48f.md`
(Step A). Protocol and selection rules were declared before any result (`results/task_2_5_protocol.md`).
Target hypothesis (a guess): official-split FPR <= 0.15 at about 95% detection, from 0.24-0.25.

#### Result against the target
| Access | Method | 40 features: FPR at ~95% detection | 48 features: FPR at ~95% detection |
|---|---|---|---|
| zero-shot | flat default (validation-chosen threshold) | 0.250 (det 0.947) | 0.244 (det 0.953) |
| zero-shot | hierarchical, stage 1 tuned | 0.243 (0.946) | 0.247 (0.965) |
| zero-shot | flat, hyperparameters tuned on validation | FPR at 95% detection 0.253-0.255 | 0.219 |
| transductive | domain weights (declared choice) | 0.247 (0.947) | 0.241 (0.941) |
| few-shot | k=5000, retrain on half, threshold on the other half (f=0.5) | 0.232 (0.951) | **0.094 +/- 0.016 (0.952)** |
| few-shot | k=1000, same | 0.267 +/- 0.038 (0.954) | 0.158 +/- 0.037 (0.947) |

- The target is met **only on the 48-feature pool and only with labelled test-distribution rows** (about 5,000, i.e. 9% of the
  test file; 1,000 rows is borderline and noisy). On 40 features no method gets below 0.23 at 95% detection (best argmax FPR
  0.182 at k=5000, f=0.5, with detection 0.936).
- No zero-shot or transductive method reaches it. The hierarchical scheme lowers the argmax FPR (0.285 -> 0.214 on 40 features)
  mostly by lowering detection; at equal detection the gain is small, and open-set detection collapses (0.26 -> 0.03 on 40
  features, 0.38 -> 0.04 on 48).
- Retraining with the labelled rows improves the ranking on 48 features (threshold-free FPR at 95% detection 0.238 -> 0.063
  at k=5000, f=0.5), but the validation-chosen threshold over-detects (0.989) and keeps the FPR at 0.217: the operating point
  must be chosen on labelled test-distribution rows that the model was not trained on (the split variant).
- Re-choosing the threshold alone (model unchanged) cannot help: the ROC curve is the same.

#### Side effects (reported favourable or not)
- Calibration: ECE falls with adaptation (48 features 0.109 -> 0.071 at k=5000 split; 40 features 0.088 -> 0.060).
- Open-set detection: unchanged on 48 features with few-shot (0.377 -> 0.375), higher on 40 (0.259 -> 0.277-0.299); it collapses
  with the hierarchical scheme.
- Accuracy rises with few-shot retraining (48 features 0.740 -> 0.796 at k=5000 split, 0.818 without a held-out threshold half).
- The combined few-shot + domain-weights variant adds nothing over few-shot alone.

#### One paragraph
The official test Normal traffic differs from the training Normal traffic (a classifier tells them apart at AUC 0.90-0.93 against
controls at 0.50), and the difference is spread over several feature groups at once - volume/size, timing and, when present,
connection counts - so removing any single group, or the TTL columns, does not lower the Normal -> Fuzzers errors; what causes
the shift remains undetermined. No method that only uses the training data (zero-shot) or the unlabelled test features
(transductive) lowered the false-positive rate at 95% detection below 0.24 on either pool. With labelled rows from the test
distribution (few-shot, about 5,000 flows and a held-out half for the threshold) the 48-feature model reached FPR 0.094 at 95%
detection, below the pooled-split reference of 0.109, while the 40-feature model did not (0.232), which is consistent with
(but does not prove) the 8 extra official columns carrying the information needed to separate those Normal flows from Fuzzers once
labelled examples are available. Caveats: the adaptation rows and the evaluation rows come from the same official test file, so
this measures adaptation within that file's distribution, not transfer to a new deployment; and what the shift is made of is
still unexplained.

## Source: task_2_6_conclusion.md

### Task 2.6 conclusion: is the 48-feature few-shot result adaptation or neighbour leakage?

Tables: `task_2_6_table_40f_48f_45f_41f_38f.md` (all rows), `leakage_*_summary.csv`, `leakage_*_validation_blocks*.csv`, `leakage_*_shift_auc.csv`,
`pooled_reference_composition.csv`. Protocol and decision rule were declared before any result (`results/task_2_6_protocol.md`).
Primary metric: FPR at about 95% detection with the threshold chosen on held-out labelled adaptation rows (`retrain_split_f0.5`), 5 runs.

#### What was found in the data
The official files are not shuffled: consecutive rows (in id order) correlate strongly on the `ct_*` window counts (lag-1 correlation 0.67-0.76
in the test file, about 0 when shuffled) and share a class 71% of the time (28% when shuffled). Neighbouring flows therefore do share window
values and labels, so the leakage concern was well founded.

#### Verdict under the declared decision rule
| 48 features, k = 5,000 | FPR at ~95% detection | detection |
|---|---|---|
| zero-shot (same rows) | 0.244 | 0.953 |
| original result (random adaptation rows) | 0.094 +/- 0.016 | 0.952 |
| rows with NO near twin (<= 0.1) in the adaptation set (check 1) | 0.096 +/- 0.016 | 0.949 |
| adaptation rows from OTHER row-order blocks, 200-row gaps (check 2) | **0.085 +/- 0.016** | 0.932 |
| adaptation rows from the evaluation blocks themselves (check 2) | 0.085 +/- 0.033 | 0.945 |

The worse of checks 1 and 2 is about 0.096, below the declared 0.15 threshold: **the 48-feature few-shot result is robust to neighbourhood
leakage.** At k = 1,000 the corresponding values are 0.159 (no near twin) and 0.153 (other blocks), at the edge of 0.15, as the original 0.158 was.

#### Caveats on that verdict
- In the neighbourhood-disjoint condition the detection at the held-out threshold is 0.932, not 0.95, so the FPR at exactly 95% detection would be
  somewhat higher than 0.085 (not measured; the declared metric is as reported). The block conditions are noisy (std 0.03-0.05; blocks are internally homogeneous).
- Near twins are rare on 48 features (4.5% of evaluation rows have one within 0.1 in the 5,000 adaptation rows, 36% on 40 features), so check 1
  has little power on this pool; check 2 is the decisive one. Evaluation rows do have more twins among the adaptation rows than among an equal-size random
  subset of training rows (exact 1.34% vs 0.11%, within 0.1 4.5% vs 1.9%), i.e. a measurable but small neighbour effect.
- Block-disjoint adaptation still draws on the same capture: the same hosts and campaigns recur across blocks. The result measures adaptation within
  one capture; transfer to another capture was not tested.

#### What it relies on (check 3)
| k = 5,000, retrain_split_f0.5 | features | FPR at ~95% detection |
|---|---|---|
| 48-feature pool | 48 | 0.094 +/- 0.016 |
| minus sttl, dttl, ct_state_ttl | 45 | 0.111 +/- 0.019 |
| minus the 7 window-count ct_* columns (ct_src_dport_ltm, ct_dst_sport_ltm, ct_srv_src, ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm) | 41 | 0.231 +/- 0.011 |
| minus every ct_* column (those 7 + ct_state_ttl, ct_flw_http_mthd, ct_ftp_cmd) | 38 | 0.228 +/- 0.013 |
| 40-feature pool | 40 | 0.232 |
The gain depends on the window-count `ct_*` columns, not on the TTL columns. Without them the 48-feature pool behaves like the 40-feature one.

#### The 40-feature pool
Its small gain is partly neighbour-dependent: adaptation rows drawn inside the evaluation blocks give 0.203, rows from other blocks 0.243, zero-shot 0.251.
(Near-twin share is high there, 36% within 0.1, and the subset rows with a twin have much lower FPR for the zero-shot model as well.)

#### Pooled reference (check 4)
The pooled random split trains on 109,559 rows, 37,013 of them from the official test file (67.8% of it), interleaved with the rows it is tested on; the
5,000-row few-shot run uses 9.2% of the test file. The comparison 0.094 vs 0.109 is not like for like, and the pooled number is itself neighbour-inflated.

#### Consequences for earlier claims
- **Validation vs test FPR (Task 2a).** The random 15% validation shares neighbours with the training rows. A validation built from contiguous blocks gives a
  mean FPR of 0.25 / 0.24 (1,000-row blocks; 40 / 48 features) and 0.19 / 0.19 (200-row blocks) against 0.12 / 0.10 for the random validation, so the
  validation-vs-test gap shrinks from 0.17 / 0.19 to 0.04 / 0.06 (1,000-row blocks) or 0.10 / 0.11 (200-row blocks). The block estimates are very noisy
  (0.03-0.60 across draws), so the size of the neighbour effect is not pinned down, but the "cost of the split shift of 0.15-0.20" overstated the
  distribution shift: part of it is neighbour leakage in the random validation split (and in the pooled split).
- **Train-vs-test Normal AUC (Task 2.5 Step A).** With random cross-validation 0.899 / 0.929 / 0.930 (40 / 45 / 48 features); with CV grouped by contiguous
  blocks 0.814 / 0.836 / 0.837 (seed 42). The shift is real (control 0.50) but about 0.09 of the earlier AUC was neighbour leakage. The per-group AUC changes of
  Step A's ablation used random CV and were not re-run; the Normal -> Fuzzers results on the official test split are unaffected.

#### The claim, restated
With about 5,000 labelled flows from the same capture (9% of the test file) and a held-out labelled half to set the threshold, the 48-feature model
reaches FPR about 0.09 at about 95% detection on flows from other time blocks of that capture (zero-shot 0.24). This is within-capture adaptation: it
relies on the window-count `ct_*` columns, is borderline at 1,000 labelled flows, is not shown for the 40-feature pool, and was not tested on a different
capture. Beating the pooled-split reference does not show more than that, because the pooled model trains on 68% of the test file.

#### One paragraph
The 0.094 is robust to the leakage this task tested for: it stays at 0.085-0.096 when evaluation rows have no near twin in the adaptation set and when
adaptation rows come from other blocks of the file with a gap. It relies on the window-count connection columns (removing them returns FPR to 0.23) and on
adapting inside one capture, whose hosts and campaigns recur across blocks; it does not show transfer to a new deployment. The same investigation showed
that two earlier numbers were partly neighbour artefacts - the random validation FPR (0.10-0.12 against 0.19-0.25 for block-built validation) and the
train-vs-test shift AUC (0.90-0.93 against 0.81-0.84 with block-grouped cross-validation) - so the distribution shift is real but smaller than first reported.

## Source: task_2_7_conclusion.md

### Task 2.7 conclusion: can the zero-shot official-split false-positive rate be lowered? XGBoost

Official split, scheme `current`, flat model, seeds 42-46 (mean +/- std). Every selection used block-grouped validation (1,000-row blocks, 200-row gaps) or, for few-shot, the labelled sample. Protocol and the
rule for "clearly beats the baseline" were declared before any result (`results/task_2_7_protocol.md`). Primary metric: official-test FPR at about 95% detection with the threshold chosen on validation (`det95 FPR`).
Tables: `task_2_7_tables.md` (one section per original table: `fpr_study_tuned_40f_45f_48f.md`, `fpr_study_prior_40f_45f_48f.md`, `fpr_study_self_40f_45f_48f.md`, `fpr_study_fewshot_48f_45f_41f.md`, `fpr_study_final_40f_45f_48f.md`; the per-seed rows behind them are in git tag `pre-cleanup-2026-10`).

#### Result against the hypothesis
Hypothesis (a guess): zero-shot methods reach about 0.20-0.22, and 0.15 or below needs labels. **Zero-shot: not reached.** No zero-shot or transductive method lowered the det95 FPR by the declared 0.02 (the best mean paired
difference is -0.007); every pool stays at 0.244-0.259 against defaults of 0.256 / 0.248 / 0.248 (40 / 45 / 48 features). **Labels: confirmed, but at a larger budget than the earlier headline suggested**
(below). Nothing here changes the earlier statement that zero-shot FPR is about 0.24-0.25.

#### Step 1 (ZERO-SHOT): re-tuning on block-grouped validation (40 trials per pool, regularised space)
| det95 FPR | 40 features | 45 features | 48 features |
|---|---|---|---|
| default | 0.256 +/- 0.010 | 0.248 +/- 0.012 | 0.248 +/- 0.011 |
| earlier tuned (random validation, attack AUC) | 0.252 +/- 0.014 | not run | 0.249 +/- 0.011 |
| tuned on block-grouped validation, attack AUC | 0.257 +/- 0.014 | 0.258 +/- 0.012 | 0.254 +/- 0.014 |
| tuned on block-grouped validation, macro F1 | 0.253 +/- 0.014 | 0.255 +/- 0.012 | 0.253 +/- 0.011 |
Caption. Stronger regularisation and selection on block-grouped validation do not lower the FPR: the mean paired differences are -0.004 to +0.010 and no variant is better in more than 4 of 5 seeds. The search itself found almost nothing to
improve on validation (best attack AUC 0.9630 against 0.9624 for the default at 40 features). The tuned models do change other things: accuracy rises by 0.01-0.02 at 40 and 48 features, ECE falls (0.093 -> 0.051 at 40,
0.115 -> 0.074 at 48), and max-softmax open-set detection rises on the 45 and 48-feature pools (0.34-0.35 -> 0.49-0.55), which is relevant to Task 4.5 but is not an FPR gain.

#### Step 2 (TRANSDUCTIVE): temperature scaling and EM class-prior correction
| det95 FPR | 40 features | 45 features | 48 features |
|---|---|---|---|
| default | 0.256 | 0.248 | 0.248 |
| temperature scaling (zero-shot) | 0.259 | 0.251 | 0.249 |
| + validation class prior (zero-shot control) | 0.256 | 0.249 | 0.248 |
| + EM prior correction (transductive) | 0.249 | 0.244 | 0.244 |
Caption. Temperature scaling lowers ECE (0.093 -> 0.070 at 40 features) and nothing else. EM prior correction lowers the argmax FPR (0.289 -> 0.196 at 40 features, 0.298 -> 0.230 at 48) but not the FPR at a fixed 95%
detection (-0.004 to -0.007, better in 5, 4 and 5 of 5 seeds, below the declared 0.02), costs macro F1 (0.712 -> 0.680) and removes most of the open-set detection (0.24 -> 0.04 at 40 features). Diagnostic only (the true shares were never used):
EM estimates the test class shares better than the model's own prior (L1 distance 0.23-0.25 against 0.60) but in the wrong direction for the classes that matter: it puts Fuzzers at 0.18 (true 0.088) and Normal at 0.52 (true 0.62), i.e. it reads the
Normal flows that look like Fuzzers as a change in class frequency. That points to a shift in the Normal flows themselves, which a class-prior correction cannot fix.

#### Step 3 (TRANSDUCTIVE, risky): self-training (two rounds, confidence 0.90, weight fraction 0.2)
| evaluation blocks (test) | 40 features | 45 features | 48 features |
|---|---|---|---|
| argmax FPR, zero-shot round 0 | 0.314 | 0.324 | 0.323 |
| argmax FPR, round 2 | 0.324 | 0.331 | 0.329 |
| lower in how many seeds | 0 of 5 | 0 of 5 | 0 of 5 |
| attack pseudo-labels that are really Normal, round 0 -> 1 | 0.089 -> 0.107 | 0.144 -> 0.176 | 0.140 -> 0.172 |
Caption. Self-training does not help and the confidently wrong Normal flows do reinforce the error: the share of attack pseudo-labels that are truly Normal and the share of Normal flows that receive an attack pseudo-label (0.041 -> 0.057 at 45 features)
both grow from round 0 to round 1. The det95 FPR is unchanged (0.271 -> 0.274 at 45 features). The validation check made before looking at the test blocks passes at 45 and 48 features and fails at 40, so it could not
catch this: validation rows come from the training distribution and carry no shift, which is the shift self-training would have to correct.

#### Step 4 (FEW-SHOT): label budget and selection strategy (5 runs; rows from other time blocks, 200-row gaps)
Zero-shot baseline on the same rows: det95 FPR 0.255 (48 features), 0.255 (45), 0.260 (41); FPR at exactly 95% detection 0.251, 0.269, 0.249.
| FPR at exactly 95% detection (threshold-free) | k=500 | k=1,000 | k=2,500 | k=5,000 |
|---|---|---|---|---|
| 48 features, random | 0.199 | 0.185 | 0.152 | 0.122 |
| 48 features, diverse (k-means) | 0.216 | 0.200 | **0.148** | 0.130 |
| 48 features, entropy / mix | 0.201 / 0.193 | 0.191 / 0.182 | 0.167 / 0.152 | 0.113 / 0.132 |
| 45 features, random / diverse | 0.215 / 0.251 | 0.198 / 0.198 | 0.164 / 0.160 | 0.138 / 0.141 |
| 41 features, random / diverse | 0.255 / 0.253 | 0.254 / 0.252 | 0.260 / 0.250 | 0.242 / 0.245 |
Caption. At exactly 95% detection the smallest budget that gets the FPR to 0.15 or below is **about 2,500 labelled rows (diverse, 48 features; random reaches 0.152) and 5,000 rows on the other strategies and on 45 features**; no strategy gets there on the
41-feature pool, which has no window-count `ct_*` column, so the dependence on those columns holds for every strategy and budget. The strategy matters little at equal detection (differences of 0.01-0.03 with a spread of about 0.04). The headline columns
`det95 FPR` (threshold chosen on the held-out labelled half) look better for diverse selection (0.126 at k=500, 0.099 at k=2,500 on 48 features) because its held-out half is not representative of the test flows and the chosen threshold lands at a test
detection of 0.89-0.93, not 0.95; compared at the same detection that advantage mostly disappears. Entropy-selected rows are 70-90% attacks at small k, which makes the held-out half a poor guide for the threshold (held-out-half FPR 0.88 at k=100 against a
test FPR near 0.2). The earlier "about 0.09 with 5,000 rows" (Tasks 2.5 / 2.6) is the det95 FPR at a test detection of 0.93; at exactly 95% detection the same budget gives 0.12-0.13.

#### Step 5: the declared combination and the final table
Declared rule (chosen on each seed's validation rows only): the block-validation-tuned configuration if its validation attack AUC is at least the default's (used in 2 of 5 seeds on every pool), temperature scaling, and the EM correction only when its
validation gate passes (4 of 5 seeds on every pool, which makes those runs transductive).
| combination vs default | 40 features | 45 features | 48 features |
|---|---|---|---|
| det95 FPR | 0.254 +/- 0.015 vs 0.256 | 0.249 +/- 0.013 vs 0.248 | 0.247 +/- 0.013 vs 0.248 |
| argmax FPR | 0.226 vs 0.289 | 0.254 vs 0.299 | 0.254 vs 0.298 |
| macro F1 | 0.698 vs 0.712 | 0.698 vs 0.706 | 0.706 vs 0.712 |
Caption. Combining the pieces does not lower the FPR at a fixed detection; it only moves the argmax decision (lower argmax FPR, lower macro F1, much lower open-set detection when EM is used). The full table of every method with accuracy, macro F1, the three FPRs,
detection, ECE and open-set detection is `fpr_study_final_40f_45f_48f.md`.

#### What did not work
Re-tuning on block-grouped validation, stronger regularisation, temperature scaling, class-prior correction (with or without test features), self-training, and their combination: none lowers the zero-shot det95 FPR (all within 0.007 of the default, below the
declared 0.02). Selecting the few-shot rows by uncertainty or diversity helps little at equal detection.

#### One paragraph
The false-positive rate on the shifted official test split could not be lowered without labels: re-tuning, calibration, class-prior correction and self-training all leave the FPR at about 0.25 for a 95%-detection operating point, and the class-prior
diagnostic suggests the shift sits in the Normal flows themselves, not in how common each class is. Labelled rows from the same capture do lower it, but a budget of about 2,500-5,000 rows (5-9% of the test file) is needed to reach 0.15 at exactly 95% detection (the earlier
0.09 was read at 93% detection), the choice of which rows to label matters little, and nothing works on the pool without the window-count `ct_*` columns. These are within-capture results on one dataset; transfer to another capture was not tested.

## Source: task_2_5_final_table_40f_48f.md

### Task 2.5 final table (official split; mean +/- std over 5 seeds or runs)

Access: zero-shot = training data only; transductive = also the unlabelled test features; few-shot = also k labelled test rows (excluded from evaluation). `det95` columns are the validation-chosen 95%-detection operating point (thr_adapt: chosen on the k rows). Macro F1 is not comparable between hierarchical (8 classes) and flat (6 classes) models.

#### 40f

| method | access | k | accuracy | f1 | false_positive_rate | detection_rate | det95_test_fpr | det95_test_detection | fpr_at_95_detection | ece | unknown_detection_rate | unknown_auroc | normal_to_Fuzzers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| flat_default | zero-shot | 0 | 0.7427 +/- 0.0009 | 0.7125 +/- 0.0012 | 0.2853 +/- 0.0013 | 0.9594 +/- 0.0007 | 0.2496 +/- 0.0025 | 0.9465 +/- 0.0017 | 0.2588 +/- 0.0019 | 0.0876 +/- 0.0009 | 0.2585 +/- 0.0140 | 0.7992 +/- 0.0039 | 0.2355 +/- 0.0014 |
| hier_default | zero-shot | 0 | 0.7624 +/- 0.0014 | 0.5687 +/- 0.0012 | 0.2137 +/- 0.0021 | 0.9351 +/- 0.0005 | 0.2440 +/- 0.0092 | 0.9465 +/- 0.0039 | 0.2521 +/- 0.0026 | 0.0539 +/- 0.0012 | 0.0271 +/- 0.0082 | 0.7891 +/- 0.0016 | 0.1790 +/- 0.0019 |
| hier_stage1_tuned | zero-shot | 0 | 0.7628 +/- 0.0009 | 0.5687 +/- 0.0009 | 0.2124 +/- 0.0021 | 0.9332 +/- 0.0008 | 0.2434 +/- 0.0059 | 0.9458 +/- 0.0024 | 0.2538 +/- 0.0026 | 0.0488 +/- 0.0010 | 0.0261 +/- 0.0079 | 0.7843 +/- 0.0013 | 0.1783 +/- 0.0022 |
| flat_tuned_f1 | zero-shot | 0 | 0.7514 +/- 0.0019 | 0.7141 +/- 0.0012 | 0.2659 +/- 0.0029 | 0.9533 +/- 0.0004 | n/a | n/a | 0.2554 +/- 0.0026 | 0.0644 +/- 0.0013 | 0.2590 +/- 0.0159 | 0.7965 +/- 0.0047 | 0.2207 +/- 0.0021 |
| flat_tuned_auc | zero-shot | 0 | 0.7647 +/- 0.0010 | 0.7192 +/- 0.0008 | 0.2395 +/- 0.0016 | 0.9452 +/- 0.0016 | n/a | n/a | 0.2532 +/- 0.0022 | 0.0521 +/- 0.0010 | 0.2589 +/- 0.0170 | 0.7991 +/- 0.0056 | 0.2007 +/- 0.0010 |
| retrain_f0.3 | few-shot | 1000 | 0.7580 +/- 0.0010 | 0.7150 +/- 0.0009 | 0.2529 +/- 0.0014 | 0.9520 +/- 0.0014 | 0.2496 +/- 0.0052 | 0.9518 +/- 0.0017 | 0.2447 +/- 0.0038 | 0.0775 +/- 0.0020 | 0.2727 +/- 0.0168 | 0.8081 +/- 0.0049 | 0.2108 +/- 0.0028 |
| retrain_f0.5 | few-shot | 1000 | 0.7616 +/- 0.0016 | 0.7149 +/- 0.0012 | 0.2450 +/- 0.0033 | 0.9494 +/- 0.0018 | 0.2563 +/- 0.0091 | 0.9552 +/- 0.0022 | 0.2421 +/- 0.0036 | 0.0782 +/- 0.0025 | 0.2751 +/- 0.0155 | 0.8125 +/- 0.0078 | 0.2035 +/- 0.0015 |
| thr_adapt | few-shot | 1000 | 0.7425 +/- 0.0009 | 0.7125 +/- 0.0012 | 0.2855 +/- 0.0012 | 0.9592 +/- 0.0007 | 0.2407 +/- 0.0207 | 0.9426 +/- 0.0091 | 0.2592 +/- 0.0021 | 0.0878 +/- 0.0010 | 0.2585 +/- 0.0140 | 0.7992 +/- 0.0039 | 0.2358 +/- 0.0011 |
| retrain_f0.3 | few-shot | 5000 | 0.7846 +/- 0.0009 | 0.7277 +/- 0.0009 | 0.2062 +/- 0.0026 | 0.9469 +/- 0.0020 | 0.2329 +/- 0.0024 | 0.9577 +/- 0.0020 | 0.2127 +/- 0.0033 | 0.0489 +/- 0.0013 | 0.3496 +/- 0.0300 | 0.8307 +/- 0.0053 | 0.1793 +/- 0.0018 |
| retrain_f0.5 | few-shot | 5000 | 0.7951 +/- 0.0016 | 0.7286 +/- 0.0015 | 0.1816 +/- 0.0015 | 0.9359 +/- 0.0018 | 0.2414 +/- 0.0038 | 0.9617 +/- 0.0021 | 0.2085 +/- 0.0053 | 0.0452 +/- 0.0016 | 0.3309 +/- 0.0309 | 0.8358 +/- 0.0063 | 0.1579 +/- 0.0022 |
| thr_adapt | few-shot | 5000 | 0.7424 +/- 0.0010 | 0.7122 +/- 0.0012 | 0.2855 +/- 0.0015 | 0.9595 +/- 0.0007 | 0.2608 +/- 0.0149 | 0.9509 +/- 0.0053 | 0.2588 +/- 0.0016 | 0.0877 +/- 0.0011 | 0.2585 +/- 0.0140 | 0.7992 +/- 0.0039 | 0.2358 +/- 0.0019 |
| retrain_f0.3_domain5 | few-shot+transductive | 5000 | 0.7757 +/- 0.0006 | 0.7235 +/- 0.0012 | 0.2223 +/- 0.0021 | 0.9501 +/- 0.0018 | 0.2359 +/- 0.0048 | 0.9562 +/- 0.0027 | 0.2179 +/- 0.0035 | 0.0578 +/- 0.0010 | 0.3535 +/- 0.0358 | 0.8324 +/- 0.0071 | 0.1923 +/- 0.0019 |
| retrain_f0.5_domain5 | few-shot+transductive | 5000 | 0.7855 +/- 0.0020 | 0.7234 +/- 0.0022 | 0.2000 +/- 0.0016 | 0.9425 +/- 0.0021 | 0.2392 +/- 0.0052 | 0.9596 +/- 0.0020 | 0.2135 +/- 0.0056 | 0.0522 +/- 0.0020 | 0.3324 +/- 0.0323 | 0.8349 +/- 0.0055 | 0.1729 +/- 0.0027 |
| retrain_split_f0.3 | few-shot | 1000 | 0.7506 +/- 0.0012 | 0.7121 +/- 0.0015 | 0.2671 +/- 0.0014 | 0.9545 +/- 0.0015 | 0.2637 +/- 0.0476 | 0.9524 +/- 0.0185 | 0.2526 +/- 0.0034 | 0.0838 +/- 0.0010 | 0.2574 +/- 0.0046 | 0.8019 +/- 0.0034 | 0.2207 +/- 0.0027 |
| retrain_split_f0.5 | few-shot | 1000 | 0.7515 +/- 0.0013 | 0.7113 +/- 0.0018 | 0.2638 +/- 0.0014 | 0.9528 +/- 0.0017 | 0.2666 +/- 0.0378 | 0.9541 +/- 0.0143 | 0.2530 +/- 0.0040 | 0.0858 +/- 0.0013 | 0.2536 +/- 0.0192 | 0.8032 +/- 0.0039 | 0.2173 +/- 0.0033 |
| retrain_split_f0.3 | few-shot | 5000 | 0.7726 +/- 0.0025 | 0.7214 +/- 0.0022 | 0.2264 +/- 0.0040 | 0.9474 +/- 0.0025 | 0.2362 +/- 0.0150 | 0.9522 +/- 0.0054 | 0.2305 +/- 0.0041 | 0.0622 +/- 0.0014 | 0.2991 +/- 0.0113 | 0.8191 +/- 0.0032 | 0.1929 +/- 0.0039 |
| retrain_split_f0.5 | few-shot | 5000 | 0.7801 +/- 0.0021 | 0.7223 +/- 0.0020 | 0.2093 +/- 0.0030 | 0.9409 +/- 0.0024 | 0.2318 +/- 0.0108 | 0.9513 +/- 0.0032 | 0.2276 +/- 0.0040 | 0.0600 +/- 0.0019 | 0.2768 +/- 0.0222 | 0.8202 +/- 0.0025 | 0.1783 +/- 0.0029 |
| domain_weights_clip5 (declared choice: best validation macro F1) | transductive | 0 | 0.7493 +/- 0.0013 | 0.7158 +/- 0.0009 | 0.2723 +/- 0.0018 | 0.9563 +/- 0.0012 | 0.2469 +/- 0.0038 | 0.9472 +/- 0.0012 | 0.2534 +/- 0.0023 | 0.0857 +/- 0.0011 | 0.2677 +/- 0.0167 | 0.8055 +/- 0.0048 | 0.2280 +/- 0.0018 |
| domain_weights_clip20 | transductive | 0 | 0.7489 +/- 0.0011 | 0.7154 +/- 0.0009 | 0.2730 +/- 0.0018 | 0.9561 +/- 0.0007 | 0.2465 +/- 0.0063 | 0.9468 +/- 0.0026 | 0.2547 +/- 0.0024 | 0.0858 +/- 0.0012 | 0.2670 +/- 0.0150 | 0.8042 +/- 0.0017 | 0.2281 +/- 0.0013 |
| drop_top5_shifted | transductive | 0 | 0.7390 +/- 0.0009 | 0.7088 +/- 0.0006 | 0.2883 +/- 0.0017 | 0.9593 +/- 0.0009 | 0.2535 +/- 0.0041 | 0.9472 +/- 0.0021 | 0.2605 +/- 0.0016 | 0.0880 +/- 0.0013 | 0.2472 +/- 0.0111 | 0.7964 +/- 0.0039 | 0.2375 +/- 0.0018 |
| drop_top10_shifted | transductive | 0 | 0.7345 +/- 0.0008 | 0.7026 +/- 0.0006 | 0.2909 +/- 0.0016 | 0.9549 +/- 0.0008 | 0.2567 +/- 0.0039 | 0.9438 +/- 0.0024 | 0.2709 +/- 0.0016 | 0.0882 +/- 0.0010 | 0.3053 +/- 0.0256 | 0.8177 +/- 0.0036 | 0.2362 +/- 0.0011 |

#### 48f

| method | access | k | accuracy | f1 | false_positive_rate | detection_rate | det95_test_fpr | det95_test_detection | fpr_at_95_detection | ece | unknown_detection_rate | unknown_auroc | normal_to_Fuzzers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| flat_default | zero-shot | 0 | 0.7401 +/- 0.0020 | 0.7130 +/- 0.0016 | 0.2933 +/- 0.0024 | 0.9681 +/- 0.0025 | 0.2442 +/- 0.0068 | 0.9526 +/- 0.0015 | 0.2375 +/- 0.0076 | 0.1093 +/- 0.0024 | 0.3770 +/- 0.0104 | 0.8358 +/- 0.0032 | 0.2475 +/- 0.0021 |
| hier_default | zero-shot | 0 | 0.7569 +/- 0.0012 | 0.5711 +/- 0.0013 | 0.2396 +/- 0.0010 | 0.9628 +/- 0.0018 | 0.2447 +/- 0.0079 | 0.9651 +/- 0.0046 | 0.2034 +/- 0.0058 | 0.0815 +/- 0.0014 | 0.0445 +/- 0.0153 | 0.8157 +/- 0.0031 | 0.2021 +/- 0.0015 |
| hier_stage1_tuned | zero-shot | 0 | 0.7543 +/- 0.0003 | 0.5700 +/- 0.0012 | 0.2438 +/- 0.0007 | 0.9637 +/- 0.0030 | 0.2466 +/- 0.0040 | 0.9653 +/- 0.0032 | 0.2061 +/- 0.0075 | 0.0843 +/- 0.0006 | 0.0431 +/- 0.0130 | 0.8142 +/- 0.0030 | 0.2052 +/- 0.0002 |
| flat_tuned_f1 | zero-shot | 0 | 0.7591 +/- 0.0012 | 0.7209 +/- 0.0013 | 0.2591 +/- 0.0019 | 0.9618 +/- 0.0010 | n/a | n/a | 0.2188 +/- 0.0056 | 0.0778 +/- 0.0017 | 0.4117 +/- 0.0093 | 0.8368 +/- 0.0044 | 0.2193 +/- 0.0014 |
| flat_tuned_auc | zero-shot | 0 | 0.7591 +/- 0.0012 | 0.7209 +/- 0.0013 | 0.2591 +/- 0.0019 | 0.9618 +/- 0.0010 | n/a | n/a | 0.2188 +/- 0.0056 | 0.0778 +/- 0.0017 | 0.4117 +/- 0.0093 | 0.8368 +/- 0.0044 | 0.2193 +/- 0.0014 |
| retrain_f0.3 | few-shot | 1000 | 0.7691 +/- 0.0021 | 0.7303 +/- 0.0046 | 0.2578 +/- 0.0024 | 0.9822 +/- 0.0016 | 0.2350 +/- 0.0080 | 0.9789 +/- 0.0023 | 0.1402 +/- 0.0070 | 0.0925 +/- 0.0034 | 0.3864 +/- 0.0191 | 0.8476 +/- 0.0040 | 0.2206 +/- 0.0020 |
| retrain_f0.5 | few-shot | 1000 | 0.7719 +/- 0.0019 | 0.7308 +/- 0.0047 | 0.2527 +/- 0.0027 | 0.9823 +/- 0.0012 | 0.2362 +/- 0.0066 | 0.9800 +/- 0.0025 | 0.1331 +/- 0.0068 | 0.0938 +/- 0.0031 | 0.3905 +/- 0.0125 | 0.8506 +/- 0.0058 | 0.2157 +/- 0.0021 |
| thr_adapt | few-shot | 1000 | 0.7400 +/- 0.0021 | 0.7130 +/- 0.0017 | 0.2934 +/- 0.0027 | 0.9681 +/- 0.0026 | 0.2246 +/- 0.0289 | 0.9441 +/- 0.0111 | 0.2378 +/- 0.0076 | 0.1093 +/- 0.0026 | 0.3770 +/- 0.0104 | 0.8358 +/- 0.0032 | 0.2476 +/- 0.0023 |
| retrain_f0.3 | few-shot | 5000 | 0.8021 +/- 0.0019 | 0.7458 +/- 0.0023 | 0.2042 +/- 0.0032 | 0.9831 +/- 0.0004 | 0.2172 +/- 0.0054 | 0.9864 +/- 0.0010 | 0.0715 +/- 0.0029 | 0.0562 +/- 0.0019 | 0.3993 +/- 0.0158 | 0.8496 +/- 0.0041 | 0.1776 +/- 0.0039 |
| retrain_f0.5 | few-shot | 5000 | 0.8180 +/- 0.0015 | 0.7524 +/- 0.0028 | 0.1759 +/- 0.0022 | 0.9812 +/- 0.0006 | 0.2171 +/- 0.0062 | 0.9885 +/- 0.0014 | 0.0629 +/- 0.0028 | 0.0484 +/- 0.0015 | 0.3901 +/- 0.0243 | 0.8557 +/- 0.0042 | 0.1522 +/- 0.0030 |
| thr_adapt | few-shot | 5000 | 0.7398 +/- 0.0023 | 0.7126 +/- 0.0018 | 0.2935 +/- 0.0026 | 0.9682 +/- 0.0028 | 0.2362 +/- 0.0080 | 0.9496 +/- 0.0036 | 0.2371 +/- 0.0088 | 0.1094 +/- 0.0027 | 0.3770 +/- 0.0104 | 0.8358 +/- 0.0032 | 0.2478 +/- 0.0023 |
| retrain_f0.3_domain20 | few-shot+transductive | 5000 | 0.7880 +/- 0.0016 | 0.7368 +/- 0.0025 | 0.2253 +/- 0.0023 | 0.9831 +/- 0.0004 | 0.2244 +/- 0.0086 | 0.9839 +/- 0.0017 | 0.0923 +/- 0.0047 | 0.0718 +/- 0.0019 | 0.3834 +/- 0.0191 | 0.8482 +/- 0.0043 | 0.1964 +/- 0.0029 |
| retrain_f0.5_domain20 | few-shot+transductive | 5000 | 0.8032 +/- 0.0023 | 0.7430 +/- 0.0037 | 0.1994 +/- 0.0027 | 0.9824 +/- 0.0007 | 0.2242 +/- 0.0063 | 0.9873 +/- 0.0013 | 0.0726 +/- 0.0033 | 0.0608 +/- 0.0025 | 0.3801 +/- 0.0093 | 0.8505 +/- 0.0036 | 0.1727 +/- 0.0042 |
| retrain_split_f0.3 | few-shot | 1000 | 0.7581 +/- 0.0014 | 0.7229 +/- 0.0024 | 0.2733 +/- 0.0014 | 0.9801 +/- 0.0022 | 0.1758 +/- 0.0413 | 0.9523 +/- 0.0155 | 0.1661 +/- 0.0140 | 0.1020 +/- 0.0016 | 0.3760 +/- 0.0192 | 0.8450 +/- 0.0045 | 0.2327 +/- 0.0017 |
| retrain_split_f0.5 | few-shot | 1000 | 0.7598 +/- 0.0015 | 0.7234 +/- 0.0027 | 0.2710 +/- 0.0017 | 0.9809 +/- 0.0024 | 0.1578 +/- 0.0374 | 0.9472 +/- 0.0164 | 0.1615 +/- 0.0096 | 0.1033 +/- 0.0017 | 0.3821 +/- 0.0211 | 0.8463 +/- 0.0042 | 0.2304 +/- 0.0018 |
| retrain_split_f0.3 | few-shot | 5000 | 0.7872 +/- 0.0022 | 0.7385 +/- 0.0024 | 0.2284 +/- 0.0040 | 0.9835 +/- 0.0011 | 0.1017 +/- 0.0122 | 0.9520 +/- 0.0060 | 0.0968 +/- 0.0049 | 0.0734 +/- 0.0019 | 0.3750 +/- 0.0109 | 0.8470 +/- 0.0031 | 0.1969 +/- 0.0038 |
| retrain_split_f0.5 | few-shot | 5000 | 0.7957 +/- 0.0031 | 0.7420 +/- 0.0034 | 0.2134 +/- 0.0046 | 0.9825 +/- 0.0013 | 0.0940 +/- 0.0156 | 0.9523 +/- 0.0076 | 0.0887 +/- 0.0029 | 0.0708 +/- 0.0028 | 0.3746 +/- 0.0242 | 0.8503 +/- 0.0044 | 0.1835 +/- 0.0043 |
| domain_weights_clip5 | transductive | 0 | 0.7435 +/- 0.0013 | 0.7139 +/- 0.0011 | 0.2817 +/- 0.0026 | 0.9578 +/- 0.0015 | 0.2408 +/- 0.0073 | 0.9439 +/- 0.0018 | 0.2576 +/- 0.0039 | 0.1148 +/- 0.0014 | 0.3999 +/- 0.0107 | 0.8370 +/- 0.0037 | 0.2407 +/- 0.0021 |
| domain_weights_clip20 (declared choice: best validation macro F1) | transductive | 0 | 0.7429 +/- 0.0017 | 0.7135 +/- 0.0018 | 0.2818 +/- 0.0015 | 0.9558 +/- 0.0026 | 0.2406 +/- 0.0043 | 0.9413 +/- 0.0023 | 0.2620 +/- 0.0079 | 0.1154 +/- 0.0022 | 0.3935 +/- 0.0105 | 0.8371 +/- 0.0042 | 0.2403 +/- 0.0010 |
| drop_top5_shifted | transductive | 0 | 0.7417 +/- 0.0024 | 0.7143 +/- 0.0029 | 0.2938 +/- 0.0028 | 0.9806 +/- 0.0041 | 0.2456 +/- 0.0069 | 0.9722 +/- 0.0069 | 0.1801 +/- 0.0203 | 0.1049 +/- 0.0022 | 0.3512 +/- 0.0292 | 0.8267 +/- 0.0048 | 0.2475 +/- 0.0026 |
| drop_top10_shifted | transductive | 0 | 0.7377 +/- 0.0009 | 0.7079 +/- 0.0005 | 0.2937 +/- 0.0014 | 0.9743 +/- 0.0126 | 0.2508 +/- 0.0043 | 0.9638 +/- 0.0169 | 0.2076 +/- 0.0514 | 0.1008 +/- 0.0052 | 0.3246 +/- 0.0640 | 0.8172 +/- 0.0126 | 0.2440 +/- 0.0048 |

The markdown shows k = 1,000 and 5,000 and omits retrain_f0.1; the CSV holds every k and method (k = 100 / 500 too).

## Source: task_2_6_table_40f_48f_45f_41f_38f.md

### Task 2.6: is the few-shot result adaptation or neighbour leakage? (official split, mean +/- std over 5 runs)

Few-shot = k labelled test rows (half retrain, half choose the 95%-detection threshold), evaluated on rows not used for adaptation. Zero-shot rows use the validation-chosen threshold.

| pool | k | row | access | FPR at ~95% detection | detection | accuracy | ECE |
|---|---|---|---|---|---|---|---|
| 40f | 1000 | original Task 2.5 result (retrain_split_f0.5, random adaptation rows) | few-shot | 0.2666 +/- 0.0378 | 0.9541 +/- 0.0143 | 0.7515 +/- 0.0013 | 0.0858 +/- 0.0013 |
| 40f | 1000 | twins: all evaluation rows (reproduction) | few-shot | 0.2666 +/- 0.0378 | 0.9541 +/- 0.0143 | 0.7515 +/- 0.0013 | 0.0858 +/- 0.0013 |
| 40f | 1000 | twins: all evaluation rows (reproduction) - zero-shot | zero-shot | 0.2498 +/- 0.0024 | 0.9464 +/- 0.0017 | 0.7425 +/- 0.0009 | 0.0878 +/- 0.0010 |
| 40f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set | few-shot | 0.3563 +/- 0.0525 | 0.9510 +/- 0.0157 | 0.7038 +/- 0.0012 | 0.0988 +/- 0.0017 |
| 40f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set - zero-shot | zero-shot | 0.3258 +/- 0.0046 | 0.9402 +/- 0.0013 | 0.6944 +/- 0.0023 | 0.1022 +/- 0.0025 |
| 40f | 1000 | twins: rows WITH a near twin (<= 0.1) | few-shot | 0.0658 +/- 0.0105 | 0.9743 +/- 0.0095 | 0.9019 +/- 0.0055 | 0.0446 +/- 0.0052 |
| 40f | 1000 | twins: rows WITH a near twin (<= 0.1) - zero-shot | zero-shot | 0.0796 +/- 0.0076 | 0.9878 +/- 0.0022 | 0.8942 +/- 0.0079 | 0.0449 +/- 0.0046 |
| 40f | 1000 | blocks: adaptation rows from the evaluation blocks (within-file) | few-shot | 0.2519 +/- 0.0649 | 0.9457 +/- 0.0293 | 0.7497 +/- 0.0253 | 0.0851 +/- 0.0104 |
| 40f | 1000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) | few-shot | 0.3045 +/- 0.0812 | 0.9622 +/- 0.0232 | 0.7472 +/- 0.0285 | 0.0862 +/- 0.0134 |
| 40f | 1000 | blocks: same rows - zero-shot | zero-shot | 0.2508 +/- 0.0411 | 0.9456 +/- 0.0103 | 0.7388 +/- 0.0298 | 0.0879 +/- 0.0132 |
| 40f | 5000 | original Task 2.5 result (retrain_split_f0.5, random adaptation rows) | few-shot | 0.2318 +/- 0.0108 | 0.9513 +/- 0.0032 | 0.7801 +/- 0.0021 | 0.0600 +/- 0.0019 |
| 40f | 5000 | twins: all evaluation rows (reproduction) | few-shot | 0.2318 +/- 0.0108 | 0.9513 +/- 0.0032 | 0.7801 +/- 0.0021 | 0.0600 +/- 0.0019 |
| 40f | 5000 | twins: all evaluation rows (reproduction) - zero-shot | zero-shot | 0.2497 +/- 0.0033 | 0.9466 +/- 0.0012 | 0.7424 +/- 0.0010 | 0.0877 +/- 0.0011 |
| 40f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set | few-shot | 0.3493 +/- 0.0185 | 0.9457 +/- 0.0050 | 0.7236 +/- 0.0035 | 0.0671 +/- 0.0031 |
| 40f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set - zero-shot | zero-shot | 0.3671 +/- 0.0056 | 0.9356 +/- 0.0014 | 0.6724 +/- 0.0026 | 0.1080 +/- 0.0029 |
| 40f | 5000 | twins: rows WITH a near twin (<= 0.1) | few-shot | 0.0824 +/- 0.0040 | 0.9696 +/- 0.0069 | 0.8791 +/- 0.0030 | 0.0482 +/- 0.0051 |
| 40f | 5000 | twins: rows WITH a near twin (<= 0.1) - zero-shot | zero-shot | 0.1002 +/- 0.0020 | 0.9817 +/- 0.0020 | 0.8651 +/- 0.0018 | 0.0530 +/- 0.0026 |
| 40f | 5000 | blocks: adaptation rows from the evaluation blocks (within-file) | few-shot | 0.2025 +/- 0.0481 | 0.9398 +/- 0.0114 | 0.7809 +/- 0.0175 | 0.0571 +/- 0.0057 |
| 40f | 5000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) | few-shot | 0.2427 +/- 0.0468 | 0.9449 +/- 0.0191 | 0.7666 +/- 0.0296 | 0.0703 +/- 0.0137 |
| 40f | 5000 | blocks: same rows - zero-shot | zero-shot | 0.2508 +/- 0.0411 | 0.9456 +/- 0.0103 | 0.7388 +/- 0.0298 | 0.0879 +/- 0.0132 |
| 48f | 1000 | original Task 2.5 result (retrain_split_f0.5, random adaptation rows) | few-shot | 0.1578 +/- 0.0374 | 0.9472 +/- 0.0164 | 0.7598 +/- 0.0015 | 0.1033 +/- 0.0017 |
| 48f | 1000 | twins: all evaluation rows (reproduction) | few-shot | 0.1578 +/- 0.0374 | 0.9472 +/- 0.0164 | 0.7598 +/- 0.0015 | 0.1033 +/- 0.0017 |
| 48f | 1000 | twins: all evaluation rows (reproduction) - zero-shot | zero-shot | 0.2444 +/- 0.0068 | 0.9525 +/- 0.0013 | 0.7400 +/- 0.0021 | 0.1093 +/- 0.0026 |
| 48f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set | few-shot | 0.1587 +/- 0.0376 | 0.9463 +/- 0.0168 | 0.7600 +/- 0.0013 | 0.1024 +/- 0.0016 |
| 48f | 1000 | twins: rows with NO near twin (<= 0.1) in the adaptation set - zero-shot | zero-shot | 0.2454 +/- 0.0069 | 0.9517 +/- 0.0013 | 0.7397 +/- 0.0021 | 0.1096 +/- 0.0025 |
| 48f | 1000 | twins: rows WITH a near twin (<= 0.1) | few-shot | 0.0289 +/- 0.0078 | 0.9957 +/- 0.0024 | 0.7342 +/- 0.0392 | 0.1887 +/- 0.0231 |
| 48f | 1000 | twins: rows WITH a near twin (<= 0.1) - zero-shot | zero-shot | 0.0997 +/- 0.0154 | 0.9950 +/- 0.0035 | 0.7607 +/- 0.0269 | 0.0916 +/- 0.0124 |
| 48f | 1000 | blocks: adaptation rows from the evaluation blocks (within-file) | few-shot | 0.1395 +/- 0.0442 | 0.9337 +/- 0.0227 | 0.7574 +/- 0.0266 | 0.1028 +/- 0.0129 |
| 48f | 1000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) | few-shot | 0.1528 +/- 0.0466 | 0.9362 +/- 0.0284 | 0.7521 +/- 0.0279 | 0.1084 +/- 0.0151 |
| 48f | 1000 | blocks: same rows - zero-shot | zero-shot | 0.2463 +/- 0.0400 | 0.9511 +/- 0.0086 | 0.7348 +/- 0.0304 | 0.1123 +/- 0.0160 |
| 48f | 5000 | original Task 2.5 result (retrain_split_f0.5, random adaptation rows) | few-shot | 0.0940 +/- 0.0156 | 0.9523 +/- 0.0076 | 0.7957 +/- 0.0031 | 0.0708 +/- 0.0028 |
| 48f | 5000 | twins: all evaluation rows (reproduction) | few-shot | 0.0940 +/- 0.0156 | 0.9523 +/- 0.0076 | 0.7957 +/- 0.0031 | 0.0708 +/- 0.0028 |
| 48f | 5000 | twins: all evaluation rows (reproduction) - zero-shot | zero-shot | 0.2442 +/- 0.0074 | 0.9527 +/- 0.0017 | 0.7398 +/- 0.0023 | 0.1094 +/- 0.0027 |
| 48f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set | few-shot | 0.0958 +/- 0.0159 | 0.9492 +/- 0.0082 | 0.7990 +/- 0.0033 | 0.0656 +/- 0.0028 |
| 48f | 5000 | twins: rows with NO near twin (<= 0.1) in the adaptation set - zero-shot | zero-shot | 0.2478 +/- 0.0078 | 0.9494 +/- 0.0019 | 0.7394 +/- 0.0025 | 0.1103 +/- 0.0028 |
| 48f | 5000 | twins: rows WITH a near twin (<= 0.1) | few-shot | 0.0311 +/- 0.0079 | 0.9920 +/- 0.0012 | 0.7251 +/- 0.0085 | 0.1843 +/- 0.0100 |
| 48f | 5000 | twins: rows WITH a near twin (<= 0.1) - zero-shot | zero-shot | 0.1142 +/- 0.0073 | 0.9934 +/- 0.0013 | 0.7480 +/- 0.0055 | 0.0910 +/- 0.0058 |
| 48f | 5000 | blocks: adaptation rows from the evaluation blocks (within-file) | few-shot | 0.0851 +/- 0.0333 | 0.9446 +/- 0.0089 | 0.7987 +/- 0.0191 | 0.0660 +/- 0.0051 |
| 48f | 5000 | blocks: adaptation rows from other blocks (neighbourhood-disjoint) | few-shot | 0.0854 +/- 0.0162 | 0.9318 +/- 0.0167 | 0.7732 +/- 0.0315 | 0.0905 +/- 0.0184 |
| 48f | 5000 | blocks: same rows - zero-shot | zero-shot | 0.2463 +/- 0.0400 | 0.9511 +/- 0.0086 | 0.7348 +/- 0.0304 | 0.1123 +/- 0.0160 |
| 45f | 1000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.1742 +/- 0.0430 | 0.9477 +/- 0.0174 | 0.7563 +/- 0.0011 | 0.1036 +/- 0.0011 |
| 45f | 5000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.1109 +/- 0.0188 | 0.9557 +/- 0.0086 | 0.7925 +/- 0.0033 | 0.0711 +/- 0.0030 |
| 45f | 0 | ablation: zero-shot (validation-chosen det95) | zero-shot | 0.2455 +/- 0.0074 | 0.9473 +/- 0.0015 | 0.7367 +/- 0.0015 | 0.1093 +/- 0.0017 |
| 41f | 1000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.2549 +/- 0.0452 | 0.9516 +/- 0.0165 | 0.7535 +/- 0.0043 | 0.0812 +/- 0.0044 |
| 41f | 5000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.2308 +/- 0.0106 | 0.9542 +/- 0.0033 | 0.7836 +/- 0.0014 | 0.0533 +/- 0.0011 |
| 41f | 0 | ablation: zero-shot (validation-chosen det95) | zero-shot | 0.2475 +/- 0.0007 | 0.9511 +/- 0.0012 | 0.7390 +/- 0.0013 | 0.0900 +/- 0.0012 |
| 38f | 1000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.2704 +/- 0.0534 | 0.9571 +/- 0.0184 | 0.7529 +/- 0.0043 | 0.0815 +/- 0.0042 |
| 38f | 5000 | ablation: retrain_split_f0.5, random adaptation rows | few-shot | 0.2281 +/- 0.0125 | 0.9527 +/- 0.0036 | 0.7837 +/- 0.0027 | 0.0528 +/- 0.0025 |
| 38f | 0 | ablation: zero-shot (validation-chosen det95) | zero-shot | 0.2473 +/- 0.0026 | 0.9518 +/- 0.0011 | 0.7381 +/- 0.0014 | 0.0908 +/- 0.0012 |

## Source: fpr_study_tuned_40f_45f_48f.md

### Task 2.7 Step 1 (ZERO-SHOT): re-tuning on block-grouped validation, official test, mean +/- std over seeds 42-46

Primary metric `det95_test_fpr` (threshold at 95% detection chosen on block-grouped validation). `earlier_tuned_*` = the Task 2a search on random validation (40 and 48 features only); `blockval_tuned_*` = the 40-trial search on block-grouped validation with the regularised space. Verdict = the declared rule against `default` on the same seeds.

#### 40f

| method | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|
| default | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.256 +/- 0.010 | 0.255 +/- 0.007 | 0.950 +/- 0.003 | 0.093 +/- 0.008 | 0.237 +/- 0.053 |
| earlier_tuned_auc | 0.761 +/- 0.005 | 0.718 +/- 0.002 | 0.245 +/- 0.011 | 0.252 +/- 0.014 | 0.253 +/- 0.009 | 0.950 +/- 0.005 | 0.058 +/- 0.006 | 0.213 +/- 0.038 |
| earlier_tuned_f1 | 0.750 +/- 0.007 | 0.714 +/- 0.003 | 0.269 +/- 0.012 | 0.254 +/- 0.012 | 0.255 +/- 0.009 | 0.950 +/- 0.005 | 0.068 +/- 0.008 | 0.222 +/- 0.051 |
| blockval_tuned_auc | 0.762 +/- 0.005 | 0.714 +/- 0.002 | 0.239 +/- 0.010 | 0.257 +/- 0.014 | 0.261 +/- 0.008 | 0.948 +/- 0.006 | 0.051 +/- 0.006 | 0.239 +/- 0.058 |
| blockval_tuned_f1 | 0.753 +/- 0.006 | 0.713 +/- 0.002 | 0.258 +/- 0.011 | 0.253 +/- 0.014 | 0.262 +/- 0.009 | 0.947 +/- 0.006 | 0.058 +/- 0.007 | 0.273 +/- 0.061 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| earlier_tuned_auc | -0.0035 | 3 of 5 | -0.0007 | no |
| earlier_tuned_f1 | -0.0020 | 4 of 5 | -0.0004 | no |
| blockval_tuned_auc | +0.0010 | 2 of 5 | -0.0022 | no |
| blockval_tuned_f1 | -0.0024 | 3 of 5 | -0.0037 | no |

#### 45f

| method | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|
| default | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.248 +/- 0.012 | 0.264 +/- 0.016 | 0.943 +/- 0.002 | 0.116 +/- 0.009 | 0.353 +/- 0.045 |
| blockval_tuned_auc | 0.726 +/- 0.007 | 0.700 +/- 0.003 | 0.310 +/- 0.013 | 0.258 +/- 0.012 | 0.265 +/- 0.016 | 0.947 +/- 0.002 | 0.093 +/- 0.010 | 0.529 +/- 0.050 |
| blockval_tuned_f1 | 0.747 +/- 0.006 | 0.708 +/- 0.002 | 0.269 +/- 0.014 | 0.255 +/- 0.012 | 0.258 +/- 0.009 | 0.948 +/- 0.003 | 0.072 +/- 0.008 | 0.493 +/- 0.040 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| blockval_tuned_auc | +0.0096 | 0 of 5 | +0.0041 | no |
| blockval_tuned_f1 | +0.0064 | 1 of 5 | +0.0058 | no |

#### 48f

| method | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|
| default | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.248 +/- 0.011 | 0.246 +/- 0.022 | 0.950 +/- 0.005 | 0.115 +/- 0.010 | 0.344 +/- 0.045 |
| earlier_tuned_auc | 0.755 +/- 0.007 | 0.718 +/- 0.003 | 0.265 +/- 0.013 | 0.249 +/- 0.011 | 0.230 +/- 0.015 | 0.957 +/- 0.004 | 0.085 +/- 0.008 | 0.399 +/- 0.052 |
| earlier_tuned_f1 | 0.755 +/- 0.007 | 0.718 +/- 0.003 | 0.265 +/- 0.013 | 0.249 +/- 0.011 | 0.230 +/- 0.015 | 0.957 +/- 0.004 | 0.085 +/- 0.008 | 0.399 +/- 0.052 |
| blockval_tuned_auc | 0.733 +/- 0.006 | 0.709 +/- 0.003 | 0.307 +/- 0.013 | 0.254 +/- 0.014 | 0.230 +/- 0.011 | 0.961 +/- 0.003 | 0.091 +/- 0.010 | 0.546 +/- 0.047 |
| blockval_tuned_f1 | 0.753 +/- 0.007 | 0.716 +/- 0.004 | 0.267 +/- 0.012 | 0.253 +/- 0.011 | 0.227 +/- 0.011 | 0.961 +/- 0.001 | 0.074 +/- 0.008 | 0.496 +/- 0.038 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| earlier_tuned_auc | +0.0012 | 2 of 5 | +0.0071 | no |
| earlier_tuned_f1 | +0.0012 | 2 of 5 | +0.0071 | no |
| blockval_tuned_auc | +0.0066 | 0 of 5 | +0.0103 | no |
| blockval_tuned_f1 | +0.0049 | 0 of 5 | +0.0111 | no |

## Source: fpr_study_prior_40f_45f_48f.md

### Task 2.7 Step 2: temperature scaling and class-prior correction, official test, mean +/- std over seeds 42-46

`calibrated` and `calibrated_valprior` are ZERO-SHOT; `calibrated_em` is TRANSDUCTIVE (uses the unlabelled test features). The same transformation is applied to validation and test; the det95 threshold is chosen on the transformed validation scores.

#### 40f

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default | zero-shot | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.256 +/- 0.010 | 0.255 +/- 0.007 | 0.950 +/- 0.003 | 0.093 +/- 0.008 | 0.237 +/- 0.053 |
| calibrated | zero-shot | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.259 +/- 0.010 | 0.256 +/- 0.007 | 0.951 +/- 0.003 | 0.070 +/- 0.006 | 0.237 +/- 0.052 |
| calibrated_valprior | zero-shot | 0.766 +/- 0.060 | 0.718 +/- 0.022 | 0.230 +/- 0.123 | 0.256 +/- 0.011 | 0.253 +/- 0.007 | 0.951 +/- 0.003 | 0.060 +/- 0.060 | 0.241 +/- 0.118 |
| calibrated_em | transductive | 0.775 +/- 0.023 | 0.680 +/- 0.030 | 0.196 +/- 0.038 | 0.249 +/- 0.008 | 0.245 +/- 0.008 | 0.952 +/- 0.004 | 0.044 +/- 0.015 | 0.037 +/- 0.028 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| calibrated | +0.0029 | 0 of 5 | +0.0008 | no |
| calibrated_valprior | +0.0008 | 2 of 5 | +0.0006 | no |
| calibrated_em | -0.0066 | 5 of 5 | +0.0012 | no |

Temperature (mean) 1.18. Diagnostic only, the true shares never enter a fit: L1 distance to the true test shares: EM estimate 0.233 +/- 0.037, model prior 0.600 +/- 0.035, validation shares 0.452 +/- 0.336. EM validation gate (simulated shifts) passes in 4 of 5 seeds.

| class | estimated share | true share |
|---|---|---|
| Exploits | 0.162 | 0.139 |
| Fuzzers | 0.182 | 0.088 |
| Generic | 0.059 | 0.063 |
| Normal | 0.528 | 0.620 |
| Overlap-Group-1 | 0.028 | 0.045 |
| Reconnaissance | 0.041 | 0.045 |

#### 45f

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.248 +/- 0.012 | 0.264 +/- 0.016 | 0.943 +/- 0.002 | 0.116 +/- 0.009 | 0.353 +/- 0.045 |
| calibrated | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.251 +/- 0.013 | 0.261 +/- 0.018 | 0.946 +/- 0.002 | 0.086 +/- 0.003 | 0.366 +/- 0.050 |
| calibrated_valprior | zero-shot | 0.753 +/- 0.052 | 0.706 +/- 0.019 | 0.249 +/- 0.108 | 0.249 +/- 0.012 | 0.259 +/- 0.017 | 0.945 +/- 0.003 | 0.074 +/- 0.057 | 0.309 +/- 0.114 |
| calibrated_em | transductive | 0.759 +/- 0.017 | 0.682 +/- 0.033 | 0.228 +/- 0.030 | 0.244 +/- 0.010 | 0.259 +/- 0.014 | 0.943 +/- 0.003 | 0.065 +/- 0.011 | 0.120 +/- 0.084 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| calibrated | +0.0029 | 0 of 5 | +0.0033 | no |
| calibrated_valprior | +0.0007 | 1 of 5 | +0.0029 | no |
| calibrated_em | -0.0037 | 4 of 5 | +0.0007 | no |

Temperature (mean) 1.25. Diagnostic only, the true shares never enter a fit: L1 distance to the true test shares: EM estimate 0.245 +/- 0.032, model prior 0.600 +/- 0.035, validation shares 0.452 +/- 0.336. EM validation gate (simulated shifts) passes in 4 of 5 seeds.

| class | estimated share | true share |
|---|---|---|
| Exploits | 0.164 | 0.139 |
| Fuzzers | 0.186 | 0.088 |
| Generic | 0.059 | 0.063 |
| Normal | 0.516 | 0.620 |
| Overlap-Group-1 | 0.036 | 0.045 |
| Reconnaissance | 0.040 | 0.045 |

#### 48f

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default | zero-shot | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.248 +/- 0.011 | 0.246 +/- 0.022 | 0.950 +/- 0.005 | 0.115 +/- 0.010 | 0.344 +/- 0.045 |
| calibrated | zero-shot | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.249 +/- 0.012 | 0.242 +/- 0.023 | 0.952 +/- 0.005 | 0.086 +/- 0.002 | 0.357 +/- 0.047 |
| calibrated_valprior | zero-shot | 0.757 +/- 0.053 | 0.712 +/- 0.020 | 0.249 +/- 0.108 | 0.248 +/- 0.012 | 0.241 +/- 0.024 | 0.952 +/- 0.006 | 0.074 +/- 0.060 | 0.290 +/- 0.131 |
| calibrated_em | transductive | 0.762 +/- 0.018 | 0.691 +/- 0.030 | 0.230 +/- 0.032 | 0.244 +/- 0.010 | 0.241 +/- 0.020 | 0.951 +/- 0.005 | 0.065 +/- 0.012 | 0.113 +/- 0.082 |

| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |
|---|---|---|---|---|
| calibrated | +0.0011 | 1 of 5 | +0.0022 | no |
| calibrated_valprior | -0.0002 | 3 of 5 | +0.0022 | no |
| calibrated_em | -0.0039 | 5 of 5 | +0.0006 | no |

Temperature (mean) 1.26. Diagnostic only, the true shares never enter a fit: L1 distance to the true test shares: EM estimate 0.250 +/- 0.033, model prior 0.600 +/- 0.035, validation shares 0.452 +/- 0.336. EM validation gate (simulated shifts) passes in 4 of 5 seeds.

| class | estimated share | true share |
|---|---|---|
| Exploits | 0.166 | 0.139 |
| Fuzzers | 0.186 | 0.088 |
| Generic | 0.059 | 0.063 |
| Normal | 0.513 | 0.620 |
| Overlap-Group-1 | 0.037 | 0.045 |
| Reconnaissance | 0.039 | 0.045 |

## Source: fpr_study_self_40f_45f_48f.md

### Task 2.7 Step 3 (TRANSDUCTIVE): self-training, mean +/- std over seeds 42-46

Two rounds, tau = 0.90, pseudo-labelled rows carry 20% of the sample weight, rounds are not cumulative. Pseudo-labels come from the unlabelled blocks and every metric is on the other blocks (200-row gaps). `validation` rows are the check made before looking at the test file (half of the block-grouped validation blocks treated as unlabelled).

#### 40f

##### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.811 +/- 0.111 | 0.729 +/- 0.065 | 0.210 +/- 0.219 | n/a | n/a | n/a |
| self_round1 | transductive | 0.811 +/- 0.111 | 0.729 +/- 0.064 | 0.209 +/- 0.218 | n/a | n/a | n/a |
| self_round2 | transductive | 0.812 +/- 0.110 | 0.704 +/- 0.077 | 0.207 +/- 0.215 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR -0.0034 (lower in 4 of 5 seeds), macro F1 -0.0245.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): fails.

##### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.726 +/- 0.042 | 0.709 +/- 0.025 | 0.314 +/- 0.071 | 0.283 +/- 0.082 | 0.944 +/- 0.007 | 0.090 +/- 0.017 |
| self_round1 | transductive | 0.721 +/- 0.046 | 0.707 +/- 0.027 | 0.325 +/- 0.080 | 0.283 +/- 0.087 | 0.944 +/- 0.009 | 0.101 +/- 0.020 |
| self_round2 | transductive | 0.722 +/- 0.045 | 0.706 +/- 0.025 | 0.324 +/- 0.079 | 0.282 +/- 0.085 | 0.944 +/- 0.007 | 0.101 +/- 0.020 |

Round 2 minus round 0: argmax FPR +0.0097 (lower in 0 of 5 seeds), macro F1 -0.0022.

##### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13360.800 +/- 1915.084 | 0.034 +/- 0.016 | 0.023 +/- 0.012 | 0.089 +/- 0.040 |
| self_round1 | 13730.400 +/- 1840.486 | 0.043 +/- 0.020 | 0.031 +/- 0.015 | 0.107 +/- 0.045 |

#### 45f

##### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.818 +/- 0.111 | 0.736 +/- 0.064 | 0.208 +/- 0.222 | n/a | n/a | n/a |
| self_round1 | transductive | 0.819 +/- 0.110 | 0.712 +/- 0.074 | 0.207 +/- 0.221 | n/a | n/a | n/a |
| self_round2 | transductive | 0.820 +/- 0.108 | 0.737 +/- 0.064 | 0.205 +/- 0.216 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR -0.0030 (lower in 3 of 5 seeds), macro F1 +0.0009.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): passes.

##### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.719 +/- 0.043 | 0.704 +/- 0.024 | 0.324 +/- 0.075 | 0.271 +/- 0.078 | 0.936 +/- 0.005 | 0.116 +/- 0.023 |
| self_round1 | transductive | 0.718 +/- 0.046 | 0.703 +/- 0.026 | 0.332 +/- 0.080 | 0.275 +/- 0.084 | 0.947 +/- 0.010 | 0.123 +/- 0.025 |
| self_round2 | transductive | 0.721 +/- 0.047 | 0.706 +/- 0.027 | 0.331 +/- 0.082 | 0.274 +/- 0.082 | 0.953 +/- 0.009 | 0.124 +/- 0.025 |

Round 2 minus round 0: argmax FPR +0.0070 (lower in 0 of 5 seeds), macro F1 +0.0022.

##### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13599.200 +/- 1789.848 | 0.054 +/- 0.026 | 0.041 +/- 0.020 | 0.144 +/- 0.055 |
| self_round1 | 14234.200 +/- 1653.202 | 0.073 +/- 0.034 | 0.057 +/- 0.027 | 0.176 +/- 0.064 |

#### 48f

##### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.822 +/- 0.111 | 0.717 +/- 0.076 | 0.207 +/- 0.220 | n/a | n/a | n/a |
| self_round1 | transductive | 0.821 +/- 0.111 | 0.716 +/- 0.074 | 0.209 +/- 0.223 | n/a | n/a | n/a |
| self_round2 | transductive | 0.820 +/- 0.111 | 0.716 +/- 0.072 | 0.209 +/- 0.222 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR +0.0022 (lower in 1 of 5 seeds), macro F1 -0.0013.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): passes.

##### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.723 +/- 0.044 | 0.710 +/- 0.025 | 0.323 +/- 0.074 | 0.272 +/- 0.080 | 0.944 +/- 0.007 | 0.114 +/- 0.022 |
| self_round1 | transductive | 0.722 +/- 0.047 | 0.710 +/- 0.027 | 0.332 +/- 0.081 | 0.274 +/- 0.080 | 0.956 +/- 0.008 | 0.123 +/- 0.025 |
| self_round2 | transductive | 0.726 +/- 0.046 | 0.714 +/- 0.027 | 0.329 +/- 0.080 | 0.271 +/- 0.080 | 0.961 +/- 0.008 | 0.122 +/- 0.025 |

Round 2 minus round 0: argmax FPR +0.0054 (lower in 0 of 5 seeds), macro F1 +0.0039.

##### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13770.600 +/- 1753.373 | 0.054 +/- 0.026 | 0.041 +/- 0.020 | 0.140 +/- 0.055 |
| self_round1 | 14412.600 +/- 1622.903 | 0.073 +/- 0.034 | 0.058 +/- 0.028 | 0.172 +/- 0.063 |

## Source: fpr_study_fewshot_48f_45f_41f.md

### Task 2.7 Step 4 (FEW-SHOT): label budget and selection strategy, mean +/- std over 5 runs

Half of the k labelled rows retrain the model (weight fraction 0.5), the other half chooses the 95%-detection threshold. Candidates and evaluation rows come from different time blocks (200-row gaps); every method is scored on the same evaluation rows as the zero-shot baseline. Two FPRs are shown: `det95 FPR` at the threshold chosen on the held-out labelled half (its test detection is in the next column and is often below 95%, which flatters the FPR) and the threshold-free FPR at exactly 95% detection. Smallest k with mean FPR <= 0.15 is stated per strategy for both.

#### 48f

Zero-shot baseline on the same rows: det95 FPR 0.255 +/- 0.049, threshold-free FPR at 95% detection 0.251 +/- 0.055, detection 0.950 +/- 0.009, argmax FPR 0.304 +/- 0.049.

| strategy | k | det95 FPR | detection | FPR at exactly 95% detection | argmax FPR | accuracy | macro F1 | ECE | held-out half FPR | labelled attack share |
|---|---|---|---|---|---|---|---|---|---|---|
| random | 100 | 0.306 +/- 0.052 | 0.967 +/- 0.022 | 0.249 +/- 0.045 | 0.302 +/- 0.049 | 0.731 +/- 0.030 | 0.702 +/- 0.015 | 0.121 +/- 0.019 | 0.325 +/- 0.119 | 0.362 +/- 0.100 |
| entropy | 100 | 0.212 +/- 0.059 | 0.936 +/- 0.025 | 0.241 +/- 0.049 | 0.307 +/- 0.048 | 0.730 +/- 0.030 | 0.704 +/- 0.017 | 0.120 +/- 0.017 | 0.883 +/- 0.162 | 0.882 +/- 0.036 |
| diverse | 100 | 0.214 +/- 0.076 | 0.923 +/- 0.031 | 0.258 +/- 0.043 | 0.305 +/- 0.049 | 0.728 +/- 0.031 | 0.699 +/- 0.018 | 0.125 +/- 0.020 | 0.273 +/- 0.085 | 0.422 +/- 0.066 |
| mix | 100 | 0.224 +/- 0.042 | 0.942 +/- 0.007 | 0.244 +/- 0.052 | 0.305 +/- 0.049 | 0.730 +/- 0.031 | 0.704 +/- 0.017 | 0.123 +/- 0.021 | 0.307 +/- 0.100 | 0.638 +/- 0.044 |
| random | 250 | 0.209 +/- 0.056 | 0.944 +/- 0.026 | 0.214 +/- 0.047 | 0.298 +/- 0.049 | 0.735 +/- 0.030 | 0.703 +/- 0.020 | 0.123 +/- 0.021 | 0.191 +/- 0.087 | 0.402 +/- 0.083 |
| entropy | 250 | 0.160 +/- 0.026 | 0.926 +/- 0.017 | 0.214 +/- 0.053 | 0.307 +/- 0.048 | 0.731 +/- 0.029 | 0.703 +/- 0.015 | 0.121 +/- 0.019 | 0.378 +/- 0.132 | 0.846 +/- 0.056 |
| diverse | 250 | 0.160 +/- 0.097 | 0.908 +/- 0.042 | 0.247 +/- 0.032 | 0.301 +/- 0.048 | 0.731 +/- 0.029 | 0.703 +/- 0.017 | 0.126 +/- 0.020 | 0.181 +/- 0.123 | 0.422 +/- 0.067 |
| mix | 250 | 0.216 +/- 0.066 | 0.942 +/- 0.023 | 0.229 +/- 0.042 | 0.304 +/- 0.048 | 0.731 +/- 0.030 | 0.702 +/- 0.019 | 0.122 +/- 0.020 | 0.257 +/- 0.047 | 0.646 +/- 0.049 |
| random | 500 | 0.201 +/- 0.062 | 0.949 +/- 0.011 | 0.199 +/- 0.039 | 0.294 +/- 0.047 | 0.740 +/- 0.030 | 0.708 +/- 0.017 | 0.120 +/- 0.019 | 0.160 +/- 0.057 | 0.366 +/- 0.058 |
| entropy | 500 | 0.168 +/- 0.042 | 0.930 +/- 0.036 | 0.201 +/- 0.045 | 0.305 +/- 0.049 | 0.733 +/- 0.030 | 0.706 +/- 0.018 | 0.121 +/- 0.020 | 0.301 +/- 0.105 | 0.802 +/- 0.056 |
| diverse | 500 | 0.126 +/- 0.062 | 0.887 +/- 0.053 | 0.216 +/- 0.036 | 0.295 +/- 0.048 | 0.737 +/- 0.028 | 0.705 +/- 0.014 | 0.122 +/- 0.018 | 0.126 +/- 0.062 | 0.420 +/- 0.079 |
| mix | 500 | 0.160 +/- 0.044 | 0.934 +/- 0.020 | 0.193 +/- 0.049 | 0.303 +/- 0.048 | 0.735 +/- 0.030 | 0.706 +/- 0.016 | 0.122 +/- 0.016 | 0.192 +/- 0.047 | 0.628 +/- 0.053 |
| random | 1000 | 0.164 +/- 0.046 | 0.941 +/- 0.008 | 0.185 +/- 0.047 | 0.286 +/- 0.048 | 0.745 +/- 0.031 | 0.711 +/- 0.019 | 0.118 +/- 0.020 | 0.138 +/- 0.049 | 0.381 +/- 0.068 |
| entropy | 1000 | 0.144 +/- 0.060 | 0.924 +/- 0.035 | 0.191 +/- 0.036 | 0.295 +/- 0.048 | 0.739 +/- 0.030 | 0.709 +/- 0.019 | 0.121 +/- 0.020 | 0.159 +/- 0.069 | 0.709 +/- 0.089 |
| diverse | 1000 | 0.138 +/- 0.031 | 0.923 +/- 0.016 | 0.200 +/- 0.058 | 0.287 +/- 0.048 | 0.742 +/- 0.031 | 0.707 +/- 0.018 | 0.119 +/- 0.020 | 0.127 +/- 0.060 | 0.411 +/- 0.066 |
| mix | 1000 | 0.159 +/- 0.038 | 0.936 +/- 0.028 | 0.182 +/- 0.036 | 0.295 +/- 0.051 | 0.739 +/- 0.031 | 0.708 +/- 0.017 | 0.119 +/- 0.020 | 0.186 +/- 0.082 | 0.602 +/- 0.059 |
| random | 2500 | 0.126 +/- 0.020 | 0.938 +/- 0.018 | 0.152 +/- 0.036 | 0.268 +/- 0.045 | 0.757 +/- 0.027 | 0.718 +/- 0.013 | 0.107 +/- 0.016 | 0.103 +/- 0.040 | 0.375 +/- 0.069 |
| entropy | 2500 | 0.164 +/- 0.039 | 0.947 +/- 0.020 | 0.167 +/- 0.042 | 0.272 +/- 0.044 | 0.753 +/- 0.027 | 0.717 +/- 0.017 | 0.112 +/- 0.018 | 0.135 +/- 0.027 | 0.578 +/- 0.064 |
| diverse | 2500 | 0.099 +/- 0.014 | 0.926 +/- 0.010 | 0.148 +/- 0.035 | 0.270 +/- 0.046 | 0.756 +/- 0.029 | 0.718 +/- 0.019 | 0.109 +/- 0.017 | 0.070 +/- 0.024 | 0.394 +/- 0.065 |
| mix | 2500 | 0.127 +/- 0.032 | 0.938 +/- 0.021 | 0.152 +/- 0.046 | 0.272 +/- 0.048 | 0.754 +/- 0.030 | 0.717 +/- 0.018 | 0.107 +/- 0.020 | 0.120 +/- 0.050 | 0.532 +/- 0.074 |
| random | 5000 | 0.089 +/- 0.003 | 0.935 +/- 0.015 | 0.122 +/- 0.032 | 0.248 +/- 0.052 | 0.769 +/- 0.033 | 0.723 +/- 0.020 | 0.095 +/- 0.022 | 0.052 +/- 0.017 | 0.373 +/- 0.060 |
| entropy | 5000 | 0.154 +/- 0.031 | 0.964 +/- 0.013 | 0.113 +/- 0.026 | 0.212 +/- 0.046 | 0.790 +/- 0.030 | 0.734 +/- 0.019 | 0.082 +/- 0.021 | 0.118 +/- 0.056 | 0.470 +/- 0.063 |
| diverse | 5000 | 0.091 +/- 0.016 | 0.933 +/- 0.016 | 0.130 +/- 0.035 | 0.248 +/- 0.050 | 0.769 +/- 0.031 | 0.722 +/- 0.019 | 0.096 +/- 0.020 | 0.056 +/- 0.022 | 0.383 +/- 0.065 |
| mix | 5000 | 0.120 +/- 0.014 | 0.945 +/- 0.015 | 0.132 +/- 0.035 | 0.248 +/- 0.047 | 0.769 +/- 0.029 | 0.724 +/- 0.018 | 0.096 +/- 0.019 | 0.088 +/- 0.029 | 0.470 +/- 0.058 |

| strategy | smallest k with mean det95 FPR <= 0.15 | smallest k with mean FPR at exactly 95% detection <= 0.15 |
|---|---|---|
| random | 2500 | 5000 |
| entropy | 1000 | 5000 |
| diverse | 500 | 2500 |
| mix | 2500 | 5000 |

#### 45f

Zero-shot baseline on the same rows: det95 FPR 0.255 +/- 0.047, threshold-free FPR at 95% detection 0.269 +/- 0.053, detection 0.942 +/- 0.009, argmax FPR 0.304 +/- 0.048.

| strategy | k | det95 FPR | detection | FPR at exactly 95% detection | argmax FPR | accuracy | macro F1 | ECE | held-out half FPR | labelled attack share |
|---|---|---|---|---|---|---|---|---|---|---|
| random | 100 | 0.305 +/- 0.070 | 0.962 +/- 0.026 | 0.267 +/- 0.052 | 0.303 +/- 0.049 | 0.726 +/- 0.031 | 0.695 +/- 0.015 | 0.122 +/- 0.020 | 0.307 +/- 0.131 | 0.362 +/- 0.100 |
| entropy | 100 | 0.208 +/- 0.059 | 0.926 +/- 0.026 | 0.261 +/- 0.053 | 0.308 +/- 0.047 | 0.726 +/- 0.030 | 0.698 +/- 0.017 | 0.122 +/- 0.018 | 0.545 +/- 0.161 | 0.836 +/- 0.051 |
| diverse | 100 | 0.166 +/- 0.133 | 0.864 +/- 0.145 | 0.271 +/- 0.047 | 0.303 +/- 0.049 | 0.726 +/- 0.031 | 0.696 +/- 0.016 | 0.125 +/- 0.019 | 0.215 +/- 0.160 | 0.396 +/- 0.074 |
| mix | 100 | 0.221 +/- 0.047 | 0.931 +/- 0.028 | 0.253 +/- 0.041 | 0.305 +/- 0.050 | 0.727 +/- 0.031 | 0.698 +/- 0.017 | 0.123 +/- 0.020 | 0.369 +/- 0.110 | 0.622 +/- 0.075 |
| random | 250 | 0.254 +/- 0.036 | 0.958 +/- 0.022 | 0.228 +/- 0.044 | 0.298 +/- 0.048 | 0.732 +/- 0.030 | 0.697 +/- 0.021 | 0.123 +/- 0.020 | 0.263 +/- 0.112 | 0.402 +/- 0.083 |
| entropy | 250 | 0.209 +/- 0.056 | 0.939 +/- 0.013 | 0.240 +/- 0.058 | 0.309 +/- 0.048 | 0.727 +/- 0.032 | 0.698 +/- 0.019 | 0.121 +/- 0.019 | 0.488 +/- 0.130 | 0.826 +/- 0.059 |
| diverse | 250 | 0.176 +/- 0.143 | 0.889 +/- 0.081 | 0.262 +/- 0.060 | 0.299 +/- 0.048 | 0.728 +/- 0.031 | 0.693 +/- 0.020 | 0.125 +/- 0.019 | 0.188 +/- 0.122 | 0.410 +/- 0.072 |
| mix | 250 | 0.202 +/- 0.048 | 0.931 +/- 0.015 | 0.243 +/- 0.061 | 0.305 +/- 0.050 | 0.728 +/- 0.033 | 0.697 +/- 0.021 | 0.123 +/- 0.021 | 0.257 +/- 0.048 | 0.620 +/- 0.038 |
| random | 500 | 0.226 +/- 0.046 | 0.955 +/- 0.012 | 0.215 +/- 0.038 | 0.294 +/- 0.048 | 0.737 +/- 0.031 | 0.702 +/- 0.018 | 0.121 +/- 0.020 | 0.182 +/- 0.096 | 0.366 +/- 0.058 |
| entropy | 500 | 0.157 +/- 0.057 | 0.915 +/- 0.031 | 0.225 +/- 0.047 | 0.306 +/- 0.049 | 0.729 +/- 0.030 | 0.698 +/- 0.017 | 0.124 +/- 0.019 | 0.262 +/- 0.076 | 0.787 +/- 0.059 |
| diverse | 500 | 0.169 +/- 0.073 | 0.900 +/- 0.052 | 0.251 +/- 0.052 | 0.293 +/- 0.045 | 0.732 +/- 0.029 | 0.696 +/- 0.018 | 0.123 +/- 0.018 | 0.168 +/- 0.048 | 0.406 +/- 0.077 |
| mix | 500 | 0.169 +/- 0.049 | 0.926 +/- 0.021 | 0.222 +/- 0.046 | 0.302 +/- 0.050 | 0.732 +/- 0.031 | 0.701 +/- 0.018 | 0.123 +/- 0.019 | 0.238 +/- 0.075 | 0.610 +/- 0.049 |
| random | 1000 | 0.182 +/- 0.043 | 0.942 +/- 0.010 | 0.198 +/- 0.046 | 0.286 +/- 0.048 | 0.742 +/- 0.031 | 0.705 +/- 0.019 | 0.119 +/- 0.020 | 0.150 +/- 0.040 | 0.381 +/- 0.068 |
| entropy | 1000 | 0.188 +/- 0.076 | 0.932 +/- 0.041 | 0.213 +/- 0.045 | 0.296 +/- 0.047 | 0.735 +/- 0.030 | 0.701 +/- 0.020 | 0.120 +/- 0.020 | 0.224 +/- 0.125 | 0.695 +/- 0.095 |
| diverse | 1000 | 0.126 +/- 0.050 | 0.907 +/- 0.030 | 0.198 +/- 0.047 | 0.287 +/- 0.049 | 0.741 +/- 0.030 | 0.706 +/- 0.017 | 0.118 +/- 0.019 | 0.115 +/- 0.040 | 0.405 +/- 0.067 |
| mix | 1000 | 0.189 +/- 0.050 | 0.943 +/- 0.020 | 0.203 +/- 0.045 | 0.296 +/- 0.049 | 0.735 +/- 0.031 | 0.699 +/- 0.021 | 0.120 +/- 0.019 | 0.208 +/- 0.080 | 0.581 +/- 0.058 |
| random | 2500 | 0.132 +/- 0.030 | 0.935 +/- 0.025 | 0.164 +/- 0.042 | 0.268 +/- 0.045 | 0.754 +/- 0.028 | 0.713 +/- 0.014 | 0.107 +/- 0.016 | 0.107 +/- 0.040 | 0.375 +/- 0.069 |
| entropy | 2500 | 0.172 +/- 0.037 | 0.945 +/- 0.027 | 0.181 +/- 0.049 | 0.277 +/- 0.046 | 0.747 +/- 0.029 | 0.711 +/- 0.017 | 0.116 +/- 0.018 | 0.134 +/- 0.050 | 0.579 +/- 0.065 |
| diverse | 2500 | 0.104 +/- 0.017 | 0.924 +/- 0.014 | 0.160 +/- 0.037 | 0.270 +/- 0.045 | 0.753 +/- 0.028 | 0.712 +/- 0.020 | 0.111 +/- 0.017 | 0.075 +/- 0.029 | 0.391 +/- 0.067 |
| mix | 2500 | 0.143 +/- 0.033 | 0.939 +/- 0.021 | 0.167 +/- 0.041 | 0.277 +/- 0.045 | 0.747 +/- 0.028 | 0.708 +/- 0.018 | 0.112 +/- 0.018 | 0.128 +/- 0.050 | 0.520 +/- 0.075 |
| random | 5000 | 0.100 +/- 0.005 | 0.934 +/- 0.015 | 0.138 +/- 0.038 | 0.249 +/- 0.052 | 0.765 +/- 0.033 | 0.717 +/- 0.019 | 0.095 +/- 0.022 | 0.060 +/- 0.018 | 0.373 +/- 0.060 |
| entropy | 5000 | 0.159 +/- 0.026 | 0.963 +/- 0.013 | 0.127 +/- 0.034 | 0.218 +/- 0.048 | 0.784 +/- 0.030 | 0.727 +/- 0.019 | 0.086 +/- 0.022 | 0.126 +/- 0.051 | 0.479 +/- 0.065 |
| diverse | 5000 | 0.104 +/- 0.009 | 0.935 +/- 0.011 | 0.141 +/- 0.037 | 0.246 +/- 0.048 | 0.767 +/- 0.031 | 0.717 +/- 0.020 | 0.096 +/- 0.021 | 0.066 +/- 0.015 | 0.382 +/- 0.066 |
| mix | 5000 | 0.112 +/- 0.016 | 0.938 +/- 0.019 | 0.139 +/- 0.034 | 0.249 +/- 0.048 | 0.765 +/- 0.030 | 0.717 +/- 0.017 | 0.097 +/- 0.021 | 0.086 +/- 0.026 | 0.470 +/- 0.057 |

| strategy | smallest k with mean det95 FPR <= 0.15 | smallest k with mean FPR at exactly 95% detection <= 0.15 |
|---|---|---|
| random | 2500 | 5000 |
| entropy | none reached | 5000 |
| diverse | 1000 | 5000 |
| mix | 2500 | 5000 |

#### 41f

Zero-shot baseline on the same rows: det95 FPR 0.260 +/- 0.042, threshold-free FPR at 95% detection 0.249 +/- 0.039, detection 0.952 +/- 0.011, argmax FPR 0.302 +/- 0.044.

| strategy | k | det95 FPR | detection | FPR at exactly 95% detection | argmax FPR | accuracy | macro F1 | ECE | held-out half FPR | labelled attack share |
|---|---|---|---|---|---|---|---|---|---|---|
| random | 100 | 0.321 +/- 0.120 | 0.961 +/- 0.045 | 0.256 +/- 0.036 | 0.307 +/- 0.046 | 0.726 +/- 0.028 | 0.700 +/- 0.013 | 0.102 +/- 0.016 | 0.275 +/- 0.155 | 0.362 +/- 0.100 |
| entropy | 100 | 0.262 +/- 0.082 | 0.949 +/- 0.039 | 0.255 +/- 0.039 | 0.307 +/- 0.044 | 0.726 +/- 0.027 | 0.700 +/- 0.015 | 0.102 +/- 0.015 | 0.691 +/- 0.141 | 0.806 +/- 0.044 |
| diverse | 100 | 0.193 +/- 0.087 | 0.913 +/- 0.068 | 0.255 +/- 0.038 | 0.306 +/- 0.046 | 0.727 +/- 0.027 | 0.700 +/- 0.014 | 0.102 +/- 0.015 | 0.229 +/- 0.152 | 0.426 +/- 0.086 |
| mix | 100 | 0.234 +/- 0.081 | 0.940 +/- 0.022 | 0.254 +/- 0.036 | 0.308 +/- 0.044 | 0.725 +/- 0.027 | 0.699 +/- 0.016 | 0.102 +/- 0.015 | 0.370 +/- 0.167 | 0.636 +/- 0.033 |
| random | 250 | 0.265 +/- 0.034 | 0.954 +/- 0.019 | 0.249 +/- 0.039 | 0.298 +/- 0.047 | 0.731 +/- 0.029 | 0.701 +/- 0.017 | 0.099 +/- 0.017 | 0.255 +/- 0.120 | 0.402 +/- 0.083 |
| entropy | 250 | 0.275 +/- 0.070 | 0.956 +/- 0.034 | 0.256 +/- 0.037 | 0.312 +/- 0.046 | 0.722 +/- 0.027 | 0.696 +/- 0.015 | 0.102 +/- 0.016 | 0.654 +/- 0.148 | 0.798 +/- 0.072 |
| diverse | 250 | 0.188 +/- 0.051 | 0.922 +/- 0.027 | 0.254 +/- 0.038 | 0.300 +/- 0.041 | 0.729 +/- 0.026 | 0.700 +/- 0.015 | 0.103 +/- 0.014 | 0.216 +/- 0.086 | 0.414 +/- 0.069 |
| mix | 250 | 0.255 +/- 0.036 | 0.949 +/- 0.025 | 0.261 +/- 0.037 | 0.308 +/- 0.046 | 0.724 +/- 0.028 | 0.698 +/- 0.016 | 0.104 +/- 0.017 | 0.380 +/- 0.139 | 0.635 +/- 0.062 |
| random | 500 | 0.257 +/- 0.126 | 0.939 +/- 0.045 | 0.255 +/- 0.035 | 0.291 +/- 0.049 | 0.734 +/- 0.030 | 0.701 +/- 0.018 | 0.099 +/- 0.016 | 0.224 +/- 0.095 | 0.366 +/- 0.058 |
| entropy | 500 | 0.242 +/- 0.064 | 0.938 +/- 0.031 | 0.258 +/- 0.036 | 0.312 +/- 0.045 | 0.720 +/- 0.026 | 0.691 +/- 0.016 | 0.105 +/- 0.016 | 0.612 +/- 0.108 | 0.808 +/- 0.076 |
| diverse | 500 | 0.267 +/- 0.081 | 0.947 +/- 0.034 | 0.253 +/- 0.038 | 0.294 +/- 0.046 | 0.732 +/- 0.028 | 0.702 +/- 0.016 | 0.100 +/- 0.017 | 0.233 +/- 0.021 | 0.410 +/- 0.071 |
| mix | 500 | 0.228 +/- 0.074 | 0.932 +/- 0.032 | 0.258 +/- 0.032 | 0.304 +/- 0.046 | 0.726 +/- 0.027 | 0.697 +/- 0.016 | 0.101 +/- 0.016 | 0.267 +/- 0.065 | 0.609 +/- 0.062 |
| random | 1000 | 0.264 +/- 0.080 | 0.950 +/- 0.022 | 0.254 +/- 0.034 | 0.275 +/- 0.048 | 0.741 +/- 0.028 | 0.704 +/- 0.013 | 0.093 +/- 0.016 | 0.248 +/- 0.056 | 0.381 +/- 0.068 |
| entropy | 1000 | 0.243 +/- 0.059 | 0.942 +/- 0.029 | 0.254 +/- 0.033 | 0.306 +/- 0.045 | 0.723 +/- 0.028 | 0.692 +/- 0.018 | 0.103 +/- 0.018 | 0.470 +/- 0.079 | 0.756 +/- 0.095 |
| diverse | 1000 | 0.268 +/- 0.054 | 0.953 +/- 0.020 | 0.252 +/- 0.043 | 0.276 +/- 0.045 | 0.741 +/- 0.028 | 0.704 +/- 0.015 | 0.093 +/- 0.018 | 0.261 +/- 0.071 | 0.394 +/- 0.068 |
| mix | 1000 | 0.251 +/- 0.080 | 0.941 +/- 0.032 | 0.256 +/- 0.035 | 0.296 +/- 0.049 | 0.729 +/- 0.028 | 0.695 +/- 0.016 | 0.100 +/- 0.017 | 0.289 +/- 0.093 | 0.601 +/- 0.059 |
| random | 2500 | 0.246 +/- 0.060 | 0.943 +/- 0.018 | 0.260 +/- 0.036 | 0.251 +/- 0.045 | 0.753 +/- 0.027 | 0.709 +/- 0.013 | 0.081 +/- 0.015 | 0.225 +/- 0.058 | 0.375 +/- 0.069 |
| entropy | 2500 | 0.332 +/- 0.047 | 0.981 +/- 0.005 | 0.246 +/- 0.035 | 0.272 +/- 0.045 | 0.742 +/- 0.028 | 0.705 +/- 0.015 | 0.096 +/- 0.017 | 0.397 +/- 0.078 | 0.535 +/- 0.078 |
| diverse | 2500 | 0.268 +/- 0.059 | 0.954 +/- 0.020 | 0.250 +/- 0.038 | 0.260 +/- 0.045 | 0.750 +/- 0.026 | 0.709 +/- 0.013 | 0.087 +/- 0.014 | 0.231 +/- 0.048 | 0.356 +/- 0.065 |
| mix | 2500 | 0.256 +/- 0.074 | 0.949 +/- 0.026 | 0.249 +/- 0.030 | 0.264 +/- 0.046 | 0.747 +/- 0.028 | 0.704 +/- 0.016 | 0.087 +/- 0.015 | 0.272 +/- 0.062 | 0.523 +/- 0.063 |
| random | 5000 | 0.228 +/- 0.066 | 0.940 +/- 0.024 | 0.242 +/- 0.037 | 0.227 +/- 0.054 | 0.766 +/- 0.032 | 0.714 +/- 0.017 | 0.069 +/- 0.020 | 0.178 +/- 0.037 | 0.373 +/- 0.060 |
| entropy | 5000 | 0.310 +/- 0.036 | 0.976 +/- 0.008 | 0.238 +/- 0.035 | 0.208 +/- 0.044 | 0.775 +/- 0.027 | 0.719 +/- 0.016 | 0.071 +/- 0.020 | 0.523 +/- 0.100 | 0.447 +/- 0.061 |
| diverse | 5000 | 0.260 +/- 0.056 | 0.953 +/- 0.017 | 0.245 +/- 0.039 | 0.233 +/- 0.048 | 0.764 +/- 0.029 | 0.714 +/- 0.014 | 0.074 +/- 0.016 | 0.219 +/- 0.051 | 0.371 +/- 0.062 |
| mix | 5000 | 0.273 +/- 0.048 | 0.961 +/- 0.014 | 0.243 +/- 0.036 | 0.234 +/- 0.050 | 0.763 +/- 0.029 | 0.715 +/- 0.015 | 0.074 +/- 0.018 | 0.268 +/- 0.066 | 0.434 +/- 0.059 |

| strategy | smallest k with mean det95 FPR <= 0.15 | smallest k with mean FPR at exactly 95% detection <= 0.15 |
|---|---|---|
| random | none reached | none reached |
| entropy | none reached | none reached |
| diverse | none reached | none reached |
| mix | none reached | none reached |

## Source: fpr_study_final_40f_45f_48f.md

### Task 2.7 Step 5: final table (official split, mean +/- std over seeds 42-46)

#### 40f

##### A. Whole official test file (zero-shot and transductive methods)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default (config.yaml) | zero-shot | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.256 +/- 0.010 | 0.255 +/- 0.007 | 0.950 +/- 0.003 | 0.093 +/- 0.008 | 0.237 +/- 0.053 |
| earlier tuned, random validation (auc) | zero-shot | 0.761 +/- 0.005 | 0.718 +/- 0.002 | 0.245 +/- 0.011 | 0.252 +/- 0.014 | 0.253 +/- 0.009 | 0.950 +/- 0.005 | 0.058 +/- 0.006 | 0.213 +/- 0.038 |
| tuned on block-grouped validation (auc) | zero-shot | 0.762 +/- 0.005 | 0.714 +/- 0.002 | 0.239 +/- 0.010 | 0.257 +/- 0.014 | 0.261 +/- 0.008 | 0.948 +/- 0.006 | 0.051 +/- 0.006 | 0.239 +/- 0.058 |
| tuned on block-grouped validation (macro F1) | zero-shot | 0.753 +/- 0.006 | 0.713 +/- 0.002 | 0.258 +/- 0.011 | 0.253 +/- 0.014 | 0.262 +/- 0.009 | 0.947 +/- 0.006 | 0.058 +/- 0.007 | 0.273 +/- 0.061 |
| temperature scaling | zero-shot | 0.741 +/- 0.006 | 0.712 +/- 0.003 | 0.289 +/- 0.012 | 0.259 +/- 0.010 | 0.256 +/- 0.007 | 0.951 +/- 0.003 | 0.070 +/- 0.006 | 0.237 +/- 0.052 |
| temperature scaling + validation class prior (control) | zero-shot | 0.766 +/- 0.060 | 0.718 +/- 0.022 | 0.230 +/- 0.123 | 0.256 +/- 0.011 | 0.253 +/- 0.007 | 0.951 +/- 0.003 | 0.060 +/- 0.060 | 0.241 +/- 0.118 |
| temperature scaling + EM prior correction | transductive | 0.775 +/- 0.023 | 0.680 +/- 0.030 | 0.196 +/- 0.038 | 0.249 +/- 0.008 | 0.245 +/- 0.008 | 0.952 +/- 0.004 | 0.044 +/- 0.015 | 0.037 +/- 0.028 |
| declared combination (tuned if validation AUC >= default, temperature, EM if its gate passes) | zero-shot / transductive | 0.764 +/- 0.025 | 0.698 +/- 0.024 | 0.226 +/- 0.055 | 0.254 +/- 0.015 | 0.253 +/- 0.013 | 0.951 +/- 0.005 | 0.050 +/- 0.019 | 0.106 +/- 0.085 |

##### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.726 +/- 0.042 | 0.709 +/- 0.025 | 0.314 +/- 0.071 | 0.283 +/- 0.082 | 0.296 +/- 0.083 | 0.944 +/- 0.007 | 0.090 +/- 0.017 | 0.237 +/- 0.053 |
| self-training, round 2 | transductive | 0.722 +/- 0.045 | 0.706 +/- 0.025 | 0.324 +/- 0.079 | 0.282 +/- 0.085 | 0.296 +/- 0.086 | 0.944 +/- 0.007 | 0.101 +/- 0.020 | 0.231 +/- 0.041 |

#### 45f

##### A. Whole official test file (zero-shot and transductive methods)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default (config.yaml) | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.248 +/- 0.012 | 0.264 +/- 0.016 | 0.943 +/- 0.002 | 0.116 +/- 0.009 | 0.353 +/- 0.045 |
| tuned on block-grouped validation (auc) | zero-shot | 0.726 +/- 0.007 | 0.700 +/- 0.003 | 0.310 +/- 0.013 | 0.258 +/- 0.012 | 0.265 +/- 0.016 | 0.947 +/- 0.002 | 0.093 +/- 0.010 | 0.529 +/- 0.050 |
| tuned on block-grouped validation (macro F1) | zero-shot | 0.747 +/- 0.006 | 0.708 +/- 0.002 | 0.269 +/- 0.014 | 0.255 +/- 0.012 | 0.258 +/- 0.009 | 0.948 +/- 0.003 | 0.072 +/- 0.008 | 0.493 +/- 0.040 |
| temperature scaling | zero-shot | 0.733 +/- 0.007 | 0.706 +/- 0.004 | 0.299 +/- 0.012 | 0.251 +/- 0.013 | 0.261 +/- 0.018 | 0.946 +/- 0.002 | 0.086 +/- 0.003 | 0.366 +/- 0.050 |
| temperature scaling + validation class prior (control) | zero-shot | 0.753 +/- 0.052 | 0.706 +/- 0.019 | 0.249 +/- 0.108 | 0.249 +/- 0.012 | 0.259 +/- 0.017 | 0.945 +/- 0.003 | 0.074 +/- 0.057 | 0.309 +/- 0.114 |
| temperature scaling + EM prior correction | transductive | 0.759 +/- 0.017 | 0.682 +/- 0.033 | 0.228 +/- 0.030 | 0.244 +/- 0.010 | 0.259 +/- 0.014 | 0.943 +/- 0.003 | 0.065 +/- 0.011 | 0.120 +/- 0.084 |
| declared combination (tuned if validation AUC >= default, temperature, EM if its gate passes) | zero-shot / transductive | 0.751 +/- 0.023 | 0.698 +/- 0.025 | 0.254 +/- 0.052 | 0.249 +/- 0.013 | 0.262 +/- 0.015 | 0.944 +/- 0.003 | 0.072 +/- 0.015 | 0.243 +/- 0.123 |

##### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.719 +/- 0.043 | 0.704 +/- 0.024 | 0.324 +/- 0.075 | 0.271 +/- 0.078 | 0.304 +/- 0.092 | 0.936 +/- 0.005 | 0.116 +/- 0.023 | 0.353 +/- 0.045 |
| self-training, round 2 | transductive | 0.721 +/- 0.047 | 0.706 +/- 0.027 | 0.331 +/- 0.082 | 0.274 +/- 0.082 | 0.266 +/- 0.093 | 0.953 +/- 0.009 | 0.124 +/- 0.025 | 0.371 +/- 0.044 |
| zero-shot baseline (few-shot evaluation rows) | zero-shot | 0.726 +/- 0.031 | 0.697 +/- 0.017 | 0.304 +/- 0.048 | 0.255 +/- 0.047 | 0.269 +/- 0.053 | 0.942 +/- 0.009 | 0.121 +/- 0.019 | 0.353 +/- 0.045 |
| few-shot, diverse selection, k = 1000 | few-shot | 0.741 +/- 0.030 | 0.706 +/- 0.017 | 0.287 +/- 0.049 | 0.126 +/- 0.050 | 0.198 +/- 0.047 | 0.907 +/- 0.030 | 0.118 +/- 0.019 | 0.374 +/- 0.065 |
| few-shot, diverse selection, k = 5000 | few-shot | 0.767 +/- 0.031 | 0.717 +/- 0.020 | 0.246 +/- 0.048 | 0.104 +/- 0.009 | 0.141 +/- 0.037 | 0.935 +/- 0.011 | 0.096 +/- 0.021 | 0.364 +/- 0.046 |

Few-shot strategy chosen by the declared rule (lowest held-out-half FPR at k = 1,000): **diverse**.

#### 48f

##### A. Whole official test file (zero-shot and transductive methods)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| default (config.yaml) | zero-shot | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.248 +/- 0.011 | 0.246 +/- 0.022 | 0.950 +/- 0.005 | 0.115 +/- 0.010 | 0.344 +/- 0.045 |
| earlier tuned, random validation (auc) | zero-shot | 0.755 +/- 0.007 | 0.718 +/- 0.003 | 0.265 +/- 0.013 | 0.249 +/- 0.011 | 0.230 +/- 0.015 | 0.957 +/- 0.004 | 0.085 +/- 0.008 | 0.399 +/- 0.052 |
| tuned on block-grouped validation (auc) | zero-shot | 0.733 +/- 0.006 | 0.709 +/- 0.003 | 0.307 +/- 0.013 | 0.254 +/- 0.014 | 0.230 +/- 0.011 | 0.961 +/- 0.003 | 0.091 +/- 0.010 | 0.546 +/- 0.047 |
| tuned on block-grouped validation (macro F1) | zero-shot | 0.753 +/- 0.007 | 0.716 +/- 0.004 | 0.267 +/- 0.012 | 0.253 +/- 0.011 | 0.227 +/- 0.011 | 0.961 +/- 0.001 | 0.074 +/- 0.008 | 0.496 +/- 0.038 |
| temperature scaling | zero-shot | 0.737 +/- 0.007 | 0.712 +/- 0.006 | 0.298 +/- 0.013 | 0.249 +/- 0.012 | 0.242 +/- 0.023 | 0.952 +/- 0.005 | 0.086 +/- 0.002 | 0.357 +/- 0.047 |
| temperature scaling + validation class prior (control) | zero-shot | 0.757 +/- 0.053 | 0.712 +/- 0.020 | 0.249 +/- 0.108 | 0.248 +/- 0.012 | 0.241 +/- 0.024 | 0.952 +/- 0.006 | 0.074 +/- 0.060 | 0.290 +/- 0.131 |
| temperature scaling + EM prior correction | transductive | 0.762 +/- 0.018 | 0.691 +/- 0.030 | 0.230 +/- 0.032 | 0.244 +/- 0.010 | 0.241 +/- 0.020 | 0.951 +/- 0.005 | 0.065 +/- 0.012 | 0.113 +/- 0.082 |
| declared combination (tuned if validation AUC >= default, temperature, EM if its gate passes) | zero-shot / transductive | 0.755 +/- 0.024 | 0.706 +/- 0.022 | 0.254 +/- 0.053 | 0.247 +/- 0.013 | 0.240 +/- 0.020 | 0.953 +/- 0.006 | 0.071 +/- 0.016 | 0.216 +/- 0.123 |

##### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | fpr_at_95_threshold_free | det95_test_detection | ece | open_set_detection |
|---|---|---|---|---|---|---|---|---|---|
| zero-shot baseline (self-training evaluation rows) | zero-shot | 0.723 +/- 0.044 | 0.710 +/- 0.025 | 0.323 +/- 0.074 | 0.272 +/- 0.080 | 0.285 +/- 0.091 | 0.944 +/- 0.007 | 0.114 +/- 0.022 | 0.344 +/- 0.045 |
| self-training, round 2 | transductive | 0.726 +/- 0.046 | 0.714 +/- 0.027 | 0.329 +/- 0.080 | 0.271 +/- 0.080 | 0.242 +/- 0.091 | 0.961 +/- 0.008 | 0.122 +/- 0.025 | 0.354 +/- 0.054 |
| zero-shot baseline (few-shot evaluation rows) | zero-shot | 0.729 +/- 0.031 | 0.702 +/- 0.017 | 0.304 +/- 0.049 | 0.255 +/- 0.049 | 0.251 +/- 0.055 | 0.950 +/- 0.009 | 0.121 +/- 0.019 | 0.344 +/- 0.045 |
| few-shot, diverse selection, k = 1000 | few-shot | 0.742 +/- 0.031 | 0.707 +/- 0.018 | 0.287 +/- 0.048 | 0.138 +/- 0.031 | 0.200 +/- 0.058 | 0.923 +/- 0.016 | 0.119 +/- 0.020 | 0.355 +/- 0.060 |
| few-shot, diverse selection, k = 5000 | few-shot | 0.769 +/- 0.031 | 0.722 +/- 0.019 | 0.248 +/- 0.050 | 0.091 +/- 0.016 | 0.130 +/- 0.035 | 0.933 +/- 0.016 | 0.096 +/- 0.020 | 0.355 +/- 0.054 |

Few-shot strategy chosen by the declared rule (lowest held-out-half FPR at k = 1,000): **diverse**.

## Source: task_2_5_protocol.md

### Task 2.5 protocol (declared before any Task 2.5 result was produced)

Goal: characterise the official-split shift (Step A), then try to lower the official-split Normal false-positive rate
(Step B). Baseline numbers are those of Task 2 (commits ebef719 .. 32e9ae1); they are not re-litigated here.

#### Access levels (every method is labelled with one)
- **ZERO-SHOT**: uses the training split (train + validation) only.
- **TRANSDUCTIVE**: additionally uses the unlabelled FEATURES of the official test file.
- **FEW-SHOT**: additionally uses k labelled rows drawn from the official test file. Those rows are excluded from
  evaluation. Each adapted result is reported next to the zero-shot result on the same evaluation rows.

#### Selection rules
- The official test LABELS never choose a method, threshold or hyperparameter.
- Primary objective: **validation macro F1** (multiclass for the flat model; the 2-class macro F1 for the binary
  stage 1 of the hierarchical model). Validation attack-vs-normal AUC is recorded as a secondary criterion only.
- Zero-shot / transductive candidates are chosen on validation; the validation-chosen operating point is
  "95% detection" (det95) on 1 - P(Normal).
- Few-shot methods may use only the adaptation sample (never the rest of the test file) for choices.

#### Declared settings
- Step A feature groups (`shift.feature_groups` in config.yaml): volume_size, rate_load, timing, tcp_window_loss,
  protocol_state, ttl, connection_counts. They partition the 48-feature pool; the 40-feature pool has no `ttl` group.
- Step B1: stage-1 search = the Task-2b search space and budget (40 trials per pool, early stopping on validation
  logloss), binary labels, objective validation macro F1; stage 2 keeps the default parameters.
- Step B2: k = 100 / 500 / 1,000 / 5,000 labelled rows, stratified by the training target classes; 5 runs, run i =
  adaptation draw seed 1000 + i with model seed 42 + i. (i) retraining with the adaptation rows carrying a fraction
  f of the total sample weight, f in {0.1, 0.3, 0.5}, **primary f = 0.3** (declared now, not tuned); (ii) re-choosing
  the det95 threshold on the adaptation sample (applied to the zero-shot model; for a retrained model the adaptation
  rows are training rows, so a threshold chosen on them would be optimistic and is not reported).
- Step B3 (only if B1 and B2 leave FPR above the target): domain-classifier importance weights (clip in {5, 20}) and
  removal of the top-5 / top-10 shift-ranked features; the candidate with the best validation macro F1 is the
  declared choice; all candidates are reported. Labelled TRANSDUCTIVE.
- Target hypothesis: official-split FPR <= 0.15 at about 95% detection (a guess, not a prediction).
- Calibration (ECE) and open-set detection / AUROC are reported for every method, favourable or not.
- 0.912 / 0.921 is an empirical feature-space ceiling (best accuracy of any classifier that assigns one label per
  distinct feature vector in this data), not a Bayes ceiling.

## Source: task_2_6_protocol.md

### Task 2.6 protocol (declared before any Task 2.6 result was produced)

Question: is the 48-feature few-shot result of Task 2.5 (FPR 0.094 at about 95% detection with 5,000 labelled rows, against 0.232
on 40 features) real adaptation, or does it come from neighbouring rows shared between the adaptation rows and the evaluation rows
(both are random draws from the same official test file)? The earlier B2/B4 result files are not modified.

#### What was verified in the data before declaring this
- The `ct_*` columns are small integers (maximum 65, minimum 0 or 1 in the official files), consistent with counts over a window of
  recent connections.
- The official files are NOT shuffled: in `id` order, consecutive rows correlate strongly on `ct_dst_ltm` / `ct_srv_src` /
  `ct_src_ltm` (lag-1 correlation 0.67-0.76 in the test file, 0.36-0.45 in the training file, about 0 after shuffling) and share a class
  71% (test) / 57% (train) of the time against 28% / 21% after shuffling. Row order (after exact deduplication and removal of the
  zero-day classes, which keep the file order) is therefore usable grouping information; it is used for check 2.

#### Primary metric (declared now)
FPR at about 95% detection with the threshold chosen on HELD-OUT labelled adaptation rows: the `retrain_split_f0.5` method of
`pipelines/run_adaptation.py --split-threshold` (retrain on half of the k rows with weight fraction 0.5, choose the 95%-detection threshold
on the other half), reported as `det95_test_fpr` with `det95_test_detection`, k = 5,000 (primary) and k = 1,000 (secondary), 5 runs
(model seed 42 + i, adaptation draw seed 1000 + i), mean and std. Accuracy and ECE are reported next to it. Access level: FEW-SHOT.
Zero-shot is reported on the same evaluation rows.

#### Checks, in order
1. **Near-twin share.** Embedding as in `src/evaluation/overlap.py` (log1p, standardised, categoricals exact) fitted on the training
   rows; L-infinity distance <= 0.1 / 0.25 and exact feature-vector equality. Share of evaluation rows with a twin in the adaptation set,
   against the share with a twin in an equally sized random subset of the TRAINING rows and in the whole training set. FPR / detection /
   accuracy / ECE on all evaluation rows, on the rows with NO near twin (<= 0.1) in the adaptation set, and on the rows with one.
2. **Neighbourhood-disjoint split by row order.** The ordered known official-test rows are cut into contiguous blocks of 1,000 rows;
   40% of the blocks (random per run) supply adaptation rows, the others are evaluation rows; 200 rows on each side of every block
   boundary between the two groups are dropped from both (a sliding window of 100 connections cannot span the gap). Three conditions
   are scored on the SAME evaluation rows: zero-shot; adaptation rows drawn at random from the evaluation blocks themselves
   ("within-file", the Task 2.5 style); adaptation rows from the other blocks ("neighbourhood-disjoint").
3. **ct_* ablation.** The 5,000- and 1,000-row `retrain_split_f0.5` runs on: `full_no_ct_window` = 48 features minus the seven window-count
   columns (ct_src_dport_ltm, ct_dst_sport_ltm, ct_srv_src, ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm; 41 features),
   `full_no_ct_any` = minus every column named ct_* (those seven plus ct_state_ttl, ct_flw_http_mthd, ct_ftp_cmd; 38 features), and the
   45-feature pool (minus sttl, dttl, ct_state_ttl), next to the standard 48- and 40-feature results.
4. **Pooled-reference composition.** What the pooled-split model trains on (rows, and the share of each official file), so the
   0.094 vs 0.109 comparison is explained.
5. **(Added because of the ordering finding.)** Validation built from contiguous blocks of the training file (same block / gap sizes)
   instead of a random 15%: does the validation-vs-test FPR gap of Task 2a shrink?

#### Decision rule (declared now)
Applied to the 48-feature pool at k = 5,000 with the mean over the 5 runs, using the worse (higher FPR) of the no-near-twin subset (check 1)
and the neighbourhood-disjoint condition (check 2):
- FPR at about 95% detection <= about 0.15: the few-shot result is reported as robust to neighbourhood leakage.
- FPR >= about 0.20: the original number measured within-file adaptation, and the conclusion is restated that way.
- Between 0.15 and 0.20: reported as partly dependent on neighbourhood overlap, with both numbers shown.
Nothing is tuned to rescue the result.

## Source: task_2_7_protocol.md

### Task 2.7 protocol (declared before any Task 2.7 result was produced)

Goal: lower the official-split Normal false-positive rate. XGBoost, flat model, scheme `current`, official split, seeds 42-46 (run i = model seed 42 + i), mean and std.
Pools: 40 (base), 45 (`full_no_ttl`), 48 (full); Step 4 uses 48, 45 and 41 (`full_no_ct_window`) so the `ct_*` dependence stays visible.
Capped at one session; if nothing clearly beats the baseline the result is reported as negative.

#### Access levels
ZERO-SHOT = training data only. TRANSDUCTIVE = also the unlabelled official-test features. FEW-SHOT = also labelled official-test rows. Every table carries the access level and the
zero-shot baseline of the same pool and rows next to every adapted row.

#### Selection data and baselines
- Every selection (hyperparameters, thresholds, temperature, rules, strategies) uses the **block-grouped validation split** (`block_validation_splits`, 1,000-row blocks, 200-row gaps,
  `data.val_size` 0.15, block draw seeded by the run's seed) or, for few-shot only, the declared labelled adaptation sample. Official-test labels are used only to report.
- Baseline = the default configuration (config.yaml, class-weight exponent 0.5) trained on the same block-grouped split, zero-shot, evaluated on the same rows. For reference Task 3 gave
  block-validated det95 FPR 0.257 / 0.248 / 0.247 (40 / 45 / 48 features).
- **Primary metric:** official-test FPR at about 95% detection with the threshold on 1 - P(Normal) chosen on block-grouped validation (`det95_test_fpr`; few-shot: chosen on the held-out half of the
  labelled sample). Also reported: argmax FPR, threshold-free FPR at 95% detection, detection at the chosen threshold, accuracy, macro F1, ECE (`evaluation.ece_bins`),
  open-set detection (max-softmax at the 5% false-Unknown threshold of Task 4, Worms + Shellcode held out).
- **"Clearly beats the baseline"** (declared now): the mean paired (same seed) difference in `det95_test_fpr` is at most -0.02, the method is better in at least 4 of 5 seeds, and its detection at the
  operating point is not more than 0.02 below the baseline's.

#### Step 1 (ZERO-SHOT): re-tune on block-grouped validation
- 40 random trials per pool (40 / 45 / 48), search seed 42, selection on the seed-42 block-grouped validation split, early stopping 30 rounds on validation mlogloss, at most 1,000 trees. The default
  configuration is scored as a reference (not part of the budget).
- Regularised space (`tuning.space_regularised`): max_depth int [3, 7]; learning_rate loguniform [0.03, 0.3]; min_child_weight choice [5, 10, 20, 50, 100]; subsample uniform [0.6, 1.0];
  colsample_bytree uniform [0.5, 1.0]; reg_lambda loguniform [2, 100]; reg_alpha choice [0, 0.1, 1, 5]; class_weight_power uniform [0, 1].
- Objectives declared up front: validation attack-vs-normal AUC (**primary**, `blockval_tuned_auc`) and validation macro F1 (`blockval_tuned_f1`). n_estimators = best_iteration + 1; no early stopping at evaluation.
- Evaluated over the 5 seeds against the default and the earlier tuned models (`tuned_params_40f.json`, `tuned_params_48f.json`, selected on random validation; none exists for 45) on the same block-grouped
  splits. Files: `hyperparameter_search_blockval_<N>f.csv`, `tuned_params_blockval_<N>f.json`; the earlier files are not touched.

#### Step 2 (TRANSDUCTIVE): class-prior correction
1. Temperature scaling: T in [0.25, 5] minimising the negative log-likelihood of the default model on the block-grouped validation split (scalar, `minimize_scalar` bounded); probabilities proportional to p^(1/T).
2. Reference prior pi_model = class shares of the training rows weighted by the sample weights actually used in training (the prior the model implies).
3. EM prior-shift estimate (Saerens et al. 2002) of the test class shares from the unlabelled test features: start at pi_model, iterate until the largest change is below 1e-6 or 100 iterations.
4. Correction p'(y|x) proportional to p_cal(y|x) * pi_hat(y) / pi_model(y). The same fixed transformation is applied to the validation probabilities, and the det95 threshold is chosen on the transformed validation scores.
5. Variants: `calibrated` (step 1 only), `calibrated_em` (1-4; TRANSDUCTIVE) and a ZERO-SHOT control `calibrated_valprior` (pi_hat = validation class shares, no test features), so the effect of undoing the class weighting is not mistaken for prior-shift correction.
6. Diagnostic only: estimated shares vs the true test shares (L1 distance); the true shares never enter a fit.
7. Validation gate for Step 5: on 5 simulated prior shifts of the validation set (class shares proportional to validation share * exp(z), z ~ N(0, 1), seeds 42-46, resampled with replacement), the EM estimate must have a mean
   L1 error below half of the L1 distance between pi_model and the simulated shares; otherwise EM is not used in the combination.

#### Step 3 (TRANSDUCTIVE, risky): self-training
- Two rounds, confidence threshold tau = 0.90 on max-softmax, pseudo-labelled rows weighted to carry a fraction f = 0.2 of the total sample weight, rounds are not cumulative (round 2 re-labels from the round-1 model).
- The ordered official-test known rows are cut into blocks (`block_split`, 1,000 / 200, share 0.5 unlabelled, draw seed 1000 + run): pseudo-labels come from the unlabelled blocks, evaluation is on the other blocks
  (neighbourhood-disjoint), so no pseudo-labelled row is evaluated. Zero-shot baseline on the same evaluation rows.
- Validation check before test: the same procedure with half of the block-grouped validation blocks as the unlabelled set, scored on the other validation blocks; passes when macro F1 does not fall by more than 0.01 and
  argmax FPR does not rise by more than 0.01. The test run is made and reported either way.
- Reinforcement diagnostics (test labels used to REPORT only): share of pseudo-labelled flows that are wrong, share of true Normal flows that receive an attack pseudo-label, and the Normal flows called an attack by the round-0 / 1 / 2 models.

#### Step 4 (FEW-SHOT): label budget and selection
- Budgets k = 100, 250, 500, 1,000, 2,500, 5,000. Strategies: `random` (uniform, labels unused), `entropy` (the k highest-entropy rows of the zero-shot model), `diverse` (rows nearest the centroids of k-means, k clusters, scaled preprocessed features,
  MiniBatchKMeans seed 0), `mix` (half entropy, half diverse). Selection uses only unlabelled features and the zero-shot model; labels are revealed for the chosen rows only.
- Candidates are the rows of the adaptation blocks (`block_split`, 1,000 / 200, share 0.4, draw seed 1000 + run); evaluation rows are the other blocks (200-row gaps). The chosen rows are split at random into two halves: one retrains the model
  (weight fraction 0.5), the other chooses the det95 threshold. 5 runs (model seed 42 + i with draw seed 1000 + i; the "5 draws x 5 seeds" are the same five runs, as in Tasks 2.5 / 2.6). Pools 48, 45, 41.
- Reported per strategy: FPR and detection vs k against the zero-shot baseline on the same rows, and the smallest k whose mean det95 FPR is at most 0.15, if any. The random-split figure is not used. The held-out-half FPR of each run is recorded for the Step 5 choice.

#### Step 5: combination and final table
- Zero-shot recipe, chosen on validation only: the tuned configuration if its validation attack AUC is at least the default's (otherwise the default); temperature scaling always (ECE); the EM prior correction only if its validation gate (Step 2) passes;
  self-training only if its validation check (Step 3) passes. Few-shot: for each pool the strategy with the lowest mean held-out-half FPR at k = 1,000 (a rule that uses only the labelled sample), reported at every k.
- Final table per pool: method, access level, accuracy, macro F1, FPR (argmax, det95, threshold-free), detection, ECE, open-set detection, next to the defaults. Hypothesis (a guess, not a prediction): zero-shot methods reach about 0.20-0.22;
  0.15 or below needs labels.
- Output under `results/metrics/xgboost/` with the pool in the file name; earlier files are never overwritten; every new function has a test.

## Source: leakage_40f_shift_auc.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| pool | pool_label | seed | block_size | n_train_normal | n_test_normal | auc_random_cv | auc_block_cv |
|---|---|---|---|---|---|---|---|
| base | 40f | 42 | 1000 | 51890 | 33832 | 0.8987 | 0.814 |

## Source: leakage_40f_validation_blocks.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| pool | pool_label | seed | validation | n_train | n_val | val_fpr | val_detection | test_fpr | test_detection | fpr_gap |
|---|---|---|---|---|---|---|---|---|---|---|
| base | 40f | 42 | random_validation | 90543 | 15979 | 0.1193 | 0.9631 | 0.2871 | 0.9597 | 0.1678 |
| base | 40f | 42 | block_validation | 84922 | 10400 | 0.2849 | 0.9692 | 0.2984 | 0.9653 | 0.0135 |
| base | 40f | 43 | random_validation | 90543 | 15979 | 0.1192 | 0.9634 | 0.2858 | 0.9584 | 0.1666 |
| base | 40f | 43 | block_validation | 85322 | 10800 | 0.1588 | 0.9681 | 0.3013 | 0.9632 | 0.1425 |
| base | 40f | 44 | random_validation | 90543 | 15979 | 0.1174 | 0.9635 | 0.2846 | 0.9597 | 0.1672 |
| base | 40f | 44 | block_validation | 84922 | 10400 | 0.0379 | 0.9538 | 0.2717 | 0.9565 | 0.2338 |
| base | 40f | 45 | random_validation | 90543 | 15979 | 0.1217 | 0.9652 | 0.2851 | 0.96 | 0.1634 |
| base | 40f | 45 | block_validation | 85322 | 10800 | 0.6026 | 0.9606 | 0.2929 | 0.963 | -0.3097 |
| base | 40f | 46 | random_validation | 90543 | 15979 | 0.1215 | 0.9633 | 0.2838 | 0.959 | 0.1623 |
| base | 40f | 46 | block_validation | 85322 | 10800 | 0.1695 | 0.9637 | 0.2824 | 0.9635 | 0.1129 |

## Source: leakage_40f_validation_blocks_b200.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| pool | pool_label | seed | validation | n_train | n_val | val_fpr | val_detection | test_fpr | test_detection | fpr_gap |
|---|---|---|---|---|---|---|---|---|---|---|
| base | 40f | 42 | random_validation | 90543 | 15979 | 0.1193 | 0.9631 | 0.2871 | 0.9597 | 0.1678 |
| base | 40f | 42 | block_validation | 77322 | 2800 | 0.2658 | 0.9613 | 0.2921 | 0.9625 | 0.0263 |
| base | 40f | 43 | random_validation | 90543 | 15979 | 0.1192 | 0.9634 | 0.2858 | 0.9584 | 0.1666 |
| base | 40f | 43 | block_validation | 76522 | 2000 | 0.3063 | 0.9582 | 0.3011 | 0.9605 | -0.0052 |
| base | 40f | 44 | random_validation | 90543 | 15979 | 0.1174 | 0.9635 | 0.2846 | 0.9597 | 0.1672 |
| base | 40f | 44 | block_validation | 76522 | 2000 | 0.1088 | 0.966 | 0.2885 | 0.9596 | 0.1797 |
| base | 40f | 45 | random_validation | 90543 | 15979 | 0.1217 | 0.9652 | 0.2851 | 0.96 | 0.1634 |
| base | 40f | 45 | block_validation | 76522 | 2000 | 0.2017 | 0.9623 | 0.3029 | 0.9597 | 0.1012 |
| base | 40f | 46 | random_validation | 90543 | 15979 | 0.1215 | 0.9633 | 0.2838 | 0.959 | 0.1623 |
| base | 40f | 46 | block_validation | 76322 | 1800 | 0.076 | 0.9656 | 0.2717 | 0.9542 | 0.1957 |

## Source: leakage_45f_shift_auc.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| pool | pool_label | seed | block_size | n_train_normal | n_test_normal | auc_random_cv | auc_block_cv |
|---|---|---|---|---|---|---|---|
| full_no_ttl | 45f | 42 | 1000 | 51890 | 33832 | 0.9291 | 0.8356 |

## Source: leakage_48f_shift_auc.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| pool | pool_label | seed | block_size | n_train_normal | n_test_normal | auc_random_cv | auc_block_cv |
|---|---|---|---|---|---|---|---|
| full | 48f | 42 | 1000 | 51890 | 33832 | 0.9296 | 0.8371 |

## Source: leakage_48f_validation_blocks.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| pool | pool_label | seed | validation | n_train | n_val | val_fpr | val_detection | test_fpr | test_detection | fpr_gap |
|---|---|---|---|---|---|---|---|---|---|---|
| full | 48f | 42 | random_validation | 90543 | 15979 | 0.1025 | 0.9684 | 0.2926 | 0.9675 | 0.1901 |
| full | 48f | 42 | block_validation | 84922 | 10400 | 0.2863 | 0.9777 | 0.3076 | 0.9787 | 0.0213 |
| full | 48f | 43 | random_validation | 90543 | 15979 | 0.0967 | 0.9689 | 0.2943 | 0.9708 | 0.1976 |
| full | 48f | 43 | block_validation | 85322 | 10800 | 0.1617 | 0.9718 | 0.3093 | 0.969 | 0.1476 |
| full | 48f | 44 | random_validation | 90543 | 15979 | 0.0978 | 0.9686 | 0.2955 | 0.9642 | 0.1977 |
| full | 48f | 44 | block_validation | 84922 | 10400 | 0.0312 | 0.9643 | 0.2791 | 0.9593 | 0.2479 |
| full | 48f | 45 | random_validation | 90543 | 15979 | 0.1019 | 0.97 | 0.2947 | 0.9695 | 0.1928 |
| full | 48f | 45 | block_validation | 85322 | 10800 | 0.5718 | 0.9664 | 0.2997 | 0.9616 | -0.2721 |
| full | 48f | 46 | random_validation | 90543 | 15979 | 0.099 | 0.9695 | 0.2894 | 0.9687 | 0.1904 |
| full | 48f | 46 | block_validation | 85322 | 10800 | 0.1608 | 0.9721 | 0.2939 | 0.969 | 0.1331 |

## Source: leakage_48f_validation_blocks_b200.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| pool | pool_label | seed | validation | n_train | n_val | val_fpr | val_detection | test_fpr | test_detection | fpr_gap |
|---|---|---|---|---|---|---|---|---|---|---|
| full | 48f | 42 | random_validation | 90543 | 15979 | 0.1025 | 0.9684 | 0.2926 | 0.9675 | 0.1901 |
| full | 48f | 42 | block_validation | 77322 | 2800 | 0.2425 | 0.9613 | 0.2991 | 0.9675 | 0.0566 |
| full | 48f | 43 | random_validation | 90543 | 15979 | 0.0967 | 0.9689 | 0.2943 | 0.9708 | 0.1976 |
| full | 48f | 43 | block_validation | 76522 | 2000 | 0.3095 | 0.9638 | 0.3084 | 0.9666 | -0.0011 |
| full | 48f | 44 | random_validation | 90543 | 15979 | 0.0978 | 0.9686 | 0.2955 | 0.9642 | 0.1977 |
| full | 48f | 44 | block_validation | 76522 | 2000 | 0.1148 | 0.9757 | 0.2959 | 0.9647 | 0.1811 |
| full | 48f | 45 | random_validation | 90543 | 15979 | 0.1019 | 0.97 | 0.2947 | 0.9695 | 0.1928 |
| full | 48f | 45 | block_validation | 76522 | 2000 | 0.1931 | 0.9528 | 0.3118 | 0.9712 | 0.1187 |
| full | 48f | 46 | random_validation | 90543 | 15979 | 0.099 | 0.9695 | 0.2894 | 0.9687 | 0.1904 |
| full | 48f | 46 | block_validation | 76322 | 1800 | 0.0668 | 0.9649 | 0.2845 | 0.9654 | 0.2177 |

## Source: pooled_reference_composition.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| protocol | part | source_file | rows | share_of_source_file | share_of_part |
|---|---|---|---|---|---|
| official | train | train | 90543 | 0.85 | 1 |
| official | train | test | 0 | 0 | 0 |
| official | val | train | 15979 | 0.15 | 1 |
| official | val | test | 0 | 0 | 0 |
| official | test | train | 0 | 0 | 0 |
| official | test | test | 54596 | 1 | 1 |
| pooled_random | train | train | 72546 | 0.681 | 0.6622 |
| pooled_random | train | test | 37013 | 0.6779 | 0.3378 |
| pooled_random | val | train | 12784 | 0.12 | 0.6612 |
| pooled_random | val | test | 6551 | 0.12 | 0.3388 |
| pooled_random | test | train | 21192 | 0.1989 | 0.6576 |
| pooled_random | test | test | 11032 | 0.2021 | 0.3424 |

## Source: normal_fpr_floor_40f_48f.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| pool | raw_columns | n_test_normal | within_test_attack_twin | within_test_forced | from_train_unseen | from_train_seen_attack_only | from_train_seen_attack_majority | from_train_seen_normal_majority |
|---|---|---|---|---|---|---|---|---|
| 40f | 34 | 33832 | 0.0288 | 0.0021 | 0.9263 | 0.0059 | 0.0291 | 0.0446 |
| 48f | 42 | 33832 | 0.0001 | 0 | 0.9951 | 0.0049 | 0.0049 | 0 |
