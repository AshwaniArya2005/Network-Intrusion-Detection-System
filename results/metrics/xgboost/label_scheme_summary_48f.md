# Label scheme comparison (report only; the choice of scheme is the team's)

Compare schemes on the scheme-independent columns below. Macro F1 is NOT comparable across schemes
(it averages over 6, 8, 5 classes for current, none, wide), and
`best_possible_accuracy` rises mechanically with coarser labels: it measures what a merge discards,
not which merge is right. `group_size_share` is the share of attack rows inside a merged group, so a
high value means the scheme lumps most attack traffic together. Ranks: 1 = best.

## Official train/test split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9674               0.2947             0.7645            0.1193                       2                         1                            0.9212
        none          8          0.9688               0.3013             0.6291            0.0000                       3                         3                            0.9134
        wide          5          0.9677               0.2947             0.8521            0.4848                       1                         1                            0.9764
```

Recall of each ORIGINAL class under each scheme (share of its rows predicted as the label that contains it):
```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.7785                0.8319           0.5691                0.8544               0.7343               0.8628                      0.7797              0.7053
        none                0.3539                0.4551           0.3081                0.8518               0.7204               0.8631                      0.7821              0.6987
        wide                0.9315                0.9449           0.9333                0.9410               0.7198               0.8631                      0.7780              0.7053
```

## Pooled random split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9428               0.0961             0.8061            0.1248                       2                         1                            0.9212
        none          8          0.9407               0.0992             0.5947            0.0000                       3                         3                            0.9134
        wide          5          0.9448               0.0972             0.8586            0.4887                       1                         2                            0.9764
```

```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.8300                0.9084           0.5855                0.8467               0.7281               0.9026                      0.7437              0.9039
        none                0.1429                0.1968           0.3100                0.8376               0.7266               0.8895                      0.7533              0.9008
        wide                0.8144                0.9284           0.9253                0.9272               0.7278               0.8908                      0.7523              0.9028
```
