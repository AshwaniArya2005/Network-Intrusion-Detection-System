# Task 2.7 Step 3 (TRANSDUCTIVE): self-training, mean +/- std over seeds 42-46

Two rounds, tau = 0.90, pseudo-labelled rows carry 20% of the sample weight, rounds are not cumulative. Pseudo-labels come from the unlabelled blocks and every metric is on the other blocks (200-row gaps). `validation` rows are the check made before looking at the test file (half of the block-grouped validation blocks treated as unlabelled).

## 40f

### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.811 +/- 0.111 | 0.729 +/- 0.065 | 0.210 +/- 0.219 | n/a | n/a | n/a |
| self_round1 | transductive | 0.811 +/- 0.111 | 0.729 +/- 0.064 | 0.209 +/- 0.218 | n/a | n/a | n/a |
| self_round2 | transductive | 0.812 +/- 0.110 | 0.704 +/- 0.077 | 0.207 +/- 0.215 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR -0.0034 (lower in 4 of 5 seeds), macro F1 -0.0245.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): fails.

### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.726 +/- 0.042 | 0.709 +/- 0.025 | 0.314 +/- 0.071 | 0.283 +/- 0.082 | 0.944 +/- 0.007 | 0.090 +/- 0.017 |
| self_round1 | transductive | 0.721 +/- 0.046 | 0.707 +/- 0.027 | 0.325 +/- 0.080 | 0.283 +/- 0.087 | 0.944 +/- 0.009 | 0.101 +/- 0.020 |
| self_round2 | transductive | 0.722 +/- 0.045 | 0.706 +/- 0.025 | 0.324 +/- 0.079 | 0.282 +/- 0.085 | 0.944 +/- 0.007 | 0.101 +/- 0.020 |

Round 2 minus round 0: argmax FPR +0.0097 (lower in 0 of 5 seeds), macro F1 -0.0022.

### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13360.800 +/- 1915.084 | 0.034 +/- 0.016 | 0.023 +/- 0.012 | 0.089 +/- 0.040 |
| self_round1 | 13730.400 +/- 1840.486 | 0.043 +/- 0.020 | 0.031 +/- 0.015 | 0.107 +/- 0.045 |

## 45f

### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.818 +/- 0.111 | 0.736 +/- 0.064 | 0.208 +/- 0.222 | n/a | n/a | n/a |
| self_round1 | transductive | 0.819 +/- 0.110 | 0.712 +/- 0.074 | 0.207 +/- 0.221 | n/a | n/a | n/a |
| self_round2 | transductive | 0.820 +/- 0.108 | 0.737 +/- 0.064 | 0.205 +/- 0.216 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR -0.0030 (lower in 3 of 5 seeds), macro F1 +0.0009.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): passes.

### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.719 +/- 0.043 | 0.704 +/- 0.024 | 0.324 +/- 0.075 | 0.271 +/- 0.078 | 0.936 +/- 0.005 | 0.116 +/- 0.023 |
| self_round1 | transductive | 0.718 +/- 0.046 | 0.703 +/- 0.026 | 0.332 +/- 0.080 | 0.275 +/- 0.084 | 0.947 +/- 0.010 | 0.123 +/- 0.025 |
| self_round2 | transductive | 0.721 +/- 0.047 | 0.706 +/- 0.027 | 0.331 +/- 0.082 | 0.274 +/- 0.082 | 0.953 +/- 0.009 | 0.124 +/- 0.025 |

Round 2 minus round 0: argmax FPR +0.0070 (lower in 0 of 5 seeds), macro F1 +0.0022.

### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13599.200 +/- 1789.848 | 0.054 +/- 0.026 | 0.041 +/- 0.020 | 0.144 +/- 0.055 |
| self_round1 | 14234.200 +/- 1653.202 | 0.073 +/- 0.034 | 0.057 +/- 0.027 | 0.176 +/- 0.064 |

## 48f

### validation blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.822 +/- 0.111 | 0.717 +/- 0.076 | 0.207 +/- 0.220 | n/a | n/a | n/a |
| self_round1 | transductive | 0.821 +/- 0.111 | 0.716 +/- 0.074 | 0.209 +/- 0.223 | n/a | n/a | n/a |
| self_round2 | transductive | 0.820 +/- 0.111 | 0.716 +/- 0.072 | 0.209 +/- 0.222 | n/a | n/a | n/a |

Round 2 minus round 0: argmax FPR +0.0022 (lower in 1 of 5 seeds), macro F1 -0.0013.

Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): passes.

### test blocks

| method | access | accuracy | macro_f1 | argmax_fpr | det95_test_fpr | det95_test_detection | ece |
|---|---|---|---|---|---|---|---|
| self_round0 | zero-shot | 0.723 +/- 0.044 | 0.710 +/- 0.025 | 0.323 +/- 0.074 | 0.272 +/- 0.080 | 0.944 +/- 0.007 | 0.114 +/- 0.022 |
| self_round1 | transductive | 0.722 +/- 0.047 | 0.710 +/- 0.027 | 0.332 +/- 0.081 | 0.274 +/- 0.080 | 0.956 +/- 0.008 | 0.123 +/- 0.025 |
| self_round2 | transductive | 0.726 +/- 0.046 | 0.714 +/- 0.027 | 0.329 +/- 0.080 | 0.271 +/- 0.080 | 0.961 +/- 0.008 | 0.122 +/- 0.025 |

Round 2 minus round 0: argmax FPR +0.0054 (lower in 0 of 5 seeds), macro F1 +0.0039.

### Reinforcement diagnostics on the test blocks (true labels used to report only)

| method | pseudo_labelled | pseudo_wrong_share | true_normal_given_attack_pseudo_label | attack_pseudo_labels_that_are_normal |
|---|---|---|---|---|
| self_round0 | 13770.600 +/- 1753.373 | 0.054 +/- 0.026 | 0.041 +/- 0.020 | 0.140 +/- 0.055 |
| self_round1 | 14412.600 +/- 1622.903 | 0.073 +/- 0.034 | 0.058 +/- 0.028 | 0.172 +/- 0.063 |

