"""SHAP explainer (per model), narrative generator, and stability metrics."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.xai.explanation_stability import compare_importances, run_stability_study
from src.xai.narrative_generator import NarrativeGenerator
from src.xai.shap_explainer import SHAPExplainer
from tests.conftest import N_CLASSES, N_FEATURES


# --- SHAPExplainer: must work for every model type --------------------------

def test_shap_global_importance(fitted_model, data, feature_names):
    X, _ = data
    imp = SHAPExplainer(fitted_model, feature_names).global_importance(X)
    assert sorted(imp.index) == sorted(feature_names)
    assert np.all(np.isfinite(imp)) and (imp >= 0).all()
    assert imp.is_monotonic_decreasing


def test_shap_per_class_shapes(fitted_model, data, feature_names):
    X, _ = data
    per_class = SHAPExplainer(fitted_model, feature_names).compute_shap_values(X)
    assert len(per_class) == N_CLASSES
    assert all(c.shape[1] == N_FEATURES for c in per_class)


def test_shap_local_explanation(fitted_model, data, feature_names):
    X, _ = data
    explainer = SHAPExplainer(fitted_model, feature_names)
    explainer.global_importance(X)  # gives non-tree explainers a proper background
    row = X[:1]
    local = explainer.local_explanation(row, int(fitted_model.predict(row)[0]))
    assert list(local.index) == feature_names and np.all(np.isfinite(local))
    top = SHAPExplainer.top_k(local, 3)
    assert len(top) == 3 and top.abs().is_monotonic_decreasing


# --- NarrativeGenerator (model-independent) ---------------------------------

def _shap(**vals) -> pd.Series:
    return pd.Series(vals)


def test_narrative_names_label_confidence_and_action():
    gen = NarrativeGenerator({"DoS": "Rate-limit the source."})
    text = gen.generate("DoS", 0.978, _shap(rate=2.0, dur=-1.0))
    assert "DoS" in text and "97.8%" in text and "packet rate" in text
    assert "Rate-limit the source." in text
    assert "flow duration" not in text  # negative contribution is not a reason


def test_narrative_unknown_uses_zero_day_wording_and_unknown_action():
    gen = NarrativeGenerator({"Unknown": "Escalate.", "DoS": "Rate-limit."})
    text = gen.generate("DoS", 0.4, _shap(rate=1.0), is_unknown=True)
    assert "zero-day" in text and "Escalate." in text and "Rate-limit." not in text


def test_narrative_diffuse_when_no_positive_contributions():
    assert "diffuse" in NarrativeGenerator().generate("DoS", 0.9, _shap(rate=-1.0, dur=-0.5))


def test_narrative_magnitude_and_categorical():
    gen = NarrativeGenerator()
    text = gen.generate("DoS", 0.9, _shap(rate=1.0, proto=0.5),
                        feature_values=pd.Series({"rate": 10.0, "proto": 2}),
                        feature_means=pd.Series({"rate": 0.0}), feature_stds=pd.Series({"rate": 1.0}),
                        categorical_features={"proto"})
    assert "extremely high packet rate" in text and "network protocol=2" in text


def test_narrative_batch_length():
    shap_df = pd.DataFrame({"rate": [1.0, 2.0, 3.0]})
    out = NarrativeGenerator().generate_batch(["a", "b", "c"], np.array([0.9, 0.8, 0.3]), shap_df,
                                              unknown_mask=np.array([False, False, True]))
    assert len(out) == 3 and "zero-day" in out[2]


# --- Explanation stability --------------------------------------------------

def test_stability_identical_importances_are_perfectly_consistent():
    imp = pd.Series({"a": 3.0, "b": 2.0, "c": 1.0})
    m = compare_importances(imp, imp)
    assert m["rank_correlation"] == 1.0 and m["cosine_similarity"] == 1.0 and m["topk_overlap"] == 1.0


def test_stability_reversed_ranking_is_anticorrelated():
    a = pd.Series({"a": 3.0, "b": 2.0, "c": 1.0})
    b = pd.Series({"a": 1.0, "b": 2.0, "c": 3.0})
    assert compare_importances(a, b)["rank_correlation"] == -1.0


def test_stability_handles_disjoint_features():
    m = compare_importances(pd.Series({"a": 1.0}), pd.Series({"b": 1.0}))
    assert m["n_common_features"] == 0 and np.isnan(m["rank_correlation"])


def test_stability_study_is_pairwise():
    imps = {k: pd.Series({"a": 3.0, "b": 2.0, "c": 1.0}) for k in ["m49", "m30", "m20"]}
    assert len(run_stability_study(imps)) == 3
