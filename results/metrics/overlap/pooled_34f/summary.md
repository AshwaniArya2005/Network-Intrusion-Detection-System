# Overlap analysis

Partition: pooled; 255988 known-class rows (duplicates kept); 34 features (base 34): dur, proto, service, state, spkts, dpkts, sbytes, dbytes, rate, sload, dload, sloss, dloss, sinpkt, dinpkt, sjit, djit, swin, dwin, stcpb, dtcpb, tcprtt, synack, ackdat, smean, dmean, trans_depth, response_body_len, ct_src_dport_ltm, ct_dst_sport_ltm, is_ftp_login, ct_ftp_cmd, ct_flw_http_mthd, is_sm_ips_ports.

## Best-possible accuracy

```
label_scheme  n_classes  best_possible_accuracy_dups_kept  best_possible_accuracy_pairs_deduped
    original          8                            0.9052                                0.9565
     current          6                            0.9117                                0.9702
        none          8                            0.9052                                0.9565
      binary          2                            0.9903                                0.9971
```

## Exact twins, label set 'original' (% of rows / % of distinct vectors with a twin in another class)

```
                rows_pct  vectors_pct
Analysis           76.99        69.56
Backdoor           84.89        74.80
DoS                77.75        27.03
Exploits           37.14         5.25
Fuzzers            23.93         8.85
Generic             0.71         8.86
Normal              4.23         0.51
Reconnaissance     33.78        13.39
```

Largest multi-label vector ('original'): label counts {'Analysis': 95, 'Backdoor': 84, 'DoS': 637, 'Exploits': 803, 'Fuzzers': 97, 'Generic': 21, 'Reconnaissance': 104}

## Exact twins, label set 'current' (% of rows / % of distinct vectors with a twin in another class)

```
                 rows_pct  vectors_pct
Exploits            37.14         5.25
Fuzzers             23.93         8.85
Generic              0.71         8.86
Normal               4.23         0.51
Overlap-Group-1     78.42        23.39
Reconnaissance      33.78        13.39
```

Largest multi-label vector ('current'): label counts {'Exploits': 803, 'Fuzzers': 97, 'Generic': 21, 'Overlap-Group-1': 816, 'Reconnaissance': 104}

## Exact twins, label set 'none' (% of rows / % of distinct vectors with a twin in another class)

```
                rows_pct  vectors_pct
Analysis           76.99        69.56
Backdoor           84.89        74.80
DoS                77.75        27.03
Exploits           37.14         5.25
Fuzzers            23.93         8.85
Generic             0.71         8.86
Normal              4.23         0.51
Reconnaissance     33.78        13.39
```

Largest multi-label vector ('none'): label counts {'Analysis': 95, 'Backdoor': 84, 'DoS': 637, 'Exploits': 803, 'Fuzzers': 97, 'Generic': 21, 'Reconnaissance': 104}

## Exact twins, label set 'binary' (% of rows / % of distinct vectors with a twin in another class)

```
   rows_pct  vectors_pct
0      4.23         0.51
1      3.22         0.70
```

Largest multi-label vector ('binary'): label counts {0: 2, 1: 1179}
