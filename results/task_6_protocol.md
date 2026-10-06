# Task 6 protocol (declared before any Task 6 result was produced)

Novelty 4: cross-dataset generalisation between UNSW-NB15 and CICIDS2017. XGBoost, binary attack-vs-normal, the common feature set only. Zero-shot is the documented baseline; the new work is a leak-free protocol, a diagnostic of why zero-shot fails,
label-free alignment, and few-shot adaptation with a target-only control. Cap: one session, two heavy jobs at a time.

## Data (facts established while preparing this protocol)
- **UNSW-NB15:** the official train and test files with exact duplicates removed, in file order (train rows, then test rows): 162,745 flows. Binary label = attack category not Normal.
- **CICIDS2017:** `data/raw/cicids2017_combined.csv`, 2,830,743 flows. It is the eight original day files concatenated in alphabetical file order, which fixes the **day structure** of the combined file (row ranges, verified against the original file sizes and the labels inside each range):
  Friday-DDoS 0-225,745 (DDoS 128,027), Friday-PortScan -512,212 (PortScan 158,930), Friday-Morning -703,245 (Bot 1,966), Monday -1,233,163 (benign only), Thursday-Afternoon -1,521,765 (Infiltration 36), Thursday-Morning -1,692,131 (Web Attack Brute Force 1,507, XSS 652, SQL Injection 21),
  Tuesday -2,138,040 (FTP-Patator 7,938, SSH-Patator 5,897), Wednesday -2,830,743 (DoS Hulk 231,073, GoldenEye 10,293, slowloris 5,796, Slowhttptest 5,499, Heartbleed 11). Benign 2,273,097 (80.3%). Within a day, attacks arrive in bursts (runs of thousands of flows), so a contiguous block is usually all benign or mostly one attack type.
- The file is streamed once with only the eight mapped columns plus the label (`usecols`, 500,000-row chunks) and cached as `data/processed/cic_common.parquet` (gitignored, about 220 MB in memory). Mapping, the microsecond-to-second conversion of `dur` and the label clean-up are those of `load_cic`; file order is kept (the earlier stratified subsample shuffled it).
- **Common features:** 8 raw (dur, spkts, dpkts, sbytes, dbytes, rate, smean, dmean) + 6 engineered (total_bytes, total_pkts, byte_ratio, pkt_ratio, avg_pkt_size, duration_log) = 14 (`CROSS_DATASET_COMMON_FEATURES`). No ct_* window count is among them.

## Blocks, splits and what is never used
- A **block** is 1,000 consecutive rows of a dataset in file order; a split drops 200 rows on each side of every boundary between groups (`src/neighbours.block_split`), for BOTH datasets. CIC blocks follow the day structure above; the class mix of every block (attack share, dominant attack type) is reported and each evaluation set is checked: both classes present,
  and per-type recall is reported only for attack types with at least 100 evaluation rows.
- **Step 1-3 split** (per seed): 60% of the blocks of the target dataset are its "train blocks" (used only for the within-dataset reference and for the target-side importance of the `stable` set), the remaining blocks (with gaps) are the **evaluation blocks** on which every Step 1-3 method is scored. A model with a SOURCE role is trained on the source dataset's train blocks
  (UNSW: all rows of its train blocks; CIC: whole blocks drawn at random until 200,000 rows), with 15% of those blocks (gaps) held out as the source validation set.
- **Step 4 split** (per seed and draw; draw seed = 100 x seed + draw): 40% of the target blocks are the adaptation candidates, the rest (with gaps) the evaluation blocks; adaptation rows come only from the candidates and no adaptation row is ever evaluated. For CIC (2.8 M rows) the evaluation uses a seeded 25% of the evaluation blocks (whole blocks) to bound the cost; UNSW uses all.
  The candidates for selection are a seeded sample of up to 100,000 rows of the candidate blocks (the same pool for every strategy).
- Target-test labels are never used to choose a method, a threshold or a setting.

## Model, preprocessing, metrics
XGBoost binary, 200 trees, depth 6, learning rate 0.1, subsample 0.9, colsample 0.9, min_child_weight 3, lambda 1.5, `n_jobs` 8, sample weights = balanced ** 0.5 (as the earlier cross-dataset code). The preprocessor (standardisation, `_clean_numeric` for infinities) is fitted on the SOURCE training rows only, so the target is scaled with source statistics (unit mismatches stay visible);
Step 3 changes this on purpose and says so.
Primary metric (declared now): **FPR at about 95% detection on the target evaluation blocks**, i.e. the evaluation FPR at the threshold on P(attack) chosen so that 95% of the attacks of the threshold-selection rows are detected (zero-shot and Step 3: the source validation set; few-shot: the held-out labelled half), always printed with the detection reached; with balanced accuracy at argmax, AUROC, and the
threshold-free FPR at exactly 95% detection. Also: FPR and detection at argmax, the predicted attack share, recall per attack type (CIC: the 15 types; UNSW: the attack categories). **Degenerate-row rule:** a predictor whose attack share at argmax is below 1% or above 99% is flagged `degenerate`, its argmax metrics are not ranked (balanced accuracy, argmax FPR and detection set to NaN in rankings), AUROC is still shown.

## Step 1: leak-free zero-shot baseline (ZERO-SHOT; `stable` uses target labels and is labelled so)
Both directions, 5 seeds (42-46), feature sets: `common_all` (14); `source_only` = top 10 common features by mean |SHAP| of a model trained on the source train blocks; `stable` = the features in the top 10 of BOTH the source model and a model trained on the target train blocks (**uses target labels through the target model; not zero-shot**);
`random` = 10 random subsets per seed of the same size as that seed's `stable` set (seeded 100 x seed + j). The within-dataset reference: a model trained on the target's own train blocks (threshold from its 15% validation blocks), scored on the same evaluation blocks. Report the primary and secondary metrics, recall per attack type, and for `stable` against its random subsets
the paired difference with an interval over seeds and subsets (the claim "stable beats random" is true only if it holds in a majority of seeds with an interval excluding 0).

## Step 2: why zero-shot fails (diagnostic, no model change)
Per common feature and dataset: the univariate AUROC of the feature for attack vs normal (all rows), the direction (above / below 0.5), whether the two datasets agree, and a feature is "absent" in a dataset when |AUROC - 0.5| < 0.05. Counts of flipped, absent and agreeing features, related to the direction of the zero-shot AUROC. SHAP importance rank agreement (Spearman) between a UNSW-trained and a CIC-trained model
on the common features (models of Step 1, 5 seeds, mean and std).

## Step 3: label-free alignment (TRANSDUCTIVE: uses the unlabelled target features, nothing else)
Against the Step 1 `common_all` baseline on the same evaluation blocks: (a) **per-dataset standardisation** (the target scaled with its own mean / std, the source with its own); (b) **quantile mapping** (each feature mapped through its dataset's empirical CDF to a normal score, source and target each with their own CDF); (c) **drop the most-shifted features**: the 3 and the 5 features with the largest KS statistic between the source and the unlabelled target;
(d) quantile mapping plus dropping 3. Report the primary and secondary metrics and the degenerate flag.

## Step 4: few-shot curve, both directions (FEW-SHOT; the baseline next to every row is the zero-shot model on the same evaluation rows, k = 0)
k = 0, 100, 500, 1,000, 5,000, 10,000 labelled target rows; selection `random` (uniform from the candidate pool) and `diverse` (MiniBatchKMeans with k clusters on the source-scaled features, the row nearest each centroid); the chosen rows are split at random into two halves, one retrains the model together with the source data (the labelled rows carry half of the total sample weight) and the other chooses the threshold;
5 seeds x 5 draws. **Target-only control:** a model trained on the fit half alone (preprocessor fitted on those rows, no source data), same threshold rule, same evaluation rows. Reported: primary and secondary metrics against k, the paired difference source+target minus target-only per (seed, draw), and the leak-free within-dataset reference as the upper line (trained on all candidate blocks, capped at 200,000 rows,
threshold on its own held-out blocks).
**Declared success level:** FPR at about 95% detection at or below 0.15 with detection at least 0.90, or balanced accuracy within 0.05 of the reference. The smallest k reaching it (mean over the 25 runs) is stated per direction and strategy, or "not reached". "The source data helps" is stated only where the paired difference favours source+target in a majority of runs with an interval excluding 0.

## Step 5
One claim for novelty 4 and this protocol, one table per step. The result is presented as what it takes to transfer; the zero-shot failure is documented, not hidden. Teammates' model families are not run or quoted.
