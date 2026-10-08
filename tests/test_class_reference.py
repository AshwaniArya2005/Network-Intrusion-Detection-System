"""Class reference (percentiles, quartiles, category shares), checked by hand."""
import numpy as np
import pytest

from src.xai.class_reference import ClassReference

FEATURES, CLASSES = ["rate", "dur", "proto"], ["Normal", "DoS"]


def reference():
    n = 1000
    rate = np.arange(n, dtype=float)                                   # 0..999
    dur = np.where(np.arange(n) < 800, 0.0, np.arange(n) - 799.0)      # 80% exact zeros: heavy ties
    y = (np.arange(n) >= 500).astype(int)                              # first half Normal, second half DoS
    proto = np.where(y == 0, np.arange(n) % 2, 2)                      # Normal: codes 0 / 1 half each; DoS: always code 2
    X = np.column_stack([rate, dur, proto])
    return ClassReference.fit(X, y, CLASSES, FEATURES, ["proto"])


def test_shares_below_and_above_by_hand():
    ref = reference()
    assert ref.share_below("rate", 500.0) == pytest.approx(0.5, abs=0.002)                       # strictly smaller values: 0..499
    assert ref.share_above("rate", 500.0) == pytest.approx(0.499, abs=0.002)                     # 501..999
    assert ref.share_below("rate", 500.0, "DoS") == pytest.approx(0.0, abs=0.002)                # no DoS flow below 500
    assert ref.share_below("rate", 750.0, "DoS") == pytest.approx(0.5, abs=0.003)
    assert ref.share_below("rate", 5000.0) == 1.0 and ref.share_above("rate", 5000.0) == 0.0     # outside the training range
    assert ref.share_below("rate", -1.0) == 0.0 and ref.share_above("rate", -1.0) == pytest.approx(1.0, abs=0.002)


def test_ties_are_strict_so_a_common_value_is_not_called_higher_than_most_flows():
    ref = reference()
    assert ref.share_below("dur", 0.0) == 0.0                                                    # 80% of flows equal 0: none is strictly smaller
    assert ref.share_above("dur", 0.0) == pytest.approx(0.2, abs=0.003)
    assert ref.share_below("dur", 100.0) == pytest.approx(0.899, abs=0.003)                  # 800 zeros + the values 1..99


def test_quartiles_by_hand():
    ref = reference()
    q25, q75 = ref.quartiles("rate")
    assert q25 == pytest.approx(249.75) and q75 == pytest.approx(749.25)
    q25, q75 = ref.quartiles("rate", "DoS")
    assert q25 == pytest.approx(624.75, abs=0.5) and q75 == pytest.approx(874.25, abs=0.5)


def test_category_shares_overall_per_class_and_for_an_unseen_code():
    ref = reference()
    assert ref.category_share("proto", 2) == pytest.approx(0.5) and ref.category_share("proto", 0) == pytest.approx(0.25)
    assert ref.category_share("proto", 2, "DoS") == 1.0 and ref.category_share("proto", 2, "Normal") == 0.0
    assert ref.category_share("proto", 99) == 0.0 and ref.category_share("proto", 3) == 0.0       # a code never seen in training


def test_save_and_load_round_trip_without_pickle(tmp_path):
    ref = reference()
    path = tmp_path / "ref.npz"
    ref.save(path)
    again = ClassReference.load(path)
    assert again.feature_names == FEATURES and again.class_names == CLASSES and again.categorical == ["proto"]
    assert again.share_below("rate", 500.0) == ref.share_below("rate", 500.0)
    assert again.quartiles("rate", "DoS") == ref.quartiles("rate", "DoS") and again.category_share("proto", 2, "DoS") == 1.0
