import pandas as pd
import pytest

from src.data_loader import make_synthetic_unsw
from src.models.model_factory import create_model
from src.preprocessing import Preprocessor
from src.xai.explanation_stability import compare_importances, run_stability_study
from src.xai.narrative_generator import NarrativeGenerator
from src.xai.shap_explainer import SHAPExplainer

FEATURES = ["sttl", "dttl", "rate", "sbytes", "dbytes", "proto", "service", "state"]


@pytest.fixture
def fitted():
    df = make_synthetic_unsw(n_rows=150, seed=3)
    pre = Preprocessor(feature_list=FEATURES).fit(df)
    X, y = pre.transform(df)
    model = create_model("xgboost", {"random_state": 42, "n_estimators": 30})
    model.fit(X, y)
    return model, pre, X, y


def test_shap_global_importance(fitted):
    model, pre, X, y = fitted
    explainer = SHAPExplainer(model, FEATURES, background_samples=50)
    importance = explainer.global_importance(X)

    assert set(importance.index) == set(FEATURES)
    assert (importance >= 0).all()
    assert importance.sum() > 0


def test_shap_local_explanation(fitted):
    model, pre, X, y = fitted
    explainer = SHAPExplainer(model, FEATURES, background_samples=50)
    pred_idx = model.predict(X[:1])[0]
    row = explainer.local_explanation(X[:1], int(pred_idx))

    assert list(row.index) == FEATURES
    top = SHAPExplainer.top_k(row, k=3)
    assert len(top) == 3


def test_explanation_stability_metrics_self_comparison(fitted):
    model, pre, X, y = fitted
    explainer = SHAPExplainer(model, FEATURES, background_samples=50)
    importance = explainer.global_importance(X)

    metrics = compare_importances(importance, importance, top_k=3)
    assert metrics["rank_correlation"] == pytest.approx(1.0, abs=1e-6)
    assert metrics["cosine_similarity"] == pytest.approx(1.0, abs=1e-6)
    assert metrics["topk_overlap"] == pytest.approx(1.0)


def test_run_stability_study_pairwise(fitted, tmp_path):
    model, pre, X, y = fitted
    explainer = SHAPExplainer(model, FEATURES, background_samples=50)
    importance = explainer.global_importance(X)

    out_csv = tmp_path / "stability.csv"
    df_result = run_stability_study({"a": importance, "b": importance.iloc[::-1]}, output_csv=str(out_csv))

    assert len(df_result) == 1
    assert out_csv.exists()


def test_narrative_generator_produces_readable_text(fitted):
    model, pre, X, y = fitted
    explainer = SHAPExplainer(model, FEATURES, background_samples=50)
    pred_idx = int(model.predict(X[:1])[0])
    predicted_label = pre.decode_target([pred_idx])[0]
    confidence = float(model.predict_proba(X[:1])[0, pred_idx])
    shap_row = explainer.local_explanation(X[:1], pred_idx)
    feature_values = pd.Series(X[0], index=FEATURES)

    generator = NarrativeGenerator({predicted_label: "Take some action."})
    text = generator.generate(predicted_label, confidence, shap_row, feature_values, top_k=3)

    assert predicted_label in text
    assert f"{confidence * 100:.1f}%" in text
    assert isinstance(text, str) and len(text) > 20


def test_narrative_generator_categorical_feature_uses_category_not_magnitude(fitted):
    """Regression test: proto/service/state are label-encoded integers, not magnitudes.
    Before the fix, a categorical top-SHAP-feature always produced 'extremely high X'
    because feature_means/feature_stds only cover numeric_features, so the categorical
    z-score silently divided by a 1e-9 fallback. This must name the category instead."""
    model, pre, X, y = fitted
    shap_row = pd.Series(0.0, index=FEATURES)
    shap_row["proto"] = 5.0  # sole dominant contributor (top_k=1 below)
    feature_values = pd.Series(X[0], index=FEATURES)  # real encoded row from the fixture

    generator = NarrativeGenerator({})
    text = generator.generate(
        "DoS", 0.9, shap_row, feature_values,
        categorical_features=frozenset(pre.categorical_features),
        category_decoders=pre.label_encoders,
        top_k=1,
    )

    magnitude_words = ["extremely high", "extremely low", "unusually high", "unusually low", "elevated", "reduced"]
    assert not any(w in text for w in magnitude_words), f"magnitude language leaked into: {text}"

    decoded_proto = pre.label_encoders["proto"].inverse_transform([int(round(feature_values["proto"]))])[0]
    assert f"network protocol={decoded_proto}" in text


def test_narrative_generator_unknown_case(fitted):
    model, pre, X, y = fitted
    explainer = SHAPExplainer(model, FEATURES, background_samples=50)
    pred_idx = int(model.predict(X[:1])[0])
    shap_row = explainer.local_explanation(X[:1], pred_idx)

    generator = NarrativeGenerator({"Unknown": "Escalate to analyst."})
    text = generator.generate("DoS", 0.4, shap_row, is_unknown=True)

    assert "unrecognized" in text.lower()
    assert "Escalate to analyst." in text
