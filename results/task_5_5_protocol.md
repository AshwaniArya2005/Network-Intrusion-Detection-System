# Task 5.5 protocol (declared before any Task 5.5 result was produced)

A more informative narrative and a faithfulness check on false-positive explanations. XGBoost, flat model, official split, scheme `current`, ZERO-SHOT, models trained as in Tasks 3 and 5 (block-grouped training / validation), seeds 42-46, pools 40 (base) and 48 (full), whole pool.
Nothing about the model or SHAP changes; only the sentence built from them. The existing generator stays: `narrative.style: classic` (the default, unchanged behaviour) or `class_relative`.

## The class-relative rule (the only rule that is evaluated; no variants are tried on the held-out sample)
For a flow predicted as class c, the narrative still cites the positive-SHAP features among the top 5 by absolute SHAP value of c (config `xai.top_k_features`), in that order. Then, per cited feature:
1. **Numeric feature.** Compute the classic cue from the z-score against the overall training mean / std. If the cue is "typical" (|z| < 0.3) the feature is **omitted**. Otherwise it is written as `<cue> <description> (<overall clause>; <class clause>)`:
   - overall clause: `higher than P% of all flows` when the cue is high (P = 100 x the share of ALL training flows with a strictly smaller value), `lower than P% of all flows` when the cue is low (P = 100 x the share with a strictly larger value);
   - class clause (only when the flow is not flagged Unknown, because a flow the system does not recognise is not described as a member of a class): with q25 / q75 the quartiles of the value among training flows of class c, `typical of <c> flows` when q25 <= value <= q75, else `higher than Q% of <c> flows` (value > q75; Q = 100 x the share of class-c training flows strictly below) or `lower than Q% of <c> flows` (value < q25; Q = 100 x the share strictly above). P and Q are rounded to whole percent.
2. **Categorical feature** (proto, service, state): `<description>=<category> (seen in A% of all flows; seen in B% of <c> flows)` with A / B the shares of all / class-c training flows with that category (the class part omitted for Unknown flows).
3. If no feature is left after omission the narrative says what the classic one says for no reasons ("No single feature dominated the decision; the pattern was diffuse across many features.").
The first sentence, the suggested action and everything else are unchanged. **Calibrated confidence (class_relative style only):** after the first sentence, `Calibrated estimate: about X% (the model's raw probability tends to be too high on new traffic; treat both numbers as estimates, not guarantees).`, with
X = 100 x the predicted-class probability after temperature scaling (T in [0.25, 5] fitted by negative log-likelihood on the block-grouped validation split of the model, as in Task 4.5); the raw value is kept in the first sentence. ECE (15 bins) of the raw and calibrated probabilities on the known official-test flows is reported per seed.
Percentiles and quartiles come from 1,001 quantile grid points per feature (all training flows and each class's flows), saved with the model (`class_reference_<set>.npz`, no pickle).

## Development and evaluation discipline
- The rule above is fixed. It is developed and inspected only on a sample of **block-grouped validation flows** (training file) of model seed 42, pool 40; any change after that inspection is limited to correctness defects (a wrong number or a broken sentence), is listed in the report, and is never made to move a metric.
- It is then evaluated **once** on a fresh official-test sample drawn with sampling seed 5000 + the model seed (Task 5 used the model seed itself, so the flows differ): per model 25 flows for each of the six predicted classes, 50 flagged-Unknown flows and 30 **false-positive Normal flows** (true Normal flows predicted as an attack and not flagged Unknown, drawn from the whole test file and
  excluded from the class strata), 230 flows, through the dashboard's `PredictionService` once with each style (the two services load the same saved artifacts).

## Step 1 primary metrics (held-out sample, pools 40 and 48, overall and per predicted class, classic against class-relative)
1. The share of cited numeric features that read "typical", and the number of features cited per narrative (mean; share of narratives that cite no numeric feature).
2. The cue-direction agreement (f), definition unchanged from Task 5 (sign of the Spearman correlation between the value and the SHAP value of the predicted class on 3,000 training rows against the cue direction; |rho| < 0.10 = no monotone relation; "typical" = no direction claimed).
3. Checks (a)-(e) as in Task 5, which must stay at 1.000; and a new check **(g)** on the new content: the percentages and the interquartile statement in every clause equal an independent computation from the raw training frame (tolerance 1 percentage point; the interquartile statement exact), and the categorical shares likewise. Also the quoted raw confidence is unchanged and the calibrated number
   equals 100 x the temperature-scaled probability (1 percentage point).

## Step 2: false-positive explanations (official test, pools 40 and 48, 5 seeds)
Groups, 300 flows each per model (all of them when fewer): **FP-attack** (true Normal predicted as any attack class), **FP-Fuzzers** (true Normal predicted as Fuzzers), **TN** (true Normal predicted Normal) and **TP-Fuzzers** (true Fuzzers predicted Fuzzers); flows flagged Unknown are included in their group and counted.
- (a) Deletion faithfulness as in Task 5: top-SHAP minus random removal of 5 features, median baseline (and a random training row), probability drop and flip rate, bootstrap interval over flows per seed; declared reading as in Task 5 (at least 0.05 with the interval above 0 in all 5 seeds).
- (b) The features the narratives cite per group (classic: the positive top-5 features; class-relative: the numeric ones that survive the omission rule) with the share of narratives citing each.
- (c) Raw and calibrated confidence: mean, share at or above 0.90, share flagged Unknown; and whether anything separates a false positive from a correct flow: AUROC (positive = FP-Fuzzers, negative = TP-Fuzzers, and FP-attack against TN) of the raw confidence (1 - confidence), of the calibrated confidence and of the **class-atypicality** of the narrative = the share of its cited numeric features that lie outside the predicted class's interquartile range (computed from the same reference the narrative uses).
- A plain-language reading of whether an analyst would get a usable reason to doubt a false positive is given from these numbers only; no human result is claimed.

## Step 3: A/B sheet
30 flows stratified over the predicted classes, Unknown and false-positive Normal (5 each for six strata of the held-out sample, pool 40, model seed 42), classic and class-relative narrative side by side in a seeded random order (which column is which is only in a separate key file), blank columns to choose the clearer and the more actionable one. Not filled in, no rating reported.

## Not claimed
Faithful to the model, not to the truth. The calibration is on this split's validation flows and does not fix the shift. No human study.
