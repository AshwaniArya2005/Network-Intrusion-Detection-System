"""Mutual-information ranking: categorical handling and redundancy-aware ordering."""
import numpy as np
import pandas as pd

from src.data_loader import make_synthetic_unsw
from src.feature_selection import compute_feature_ranking, redundancy_reorder


def test_categorical_feature_that_determines_the_target_ranks_first():
    """proto/service/state are label-encoded integers; estimated as continuous their MI is
    meaninglessly low (they ranked 26th-28th on real data). They must be treated as discrete."""
    rng = np.random.default_rng(0)
    df = make_synthetic_unsw(n_rows=3000, seed=4)
    codes = rng.permutation(12)  # codes whose integer order carries no information
    df["service"] = [f"svc{c}" for c in rng.integers(0, 12, len(df))]
    df["attack_cat"] = [f"c{codes[int(s[3:])] % 4}" for s in df["service"]]
    ranking = compute_feature_ranking(df, ["rate", "dur", "sbytes", "dbytes", "service"], "attack_cat", seed=1)
    assert ranking.index[0] == "service"


def test_redundancy_reorder_defers_correlated_features():
    rng = np.random.default_rng(0)
    a = rng.normal(size=500)
    X = np.column_stack([a, a * 2 + 0.01 * rng.normal(size=500), rng.normal(size=500)])
    ranking = pd.Series([3.0, 2.0, 1.0], index=["a", "a_copy", "indep"])
    assert list(redundancy_reorder(ranking, X, list(ranking.index), 0.8).index) == ["a", "indep", "a_copy"]


def test_mutual_info_is_told_which_features_are_discrete(monkeypatch):
    """The label-encoded proto/service/state columns must go to mutual_info_classif as discrete."""
    import src.feature_selection as fs

    seen = {}
    real = fs.mutual_info_classif

    def spy(X, y, discrete_features=None, random_state=None):
        seen["mask"] = discrete_features
        return real(X, y, discrete_features=discrete_features, random_state=random_state)

    monkeypatch.setattr(fs, "mutual_info_classif", spy)
    df = make_synthetic_unsw(n_rows=500, seed=1)
    compute_feature_ranking(df, ["rate", "proto", "service", "dur", "state"], "attack_cat")
    assert list(seen["mask"]) == [False, True, True, False, True]
