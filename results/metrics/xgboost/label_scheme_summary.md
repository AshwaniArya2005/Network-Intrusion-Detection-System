# Label scheme comparison (report only; the choice of scheme is the team's)

Compare schemes on the scheme-independent columns below. Macro F1 is NOT comparable across schemes
(it averages over 6, 8, 5, 8 classes for current, none, wide, hierarchical), and
`best_possible_accuracy` rises mechanically with coarser labels: it measures what a merge discards,
not which merge is right. `group_size_share` is the share of attack rows inside a merged group, so a
high value means the scheme lumps most attack traffic together. Ranks: 1 = best.

## Official train/test split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9552               0.2761             0.7555            0.1234                       2                         2                            0.9117
        none          8          0.9548               0.2776             0.6114            0.0000                       3                         3                            0.9052
        wide          5          0.9570               0.2836             0.8319            0.5584                       1                         4                            0.9690
hierarchical          8          0.9254               0.2076             0.6085            0.0000                       4                         1                            0.9052
```

Recall of each ORIGINAL class under each scheme (share of its rows predicted as the label that contains it):
```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.8266                0.9403           0.5040                0.8399               0.7691               0.6539                      0.7863              0.7239
        none                0.3437                0.5000           0.2979                0.8380               0.7733               0.6309                      0.7853              0.7224
        wide                0.9598                0.9627           0.8896                0.9108               0.7738               0.6547                      0.7873              0.7164
hierarchical                0.3251                0.5261           0.2919                0.8353               0.6696               0.6404                      0.7873              0.7924
```

## Pooled random split
```
label_scheme  n_classes  detection_rate  false_positive_rate  fine_recall_macro  group_size_share  rank_fine_recall_macro  rank_false_positive_rate  best_possible_accuracy_dups_kept
     current          6          0.9307               0.1109             0.7715            0.1207                       2                         3                            0.9117
        none          8          0.9297               0.1152             0.5799            0.0000                       3                         4                            0.9052
        wide          5          0.9281               0.1085             0.8096            0.5398                       1                         2                            0.9690
hierarchical          8          0.8892               0.0717             0.5642            0.0000                       4                         1                            0.9052
```

```
label_scheme  fine_recall_Analysis  fine_recall_Backdoor  fine_recall_DoS  fine_recall_Exploits  fine_recall_Fuzzers  fine_recall_Generic  fine_recall_Reconnaissance  fine_recall_Normal
     current                0.7865                0.9011           0.4882                0.8441               0.7311               0.7594                      0.7728              0.8891
        none                0.1458                0.2482           0.2646                0.8305               0.7314               0.7594                      0.7747              0.8848
        wide                0.7313                0.8707           0.8546                0.9027               0.7158               0.7316                      0.7784              0.8915
hierarchical                0.1076                0.2374           0.2738                0.8288               0.6123               0.7545                      0.7709              0.9283
```
