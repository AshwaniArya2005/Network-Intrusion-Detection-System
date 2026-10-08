"""Neighbourhood utilities for leakage checks: near-twin distances and a row-order block split.

A near twin of a row is a row of another set within L-infinity distance r in the embedding of src.evaluation.overlap (log1p of the
numeric features clipped at 0, standardised, categoricals required to match exactly), here STANDARDISED ON THE TRAINING ROWS so
every comparison (adaptation rows, training rows, ...) uses the same scale. `block_split` cuts rows in their file order into
contiguous blocks and leaves a gap between blocks of different groups, so a sliding-window feature (the ct_* columns count recent
connections) cannot link an adaptation row to an evaluation row.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from src.evaluation.overlap import vector_ids
from src.preprocessing import CATEGORICAL_FEATURES, engineer_features

UNSEEN_CATEGORY = -1000.0   # a category never seen in the fit rows is "far" from everything (>= 1000 away)


class Embedder:
    """log1p / standardise the numeric `features` (statistics from the fit rows) and code the categoricals (x 1000, so a
    mismatch is never "near")."""

    def __init__(self, features: list[str]):
        self.features = list(features)
        self.numeric = [f for f in self.features if f not in CATEGORICAL_FEATURES]
        self.categorical = [f for f in self.features if f in CATEGORICAL_FEATURES]

    def _numeric(self, df: pd.DataFrame) -> np.ndarray:
        return np.log1p(df[self.numeric].astype(float).clip(lower=0)).to_numpy()

    def fit(self, df: pd.DataFrame) -> "Embedder":
        df = engineer_features(df, allow_missing=True)
        x = self._numeric(df)
        self.mean_, self.sd_ = x.mean(axis=0), x.std(axis=0)
        self.sd_ = np.where(self.sd_ > 0, self.sd_, 1.0)
        self.codes_ = {f: {v: i for i, v in enumerate(pd.unique(df[f].astype(str)))} for f in self.categorical}
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        df = engineer_features(df, allow_missing=True)
        x = (self._numeric(df) - self.mean_) / self.sd_
        codes = [df[f].astype(str).map(self.codes_[f]).fillna(UNSEEN_CATEGORY / 1000.0).to_numpy(dtype=float) * 1000.0 for f in self.categorical]
        return np.hstack([x, np.column_stack(codes)]) if codes else x


def nearest_distance(query: np.ndarray, reference: np.ndarray, cutoff: float = 0.25) -> np.ndarray:
    """L-infinity distance from each query row to its nearest reference row, `inf` where it exceeds `cutoff`."""
    dist, _ = cKDTree(reference).query(query, p=np.inf, distance_upper_bound=cutoff + 1e-9, workers=-1)
    return dist


def exact_twin_mask(query: pd.DataFrame, reference: pd.DataFrame, features: list[str]) -> np.ndarray:
    """True for query rows whose feature vector (engineered features included) also occurs in `reference`."""
    q, r = engineer_features(query, allow_missing=True), engineer_features(reference, allow_missing=True)
    return np.isin(vector_ids(q, features), vector_ids(r, features))


def twin_shares(dist: np.ndarray, exact: np.ndarray, thresholds: tuple[float, ...] = (0.1, 0.25)) -> dict[str, float]:
    """Share of query rows with an exact twin and with a near twin within each threshold."""
    return {"exact_twin": float(np.mean(exact)), **{f"near_twin_{t}": float(np.mean(dist <= t + 1e-12)) for t in thresholds}}


def block_split(n_rows: int, block_size: int, buffer: int, adapt_share: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """(adaptation positions, evaluation positions) of `n_rows` rows kept in file order. Contiguous blocks of `block_size` rows go
    to the adaptation group (a random `adapt_share` of the blocks, drawn with `seed`) or the evaluation group; `buffer` rows on each
    side of every boundary between the two groups are dropped from both, so no adaptation row lies within `buffer` rows of an
    evaluation row."""
    n_blocks = int(np.ceil(n_rows / block_size))
    rng = np.random.default_rng(seed)
    adapt_blocks = set(rng.choice(n_blocks, size=max(1, round(adapt_share * n_blocks)), replace=False).tolist())
    group = np.array([(i // block_size) in adapt_blocks for i in range(n_rows)])   # True = adaptation block
    drop = np.zeros(n_rows, dtype=bool)
    for c in np.flatnonzero(group[1:] != group[:-1]) + 1:                          # c = first row of the new block
        drop[max(0, c - buffer): c + buffer] = True
    positions = np.arange(n_rows)
    return positions[group & ~drop], positions[~group & ~drop]
