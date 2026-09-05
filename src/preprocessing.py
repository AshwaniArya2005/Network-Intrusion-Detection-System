"""Fit/transform preprocessing pipeline: feature engineering, categorical encoding, scaling.

Usage:
    pre = Preprocessor(feature_list=["rate", "sload", ...])
    pre.fit(train_df)
    X_train, y_train = pre.transform(train_df)
    X_test, y_test = pre.transform(test_df)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

from src.utils.logger import get_logger

logger = get_logger(__name__)

CATEGORICAL_FEATURES = {"proto", "service", "state"}


def _clean_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Coerce to numeric and sanitize +-inf (CICIDS2017's Flow Bytes/Packets-per-second
    columns are Infinity for zero-duration flows) and NaN to 0.0 so StandardScaler
    never sees a non-finite value."""
    numeric = df[columns].apply(pd.to_numeric, errors="coerce")
    return numeric.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add the 6 derived features referenced in configs/feature_sets.yaml.

    Computed defensively: any missing base column is treated as 0 so this works
    on both the full UNSW schema and the smaller common CIC feature set.
    """
    df = df.copy()
    sbytes = df.get("sbytes", pd.Series(0.0, index=df.index))
    dbytes = df.get("dbytes", pd.Series(0.0, index=df.index))
    spkts = df.get("spkts", pd.Series(0.0, index=df.index))
    dpkts = df.get("dpkts", pd.Series(0.0, index=df.index))
    dur = df.get("dur", pd.Series(0.0, index=df.index))

    total_bytes = sbytes + dbytes
    total_pkts = spkts + dpkts

    df["total_bytes"] = total_bytes
    df["total_pkts"] = total_pkts
    df["byte_ratio"] = sbytes / dbytes.replace(0, np.nan)
    df["pkt_ratio"] = spkts / dpkts.replace(0, np.nan)
    df["avg_pkt_size"] = total_bytes / total_pkts.replace(0, np.nan)
    df["duration_log"] = np.log1p(dur.clip(lower=0))

    for col in ["byte_ratio", "pkt_ratio", "avg_pkt_size"]:
        df[col] = df[col].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return df


class Preprocessor:
    """Sklearn-style fit/transform preprocessor: engineers features, encodes categoricals,
    scales numerics, and encodes the multiclass target (attack_cat)."""

    def __init__(self, feature_list: list[str], target_column: str = "attack_cat"):
        self.feature_list = feature_list
        self.target_column = target_column
        self.categorical_features = [f for f in feature_list if f in CATEGORICAL_FEATURES]
        self.numeric_features = [f for f in feature_list if f not in CATEGORICAL_FEATURES]
        self.scaler = StandardScaler()
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.target_encoder = LabelEncoder()
        self._fitted = False

    def fit(self, df: pd.DataFrame) -> "Preprocessor":
        df = engineer_features(df)
        for col in self.categorical_features:
            le = LabelEncoder()
            values = df[col].astype(str).fillna("unknown")
            le.fit(list(values) + ["__unseen__"])
            self.label_encoders[col] = le

        numeric_df = _clean_numeric(df, self.numeric_features)
        self.scaler.fit(numeric_df)

        self.target_encoder.fit(df[self.target_column].astype(str))
        self._fitted = True
        logger.info(f"Preprocessor fitted on {len(df)} rows, {len(self.feature_list)} features, "
                    f"{len(self.target_encoder.classes_)} target classes")
        return self

    def transform(self, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        if not self._fitted:
            raise RuntimeError("Preprocessor.fit() must be called before transform().")
        df = engineer_features(df)

        parts = []
        for col in self.categorical_features:
            le = self.label_encoders[col]
            values = df[col].astype(str).fillna("unknown")
            values = values.where(values.isin(le.classes_), "__unseen__")
            parts.append(pd.Series(le.transform(values), index=df.index, name=col))

        numeric_df = _clean_numeric(df, self.numeric_features)
        scaled = pd.DataFrame(self.scaler.transform(numeric_df), columns=self.numeric_features, index=df.index)
        parts.append(scaled)

        X = pd.concat(parts, axis=1)[self.feature_list].values

        if self.target_column in df.columns:
            # Any target value unseen during fit (e.g. a held-out zero-day category
            # leaking into a transform call) falls back to the encoder's first known
            # class so .transform() never raises on unseen labels.
            fallback = self.target_encoder.classes_[0]
            str_targets = df[self.target_column].astype(str)
            known_targets = str_targets.where(str_targets.isin(self.target_encoder.classes_), fallback)
            y = self.target_encoder.transform(known_targets)
        else:
            y = np.array([])

        return X, y

    def get_feature_names(self) -> list[str]:
        return list(self.feature_list)

    def decode_target(self, y_encoded: np.ndarray) -> np.ndarray:
        return self.target_encoder.inverse_transform(y_encoded)


def split_known_unknown(df: pd.DataFrame, unknown_categories: list[str], target_column: str = "attack_cat") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a dataframe into (known, unknown) rows for zero-day / open-set simulation.

    `unknown_categories` are attack types entirely withheld from training so the
    open-set model must recognize them as "Unknown" rather than misclassifying
    them as a known attack type.
    """
    is_unknown = df[target_column].isin(unknown_categories)
    known_df = df.loc[~is_unknown].reset_index(drop=True)
    unknown_df = df.loc[is_unknown].reset_index(drop=True)
    logger.info(f"Split dataset: {len(known_df)} known rows, {len(unknown_df)} unknown/zero-day rows")
    return known_df, unknown_df


def add_merged_label(df: pd.DataFrame, merge_groups: dict[str, list[str]],
                      source_column: str = "attack_cat", target_column: str = "label_merged") -> pd.DataFrame:
    """Add a coarser label column by merging specific source categories into named groups
    (e.g. classes that are statistically indistinguishable in this feature set — see
    configs/config.yaml `data.label_merge_groups`). `source_column` is left untouched;
    categories not mentioned in any group pass through to `target_column` unchanged.
    """
    df = df.copy()
    category_to_group = {cat: group for group, cats in merge_groups.items() for cat in cats}
    df[target_column] = df[source_column].map(lambda c: category_to_group.get(c, c))
    return df
