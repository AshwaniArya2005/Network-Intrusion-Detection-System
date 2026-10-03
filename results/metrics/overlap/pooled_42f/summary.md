# Overlap analysis

Partition: pooled; 255988 known-class rows (duplicates kept); 42 features (all loaded): dur, proto, service, state, spkts, dpkts, sbytes, dbytes, rate, sttl, dttl, sload, dload, sloss, dloss, sinpkt, dinpkt, sjit, djit, swin, dwin, stcpb, dtcpb, tcprtt, synack, ackdat, smean, dmean, trans_depth, response_body_len, ct_srv_src, ct_state_ttl, ct_dst_ltm, ct_src_dport_ltm, ct_dst_sport_ltm, ct_dst_src_ltm, is_ftp_login, ct_ftp_cmd, ct_flw_http_mthd, ct_src_ltm, ct_srv_dst, is_sm_ips_ports.

## Best-possible accuracy

```
label_scheme  n_classes  best_possible_accuracy_dups_kept  best_possible_accuracy_pairs_deduped
    original          8                            0.9134                                0.9439
     current          6                            0.9212                                0.9624
        none          8                            0.9134                                0.9439
      binary          2                            0.9974                                0.9973
```

## Exact twins, label set 'original' (% of rows / % of distinct vectors with a twin in another class)

```
                rows_pct  vectors_pct
Analysis           76.99        77.85
Backdoor           84.89        81.38
DoS                77.41        34.04
Exploits           37.04         7.18
Fuzzers            14.92        10.55
Generic             0.63         4.15
Normal              1.00         0.48
Reconnaissance     16.06        15.73
```

Largest multi-label vector ('original'): label counts {'Analysis': 10, 'Backdoor': 10, 'DoS': 66, 'Exploits': 76, 'Fuzzers': 10, 'Generic': 6, 'Reconnaissance': 10}

## Exact twins, label set 'current' (% of rows / % of distinct vectors with a twin in another class)

```
                 rows_pct  vectors_pct
Exploits            37.04         7.18
Fuzzers             14.92        10.55
Generic              0.63         4.15
Normal               1.00         0.48
Overlap-Group-1     78.16        29.82
Reconnaissance      16.06        15.73
```

Largest multi-label vector ('current'): label counts {'Exploits': 76, 'Fuzzers': 10, 'Generic': 6, 'Overlap-Group-1': 86, 'Reconnaissance': 10}

## Exact twins, label set 'none' (% of rows / % of distinct vectors with a twin in another class)

```
                rows_pct  vectors_pct
Analysis           76.99        77.85
Backdoor           84.89        81.38
DoS                77.41        34.04
Exploits           37.04         7.18
Fuzzers            14.92        10.55
Generic             0.63         4.15
Normal              1.00         0.48
Reconnaissance     16.06        15.73
```

Largest multi-label vector ('none'): label counts {'Analysis': 10, 'Backdoor': 10, 'DoS': 66, 'Exploits': 76, 'Fuzzers': 10, 'Generic': 6, 'Reconnaissance': 10}

## Exact twins, label set 'binary' (% of rows / % of distinct vectors with a twin in another class)

```
   rows_pct  vectors_pct
0      1.00         0.48
1      0.51         0.62
```

Largest multi-label vector ('binary'): label counts {0: 14, 1: 20}
