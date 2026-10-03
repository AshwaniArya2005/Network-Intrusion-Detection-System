# Task 2.5 conclusion: the official-split shift and the Normal false-positive rate

Numbers: `task_2_5_final_table_40f_48f.md` (all methods, access levels, 5 seeds/runs), `shift_conclusion_40f_45f_48f.md`
(Step A). Protocol and selection rules were declared before any result (`results/task_2_5_protocol.md`).
Target hypothesis (a guess): official-split FPR <= 0.15 at about 95% detection, from 0.24-0.25.

## Result against the target
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

## Side effects (reported favourable or not)
- Calibration: ECE falls with adaptation (48 features 0.109 -> 0.071 at k=5000 split; 40 features 0.088 -> 0.060).
- Open-set detection: unchanged on 48 features with few-shot (0.377 -> 0.375), higher on 40 (0.259 -> 0.277-0.299); it collapses
  with the hierarchical scheme.
- Accuracy rises with few-shot retraining (48 features 0.740 -> 0.796 at k=5000 split, 0.818 without a held-out threshold half).
- The combined few-shot + domain-weights variant adds nothing over few-shot alone.

## One paragraph
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
