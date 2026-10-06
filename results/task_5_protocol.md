# Task 5 protocol (declared before any Task 5 result was produced)

Novelty 2: human-centered, actionable explanations. XGBoost, flat model, official split, scheme `current`, ZERO-SHOT throughout. Models are trained exactly as in Task 3 (block-grouped training / validation split of the training file,
seed 42-46 for the split and the model; `pipelines/run_tier_study.prepare`), pools 40 (base), 45 (`full_no_ttl`) and 48 (full), and the 30- and 15-feature mutual-information tiers of each pool (shared blockval rankings), i.e. nine configurations x 5 seeds.
Mean and std over seeds. Explanation stability is not repeated (Task 3). Nothing is selected on the official-test labels; the test labels are used only to report.

## Samples (stratified, seeded; rule and size stated here)
- A flow's stratum is its predicted class (6 classes: Normal, Overlap-Group-1, Exploits, Fuzzers, Generic, Reconnaissance) or **Unknown** when the open-set rule flags it (max-softmax below the 5% false-Unknown threshold fixed on the block-grouped validation split, the
  threshold the dashboard uses).
- **Faithfulness sample (Step 2):** 300 flows per predicted class (all of them when a class has fewer) + 200 flows flagged Unknown, about 2,000 flows, drawn with `numpy.random.default_rng(seed)` without replacement. Official-test candidates are the known test flows plus the zero-day flows
  (Worms, Shellcode), because the dashboard would receive both. A second sample of the same size is drawn from the block-grouped validation flows (training file, never seen by the model, no zero-day flows) for the shift comparison.
- **Narrative-audit sample (Step 3):** per model 25 flows per predicted class (6 x 25) + 50 flagged-Unknown flows = 200 flows from the same official-test candidates; seeds 42-46, pools 40 and 48 (tier = the whole pool, which is what the dashboard serves); 2,000 narratives in total.

## Step 1: what the explanation computes
- **SHAP additivity.** For every flow of the Step 2 sample (every model, 5 seeds): |sum of the SHAP values of the predicted class + the explainer's expected value - the model's raw margin (`output_margin=True`) for that class|. Declared tolerance: 1e-3 (float32 trees). Report the
  maximum error and any failures.
- **Quoted confidence.** For every audit-sample flow through the dashboard path: the percentage printed in the narrative (one decimal) equals `100 x` the model's predicted probability of the predicted class rounded to one decimal, and the `confidence` field equals that probability rounded to four decimals. No calibrated
  score is shown anywhere in the backend or the frontend (only `confidence`); this is stated, not tested.

## Step 2: faithfulness (deletion and insertion)
- For each flow, SHAP values of the predicted class (TreeExplainer, the repository's `SHAPExplainer`). "Top" = the k features with the largest (signed) SHAP value for the predicted class; "least important" = the k features with the smallest absolute SHAP value; "random" = k features
  drawn uniformly (one draw per flow). k = 1, 3, 5, 10.
- **Deletion:** the chosen features of the flow are replaced by a baseline; record the drop in the predicted-class probability and whether the predicted class flips. Baseline 1: the training median of the feature in the model's input space (the training mode for the three categorical features
  proto, service, state). Baseline 2: the feature values of one random training row (one row per flow). **Insertion:** start from the baseline vector (the whole row replaced) and insert the chosen features of the flow; record the predicted-class probability.
  Comprehensiveness = the deletion drop of the top features; sufficiency = the original probability minus the insertion probability of the top features (lower = the top features alone suffice).
- **Primary metric (declared now):** the mean probability drop at k = 5 for top-SHAP removal minus random removal (median baseline), with a 95% bootstrap interval over flows (1,000 resamples, per seed); headline = mean over the 5 seeds. Declared reading: the explanation is **faithful** for a configuration when
  the difference is at least 0.05 and its interval excludes 0 in all 5 seeds. Also reported per predicted class (including Unknown) for the three whole pools, and for the 30- and 15-feature tiers.
- **Shift check:** the same metric on the validation sample and on the official-test sample of the same model; the declared reading of "faithfulness is lost under the shift" is a test-minus-validation difference below -0.05 with a bootstrap interval excluding 0.

## Step 3: narrative audit (the dashboard path)
The narratives are produced by `dashboard.backend.prediction_service.PredictionService.predict` on a model trained in step order and saved to a scratch directory (the service loads the saved artifacts exactly as the dashboard does), not by a re-implementation. The reference quantities come from independent computations
(a separate `shap.TreeExplainer`, the training frame's own mean and standard deviation). Cited features are parsed from the "Main reasons" list by the longest matching feature description. Rates, overall and per predicted class, mean +/- std over the 5 seeds; a check below 95% is treated as a defect to fix.
- (a) every cited feature is among the positive-SHAP features of the top 5 (config `xai.top_k_features`) by absolute SHAP of the predicted class;
- (b) the magnitude / direction cue equals the cue `_magnitude_phrase` gives for the z-score of the flow's value relative to the TRAINING mean and standard deviation, computed from the raw engineered values of the training frame (tolerance 1e-6 at the thresholds); reported both as an exact match and as a direction match
  (high / low / typical);
- (c) categorical features (proto, service, state) are named by the flow's actual category and carry no magnitude cue;
- (d) the suggested action equals the configured action of the predicted label ("Unknown" when flagged, including the Overlap-Group-1 text);
- (e) the narrative makes no false statement about the label: the label it names equals the prediction ("an unrecognized (potential zero-day) pattern" exactly when the flow is flagged Unknown), and any other class name it mentions is licensed (the members of the predicted merged group).
- (f) **directional consistency:** for each cited non-categorical feature with a magnitude cue, the sign of the Spearman correlation between the feature value and the SHAP value of the predicted class on a seeded sample of 3,000 training rows must agree with the cue direction (high cue: positive; low cue: negative). A cited feature with |rho| < 0.10 is counted
  as "no monotone relation" and reported separately, a "typical" cue as "no direction claimed".
Every failure is listed (flow, narrative, check, reason) in a CSV.

## Step 4: dashboard end to end
The FastAPI app (`dashboard.backend.main:app`) is called with `data/samples/sample_flows.csv` through the framework's own test client (the same request path as uvicorn). Its narratives, confidences and top SHAP features are compared row by row with an independent computation from the same saved artifact
(model.predict_proba, a separate SHAPExplainer, a separate NarrativeGenerator call); they must match exactly. Differences are fixed at their cause with a regression test. `scripts/check_explainability.py` (the pipeline's own check) is compared as well. If the frontend can be started, one screenshot of
the prediction and explanation view is taken; otherwise the report says the frontend was not run.

## Step 5 (small): human audit sheet
`results/task_5_human_audit_sheet.csv`: 30 narratives stratified over the predicted classes and Unknown, with blank rating columns (understandable, actionable, agrees with the rater's judgement of the flow). It is a template only; no rating is filled in or reported.

## Not claimed
The explanations describe the model, not the traffic: a faithful explanation of a wrong prediction is still a wrong prediction. Teammates' model families are not run or quoted here.
