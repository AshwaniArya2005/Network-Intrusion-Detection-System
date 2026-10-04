# Task 4 conclusion: open-set / zero-day detection under an honest protocol (novelty 1), XGBoost

ZERO-SHOT throughout; official split, scheme `current`, flat model; seeds 42-46, mean +/- std. Protocol declared before any result: `results/task_4_protocol.md`.
Thresholds come only from KNOWN validation flows (block-grouped, 1,000-row blocks / 200-row gaps; threshold half vs calibration half) at a **5% false-Unknown** target; the
combination rule and the "best" score were chosen on pseudo-unknowns carved from known classes (Reconnaissance / Generic held out of inner models), never on the zero-day flows.
Tables: `open_set_step1_40f_45f_48f.md`, `open_set_step2_40f_48f.md` + `open_set_step2_sources_40f_45f_48f.md`, `open_set_step3_40f_45f_48f.md`, `open_set_step4_*.md`.
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
