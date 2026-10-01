"""Feature selection utilities: static config-driven selection, statistical ranking,
and stable-feature identification (features that matter across datasets/feature sets).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif

from src.preprocessing import CATEGORICAL_FEATURES, Preprocessor
from src.utils.logger import get_logger

logger = get_logger(__name__)


def select_features(df: pd.DataFrame, feature_list: list[str]) -> pd.DataFrame:
    """Return only the columns in feature_list that exist in df (missing ones logged, not fatal)."""
    available = [f for f in feature_list if f in df.columns]
    missing = set(feature_list) - set(available)
    if missing:
        logger.warning(f"Feature selection: {len(missing)} requested features not in dataframe: {sorted(missing)}")
    return df[available]


def rank_by_mutual_info(X: np.ndarray, y: np.ndarray, feature_names: list[str], seed: int = 42,
                        discrete: list[str] | None = None) -> pd.Series:
    """Statistical feature ranking via mutual information with the target.

    `discrete` names label-encoded categorical features, which must be estimated as
    discrete variables: treated as continuous, their arbitrary integer codes make MI
    meaninglessly low. Used as an independent cross-check against SHAP importance rankings
    in the feature-selection / explanation-consistency study (novelty #3).
    """
    mask = np.array([f in (discrete or []) for f in feature_names])
    scores = mutual_info_classif(X, y, discrete_features=mask, random_state=seed)
    return pd.Series(scores, index=feature_names).sort_values(ascending=False)


def redundancy_reorder(ranking: pd.Series, X: np.ndarray, feature_names: list[str], threshold: float) -> pd.Series:
    """Greedy de-duplication of a ranking: walk it best-first and keep a feature only if its
    |correlation| with every feature kept so far is <= threshold; the skipped (redundant)
    features follow, in their original order. Still a permutation of the pool, so top-N sets
    spread over distinct signals instead of five byte-count variants."""
    corr = pd.DataFrame(X, columns=feature_names).corr().abs().fillna(0.0)
    kept: list[str] = []
    deferred: list[str] = []
    for f in ranking.index:
        (deferred if kept and corr.loc[f, kept].max() > threshold else kept).append(f)
    return ranking.reindex(kept + deferred)


def compute_feature_ranking(train_df: pd.DataFrame, pool: list[str], target_column: str,
                            max_rows: int = 20000, seed: int = 42,
                            redundancy_threshold: float | None = None) -> pd.Series:
    """Rank the feature pool by mutual information with the target, using the TRAINING
    split only (a subsample of at most `max_rows` rows keeps the kNN-based estimator fast).
    With `redundancy_threshold`, highly correlated features are pushed down (redundancy_reorder)."""
    if len(train_df) > max_rows:
        train_df = train_df.sample(max_rows, random_state=seed)
    X, y = Preprocessor(feature_list=pool, target_column=target_column).fit(train_df).transform(train_df)
    ranking = rank_by_mutual_info(X, y, pool, seed=seed, discrete=sorted(CATEGORICAL_FEATURES))
    if redundancy_threshold is not None:
        ranking = redundancy_reorder(ranking, X, pool, redundancy_threshold)
    return ranking


def data_signature(df: pd.DataFrame, seed: int, extra: str = "") -> str:
    """Short hash of what a ranking was computed from: the frame's shape and columns, ~200 evenly
    spaced rows, the seed and `extra` (pool / source / redundancy settings)."""
    sample = df.iloc[:: max(1, len(df) // 200)]
    content = int(pd.util.hash_pandas_object(sample, index=False).sum()) if len(sample) else 0
    return hashlib.sha256(f"{df.shape}|{list(df.columns)}|{seed}|{extra}|{content}".encode()).hexdigest()[:16]


def _sidecar(path) -> Path:
    return Path(path).with_suffix(".meta.json")


def ranking_is_current(path, signature: str) -> bool:
    """True if the ranking file exists and its sidecar records this exact `signature`."""
    sidecar = _sidecar(path)
    return Path(path).exists() and sidecar.exists() and json.loads(sidecar.read_text()).get("signature") == signature


def write_feature_ranking(ranking: pd.Series, path, signature: str | None = None) -> None:
    """Persist a ranking (feature, score; most important first); with `signature`, also a sidecar
    JSON so a later run can tell whether the ranking still matches its training data."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ranking.rename_axis("feature").rename("score").reset_index().to_csv(path, index=False)
    if signature is not None:
        _sidecar(path).write_text(json.dumps({"signature": signature}))
    logger.info(f"Wrote feature ranking ({len(ranking)} features) to {path}")


def get_stable_features(importance_a: dict[str, float], importance_b: dict[str, float], top_k: int = 15) -> list[str]:
    """Return features that rank in the top_k of BOTH importance dicts (e.g. SHAP importance
    computed independently on two datasets), used for cross-dataset generalization (novelty #4).
    """
    top_a = set(pd.Series(importance_a).sort_values(ascending=False).head(top_k).index)
    top_b = set(pd.Series(importance_b).sort_values(ascending=False).head(top_k).index)
    stable = sorted(top_a & top_b, key=lambda f: importance_a.get(f, 0) + importance_b.get(f, 0), reverse=True)
    logger.info(f"Stable features (top-{top_k} in both): {stable}")
    return stable
