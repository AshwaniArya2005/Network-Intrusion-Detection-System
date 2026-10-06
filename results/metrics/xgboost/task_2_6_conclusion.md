# Task 2.6 conclusion: is the 48-feature few-shot result adaptation or neighbour leakage?

Tables: `task_2_6_table_40f_48f_45f_41f_38f.md` (all rows), `leakage_*_summary.csv`, `leakage_*_validation_blocks*.csv`, `leakage_*_shift_auc.csv`,
`pooled_reference_composition.csv`. Protocol and decision rule were declared before any result (`results/task_2_6_protocol.md`).
Primary metric: FPR at about 95% detection with the threshold chosen on held-out labelled adaptation rows (`retrain_split_f0.5`), 5 runs.

## What was found in the data
The official files are not shuffled: consecutive rows (in id order) correlate strongly on the `ct_*` window counts (lag-1 correlation 0.67-0.76
in the test file, about 0 when shuffled) and share a class 71% of the time (28% when shuffled). Neighbouring flows therefore do share window
values and labels, so the leakage concern was well founded.

## Verdict under the declared decision rule
| 48 features, k = 5,000 | FPR at ~95% detection | detection |
|---|---|---|
| zero-shot (same rows) | 0.244 | 0.953 |
| original result (random adaptation rows) | 0.094 +/- 0.016 | 0.952 |
| rows with NO near twin (<= 0.1) in the adaptation set (check 1) | 0.096 +/- 0.016 | 0.949 |
| adaptation rows from OTHER row-order blocks, 200-row gaps (check 2) | **0.085 +/- 0.016** | 0.932 |
| adaptation rows from the evaluation blocks themselves (check 2) | 0.085 +/- 0.033 | 0.945 |

The worse of checks 1 and 2 is about 0.096, below the declared 0.15 threshold: **the 48-feature few-shot result is robust to neighbourhood
leakage.** At k = 1,000 the corresponding values are 0.159 (no near twin) and 0.153 (other blocks), at the edge of 0.15, as the original 0.158 was.

## Caveats on that verdict
- In the neighbourhood-disjoint condition the detection at the held-out threshold is 0.932, not 0.95, so the FPR at exactly 95% detection would be
  somewhat higher than 0.085 (not measured; the declared metric is as reported). The block conditions are noisy (std 0.03-0.05; blocks are internally homogeneous).
- Near twins are rare on 48 features (4.5% of evaluation rows have one within 0.1 in the 5,000 adaptation rows, 36% on 40 features), so check 1
  has little power on this pool; check 2 is the decisive one. Evaluation rows do have more twins among the adaptation rows than among an equal-size random
  subset of training rows (exact 1.34% vs 0.11%, within 0.1 4.5% vs 1.9%), i.e. a measurable but small neighbour effect.
- Block-disjoint adaptation still draws on the same capture: the same hosts and campaigns recur across blocks. The result measures adaptation within
  one capture; transfer to another capture was not tested.

## What it relies on (check 3)
| k = 5,000, retrain_split_f0.5 | features | FPR at ~95% detection |
|---|---|---|
| 48-feature pool | 48 | 0.094 +/- 0.016 |
| minus sttl, dttl, ct_state_ttl | 45 | 0.111 +/- 0.019 |
| minus the 7 window-count ct_* columns (ct_src_dport_ltm, ct_dst_sport_ltm, ct_srv_src, ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm) | 41 | 0.231 +/- 0.011 |
| minus every ct_* column (those 7 + ct_state_ttl, ct_flw_http_mthd, ct_ftp_cmd) | 38 | 0.228 +/- 0.013 |
| 40-feature pool | 40 | 0.232 |
The gain depends on the window-count `ct_*` columns, not on the TTL columns. Without them the 48-feature pool behaves like the 40-feature one.

## The 40-feature pool
Its small gain is partly neighbour-dependent: adaptation rows drawn inside the evaluation blocks give 0.203, rows from other blocks 0.243, zero-shot 0.251.
(Near-twin share is high there, 36% within 0.1, and the subset rows with a twin have much lower FPR for the zero-shot model as well.)

## Pooled reference (check 4)
The pooled random split trains on 109,559 rows, 37,013 of them from the official test file (67.8% of it), interleaved with the rows it is tested on; the
5,000-row few-shot run uses 9.2% of the test file. The comparison 0.094 vs 0.109 is not like for like, and the pooled number is itself neighbour-inflated.

## Consequences for earlier claims
- **Validation vs test FPR (Task 2a).** The random 15% validation shares neighbours with the training rows. A validation built from contiguous blocks gives a
  mean FPR of 0.25 / 0.24 (1,000-row blocks; 40 / 48 features) and 0.19 / 0.19 (200-row blocks) against 0.12 / 0.10 for the random validation, so the
  validation-vs-test gap shrinks from 0.17 / 0.19 to 0.04 / 0.06 (1,000-row blocks) or 0.10 / 0.11 (200-row blocks). The block estimates are very noisy
  (0.03-0.60 across draws), so the size of the neighbour effect is not pinned down, but the "cost of the split shift of 0.15-0.20" overstated the
  distribution shift: part of it is neighbour leakage in the random validation split (and in the pooled split).
- **Train-vs-test Normal AUC (Task 2.5 Step A).** With random cross-validation 0.899 / 0.929 / 0.930 (40 / 45 / 48 features); with CV grouped by contiguous
  blocks 0.814 / 0.836 / 0.837 (seed 42). The shift is real (control 0.50) but about 0.09 of the earlier AUC was neighbour leakage. The per-group AUC changes of
  Step A's ablation used random CV and were not re-run; the Normal -> Fuzzers results on the official test split are unaffected.

## The claim, restated
With about 5,000 labelled flows from the same capture (9% of the test file) and a held-out labelled half to set the threshold, the 48-feature model
reaches FPR about 0.09 at about 95% detection on flows from other time blocks of that capture (zero-shot 0.24). This is within-capture adaptation: it
relies on the window-count `ct_*` columns, is borderline at 1,000 labelled flows, is not shown for the 40-feature pool, and was not tested on a different
capture. Beating the pooled-split reference does not show more than that, because the pooled model trains on 68% of the test file.

## One paragraph
The 0.094 is robust to the leakage this task tested for: it stays at 0.085-0.096 when evaluation rows have no near twin in the adaptation set and when
adaptation rows come from other blocks of the file with a gap. It relies on the window-count connection columns (removing them returns FPR to 0.23) and on
adapting inside one capture, whose hosts and campaigns recur across blocks; it does not show transfer to a new deployment. The same investigation showed
that two earlier numbers were partly neighbour artefacts - the random validation FPR (0.10-0.12 against 0.19-0.25 for block-built validation) and the
train-vs-test shift AUC (0.90-0.93 against 0.81-0.84 with block-grouped cross-validation) - so the distribution shift is real but smaller than first reported.
