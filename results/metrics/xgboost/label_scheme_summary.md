# Label scheme comparison (report only; the choice of scheme is the team's)

Compare schemes on the scheme-independent columns below. Macro F1 is NOT comparable across schemes
(it averages over 6, 8, 5 classes for current, none, wide), and
`best_possible_accuracy` rises mechanically with coarser labels: it measures what a merge discards,
not which merge is right. `group_size_share` is the share of attack rows inside a merged group, so a
high value means the scheme lumps most attack traffic together. Ranks: 1 = best.

## Official train/test split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9607               0.2860             0.7859            0.1193                       2                         1                            0.9117
        none          8          0.9622               0.2895             0.6327            0.0000                       3                         2                            0.9052
        wide          5          0.9598               0.2895             0.8590            0.4848                       1                         2                            0.9690
```

Recall of each ORIGINAL class under each scheme (share of its rows predicted as the label that contains it):
```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.8721                0.9449           0.5437                0.8221               0.7538               0.8596                      0.7768              0.7140
        none                0.3699                0.5072           0.2591                0.8236               0.7553               0.8575                      0.7785              0.7105
        wide                0.9749                0.9710           0.9044                0.9141               0.7476               0.8675                      0.7821              0.7105
```

## Pooled random split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9320               0.1197             0.7898            0.1248                       2                         2                            0.9117
        none          8          0.9330               0.1204             0.6060            0.0000                       3                         3                            0.9052
        wide          5          0.9375               0.1180             0.8548            0.4887                       1                         1                            0.9690
```

```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.8325                0.9005           0.5264                0.8234               0.7142               0.8993                      0.7417              0.8803
        none                0.2759                0.2793           0.2545                0.8152               0.7109               0.8888                      0.7437              0.8796
        wide                0.8515                0.9449           0.8897                0.9132               0.7188               0.8895                      0.7487              0.8820
```
