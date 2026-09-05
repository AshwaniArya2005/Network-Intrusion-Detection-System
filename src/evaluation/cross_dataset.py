"""Cross-Dataset Generalization study (novelty #4).

Trains on UNSW-NB15, tests on CICIDS2017 (and vice versa) using only the
feature namespace the two datasets share (see CIC_TO_COMMON in
src/data_loader.py), and compares three feature-selection strategies:

  - "common_all":  every feature common to both datasets
  - "unsw_only":   top-k common features ranked by SHAP importance on UNSW alone
  - "stable":      common features that rank in the top-k on BOTH datasets
                    (src/feature_selection.get_stable_features)
"""
from __future__ import annotations

import pandas as pd

from src.evaluation.metrics import compute_metrics
from src.feature_selection import get_stable_features
from src.models.model_factory import create_model
from src.preprocessing import Preprocessor
from src.utils.logger import get_logger
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)


def _train_eval(model_type: str, model_params: dict, X_train, y_train, X_test, y_test) -> dict:
    model = create_model(model_type, model_params)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return model, compute_metrics(y_test, y_pred)


def run_cross_dataset_study(
    unsw_df: pd.DataFrame,
    cic_df: pd.DataFrame,
    common_features: list[str],
    model_type: str,
    model_params: dict,
    top_k: int = 10,
) -> pd.DataFrame:
    """Run the full cross-dataset generalization comparison and return a results dataframe
    with one row per (strategy, train_dataset -> test_dataset) combination."""

    # attack_cat taxonomies differ between UNSW and CIC (e.g. "Generic" vs "PortScan"),
    # so cross-dataset transfer is evaluated on the shared binary label (normal/attack)
    # rather than the multiclass target, which wouldn't align across datasets.
    pre_unsw = Preprocessor(feature_list=common_features, target_column="label").fit(unsw_df)
    pre_cic = Preprocessor(feature_list=common_features, target_column="label").fit(cic_df)
    X_unsw, y_unsw = pre_unsw.transform(unsw_df)
    X_cic, y_cic = pre_cic.transform(cic_df)

    # SHAP importance computed independently on each dataset using the full common set.
    base_model_unsw = create_model(model_type, model_params).fit(X_unsw, y_unsw)
    base_model_cic = create_model(model_type, model_params).fit(X_cic, y_cic)
    imp_unsw = SHAPExplainer(base_model_unsw, common_features).global_importance(X_unsw)
    imp_cic = SHAPExplainer(base_model_cic, common_features).global_importance(X_cic)

    strategies = {
        "common_all": common_features,
        "unsw_only": list(imp_unsw.sort_values(ascending=False).head(top_k).index),
        "stable": get_stable_features(imp_unsw.to_dict(), imp_cic.to_dict(), top_k=top_k),
    }

    rows = []
    for strategy_name, features in strategies.items():
        if len(features) < 2:
            logger.warning(f"Strategy '{strategy_name}' has too few features ({len(features)}); skipping.")
            continue

        pre_u = Preprocessor(feature_list=features, target_column="label").fit(unsw_df)
        pre_c = Preprocessor(feature_list=features, target_column="label").fit(cic_df)
        Xu, yu = pre_u.transform(unsw_df)
        Xc, yc = pre_c.transform(cic_df)

        _, metrics_u_to_c = _train_eval(model_type, model_params, Xu, yu, Xc, yc)
        rows.append({"strategy": strategy_name, "n_features": len(features),
                     "train": "UNSW", "test": "CIC", **metrics_u_to_c})

        _, metrics_c_to_u = _train_eval(model_type, model_params, Xc, yc, Xu, yu)
        rows.append({"strategy": strategy_name, "n_features": len(features),
                     "train": "CIC", "test": "UNSW", **metrics_c_to_u})

    return pd.DataFrame(rows)
