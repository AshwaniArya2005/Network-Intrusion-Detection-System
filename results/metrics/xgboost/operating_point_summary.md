# Attack-vs-normal operating points chosen on validation, official test split (mean +/- std over seeds [42, 43, 44, 45, 46])

Thresholds on 1 - P(Normal) are fixed on the validation split (drawn from the training file) and never adjusted; `fpr_gap` = test FPR - validation FPR is the cost of the train/test shift.

| pool | rule | threshold | val detection | val FPR | test detection | test FPR | FPR gap (test - val) |
|---|---|---|---|---|---|---|---|
| 40f | argmax | n/a | 0.9637 +/- 0.0009 | 0.1198 +/- 0.0018 | 0.9594 +/- 0.0007 | 0.2853 +/- 0.0013 | 0.1654 +/- 0.0024 |
| 40f | det95 | 0.5966 +/- 0.0060 | 0.9501 +/- 0.0000 | 0.0999 +/- 0.0013 | 0.9465 +/- 0.0017 | 0.2496 +/- 0.0025 | 0.1497 +/- 0.0025 |
| 40f | fpr10 | 0.5961 +/- 0.0057 | 0.9502 +/- 0.0010 | 0.0998 +/- 0.0001 | 0.9466 +/- 0.0016 | 0.2498 +/- 0.0035 | 0.1500 +/- 0.0035 |
| 48f | argmax | n/a | 0.9691 +/- 0.0007 | 0.0996 +/- 0.0025 | 0.9681 +/- 0.0025 | 0.2933 +/- 0.0024 | 0.1937 +/- 0.0037 |
| 48f | det95 | 0.6168 +/- 0.0114 | 0.9501 +/- 0.0000 | 0.0744 +/- 0.0036 | 0.9526 +/- 0.0015 | 0.2442 +/- 0.0068 | 0.1698 +/- 0.0056 |
| 48f | fpr10 | 0.5169 +/- 0.0095 | 0.9692 +/- 0.0018 | 0.0999 +/- 0.0000 | 0.9710 +/- 0.0025 | 0.2986 +/- 0.0055 | 0.1986 +/- 0.0055 |
