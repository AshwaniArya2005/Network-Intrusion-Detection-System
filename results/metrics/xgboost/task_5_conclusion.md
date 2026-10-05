# Task 5 conclusion: are the explanations faithful and are the narratives correct? (novelty 2), XGBoost

Official split, scheme `current`, flat model, ZERO-SHOT, models trained as in Task 3 (block-grouped training / validation), seeds 42-46 (mean +/- std), pools 40 / 45 / 48 and the 30- and 15-feature tiers of each. Protocol, primary metrics and readings were declared
before any result (`results/task_5_protocol.md`). Tables: `xai_faithfulness_40f_45f_48f.md` (Steps 1-2), `xai_audit_40f_48f.md` (Steps 1 and 3, with the shift comparison), `dashboard_end_to_end_40f.csv` (Step 4), `results/task_5_human_audit_sheet.csv` (Step 5).
Explanation stability was measured in Task 3 and is not repeated.

## The claim for novelty 2
For the XGBoost model, the SHAP explanations are faithful to the model (removing the features the explanation names as most important changes the prediction far more than removing random ones, on shifted test flows as much as on validation flows), and the analyst narratives built from them
are correct in every mechanical respect we could test automatically: the label, the confidence, the cited features, the magnitude cues, the category names and the suggested action. What the narratives do not yet do reliably is tell the analyst something useful: between a third and a half of the cited features are described as
"typical", and a cue direction agrees with the model's general behaviour for that feature in only 72-76% of cases (36-49% for Overlap-Group-1). Faithful and correct do not make a prediction right: the narrative explains the model's decision, including a wrong one.

## Step 1: what the explanation computes
| check | result |
|---|---|
| SHAP additivity (sum of SHAP values + expected value against the raw margin of the predicted class) | maximum error 1.4e-5 over about 179,000 flows (nine configurations, 5 seeds, test and validation); no flow over the 1e-3 tolerance |
| Quoted confidence in the narrative against the model's probability of the predicted class | equal on all 2,000 audited narratives (one decimal), and the JSON `confidence` equals it to four decimals |
Caption. The numbers the dashboard prints are the model's own. The confidence is the raw (uncalibrated) probability: no calibrated score is shown in the backend or the frontend. On the official split the model's ECE is about 0.09-0.12, so "97.8% confidence"
is not a calibrated chance of being right.

## Step 2: faithfulness (deletion and insertion)
Sample: 300 flows per predicted class + 200 flagged-Unknown flows per model and source (about 2,000), seeded.
| primary metric: probability drop at k = 5, top SHAP minus random removal, official test | 40 features | 45 features | 48 features |
|---|---|---|---|
| whole pool | 0.512 +/- 0.012 | 0.501 +/- 0.023 | 0.553 +/- 0.011 |
| 30-feature tier | 0.466 +/- 0.011 | 0.429 +/- 0.014 | 0.489 +/- 0.007 |
| 15-feature tier | 0.333 +/- 0.011 | 0.344 +/- 0.012 | 0.340 +/- 0.026 |
| faithful under the declared reading (difference at least 0.05, interval above 0, all 5 seeds) | yes, yes, yes | yes, yes, yes | yes, yes, yes |
Caption. Removing the top-5 SHAP features (replacing them by the training median) lowers the predicted-class probability by about 0.62 and flips the predicted class in about 86% of flows; removing five random features lowers it by 0.18 (flips 28%) and
removing the five least important ones by 0.02 (flips 7%) (40 features). A second baseline (a random training row) gives the same picture (0.60 / 0.20 / 0.04). Insertion agrees: the top five features on the baseline vector recover the prediction (sufficiency 0.16-0.22) where five random features do not (0.56).
The effect falls with fewer features (0.33-0.34 at 15) as the remaining features carry redundant information. Per predicted class the difference is positive in every class, seed and interval, but varies: Generic 0.76-0.79 and Reconnaissance 0.55-0.59 are the most faithful, Fuzzers 0.26-0.39, Overlap-Group-1 0.26-0.39, flows flagged
Unknown 0.22-0.24 and Normal 0.18 (40 features), 0.26 (45) and 0.65 (48).
**Under the shift:** the same metric on official-test flows and on block-grouped validation flows is 0.512 / 0.513 (40), 0.501 / 0.495 (45) and 0.553 / 0.540 (48); test minus validation is within +/-0.013 for every configuration and the interval of the declared reading (below -0.05) is never met. We find no loss of faithfulness under the shift.

## Step 3: narrative audit through the dashboard path (2,000 narratives: 5 seeds x 200 flows x 2 pools; 25 per predicted class + 50 flagged Unknown)
| check | 40 features | 48 features |
|---|---|---|
| (a) every cited feature is a positive top-5 SHAP feature of the predicted class | 1.000 | 1.000 |
| (b) magnitude cue equals the cue for the z-score against the TRAINING mean / std (exact; direction) | 1.000; 1.000 | 1.000; 1.000 |
| (c) categorical features named by their category, no magnitude cue | 1.000 | 1.000 |
| (d) the suggested action matches the label (including the Overlap-Group-1 and Unknown texts) | 1.000 | 1.000 |
| (e) no false statement about the label | 1.000 | 1.000 |
| (f) the cue direction agrees with the sign of the SHAP-vs-value relation on training flows (determined cases) | 0.757 +/- 0.018 | 0.722 +/- 0.013 |
| share of cited numeric features read "typical" | 46.9% | 35.7% |
Caption. The two defects found earlier (a magnitude cue on a categorical feature; standardising twice) do not occur: (b) and (c) are 1.000 and the cue is computed in the right units. The narrative generator never misnames the prediction, including Overlap-Group-1 and Unknown flows. The
weaknesses are in what is said, not in whether it is true: (f) is 0.25-0.36 for Generic and Overlap-Group-1 on some pools (Overlap-Group-1 0.36 / 0.49, Generic 0.61 / 0.25, flows flagged Unknown 0.69 / 0.68; Normal 0.89, Reconnaissance 0.99-1.00). A typical failure is "reduced average packet size" cited as a reason for
Overlap-Group-1 although higher values usually push towards that class on training flows (rho 0.4-0.55); the cue describes the flow's value correctly and the SHAP value is positive for this flow, so the sentence is true locally but would mislead a reader who assumes "reduced" is the reason. 403 (40 features) and 622 (48 features) cited
features were listed as inconsistent, every one in check (f). "Typical" cues make up 36-47% of cited numeric features, and in 7.5% / 2.7% of the narratives no cited numeric feature carries any direction. A category of "-" (UNSW's "none") is printed as "network service=-".
**Under the shift:** on validation flows the same audit gives (a)-(e) = 1.000 and (f) = 0.788 / 0.731 against 0.757 / 0.722 on official-test flows (test minus validation -0.030 and -0.009), "typical" 47.9% / 36.3% against 46.9% / 35.7%. The shift does not change the narrative's correctness.

## Step 4: the dashboard end to end
The FastAPI `/predict` output for `data/samples/sample_flows.csv` (64 flows) matches an independent computation from the same saved artifact on every field for all 64 flows (prediction, confidence, Unknown flag, narrative, top SHAP features: 1.000 each). The frontend (Vite dev server and the API on localhost) was run: the
upload, the prediction table (64 rows, confidences equal to the API's) and the narrative panel work (`results/plots/xgboost/dashboard_prediction_explanation_view.png`; a full-page capture, the narrative sits below the table). The one difference found was in the pipeline's own check script: `scripts/check_explainability.py` passed the scaler's raw mean and scale together with already-standardised
values (the dashboard was fixed earlier, the script was not); both now use `standardised_value_statistics`, with a regression test (`tests/test_xai_audit.py`) and a test that the service and an independent computation agree on a freshly trained model (`tests/test_dashboard_end_to_end.py`). The saved model scores 42% on those 64 flows against their original labels (merged classes counted correct only when named
exactly), which shows the sample is hard, not that the pipeline differs.

## Step 5: human audit sheet
`results/task_5_human_audit_sheet.csv` (30 narratives: 4 per predicted class, 5 for Overlap-Group-1 and 5 for Unknown, with raw flow values, blank rating columns and no true label), `task_5_human_audit_key.csv` and `task_5_human_audit_instructions.md`. Nothing is rated or reported.

## What did not hold
- Not every narrative is informative: 36-47% of cited features read "typical", and for Overlap-Group-1 and Generic the cue direction often disagrees with the model's general behaviour for that feature (check f), although the text is locally true.
- Faithfulness is lowest for Normal flows on 40 features (0.18) and for flows flagged Unknown (0.22-0.24), and it falls to 0.33-0.34 with only 15 features; it is positive in every class, seed and interval.
- A faithful explanation of a wrong prediction is still wrong: nothing here tests whether the prediction is right, and the narrative quotes an uncalibrated confidence.
- The only code defect found (double standardisation in the check script) was fixed. We did not find a failure of the five mechanical checks in 2,000 narratives, so a 100% rate here is a statement about those checks, not about the usefulness of the text; the human sheet is for that.

## One paragraph
The explanations are faithful to the model: SHAP values add up to the model's output to within 1.4e-5, and removing the features they name as important changes the prediction far more than removing random features does (a difference of 0.50-0.55 in predicted-class probability at five features on the whole pools, in every seed and class, and 0.33 with only 15 features). The narratives are correct in every
way we can check automatically (the label, the confidence, the cited features, the cues in the right units, the category names and the suggested action, on all 2,000 audited narratives, and identical between the dashboard and the pipeline), and the official-split shift does not change any of this: faithfulness and the narrative checks are the same on shifted test flows as on validation flows. They fail
in a different way: a third to a half of the cited features are described as "typical", and a cue such as "reduced" often disagrees with how the model usually uses that feature (72-76% agreement overall, 36-49% for Overlap-Group-1), so a correct sentence can still mislead; and the confidence they quote is the model's uncalibrated probability on a split where the model's calibration is poor. Whether analysts find the narratives
understandable and actionable is not measured here; the 30-narrative sheet is ready for the team to rate.
