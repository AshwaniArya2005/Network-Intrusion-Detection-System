# Novelty 2: faithful, human-centred explanations

Faithfulness, narrative audit, class-relative narratives and false-positive explanations: conclusions, tables and the declared protocols. The blank rating sheet is `narratives_ab_sheet.csv` (with its key and instructions); the 30-narrative human-audit template mentioned in the conclusion was removed (rebuild it with `scripts/make_human_audit_sheet.py`, or recover it from git tag `pre-lean-2026-10`); samples are `xai_audit_40f_narratives.csv`, `xai_audit_40f_example_failures.csv` and `narrative_test_40f_narratives.csv`.

File names mentioned inside this file (for example `cross_dataset_tables.md`, `results/explanations_protocol.md` or `xai_audit_40f_example_failures.csv`) are the `Source:` sections of this file or of one of the other numbered files, or files that were removed in the cleanup and are recoverable from the git tags `pre-cleanup-2026-10` and `pre-lean-2026-10`. Text under a `Source:` heading is the original file, unchanged except that its headings are demoted two levels. The dashboard screenshot mentioned in the explanation conclusion (`dashboard_prediction_explanation_view.png`) was removed. Two kinds of file moved after the originals were written: the feature rankings are now in `results/rankings/` and the A/B rating sheet, key and instructions in `results/rating/`.

## Source: explanations_conclusion.md

### Explanation study conclusion: are the explanations faithful and are the narratives correct? (novelty 2), XGBoost

Official split, scheme `current`, flat model, ZERO-SHOT, models trained as in the feature-tier study (block-grouped training / validation), seeds 42-46 (mean +/- std), pools 40 / 45 / 48 and the 30- and 15-feature tiers of each. Protocol, primary metrics and readings were declared
before any result (`results/explanations_protocol.md`). Tables: `explanations_tables.md` (sections `xai_faithfulness_40f_45f_48f.md` for Steps 1-2 and `xai_audit_40f_48f.md` for Steps 1 and 3, with the shift comparison; a 1,000-narrative sample `xai_audit_40f_narratives.csv` and ten example failures `xai_audit_40f_example_failures.csv`), `dashboard_end_to_end_40f.csv` (Step 4), `results/explanations_human_audit_sheet.csv` (Step 5).
Explanation stability was measured in the feature-tier study and is not repeated.

#### The claim for novelty 2
For the XGBoost model, the SHAP explanations are faithful to the model (removing the features the explanation names as most important changes the prediction far more than removing random ones, on shifted test flows as much as on validation flows), and the analyst narratives built from them
are correct in every mechanical respect we could test automatically: the label, the confidence, the cited features, the magnitude cues, the category names and the suggested action. What the narratives do not yet do reliably is tell the analyst something useful: between a third and a half of the cited features are described as
"typical", and a cue direction agrees with the model's general behaviour for that feature in only 72-76% of cases (36-49% for Overlap-Group-1). Faithful and correct do not make a prediction right: the narrative explains the model's decision, including a wrong one.

#### Step 1: what the explanation computes
| check | result |
|---|---|
| SHAP additivity (sum of SHAP values + expected value against the raw margin of the predicted class) | maximum error 1.4e-5 over about 179,000 flows (nine configurations, 5 seeds, test and validation); no flow over the 1e-3 tolerance |
| Quoted confidence in the narrative against the model's probability of the predicted class | equal on all 2,000 audited narratives (one decimal), and the JSON `confidence` equals it to four decimals |
Caption. The numbers the dashboard prints are the model's own. The confidence is the raw (uncalibrated) probability: no calibrated score is shown in the backend or the frontend. On the official split the model's ECE is about 0.09-0.12, so "97.8% confidence"
is not a calibrated chance of being right.

#### Step 2: faithfulness (deletion and insertion)
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

#### Step 3: narrative audit through the dashboard path (2,000 narratives: 5 seeds x 200 flows x 2 pools; 25 per predicted class + 50 flagged Unknown)
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
Overlap-Group-1 although higher values usually push towards that class on training flows (rho 0.4-0.55; ten examples, with the narrative text, are in `xai_audit_40f_example_failures.csv`: its `reason` column was written by a failure-list template that always read "falls as the value rises" whatever the sign of rho; the template is fixed in the code (`shap_trend_phrase`), but this committed file keeps the old wording, so read the `shap_trend_on_training_rows` column, which states the real sign); the cue describes the flow's value correctly and the SHAP value is positive for this flow, so the sentence is true locally but would mislead a reader who assumes "reduced" is the reason. 403 (40 features) and 622 (48 features) cited
features were listed as inconsistent, every one in check (f). "Typical" cues make up 36-47% of cited numeric features, and in 7.5% / 2.7% of the narratives no cited numeric feature carries any direction. A category of "-" (UNSW's "none") is printed as "network service=-".
**Under the shift:** on validation flows the same audit gives (a)-(e) = 1.000 and (f) = 0.788 / 0.731 against 0.757 / 0.722 on official-test flows (test minus validation -0.030 and -0.009), "typical" 47.9% / 36.3% against 46.9% / 35.7%. The shift does not change the narrative's correctness.

#### Step 4: the dashboard end to end
The FastAPI `/predict` output for `data/samples/sample_flows.csv` (64 flows) matches an independent computation from the same saved artifact on every field for all 64 flows (prediction, confidence, Unknown flag, narrative, top SHAP features: 1.000 each). The frontend (Vite dev server and the API on localhost) was run: the
upload, the prediction table (64 rows, confidences equal to the API's) and the narrative panel work (`results/plots/xgboost/dashboard_prediction_explanation_view.png`; a full-page capture, the narrative sits below the table). The one difference found was in the pipeline's own check script: `scripts/check_explainability.py` passed the scaler's raw mean and scale together with already-standardised
values (the dashboard was fixed earlier, the script was not); both now use `standardised_value_statistics`, with a regression test (`tests/test_xai_audit.py`) and a test that the service and an independent computation agree on a freshly trained model (`tests/test_dashboard_end_to_end.py`). The saved model scores 42% on those 64 flows against their original labels (merged classes counted correct only when named
exactly), which shows the sample is hard, not that the pipeline differs.

#### Step 5: human audit sheet
`results/explanations_human_audit_sheet.csv` (30 narratives: 4 per predicted class, 5 for Overlap-Group-1 and 5 for Unknown, with raw flow values, blank rating columns and no true label), `explanations_human_audit_key.csv` and `explanations_human_audit_instructions.md`. Nothing is rated or reported.

#### What did not hold
- Not every narrative is informative: 36-47% of cited features read "typical", and for Overlap-Group-1 and Generic the cue direction often disagrees with the model's general behaviour for that feature (check f), although the text is locally true.
- Faithfulness is lowest for Normal flows on 40 features (0.18) and for flows flagged Unknown (0.22-0.24), and it falls to 0.33-0.34 with only 15 features; it is positive in every class, seed and interval.
- A faithful explanation of a wrong prediction is still wrong: nothing here tests whether the prediction is right, and the narrative quotes an uncalibrated confidence.
- The only code defect found (double standardisation in the check script) was fixed. We did not find a failure of the five mechanical checks in 2,000 narratives, so a 100% rate here is a statement about those checks, not about the usefulness of the text; the human sheet is for that.

#### One paragraph
The explanations are faithful to the model: SHAP values add up to the model's output to within 1.4e-5, and removing the features they name as important changes the prediction far more than removing random features does (a difference of 0.50-0.55 in predicted-class probability at five features on the whole pools, in every seed and class, and 0.33 with only 15 features). The narratives are correct in every
way we can check automatically (the label, the confidence, the cited features, the cues in the right units, the category names and the suggested action, on all 2,000 audited narratives, and identical between the dashboard and the pipeline), and the official-split shift does not change any of this: faithfulness and the narrative checks are the same on shifted test flows as on validation flows. They fail
in a different way: a third to a half of the cited features are described as "typical", and a cue such as "reduced" often disagrees with how the model usually uses that feature (72-76% agreement overall, 36-49% for Overlap-Group-1), so a correct sentence can still mislead; and the confidence they quote is the model's uncalibrated probability on a split where the model's calibration is poor. Whether analysts find the narratives
understandable and actionable is not measured here; the 30-narrative sheet is ready for the team to rate.

---

### Narrative study: a more informative narrative, and the explanations of false positives (novelty 2)

Official split, XGBoost, ZERO-SHOT, seeds 42-46, pools 40 and 48, models trained as in the explanation study. Protocol, rule and primary metrics were declared before any result (`results/narratives_protocol.md`). The rule was inspected only on block-grouped validation flows (model seed 42, 40 features) and
**not changed** after that inspection; it was then evaluated once on a fresh official-test sample (sampling seed 5000 + the model seed, so the flows differ from the explanation study's). Tables: `explanations_tables.md` (sections `narrative_test_40f_48f.md` for Step 1 and `narrative_falsepos_40f_48f.md` for Step 2), `results/narratives_ab_sheet.csv` (Step 3).
The classic generator is kept (`narrative.style: classic`, the default); `class_relative` is switched on in `configs/config.yaml`.

#### The updated claim for novelty 2
The narratives can be made shorter and less filled with uninformative statements without losing correctness: features that read "typical" are no longer cited, the others say where the value sits among all training flows and among flows of the predicted class, and a calibrated confidence appears next
to the raw one. This removes every "typical" reason and cuts the cited features from about 4 to about 2.6 per narrative with every correctness check still at 1.000. It does **not** make the narrative a better guide to when the model is wrong: for false-positive Normal flows the explanation is as faithful to the
model as for true attacks, but it reads like the explanation of a true attack, and only the (weak) confidence number differs. All of this is about faithfulness to the model, not to the truth; the confidence is not calibrated on this split even after temperature scaling; no human has rated either narrative.

#### Step 1: class-relative narrative, held-out official-test sample (230 flows per model and style: 25 per predicted class, 50 flagged Unknown, 30 false-positive Normal)
| metric (mean over 5 seeds) | 40 features: classic | 40: class-relative | 48 features: classic | 48: class-relative |
|---|---|---|---|---|
| cited numeric features that read "typical" (primary 1) | 45.2% | **0** | 36.5% | **0** |
| features cited per narrative (numeric + categorical) | 4.11 | 2.56 | 4.02 | 2.71 |
| numeric features cited per narrative | 3.43 | 1.88 | 3.57 | 2.26 |
| narratives that cite no numeric feature | 0.4% | 7.3% | 0.1% | 4.0% |
| cue-direction agreement (f), definition unchanged (primary 2) | 0.780 | 0.780 | 0.733 | 0.733 |
| checks (a)-(e) (primary 3) | 1.000 | 1.000 | 1.000 | 1.000 |
| (g) every clause equals an independent computation from the training flows | n/a | 1.000 | n/a | 1.000 |
| the calibrated number equals the temperature-scaled probability | n/a | 1.000 | n/a | 1.000 |
| ECE of the known official-test flows, raw -> calibrated (temperature 1.18 / 1.26) | 0.093 -> 0.070 | | 0.115 -> 0.086 | |
Caption. The "typical" share falls to zero by construction, so the informative numbers are the others: a third to two fifths fewer cited features (33-38%), and a few narratives (4-7%) are left with no numeric feature and name only categorical features or say the pattern was diffuse. Checks (a)-(e) are unchanged (the narrative is built from the same top SHAP features) and the new clauses are
all correct against an independent computation (percent of all flows, percent of the class's flows, the interquartile statement and the category shares). The cue-direction agreement (f) does not move because the cue is the same; it stays low for Overlap-Group-1 (0.44 / 0.55) and, on 48 features, Generic (0.26) (per predicted class in the table file). Temperature scaling lowers the ECE by 0.02-0.03 but not
to zero: the calibrated estimate is still too high on shifted flows, it reads "about 100%" in 18% of the narratives (raw 100% in about a quarter), and the caution in the sentence ("treat both numbers as estimates, not guarantees") is the only guard against reading it as certainty. Whether a reader finds the class-relative clauses clearer is not measured (Step 3 is the template for that).

#### Step 2: explanations of false-positive flows (official test, 300 flows per group and model, 5 seeds)
| group (40 features / 48 features) | flows in test | deletion faithfulness: top-SHAP minus random, k = 5 | raw confidence | calibrated confidence | raw >= 0.90 | flagged Unknown |
|---|---|---|---|---|---|---|
| true Normal predicted Normal (TN) | 24,057 / 23,754 | 0.184 / 0.693 | 0.928 / 0.940 | 0.920 / 0.932 | 83% / 84% | 4% / 3% |
| false positive: Normal predicted as an attack (FP-attack) | 9,775 / 10,078 | 0.349 / 0.474 | 0.675 / 0.719 | 0.638 / 0.668 | 9% / 13% | 13% / 9% |
| false positive: Normal predicted as Fuzzers (FP-Fuzzers) | 8,218 / 8,594 | 0.359 / 0.509 | 0.701 / 0.742 | 0.662 / 0.692 | 11% / 17% | 7% / 4% |
| true Fuzzers predicted Fuzzers (TP-Fuzzers) | 3,658 / 3,472 | 0.435 / 0.558 | 0.771 / 0.778 | 0.734 / 0.723 | 29% / 30% | 5% / 7% |
| What separates a false positive from a correct flow (AUROC; 0.5 = nothing) | FP-Fuzzers vs TP-Fuzzers | FP-attack vs TN | | | | |
| 1 - raw confidence | 0.63 / 0.58 | 0.89 / 0.89 | | | | |
| 1 - calibrated confidence | 0.63 / 0.57 | 0.89 / 0.89 | | | | |
| class-atypicality of the cited features (share outside the class's interquartile range) | 0.47 / 0.52 | 0.55 / 0.58 | | | | |
Caption. (a) The explanations of false positives are faithful: removing the top-5 SHAP features lowers the predicted-class probability 0.35-0.51 more than removing random ones (interval above 0 in 5 of 5 seeds for every group and pool), close to true Fuzzers (0.44-0.56) and much higher than for correctly predicted Normal on 40 features (0.18, the
weak spot of the explanation study). (b) The narratives of FP-Fuzzers cite the same features as those of true Fuzzers: on 40 features dload (88% / 76%), service (77% / 75%), sbytes (55% / 70%); on 48 features sttl in 100% of both. (c) The model is less confident on false positives (raw 0.68-0.74 against 0.93-0.94 for correct Normal flows, and 0.77-0.78 for true Fuzzers) and calibration lowers it a little more,
but confidence only separates a false positive from a correct *Fuzzers* alert weakly (AUROC 0.58-0.63; 11-17% of FP-Fuzzers still have a raw probability of 0.90 or more), the open-set flag catches 4-13% of false positives, and the class-atypicality of the cited features carries no information (0.47-0.52 against FP-Fuzzers vs TP-Fuzzers; the false positives are not more atypical for the predicted class than true Fuzzers).
**Plainly:** an analyst reading the narrative of a false-positive Fuzzers alert would see the reasons they would see for a real one, with a confidence of about 70% (calibrated about 66%) against about 77% for a real alert; from these metrics the only reason to doubt it is that lower number, which is a weak signal. The explanation is a correct account of why the model said Fuzzers, which is not the same as a reason to believe it.

#### Step 3: A/B sheet
`results/narratives_ab_sheet.csv`: 30 flows (5 each from Normal, Overlap-Group-1, Fuzzers, flagged Unknown, false-positive Normal and one group of the other attack classes) with the classic and the class-relative narrative as A and B in a random order, blank columns for "clearer" and "more actionable"; the key (which column is which) is in `narratives_ab_key.csv`;
instructions in `narratives_ab_instructions.md`. Nothing is rated.

#### What did not improve, and the limits
- The cue-direction agreement (f) is unchanged (0.78 / 0.73; Overlap-Group-1 0.44 / 0.55, Generic on 48 features 0.26): the rule changes what is cited, not what a cue means.
- Between 4% and 7% of the new narratives cite no numeric feature at all.
- The calibrated confidence is still too high on shifted flows (ECE 0.07-0.09), and it can read "about 100%".
- The new narrative does not help to spot a false positive: the cited features and their atypicality for the predicted class are the same as for a true positive, and confidence is a weak separator.
- Limits: faithful to the model, not to the truth; the confidence is not calibrated on this split; no human study (both sheets are blank templates).

#### One paragraph (the narrative study)
The class-relative narratives are more informative in the way we set out to measure: no "typical" reason is cited any more (it was 45% and 37% of the cited numeric features), each narrative cites about 2.6 features instead of 4.1, every statement is checked against the training flows and correct, and a calibrated confidence now sits next to the raw one (ECE 0.093 -> 0.070 and 0.115 -> 0.086), while the cue direction, which depends on the cue and not on the
omission, still agrees with the model's general behaviour only 73-78% of the time. The check on false positives exposed a limit rather than a bug: the explanation of a false-positive Normal flow is as faithful to the model as that of a true attack (0.35-0.51 against 0.44-0.56), but it cites the same features, is no more atypical for the predicted class, and differs from a real alert only by a lower and still poorly
calibrated confidence, so a narrative on its own does not give an analyst a reason to doubt a false alarm. What remains: a human rating of the old and the new wording (the A/B sheet), a way to bring information about doubt into the narrative (for example a measure of how far the flow sits from the class, or the open-set score) and a better calibration on the shifted split.

## Source: xai_faithfulness_40f_45f_48f.md

### Explanation study Steps 1-2: SHAP additivity and faithfulness (XGBoost, official split, 5 seeds)

Sample: 300 flows per predicted class + 200 flagged-Unknown flows per model and source (official test = known + zero-day flows; validation = block-grouped validation flows).

#### Step 1: SHAP additivity (sum of SHAP values + expected value against the raw margin of the predicted class)

| pool | tier | flows checked | maximum error | flows over 1e-3 |
|---|---|---|---|---|
| 40f | 40 | 19868 | 1.19e-05 | 0 |
| 40f | 30 | 19867 | 1.07e-05 | 0 |
| 40f | 15 | 19869 | 9.95e-06 | 0 |
| 45f | 45 | 19863 | 1.39e-05 | 0 |
| 45f | 30 | 19857 | 1.21e-05 | 0 |
| 45f | 15 | 19870 | 1.32e-05 | 0 |
| 48f | 48 | 19865 | 1.08e-05 | 0 |
| 48f | 30 | 19860 | 1.08e-05 | 0 |
| 48f | 15 | 19873 | 1.02e-05 | 0 |

#### Primary metric: probability drop at k = 5, top-SHAP removal minus random removal (median baseline), official-test flows

| pool | tier | features | difference (mean +/- std over seeds) | seeds with interval above 0 and difference >= 0.05 | faithful (declared reading) |
|---|---|---|---|---|---|
| 40f | 40 | 40 | 0.512 +/- 0.012 | 5 of 5 | yes |
| 40f | 30 | 30 | 0.466 +/- 0.011 | 5 of 5 | yes |
| 40f | 15 | 15 | 0.333 +/- 0.011 | 5 of 5 | yes |
| 45f | 45 | 45 | 0.501 +/- 0.023 | 5 of 5 | yes |
| 45f | 30 | 30 | 0.429 +/- 0.014 | 5 of 5 | yes |
| 45f | 15 | 15 | 0.344 +/- 0.012 | 5 of 5 | yes |
| 48f | 48 | 48 | 0.553 +/- 0.011 | 5 of 5 | yes |
| 48f | 30 | 30 | 0.489 +/- 0.007 | 5 of 5 | yes |
| 48f | 15 | 15 | 0.340 +/- 0.026 | 5 of 5 | yes |

#### Deletion curve, whole pools, official-test flows, baseline = training median (probability drop; flip rate)

| pool | k | top SHAP | random | least important | top: class flips | random: class flips | least: class flips |
|---|---|---|---|---|---|---|---|
| 40f | 1 | 0.273 +/- 0.050 | 0.035 +/- 0.018 | 0.003 +/- 0.002 | 0.342 +/- 0.087 | 0.075 +/- 0.034 | 0.018 +/- 0.014 |
| 40f | 3 | 0.547 +/- 0.018 | 0.109 +/- 0.053 | 0.011 +/- 0.011 | 0.790 +/- 0.033 | 0.186 +/- 0.075 | 0.047 +/- 0.038 |
| 40f | 5 | 0.619 +/- 0.011 | 0.182 +/- 0.083 | 0.022 +/- 0.022 | 0.860 +/- 0.018 | 0.280 +/- 0.111 | 0.074 +/- 0.055 |
| 40f | 10 | 0.668 +/- 0.013 | 0.344 +/- 0.121 | 0.074 +/- 0.076 | 0.883 +/- 0.029 | 0.485 +/- 0.166 | 0.167 +/- 0.116 |
| 45f | 1 | 0.234 +/- 0.031 | 0.032 +/- 0.015 | 0.003 +/- 0.003 | 0.295 +/- 0.052 | 0.068 +/- 0.029 | 0.017 +/- 0.014 |
| 45f | 3 | 0.513 +/- 0.025 | 0.102 +/- 0.047 | 0.012 +/- 0.010 | 0.713 +/- 0.040 | 0.172 +/- 0.064 | 0.046 +/- 0.037 |
| 45f | 5 | 0.598 +/- 0.023 | 0.173 +/- 0.079 | 0.025 +/- 0.021 | 0.814 +/- 0.041 | 0.263 +/- 0.104 | 0.070 +/- 0.055 |
| 45f | 10 | 0.670 +/- 0.011 | 0.330 +/- 0.126 | 0.075 +/- 0.070 | 0.893 +/- 0.023 | 0.464 +/- 0.167 | 0.151 +/- 0.109 |
| 48f | 1 | 0.314 +/- 0.053 | 0.035 +/- 0.020 | 0.000 +/- 0.001 | 0.375 +/- 0.094 | 0.071 +/- 0.038 | 0.013 +/- 0.013 |
| 48f | 3 | 0.594 +/- 0.022 | 0.106 +/- 0.059 | 0.001 +/- 0.004 | 0.796 +/- 0.042 | 0.174 +/- 0.088 | 0.029 +/- 0.022 |
| 48f | 5 | 0.635 +/- 0.016 | 0.175 +/- 0.093 | 0.014 +/- 0.022 | 0.836 +/- 0.033 | 0.262 +/- 0.130 | 0.058 +/- 0.047 |
| 48f | 10 | 0.685 +/- 0.027 | 0.321 +/- 0.140 | 0.079 +/- 0.101 | 0.900 +/- 0.035 | 0.439 +/- 0.187 | 0.162 +/- 0.151 |

#### Deletion curve, whole pools, official-test flows, baseline = a random training row (probability drop; flip rate)

| pool | k | top SHAP | random | least important | top: class flips | random: class flips | least: class flips |
|---|---|---|---|---|---|---|---|
| 40f | 1 | 0.240 +/- 0.036 | 0.038 +/- 0.018 | 0.005 +/- 0.006 | 0.311 +/- 0.062 | 0.083 +/- 0.033 | 0.023 +/- 0.019 |
| 40f | 3 | 0.517 +/- 0.014 | 0.117 +/- 0.055 | 0.020 +/- 0.022 | 0.726 +/- 0.024 | 0.200 +/- 0.076 | 0.058 +/- 0.048 |
| 40f | 5 | 0.603 +/- 0.008 | 0.195 +/- 0.088 | 0.041 +/- 0.046 | 0.818 +/- 0.013 | 0.303 +/- 0.112 | 0.096 +/- 0.077 |
| 40f | 10 | 0.656 +/- 0.015 | 0.361 +/- 0.125 | 0.124 +/- 0.129 | 0.870 +/- 0.013 | 0.509 +/- 0.164 | 0.226 +/- 0.169 |
| 45f | 1 | 0.223 +/- 0.035 | 0.038 +/- 0.018 | 0.006 +/- 0.006 | 0.286 +/- 0.054 | 0.080 +/- 0.033 | 0.026 +/- 0.023 |
| 45f | 3 | 0.497 +/- 0.023 | 0.115 +/- 0.054 | 0.021 +/- 0.020 | 0.686 +/- 0.039 | 0.194 +/- 0.076 | 0.060 +/- 0.050 |
| 45f | 5 | 0.588 +/- 0.014 | 0.195 +/- 0.089 | 0.042 +/- 0.041 | 0.792 +/- 0.027 | 0.298 +/- 0.119 | 0.094 +/- 0.073 |
| 45f | 10 | 0.657 +/- 0.018 | 0.359 +/- 0.133 | 0.128 +/- 0.125 | 0.863 +/- 0.010 | 0.505 +/- 0.177 | 0.223 +/- 0.173 |
| 48f | 1 | 0.285 +/- 0.028 | 0.040 +/- 0.021 | 0.003 +/- 0.004 | 0.358 +/- 0.052 | 0.082 +/- 0.038 | 0.019 +/- 0.017 |
| 48f | 3 | 0.556 +/- 0.017 | 0.125 +/- 0.062 | 0.016 +/- 0.017 | 0.741 +/- 0.032 | 0.204 +/- 0.087 | 0.058 +/- 0.049 |
| 48f | 5 | 0.619 +/- 0.013 | 0.201 +/- 0.094 | 0.042 +/- 0.046 | 0.812 +/- 0.023 | 0.303 +/- 0.127 | 0.099 +/- 0.079 |
| 48f | 10 | 0.666 +/- 0.013 | 0.356 +/- 0.128 | 0.118 +/- 0.121 | 0.867 +/- 0.012 | 0.496 +/- 0.170 | 0.210 +/- 0.161 |

#### Insertion and sufficiency at k = 5, whole pools, official-test flows, median baseline

Comprehensiveness = the deletion drop; sufficiency = the original probability minus the probability with ONLY the chosen features on the baseline vector (lower = the chosen features alone nearly reproduce the prediction).

| pool | comprehensiveness: top / random | sufficiency: top / random |
|---|---|---|
| 40f | 0.619 +/- 0.011 / 0.182 +/- 0.083 | 0.163 +/- 0.029 / 0.559 +/- 0.045 |
| 45f | 0.598 +/- 0.023 / 0.173 +/- 0.079 | 0.217 +/- 0.056 / 0.569 +/- 0.059 |
| 48f | 0.635 +/- 0.016 / 0.175 +/- 0.093 | 0.200 +/- 0.034 / 0.562 +/- 0.046 |

#### Primary metric per predicted class (whole pools, official-test flows; mean +/- std over seeds)

| pool | stratum | flows per seed | difference | interval above 0 in |
|---|---|---|---|---|
| 40f | Exploits | 300 | 0.519 +/- 0.081 | 15 of 15 |
| 40f | Fuzzers | 300 | 0.304 +/- 0.099 | 15 of 15 |
| 40f | Generic | 300 | 0.776 +/- 0.111 | 15 of 15 |
| 40f | Normal | 300 | 0.182 +/- 0.025 | 15 of 15 |
| 40f | Overlap-Group-1 | 300 | 0.382 +/- 0.091 | 15 of 15 |
| 40f | Reconnaissance | 300 | 0.590 +/- 0.149 | 15 of 15 |
| 40f | Unknown | 200 | 0.238 +/- 0.034 | 15 of 15 |
| 45f | Exploits | 300 | 0.404 +/- 0.132 | 15 of 15 |
| 45f | Fuzzers | 300 | 0.264 +/- 0.075 | 15 of 15 |
| 45f | Generic | 300 | 0.760 +/- 0.108 | 15 of 15 |
| 45f | Normal | 300 | 0.263 +/- 0.140 | 15 of 15 |
| 45f | Overlap-Group-1 | 300 | 0.391 +/- 0.091 | 15 of 15 |
| 45f | Reconnaissance | 300 | 0.593 +/- 0.174 | 15 of 15 |
| 45f | Unknown | 200 | 0.235 +/- 0.047 | 15 of 15 |
| 48f | Exploits | 300 | 0.290 +/- 0.039 | 15 of 15 |
| 48f | Fuzzers | 300 | 0.392 +/- 0.172 | 15 of 15 |
| 48f | Generic | 300 | 0.785 +/- 0.106 | 15 of 15 |
| 48f | Normal | 300 | 0.650 +/- 0.063 | 15 of 15 |
| 48f | Overlap-Group-1 | 300 | 0.258 +/- 0.122 | 15 of 15 |
| 48f | Reconnaissance | 300 | 0.551 +/- 0.188 | 15 of 15 |
| 48f | Unknown | 200 | 0.217 +/- 0.052 | 15 of 15 |

#### Shift check: the primary metric on official-test flows against block-grouped validation flows (flows pooled over the 5 seeds; two-sample bootstrap)

| pool | tier | official test | validation | test minus validation (95% interval) | faithfulness lost under the shift (declared reading) |
|---|---|---|---|---|---|
| 40f | 40 | 0.512 | 0.513 | -0.001 (-0.010, +0.009) | no |
| 40f | 30 | 0.466 | 0.470 | -0.004 (-0.013, +0.006) | no |
| 40f | 15 | 0.333 | 0.334 | -0.001 (-0.010, +0.008) | no |
| 45f | 45 | 0.501 | 0.495 | +0.006 (-0.004, +0.015) | no |
| 45f | 30 | 0.429 | 0.436 | -0.007 (-0.017, +0.002) | no |
| 45f | 15 | 0.344 | 0.349 | -0.005 (-0.014, +0.004) | no |
| 48f | 48 | 0.553 | 0.540 | +0.013 (+0.003, +0.023) | no |
| 48f | 30 | 0.489 | 0.486 | +0.002 (-0.008, +0.013) | no |
| 48f | 15 | 0.340 | 0.340 | +0.000 (-0.009, +0.011) | no |

## Source: xai_audit_40f_48f.md

### Explanation study Steps 1 and 3: narrative audit through the dashboard path (XGBoost, official split, 5 seeds x 200 flows per pool)

| check | 40f | 48f |
|---|---|---|
| quoted confidence = model probability | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| JSON confidence = model probability | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (a) cited features are positive top-5 SHAP features | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (b) cue exact vs training z-score (per cited feature) | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (b) cue direction (per cited feature) | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (c) categorical named by category (per cited feature) | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (d) action matches the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (e) no false statement about the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (f) cue direction agrees with the SHAP-vs-value relation (determined cases) | 0.757 +/- 0.018 | 0.722 +/- 0.013 |

40f: of the cited numeric features 46.9% carry the cue "typical" (no direction claimed), 4.5% have no monotone SHAP-vs-value relation, and in 7.5% of the narratives no cited numeric feature carries a direction at all; 0.0% of narratives say the decision was diffuse.

48f: of the cited numeric features 35.7% carry the cue "typical" (no direction claimed), 1.7% have no monotone SHAP-vs-value relation, and in 2.7% of the narratives no cited numeric feature carries a direction at all; 0.0% of narratives say the decision was diffuse.

#### Per predicted class (mean over seeds; all deterministic checks a-e must be 1.000)

| pool | stratum | narratives | (a) | (b) exact | (d) | (e) | (f) consistent |
|---|---|---|---|---|---|---|---|
| 40f | Exploits | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.719 |
| 40f | Fuzzers | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.846 |
| 40f | Generic | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.611 |
| 40f | Normal | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.891 |
| 40f | Overlap-Group-1 | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.361 |
| 40f | Reconnaissance | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.993 |
| 40f | Unknown | 250 | 1.000 | 1.000 | 1.000 | 1.000 | 0.692 |
| 48f | Exploits | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.718 |
| 48f | Fuzzers | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.753 |
| 48f | Generic | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.253 |
| 48f | Normal | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.892 |
| 48f | Overlap-Group-1 | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 0.489 |
| 48f | Reconnaissance | 125 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 48f | Unknown | 250 | 1.000 | 1.000 | 1.000 | 1.000 | 0.676 |

#### Failures

| pool | f_direction |
|---|---|
| 40f | 403 |
| 48f | 622 |

Most frequent reasons:

- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.44 on training rows) (54)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.55 on training rows) (32)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.47 on training rows) (32)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.46 on training rows) (32)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.49 on training rows) (31)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.51 on training rows) (30)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.43 on training rows) (28)
- f_direction: avg_pkt_size: cue 'reduced' but SHAP for Overlap-Group-1 falls as the value rises (rho 0.45 on training rows) (26)

#### Audit rates on official-test flows against validation flows (the shift check)

| check | pool | official test | validation | test minus validation |
|---|---|---|---|---|
| (a) cited features in the SHAP top 5 | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (a) cited features in the SHAP top 5 | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (b) cue exact | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (b) cue exact | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (c) categorical named | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (c) categorical named | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (d) action | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (d) action | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (e) label statement | 40f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (e) label statement | 48f | 1.000 +/- 0.000 | 1.000 +/- 0.000 | +0.000 |
| (f) directional consistency | 40f | 0.757 +/- 0.018 | 0.788 +/- 0.017 | -0.030 |
| (f) directional consistency | 48f | 0.722 +/- 0.013 | 0.731 +/- 0.029 | -0.009 |
| share of cited features read "typical" | 40f | 0.469 +/- 0.017 | 0.479 +/- 0.034 | -0.010 |
| share of cited features read "typical" | 48f | 0.357 +/- 0.031 | 0.363 +/- 0.030 | -0.005 |
| share with no monotone SHAP-vs-value relation | 40f | 0.045 +/- 0.013 | 0.034 +/- 0.013 | +0.011 |
| share with no monotone SHAP-vs-value relation | 48f | 0.017 +/- 0.010 | 0.016 +/- 0.009 | +0.000 |

## Source: narrative_test_40f_48f.md

### Narrative study Step 1: classic against class-relative narratives (test flows, 5 seeds, mean +/- std)

#### 40f

| metric | classic | class-relative |
|---|---|---|
| narratives | 230 +/- 0 | 230 +/- 0 |
| cited numeric features read "typical" | 0.452 +/- 0.016 | 0.000 +/- 0.000 |
| features cited per narrative | 4.108 +/- 0.061 | 2.558 +/- 0.056 |
| numeric features cited per narrative | 3.430 +/- 0.076 | 1.880 +/- 0.081 |
| narratives citing no numeric feature | 0.004 +/- 0.008 | 0.073 +/- 0.011 |
| (a) cited features are positive top-5 SHAP features | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (b) cue exact vs training z-score | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (c) categorical named | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (d) action matches the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (e) no false statement about the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (f) cue direction agrees with the SHAP trend | 0.780 +/- 0.016 | 0.780 +/- 0.016 |
| (g) clauses equal an independent computation | n/a | 1.000 +/- 0.000 |
| calibrated number = temperature-scaled probability | n/a | 1.000 +/- 0.000 |

##### 40f per predicted class

| predicted class (stratum) | flows per seed | "typical" share: classic -> class-relative | features cited: classic -> class-relative | (f): classic -> class-relative |
|---|---|---|---|---|
| Exploits | 25 | 0.462 +/- 0.035 -> 0.000 +/- 0.000 | 4.368 +/- 0.137 -> 2.640 +/- 0.075 | 0.693 +/- 0.059 -> 0.693 +/- 0.059 |
| FP-Normal | 30 | 0.369 +/- 0.025 -> 0.000 +/- 0.000 | 4.320 +/- 0.159 -> 2.993 +/- 0.182 | 0.823 +/- 0.026 -> 0.823 +/- 0.026 |
| Fuzzers | 25 | 0.409 +/- 0.053 -> 0.000 +/- 0.000 | 4.200 +/- 0.075 -> 2.816 +/- 0.254 | 0.876 +/- 0.038 -> 0.876 +/- 0.038 |
| Generic | 25 | 0.611 +/- 0.056 -> 0.000 +/- 0.000 | 4.200 +/- 0.113 -> 2.136 +/- 0.185 | 0.656 +/- 0.175 -> 0.656 +/- 0.175 |
| Normal | 25 | 0.321 +/- 0.045 -> 0.000 +/- 0.000 | 4.464 +/- 0.092 -> 3.216 +/- 0.236 | 0.895 +/- 0.073 -> 0.895 +/- 0.073 |
| Overlap-Group-1 | 25 | 0.519 +/- 0.046 -> 0.000 +/- 0.000 | 4.024 +/- 0.197 -> 2.368 +/- 0.214 | 0.437 +/- 0.094 -> 0.437 +/- 0.094 |
| Reconnaissance | 25 | 0.416 +/- 0.109 -> 0.000 +/- 0.000 | 4.816 +/- 0.036 -> 2.928 +/- 0.512 | 0.976 +/- 0.024 -> 0.976 +/- 0.024 |
| Unknown | 50 | 0.528 +/- 0.025 -> 0.000 +/- 0.000 | 3.268 +/- 0.129 -> 1.920 +/- 0.141 | 0.688 +/- 0.063 -> 0.688 +/- 0.063 |

#### 48f

| metric | classic | class-relative |
|---|---|---|
| narratives | 230 +/- 0 | 230 +/- 0 |
| cited numeric features read "typical" | 0.365 +/- 0.036 | 0.000 +/- 0.000 |
| features cited per narrative | 4.018 +/- 0.037 | 2.714 +/- 0.140 |
| numeric features cited per narrative | 3.568 +/- 0.097 | 2.263 +/- 0.130 |
| narratives citing no numeric feature | 0.001 +/- 0.002 | 0.040 +/- 0.014 |
| (a) cited features are positive top-5 SHAP features | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (b) cue exact vs training z-score | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (c) categorical named | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (d) action matches the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (e) no false statement about the label | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| (f) cue direction agrees with the SHAP trend | 0.733 +/- 0.019 | 0.733 +/- 0.019 |
| (g) clauses equal an independent computation | n/a | 1.000 +/- 0.000 |
| calibrated number = temperature-scaled probability | n/a | 1.000 +/- 0.000 |

##### 48f per predicted class

| predicted class (stratum) | flows per seed | "typical" share: classic -> class-relative | features cited: classic -> class-relative | (f): classic -> class-relative |
|---|---|---|---|---|
| Exploits | 25 | 0.303 +/- 0.055 -> 0.000 +/- 0.000 | 4.544 +/- 0.176 -> 3.312 +/- 0.270 | 0.722 +/- 0.055 -> 0.722 +/- 0.055 |
| FP-Normal | 30 | 0.321 +/- 0.030 -> 0.000 +/- 0.000 | 4.380 +/- 0.150 -> 3.120 +/- 0.227 | 0.675 +/- 0.032 -> 0.675 +/- 0.032 |
| Fuzzers | 25 | 0.403 +/- 0.039 -> 0.000 +/- 0.000 | 4.192 +/- 0.134 -> 2.680 +/- 0.080 | 0.830 +/- 0.089 -> 0.830 +/- 0.089 |
| Generic | 25 | 0.607 +/- 0.031 -> 0.000 +/- 0.000 | 4.232 +/- 0.158 -> 2.232 +/- 0.087 | 0.262 +/- 0.172 -> 0.262 +/- 0.172 |
| Normal | 25 | 0.247 +/- 0.074 -> 0.000 +/- 0.000 | 3.280 +/- 0.102 -> 2.480 +/- 0.172 | 0.909 +/- 0.053 -> 0.909 +/- 0.053 |
| Overlap-Group-1 | 25 | 0.303 +/- 0.042 -> 0.000 +/- 0.000 | 3.960 +/- 0.188 -> 2.976 +/- 0.218 | 0.550 +/- 0.043 -> 0.550 +/- 0.043 |
| Reconnaissance | 25 | 0.372 +/- 0.088 -> 0.000 +/- 0.000 | 4.896 +/- 0.061 -> 3.176 +/- 0.419 | 0.991 +/- 0.008 -> 0.991 +/- 0.008 |
| Unknown | 50 | 0.382 +/- 0.023 -> 0.000 +/- 0.000 | 3.304 +/- 0.151 -> 2.184 +/- 0.123 | 0.681 +/- 0.043 -> 0.681 +/- 0.043 |

#### Calibration (temperature fitted on block-grouped validation; ECE of the known official-test flows, 15 bins)

| pool | temperature | ECE raw | ECE calibrated |
|---|---|---|---|
| 40f | 1.18 +/- 0.09 | 0.093 +/- 0.008 | 0.070 +/- 0.006 |
| 48f | 1.26 +/- 0.10 | 0.115 +/- 0.010 | 0.086 +/- 0.002 |

#### Failures

| style | f_direction |
|---|---|
| class_relative | 1112 |
| classic | 1112 |

Failures other than the cue-direction check (f): 0.

## Source: narrative_falsepos_40f_48f.md

### Narrative study Step 2: explanations of false-positive flows (official test, 5 seeds, 300 flows per group and model, mean +/- std)

FP-attack = true Normal predicted as an attack; FP-Fuzzers = true Normal predicted as Fuzzers; TN = true Normal predicted Normal; TP-Fuzzers = true Fuzzers predicted Fuzzers.

#### 40f

##### (a) Deletion faithfulness: probability drop at k = 5, top SHAP minus random removal (median baseline; random-row baseline in brackets)

| group | flows in test | top SHAP drop | random drop | difference (std over seeds) | seeds with interval above 0 and difference >= 0.05 | top: class flips |
|---|---|---|---|---|---|---|
| TN | 24057 | 0.215 +/- 0.030 | 0.031 +/- 0.012 | 0.184 +/- 0.024 (0.386 +/- 0.029) | 5 of 5 | 0.263 +/- 0.086 |
| FP-attack | 9775 | 0.510 +/- 0.053 | 0.161 +/- 0.015 | 0.349 +/- 0.051 (0.336 +/- 0.017) | 5 of 5 | 0.904 +/- 0.063 |
| FP-Fuzzers | 8218 | 0.531 +/- 0.067 | 0.172 +/- 0.028 | 0.359 +/- 0.065 (0.342 +/- 0.034) | 5 of 5 | 0.881 +/- 0.077 |
| TP-Fuzzers | 3658 | 0.615 +/- 0.042 | 0.181 +/- 0.014 | 0.435 +/- 0.042 (0.416 +/- 0.010) | 5 of 5 | 0.893 +/- 0.060 |

##### (c) Confidence on these flows

| group | raw confidence | calibrated confidence | raw >= 0.90 | calibrated >= 0.90 | flagged Unknown | features cited (class-relative) | class-atypicality of cited features |
|---|---|---|---|---|---|---|---|
| TN | 0.928 +/- 0.011 | 0.920 +/- 0.013 | 0.826 +/- 0.026 | 0.819 +/- 0.027 | 0.044 +/- 0.010 | 3.12 +/- 0.17 | 0.411 +/- 0.039 |
| FP-attack | 0.675 +/- 0.008 | 0.638 +/- 0.012 | 0.088 +/- 0.026 | 0.043 +/- 0.022 | 0.130 +/- 0.036 | 2.94 +/- 0.14 | 0.457 +/- 0.020 |
| FP-Fuzzers | 0.701 +/- 0.011 | 0.662 +/- 0.010 | 0.105 +/- 0.016 | 0.048 +/- 0.014 | 0.065 +/- 0.034 | 3.02 +/- 0.11 | 0.463 +/- 0.014 |
| TP-Fuzzers | 0.771 +/- 0.011 | 0.734 +/- 0.015 | 0.294 +/- 0.040 | 0.206 +/- 0.031 | 0.051 +/- 0.018 | 2.71 +/- 0.09 | 0.500 +/- 0.042 |

##### (c) Does anything separate a false positive from a correct flow? (AUROC; 0.5 = nothing; positive = the false-positive group)

| false positives | compared with | score | AUROC |
|---|---|---|---|
| FP-Fuzzers | TP-Fuzzers | 1 - raw confidence | 0.632 +/- 0.022 |
| FP-Fuzzers | TP-Fuzzers | 1 - calibrated confidence | 0.632 +/- 0.022 |
| FP-Fuzzers | TP-Fuzzers | class-atypicality of the cited features | 0.470 +/- 0.035 |
| FP-attack | TN | 1 - raw confidence | 0.886 +/- 0.019 |
| FP-attack | TN | 1 - calibrated confidence | 0.887 +/- 0.019 |
| FP-attack | TN | class-atypicality of the cited features | 0.553 +/- 0.039 |

##### (b) Features the classic narrative cites most often (share of narratives, mean over seeds)

| group | top cited features |
|---|---|
| TN | ackdat (76%), dload (63%), dloss (41%), synack (39%), dbytes (37%) |
| FP-attack | service (76%), dload (75%), avg_pkt_size (52%), sbytes (47%), smean (44%) |
| FP-Fuzzers | dload (88%), service (77%), sbytes (55%), avg_pkt_size (50%), smean (48%) |
| TP-Fuzzers | dload (76%), service (75%), sbytes (70%), smean (42%), dbytes (38%) |

#### 48f

##### (a) Deletion faithfulness: probability drop at k = 5, top SHAP minus random removal (median baseline; random-row baseline in brackets)

| group | flows in test | top SHAP drop | random drop | difference (std over seeds) | seeds with interval above 0 and difference >= 0.05 | top: class flips |
|---|---|---|---|---|---|---|
| TN | 23754 | 0.748 +/- 0.027 | 0.055 +/- 0.018 | 0.693 +/- 0.038 (0.469 +/- 0.058) | 5 of 5 | 0.848 +/- 0.021 |
| FP-attack | 10078 | 0.594 +/- 0.157 | 0.120 +/- 0.039 | 0.474 +/- 0.122 (0.387 +/- 0.010) | 5 of 5 | 0.891 +/- 0.197 |
| FP-Fuzzers | 8594 | 0.640 +/- 0.192 | 0.131 +/- 0.036 | 0.509 +/- 0.159 (0.404 +/- 0.022) | 5 of 5 | 0.903 +/- 0.218 |
| TP-Fuzzers | 3472 | 0.701 +/- 0.133 | 0.144 +/- 0.033 | 0.558 +/- 0.104 (0.447 +/- 0.022) | 5 of 5 | 0.929 +/- 0.158 |

##### (c) Confidence on these flows

| group | raw confidence | calibrated confidence | raw >= 0.90 | calibrated >= 0.90 | flagged Unknown | features cited (class-relative) | class-atypicality of cited features |
|---|---|---|---|---|---|---|---|
| TN | 0.940 +/- 0.010 | 0.932 +/- 0.009 | 0.843 +/- 0.023 | 0.841 +/- 0.023 | 0.026 +/- 0.017 | 2.49 +/- 0.11 | 0.326 +/- 0.031 |
| FP-attack | 0.719 +/- 0.011 | 0.668 +/- 0.015 | 0.128 +/- 0.018 | 0.057 +/- 0.023 | 0.089 +/- 0.052 | 2.88 +/- 0.12 | 0.384 +/- 0.018 |
| FP-Fuzzers | 0.742 +/- 0.023 | 0.692 +/- 0.013 | 0.165 +/- 0.047 | 0.072 +/- 0.019 | 0.044 +/- 0.032 | 3.00 +/- 0.15 | 0.424 +/- 0.024 |
| TP-Fuzzers | 0.778 +/- 0.016 | 0.723 +/- 0.019 | 0.297 +/- 0.047 | 0.157 +/- 0.046 | 0.065 +/- 0.029 | 2.73 +/- 0.10 | 0.414 +/- 0.023 |

##### (c) Does anything separate a false positive from a correct flow? (AUROC; 0.5 = nothing; positive = the false-positive group)

| false positives | compared with | score | AUROC |
|---|---|---|---|
| FP-Fuzzers | TP-Fuzzers | 1 - raw confidence | 0.580 +/- 0.051 |
| FP-Fuzzers | TP-Fuzzers | 1 - calibrated confidence | 0.569 +/- 0.052 |
| FP-Fuzzers | TP-Fuzzers | class-atypicality of the cited features | 0.519 +/- 0.031 |
| FP-attack | TN | 1 - raw confidence | 0.892 +/- 0.016 |
| FP-attack | TN | 1 - calibrated confidence | 0.892 +/- 0.017 |
| FP-attack | TN | class-atypicality of the cited features | 0.581 +/- 0.032 |

##### (b) Features the classic narrative cites most often (share of narratives, mean over seeds)

| group | top cited features |
|---|---|
| TN | ct_state_ttl (84%), sttl (71%), ct_srv_dst (51%), ct_srv_src (35%), dload (27%) |
| FP-attack | sttl (95%), smean (47%), ct_dst_src_ltm (46%), sbytes (44%), avg_pkt_size (37%) |
| FP-Fuzzers | sttl (100%), smean (52%), sbytes (51%), ct_dst_src_ltm (48%), ct_srv_dst (39%) |
| TP-Fuzzers | sttl (100%), sbytes (62%), smean (38%), dbytes (36%), service (33%) |

## Source: explanations_protocol.md

### Explanation study protocol (declared before any the explanation study result was produced)

Novelty 2: human-centered, actionable explanations. XGBoost, flat model, official split, scheme `current`, ZERO-SHOT throughout. Models are trained exactly as in the feature-tier study (block-grouped training / validation split of the training file,
seed 42-46 for the split and the model; `pipelines/run_tier_study.prepare`), pools 40 (base), 45 (`full_no_ttl`) and 48 (full), and the 30- and 15-feature mutual-information tiers of each pool (shared blockval rankings), i.e. nine configurations x 5 seeds.
Mean and std over seeds. Explanation stability is not repeated (the feature-tier study). Nothing is selected on the official-test labels; the test labels are used only to report.

#### Samples (stratified, seeded; rule and size stated here)
- A flow's stratum is its predicted class (6 classes: Normal, Overlap-Group-1, Exploits, Fuzzers, Generic, Reconnaissance) or **Unknown** when the open-set rule flags it (max-softmax below the 5% false-Unknown threshold fixed on the block-grouped validation split, the
  threshold the dashboard uses).
- **Faithfulness sample (Step 2):** 300 flows per predicted class (all of them when a class has fewer) + 200 flows flagged Unknown, about 2,000 flows, drawn with `numpy.random.default_rng(seed)` without replacement. Official-test candidates are the known test flows plus the zero-day flows
  (Worms, Shellcode), because the dashboard would receive both. A second sample of the same size is drawn from the block-grouped validation flows (training file, never seen by the model, no zero-day flows) for the shift comparison.
- **Narrative-audit sample (Step 3):** per model 25 flows per predicted class (6 x 25) + 50 flagged-Unknown flows = 200 flows from the same official-test candidates; seeds 42-46, pools 40 and 48 (tier = the whole pool, which is what the dashboard serves); 2,000 narratives in total.

#### Step 1: what the explanation computes
- **SHAP additivity.** For every flow of the Step 2 sample (every model, 5 seeds): |sum of the SHAP values of the predicted class + the explainer's expected value - the model's raw margin (`output_margin=True`) for that class|. Declared tolerance: 1e-3 (float32 trees). Report the
  maximum error and any failures.
- **Quoted confidence.** For every audit-sample flow through the dashboard path: the percentage printed in the narrative (one decimal) equals `100 x` the model's predicted probability of the predicted class rounded to one decimal, and the `confidence` field equals that probability rounded to four decimals. No calibrated
  score is shown anywhere in the backend or the frontend (only `confidence`); this is stated, not tested.

#### Step 2: faithfulness (deletion and insertion)
- For each flow, SHAP values of the predicted class (TreeExplainer, the repository's `SHAPExplainer`). "Top" = the k features with the largest (signed) SHAP value for the predicted class; "least important" = the k features with the smallest absolute SHAP value; "random" = k features
  drawn uniformly (one draw per flow). k = 1, 3, 5, 10.
- **Deletion:** the chosen features of the flow are replaced by a baseline; record the drop in the predicted-class probability and whether the predicted class flips. Baseline 1: the training median of the feature in the model's input space (the training mode for the three categorical features
  proto, service, state). Baseline 2: the feature values of one random training row (one row per flow). **Insertion:** start from the baseline vector (the whole row replaced) and insert the chosen features of the flow; record the predicted-class probability.
  Comprehensiveness = the deletion drop of the top features; sufficiency = the original probability minus the insertion probability of the top features (lower = the top features alone suffice).
- **Primary metric (declared now):** the mean probability drop at k = 5 for top-SHAP removal minus random removal (median baseline), with a 95% bootstrap interval over flows (1,000 resamples, per seed); headline = mean over the 5 seeds. Declared reading: the explanation is **faithful** for a configuration when
  the difference is at least 0.05 and its interval excludes 0 in all 5 seeds. Also reported per predicted class (including Unknown) for the three whole pools, and for the 30- and 15-feature tiers.
- **Shift check:** the same metric on the validation sample and on the official-test sample of the same model; the declared reading of "faithfulness is lost under the shift" is a test-minus-validation difference below -0.05 with a bootstrap interval excluding 0.

#### Step 3: narrative audit (the dashboard path)
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

#### Step 4: dashboard end to end
The FastAPI app (`dashboard.backend.main:app`) is called with `data/samples/sample_flows.csv` through the framework's own test client (the same request path as uvicorn). Its narratives, confidences and top SHAP features are compared row by row with an independent computation from the same saved artifact
(model.predict_proba, a separate SHAPExplainer, a separate NarrativeGenerator call); they must match exactly. Differences are fixed at their cause with a regression test. `scripts/check_explainability.py` (the pipeline's own check) is compared as well. If the frontend can be started, one screenshot of
the prediction and explanation view is taken; otherwise the report says the frontend was not run.

#### Step 5 (small): human audit sheet
`results/explanations_human_audit_sheet.csv`: 30 narratives stratified over the predicted classes and Unknown, with blank rating columns (understandable, actionable, agrees with the rater's judgement of the flow). It is a template only; no rating is filled in or reported.

#### Not claimed
The explanations describe the model, not the traffic: a faithful explanation of a wrong prediction is still a wrong prediction. Teammates' model families are not run or quoted here.

## Source: narratives_protocol.md

### Narrative study protocol (declared before any the narrative study result was produced)

A more informative narrative and a faithfulness check on false-positive explanations. XGBoost, flat model, official split, scheme `current`, ZERO-SHOT, models trained as in the feature-tier and explanation studies (block-grouped training / validation), seeds 42-46, pools 40 (base) and 48 (full), whole pool.
Nothing about the model or SHAP changes; only the sentence built from them. The existing generator stays: `narrative.style: classic` (the default, unchanged behaviour) or `class_relative`.

#### The class-relative rule (the only rule that is evaluated; no variants are tried on the held-out sample)
For a flow predicted as class c, the narrative still cites the positive-SHAP features among the top 5 by absolute SHAP value of c (config `xai.top_k_features`), in that order. Then, per cited feature:
1. **Numeric feature.** Compute the classic cue from the z-score against the overall training mean / std. If the cue is "typical" (|z| < 0.3) the feature is **omitted**. Otherwise it is written as `<cue> <description> (<overall clause>; <class clause>)`:
   - overall clause: `higher than P% of all flows` when the cue is high (P = 100 x the share of ALL training flows with a strictly smaller value), `lower than P% of all flows` when the cue is low (P = 100 x the share with a strictly larger value);
   - class clause (only when the flow is not flagged Unknown, because a flow the system does not recognise is not described as a member of a class): with q25 / q75 the quartiles of the value among training flows of class c, `typical of <c> flows` when q25 <= value <= q75, else `higher than Q% of <c> flows` (value > q75; Q = 100 x the share of class-c training flows strictly below) or `lower than Q% of <c> flows` (value < q25; Q = 100 x the share strictly above). P and Q are rounded to whole percent.
2. **Categorical feature** (proto, service, state): `<description>=<category> (seen in A% of all flows; seen in B% of <c> flows)` with A / B the shares of all / class-c training flows with that category (the class part omitted for Unknown flows).
3. If no feature is left after omission the narrative says what the classic one says for no reasons ("No single feature dominated the decision; the pattern was diffuse across many features.").
The first sentence, the suggested action and everything else are unchanged. **Calibrated confidence (class_relative style only):** after the first sentence, `Calibrated estimate: about X% (the model's raw probability tends to be too high on new traffic; treat both numbers as estimates, not guarantees).`, with
X = 100 x the predicted-class probability after temperature scaling (T in [0.25, 5] fitted by negative log-likelihood on the block-grouped validation split of the model, as in the open-set boost study); the raw value is kept in the first sentence. ECE (15 bins) of the raw and calibrated probabilities on the known official-test flows is reported per seed.
Percentiles and quartiles come from 1,001 quantile grid points per feature (all training flows and each class's flows), saved with the model (`class_reference_<set>.npz`, no pickle).

#### Development and evaluation discipline
- The rule above is fixed. It is developed and inspected only on a sample of **block-grouped validation flows** (training file) of model seed 42, pool 40; any change after that inspection is limited to correctness defects (a wrong number or a broken sentence), is listed in the report, and is never made to move a metric.
- It is then evaluated **once** on a fresh official-test sample drawn with sampling seed 5000 + the model seed (the explanation study used the model seed itself, so the flows differ): per model 25 flows for each of the six predicted classes, 50 flagged-Unknown flows and 30 **false-positive Normal flows** (true Normal flows predicted as an attack and not flagged Unknown, drawn from the whole test file and
  excluded from the class strata), 230 flows, through the dashboard's `PredictionService` once with each style (the two services load the same saved artifacts).

#### Step 1 primary metrics (held-out sample, pools 40 and 48, overall and per predicted class, classic against class-relative)
1. The share of cited numeric features that read "typical", and the number of features cited per narrative (mean; share of narratives that cite no numeric feature).
2. The cue-direction agreement (f), definition unchanged from the explanation study (sign of the Spearman correlation between the value and the SHAP value of the predicted class on 3,000 training rows against the cue direction; |rho| < 0.10 = no monotone relation; "typical" = no direction claimed).
3. Checks (a)-(e) as in the explanation study, which must stay at 1.000; and a new check **(g)** on the new content: the percentages and the interquartile statement in every clause equal an independent computation from the raw training frame (tolerance 1 percentage point; the interquartile statement exact), and the categorical shares likewise. Also the quoted raw confidence is unchanged and the calibrated number
   equals 100 x the temperature-scaled probability (1 percentage point).

#### Step 2: false-positive explanations (official test, pools 40 and 48, 5 seeds)
Groups, 300 flows each per model (all of them when fewer): **FP-attack** (true Normal predicted as any attack class), **FP-Fuzzers** (true Normal predicted as Fuzzers), **TN** (true Normal predicted Normal) and **TP-Fuzzers** (true Fuzzers predicted Fuzzers); flows flagged Unknown are included in their group and counted.
- (a) Deletion faithfulness as in the explanation study: top-SHAP minus random removal of 5 features, median baseline (and a random training row), probability drop and flip rate, bootstrap interval over flows per seed; declared reading as in the explanation study (at least 0.05 with the interval above 0 in all 5 seeds).
- (b) The features the narratives cite per group (classic: the positive top-5 features; class-relative: the numeric ones that survive the omission rule) with the share of narratives citing each.
- (c) Raw and calibrated confidence: mean, share at or above 0.90, share flagged Unknown; and whether anything separates a false positive from a correct flow: AUROC (positive = FP-Fuzzers, negative = TP-Fuzzers, and FP-attack against TN) of the raw confidence (1 - confidence), of the calibrated confidence and of the **class-atypicality** of the narrative = the share of its cited numeric features that lie outside the predicted class's interquartile range (computed from the same reference the narrative uses).
- A plain-language reading of whether an analyst would get a usable reason to doubt a false positive is given from these numbers only; no human result is claimed.

#### Step 3: A/B sheet
30 flows stratified over the predicted classes, Unknown and false-positive Normal (5 each for six strata of the held-out sample, pool 40, model seed 42), classic and class-relative narrative side by side in a seeded random order (which column is which is only in a separate key file), blank columns to choose the clearer and the more actionable one. Not filled in, no rating reported.

#### Not claimed
Faithful to the model, not to the truth. The calibration is on this split's validation flows and does not fix the shift. No human study.
