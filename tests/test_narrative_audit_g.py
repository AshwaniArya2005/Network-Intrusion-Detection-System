"""Check (g) and the parser for the class-relative style (Task 5.5), checked by hand against narratives from the real generator."""
import numpy as np
import pandas as pd
import pytest

from src.xai.class_reference import ClassReference
from src.xai.narrative_audit import check_category_clause, check_numeric_clause, parse_narrative
from src.xai.narrative_generator import NarrativeGenerator

FEATURES, CLASSES = ["rate", "dur", "proto"], ["Normal", "DoS"]
ACTIONS = {"DoS": "Rate-limit.", "Unknown": "Escalate."}
ALL = np.linspace(-3.0, 3.0, 1000)
DOS = ALL[ALL > 0]


@pytest.fixture
def generator():
    y = (ALL > 0).astype(int)
    proto = np.where(y == 0, np.arange(1000) % 2, 2)
    ref = ClassReference.fit(np.column_stack([ALL, ALL, proto]), y, CLASSES, FEATURES, ["proto"])
    return NarrativeGenerator(ACTIONS, style="class_relative", reference=ref)


def narrative(gen, values, shap, **kw):
    return gen.generate("DoS", 0.978, pd.Series(shap), pd.Series(values), pd.Series(0.0, index=FEATURES), pd.Series(1.0, index=FEATURES), categorical_features=frozenset({"proto"}), top_k=3, **kw)


def test_parser_reads_clauses_calibrated_estimate_and_keeps_the_reason_tuples(generator):
    text = narrative(generator, {"rate": 2.8, "dur": 1.5, "proto": 2.0}, {"rate": 2.0, "dur": 1.5, "proto": 1.0}, calibrated_confidence=0.913)
    p = parse_narrative(text, FEATURES)
    assert p["label"] == "DoS" and p["confidence_pct"] == 97.8 and p["calibrated_pct"] == 91.0 and p["action"] == "Rate-limit."
    assert [r[:2] for r in p["reasons"][:2]] == [("rate", "extremely high"), ("dur", "unusually high")]
    assert p["clauses"][0] == "higher than 97% of all flows; higher than 93% of DoS flows" and p["clauses"][1] == "higher than 75% of all flows; typical of DoS flows"
    assert p["reasons"][2][0] == "proto" and p["reasons"][2][2] == "2.0" and p["clauses"][2] == "seen in 50% of all flows; seen in 100% of DoS flows"
    classic = parse_narrative(NarrativeGenerator(ACTIONS).generate("DoS", 0.9, pd.Series({"rate": 2.0}), pd.Series({"rate": 2.8}), pd.Series(0.0, index=["rate"]), pd.Series(1.0, index=["rate"]), top_k=1), ["rate"])
    assert classic["clauses"] == [None] and classic["calibrated_pct"] is None


def test_numeric_clause_check_accepts_the_true_statement_and_rejects_wrong_ones():
    ok = check_numeric_clause("higher than 97% of all flows; higher than 93% of DoS flows", "extremely high", 2.8, ALL, DOS, "DoS", False)
    assert ok[:2] == (True, True)
    assert check_numeric_clause("higher than 75% of all flows; typical of DoS flows", "unusually high", 1.5, ALL, DOS, "DoS", False)[:2] == (True, False)
    wrong_pct = check_numeric_clause("higher than 90% of all flows; typical of DoS flows", "unusually high", 1.5, ALL, DOS, "DoS", False)
    assert wrong_pct[0] is False and "training flows give" in wrong_pct[2]
    wrong_dir = check_numeric_clause("lower than 25% of all flows; typical of DoS flows", "unusually high", 1.5, ALL, DOS, "DoS", False)
    assert wrong_dir[0] is False and "cue" in wrong_dir[2]
    false_typical = check_numeric_clause("higher than 97% of all flows; typical of DoS flows", "extremely high", 2.8, ALL, DOS, "DoS", False)
    assert false_typical[0] is False and "outside" in false_typical[2]                          # 2.8 is above the DoS upper quartile
    assert check_numeric_clause("lower than 83% of all flows; lower than 100% of DoS flows", "unusually low", -2.0, ALL, DOS, "DoS", False)[:2] == (True, True)


def test_unknown_flows_must_have_no_class_clause_and_ties_are_strict():
    assert check_numeric_clause("higher than 97% of all flows", "extremely high", 2.8, ALL, DOS, "DoS", True)[0] is True
    assert check_numeric_clause("higher than 97% of all flows; higher than 93% of DoS flows", "extremely high", 2.8, ALL, DOS, "DoS", True)[0] is False
    ties = np.array([0.0] * 80 + list(range(1, 21)), dtype=float)                                # 80% exact zeros
    assert check_numeric_clause("higher than 0% of all flows; typical of Normal flows", "elevated", 0.0, ties, ties, "Normal", False)[0] is True   # nothing is strictly below 0
    assert check_numeric_clause("higher than 80% of all flows; typical of Normal flows", "elevated", 0.0, ties, ties, "Normal", False)[0] is False


def test_category_clause_check():
    all_cat = np.array(["tcp"] * 60 + ["udp"] * 40)
    dos_cat = np.array(["tcp"] * 10 + ["udp"] * 10)
    assert check_category_clause("seen in 60% of all flows; seen in 50% of DoS flows", "tcp", all_cat, dos_cat, "DoS", False)[0] is True
    assert check_category_clause("seen in 60% of all flows; seen in 90% of DoS flows", "tcp", all_cat, dos_cat, "DoS", False)[0] is False
    assert check_category_clause("seen in 60% of all flows", "tcp", all_cat, dos_cat, "DoS", True)[0] is True
    assert check_category_clause("seen in 0% of all flows; seen in 0% of DoS flows", "weird", all_cat, dos_cat, "DoS", False)[0] is True        # a category never seen in training
