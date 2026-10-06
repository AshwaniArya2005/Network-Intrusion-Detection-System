# Task 4 protocol (declared before any Task 4 result was produced)

Novelty 1: open-set / zero-day detection. XGBoost, flat model (not the hierarchical scheme), official split, scheme `current`, ZERO-SHOT throughout
(training data only), seeds 42-46, mean and std.

## Data facts (after exact deduplication, both official files)
Zero-day flows with Worms and Shellcode held out: 1,627 (Shellcode 1,456 = 89.5%, Worms 171). Known classes in the official test file: Normal 33,832,
Exploits 7,590, Fuzzers 4,810, Generic 3,418, Reconnaissance 2,469, DoS 1,694, Analysis 438, Backdoor 345. One held-out class mix is not a general result;
Step 2 rotates the held-out class. The "67-75% detection at 26-28% false alarms" figure came from a threshold tuned on the zero-day samples and is withdrawn.

## Splits and thresholds
- Training / validation are block-grouped (1,000-row blocks, 200-row gaps; `block_validation_splits`). Zero-day flows are never in training or validation.
- The known validation flows are split in two halves by validation block: a **threshold half** (threshold for the declared **5% false-Unknown** target: a flow is
  Unknown when its score exceeds the 95th percentile of the known threshold-half scores) and a **calibration half** (conformal calibration, rank normalisation of the
  anomaly / combined scores). The halves are disjoint. Nothing about the zero-day flows or the official test labels enters any threshold or choice.
- The open-set wrapper does not change the closed-set prediction.

## Scores (higher = more likely Unknown), Step 1
- `msp` = 1 - max softmax (current); `entropy` = Shannon entropy of the class probabilities / ln K; `margin` = 1 - (top probability - second probability).
- `conformal` = 1 - the largest class-conditional (Mondrian) split-conformal p-value, p_k(x) = (#{calibration flows of class k with nonconformity >= 1 - p_k(x)} + 1) / (n_k + 1),
  nonconformity 1 - p(true class), calibration = the calibration half. A flow is Unknown exactly when its conformal prediction set is empty at the level the threshold implies.
  (The existing `results/diagnostics/conformal_prediction_sets.py` is a coverage diagnostic and is not reused for scoring.)
- `iforest` = isolation forest (200 trees) fitted on Normal TRAINING flows only (same scaled / encoded matrix as the classifier); score = -score_samples.
- Combinations of `iforest` with each confidence score s in {msp, entropy, margin, conformal}: both scores are mapped to their empirical-CDF rank on the calibration half;
  rule `mean` = average of the two ranks, rule `max` = larger rank. **The rule is chosen on validation** (below), per score, pool and seed.

## Choosing the rule and the "best" score without zero-day samples
Pseudo-unknown validation: for each of two declared known classes X in {Reconnaissance, Generic} (not members of the merged group, not Worms / Shellcode), an inner model is trained
on the block-grouped training rows without class X and scored on the validation flows: the validation rows of X are the pseudo-unknowns, the other known validation rows (threshold half) the
knowns. The AUROC of each candidate score, averaged over the two X, is the selection criterion. It picks (a) mean vs max per combination, and (b) the **best score of a pool** =
the candidate with the highest mean pseudo-unknown AUROC over the 5 seeds. That best score is used for Steps 2 and 3. The score that happens to be best on the real zero-day flows is
reported but never used for a choice.

## Step 1 metrics (pools 40, 45, 48)
Primary: **unknown AUROC** (official-test known flows vs zero-day flows) and **detection at the validation-chosen 5% threshold** (share of zero-day flows flagged Unknown).
Also: share of zero-day flows flagged Unknown or predicted as any attack class, per zero-day class (Worms, Shellcode), and the realised false-Unknown rate on the calibration
half of validation (held-out) and on the official test known flows (the gap is the cost of the shift).

## Step 2: leave-one-attack-class-out
Each of Analysis, Backdoor, DoS, Exploits, Fuzzers, Generic, Reconnaissance, Worms, Shellcode is held out in turn (its flows from both files are never trained on); retrain, threshold on
known block-grouped validation at 5%, test with that class as the zero-day. **Merged group:** the label scheme stays `current`; a held-out member of Overlap-Group-1 (Analysis, Backdoor, DoS) is removed from the
group's training rows while its siblings stay known and still form `Overlap-Group-1`. Most of those flows have exact twins among the known siblings (and Exploits), so low detection there is expected and is explained
by the twin share, not hidden by relabelling. As an extra row all three members are held out together ("Overlap-Group-1 as a unit"). Per class: AUROC, detection at 5%, share flagged Unknown
or predicted as any attack class; mean and worst class; the best score of the pool vs `msp`; and the known classes the false-Unknown alarms come from (validation and test). Pools 40 and 48.

## Step 3: alert-level FPR and the review queue
Alert = predicted as any attack class (open-set OFF) or predicted attack / flagged Unknown (open-set ON), on Normal flows of the official test. Confidence / abstain curve over the
false-Unknown targets {0.5, 1, 2, 3, 5, 7.5, 10, 15, 20, 30}% of the best score: confident-alert FPR (Normal called an attack and NOT flagged), review rate on Normal (Normal flagged Unknown), alert FPR
(attack or Unknown), zero-day catch (flagged or called an attack), known-attack alert rate. The operating point is the declared 5% target (chosen on validation only).

## Step 4: where the gain comes from (48 features)
Step 1 repeated, zero-day = Worms + Shellcode, on: 48 features minus the 7 window-count ct_* columns (ct_src_dport_ltm, ct_dst_sport_ltm, ct_srv_src, ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm; `full_no_ct_window`),
minus every ct_* column (`full_no_ct_any`), and the 30- and 15-feature tiers of the 48 pool (shared blockval rankings). Declared reading: the ct_* columns carry the open-set gain if removing the
window-count columns lowers the `msp` detection by at least half of the 40 -> 48 gap (confirm), by less than a quarter (reject), otherwise partial.

## Not claimed
Calibration under the official-split shift is poor, so confidence is not assumed reliable; the results are reported as measured. Teammates' model families are not run or quoted here.
