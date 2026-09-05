"""Abstract base class every model implementation must inherit from.

To add a new model (e.g. Random Forest, LightGBM, an MLP):
  1. Create src/models/your_model.py with a class inheriting BaseModel.
  2. Implement fit / predict / predict_proba / get_feature_importance / save / load.
  3. Register it in src/models/model_factory.py (one line).
  4. Set `model.type: "your_model"` in configs/config.yaml.
No other pipeline code needs to change — train_pipeline.py, evaluate_pipeline.py,
OpenSetWrapper, and the SHAP explainer all work against this interface only.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseModel(ABC):
    """Common interface for all IDS classifiers used in this project."""

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray | None = None) -> "BaseModel":
        """Train the model on features X and encoded multiclass labels y. `sample_weight`
        (e.g. from sklearn.utils.class_weight.compute_sample_weight) lets the caller
        counteract class imbalance without every model needing its own balancing logic."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return predicted class indices for each row of X."""
        raise NotImplementedError

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return class probability matrix, shape (n_samples, n_classes)."""
        raise NotImplementedError

    @abstractmethod
    def get_feature_importance(self) -> np.ndarray:
        """Return a 1D array of per-feature importance scores, same order as training features."""
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str) -> "BaseModel":
        raise NotImplementedError

    @property
    @abstractmethod
    def underlying_model(self) -> Any:
        """Return the raw fitted estimator (e.g. for SHAP TreeExplainer)."""
        raise NotImplementedError
