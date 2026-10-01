"""Explanation Stability study (novelty #3): how consistent are SHAP explanations
across different feature-set sizes (40 vs 30 vs 20 vs 15) or different models?

Metrics computed pairwise, restricted to the features common to both configs:
  - rank_correlation: Spearman correlation of importance ranks
  - cosine_similarity: cosine similarity of importance vectors
  - topk_overlap: Jaccard overlap of each side's top-k most important features
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.utils.logger import get_logger

logger = get_logger(__name__)


def compare_importances(importance_a: pd.Series, importance_b: pd.Series, top_k: int = 10) -> dict[str, float]:
    """Compare two feature-importance Series over their common feature names."""
    common = importance_a.index.intersection(importance_b.index)
    if len(common) < 2:
        return {"n_common_features": len(common), "rank_correlation": np.nan,
                "cosine_similarity": np.nan, "topk_overlap": np.nan}

    a = importance_a.reindex(common).fillna(0.0)
    b = importance_b.reindex(common).fillna(0.0)

    rank_corr, _ = spearmanr(a.values, b.values)
    cosine_sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

    top_a = set(a.sort_values(ascending=False).head(top_k).index)
    top_b = set(b.sort_values(ascending=False).head(top_k).index)
    topk_overlap = len(top_a & top_b) / len(top_a | top_b) if (top_a | top_b) else np.nan

    return {
        "n_common_features": len(common),
        "rank_correlation": round(float(rank_corr), 4),
        "cosine_similarity": round(cosine_sim, 4),
        "topk_overlap": round(float(topk_overlap), 4),
    }


def run_stability_study(importances_by_config: dict[str, pd.Series], output_csv: str | None = None) -> pd.DataFrame:
    """Pairwise-compare every config's SHAP importance vector against every other's.

    `importances_by_config` keys identify a configuration (e.g. "xgboost_40",
    "xgboost_30"); values are pd.Series[feature_name -> importance].
    """
    rows = []
    for name_a, name_b in combinations(importances_by_config.keys(), 2):
        metrics = compare_importances(importances_by_config[name_a], importances_by_config[name_b])
        rows.append({"config_a": name_a, "config_b": name_b, **metrics})

    df = pd.DataFrame(rows)
    if output_csv:
        df.to_csv(output_csv, index=False)
        logger.info(f"Saved explanation stability results to {output_csv}")
    return df
