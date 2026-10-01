"""Shared fixtures. Every model-facing test is parametrized over MODEL_TYPES, so a
new model only needs its name added here to get the full contract test suite."""
from __future__ import annotations

import pytest
from sklearn.datasets import make_classification

from src.models.model_factory import create_model

MODEL_TYPES = ["xgboost", "random_forest", "logistic_regression"]
N_FEATURES = 8
N_CLASSES = 3
FAST_PARAMS = {"n_estimators": 20, "max_depth": 3, "random_state": 0}


def params_for(model_type: str) -> dict:
    """FAST_PARAMS plus params only the given model accepts (max_iter is sklearn-LR-only;
    XGBoost warns about unused parameters)."""
    return dict(FAST_PARAMS, **({"max_iter": 200} if model_type == "logistic_regression" else {}))


@pytest.fixture(scope="session")
def data():
    X, y = make_classification(n_samples=300, n_features=N_FEATURES, n_informative=5,
                               n_classes=N_CLASSES, random_state=0)
    return X, y


@pytest.fixture(scope="session")
def feature_names():
    return [f"f{i}" for i in range(N_FEATURES)]


@pytest.fixture(scope="session", params=MODEL_TYPES)
def model_type(request):
    return request.param


@pytest.fixture(scope="session")
def fitted_model(model_type, data):
    X, y = data
    return create_model(model_type, params_for(model_type)).fit(X, y)
