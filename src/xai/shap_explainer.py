"""SHAP-based global and local explanations for any BaseModel — tree-based
(XGBoost/RandomForest/LightGBM/CatBoost), linear (LogisticRegression and anything
else exposing `.coef_`), or an arbitrary black-box model (MLP, SVM, ...)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import shap

from src.models.base_model import BaseModel
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _normalize_shap_output(raw_shap, n_classes: int) -> list[np.ndarray]:
    """Normalize the various shapes shap.TreeExplainer can return into a list of
    (n_samples, n_features) arrays, one per class.

    Handles: list[np.ndarray] (older SHAP API), 3D array (n_samples, n_features,
    n_classes) (newer SHAP API), and plain 2D array for binary/regression models.
    """
    if isinstance(raw_shap, list):
        return [np.asarray(a) for a in raw_shap]
    arr = np.asarray(raw_shap)
    if arr.ndim == 3:
        return [arr[:, :, c] for c in range(arr.shape[2])]
    if arr.ndim == 2 and n_classes <= 2:
        return [-arr, arr] if n_classes == 2 else [arr]
    raise ValueError(f"Unrecognized SHAP output shape: {arr.shape}")


class SHAPExplainer:
    """Wraps the right SHAP explainer for whatever BaseModel it's given.

    Picks automatically, in order:
      1. TreeExplainer — works for XGBoost, LightGBM, CatBoost, and sklearn tree
         ensembles (RandomForest, GradientBoosting, ...) uniformly; fast, exact.
      2. LinearExplainer — for anything exposing `.coef_` (LogisticRegression and
         other sklearn linear models); fast, exact for linear models.
      3. KernelExplainer — universal fallback for opaque models (MLP, SVM, ...);
         much slower (sampling-based), but correct for any `predict_proba`.
    No caller needs to know which one applies — swapping `model.type` in config.yaml
    is enough; this class detects the right explainer from the fitted model itself.
    """

    def __init__(self, model: BaseModel, feature_names: list[str], background_samples: int = 100):
        self.model = model
        self.feature_names = feature_names
        self._background_samples = background_samples
        self._explainer = None  # built lazily on first use, once we have X for background data

    def _get_explainer(self, X: np.ndarray):
        if self._explainer is not None:
            return self._explainer

        underlying = self.model.underlying_model
        try:
            self._explainer = shap.TreeExplainer(underlying)
            logger.info("SHAPExplainer: using TreeExplainer (tree-based model detected).")
            return self._explainer
        except Exception:
            pass

        background = X[:min(len(X), self._background_samples)]
        if len(background) < 10:
            logger.warning(f"Building a non-tree SHAP explainer's background from only "
                            f"{len(background)} row(s) — explanations may be low quality. Call "
                            f"compute_shap_values()/global_importance() with a larger batch (e.g. "
                            f"X_train) once before local_explanation() for a non-tree model.")

        if hasattr(underlying, "coef_"):
            self._explainer = shap.LinearExplainer(underlying, background)
            logger.info("SHAPExplainer: using LinearExplainer (linear model detected via `.coef_`).")
        else:
            self._explainer = shap.KernelExplainer(self.model.predict_proba, background)
            logger.info("SHAPExplainer: no tree/linear structure detected — falling back to "
                        "KernelExplainer (works for any model, but is much slower).")
        return self._explainer

    def compute_shap_values(self, X: np.ndarray) -> list[np.ndarray]:
        """Return per-class SHAP value matrices for X, each shaped (n_samples, n_features)."""
        if len(X) > self._background_samples:
            idx = np.random.default_rng(42).choice(len(X), self._background_samples, replace=False)
            X = X[idx]
        explainer = self._get_explainer(X)
        raw = explainer.shap_values(X)
        n_classes = self.model.predict_proba(X[:1]).shape[1]
        return _normalize_shap_output(raw, n_classes)

    def global_importance(self, X: np.ndarray) -> pd.Series:
        """Mean absolute SHAP value per feature, averaged across all classes — a
        global ranking of which features drive the model's decisions overall."""
        per_class = self.compute_shap_values(X)
        stacked = np.stack([np.abs(c).mean(axis=0) for c in per_class], axis=0)
        importance = stacked.mean(axis=0)
        return pd.Series(importance, index=self.feature_names).sort_values(ascending=False)

    def local_explanation(self, x_row: np.ndarray, predicted_class_idx: int) -> pd.Series:
        """SHAP values for a single sample, for the class it was predicted as.
        x_row must be shape (1, n_features).

        For non-tree models: if this is the very first call (explainer not built yet),
        the Linear/KernelExplainer background is built from whatever X is passed here —
        a single row makes a poor background (a warning is logged when this happens).
        Call compute_shap_values()/global_importance() once with a proper batch (e.g.
        X_train) during setup first if you're using a non-tree model."""
        explainer = self._get_explainer(x_row)
        raw = explainer.shap_values(x_row)
        n_classes = self.model.predict_proba(x_row).shape[1]
        per_class = _normalize_shap_output(raw, n_classes)
        class_idx = min(predicted_class_idx, len(per_class) - 1)
        values = per_class[class_idx][0]
        return pd.Series(values, index=self.feature_names)

    @staticmethod
    def top_k(shap_row: pd.Series, k: int = 5) -> pd.Series:
        """Top-k features by absolute SHAP value for one sample, signed values preserved."""
        return shap_row.reindex(shap_row.abs().sort_values(ascending=False).index[:k])
