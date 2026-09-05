"""Model swap point. This is the ONE file to edit to plug in a new model:

    1. Implement your model in src/models/your_model.py (inherit BaseModel).
    2. Add one `elif model_type == "your_model": return YourModel(params)` branch below.
    3. Set `model.type: "your_model"` in configs/config.yaml.

Every pipeline (train_pipeline.py, evaluate_pipeline.py, run_all_experiments.py,
the dashboard) calls create_model(config) — none of them need to change.
"""
from __future__ import annotations

from typing import Any

from src.models.base_model import BaseModel
from src.models.sklearn_model import logistic_regression, random_forest
from src.models.xgboost_model import XGBoostModel


def create_model(model_type: str, params: dict[str, Any] | None = None) -> BaseModel:
    """Instantiate a BaseModel implementation by name (see configs/config.yaml `model.type`)."""
    params = params or {}
    if model_type == "xgboost":
        return XGBoostModel(params)
    elif model_type == "random_forest":
        return random_forest(params)
    elif model_type == "logistic_regression":
        return logistic_regression(params)
    else:
        raise ValueError(
            f"Unknown model.type '{model_type}'. Add it to src/models/model_factory.py "
            f"(known types: xgboost, random_forest, logistic_regression)."
        )
