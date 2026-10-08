"""Few-shot adaptation helpers (reused by the official-split few-shot study and the cross-dataset curve).

Access level: FEW-SHOT = the training data plus k labelled rows drawn from the TARGET distribution (the official test
file, or the other dataset). The adaptation rows are removed from the evaluation set, so a method is never scored on
rows it saw. Nothing here looks at the labels of the remaining (evaluation) rows.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def draw_adaptation_sample(df: pd.DataFrame, k: int, label_column: str, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(adaptation rows, remaining rows): `k` rows drawn without replacement, stratified by `label_column` with
    proportional allocation (largest-remainder rounding; every class with rows gets at least one when k allows, and a
    class never gives more rows than it has). The remaining rows are the evaluation set. The draw is reproducible from `seed`."""
    if not 0 < k < len(df):
        raise ValueError(f"k must be between 1 and {len(df) - 1}, got {k}")
    rng = np.random.default_rng(seed)
    groups = {label: idx.to_numpy() for label, idx in df.groupby(label_column).groups.items()}
    share = pd.Series({label: len(idx) for label, idx in groups.items()}) * k / len(df)
    take = np.floor(share).astype(int)
    take = take.clip(lower=1) if k >= len(groups) else take
    remainder = k - int(take.sum())
    if remainder > 0:  # hand the remaining rows to the classes with the largest fractional parts
        take[(share - np.floor(share)).sort_values(ascending=False).index[:remainder]] += 1
    while take.sum() > k:  # the "at least one" floor can overshoot: take rows back from the largest classes
        take[take.idxmax()] -= 1
    chosen = np.concatenate([rng.choice(groups[label], size=min(int(n), len(groups[label])), replace=False) for label, n in take.items()])
    mask = df.index.isin(chosen)
    return df[mask].copy(), df[~mask].copy()


def adaptation_weights(weights: np.ndarray, is_adaptation: np.ndarray, fraction: float) -> np.ndarray:
    """Rescale the sample weights so the adaptation rows carry `fraction` of the total weight and the other rows keep
    theirs: the adaptation rows' relative (class-balancing) weights are kept, their sum becomes
    fraction / (1 - fraction) * (sum of the other rows' weights)."""
    if not 0 < fraction < 1:
        raise ValueError(f"fraction must be in (0, 1), got {fraction}")
    weights, flag = np.asarray(weights, dtype=float).copy(), np.asarray(is_adaptation, dtype=bool)
    if not flag.any():
        return weights
    weights[flag] *= fraction / (1 - fraction) * weights[~flag].sum() / weights[flag].sum()
    return weights


def with_adaptation(splits, adaptation_rows: pd.DataFrame, remaining_test: pd.DataFrame, fraction: float | None):
    """A copy of `splits` (pipelines.train_pipeline.Splits) whose training data also holds the adaptation rows (flagged in
    `adapt_flag`, weighted to carry `fraction` of the sample weight when given) and whose test split is the remaining rows."""
    from dataclasses import replace
    train = pd.concat([splits.train.assign(adapt_flag=False), adaptation_rows.assign(adapt_flag=True)], ignore_index=True)
    return replace(splits, train=train, test=remaining_test.reset_index(drop=True), adapt_fraction=fraction)


# ---- TRANSDUCTIVE helpers: they read the unlabelled FEATURES of the target rows and nothing else ----

def _feature_matrix(source: pd.DataFrame, target: pd.DataFrame, features: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    """Numeric matrix of both frames over `features` (categoricals as integer codes shared across the two frames) and
    the domain label (0 = source row, 1 = target row)."""
    from src.preprocessing import CATEGORICAL_FEATURES, engineer_features
    both = pd.concat([engineer_features(source[[c for c in source.columns if c != "attack_cat"]], allow_missing=True),
                      engineer_features(target[[c for c in target.columns if c != "attack_cat"]], allow_missing=True)], ignore_index=True)
    X = pd.DataFrame({f: pd.factorize(both[f])[0] if f in CATEGORICAL_FEATURES else pd.to_numeric(both[f], errors="coerce")
                      for f in features}).replace([np.inf, -np.inf], np.nan)
    return X, np.r_[np.zeros(len(source)), np.ones(len(target))]


def domain_importance_weights(source: pd.DataFrame, target: pd.DataFrame, features: list[str], clip: float, seed: int = 0,
                              folds: int = 5) -> np.ndarray:
    """Importance weights for the SOURCE (training) rows that make them resemble the TARGET (official test) rows: a
    domain classifier (source vs target, features only) gives p(target | x) cross-fitted over `folds` folds (a row's weight
    never comes from a model that saw that row); w = p / (1 - p) * n_source / n_target, clipped at `clip` and rescaled to
    mean 1 so the total sample weight is unchanged. Labels are never read (the label column is dropped)."""
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from xgboost import XGBClassifier
    X, domain = _feature_matrix(source, target, features)
    p = cross_val_predict(XGBClassifier(n_estimators=150, max_depth=5, learning_rate=0.1, subsample=0.9, n_jobs=-1, random_state=seed,
                                        eval_metric="logloss"), X, domain, cv=StratifiedKFold(folds, shuffle=True, random_state=seed),
                          method="predict_proba")[:, 1][: len(source)].astype(float)
    w = np.clip(p / np.clip(1 - p, 1e-6, None) * len(source) / len(target), None, clip)
    return w / w.mean()


def unlabelled_shift_ranking(source: pd.DataFrame, target: pd.DataFrame, features: list[str]) -> pd.Series:
    """`features` ranked by how differently they are distributed in the source and target rows over ALL rows, labels unused:
    Kolmogorov-Smirnov statistic (total-variation distance for the categorical proto / service / state), largest first."""
    from scipy.stats import ks_2samp
    from src.preprocessing import CATEGORICAL_FEATURES, engineer_features
    s = engineer_features(source[[c for c in source.columns if c != "attack_cat"]], allow_missing=True)
    t = engineer_features(target[[c for c in target.columns if c != "attack_cat"]], allow_missing=True)
    out = {}
    for f in features:
        if f in CATEGORICAL_FEATURES:
            ps, pt = s[f].value_counts(normalize=True), t[f].value_counts(normalize=True)
            out[f] = float(ps.sub(pt, fill_value=0).abs().sum() / 2)
        else:
            out[f] = float(ks_2samp(pd.to_numeric(s[f], errors="coerce").dropna(), pd.to_numeric(t[f], errors="coerce").dropna()).statistic)
    return pd.Series(out).sort_values(ascending=False)
