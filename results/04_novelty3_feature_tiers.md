# Novelty 3: feature tiers and explanation stability

The tier study and the stability of SHAP explanations across tiers: conclusion, tables and the declared protocol. The shared rules and commands for running the same study with another model are in `PROTOCOL.md` and `ONBOARDING.md`; the XGBoost SHAP files used for the cross-model comparison are `metrics/xgboost/shap_importance_xgboost_<N>f.csv` and `shap_boot_xgboost_<N>f.npz`.

File names mentioned inside this file (for example `task_6_tables.md`, `results/task_5_protocol.md` or `xai_audit_40f_example_failures.csv`) are the `Source:` sections of this file or of one of the other numbered files, or files that were removed in the cleanup and are recoverable from the git tags `pre-cleanup-2026-10` and `pre-lean-2026-10`. Text under a `Source:` heading is the original file, unchanged except that its headings are demoted two levels. Two kinds of file moved after the originals were written: the feature rankings are now in `results/rankings/` and the A/B rating sheet, key and instructions in `results/rating/`.

## Source: task_3_conclusion.md

### Task 3 conclusion: feature selection and explanation consistency (novelty 3), XGBoost

Zero-shot throughout (training data only); official split, scheme `current`; seeds 42-46, mean +/- std. Training / validation come from contiguous
blocks of the training file (1,000-row blocks, 200-row gaps), because a random validation split shares neighbouring flows with the training rows and is
optimistic. Protocol declared before any result: `results/task_3_protocol.md` (two amendments: the other model families are teammates' and are not run here).
Tables: `task_3_tables.md` (sections `tier_summary_xgboost.md` for Step 1 and `stability_xgboost.md` for Step 2; per-tier CSVs `tier_summary_xgboost_<N>f.csv`, `stability_xgboost_<N>f.csv`). Steps 3 and 4 (other model families, cross-model agreement) are not part of
this work package; `pipelines/run_tier_study.py --model <type>` and `scripts/cross_model_agreement.py` are ready, with the same rankings, seeds and splits.

#### The claim for novelty 3
Shrinking the XGBoost feature set to the top 30 mutual-information features costs no measurable accuracy (macro F1 within 0.003 of the full 40 / 45 / 48-feature pool,
all three pools) and leaves the SHAP explanation as stable as retraining does (30-feature tier vs the full tier Spearman 0.97-0.99 against a same-tier / different-seed floor of
0.97-0.98). Going down to 20 or 15 features costs 0.006-0.014 macro F1 (statistically clear, still under 0.02), about 0.02 FPR and roughly half of the open-set
detection, and the 15-feature explanations agree with the full model's slightly below the retraining floor. The earlier headline "shrinking to 15 features costs no
more than retraining noise" therefore holds to 30 features only.

#### Step 1: tier study (official split; macro F1 / FPR / open-set detection, mean over 5 seeds)
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

#### Step 2: explanation stability (SHAP, mean over seeds)
| pool | tier agreement: Spearman / cosine / top-10 Jaccard | noise floor (same tier, different seeds): Spearman / cosine / top-10 Jaccard |
|---|---|---|
| 40 | 0.869-0.990 (mean 0.920) / 0.966-0.999 / 0.818-1.000 | 0.935-0.980 / 0.988-0.992 / 0.812-1.000 |
| 45 | 0.900-0.991 (mean 0.952) / 0.969-0.999 / 0.727-0.891 | 0.932-0.977 / 0.988-0.992 / 0.758-0.927 |
| 48 | 0.916-0.992 (mean 0.952) / 0.978-0.999 / 0.727-0.964 | 0.946-0.975 / 0.991-0.993 / 0.788-0.927 |

Caption. Explanations of tiers of the same seed agree at Spearman 0.87-0.99, about as well as the same tier retrained under another seed (0.93-0.98). The largest tier gaps (15 features vs the full tier: 0.87-0.92)
sit slightly below the floor; the 30-feature tier is indistinguishable from the full tier (0.97-0.99). Earlier study: tier agreement 0.83-0.99, noise floor 0.98-0.99. Protocol changes: 1,000 instead of 2,000 explained rows,
and a seed now also changes the block-grouped split, so the floor includes training-subset variation (hence the lower floor).

#### What stability does and does not show
Stable explanations are evidence that XGBoost's feature attributions are reproducible across retraining and feature-set size. They say nothing about the cause of the official-split shift,
which remains undetermined.

#### What did not hold
- "Shrinking to 15 features costs no more than retraining noise": not supported beyond 30 features (z 2.3-8.9 at 20 / 15, the open-set detection halves).
- The mutual-information ranking is not reliably better than random subsets (only at 30 features of the 40-feature pool).
- The window-count ct_* columns, which the few-shot result needed, do not survive into the small tiers.

#### One paragraph
Shrinking the feature set barely changes XGBoost on the official split down to 30 features (macro F1 within 0.003 on every pool) and the SHAP explanations stay as stable as retraining makes them
(Spearman 0.97-0.99 against the full model); at 20 or 15 features accuracy drops by 0.006-0.014 macro F1 and the open-set detection halves, and the smaller tiers' explanations agree slightly less (0.87-0.92) than the retraining floor.
The ranking is not reliably better than random subsets, the window-count connection columns disappear below 30 features, and the random validation split is too optimistic to select anything with (block-grouped
validation predicts the test FPR to within 0.03-0.05). Whether other model families agree on what matters was left to their owners; stability of the explanations says nothing about why the official split is harder.

## Source: tier_summary_xgboost.md

### Task 3 Step 1: tier study, xgboost (official split, block-grouped validation, mean +/- std over 5 seeds)

Ranked top-N tiers (mutual information on the training split). `det95 FPR` is the 95%-detection operating point chosen on the BLOCK-GROUPED validation split. The pooled random split is a best case: it shares neighbouring flows with its training rows and is optimistic. `noise` / `practical`: macro F1 drop from the full pool within 2 x seed std / within 0.02.

#### 40f

| tier | features | macro F1 | accuracy | FPR | det95 FPR | det95 detection | ROC-AUC | ECE | open-set det. | open-set AUROC | pooled macro F1 (best case) | drop F1 | z | noise | practical | ct window / other / TTL cols |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | 40 | 0.7113 +/- 0.0029 | 0.7398 +/- 0.0065 | 0.2899 +/- 0.0119 | 0.2573 +/- 0.0113 | 0.9509 +/- 0.0036 | 0.9629 +/- 0.0010 | 0.0934 +/- 0.0087 | 0.2311 +/- 0.0520 | 0.7986 +/- 0.0034 | 0.7810 +/- 0.0010 | +0.0000 | 0.0 | yes | yes | 2 / 2 / 0 |
| 30 | 30 | 0.7141 +/- 0.0033 | 0.7403 +/- 0.0064 | 0.2924 +/- 0.0114 | 0.2588 +/- 0.0111 | 0.9514 +/- 0.0029 | 0.9630 +/- 0.0012 | 0.0929 +/- 0.0087 | 0.2295 +/- 0.0585 | 0.7973 +/- 0.0041 | 0.7806 +/- 0.0019 | -0.0028 | -1.4 | yes | yes | 2 / 0 / 0 |
| 20 | 20 | 0.6973 +/- 0.0021 | 0.7260 +/- 0.0058 | 0.3123 +/- 0.0109 | 0.2637 +/- 0.0081 | 0.9539 +/- 0.0014 | 0.9601 +/- 0.0015 | 0.0969 +/- 0.0079 | 0.1866 +/- 0.0428 | 0.7595 +/- 0.0059 | 0.7658 +/- 0.0019 | +0.0141 | 8.9 | NO | yes | 0 / 0 / 0 |
| 15 | 15 | 0.6986 +/- 0.0027 | 0.7254 +/- 0.0062 | 0.3160 +/- 0.0113 | 0.2604 +/- 0.0104 | 0.9537 +/- 0.0017 | 0.9605 +/- 0.0013 | 0.0977 +/- 0.0083 | 0.1918 +/- 0.0497 | 0.7591 +/- 0.0047 | 0.7675 +/- 0.0018 | +0.0128 | 7.2 | NO | yes | 0 / 0 / 0 |

Ranked vs 10 random subsets vs worst-N (40f, macro F1):

| tier | ranked | random mean +/- std (min-max) | worst | ranked percentile | z |
|---|---|---|---|---|---|
| 30 | 0.7141 | 0.7049 +/- 0.0035 (0.6977-0.7101) | 0.6236 | 100 | 2.68 |
| 20 | 0.6973 | 0.6985 +/- 0.0051 (0.6881-0.7044) | 0.6183 | 20 | -0.24 |
| 15 | 0.6986 | 0.6804 +/- 0.0414 (0.5655-0.7002) | 0.5089 | 70 | 0.44 |

#### 45f

| tier | features | macro F1 | accuracy | FPR | det95 FPR | det95 detection | ROC-AUC | ECE | open-set det. | open-set AUROC | pooled macro F1 (best case) | drop F1 | z | noise | practical | ct window / other / TTL cols |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 45 | 45 | 0.7065 +/- 0.0048 | 0.7332 +/- 0.0067 | 0.2988 +/- 0.0118 | 0.2482 +/- 0.0127 | 0.9436 +/- 0.0041 | 0.9593 +/- 0.0031 | 0.1155 +/- 0.0093 | 0.3642 +/- 0.0609 | 0.8310 +/- 0.0102 | 0.7929 +/- 0.0010 | +0.0000 | 0.0 | yes | yes | 7 / 2 / 0 |
| 40 | 40 | 0.7052 +/- 0.0053 | 0.7327 +/- 0.0071 | 0.2992 +/- 0.0120 | 0.2501 +/- 0.0124 | 0.9457 +/- 0.0045 | 0.9598 +/- 0.0031 | 0.1157 +/- 0.0090 | 0.3567 +/- 0.0484 | 0.8285 +/- 0.0107 | 0.7930 +/- 0.0011 | +0.0013 | 0.4 | yes | yes | 7 / 0 / 0 |
| 30 | 30 | 0.7057 +/- 0.0038 | 0.7341 +/- 0.0065 | 0.2957 +/- 0.0117 | 0.2534 +/- 0.0113 | 0.9459 +/- 0.0046 | 0.9598 +/- 0.0030 | 0.1142 +/- 0.0090 | 0.3369 +/- 0.0372 | 0.8224 +/- 0.0064 | 0.7929 +/- 0.0018 | +0.0008 | 0.3 | yes | yes | 4 / 0 / 0 |
| 20 | 20 | 0.6976 +/- 0.0024 | 0.7255 +/- 0.0063 | 0.3135 +/- 0.0116 | 0.2665 +/- 0.0085 | 0.9548 +/- 0.0017 | 0.9600 +/- 0.0015 | 0.0974 +/- 0.0084 | 0.1844 +/- 0.0441 | 0.7590 +/- 0.0043 | 0.7663 +/- 0.0015 | +0.0089 | 3.7 | yes | yes | 0 / 0 / 0 |
| 15 | 15 | 0.6972 +/- 0.0038 | 0.7220 +/- 0.0075 | 0.3224 +/- 0.0132 | 0.2653 +/- 0.0118 | 0.9546 +/- 0.0030 | 0.9597 +/- 0.0015 | 0.0981 +/- 0.0104 | 0.1977 +/- 0.0538 | 0.7626 +/- 0.0085 | 0.7669 +/- 0.0024 | +0.0093 | 3.4 | yes | yes | 0 / 0 / 0 |

Ranked vs 10 random subsets vs worst-N (45f, macro F1):

| tier | ranked | random mean +/- std (min-max) | worst | ranked percentile | z |
|---|---|---|---|---|---|
| 30 | 0.7057 | 0.7054 +/- 0.0024 (0.7022-0.7102) | 0.6179 | 70 | 0.13 |
| 20 | 0.6976 | 0.7007 +/- 0.0048 (0.6934-0.7109) | 0.5589 | 20 | -0.64 |
| 15 | 0.6972 | 0.6812 +/- 0.0545 (0.5271-0.7069) | 0.4752 | 40 | 0.29 |

#### 48f

| tier | features | macro F1 | accuracy | FPR | det95 FPR | det95 detection | ROC-AUC | ECE | open-set det. | open-set AUROC | pooled macro F1 (best case) | drop F1 | z | noise | practical | ct window / other / TTL cols |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 48 | 48 | 0.7126 +/- 0.0047 | 0.7377 +/- 0.0061 | 0.2976 +/- 0.0120 | 0.2467 +/- 0.0098 | 0.9529 +/- 0.0042 | 0.9634 +/- 0.0028 | 0.1144 +/- 0.0086 | 0.3479 +/- 0.0477 | 0.8353 +/- 0.0063 | 0.7982 +/- 0.0008 | +0.0000 | 0.0 | yes | yes | 7 / 2 / 3 |
| 40 | 40 | 0.7125 +/- 0.0053 | 0.7359 +/- 0.0064 | 0.3008 +/- 0.0114 | 0.2480 +/- 0.0138 | 0.9504 +/- 0.0045 | 0.9629 +/- 0.0027 | 0.1162 +/- 0.0088 | 0.3305 +/- 0.0447 | 0.8331 +/- 0.0080 | 0.7987 +/- 0.0019 | +0.0001 | 0.0 | yes | yes | 7 / 0 / 3 |
| 30 | 30 | 0.7129 +/- 0.0022 | 0.7378 +/- 0.0055 | 0.2992 +/- 0.0109 | 0.2551 +/- 0.0111 | 0.9428 +/- 0.0046 | 0.9586 +/- 0.0021 | 0.1105 +/- 0.0087 | 0.3469 +/- 0.0393 | 0.8248 +/- 0.0053 | 0.7885 +/- 0.0014 | -0.0002 | -0.1 | yes | yes | 2 / 0 / 3 |
| 20 | 20 | 0.7063 +/- 0.0029 | 0.7307 +/- 0.0064 | 0.3126 +/- 0.0117 | 0.2572 +/- 0.0109 | 0.9554 +/- 0.0020 | 0.9620 +/- 0.0012 | 0.0959 +/- 0.0084 | 0.1902 +/- 0.0559 | 0.7611 +/- 0.0067 | 0.7725 +/- 0.0025 | +0.0063 | 2.6 | yes | yes | 0 / 0 / 3 |
| 15 | 15 | 0.7067 +/- 0.0034 | 0.7272 +/- 0.0074 | 0.3213 +/- 0.0137 | 0.2557 +/- 0.0124 | 0.9564 +/- 0.0036 | 0.9630 +/- 0.0013 | 0.0970 +/- 0.0103 | 0.1942 +/- 0.0546 | 0.7635 +/- 0.0102 | 0.7753 +/- 0.0022 | +0.0060 | 2.3 | yes | yes | 0 / 0 / 3 |

Ranked vs 10 random subsets vs worst-N (48f, macro F1):

| tier | ranked | random mean +/- std (min-max) | worst | ranked percentile | z |
|---|---|---|---|---|---|
| 30 | 0.7129 | 0.7080 +/- 0.0043 (0.7008-0.7127) | 0.6185 | 100 | 1.16 |
| 20 | 0.7063 | 0.6835 +/- 0.0436 (0.5686-0.7077) | 0.5597 | 80 | 0.52 |
| 15 | 0.7067 | 0.6644 +/- 0.0641 (0.5448-0.7082) | 0.4746 | 80 | 0.66 |

## Source: stability_xgboost.md

### Task 3 Step 2: explanation stability, xgboost (mean over seeds 42-46; zero-shot)

Tier agreement = SHAP importance of two tiers of the same seed; noise floor = the same tier under two seeds. Spearman rank correlation / cosine / top-10 Jaccard. Stability is evidence about the explanations, not about the cause of the official-split shift.

#### 40f

Tier agreement: Spearman 0.869-0.990 (mean 0.920), cosine 0.966-0.999, top-10 Jaccard 0.818-1.000. Noise floor (same tier, different seeds): Spearman 0.935-0.980, cosine 0.988-0.992, top-10 Jaccard 0.812-1.000.

| comparison | a | b | common features | Spearman | cosine | top-10 Jaccard |
|---|---|---|---|---|---|---|
| tier_pair | 40 | 30 | 30 | 0.990 +/- 0.004 | 0.999 +/- 0.001 | 0.855 +/- 0.081 |
| tier_pair | 40 | 20 | 20 | 0.936 +/- 0.023 | 0.988 +/- 0.003 | 1.000 +/- 0.000 |
| tier_pair | 40 | 15 | 15 | 0.871 +/- 0.029 | 0.966 +/- 0.003 | 0.855 +/- 0.081 |
| tier_pair | 30 | 20 | 20 | 0.938 +/- 0.021 | 0.989 +/- 0.002 | 1.000 +/- 0.000 |
| tier_pair | 30 | 15 | 15 | 0.869 +/- 0.031 | 0.967 +/- 0.003 | 0.818 +/- 0.000 |
| tier_pair | 20 | 15 | 15 | 0.917 +/- 0.017 | 0.977 +/- 0.001 | 1.000 +/- 0.000 |
| same_tier_seeds | 40 | 40 | 40 | 0.980 +/- 0.007 | 0.988 +/- 0.006 | 0.812 +/- 0.145 |
| same_tier_seeds | 30 | 30 | 30 | 0.978 +/- 0.008 | 0.988 +/- 0.007 | 0.873 +/- 0.088 |
| same_tier_seeds | 20 | 20 | 20 | 0.952 +/- 0.023 | 0.988 +/- 0.006 | 1.000 +/- 0.000 |
| same_tier_seeds | 15 | 15 | 15 | 0.935 +/- 0.030 | 0.992 +/- 0.004 | 1.000 +/- 0.000 |

#### 45f

Tier agreement: Spearman 0.900-0.991 (mean 0.952), cosine 0.969-0.999, top-10 Jaccard 0.727-0.891. Noise floor (same tier, different seeds): Spearman 0.932-0.977, cosine 0.988-0.992, top-10 Jaccard 0.758-0.927.

| comparison | a | b | common features | Spearman | cosine | top-10 Jaccard |
|---|---|---|---|---|---|---|
| tier_pair | 45 | 40 | 40 | 0.991 +/- 0.003 | 0.999 +/- 0.000 | 0.855 +/- 0.081 |
| tier_pair | 45 | 30 | 30 | 0.980 +/- 0.003 | 0.997 +/- 0.000 | 0.788 +/- 0.068 |
| tier_pair | 45 | 20 | 20 | 0.962 +/- 0.018 | 0.988 +/- 0.002 | 0.855 +/- 0.081 |
| tier_pair | 45 | 15 | 15 | 0.900 +/- 0.045 | 0.969 +/- 0.007 | 0.727 +/- 0.083 |
| tier_pair | 40 | 30 | 30 | 0.979 +/- 0.003 | 0.997 +/- 0.000 | 0.818 +/- 0.000 |
| tier_pair | 40 | 20 | 20 | 0.965 +/- 0.015 | 0.989 +/- 0.003 | 0.891 +/- 0.100 |
| tier_pair | 40 | 15 | 15 | 0.900 +/- 0.045 | 0.971 +/- 0.006 | 0.727 +/- 0.083 |
| tier_pair | 30 | 20 | 20 | 0.962 +/- 0.013 | 0.989 +/- 0.002 | 0.818 +/- 0.000 |
| tier_pair | 30 | 15 | 15 | 0.921 +/- 0.039 | 0.976 +/- 0.004 | 0.891 +/- 0.100 |
| tier_pair | 20 | 15 | 15 | 0.961 +/- 0.023 | 0.988 +/- 0.004 | 0.891 +/- 0.100 |
| same_tier_seeds | 45 | 45 | 45 | 0.977 +/- 0.006 | 0.990 +/- 0.006 | 0.758 +/- 0.078 |
| same_tier_seeds | 40 | 40 | 40 | 0.972 +/- 0.009 | 0.990 +/- 0.005 | 0.818 +/- 0.000 |
| same_tier_seeds | 30 | 30 | 30 | 0.977 +/- 0.009 | 0.992 +/- 0.004 | 0.855 +/- 0.077 |
| same_tier_seeds | 20 | 20 | 20 | 0.961 +/- 0.018 | 0.988 +/- 0.006 | 0.927 +/- 0.094 |
| same_tier_seeds | 15 | 15 | 15 | 0.932 +/- 0.033 | 0.991 +/- 0.006 | 0.891 +/- 0.094 |

#### 48f

Tier agreement: Spearman 0.916-0.992 (mean 0.952), cosine 0.978-0.999, top-10 Jaccard 0.727-0.964. Noise floor (same tier, different seeds): Spearman 0.946-0.975, cosine 0.991-0.993, top-10 Jaccard 0.788-0.927.

| comparison | a | b | common features | Spearman | cosine | top-10 Jaccard |
|---|---|---|---|---|---|---|
| tier_pair | 48 | 40 | 40 | 0.992 +/- 0.003 | 0.999 +/- 0.000 | 0.964 +/- 0.081 |
| tier_pair | 48 | 30 | 30 | 0.974 +/- 0.010 | 0.991 +/- 0.003 | 0.927 +/- 0.100 |
| tier_pair | 48 | 20 | 20 | 0.952 +/- 0.012 | 0.985 +/- 0.003 | 0.788 +/- 0.068 |
| tier_pair | 48 | 15 | 15 | 0.916 +/- 0.018 | 0.979 +/- 0.005 | 0.727 +/- 0.083 |
| tier_pair | 40 | 30 | 30 | 0.977 +/- 0.009 | 0.990 +/- 0.003 | 0.964 +/- 0.081 |
| tier_pair | 40 | 20 | 20 | 0.950 +/- 0.011 | 0.984 +/- 0.003 | 0.758 +/- 0.083 |
| tier_pair | 40 | 15 | 15 | 0.919 +/- 0.026 | 0.978 +/- 0.005 | 0.727 +/- 0.083 |
| tier_pair | 30 | 20 | 20 | 0.949 +/- 0.018 | 0.991 +/- 0.001 | 0.758 +/- 0.083 |
| tier_pair | 30 | 15 | 15 | 0.928 +/- 0.018 | 0.989 +/- 0.003 | 0.727 +/- 0.083 |
| tier_pair | 20 | 15 | 15 | 0.959 +/- 0.008 | 0.996 +/- 0.001 | 0.788 +/- 0.068 |
| same_tier_seeds | 48 | 48 | 48 | 0.975 +/- 0.009 | 0.993 +/- 0.005 | 0.788 +/- 0.064 |
| same_tier_seeds | 40 | 40 | 40 | 0.971 +/- 0.012 | 0.993 +/- 0.005 | 0.821 +/- 0.079 |
| same_tier_seeds | 30 | 30 | 30 | 0.969 +/- 0.012 | 0.991 +/- 0.005 | 0.927 +/- 0.094 |
| same_tier_seeds | 20 | 20 | 20 | 0.968 +/- 0.018 | 0.991 +/- 0.005 | 0.821 +/- 0.079 |
| same_tier_seeds | 15 | 15 | 15 | 0.946 +/- 0.033 | 0.992 +/- 0.005 | 0.873 +/- 0.088 |

## Source: task_3_protocol.md

### Task 3 protocol (declared before any Task 3 result was produced)

Novelty 3: feature selection and explanation consistency. Everything is ZERO-SHOT (training data only), official split, scheme `current`.

#### Design
- **Block-grouped validation.** The training / validation split of every run is built from contiguous blocks of the training file
  (block size 1,000 rows, 200-row gap on each side of every boundary, `data.val_size` = 15% of the blocks;
  `pipelines/train_pipeline.block_validation_splits`). A random validation split shares neighbouring flows with the training rows and is
  optimistic (Task 2.6); it is used only for comparison. The validation-chosen 95%-detection operating point (`det95`) is therefore chosen
  on the block-grouped validation split; the random-validation counterpart is quoted from the earlier headline / operating-point files for
  the full pools (40 / 48 features; the 45-feature pool is run once with `run_operating_point.py`).
- **Seeds 42-46** change the model seed and the block draw (which blocks are validation); the official test file is fixed.
- **Feature rankings:** mutual information with the target on the seed-42 block-grouped TRAINING split (20,000-row sample, seed 42), one ranking
  per pool, shared by all seeds and all three model types (so the tiers are the same feature sets for every model). Files:
  `results/feature_ranking_mutual_info_blockval[_40f|_45f|_48f].csv`. Tiers: 48 pool: 48 / 40 / 30 / 20 / 15; 45 pool: 45 / 40 / 30 / 20 / 15;
  40 pool: 40 / 30 / 20 / 15.
- **Pools:** 40 (34 raw + 6 engineered), 45 (48 minus sttl, dttl, ct_state_ttl), 48 (42 raw + 6 engineered).
- **Which extra official columns survive** is reported for every tier: the seven window-count ct_* columns, the other ct_* columns
  (ct_state_ttl, ct_flw_http_mthd, ct_ftp_cmd) and the TTL columns (sttl, dttl, ct_state_ttl).

#### Step 1 (XGBoost tier study)
- Primary metric: **macro F1** on the official test split (mean and std over the 5 seeds). Also accuracy, detection, FPR (argmax and block-validated
  det95), attack-vs-normal ROC-AUC, ECE, open-set detection and AUROC. The pooled random split is shown as a labelled best-case column
  (it shares neighbouring flows with its training rows and is optimistic).
- Claim tested: shrinking the feature set to 15 costs no more than retraining noise. Criterion A (noise): the mean macro F1 drop from the full pool
  is at most 2 x the seed-to-seed std of the full pool. Criterion B (practical): the drop is at most 0.02 macro F1. Both are reported for every tier;
  a tier failing A is reported as significantly worse (with the Welch z of the difference).
- Ranked tier vs 10 random subsets vs the worst-N features, for tiers 30 / 20 / 15 of each pool (macro F1; z-score and percentile of the ranked mean
  among the random draws, as in the earlier study). Random draws: model seed 42 on the seed-42 split, subset seed 42 + draw.

#### Step 2 (explanation stability, XGBoost)
- Global SHAP importance = mean |SHAP| over classes, on 1,000 random training rows (the earlier study used 2,000; reduced so the same rows can be
  explained for every model type in Step 4). Pairwise definitions kept from `src/xai/explanation_stability.py`: Spearman rank correlation,
  cosine similarity and top-10 Jaccard overlap over the common features. Tier agreement = pairs of tiers of the same seed; noise floor = the same
  tier under different seeds (all 10 pairs of the 5 seeds). Protocol change from the earlier study: the earlier noise floor kept the training rows
  fixed and changed only the model seed; here a seed also changes the block draw, so the floor includes training-subset variation.
- Descriptive bands (no threshold test): high >= 0.9, moderate 0.7-0.9, low < 0.7.

#### Step 3 (logistic regression, random forest)
Same grid, metrics and stability study. Declared settings (no tuning): random forest 150 trees, max depth 10, min leaf 5; logistic regression
`max_iter` 300 (lbfgs, balanced ** 0.5 sample weights as for XGBoost); inputs are the same scaled numeric / label-encoded categorical matrix
(logistic regression sees categorical codes as numbers, which XGBoost and the forest handle by splits). SHAP explainer: TreeExplainer for the forest,
LinearExplainer for logistic regression (background 100 rows). Random subsets / worst-N are run for XGBoost only. FPR on the official split is
reported for every model; nothing is tuned on test.

#### Step 4 (cross-model agreement)
For every pool, tier and seed, XGBoost vs logistic regression vs random forest global SHAP importance (Spearman, cosine, top-10 Jaccard), with
95% percentile intervals from 100 paired bootstrap resamples of the explained rows (the same 1,000 rows and the same resample indices for all
three models), averaged over the seeds. Whether agreement drops for the smaller tiers is read from these numbers.

#### Not claimed
Stability is evidence about the explanations, not about the cause of the official-split shift, which remains undetermined.

#### Amendment (declared before any Task 3 result was read)
Logistic regression belongs to a teammate's work package and is **not part of this task's results**: no logistic-regression tier study, stability or
agreement results are produced or kept. Its code path (`model_config`, the declared `max_iter` 300, the LinearExplainer route) stays in the repository and
is exercised by tests only. Steps 3 and 4 therefore compare XGBoost with the random forest (the Step 4 agreement is between those two models; the script
accepts any number of models). The random forest is run with the declared settings above.

#### Second amendment (declared before any Task 3 result was read)
The other model families (logistic regression, random forest) are teammates' work packages; this task's results are **XGBoost only**. Steps 3 and 4 (other
model families, cross-model agreement) are therefore not run here: no logistic-regression or random-forest tier, stability or agreement results are
produced or kept. The code for them (`model_config`, the declared per-family parameters, the SHAP paths, `scripts/cross_model_agreement.py`) stays in the
repository, tested on synthetic data, so a teammate can run `pipelines/run_tier_study.py --model <type>` and `scripts/cross_model_agreement.py` with the same
rankings, seeds and block-grouped validation and obtain comparable numbers. A partial random-forest run (40-feature pool only) was stopped and deleted.
