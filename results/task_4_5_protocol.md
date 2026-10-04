# Task 4.5 protocol (declared before any Task 4.5 result was produced)

Goal: improve zero-day (open-set) detection. XGBoost, flat model, official split, scheme `current`, ZERO-SHOT throughout, seeds 42-46 (mean and std), pools 40 (base) and 48 (full).
Everything of Task 4 that is not changed stays: block-grouped validation (1,000-row blocks, 200-row gaps) split into a THRESHOLD half and a CALIBRATION half by whole blocks; a flow is flagged
Unknown when its score exceeds the 95th percentile of the known threshold-half scores (5% false-Unknown target); no zero-day flow and no official-test label ever enters a threshold, a fit,
a parameter or a choice (`results/task_4_protocol.md`). Evaluation sets are the same as Task 4: Worms + Shellcode (the Step 1 setting), the nine-class leave-one-class-out rotation, and the
Overlap-Group-1 trio held out together (merged-group handling as in Task 4).

## Baselines and the declared success rule
Baselines, rerun in the same pass: max-softmax (`msp`) and `entropy`. A score **clearly beats** max-softmax when (all three) the rotation-mean detection (nine classes) is at least 0.05 higher, the
rotation-mean AUROC is not lower, and the mean paired (same seed) rotation detection difference is positive in at least 4 of 5 seeds; and its Worms + Shellcode detection is not more than 0.02 below
max-softmax's. Hypothesis (a guess): rotation-mean detection rises from about 0.21 to 0.30-0.35. If nothing clears the rule the result is reported as negative.

## Scores (higher = more likely Unknown) and their declared parameters
1. **Calibration.** Temperature T in [0.25, 5] fitted on the CALIBRATION half of the validation rows by negative log-likelihood; `msp_cal` and `entropy_cal` on p^(1/T) renormalised. ECE (15 bins) on the known
   test flows is reported before and after.
2. **Per-class thresholds** (`msp_pc`, `entropy_pc`). For each predicted class c the threshold is the 95th percentile of the known threshold-half scores of the flows predicted c (allocation rule: the same 5%
   false-Unknown rate inside every predicted class, so the overall rate is 5% by construction); a predicted class with fewer than 30 threshold-half flows uses the global threshold. The AUROC of this rule is
   computed on the shifted score (score minus the threshold of the flow's predicted class); the review-queue curve uses, for each target, the (1 - target) percentile within each predicted class.
3. **Ensemble disagreement** (M = 5): the main model plus 4 members with seeds seed + 100 j (j = 1..4), subsample 0.7, colsample_bytree 0.7, 150 trees, learning rate 0.2, depth and regularisation as the main model,
   same class weights, same preprocessing. Scores: `ens_mi` = predictive mutual information, entropy of the mean probability minus the mean member entropy; `ens_var` = mean over classes of the variance across
   members of the class probability; `ens_msp` = 1 - max of the mean probability.
4. **Distance to the training data** in the scaled feature matrix the classifier sees. `knn` = mean distance to the k = 10 nearest neighbours among 20,000 training rows (uniform sample, seeded); `maha` = the
   minimum over the known training classes of the Mahalanobis distance (class mean, class covariance plus a ridge of 0.01 x the mean variance). Scores are computed for validation, test and zero-day flows.
5. **Pseudo-unknown training (outlier exposure).** An extra class "Unknown" is made from two known classes P held out inside the training split: P = the first two of (Reconnaissance, Generic, Fuzzers, Exploits)
   that are not the evaluation's held-out class and not a member of a held-out trio. The model is trained on the other known classes plus Unknown; scores: `oe_pu` = predicted probability of Unknown, `oe_msp` =
   1 - max probability. P flows are removed from the known validation and test sets of this comparison (they are Unknown by construction), and the comparison baseline is a closed-set model trained without P
   (`noP_msp`, `noP_entropy`) on the same known flows. The cost to known-class recall is reported: macro recall over the remaining known classes of the Unknown-class model (a flow predicted Unknown counts as missed)
   against the model trained without P, and the attack classes in P can no longer be recognised.
6. **Combination.** Rank-average (`mean` of the empirical-CDF ranks fitted on the calibration half) of the two individual scores with the highest mean pseudo-unknown validation AUROC among
   {msp, entropy, msp_cal, entropy_cal, ens_mi, ens_var, ens_msp, knn, maha, oe_pu}. The selection uses the Task 4 pseudo-unknown validation (inner models trained without Reconnaissance or Generic; the
   validation flows of the held-out class are the pseudo-unknowns, the other known threshold-half flows the knowns; for the Unknown-class model P excludes the inner held-out class by the same rule), averaged
   over the 5 seeds and the two inner classes, once per pool. The real zero-day classes and the rotation are never used to choose.

## Isolation-forest check (diagnostic)
Using the Task 4 score (isolation forest on Normal training flows, score = minus `score_samples`, higher = more anomalous) on the official test: AUROC of the score for known attacks (positive) against known Normal
flows; the mean percentile of Worms and Shellcode scores among the known test scores (above 50% = the zero-day flows look more anomalous than a typical known flow); the same two numbers for `knn` and `maha`.

## Reporting (per idea and for the combination)
- Per held-out class (rotation, trio, Worms + Shellcode): unknown AUROC, detection at the 5% target, realised false-Unknown rate on the two validation halves and on the official test, share flagged Unknown or
  predicted as an attack class. Diagnostic column, never used for selection: detection at the threshold that gives the SAME realised test false-Unknown rate as `msp` in the same run.
- Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out, 5% threshold): counts of Shellcode, Worms, each known attack class and Normal, and the precision of Unknown (zero-day
  share of the flagged flows).
- Effect on alert FPR and the review queue (Task 4 Step 3 measures): alert FPR with the wrapper off / on, confident-alert FPR, review rate on Normal, zero-day catch, at the 5% target and over the target curve.
- Output under `results/metrics/xgboost/` with the pool in the file name, never overwriting earlier files; each new function has a test; each idea is its own commit (`--idea calibration|perclass|ensemble|distance|oe|combo`).
- One claim for novelty 1 and the protocol behind it; `task_4_conclusion.md`, README.md and PROJECT_PLAN.md are updated only for facts established here. Then stop and wait before Task 5.
