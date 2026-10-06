"""Class-relative narrative style (the narrative study), checked by hand; the classic style must be unchanged."""
import numpy as np
import pandas as pd
import pytest

from src.xai.class_reference import ClassReference
from src.xai.narrative_generator import NarrativeGenerator

FEATURES, CLASSES = ["rate", "dur", "proto"], ["Normal", "DoS"]
ACTIONS = {"DoS": "Rate-limit.", "Normal": "No action required.", "Unknown": "Escalate."}


@pytest.fixture
def reference():
    n = 1000
    rate = np.linspace(-3.0, 3.0, n)                                   # standardised-like values; Normal = the lower half, DoS = the upper half
    y = (rate > 0).astype(int)
    dur = np.linspace(-3.0, 3.0, n)
    proto = np.where(y == 0, np.arange(n) % 2, 2)                      # Normal: codes 0 / 1; DoS: code 2
    return ClassReference.fit(np.column_stack([rate, dur, proto]), y, CLASSES, FEATURES, ["proto"])


def make(reference, **kw):
    return NarrativeGenerator(ACTIONS, style="class_relative", reference=reference).generate(
        kw.pop("label", "DoS"), 0.978, pd.Series(kw.pop("shap")), pd.Series(kw.pop("values")), pd.Series(0.0, index=FEATURES), pd.Series(1.0, index=FEATURES),
        categorical_features=frozenset({"proto"}), top_k=3, **kw)


def test_typical_features_are_omitted_and_the_rest_get_overall_and_class_clauses(reference):
    text = make(reference, shap={"rate": 2.0, "dur": 1.5, "proto": 1.0}, values={"rate": 2.8, "dur": 0.1, "proto": 2.0})
    assert "flow duration" not in text                                                           # |z| = 0.1 reads "typical": omitted
    assert "extremely high packet rate (higher than 97% of all flows; higher than 93% of DoS flows)" in text   # 2.8: above 97% of all flows, above the DoS upper quartile
    assert "network protocol=2.0 (seen in 50% of all flows; seen in 100% of DoS flows)" in text  # no decoder here: the raw code is shown


def test_inside_the_class_interquartile_range_says_typical_of_the_class(reference):
    text = make(reference, shap={"rate": 2.0}, values={"rate": 1.5})
    assert "unusually high packet rate (higher than 75% of all flows; typical of DoS flows)" in text
    low = make(reference, label="Normal", shap={"rate": 2.0}, values={"rate": -2.0})
    assert "unusually low packet rate (lower than 83% of all flows; typical of Normal flows)" in low
    below = make(reference, shap={"rate": 2.0}, values={"rate": -2.0})                           # predicted DoS but the value is far below every DoS flow
    assert "lower than 100% of DoS flows" in below


def test_unknown_flows_get_no_class_clause_and_the_unrecognized_wording(reference):
    text = make(reference, shap={"rate": 2.0, "proto": 1.0}, values={"rate": 2.8, "proto": 2.0}, is_unknown=True)
    assert "unrecognized" in text and "of DoS flows" not in text and "typical of" not in text
    assert "extremely high packet rate (higher than 97% of all flows)" in text and "(seen in 50% of all flows)" in text


def test_when_every_cited_feature_is_typical_the_pattern_is_called_diffuse(reference):
    text = make(reference, shap={"rate": 2.0, "dur": 1.0}, values={"rate": 0.1, "dur": -0.2})
    assert "diffuse" in text and "Main reasons" not in text and "Suggested action: Rate-limit." in text


def test_calibrated_confidence_is_added_next_to_the_raw_one_with_a_caution(reference):
    text = make(reference, shap={"rate": 2.0}, values={"rate": 2.8}, calibrated_confidence=0.913)
    assert text.startswith("This flow was flagged as DoS with 97.8% confidence. Calibrated estimate: about 91% (the model's raw probability tends to be too high")
    assert "estimates, not guarantees" in text
    classic = NarrativeGenerator(ACTIONS).generate("DoS", 0.978, pd.Series({"rate": 2.0}), pd.Series({"rate": 2.8}), pd.Series(0.0, index=["rate"]), pd.Series(1.0, index=["rate"]),
                                                   top_k=1, calibrated_confidence=0.913)
    assert "Calibrated" not in classic                                                          # the classic style ignores it


def test_classic_style_is_unchanged_and_the_style_is_validated(reference):
    classic = NarrativeGenerator(ACTIONS).generate("DoS", 0.978, pd.Series({"rate": 2.0, "dur": 1.5}), pd.Series({"rate": 2.8, "dur": 0.1}), pd.Series(0.0, index=["rate", "dur"]),
                                                   pd.Series(1.0, index=["rate", "dur"]), top_k=2)
    assert classic == "This flow was flagged as DoS with 97.8% confidence. Main reasons: extremely high packet rate, typical flow duration. Suggested action: Rate-limit."
    with pytest.raises(ValueError):
        NarrativeGenerator(ACTIONS, style="bogus")
    with pytest.raises(ValueError):
        NarrativeGenerator(ACTIONS, style="class_relative")                                      # needs a reference
