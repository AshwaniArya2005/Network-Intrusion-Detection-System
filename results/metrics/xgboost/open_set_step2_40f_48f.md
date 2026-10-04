# Task 4 Step 2: leave-one-attack-class-out (XGBoost, official split, threshold at 5% false-Unknown on block-grouped known validation, mean +/- std over 5 seeds)

Each class is held out in turn (never trained on); `best` = the pool's pseudo-unknown-selected score, compared with `msp`. Overlap-Group-1 members are held out one at a time (siblings stay known and still form the merged group); the trio is also held out as a unit. `exact twin share` = share of the class's flows with an identical feature vector among the known flows.

## 40f  (best score: entropy)

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

## 48f  (best score: iforest+entropy:max)

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

