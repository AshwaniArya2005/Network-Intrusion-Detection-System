# Task 2.7 conclusion: can the zero-shot official-split false-positive rate be lowered? XGBoost

Official split, scheme `current`, flat model, seeds 42-46 (mean +/- std). Every selection used block-grouped validation (1,000-row blocks, 200-row gaps) or, for few-shot, the labelled sample. Protocol and the
rule for "clearly beats the baseline" were declared before any result (`results/task_2_7_protocol.md`). Primary metric: official-test FPR at about 95% detection with the threshold chosen on validation (`det95 FPR`).
Tables: `fpr_study_tuned_40f_45f_48f.md`, `fpr_study_prior_40f_45f_48f.md`, `fpr_study_self_40f_45f_48f.md`, `fpr_study_fewshot_48f_45f_41f.md`, `fpr_study_final_40f_45f_48f.md`.

## Result against the hypothesis
Hypothesis (a guess): zero-shot methods reach about 0.20-0.22, and 0.15 or below needs labels. **Zero-shot: not reached.** No zero-shot or transductive method lowered the det95 FPR by the declared 0.02 (the best mean paired
difference is -0.007); every pool stays at 0.244-0.259 against defaults of 0.256 / 0.248 / 0.248 (40 / 45 / 48 features). **Labels: confirmed, but at a larger budget than the earlier headline suggested**
(below). Nothing here changes the earlier statement that zero-shot FPR is about 0.24-0.25.

## Step 1 (ZERO-SHOT): re-tuning on block-grouped validation (40 trials per pool, regularised space)
| det95 FPR | 40 features | 45 features | 48 features |
|---|---|---|---|
| default | 0.256 +/- 0.010 | 0.248 +/- 0.012 | 0.248 +/- 0.011 |
| earlier tuned (random validation, attack AUC) | 0.252 +/- 0.014 | not run | 0.249 +/- 0.011 |
| tuned on block-grouped validation, attack AUC | 0.257 +/- 0.014 | 0.258 +/- 0.012 | 0.254 +/- 0.014 |
| tuned on block-grouped validation, macro F1 | 0.253 +/- 0.014 | 0.255 +/- 0.012 | 0.253 +/- 0.011 |
Caption. Stronger regularisation and selection on block-grouped validation do not lower the FPR: the mean paired differences are -0.004 to +0.010 and no variant is better in more than 4 of 5 seeds. The search itself found almost nothing to
improve on validation (best attack AUC 0.9630 against 0.9624 for the default at 40 features). The tuned models do change other things: accuracy rises by 0.01-0.02 at 40 and 48 features, ECE falls (0.093 -> 0.051 at 40,
0.115 -> 0.074 at 48), and max-softmax open-set detection rises on the 45 and 48-feature pools (0.34-0.35 -> 0.49-0.55), which is relevant to Task 4.5 but is not an FPR gain.

## Step 2 (TRANSDUCTIVE): temperature scaling and EM class-prior correction
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

## Step 3 (TRANSDUCTIVE, risky): self-training (two rounds, confidence 0.90, weight fraction 0.2)
| evaluation blocks (test) | 40 features | 45 features | 48 features |
|---|---|---|---|
| argmax FPR, zero-shot round 0 | 0.314 | 0.324 | 0.323 |
| argmax FPR, round 2 | 0.324 | 0.331 | 0.329 |
| lower in how many seeds | 0 of 5 | 0 of 5 | 0 of 5 |
| attack pseudo-labels that are really Normal, round 0 -> 1 | 0.089 -> 0.107 | 0.144 -> 0.176 | 0.140 -> 0.172 |
Caption. Self-training does not help and the confidently wrong Normal flows do reinforce the error: the share of attack pseudo-labels that are truly Normal and the share of Normal flows that receive an attack pseudo-label (0.041 -> 0.057 at 45 features)
both grow from round 0 to round 1. The det95 FPR is unchanged (0.271 -> 0.274 at 45 features). The validation check made before looking at the test blocks passes at 45 and 48 features and fails at 40, so it could not
catch this: validation rows come from the training distribution and carry no shift, which is the shift self-training would have to correct.

## Step 4 (FEW-SHOT): label budget and selection strategy (5 runs; rows from other time blocks, 200-row gaps)
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

## Step 5: the declared combination and the final table
Declared rule (chosen on each seed's validation rows only): the block-validation-tuned configuration if its validation attack AUC is at least the default's (used in 2 of 5 seeds on every pool), temperature scaling, and the EM correction only when its
validation gate passes (4 of 5 seeds on every pool, which makes those runs transductive).
| combination vs default | 40 features | 45 features | 48 features |
|---|---|---|---|
| det95 FPR | 0.254 +/- 0.015 vs 0.256 | 0.249 +/- 0.013 vs 0.248 | 0.247 +/- 0.013 vs 0.248 |
| argmax FPR | 0.226 vs 0.289 | 0.254 vs 0.299 | 0.254 vs 0.298 |
| macro F1 | 0.698 vs 0.712 | 0.698 vs 0.706 | 0.706 vs 0.712 |
Caption. Combining the pieces does not lower the FPR at a fixed detection; it only moves the argmax decision (lower argmax FPR, lower macro F1, much lower open-set detection when EM is used). The full table of every method with accuracy, macro F1, the three FPRs,
detection, ECE and open-set detection is `fpr_study_final_40f_45f_48f.md`.

## What did not work
Re-tuning on block-grouped validation, stronger regularisation, temperature scaling, class-prior correction (with or without test features), self-training, and their combination: none lowers the zero-shot det95 FPR (all within 0.007 of the default, below the
declared 0.02). Selecting the few-shot rows by uncertainty or diversity helps little at equal detection.

## One paragraph
The false-positive rate on the shifted official test split could not be lowered without labels: re-tuning, calibration, class-prior correction and self-training all leave the FPR at about 0.25 for a 95%-detection operating point, and the class-prior
diagnostic suggests the shift sits in the Normal flows themselves, not in how common each class is. Labelled rows from the same capture do lower it, but a budget of about 2,500-5,000 rows (5-9% of the test file) is needed to reach 0.15 at exactly 95% detection (the earlier
0.09 was read at 93% detection), the choice of which rows to label matters little, and nothing works on the pool without the window-count `ct_*` columns. These are within-capture results on one dataset; transfer to another capture was not tested.
