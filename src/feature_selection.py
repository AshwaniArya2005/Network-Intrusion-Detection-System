"""Feature selection utilities: static config-driven selection, statistical ranking,
and stable-feature identification (features that matter across datasets/feature sets).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif

from src.utils.logger import get_logger

logger = get_logger(__name__)


def select_features(df: pd.DataFrame, feature_list: list[str]) -> pd.DataFrame:
    """Return only the columns in feature_list that exist in df (missing ones logged, not fatal)."""
    available = [f for f in feature_list if f in df.columns]
    missing = set(feature_list) - set(available)
    if missing:
        logger.warning(f"Feature selection: {len(missing)} requested features not in dataframe: {sorted(missing)}")
    return df[available]


def rank_by_mutual_info(X: np.ndarray, y: np.ndarray, feature_names: list[str], seed: int = 42) -> pd.Series:
    """Statistical feature ranking via mutual information with the target.

    Used as an independent cross-check against SHAP-based importance rankings
    in the feature-selection / explanation-consistency study (novelty #3).
    """
    scores = mutual_info_classif(X, y, random_state=seed)
    return pd.Series(scores, index=feature_names).sort_values(ascending=False)


def get_stable_features(importance_a: dict[str, float], importance_b: dict[str, float], top_k: int = 15) -> list[str]:
    """Return features that rank in the top_k of BOTH importance dicts (e.g. SHAP importance
    computed independently on two datasets), used for cross-dataset generalization (novelty #4).
    """
    top_a = set(pd.Series(importance_a).sort_values(ascending=False).head(top_k).index)
    top_b = set(pd.Series(importance_b).sort_values(ascending=False).head(top_k).index)
    stable = sorted(top_a & top_b, key=lambda f: importance_a.get(f, 0) + importance_b.get(f, 0), reverse=True)
    logger.info(f"Stable features (top-{top_k} in both): {stable}")
    return stable
