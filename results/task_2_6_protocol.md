# Task 2.6 protocol (declared before any Task 2.6 result was produced)

Question: is the 48-feature few-shot result of Task 2.5 (FPR 0.094 at about 95% detection with 5,000 labelled rows, against 0.232
on 40 features) real adaptation, or does it come from neighbouring rows shared between the adaptation rows and the evaluation rows
(both are random draws from the same official test file)? The earlier B2/B4 result files are not modified.

## What was verified in the data before declaring this
- The `ct_*` columns are small integers (maximum 65, minimum 0 or 1 in the official files), consistent with counts over a window of
  recent connections.
- The official files are NOT shuffled: in `id` order, consecutive rows correlate strongly on `ct_dst_ltm` / `ct_srv_src` /
  `ct_src_ltm` (lag-1 correlation 0.67-0.76 in the test file, 0.36-0.45 in the training file, about 0 after shuffling) and share a class
  71% (test) / 57% (train) of the time against 28% / 21% after shuffling. Row order (after exact deduplication and removal of the
  zero-day classes, which keep the file order) is therefore usable grouping information; it is used for check 2.

## Primary metric (declared now)
FPR at about 95% detection with the threshold chosen on HELD-OUT labelled adaptation rows: the `retrain_split_f0.5` method of
`pipelines/run_adaptation.py --split-threshold` (retrain on half of the k rows with weight fraction 0.5, choose the 95%-detection threshold
on the other half), reported as `det95_test_fpr` with `det95_test_detection`, k = 5,000 (primary) and k = 1,000 (secondary), 5 runs
(model seed 42 + i, adaptation draw seed 1000 + i), mean and std. Accuracy and ECE are reported next to it. Access level: FEW-SHOT.
Zero-shot is reported on the same evaluation rows.

## Checks, in order
1. **Near-twin share.** Embedding as in `src/evaluation/overlap.py` (log1p, standardised, categoricals exact) fitted on the training
   rows; L-infinity distance <= 0.1 / 0.25 and exact feature-vector equality. Share of evaluation rows with a twin in the adaptation set,
   against the share with a twin in an equally sized random subset of the TRAINING rows and in the whole training set. FPR / detection /
   accuracy / ECE on all evaluation rows, on the rows with NO near twin (<= 0.1) in the adaptation set, and on the rows with one.
2. **Neighbourhood-disjoint split by row order.** The ordered known official-test rows are cut into contiguous blocks of 1,000 rows;
   40% of the blocks (random per run) supply adaptation rows, the others are evaluation rows; 200 rows on each side of every block
   boundary between the two groups are dropped from both (a sliding window of 100 connections cannot span the gap). Three conditions
   are scored on the SAME evaluation rows: zero-shot; adaptation rows drawn at random from the evaluation blocks themselves
   ("within-file", the Task 2.5 style); adaptation rows from the other blocks ("neighbourhood-disjoint").
3. **ct_* ablation.** The 5,000- and 1,000-row `retrain_split_f0.5` runs on: `full_no_ct_window` = 48 features minus the seven window-count
   columns (ct_src_dport_ltm, ct_dst_sport_ltm, ct_srv_src, ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm; 41 features),
   `full_no_ct_any` = minus every column named ct_* (those seven plus ct_state_ttl, ct_flw_http_mthd, ct_ftp_cmd; 38 features), and the
   45-feature pool (minus sttl, dttl, ct_state_ttl), next to the standard 48- and 40-feature results.
4. **Pooled-reference composition.** What the pooled-split model trains on (rows, and the share of each official file), so the
   0.094 vs 0.109 comparison is explained.
5. **(Added because of the ordering finding.)** Validation built from contiguous blocks of the training file (same block / gap sizes)
   instead of a random 15%: does the validation-vs-test FPR gap of Task 2a shrink?

## Decision rule (declared now)
Applied to the 48-feature pool at k = 5,000 with the mean over the 5 runs, using the worse (higher FPR) of the no-near-twin subset (check 1)
and the neighbourhood-disjoint condition (check 2):
- FPR at about 95% detection <= about 0.15: the few-shot result is reported as robust to neighbourhood leakage.
- FPR >= about 0.20: the original number measured within-file adaptation, and the conclusion is restated that way.
- Between 0.15 and 0.20: reported as partly dependent on neighbourhood overlap, with both numbers shown.
Nothing is tuned to rescue the result.
