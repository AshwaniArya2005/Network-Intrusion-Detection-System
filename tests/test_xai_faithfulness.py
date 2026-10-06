"""Task 5 faithfulness machinery, checked by hand."""
import numpy as np
import pytest

from src.xai.faithfulness import (
    additivity_error, baseline_matrix, bootstrap_mean_interval, delete_features, faithfulness_curves, feature_order, insert_features, median_baseline, stratified_sample,
)


class LinearSoftmax:
    """Two classes; the margin of class 1 is x . w, so only features with weight matter."""
    def __init__(self, w):
        self.w = np.asarray(w, dtype=float)

    def predict_proba(self, X):
        z = X @ self.w
        p1 = 1 / (1 + np.exp(-z))
        return np.column_stack([1 - p1, p1])


def test_feature_order_by_hand():
    shap = np.array([[0.5, -2.0, 0.1, 1.0]])
    assert feature_order(shap, "top", np.random.default_rng(0))[0].tolist() == [3, 0, 2, 1]          # largest signed value first
    assert feature_order(shap, "least", np.random.default_rng(0))[0].tolist() == [2, 0, 3, 1]        # smallest absolute value first
    r = feature_order(np.zeros((50, 6)), "random", np.random.default_rng(1))
    assert all(sorted(row.tolist()) == list(range(6)) for row in r) and len({tuple(row) for row in r}) > 1
    with pytest.raises(ValueError):
        feature_order(shap, "bogus", np.random.default_rng(0))


def test_median_baseline_uses_the_mode_for_categorical_columns():
    X = np.array([[1.0, 5], [2.0, 5], [30.0, 7], [4.0, 5], [5.0, 7]])
    base = median_baseline(X, [1])
    assert base.tolist() == [4.0, 5.0]                                                                  # median 4; the code 5 is the most frequent
    rows = baseline_matrix("random_row", 4, X, [1], np.random.default_rng(0))
    assert rows.shape == (4, 2) and all(any((row == r).all() for r in X) for row in rows)               # whole training rows
    assert baseline_matrix("median", 3, X, [1], np.random.default_rng(0)).shape == (3, 2)


def test_delete_and_insert_by_hand():
    X = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    order = np.array([[2, 0, 1], [1, 2, 0]])
    base = np.zeros((2, 3))
    assert delete_features(X, order, 1, base).tolist() == [[1.0, 2.0, 0.0], [4.0, 0.0, 6.0]]
    assert delete_features(X, order, 2, base).tolist() == [[0.0, 2.0, 0.0], [4.0, 0.0, 0.0]]
    assert insert_features(X, order, 1, base).tolist() == [[0.0, 0.0, 3.0], [0.0, 5.0, 0.0]]
    assert X.tolist() == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]                                             # inputs are not modified


def test_faithful_explanation_beats_random_and_least_on_a_known_model():
    """Margin of class 1 = 2 * x0 + 0.05 * x1 (features 2, 3 irrelevant), features centred at 0. SHAP of a linear model = w * (x - mean). For flows predicted as class 1 the top feature is x0:
    replacing it by the median (about 0) drops P(class 1) to about 0.5, replacing an irrelevant feature changes nothing."""
    rng = np.random.default_rng(0)
    X = rng.normal(0.0, 1.0, size=(600, 4))
    model = LinearSoftmax([2.0, 0.05, 0.0, 0.0])
    pred = model.predict_proba(X).argmax(axis=1)
    keep = pred == 1
    shap = (X - X.mean(axis=0)) * np.array([2.0, 0.05, 0.0, 0.0])
    out = faithfulness_curves(model, X[keep], pred[keep], shap[keep], X, [], np.random.default_rng(1), ks=(1,), baselines=("median",))
    top, least, rand = (out["drop"][(m, "median", 1)].mean() for m in ("top", "least", "random"))
    assert top > 0.05 and top > rand and top > least                                                    # removing the feature that carries the prediction hurts most
    assert out["drop"][("least", "median", 1)].max() < 0.05                                             # the least important features are irrelevant
    assert out["flip"][("top", "median", 1)].mean() >= out["flip"][("least", "median", 1)].mean()
    # insertion: feature 0 alone on the median vector keeps most of the original probability, an irrelevant feature keeps none of it
    assert np.abs(out["p0"] - out["insertion"][("top", "median", 1)]).mean() < np.abs(out["p0"] - out["insertion"][("least", "median", 1)]).mean()


def test_a_random_explanation_is_not_better_than_random():
    rng = np.random.default_rng(2)
    X = rng.normal(2.0, 1.0, size=(3000, 4))
    model = LinearSoftmax([3.0, 0.1, 0.0, 0.0])
    pred = model.predict_proba(X).argmax(axis=1)
    junk = rng.normal(size=X.shape)                                                                     # SHAP values unrelated to the model
    out = faithfulness_curves(model, X, pred, junk, X, [], np.random.default_rng(3), ks=(1,), baselines=("median",))
    diff = out["drop"][("top", "median", 1)] - out["drop"][("random", "median", 1)]
    mean, lo, hi = bootstrap_mean_interval(diff, 500, 0)
    assert lo < 0 < hi                                                                                  # the interval includes zero: no evidence of faithfulness


def test_bootstrap_interval_contains_the_mean_and_narrows_with_more_flows():
    rng = np.random.default_rng(0)
    a, b = rng.normal(0.3, 1, 100), rng.normal(0.3, 1, 5000)
    ma, la, ha = bootstrap_mean_interval(a, 500, 1)
    mb, lb, hb = bootstrap_mean_interval(b, 500, 1)
    assert la < ma < ha and lb < mb < hb and (hb - lb) < (ha - la)
    assert bootstrap_mean_interval(a, 500, 1) == (ma, la, ha)                                           # seeded


def test_stratified_sample_caps_each_stratum_and_the_special_one():
    strata = np.array(["A"] * 50 + ["B"] * 5 + ["Unknown"] * 40)
    pick = stratified_sample(strata, 10, "Unknown", 7, np.random.default_rng(0))
    chosen = strata[pick]
    assert (chosen == "A").sum() == 10 and (chosen == "B").sum() == 5 and (chosen == "Unknown").sum() == 7     # B has only 5 flows
    assert len(set(pick.tolist())) == len(pick) and np.array_equal(pick, np.sort(pick))
    assert np.array_equal(pick, stratified_sample(strata, 10, "Unknown", 7, np.random.default_rng(0)))         # seeded


def test_additivity_error_by_hand():
    err = additivity_error(np.array([1.0, -0.5]), np.array([0.2, 0.2]), np.array([1.2, -0.3005]))
    assert err == pytest.approx([0.0, 0.0005])


def test_two_sample_bootstrap_difference():
    from src.xai.faithfulness import bootstrap_difference_interval
    rng = np.random.default_rng(0)
    same = bootstrap_difference_interval(rng.normal(0.2, 1, 2000), rng.normal(0.2, 1, 2000), 500, 1)
    assert same[1] < 0 < same[2]                                                   # two samples from one distribution: the interval includes zero
    lower = bootstrap_difference_interval(rng.normal(0.0, 1, 2000), rng.normal(0.5, 1, 2000), 500, 1)
    assert lower[0] < -0.4 and lower[2] < 0                                        # a clearly lower first sample: the interval excludes zero
    assert bootstrap_difference_interval(np.arange(10.0), np.arange(10.0) + 1, 100, 3) == bootstrap_difference_interval(np.arange(10.0), np.arange(10.0) + 1, 100, 3)   # seeded
