# Task 4.5: iforest

## isolation-forest sign check (40f, mean over seeds 42-46)

Worms + Shellcode held out.

| score | known attacks vs Normal (AUROC) | Worms: mean percentile among known test flows | Shellcode: mean percentile |
|---|---|---|---|
| iforest | 0.672 +/- 0.012 | 0.684 +/- 0.023 | 0.407 +/- 0.021 |
| knn | 0.675 +/- 0.010 | 0.633 +/- 0.007 | 0.387 +/- 0.008 |
| maha | 0.411 +/- 0.005 | 0.510 +/- 0.003 | 0.307 +/- 0.005 |

Known attacks vs Normal, averaged over the nine rotation runs: iforest AUROC 0.668; knn AUROC 0.666; maha AUROC 0.403.

## isolation-forest sign check (48f, mean over seeds 42-46)

Worms + Shellcode held out.

| score | known attacks vs Normal (AUROC) | Worms: mean percentile among known test flows | Shellcode: mean percentile |
|---|---|---|---|
| iforest | 0.724 +/- 0.014 | 0.707 +/- 0.007 | 0.473 +/- 0.031 |
| knn | 0.635 +/- 0.010 | 0.515 +/- 0.008 | 0.288 +/- 0.007 |
| maha | 0.429 +/- 0.005 | 0.477 +/- 0.002 | 0.283 +/- 0.005 |

Known attacks vs Normal, averaged over the nine rotation runs: iforest AUROC 0.719; knn AUROC 0.625; maha AUROC 0.419.

