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
from src.models.hierarchical_model import HierarchicalModel
from src.models.sklearn_model import logistic_regression, random_forest
from src.models.xgboost_model import XGBoostModel
from src.utils.config_loader import artifact_suffix


def create_model(model_type: str, params: dict[str, Any] | None = None) -> BaseModel:
    """Instantiate a BaseModel implementation by name (see configs/config.yaml `model.type`)."""
    params = params or {}
    if model_type == "xgboost":
        return XGBoostModel(params)
    
    elif model_type == "lightgbm":
        from src.models.lightgbm_model import lightgbm_classifier
        return lightgbm_classifier(params)

    elif model_type == "random_forest":
        return random_forest(params)
    elif model_type == "logistic_regression":
        return logistic_regression(params)
    else:
        raise ValueError(
            f"Unknown model.type '{model_type}'. Add it to src/models/model_factory.py "
            f"(known types: xgboost, lightgbm, random_forest, logistic_regression)."
        )


def create_scheme_model(model_type: str, params: dict[str, Any] | None, hierarchical: bool, normal_index: int | None = None,
                        stage1_params: dict[str, Any] | None = None, stage1_power: float = 0.5) -> BaseModel:
    """The model for the active label scheme: a plain `create_model` classifier, or — when the
    scheme is hierarchical (configs/config.yaml `data.label_schemes`) — a two-stage
    HierarchicalModel of that model type (needs the encoded index of the Normal class). `stage1_params` /
    `stage1_power` give the attack-vs-normal stage its own hyperparameters and class-weight exponent."""
    if not hierarchical:
        return create_model(model_type, params)
    if normal_index is None:
        raise ValueError("A hierarchical model needs normal_index (the encoded Normal class).")
    make_stage1 = (lambda: create_model(model_type, dict(params or {}, **stage1_params))) if stage1_params else None
    return HierarchicalModel(lambda: create_model(model_type, params), normal_index, artifact_suffix(model_type),
                             make_stage1=make_stage1, stage1_power=stage1_power)
