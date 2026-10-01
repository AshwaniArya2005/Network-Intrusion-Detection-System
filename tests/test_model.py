import numpy as np
import pytest

from src.data_loader import make_synthetic_unsw
from src.models.model_factory import create_model
from src.models.open_set_wrapper import OpenSetWrapper
from src.preprocessing import Preprocessor

FEATURES = ["sttl", "dttl", "rate", "sbytes", "dbytes", "proto", "service", "state"]


@pytest.fixture
def xy():
    df = make_synthetic_unsw(n_rows=200, seed=2)
    pre = Preprocessor(feature_list=FEATURES).fit(df)
    return pre.transform(df)


@pytest.mark.parametrize("model_type", ["xgboost", "random_forest", "logistic_regression"])
def test_model_factory_implements_base_model_interface(model_type, xy):
    X, y = xy
    model = create_model(model_type, {"random_state": 42, "max_iter": 200} if model_type == "logistic_regression" else {"random_state": 42})
    model.fit(X, y)

    preds = model.predict(X)
    proba = model.predict_proba(X)
    importance = model.get_feature_importance()

    assert preds.shape == (len(X),)
    assert proba.shape[0] == len(X)
    assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-3)
    assert importance.shape[0] == len(FEATURES)


def test_model_save_and_load_roundtrip(xy, tmp_path):
    X, y = xy
    model = create_model("xgboost", {"random_state": 42})
    model.fit(X, y)
    preds_before = model.predict(X)

    save_path = tmp_path / "model.json"
    model.save(str(save_path))

    reloaded = create_model("xgboost")
    reloaded.load(str(save_path))
    preds_after = reloaded.predict(X)

    assert np.array_equal(preds_before, preds_after)


def test_open_set_wrapper_flags_low_confidence_as_unknown(xy):
    X, y = xy
    model = create_model("xgboost", {"random_state": 42})
    wrapper = OpenSetWrapper(model, confidence_threshold=0.99)  # near-impossible threshold
    wrapper.fit(X, y)

    result = wrapper.predict(X)
    assert result.is_unknown.any()
    assert (result.open_set_label[result.is_unknown] == OpenSetWrapper.UNKNOWN_INDEX).all()
    assert result.confidence.shape == (len(X),)


def test_open_set_wrapper_low_threshold_never_flags_unknown(xy):
    X, y = xy
    model = create_model("xgboost", {"random_state": 42})
    wrapper = OpenSetWrapper(model, confidence_threshold=0.0)
    wrapper.fit(X, y)

    result = wrapper.predict(X)
    assert not result.is_unknown.any()
    assert np.array_equal(result.open_set_label, result.closed_set_label)
