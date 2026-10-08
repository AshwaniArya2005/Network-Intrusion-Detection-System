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
from sklearn.utils.class_weight import compute_sample_weight

from src.utils.logger import get_logger

logger = get_logger(__name__)

CATEGORICAL_FEATURES = {"proto", "service", "state"}
ENGINEERED_FEATURES = {"total_bytes", "total_pkts", "byte_ratio", "pkt_ratio", "avg_pkt_size", "duration_log"}

# Raw flow columns each engineered feature is computed from.
ENGINEERED_INPUTS = {
    "total_bytes": ["sbytes", "dbytes"],
    "byte_ratio": ["sbytes", "dbytes"],
    "total_pkts": ["spkts", "dpkts"],
    "pkt_ratio": ["spkts", "dpkts"],
    "avg_pkt_size": ["sbytes", "dbytes", "spkts", "dpkts"],
    "duration_log": ["dur"],
}
BASE_COLUMNS = ["sbytes", "dbytes", "spkts", "dpkts", "dur"]

# byte_ratio / pkt_ratio / avg_pkt_size are undefined when their denominator is 0. Real
# ratios are >= 0, so -1 is a distinct "undefined" sentinel: a flow with no reply
# (dbytes == 0, byte_ratio = -1) must not look like a flow that sent no data
# (sbytes == 0 with a reply, byte_ratio = 0).
UNDEFINED_RATIO = -1.0


def balanced_sample_weight(y: np.ndarray, power: float = 0.5) -> np.ndarray:
    """Square-rooted ("balanced" ** `power`, default 0.5) class weights, used by every model fit in this
    project; `model.class_weight_power` in configs/config.yaml sets the exponent (0 = unweighted, 1 = fully balanced).

    UNSW-NB15's attack categories are heavily imbalanced (e.g. Normal=56k rows vs.
    Analysis=2k). Full inverse-frequency weighting (Analysis at ~28x Normal) proved
    too aggressive in practice — it pushed recall up but tanked precision by leaking
    majority-class traffic into minority predictions. A hard cap on the ratio was
    tried too and scored worse on every metric (F1 0.60 vs 0.61, weaker zero-day
    detection) — square-rooting the weights was the best of the three in practice.
    """
    return compute_sample_weight("balanced", y) ** power


def _clean_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Coerce to numeric and sanitize +-inf (CICIDS2017's Flow Bytes/Packets-per-second
    columns are Infinity for zero-duration flows) and NaN to 0.0 so StandardScaler
    never sees a non-finite value."""
    numeric = df[columns].apply(pd.to_numeric, errors="coerce")
    return numeric.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def engineer_features(df: pd.DataFrame, allow_missing: bool = False) -> pd.DataFrame:
    """Add the 6 derived features referenced in configs/feature_sets.yaml.

    Raises ValueError if a base column (sbytes/dbytes/spkts/dpkts/dur) is missing, since
    silently treating it as 0 yields different features; pass allow_missing=True only when
    the caller has already validated the columns it needs (Preprocessor does). Ratios with
    a zero denominator are set to UNDEFINED_RATIO (-1), not 0 — see its comment.
    """
    missing = [c for c in BASE_COLUMNS if c not in df.columns]
    if missing and not allow_missing:
        raise ValueError(f"engineer_features needs columns {missing}")
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
        df[col] = df[col].replace([np.inf, -np.inf], np.nan).fillna(UNDEFINED_RATIO)
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
        self.metadata: dict = {}   # provenance (feature set, ranking source, ...) set by the training pipeline

    def _check_columns(self, df: pd.DataFrame, need_target: bool = False) -> None:
        missing = [c for c in self.required_columns + ([self.target_column] if need_target else []) if c not in df.columns]
        if missing:
            raise ValueError(f"Input is missing required columns: {missing}")

    def fit(self, df: pd.DataFrame) -> "Preprocessor":
        self._check_columns(df, need_target=True)
        df = engineer_features(df, allow_missing=True)
        for col in self.categorical_features:
            le = LabelEncoder()
            values = df[col].fillna("unknown").astype(str)
            le.fit(list(values) + ["__unseen__"])
            self.label_encoders[col] = le

        numeric_df = _clean_numeric(df, self.numeric_features)
        self.scaler.fit(numeric_df)

        self.target_encoder.fit(df[self.target_column].astype(str))
        self._fitted = True
        logger.info(f"Preprocessor fitted on {len(df)} rows, {len(self.feature_list)} features, "
                    f"{len(self.target_encoder.classes_)} target classes")
        return self

    @property
    def required_columns(self) -> list[str]:
        """Raw input columns a caller must supply: the raw features plus the base columns
        every requested engineered feature is derived from."""
        needed = [f for f in self.feature_list if f not in ENGINEERED_FEATURES]
        for f in self.feature_list:
            needed += ENGINEERED_INPUTS.get(f, [])
        return list(dict.fromkeys(needed))

    def transform_features(self, df: pd.DataFrame) -> np.ndarray:
        """Feature matrix only — for rows whose target labels are unknown to this
        preprocessor (e.g. held-out zero-day categories) or absent."""
        if not self._fitted:
            raise RuntimeError("Preprocessor.fit() must be called before transform().")
        self._check_columns(df)
        df = engineer_features(df, allow_missing=True)

        parts = []
        for col in self.categorical_features:
            le = self.label_encoders[col]
            values = df[col].fillna("unknown").astype(str)
            values = values.where(values.isin(le.classes_), "__unseen__")
            parts.append(pd.Series(le.transform(values), index=df.index, name=col))

        numeric_df = _clean_numeric(df, self.numeric_features)
        scaled = pd.DataFrame(self.scaler.transform(numeric_df), columns=self.numeric_features, index=df.index)
        parts.append(scaled)

        return pd.concat(parts, axis=1)[self.feature_list].values

    def transform(self, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        """(X, y). Raises ValueError if the target column holds a label unseen during fit —
        use transform_features() for rows that are meant to carry unknown labels."""
        X = self.transform_features(df)
        if self.target_column in df.columns:
            str_targets = df[self.target_column].astype(str)
            unseen = sorted(set(str_targets) - set(self.target_encoder.classes_))
            if unseen:
                raise ValueError(f"Target labels not seen during fit: {unseen}")
            y = self.target_encoder.transform(str_targets)
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
    a `data.label_schemes.<name>.merge_groups` entry in configs/config.yaml). `source_column` is left untouched;
    categories not mentioned in any group pass through to `target_column` unchanged.
    """
    df = df.copy()
    category_to_group = {cat: group for group, cats in merge_groups.items() for cat in cats}
    df[target_column] = df[source_column].map(lambda c: category_to_group.get(c, c))
    return df
