# Task 2.5 protocol (declared before any Task 2.5 result was produced)

Goal: characterise the official-split shift (Step A), then try to lower the official-split Normal false-positive rate
(Step B). Baseline numbers are those of Task 2 (commits ebef719 .. 32e9ae1); they are not re-litigated here.

## Access levels (every method is labelled with one)
- **ZERO-SHOT**: uses the training split (train + validation) only.
- **TRANSDUCTIVE**: additionally uses the unlabelled FEATURES of the official test file.
- **FEW-SHOT**: additionally uses k labelled rows drawn from the official test file. Those rows are excluded from
  evaluation. Each adapted result is reported next to the zero-shot result on the same evaluation rows.

## Selection rules
- The official test LABELS never choose a method, threshold or hyperparameter.
- Primary objective: **validation macro F1** (multiclass for the flat model; the 2-class macro F1 for the binary
  stage 1 of the hierarchical model). Validation attack-vs-normal AUC is recorded as a secondary criterion only.
- Zero-shot / transductive candidates are chosen on validation; the validation-chosen operating point is
  "95% detection" (det95) on 1 - P(Normal).
- Few-shot methods may use only the adaptation sample (never the rest of the test file) for choices.

## Declared settings
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
