# Task 6 conclusion: cross-dataset generalisation UNSW-NB15 <-> CICIDS2017 (novelty 4), XGBoost

Binary attack-vs-normal on the 14 common features (8 raw + 6 engineered; no `ct_*` window count among them), seeds 42-46 (and 5 adaptation draws per seed in Step 4), mean +/- std. Protocol, every method, the primary metric and the success level were declared before any result
(`results/task_6_protocol.md`). **Leak-free for both datasets:** blocks of 1,000 consecutive rows in file order, 200-row gaps between groups, no adaptation row ever evaluated; CICIDS2017 is the eight day files concatenated in file order (Friday-DDoS, Friday-PortScan, Friday-Morning, Monday, Thursday-Afternoon,
Thursday-Morning, Tuesday, Wednesday; verified against the original sizes), streamed once and cached. Primary metric: FPR at about 95% detection on the target evaluation blocks, with the threshold chosen on the source validation blocks (zero-shot) or the held-out labelled half (few-shot), always printed with the detection reached;
also balanced accuracy, AUROC and the threshold-free FPR at exactly 95% detection. Tables: `cross_dataset_step1_zero_shot.md` ... `cross_dataset_step4_fewshot.md`.

## The claim for novelty 4
**Zero-shot transfer between UNSW-NB15 and CICIDS2017 does not work on the common flow features, in either direction, under a leak-free protocol** (AUROC 0.49 UNSW to CIC and 0.58 CIC to UNSW, against 0.997 and 0.972 for a model trained on the target's own blocks). The common features carry weak or inconsistent attack signal:
of 14, 7 point in opposite directions in the two datasets and 11 are near 0.5 in at least one of them. Label-free alignment recovers part of the gap in one direction (UNSW to CIC, AUROC 0.79) and none in the other. Transfer takes labelled target flows: for CICIDS2017 about **1,000** (FPR at or below 0.15 at about 95% detection) and
for UNSW-NB15 about 1,000-5,000 to match its own ceiling (which itself has FPR 0.21 on these 14 features); and **the source data does not help** beyond a hundred labelled rows (target-only is as good or better from k = 500). The SHAP-selected "stable" feature set is **not** better than random subsets of its size.

## Step 1: leak-free zero-shot baseline (ZERO-SHOT; `stable` uses target labels and is not zero-shot)
| target = evaluation blocks | UNSW -> CIC: balanced acc. | AUROC | FPR at the source threshold (detection) | FPR at exactly 95% det. | attack share | CIC -> UNSW: balanced acc. | AUROC | FPR at the source threshold (detection) | FPR at exactly 95% det. | attack share |
|---|---|---|---|---|---|---|---|---|---|---|
| common_all (14 features) | 0.492 +/- 0.036 | 0.485 +/- 0.023 | 0.786 (0.845) | 0.926 | 0.69 | 0.502 (4 of 5 runs degenerate) | 0.578 +/- 0.019 | 0.000 (0.000) | 0.927 | 0.003 |
| source_only (top 10 by SHAP) | 0.521 | 0.466 +/- 0.041 | 0.795 (0.817) | 0.933 | 0.75 | degenerate | 0.551 +/- 0.046 | 0.000 (0.000) | 0.957 | 0.001 |
| stable (top 10 on both; target-label informed) | 0.502 | 0.499 +/- 0.051 | 0.750 (0.771) | 0.935 | 0.69 | degenerate | 0.521 +/- 0.044 | 0.000 (0.000) | 0.968 | 0.001 |
| random subsets of the same size (10 per seed, 7-9 features) | 0.487 | 0.482 +/- 0.068 | 0.710 (0.697) | 0.899 | 0.64 | 0.531 | 0.541 +/- 0.075 | 0.001 (0.007) | 0.926 | 0.005 |
| leak-free within-dataset reference | 0.975 +/- 0.005 | 0.997 +/- 0.002 | 0.006 (0.915) | 0.014 | 0.20 | 0.896 +/- 0.011 | 0.972 +/- 0.006 | 0.159 (0.947) | 0.163 | 0.45 |
Caption. UNSW to CIC is below chance: the model flags 69% of CICIDS2017 flows as attacks (CIC is 80% benign), so its high recall of individual attack types (DoS Hulk 0.82, DDoS 0.65, PortScan 0.53) is only the rate at which it flags everything, against a benign false-positive rate of 0.79. CIC to UNSW is degenerate: it predicts almost
no attacks (0.3%) and detects none at the source threshold. The within-dataset references are no longer inflated by neighbouring flows: 0.975 (CIC) and 0.896 (UNSW) balanced accuracy, against 0.981 and 0.902 for the earlier random split, so on these 14 features the earlier references were only slightly optimistic; even the CIC reference cannot find web attacks (recall 0.01-0.06) or Bot (0.37) from flow size and timing alone.
**Stable against random** (same size, 5 seeds): AUROC better in 2 of 5 seeds in each direction, mean difference +0.017 (95% interval -0.064, +0.097) UNSW to CIC and -0.020 (-0.080, +0.041) CIC to UNSW, against a spread of 0.07 between random subsets; FPR at exactly 95% detection +0.036 and +0.042 (worse, not better). Under the declared rule (a majority of seeds and an interval excluding 0) "stable beats random" is **no** in both directions.
CIC block mix: 2,831 blocks, 1,308 contain an attack; Monday (530 blocks) is pure benign; attack types sit in day-bounded bursts (e.g. DDoS, PortScan on Friday, the DoS family on Wednesday); Infiltration, SQL Injection and Heartbleed have too few evaluation rows (11 or fewer) for a per-type recall.

## Step 2: why zero-shot fails (diagnostic)
| | result |
|---|---|
| common features whose attack-vs-normal AUROC points the same way in both datasets | 7 of 14 |
| ... point opposite ways | 7 of 14 (only dmean clearly: attack flows have higher mean packet size from the destination in CIC, AUROC 0.56, lower in UNSW, 0.30) |
| features near 0.5 (absent, |AUROC - 0.5| < 0.05) in at least one dataset | 11 of 14 |
| features with a clear signal pointing the same way in both | rate (0.44 / 0.44), sbytes (0.36 / 0.42) |
| SHAP importance rank agreement, UNSW-trained vs CIC-trained model (Spearman, 5 seeds) | 0.52 +/- 0.06 |
| largest feature shifts (KS, from the earlier table) | smean 0.72, sbytes 0.69, total_pkts 0.64 |
Caption. A model trained on UNSW learns that large, fast flows are attacks; in CICIDS2017 the relationship is different or absent for most of the 14 features, so the learned rule is wrong or empty. CIC to UNSW fails the other way (the UNSW flows look benign to a CIC model, hence no attacks predicted). The two models rank the features only moderately alike (0.52), which is why choosing features by one dataset's SHAP ranking does not carry over.

## Step 3: label-free alignment (TRANSDUCTIVE: uses the unlabelled target features), against the zero-shot baseline
| UNSW -> CIC (5 seeds) | balanced acc. | AUROC | FPR at the source threshold (detection) | FPR at exactly 95% det. |
|---|---|---|---|---|
| baseline common_all (ZERO-SHOT) | 0.492 | 0.485 | 0.786 (0.845) | 0.926 |
| per-dataset standardisation | 0.550 | **0.785** | 0.139 (0.359) | **0.410** |
| quantile mapping | 0.627 | 0.720 | 0.723 (0.960) | 0.683 |
| drop the 3 / 5 most-shifted features | 0.500 / 0.508 | 0.524 / 0.512 | 0.726 / 0.651 | 0.862 / 0.850 |
| quantile mapping + drop 3 | 0.628 | 0.727 | 0.728 (0.976) | 0.681 |
| **CIC -> UNSW** | | | | |
| baseline common_all | 0.502 (4 of 5 degenerate) | 0.578 | 0.000 (0.000) | 0.927 |
| per-dataset standardisation | 0.511 (2 of 5 degenerate) | 0.581 | 0.005 (0.013) | 0.926 |
| quantile mapping | 0.474 | 0.566 | 0.054 (0.029) | 0.922 |
| drop the 3 / 5 most-shifted features | 0.502 / degenerate | 0.545 / 0.624 | 0.000 / 0.001 | 0.971 / 0.793 |
Caption. Putting each dataset on its own scale (a label-free step) lifts UNSW to CIC from below chance to AUROC 0.79 and halves the FPR at exactly 95% detection (0.93 to 0.41), so a large part of the zero-shot failure is a scale mismatch; but the threshold chosen on the source no longer transfers (detection 0.36), the result is still far from the reference (AUROC 0.997, FPR 0.014), and
nothing helps in the other direction. Dropping the most shifted features does little.

## Step 4: few-shot curve, both directions (FEW-SHOT; random selection shown, diverse in the table file; 25 runs per cell; k labelled target rows, half fit / half choose the threshold)
| k | UNSW -> CIC: source+target FPR | target-only FPR | target-only AUROC | CIC -> UNSW: source+target FPR | target-only FPR | target-only balanced acc. |
|---|---|---|---|---|---|---|
| 0 (zero-shot) | 0.786 (det 0.84) | n/a | n/a | 0.000 (det 0.00) | n/a | n/a |
| 100 | 0.604 | 0.508 | 0.822 | 0.554 | 0.575 | 0.687 |
| 500 | 0.326 | 0.169 | 0.968 | 0.345 | 0.356 | 0.801 |
| 1,000 | 0.187 | **0.096** | 0.981 | 0.292 | 0.296 | 0.830 |
| 5,000 | 0.030 | 0.022 | 0.994 | 0.245 | 0.235 | 0.858 |
| 10,000 | 0.021 | 0.017 | 0.995 | 0.232 | 0.224 | 0.865 |
| leak-free reference | 0.019 (AUROC 0.997, bal. 0.976) | | | 0.210 (AUROC 0.960, bal. 0.876) | | |
Caption. **CICIDS2017 as the target:** FPR at or below 0.15 with detection of at least 0.90 is reached at **k = 1,000** by the target-only model (FPR 0.10, detection 0.95) and at k = 5,000 with the source data added; 500 rows are close (0.17). **UNSW-NB15 as the target:** FPR never gets below 0.22 even with 10,000 rows, and the leak-free reference trained on 50,000 rows has FPR 0.21, so on these 14 features UNSW is
intrinsically hard (the earlier few-shot FPR of 0.09 within UNSW used the 48 features including the `ct_*` window counts, which are not common); the balanced-accuracy criterion (within 0.05 of the reference) is reached at k = 1,000 target-only and 5,000 with source data. **The source data does not help:** source+target is worse than target-only for CIC at every k (FPR +0.02 to +0.16 at k <= 1,000) and equal or slightly worse for UNSW from k = 500; the only gain is on
UNSW at k = 100 (AUROC 0.81 against 0.75, FPR -0.08 with diverse selection, the only cell where the paired interval excludes 0). Diverse (k-means) selection, which beat random selection within UNSW in Task 2.7, gives no advantage here (CIC target-only k = 1,000: FPR 0.108 against 0.096).

## What it takes to transfer, what did not work, and the limits
- Zero-shot transfer fails in both directions; the UNSW-NB15 within-dataset ceiling on the 14 common features (FPR 0.16-0.21) is itself modest, and web attacks, Bot and SSH-Patator are barely detectable in CIC from these features even with all labels.
- The SHAP-selected "stable" set is no better than random subsets of its size (and it uses target labels to be built); the earlier single-run claims about feature strategies are not supported.
- Label-free alignment (per-dataset standardisation) helps in one direction only, and only for ranking (AUROC), not for the operating point.
- Limits: adaptation and evaluation blocks come from the same capture days, so a CIC result at k = 1,000 is within-capture (same day, same attackers), not a held-out day or network; the few-shot CIC evaluation uses a 25% sample of the evaluation blocks; per-type recall in the few-shot curve was not computed; the 14 common features exclude the `ct_*` window counts that mattered within UNSW.

## One paragraph
The model does not transfer zero-shot: under a protocol with no neighbouring-flow leakage on either side, a UNSW-trained model scores at chance on CICIDS2017 (AUROC 0.49, flagging 69% of flows) and a CIC-trained model detects nothing on UNSW-NB15 (AUROC 0.58, 0.3% flagged), because most of the 14 common features either carry no attack signal in one of the datasets (11 of 14) or point
the opposite way (7 of 14), and part of the UNSW to CIC failure is a scale mismatch that per-dataset standardisation removes for ranking (AUROC 0.79) but not for the operating point. Transfer takes labelled target flows: about 1,000 for CICIDS2017 to reach FPR 0.10 at 95% detection, and for UNSW-NB15 about 1,000-5,000 to reach its own ceiling (FPR 0.21 on these 14 features); the source data does not help beyond
a hundred rows, since a model trained only on the same few labelled target rows is as good or better from k = 500. The SHAP-selected "stable" feature set does not beat random subsets of the same size (better in 2 of 5 seeds in each direction). These are within-capture results on two datasets; transfer to another day or network was not tested.
