# Task 5 Steps 1 and 3: narrative audit through the dashboard path (XGBoost, official split, 5 seeds x 200 flows per pool)

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

## Per predicted class (mean over seeds; all deterministic checks a-e must be 1.000)

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

## Failures

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

## Audit rates on official-test flows against validation flows (the shift check)

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
