"""Task 4.5 scores, checked by hand."""
import numpy as np
import pandas as pd
import pytest

from src.openset_extra import (
    KnnScorer, MahalanobisScorer, ensemble_msp, matched_detection, member_variance, per_class_thresholds, predictive_mutual_information,
    pseudo_unknown_classes, relabel_unknown, shift_by_class, zero_day_percentile,
)


def test_per_class_thresholds_flag_the_same_share_inside_every_class_and_overall():
    rng = np.random.default_rng(0)
    scores = np.concatenate([rng.uniform(0, 1, 1000), rng.uniform(0, 0.2, 1000)])       # class 1 is far more confident than class 0
    predicted = np.r_[np.zeros(1000, int), np.ones(1000, int)]
    thr = per_class_thresholds(scores, predicted, 2, 0.05)
    assert thr[0] == pytest.approx(0.95, abs=0.03) and thr[1] == pytest.approx(0.19, abs=0.02)
    flagged = shift_by_class(scores, predicted, thr) > 0
    assert flagged[predicted == 0].mean() == pytest.approx(0.05, abs=0.005) and flagged[predicted == 1].mean() == pytest.approx(0.05, abs=0.005)
    assert flagged.mean() == pytest.approx(0.05, abs=0.005)
    one_global = scores > np.quantile(scores, 0.95)
    assert one_global[predicted == 1].mean() < 0.01                                      # a single threshold would almost never flag the confident class


def test_a_class_with_too_few_rows_uses_the_global_threshold():
    scores, predicted = np.r_[np.linspace(0, 1, 100), [0.5] * 5], np.r_[np.zeros(100, int), np.ones(5, int)]
    thr = per_class_thresholds(scores, predicted, 3, 0.05, min_rows=30)
    assert thr[1] == thr[2] == pytest.approx(np.quantile(scores, 0.95))                  # class 1 has 5 rows, class 2 none


def test_ensemble_scores_by_hand():
    agree = np.array([[[0.9, 0.1]], [[0.9, 0.1]]])                                      # 2 members, 1 row, 2 classes
    disagree = np.array([[[1.0, 0.0]], [[0.0, 1.0]]])
    assert predictive_mutual_information(agree)[0] == pytest.approx(0.0, abs=1e-9) and member_variance(agree)[0] == pytest.approx(0.0)
    assert predictive_mutual_information(disagree)[0] == pytest.approx(np.log(2), abs=1e-6)   # H([.5,.5]) - mean H(one-hot) = ln 2
    assert member_variance(disagree)[0] == pytest.approx(0.25)                          # each class probability is 0 / 1: variance 0.25
    assert ensemble_msp(disagree)[0] == pytest.approx(0.5) and ensemble_msp(agree)[0] == pytest.approx(0.1)


def test_knn_distance_by_hand():
    ref = np.array([[0.0, 0.0], [1.0, 0.0], [10.0, 0.0]])
    scorer = KnnScorer(k=2, reference_size=10, seed=0).fit(ref)
    assert scorer.score(np.array([[0.0, 0.0]]))[0] == pytest.approx((0 + 1) / 2)         # neighbours at distance 0 and 1
    assert scorer.score(np.array([[100.0, 0.0]]))[0] > scorer.score(np.array([[0.5, 0.0]]))[0]


def test_mahalanobis_is_the_minimum_over_classes_and_scales_by_the_class_spread():
    rng = np.random.default_rng(1)
    a = rng.normal([0, 0], [1.0, 1.0], size=(500, 2))
    b = rng.normal([10, 0], [1.0, 1.0], size=(500, 2))
    scorer = MahalanobisScorer(ridge=0.0).fit(np.vstack([a, b]), np.r_[np.zeros(500), np.ones(500)])
    near_b = scorer.score(np.array([[10.0, 0.0]]))[0]
    far = scorer.score(np.array([[5.0, 8.0]]))[0]
    assert near_b < 0.3 and far > 5                                                      # the distance to the nearest class, in standard deviations
    wide = MahalanobisScorer(ridge=0.0).fit(rng.normal(0, 4.0, size=(500, 2)), np.zeros(500))
    narrow = MahalanobisScorer(ridge=0.0).fit(rng.normal(0, 1.0, size=(500, 2)), np.zeros(500))
    assert narrow.score(np.array([[4.0, 0.0]]))[0] > wide.score(np.array([[4.0, 0.0]]))[0]


def test_pseudo_unknown_classes_skip_the_held_out_class_and_relabel_only_those_rows():
    assert pseudo_unknown_classes(["Worms", "Shellcode"]) == ["Reconnaissance", "Generic"]
    assert pseudo_unknown_classes(["Generic"]) == ["Reconnaissance", "Fuzzers"]
    assert pseudo_unknown_classes(["Reconnaissance", "Generic"]) == ["Fuzzers", "Exploits"]
    frame = pd.DataFrame({"label_merged": ["Normal", "Generic", "Fuzzers"], "attack_cat": ["Normal", "Generic", "Fuzzers"]})
    out = relabel_unknown(frame, ["Generic"], "label_merged", "attack_cat")
    assert out["label_merged"].tolist() == ["Normal", "Unknown", "Fuzzers"] and out["attack_cat"].tolist() == ["Normal", "Generic", "Fuzzers"]
    assert frame["label_merged"].tolist() == ["Normal", "Generic", "Fuzzers"]            # the input is untouched


def test_percentile_and_matched_detection_by_hand():
    known = np.arange(100, dtype=float)                                                  # 0..99
    assert zero_day_percentile(known, np.array([50.0])) == pytest.approx(0.5)
    assert zero_day_percentile(known, np.array([-1.0, 200.0])) == pytest.approx((0.0 + 1.0) / 2)
    assert matched_detection(known, np.array([10.0, 96.0, 99.5]), 0.05) == pytest.approx(2 / 3)   # the 95% quantile of 0..99 is 94.05
