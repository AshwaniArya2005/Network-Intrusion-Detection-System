# Step A: what the official-split shift is made of (XGBoost, official split, scheme `current`)

Sources: `shift_normal_*`, `shift_ranking_stability_40f_45f_48f.csv`, `shift_nf_groups_*`, `shift_group_ablation_*`
(`scripts/characterize_shift.py`). NF = Normal flows the default model calls Fuzzers, NN = correctly predicted Normal,
TF = true Fuzzers, all on the official test split.

## Evidence
1. **The shift is detectable in every pool, and its ranking is stable.** A classifier separating train-Normal from
   official-test-Normal reaches AUC 0.8994 (40 features), 0.9293 (45) and 0.9301 (48), std <= 0.0002 over 5 seeds. SHAP
   importance rankings agree across seeds (Spearman 0.971 / 0.983 / 0.985) and across pools (0.958-0.978). The KS ranking
   is a fixed statistic of the data, so it agrees exactly on shared features; SHAP and KS rankings agree only moderately
   (Spearman 0.67 / 0.55 / 0.50), i.e. the classifier uses feature combinations, not just marginal shifts.
2. **The extra columns add shift.** 40 -> 45/48 features raises the AUC by 0.03. Without the three TTL columns it is
   unchanged (0.9293 vs 0.9301); the connection-count group takes over the top of the SHAP ranking (`ct_dst_src_ltm`).
3. **NF flows resemble Fuzzers on most groups.** Using one group at a time, AUC(NF vs NN) is 0.81-0.98 but AUC(NF vs TF)
   only 0.51-0.74 for volume_size, rate_load, timing, tcp_window_loss, protocol_state and ttl (ttl: 0.945 vs 0.506). The
   exception is connection_counts in the 45/48 pools, where NF differs from BOTH classes (0.905 vs NN, 0.937 vs TF); on
   the 40-feature pool the two connection-count features carry no signal (0.58 / 0.58).
4. **No single group is necessary for the sink.** Removing one group at a time (3 seeds) never lowers the
   Normal -> Fuzzers rate by more than 0.006 (protocol_state, 40 features: 0.2363 -> 0.2300; every other change is within
   +/- 0.002 or an increase). Removing volume_size RAISES it (+0.018 / +0.013) and the FPR (0.286 -> 0.333 / 0.294 -> 0.324).
   The train-vs-test AUC falls only when volume_size (-0.050 / -0.035), timing (-0.034 / -0.020) or connection_counts
   (-0.003 / -0.034) is removed, and stays at 0.85-0.93; rate_load, tcp_window_loss, protocol_state and ttl change it by
   <= 0.003. Groups that turn out to be irrelevant to the shift AUC: rate_load, tcp_window_loss, protocol_state, ttl.

## What the shift is made of (one paragraph)
The shift between training and official-test Normal traffic is real (AUC 0.90-0.93, controls 0.50) and is spread over
several feature groups at once: size/volume, timing and (when present) connection counts each carry part of it, and
removing one group leaves a classifier that still separates the two Normal populations at AUC 0.85-0.93, so the shift is
encoded redundantly. The Normal flows that are called Fuzzers look like Fuzzers on most groups simultaneously, so no single
group, and in particular not the TTL columns, explains the Normal -> Fuzzers errors: removing any one group does not reduce
them. The cause of the shift (for example a different capture period or host mix in the test file) is **undetermined**: the
data do not identify it, and no feature is named as the cause on correlation alone.
