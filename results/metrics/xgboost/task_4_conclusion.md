# Task 4 conclusion: open-set / zero-day detection under an honest protocol (novelty 1), XGBoost

ZERO-SHOT throughout; official split, scheme `current`, flat model; seeds 42-46, mean +/- std. Protocol declared before any result: `results/task_4_protocol.md`.
Thresholds come only from KNOWN validation flows (block-grouped, 1,000-row blocks / 200-row gaps; threshold half vs calibration half) at a **5% false-Unknown** target; the
combination rule and the "best" score were chosen on pseudo-unknowns carved from known classes (Reconnaissance / Generic held out of inner models), never on the zero-day flows.
Tables: `task_4_tables.md` (sections `open_set_step1_40f_45f_48f.md`, `open_set_step2_40f_48f.md` + `open_set_step2_sources_40f_45f_48f.md`, `open_set_step3_40f_45f_48f.md`, `open_set_step4_*.md`; CSVs `open_set_step1_<N>f.csv`, `open_set_step2_<N>f.csv`, `open_set_step4_*.csv`).
Zero-day flows after deduplication (Worms + Shellcode): 1,627 = Shellcode 1,456 (89.5%) + Worms 171. The earlier "67-75% detection at 26-28% false alarms" came from a threshold tuned on the
zero-day flows and is withdrawn.

## The claim for novelty 1
Confidence-based open-set detection flags only a minority of zero-day flows at a 5% false-Unknown budget (detection 0.16-0.34 for Worms + Shellcode with max-softmax or entropy, AUROC 0.80-0.88), depends strongly on which class
is the zero-day (max-softmax, nine held-out classes: detection 0.04-0.41, AUROC 0.63-0.90), and adds almost nothing to what the closed-set classifier already does, because 94-99% of the zero-day flows are flagged or called an attack
even at the smallest target (raising the flagged share from 4% to 22% of zero-day flows raises that catch by only 0.8-1.6 points); it also does not shield the analyst from the Normal false alarms, 88-92% of which are confidently wrong and skip the review queue.
No alternative score beats max-softmax on detection for Worms + Shellcode; across the rotation entropy is the only one that does (40 features: AUROC 0.809 vs 0.768, detection 0.266 vs 0.212), while margin, conformal, the isolation forest and the
combinations are worse. The 40 -> 48-feature gain comes from the window-count `ct_*` columns.

## Step 1: scoring functions (zero-day = Worms + Shellcode; threshold at 5% on the known threshold half; 5 seeds)
| pool | score | unknown AUROC | detection @5% | false-Unknown on test (target 5%) | pseudo-unknown validation AUROC |
|---|---|---|---|---|---|
| 40 | max-softmax (current) | 0.798 | 0.223 | 0.059 | 0.744 |
| 40 | entropy (selected on validation) | **0.862** | 0.158 | 0.025 | 0.786 |
| 40 | margin / conformal | 0.761 / 0.673 | 0.143 / 0.097 | 0.071 / 0.082 | 0.727 / 0.475 |
| 40 | isolation forest alone | 0.436 | 0.015 | 0.038 | 0.631 |
| 45 | max-softmax | 0.829 | 0.343 | 0.051 | 0.810 |
| 45 | entropy (selected) | 0.875 | 0.296 | 0.030 | 0.858 |
| 48 | max-softmax | 0.834 | 0.333 | 0.050 | 0.759 |
| 48 | entropy | 0.881 | 0.302 | 0.028 | 0.816 |
| 48 | iforest + entropy, max rule (selected on validation) | 0.810 | 0.187 | 0.034 | 0.823 |
Caption. Entropy ranks zero-day flows better than max-softmax (AUROC +0.05) but flags fewer of them at the validation-chosen threshold, because its threshold lands stricter on the shifted test flows (realised
false-Unknown 0.025-0.030 against the 5% target); max-softmax's realised test false-Unknown stays near the target (0.050-0.059). Margin and the class-conditional conformal score are worse than max-softmax; the isolation forest
trained on Normal flows alone is at or below chance (the zero-day flows look LESS anomalous than known test flows), and every combination of it with a confidence score is worse than the confidence score alone.
The pseudo-unknown selection picked entropy (40, 45 features) and iforest+entropy:max (48 features, by 0.823 vs 0.816); on the real zero-day flows that choice is worse than plain entropy (0.810 vs 0.881), so Reconnaissance / Generic
are not representative proxies for Shellcode / Worms. Shellcode dominates the zero-day set (max-softmax detection 0.25-0.38 on Shellcode against 0.04-0.06 on Worms), so one class mix is not a general result.
The realised false-Unknown on the held-out validation half is 0.041-0.054 (+/- 0.02-0.03; blocks are internally homogeneous).

## Step 2: leave-one-attack-class-out (threshold at 5% on known block-grouped validation)
| held-out class | exact twins in known data | max-softmax AUROC | detection @5% | flagged or called attack |
|---|---|---|---|---|
| Analysis | 0.78 | 0.885 | 0.253 | 0.851 |
| Backdoor | 0.81 | 0.882 | 0.273 | 0.994 |
| DoS | 0.35 | 0.697 | 0.160 | 0.984 |
| Exploits | 0.07 | 0.681 | 0.123 | 0.961 |
| Fuzzers | 0.19 | 0.693 | 0.092 | **0.262** |
| Generic | 0.05 | 0.828 | 0.400 | 0.999 |
| Reconnaissance | 0.22 | 0.800 | 0.320 | 0.859 |
| Worms | 0.08 | 0.632 | 0.041 | 0.994 |
| Shellcode | 0.11 | 0.817 | 0.244 | 0.953 |
| Overlap-Group-1 (all three) | 0.53 | 0.804 | 0.374 | 0.953 |
Caption (40 features, max-softmax; the nine classes exclude the trio row). Mean over the nine classes: AUROC 0.768, detection 0.212; the validation-selected entropy is better here: 0.809 / 0.266 (it flags more of Analysis, Backdoor, DoS, Generic and Reconnaissance, fewer of Shellcode and Worms). Margin 0.729 / 0.101 and conformal 0.555 / 0.041 are worse. Worst class: Worms (AUROC 0.632, detection 0.041). On 48 features max-softmax: 0.774 / 0.232, worst Exploits
(0.674 / 0.102); the validation-selected `iforest+entropy:max`: 0.769 / 0.217 (no better); entropy (not the validation-selected score at 48 features): 0.811 / 0.280, margin 0.741 / 0.110, conformal 0.575 / 0.060. A held-out member of Overlap-Group-1 is removed from the group's training rows while its
siblings stay known and still form the merged group (the label scheme is unchanged). The exact-twin share does NOT predict failure: Analysis and Backdoor have 78-81% twins and the highest AUROC, because their vectors also occur
under several known labels, which makes the model uncertain on exactly them. Held-out Fuzzers are mostly invisible (74% are neither flagged nor called an attack, i.e. predicted Normal). **False-alarm sources (max-softmax, 40 features, Worms + Shellcode held out):** Normal flows are
16-17% of the false alarms on validation but **60% on the official test** (Normal flows are flagged 5.7% of the time on test against ~2% on validation; 46% of the alarms on test with 48 features), while Analysis / Backdoor flows are flagged half as often on test (0.10 vs 0.21-0.27).

## Step 3: alert-level FPR and the review queue (max-softmax, 5% target, Worms + Shellcode held out)
| | 40 features | 48 features |
|---|---|---|
| alert FPR, open-set OFF (Normal called an attack) | 0.289 | 0.298 |
| alert FPR, open-set ON (attack or Unknown) | 0.311 | 0.313 |
| confident-alert FPR (called an attack, NOT sent to review) | 0.254 | 0.276 |
| review rate on Normal | 0.057 | 0.038 |
| share of false alerts that skip review | 0.878 | 0.925 |
| zero-day flows flagged Unknown | 0.223 | 0.333 |
| zero-day catch (flagged or called an attack) | 0.955 | 0.990 |
Caption. Routing uncertain flows to review lowers the alerts that reach the analyst only slightly (0.289 -> 0.254 at the 5% operating point with 40 features; 0.298 -> 0.276 with 48) for a review queue of 4-6% of Normal flows, because the shifted Normal flows
the model gets wrong are confidently wrong: 88-92% skip the queue (98% with entropy at 40 features). Halving the confident-alert FPR (0.289 -> ~0.145) takes the 30% target (confident-alert FPR 0.116-0.132, 26-28% of Normal flows sent to review) and the confidently
detected known attacks fall to 0.64-0.65 (0.91 at 5%); at 20% the confident-alert FPR is still 0.18-0.20 with 17-18% of Normal in the queue. Alert FPR with the wrapper ON can only be higher than OFF (0.311 vs 0.289). Zero-day catch is already 0.939 (40 features) / 0.984 (48 features)
at the 0.5% target (4-8% flagged) and reaches 0.955 / 0.990 at 5%, because most zero-day flows are called some attack class anyway; the Unknown flag changes the label the analyst sees more than the number of zero-day flows caught.

## Step 4: where the 40 -> 48 gain comes from (max-softmax; 5 seeds)
| variant | features | unknown AUROC | detection @5% |
|---|---|---|---|
| 40-feature pool | 40 | 0.798 | 0.223 |
| 48-feature pool | 48 | 0.834 | 0.333 |
| 48 minus the 7 window-count ct_* columns | 41 | 0.764 | 0.172 |
| 48 minus every ct_* column | 38 | 0.762 | 0.171 |
| 48-feature pool, 30-feature tier (keeps ct_srv_dst, ct_srv_src, ct_state_ttl) | 30 | 0.825 | 0.340 |
| 48-feature pool, 15-feature tier (keeps only ct_state_ttl, no window column) | 15 | 0.763 | 0.193 |
Caption. Removing the seven window-count columns (ct_src_dport_ltm, ct_dst_sport_ltm, ct_srv_src, ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm) removes the whole 40 -> 48 gain and more (detection 0.172, below the
40-feature pool's 0.223); the 30-feature tier, which keeps two window columns, keeps the gain; the 15-feature tier, which keeps none, loses it. Declared reading: **confirmed**. The ct_* window counts are the likely source of the gain; because they encode neighbouring flows of one capture, the gain should be read
as a within-capture effect.

## What did not work
- For Worms + Shellcode, entropy, margin, conformal, the Normal-trained isolation forest and all combinations flag no more zero-day flows than max-softmax at the declared threshold (entropy has the better AUROC but a stricter transferred threshold, realised false-Unknown 0.025-0.030). Margin, conformal, the isolation forest and every combination are also worse across the nine-class rotation; only entropy is better there.
- Entropy's advantage is not stable: it flags more of Analysis, Backdoor, DoS, Generic and Reconnaissance but fewer of Shellcode and Worms, so the "best score" depends on the held-out class.
- The pseudo-unknown validation does not reliably pick the best score for the real zero-day classes (48 features: it chose iforest+entropy:max, worse than entropy and max-softmax on detection).
- The review queue does not remove the confidently wrong Normal alerts.

## One paragraph
Under an honest protocol (thresholds fixed on known block-grouped validation at 5% false-Unknown, no zero-day flow used for any choice), open-set detection with the existing max-softmax confidence flags about a fifth to a third of the
Worms + Shellcode flows (AUROC 0.80-0.83), and a flag rate of 0.04-0.41 across nine held-out classes (mean 0.21-0.23), with Worms, Exploits and Fuzzers the hardest; entropy ranks better (AUROC 0.86-0.88 on Worms + Shellcode) but does not flag more of them at the transferred threshold,
although it is the best score over the nine-class rotation (mean detection 0.27-0.28, AUROC 0.81); the anomaly detector, the conformal score and margin are no help. The 48-feature gain over 40 features disappears when the window-count ct_* columns are removed, so it is a within-capture effect. Most zero-day flows are already called some attack
class, so the Unknown flag adds little catch, and routing uncertain flows to review barely lowers the alert FPR: the shifted Normal flows behind most false alerts are confidently wrong (88-92% skip the queue) and make up 46-60% of the alarms on the test split
against 8-17% on validation. Confidence is not reliable under the official-split shift, and these results come from one capture.

---

# Task 4.5: trying to improve zero-day detection (novelty 1, ZERO-SHOT)

Protocol declared before any result: `results/task_4_5_protocol.md`. Same evaluation as above: thresholds at 5% false-Unknown from known block-grouped validation, the nine-class rotation, the Overlap-Group-1 trio
and Worms + Shellcode, seeds 42-46. Score selection used the pseudo-unknown validation only (inner models without Reconnaissance or Generic), never the real zero-day classes. Declared rule: a score **clearly beats**
max-softmax when its rotation-mean detection is at least 0.05 higher, its rotation-mean AUROC is not lower, it is better in at least 4 of 5 seeds and its Worms + Shellcode detection is not more than 0.02 lower.
Tables: `task_4_5_tables.md` (one section `open_set_boost_<idea>_40f_48f.md` for each of calibration, perclass, ensemble, distance, oe, combo and iforest; the pseudo-unknown selection scores are `open_set_boost_selection_<N>f_scores.csv`).

## The updated claim for novelty 1
Cheap changes to the confidence score do not make zero-day detection good. Under an honest protocol the best result is a rank-average of ensemble mutual information and an Unknown-class probability, which raises the
nine-class mean detection at a 5% false-Unknown budget to 0.27 (40 features) / 0.34 (48 features); it clearly beats max-softmax under the declared rule, but only in a setting that removes two known classes, it is only 0.02-0.07
above entropy, it loses on Shellcode, and the flagged bucket stays mostly known flows (precision of Unknown 0.11-0.17). In the full known set the only clear gain is calibrated entropy on 48 features (0.304 against 0.234).
Per-class thresholds, ensemble variance, and kNN / Mahalanobis distance are worse than max-softmax, and the review queue still does not lower the alert FPR.

## Results (rotation mean over nine held-out classes: AUROC / detection; Worms + Shellcode detection; the full known set)
| idea | score | 40 features | 48 features | clearly beats max-softmax (40, 48) |
|---|---|---|---|---|
| baseline | max-softmax | 0.769 / 0.213; W+S 0.224 | 0.774 / 0.234; W+S 0.334 | |
| baseline (Task 4) | entropy | 0.810 / 0.266; W+S 0.159 | 0.811 / 0.283; W+S 0.294 | no, no |
| 1 calibration | max-softmax, temperature-scaled | 0.780 / 0.230; W+S 0.232 | 0.787 / 0.260; W+S 0.347 | no, no |
| 1 calibration | entropy, temperature-scaled | 0.819 / 0.276; W+S 0.165 | 0.826 / 0.304; W+S 0.317 | no, **yes** |
| 2 per-class thresholds | max-softmax / entropy | 0.705 / 0.160; 0.742 / 0.216 | 0.687 / 0.170; 0.717 / 0.253 | no, no |
| 3 ensemble (5 members) | mutual information | 0.733 / 0.202; W+S 0.134 | 0.757 / 0.268; W+S 0.335 | no, no |
| 3 ensemble | variance / ensemble max-softmax | 0.717 / 0.150; 0.770 / 0.206 | 0.734 / 0.199; 0.776 / 0.242 | no, no |
| 4 distance | kNN / Mahalanobis | 0.623 / 0.152; 0.471 / 0.098 | 0.571 / 0.156; 0.469 / 0.089 | no, no |

Caption. Temperature scaling helps a little (ECE of the known test flows 0.087 -> 0.067 and 0.112 -> 0.086; mean temperature 1.19 / 1.25) and calibrated entropy is the best score in the full known set, but its Worms + Shellcode detection
is still below max-softmax's on 40 features (0.165 against 0.224), which is why the rule says no there. The detection-at-matched-false-Unknown diagnostic (0.348 / 0.477 for calibrated entropy against 0.224 / 0.334 for max-softmax) says
part of entropy's disadvantage on Worms + Shellcode is where its threshold lands on the shifted test flows, not its ranking. Per-class thresholds split the 5% budget evenly over predicted classes and spend it on classes whose flows look
confident, so Exploits AUROC drops to 0.51 / 0.38. The two distance scores fail for a structural reason: Shellcode, 89.5% of the Worms + Shellcode set, sits **closer** to the training data than a typical known test flow (mean percentile 0.28-0.39), so distance ranks it as
more normal than normal.

## Outlier exposure and the combination (a smaller known set: two known classes, by default Reconnaissance and Generic, become the "Unknown" training class)
| score | 40 features | 48 features | clearly beats max-softmax (40, 48) |
|---|---|---|---|
| max-softmax of the model trained without them (baseline) | 0.730 / 0.128; W+S 0.248 | 0.754 / 0.209; W+S 0.416 | |
| entropy of that model (Task 4 baseline) | 0.765 / 0.200; W+S 0.462 | 0.782 / 0.318; W+S 0.598 | yes, yes (a baseline, not a new idea) |
| P(Unknown) of the Unknown-class model | 0.842 / 0.179; W+S 0.049 | 0.868 / 0.239; W+S 0.101 | no, no |
| max-softmax of the Unknown-class model | 0.754 / 0.195; W+S 0.230 | 0.752 / 0.212; W+S 0.390 | yes, no |
| **rank-average of ensemble mutual information and P(Unknown)** (chosen on pseudo-unknown validation, both pools) | 0.794 / **0.268**; W+S 0.236 | 0.810 / **0.335**; W+S 0.466 | **yes, yes** |

Caption. P(Unknown) has the best AUROC of any score (0.84-0.87) but its threshold, fixed on validation flows that almost never carry Unknown probability, lands far too strict on the shifted test flows (Worms + Shellcode detection 0.05 / 0.10, realised
false-Unknown 0.044); the rank-average repairs that. Ensemble mutual information and the Unknown-class probability had the top two mean pseudo-unknown validation AUROCs on both pools (0.818 / 0.815 at 40 features, 0.841 / 0.869 at 48). The gain is **not uniform across held-out classes**: against
max-softmax of the same setting the combination detects 0.42 / 0.34 of Exploits (against 0.10 / 0.08), 0.56 / 0.82 of Generic, 0.26 / 0.26 of Worms and 0.43 / 0.45 of Reconnaissance, but loses on Shellcode (0.21 / 0.49 against 0.28 / 0.44 at max-softmax and
0.50 / 0.64 for entropy), is flat on Worms + Shellcode (0.236 / 0.466 against 0.248 / 0.416), on the trio and on Fuzzers (0.09 / 0.12). Against **entropy** in the same setting the combination gains 0.068 / 0.017 detection and 0.029 / 0.028 AUROC but detects far fewer
Worms + Shellcode flows (0.236 / 0.466 against 0.462 / 0.598). Costs: the two pseudo-unknown classes can no longer be recognised as attacks, the known-class macro recall is 0.020-0.022 lower than for the model trained without them (0.747 -> 0.727; 0.781 -> 0.759), and in the two specs where Fuzzers had to be
used as a pseudo-unknown class 17% of known test flows are predicted Unknown. The realised false-Unknown on the official test is 0.074 / 0.082 against the 5% target. Because the baselines in this setting have lost two classes (max-softmax rotation detection 0.128 / 0.209
against 0.213 / 0.234 in the full set), the 0.268 / 0.335 are not directly comparable with the full-set figures above.

## Flagged-Unknown bucket and review queue (Worms + Shellcode held out, 5% target, official test)
| score (setting) | zero-day flagged: Shellcode / Worms | known flows flagged: Normal / Exploits / Fuzzers | precision of Unknown | alert FPR off -> on | confident-alert FPR | review rate on Normal |
|---|---|---|---|---|---|---|
| max-softmax, 40 features (full set) | 358 of 1,456 / 7 of 171 | 1,937 / 437 / 319 | 0.103 | 0.289 -> 0.311 | 0.254 | 0.057 |
| calibrated entropy, 40 features | 264 / 4 | 249 / 250 / 215 | 0.179 | 0.289 -> 0.290 | 0.283 | 0.007 |
| calibrated entropy, 48 features | 510 / 6 | 253 / 263 / 355 | 0.264 | 0.298 -> 0.299 | 0.292 | 0.007 |
| combination, 40 features (smaller known set) | 334 / 51 | 1,376 / 980 / 321 | 0.107 | 0.288 -> 0.304 | 0.263 | 0.041 |
| combination, 48 features (smaller known set) | 716 / 41 | 1,248 / 957 / 740 | 0.174 | 0.297 -> 0.308 | 0.272 | 0.037 |

Caption. Whatever the score, three quarters or more of the flagged flows are known flows (precision of Unknown 0.10-0.26). Entropy-based scores keep the queue small (under 1% of Normal) but then the confident alerts are still 0.28-0.29 of Normal; max-softmax and the combination
send 4-6% of Normal flows to review and the confident-alert FPR still stays at 0.25-0.27. No score lowers the alert FPR (it can only rise when Unknown is added); the queue does not remove the confidently wrong shifted Normal flows.

## Isolation-forest check
The sign is right: on the official test the isolation-forest score ranks known attacks above Normal flows (AUROC 0.67 on 40 features, 0.72 on 48; the same over the nine rotation runs). The zero-day flows split: Worms look more anomalous than a typical known test flow (mean percentile 0.68 / 0.71) but
Shellcode looks like an inlier (0.41 / 0.47), and Shellcode is 89.5% of the set, which is why the Task 4 union AUROC was below 0.5. The kNN score shows the same split (0.63 / 0.52 and 0.39 / 0.29); the Mahalanobis score ranks attacks below Normal (AUROC 0.41 / 0.43) and does not look
like an anomaly score on this data.

## What did not work, and the hypothesis
- Hypothesis (a guess): rotation mean detection rises from about 21% to 30-35%. **Partly:** 0.268 / 0.335 for the combination in the outlier-exposure setting, 0.276 / 0.304 for calibrated entropy in the full known set; but the first uses a smaller known set with its own lower baseline
  and the gain over entropy is 0.02-0.07.
- Per-class thresholds, ensemble variance and mutual information on their own, kNN and Mahalanobis distance, and P(Unknown) alone are not better than max-softmax at the declared threshold.
- The pseudo-unknown validation chose the same pair on both pools, so it was never tested on a case where it picks a bad one (as it did for the isolation-forest combination in Task 4).
- The review queue does not lower the alert FPR for any score.

## One paragraph (Task 4.5)
Of six ideas for improving zero-day detection, only two produce a gain that holds over seeds: temperature-scaled entropy in the full known set (detection 0.304 against 0.234 for max-softmax on 48 features) and a rank-average of ensemble disagreement and an Unknown-class probability trained
with two known classes as stand-ins (0.27 / 0.34 against 0.13 / 0.21 for max-softmax in the same, smaller setting). Both gains depend on the held-out class (Exploits, Generic, Reconnaissance and Worms gain; Shellcode and Fuzzers do not), the second removes two known attack classes from what the model can recognise,
and neither changes what the analyst receives: most of the flagged flows are still known traffic and the confidently wrong Normal alerts are not reduced. Distance-based scores fail because the most common zero-day class sits inside the training data, and one fitted anomaly score is not a reliable guide to novelty on this capture.
