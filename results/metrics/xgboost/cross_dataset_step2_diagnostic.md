# Task 6 Step 2: why zero-shot fails (diagnostic)

AUROC of each common feature alone for attack against normal (all rows of each dataset; above 0.5 = attack flows have higher values). `absent` = |AUROC - 0.5| < 0.05 in at least one dataset.

| feature | UNSW | CIC | same direction | absent in either dataset | flipped (clear and opposite) |
|---|---|---|---|---|---|
| avg_pkt_size | 0.445 | 0.521 | no | yes | no |
| byte_ratio | 0.470 | 0.278 | yes | yes | no |
| dbytes | 0.362 | 0.543 | no | yes | no |
| dmean | 0.302 | 0.561 | no | no | yes |
| dpkts | 0.367 | 0.489 | yes | yes | no |
| dur | 0.560 | 0.542 | yes | yes | no |
| duration_log | 0.560 | 0.542 | yes | yes | no |
| pkt_ratio | 0.499 | 0.429 | yes | yes | no |
| rate | 0.441 | 0.440 | yes | no | no |
| sbytes | 0.416 | 0.363 | yes | no | no |
| smean | 0.526 | 0.343 | no | yes | no |
| spkts | 0.404 | 0.547 | no | yes | no |
| total_bytes | 0.398 | 0.509 | no | yes | no |
| total_pkts | 0.382 | 0.525 | no | yes | no |

Of 14 features: 7 point the same way, 7 do not, 11 are absent (near 0.5) in at least one dataset and 1 are clearly flipped. SHAP importance rank agreement between a UNSW-trained and a CIC-trained model on the common features: Spearman 0.52 +/- 0.05 over 5 seeds.

Zero-shot AUROC of the common_all model: CIC -> UNSW 0.578 +/- 0.019; UNSW -> CIC 0.485 +/- 0.023.

