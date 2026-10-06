# Novelty 4: cross-dataset generalisation (UNSW-NB15 and CICIDS2017)

Leak-free zero-shot transfer, diagnostic, label-free alignment and the few-shot curve: conclusion, tables, the declared protocol, and the earlier random-split run that the leak-free study contradicts.

File names mentioned inside this file (for example `task_6_tables.md`, `results/task_5_protocol.md` or `xai_audit_40f_example_failures.csv`) are the `Source:` sections of this file or of one of the other numbered files, or files that were removed in the cleanup and are recoverable from the git tags `pre-cleanup-2026-10` and `pre-lean-2026-10`. Text under a `Source:` heading is the original file, unchanged except that its headings are demoted two levels. Two kinds of file moved after the originals were written: the feature rankings are now in `results/rankings/` and the A/B rating sheet, key and instructions in `results/rating/`.

## Source: task_6_conclusion.md

### Task 6 conclusion: cross-dataset generalisation UNSW-NB15 <-> CICIDS2017 (novelty 4), XGBoost

Binary attack-vs-normal on the 14 common features (8 raw + 6 engineered; no `ct_*` window count among them), seeds 42-46 (and 5 adaptation draws per seed in Step 4), mean +/- std. Protocol, every method, the primary metric and the success level were declared before any result
(`results/task_6_protocol.md`). **Leak-free for both datasets:** blocks of 1,000 consecutive rows in file order, 200-row gaps between groups, no adaptation row ever evaluated; CICIDS2017 is the eight day files concatenated in file order (Friday-DDoS, Friday-PortScan, Friday-Morning, Monday, Thursday-Afternoon,
Thursday-Morning, Tuesday, Wednesday; verified against the original sizes), streamed once and cached. Primary metric: FPR at about 95% detection on the target evaluation blocks, with the threshold chosen on the source validation blocks (zero-shot) or the held-out labelled half (few-shot), always printed with the detection reached;
also balanced accuracy, AUROC and the threshold-free FPR at exactly 95% detection. Tables: `task_6_tables.md` (sections `cross_dataset_step1_zero_shot.md` ... `cross_dataset_step4_fewshot.md`).

#### The claim for novelty 4
**Zero-shot transfer between UNSW-NB15 and CICIDS2017 does not work on the common flow features, in either direction, under a leak-free protocol** (AUROC 0.49 UNSW to CIC and 0.58 CIC to UNSW, against 0.997 and 0.972 for a model trained on the target's own blocks). The common features carry weak or inconsistent attack signal:
of 14, 7 point in opposite directions in the two datasets and 11 are near 0.5 in at least one of them. Label-free alignment recovers part of the gap in one direction (UNSW to CIC, AUROC 0.79) and none in the other. Transfer takes labelled target flows: for CICIDS2017 about **1,000** (FPR at or below 0.15 at about 95% detection) and
for UNSW-NB15 about 1,000-5,000 to match its own ceiling (which itself has FPR 0.21 on these 14 features); and **the source data does not help** beyond a hundred labelled rows (target-only is as good or better from k = 500). The SHAP-selected "stable" feature set is **not** better than random subsets of its size.

#### Step 1: leak-free zero-shot baseline (ZERO-SHOT; `stable` uses target labels and is not zero-shot)
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

#### Step 2: why zero-shot fails (diagnostic)
| | result |
|---|---|
| common features whose attack-vs-normal AUROC points the same way in both datasets | 7 of 14 |
| ... point opposite ways | 7 of 14 (only dmean clearly: attack flows have higher mean packet size from the destination in CIC, AUROC 0.56, lower in UNSW, 0.30) |
| features near 0.5 (absent, |AUROC - 0.5| < 0.05) in at least one dataset | 11 of 14 |
| features with a clear signal pointing the same way in both | rate (0.44 / 0.44), sbytes (0.36 / 0.42) |
| SHAP importance rank agreement, UNSW-trained vs CIC-trained model (Spearman, 5 seeds) | 0.52 +/- 0.05 |
| largest feature shifts (KS, from the earlier table) | smean 0.72, sbytes 0.69, total_pkts 0.64 |
Caption. A model trained on UNSW learns that large, fast flows are attacks; in CICIDS2017 the relationship is different or absent for most of the 14 features, so the learned rule is wrong or empty. CIC to UNSW fails the other way (the UNSW flows look benign to a CIC model, hence no attacks predicted). The two models rank the features only moderately alike (0.52), which is why choosing features by one dataset's SHAP ranking does not carry over.

#### Step 3: label-free alignment (TRANSDUCTIVE: uses the unlabelled target features), against the zero-shot baseline
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

#### Step 4: few-shot curve, both directions (FEW-SHOT; random selection shown, diverse in the table file; 25 runs per cell; k labelled target rows, half fit / half choose the threshold)
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

#### What it takes to transfer, what did not work, and the limits
- Zero-shot transfer fails in both directions; the UNSW-NB15 within-dataset ceiling on the 14 common features (FPR 0.16-0.21) is itself modest, and web attacks, Bot and SSH-Patator are barely detectable in CIC from these features even with all labels.
- The SHAP-selected "stable" set is no better than random subsets of its size (and it uses target labels to be built); the earlier single-run claims about feature strategies are not supported.
- Label-free alignment (per-dataset standardisation) helps in one direction only, and only for ranking (AUROC), not for the operating point.
- Limits: adaptation and evaluation blocks come from the same capture days, so a CIC result at k = 1,000 is within-capture (same day, same attackers), not a held-out day or network; the few-shot CIC evaluation uses a 25% sample of the evaluation blocks; per-type recall in the few-shot curve was not computed; the 14 common features exclude the `ct_*` window counts that mattered within UNSW.

#### One paragraph
The model does not transfer zero-shot: under a protocol with no neighbouring-flow leakage on either side, a UNSW-trained model scores at chance on CICIDS2017 (AUROC 0.49, flagging 69% of flows) and a CIC-trained model detects nothing on UNSW-NB15 (AUROC 0.58, 0.3% flagged), because most of the 14 common features either carry no attack signal in one of the datasets (11 of 14) or point
the opposite way (7 of 14), and part of the UNSW to CIC failure is a scale mismatch that per-dataset standardisation removes for ranking (AUROC 0.79) but not for the operating point. Transfer takes labelled target flows: about 1,000 for CICIDS2017 to reach FPR 0.10 at 95% detection, and for UNSW-NB15 about 1,000-5,000 to reach its own ceiling (FPR 0.21 on these 14 features); the source data does not help beyond
a hundred rows, since a model trained only on the same few labelled target rows is as good or better from k = 500. The SHAP-selected "stable" feature set does not beat random subsets of the same size (better in 2 of 5 seeds in each direction). These are within-capture results on two datasets; transfer to another day or network was not tested.

## Source: cross_dataset_step1_zero_shot.md

### Task 6 Step 1: leak-free zero-shot baseline (5 seeds, mean +/- std; target = the evaluation blocks, 200-row gaps)

#### UNSW -> CIC

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| within_dataset_reference | 0.975 +/- 0.005 | 0.997 +/- 0.002 | 0.006 +/- 0.005 | 0.915 +/- 0.032 | 0.014 +/- 0.001 | 0.198 +/- 0.008 | 0 of 5 |
| common_all | 0.492 +/- 0.036 | 0.485 +/- 0.023 | 0.786 +/- 0.104 | 0.845 +/- 0.069 | 0.926 +/- 0.070 | 0.690 +/- 0.117 | 0 of 5 |
| source_only | 0.521 +/- 0.037 | 0.466 +/- 0.041 | 0.795 +/- 0.167 | 0.817 +/- 0.220 | 0.933 +/- 0.046 | 0.745 +/- 0.155 | 0 of 5 |
| stable | 0.502 +/- 0.058 | 0.499 +/- 0.051 | 0.750 +/- 0.150 | 0.771 +/- 0.216 | 0.935 +/- 0.062 | 0.691 +/- 0.128 | 0 of 5 |
| random (10 subsets x 5 seeds) | 0.487 +/- 0.054 | 0.482 +/- 0.068 | 0.710 +/- 0.108 | 0.697 +/- 0.182 | 0.899 +/- 0.072 | 0.642 +/- 0.103 | 0 of 50 |

Stable against random subsets of the same size (AUROC): better in 2 of 5 seeds, mean difference +0.017 (95% interval -0.064, +0.097); spread of the random subsets 0.068; **stable beats random: no**.
Stable against random subsets of the same size (FPR at exactly 95% detection): better in 2 of 5 seeds, mean difference +0.036 (95% interval -0.035, +0.107); spread of the random subsets 0.072; **stable beats random: no**.

#### CIC -> UNSW

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| within_dataset_reference | 0.896 +/- 0.011 | 0.972 +/- 0.006 | 0.159 +/- 0.035 | 0.947 +/- 0.016 | 0.163 +/- 0.036 | 0.454 +/- 0.043 | 0 of 5 |
| common_all | 0.502 | 0.578 +/- 0.019 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.927 +/- 0.064 | 0.003 +/- 0.006 | 4 of 5 |
| source_only | n/a | 0.551 +/- 0.046 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.957 +/- 0.026 | 0.001 +/- 0.002 | 5 of 5 |
| stable | n/a | 0.521 +/- 0.044 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.968 +/- 0.017 | 0.001 +/- 0.001 | 5 of 5 |
| random (10 subsets x 5 seeds) | 0.531 +/- 0.056 | 0.541 +/- 0.075 | 0.001 +/- 0.006 | 0.007 +/- 0.045 | 0.926 +/- 0.071 | 0.005 +/- 0.023 | 46 of 50 |

Stable against random subsets of the same size (AUROC): better in 2 of 5 seeds, mean difference -0.020 (95% interval -0.080, +0.041); spread of the random subsets 0.075; **stable beats random: no**.
Stable against random subsets of the same size (FPR at exactly 95% detection): better in 1 of 5 seeds, mean difference +0.042 (95% interval -0.011, +0.095); spread of the random subsets 0.071; **stable beats random: no**.

#### Recall per attack type at the argmax (mean over seeds; types with at least 100 evaluation rows)

##### UNSW -> CIC

| attack type | evaluation rows | zero-shot (common_all) | leak-free reference |
|---|---|---|---|
| Bot | 660 | 0.537 | 0.372 |
| DDoS | 38482 | 0.650 | 0.997 |
| DoS GoldenEye | 3058 | 0.692 | 0.893 |
| DoS Hulk | 67302 | 0.824 | 0.967 |
| DoS Slowhttptest | 1310 | 0.384 | 0.456 |
| DoS slowloris | 1409 | 0.385 | 0.695 |
| FTP-Patator | 2821 | 0.568 | 0.981 |
| PortScan | 48166 | 0.534 | 0.998 |
| SSH-Patator | 1596 | 0.525 | 0.494 |
| Web Attack - Brute Force | 400 | 0.139 | 0.060 |
| Web Attack - XSS | 244 | 0.047 | 0.011 |

##### CIC -> UNSW

| attack type | evaluation rows | zero-shot (common_all) | leak-free reference |
|---|---|---|---|
| Analysis | 601 | 0.000 | 0.809 |
| Backdoor | 517 | 0.000 | 0.983 |
| DoS | 1525 | 0.001 | 0.955 |
| Exploits | 7659 | 0.001 | 0.968 |
| Fuzzers | 6060 | 0.009 | 0.702 |
| Generic | 2352 | 0.004 | 0.991 |
| Reconnaissance | 2857 | 0.000 | 0.992 |
| Shellcode | 412 | 0.004 | 0.859 |

#### Block class mix (1,000-row blocks in file order)

| dataset | blocks | pure normal | mixed | pure attack | most frequent dominant attack types (blocks) |
|---|---|---|---|---|---|
| CIC | 2831 | 1523 | 1198 | 110 | DoS Hulk (255), SSH-Patator (218), PortScan (187), DoS GoldenEye (181), DDoS (152) |
| UNSW | 163 | 78 | 38 | 47 | Exploits (60), Fuzzers (13), Generic (12) |

Evaluation rows per attack type (mean over seeds, minimum over seeds): types with fewer than 100 rows in some seed are not reported per type: CIC Heartbleed (min 10), CIC Infiltration (min 7), CIC Web Attack - Sql Injection (min 4), UNSW Worms (min 44).

## Source: cross_dataset_step2_diagnostic.md

### Task 6 Step 2: why zero-shot fails (diagnostic)

AUROC of each common feature alone for attack against normal (all rows of each dataset; above 0.5 = attack flows have higher values). `absent` = |AUROC - 0.5| < 0.05 in at least one dataset.

| feature | UNSW | CIC | same direction | absent in either dataset | flipped (clear and opposite) |
|---|---|---|---|---|---|
| avg_pkt_size | 0.445 | 0.521 | no | yes | no |
| byte_ratio | 0.470 | 0.278 | yes | yes | no |
| dbytes | 0.362 | 0.543 | no | yes | no |
| dmean | 0.302 | 0.561 | no | no | yes |
| dpkts | 0.367 | 0.489 | yes | yes | no |
| dur | 0.560 | 0.542 | yes | yes | no |
| duration_log | 0.560 | 0.542 | yes | yes | no |
| pkt_ratio | 0.499 | 0.429 | yes | yes | no |
| rate | 0.441 | 0.440 | yes | no | no |
| sbytes | 0.416 | 0.363 | yes | no | no |
| smean | 0.526 | 0.343 | no | yes | no |
| spkts | 0.404 | 0.547 | no | yes | no |
| total_bytes | 0.398 | 0.509 | no | yes | no |
| total_pkts | 0.382 | 0.525 | no | yes | no |

Of 14 features: 7 point the same way, 7 do not, 11 are absent (near 0.5) in at least one dataset and 1 are clearly flipped. SHAP importance rank agreement between a UNSW-trained and a CIC-trained model on the common features: Spearman 0.52 +/- 0.05 over 5 seeds.

Zero-shot AUROC of the common_all model: CIC -> UNSW 0.578 +/- 0.019; UNSW -> CIC 0.485 +/- 0.023.

## Source: cross_dataset_step3_align.md

### Task 6 Step 3: label-free alignment (TRANSDUCTIVE) against the zero-shot baseline (5 seeds, mean +/- std)

#### UNSW -> CIC

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| baseline: common_all (ZERO-SHOT, Step 1) | 0.492 +/- 0.036 | 0.485 +/- 0.023 | 0.786 +/- 0.104 | 0.845 +/- 0.069 | 0.926 +/- 0.070 | 0.690 +/- 0.117 | 0 of 5 |
| per_dataset_standardisation | 0.550 +/- 0.044 | 0.785 +/- 0.030 | 0.139 +/- 0.112 | 0.359 +/- 0.253 | 0.410 +/- 0.041 | 0.107 +/- 0.089 | 0 of 5 |
| quantile_mapping | 0.627 +/- 0.040 | 0.720 +/- 0.035 | 0.723 +/- 0.051 | 0.960 +/- 0.045 | 0.683 +/- 0.070 | 0.708 +/- 0.042 | 0 of 5 |
| drop_top3_shifted | 0.500 +/- 0.015 | 0.524 +/- 0.011 | 0.726 +/- 0.065 | 0.802 +/- 0.134 | 0.862 +/- 0.087 | 0.646 +/- 0.061 | 0 of 5 |
| drop_top5_shifted | 0.508 +/- 0.019 | 0.512 +/- 0.030 | 0.651 +/- 0.060 | 0.696 +/- 0.117 | 0.850 +/- 0.052 | 0.601 +/- 0.043 | 0 of 5 |
| quantile_mapping_drop_top3 | 0.628 +/- 0.025 | 0.727 +/- 0.040 | 0.728 +/- 0.059 | 0.976 +/- 0.023 | 0.681 +/- 0.053 | 0.721 +/- 0.044 | 0 of 5 |

#### CIC -> UNSW

| method | balanced accuracy (argmax) | AUROC | FPR at the 95%-detection threshold | detection at that threshold | FPR at exactly 95% detection | predicted attack share | degenerate runs |
|---|---|---|---|---|---|---|---|
| baseline: common_all (ZERO-SHOT, Step 1) | 0.502 | 0.578 +/- 0.019 | 0.000 +/- 0.000 | 0.000 +/- 0.000 | 0.927 +/- 0.064 | 0.003 +/- 0.006 | 4 of 5 |
| per_dataset_standardisation | 0.511 +/- 0.006 | 0.581 +/- 0.039 | 0.005 +/- 0.007 | 0.013 +/- 0.011 | 0.926 +/- 0.063 | 0.025 +/- 0.025 | 2 of 5 |
| quantile_mapping | 0.474 +/- 0.013 | 0.566 +/- 0.032 | 0.054 +/- 0.038 | 0.029 +/- 0.008 | 0.922 +/- 0.021 | 0.070 +/- 0.026 | 0 of 5 |
| drop_top3_shifted | 0.502 | 0.545 +/- 0.020 | 0.000 +/- 0.000 | 0.000 +/- 0.001 | 0.971 +/- 0.035 | 0.004 +/- 0.008 | 4 of 5 |
| drop_top5_shifted | n/a | 0.624 +/- 0.044 | 0.001 +/- 0.003 | 0.003 +/- 0.006 | 0.793 +/- 0.073 | 0.001 +/- 0.002 | 5 of 5 |
| quantile_mapping_drop_top3 | 0.484 +/- 0.025 | 0.553 +/- 0.033 | 0.040 +/- 0.033 | 0.029 +/- 0.004 | 0.937 +/- 0.024 | 0.056 +/- 0.029 | 0 of 5 |

## Source: cross_dataset_step4_fewshot.md

### Task 6 Step 4: few-shot curve, both directions (25 runs per cell = 5 seeds x 5 draws; mean +/- std)

k labelled target rows: half retrain the model (together with the source data for source+target), half choose the threshold; evaluation on target rows from other blocks. Success level: FPR at the held-out-half threshold <= 0.15 with detection >= 0.90, or balanced accuracy within 0.05 of the leak-free reference.

#### UNSW -> CIC

Zero-shot baseline on the same evaluation rows (k = 0): FPR 0.786 +/- 0.095, detection 0.838 +/- 0.068, AUROC 0.492 +/- 0.035, balanced accuracy 0.495 +/- 0.035. Leak-free reference (trained on all candidate blocks): FPR 0.019 +/- 0.031, detection 0.938 +/- 0.055, AUROC 0.997 +/- 0.001, balanced accuracy 0.976 +/- 0.005.

| strategy | k | model | FPR at threshold | detection | balanced accuracy | AUROC | FPR at exactly 95% detection | degenerate runs |
|---|---|---|---|---|---|---|---|---|
| random | 100 | source+target | 0.604 +/- 0.306 | 0.893 +/- 0.097 | 0.750 +/- 0.072 | 0.801 +/- 0.100 | 0.743 +/- 0.185 | 0 of 25 |
| random | 100 | target_only | 0.508 +/- 0.230 | 0.936 +/- 0.093 | 0.700 +/- 0.079 | 0.822 +/- 0.069 | 0.530 +/- 0.221 | 0 of 25 |
| random | 500 | source+target | 0.326 +/- 0.233 | 0.937 +/- 0.039 | 0.896 +/- 0.026 | 0.948 +/- 0.023 | 0.352 +/- 0.157 | 0 of 25 |
| random | 500 | target_only | 0.169 +/- 0.130 | 0.941 +/- 0.040 | 0.905 +/- 0.033 | 0.968 +/- 0.013 | 0.163 +/- 0.095 | 0 of 25 |
| random | 1000 | source+target | 0.187 +/- 0.117 | 0.946 +/- 0.027 | 0.923 +/- 0.014 | 0.971 +/- 0.008 | 0.196 +/- 0.075 | 0 of 25 |
| random | 1000 | target_only | 0.096 +/- 0.078 | 0.945 +/- 0.024 | 0.935 +/- 0.015 | 0.981 +/- 0.006 | 0.090 +/- 0.054 | 0 of 25 |
| random | 5000 | source+target | 0.030 +/- 0.009 | 0.948 +/- 0.014 | 0.959 +/- 0.006 | 0.991 +/- 0.002 | 0.036 +/- 0.014 | 0 of 25 |
| random | 5000 | target_only | 0.022 +/- 0.006 | 0.946 +/- 0.016 | 0.963 +/- 0.006 | 0.994 +/- 0.001 | 0.024 +/- 0.006 | 0 of 25 |
| random | 10000 | source+target | 0.021 +/- 0.002 | 0.952 +/- 0.010 | 0.966 +/- 0.004 | 0.994 +/- 0.001 | 0.023 +/- 0.007 | 0 of 25 |
| random | 10000 | target_only | 0.017 +/- 0.002 | 0.952 +/- 0.009 | 0.969 +/- 0.004 | 0.995 +/- 0.001 | 0.018 +/- 0.002 | 0 of 25 |
| diverse | 100 | source+target | 0.580 +/- 0.328 | 0.880 +/- 0.116 | 0.772 +/- 0.048 | 0.823 +/- 0.097 | 0.706 +/- 0.223 | 0 of 25 |
| diverse | 100 | target_only | 0.491 +/- 0.216 | 0.970 +/- 0.046 | 0.738 +/- 0.042 | 0.869 +/- 0.034 | 0.399 +/- 0.166 | 0 of 25 |
| diverse | 500 | source+target | 0.220 +/- 0.218 | 0.896 +/- 0.044 | 0.902 +/- 0.017 | 0.940 +/- 0.027 | 0.456 +/- 0.218 | 0 of 25 |
| diverse | 500 | target_only | 0.199 +/- 0.173 | 0.937 +/- 0.047 | 0.910 +/- 0.020 | 0.970 +/- 0.009 | 0.163 +/- 0.062 | 0 of 25 |
| diverse | 1000 | source+target | 0.178 +/- 0.136 | 0.928 +/- 0.028 | 0.922 +/- 0.017 | 0.964 +/- 0.013 | 0.269 +/- 0.148 | 0 of 25 |
| diverse | 1000 | target_only | 0.108 +/- 0.093 | 0.947 +/- 0.026 | 0.929 +/- 0.020 | 0.980 +/- 0.005 | 0.099 +/- 0.050 | 0 of 25 |
| diverse | 5000 | source+target | 0.032 +/- 0.016 | 0.932 +/- 0.024 | 0.951 +/- 0.011 | 0.990 +/- 0.003 | 0.048 +/- 0.026 | 0 of 25 |
| diverse | 5000 | target_only | 0.023 +/- 0.013 | 0.944 +/- 0.027 | 0.959 +/- 0.012 | 0.993 +/- 0.002 | 0.023 +/- 0.007 | 0 of 25 |
| diverse | 10000 | source+target | 0.015 +/- 0.007 | 0.925 +/- 0.023 | 0.962 +/- 0.008 | 0.994 +/- 0.002 | 0.029 +/- 0.011 | 0 of 25 |
| diverse | 10000 | target_only | 0.013 +/- 0.006 | 0.931 +/- 0.030 | 0.969 +/- 0.007 | 0.995 +/- 0.001 | 0.019 +/- 0.005 | 0 of 25 |

| strategy | model | smallest k: FPR <= 0.15 with detection >= 0.90 | smallest k: balanced accuracy within 0.05 of the reference | source data helps? (source+target minus target-only, FPR, by k) |
|---|---|---|---|---|
| diverse | source+target | 5000 | 5000 | k=100: +0.088 (no); k=500: +0.021 (no); k=1000: +0.069 (no); k=5000: +0.008 (no); k=10000: +0.002 (no) |
| diverse | target_only | 1000 | 1000 |  |
| random | source+target | 5000 | 5000 | k=100: +0.095 (no); k=500: +0.158 (no); k=1000: +0.091 (no); k=5000: +0.009 (no); k=10000: +0.003 (no) |
| random | target_only | 1000 | 1000 |  |

#### CIC -> UNSW

Zero-shot baseline on the same evaluation rows (k = 0): FPR 0.000 +/- 0.000, detection 0.000 +/- 0.000, AUROC 0.574 +/- 0.025, balanced accuracy 0.501 +/- 0.001. Leak-free reference (trained on all candidate blocks): FPR 0.210 +/- 0.035, detection 0.951 +/- 0.012, AUROC 0.960 +/- 0.007, balanced accuracy 0.876 +/- 0.013.

| strategy | k | model | FPR at threshold | detection | balanced accuracy | AUROC | FPR at exactly 95% detection | degenerate runs |
|---|---|---|---|---|---|---|---|---|
| random | 100 | source+target | 0.554 +/- 0.144 | 0.938 +/- 0.047 | 0.667 +/- 0.027 | 0.814 +/- 0.026 | 0.540 +/- 0.096 | 0 of 25 |
| random | 100 | target_only | 0.575 +/- 0.162 | 0.939 +/- 0.055 | 0.687 +/- 0.028 | 0.748 +/- 0.030 | 0.582 +/- 0.108 | 0 of 25 |
| random | 500 | source+target | 0.345 +/- 0.054 | 0.949 +/- 0.019 | 0.762 +/- 0.026 | 0.888 +/- 0.019 | 0.340 +/- 0.042 | 0 of 25 |
| random | 500 | target_only | 0.356 +/- 0.055 | 0.946 +/- 0.022 | 0.801 +/- 0.024 | 0.892 +/- 0.018 | 0.358 +/- 0.034 | 0 of 25 |
| random | 1000 | source+target | 0.292 +/- 0.033 | 0.948 +/- 0.013 | 0.803 +/- 0.016 | 0.906 +/- 0.017 | 0.293 +/- 0.028 | 0 of 25 |
| random | 1000 | target_only | 0.296 +/- 0.035 | 0.946 +/- 0.015 | 0.830 +/- 0.014 | 0.918 +/- 0.013 | 0.298 +/- 0.028 | 0 of 25 |
| random | 5000 | source+target | 0.245 +/- 0.032 | 0.945 +/- 0.008 | 0.850 +/- 0.011 | 0.941 +/- 0.009 | 0.252 +/- 0.029 | 0 of 25 |
| random | 5000 | target_only | 0.235 +/- 0.035 | 0.945 +/- 0.009 | 0.858 +/- 0.012 | 0.947 +/- 0.008 | 0.242 +/- 0.029 | 0 of 25 |
| random | 10000 | source+target | 0.232 +/- 0.032 | 0.947 +/- 0.006 | 0.861 +/- 0.012 | 0.950 +/- 0.008 | 0.236 +/- 0.030 | 0 of 25 |
| random | 10000 | target_only | 0.224 +/- 0.030 | 0.946 +/- 0.006 | 0.865 +/- 0.012 | 0.954 +/- 0.007 | 0.230 +/- 0.030 | 0 of 25 |
| diverse | 100 | source+target | 0.512 +/- 0.141 | 0.927 +/- 0.062 | 0.653 +/- 0.054 | 0.807 +/- 0.036 | 0.519 +/- 0.085 | 0 of 25 |
| diverse | 100 | target_only | 0.591 +/- 0.139 | 0.942 +/- 0.051 | 0.684 +/- 0.055 | 0.731 +/- 0.040 | 0.592 +/- 0.118 | 0 of 25 |
| diverse | 500 | source+target | 0.340 +/- 0.052 | 0.959 +/- 0.019 | 0.780 +/- 0.022 | 0.885 +/- 0.021 | 0.320 +/- 0.039 | 0 of 25 |
| diverse | 500 | target_only | 0.348 +/- 0.045 | 0.948 +/- 0.020 | 0.804 +/- 0.019 | 0.887 +/- 0.023 | 0.347 +/- 0.038 | 0 of 25 |
| diverse | 1000 | source+target | 0.294 +/- 0.032 | 0.952 +/- 0.013 | 0.814 +/- 0.016 | 0.907 +/- 0.015 | 0.290 +/- 0.028 | 0 of 25 |
| diverse | 1000 | target_only | 0.293 +/- 0.040 | 0.946 +/- 0.015 | 0.831 +/- 0.013 | 0.914 +/- 0.012 | 0.296 +/- 0.028 | 0 of 25 |
| diverse | 5000 | source+target | 0.254 +/- 0.034 | 0.954 +/- 0.007 | 0.855 +/- 0.011 | 0.942 +/- 0.010 | 0.247 +/- 0.031 | 0 of 25 |
| diverse | 5000 | target_only | 0.244 +/- 0.033 | 0.950 +/- 0.007 | 0.859 +/- 0.012 | 0.946 +/- 0.009 | 0.244 +/- 0.029 | 0 of 25 |
| diverse | 10000 | source+target | 0.242 +/- 0.033 | 0.956 +/- 0.005 | 0.863 +/- 0.011 | 0.950 +/- 0.008 | 0.233 +/- 0.029 | 0 of 25 |
| diverse | 10000 | target_only | 0.234 +/- 0.034 | 0.955 +/- 0.005 | 0.866 +/- 0.012 | 0.953 +/- 0.007 | 0.225 +/- 0.029 | 0 of 25 |

| strategy | model | smallest k: FPR <= 0.15 with detection >= 0.90 | smallest k: balanced accuracy within 0.05 of the reference | source data helps? (source+target minus target-only, FPR, by k) |
|---|---|---|---|---|
| diverse | source+target | not reached | 5000 | k=100: -0.079 (yes); k=500: -0.008 (no); k=1000: +0.001 (no); k=5000: +0.010 (no); k=10000: +0.008 (no) |
| diverse | target_only | not reached | 1000 |  |
| random | source+target | not reached | 5000 | k=100: -0.021 (no); k=500: -0.011 (no); k=1000: -0.004 (no); k=5000: +0.010 (no); k=10000: +0.008 (no) |
| random | target_only | not reached | 1000 |  |

## Source: task_6_protocol.md

### Task 6 protocol (declared before any Task 6 result was produced)

Novelty 4: cross-dataset generalisation between UNSW-NB15 and CICIDS2017. XGBoost, binary attack-vs-normal, the common feature set only. Zero-shot is the documented baseline; the new work is a leak-free protocol, a diagnostic of why zero-shot fails,
label-free alignment, and few-shot adaptation with a target-only control. Cap: one session, two heavy jobs at a time.

#### Data (facts established while preparing this protocol)
- **UNSW-NB15:** the official train and test files with exact duplicates removed, in file order (train rows, then test rows): 162,745 flows. Binary label = attack category not Normal.
- **CICIDS2017:** `data/raw/cicids2017_combined.csv`, 2,830,743 flows. It is the eight original day files concatenated in alphabetical file order, which fixes the **day structure** of the combined file (row ranges, verified against the original file sizes and the labels inside each range):
  Friday-DDoS 0-225,745 (DDoS 128,027), Friday-PortScan -512,212 (PortScan 158,930), Friday-Morning -703,245 (Bot 1,966), Monday -1,233,163 (benign only), Thursday-Afternoon -1,521,765 (Infiltration 36), Thursday-Morning -1,692,131 (Web Attack Brute Force 1,507, XSS 652, SQL Injection 21),
  Tuesday -2,138,040 (FTP-Patator 7,938, SSH-Patator 5,897), Wednesday -2,830,743 (DoS Hulk 231,073, GoldenEye 10,293, slowloris 5,796, Slowhttptest 5,499, Heartbleed 11). Benign 2,273,097 (80.3%). Within a day, attacks arrive in bursts (runs of thousands of flows), so a contiguous block is usually all benign or mostly one attack type.
- The file is streamed once with only the eight mapped columns plus the label (`usecols`, 500,000-row chunks) and cached as `data/processed/cic_common.parquet` (gitignored, about 220 MB in memory). Mapping, the microsecond-to-second conversion of `dur` and the label clean-up are those of `load_cic`; file order is kept (the earlier stratified subsample shuffled it).
- **Common features:** 8 raw (dur, spkts, dpkts, sbytes, dbytes, rate, smean, dmean) + 6 engineered (total_bytes, total_pkts, byte_ratio, pkt_ratio, avg_pkt_size, duration_log) = 14 (`CROSS_DATASET_COMMON_FEATURES`). No ct_* window count is among them.

#### Blocks, splits and what is never used
- A **block** is 1,000 consecutive rows of a dataset in file order; a split drops 200 rows on each side of every boundary between groups (`src/neighbours.block_split`), for BOTH datasets. CIC blocks follow the day structure above; the class mix of every block (attack share, dominant attack type) is reported and each evaluation set is checked: both classes present,
  and per-type recall is reported only for attack types with at least 100 evaluation rows.
- **Step 1-3 split** (per seed): 60% of the blocks of the target dataset are its "train blocks" (used only for the within-dataset reference and for the target-side importance of the `stable` set), the remaining blocks (with gaps) are the **evaluation blocks** on which every Step 1-3 method is scored. A model with a SOURCE role is trained on the source dataset's train blocks
  (UNSW: all rows of its train blocks; CIC: whole blocks drawn at random until 200,000 rows), with 15% of those blocks (gaps) held out as the source validation set.
- **Step 4 split** (per seed and draw; draw seed = 100 x seed + draw): 40% of the target blocks are the adaptation candidates, the rest (with gaps) the evaluation blocks; adaptation rows come only from the candidates and no adaptation row is ever evaluated. For CIC (2.8 M rows) the evaluation uses a seeded 25% of the evaluation blocks (whole blocks) to bound the cost; UNSW uses all.
  The candidates for selection are a seeded sample of up to 100,000 rows of the candidate blocks (the same pool for every strategy).
- Target-test labels are never used to choose a method, a threshold or a setting.

#### Model, preprocessing, metrics
XGBoost binary, 200 trees, depth 6, learning rate 0.1, subsample 0.9, colsample 0.9, min_child_weight 3, lambda 1.5, `n_jobs` 8, sample weights = balanced ** 0.5 (as the earlier cross-dataset code). The preprocessor (standardisation, `_clean_numeric` for infinities) is fitted on the SOURCE training rows only, so the target is scaled with source statistics (unit mismatches stay visible);
Step 3 changes this on purpose and says so.
Primary metric (declared now): **FPR at about 95% detection on the target evaluation blocks**, i.e. the evaluation FPR at the threshold on P(attack) chosen so that 95% of the attacks of the threshold-selection rows are detected (zero-shot and Step 3: the source validation set; few-shot: the held-out labelled half), always printed with the detection reached; with balanced accuracy at argmax, AUROC, and the
threshold-free FPR at exactly 95% detection. Also: FPR and detection at argmax, the predicted attack share, recall per attack type (CIC: the 15 types; UNSW: the attack categories). **Degenerate-row rule:** a predictor whose attack share at argmax is below 1% or above 99% is flagged `degenerate`, its argmax metrics are not ranked (balanced accuracy, argmax FPR and detection set to NaN in rankings), AUROC is still shown.

#### Step 1: leak-free zero-shot baseline (ZERO-SHOT; `stable` uses target labels and is labelled so)
Both directions, 5 seeds (42-46), feature sets: `common_all` (14); `source_only` = top 10 common features by mean |SHAP| of a model trained on the source train blocks; `stable` = the features in the top 10 of BOTH the source model and a model trained on the target train blocks (**uses target labels through the target model; not zero-shot**);
`random` = 10 random subsets per seed of the same size as that seed's `stable` set (seeded 100 x seed + j). The within-dataset reference: a model trained on the target's own train blocks (threshold from its 15% validation blocks), scored on the same evaluation blocks. Report the primary and secondary metrics, recall per attack type, and for `stable` against its random subsets
the paired difference with an interval over seeds and subsets (the claim "stable beats random" is true only if it holds in a majority of seeds with an interval excluding 0).

#### Step 2: why zero-shot fails (diagnostic, no model change)
Per common feature and dataset: the univariate AUROC of the feature for attack vs normal (all rows), the direction (above / below 0.5), whether the two datasets agree, and a feature is "absent" in a dataset when |AUROC - 0.5| < 0.05. Counts of flipped, absent and agreeing features, related to the direction of the zero-shot AUROC. SHAP importance rank agreement (Spearman) between a UNSW-trained and a CIC-trained model
on the common features (models of Step 1, 5 seeds, mean and std).

#### Step 3: label-free alignment (TRANSDUCTIVE: uses the unlabelled target features, nothing else)
Against the Step 1 `common_all` baseline on the same evaluation blocks: (a) **per-dataset standardisation** (the target scaled with its own mean / std, the source with its own); (b) **quantile mapping** (each feature mapped through its dataset's empirical CDF to a normal score, source and target each with their own CDF); (c) **drop the most-shifted features**: the 3 and the 5 features with the largest KS statistic between the source and the unlabelled target;
(d) quantile mapping plus dropping 3. Report the primary and secondary metrics and the degenerate flag.

#### Step 4: few-shot curve, both directions (FEW-SHOT; the baseline next to every row is the zero-shot model on the same evaluation rows, k = 0)
k = 0, 100, 500, 1,000, 5,000, 10,000 labelled target rows; selection `random` (uniform from the candidate pool) and `diverse` (MiniBatchKMeans with k clusters on the source-scaled features, the row nearest each centroid); the chosen rows are split at random into two halves, one retrains the model together with the source data (the labelled rows carry half of the total sample weight) and the other chooses the threshold;
5 seeds x 5 draws. **Target-only control:** a model trained on the fit half alone (preprocessor fitted on those rows, no source data), same threshold rule, same evaluation rows. Reported: primary and secondary metrics against k, the paired difference source+target minus target-only per (seed, draw), and the leak-free within-dataset reference as the upper line (trained on all candidate blocks, capped at 200,000 rows,
threshold on its own held-out blocks).
**Declared success level:** FPR at about 95% detection at or below 0.15 with detection at least 0.90, or balanced accuracy within 0.05 of the reference. The smallest k reaching it (mean over the 25 runs) is stated per direction and strategy, or "not reached". "The source data helps" is stated only where the paired difference favours source+target in a majority of runs with an interval excluding 0.

#### Step 5
One claim for novelty 4 and this protocol, one table per step. The result is presented as what it takes to transfer; the zero-shot failure is documented, not hidden. Teammates' model families are not run or quoted.

## Source: cross_dataset_diagnostic_importance_agreement.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed. Each original column is a row here; each original row is a column.

| metric | 42.0 | 43.0 | 44.0 | 45.0 | 46.0 |
|---|---|---|---|---|---|
| spearman_importance | 0.595604 | 0.538462 | 0.446154 | 0.498901 | 0.512088 |
| importance_rank_UNSW_dur | 11 | 11 | 11 | 12 | 12 |
| importance_rank_UNSW_spkts | 14 | 13 | 13 | 13 | 14 |
| importance_rank_UNSW_dpkts | 5 | 6 | 6 | 4 | 8 |
| importance_rank_UNSW_sbytes | 4 | 3 | 3 | 6 | 4 |
| importance_rank_UNSW_dbytes | 7 | 10 | 5 | 11 | 11 |
| importance_rank_UNSW_rate | 1 | 2 | 1 | 1 | 1 |
| importance_rank_UNSW_smean | 6 | 4 | 4 | 5 | 3 |
| importance_rank_UNSW_dmean | 2 | 1 | 2 | 2 | 2 |
| importance_rank_UNSW_total_bytes | 9 | 9 | 9 | 8 | 6 |
| importance_rank_UNSW_total_pkts | 12 | 12 | 12 | 10 | 10 |
| importance_rank_UNSW_byte_ratio | 8 | 8 | 10 | 7 | 9 |
| importance_rank_UNSW_pkt_ratio | 10 | 7 | 8 | 9 | 7 |
| importance_rank_UNSW_avg_pkt_size | 3 | 5 | 7 | 3 | 5 |
| importance_rank_UNSW_duration_log | 13 | 14 | 14 | 14 | 13 |
| importance_rank_CIC_dur | 10 | 9 | 7 | 5 | 4 |
| importance_rank_CIC_spkts | 12 | 10 | 10 | 9 | 9 |
| importance_rank_CIC_dpkts | 6 | 8 | 5 | 8 | 8 |
| importance_rank_CIC_sbytes | 9 | 2 | 2 | 1 | 6 |
| importance_rank_CIC_dbytes | 7 | 7 | 9 | 12 | 10 |
| importance_rank_CIC_rate | 8 | 6 | 8 | 6 | 5 |
| importance_rank_CIC_smean | 4 | 12 | 12 | 3 | 7 |
| importance_rank_CIC_dmean | 1 | 1 | 1 | 2 | 2 |
| importance_rank_CIC_total_bytes | 2 | 3 | 4 | 4 | 1 |
| importance_rank_CIC_total_pkts | 13 | 11 | 11 | 11 | 11 |
| importance_rank_CIC_byte_ratio | 3 | 4 | 6 | 7 | 13 |
| importance_rank_CIC_pkt_ratio | 14 | 14 | 14 | 14 | 14 |
| importance_rank_CIC_avg_pkt_size | 5 | 5 | 3 | 10 | 3 |
| importance_rank_CIC_duration_log | 11 | 13 | 13 | 13 | 12 |

## Source: cross_dataset_zero_shot_eval_mix.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| dataset | seed | attack_type | evaluation_rows | attack_blocks_in_dataset |
|---|---|---|---|---|
| UNSW | 42 | Exploits | 7078 | 85 |
| UNSW | 42 | Fuzzers | 5647 | 85 |
| UNSW | 42 | Reconnaissance | 2645 | 85 |
| UNSW | 42 | Generic | 2230 | 85 |
| UNSW | 42 | DoS | 1366 | 85 |
| UNSW | 42 | Analysis | 558 | 85 |
| UNSW | 42 | Backdoor | 464 | 85 |
| UNSW | 42 | Shellcode | 369 | 85 |
| UNSW | 42 | Worms | 47 | 85 |
| CIC | 42 | DoS Hulk | 66798 | 1308 |
| CIC | 42 | PortScan | 52879 | 1308 |
| CIC | 42 | DDoS | 35286 | 1308 |
| CIC | 42 | DoS GoldenEye | 3054 | 1308 |
| CIC | 42 | FTP-Patator | 2059 | 1308 |
| CIC | 42 | SSH-Patator | 1908 | 1308 |
| CIC | 42 | DoS slowloris | 1194 | 1308 |
| CIC | 42 | Bot | 724 | 1308 |
| CIC | 42 | DoS Slowhttptest | 547 | 1308 |
| CIC | 42 | Web Attack - Brute Force | 511 | 1308 |
| CIC | 42 | Web Attack - XSS | 270 | 1308 |
| CIC | 42 | Infiltration | 11 | 1308 |
| CIC | 42 | Web Attack - Sql Injection | 11 | 1308 |
| UNSW | 43 | Exploits | 7756 | 85 |
| UNSW | 43 | Fuzzers | 5731 | 85 |
| UNSW | 43 | Reconnaissance | 2898 | 85 |
| UNSW | 43 | Generic | 2363 | 85 |
| UNSW | 43 | DoS | 1387 | 85 |
| UNSW | 43 | Backdoor | 672 | 85 |
| UNSW | 43 | Analysis | 632 | 85 |
| UNSW | 43 | Shellcode | 421 | 85 |
| UNSW | 43 | Worms | 57 | 85 |
| CIC | 43 | DoS Hulk | 58067 | 1308 |
| CIC | 43 | DDoS | 44770 | 1308 |
| CIC | 43 | PortScan | 40626 | 1308 |
| CIC | 43 | DoS GoldenEye | 2695 | 1308 |
| CIC | 43 | FTP-Patator | 2248 | 1308 |
| CIC | 43 | SSH-Patator | 1727 | 1308 |
| CIC | 43 | DoS slowloris | 1407 | 1308 |
| CIC | 43 | Bot | 615 | 1308 |
| CIC | 43 | Web Attack - Brute Force | 327 | 1308 |
| CIC | 43 | Web Attack - XSS | 259 | 1308 |
| CIC | 43 | Infiltration | 7 | 1308 |
| UNSW | 44 | Exploits | 7544 | 85 |
| UNSW | 44 | Fuzzers | 6151 | 85 |
| UNSW | 44 | Generic | 2834 | 85 |
| UNSW | 44 | Reconnaissance | 2734 | 85 |
| UNSW | 44 | DoS | 1667 | 85 |
| UNSW | 44 | Analysis | 540 | 85 |
| UNSW | 44 | Backdoor | 460 | 85 |
| UNSW | 44 | Shellcode | 425 | 85 |
| UNSW | 44 | Worms | 48 | 85 |
| CIC | 44 | DoS Hulk | 70111 | 1308 |
| CIC | 44 | PortScan | 43166 | 1308 |
| CIC | 44 | DDoS | 35189 | 1308 |
| CIC | 44 | FTP-Patator | 3333 | 1308 |
| CIC | 44 | DoS GoldenEye | 3280 | 1308 |
| CIC | 44 | DoS slowloris | 1489 | 1308 |
| CIC | 44 | SSH-Patator | 1323 | 1308 |
| CIC | 44 | DoS Slowhttptest | 1200 | 1308 |
| CIC | 44 | Bot | 553 | 1308 |
| CIC | 44 | Web Attack - Brute Force | 461 | 1308 |
| CIC | 44 | Web Attack - XSS | 260 | 1308 |
| CIC | 44 | Infiltration | 18 | 1308 |
| CIC | 44 | Web Attack - Sql Injection | 4 | 1308 |
| UNSW | 45 | Exploits | 6932 | 85 |
| UNSW | 45 | Fuzzers | 5686 | 85 |
| UNSW | 45 | Reconnaissance | 2599 | 85 |
| UNSW | 45 | Generic | 1370 | 85 |
| UNSW | 45 | DoS | 1340 | 85 |
| UNSW | 45 | Analysis | 515 | 85 |
| UNSW | 45 | Backdoor | 435 | 85 |
| UNSW | 45 | Shellcode | 377 | 85 |
| UNSW | 45 | Worms | 44 | 85 |
| CIC | 45 | DoS Hulk | 71300 | 1308 |
| CIC | 45 | PortScan | 54031 | 1308 |
| CIC | 45 | DDoS | 36457 | 1308 |
| CIC | 45 | DoS GoldenEye | 3494 | 1308 |
| CIC | 45 | FTP-Patator | 3246 | 1308 |
| CIC | 45 | DoS slowloris | 2033 | 1308 |
| CIC | 45 | DoS Slowhttptest | 2024 | 1308 |
| CIC | 45 | SSH-Patator | 1513 | 1308 |
| CIC | 45 | Bot | 809 | 1308 |
| CIC | 45 | Web Attack - Brute Force | 517 | 1308 |
| CIC | 45 | Web Attack - XSS | 197 | 1308 |
| CIC | 45 | Heartbleed | 10 | 1308 |
| CIC | 45 | Infiltration | 9 | 1308 |
| CIC | 45 | Web Attack - Sql Injection | 5 | 1308 |
| UNSW | 46 | Exploits | 8983 | 85 |
| UNSW | 46 | Fuzzers | 7086 | 85 |
| UNSW | 46 | Reconnaissance | 3411 | 85 |
| UNSW | 46 | Generic | 2962 | 85 |
| UNSW | 46 | DoS | 1864 | 85 |
| UNSW | 46 | Analysis | 762 | 85 |
| UNSW | 46 | Backdoor | 555 | 85 |
| UNSW | 46 | Shellcode | 467 | 85 |
| UNSW | 46 | Worms | 63 | 85 |
| CIC | 46 | DoS Hulk | 70236 | 1308 |
| CIC | 46 | PortScan | 50127 | 1308 |
| CIC | 46 | DDoS | 40709 | 1308 |
| CIC | 46 | FTP-Patator | 3217 | 1308 |
| CIC | 46 | DoS GoldenEye | 2767 | 1308 |
| CIC | 46 | SSH-Patator | 1510 | 1308 |
| CIC | 46 | DoS Slowhttptest | 1470 | 1308 |
| CIC | 46 | DoS slowloris | 921 | 1308 |
| CIC | 46 | Bot | 600 | 1308 |
| CIC | 46 | Web Attack - XSS | 234 | 1308 |
| CIC | 46 | Web Attack - Brute Force | 183 | 1308 |
| CIC | 46 | Infiltration | 14 | 1308 |

## Source: cross_dataset_results.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| strategy | n_features | train | test | accuracy | precision | recall | f1 | balanced_accuracy | predicted_attack_share | degenerate |
|---|---|---|---|---|---|---|---|---|---|---|
| within_dataset | 14 | UNSW | UNSW | 0.9012 | 0.8997 | 0.9015 | 0.9005 | 0.9015 | 0.4621 | False |
| within_dataset | 14 | CIC | CIC | 0.9826 | 0.9651 | 0.9812 | 0.9729 | 0.9812 | 0.2061 | False |
| common_all | 14 | UNSW | CIC | 0.4269 | 0.4412 | 0.4073 | 0.3785 | 0.4073 | 0.5239 | False |
| source_only | 10 | UNSW | CIC | 0.4744 | 0.4759 | 0.462 | 0.4223 | 0.462 | 0.5024 | False |
| stable | 7 | UNSW | CIC | 0.4821 | 0.4811 | 0.4702 | 0.4291 | 0.4702 | 0.4984 | False |
| common_all | 14 | CIC | UNSW |  |  |  |  |  | 0 | True |
| source_only | 10 | CIC | UNSW |  |  |  |  |  | 0.0002 | True |
| stable | 7 | CIC | UNSW |  |  |  |  |  | 0.001 | True |

## Source: cross_dataset_feature_shift.csv (rendered table)

Rendered from the CSV of this name (removed in the cleanup; recoverable from git tag `pre-lean-2026-10`); numbers rounded to 6 decimals, nothing else changed.

| feature | unsw_median | unsw_iqr | cic_median | cic_iqr | ks_statistic |
|---|---|---|---|---|---|
| smean | 83 | 73 | 34 | 44.2857 | 0.718 |
| sbytes | 1012 | 2290 | 62 | 184 | 0.6946 |
| total_pkts | 20 | 30 | 4 | 6 | 0.6404 |
| spkts | 10 | 14 | 2 | 3 | 0.6322 |
| total_bytes | 2072 | 10830 | 212 | 1171 | 0.5933 |
| dpkts | 8 | 14 | 2 | 3 | 0.5709 |
| dbytes | 678 | 3112 | 124 | 475 | 0.4912 |
| byte_ratio | 0.9367 | 1.9967 | 0.2355 | 0.5 | 0.4694 |
| avg_pkt_size | 107.1111 | 290.2653 | 62 | 127 | 0.4105 |
| dur | 0.476 | 0.995 | 0.0315 | 3.2148 | 0.2979 |
| duration_log | 0.3894 | 0.6812 | 0.031 | 1.4385 | 0.2979 |
| dmean | 78 | 110 | 73 | 179 | 0.2912 |
| rate | 56.8612 | 2683.7693 | 105.8311 | 23252.4223 | 0.278 |
| pkt_ratio | 1 | 0.5111 | 1 | 0.1429 | 0.2623 |
