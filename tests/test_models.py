"""BaseModel contract + OpenSetWrapper — must hold for every model in MODEL_TYPES."""
from __future__ import annotations

import numpy as np
import pytest
from sklearn.utils.class_weight import compute_sample_weight

from src.models.base_model import BaseModel
from src.models.model_factory import create_model
from src.models.open_set_wrapper import OpenSetWrapper
from tests.conftest import FAST_PARAMS, N_CLASSES, N_FEATURES


def test_factory_rejects_unknown_type():
    with pytest.raises(ValueError):
        create_model("not_a_model")


def test_is_base_model(fitted_model):
    assert isinstance(fitted_model, BaseModel)
    assert fitted_model.underlying_model is not None


def test_predict_shapes_and_range(fitted_model, data):
    X, _ = data
    pred = fitted_model.predict(X)
    assert pred.shape == (len(X),)
    assert set(np.unique(pred)) <= set(range(N_CLASSES))


def test_predict_proba_is_valid_distribution(fitted_model, data):
    X, _ = data
    proba = fitted_model.predict_proba(X)
    assert proba.shape == (len(X), N_CLASSES)
    assert np.all(proba >= 0) and np.all(proba <= 1)
    np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-5)


def test_predict_agrees_with_proba_argmax(fitted_model, data):
    X, _ = data
    np.testing.assert_array_equal(fitted_model.predict(X), fitted_model.predict_proba(X).argmax(axis=1))


def test_learns_better_than_chance(fitted_model, data):
    X, y = data
    assert (fitted_model.predict(X) == y).mean() > 1 / N_CLASSES + 0.2


def test_feature_importance(fitted_model):
    imp = np.asarray(fitted_model.get_feature_importance())
    assert imp.shape == (N_FEATURES,)
    assert np.all(np.isfinite(imp)) and np.all(imp >= 0)


def test_save_load_roundtrip(fitted_model, model_type, data, tmp_path):
    X, _ = data
    path = str(tmp_path / "model.pkl")
    fitted_model.save(path)
    restored = create_model(model_type, dict(FAST_PARAMS)).load(path)
    np.testing.assert_allclose(restored.predict_proba(X), fitted_model.predict_proba(X), atol=1e-6)


def test_fit_accepts_sample_weight(model_type, data):
    X, y = data
    model = create_model(model_type, dict(FAST_PARAMS))
    assert model.fit(X, y, sample_weight=compute_sample_weight("balanced", y)) is model
    assert model.predict(X).shape == (len(X),)


# --- OpenSetWrapper ---------------------------------------------------------

def test_open_set_threshold_zero_flags_nothing(fitted_model, data):
    X, _ = data
    out = OpenSetWrapper(fitted_model, confidence_threshold=0.0).predict(X)
    assert not out.is_unknown.any()
    np.testing.assert_array_equal(out.open_set_label, out.closed_set_label)


def test_open_set_threshold_above_one_flags_everything(fitted_model, data):
    X, _ = data
    out = OpenSetWrapper(fitted_model, confidence_threshold=1.01).predict(X)
    assert out.is_unknown.all()
    assert (out.open_set_label == OpenSetWrapper.UNKNOWN_INDEX).all()


def test_open_set_flags_exactly_low_confidence(fitted_model, data):
    X, _ = data
    out = OpenSetWrapper(fitted_model, confidence_threshold=0.7).predict(X)
    np.testing.assert_array_equal(out.is_unknown, out.confidence < 0.7)
    np.testing.assert_allclose(out.confidence, fitted_model.predict_proba(X).max(axis=1))
    np.testing.assert_array_equal(out.open_set_label[~out.is_unknown], out.closed_set_label[~out.is_unknown])
