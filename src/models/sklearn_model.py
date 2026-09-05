"""Example alternative models proving the BaseModel interface is swappable without
touching any pipeline code. Both use scikit-learn, already a project dependency —
no new packages required to try a different model.
"""
from __future__ import annotations

import inspect
from typing import Any

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from src.models.base_model import BaseModel
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _filter_kwargs(cls, params: dict[str, Any]) -> dict[str, Any]:
    """Drop config keys the estimator's constructor doesn't accept (e.g. XGBoost-only
    params like eval_metric when config.yaml's shared params block is reused for
    a different model.type)."""
    accepted = set(inspect.signature(cls.__init__).parameters)
    return {k: v for k, v in params.items() if k in accepted}


class SklearnModel(BaseModel):
    """Generic wrapper for any scikit-learn classifier with feature_importances_
    or coef_ (Random Forest, Logistic Regression, ...)."""

    def __init__(self, estimator):
        self._model = estimator

    def fit(self, X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray | None = None) -> "SklearnModel":
        logger.info(f"Training {type(self._model).__name__} on {X.shape[0]} samples, {X.shape[1]} features")
        self._model.fit(X, y, sample_weight=sample_weight)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict_proba(X)

    def get_feature_importance(self) -> np.ndarray:
        if hasattr(self._model, "feature_importances_"):
            return self._model.feature_importances_
        if hasattr(self._model, "coef_"):
            return np.abs(self._model.coef_).mean(axis=0)
        raise AttributeError(f"{type(self._model).__name__} exposes no importance/coef attribute")

    def save(self, path: str) -> None:
        joblib.dump(self._model, path)
        logger.info(f"Saved {type(self._model).__name__} model to {path}")

    def load(self, path: str) -> "SklearnModel":
        # joblib.load executes arbitrary code on untrusted input; only ever load
        # artifacts this project trained and wrote to models_saved/ itself.
        self._model = joblib.load(path)
        return self

    @property
    def underlying_model(self) -> Any:
        return self._model


def random_forest(params: dict[str, Any] | None = None) -> SklearnModel:
    return SklearnModel(RandomForestClassifier(**_filter_kwargs(RandomForestClassifier, params or {})))


def logistic_regression(params: dict[str, Any] | None = None) -> SklearnModel:
    return SklearnModel(LogisticRegression(**_filter_kwargs(LogisticRegression, params or {})))
