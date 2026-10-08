# Feature-tier study Step 2: explanation stability, logistic_regression (mean over seeds 42-46; zero-shot)

Tier agreement = SHAP importance of two tiers of the same seed; noise floor = the same tier under two seeds. Spearman rank correlation / cosine / top-10 Jaccard. Stability is evidence about the explanations, not about the cause of the official-split shift.

## 48f

Tier agreement: Spearman 0.590-0.984 (mean 0.798), cosine 0.686-0.998, top-10 Jaccard 0.538-0.891. Noise floor (same tier, different seeds): Spearman 0.927-0.976, cosine 0.986-0.991, top-10 Jaccard 0.776-0.927.

| comparison | a | b | common features | Spearman | cosine | top-10 Jaccard |
|---|---|---|---|---|---|---|
| tier_pair | 48 | 40 | 40 | 0.984 +/- 0.004 | 0.994 +/- 0.002 | 0.891 +/- 0.100 |
| tier_pair | 48 | 30 | 30 | 0.590 +/- 0.036 | 0.695 +/- 0.005 | 0.641 +/- 0.057 |
| tier_pair | 48 | 20 | 20 | 0.742 +/- 0.051 | 0.728 +/- 0.003 | 0.538 +/- 0.000 |
| tier_pair | 48 | 15 | 15 | 0.714 +/- 0.017 | 0.709 +/- 0.007 | 0.667 +/- 0.000 |
| tier_pair | 40 | 30 | 30 | 0.600 +/- 0.061 | 0.686 +/- 0.015 | 0.641 +/- 0.057 |
| tier_pair | 40 | 20 | 20 | 0.749 +/- 0.053 | 0.719 +/- 0.015 | 0.538 +/- 0.000 |
| tier_pair | 40 | 15 | 15 | 0.733 +/- 0.023 | 0.700 +/- 0.015 | 0.667 +/- 0.000 |
| tier_pair | 30 | 20 | 20 | 0.953 +/- 0.014 | 0.988 +/- 0.006 | 0.727 +/- 0.083 |
| tier_pair | 30 | 15 | 15 | 0.928 +/- 0.046 | 0.988 +/- 0.006 | 0.727 +/- 0.083 |
| tier_pair | 20 | 15 | 15 | 0.982 +/- 0.012 | 0.998 +/- 0.000 | 0.891 +/- 0.100 |
| same_tier_seeds | 48 | 48 | 48 | 0.944 +/- 0.020 | 0.991 +/- 0.004 | 0.776 +/- 0.109 |
| same_tier_seeds | 40 | 40 | 40 | 0.927 +/- 0.026 | 0.990 +/- 0.003 | 0.858 +/- 0.109 |
| same_tier_seeds | 30 | 30 | 30 | 0.959 +/- 0.015 | 0.986 +/- 0.005 | 0.788 +/- 0.064 |
| same_tier_seeds | 20 | 20 | 20 | 0.976 +/- 0.019 | 0.988 +/- 0.009 | 0.927 +/- 0.094 |
| same_tier_seeds | 15 | 15 | 15 | 0.971 +/- 0.016 | 0.988 +/- 0.008 | 0.836 +/- 0.058 |

