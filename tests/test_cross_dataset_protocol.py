"""Leak-free cross-dataset protocol functions, checked by hand."""
import numpy as np
import pandas as pd
import pytest

from src.evaluation import cross_dataset_protocol as cdp
from src.evaluation.cross_dataset_protocol import (
    QuantileMapper, block_mix, cap_blocks, evaluate_scores, feature_matrix, fit_adapted, fit_binary, ks_ranking, operating_threshold, score, split_positions, standardise,
    thin_blocks, type_recall, univariate_auroc,
)


def test_split_positions_are_block_disjoint_with_a_gap():
    a, b = split_positions(np.arange(20000), 0.4, seed=1)
    assert len(set(a) & set(b)) == 0 and a.min() >= 0
    gaps = [min(abs(int(x) - int(y)) for y in (b[np.searchsorted(b, x) - 1] if np.searchsorted(b, x) > 0 else -10**9, b[np.searchsorted(b, x)] if np.searchsorted(b, x) < len(b) else 10**9)) for x in a[::97]]
    assert min(gaps) > cdp.BUFFER                                                                  # no A row within 200 positions of a B row
    assert abs(len(a) / (len(a) + len(b)) - 0.4) < 0.15 and np.array_equal(a, split_positions(np.arange(20000), 0.4, seed=1)[0])
    sub = np.arange(20000)[np.arange(20000) % 3 != 0]                                               # works on a subset of rows too
    a2, b2 = split_positions(sub, 0.5, seed=2)
    assert set(a2) <= set(sub.tolist()) and set(b2) <= set(sub.tolist()) and not set(a2) & set(b2)


def test_cap_and_thin_keep_whole_blocks():
    pos = np.arange(10000)
    capped = cap_blocks(pos, 2500, seed=0)
    assert 2500 <= len(capped) <= 3500 and len(np.unique(capped // 1000)) * 1000 == len(capped)      # whole blocks of 1,000
    assert len(cap_blocks(pos, 20000, seed=0)) == 10000
    thin = thin_blocks(pos, 0.3, seed=0)
    assert len(np.unique(thin // 1000)) == 3 and len(thin) == 3000


def test_block_mix_by_hand():
    attack = np.array(["Normal"] * 1000 + ["DoS"] * 700 + ["Normal"] * 300 + ["Normal"] * 500, dtype=object)
    y = (attack != "Normal").astype(int)
    mix = block_mix(attack, y)
    assert mix["rows"].tolist() == [1000, 1000, 500] and mix["attack_share"].tolist() == [0.0, 0.7, 0.0]
    assert mix["dominant"].tolist() == ["Normal", "DoS", "Normal"] and mix["dominant_share"].tolist()[1] == 0.7


def test_evaluate_scores_by_hand_and_the_degenerate_rule():
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    s = np.array([0.1, 0.2, 0.6, 0.3, 0.9, 0.7, 0.4, 0.8])
    m = evaluate_scores(y, s, threshold=0.35)
    assert m["detection_argmax"] == 0.75 and m["fpr_argmax"] == 0.25 and m["balanced_accuracy"] == pytest.approx(0.75)
    assert m["predicted_attack_share"] == pytest.approx(4 / 8) and m["degenerate"] is False and m["auroc"] == pytest.approx(15 / 16)
    assert m["detection_at_threshold"] == 1.0 and m["fpr_at_threshold"] == 0.25                      # P >= 0.35 flags all four attacks and only the Normal flow scored 0.6
    constant = evaluate_scores(y, np.full(8, 0.01), threshold=0.35)
    assert constant["degenerate"] is True and np.isnan(constant["balanced_accuracy"]) and constant["balanced_accuracy_unranked"] == 0.5
    assert constant["auroc"] == 0.5 and np.isnan(evaluate_scores(np.zeros(5), np.random.rand(5), 0.5)["auroc"])


def test_operating_threshold_and_threshold_free_fpr():
    y = np.array([0] * 100 + [1] * 100)
    s = np.r_[np.linspace(0.0, 0.5, 100), np.linspace(0.3, 1.0, 100)]
    t = operating_threshold(y, s, 0.95)
    m = evaluate_scores(y, s, t)
    assert m["detection_at_threshold"] >= 0.95 and m["fpr_at_threshold"] == pytest.approx(m["fpr_at_95_threshold_free"]) and 0 < m["fpr_at_threshold"] < 0.6
    assert operating_threshold(np.zeros(4), np.random.rand(4)) is None


def test_type_recall_reports_only_types_with_enough_rows():
    attack = np.array(["Normal"] * 10 + ["DoS"] * 120 + ["Bot"] * 30, dtype=object)
    y = (attack != "Normal").astype(int)
    s = np.r_[np.zeros(10), np.r_[np.ones(60), np.zeros(60)], np.ones(30)]
    r = type_recall(attack, y, s, 0.5, min_rows=100)
    assert r["attack_type"].tolist() == ["DoS"] and r["recall_argmax"].iloc[0] == 0.5               # Bot has 30 rows: not reportable


def test_univariate_auroc_direction_and_absent_features():
    rng = np.random.default_rng(0)
    y = np.r_[np.zeros(500), np.ones(500)].astype(int)
    X = np.column_stack([np.r_[rng.normal(0, 1, 500), rng.normal(2, 1, 500)], np.r_[rng.normal(2, 1, 500), rng.normal(0, 1, 500)], rng.normal(0, 1, 1000), np.ones(1000)])
    r = univariate_auroc(X, y, ["up", "down", "noise", "const"]).set_index("feature")
    assert r.loc["up", "direction"] == "attack higher" and r.loc["down", "direction"] == "attack lower" and r.loc["noise", "absent"] and r.loc["const", "auroc"] == 0.5 and not r.loc["up", "absent"]


def test_alignment_transforms_by_hand():
    rng = np.random.default_rng(0)
    A, B = rng.normal(100, 20, (4000, 2)), rng.exponential(5, (4000, 2))
    z, mean, std = standardise(B)
    assert z.mean(axis=0) == pytest.approx([0, 0], abs=1e-9) and z.std(axis=0) == pytest.approx([1, 1])
    assert standardise(B, mean, std)[0] == pytest.approx(z) and standardise(np.ones((5, 1)))[0].tolist() == [[0.0]] * 5
    mapped = QuantileMapper().fit(B).transform(B)
    assert mapped.mean(axis=0) == pytest.approx([0, 0], abs=0.01) and mapped.std(axis=0) == pytest.approx([1, 1], abs=0.02)         # a normal score whatever the shape
    ties = QuantileMapper().fit(np.zeros((10, 1))).transform(np.zeros((3, 1)))
    assert np.allclose(ties, ties[0]) and abs(ties[0, 0]) < 1e-9                                      # a constant column maps to the middle
    ranking = ks_ranking(np.column_stack([A[:, 0], A[:, 1]]), np.column_stack([A[:, 0] + 0.0, B[:, 1]]), ["same", "shifted"])
    assert ranking.index[0] == "shifted" and ranking["same"] < 0.05


def test_fit_adapted_gives_the_labelled_rows_their_weight_share_and_models_score_in_0_1():
    rng = np.random.default_rng(0)
    Xs, ys = rng.normal(0, 1, (2000, 3)), (rng.random(2000) < 0.4).astype(int)
    Xa, ya = rng.normal(0, 1, (100, 3)), (rng.random(100) < 0.4).astype(int)
    from src.adaptation import adaptation_weights
    from src.preprocessing import balanced_sample_weight
    w = np.r_[balanced_sample_weight(ys, 0.5), balanced_sample_weight(ya, 0.5)]
    w = adaptation_weights(w, np.r_[np.zeros(2000, bool), np.ones(100, bool)], 0.5)
    assert w[2000:].sum() == pytest.approx(w.sum() / 2)                                              # the labelled rows carry half of the total weight
    model = fit_adapted(Xs, ys, Xa, ya, seed=1)
    p = score(model, rng.normal(0, 1, (50, 3)))
    assert ((p >= 0) & (p <= 1)).all() and fit_binary(Xs, np.zeros(2000, int), 1) is None
    sub = fit_binary(Xs, ys, 1, columns=[0, 2])
    assert score(sub, Xs[:5], columns=[0, 2]).shape == (5,)


def test_feature_matrix_has_the_14_common_features_in_order():
    df = pd.DataFrame({"dur": [1.0, 0.0], "spkts": [2, 1], "dpkts": [0, 1], "sbytes": [100, 50], "dbytes": [0, 20], "rate": [np.inf, 3.0], "smean": [50.0, 50.0], "dmean": [0.0, 20.0]})
    X = feature_matrix(df)
    assert X.shape == (2, 14) and np.isfinite(X).all() and X[0, 5] == 0.0                              # an infinite rate is cleaned to 0
    assert X[0, cdp.COMMON_FEATURES.index("total_bytes")] == 100 and X[1, cdp.COMMON_FEATURES.index("total_pkts")] == 2
