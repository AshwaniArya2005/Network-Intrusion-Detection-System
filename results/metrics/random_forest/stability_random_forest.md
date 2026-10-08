# Feature-tier study Step 2: explanation stability, random_forest (mean over seeds 42-46; zero-shot)

Tier agreement = SHAP importance of two tiers of the same seed; noise floor = the same tier under two seeds. Spearman rank correlation / cosine / top-10 Jaccard. Stability is evidence about the explanations, not about the cause of the official-split shift.

## 48f

Tier agreement: Spearman 0.940-0.981 (mean 0.956), cosine 0.988-0.996, top-10 Jaccard 0.758-0.927. Noise floor (same tier, different seeds): Spearman 0.944-0.979, cosine 0.989-0.994, top-10 Jaccard 0.791-0.927.

| comparison | a | b | common features | Spearman | cosine | top-10 Jaccard |
|---|---|---|---|---|---|---|
| tier_pair | 48 | 40 | 40 | 0.981 +/- 0.006 | 0.995 +/- 0.002 | 0.927 +/- 0.100 |
| tier_pair | 48 | 30 | 30 | 0.943 +/- 0.013 | 0.989 +/- 0.005 | 0.758 +/- 0.083 |
| tier_pair | 48 | 20 | 20 | 0.956 +/- 0.023 | 0.994 +/- 0.002 | 0.891 +/- 0.100 |
| tier_pair | 48 | 15 | 15 | 0.959 +/- 0.012 | 0.992 +/- 0.002 | 0.891 +/- 0.100 |
| tier_pair | 40 | 30 | 30 | 0.953 +/- 0.011 | 0.988 +/- 0.003 | 0.758 +/- 0.083 |
| tier_pair | 40 | 20 | 20 | 0.959 +/- 0.009 | 0.993 +/- 0.002 | 0.855 +/- 0.081 |
| tier_pair | 40 | 15 | 15 | 0.955 +/- 0.026 | 0.991 +/- 0.003 | 0.891 +/- 0.100 |
| tier_pair | 30 | 20 | 20 | 0.961 +/- 0.029 | 0.991 +/- 0.004 | 0.927 +/- 0.100 |
| tier_pair | 30 | 15 | 15 | 0.957 +/- 0.027 | 0.992 +/- 0.004 | 0.927 +/- 0.100 |
| tier_pair | 20 | 15 | 15 | 0.940 +/- 0.036 | 0.996 +/- 0.002 | 0.927 +/- 0.100 |
| same_tier_seeds | 48 | 48 | 48 | 0.979 +/- 0.007 | 0.989 +/- 0.008 | 0.873 +/- 0.088 |
| same_tier_seeds | 40 | 40 | 40 | 0.967 +/- 0.011 | 0.991 +/- 0.004 | 0.927 +/- 0.094 |
| same_tier_seeds | 30 | 30 | 30 | 0.963 +/- 0.015 | 0.993 +/- 0.004 | 0.791 +/- 0.102 |
| same_tier_seeds | 20 | 20 | 20 | 0.964 +/- 0.011 | 0.991 +/- 0.007 | 0.927 +/- 0.094 |
| same_tier_seeds | 15 | 15 | 15 | 0.944 +/- 0.016 | 0.994 +/- 0.004 | 0.927 +/- 0.094 |

