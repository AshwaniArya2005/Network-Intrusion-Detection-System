# Novelty 1: open-set (zero-day) detection

Open-set studies and their boosts: conclusions, tables and the declared protocols.

File names mentioned inside this file (for example `task_6_tables.md`, `results/task_5_protocol.md` or `xai_audit_40f_example_failures.csv`) are the `Source:` sections of this file or of one of the other numbered files, or files that were removed in the cleanup and are recoverable from the git tags `pre-cleanup-2026-10` and `pre-lean-2026-10`. Text under a `Source:` heading is the original file, unchanged except that its headings are demoted two levels. Two kinds of file moved after the originals were written: the feature rankings are now in `results/rankings/` and the A/B rating sheet, key and instructions in `results/rating/`.

## Source: task_4_conclusion.md

### Task 4 conclusion: open-set / zero-day detection under an honest protocol (novelty 1), XGBoost

ZERO-SHOT throughout; official split, scheme `current`, flat model; seeds 42-46, mean +/- std. Protocol declared before any result: `results/task_4_protocol.md`.
Thresholds come only from KNOWN validation flows (block-grouped, 1,000-row blocks / 200-row gaps; threshold half vs calibration half) at a **5% false-Unknown** target; the
combination rule and the "best" score were chosen on pseudo-unknowns carved from known classes (Reconnaissance / Generic held out of inner models), never on the zero-day flows.
Tables: `task_4_tables.md` (sections `open_set_step1_40f_45f_48f.md`, `open_set_step2_40f_48f.md` + `open_set_step2_sources_40f_45f_48f.md`, `open_set_step3_40f_45f_48f.md`, `open_set_step4_*.md`; CSVs `open_set_step1_<N>f.csv`, `open_set_step2_<N>f.csv`, `open_set_step4_*.csv`).
Zero-day flows after deduplication (Worms + Shellcode): 1,627 = Shellcode 1,456 (89.5%) + Worms 171. The earlier "67-75% detection at 26-28% false alarms" came from a threshold tuned on the
zero-day flows and is withdrawn.

#### The claim for novelty 1
Confidence-based open-set detection flags only a minority of zero-day flows at a 5% false-Unknown budget (detection 0.16-0.34 for Worms + Shellcode with max-softmax or entropy, AUROC 0.80-0.88), depends strongly on which class
is the zero-day (max-softmax, nine held-out classes: detection 0.04-0.41, AUROC 0.63-0.90), and adds almost nothing to what the closed-set classifier already does, because 94-99% of the zero-day flows are flagged or called an attack
even at the smallest target (raising the flagged share from 4% to 22% of zero-day flows raises that catch by only 0.8-1.6 points); it also does not shield the analyst from the Normal false alarms, 88-92% of which are confidently wrong and skip the review queue.
No alternative score beats max-softmax on detection for Worms + Shellcode; across the rotation entropy is the only one that does (40 features: AUROC 0.809 vs 0.768, detection 0.266 vs 0.212), while margin, conformal, the isolation forest and the
combinations are worse. The 40 -> 48-feature gain comes from the window-count `ct_*` columns.

#### Step 1: scoring functions (zero-day = Worms + Shellcode; threshold at 5% on the known threshold half; 5 seeds)
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

#### Step 2: leave-one-attack-class-out (threshold at 5% on known block-grouped validation)
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

#### Step 3: alert-level FPR and the review queue (max-softmax, 5% target, Worms + Shellcode held out)
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

#### Step 4: where the 40 -> 48 gain comes from (max-softmax; 5 seeds)
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

#### What did not work
- For Worms + Shellcode, entropy, margin, conformal, the Normal-trained isolation forest and all combinations flag no more zero-day flows than max-softmax at the declared threshold (entropy has the better AUROC but a stricter transferred threshold, realised false-Unknown 0.025-0.030). Margin, conformal, the isolation forest and every combination are also worse across the nine-class rotation; only entropy is better there.
- Entropy's advantage is not stable: it flags more of Analysis, Backdoor, DoS, Generic and Reconnaissance but fewer of Shellcode and Worms, so the "best score" depends on the held-out class.
- The pseudo-unknown validation does not reliably pick the best score for the real zero-day classes (48 features: it chose iforest+entropy:max, worse than entropy and max-softmax on detection).
- The review queue does not remove the confidently wrong Normal alerts.

#### One paragraph
Under an honest protocol (thresholds fixed on known block-grouped validation at 5% false-Unknown, no zero-day flow used for any choice), open-set detection with the existing max-softmax confidence flags about a fifth to a third of the
Worms + Shellcode flows (AUROC 0.80-0.83), and a flag rate of 0.04-0.41 across nine held-out classes (mean 0.21-0.23), with Worms, Exploits and Fuzzers the hardest; entropy ranks better (AUROC 0.86-0.88 on Worms + Shellcode) but does not flag more of them at the transferred threshold,
although it is the best score over the nine-class rotation (mean detection 0.27-0.28, AUROC 0.81); the anomaly detector, the conformal score and margin are no help. The 48-feature gain over 40 features disappears when the window-count ct_* columns are removed, so it is a within-capture effect. Most zero-day flows are already called some attack
class, so the Unknown flag adds little catch, and routing uncertain flows to review barely lowers the alert FPR: the shifted Normal flows behind most false alerts are confidently wrong (88-92% skip the queue) and make up 46-60% of the alarms on the test split
against 8-17% on validation. Confidence is not reliable under the official-split shift, and these results come from one capture.

---

### Task 4.5: trying to improve zero-day detection (novelty 1, ZERO-SHOT)

Protocol declared before any result: `results/task_4_5_protocol.md`. Same evaluation as above: thresholds at 5% false-Unknown from known block-grouped validation, the nine-class rotation, the Overlap-Group-1 trio
and Worms + Shellcode, seeds 42-46. Score selection used the pseudo-unknown validation only (inner models without Reconnaissance or Generic), never the real zero-day classes. Declared rule: a score **clearly beats**
max-softmax when its rotation-mean detection is at least 0.05 higher, its rotation-mean AUROC is not lower, it is better in at least 4 of 5 seeds and its Worms + Shellcode detection is not more than 0.02 lower.
Tables: `task_4_5_tables.md` (one section `open_set_boost_<idea>_40f_48f.md` for each of calibration, perclass, ensemble, distance, oe, combo and iforest; the pseudo-unknown selection scores are `open_set_boost_selection_<N>f_scores.csv`).

#### The updated claim for novelty 1
Cheap changes to the confidence score do not make zero-day detection good. Under an honest protocol the best result is a rank-average of ensemble mutual information and an Unknown-class probability, which raises the
nine-class mean detection at a 5% false-Unknown budget to 0.27 (40 features) / 0.34 (48 features); it clearly beats max-softmax under the declared rule, but only in a setting that removes two known classes, it is only 0.02-0.07
above entropy, it loses on Shellcode, and the flagged bucket stays mostly known flows (precision of Unknown 0.11-0.17). In the full known set the only clear gain is calibrated entropy on 48 features (0.304 against 0.234).
Per-class thresholds, ensemble variance, and kNN / Mahalanobis distance are worse than max-softmax, and the review queue still does not lower the alert FPR.

#### Results (rotation mean over nine held-out classes: AUROC / detection; Worms + Shellcode detection; the full known set)
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

#### Outlier exposure and the combination (a smaller known set: two known classes, by default Reconnaissance and Generic, become the "Unknown" training class)
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

#### Flagged-Unknown bucket and review queue (Worms + Shellcode held out, 5% target, official test)
| score (setting) | zero-day flagged: Shellcode / Worms | known flows flagged: Normal / Exploits / Fuzzers | precision of Unknown | alert FPR off -> on | confident-alert FPR | review rate on Normal |
|---|---|---|---|---|---|---|
| max-softmax, 40 features (full set) | 358 of 1,456 / 7 of 171 | 1,937 / 437 / 319 | 0.103 | 0.289 -> 0.311 | 0.254 | 0.057 |
| calibrated entropy, 40 features | 264 / 4 | 249 / 250 / 215 | 0.179 | 0.289 -> 0.290 | 0.283 | 0.007 |
| calibrated entropy, 48 features | 510 / 6 | 253 / 263 / 355 | 0.264 | 0.298 -> 0.299 | 0.292 | 0.007 |
| combination, 40 features (smaller known set) | 334 / 51 | 1,376 / 980 / 321 | 0.107 | 0.288 -> 0.304 | 0.263 | 0.041 |
| combination, 48 features (smaller known set) | 716 / 41 | 1,248 / 957 / 740 | 0.174 | 0.297 -> 0.308 | 0.272 | 0.037 |

Caption. Whatever the score, three quarters or more of the flagged flows are known flows (precision of Unknown 0.10-0.26). Entropy-based scores keep the queue small (under 1% of Normal) but then the confident alerts are still 0.28-0.29 of Normal; max-softmax and the combination
send 4-6% of Normal flows to review and the confident-alert FPR still stays at 0.25-0.27. No score lowers the alert FPR (it can only rise when Unknown is added); the queue does not remove the confidently wrong shifted Normal flows.

#### Isolation-forest check
The sign is right: on the official test the isolation-forest score ranks known attacks above Normal flows (AUROC 0.67 on 40 features, 0.72 on 48; the same over the nine rotation runs). The zero-day flows split: Worms look more anomalous than a typical known test flow (mean percentile 0.68 / 0.71) but
Shellcode looks like an inlier (0.41 / 0.47), and Shellcode is 89.5% of the set, which is why the Task 4 union AUROC was below 0.5. The kNN score shows the same split (0.63 / 0.52 and 0.39 / 0.29); the Mahalanobis score ranks attacks below Normal (AUROC 0.41 / 0.43) and does not look
like an anomaly score on this data.

#### What did not work, and the hypothesis
- Hypothesis (a guess): rotation mean detection rises from about 21% to 30-35%. **Partly:** 0.268 / 0.335 for the combination in the outlier-exposure setting, 0.276 / 0.304 for calibrated entropy in the full known set; but the first uses a smaller known set with its own lower baseline
  and the gain over entropy is 0.02-0.07.
- Per-class thresholds, ensemble variance and mutual information on their own, kNN and Mahalanobis distance, and P(Unknown) alone are not better than max-softmax at the declared threshold.
- The pseudo-unknown validation chose the same pair on both pools, so it was never tested on a case where it picks a bad one (as it did for the isolation-forest combination in Task 4).
- The review queue does not lower the alert FPR for any score.

#### One paragraph (Task 4.5)
Of six ideas for improving zero-day detection, only two produce a gain that holds over seeds: temperature-scaled entropy in the full known set (detection 0.304 against 0.234 for max-softmax on 48 features) and a rank-average of ensemble disagreement and an Unknown-class probability trained
with two known classes as stand-ins (0.27 / 0.34 against 0.13 / 0.21 for max-softmax in the same, smaller setting). Both gains depend on the held-out class (Exploits, Generic, Reconnaissance and Worms gain; Shellcode and Fuzzers do not), the second removes two known attack classes from what the model can recognise,
and neither changes what the analyst receives: most of the flagged flows are still known traffic and the confidently wrong Normal alerts are not reduced. Distance-based scores fail because the most common zero-day class sits inside the training data, and one fitted anomaly score is not a reliable guide to novelty on this capture.

## Source: open_set_step1_40f_45f_48f.md

### Task 4 Step 1: open-set scoring functions (XGBoost, official split, block-grouped validation, threshold at 5% false-Unknown, mean +/- std over 5 seeds)

Zero-day = Worms + Shellcode (Shellcode is 89.5% of the 1,627 flows). Threshold fixed on the known THRESHOLD half of the validation flows; `false-Unknown cal half` is the held-out validation half, `false-Unknown test` the official test known flows (the gap to 5% is the cost of the shift). `chosen` = candidates after the rule choice; `*` = best on pseudo-unknown validation (used downstream), `+` = best on the real zero-day AUROC (reported only). Pseudo-unknown AUROC = validation flows of Reconnaissance / Generic held out of an inner model.

#### 40f  (rules chosen on validation: {'msp': 'mean', 'entropy': 'mean', 'margin': 'mean', 'conformal': 'max'}; best: **entropy**)

| score | chosen | unknown AUROC | detection @5% | flagged or called attack | det. Shellcode | det. Worms | false-Unknown thr half | cal half | test | pseudo-unknown AUROC |
|---|---|---|---|---|---|---|---|---|---|---|
| msp | yes | 0.798 +/- 0.004 | 0.223 +/- 0.037 | 0.955 +/- 0.009 | 0.245 | 0.040 | 0.050 +/- 0.000 | 0.044 +/- 0.019 | 0.059 +/- 0.014 | 0.744 |
| entropy*+ | yes | 0.862 +/- 0.005 | 0.158 +/- 0.047 | 0.940 +/- 0.012 | 0.174 | 0.025 | 0.048 +/- 0.003 | 0.041 +/- 0.026 | 0.025 +/- 0.010 | 0.786 |
| margin | yes | 0.761 +/- 0.003 | 0.143 +/- 0.043 | 0.958 +/- 0.006 | 0.155 | 0.037 | 0.050 +/- 0.000 | 0.047 +/- 0.019 | 0.071 +/- 0.020 | 0.727 |
| conformal | yes | 0.673 +/- 0.086 | 0.097 +/- 0.056 | 0.964 +/- 0.016 | 0.104 | 0.039 | 0.050 +/- 0.000 | 0.054 +/- 0.034 | 0.082 +/- 0.033 | 0.475 |
| iforest | yes | 0.436 +/- 0.019 | 0.015 +/- 0.003 | 0.935 +/- 0.014 | 0.000 | 0.138 | 0.050 +/- 0.000 | 0.053 +/- 0.012 | 0.038 +/- 0.006 | 0.631 |
| iforest+msp:mean | yes | 0.645 +/- 0.048 | 0.024 +/- 0.008 | 0.937 +/- 0.014 | 0.022 | 0.043 | 0.050 +/- 0.000 | 0.044 +/- 0.024 | 0.038 +/- 0.014 | 0.729 |
| iforest+msp:max | no | 0.714 +/- 0.036 | 0.163 +/- 0.057 | 0.948 +/- 0.009 | 0.171 | 0.092 | 0.049 +/- 0.000 | 0.050 +/- 0.018 | 0.056 +/- 0.014 | 0.727 |
| iforest+entropy:mean | yes | 0.676 +/- 0.061 | 0.021 +/- 0.010 | 0.936 +/- 0.014 | 0.018 | 0.044 | 0.050 +/- 0.000 | 0.048 +/- 0.025 | 0.034 +/- 0.014 | 0.749 |
| iforest+entropy:max | no | 0.794 +/- 0.031 | 0.121 +/- 0.033 | 0.939 +/- 0.012 | 0.126 | 0.080 | 0.049 +/- 0.001 | 0.045 +/- 0.022 | 0.031 +/- 0.007 | 0.741 |
| iforest+margin:mean | yes | 0.623 +/- 0.041 | 0.022 +/- 0.009 | 0.937 +/- 0.014 | 0.019 | 0.048 | 0.050 +/- 0.000 | 0.042 +/- 0.022 | 0.041 +/- 0.016 | 0.723 |
| iforest+margin:max | no | 0.668 +/- 0.038 | 0.086 +/- 0.036 | 0.950 +/- 0.009 | 0.086 | 0.083 | 0.050 +/- 0.001 | 0.048 +/- 0.015 | 0.057 +/- 0.013 | 0.718 |
| iforest+conformal:mean | no | 0.584 +/- 0.058 | 0.016 +/- 0.002 | 0.938 +/- 0.012 | 0.014 | 0.032 | 0.050 +/- 0.000 | 0.045 +/- 0.020 | 0.058 +/- 0.027 | 0.567 |
| iforest+conformal:max | yes | 0.584 +/- 0.096 | 0.068 +/- 0.036 | 0.955 +/- 0.019 | 0.065 | 0.092 | 0.049 +/- 0.001 | 0.046 +/- 0.019 | 0.066 +/- 0.022 | 0.666 |

#### 45f  (rules chosen on validation: {'msp': 'max', 'entropy': 'max', 'margin': 'max', 'conformal': 'max'}; best: **entropy**)

| score | chosen | unknown AUROC | detection @5% | flagged or called attack | det. Shellcode | det. Worms | false-Unknown thr half | cal half | test | pseudo-unknown AUROC |
|---|---|---|---|---|---|---|---|---|---|---|
| msp | yes | 0.829 +/- 0.010 | 0.343 +/- 0.036 | 0.989 +/- 0.004 | 0.376 | 0.063 | 0.050 +/- 0.000 | 0.045 +/- 0.024 | 0.051 +/- 0.017 | 0.810 |
| entropy*+ | yes | 0.875 +/- 0.010 | 0.296 +/- 0.059 | 0.985 +/- 0.006 | 0.328 | 0.025 | 0.050 +/- 0.000 | 0.048 +/- 0.035 | 0.030 +/- 0.014 | 0.858 |
| margin | yes | 0.796 +/- 0.008 | 0.205 +/- 0.058 | 0.987 +/- 0.004 | 0.223 | 0.050 | 0.050 +/- 0.000 | 0.043 +/- 0.018 | 0.065 +/- 0.020 | 0.772 |
| conformal | yes | 0.628 +/- 0.101 | 0.102 +/- 0.090 | 0.987 +/- 0.006 | 0.106 | 0.067 | 0.050 +/- 0.000 | 0.050 +/- 0.030 | 0.081 +/- 0.034 | 0.710 |
| iforest | yes | 0.456 +/- 0.020 | 0.011 +/- 0.003 | 0.978 +/- 0.007 | 0.000 | 0.108 | 0.050 +/- 0.000 | 0.059 +/- 0.030 | 0.052 +/- 0.011 | 0.667 |
| iforest+msp:mean | no | 0.679 +/- 0.045 | 0.046 +/- 0.012 | 0.980 +/- 0.007 | 0.044 | 0.064 | 0.050 +/- 0.000 | 0.043 +/- 0.023 | 0.036 +/- 0.013 | 0.771 |
| iforest+msp:max | yes | 0.754 +/- 0.031 | 0.271 +/- 0.068 | 0.987 +/- 0.004 | 0.294 | 0.078 | 0.050 +/- 0.000 | 0.051 +/- 0.028 | 0.054 +/- 0.014 | 0.807 |
| iforest+entropy:mean | no | 0.701 +/- 0.054 | 0.049 +/- 0.016 | 0.979 +/- 0.007 | 0.046 | 0.078 | 0.050 +/- 0.000 | 0.047 +/- 0.026 | 0.035 +/- 0.013 | 0.795 |
| iforest+entropy:max | yes | 0.809 +/- 0.031 | 0.200 +/- 0.048 | 0.984 +/- 0.006 | 0.217 | 0.056 | 0.049 +/- 0.001 | 0.049 +/- 0.035 | 0.036 +/- 0.012 | 0.846 |
| iforest+margin:mean | no | 0.661 +/- 0.039 | 0.044 +/- 0.015 | 0.979 +/- 0.007 | 0.041 | 0.070 | 0.050 +/- 0.000 | 0.042 +/- 0.027 | 0.040 +/- 0.016 | 0.756 |
| iforest+margin:max | yes | 0.707 +/- 0.034 | 0.123 +/- 0.046 | 0.984 +/- 0.006 | 0.129 | 0.069 | 0.049 +/- 0.001 | 0.046 +/- 0.017 | 0.061 +/- 0.012 | 0.775 |
| iforest+conformal:mean | no | 0.568 +/- 0.075 | 0.035 +/- 0.014 | 0.980 +/- 0.005 | 0.030 | 0.071 | 0.050 +/- 0.000 | 0.044 +/- 0.023 | 0.064 +/- 0.031 | 0.727 |
| iforest+conformal:max | yes | 0.560 +/- 0.102 | 0.070 +/- 0.057 | 0.984 +/- 0.006 | 0.068 | 0.085 | 0.049 +/- 0.001 | 0.051 +/- 0.030 | 0.073 +/- 0.025 | 0.731 |

#### 48f  (rules chosen on validation: {'msp': 'max', 'entropy': 'max', 'margin': 'max', 'conformal': 'max'}; best: **iforest+entropy:max**)

| score | chosen | unknown AUROC | detection @5% | flagged or called attack | det. Shellcode | det. Worms | false-Unknown thr half | cal half | test | pseudo-unknown AUROC |
|---|---|---|---|---|---|---|---|---|---|---|
| msp | yes | 0.834 +/- 0.007 | 0.333 +/- 0.044 | 0.990 +/- 0.003 | 0.366 | 0.055 | 0.050 +/- 0.000 | 0.045 +/- 0.025 | 0.050 +/- 0.017 | 0.759 |
| entropy+ | yes | 0.881 +/- 0.008 | 0.302 +/- 0.068 | 0.987 +/- 0.004 | 0.334 | 0.028 | 0.050 +/- 0.000 | 0.048 +/- 0.034 | 0.028 +/- 0.012 | 0.816 |
| margin | yes | 0.800 +/- 0.006 | 0.205 +/- 0.062 | 0.988 +/- 0.002 | 0.224 | 0.044 | 0.050 +/- 0.000 | 0.044 +/- 0.019 | 0.067 +/- 0.021 | 0.730 |
| conformal | yes | 0.659 +/- 0.101 | 0.117 +/- 0.105 | 0.990 +/- 0.006 | 0.124 | 0.060 | 0.050 +/- 0.000 | 0.051 +/- 0.028 | 0.091 +/- 0.042 | 0.627 |
| iforest | yes | 0.498 +/- 0.028 | 0.013 +/- 0.005 | 0.981 +/- 0.005 | 0.000 | 0.120 | 0.050 +/- 0.000 | 0.054 +/- 0.033 | 0.050 +/- 0.015 | 0.685 |
| iforest+msp:mean | no | 0.692 +/- 0.034 | 0.048 +/- 0.020 | 0.983 +/- 0.005 | 0.040 | 0.118 | 0.050 +/- 0.000 | 0.045 +/- 0.028 | 0.038 +/- 0.019 | 0.757 |
| iforest+msp:max | yes | 0.752 +/- 0.033 | 0.254 +/- 0.088 | 0.988 +/- 0.003 | 0.274 | 0.082 | 0.050 +/- 0.000 | 0.047 +/- 0.028 | 0.052 +/- 0.017 | 0.786 |
| iforest+entropy:mean | no | 0.719 +/- 0.043 | 0.046 +/- 0.020 | 0.983 +/- 0.005 | 0.035 | 0.144 | 0.050 +/- 0.000 | 0.047 +/- 0.028 | 0.036 +/- 0.016 | 0.786 |
| iforest+entropy:max* | yes | 0.810 +/- 0.031 | 0.187 +/- 0.050 | 0.985 +/- 0.003 | 0.202 | 0.058 | 0.048 +/- 0.002 | 0.046 +/- 0.035 | 0.034 +/- 0.013 | 0.823 |
| iforest+margin:mean | no | 0.672 +/- 0.029 | 0.045 +/- 0.018 | 0.983 +/- 0.005 | 0.036 | 0.123 | 0.050 +/- 0.000 | 0.043 +/- 0.026 | 0.041 +/- 0.019 | 0.743 |
| iforest+margin:max | yes | 0.705 +/- 0.036 | 0.128 +/- 0.057 | 0.986 +/- 0.004 | 0.134 | 0.082 | 0.050 +/- 0.000 | 0.042 +/- 0.018 | 0.058 +/- 0.016 | 0.762 |
| iforest+conformal:mean | no | 0.611 +/- 0.058 | 0.043 +/- 0.023 | 0.985 +/- 0.004 | 0.032 | 0.135 | 0.050 +/- 0.000 | 0.045 +/- 0.018 | 0.077 +/- 0.038 | 0.709 |
| iforest+conformal:max | yes | 0.585 +/- 0.107 | 0.078 +/- 0.065 | 0.987 +/- 0.005 | 0.076 | 0.098 | 0.049 +/- 0.001 | 0.045 +/- 0.024 | 0.071 +/- 0.029 | 0.724 |

## Source: open_set_step2_40f_48f.md

### Task 4 Step 2: leave-one-attack-class-out (XGBoost, official split, threshold at 5% false-Unknown on block-grouped known validation, mean +/- std over 5 seeds)

Each class is held out in turn (never trained on); `best` = the pool's pseudo-unknown-selected score, compared with `msp`. Overlap-Group-1 members are held out one at a time (siblings stay known and still form the merged group); the trio is also held out as a unit. `exact twin share` = share of the class's flows with an identical feature vector among the known flows.

#### 40f  (best score: entropy)

| held-out class | flows | exact twin share | score | AUROC | detection @5% | flagged or called attack | false-Unknown test |
|---|---|---|---|---|---|---|---|
| Analysis | 2032 | 0.78 | msp | 0.885 +/- 0.009 | 0.253 +/- 0.115 | 0.851 +/- 0.006 | 0.047 +/- 0.010 |
| Analysis | 2032 | 0.78 | entropy | 0.924 +/- 0.003 | 0.363 +/- 0.137 | 0.842 +/- 0.008 | 0.031 +/- 0.010 |
| Backdoor | 1880 | 0.81 | msp | 0.882 +/- 0.009 | 0.273 +/- 0.104 | 0.994 +/- 0.004 | 0.055 +/- 0.015 |
| Backdoor | 1880 | 0.81 | entropy | 0.926 +/- 0.005 | 0.420 +/- 0.144 | 0.993 +/- 0.003 | 0.034 +/- 0.011 |
| DoS | 5500 | 0.35 | msp | 0.697 +/- 0.006 | 0.160 +/- 0.042 | 0.984 +/- 0.004 | 0.070 +/- 0.023 |
| DoS | 5500 | 0.35 | entropy | 0.736 +/- 0.007 | 0.204 +/- 0.069 | 0.976 +/- 0.005 | 0.036 +/- 0.021 |
| Exploits | 27434 | 0.07 | msp | 0.681 +/- 0.010 | 0.123 +/- 0.035 | 0.961 +/- 0.007 | 0.073 +/- 0.037 |
| Exploits | 27434 | 0.07 | entropy | 0.710 +/- 0.007 | 0.119 +/- 0.020 | 0.957 +/- 0.007 | 0.041 +/- 0.007 |
| Fuzzers | 20960 | 0.19 | msp | 0.693 +/- 0.007 | 0.092 +/- 0.019 | 0.262 +/- 0.016 | 0.065 +/- 0.017 |
| Fuzzers | 20960 | 0.19 | entropy | 0.699 +/- 0.007 | 0.103 +/- 0.023 | 0.259 +/- 0.018 | 0.055 +/- 0.017 |
| Generic | 7599 | 0.05 | msp | 0.828 +/- 0.067 | 0.400 +/- 0.229 | 0.999 +/- 0.000 | 0.081 +/- 0.024 |
| Generic | 7599 | 0.05 | entropy | 0.896 +/- 0.036 | 0.607 +/- 0.217 | 0.998 +/- 0.001 | 0.058 +/- 0.016 |
| Reconnaissance | 9991 | 0.22 | msp | 0.800 +/- 0.010 | 0.320 +/- 0.100 | 0.859 +/- 0.070 | 0.069 +/- 0.018 |
| Reconnaissance | 9991 | 0.22 | entropy | 0.839 +/- 0.010 | 0.377 +/- 0.158 | 0.897 +/- 0.063 | 0.062 +/- 0.027 |
| Worms | 171 | 0.08 | msp | 0.632 +/- 0.016 | 0.041 +/- 0.024 | 0.994 +/- 0.000 | 0.064 +/- 0.019 |
| Worms | 171 | 0.08 | entropy | 0.671 +/- 0.016 | 0.033 +/- 0.022 | 0.994 +/- 0.000 | 0.039 +/- 0.012 |
| Shellcode | 1456 | 0.11 | msp | 0.817 +/- 0.003 | 0.244 +/- 0.057 | 0.953 +/- 0.013 | 0.061 +/- 0.017 |
| Shellcode | 1456 | 0.11 | entropy | 0.882 +/- 0.004 | 0.170 +/- 0.057 | 0.935 +/- 0.017 | 0.024 +/- 0.009 |
| Overlap-Group-1 (all three) | 9412 | 0.53 | msp | 0.804 +/- 0.005 | 0.374 +/- 0.109 | 0.953 +/- 0.010 | 0.040 +/- 0.026 |
| Overlap-Group-1 (all three) | 9412 | 0.53 | entropy | 0.816 +/- 0.003 | 0.369 +/- 0.131 | 0.954 +/- 0.012 | 0.040 +/- 0.028 |
| **mean over the nine classes** | | | entropy | 0.809 | 0.266 | 0.872 | 0.042 |
| **worst class by AUROC (Worms)** | | | entropy | 0.671 | 0.033 | 0.994 | 0.039 |
| **mean over the nine classes** | | | msp | 0.768 | 0.212 | 0.873 | 0.065 |
| **worst class by AUROC (Worms)** | | | msp | 0.632 | 0.041 | 0.994 | 0.064 |

#### 48f  (best score: iforest+entropy:max)

| held-out class | flows | exact twin share | score | AUROC | detection @5% | flagged or called attack | false-Unknown test |
|---|---|---|---|---|---|---|---|
| Analysis | 2032 | 0.78 | msp | 0.882 +/- 0.016 | 0.381 +/- 0.152 | 0.845 +/- 0.003 | 0.039 +/- 0.015 |
| Analysis | 2032 | 0.78 | iforest+entropy:max | 0.864 +/- 0.020 | 0.243 +/- 0.115 | 0.843 +/- 0.004 | 0.037 +/- 0.010 |
| Backdoor | 1880 | 0.81 | msp | 0.900 +/- 0.012 | 0.414 +/- 0.180 | 0.998 +/- 0.001 | 0.043 +/- 0.021 |
| Backdoor | 1880 | 0.81 | iforest+entropy:max | 0.885 +/- 0.025 | 0.312 +/- 0.143 | 0.997 +/- 0.001 | 0.039 +/- 0.014 |
| DoS | 5500 | 0.34 | msp | 0.713 +/- 0.007 | 0.167 +/- 0.043 | 0.994 +/- 0.002 | 0.048 +/- 0.022 |
| DoS | 5500 | 0.34 | iforest+entropy:max | 0.710 +/- 0.011 | 0.171 +/- 0.046 | 0.992 +/- 0.003 | 0.034 +/- 0.016 |
| Exploits | 27434 | 0.07 | msp | 0.674 +/- 0.007 | 0.102 +/- 0.030 | 0.969 +/- 0.003 | 0.065 +/- 0.031 |
| Exploits | 27434 | 0.07 | iforest+entropy:max | 0.672 +/- 0.006 | 0.115 +/- 0.035 | 0.964 +/- 0.003 | 0.045 +/- 0.024 |
| Fuzzers | 20960 | 0.10 | msp | 0.698 +/- 0.006 | 0.082 +/- 0.017 | 0.238 +/- 0.015 | 0.051 +/- 0.012 |
| Fuzzers | 20960 | 0.10 | iforest+entropy:max | 0.647 +/- 0.008 | 0.092 +/- 0.027 | 0.246 +/- 0.023 | 0.051 +/- 0.018 |
| Generic | 7599 | 0.04 | msp | 0.773 +/- 0.057 | 0.187 +/- 0.098 | 0.906 +/- 0.094 | 0.064 +/- 0.024 |
| Generic | 7599 | 0.04 | iforest+entropy:max | 0.878 +/- 0.017 | 0.305 +/- 0.158 | 0.900 +/- 0.102 | 0.043 +/- 0.010 |
| Reconnaissance | 9991 | 0.16 | msp | 0.792 +/- 0.013 | 0.304 +/- 0.046 | 0.995 +/- 0.002 | 0.068 +/- 0.013 |
| Reconnaissance | 9991 | 0.16 | iforest+entropy:max | 0.784 +/- 0.019 | 0.396 +/- 0.052 | 0.994 +/- 0.001 | 0.059 +/- 0.025 |
| Worms | 171 | 0.05 | msp | 0.676 +/- 0.020 | 0.074 +/- 0.027 | 1.000 +/- 0.000 | 0.057 +/- 0.020 |
| Worms | 171 | 0.05 | iforest+entropy:max | 0.650 +/- 0.021 | 0.094 +/- 0.032 | 0.999 +/- 0.003 | 0.043 +/- 0.016 |
| Shellcode | 1456 | 0.01 | msp | 0.855 +/- 0.005 | 0.376 +/- 0.050 | 0.989 +/- 0.003 | 0.048 +/- 0.018 |
| Shellcode | 1456 | 0.01 | iforest+entropy:max | 0.832 +/- 0.029 | 0.226 +/- 0.051 | 0.983 +/- 0.004 | 0.032 +/- 0.013 |
| Overlap-Group-1 (all three) | 9412 | 0.53 | msp | 0.811 +/- 0.004 | 0.423 +/- 0.084 | 0.964 +/- 0.008 | 0.039 +/- 0.022 |
| Overlap-Group-1 (all three) | 9412 | 0.53 | iforest+entropy:max | 0.782 +/- 0.008 | 0.285 +/- 0.092 | 0.964 +/- 0.008 | 0.040 +/- 0.026 |
| **mean over the nine classes** | | | iforest+entropy:max | 0.769 | 0.217 | 0.880 | 0.043 |
| **worst class by AUROC (Fuzzers)** | | | iforest+entropy:max | 0.647 | 0.092 | 0.246 | 0.051 |
| **mean over the nine classes** | | | msp | 0.774 | 0.232 | 0.882 | 0.054 |
| **worst class by AUROC (Exploits)** | | | msp | 0.674 | 0.102 | 0.969 | 0.065 |

## Source: open_set_step2_sources_40f_45f_48f.md

### Task 4 Step 2 (continued): known classes behind the false-Unknown alarms

#### 40f: where the false-Unknown alarms come from (Worms + Shellcode held out, threshold at 5%, mean over 5 seeds)

`flagged` = share of the class's known flows flagged Unknown; `of alarms` = the class's share of all false alarms. thr / cal = the two validation halves, test = official test.

**entropy**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.414 | 0.334 | 0.205 | 0.177 | 0.128 | 0.063 |
| Backdoor | 345 | 0.434 | 0.421 | 0.176 | 0.226 | 0.187 | 0.043 |
| DoS | 1694 | 0.160 | 0.117 | 0.121 | 0.133 | 0.117 | 0.151 |
| Exploits | 7590 | 0.035 | 0.027 | 0.035 | 0.140 | 0.159 | 0.194 |
| Fuzzers | 4810 | 0.047 | 0.050 | 0.046 | 0.153 | 0.189 | 0.162 |
| Generic | 3418 | 0.027 | 0.041 | 0.030 | 0.024 | 0.051 | 0.078 |
| Normal | 33832 | 0.005 | 0.004 | 0.009 | 0.036 | 0.042 | 0.224 |
| Reconnaissance | 2469 | 0.068 | 0.073 | 0.047 | 0.115 | 0.136 | 0.085 |

**msp**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.207 | 0.271 | 0.099 | 0.087 | 0.098 | 0.013 |
| Backdoor | 345 | 0.201 | 0.219 | 0.108 | 0.104 | 0.089 | 0.012 |
| DoS | 1694 | 0.177 | 0.132 | 0.127 | 0.135 | 0.113 | 0.067 |
| Exploits | 7590 | 0.063 | 0.052 | 0.057 | 0.245 | 0.247 | 0.136 |
| Fuzzers | 4810 | 0.060 | 0.057 | 0.066 | 0.194 | 0.198 | 0.098 |
| Generic | 3418 | 0.036 | 0.035 | 0.040 | 0.027 | 0.047 | 0.043 |
| Normal | 33832 | 0.024 | 0.021 | 0.057 | 0.167 | 0.161 | 0.599 |
| Reconnaissance | 2469 | 0.030 | 0.033 | 0.043 | 0.047 | 0.056 | 0.033 |

#### 45f: where the false-Unknown alarms come from (Worms + Shellcode held out, threshold at 5%, mean over 5 seeds)

`flagged` = share of the class's known flows flagged Unknown; `of alarms` = the class's share of all false alarms. thr / cal = the two validation halves, test = official test.

**entropy**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.454 | 0.417 | 0.270 | 0.184 | 0.148 | 0.068 |
| Backdoor | 345 | 0.448 | 0.531 | 0.285 | 0.219 | 0.204 | 0.060 |
| DoS | 1694 | 0.194 | 0.155 | 0.145 | 0.158 | 0.130 | 0.152 |
| Exploits | 7590 | 0.036 | 0.029 | 0.036 | 0.138 | 0.150 | 0.171 |
| Fuzzers | 4810 | 0.041 | 0.050 | 0.072 | 0.130 | 0.148 | 0.216 |
| Generic | 3418 | 0.047 | 0.085 | 0.028 | 0.039 | 0.070 | 0.062 |
| Normal | 33832 | 0.002 | 0.003 | 0.009 | 0.015 | 0.019 | 0.199 |
| Reconnaissance | 2469 | 0.076 | 0.089 | 0.047 | 0.124 | 0.145 | 0.071 |

**msp**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.313 | 0.335 | 0.196 | 0.135 | 0.116 | 0.031 |
| Backdoor | 345 | 0.319 | 0.380 | 0.220 | 0.156 | 0.141 | 0.028 |
| DoS | 1694 | 0.199 | 0.151 | 0.142 | 0.159 | 0.127 | 0.087 |
| Exploits | 7590 | 0.054 | 0.047 | 0.050 | 0.211 | 0.217 | 0.137 |
| Fuzzers | 4810 | 0.049 | 0.052 | 0.101 | 0.153 | 0.163 | 0.176 |
| Generic | 3418 | 0.030 | 0.055 | 0.033 | 0.025 | 0.042 | 0.041 |
| Normal | 33832 | 0.009 | 0.013 | 0.038 | 0.082 | 0.101 | 0.461 |
| Reconnaissance | 2469 | 0.055 | 0.071 | 0.044 | 0.084 | 0.102 | 0.038 |

#### 48f: where the false-Unknown alarms come from (Worms + Shellcode held out, threshold at 5%, mean over 5 seeds)

`flagged` = share of the class's known flows flagged Unknown; `of alarms` = the class's share of all false alarms. thr / cal = the two validation halves, test = official test.

**iforest+entropy:max**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.238 | 0.217 | 0.116 | 0.109 | 0.066 | 0.029 |
| Backdoor | 345 | 0.266 | 0.313 | 0.149 | 0.140 | 0.112 | 0.030 |
| DoS | 1694 | 0.157 | 0.117 | 0.117 | 0.132 | 0.115 | 0.115 |
| Exploits | 7590 | 0.049 | 0.047 | 0.043 | 0.194 | 0.263 | 0.183 |
| Fuzzers | 4810 | 0.037 | 0.048 | 0.048 | 0.126 | 0.141 | 0.128 |
| Generic | 3418 | 0.073 | 0.116 | 0.113 | 0.100 | 0.097 | 0.188 |
| Normal | 33832 | 0.017 | 0.012 | 0.016 | 0.143 | 0.147 | 0.289 |
| Reconnaissance | 2469 | 0.043 | 0.060 | 0.027 | 0.075 | 0.078 | 0.038 |

**msp**

| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |
|---|---|---|---|---|---|---|---|
| Analysis | 438 | 0.310 | 0.344 | 0.206 | 0.134 | 0.120 | 0.033 |
| Backdoor | 345 | 0.328 | 0.392 | 0.241 | 0.161 | 0.148 | 0.031 |
| DoS | 1694 | 0.206 | 0.159 | 0.142 | 0.166 | 0.130 | 0.088 |
| Exploits | 7590 | 0.053 | 0.044 | 0.046 | 0.205 | 0.202 | 0.127 |
| Fuzzers | 4810 | 0.049 | 0.047 | 0.102 | 0.150 | 0.155 | 0.182 |
| Generic | 3418 | 0.032 | 0.056 | 0.034 | 0.024 | 0.056 | 0.044 |
| Normal | 33832 | 0.009 | 0.013 | 0.038 | 0.081 | 0.099 | 0.457 |
| Reconnaissance | 2469 | 0.054 | 0.068 | 0.045 | 0.084 | 0.102 | 0.039 |

## Source: open_set_step3_40f_45f_48f.md

### Task 4 Step 3: alert-level FPR and the review queue (XGBoost, official split, mean +/- std over 5 seeds)

Alert FPR OFF = Normal flows predicted as any attack class. Alert FPR ON = Normal flows predicted as an attack class OR sent to review as Unknown (it can only be higher). Confident-alert FPR = Normal flows called an attack and NOT sent to review (the alerts that skip the queue). Review rate = Normal flows sent to Unknown (the cost). Zero-day catch = zero-day flows flagged Unknown or called an attack. The declared operating point is the 5% target, chosen on validation only.

#### 40f: entropy (best)

| false-Unknown target | alert FPR OFF | alert FPR ON | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown | known-attack alert rate | known attacks detected confidently |
|---|---|---|---|---|---|---|---|---|---|
| 0.5% | 0.289 +/- 0.012 | 0.290 +/- 0.012 | 0.288 +/- 0.012 | 0.001 +/- 0.001 | 0.997 +/- 0.001 | 0.936 +/- 0.014 | 0.048 +/- 0.009 | 0.963 +/- 0.003 | 0.954 +/- 0.005 |
| 1.0% | 0.289 +/- 0.012 | 0.290 +/- 0.012 | 0.288 +/- 0.012 | 0.002 +/- 0.000 | 0.995 +/- 0.001 | 0.937 +/- 0.013 | 0.064 +/- 0.014 | 0.963 +/- 0.003 | 0.950 +/- 0.006 |
| 2.0% | 0.289 +/- 0.012 | 0.290 +/- 0.012 | 0.286 +/- 0.012 | 0.004 +/- 0.001 | 0.989 +/- 0.003 | 0.938 +/- 0.013 | 0.099 +/- 0.023 | 0.963 +/- 0.003 | 0.939 +/- 0.008 |
| 3.0% | 0.289 +/- 0.012 | 0.290 +/- 0.012 | 0.285 +/- 0.012 | 0.005 +/- 0.002 | 0.985 +/- 0.004 | 0.938 +/- 0.013 | 0.118 +/- 0.029 | 0.964 +/- 0.003 | 0.932 +/- 0.009 |
| 5.0% | 0.289 +/- 0.012 | 0.291 +/- 0.013 | 0.282 +/- 0.011 | 0.009 +/- 0.004 | 0.976 +/- 0.009 | 0.940 +/- 0.012 | 0.158 +/- 0.047 | 0.964 +/- 0.003 | 0.913 +/- 0.020 |
| 7.5% | 0.289 +/- 0.012 | 0.294 +/- 0.015 | 0.276 +/- 0.010 | 0.018 +/- 0.011 | 0.955 +/- 0.026 | 0.943 +/- 0.013 | 0.234 +/- 0.104 | 0.966 +/- 0.004 | 0.881 +/- 0.042 |
| 10.0% | 0.289 +/- 0.012 | 0.302 +/- 0.024 | 0.264 +/- 0.017 | 0.039 +/- 0.035 | 0.913 +/- 0.069 | 0.949 +/- 0.015 | 0.347 +/- 0.191 | 0.968 +/- 0.005 | 0.848 +/- 0.057 |
| 15.0% | 0.289 +/- 0.012 | 0.320 +/- 0.032 | 0.236 +/- 0.032 | 0.084 +/- 0.060 | 0.817 +/- 0.114 | 0.964 +/- 0.020 | 0.542 +/- 0.214 | 0.972 +/- 0.006 | 0.789 +/- 0.067 |
| 20.0% | 0.289 +/- 0.012 | 0.344 +/- 0.032 | 0.198 +/- 0.040 | 0.146 +/- 0.069 | 0.683 +/- 0.137 | 0.982 +/- 0.015 | 0.717 +/- 0.158 | 0.978 +/- 0.008 | 0.727 +/- 0.067 |
| 30.0% | 0.289 +/- 0.012 | 0.385 +/- 0.029 | 0.121 +/- 0.057 | 0.264 +/- 0.085 | 0.419 +/- 0.193 | 0.996 +/- 0.005 | 0.856 +/- 0.078 | 0.990 +/- 0.009 | 0.625 +/- 0.077 |

#### 40f: msp

| false-Unknown target | alert FPR OFF | alert FPR ON | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown | known-attack alert rate | known attacks detected confidently |
|---|---|---|---|---|---|---|---|---|---|
| 0.5% | 0.289 +/- 0.012 | 0.291 +/- 0.012 | 0.285 +/- 0.012 | 0.006 +/- 0.003 | 0.985 +/- 0.007 | 0.939 +/- 0.013 | 0.042 +/- 0.014 | 0.964 +/- 0.003 | 0.954 +/- 0.005 |
| 1.0% | 0.289 +/- 0.012 | 0.294 +/- 0.013 | 0.280 +/- 0.012 | 0.014 +/- 0.007 | 0.967 +/- 0.015 | 0.941 +/- 0.012 | 0.071 +/- 0.022 | 0.965 +/- 0.003 | 0.947 +/- 0.006 |
| 2.0% | 0.289 +/- 0.012 | 0.299 +/- 0.014 | 0.272 +/- 0.011 | 0.027 +/- 0.010 | 0.939 +/- 0.019 | 0.944 +/- 0.010 | 0.119 +/- 0.035 | 0.966 +/- 0.004 | 0.936 +/- 0.010 |
| 3.0% | 0.289 +/- 0.012 | 0.303 +/- 0.015 | 0.265 +/- 0.012 | 0.039 +/- 0.013 | 0.915 +/- 0.024 | 0.947 +/- 0.010 | 0.160 +/- 0.043 | 0.968 +/- 0.004 | 0.926 +/- 0.012 |
| 5.0% | 0.289 +/- 0.012 | 0.311 +/- 0.014 | 0.254 +/- 0.012 | 0.057 +/- 0.013 | 0.878 +/- 0.023 | 0.955 +/- 0.009 | 0.223 +/- 0.037 | 0.970 +/- 0.003 | 0.908 +/- 0.013 |
| 7.5% | 0.289 +/- 0.012 | 0.322 +/- 0.014 | 0.240 +/- 0.013 | 0.082 +/- 0.016 | 0.830 +/- 0.027 | 0.961 +/- 0.009 | 0.274 +/- 0.039 | 0.973 +/- 0.003 | 0.886 +/- 0.020 |
| 10.0% | 0.289 +/- 0.012 | 0.330 +/- 0.015 | 0.230 +/- 0.013 | 0.100 +/- 0.018 | 0.795 +/- 0.033 | 0.965 +/- 0.010 | 0.310 +/- 0.046 | 0.975 +/- 0.004 | 0.864 +/- 0.028 |
| 15.0% | 0.289 +/- 0.012 | 0.347 +/- 0.021 | 0.206 +/- 0.018 | 0.141 +/- 0.033 | 0.713 +/- 0.062 | 0.974 +/- 0.010 | 0.408 +/- 0.091 | 0.980 +/- 0.005 | 0.809 +/- 0.054 |
| 20.0% | 0.289 +/- 0.012 | 0.362 +/- 0.024 | 0.181 +/- 0.030 | 0.181 +/- 0.050 | 0.626 +/- 0.104 | 0.983 +/- 0.008 | 0.507 +/- 0.129 | 0.985 +/- 0.006 | 0.757 +/- 0.065 |
| 30.0% | 0.289 +/- 0.012 | 0.393 +/- 0.020 | 0.116 +/- 0.054 | 0.276 +/- 0.072 | 0.402 +/- 0.182 | 0.995 +/- 0.003 | 0.731 +/- 0.141 | 0.992 +/- 0.005 | 0.647 +/- 0.088 |

#### 45f: entropy (best)

| false-Unknown target | alert FPR OFF | alert FPR ON | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown | known-attack alert rate | known attacks detected confidently |
|---|---|---|---|---|---|---|---|---|---|
| 0.5% | 0.299 +/- 0.012 | 0.299 +/- 0.012 | 0.298 +/- 0.012 | 0.001 +/- 0.000 | 0.997 +/- 0.001 | 0.980 +/- 0.007 | 0.064 +/- 0.017 | 0.961 +/- 0.006 | 0.952 +/- 0.007 |
| 1.0% | 0.299 +/- 0.012 | 0.299 +/- 0.012 | 0.297 +/- 0.012 | 0.002 +/- 0.001 | 0.995 +/- 0.002 | 0.981 +/- 0.007 | 0.097 +/- 0.030 | 0.961 +/- 0.006 | 0.946 +/- 0.010 |
| 2.0% | 0.299 +/- 0.012 | 0.299 +/- 0.012 | 0.296 +/- 0.012 | 0.003 +/- 0.001 | 0.990 +/- 0.004 | 0.983 +/- 0.006 | 0.155 +/- 0.040 | 0.961 +/- 0.006 | 0.934 +/- 0.014 |
| 3.0% | 0.299 +/- 0.012 | 0.299 +/- 0.012 | 0.294 +/- 0.012 | 0.005 +/- 0.002 | 0.986 +/- 0.005 | 0.984 +/- 0.006 | 0.200 +/- 0.049 | 0.962 +/- 0.006 | 0.924 +/- 0.016 |
| 5.0% | 0.299 +/- 0.012 | 0.301 +/- 0.012 | 0.291 +/- 0.012 | 0.009 +/- 0.004 | 0.975 +/- 0.010 | 0.985 +/- 0.006 | 0.296 +/- 0.059 | 0.963 +/- 0.006 | 0.901 +/- 0.028 |
| 7.5% | 0.299 +/- 0.012 | 0.305 +/- 0.017 | 0.284 +/- 0.012 | 0.022 +/- 0.017 | 0.950 +/- 0.033 | 0.989 +/- 0.004 | 0.424 +/- 0.110 | 0.965 +/- 0.007 | 0.869 +/- 0.051 |
| 10.0% | 0.299 +/- 0.012 | 0.312 +/- 0.020 | 0.274 +/- 0.017 | 0.038 +/- 0.030 | 0.919 +/- 0.058 | 0.991 +/- 0.003 | 0.520 +/- 0.134 | 0.968 +/- 0.008 | 0.839 +/- 0.062 |
| 15.0% | 0.299 +/- 0.012 | 0.329 +/- 0.025 | 0.250 +/- 0.029 | 0.080 +/- 0.049 | 0.837 +/- 0.093 | 0.995 +/- 0.003 | 0.659 +/- 0.122 | 0.973 +/- 0.009 | 0.765 +/- 0.074 |
| 20.0% | 0.299 +/- 0.012 | 0.352 +/- 0.029 | 0.213 +/- 0.039 | 0.138 +/- 0.064 | 0.715 +/- 0.129 | 0.997 +/- 0.002 | 0.753 +/- 0.082 | 0.981 +/- 0.011 | 0.702 +/- 0.074 |
| 30.0% | 0.299 +/- 0.012 | 0.390 +/- 0.027 | 0.137 +/- 0.058 | 0.252 +/- 0.083 | 0.459 +/- 0.190 | 0.999 +/- 0.001 | 0.845 +/- 0.050 | 0.990 +/- 0.009 | 0.603 +/- 0.083 |

#### 45f: msp

| false-Unknown target | alert FPR OFF | alert FPR ON | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown | known-attack alert rate | known attacks detected confidently |
|---|---|---|---|---|---|---|---|---|---|
| 0.5% | 0.299 +/- 0.012 | 0.300 +/- 0.012 | 0.295 +/- 0.012 | 0.005 +/- 0.002 | 0.989 +/- 0.005 | 0.982 +/- 0.006 | 0.082 +/- 0.028 | 0.962 +/- 0.006 | 0.947 +/- 0.010 |
| 1.0% | 0.299 +/- 0.012 | 0.301 +/- 0.012 | 0.293 +/- 0.012 | 0.009 +/- 0.005 | 0.980 +/- 0.010 | 0.984 +/- 0.006 | 0.146 +/- 0.053 | 0.962 +/- 0.006 | 0.939 +/- 0.013 |
| 2.0% | 0.299 +/- 0.012 | 0.304 +/- 0.013 | 0.288 +/- 0.013 | 0.016 +/- 0.007 | 0.966 +/- 0.014 | 0.986 +/- 0.004 | 0.226 +/- 0.061 | 0.964 +/- 0.006 | 0.927 +/- 0.016 |
| 3.0% | 0.299 +/- 0.012 | 0.307 +/- 0.012 | 0.285 +/- 0.014 | 0.022 +/- 0.009 | 0.953 +/- 0.017 | 0.987 +/- 0.004 | 0.273 +/- 0.046 | 0.965 +/- 0.006 | 0.917 +/- 0.016 |
| 5.0% | 0.299 +/- 0.012 | 0.314 +/- 0.012 | 0.276 +/- 0.016 | 0.038 +/- 0.015 | 0.923 +/- 0.027 | 0.989 +/- 0.004 | 0.343 +/- 0.036 | 0.967 +/- 0.007 | 0.896 +/- 0.021 |
| 7.5% | 0.299 +/- 0.012 | 0.322 +/- 0.014 | 0.266 +/- 0.017 | 0.057 +/- 0.020 | 0.890 +/- 0.036 | 0.990 +/- 0.004 | 0.389 +/- 0.039 | 0.970 +/- 0.007 | 0.875 +/- 0.031 |
| 10.0% | 0.299 +/- 0.012 | 0.331 +/- 0.015 | 0.255 +/- 0.018 | 0.076 +/- 0.023 | 0.854 +/- 0.042 | 0.992 +/- 0.003 | 0.432 +/- 0.044 | 0.973 +/- 0.007 | 0.852 +/- 0.042 |
| 15.0% | 0.299 +/- 0.012 | 0.350 +/- 0.019 | 0.230 +/- 0.024 | 0.120 +/- 0.038 | 0.770 +/- 0.074 | 0.995 +/- 0.003 | 0.521 +/- 0.062 | 0.978 +/- 0.008 | 0.801 +/- 0.062 |
| 20.0% | 0.299 +/- 0.012 | 0.366 +/- 0.022 | 0.202 +/- 0.035 | 0.164 +/- 0.054 | 0.678 +/- 0.115 | 0.997 +/- 0.002 | 0.602 +/- 0.087 | 0.983 +/- 0.008 | 0.751 +/- 0.076 |
| 30.0% | 0.299 +/- 0.012 | 0.396 +/- 0.018 | 0.133 +/- 0.054 | 0.263 +/- 0.071 | 0.446 +/- 0.177 | 0.999 +/- 0.001 | 0.759 +/- 0.109 | 0.991 +/- 0.008 | 0.633 +/- 0.102 |

#### 48f: iforest+entropy:max (best)

| false-Unknown target | alert FPR OFF | alert FPR ON | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown | known-attack alert rate | known attacks detected confidently |
|---|---|---|---|---|---|---|---|---|---|
| 0.5% | 0.298 +/- 0.012 | 0.298 +/- 0.013 | 0.297 +/- 0.012 | 0.001 +/- 0.001 | 0.998 +/- 0.001 | 0.982 +/- 0.005 | 0.040 +/- 0.003 | 0.968 +/- 0.008 | 0.961 +/- 0.008 |
| 1.0% | 0.298 +/- 0.012 | 0.299 +/- 0.013 | 0.297 +/- 0.012 | 0.002 +/- 0.002 | 0.997 +/- 0.001 | 0.983 +/- 0.005 | 0.061 +/- 0.014 | 0.968 +/- 0.008 | 0.955 +/- 0.008 |
| 2.0% | 0.298 +/- 0.012 | 0.302 +/- 0.013 | 0.296 +/- 0.012 | 0.006 +/- 0.003 | 0.994 +/- 0.002 | 0.984 +/- 0.004 | 0.093 +/- 0.034 | 0.968 +/- 0.007 | 0.945 +/- 0.009 |
| 3.0% | 0.298 +/- 0.012 | 0.304 +/- 0.014 | 0.295 +/- 0.012 | 0.009 +/- 0.004 | 0.990 +/- 0.003 | 0.985 +/- 0.004 | 0.129 +/- 0.045 | 0.969 +/- 0.007 | 0.931 +/- 0.011 |
| 5.0% | 0.298 +/- 0.012 | 0.308 +/- 0.014 | 0.292 +/- 0.011 | 0.016 +/- 0.006 | 0.981 +/- 0.009 | 0.985 +/- 0.003 | 0.187 +/- 0.050 | 0.969 +/- 0.007 | 0.906 +/- 0.025 |
| 7.5% | 0.298 +/- 0.012 | 0.311 +/- 0.014 | 0.287 +/- 0.011 | 0.024 +/- 0.007 | 0.965 +/- 0.012 | 0.987 +/- 0.004 | 0.269 +/- 0.090 | 0.970 +/- 0.007 | 0.873 +/- 0.038 |
| 10.0% | 0.298 +/- 0.012 | 0.316 +/- 0.015 | 0.281 +/- 0.011 | 0.035 +/- 0.011 | 0.943 +/- 0.020 | 0.988 +/- 0.004 | 0.338 +/- 0.121 | 0.971 +/- 0.007 | 0.838 +/- 0.051 |
| 15.0% | 0.298 +/- 0.012 | 0.332 +/- 0.021 | 0.263 +/- 0.021 | 0.069 +/- 0.034 | 0.882 +/- 0.058 | 0.991 +/- 0.003 | 0.479 +/- 0.188 | 0.974 +/- 0.006 | 0.770 +/- 0.077 |
| 20.0% | 0.298 +/- 0.012 | 0.347 +/- 0.026 | 0.245 +/- 0.031 | 0.103 +/- 0.050 | 0.821 +/- 0.092 | 0.994 +/- 0.003 | 0.569 +/- 0.190 | 0.978 +/- 0.006 | 0.704 +/- 0.095 |
| 30.0% | 0.298 +/- 0.012 | 0.393 +/- 0.038 | 0.193 +/- 0.055 | 0.200 +/- 0.088 | 0.645 +/- 0.175 | 0.997 +/- 0.001 | 0.720 +/- 0.128 | 0.985 +/- 0.008 | 0.578 +/- 0.107 |

#### 48f: msp

| false-Unknown target | alert FPR OFF | alert FPR ON | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown | known-attack alert rate | known attacks detected confidently |
|---|---|---|---|---|---|---|---|---|---|
| 0.5% | 0.298 +/- 0.012 | 0.299 +/- 0.013 | 0.295 +/- 0.012 | 0.004 +/- 0.003 | 0.992 +/- 0.005 | 0.984 +/- 0.004 | 0.077 +/- 0.027 | 0.969 +/- 0.008 | 0.955 +/- 0.009 |
| 1.0% | 0.298 +/- 0.012 | 0.301 +/- 0.013 | 0.293 +/- 0.012 | 0.008 +/- 0.005 | 0.982 +/- 0.011 | 0.986 +/- 0.003 | 0.146 +/- 0.058 | 0.969 +/- 0.008 | 0.945 +/- 0.014 |
| 2.0% | 0.298 +/- 0.012 | 0.304 +/- 0.013 | 0.288 +/- 0.013 | 0.015 +/- 0.008 | 0.967 +/- 0.016 | 0.987 +/- 0.003 | 0.221 +/- 0.062 | 0.971 +/- 0.007 | 0.932 +/- 0.018 |
| 3.0% | 0.298 +/- 0.012 | 0.306 +/- 0.013 | 0.284 +/- 0.013 | 0.022 +/- 0.009 | 0.955 +/- 0.017 | 0.988 +/- 0.003 | 0.270 +/- 0.051 | 0.972 +/- 0.007 | 0.922 +/- 0.018 |
| 5.0% | 0.298 +/- 0.012 | 0.313 +/- 0.014 | 0.276 +/- 0.014 | 0.038 +/- 0.014 | 0.925 +/- 0.026 | 0.990 +/- 0.003 | 0.333 +/- 0.044 | 0.974 +/- 0.007 | 0.903 +/- 0.022 |
| 7.5% | 0.298 +/- 0.012 | 0.322 +/- 0.015 | 0.265 +/- 0.016 | 0.057 +/- 0.019 | 0.889 +/- 0.035 | 0.992 +/- 0.002 | 0.387 +/- 0.044 | 0.977 +/- 0.007 | 0.882 +/- 0.030 |
| 10.0% | 0.298 +/- 0.012 | 0.331 +/- 0.016 | 0.254 +/- 0.018 | 0.077 +/- 0.023 | 0.852 +/- 0.044 | 0.993 +/- 0.002 | 0.428 +/- 0.056 | 0.979 +/- 0.007 | 0.860 +/- 0.041 |
| 15.0% | 0.298 +/- 0.012 | 0.349 +/- 0.020 | 0.229 +/- 0.024 | 0.120 +/- 0.039 | 0.770 +/- 0.076 | 0.995 +/- 0.002 | 0.520 +/- 0.079 | 0.984 +/- 0.007 | 0.813 +/- 0.059 |
| 20.0% | 0.298 +/- 0.012 | 0.366 +/- 0.022 | 0.200 +/- 0.037 | 0.167 +/- 0.056 | 0.671 +/- 0.121 | 0.997 +/- 0.001 | 0.608 +/- 0.102 | 0.988 +/- 0.007 | 0.759 +/- 0.074 |
| 30.0% | 0.298 +/- 0.012 | 0.395 +/- 0.018 | 0.132 +/- 0.056 | 0.263 +/- 0.073 | 0.442 +/- 0.183 | 0.999 +/- 0.001 | 0.765 +/- 0.112 | 0.994 +/- 0.006 | 0.644 +/- 0.100 |

## Source: open_set_step4_40f_48f_41f_38f_48f_t30_48f_t15.md

### Task 4 Step 4: does ct_* carry the open-set gain? (XGBoost, official split, threshold at 5% false-Unknown, mean +/- std over 5 seeds)

msp detection: 40f 0.223, 48f 0.333 (gap 0.110); without the 7 window-count ct_* columns 0.172 (drop 0.161). Declared reading: **confirmed**.

| variant | score | unknown AUROC | detection @5% | false-Unknown test |
|---|---|---|---|---|
| 40f | msp | 0.798 +/- 0.004 | 0.223 +/- 0.037 | 0.059 +/- 0.014 |
| 40f | entropy | 0.862 +/- 0.005 | 0.158 +/- 0.047 | 0.025 +/- 0.010 |
| 48f | msp | 0.834 +/- 0.007 | 0.333 +/- 0.044 | 0.050 +/- 0.017 |
| 48f | iforest+entropy:max | 0.810 +/- 0.031 | 0.187 +/- 0.050 | 0.034 +/- 0.013 |
| 41f | msp | 0.764 +/- 0.006 | 0.172 +/- 0.038 | 0.061 +/- 0.012 |
| 41f | margin | 0.743 +/- 0.006 | 0.136 +/- 0.043 | 0.075 +/- 0.018 |
| 38f | msp | 0.762 +/- 0.007 | 0.171 +/- 0.031 | 0.062 +/- 0.014 |
| 38f | margin | 0.740 +/- 0.006 | 0.126 +/- 0.040 | 0.073 +/- 0.017 |
| 48f_t30 | msp | 0.825 +/- 0.005 | 0.340 +/- 0.024 | 0.057 +/- 0.012 |
| 48f_t30 | entropy | 0.870 +/- 0.003 | 0.224 +/- 0.042 | 0.024 +/- 0.008 |
| 48f_t15 | msp | 0.763 +/- 0.010 | 0.193 +/- 0.045 | 0.065 +/- 0.015 |
| 48f_t15 | margin | 0.740 +/- 0.011 | 0.132 +/- 0.051 | 0.075 +/- 0.016 |

## Source: open_set_boost_calibration_40f_48f.md

### Task 4.5: calibration

#### calibration (40f, mean over seeds 42-46)

Baseline for the verdict: `msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| msp | 0.769 | 0.213 | +0.000 | 0 of 5 | Worms (0.634) | 0.798 +/- 0.004 | 0.224 +/- 0.038 | 0.224 +/- 0.038 | no |
| entropy | 0.810 | 0.266 | +0.053 | 5 of 5 | Worms (0.674) | 0.862 +/- 0.005 | 0.159 +/- 0.047 | 0.307 +/- 0.034 | no |
| msp_cal | 0.780 | 0.230 | +0.018 | 5 of 5 | Worms (0.641) | 0.811 +/- 0.012 | 0.232 +/- 0.045 | 0.241 +/- 0.042 | no |
| entropy_cal | 0.819 | 0.276 | +0.063 | 5 of 5 | Worms (0.693) | 0.874 +/- 0.011 | 0.165 +/- 0.047 | 0.348 +/- 0.035 | no |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | msp | 0.798 +/- 0.004 | 0.224 +/- 0.038 | 0.050 / 0.044 / 0.059 | 0.955 +/- 0.009 | 0.224 +/- 0.038 |
| Worms + Shellcode | entropy | 0.862 +/- 0.005 | 0.159 +/- 0.047 | 0.048 / 0.041 / 0.025 | 0.941 +/- 0.012 | 0.307 +/- 0.034 |
| Worms + Shellcode | msp_cal | 0.811 +/- 0.012 | 0.232 +/- 0.045 | 0.050 / 0.046 / 0.057 | 0.953 +/- 0.010 | 0.241 +/- 0.042 |
| Worms + Shellcode | entropy_cal | 0.874 +/- 0.011 | 0.165 +/- 0.047 | 0.049 / 0.041 / 0.024 | 0.940 +/- 0.011 | 0.348 +/- 0.035 |
| Analysis | msp | 0.885 +/- 0.009 | 0.253 +/- 0.114 | 0.050 / 0.044 / 0.047 | 0.849 +/- 0.006 | 0.253 +/- 0.114 |
| Analysis | entropy | 0.923 +/- 0.003 | 0.362 +/- 0.136 | 0.048 / 0.043 / 0.031 | 0.842 +/- 0.007 | 0.533 +/- 0.112 |
| Analysis | msp_cal | 0.897 +/- 0.006 | 0.259 +/- 0.114 | 0.050 / 0.043 / 0.044 | 0.848 +/- 0.007 | 0.304 +/- 0.115 |
| Analysis | entropy_cal | 0.924 +/- 0.003 | 0.350 +/- 0.133 | 0.049 / 0.042 / 0.032 | 0.842 +/- 0.007 | 0.515 +/- 0.120 |
| Backdoor | msp | 0.882 +/- 0.009 | 0.274 +/- 0.104 | 0.050 / 0.045 / 0.055 | 0.994 +/- 0.004 | 0.274 +/- 0.104 |
| Backdoor | entropy | 0.926 +/- 0.004 | 0.421 +/- 0.144 | 0.050 / 0.042 / 0.034 | 0.993 +/- 0.003 | 0.632 +/- 0.147 |
| Backdoor | msp_cal | 0.894 +/- 0.008 | 0.288 +/- 0.094 | 0.050 / 0.044 / 0.051 | 0.994 +/- 0.004 | 0.326 +/- 0.113 |
| Backdoor | entropy_cal | 0.928 +/- 0.004 | 0.406 +/- 0.144 | 0.050 / 0.040 / 0.034 | 0.993 +/- 0.003 | 0.613 +/- 0.163 |
| DoS | msp | 0.697 +/- 0.006 | 0.162 +/- 0.041 | 0.050 / 0.058 / 0.072 | 0.984 +/- 0.004 | 0.162 +/- 0.041 |
| DoS | entropy | 0.736 +/- 0.007 | 0.203 +/- 0.069 | 0.050 / 0.050 / 0.036 | 0.976 +/- 0.005 | 0.324 +/- 0.046 |
| DoS | msp_cal | 0.711 +/- 0.005 | 0.184 +/- 0.065 | 0.050 / 0.057 / 0.062 | 0.983 +/- 0.005 | 0.209 +/- 0.075 |
| DoS | entropy_cal | 0.746 +/- 0.006 | 0.208 +/- 0.071 | 0.050 / 0.050 / 0.033 | 0.976 +/- 0.005 | 0.338 +/- 0.038 |
| Exploits | msp | 0.681 +/- 0.010 | 0.123 +/- 0.035 | 0.050 / 0.056 / 0.073 | 0.961 +/- 0.007 | 0.123 +/- 0.035 |
| Exploits | entropy | 0.710 +/- 0.007 | 0.119 +/- 0.020 | 0.050 / 0.050 / 0.041 | 0.957 +/- 0.007 | 0.191 +/- 0.079 |
| Exploits | msp_cal | 0.691 +/- 0.014 | 0.136 +/- 0.031 | 0.050 / 0.056 / 0.065 | 0.962 +/- 0.007 | 0.144 +/- 0.032 |
| Exploits | entropy_cal | 0.728 +/- 0.015 | 0.121 +/- 0.021 | 0.050 / 0.048 / 0.041 | 0.955 +/- 0.007 | 0.196 +/- 0.080 |
| Fuzzers | msp | 0.693 +/- 0.007 | 0.092 +/- 0.019 | 0.050 / 0.051 / 0.065 | 0.262 +/- 0.016 | 0.092 +/- 0.019 |
| Fuzzers | entropy | 0.699 +/- 0.007 | 0.103 +/- 0.023 | 0.049 / 0.057 / 0.055 | 0.259 +/- 0.018 | 0.121 +/- 0.023 |
| Fuzzers | msp_cal | 0.693 +/- 0.007 | 0.097 +/- 0.019 | 0.050 / 0.052 / 0.066 | 0.263 +/- 0.017 | 0.095 +/- 0.019 |
| Fuzzers | entropy_cal | 0.700 +/- 0.008 | 0.105 +/- 0.024 | 0.050 / 0.057 / 0.053 | 0.259 +/- 0.018 | 0.127 +/- 0.023 |
| Generic | msp | 0.828 +/- 0.067 | 0.402 +/- 0.229 | 0.050 / 0.058 / 0.081 | 0.999 +/- 0.000 | 0.402 +/- 0.229 |
| Generic | entropy | 0.896 +/- 0.036 | 0.607 +/- 0.216 | 0.050 / 0.054 / 0.058 | 0.998 +/- 0.001 | 0.657 +/- 0.210 |
| Generic | msp_cal | 0.853 +/- 0.053 | 0.487 +/- 0.221 | 0.050 / 0.058 / 0.076 | 0.999 +/- 0.000 | 0.512 +/- 0.230 |
| Generic | entropy_cal | 0.912 +/- 0.019 | 0.701 +/- 0.129 | 0.050 / 0.051 / 0.058 | 0.998 +/- 0.000 | 0.749 +/- 0.121 |
| Reconnaissance | msp | 0.799 +/- 0.010 | 0.319 +/- 0.100 | 0.050 / 0.039 / 0.069 | 0.857 +/- 0.068 | 0.319 +/- 0.100 |
| Reconnaissance | entropy | 0.839 +/- 0.009 | 0.373 +/- 0.161 | 0.050 / 0.048 / 0.062 | 0.896 +/- 0.061 | 0.416 +/- 0.131 |
| Reconnaissance | msp_cal | 0.806 +/- 0.012 | 0.332 +/- 0.103 | 0.050 / 0.040 / 0.069 | 0.864 +/- 0.066 | 0.333 +/- 0.103 |
| Reconnaissance | entropy_cal | 0.843 +/- 0.010 | 0.380 +/- 0.157 | 0.050 / 0.047 / 0.061 | 0.900 +/- 0.057 | 0.433 +/- 0.131 |
| Worms | msp | 0.634 +/- 0.015 | 0.046 +/- 0.028 | 0.050 / 0.042 / 0.064 | 0.994 +/- 0.000 | 0.046 +/- 0.028 |
| Worms | entropy | 0.674 +/- 0.013 | 0.036 +/- 0.026 | 0.049 / 0.049 / 0.039 | 0.994 +/- 0.000 | 0.048 +/- 0.029 |
| Worms | msp_cal | 0.641 +/- 0.018 | 0.046 +/- 0.027 | 0.050 / 0.045 / 0.062 | 0.994 +/- 0.000 | 0.046 +/- 0.027 |
| Worms | entropy_cal | 0.693 +/- 0.023 | 0.036 +/- 0.024 | 0.050 / 0.049 / 0.039 | 0.994 +/- 0.000 | 0.051 +/- 0.028 |
| Shellcode | msp | 0.817 +/- 0.003 | 0.244 +/- 0.057 | 0.050 / 0.046 / 0.061 | 0.953 +/- 0.013 | 0.244 +/- 0.057 |
| Shellcode | entropy | 0.882 +/- 0.004 | 0.170 +/- 0.057 | 0.049 / 0.040 / 0.024 | 0.935 +/- 0.017 | 0.355 +/- 0.069 |
| Shellcode | msp_cal | 0.831 +/- 0.010 | 0.245 +/- 0.054 | 0.050 / 0.046 / 0.056 | 0.949 +/- 0.014 | 0.262 +/- 0.054 |
| Shellcode | entropy_cal | 0.894 +/- 0.008 | 0.173 +/- 0.046 | 0.050 / 0.039 / 0.023 | 0.934 +/- 0.016 | 0.399 +/- 0.059 |
| Overlap-Group-1 (all three) | msp | 0.804 +/- 0.005 | 0.372 +/- 0.111 | 0.050 / 0.048 / 0.040 | 0.953 +/- 0.010 | 0.372 +/- 0.111 |
| Overlap-Group-1 (all three) | entropy | 0.816 +/- 0.003 | 0.370 +/- 0.130 | 0.050 / 0.050 / 0.040 | 0.954 +/- 0.012 | 0.372 +/- 0.128 |
| Overlap-Group-1 (all three) | msp_cal | 0.807 +/- 0.005 | 0.373 +/- 0.114 | 0.050 / 0.048 / 0.040 | 0.953 +/- 0.011 | 0.373 +/- 0.112 |
| Overlap-Group-1 (all three) | entropy_cal | 0.818 +/- 0.004 | 0.353 +/- 0.136 | 0.050 / 0.050 / 0.040 | 0.954 +/- 0.012 | 0.352 +/- 0.134 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | Generic | Reconnaissance | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msp | 358 of 1456 | 7 of 171 | 437 of 7590 | 319 of 4810 | 137 of 3418 | 107 of 2469 | 218 of 1694 | 44 of 438 | 38 of 345 | 1937 of 33832 | 0.103 |
| entropy | 254 of 1456 | 4 of 171 | 262 of 7590 | 223 of 4810 | 103 of 3418 | 115 of 2469 | 205 of 1694 | 89 of 438 | 60 of 345 | 307 of 33832 | 0.163 |
| msp_cal | 372 of 1456 | 6 of 171 | 427 of 7590 | 310 of 4810 | 139 of 3418 | 109 of 2469 | 224 of 1694 | 52 of 438 | 42 of 345 | 1785 of 33832 | 0.111 |
| entropy_cal | 264 of 1456 | 4 of 171 | 250 of 7590 | 215 of 4810 | 103 of 3418 | 121 of 2469 | 208 of 1694 | 95 of 438 | 61 of 345 | 249 of 33832 | 0.179 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| msp | 0.289 +/- 0.012 | 0.311 +/- 0.014 | 0.254 +/- 0.012 | 0.057 +/- 0.013 | 0.879 +/- 0.023 | 0.955 +/- 0.009 | 0.224 +/- 0.038 |
| entropy | 0.289 +/- 0.012 | 0.291 +/- 0.012 | 0.282 +/- 0.011 | 0.009 +/- 0.004 | 0.976 +/- 0.009 | 0.941 +/- 0.012 | 0.159 +/- 0.047 |
| msp_cal | 0.289 +/- 0.012 | 0.309 +/- 0.015 | 0.256 +/- 0.012 | 0.053 +/- 0.014 | 0.886 +/- 0.024 | 0.953 +/- 0.010 | 0.232 +/- 0.045 |
| entropy_cal | 0.289 +/- 0.012 | 0.290 +/- 0.012 | 0.283 +/- 0.010 | 0.007 +/- 0.004 | 0.980 +/- 0.009 | 0.940 +/- 0.011 | 0.165 +/- 0.047 |

##### Diagnostics (mean over seeds, per held-out set)

| held-out set | temperature | ece_before | ece_after |
|---|---|---|---|
| Worms + Shellcode | 1.163 | 0.093 | 0.073 |
| Analysis | 1.196 | 0.086 | 0.062 |
| Backdoor | 1.178 | 0.094 | 0.072 |
| DoS | 1.256 | 0.098 | 0.073 |
| Exploits | 1.300 | 0.111 | 0.083 |
| Fuzzers | 1.132 | 0.017 | 0.013 |
| Generic | 1.259 | 0.098 | 0.068 |
| Reconnaissance | 1.140 | 0.092 | 0.077 |
| Worms | 1.167 | 0.094 | 0.074 |
| Shellcode | 1.159 | 0.092 | 0.073 |
| Overlap-Group-1 (all three) | 1.182 | 0.089 | 0.073 |

#### calibration (48f, mean over seeds 42-46)

Baseline for the verdict: `msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| msp | 0.774 | 0.234 | +0.000 | 0 of 5 | Exploits (0.675) | 0.833 +/- 0.006 | 0.334 +/- 0.037 | 0.334 +/- 0.037 | no |
| entropy | 0.811 | 0.283 | +0.049 | 5 of 5 | Exploits (0.702) | 0.881 +/- 0.007 | 0.294 +/- 0.072 | 0.447 +/- 0.081 | no |
| msp_cal | 0.787 | 0.260 | +0.026 | 5 of 5 | Worms (0.684) | 0.846 +/- 0.012 | 0.347 +/- 0.042 | 0.373 +/- 0.053 | no |
| entropy_cal | 0.826 | 0.304 | +0.070 | 5 of 5 | Fuzzers (0.706) | 0.894 +/- 0.012 | 0.317 +/- 0.082 | 0.477 +/- 0.081 | yes |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | msp | 0.833 +/- 0.006 | 0.334 +/- 0.037 | 0.050 / 0.044 / 0.050 | 0.991 +/- 0.003 | 0.334 +/- 0.037 |
| Worms + Shellcode | entropy | 0.881 +/- 0.007 | 0.294 +/- 0.072 | 0.050 / 0.048 / 0.029 | 0.987 +/- 0.004 | 0.447 +/- 0.081 |
| Worms + Shellcode | msp_cal | 0.846 +/- 0.012 | 0.347 +/- 0.042 | 0.050 / 0.045 / 0.044 | 0.990 +/- 0.003 | 0.373 +/- 0.053 |
| Worms + Shellcode | entropy_cal | 0.894 +/- 0.012 | 0.317 +/- 0.082 | 0.050 / 0.047 / 0.028 | 0.986 +/- 0.004 | 0.477 +/- 0.081 |
| Analysis | msp | 0.882 +/- 0.016 | 0.381 +/- 0.152 | 0.050 / 0.048 / 0.039 | 0.845 +/- 0.003 | 0.382 +/- 0.152 |
| Analysis | entropy | 0.910 +/- 0.009 | 0.444 +/- 0.147 | 0.050 / 0.052 / 0.030 | 0.841 +/- 0.005 | 0.529 +/- 0.183 |
| Analysis | msp_cal | 0.892 +/- 0.012 | 0.405 +/- 0.158 | 0.050 / 0.048 / 0.036 | 0.844 +/- 0.004 | 0.432 +/- 0.177 |
| Analysis | entropy_cal | 0.913 +/- 0.007 | 0.423 +/- 0.141 | 0.050 / 0.053 / 0.033 | 0.841 +/- 0.005 | 0.481 +/- 0.197 |
| Backdoor | msp | 0.901 +/- 0.012 | 0.419 +/- 0.180 | 0.050 / 0.045 / 0.043 | 0.998 +/- 0.001 | 0.419 +/- 0.180 |
| Backdoor | entropy | 0.933 +/- 0.006 | 0.510 +/- 0.188 | 0.050 / 0.049 / 0.034 | 0.998 +/- 0.001 | 0.590 +/- 0.192 |
| Backdoor | msp_cal | 0.912 +/- 0.008 | 0.457 +/- 0.202 | 0.050 / 0.046 / 0.041 | 0.998 +/- 0.001 | 0.479 +/- 0.194 |
| Backdoor | entropy_cal | 0.936 +/- 0.005 | 0.502 +/- 0.197 | 0.050 / 0.049 / 0.037 | 0.998 +/- 0.001 | 0.554 +/- 0.207 |
| DoS | msp | 0.713 +/- 0.007 | 0.168 +/- 0.042 | 0.050 / 0.049 / 0.049 | 0.994 +/- 0.002 | 0.168 +/- 0.042 |
| DoS | entropy | 0.743 +/- 0.008 | 0.212 +/- 0.073 | 0.050 / 0.048 / 0.029 | 0.992 +/- 0.003 | 0.291 +/- 0.052 |
| DoS | msp_cal | 0.728 +/- 0.006 | 0.197 +/- 0.067 | 0.050 / 0.050 / 0.040 | 0.994 +/- 0.002 | 0.223 +/- 0.069 |
| DoS | entropy_cal | 0.759 +/- 0.008 | 0.214 +/- 0.073 | 0.050 / 0.048 / 0.030 | 0.992 +/- 0.003 | 0.296 +/- 0.057 |
| Exploits | msp | 0.675 +/- 0.007 | 0.102 +/- 0.030 | 0.050 / 0.053 / 0.064 | 0.970 +/- 0.004 | 0.102 +/- 0.030 |
| Exploits | entropy | 0.702 +/- 0.003 | 0.123 +/- 0.033 | 0.050 / 0.052 / 0.036 | 0.968 +/- 0.005 | 0.197 +/- 0.057 |
| Exploits | msp_cal | 0.687 +/- 0.012 | 0.127 +/- 0.028 | 0.050 / 0.053 / 0.055 | 0.971 +/- 0.005 | 0.137 +/- 0.019 |
| Exploits | entropy_cal | 0.726 +/- 0.014 | 0.134 +/- 0.032 | 0.050 / 0.046 / 0.037 | 0.967 +/- 0.005 | 0.205 +/- 0.058 |
| Fuzzers | msp | 0.699 +/- 0.007 | 0.083 +/- 0.017 | 0.050 / 0.053 / 0.051 | 0.238 +/- 0.016 | 0.083 +/- 0.017 |
| Fuzzers | entropy | 0.704 +/- 0.006 | 0.110 +/- 0.029 | 0.050 / 0.062 / 0.049 | 0.240 +/- 0.019 | 0.113 +/- 0.025 |
| Fuzzers | msp_cal | 0.700 +/- 0.007 | 0.089 +/- 0.021 | 0.050 / 0.055 / 0.051 | 0.239 +/- 0.017 | 0.088 +/- 0.020 |
| Fuzzers | entropy_cal | 0.706 +/- 0.007 | 0.111 +/- 0.031 | 0.050 / 0.060 / 0.048 | 0.241 +/- 0.020 | 0.115 +/- 0.026 |
| Generic | msp | 0.776 +/- 0.059 | 0.191 +/- 0.100 | 0.050 / 0.050 / 0.063 | 0.892 +/- 0.103 | 0.191 +/- 0.100 |
| Generic | entropy | 0.852 +/- 0.049 | 0.258 +/- 0.131 | 0.050 / 0.048 / 0.038 | 0.890 +/- 0.101 | 0.383 +/- 0.164 |
| Generic | msp_cal | 0.806 +/- 0.056 | 0.239 +/- 0.123 | 0.050 / 0.050 / 0.052 | 0.900 +/- 0.098 | 0.276 +/- 0.140 |
| Generic | entropy_cal | 0.886 +/- 0.034 | 0.401 +/- 0.150 | 0.050 / 0.046 / 0.041 | 0.922 +/- 0.068 | 0.510 +/- 0.182 |
| Reconnaissance | msp | 0.792 +/- 0.013 | 0.303 +/- 0.047 | 0.050 / 0.039 / 0.068 | 0.995 +/- 0.002 | 0.303 +/- 0.047 |
| Reconnaissance | entropy | 0.843 +/- 0.011 | 0.482 +/- 0.067 | 0.050 / 0.052 / 0.061 | 0.995 +/- 0.001 | 0.510 +/- 0.045 |
| Reconnaissance | msp_cal | 0.806 +/- 0.013 | 0.357 +/- 0.039 | 0.050 / 0.039 / 0.067 | 0.995 +/- 0.002 | 0.362 +/- 0.039 |
| Reconnaissance | entropy_cal | 0.853 +/- 0.011 | 0.512 +/- 0.046 | 0.050 / 0.052 / 0.060 | 0.995 +/- 0.001 | 0.542 +/- 0.037 |
| Worms | msp | 0.676 +/- 0.021 | 0.082 +/- 0.024 | 0.050 / 0.049 / 0.056 | 1.000 +/- 0.000 | 0.082 +/- 0.024 |
| Worms | entropy | 0.715 +/- 0.023 | 0.068 +/- 0.017 | 0.050 / 0.054 / 0.038 | 0.999 +/- 0.003 | 0.099 +/- 0.033 |
| Worms | msp_cal | 0.684 +/- 0.025 | 0.081 +/- 0.025 | 0.050 / 0.051 / 0.052 | 1.000 +/- 0.000 | 0.084 +/- 0.025 |
| Worms | entropy_cal | 0.739 +/- 0.033 | 0.076 +/- 0.023 | 0.050 / 0.054 / 0.038 | 1.000 +/- 0.000 | 0.103 +/- 0.035 |
| Shellcode | msp | 0.855 +/- 0.005 | 0.378 +/- 0.058 | 0.050 / 0.045 / 0.048 | 0.989 +/- 0.002 | 0.378 +/- 0.058 |
| Shellcode | entropy | 0.901 +/- 0.007 | 0.340 +/- 0.080 | 0.050 / 0.044 / 0.028 | 0.985 +/- 0.004 | 0.490 +/- 0.077 |
| Shellcode | msp_cal | 0.867 +/- 0.011 | 0.392 +/- 0.058 | 0.050 / 0.045 / 0.043 | 0.989 +/- 0.003 | 0.416 +/- 0.059 |
| Shellcode | entropy_cal | 0.913 +/- 0.013 | 0.366 +/- 0.078 | 0.050 / 0.044 / 0.027 | 0.985 +/- 0.004 | 0.521 +/- 0.071 |
| Overlap-Group-1 (all three) | msp | 0.811 +/- 0.004 | 0.423 +/- 0.084 | 0.050 / 0.043 / 0.039 | 0.964 +/- 0.008 | 0.423 +/- 0.084 |
| Overlap-Group-1 (all three) | entropy | 0.821 +/- 0.002 | 0.400 +/- 0.125 | 0.050 / 0.048 / 0.041 | 0.965 +/- 0.010 | 0.416 +/- 0.109 |
| Overlap-Group-1 (all three) | msp_cal | 0.816 +/- 0.005 | 0.429 +/- 0.092 | 0.050 / 0.044 / 0.040 | 0.965 +/- 0.008 | 0.432 +/- 0.089 |
| Overlap-Group-1 (all three) | entropy_cal | 0.827 +/- 0.003 | 0.354 +/- 0.141 | 0.050 / 0.048 / 0.041 | 0.965 +/- 0.010 | 0.365 +/- 0.122 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | Generic | Reconnaissance | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msp | 534 of 1456 | 10 of 171 | 339 of 7590 | 489 of 4810 | 119 of 3418 | 107 of 2469 | 240 of 1694 | 85 of 438 | 79 of 345 | 1294 of 33832 | 0.175 |
| entropy | 472 of 1456 | 6 of 171 | 263 of 7590 | 368 of 4810 | 96 of 3418 | 119 of 2469 | 238 of 1694 | 120 of 438 | 101 of 345 | 270 of 33832 | 0.244 |
| msp_cal | 554 of 1456 | 9 of 171 | 319 of 7590 | 456 of 4810 | 117 of 3418 | 108 of 2469 | 235 of 1694 | 93 of 438 | 83 of 345 | 987 of 33832 | 0.201 |
| entropy_cal | 510 of 1456 | 6 of 171 | 263 of 7590 | 355 of 4810 | 100 of 3418 | 127 of 2469 | 242 of 1694 | 118 of 438 | 96 of 345 | 253 of 33832 | 0.264 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| msp | 0.298 +/- 0.013 | 0.314 +/- 0.013 | 0.275 +/- 0.016 | 0.038 +/- 0.016 | 0.924 +/- 0.030 | 0.991 +/- 0.003 | 0.334 +/- 0.037 |
| entropy | 0.298 +/- 0.013 | 0.300 +/- 0.013 | 0.292 +/- 0.012 | 0.008 +/- 0.004 | 0.979 +/- 0.009 | 0.987 +/- 0.004 | 0.294 +/- 0.072 |
| msp_cal | 0.298 +/- 0.013 | 0.309 +/- 0.014 | 0.280 +/- 0.014 | 0.029 +/- 0.012 | 0.940 +/- 0.023 | 0.990 +/- 0.003 | 0.347 +/- 0.042 |
| entropy_cal | 0.298 +/- 0.013 | 0.299 +/- 0.013 | 0.292 +/- 0.012 | 0.007 +/- 0.004 | 0.980 +/- 0.009 | 0.986 +/- 0.004 | 0.317 +/- 0.082 |

##### Diagnostics (mean over seeds, per held-out set)

| held-out set | temperature | ece_before | ece_after |
|---|---|---|---|
| Worms + Shellcode | 1.188 | 0.115 | 0.093 |
| Analysis | 1.223 | 0.113 | 0.086 |
| Backdoor | 1.214 | 0.117 | 0.092 |
| DoS | 1.355 | 0.129 | 0.093 |
| Exploits | 1.376 | 0.141 | 0.106 |
| Fuzzers | 1.159 | 0.021 | 0.013 |
| Generic | 1.327 | 0.125 | 0.087 |
| Reconnaissance | 1.219 | 0.120 | 0.095 |
| Worms | 1.204 | 0.120 | 0.095 |
| Shellcode | 1.183 | 0.114 | 0.093 |
| Overlap-Group-1 (all three) | 1.305 | 0.116 | 0.089 |

## Source: open_set_boost_perclass_40f_48f.md

### Task 4.5: perclass

#### perclass (40f, mean over seeds 42-46)

Baseline for the verdict: `msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| msp | 0.769 | 0.213 | +0.000 | 0 of 5 | Worms (0.634) | 0.798 +/- 0.004 | 0.224 +/- 0.038 | 0.224 +/- 0.038 | no |
| entropy | 0.810 | 0.266 | +0.053 | 5 of 5 | Worms (0.674) | 0.862 +/- 0.005 | 0.159 +/- 0.047 | 0.307 +/- 0.034 | no |
| msp_pc | 0.705 | 0.160 | -0.053 | 0 of 5 | Exploits (0.544) | 0.770 +/- 0.029 | 0.214 +/- 0.038 | 0.161 +/- 0.031 | no |
| entropy_pc | 0.742 | 0.216 | +0.003 | 4 of 5 | Exploits (0.512) | 0.830 +/- 0.029 | 0.339 +/- 0.030 | 0.268 +/- 0.045 | no |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | msp | 0.798 +/- 0.004 | 0.224 +/- 0.038 | 0.050 / 0.044 / 0.059 | 0.955 +/- 0.009 | 0.224 +/- 0.038 |
| Worms + Shellcode | entropy | 0.862 +/- 0.005 | 0.159 +/- 0.047 | 0.048 / 0.041 / 0.025 | 0.941 +/- 0.012 | 0.307 +/- 0.034 |
| Worms + Shellcode | msp_pc | 0.770 +/- 0.029 | 0.214 +/- 0.038 | 0.050 / 0.046 / 0.078 | 0.974 +/- 0.011 | 0.161 +/- 0.031 |
| Worms + Shellcode | entropy_pc | 0.830 +/- 0.029 | 0.339 +/- 0.030 | 0.050 / 0.046 / 0.078 | 0.986 +/- 0.015 | 0.268 +/- 0.045 |
| Analysis | msp | 0.885 +/- 0.009 | 0.253 +/- 0.114 | 0.050 / 0.044 / 0.047 | 0.849 +/- 0.006 | 0.253 +/- 0.114 |
| Analysis | entropy | 0.923 +/- 0.003 | 0.362 +/- 0.136 | 0.048 / 0.043 / 0.031 | 0.842 +/- 0.007 | 0.533 +/- 0.112 |
| Analysis | msp_pc | 0.816 +/- 0.029 | 0.093 +/- 0.020 | 0.050 / 0.045 / 0.078 | 0.878 +/- 0.016 | 0.047 +/- 0.011 |
| Analysis | entropy_pc | 0.856 +/- 0.020 | 0.148 +/- 0.036 | 0.050 / 0.047 / 0.085 | 0.916 +/- 0.035 | 0.070 +/- 0.009 |
| Backdoor | msp | 0.882 +/- 0.009 | 0.274 +/- 0.104 | 0.050 / 0.045 / 0.055 | 0.994 +/- 0.004 | 0.274 +/- 0.104 |
| Backdoor | entropy | 0.926 +/- 0.004 | 0.421 +/- 0.144 | 0.050 / 0.042 / 0.034 | 0.993 +/- 0.003 | 0.632 +/- 0.147 |
| Backdoor | msp_pc | 0.803 +/- 0.036 | 0.119 +/- 0.019 | 0.050 / 0.045 / 0.075 | 0.997 +/- 0.002 | 0.085 +/- 0.026 |
| Backdoor | entropy_pc | 0.851 +/- 0.032 | 0.145 +/- 0.024 | 0.050 / 0.046 / 0.078 | 0.999 +/- 0.002 | 0.084 +/- 0.026 |
| DoS | msp | 0.697 +/- 0.006 | 0.162 +/- 0.041 | 0.050 / 0.058 / 0.072 | 0.984 +/- 0.004 | 0.162 +/- 0.041 |
| DoS | entropy | 0.736 +/- 0.007 | 0.203 +/- 0.069 | 0.050 / 0.050 / 0.036 | 0.976 +/- 0.005 | 0.324 +/- 0.046 |
| DoS | msp_pc | 0.568 +/- 0.077 | 0.106 +/- 0.007 | 0.050 / 0.058 / 0.089 | 0.988 +/- 0.006 | 0.086 +/- 0.010 |
| DoS | entropy_pc | 0.614 +/- 0.071 | 0.134 +/- 0.009 | 0.050 / 0.059 / 0.087 | 0.991 +/- 0.007 | 0.115 +/- 0.023 |
| Exploits | msp | 0.681 +/- 0.010 | 0.123 +/- 0.035 | 0.050 / 0.056 / 0.073 | 0.961 +/- 0.007 | 0.123 +/- 0.035 |
| Exploits | entropy | 0.710 +/- 0.007 | 0.119 +/- 0.020 | 0.050 / 0.050 / 0.041 | 0.957 +/- 0.007 | 0.191 +/- 0.079 |
| Exploits | msp_pc | 0.544 +/- 0.129 | 0.150 +/- 0.025 | 0.051 / 0.055 / 0.083 | 0.968 +/- 0.014 | 0.127 +/- 0.033 |
| Exploits | entropy_pc | 0.512 +/- 0.111 | 0.151 +/- 0.020 | 0.050 / 0.054 / 0.081 | 0.975 +/- 0.012 | 0.133 +/- 0.040 |
| Fuzzers | msp | 0.693 +/- 0.007 | 0.092 +/- 0.019 | 0.050 / 0.051 / 0.065 | 0.262 +/- 0.016 | 0.092 +/- 0.019 |
| Fuzzers | entropy | 0.699 +/- 0.007 | 0.103 +/- 0.023 | 0.049 / 0.057 / 0.055 | 0.259 +/- 0.018 | 0.121 +/- 0.023 |
| Fuzzers | msp_pc | 0.721 +/- 0.020 | 0.185 +/- 0.089 | 0.051 / 0.044 / 0.086 | 0.372 +/- 0.085 | 0.134 +/- 0.048 |
| Fuzzers | entropy_pc | 0.731 +/- 0.033 | 0.192 +/- 0.082 | 0.051 / 0.050 / 0.082 | 0.372 +/- 0.080 | 0.149 +/- 0.049 |
| Generic | msp | 0.828 +/- 0.067 | 0.402 +/- 0.229 | 0.050 / 0.058 / 0.081 | 0.999 +/- 0.000 | 0.402 +/- 0.229 |
| Generic | entropy | 0.896 +/- 0.036 | 0.607 +/- 0.216 | 0.050 / 0.054 / 0.058 | 0.998 +/- 0.001 | 0.657 +/- 0.210 |
| Generic | msp_pc | 0.751 +/- 0.106 | 0.242 +/- 0.163 | 0.050 / 0.053 / 0.086 | 0.996 +/- 0.007 | 0.254 +/- 0.176 |
| Generic | entropy_pc | 0.836 +/- 0.060 | 0.458 +/- 0.233 | 0.050 / 0.054 / 0.085 | 0.999 +/- 0.001 | 0.426 +/- 0.237 |
| Reconnaissance | msp | 0.799 +/- 0.010 | 0.319 +/- 0.100 | 0.050 / 0.039 / 0.069 | 0.857 +/- 0.068 | 0.319 +/- 0.100 |
| Reconnaissance | entropy | 0.839 +/- 0.009 | 0.373 +/- 0.161 | 0.050 / 0.048 / 0.062 | 0.896 +/- 0.061 | 0.416 +/- 0.131 |
| Reconnaissance | msp_pc | 0.769 +/- 0.018 | 0.269 +/- 0.100 | 0.051 / 0.039 / 0.071 | 0.874 +/- 0.074 | 0.261 +/- 0.093 |
| Reconnaissance | entropy_pc | 0.806 +/- 0.012 | 0.286 +/- 0.143 | 0.051 / 0.043 / 0.068 | 0.939 +/- 0.081 | 0.288 +/- 0.115 |
| Worms | msp | 0.634 +/- 0.015 | 0.046 +/- 0.028 | 0.050 / 0.042 / 0.064 | 0.994 +/- 0.000 | 0.046 +/- 0.028 |
| Worms | entropy | 0.674 +/- 0.013 | 0.036 +/- 0.026 | 0.049 / 0.049 / 0.039 | 0.994 +/- 0.000 | 0.048 +/- 0.029 |
| Worms | msp_pc | 0.571 +/- 0.084 | 0.044 +/- 0.029 | 0.050 / 0.039 / 0.072 | 0.994 +/- 0.000 | 0.041 +/- 0.026 |
| Worms | entropy_pc | 0.618 +/- 0.074 | 0.063 +/- 0.022 | 0.050 / 0.040 / 0.072 | 0.994 +/- 0.000 | 0.062 +/- 0.035 |
| Shellcode | msp | 0.817 +/- 0.003 | 0.244 +/- 0.057 | 0.050 / 0.046 / 0.061 | 0.953 +/- 0.013 | 0.244 +/- 0.057 |
| Shellcode | entropy | 0.882 +/- 0.004 | 0.170 +/- 0.057 | 0.049 / 0.040 / 0.024 | 0.935 +/- 0.017 | 0.355 +/- 0.069 |
| Shellcode | msp_pc | 0.801 +/- 0.015 | 0.229 +/- 0.042 | 0.050 / 0.044 / 0.073 | 0.972 +/- 0.008 | 0.189 +/- 0.032 |
| Shellcode | entropy_pc | 0.854 +/- 0.020 | 0.367 +/- 0.053 | 0.050 / 0.043 / 0.075 | 0.984 +/- 0.015 | 0.298 +/- 0.055 |
| Overlap-Group-1 (all three) | msp | 0.804 +/- 0.005 | 0.372 +/- 0.111 | 0.050 / 0.048 / 0.040 | 0.953 +/- 0.010 | 0.372 +/- 0.111 |
| Overlap-Group-1 (all three) | entropy | 0.816 +/- 0.003 | 0.370 +/- 0.130 | 0.050 / 0.050 / 0.040 | 0.954 +/- 0.012 | 0.372 +/- 0.128 |
| Overlap-Group-1 (all three) | msp_pc | 0.720 +/- 0.048 | 0.137 +/- 0.021 | 0.050 / 0.040 / 0.060 | 0.960 +/- 0.011 | 0.086 +/- 0.024 |
| Overlap-Group-1 (all three) | entropy_pc | 0.720 +/- 0.052 | 0.154 +/- 0.021 | 0.050 / 0.041 / 0.063 | 0.966 +/- 0.013 | 0.077 +/- 0.041 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | Generic | Reconnaissance | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msp | 358 of 1456 | 7 of 171 | 437 of 7590 | 319 of 4810 | 137 of 3418 | 107 of 2469 | 218 of 1694 | 44 of 438 | 38 of 345 | 1937 of 33832 | 0.103 |
| entropy | 254 of 1456 | 4 of 171 | 262 of 7590 | 223 of 4810 | 103 of 3418 | 115 of 2469 | 205 of 1694 | 89 of 438 | 60 of 345 | 307 of 33832 | 0.163 |
| msp_pc | 341 of 1456 | 7 of 171 | 438 of 7590 | 431 of 4810 | 169 of 3418 | 106 of 2469 | 161 of 1694 | 23 of 438 | 19 of 345 | 2896 of 33832 | 0.081 |
| entropy_pc | 540 of 1456 | 11 of 171 | 488 of 7590 | 443 of 4810 | 195 of 3418 | 129 of 2469 | 168 of 1694 | 30 of 438 | 21 of 345 | 2810 of 33832 | 0.123 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| msp | 0.289 +/- 0.012 | 0.311 +/- 0.014 | 0.254 +/- 0.012 | 0.057 +/- 0.013 | 0.879 +/- 0.023 | 0.955 +/- 0.009 | 0.224 +/- 0.038 |
| entropy | 0.289 +/- 0.012 | 0.291 +/- 0.012 | 0.282 +/- 0.011 | 0.009 +/- 0.004 | 0.976 +/- 0.009 | 0.941 +/- 0.012 | 0.159 +/- 0.047 |
| msp_pc | 0.289 +/- 0.012 | 0.346 +/- 0.035 | 0.260 +/- 0.009 | 0.086 +/- 0.038 | 0.901 +/- 0.019 | 0.974 +/- 0.011 | 0.214 +/- 0.038 |
| entropy_pc | 0.289 +/- 0.012 | 0.351 +/- 0.037 | 0.268 +/- 0.008 | 0.083 +/- 0.036 | 0.927 +/- 0.014 | 0.986 +/- 0.015 | 0.339 +/- 0.030 |

#### perclass (48f, mean over seeds 42-46)

Baseline for the verdict: `msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| msp | 0.774 | 0.234 | +0.000 | 0 of 5 | Exploits (0.675) | 0.833 +/- 0.006 | 0.334 +/- 0.037 | 0.334 +/- 0.037 | no |
| entropy | 0.811 | 0.283 | +0.049 | 5 of 5 | Exploits (0.702) | 0.881 +/- 0.007 | 0.294 +/- 0.072 | 0.447 +/- 0.081 | no |
| msp_pc | 0.687 | 0.170 | -0.064 | 0 of 5 | Exploits (0.398) | 0.788 +/- 0.044 | 0.326 +/- 0.035 | 0.223 +/- 0.034 | no |
| entropy_pc | 0.717 | 0.253 | +0.019 | 3 of 5 | Exploits (0.380) | 0.829 +/- 0.020 | 0.472 +/- 0.019 | 0.362 +/- 0.046 | no |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | msp | 0.833 +/- 0.006 | 0.334 +/- 0.037 | 0.050 / 0.044 / 0.050 | 0.991 +/- 0.003 | 0.334 +/- 0.037 |
| Worms + Shellcode | entropy | 0.881 +/- 0.007 | 0.294 +/- 0.072 | 0.050 / 0.048 / 0.029 | 0.987 +/- 0.004 | 0.447 +/- 0.081 |
| Worms + Shellcode | msp_pc | 0.788 +/- 0.044 | 0.326 +/- 0.035 | 0.050 / 0.045 / 0.081 | 0.996 +/- 0.001 | 0.223 +/- 0.034 |
| Worms + Shellcode | entropy_pc | 0.829 +/- 0.020 | 0.472 +/- 0.019 | 0.050 / 0.052 / 0.092 | 0.998 +/- 0.001 | 0.362 +/- 0.046 |
| Analysis | msp | 0.882 +/- 0.016 | 0.381 +/- 0.152 | 0.050 / 0.048 / 0.039 | 0.845 +/- 0.003 | 0.382 +/- 0.152 |
| Analysis | entropy | 0.910 +/- 0.009 | 0.444 +/- 0.147 | 0.050 / 0.052 / 0.030 | 0.841 +/- 0.005 | 0.529 +/- 0.183 |
| Analysis | msp_pc | 0.785 +/- 0.038 | 0.097 +/- 0.023 | 0.050 / 0.048 / 0.076 | 0.863 +/- 0.013 | 0.042 +/- 0.008 |
| Analysis | entropy_pc | 0.808 +/- 0.034 | 0.147 +/- 0.029 | 0.050 / 0.050 / 0.085 | 0.890 +/- 0.019 | 0.058 +/- 0.020 |
| Backdoor | msp | 0.901 +/- 0.012 | 0.419 +/- 0.180 | 0.050 / 0.045 / 0.043 | 0.998 +/- 0.001 | 0.419 +/- 0.180 |
| Backdoor | entropy | 0.933 +/- 0.006 | 0.510 +/- 0.188 | 0.050 / 0.049 / 0.034 | 0.998 +/- 0.001 | 0.590 +/- 0.192 |
| Backdoor | msp_pc | 0.790 +/- 0.025 | 0.137 +/- 0.026 | 0.050 / 0.044 / 0.077 | 0.998 +/- 0.001 | 0.070 +/- 0.031 |
| Backdoor | entropy_pc | 0.818 +/- 0.031 | 0.172 +/- 0.038 | 0.050 / 0.048 / 0.084 | 1.000 +/- 0.000 | 0.066 +/- 0.030 |
| DoS | msp | 0.713 +/- 0.007 | 0.168 +/- 0.042 | 0.050 / 0.049 / 0.049 | 0.994 +/- 0.002 | 0.168 +/- 0.042 |
| DoS | entropy | 0.743 +/- 0.008 | 0.212 +/- 0.073 | 0.050 / 0.048 / 0.029 | 0.992 +/- 0.003 | 0.291 +/- 0.052 |
| DoS | msp_pc | 0.580 +/- 0.081 | 0.103 +/- 0.005 | 0.051 / 0.045 / 0.072 | 0.996 +/- 0.002 | 0.077 +/- 0.015 |
| DoS | entropy_pc | 0.602 +/- 0.070 | 0.141 +/- 0.006 | 0.050 / 0.051 / 0.081 | 0.998 +/- 0.002 | 0.095 +/- 0.026 |
| Exploits | msp | 0.675 +/- 0.007 | 0.102 +/- 0.030 | 0.050 / 0.053 / 0.064 | 0.970 +/- 0.004 | 0.102 +/- 0.030 |
| Exploits | entropy | 0.702 +/- 0.003 | 0.123 +/- 0.033 | 0.050 / 0.052 / 0.036 | 0.968 +/- 0.005 | 0.197 +/- 0.057 |
| Exploits | msp_pc | 0.398 +/- 0.083 | 0.105 +/- 0.016 | 0.050 / 0.053 / 0.082 | 0.979 +/- 0.012 | 0.082 +/- 0.013 |
| Exploits | entropy_pc | 0.380 +/- 0.070 | 0.121 +/- 0.007 | 0.051 / 0.049 / 0.083 | 0.986 +/- 0.008 | 0.097 +/- 0.024 |
| Fuzzers | msp | 0.699 +/- 0.007 | 0.083 +/- 0.017 | 0.050 / 0.053 / 0.051 | 0.238 +/- 0.016 | 0.083 +/- 0.017 |
| Fuzzers | entropy | 0.704 +/- 0.006 | 0.110 +/- 0.029 | 0.050 / 0.062 / 0.049 | 0.240 +/- 0.019 | 0.113 +/- 0.025 |
| Fuzzers | msp_pc | 0.755 +/- 0.015 | 0.206 +/- 0.089 | 0.051 / 0.051 / 0.076 | 0.381 +/- 0.087 | 0.136 +/- 0.044 |
| Fuzzers | entropy_pc | 0.763 +/- 0.014 | 0.228 +/- 0.092 | 0.050 / 0.055 / 0.080 | 0.386 +/- 0.089 | 0.141 +/- 0.042 |
| Generic | msp | 0.776 +/- 0.059 | 0.191 +/- 0.100 | 0.050 / 0.050 / 0.063 | 0.892 +/- 0.103 | 0.191 +/- 0.100 |
| Generic | entropy | 0.852 +/- 0.049 | 0.258 +/- 0.131 | 0.050 / 0.048 / 0.038 | 0.890 +/- 0.101 | 0.383 +/- 0.164 |
| Generic | msp_pc | 0.730 +/- 0.110 | 0.216 +/- 0.130 | 0.050 / 0.046 / 0.079 | 0.922 +/- 0.098 | 0.182 +/- 0.111 |
| Generic | entropy_pc | 0.835 +/- 0.071 | 0.517 +/- 0.237 | 0.050 / 0.047 / 0.083 | 0.981 +/- 0.022 | 0.454 +/- 0.210 |
| Reconnaissance | msp | 0.792 +/- 0.013 | 0.303 +/- 0.047 | 0.050 / 0.039 / 0.068 | 0.995 +/- 0.002 | 0.303 +/- 0.047 |
| Reconnaissance | entropy | 0.843 +/- 0.011 | 0.482 +/- 0.067 | 0.050 / 0.052 / 0.061 | 0.995 +/- 0.001 | 0.510 +/- 0.045 |
| Reconnaissance | msp_pc | 0.728 +/- 0.037 | 0.227 +/- 0.058 | 0.051 / 0.035 / 0.070 | 0.996 +/- 0.002 | 0.223 +/- 0.051 |
| Reconnaissance | entropy_pc | 0.735 +/- 0.046 | 0.328 +/- 0.113 | 0.051 / 0.042 / 0.075 | 0.998 +/- 0.002 | 0.318 +/- 0.101 |
| Worms | msp | 0.676 +/- 0.021 | 0.082 +/- 0.024 | 0.050 / 0.049 / 0.056 | 1.000 +/- 0.000 | 0.082 +/- 0.024 |
| Worms | entropy | 0.715 +/- 0.023 | 0.068 +/- 0.017 | 0.050 / 0.054 / 0.038 | 0.999 +/- 0.003 | 0.099 +/- 0.033 |
| Worms | msp_pc | 0.600 +/- 0.109 | 0.071 +/- 0.022 | 0.050 / 0.040 / 0.075 | 1.000 +/- 0.000 | 0.056 +/- 0.025 |
| Worms | entropy_pc | 0.660 +/- 0.053 | 0.112 +/- 0.015 | 0.051 / 0.044 / 0.082 | 1.000 +/- 0.000 | 0.077 +/- 0.030 |
| Shellcode | msp | 0.855 +/- 0.005 | 0.378 +/- 0.058 | 0.050 / 0.045 / 0.048 | 0.989 +/- 0.002 | 0.378 +/- 0.058 |
| Shellcode | entropy | 0.901 +/- 0.007 | 0.340 +/- 0.080 | 0.050 / 0.044 / 0.028 | 0.985 +/- 0.004 | 0.490 +/- 0.077 |
| Shellcode | msp_pc | 0.817 +/- 0.032 | 0.366 +/- 0.033 | 0.050 / 0.044 / 0.077 | 0.995 +/- 0.002 | 0.267 +/- 0.036 |
| Shellcode | entropy_pc | 0.850 +/- 0.018 | 0.508 +/- 0.021 | 0.050 / 0.051 / 0.088 | 0.997 +/- 0.001 | 0.398 +/- 0.045 |
| Overlap-Group-1 (all three) | msp | 0.811 +/- 0.004 | 0.423 +/- 0.084 | 0.050 / 0.043 / 0.039 | 0.964 +/- 0.008 | 0.423 +/- 0.084 |
| Overlap-Group-1 (all three) | entropy | 0.821 +/- 0.002 | 0.400 +/- 0.125 | 0.050 / 0.048 / 0.041 | 0.965 +/- 0.010 | 0.416 +/- 0.109 |
| Overlap-Group-1 (all three) | msp_pc | 0.723 +/- 0.065 | 0.180 +/- 0.035 | 0.051 / 0.038 / 0.054 | 0.967 +/- 0.008 | 0.139 +/- 0.057 |
| Overlap-Group-1 (all three) | entropy_pc | 0.703 +/- 0.057 | 0.191 +/- 0.038 | 0.051 / 0.037 / 0.061 | 0.972 +/- 0.009 | 0.131 +/- 0.060 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | Generic | Reconnaissance | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msp | 534 of 1456 | 10 of 171 | 339 of 7590 | 489 of 4810 | 119 of 3418 | 107 of 2469 | 240 of 1694 | 85 of 438 | 79 of 345 | 1294 of 33832 | 0.175 |
| entropy | 472 of 1456 | 6 of 171 | 263 of 7590 | 368 of 4810 | 96 of 3418 | 119 of 2469 | 238 of 1694 | 120 of 438 | 101 of 345 | 270 of 33832 | 0.244 |
| msp_pc | 518 of 1456 | 12 of 171 | 391 of 7590 | 727 of 4810 | 134 of 3418 | 111 of 2469 | 185 of 1694 | 57 of 438 | 50 of 345 | 2782 of 33832 | 0.114 |
| entropy_pc | 743 of 1456 | 25 of 171 | 446 of 7590 | 956 of 4810 | 171 of 3418 | 119 of 2469 | 176 of 1694 | 59 of 438 | 41 of 345 | 3035 of 33832 | 0.138 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| msp | 0.298 +/- 0.013 | 0.314 +/- 0.013 | 0.275 +/- 0.016 | 0.038 +/- 0.016 | 0.924 +/- 0.030 | 0.991 +/- 0.003 | 0.334 +/- 0.037 |
| entropy | 0.298 +/- 0.013 | 0.300 +/- 0.013 | 0.292 +/- 0.012 | 0.008 +/- 0.004 | 0.979 +/- 0.009 | 0.987 +/- 0.004 | 0.294 +/- 0.072 |
| msp_pc | 0.298 +/- 0.013 | 0.354 +/- 0.030 | 0.271 +/- 0.014 | 0.082 +/- 0.034 | 0.910 +/- 0.014 | 0.996 +/- 0.001 | 0.326 +/- 0.035 |
| entropy_pc | 0.298 +/- 0.013 | 0.364 +/- 0.029 | 0.274 +/- 0.011 | 0.090 +/- 0.030 | 0.919 +/- 0.010 | 0.998 +/- 0.001 | 0.472 +/- 0.019 |

## Source: open_set_boost_ensemble_40f_48f.md

### Task 4.5: ensemble

#### ensemble (40f, mean over seeds 42-46)

Baseline for the verdict: `msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| msp | 0.769 | 0.213 | +0.000 | 0 of 5 | Worms (0.634) | 0.798 +/- 0.004 | 0.224 +/- 0.038 | 0.224 +/- 0.038 | no |
| entropy | 0.810 | 0.266 | +0.053 | 5 of 5 | Worms (0.674) | 0.862 +/- 0.005 | 0.159 +/- 0.047 | 0.307 +/- 0.034 | no |
| ens_mi | 0.733 | 0.202 | -0.011 | 1 of 5 | Analysis (0.620) | 0.775 +/- 0.004 | 0.134 +/- 0.037 | 0.120 +/- 0.031 | no |
| ens_var | 0.717 | 0.150 | -0.063 | 0 of 5 | Analysis (0.643) | 0.756 +/- 0.005 | 0.100 +/- 0.023 | 0.094 +/- 0.022 | no |
| ens_msp | 0.770 | 0.206 | -0.007 | 2 of 5 | Worms (0.637) | 0.799 +/- 0.003 | 0.228 +/- 0.040 | 0.228 +/- 0.041 | no |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | msp | 0.798 +/- 0.004 | 0.224 +/- 0.038 | 0.050 / 0.044 / 0.059 | 0.955 +/- 0.009 | 0.224 +/- 0.038 |
| Worms + Shellcode | entropy | 0.862 +/- 0.005 | 0.159 +/- 0.047 | 0.048 / 0.041 / 0.025 | 0.941 +/- 0.012 | 0.307 +/- 0.034 |
| Worms + Shellcode | ens_mi | 0.775 +/- 0.004 | 0.134 +/- 0.037 | 0.050 / 0.049 / 0.065 | 0.947 +/- 0.009 | 0.120 +/- 0.031 |
| Worms + Shellcode | ens_var | 0.756 +/- 0.005 | 0.100 +/- 0.023 | 0.050 / 0.047 / 0.063 | 0.948 +/- 0.010 | 0.094 +/- 0.022 |
| Worms + Shellcode | ens_msp | 0.799 +/- 0.003 | 0.228 +/- 0.040 | 0.050 / 0.045 / 0.060 | 0.955 +/- 0.010 | 0.228 +/- 0.041 |
| Analysis | msp | 0.885 +/- 0.009 | 0.253 +/- 0.114 | 0.050 / 0.044 / 0.047 | 0.849 +/- 0.006 | 0.253 +/- 0.114 |
| Analysis | entropy | 0.923 +/- 0.003 | 0.362 +/- 0.136 | 0.048 / 0.043 / 0.031 | 0.842 +/- 0.007 | 0.533 +/- 0.112 |
| Analysis | ens_mi | 0.620 +/- 0.012 | 0.070 +/- 0.013 | 0.050 / 0.050 / 0.068 | 0.880 +/- 0.006 | 0.053 +/- 0.013 |
| Analysis | ens_var | 0.643 +/- 0.014 | 0.057 +/- 0.007 | 0.050 / 0.048 / 0.063 | 0.871 +/- 0.005 | 0.045 +/- 0.011 |
| Analysis | ens_msp | 0.883 +/- 0.009 | 0.253 +/- 0.113 | 0.050 / 0.045 / 0.049 | 0.851 +/- 0.005 | 0.235 +/- 0.109 |
| Backdoor | msp | 0.882 +/- 0.009 | 0.274 +/- 0.104 | 0.050 / 0.045 / 0.055 | 0.994 +/- 0.004 | 0.274 +/- 0.104 |
| Backdoor | entropy | 0.926 +/- 0.004 | 0.421 +/- 0.144 | 0.050 / 0.042 / 0.034 | 0.993 +/- 0.003 | 0.632 +/- 0.147 |
| Backdoor | ens_mi | 0.631 +/- 0.017 | 0.106 +/- 0.007 | 0.050 / 0.050 / 0.069 | 0.996 +/- 0.001 | 0.095 +/- 0.011 |
| Backdoor | ens_var | 0.649 +/- 0.016 | 0.081 +/- 0.009 | 0.050 / 0.048 / 0.065 | 0.995 +/- 0.001 | 0.072 +/- 0.010 |
| Backdoor | ens_msp | 0.881 +/- 0.009 | 0.272 +/- 0.085 | 0.050 / 0.046 / 0.056 | 0.996 +/- 0.001 | 0.264 +/- 0.094 |
| DoS | msp | 0.697 +/- 0.006 | 0.162 +/- 0.041 | 0.050 / 0.058 / 0.072 | 0.984 +/- 0.004 | 0.162 +/- 0.041 |
| DoS | entropy | 0.736 +/- 0.007 | 0.203 +/- 0.069 | 0.050 / 0.050 / 0.036 | 0.976 +/- 0.005 | 0.324 +/- 0.046 |
| DoS | ens_mi | 0.673 +/- 0.012 | 0.139 +/- 0.017 | 0.050 / 0.064 / 0.080 | 0.987 +/- 0.002 | 0.127 +/- 0.019 |
| DoS | ens_var | 0.654 +/- 0.011 | 0.109 +/- 0.014 | 0.050 / 0.061 / 0.079 | 0.985 +/- 0.002 | 0.101 +/- 0.017 |
| DoS | ens_msp | 0.700 +/- 0.006 | 0.158 +/- 0.041 | 0.050 / 0.057 / 0.071 | 0.985 +/- 0.004 | 0.162 +/- 0.040 |
| Exploits | msp | 0.681 +/- 0.010 | 0.123 +/- 0.035 | 0.050 / 0.056 / 0.073 | 0.961 +/- 0.007 | 0.123 +/- 0.035 |
| Exploits | entropy | 0.710 +/- 0.007 | 0.119 +/- 0.020 | 0.050 / 0.050 / 0.041 | 0.957 +/- 0.007 | 0.191 +/- 0.079 |
| Exploits | ens_mi | 0.795 +/- 0.006 | 0.321 +/- 0.109 | 0.050 / 0.057 / 0.083 | 0.973 +/- 0.006 | 0.303 +/- 0.087 |
| Exploits | ens_var | 0.747 +/- 0.007 | 0.260 +/- 0.082 | 0.050 / 0.056 / 0.090 | 0.971 +/- 0.005 | 0.234 +/- 0.062 |
| Exploits | ens_msp | 0.685 +/- 0.010 | 0.128 +/- 0.038 | 0.049 / 0.056 / 0.072 | 0.963 +/- 0.007 | 0.129 +/- 0.036 |
| Fuzzers | msp | 0.693 +/- 0.007 | 0.092 +/- 0.019 | 0.050 / 0.051 / 0.065 | 0.262 +/- 0.016 | 0.092 +/- 0.019 |
| Fuzzers | entropy | 0.699 +/- 0.007 | 0.103 +/- 0.023 | 0.049 / 0.057 / 0.055 | 0.259 +/- 0.018 | 0.121 +/- 0.023 |
| Fuzzers | ens_mi | 0.692 +/- 0.009 | 0.107 +/- 0.027 | 0.050 / 0.059 / 0.065 | 0.291 +/- 0.012 | 0.108 +/- 0.019 |
| Fuzzers | ens_var | 0.690 +/- 0.009 | 0.089 +/- 0.021 | 0.050 / 0.057 / 0.063 | 0.278 +/- 0.009 | 0.094 +/- 0.016 |
| Fuzzers | ens_msp | 0.696 +/- 0.008 | 0.091 +/- 0.017 | 0.050 / 0.054 / 0.065 | 0.263 +/- 0.014 | 0.092 +/- 0.018 |
| Generic | msp | 0.828 +/- 0.067 | 0.402 +/- 0.229 | 0.050 / 0.058 / 0.081 | 0.999 +/- 0.000 | 0.402 +/- 0.229 |
| Generic | entropy | 0.896 +/- 0.036 | 0.607 +/- 0.216 | 0.050 / 0.054 / 0.058 | 0.998 +/- 0.001 | 0.657 +/- 0.210 |
| Generic | ens_mi | 0.891 +/- 0.035 | 0.624 +/- 0.189 | 0.050 / 0.054 / 0.073 | 0.998 +/- 0.001 | 0.648 +/- 0.182 |
| Generic | ens_var | 0.857 +/- 0.043 | 0.429 +/- 0.221 | 0.050 / 0.057 / 0.077 | 0.997 +/- 0.003 | 0.442 +/- 0.210 |
| Generic | ens_msp | 0.835 +/- 0.048 | 0.341 +/- 0.168 | 0.050 / 0.055 / 0.078 | 0.988 +/- 0.025 | 0.351 +/- 0.173 |
| Reconnaissance | msp | 0.799 +/- 0.010 | 0.319 +/- 0.100 | 0.050 / 0.039 / 0.069 | 0.857 +/- 0.068 | 0.319 +/- 0.100 |
| Reconnaissance | entropy | 0.839 +/- 0.009 | 0.373 +/- 0.161 | 0.050 / 0.048 / 0.062 | 0.896 +/- 0.061 | 0.416 +/- 0.131 |
| Reconnaissance | ens_mi | 0.771 +/- 0.009 | 0.184 +/- 0.066 | 0.050 / 0.048 / 0.061 | 0.819 +/- 0.080 | 0.203 +/- 0.077 |
| Reconnaissance | ens_var | 0.755 +/- 0.009 | 0.125 +/- 0.038 | 0.050 / 0.043 / 0.057 | 0.788 +/- 0.079 | 0.156 +/- 0.066 |
| Reconnaissance | ens_msp | 0.799 +/- 0.009 | 0.316 +/- 0.090 | 0.050 / 0.040 / 0.070 | 0.863 +/- 0.067 | 0.312 +/- 0.088 |
| Worms | msp | 0.634 +/- 0.015 | 0.046 +/- 0.028 | 0.050 / 0.042 / 0.064 | 0.994 +/- 0.000 | 0.046 +/- 0.028 |
| Worms | entropy | 0.674 +/- 0.013 | 0.036 +/- 0.026 | 0.049 / 0.049 / 0.039 | 0.994 +/- 0.000 | 0.048 +/- 0.029 |
| Worms | ens_mi | 0.748 +/- 0.017 | 0.139 +/- 0.019 | 0.050 / 0.051 / 0.072 | 0.996 +/- 0.003 | 0.124 +/- 0.022 |
| Worms | ens_var | 0.704 +/- 0.016 | 0.099 +/- 0.023 | 0.050 / 0.050 / 0.068 | 0.995 +/- 0.003 | 0.092 +/- 0.016 |
| Worms | ens_msp | 0.637 +/- 0.016 | 0.056 +/- 0.024 | 0.050 / 0.043 / 0.065 | 0.994 +/- 0.000 | 0.055 +/- 0.026 |
| Shellcode | msp | 0.817 +/- 0.003 | 0.244 +/- 0.057 | 0.050 / 0.046 / 0.061 | 0.953 +/- 0.013 | 0.244 +/- 0.057 |
| Shellcode | entropy | 0.882 +/- 0.004 | 0.170 +/- 0.057 | 0.049 / 0.040 / 0.024 | 0.935 +/- 0.017 | 0.355 +/- 0.069 |
| Shellcode | ens_mi | 0.776 +/- 0.006 | 0.129 +/- 0.027 | 0.050 / 0.045 / 0.064 | 0.942 +/- 0.015 | 0.124 +/- 0.031 |
| Shellcode | ens_var | 0.759 +/- 0.004 | 0.100 +/- 0.024 | 0.050 / 0.048 / 0.064 | 0.943 +/- 0.014 | 0.095 +/- 0.030 |
| Shellcode | ens_msp | 0.817 +/- 0.004 | 0.237 +/- 0.057 | 0.050 / 0.043 / 0.060 | 0.951 +/- 0.014 | 0.238 +/- 0.056 |
| Overlap-Group-1 (all three) | msp | 0.804 +/- 0.005 | 0.372 +/- 0.111 | 0.050 / 0.048 / 0.040 | 0.953 +/- 0.010 | 0.372 +/- 0.111 |
| Overlap-Group-1 (all three) | entropy | 0.816 +/- 0.003 | 0.370 +/- 0.130 | 0.050 / 0.050 / 0.040 | 0.954 +/- 0.012 | 0.372 +/- 0.128 |
| Overlap-Group-1 (all three) | ens_mi | 0.679 +/- 0.004 | 0.094 +/- 0.010 | 0.050 / 0.039 / 0.063 | 0.964 +/- 0.009 | 0.066 +/- 0.027 |
| Overlap-Group-1 (all three) | ens_var | 0.677 +/- 0.003 | 0.074 +/- 0.010 | 0.050 / 0.041 / 0.065 | 0.963 +/- 0.008 | 0.051 +/- 0.022 |
| Overlap-Group-1 (all three) | ens_msp | 0.806 +/- 0.005 | 0.371 +/- 0.107 | 0.050 / 0.048 / 0.040 | 0.954 +/- 0.011 | 0.361 +/- 0.115 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | Generic | Reconnaissance | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msp | 358 of 1456 | 7 of 171 | 437 of 7590 | 319 of 4810 | 137 of 3418 | 107 of 2469 | 218 of 1694 | 44 of 438 | 38 of 345 | 1937 of 33832 | 0.103 |
| entropy | 254 of 1456 | 4 of 171 | 262 of 7590 | 223 of 4810 | 103 of 3418 | 115 of 2469 | 205 of 1694 | 89 of 438 | 60 of 345 | 307 of 33832 | 0.163 |
| ens_mi | 194 of 1456 | 24 of 171 | 900 of 7590 | 357 of 4810 | 249 of 3418 | 147 of 2469 | 294 of 1694 | 44 of 438 | 22 of 345 | 1559 of 33832 | 0.058 |
| ens_var | 145 of 1456 | 18 of 171 | 741 of 7590 | 363 of 4810 | 193 of 3418 | 139 of 2469 | 280 of 1694 | 40 of 438 | 15 of 345 | 1684 of 33832 | 0.045 |
| ens_msp | 365 of 1456 | 6 of 171 | 437 of 7590 | 323 of 4810 | 139 of 3418 | 114 of 2469 | 218 of 1694 | 51 of 438 | 38 of 345 | 1962 of 33832 | 0.103 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| msp | 0.289 +/- 0.012 | 0.311 +/- 0.014 | 0.254 +/- 0.012 | 0.057 +/- 0.013 | 0.879 +/- 0.023 | 0.955 +/- 0.009 | 0.224 +/- 0.038 |
| entropy | 0.289 +/- 0.012 | 0.291 +/- 0.012 | 0.282 +/- 0.011 | 0.009 +/- 0.004 | 0.976 +/- 0.009 | 0.941 +/- 0.012 | 0.159 +/- 0.047 |
| ens_mi | 0.289 +/- 0.012 | 0.307 +/- 0.011 | 0.261 +/- 0.014 | 0.046 +/- 0.012 | 0.904 +/- 0.023 | 0.947 +/- 0.009 | 0.134 +/- 0.037 |
| ens_var | 0.289 +/- 0.012 | 0.310 +/- 0.012 | 0.260 +/- 0.014 | 0.050 +/- 0.013 | 0.899 +/- 0.025 | 0.948 +/- 0.010 | 0.100 +/- 0.023 |
| ens_msp | 0.289 +/- 0.012 | 0.312 +/- 0.014 | 0.254 +/- 0.013 | 0.058 +/- 0.014 | 0.878 +/- 0.024 | 0.955 +/- 0.010 | 0.228 +/- 0.040 |

#### ensemble (48f, mean over seeds 42-46)

Baseline for the verdict: `msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| msp | 0.774 | 0.234 | +0.000 | 0 of 5 | Exploits (0.675) | 0.833 +/- 0.006 | 0.334 +/- 0.037 | 0.334 +/- 0.037 | no |
| entropy | 0.811 | 0.283 | +0.049 | 5 of 5 | Exploits (0.702) | 0.881 +/- 0.007 | 0.294 +/- 0.072 | 0.447 +/- 0.081 | no |
| ens_mi | 0.757 | 0.268 | +0.034 | 5 of 5 | Analysis (0.667) | 0.832 +/- 0.007 | 0.335 +/- 0.080 | 0.192 +/- 0.059 | no |
| ens_var | 0.734 | 0.199 | -0.035 | 0 of 5 | DoS (0.670) | 0.803 +/- 0.007 | 0.222 +/- 0.053 | 0.132 +/- 0.042 | no |
| ens_msp | 0.776 | 0.242 | +0.008 | 3 of 5 | Worms (0.675) | 0.841 +/- 0.007 | 0.368 +/- 0.046 | 0.364 +/- 0.048 | no |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | msp | 0.833 +/- 0.006 | 0.334 +/- 0.037 | 0.050 / 0.044 / 0.050 | 0.991 +/- 0.003 | 0.334 +/- 0.037 |
| Worms + Shellcode | entropy | 0.881 +/- 0.007 | 0.294 +/- 0.072 | 0.050 / 0.048 / 0.029 | 0.987 +/- 0.004 | 0.447 +/- 0.081 |
| Worms + Shellcode | ens_mi | 0.832 +/- 0.007 | 0.335 +/- 0.080 | 0.050 / 0.055 / 0.090 | 0.993 +/- 0.001 | 0.192 +/- 0.059 |
| Worms + Shellcode | ens_var | 0.803 +/- 0.007 | 0.222 +/- 0.053 | 0.050 / 0.051 / 0.081 | 0.991 +/- 0.001 | 0.132 +/- 0.042 |
| Worms + Shellcode | ens_msp | 0.841 +/- 0.007 | 0.368 +/- 0.046 | 0.050 / 0.047 / 0.052 | 0.991 +/- 0.003 | 0.364 +/- 0.048 |
| Analysis | msp | 0.882 +/- 0.016 | 0.381 +/- 0.152 | 0.050 / 0.048 / 0.039 | 0.845 +/- 0.003 | 0.382 +/- 0.152 |
| Analysis | entropy | 0.910 +/- 0.009 | 0.444 +/- 0.147 | 0.050 / 0.052 / 0.030 | 0.841 +/- 0.005 | 0.529 +/- 0.183 |
| Analysis | ens_mi | 0.667 +/- 0.015 | 0.102 +/- 0.019 | 0.050 / 0.053 / 0.085 | 0.878 +/- 0.009 | 0.049 +/- 0.018 |
| Analysis | ens_var | 0.671 +/- 0.013 | 0.075 +/- 0.015 | 0.050 / 0.050 / 0.076 | 0.866 +/- 0.004 | 0.038 +/- 0.013 |
| Analysis | ens_msp | 0.881 +/- 0.015 | 0.369 +/- 0.148 | 0.050 / 0.048 / 0.039 | 0.844 +/- 0.004 | 0.359 +/- 0.152 |
| Backdoor | msp | 0.901 +/- 0.012 | 0.419 +/- 0.180 | 0.050 / 0.045 / 0.043 | 0.998 +/- 0.001 | 0.419 +/- 0.180 |
| Backdoor | entropy | 0.933 +/- 0.006 | 0.510 +/- 0.188 | 0.050 / 0.049 / 0.034 | 0.998 +/- 0.001 | 0.590 +/- 0.192 |
| Backdoor | ens_mi | 0.687 +/- 0.018 | 0.154 +/- 0.021 | 0.050 / 0.054 / 0.085 | 1.000 +/- 0.001 | 0.094 +/- 0.023 |
| Backdoor | ens_var | 0.688 +/- 0.016 | 0.114 +/- 0.022 | 0.050 / 0.054 / 0.079 | 0.999 +/- 0.001 | 0.073 +/- 0.019 |
| Backdoor | ens_msp | 0.900 +/- 0.012 | 0.420 +/- 0.170 | 0.050 / 0.045 / 0.046 | 0.998 +/- 0.001 | 0.393 +/- 0.171 |
| DoS | msp | 0.713 +/- 0.007 | 0.168 +/- 0.042 | 0.050 / 0.049 / 0.049 | 0.994 +/- 0.002 | 0.168 +/- 0.042 |
| DoS | entropy | 0.743 +/- 0.008 | 0.212 +/- 0.073 | 0.050 / 0.048 / 0.029 | 0.992 +/- 0.003 | 0.291 +/- 0.052 |
| DoS | ens_mi | 0.694 +/- 0.015 | 0.160 +/- 0.035 | 0.050 / 0.050 / 0.083 | 0.996 +/- 0.001 | 0.106 +/- 0.027 |
| DoS | ens_var | 0.670 +/- 0.013 | 0.129 +/- 0.021 | 0.050 / 0.050 / 0.083 | 0.996 +/- 0.001 | 0.087 +/- 0.023 |
| DoS | ens_msp | 0.713 +/- 0.007 | 0.170 +/- 0.042 | 0.050 / 0.049 / 0.052 | 0.995 +/- 0.002 | 0.164 +/- 0.043 |
| Exploits | msp | 0.675 +/- 0.007 | 0.102 +/- 0.030 | 0.050 / 0.053 / 0.064 | 0.970 +/- 0.004 | 0.102 +/- 0.030 |
| Exploits | entropy | 0.702 +/- 0.003 | 0.123 +/- 0.033 | 0.050 / 0.052 / 0.036 | 0.968 +/- 0.005 | 0.197 +/- 0.057 |
| Exploits | ens_mi | 0.759 +/- 0.005 | 0.280 +/- 0.093 | 0.050 / 0.051 / 0.091 | 0.979 +/- 0.005 | 0.226 +/- 0.069 |
| Exploits | ens_var | 0.713 +/- 0.005 | 0.224 +/- 0.067 | 0.050 / 0.057 / 0.097 | 0.978 +/- 0.005 | 0.175 +/- 0.047 |
| Exploits | ens_msp | 0.677 +/- 0.008 | 0.108 +/- 0.035 | 0.050 / 0.054 / 0.066 | 0.972 +/- 0.005 | 0.106 +/- 0.033 |
| Fuzzers | msp | 0.699 +/- 0.007 | 0.083 +/- 0.017 | 0.050 / 0.053 / 0.051 | 0.238 +/- 0.016 | 0.083 +/- 0.017 |
| Fuzzers | entropy | 0.704 +/- 0.006 | 0.110 +/- 0.029 | 0.050 / 0.062 / 0.049 | 0.240 +/- 0.019 | 0.113 +/- 0.025 |
| Fuzzers | ens_mi | 0.699 +/- 0.006 | 0.137 +/- 0.033 | 0.050 / 0.061 / 0.068 | 0.283 +/- 0.021 | 0.110 +/- 0.023 |
| Fuzzers | ens_var | 0.695 +/- 0.006 | 0.111 +/- 0.030 | 0.050 / 0.056 / 0.063 | 0.267 +/- 0.018 | 0.095 +/- 0.021 |
| Fuzzers | ens_msp | 0.697 +/- 0.005 | 0.085 +/- 0.019 | 0.050 / 0.053 / 0.052 | 0.236 +/- 0.016 | 0.083 +/- 0.017 |
| Generic | msp | 0.776 +/- 0.059 | 0.191 +/- 0.100 | 0.050 / 0.050 / 0.063 | 0.892 +/- 0.103 | 0.191 +/- 0.100 |
| Generic | entropy | 0.852 +/- 0.049 | 0.258 +/- 0.131 | 0.050 / 0.048 / 0.038 | 0.890 +/- 0.101 | 0.383 +/- 0.164 |
| Generic | ens_mi | 0.915 +/- 0.020 | 0.735 +/- 0.142 | 0.050 / 0.052 / 0.084 | 0.993 +/- 0.003 | 0.681 +/- 0.150 |
| Generic | ens_var | 0.875 +/- 0.036 | 0.558 +/- 0.185 | 0.050 / 0.054 / 0.084 | 0.983 +/- 0.010 | 0.483 +/- 0.204 |
| Generic | ens_msp | 0.790 +/- 0.060 | 0.235 +/- 0.130 | 0.050 / 0.053 / 0.067 | 0.948 +/- 0.051 | 0.229 +/- 0.125 |
| Reconnaissance | msp | 0.792 +/- 0.013 | 0.303 +/- 0.047 | 0.050 / 0.039 / 0.068 | 0.995 +/- 0.002 | 0.303 +/- 0.047 |
| Reconnaissance | entropy | 0.843 +/- 0.011 | 0.482 +/- 0.067 | 0.050 / 0.052 / 0.061 | 0.995 +/- 0.001 | 0.510 +/- 0.045 |
| Reconnaissance | ens_mi | 0.787 +/- 0.013 | 0.315 +/- 0.062 | 0.050 / 0.041 / 0.066 | 0.991 +/- 0.003 | 0.319 +/- 0.050 |
| Reconnaissance | ens_var | 0.763 +/- 0.014 | 0.217 +/- 0.064 | 0.050 / 0.037 / 0.061 | 0.986 +/- 0.006 | 0.234 +/- 0.046 |
| Reconnaissance | ens_msp | 0.791 +/- 0.016 | 0.305 +/- 0.057 | 0.050 / 0.040 / 0.068 | 0.995 +/- 0.001 | 0.306 +/- 0.053 |
| Worms | msp | 0.676 +/- 0.021 | 0.082 +/- 0.024 | 0.050 / 0.049 / 0.056 | 1.000 +/- 0.000 | 0.082 +/- 0.024 |
| Worms | entropy | 0.715 +/- 0.023 | 0.068 +/- 0.017 | 0.050 / 0.054 / 0.038 | 0.999 +/- 0.003 | 0.099 +/- 0.033 |
| Worms | ens_mi | 0.765 +/- 0.006 | 0.199 +/- 0.071 | 0.050 / 0.050 / 0.088 | 0.999 +/- 0.003 | 0.132 +/- 0.045 |
| Worms | ens_var | 0.717 +/- 0.007 | 0.132 +/- 0.042 | 0.050 / 0.050 / 0.082 | 0.998 +/- 0.005 | 0.092 +/- 0.034 |
| Worms | ens_msp | 0.675 +/- 0.015 | 0.089 +/- 0.019 | 0.050 / 0.053 / 0.060 | 1.000 +/- 0.000 | 0.087 +/- 0.016 |
| Shellcode | msp | 0.855 +/- 0.005 | 0.378 +/- 0.058 | 0.050 / 0.045 / 0.048 | 0.989 +/- 0.002 | 0.378 +/- 0.058 |
| Shellcode | entropy | 0.901 +/- 0.007 | 0.340 +/- 0.080 | 0.050 / 0.044 / 0.028 | 0.985 +/- 0.004 | 0.490 +/- 0.077 |
| Shellcode | ens_mi | 0.838 +/- 0.001 | 0.334 +/- 0.062 | 0.050 / 0.053 / 0.084 | 0.991 +/- 0.002 | 0.192 +/- 0.072 |
| Shellcode | ens_var | 0.812 +/- 0.001 | 0.235 +/- 0.059 | 0.050 / 0.052 / 0.079 | 0.988 +/- 0.001 | 0.140 +/- 0.051 |
| Shellcode | ens_msp | 0.860 +/- 0.007 | 0.402 +/- 0.058 | 0.050 / 0.047 / 0.051 | 0.989 +/- 0.003 | 0.394 +/- 0.059 |
| Overlap-Group-1 (all three) | msp | 0.811 +/- 0.004 | 0.423 +/- 0.084 | 0.050 / 0.043 / 0.039 | 0.964 +/- 0.008 | 0.423 +/- 0.084 |
| Overlap-Group-1 (all three) | entropy | 0.821 +/- 0.002 | 0.400 +/- 0.125 | 0.050 / 0.048 / 0.041 | 0.965 +/- 0.010 | 0.416 +/- 0.109 |
| Overlap-Group-1 (all three) | ens_mi | 0.716 +/- 0.006 | 0.129 +/- 0.019 | 0.050 / 0.042 / 0.074 | 0.973 +/- 0.008 | 0.077 +/- 0.034 |
| Overlap-Group-1 (all three) | ens_var | 0.706 +/- 0.005 | 0.099 +/- 0.016 | 0.050 / 0.042 / 0.071 | 0.971 +/- 0.007 | 0.059 +/- 0.028 |
| Overlap-Group-1 (all three) | ens_msp | 0.811 +/- 0.004 | 0.432 +/- 0.080 | 0.050 / 0.044 / 0.042 | 0.965 +/- 0.008 | 0.416 +/- 0.083 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | Generic | Reconnaissance | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msp | 534 of 1456 | 10 of 171 | 339 of 7590 | 489 of 4810 | 119 of 3418 | 107 of 2469 | 240 of 1694 | 85 of 438 | 79 of 345 | 1294 of 33832 | 0.175 |
| entropy | 472 of 1456 | 6 of 171 | 263 of 7590 | 368 of 4810 | 96 of 3418 | 119 of 2469 | 238 of 1694 | 120 of 438 | 101 of 345 | 270 of 33832 | 0.244 |
| ens_mi | 509 of 1456 | 36 of 171 | 952 of 7590 | 1075 of 4810 | 280 of 3418 | 167 of 2469 | 432 of 1694 | 109 of 438 | 85 of 345 | 1789 of 33832 | 0.101 |
| ens_var | 339 of 1456 | 22 of 171 | 743 of 7590 | 913 of 4810 | 211 of 3418 | 152 of 2469 | 361 of 1694 | 77 of 438 | 52 of 345 | 1886 of 33832 | 0.076 |
| ens_msp | 588 of 1456 | 11 of 171 | 369 of 7590 | 497 of 4810 | 125 of 3418 | 113 of 2469 | 251 of 1694 | 97 of 438 | 88 of 345 | 1283 of 33832 | 0.184 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| msp | 0.298 +/- 0.013 | 0.314 +/- 0.013 | 0.275 +/- 0.016 | 0.038 +/- 0.016 | 0.924 +/- 0.030 | 0.991 +/- 0.003 | 0.334 +/- 0.037 |
| entropy | 0.298 +/- 0.013 | 0.300 +/- 0.013 | 0.292 +/- 0.012 | 0.008 +/- 0.004 | 0.979 +/- 0.009 | 0.987 +/- 0.004 | 0.294 +/- 0.072 |
| ens_mi | 0.298 +/- 0.013 | 0.317 +/- 0.015 | 0.264 +/- 0.015 | 0.053 +/- 0.016 | 0.886 +/- 0.032 | 0.993 +/- 0.001 | 0.335 +/- 0.080 |
| ens_var | 0.298 +/- 0.013 | 0.320 +/- 0.013 | 0.264 +/- 0.015 | 0.056 +/- 0.015 | 0.888 +/- 0.029 | 0.991 +/- 0.001 | 0.222 +/- 0.053 |
| ens_msp | 0.298 +/- 0.013 | 0.314 +/- 0.014 | 0.276 +/- 0.015 | 0.038 +/- 0.015 | 0.927 +/- 0.026 | 0.991 +/- 0.003 | 0.368 +/- 0.046 |

## Source: open_set_boost_distance_40f_48f.md

### Task 4.5: distance

#### distance (40f, mean over seeds 42-46)

Baseline for the verdict: `msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| msp | 0.769 | 0.213 | +0.000 | 0 of 5 | Worms (0.634) | 0.798 +/- 0.004 | 0.224 +/- 0.038 | 0.224 +/- 0.038 | no |
| entropy | 0.810 | 0.266 | +0.053 | 5 of 5 | Worms (0.674) | 0.862 +/- 0.005 | 0.159 +/- 0.047 | 0.307 +/- 0.034 | no |
| knn | 0.623 | 0.152 | -0.061 | 0 of 5 | Shellcode (0.388) | 0.413 +/- 0.008 | 0.024 +/- 0.006 | 0.022 +/- 0.005 | no |
| maha | 0.471 | 0.098 | -0.115 | 0 of 5 | Shellcode (0.307) | 0.328 +/- 0.004 | 0.012 +/- 0.001 | 0.013 +/- 0.005 | no |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | msp | 0.798 +/- 0.004 | 0.224 +/- 0.038 | 0.050 / 0.044 / 0.059 | 0.955 +/- 0.009 | 0.224 +/- 0.038 |
| Worms + Shellcode | entropy | 0.862 +/- 0.005 | 0.159 +/- 0.047 | 0.048 / 0.041 / 0.025 | 0.941 +/- 0.012 | 0.307 +/- 0.034 |
| Worms + Shellcode | knn | 0.413 +/- 0.008 | 0.024 +/- 0.006 | 0.050 / 0.052 / 0.062 | 0.939 +/- 0.013 | 0.022 +/- 0.005 |
| Worms + Shellcode | maha | 0.328 +/- 0.004 | 0.012 +/- 0.001 | 0.050 / 0.048 / 0.053 | 0.936 +/- 0.013 | 0.013 +/- 0.005 |
| Analysis | msp | 0.885 +/- 0.009 | 0.253 +/- 0.114 | 0.050 / 0.044 / 0.047 | 0.849 +/- 0.006 | 0.253 +/- 0.114 |
| Analysis | entropy | 0.923 +/- 0.003 | 0.362 +/- 0.136 | 0.048 / 0.043 / 0.031 | 0.842 +/- 0.007 | 0.533 +/- 0.112 |
| Analysis | knn | 0.587 +/- 0.012 | 0.119 +/- 0.027 | 0.050 / 0.049 / 0.059 | 0.867 +/- 0.006 | 0.098 +/- 0.018 |
| Analysis | maha | 0.371 +/- 0.009 | 0.088 +/- 0.012 | 0.050 / 0.049 / 0.055 | 0.902 +/- 0.006 | 0.077 +/- 0.016 |
| Backdoor | msp | 0.882 +/- 0.009 | 0.274 +/- 0.104 | 0.050 / 0.045 / 0.055 | 0.994 +/- 0.004 | 0.274 +/- 0.104 |
| Backdoor | entropy | 0.926 +/- 0.004 | 0.421 +/- 0.144 | 0.050 / 0.042 / 0.034 | 0.993 +/- 0.003 | 0.632 +/- 0.147 |
| Backdoor | knn | 0.567 +/- 0.017 | 0.091 +/- 0.029 | 0.050 / 0.048 / 0.057 | 0.990 +/- 0.005 | 0.086 +/- 0.024 |
| Backdoor | maha | 0.357 +/- 0.011 | 0.041 +/- 0.007 | 0.050 / 0.046 / 0.052 | 0.990 +/- 0.005 | 0.042 +/- 0.012 |
| DoS | msp | 0.697 +/- 0.006 | 0.162 +/- 0.041 | 0.050 / 0.058 / 0.072 | 0.984 +/- 0.004 | 0.162 +/- 0.041 |
| DoS | entropy | 0.736 +/- 0.007 | 0.203 +/- 0.069 | 0.050 / 0.050 / 0.036 | 0.976 +/- 0.005 | 0.324 +/- 0.046 |
| DoS | knn | 0.641 +/- 0.010 | 0.083 +/- 0.039 | 0.050 / 0.048 / 0.044 | 0.974 +/- 0.003 | 0.121 +/- 0.018 |
| DoS | maha | 0.425 +/- 0.003 | 0.059 +/- 0.012 | 0.050 / 0.060 / 0.044 | 0.974 +/- 0.004 | 0.074 +/- 0.007 |
| Exploits | msp | 0.681 +/- 0.010 | 0.123 +/- 0.035 | 0.050 / 0.056 / 0.073 | 0.961 +/- 0.007 | 0.123 +/- 0.035 |
| Exploits | entropy | 0.710 +/- 0.007 | 0.119 +/- 0.020 | 0.050 / 0.050 / 0.041 | 0.957 +/- 0.007 | 0.191 +/- 0.079 |
| Exploits | knn | 0.806 +/- 0.004 | 0.192 +/- 0.135 | 0.050 / 0.039 / 0.047 | 0.943 +/- 0.008 | 0.308 +/- 0.165 |
| Exploits | maha | 0.653 +/- 0.004 | 0.063 +/- 0.040 | 0.050 / 0.047 / 0.042 | 0.948 +/- 0.012 | 0.144 +/- 0.093 |
| Fuzzers | msp | 0.693 +/- 0.007 | 0.092 +/- 0.019 | 0.050 / 0.051 / 0.065 | 0.262 +/- 0.016 | 0.092 +/- 0.019 |
| Fuzzers | entropy | 0.699 +/- 0.007 | 0.103 +/- 0.023 | 0.049 / 0.057 / 0.055 | 0.259 +/- 0.018 | 0.121 +/- 0.023 |
| Fuzzers | knn | 0.597 +/- 0.004 | 0.069 +/- 0.020 | 0.050 / 0.060 / 0.052 | 0.274 +/- 0.006 | 0.080 +/- 0.015 |
| Fuzzers | maha | 0.508 +/- 0.008 | 0.085 +/- 0.014 | 0.050 / 0.063 / 0.050 | 0.290 +/- 0.007 | 0.107 +/- 0.027 |
| Generic | msp | 0.828 +/- 0.067 | 0.402 +/- 0.229 | 0.050 / 0.058 / 0.081 | 0.999 +/- 0.000 | 0.402 +/- 0.229 |
| Generic | entropy | 0.896 +/- 0.036 | 0.607 +/- 0.216 | 0.050 / 0.054 / 0.058 | 0.998 +/- 0.001 | 0.657 +/- 0.210 |
| Generic | knn | 0.896 +/- 0.010 | 0.641 +/- 0.104 | 0.050 / 0.049 / 0.047 | 0.996 +/- 0.002 | 0.736 +/- 0.038 |
| Generic | maha | 0.759 +/- 0.003 | 0.474 +/- 0.023 | 0.050 / 0.052 / 0.049 | 0.996 +/- 0.003 | 0.512 +/- 0.017 |
| Reconnaissance | msp | 0.799 +/- 0.010 | 0.319 +/- 0.100 | 0.050 / 0.039 / 0.069 | 0.857 +/- 0.068 | 0.319 +/- 0.100 |
| Reconnaissance | entropy | 0.839 +/- 0.009 | 0.373 +/- 0.161 | 0.050 / 0.048 / 0.062 | 0.896 +/- 0.061 | 0.416 +/- 0.131 |
| Reconnaissance | knn | 0.492 +/- 0.005 | 0.020 +/- 0.005 | 0.050 / 0.048 / 0.049 | 0.740 +/- 0.091 | 0.025 +/- 0.004 |
| Reconnaissance | maha | 0.348 +/- 0.005 | 0.008 +/- 0.002 | 0.050 / 0.056 / 0.050 | 0.740 +/- 0.091 | 0.013 +/- 0.006 |
| Worms | msp | 0.634 +/- 0.015 | 0.046 +/- 0.028 | 0.050 / 0.042 / 0.064 | 0.994 +/- 0.000 | 0.046 +/- 0.028 |
| Worms | entropy | 0.674 +/- 0.013 | 0.036 +/- 0.026 | 0.049 / 0.049 / 0.039 | 0.994 +/- 0.000 | 0.048 +/- 0.029 |
| Worms | knn | 0.632 +/- 0.008 | 0.142 +/- 0.030 | 0.050 / 0.050 / 0.064 | 1.000 +/- 0.000 | 0.138 +/- 0.034 |
| Worms | maha | 0.510 +/- 0.003 | 0.055 +/- 0.008 | 0.050 / 0.054 / 0.056 | 0.994 +/- 0.000 | 0.058 +/- 0.004 |
| Shellcode | msp | 0.817 +/- 0.003 | 0.244 +/- 0.057 | 0.050 / 0.046 / 0.061 | 0.953 +/- 0.013 | 0.244 +/- 0.057 |
| Shellcode | entropy | 0.882 +/- 0.004 | 0.170 +/- 0.057 | 0.049 / 0.040 / 0.024 | 0.935 +/- 0.017 | 0.355 +/- 0.069 |
| Shellcode | knn | 0.388 +/- 0.007 | 0.009 +/- 0.003 | 0.050 / 0.047 / 0.059 | 0.930 +/- 0.015 | 0.010 +/- 0.004 |
| Shellcode | maha | 0.307 +/- 0.005 | 0.007 +/- 0.001 | 0.050 / 0.048 / 0.053 | 0.928 +/- 0.017 | 0.008 +/- 0.005 |
| Overlap-Group-1 (all three) | msp | 0.804 +/- 0.005 | 0.372 +/- 0.111 | 0.050 / 0.048 / 0.040 | 0.953 +/- 0.010 | 0.372 +/- 0.111 |
| Overlap-Group-1 (all three) | entropy | 0.816 +/- 0.003 | 0.370 +/- 0.130 | 0.050 / 0.050 / 0.040 | 0.954 +/- 0.012 | 0.372 +/- 0.128 |
| Overlap-Group-1 (all three) | knn | 0.649 +/- 0.009 | 0.127 +/- 0.051 | 0.050 / 0.053 / 0.053 | 0.955 +/- 0.007 | 0.089 +/- 0.043 |
| Overlap-Group-1 (all three) | maha | 0.516 +/- 0.003 | 0.094 +/- 0.037 | 0.050 / 0.058 / 0.062 | 0.960 +/- 0.006 | 0.063 +/- 0.037 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | Generic | Reconnaissance | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msp | 358 of 1456 | 7 of 171 | 437 of 7590 | 319 of 4810 | 137 of 3418 | 107 of 2469 | 218 of 1694 | 44 of 438 | 38 of 345 | 1937 of 33832 | 0.103 |
| entropy | 254 of 1456 | 4 of 171 | 262 of 7590 | 223 of 4810 | 103 of 3418 | 115 of 2469 | 205 of 1694 | 89 of 438 | 60 of 345 | 307 of 33832 | 0.163 |
| knn | 16 of 1456 | 24 of 171 | 690 of 7590 | 317 of 4810 | 377 of 3418 | 42 of 2469 | 195 of 1694 | 73 of 438 | 62 of 345 | 1626 of 33832 | 0.012 |
| maha | 9 of 1456 | 10 of 171 | 283 of 7590 | 285 of 4810 | 35 of 3418 | 23 of 2469 | 105 of 1694 | 12 of 438 | 10 of 345 | 2123 of 33832 | 0.007 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| msp | 0.289 +/- 0.012 | 0.311 +/- 0.014 | 0.254 +/- 0.012 | 0.057 +/- 0.013 | 0.879 +/- 0.023 | 0.955 +/- 0.009 | 0.224 +/- 0.038 |
| entropy | 0.289 +/- 0.012 | 0.291 +/- 0.012 | 0.282 +/- 0.011 | 0.009 +/- 0.004 | 0.976 +/- 0.009 | 0.941 +/- 0.012 | 0.159 +/- 0.047 |
| knn | 0.289 +/- 0.012 | 0.326 +/- 0.008 | 0.278 +/- 0.013 | 0.048 +/- 0.013 | 0.962 +/- 0.007 | 0.939 +/- 0.013 | 0.024 +/- 0.006 |
| maha | 0.289 +/- 0.012 | 0.341 +/- 0.009 | 0.278 +/- 0.013 | 0.063 +/- 0.009 | 0.962 +/- 0.006 | 0.936 +/- 0.013 | 0.012 +/- 0.001 |

#### distance (48f, mean over seeds 42-46)

Baseline for the verdict: `msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| msp | 0.774 | 0.234 | +0.000 | 0 of 5 | Exploits (0.675) | 0.833 +/- 0.006 | 0.334 +/- 0.037 | 0.334 +/- 0.037 | no |
| entropy | 0.811 | 0.283 | +0.049 | 5 of 5 | Exploits (0.702) | 0.881 +/- 0.007 | 0.294 +/- 0.072 | 0.447 +/- 0.081 | no |
| knn | 0.571 | 0.156 | -0.078 | 0 of 5 | Shellcode (0.288) | 0.312 +/- 0.007 | 0.027 +/- 0.004 | 0.022 +/- 0.007 | no |
| maha | 0.469 | 0.089 | -0.145 | 0 of 5 | Shellcode (0.283) | 0.303 +/- 0.004 | 0.015 +/- 0.005 | 0.011 +/- 0.006 | no |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | msp | 0.833 +/- 0.006 | 0.334 +/- 0.037 | 0.050 / 0.044 / 0.050 | 0.991 +/- 0.003 | 0.334 +/- 0.037 |
| Worms + Shellcode | entropy | 0.881 +/- 0.007 | 0.294 +/- 0.072 | 0.050 / 0.048 / 0.029 | 0.987 +/- 0.004 | 0.447 +/- 0.081 |
| Worms + Shellcode | knn | 0.312 +/- 0.007 | 0.027 +/- 0.004 | 0.050 / 0.052 / 0.060 | 0.982 +/- 0.005 | 0.022 +/- 0.007 |
| Worms + Shellcode | maha | 0.303 +/- 0.004 | 0.015 +/- 0.005 | 0.050 / 0.065 / 0.075 | 0.982 +/- 0.005 | 0.011 +/- 0.006 |
| Analysis | msp | 0.882 +/- 0.016 | 0.381 +/- 0.152 | 0.050 / 0.048 / 0.039 | 0.845 +/- 0.003 | 0.382 +/- 0.152 |
| Analysis | entropy | 0.910 +/- 0.009 | 0.444 +/- 0.147 | 0.050 / 0.052 / 0.030 | 0.841 +/- 0.005 | 0.529 +/- 0.183 |
| Analysis | knn | 0.611 +/- 0.013 | 0.134 +/- 0.023 | 0.050 / 0.050 / 0.059 | 0.866 +/- 0.002 | 0.090 +/- 0.029 |
| Analysis | maha | 0.407 +/- 0.007 | 0.077 +/- 0.009 | 0.050 / 0.064 / 0.077 | 0.899 +/- 0.002 | 0.043 +/- 0.018 |
| Backdoor | msp | 0.901 +/- 0.012 | 0.419 +/- 0.180 | 0.050 / 0.045 / 0.043 | 0.998 +/- 0.001 | 0.419 +/- 0.180 |
| Backdoor | entropy | 0.933 +/- 0.006 | 0.510 +/- 0.188 | 0.050 / 0.049 / 0.034 | 0.998 +/- 0.001 | 0.590 +/- 0.192 |
| Backdoor | knn | 0.571 +/- 0.017 | 0.118 +/- 0.027 | 0.050 / 0.053 / 0.060 | 0.997 +/- 0.001 | 0.079 +/- 0.039 |
| Backdoor | maha | 0.384 +/- 0.010 | 0.037 +/- 0.010 | 0.050 / 0.066 / 0.075 | 0.996 +/- 0.001 | 0.020 +/- 0.015 |
| DoS | msp | 0.713 +/- 0.007 | 0.168 +/- 0.042 | 0.050 / 0.049 / 0.049 | 0.994 +/- 0.002 | 0.168 +/- 0.042 |
| DoS | entropy | 0.743 +/- 0.008 | 0.212 +/- 0.073 | 0.050 / 0.048 / 0.029 | 0.992 +/- 0.003 | 0.291 +/- 0.052 |
| DoS | knn | 0.588 +/- 0.012 | 0.089 +/- 0.047 | 0.050 / 0.050 / 0.045 | 0.992 +/- 0.002 | 0.091 +/- 0.020 |
| DoS | maha | 0.429 +/- 0.004 | 0.048 +/- 0.016 | 0.050 / 0.064 / 0.053 | 0.992 +/- 0.002 | 0.047 +/- 0.005 |
| Exploits | msp | 0.675 +/- 0.007 | 0.102 +/- 0.030 | 0.050 / 0.053 / 0.064 | 0.970 +/- 0.004 | 0.102 +/- 0.030 |
| Exploits | entropy | 0.702 +/- 0.003 | 0.123 +/- 0.033 | 0.050 / 0.052 / 0.036 | 0.968 +/- 0.005 | 0.197 +/- 0.057 |
| Exploits | knn | 0.733 +/- 0.002 | 0.137 +/- 0.094 | 0.050 / 0.036 / 0.043 | 0.960 +/- 0.004 | 0.218 +/- 0.127 |
| Exploits | maha | 0.606 +/- 0.007 | 0.036 +/- 0.033 | 0.050 / 0.041 / 0.040 | 0.963 +/- 0.007 | 0.072 +/- 0.042 |
| Fuzzers | msp | 0.699 +/- 0.007 | 0.083 +/- 0.017 | 0.050 / 0.053 / 0.051 | 0.238 +/- 0.016 | 0.083 +/- 0.017 |
| Fuzzers | entropy | 0.704 +/- 0.006 | 0.110 +/- 0.029 | 0.050 / 0.062 / 0.049 | 0.240 +/- 0.019 | 0.113 +/- 0.025 |
| Fuzzers | knn | 0.548 +/- 0.010 | 0.072 +/- 0.028 | 0.050 / 0.060 / 0.052 | 0.263 +/- 0.009 | 0.070 +/- 0.014 |
| Fuzzers | maha | 0.500 +/- 0.009 | 0.062 +/- 0.019 | 0.050 / 0.058 / 0.049 | 0.263 +/- 0.006 | 0.065 +/- 0.009 |
| Generic | msp | 0.776 +/- 0.059 | 0.191 +/- 0.100 | 0.050 / 0.050 / 0.063 | 0.892 +/- 0.103 | 0.191 +/- 0.100 |
| Generic | entropy | 0.852 +/- 0.049 | 0.258 +/- 0.131 | 0.050 / 0.048 / 0.038 | 0.890 +/- 0.101 | 0.383 +/- 0.164 |
| Generic | knn | 0.900 +/- 0.003 | 0.666 +/- 0.112 | 0.050 / 0.045 / 0.046 | 0.981 +/- 0.011 | 0.741 +/- 0.069 |
| Generic | maha | 0.805 +/- 0.004 | 0.487 +/- 0.077 | 0.050 / 0.049 / 0.055 | 0.961 +/- 0.018 | 0.515 +/- 0.037 |
| Reconnaissance | msp | 0.792 +/- 0.013 | 0.303 +/- 0.047 | 0.050 / 0.039 / 0.068 | 0.995 +/- 0.002 | 0.303 +/- 0.047 |
| Reconnaissance | entropy | 0.843 +/- 0.011 | 0.482 +/- 0.067 | 0.050 / 0.052 / 0.061 | 0.995 +/- 0.001 | 0.510 +/- 0.045 |
| Reconnaissance | knn | 0.385 +/- 0.007 | 0.033 +/- 0.012 | 0.050 / 0.047 / 0.054 | 0.975 +/- 0.012 | 0.041 +/- 0.007 |
| Reconnaissance | maha | 0.329 +/- 0.003 | 0.012 +/- 0.005 | 0.050 / 0.053 / 0.058 | 0.975 +/- 0.012 | 0.014 +/- 0.004 |
| Worms | msp | 0.676 +/- 0.021 | 0.082 +/- 0.024 | 0.050 / 0.049 / 0.056 | 1.000 +/- 0.000 | 0.082 +/- 0.024 |
| Worms | entropy | 0.715 +/- 0.023 | 0.068 +/- 0.017 | 0.050 / 0.054 / 0.038 | 0.999 +/- 0.003 | 0.099 +/- 0.033 |
| Worms | knn | 0.515 +/- 0.009 | 0.143 +/- 0.035 | 0.050 / 0.055 / 0.066 | 0.998 +/- 0.005 | 0.118 +/- 0.041 |
| Worms | maha | 0.476 +/- 0.003 | 0.028 +/- 0.023 | 0.050 / 0.058 / 0.067 | 0.998 +/- 0.005 | 0.026 +/- 0.020 |
| Shellcode | msp | 0.855 +/- 0.005 | 0.378 +/- 0.058 | 0.050 / 0.045 / 0.048 | 0.989 +/- 0.002 | 0.378 +/- 0.058 |
| Shellcode | entropy | 0.901 +/- 0.007 | 0.340 +/- 0.080 | 0.050 / 0.044 / 0.028 | 0.985 +/- 0.004 | 0.490 +/- 0.077 |
| Shellcode | knn | 0.288 +/- 0.010 | 0.013 +/- 0.001 | 0.050 / 0.050 / 0.059 | 0.978 +/- 0.005 | 0.011 +/- 0.004 |
| Shellcode | maha | 0.283 +/- 0.005 | 0.013 +/- 0.003 | 0.050 / 0.061 / 0.073 | 0.978 +/- 0.005 | 0.009 +/- 0.004 |
| Overlap-Group-1 (all three) | msp | 0.811 +/- 0.004 | 0.423 +/- 0.084 | 0.050 / 0.043 / 0.039 | 0.964 +/- 0.008 | 0.423 +/- 0.084 |
| Overlap-Group-1 (all three) | entropy | 0.821 +/- 0.002 | 0.400 +/- 0.125 | 0.050 / 0.048 / 0.041 | 0.965 +/- 0.010 | 0.416 +/- 0.109 |
| Overlap-Group-1 (all three) | knn | 0.629 +/- 0.012 | 0.143 +/- 0.059 | 0.050 / 0.054 / 0.059 | 0.968 +/- 0.006 | 0.096 +/- 0.041 |
| Overlap-Group-1 (all three) | maha | 0.520 +/- 0.005 | 0.085 +/- 0.033 | 0.050 / 0.070 / 0.073 | 0.974 +/- 0.003 | 0.048 +/- 0.019 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | Generic | Reconnaissance | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| msp | 534 of 1456 | 10 of 171 | 339 of 7590 | 489 of 4810 | 119 of 3418 | 107 of 2469 | 240 of 1694 | 85 of 438 | 79 of 345 | 1294 of 33832 | 0.175 |
| entropy | 472 of 1456 | 6 of 171 | 263 of 7590 | 368 of 4810 | 96 of 3418 | 119 of 2469 | 238 of 1694 | 120 of 438 | 101 of 345 | 270 of 33832 | 0.244 |
| knn | 23 of 1456 | 22 of 171 | 468 of 7590 | 355 of 4810 | 462 of 3418 | 45 of 2469 | 205 of 1694 | 90 of 438 | 86 of 345 | 1587 of 33832 | 0.014 |
| maha | 19 of 1456 | 6 of 171 | 205 of 7590 | 297 of 4810 | 66 of 3418 | 21 of 2469 | 94 of 1694 | 11 of 438 | 8 of 345 | 3394 of 33832 | 0.006 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| msp | 0.298 +/- 0.013 | 0.314 +/- 0.013 | 0.275 +/- 0.016 | 0.038 +/- 0.016 | 0.924 +/- 0.030 | 0.991 +/- 0.003 | 0.334 +/- 0.037 |
| entropy | 0.298 +/- 0.013 | 0.300 +/- 0.013 | 0.292 +/- 0.012 | 0.008 +/- 0.004 | 0.979 +/- 0.009 | 0.987 +/- 0.004 | 0.294 +/- 0.072 |
| knn | 0.298 +/- 0.013 | 0.331 +/- 0.009 | 0.284 +/- 0.014 | 0.047 +/- 0.010 | 0.953 +/- 0.009 | 0.982 +/- 0.005 | 0.027 +/- 0.004 |
| maha | 0.298 +/- 0.013 | 0.387 +/- 0.022 | 0.287 +/- 0.014 | 0.100 +/- 0.021 | 0.963 +/- 0.009 | 0.982 +/- 0.005 | 0.015 +/- 0.005 |

## Source: open_set_boost_oe_40f_48f.md

### Task 4.5: oe

#### oe (40f, mean over seeds 42-46)

Baseline for the verdict: `noP_msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs noP_msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| noP_msp | 0.730 | 0.128 | +0.000 | 0 of 5 | Exploits (0.609) | 0.793 +/- 0.003 | 0.248 +/- 0.052 | 0.248 +/- 0.052 | no |
| noP_entropy | 0.765 | 0.200 | +0.073 | 5 of 5 | Exploits (0.627) | 0.858 +/- 0.006 | 0.462 +/- 0.123 | 0.462 +/- 0.117 | yes |
| oe_pu | 0.842 | 0.179 | +0.051 | 4 of 5 | Fuzzers (0.693) | 0.864 +/- 0.004 | 0.049 +/- 0.006 | 0.240 +/- 0.185 | no |
| oe_msp | 0.754 | 0.195 | +0.067 | 5 of 5 | Worms (0.616) | 0.787 +/- 0.004 | 0.230 +/- 0.047 | 0.247 +/- 0.045 | yes |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | noP_msp | 0.793 +/- 0.003 | 0.248 +/- 0.052 | 0.050 / 0.040 / 0.074 | 0.958 +/- 0.011 | 0.248 +/- 0.052 |
| Worms + Shellcode | noP_entropy | 0.858 +/- 0.006 | 0.462 +/- 0.123 | 0.050 / 0.046 / 0.075 | 0.954 +/- 0.010 | 0.462 +/- 0.117 |
| Worms + Shellcode | oe_pu | 0.864 +/- 0.004 | 0.049 +/- 0.006 | 0.050 / 0.046 / 0.020 | 0.931 +/- 0.016 | 0.240 +/- 0.185 |
| Worms + Shellcode | oe_msp | 0.787 +/- 0.004 | 0.230 +/- 0.047 | 0.050 / 0.042 / 0.067 | 0.952 +/- 0.009 | 0.247 +/- 0.045 |
| Analysis | noP_msp | 0.782 +/- 0.012 | 0.055 +/- 0.022 | 0.050 / 0.043 / 0.067 | 0.858 +/- 0.005 | 0.055 +/- 0.022 |
| Analysis | noP_entropy | 0.852 +/- 0.007 | 0.065 +/- 0.089 | 0.050 / 0.047 / 0.062 | 0.856 +/- 0.012 | 0.091 +/- 0.123 |
| Analysis | oe_pu | 0.937 +/- 0.003 | 0.225 +/- 0.163 | 0.050 / 0.043 / 0.022 | 0.840 +/- 0.008 | 0.758 +/- 0.064 |
| Analysis | oe_msp | 0.863 +/- 0.012 | 0.170 +/- 0.135 | 0.050 / 0.040 / 0.050 | 0.854 +/- 0.005 | 0.280 +/- 0.224 |
| Backdoor | noP_msp | 0.766 +/- 0.009 | 0.081 +/- 0.030 | 0.050 / 0.045 / 0.075 | 0.996 +/- 0.001 | 0.081 +/- 0.030 |
| Backdoor | noP_entropy | 0.829 +/- 0.004 | 0.079 +/- 0.091 | 0.050 / 0.049 / 0.068 | 0.997 +/- 0.001 | 0.097 +/- 0.105 |
| Backdoor | oe_pu | 0.958 +/- 0.001 | 0.342 +/- 0.288 | 0.050 / 0.042 / 0.026 | 0.992 +/- 0.002 | 0.878 +/- 0.082 |
| Backdoor | oe_msp | 0.862 +/- 0.010 | 0.215 +/- 0.105 | 0.050 / 0.041 / 0.058 | 0.995 +/- 0.001 | 0.321 +/- 0.204 |
| DoS | noP_msp | 0.630 +/- 0.008 | 0.090 +/- 0.020 | 0.050 / 0.063 / 0.097 | 0.986 +/- 0.004 | 0.090 +/- 0.020 |
| DoS | noP_entropy | 0.670 +/- 0.007 | 0.158 +/- 0.071 | 0.050 / 0.073 / 0.090 | 0.987 +/- 0.005 | 0.183 +/- 0.085 |
| DoS | oe_pu | 0.854 +/- 0.003 | 0.168 +/- 0.081 | 0.050 / 0.040 / 0.022 | 0.975 +/- 0.003 | 0.519 +/- 0.077 |
| DoS | oe_msp | 0.676 +/- 0.007 | 0.133 +/- 0.035 | 0.050 / 0.059 / 0.079 | 0.982 +/- 0.004 | 0.159 +/- 0.046 |
| Exploits | noP_msp | 0.609 +/- 0.006 | 0.102 +/- 0.076 | 0.050 / 0.079 / 0.115 | 0.961 +/- 0.010 | 0.102 +/- 0.076 |
| Exploits | noP_entropy | 0.627 +/- 0.004 | 0.146 +/- 0.072 | 0.050 / 0.088 / 0.113 | 0.964 +/- 0.008 | 0.150 +/- 0.073 |
| Exploits | oe_pu | 0.913 +/- 0.004 | 0.405 +/- 0.276 | 0.050 / 0.100 / 0.052 | 0.952 +/- 0.021 | 0.585 +/- 0.251 |
| Exploits | oe_msp | 0.656 +/- 0.010 | 0.134 +/- 0.074 | 0.050 / 0.084 / 0.094 | 0.960 +/- 0.008 | 0.156 +/- 0.113 |
| Fuzzers | noP_msp | 0.689 +/- 0.010 | 0.085 +/- 0.035 | 0.050 / 0.049 / 0.067 | 0.265 +/- 0.008 | 0.085 +/- 0.035 |
| Fuzzers | noP_entropy | 0.692 +/- 0.011 | 0.104 +/- 0.051 | 0.050 / 0.049 / 0.073 | 0.276 +/- 0.018 | 0.090 +/- 0.034 |
| Fuzzers | oe_pu | 0.693 +/- 0.005 | 0.039 +/- 0.011 | 0.050 / 0.054 / 0.022 | 0.230 +/- 0.013 | 0.127 +/- 0.038 |
| Fuzzers | oe_msp | 0.686 +/- 0.007 | 0.092 +/- 0.014 | 0.050 / 0.053 / 0.070 | 0.264 +/- 0.010 | 0.089 +/- 0.025 |
| Generic | noP_msp | 0.835 +/- 0.038 | 0.168 +/- 0.228 | 0.050 / 0.060 / 0.087 | 0.995 +/- 0.002 | 0.169 +/- 0.230 |
| Generic | noP_entropy | 0.850 +/- 0.037 | 0.317 +/- 0.309 | 0.050 / 0.061 / 0.093 | 0.995 +/- 0.002 | 0.248 +/- 0.270 |
| Generic | oe_pu | 0.758 +/- 0.026 | 0.108 +/- 0.124 | 0.050 / 0.056 / 0.103 | 0.993 +/- 0.004 | 0.091 +/- 0.083 |
| Generic | oe_msp | 0.824 +/- 0.044 | 0.364 +/- 0.237 | 0.050 / 0.057 / 0.094 | 0.992 +/- 0.008 | 0.348 +/- 0.230 |
| Reconnaissance | noP_msp | 0.831 +/- 0.014 | 0.220 +/- 0.079 | 0.050 / 0.050 / 0.074 | 0.665 +/- 0.110 | 0.220 +/- 0.079 |
| Reconnaissance | noP_entropy | 0.839 +/- 0.015 | 0.342 +/- 0.115 | 0.050 / 0.058 / 0.090 | 0.753 +/- 0.130 | 0.283 +/- 0.100 |
| Reconnaissance | oe_pu | 0.721 +/- 0.011 | 0.195 +/- 0.261 | 0.050 / 0.064 / 0.141 | 0.677 +/- 0.185 | 0.013 +/- 0.018 |
| Reconnaissance | oe_msp | 0.798 +/- 0.010 | 0.369 +/- 0.072 | 0.050 / 0.059 / 0.093 | 0.798 +/- 0.103 | 0.330 +/- 0.069 |
| Worms | noP_msp | 0.613 +/- 0.017 | 0.068 +/- 0.036 | 0.050 / 0.042 / 0.076 | 0.994 +/- 0.000 | 0.068 +/- 0.036 |
| Worms | noP_entropy | 0.640 +/- 0.020 | 0.095 +/- 0.014 | 0.050 / 0.045 / 0.072 | 0.994 +/- 0.000 | 0.097 +/- 0.016 |
| Worms | oe_pu | 0.883 +/- 0.002 | 0.085 +/- 0.013 | 0.050 / 0.057 / 0.028 | 0.994 +/- 0.000 | 0.332 +/- 0.287 |
| Worms | oe_msp | 0.616 +/- 0.022 | 0.030 +/- 0.018 | 0.050 / 0.046 / 0.071 | 0.994 +/- 0.000 | 0.039 +/- 0.011 |
| Shellcode | noP_msp | 0.816 +/- 0.004 | 0.282 +/- 0.064 | 0.050 / 0.040 / 0.075 | 0.955 +/- 0.009 | 0.282 +/- 0.064 |
| Shellcode | noP_entropy | 0.882 +/- 0.007 | 0.498 +/- 0.147 | 0.050 / 0.044 / 0.074 | 0.949 +/- 0.011 | 0.503 +/- 0.134 |
| Shellcode | oe_pu | 0.863 +/- 0.006 | 0.043 +/- 0.010 | 0.050 / 0.044 / 0.021 | 0.925 +/- 0.016 | 0.230 +/- 0.173 |
| Shellcode | oe_msp | 0.806 +/- 0.007 | 0.243 +/- 0.068 | 0.050 / 0.042 / 0.067 | 0.948 +/- 0.011 | 0.266 +/- 0.061 |
| Overlap-Group-1 (all three) | noP_msp | 0.735 +/- 0.016 | 0.211 +/- 0.132 | 0.050 / 0.062 / 0.077 | 0.956 +/- 0.009 | 0.211 +/- 0.132 |
| Overlap-Group-1 (all three) | noP_entropy | 0.705 +/- 0.008 | 0.072 +/- 0.026 | 0.050 / 0.059 / 0.077 | 0.958 +/- 0.012 | 0.071 +/- 0.023 |
| Overlap-Group-1 (all three) | oe_pu | 0.904 +/- 0.002 | 0.481 +/- 0.164 | 0.049 / 0.062 / 0.031 | 0.950 +/- 0.010 | 0.657 +/- 0.048 |
| Overlap-Group-1 (all three) | oe_msp | 0.795 +/- 0.004 | 0.470 +/- 0.091 | 0.050 / 0.064 / 0.060 | 0.954 +/- 0.009 | 0.508 +/- 0.049 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|
| noP_msp | 393 of 1456 | 10 of 171 | 388 of 7590 | 381 of 4810 | 165 of 1694 | 17 of 438 | 11 of 345 | 2641 of 33832 | 0.103 |
| noP_entropy | 733 of 1456 | 19 of 171 | 527 of 7590 | 405 of 4810 | 209 of 1694 | 32 of 438 | 25 of 345 | 2447 of 33832 | 0.174 |
| oe_pu | 69 of 1456 | 11 of 171 | 566 of 7590 | 112 of 4810 | 152 of 1694 | 53 of 438 | 45 of 345 | 57 of 33832 | 0.078 |
| oe_msp | 368 of 1456 | 7 of 171 | 441 of 7590 | 342 of 4810 | 205 of 1694 | 32 of 438 | 31 of 345 | 2191 of 33832 | 0.108 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| noP_msp | 0.288 +/- 0.013 | 0.320 +/- 0.020 | 0.242 +/- 0.014 | 0.078 +/- 0.026 | 0.841 +/- 0.045 | 0.958 +/- 0.011 | 0.248 +/- 0.052 |
| noP_entropy | 0.288 +/- 0.013 | 0.315 +/- 0.019 | 0.242 +/- 0.013 | 0.072 +/- 0.025 | 0.841 +/- 0.045 | 0.954 +/- 0.010 | 0.462 +/- 0.123 |
| oe_pu | 0.288 +/- 0.013 | 0.289 +/- 0.013 | 0.287 +/- 0.012 | 0.002 +/- 0.000 | 0.995 +/- 0.001 | 0.931 +/- 0.016 | 0.049 +/- 0.006 |
| oe_msp | 0.288 +/- 0.013 | 0.314 +/- 0.019 | 0.249 +/- 0.014 | 0.065 +/- 0.025 | 0.864 +/- 0.045 | 0.952 +/- 0.009 | 0.230 +/- 0.047 |

##### Diagnostics (mean over seeds, per held-out set)

| held-out set | known_macro_recall_noP | known_macro_recall_oe | oe_predicts_unknown_on_known_test |
|---|---|---|---|
| Worms + Shellcode | 0.747 | 0.738 | 0.006 |
| Analysis | 0.712 | 0.700 | 0.007 |
| Backdoor | 0.709 | 0.694 | 0.007 |
| DoS | 0.755 | 0.746 | 0.006 |
| Exploits | 0.795 | 0.777 | 0.003 |
| Fuzzers | 0.758 | 0.751 | 0.007 |
| Generic | 0.770 | 0.714 | 0.174 |
| Reconnaissance | 0.762 | 0.708 | 0.171 |
| Worms | 0.749 | 0.741 | 0.006 |
| Shellcode | 0.705 | 0.699 | 0.006 |
| Overlap-Group-1 (all three) | 0.755 | 0.729 | 0.023 |

#### oe (48f, mean over seeds 42-46)

Baseline for the verdict: `noP_msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs noP_msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| noP_msp | 0.754 | 0.209 | +0.000 | 0 of 5 | Exploits (0.591) | 0.824 +/- 0.005 | 0.416 +/- 0.054 | 0.416 +/- 0.054 | no |
| noP_entropy | 0.782 | 0.318 | +0.109 | 5 of 5 | Exploits (0.606) | 0.867 +/- 0.005 | 0.598 +/- 0.036 | 0.601 +/- 0.056 | yes |
| oe_pu | 0.868 | 0.239 | +0.030 | 3 of 5 | Reconnaissance (0.700) | 0.914 +/- 0.006 | 0.101 +/- 0.017 | 0.546 +/- 0.187 | no |
| oe_msp | 0.752 | 0.212 | +0.003 | 3 of 5 | Exploits (0.648) | 0.832 +/- 0.008 | 0.390 +/- 0.037 | 0.431 +/- 0.039 | no |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | noP_msp | 0.824 +/- 0.005 | 0.416 +/- 0.054 | 0.050 / 0.041 / 0.080 | 0.991 +/- 0.001 | 0.416 +/- 0.054 |
| Worms + Shellcode | noP_entropy | 0.867 +/- 0.005 | 0.598 +/- 0.036 | 0.050 / 0.046 / 0.075 | 0.993 +/- 0.001 | 0.601 +/- 0.056 |
| Worms + Shellcode | oe_pu | 0.914 +/- 0.006 | 0.101 +/- 0.017 | 0.050 / 0.044 / 0.021 | 0.979 +/- 0.005 | 0.546 +/- 0.187 |
| Worms + Shellcode | oe_msp | 0.832 +/- 0.008 | 0.390 +/- 0.037 | 0.050 / 0.045 / 0.060 | 0.990 +/- 0.003 | 0.431 +/- 0.039 |
| Analysis | noP_msp | 0.805 +/- 0.016 | 0.098 +/- 0.043 | 0.050 / 0.040 / 0.068 | 0.848 +/- 0.004 | 0.098 +/- 0.043 |
| Analysis | noP_entropy | 0.866 +/- 0.013 | 0.225 +/- 0.155 | 0.050 / 0.047 / 0.061 | 0.850 +/- 0.004 | 0.330 +/- 0.274 |
| Analysis | oe_pu | 0.937 +/- 0.004 | 0.228 +/- 0.211 | 0.050 / 0.042 / 0.020 | 0.839 +/- 0.003 | 0.758 +/- 0.050 |
| Analysis | oe_msp | 0.869 +/- 0.017 | 0.300 +/- 0.139 | 0.050 / 0.042 / 0.039 | 0.845 +/- 0.004 | 0.477 +/- 0.156 |
| Backdoor | noP_msp | 0.801 +/- 0.011 | 0.126 +/- 0.036 | 0.050 / 0.043 / 0.074 | 0.999 +/- 0.001 | 0.126 +/- 0.036 |
| Backdoor | noP_entropy | 0.861 +/- 0.008 | 0.265 +/- 0.223 | 0.050 / 0.045 / 0.071 | 0.999 +/- 0.001 | 0.328 +/- 0.294 |
| Backdoor | oe_pu | 0.962 +/- 0.003 | 0.326 +/- 0.291 | 0.050 / 0.039 / 0.023 | 0.997 +/- 0.000 | 0.885 +/- 0.084 |
| Backdoor | oe_msp | 0.891 +/- 0.011 | 0.347 +/- 0.167 | 0.050 / 0.037 / 0.047 | 0.998 +/- 0.001 | 0.509 +/- 0.196 |
| DoS | noP_msp | 0.641 +/- 0.010 | 0.090 +/- 0.028 | 0.050 / 0.059 / 0.092 | 0.995 +/- 0.002 | 0.090 +/- 0.028 |
| DoS | noP_entropy | 0.676 +/- 0.011 | 0.200 +/- 0.083 | 0.050 / 0.061 / 0.073 | 0.996 +/- 0.002 | 0.243 +/- 0.105 |
| DoS | oe_pu | 0.880 +/- 0.006 | 0.193 +/- 0.087 | 0.050 / 0.040 / 0.019 | 0.992 +/- 0.001 | 0.557 +/- 0.101 |
| DoS | oe_msp | 0.695 +/- 0.008 | 0.154 +/- 0.041 | 0.050 / 0.056 / 0.063 | 0.994 +/- 0.002 | 0.204 +/- 0.064 |
| Exploits | noP_msp | 0.591 +/- 0.004 | 0.076 +/- 0.057 | 0.050 / 0.074 / 0.115 | 0.972 +/- 0.008 | 0.076 +/- 0.057 |
| Exploits | noP_entropy | 0.606 +/- 0.003 | 0.136 +/- 0.044 | 0.050 / 0.082 / 0.122 | 0.979 +/- 0.006 | 0.131 +/- 0.044 |
| Exploits | oe_pu | 0.921 +/- 0.002 | 0.392 +/- 0.308 | 0.050 / 0.101 / 0.053 | 0.968 +/- 0.016 | 0.634 +/- 0.218 |
| Exploits | oe_msp | 0.648 +/- 0.010 | 0.117 +/- 0.071 | 0.050 / 0.082 / 0.093 | 0.970 +/- 0.006 | 0.138 +/- 0.095 |
| Fuzzers | noP_msp | 0.699 +/- 0.007 | 0.100 +/- 0.028 | 0.050 / 0.053 / 0.067 | 0.256 +/- 0.009 | 0.101 +/- 0.028 |
| Fuzzers | noP_entropy | 0.701 +/- 0.007 | 0.125 +/- 0.030 | 0.050 / 0.055 / 0.075 | 0.268 +/- 0.012 | 0.111 +/- 0.032 |
| Fuzzers | oe_pu | 0.709 +/- 0.007 | 0.035 +/- 0.010 | 0.050 / 0.055 / 0.021 | 0.213 +/- 0.013 | 0.128 +/- 0.032 |
| Fuzzers | oe_msp | 0.695 +/- 0.006 | 0.080 +/- 0.013 | 0.050 / 0.051 / 0.054 | 0.240 +/- 0.008 | 0.104 +/- 0.032 |
| Generic | noP_msp | 0.932 +/- 0.013 | 0.656 +/- 0.225 | 0.050 / 0.068 / 0.078 | 0.881 +/- 0.204 | 0.656 +/- 0.225 |
| Generic | noP_entropy | 0.939 +/- 0.008 | 0.760 +/- 0.090 | 0.050 / 0.066 / 0.086 | 0.942 +/- 0.074 | 0.734 +/- 0.121 |
| Generic | oe_pu | 0.873 +/- 0.024 | 0.632 +/- 0.165 | 0.050 / 0.057 / 0.113 | 0.885 +/- 0.173 | 0.555 +/- 0.183 |
| Generic | oe_msp | 0.666 +/- 0.055 | 0.084 +/- 0.079 | 0.050 / 0.052 / 0.079 | 0.754 +/- 0.215 | 0.087 +/- 0.087 |
| Reconnaissance | noP_msp | 0.853 +/- 0.012 | 0.210 +/- 0.057 | 0.050 / 0.054 / 0.065 | 0.952 +/- 0.006 | 0.210 +/- 0.057 |
| Reconnaissance | noP_entropy | 0.867 +/- 0.012 | 0.373 +/- 0.042 | 0.050 / 0.057 / 0.079 | 0.962 +/- 0.005 | 0.336 +/- 0.048 |
| Reconnaissance | oe_pu | 0.700 +/- 0.011 | 0.153 +/- 0.205 | 0.050 / 0.065 / 0.148 | 0.950 +/- 0.037 | 0.004 +/- 0.002 |
| Reconnaissance | oe_msp | 0.789 +/- 0.016 | 0.311 +/- 0.072 | 0.050 / 0.057 / 0.086 | 0.958 +/- 0.011 | 0.280 +/- 0.059 |
| Worms | noP_msp | 0.620 +/- 0.012 | 0.085 +/- 0.019 | 0.050 / 0.038 / 0.078 | 0.995 +/- 0.003 | 0.085 +/- 0.019 |
| Worms | noP_entropy | 0.635 +/- 0.012 | 0.138 +/- 0.013 | 0.050 / 0.047 / 0.078 | 0.999 +/- 0.003 | 0.139 +/- 0.014 |
| Worms | oe_pu | 0.911 +/- 0.003 | 0.090 +/- 0.035 | 0.050 / 0.054 / 0.025 | 0.999 +/- 0.003 | 0.506 +/- 0.238 |
| Worms | oe_msp | 0.658 +/- 0.022 | 0.074 +/- 0.027 | 0.050 / 0.042 / 0.062 | 0.993 +/- 0.005 | 0.084 +/- 0.025 |
| Shellcode | noP_msp | 0.844 +/- 0.003 | 0.440 +/- 0.059 | 0.050 / 0.040 / 0.080 | 0.990 +/- 0.002 | 0.440 +/- 0.059 |
| Shellcode | noP_entropy | 0.890 +/- 0.004 | 0.637 +/- 0.050 | 0.050 / 0.046 / 0.076 | 0.993 +/- 0.002 | 0.639 +/- 0.070 |
| Shellcode | oe_pu | 0.915 +/- 0.005 | 0.099 +/- 0.013 | 0.050 / 0.043 / 0.022 | 0.979 +/- 0.005 | 0.543 +/- 0.181 |
| Shellcode | oe_msp | 0.853 +/- 0.008 | 0.444 +/- 0.054 | 0.050 / 0.043 / 0.061 | 0.991 +/- 0.002 | 0.487 +/- 0.046 |
| Overlap-Group-1 (all three) | noP_msp | 0.740 +/- 0.014 | 0.279 +/- 0.123 | 0.050 / 0.060 / 0.080 | 0.966 +/- 0.007 | 0.279 +/- 0.123 |
| Overlap-Group-1 (all three) | noP_entropy | 0.721 +/- 0.010 | 0.152 +/- 0.107 | 0.050 / 0.061 / 0.094 | 0.970 +/- 0.008 | 0.124 +/- 0.111 |
| Overlap-Group-1 (all three) | oe_pu | 0.920 +/- 0.001 | 0.489 +/- 0.185 | 0.050 / 0.061 / 0.029 | 0.962 +/- 0.007 | 0.693 +/- 0.063 |
| Overlap-Group-1 (all three) | oe_msp | 0.803 +/- 0.005 | 0.470 +/- 0.063 | 0.050 / 0.064 / 0.065 | 0.965 +/- 0.007 | 0.491 +/- 0.058 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|
| noP_msp | 662 of 1456 | 15 of 171 | 328 of 7590 | 750 of 4810 | 216 of 1694 | 50 of 438 | 47 of 345 | 2526 of 33832 | 0.152 |
| noP_entropy | 948 of 1456 | 24 of 171 | 463 of 7590 | 829 of 4810 | 254 of 1694 | 93 of 438 | 69 of 345 | 1926 of 33832 | 0.214 |
| oe_pu | 153 of 1456 | 11 of 171 | 573 of 7590 | 114 of 4810 | 169 of 1694 | 76 of 438 | 64 of 345 | 32 of 33832 | 0.153 |
| oe_msp | 621 of 1456 | 14 of 171 | 397 of 7590 | 545 of 4810 | 255 of 1694 | 88 of 438 | 85 of 345 | 1547 of 33832 | 0.186 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| noP_msp | 0.297 +/- 0.012 | 0.329 +/- 0.017 | 0.255 +/- 0.016 | 0.075 +/- 0.024 | 0.858 +/- 0.042 | 0.991 +/- 0.001 | 0.416 +/- 0.054 |
| noP_entropy | 0.297 +/- 0.012 | 0.319 +/- 0.014 | 0.262 +/- 0.011 | 0.057 +/- 0.009 | 0.884 +/- 0.015 | 0.993 +/- 0.001 | 0.598 +/- 0.036 |
| oe_pu | 0.297 +/- 0.012 | 0.297 +/- 0.012 | 0.296 +/- 0.012 | 0.001 +/- 0.000 | 0.997 +/- 0.001 | 0.979 +/- 0.005 | 0.101 +/- 0.017 |
| oe_msp | 0.297 +/- 0.012 | 0.316 +/- 0.016 | 0.270 +/- 0.013 | 0.046 +/- 0.016 | 0.911 +/- 0.026 | 0.990 +/- 0.003 | 0.390 +/- 0.037 |

##### Diagnostics (mean over seeds, per held-out set)

| held-out set | known_macro_recall_noP | known_macro_recall_oe | oe_predicts_unknown_on_known_test |
|---|---|---|---|
| Worms + Shellcode | 0.744 | 0.736 | 0.006 |
| Analysis | 0.743 | 0.735 | 0.007 |
| Backdoor | 0.744 | 0.735 | 0.007 |
| DoS | 0.794 | 0.777 | 0.006 |
| Exploits | 0.820 | 0.800 | 0.002 |
| Fuzzers | 0.820 | 0.810 | 0.007 |
| Generic | 0.823 | 0.758 | 0.189 |
| Reconnaissance | 0.814 | 0.748 | 0.186 |
| Worms | 0.763 | 0.753 | 0.006 |
| Shellcode | 0.731 | 0.724 | 0.007 |
| Overlap-Group-1 (all three) | 0.791 | 0.776 | 0.017 |

## Source: open_set_boost_combo_40f_48f.md

### Task 4.5: combo

#### combo (40f, mean over seeds 42-46)

Baseline for the verdict: `noP_msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs noP_msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| noP_msp | 0.730 | 0.128 | +0.000 | 0 of 5 | Exploits (0.609) | 0.793 +/- 0.003 | 0.248 +/- 0.052 | 0.248 +/- 0.052 | no |
| noP_entropy | 0.765 | 0.200 | +0.073 | 5 of 5 | Exploits (0.627) | 0.858 +/- 0.006 | 0.462 +/- 0.123 | 0.462 +/- 0.117 | yes |
| ens_mi | 0.702 | 0.155 | +0.027 | 5 of 5 | Backdoor (0.575) | 0.752 +/- 0.009 | 0.113 +/- 0.051 | 0.126 +/- 0.053 | no |
| oe_pu | 0.842 | 0.179 | +0.051 | 4 of 5 | Fuzzers (0.693) | 0.864 +/- 0.004 | 0.049 +/- 0.006 | 0.240 +/- 0.185 | no |
| combo | 0.794 | 0.268 | +0.141 | 5 of 5 | Fuzzers (0.688) | 0.848 +/- 0.009 | 0.236 +/- 0.133 | 0.270 +/- 0.113 | yes |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | noP_msp | 0.793 +/- 0.003 | 0.248 +/- 0.052 | 0.050 / 0.040 / 0.074 | 0.958 +/- 0.011 | 0.248 +/- 0.052 |
| Worms + Shellcode | noP_entropy | 0.858 +/- 0.006 | 0.462 +/- 0.123 | 0.050 / 0.046 / 0.075 | 0.954 +/- 0.010 | 0.462 +/- 0.117 |
| Worms + Shellcode | ens_mi | 0.752 +/- 0.009 | 0.113 +/- 0.051 | 0.050 / 0.046 / 0.068 | 0.943 +/- 0.011 | 0.126 +/- 0.053 |
| Worms + Shellcode | oe_pu | 0.864 +/- 0.004 | 0.049 +/- 0.006 | 0.050 / 0.046 / 0.020 | 0.931 +/- 0.016 | 0.240 +/- 0.185 |
| Worms + Shellcode | combo | 0.848 +/- 0.009 | 0.236 +/- 0.133 | 0.050 / 0.054 / 0.065 | 0.950 +/- 0.012 | 0.270 +/- 0.113 |
| Analysis | noP_msp | 0.782 +/- 0.012 | 0.055 +/- 0.022 | 0.050 / 0.043 / 0.067 | 0.858 +/- 0.005 | 0.055 +/- 0.022 |
| Analysis | noP_entropy | 0.852 +/- 0.007 | 0.065 +/- 0.089 | 0.050 / 0.047 / 0.062 | 0.856 +/- 0.012 | 0.091 +/- 0.123 |
| Analysis | ens_mi | 0.577 +/- 0.015 | 0.072 +/- 0.024 | 0.050 / 0.048 / 0.064 | 0.882 +/- 0.011 | 0.075 +/- 0.024 |
| Analysis | oe_pu | 0.937 +/- 0.003 | 0.225 +/- 0.163 | 0.050 / 0.043 / 0.022 | 0.840 +/- 0.008 | 0.758 +/- 0.064 |
| Analysis | combo | 0.749 +/- 0.037 | 0.097 +/- 0.044 | 0.050 / 0.052 / 0.062 | 0.885 +/- 0.015 | 0.102 +/- 0.040 |
| Backdoor | noP_msp | 0.766 +/- 0.009 | 0.081 +/- 0.030 | 0.050 / 0.045 / 0.075 | 0.996 +/- 0.001 | 0.081 +/- 0.030 |
| Backdoor | noP_entropy | 0.829 +/- 0.004 | 0.079 +/- 0.091 | 0.050 / 0.049 / 0.068 | 0.997 +/- 0.001 | 0.097 +/- 0.105 |
| Backdoor | ens_mi | 0.575 +/- 0.016 | 0.081 +/- 0.015 | 0.050 / 0.050 / 0.064 | 0.996 +/- 0.001 | 0.086 +/- 0.018 |
| Backdoor | oe_pu | 0.958 +/- 0.001 | 0.342 +/- 0.288 | 0.050 / 0.042 / 0.026 | 0.992 +/- 0.002 | 0.878 +/- 0.082 |
| Backdoor | combo | 0.763 +/- 0.037 | 0.151 +/- 0.047 | 0.050 / 0.055 / 0.063 | 0.996 +/- 0.002 | 0.170 +/- 0.053 |
| DoS | noP_msp | 0.630 +/- 0.008 | 0.090 +/- 0.020 | 0.050 / 0.063 / 0.097 | 0.986 +/- 0.004 | 0.090 +/- 0.020 |
| DoS | noP_entropy | 0.670 +/- 0.007 | 0.158 +/- 0.071 | 0.050 / 0.073 / 0.090 | 0.987 +/- 0.005 | 0.183 +/- 0.085 |
| DoS | ens_mi | 0.621 +/- 0.010 | 0.125 +/- 0.030 | 0.050 / 0.075 / 0.091 | 0.987 +/- 0.005 | 0.130 +/- 0.030 |
| DoS | oe_pu | 0.854 +/- 0.003 | 0.168 +/- 0.081 | 0.050 / 0.040 / 0.022 | 0.975 +/- 0.003 | 0.519 +/- 0.077 |
| DoS | combo | 0.749 +/- 0.015 | 0.191 +/- 0.051 | 0.050 / 0.068 / 0.081 | 0.987 +/- 0.003 | 0.224 +/- 0.065 |
| Exploits | noP_msp | 0.609 +/- 0.006 | 0.102 +/- 0.076 | 0.050 / 0.079 / 0.115 | 0.961 +/- 0.010 | 0.102 +/- 0.076 |
| Exploits | noP_entropy | 0.627 +/- 0.004 | 0.146 +/- 0.072 | 0.050 / 0.088 / 0.113 | 0.964 +/- 0.008 | 0.150 +/- 0.073 |
| Exploits | ens_mi | 0.727 +/- 0.007 | 0.267 +/- 0.171 | 0.050 / 0.085 / 0.114 | 0.972 +/- 0.009 | 0.269 +/- 0.170 |
| Exploits | oe_pu | 0.913 +/- 0.004 | 0.405 +/- 0.276 | 0.050 / 0.100 / 0.052 | 0.952 +/- 0.021 | 0.585 +/- 0.251 |
| Exploits | combo | 0.842 +/- 0.010 | 0.420 +/- 0.209 | 0.050 / 0.092 / 0.104 | 0.977 +/- 0.008 | 0.438 +/- 0.227 |
| Fuzzers | noP_msp | 0.689 +/- 0.010 | 0.085 +/- 0.035 | 0.050 / 0.049 / 0.067 | 0.265 +/- 0.008 | 0.085 +/- 0.035 |
| Fuzzers | noP_entropy | 0.692 +/- 0.011 | 0.104 +/- 0.051 | 0.050 / 0.049 / 0.073 | 0.276 +/- 0.018 | 0.090 +/- 0.034 |
| Fuzzers | ens_mi | 0.681 +/- 0.010 | 0.087 +/- 0.051 | 0.050 / 0.050 / 0.060 | 0.280 +/- 0.021 | 0.097 +/- 0.037 |
| Fuzzers | oe_pu | 0.693 +/- 0.005 | 0.039 +/- 0.011 | 0.050 / 0.054 / 0.022 | 0.230 +/- 0.013 | 0.127 +/- 0.038 |
| Fuzzers | combo | 0.688 +/- 0.008 | 0.094 +/- 0.031 | 0.050 / 0.059 / 0.051 | 0.275 +/- 0.010 | 0.118 +/- 0.031 |
| Generic | noP_msp | 0.835 +/- 0.038 | 0.168 +/- 0.228 | 0.050 / 0.060 / 0.087 | 0.995 +/- 0.002 | 0.169 +/- 0.230 |
| Generic | noP_entropy | 0.850 +/- 0.037 | 0.317 +/- 0.309 | 0.050 / 0.061 / 0.093 | 0.995 +/- 0.002 | 0.248 +/- 0.270 |
| Generic | ens_mi | 0.876 +/- 0.030 | 0.340 +/- 0.322 | 0.050 / 0.059 / 0.075 | 0.993 +/- 0.004 | 0.389 +/- 0.315 |
| Generic | oe_pu | 0.758 +/- 0.026 | 0.108 +/- 0.124 | 0.050 / 0.056 / 0.103 | 0.993 +/- 0.004 | 0.091 +/- 0.083 |
| Generic | combo | 0.883 +/- 0.023 | 0.561 +/- 0.223 | 0.050 / 0.059 / 0.094 | 0.996 +/- 0.002 | 0.525 +/- 0.238 |
| Reconnaissance | noP_msp | 0.831 +/- 0.014 | 0.220 +/- 0.079 | 0.050 / 0.050 / 0.074 | 0.665 +/- 0.110 | 0.220 +/- 0.079 |
| Reconnaissance | noP_entropy | 0.839 +/- 0.015 | 0.342 +/- 0.115 | 0.050 / 0.058 / 0.090 | 0.753 +/- 0.130 | 0.283 +/- 0.100 |
| Reconnaissance | ens_mi | 0.792 +/- 0.013 | 0.211 +/- 0.072 | 0.050 / 0.057 / 0.070 | 0.666 +/- 0.122 | 0.231 +/- 0.057 |
| Reconnaissance | oe_pu | 0.721 +/- 0.011 | 0.195 +/- 0.261 | 0.050 / 0.064 / 0.141 | 0.677 +/- 0.185 | 0.013 +/- 0.018 |
| Reconnaissance | combo | 0.798 +/- 0.010 | 0.426 +/- 0.101 | 0.050 / 0.063 / 0.098 | 0.848 +/- 0.075 | 0.368 +/- 0.064 |
| Worms | noP_msp | 0.613 +/- 0.017 | 0.068 +/- 0.036 | 0.050 / 0.042 / 0.076 | 0.994 +/- 0.000 | 0.068 +/- 0.036 |
| Worms | noP_entropy | 0.640 +/- 0.020 | 0.095 +/- 0.014 | 0.050 / 0.045 / 0.072 | 0.994 +/- 0.000 | 0.097 +/- 0.016 |
| Worms | ens_mi | 0.717 +/- 0.014 | 0.104 +/- 0.039 | 0.050 / 0.043 / 0.067 | 0.998 +/- 0.003 | 0.120 +/- 0.048 |
| Worms | oe_pu | 0.883 +/- 0.002 | 0.085 +/- 0.013 | 0.050 / 0.057 / 0.028 | 0.994 +/- 0.000 | 0.332 +/- 0.287 |
| Worms | combo | 0.830 +/- 0.011 | 0.263 +/- 0.082 | 0.050 / 0.052 / 0.067 | 0.998 +/- 0.003 | 0.288 +/- 0.065 |
| Shellcode | noP_msp | 0.816 +/- 0.004 | 0.282 +/- 0.064 | 0.050 / 0.040 / 0.075 | 0.955 +/- 0.009 | 0.282 +/- 0.064 |
| Shellcode | noP_entropy | 0.882 +/- 0.007 | 0.498 +/- 0.147 | 0.050 / 0.044 / 0.074 | 0.949 +/- 0.011 | 0.503 +/- 0.134 |
| Shellcode | ens_mi | 0.752 +/- 0.008 | 0.109 +/- 0.048 | 0.050 / 0.045 / 0.062 | 0.939 +/- 0.011 | 0.135 +/- 0.062 |
| Shellcode | oe_pu | 0.863 +/- 0.006 | 0.043 +/- 0.010 | 0.050 / 0.044 / 0.021 | 0.925 +/- 0.016 | 0.230 +/- 0.173 |
| Shellcode | combo | 0.848 +/- 0.007 | 0.210 +/- 0.130 | 0.050 / 0.051 / 0.059 | 0.944 +/- 0.013 | 0.264 +/- 0.122 |
| Overlap-Group-1 (all three) | noP_msp | 0.735 +/- 0.016 | 0.211 +/- 0.132 | 0.050 / 0.062 / 0.077 | 0.956 +/- 0.009 | 0.211 +/- 0.132 |
| Overlap-Group-1 (all three) | noP_entropy | 0.705 +/- 0.008 | 0.072 +/- 0.026 | 0.050 / 0.059 / 0.077 | 0.958 +/- 0.012 | 0.071 +/- 0.023 |
| Overlap-Group-1 (all three) | ens_mi | 0.621 +/- 0.008 | 0.081 +/- 0.025 | 0.050 / 0.062 / 0.079 | 0.965 +/- 0.009 | 0.079 +/- 0.020 |
| Overlap-Group-1 (all three) | oe_pu | 0.904 +/- 0.002 | 0.481 +/- 0.164 | 0.049 / 0.062 / 0.031 | 0.950 +/- 0.010 | 0.657 +/- 0.048 |
| Overlap-Group-1 (all three) | combo | 0.791 +/- 0.008 | 0.193 +/- 0.074 | 0.050 / 0.055 / 0.069 | 0.970 +/- 0.008 | 0.218 +/- 0.092 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|
| noP_msp | 393 of 1456 | 10 of 171 | 388 of 7590 | 381 of 4810 | 165 of 1694 | 17 of 438 | 11 of 345 | 2641 of 33832 | 0.103 |
| noP_entropy | 733 of 1456 | 19 of 171 | 527 of 7590 | 405 of 4810 | 209 of 1694 | 32 of 438 | 25 of 345 | 2447 of 33832 | 0.174 |
| ens_mi | 163 of 1456 | 21 of 171 | 750 of 7590 | 395 of 4810 | 292 of 1694 | 38 of 438 | 17 of 345 | 1832 of 33832 | 0.051 |
| oe_pu | 69 of 1456 | 11 of 171 | 566 of 7590 | 112 of 4810 | 152 of 1694 | 53 of 438 | 45 of 345 | 57 of 33832 | 0.078 |
| combo | 334 of 1456 | 51 of 171 | 980 of 7590 | 321 of 4810 | 376 of 1694 | 59 of 438 | 52 of 345 | 1376 of 33832 | 0.107 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| noP_msp | 0.288 +/- 0.013 | 0.320 +/- 0.020 | 0.242 +/- 0.014 | 0.078 +/- 0.026 | 0.841 +/- 0.045 | 0.958 +/- 0.011 | 0.248 +/- 0.052 |
| noP_entropy | 0.288 +/- 0.013 | 0.315 +/- 0.019 | 0.242 +/- 0.013 | 0.072 +/- 0.025 | 0.841 +/- 0.045 | 0.954 +/- 0.010 | 0.462 +/- 0.123 |
| ens_mi | 0.288 +/- 0.013 | 0.311 +/- 0.016 | 0.257 +/- 0.014 | 0.054 +/- 0.020 | 0.890 +/- 0.041 | 0.943 +/- 0.011 | 0.113 +/- 0.051 |
| oe_pu | 0.288 +/- 0.013 | 0.289 +/- 0.013 | 0.287 +/- 0.012 | 0.002 +/- 0.000 | 0.995 +/- 0.001 | 0.931 +/- 0.016 | 0.049 +/- 0.006 |
| combo | 0.288 +/- 0.013 | 0.304 +/- 0.017 | 0.263 +/- 0.014 | 0.041 +/- 0.022 | 0.913 +/- 0.043 | 0.950 +/- 0.012 | 0.236 +/- 0.133 |

##### Diagnostics (mean over seeds, per held-out set)

| held-out set | known_macro_recall_noP | known_macro_recall_oe | oe_predicts_unknown_on_known_test |
|---|---|---|---|
| Worms + Shellcode | 0.747 | 0.738 | 0.006 |
| Analysis | 0.712 | 0.700 | 0.007 |
| Backdoor | 0.709 | 0.694 | 0.007 |
| DoS | 0.755 | 0.746 | 0.006 |
| Exploits | 0.795 | 0.777 | 0.003 |
| Fuzzers | 0.758 | 0.751 | 0.007 |
| Generic | 0.770 | 0.714 | 0.174 |
| Reconnaissance | 0.762 | 0.708 | 0.171 |
| Worms | 0.749 | 0.741 | 0.006 |
| Shellcode | 0.705 | 0.699 | 0.006 |
| Overlap-Group-1 (all three) | 0.755 | 0.729 | 0.023 |

#### combo (48f, mean over seeds 42-46)

Baseline for the verdict: `noP_msp`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.

##### Summary and verdict against the declared rule

| score | rotation mean AUROC | rotation mean detection | detection gain vs noP_msp | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | detection at msp's realised test false-Unknown (diagnostic) | clearly beats |
|---|---|---|---|---|---|---|---|---|---|
| noP_msp | 0.754 | 0.209 | +0.000 | 0 of 5 | Exploits (0.591) | 0.824 +/- 0.005 | 0.416 +/- 0.054 | 0.416 +/- 0.054 | no |
| noP_entropy | 0.782 | 0.318 | +0.109 | 5 of 5 | Exploits (0.606) | 0.867 +/- 0.005 | 0.598 +/- 0.036 | 0.601 +/- 0.056 | yes |
| oe_pu | 0.868 | 0.239 | +0.030 | 3 of 5 | Reconnaissance (0.700) | 0.914 +/- 0.006 | 0.101 +/- 0.017 | 0.546 +/- 0.187 | no |
| ens_mi | 0.722 | 0.233 | +0.024 | 4 of 5 | Analysis (0.618) | 0.793 +/- 0.008 | 0.247 +/- 0.072 | 0.235 +/- 0.057 | no |
| combo | 0.810 | 0.335 | +0.126 | 5 of 5 | Fuzzers (0.703) | 0.887 +/- 0.015 | 0.466 +/- 0.169 | 0.486 +/- 0.140 | yes |

##### Per held-out set

| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |
|---|---|---|---|---|---|---|
| Worms + Shellcode | noP_msp | 0.824 +/- 0.005 | 0.416 +/- 0.054 | 0.050 / 0.041 / 0.080 | 0.991 +/- 0.001 | 0.416 +/- 0.054 |
| Worms + Shellcode | noP_entropy | 0.867 +/- 0.005 | 0.598 +/- 0.036 | 0.050 / 0.046 / 0.075 | 0.993 +/- 0.001 | 0.601 +/- 0.056 |
| Worms + Shellcode | oe_pu | 0.914 +/- 0.006 | 0.101 +/- 0.017 | 0.050 / 0.044 / 0.021 | 0.979 +/- 0.005 | 0.546 +/- 0.187 |
| Worms + Shellcode | ens_mi | 0.793 +/- 0.008 | 0.247 +/- 0.072 | 0.050 / 0.050 / 0.085 | 0.991 +/- 0.002 | 0.235 +/- 0.057 |
| Worms + Shellcode | combo | 0.887 +/- 0.015 | 0.466 +/- 0.169 | 0.050 / 0.051 / 0.076 | 0.991 +/- 0.002 | 0.486 +/- 0.140 |
| Analysis | noP_msp | 0.805 +/- 0.016 | 0.098 +/- 0.043 | 0.050 / 0.040 / 0.068 | 0.848 +/- 0.004 | 0.098 +/- 0.043 |
| Analysis | noP_entropy | 0.866 +/- 0.013 | 0.225 +/- 0.155 | 0.050 / 0.047 / 0.061 | 0.850 +/- 0.004 | 0.330 +/- 0.274 |
| Analysis | oe_pu | 0.937 +/- 0.004 | 0.228 +/- 0.211 | 0.050 / 0.042 / 0.020 | 0.839 +/- 0.003 | 0.758 +/- 0.050 |
| Analysis | ens_mi | 0.618 +/- 0.015 | 0.081 +/- 0.029 | 0.050 / 0.047 / 0.076 | 0.873 +/- 0.009 | 0.073 +/- 0.018 |
| Analysis | combo | 0.780 +/- 0.029 | 0.132 +/- 0.065 | 0.050 / 0.053 / 0.069 | 0.873 +/- 0.012 | 0.128 +/- 0.051 |
| Backdoor | noP_msp | 0.801 +/- 0.011 | 0.126 +/- 0.036 | 0.050 / 0.043 / 0.074 | 0.999 +/- 0.001 | 0.126 +/- 0.036 |
| Backdoor | noP_entropy | 0.861 +/- 0.008 | 0.265 +/- 0.223 | 0.050 / 0.045 / 0.071 | 0.999 +/- 0.001 | 0.328 +/- 0.294 |
| Backdoor | oe_pu | 0.962 +/- 0.003 | 0.326 +/- 0.291 | 0.050 / 0.039 / 0.023 | 0.997 +/- 0.000 | 0.885 +/- 0.084 |
| Backdoor | ens_mi | 0.625 +/- 0.018 | 0.099 +/- 0.030 | 0.050 / 0.051 / 0.080 | 1.000 +/- 0.000 | 0.094 +/- 0.025 |
| Backdoor | combo | 0.792 +/- 0.038 | 0.204 +/- 0.072 | 0.050 / 0.054 / 0.070 | 1.000 +/- 0.000 | 0.209 +/- 0.066 |
| DoS | noP_msp | 0.641 +/- 0.010 | 0.090 +/- 0.028 | 0.050 / 0.059 / 0.092 | 0.995 +/- 0.002 | 0.090 +/- 0.028 |
| DoS | noP_entropy | 0.676 +/- 0.011 | 0.200 +/- 0.083 | 0.050 / 0.061 / 0.073 | 0.996 +/- 0.002 | 0.243 +/- 0.105 |
| DoS | oe_pu | 0.880 +/- 0.006 | 0.193 +/- 0.087 | 0.050 / 0.040 / 0.019 | 0.992 +/- 0.001 | 0.557 +/- 0.101 |
| DoS | ens_mi | 0.629 +/- 0.017 | 0.126 +/- 0.026 | 0.050 / 0.061 / 0.096 | 0.997 +/- 0.002 | 0.122 +/- 0.029 |
| DoS | combo | 0.762 +/- 0.016 | 0.204 +/- 0.050 | 0.050 / 0.064 / 0.082 | 0.997 +/- 0.002 | 0.231 +/- 0.078 |
| Exploits | noP_msp | 0.591 +/- 0.004 | 0.076 +/- 0.057 | 0.050 / 0.074 / 0.115 | 0.972 +/- 0.008 | 0.076 +/- 0.057 |
| Exploits | noP_entropy | 0.606 +/- 0.003 | 0.136 +/- 0.044 | 0.050 / 0.082 / 0.122 | 0.979 +/- 0.006 | 0.131 +/- 0.044 |
| Exploits | oe_pu | 0.921 +/- 0.002 | 0.392 +/- 0.308 | 0.050 / 0.101 / 0.053 | 0.968 +/- 0.016 | 0.634 +/- 0.218 |
| Exploits | ens_mi | 0.672 +/- 0.007 | 0.215 +/- 0.143 | 0.050 / 0.085 / 0.126 | 0.981 +/- 0.006 | 0.203 +/- 0.113 |
| Exploits | combo | 0.801 +/- 0.013 | 0.336 +/- 0.166 | 0.050 / 0.084 / 0.104 | 0.984 +/- 0.005 | 0.358 +/- 0.167 |
| Fuzzers | noP_msp | 0.699 +/- 0.007 | 0.100 +/- 0.028 | 0.050 / 0.053 / 0.067 | 0.256 +/- 0.009 | 0.101 +/- 0.028 |
| Fuzzers | noP_entropy | 0.701 +/- 0.007 | 0.125 +/- 0.030 | 0.050 / 0.055 / 0.075 | 0.268 +/- 0.012 | 0.111 +/- 0.032 |
| Fuzzers | oe_pu | 0.709 +/- 0.007 | 0.035 +/- 0.010 | 0.050 / 0.055 / 0.021 | 0.213 +/- 0.013 | 0.128 +/- 0.032 |
| Fuzzers | ens_mi | 0.695 +/- 0.008 | 0.125 +/- 0.047 | 0.050 / 0.053 / 0.063 | 0.278 +/- 0.021 | 0.132 +/- 0.032 |
| Fuzzers | combo | 0.703 +/- 0.007 | 0.115 +/- 0.033 | 0.050 / 0.061 / 0.054 | 0.262 +/- 0.017 | 0.136 +/- 0.032 |
| Generic | noP_msp | 0.932 +/- 0.013 | 0.656 +/- 0.225 | 0.050 / 0.068 / 0.078 | 0.881 +/- 0.204 | 0.656 +/- 0.225 |
| Generic | noP_entropy | 0.939 +/- 0.008 | 0.760 +/- 0.090 | 0.050 / 0.066 / 0.086 | 0.942 +/- 0.074 | 0.734 +/- 0.121 |
| Generic | oe_pu | 0.873 +/- 0.024 | 0.632 +/- 0.165 | 0.050 / 0.057 / 0.113 | 0.885 +/- 0.173 | 0.555 +/- 0.183 |
| Generic | ens_mi | 0.935 +/- 0.010 | 0.782 +/- 0.030 | 0.050 / 0.062 / 0.073 | 0.969 +/- 0.018 | 0.789 +/- 0.033 |
| Generic | combo | 0.934 +/- 0.004 | 0.817 +/- 0.017 | 0.050 / 0.069 / 0.104 | 0.994 +/- 0.005 | 0.803 +/- 0.024 |
| Reconnaissance | noP_msp | 0.853 +/- 0.012 | 0.210 +/- 0.057 | 0.050 / 0.054 / 0.065 | 0.952 +/- 0.006 | 0.210 +/- 0.057 |
| Reconnaissance | noP_entropy | 0.867 +/- 0.012 | 0.373 +/- 0.042 | 0.050 / 0.057 / 0.079 | 0.962 +/- 0.005 | 0.336 +/- 0.048 |
| Reconnaissance | oe_pu | 0.700 +/- 0.011 | 0.153 +/- 0.205 | 0.050 / 0.065 / 0.148 | 0.950 +/- 0.037 | 0.004 +/- 0.002 |
| Reconnaissance | ens_mi | 0.827 +/- 0.014 | 0.297 +/- 0.059 | 0.050 / 0.059 / 0.066 | 0.955 +/- 0.012 | 0.297 +/- 0.052 |
| Reconnaissance | combo | 0.807 +/- 0.013 | 0.453 +/- 0.101 | 0.050 / 0.063 / 0.107 | 0.988 +/- 0.006 | 0.319 +/- 0.068 |
| Worms | noP_msp | 0.620 +/- 0.012 | 0.085 +/- 0.019 | 0.050 / 0.038 / 0.078 | 0.995 +/- 0.003 | 0.085 +/- 0.019 |
| Worms | noP_entropy | 0.635 +/- 0.012 | 0.138 +/- 0.013 | 0.050 / 0.047 / 0.078 | 0.999 +/- 0.003 | 0.139 +/- 0.014 |
| Worms | oe_pu | 0.911 +/- 0.003 | 0.090 +/- 0.035 | 0.050 / 0.054 / 0.025 | 0.999 +/- 0.003 | 0.506 +/- 0.238 |
| Worms | ens_mi | 0.698 +/- 0.014 | 0.125 +/- 0.065 | 0.050 / 0.044 / 0.083 | 1.000 +/- 0.000 | 0.123 +/- 0.059 |
| Worms | combo | 0.818 +/- 0.014 | 0.263 +/- 0.109 | 0.050 / 0.053 / 0.077 | 1.000 +/- 0.000 | 0.268 +/- 0.104 |
| Shellcode | noP_msp | 0.844 +/- 0.003 | 0.440 +/- 0.059 | 0.050 / 0.040 / 0.080 | 0.990 +/- 0.002 | 0.440 +/- 0.059 |
| Shellcode | noP_entropy | 0.890 +/- 0.004 | 0.637 +/- 0.050 | 0.050 / 0.046 / 0.076 | 0.993 +/- 0.002 | 0.639 +/- 0.070 |
| Shellcode | oe_pu | 0.915 +/- 0.005 | 0.099 +/- 0.013 | 0.050 / 0.043 / 0.022 | 0.979 +/- 0.005 | 0.543 +/- 0.181 |
| Shellcode | ens_mi | 0.801 +/- 0.005 | 0.244 +/- 0.069 | 0.050 / 0.046 / 0.082 | 0.990 +/- 0.003 | 0.235 +/- 0.054 |
| Shellcode | combo | 0.894 +/- 0.014 | 0.492 +/- 0.154 | 0.050 / 0.057 / 0.080 | 0.991 +/- 0.003 | 0.499 +/- 0.118 |
| Overlap-Group-1 (all three) | noP_msp | 0.740 +/- 0.014 | 0.279 +/- 0.123 | 0.050 / 0.060 / 0.080 | 0.966 +/- 0.007 | 0.279 +/- 0.123 |
| Overlap-Group-1 (all three) | noP_entropy | 0.721 +/- 0.010 | 0.152 +/- 0.107 | 0.050 / 0.061 / 0.094 | 0.970 +/- 0.008 | 0.124 +/- 0.111 |
| Overlap-Group-1 (all three) | oe_pu | 0.920 +/- 0.001 | 0.489 +/- 0.185 | 0.050 / 0.061 / 0.029 | 0.962 +/- 0.007 | 0.693 +/- 0.063 |
| Overlap-Group-1 (all three) | ens_mi | 0.644 +/- 0.008 | 0.097 +/- 0.038 | 0.050 / 0.053 / 0.087 | 0.973 +/- 0.005 | 0.091 +/- 0.039 |
| Overlap-Group-1 (all three) | combo | 0.811 +/- 0.009 | 0.257 +/- 0.084 | 0.050 / 0.055 / 0.077 | 0.978 +/- 0.006 | 0.269 +/- 0.127 |

##### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)

| score | Shellcode | Worms | Exploits | Fuzzers | DoS | Analysis | Backdoor | Normal | precision of Unknown (zero-day share of flagged flows) |
|---|---|---|---|---|---|---|---|---|---|
| noP_msp | 662 of 1456 | 15 of 171 | 328 of 7590 | 750 of 4810 | 216 of 1694 | 50 of 438 | 47 of 345 | 2526 of 33832 | 0.152 |
| noP_entropy | 948 of 1456 | 24 of 171 | 463 of 7590 | 829 of 4810 | 254 of 1694 | 93 of 438 | 69 of 345 | 1926 of 33832 | 0.214 |
| oe_pu | 153 of 1456 | 11 of 171 | 573 of 7590 | 114 of 4810 | 169 of 1694 | 76 of 438 | 64 of 345 | 32 of 33832 | 0.153 |
| ens_mi | 382 of 1456 | 21 of 171 | 742 of 7590 | 999 of 4810 | 360 of 1694 | 80 of 438 | 55 of 345 | 1921 of 33832 | 0.090 |
| combo | 716 of 1456 | 41 of 171 | 957 of 7590 | 740 of 4810 | 496 of 1694 | 138 of 438 | 133 of 345 | 1248 of 33832 | 0.174 |

##### Alert FPR and the review queue at the 5% target (Task 4 Step 3 measures; Worms + Shellcode held out)

| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |
|---|---|---|---|---|---|---|---|
| noP_msp | 0.297 +/- 0.012 | 0.329 +/- 0.017 | 0.255 +/- 0.016 | 0.075 +/- 0.024 | 0.858 +/- 0.042 | 0.991 +/- 0.001 | 0.416 +/- 0.054 |
| noP_entropy | 0.297 +/- 0.012 | 0.319 +/- 0.014 | 0.262 +/- 0.011 | 0.057 +/- 0.009 | 0.884 +/- 0.015 | 0.993 +/- 0.001 | 0.598 +/- 0.036 |
| oe_pu | 0.297 +/- 0.012 | 0.297 +/- 0.012 | 0.296 +/- 0.012 | 0.001 +/- 0.000 | 0.997 +/- 0.001 | 0.979 +/- 0.005 | 0.101 +/- 0.017 |
| ens_mi | 0.297 +/- 0.012 | 0.318 +/- 0.017 | 0.262 +/- 0.014 | 0.057 +/- 0.022 | 0.882 +/- 0.042 | 0.991 +/- 0.002 | 0.247 +/- 0.072 |
| combo | 0.297 +/- 0.012 | 0.308 +/- 0.015 | 0.272 +/- 0.015 | 0.037 +/- 0.020 | 0.915 +/- 0.039 | 0.991 +/- 0.002 | 0.466 +/- 0.169 |

##### Diagnostics (mean over seeds, per held-out set)

| held-out set | known_macro_recall_noP | known_macro_recall_oe | oe_predicts_unknown_on_known_test |
|---|---|---|---|
| Worms + Shellcode | 0.744 | 0.736 | 0.006 |
| Analysis | 0.743 | 0.735 | 0.007 |
| Backdoor | 0.744 | 0.735 | 0.007 |
| DoS | 0.794 | 0.777 | 0.006 |
| Exploits | 0.820 | 0.800 | 0.002 |
| Fuzzers | 0.820 | 0.810 | 0.007 |
| Generic | 0.823 | 0.758 | 0.189 |
| Reconnaissance | 0.814 | 0.748 | 0.186 |
| Worms | 0.763 | 0.753 | 0.006 |
| Shellcode | 0.731 | 0.724 | 0.007 |
| Overlap-Group-1 (all three) | 0.791 | 0.776 | 0.017 |

## Source: open_set_boost_iforest_40f_48f.md

### Task 4.5: iforest

#### isolation-forest sign check (40f, mean over seeds 42-46)

Worms + Shellcode held out.

| score | known attacks vs Normal (AUROC) | Worms: mean percentile among known test flows | Shellcode: mean percentile |
|---|---|---|---|
| iforest | 0.672 +/- 0.012 | 0.684 +/- 0.023 | 0.407 +/- 0.021 |
| knn | 0.675 +/- 0.010 | 0.633 +/- 0.007 | 0.387 +/- 0.008 |
| maha | 0.411 +/- 0.005 | 0.510 +/- 0.003 | 0.307 +/- 0.005 |

Known attacks vs Normal, averaged over the nine rotation runs: iforest AUROC 0.668; knn AUROC 0.666; maha AUROC 0.403.

#### isolation-forest sign check (48f, mean over seeds 42-46)

Worms + Shellcode held out.

| score | known attacks vs Normal (AUROC) | Worms: mean percentile among known test flows | Shellcode: mean percentile |
|---|---|---|---|
| iforest | 0.724 +/- 0.014 | 0.707 +/- 0.007 | 0.473 +/- 0.031 |
| knn | 0.635 +/- 0.010 | 0.515 +/- 0.008 | 0.288 +/- 0.007 |
| maha | 0.429 +/- 0.005 | 0.477 +/- 0.002 | 0.283 +/- 0.005 |

Known attacks vs Normal, averaged over the nine rotation runs: iforest AUROC 0.719; knn AUROC 0.625; maha AUROC 0.419.

## Source: task_4_protocol.md

### Task 4 protocol (declared before any Task 4 result was produced)

Novelty 1: open-set / zero-day detection. XGBoost, flat model (not the hierarchical scheme), official split, scheme `current`, ZERO-SHOT throughout
(training data only), seeds 42-46, mean and std.

#### Data facts (after exact deduplication, both official files)
Zero-day flows with Worms and Shellcode held out: 1,627 (Shellcode 1,456 = 89.5%, Worms 171). Known classes in the official test file: Normal 33,832,
Exploits 7,590, Fuzzers 4,810, Generic 3,418, Reconnaissance 2,469, DoS 1,694, Analysis 438, Backdoor 345. One held-out class mix is not a general result;
Step 2 rotates the held-out class. The "67-75% detection at 26-28% false alarms" figure came from a threshold tuned on the zero-day samples and is withdrawn.

#### Splits and thresholds
- Training / validation are block-grouped (1,000-row blocks, 200-row gaps; `block_validation_splits`). Zero-day flows are never in training or validation.
- The known validation flows are split in two halves by validation block: a **threshold half** (threshold for the declared **5% false-Unknown** target: a flow is
  Unknown when its score exceeds the 95th percentile of the known threshold-half scores) and a **calibration half** (conformal calibration, rank normalisation of the
  anomaly / combined scores). The halves are disjoint. Nothing about the zero-day flows or the official test labels enters any threshold or choice.
- The open-set wrapper does not change the closed-set prediction.

#### Scores (higher = more likely Unknown), Step 1
- `msp` = 1 - max softmax (current); `entropy` = Shannon entropy of the class probabilities / ln K; `margin` = 1 - (top probability - second probability).
- `conformal` = 1 - the largest class-conditional (Mondrian) split-conformal p-value, p_k(x) = (#{calibration flows of class k with nonconformity >= 1 - p_k(x)} + 1) / (n_k + 1),
  nonconformity 1 - p(true class), calibration = the calibration half. A flow is Unknown exactly when its conformal prediction set is empty at the level the threshold implies.
  (The existing `results/diagnostics/conformal_prediction_sets.py` is a coverage diagnostic and is not reused for scoring.)
- `iforest` = isolation forest (200 trees) fitted on Normal TRAINING flows only (same scaled / encoded matrix as the classifier); score = -score_samples.
- Combinations of `iforest` with each confidence score s in {msp, entropy, margin, conformal}: both scores are mapped to their empirical-CDF rank on the calibration half;
  rule `mean` = average of the two ranks, rule `max` = larger rank. **The rule is chosen on validation** (below), per score, pool and seed.

#### Choosing the rule and the "best" score without zero-day samples
Pseudo-unknown validation: for each of two declared known classes X in {Reconnaissance, Generic} (not members of the merged group, not Worms / Shellcode), an inner model is trained
on the block-grouped training rows without class X and scored on the validation flows: the validation rows of X are the pseudo-unknowns, the other known validation rows (threshold half) the
knowns. The AUROC of each candidate score, averaged over the two X, is the selection criterion. It picks (a) mean vs max per combination, and (b) the **best score of a pool** =
the candidate with the highest mean pseudo-unknown AUROC over the 5 seeds. That best score is used for Steps 2 and 3. The score that happens to be best on the real zero-day flows is
reported but never used for a choice.

#### Step 1 metrics (pools 40, 45, 48)
Primary: **unknown AUROC** (official-test known flows vs zero-day flows) and **detection at the validation-chosen 5% threshold** (share of zero-day flows flagged Unknown).
Also: share of zero-day flows flagged Unknown or predicted as any attack class, per zero-day class (Worms, Shellcode), and the realised false-Unknown rate on the calibration
half of validation (held-out) and on the official test known flows (the gap is the cost of the shift).

#### Step 2: leave-one-attack-class-out
Each of Analysis, Backdoor, DoS, Exploits, Fuzzers, Generic, Reconnaissance, Worms, Shellcode is held out in turn (its flows from both files are never trained on); retrain, threshold on
known block-grouped validation at 5%, test with that class as the zero-day. **Merged group:** the label scheme stays `current`; a held-out member of Overlap-Group-1 (Analysis, Backdoor, DoS) is removed from the
group's training rows while its siblings stay known and still form `Overlap-Group-1`. Most of those flows have exact twins among the known siblings (and Exploits), so low detection there is expected and is explained
by the twin share, not hidden by relabelling. As an extra row all three members are held out together ("Overlap-Group-1 as a unit"). Per class: AUROC, detection at 5%, share flagged Unknown
or predicted as any attack class; mean and worst class; the best score of the pool vs `msp`; and the known classes the false-Unknown alarms come from (validation and test). Pools 40 and 48.

#### Step 3: alert-level FPR and the review queue
Alert = predicted as any attack class (open-set OFF) or predicted attack / flagged Unknown (open-set ON), on Normal flows of the official test. Confidence / abstain curve over the
false-Unknown targets {0.5, 1, 2, 3, 5, 7.5, 10, 15, 20, 30}% of the best score: confident-alert FPR (Normal called an attack and NOT flagged), review rate on Normal (Normal flagged Unknown), alert FPR
(attack or Unknown), zero-day catch (flagged or called an attack), known-attack alert rate. The operating point is the declared 5% target (chosen on validation only).

#### Step 4: where the gain comes from (48 features)
Step 1 repeated, zero-day = Worms + Shellcode, on: 48 features minus the 7 window-count ct_* columns (ct_src_dport_ltm, ct_dst_sport_ltm, ct_srv_src, ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm; `full_no_ct_window`),
minus every ct_* column (`full_no_ct_any`), and the 30- and 15-feature tiers of the 48 pool (shared blockval rankings). Declared reading: the ct_* columns carry the open-set gain if removing the
window-count columns lowers the `msp` detection by at least half of the 40 -> 48 gap (confirm), by less than a quarter (reject), otherwise partial.

#### Not claimed
Calibration under the official-split shift is poor, so confidence is not assumed reliable; the results are reported as measured. Teammates' model families are not run or quoted here.

## Source: task_4_5_protocol.md

### Task 4.5 protocol (declared before any Task 4.5 result was produced)

Goal: improve zero-day (open-set) detection. XGBoost, flat model, official split, scheme `current`, ZERO-SHOT throughout, seeds 42-46 (mean and std), pools 40 (base) and 48 (full).
Everything of Task 4 that is not changed stays: block-grouped validation (1,000-row blocks, 200-row gaps) split into a THRESHOLD half and a CALIBRATION half by whole blocks; a flow is flagged
Unknown when its score exceeds the 95th percentile of the known threshold-half scores (5% false-Unknown target); no zero-day flow and no official-test label ever enters a threshold, a fit,
a parameter or a choice (`results/task_4_protocol.md`). Evaluation sets are the same as Task 4: Worms + Shellcode (the Step 1 setting), the nine-class leave-one-class-out rotation, and the
Overlap-Group-1 trio held out together (merged-group handling as in Task 4).

#### Baselines and the declared success rule
Baselines, rerun in the same pass: max-softmax (`msp`) and `entropy`. A score **clearly beats** max-softmax when (all three) the rotation-mean detection (nine classes) is at least 0.05 higher, the
rotation-mean AUROC is not lower, and the mean paired (same seed) rotation detection difference is positive in at least 4 of 5 seeds; and its Worms + Shellcode detection is not more than 0.02 below
max-softmax's. Hypothesis (a guess): rotation-mean detection rises from about 0.21 to 0.30-0.35. If nothing clears the rule the result is reported as negative.

#### Scores (higher = more likely Unknown) and their declared parameters
1. **Calibration.** Temperature T in [0.25, 5] fitted on the CALIBRATION half of the validation rows by negative log-likelihood; `msp_cal` and `entropy_cal` on p^(1/T) renormalised. ECE (15 bins) on the known
   test flows is reported before and after.
2. **Per-class thresholds** (`msp_pc`, `entropy_pc`). For each predicted class c the threshold is the 95th percentile of the known threshold-half scores of the flows predicted c (allocation rule: the same 5%
   false-Unknown rate inside every predicted class, so the overall rate is 5% by construction); a predicted class with fewer than 30 threshold-half flows uses the global threshold. The AUROC of this rule is
   computed on the shifted score (score minus the threshold of the flow's predicted class); the review-queue curve uses, for each target, the (1 - target) percentile within each predicted class.
3. **Ensemble disagreement** (M = 5): the main model plus 4 members with seeds seed + 100 j (j = 1..4), subsample 0.7, colsample_bytree 0.7, 150 trees, learning rate 0.2, depth and regularisation as the main model,
   same class weights, same preprocessing. Scores: `ens_mi` = predictive mutual information, entropy of the mean probability minus the mean member entropy; `ens_var` = mean over classes of the variance across
   members of the class probability; `ens_msp` = 1 - max of the mean probability.
4. **Distance to the training data** in the scaled feature matrix the classifier sees. `knn` = mean distance to the k = 10 nearest neighbours among 20,000 training rows (uniform sample, seeded); `maha` = the
   minimum over the known training classes of the Mahalanobis distance (class mean, class covariance plus a ridge of 0.01 x the mean variance). Scores are computed for validation, test and zero-day flows.
5. **Pseudo-unknown training (outlier exposure).** An extra class "Unknown" is made from two known classes P held out inside the training split: P = the first two of (Reconnaissance, Generic, Fuzzers, Exploits)
   that are not the evaluation's held-out class and not a member of a held-out trio. The model is trained on the other known classes plus Unknown; scores: `oe_pu` = predicted probability of Unknown, `oe_msp` =
   1 - max probability. P flows are removed from the known validation and test sets of this comparison (they are Unknown by construction), and the comparison baseline is a closed-set model trained without P
   (`noP_msp`, `noP_entropy`) on the same known flows. The cost to known-class recall is reported: macro recall over the remaining known classes of the Unknown-class model (a flow predicted Unknown counts as missed)
   against the model trained without P, and the attack classes in P can no longer be recognised.
6. **Combination.** Rank-average (`mean` of the empirical-CDF ranks fitted on the calibration half) of the two individual scores with the highest mean pseudo-unknown validation AUROC among
   {msp, entropy, msp_cal, entropy_cal, ens_mi, ens_var, ens_msp, knn, maha, oe_pu}. The selection uses the Task 4 pseudo-unknown validation (inner models trained without Reconnaissance or Generic; the
   validation flows of the held-out class are the pseudo-unknowns, the other known threshold-half flows the knowns; for the Unknown-class model P excludes the inner held-out class by the same rule), averaged
   over the 5 seeds and the two inner classes, once per pool. The real zero-day classes and the rotation are never used to choose.

#### Isolation-forest check (diagnostic)
Using the Task 4 score (isolation forest on Normal training flows, score = minus `score_samples`, higher = more anomalous) on the official test: AUROC of the score for known attacks (positive) against known Normal
flows; the mean percentile of Worms and Shellcode scores among the known test scores (above 50% = the zero-day flows look more anomalous than a typical known flow); the same two numbers for `knn` and `maha`.

#### Reporting (per idea and for the combination)
- Per held-out class (rotation, trio, Worms + Shellcode): unknown AUROC, detection at the 5% target, realised false-Unknown rate on the two validation halves and on the official test, share flagged Unknown or
  predicted as an attack class. Diagnostic column, never used for selection: detection at the threshold that gives the SAME realised test false-Unknown rate as `msp` in the same run.
- Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out, 5% threshold): counts of Shellcode, Worms, each known attack class and Normal, and the precision of Unknown (zero-day
  share of the flagged flows).
- Effect on alert FPR and the review queue (Task 4 Step 3 measures): alert FPR with the wrapper off / on, confident-alert FPR, review rate on Normal, zero-day catch, at the 5% target and over the target curve.
- Output under `results/metrics/xgboost/` with the pool in the file name, never overwriting earlier files; each new function has a test; each idea is its own commit (`--idea calibration|perclass|ensemble|distance|oe|combo`).
- One claim for novelty 1 and the protocol behind it; `task_4_conclusion.md`, README.md and PROJECT_PLAN.md are updated only for facts established here. Then stop and wait before Task 5.
