# Task 3 conclusion: feature selection and explanation consistency (novelty 3), XGBoost

Zero-shot throughout (training data only); official split, scheme `current`; seeds 42-46, mean +/- std. Training / validation come from contiguous
blocks of the training file (1,000-row blocks, 200-row gaps), because a random validation split shares neighbouring flows with the training rows and is
optimistic. Protocol declared before any result: `results/task_3_protocol.md` (two amendments: the other model families are teammates' and are not run here).
Tables: `tier_summary_xgboost.md` (Step 1), `stability_xgboost.md` (Step 2). Steps 3 and 4 (other model families, cross-model agreement) are not part of
this work package; `pipelines/run_tier_study.py --model <type>` and `scripts/cross_model_agreement.py` are ready, with the same rankings, seeds and splits.

## The claim for novelty 3
Shrinking the XGBoost feature set to the top 30 mutual-information features costs no measurable accuracy (macro F1 within 0.003 of the full 40 / 45 / 48-feature pool,
all three pools) and leaves the SHAP explanation as stable as retraining does (30-feature tier vs the full tier Spearman 0.97-0.99 against a same-tier / different-seed floor of
0.97-0.98). Going down to 20 or 15 features costs 0.006-0.014 macro F1 (statistically clear, still under 0.02), about 0.02 FPR and roughly half of the open-set
detection, and the 15-feature explanations agree with the full model's slightly below the retraining floor. The earlier headline "shrinking to 15 features costs no
more than retraining noise" therefore holds to 30 features only.

## Step 1: tier study (official split; macro F1 / FPR / open-set detection, mean over 5 seeds)
| pool | tier | macro F1 | drop vs full | Welch z | FPR (argmax) | det95 FPR (block-validated) | open-set detection | pooled-split macro F1 (best case, optimistic) | ct window / other / TTL columns kept |
|---|---|---|---|---|---|---|---|---|---|
| 40 | 40 | 0.7113 | | | 0.290 | 0.257 | 0.231 | 0.781 | 2 / 2 / 0 |
| 40 | 30 | 0.7141 | -0.003 | -1.4 | 0.292 | 0.259 | 0.230 | 0.781 | 2 / 0 / 0 |
| 40 | 20 | 0.6973 | +0.014 | 8.9 | 0.312 | 0.264 | 0.187 | 0.766 | 0 / 0 / 0 |
| 40 | 15 | 0.6986 | +0.013 | 7.2 | 0.316 | 0.260 | 0.192 | 0.768 | 0 / 0 / 0 |
| 45 | 45 | 0.7065 | | | 0.299 | 0.248 | 0.364 | 0.793 | 7 / 2 / 0 |
| 45 | 30 | 0.7057 | +0.001 | 0.3 | 0.296 | 0.253 | 0.337 | 0.793 | 4 / 0 / 0 |
| 45 | 20 | 0.6976 | +0.009 | 3.7 | 0.314 | 0.267 | 0.184 | 0.766 | 0 / 0 / 0 |
| 45 | 15 | 0.6972 | +0.009 | 3.4 | 0.322 | 0.265 | 0.198 | 0.767 | 0 / 0 / 0 |
| 48 | 48 | 0.7126 | | | 0.298 | 0.247 | 0.348 | 0.798 | 7 / 2 / 3 |
| 48 | 30 | 0.7129 | -0.000 | -0.1 | 0.299 | 0.255 | 0.347 | 0.789 | 2 / 0 / 3 |
| 48 | 20 | 0.7063 | +0.006 | 2.6 | 0.313 | 0.257 | 0.190 | 0.773 | 0 / 0 / 3 |
| 48 | 15 | 0.7067 | +0.006 | 2.3 | 0.321 | 0.256 | 0.194 | 0.775 | 0 / 0 / 3 |

Caption. Dropping features down to 30 changes nothing measurable; 20 and 15 features lose 0.006-0.014 macro F1, raise the argmax FPR by about 0.02 and halve the
open-set detection on the 45 / 48-feature pools (open-set AUROC 0.83 -> 0.76). Criterion A (drop <= 2 x the full pool's seed std) holds for every tier except the
20 / 15-feature tiers of the 40-feature pool; the Welch z shows the 20 / 15-feature drops are outside seed noise on every pool (the criterion is permissive when the full pool's
own std is large). All drops stay below the 0.02 practical bound. The det95 operating point is chosen on the block-grouped validation split.

- **Which extra official columns survive.** The window-count ct_* columns (seven in the 45 / 48 pools) fall to 4 / 2 at 30 features and to **none at 20 or 15** on every pool; the three TTL
  columns stay in every tier of the 48 pool. The within-capture few-shot result of Task 2.5 / 2.6 depended on the window-count ct_* columns, so it does not carry to the 20 / 15-feature tiers.
- **Ranked vs random vs worst-N.** The mutual-information ranking beats 10 random subsets only at 30 features on the 40-feature pool (ranked 0.7141 vs random 0.7049 +/- 0.0035, z 2.68);
  elsewhere it is indistinguishable from random (z -0.6 to 1.2), and the worst-N subsets are far worse (macro F1 0.47-0.62). Random subsets at 20 / 15 features vary widely (std up to 0.06):
  which features matter is real, the ranking does not reliably pick better-than-random sets, as in the earlier study.
- **Block-grouped vs random validation (det95 at the full tier).** The random validation FPR at the 95%-detection point was 0.100 / 0.074 / 0.074 (40 / 45 / 48 features) against a test FPR of 0.250 / 0.246 / 0.244;
  the block-grouped validation gives 0.221 / 0.200 / 0.198 against 0.257 / 0.248 / 0.247. The random validation split under-predicts the test FPR by 0.15-0.17, the block-grouped one by 0.03-0.05.
- **Pooled split (best case).** Pooled macro F1 is 0.78-0.80 at the full tier (against 0.71 official). Shrinking to 15 features costs 0.013 (40 pool) to 0.023-0.026 (45 / 48 pools) on the pooled split but 0.006-0.013 on the official split;
  the extra pooled cost is consistent with (not proof of) the window-count ct_* columns helping only where neighbouring flows are shared.

## Step 2: explanation stability (SHAP, mean over seeds)
| pool | tier agreement: Spearman / cosine / top-10 Jaccard | noise floor (same tier, different seeds): Spearman / cosine / top-10 Jaccard |
|---|---|---|
| 40 | 0.869-0.990 (mean 0.920) / 0.966-0.999 / 0.818-1.000 | 0.935-0.980 / 0.988-0.992 / 0.812-1.000 |
| 45 | 0.900-0.991 (mean 0.952) / 0.969-0.999 / 0.727-0.891 | 0.932-0.977 / 0.988-0.992 / 0.758-0.927 |
| 48 | 0.916-0.992 (mean 0.952) / 0.978-0.999 / 0.727-0.964 | 0.946-0.975 / 0.991-0.993 / 0.788-0.927 |

Caption. Explanations of tiers of the same seed agree at Spearman 0.87-0.99, about as well as the same tier retrained under another seed (0.93-0.98). The largest tier gaps (15 features vs the full tier: 0.87-0.92)
sit slightly below the floor; the 30-feature tier is indistinguishable from the full tier (0.97-0.99). Earlier study: tier agreement 0.83-0.99, noise floor 0.98-0.99. Protocol changes: 1,000 instead of 2,000 explained rows,
and a seed now also changes the block-grouped split, so the floor includes training-subset variation (hence the lower floor).

## What stability does and does not show
Stable explanations are evidence that XGBoost's feature attributions are reproducible across retraining and feature-set size. They say nothing about the cause of the official-split shift,
which remains undetermined.

## What did not hold
- "Shrinking to 15 features costs no more than retraining noise": not supported beyond 30 features (z 2.3-8.9 at 20 / 15, the open-set detection halves).
- The mutual-information ranking is not reliably better than random subsets (only at 30 features of the 40-feature pool).
- The window-count ct_* columns, which the few-shot result needed, do not survive into the small tiers.

## One paragraph
Shrinking the feature set barely changes XGBoost on the official split down to 30 features (macro F1 within 0.003 on every pool) and the SHAP explanations stay as stable as retraining makes them
(Spearman 0.97-0.99 against the full model); at 20 or 15 features accuracy drops by 0.006-0.014 macro F1 and the open-set detection halves, and the smaller tiers' explanations agree slightly less (0.87-0.92) than the retraining floor.
The ranking is not reliably better than random subsets, the window-count connection columns disappear below 30 features, and the random validation split is too optimistic to select anything with (block-grouped
validation predicts the test FPR to within 0.03-0.05). Whether other model families agree on what matters was left to their owners; stability of the explanations says nothing about why the official split is harder.
