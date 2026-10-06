"""Helpers of scripts/diagnose_normal_fuzzers.py."""
import numpy as np
import pandas as pd

from scripts.diagnose_normal_fuzzers import cv_auc, distance, twin_shares


def test_distance_ks_for_numeric_and_total_variation_for_categorical():
    a, b = pd.Series([1.0, 2.0, 3.0]), pd.Series([10.0, 11.0, 12.0])
    assert distance(a, a, False) == 0.0 and distance(a, b, False) == 1.0  # identical / disjoint
    ca, cb = pd.Series(["tcp"] * 3 + ["udp"]), pd.Series(["tcp"] * 2 + ["udp"] * 2)
    assert abs(distance(ca, cb, True) - 0.25) < 1e-9  # |0.75-0.5|/2 + |0.25-0.5|/2


def test_twin_shares_counts_exact_and_near_twins_by_hand():
    cols = ["dur", "sbytes", "proto"]
    normal = pd.DataFrame({"dur": [1.0, 5.0, 100.0], "sbytes": [10.0, 50.0, 1000.0], "proto": ["tcp"] * 3})
    fuzz = pd.DataFrame({"dur": [1.0, 5.1, 7000.0], "sbytes": [10.0, 50.0, 9e6], "proto": ["tcp", "tcp", "tcp"]})
    nf = np.array([True, True, False])  # first two Normal rows are "called Fuzzers"
    out = twin_shares(normal, fuzz, nf, cols, cols)
    assert out["exact_twin_in_fuzzers_NF_pct"] == 50.0 and out["exact_twin_in_fuzzers_NN_pct"] == 0.0
    assert out["near_twin_0.25_in_fuzzers_NF_pct"] == 100.0 and out["near_twin_0.25_in_fuzzers_NN_pct"] == 0.0


def test_cv_auc_is_half_for_identical_populations_and_high_for_shifted_ones():
    rng = np.random.default_rng(0)
    make = lambda shift: pd.DataFrame({"x": rng.normal(shift, 1, 600), "y": rng.normal(0, 1, 600)})  # noqa: E731
    same, _ = cv_auc(make(0), make(0), ["x", "y"])
    shifted, importance = cv_auc(make(0), make(3), ["x", "y"])
    assert abs(same - 0.5) < 0.08 and shifted > 0.95 and importance.index[0] == "x"
