"""Reference model implementation: XGBoost multiclass classifier."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import xgboost as xgb

from src.models.base_model import BaseModel
from src.utils.logger import get_logger

logger = get_logger(__name__)


class XGBoostModel(BaseModel):
    """XGBoost wrapper implementing the BaseModel interface. This is the project's
    reference model — swap by adding a sibling class and registering it in
    src/models/model_factory.py."""

    def __init__(self, params: dict[str, Any] | None = None):
        self.params = params or {}
        self._model = xgb.XGBClassifier(**self._effective_params(n_classes=None))

    def _effective_params(self, n_classes: int | None) -> dict[str, Any]:
        # configs/config.yaml sets eval_metric="mlogloss" for the usual multiclass
        # (attack_cat) task, but the cross-dataset study trains on the binary
        # label column — mlogloss errors out on 2-class data, so downgrade it.
        params = dict(self.params)
        if n_classes == 2 and params.get("eval_metric") == "mlogloss":
            params["eval_metric"] = "logloss"
        return params

    def fit(self, X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray | None = None) -> "XGBoostModel":
        n_classes = len(np.unique(y))
        logger.info(f"Training XGBoost on {X.shape[0]} samples, {X.shape[1]} features, {n_classes} classes")
        self._model = xgb.XGBClassifier(**self._effective_params(n_classes))
        self._model.fit(X, y, sample_weight=sample_weight)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict_proba(X)

    def get_feature_importance(self) -> np.ndarray:
        return self._model.feature_importances_

    def save(self, path: str) -> None:
        # XGBoost's native format (not pickle) — portable across xgboost versions and
        # doesn't execute arbitrary code on load. The caller's path (still ".pkl" by
        # convention from train_pipeline.py) is remapped to ".json" so no other file
        # needs to change to pick this up.
        json_path = str(Path(path).with_suffix(".json"))
        self._model.save_model(json_path)
        logger.info(f"Saved XGBoost model to {json_path}")

    def load(self, path: str) -> "XGBoostModel":
        json_path = str(Path(path).with_suffix(".json"))
        self._model = xgb.XGBClassifier()
        self._model.load_model(json_path)
        return self

    @property
    def underlying_model(self) -> Any:
        return self._model
