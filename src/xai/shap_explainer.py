"""SHAP-based global and local explanations for any BaseModel — tree-based
(XGBoost/RandomForest/LightGBM/CatBoost), linear (LogisticRegression and anything
else exposing `.coef_`), or an arbitrary black-box model (MLP, SVM, ...)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import shap

from src.models.base_model import BaseModel
from src.models.hierarchical_model import HierarchicalModel
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
        # A hierarchical model is explained stage by stage: stage 1 (binary attack score) for
        # Normal, stage 2 (family) for each attack class; class indexes are mapped, never mixed.
        self._stages = ((SHAPExplainer(model.stage1, feature_names, background_samples),
                         SHAPExplainer(model.stage2, feature_names, background_samples))
                        if isinstance(model, HierarchicalModel) else None)

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

    def compute_shap_values(self, X: np.ndarray, max_samples: int | None = None) -> list[np.ndarray]:
        """Return per-class SHAP value matrices for X, each shaped (n_samples, n_features).
        X is randomly subsampled to `max_samples` rows (default: the background size)."""
        max_samples = max_samples or self._background_samples
        if len(X) > max_samples:
            idx = np.random.default_rng(42).choice(len(X), max_samples, replace=False)
            X = X[idx]
        if self._stages is not None:
            return self._hierarchical_shap_values(X)
        explainer = self._get_explainer(X)
        raw = explainer.shap_values(X)
        n_classes = self.model.predict_proba(X[:1]).shape[1]
        return _normalize_shap_output(raw, n_classes)

    def global_importance(self, X: np.ndarray, max_samples: int | None = None) -> pd.Series:
        """Mean absolute SHAP value per feature, averaged across all classes — a
        global ranking of which features drive the model's decisions overall. Computed
        on a random sample of `max_samples` rows (default: the background size; pass
        config xai.importance_samples for a stable ranking)."""
        per_class = self.compute_shap_values(X, max_samples)
        stacked = np.stack([np.abs(c).mean(axis=0) for c in per_class], axis=0)
        importance = stacked.mean(axis=0)
        return pd.Series(importance, index=self.feature_names).sort_values(ascending=False)

    def _hierarchical_shap_values(self, X: np.ndarray) -> list[np.ndarray]:
        """Per composed class (label-encoder index): stage-1 SHAP of "normal" for Normal, stage-2
        SHAP of the family for each attack class (zeros for classes the model never saw)."""
        stage1, stage2 = self._stages
        model = self.model
        s1 = stage1.compute_shap_values(X, len(X))
        s2 = stage2.compute_shap_values(X, len(X))
        out = [np.zeros_like(s1[0]) for _ in range(model.n_classes)]
        out[model.normal_index] = s1[0]
        for family, cls in enumerate(model.attack_classes):
            out[int(cls)] = s2[family]
        return out

    def _hierarchical_local(self, X: np.ndarray, class_idx) -> pd.DataFrame:
        stage1, stage2 = self._stages
        model = self.model
        idx = np.asarray(class_idx, dtype=int)
        is_normal = idx == model.normal_index
        unknown = ~is_normal & ~np.isin(idx, model.attack_classes)
        if unknown.any():
            raise ValueError(f"Class indexes {sorted(set(idx[unknown]))} are not known to the hierarchical model")
        out = np.zeros((len(X), len(self.feature_names)))
        if is_normal.any():
            out[is_normal] = stage1.local_explanations(X[is_normal], np.zeros(is_normal.sum(), dtype=int)).to_numpy()
        if (~is_normal).any():
            family = np.searchsorted(model.attack_classes, idx[~is_normal])  # encoder index -> stage-2 index
            out[~is_normal] = stage2.local_explanations(X[~is_normal], family).to_numpy()
        return pd.DataFrame(out, columns=self.feature_names)

    def local_explanations(self, X: np.ndarray, class_idx) -> pd.DataFrame:
        """SHAP values for each row of X, for that row's class in `class_idx` — one
        batched explainer call. Shape (n_samples, n_features).

        For non-tree models: if this is the very first call (explainer not built yet),
        the Linear/KernelExplainer background is built from whatever X is passed here —
        a tiny batch makes a poor background (a warning is logged when this happens).
        Call compute_shap_values()/global_importance() once with a proper batch (e.g.
        X_train) during setup first if you're using a non-tree model."""
        if self._stages is not None:
            return self._hierarchical_local(X, class_idx)
        explainer = self._get_explainer(X)
        n_classes = self.model.predict_proba(X[:1]).shape[1]
        per_class = _normalize_shap_output(explainer.shap_values(X), n_classes)
        rows = [per_class[min(int(c), len(per_class) - 1)][i] for i, c in enumerate(class_idx)]
        return pd.DataFrame(np.vstack(rows), columns=self.feature_names)

    def local_explanation(self, x_row: np.ndarray, predicted_class_idx: int) -> pd.Series:
        """SHAP values for a single sample (x_row shape (1, n_features)), for the class
        it was predicted as. See local_explanations() for the non-tree-model caveat."""
        return self.local_explanations(x_row, [predicted_class_idx]).iloc[0]

    @staticmethod
    def top_k(shap_row: pd.Series, k: int = 5) -> pd.Series:
        """Top-k features by absolute SHAP value for one sample, signed values preserved."""
        return shap_row.reindex(shap_row.abs().sort_values(ascending=False).index[:k])
