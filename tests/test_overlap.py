"""Overlap analysis: exact/near twins and the best-possible accuracy, checked by hand."""
import pandas as pd
import pytest

from src.evaluation.overlap import (
    analyse, best_possible_accuracy, exact_twin_matrix, largest_multilabel_vector, near_twin_rates,
)

FEATURES = ["x", "y"]


@pytest.fixture
def toy():
    # vector (1,1): A x3, B x1 ; vector (2,2): B x2 ; vector (3,3): A x1  -> 7 rows
    rows = [(1, 1, "A")] * 3 + [(1, 1, "B")] + [(2, 2, "B")] * 2 + [(3, 3, "A")]
    return pd.DataFrame(rows, columns=["x", "y", "label"])


def test_best_possible_accuracy_by_hand(toy):
    assert best_possible_accuracy(toy, FEATURES, "label") == pytest.approx(6 / 7)  # (3 + 2 + 1) / 7
    # distinct (vector, label) pairs: (1,1)A (1,1)B (2,2)B (3,3)A -> ties pick one: (1 + 1 + 1) / 4
    assert best_possible_accuracy(toy, FEATURES, "label", dedup_pairs=True) == pytest.approx(3 / 4)
    toy["merged"] = "same"
    assert best_possible_accuracy(toy, FEATURES, "merged") == 1.0  # a coarser label raises the ceiling


def test_exact_twin_matrix_by_hand(toy):
    rows_pct, vecs_pct = exact_twin_matrix(toy, FEATURES, "label")
    assert rows_pct.loc["A", "B"] == pytest.approx(75.0)   # 3 of A's 4 rows share vector (1,1) with B
    assert vecs_pct.loc["A", "B"] == pytest.approx(50.0)   # 1 of A's 2 distinct vectors
    assert rows_pct.loc["B", "any_other"] == pytest.approx(100 / 3, abs=0.01)


def test_largest_multilabel_vector(toy):
    assert largest_multilabel_vector(toy, FEATURES, "label")["label_counts"] == {"A": 3, "B": 1}


def test_near_twins_require_matching_categoricals_and_distance():
    df = pd.DataFrame({"dur": [1.0, 1.0, 1.0, 50.0], "proto": ["tcp", "tcp", "udp", "tcp"],
                       "label": ["A", "B", "B", "B"]})
    rates = near_twin_rates(df, ["dur", "proto"], "label")
    assert rates.loc["A", "within_0.05"] == 100.0  # (1.0, tcp) has an identical twin in B
    far = df.assign(proto=["tcp", "udp", "udp", "udp"])  # only a different protocol sits at the same dur
    assert near_twin_rates(far, ["dur", "proto"], "label").loc["A", "within_0.25"] == 0.0


def test_analyse_covers_every_label_set(toy):
    toy["merged"] = "same"
    result = analyse(toy, FEATURES, {"original": "label", "merged": "merged"}, near=False)
    assert list(result["ceilings"]["label_scheme"]) == ["original", "merged"]
    assert set(result["twin_rows"]) == {"original", "merged"}
