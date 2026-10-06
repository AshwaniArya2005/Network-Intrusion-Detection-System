# Task 2.7 protocol (declared before any Task 2.7 result was produced)

Goal: lower the official-split Normal false-positive rate. XGBoost, flat model, scheme `current`, official split, seeds 42-46 (run i = model seed 42 + i), mean and std.
Pools: 40 (base), 45 (`full_no_ttl`), 48 (full); Step 4 uses 48, 45 and 41 (`full_no_ct_window`) so the `ct_*` dependence stays visible.
Capped at one session; if nothing clearly beats the baseline the result is reported as negative.

## Access levels
ZERO-SHOT = training data only. TRANSDUCTIVE = also the unlabelled official-test features. FEW-SHOT = also labelled official-test rows. Every table carries the access level and the
zero-shot baseline of the same pool and rows next to every adapted row.

## Selection data and baselines
- Every selection (hyperparameters, thresholds, temperature, rules, strategies) uses the **block-grouped validation split** (`block_validation_splits`, 1,000-row blocks, 200-row gaps,
  `data.val_size` 0.15, block draw seeded by the run's seed) or, for few-shot only, the declared labelled adaptation sample. Official-test labels are used only to report.
- Baseline = the default configuration (config.yaml, class-weight exponent 0.5) trained on the same block-grouped split, zero-shot, evaluated on the same rows. For reference Task 3 gave
  block-validated det95 FPR 0.257 / 0.248 / 0.247 (40 / 45 / 48 features).
- **Primary metric:** official-test FPR at about 95% detection with the threshold on 1 - P(Normal) chosen on block-grouped validation (`det95_test_fpr`; few-shot: chosen on the held-out half of the
  labelled sample). Also reported: argmax FPR, threshold-free FPR at 95% detection, detection at the chosen threshold, accuracy, macro F1, ECE (`evaluation.ece_bins`),
  open-set detection (max-softmax at the 5% false-Unknown threshold of Task 4, Worms + Shellcode held out).
- **"Clearly beats the baseline"** (declared now): the mean paired (same seed) difference in `det95_test_fpr` is at most -0.02, the method is better in at least 4 of 5 seeds, and its detection at the
  operating point is not more than 0.02 below the baseline's.

## Step 1 (ZERO-SHOT): re-tune on block-grouped validation
- 40 random trials per pool (40 / 45 / 48), search seed 42, selection on the seed-42 block-grouped validation split, early stopping 30 rounds on validation mlogloss, at most 1,000 trees. The default
  configuration is scored as a reference (not part of the budget).
- Regularised space (`tuning.space_regularised`): max_depth int [3, 7]; learning_rate loguniform [0.03, 0.3]; min_child_weight choice [5, 10, 20, 50, 100]; subsample uniform [0.6, 1.0];
  colsample_bytree uniform [0.5, 1.0]; reg_lambda loguniform [2, 100]; reg_alpha choice [0, 0.1, 1, 5]; class_weight_power uniform [0, 1].
- Objectives declared up front: validation attack-vs-normal AUC (**primary**, `blockval_tuned_auc`) and validation macro F1 (`blockval_tuned_f1`). n_estimators = best_iteration + 1; no early stopping at evaluation.
- Evaluated over the 5 seeds against the default and the earlier tuned models (`tuned_params_40f.json`, `tuned_params_48f.json`, selected on random validation; none exists for 45) on the same block-grouped
  splits. Files: `hyperparameter_search_blockval_<N>f.csv`, `tuned_params_blockval_<N>f.json`; the earlier files are not touched.

## Step 2 (TRANSDUCTIVE): class-prior correction
1. Temperature scaling: T in [0.25, 5] minimising the negative log-likelihood of the default model on the block-grouped validation split (scalar, `minimize_scalar` bounded); probabilities proportional to p^(1/T).
2. Reference prior pi_model = class shares of the training rows weighted by the sample weights actually used in training (the prior the model implies).
3. EM prior-shift estimate (Saerens et al. 2002) of the test class shares from the unlabelled test features: start at pi_model, iterate until the largest change is below 1e-6 or 100 iterations.
4. Correction p'(y|x) proportional to p_cal(y|x) * pi_hat(y) / pi_model(y). The same fixed transformation is applied to the validation probabilities, and the det95 threshold is chosen on the transformed validation scores.
5. Variants: `calibrated` (step 1 only), `calibrated_em` (1-4; TRANSDUCTIVE) and a ZERO-SHOT control `calibrated_valprior` (pi_hat = validation class shares, no test features), so the effect of undoing the class weighting is not mistaken for prior-shift correction.
6. Diagnostic only: estimated shares vs the true test shares (L1 distance); the true shares never enter a fit.
7. Validation gate for Step 5: on 5 simulated prior shifts of the validation set (class shares proportional to validation share * exp(z), z ~ N(0, 1), seeds 42-46, resampled with replacement), the EM estimate must have a mean
   L1 error below half of the L1 distance between pi_model and the simulated shares; otherwise EM is not used in the combination.

## Step 3 (TRANSDUCTIVE, risky): self-training
- Two rounds, confidence threshold tau = 0.90 on max-softmax, pseudo-labelled rows weighted to carry a fraction f = 0.2 of the total sample weight, rounds are not cumulative (round 2 re-labels from the round-1 model).
- The ordered official-test known rows are cut into blocks (`block_split`, 1,000 / 200, share 0.5 unlabelled, draw seed 1000 + run): pseudo-labels come from the unlabelled blocks, evaluation is on the other blocks
  (neighbourhood-disjoint), so no pseudo-labelled row is evaluated. Zero-shot baseline on the same evaluation rows.
- Validation check before test: the same procedure with half of the block-grouped validation blocks as the unlabelled set, scored on the other validation blocks; passes when macro F1 does not fall by more than 0.01 and
  argmax FPR does not rise by more than 0.01. The test run is made and reported either way.
- Reinforcement diagnostics (test labels used to REPORT only): share of pseudo-labelled flows that are wrong, share of true Normal flows that receive an attack pseudo-label, and the Normal flows called an attack by the round-0 / 1 / 2 models.

## Step 4 (FEW-SHOT): label budget and selection
- Budgets k = 100, 250, 500, 1,000, 2,500, 5,000. Strategies: `random` (uniform, labels unused), `entropy` (the k highest-entropy rows of the zero-shot model), `diverse` (rows nearest the centroids of k-means, k clusters, scaled preprocessed features,
  MiniBatchKMeans seed 0), `mix` (half entropy, half diverse). Selection uses only unlabelled features and the zero-shot model; labels are revealed for the chosen rows only.
- Candidates are the rows of the adaptation blocks (`block_split`, 1,000 / 200, share 0.4, draw seed 1000 + run); evaluation rows are the other blocks (200-row gaps). The chosen rows are split at random into two halves: one retrains the model
  (weight fraction 0.5), the other chooses the det95 threshold. 5 runs (model seed 42 + i with draw seed 1000 + i; the "5 draws x 5 seeds" are the same five runs, as in Tasks 2.5 / 2.6). Pools 48, 45, 41.
- Reported per strategy: FPR and detection vs k against the zero-shot baseline on the same rows, and the smallest k whose mean det95 FPR is at most 0.15, if any. The random-split figure is not used. The held-out-half FPR of each run is recorded for the Step 5 choice.

## Step 5: combination and final table
- Zero-shot recipe, chosen on validation only: the tuned configuration if its validation attack AUC is at least the default's (otherwise the default); temperature scaling always (ECE); the EM prior correction only if its validation gate (Step 2) passes;
  self-training only if its validation check (Step 3) passes. Few-shot: for each pool the strategy with the lowest mean held-out-half FPR at k = 1,000 (a rule that uses only the labelled sample), reported at every k.
- Final table per pool: method, access level, accuracy, macro F1, FPR (argmax, det95, threshold-free), detection, ECE, open-set detection, next to the defaults. Hypothesis (a guess, not a prediction): zero-shot methods reach about 0.20-0.22;
  0.15 or below needs labels.
- Output under `results/metrics/xgboost/` with the pool in the file name; earlier files are never overwritten; every new function has a test.
