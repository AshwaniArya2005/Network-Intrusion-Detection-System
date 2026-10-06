"""Faithfulness of SHAP explanations by deletion and insertion (Task 5; protocol: results/03_novelty2_explanations.md, section `Source: explanations_protocol.md`).

An explanation is faithful when the features it calls important change the model's output when they are removed. For one flow with predicted class c and SHAP values s (class c):
  deletion   replace the chosen features by a baseline value -> drop in P(c), and whether the predicted class flips
  insertion  start from the baseline vector and put the chosen features back -> P(c)
The chosen features are the k with the largest SHAP value ("top"), the k with the smallest absolute SHAP value ("least") or k drawn at random ("random").
Everything works on the model's input matrix (numeric columns standardised, categorical columns integer codes), so the baseline is a vector in that space.
"""
from __future__ import annotations

import numpy as np

KS = (1, 3, 5, 10)
METHODS = ("top", "least", "random")


def feature_order(shap: np.ndarray, method: str, rng: np.random.Generator) -> np.ndarray:
    """(n, F) feature indexes per flow in the order they would be removed / inserted: `top` = largest SHAP value first, `least` = smallest absolute SHAP first,
    `random` = an independent random permutation per flow. Ties are broken by feature position."""
    if method == "top":
        return np.argsort(-shap, axis=1, kind="stable")
    if method == "least":
        return np.argsort(np.abs(shap), axis=1, kind="stable")
    if method == "random":
        return np.argsort(rng.random(shap.shape), axis=1)
    raise ValueError(f"unknown method {method!r} (top, least or random)")


def median_baseline(X_train: np.ndarray, categorical_columns: list[int]) -> np.ndarray:
    """Per-column training median; the training mode (smallest of equally frequent codes) for the label-encoded categorical columns, where a median code is meaningless."""
    base = np.median(X_train, axis=0)
    for c in categorical_columns:
        values, counts = np.unique(X_train[:, c], return_counts=True)
        base[c] = values[np.argmax(counts)]
    return base


def baseline_matrix(kind: str, n: int, X_train: np.ndarray, categorical_columns: list[int], rng: np.random.Generator) -> np.ndarray:
    """(n, F) baseline vectors: `median` (the same vector for every flow) or `random_row` (one random training row per flow, all of its features)."""
    if kind == "median":
        return np.tile(median_baseline(X_train, categorical_columns), (n, 1))
    if kind == "random_row":
        return X_train[rng.integers(0, len(X_train), n)].copy()
    raise ValueError(f"unknown baseline {kind!r} (median or random_row)")


def predicted_probability(model, X: np.ndarray, pred: np.ndarray) -> np.ndarray:
    return model.predict_proba(X)[np.arange(len(X)), pred]


def delete_features(X: np.ndarray, order: np.ndarray, k: int, baseline: np.ndarray) -> np.ndarray:
    """A copy of X in which the first k features of each flow's `order` are replaced by the baseline's values."""
    out, rows, chosen = X.copy(), np.arange(len(X))[:, None], order[:, :k]
    out[rows, chosen] = baseline[rows, chosen]
    return out


def insert_features(X: np.ndarray, order: np.ndarray, k: int, baseline: np.ndarray) -> np.ndarray:
    """The baseline vectors with the first k features of each flow's `order` put back from X."""
    out, rows, chosen = baseline.copy(), np.arange(len(X))[:, None], order[:, :k]
    out[rows, chosen] = X[rows, chosen]
    return out


def faithfulness_curves(model, X: np.ndarray, pred: np.ndarray, shap: np.ndarray, X_train: np.ndarray, categorical_columns: list[int], rng: np.random.Generator,
                        ks: tuple[int, ...] = KS, baselines: tuple[str, ...] = ("median", "random_row")) -> dict:
    """Per-flow results for every (method, baseline, k): {"drop": ..., "flip": ..., "insertion": ...}[(method, baseline, k)] -> (n,) arrays. `drop` = P(pred) - P(pred) after deleting
    the chosen features (comprehensiveness, higher = the features mattered), `flip` = the argmax changed, `insertion` = P(pred) with only the chosen features of the flow on a baseline vector.
    The same orders and the same baseline vectors are used for deletion and insertion; one random permutation per flow serves every k of the `random` method."""
    p0 = predicted_probability(model, X, pred)
    orders = {m: feature_order(shap, m, rng) for m in METHODS}
    out = {"drop": {}, "flip": {}, "insertion": {}, "p0": p0}
    for b in baselines:
        base = baseline_matrix(b, len(X), X_train, categorical_columns, rng)
        for m in METHODS:
            for k in ks:
                proba = model.predict_proba(delete_features(X, orders[m], k, base))
                out["drop"][(m, b, k)] = p0 - proba[np.arange(len(X)), pred]
                out["flip"][(m, b, k)] = proba.argmax(axis=1) != pred
                out["insertion"][(m, b, k)] = predicted_probability(model, insert_features(X, orders[m], k, base), pred)
    return out


def bootstrap_mean_interval(values: np.ndarray, n_boot: int = 1000, seed: int = 0, level: float = 0.95) -> tuple[float, float, float]:
    """(mean, lower, upper) of the mean of `values` over `n_boot` resamples of the flows."""
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = values[rng.integers(0, len(values), (n_boot, len(values)))].mean(axis=1)
    lo, hi = np.quantile(means, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(values.mean()), float(lo), float(hi)


def bootstrap_difference_interval(a: np.ndarray, b: np.ndarray, n_boot: int = 1000, seed: int = 0, level: float = 0.95) -> tuple[float, float, float]:
    """(mean(a) - mean(b), lower, upper) with the two samples of flows resampled independently (a two-sample bootstrap, used for test flows against validation flows)."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    rng = np.random.default_rng(seed)
    diffs = a[rng.integers(0, len(a), (n_boot, len(a)))].mean(axis=1) - b[rng.integers(0, len(b), (n_boot, len(b)))].mean(axis=1)
    lo, hi = np.quantile(diffs, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(a.mean() - b.mean()), float(lo), float(hi)


def stratified_sample(strata: np.ndarray, per_class: int, special: str, special_n: int, rng: np.random.Generator) -> np.ndarray:
    """Sorted row positions: up to `per_class` rows from every stratum except `special`, and up to `special_n` rows from `special`, each drawn without replacement."""
    strata = np.asarray(strata)
    chosen = []
    for s in sorted(set(strata.tolist())):
        rows = np.flatnonzero(strata == s)
        n = special_n if s == special else per_class
        chosen.append(rng.choice(rows, size=min(n, len(rows)), replace=False))
    return np.sort(np.concatenate(chosen)) if chosen else np.array([], dtype=int)


def additivity_error(shap_row_sum: np.ndarray, expected_value: np.ndarray, raw_margin: np.ndarray) -> np.ndarray:
    """|sum of a flow's SHAP values + the explainer's expected value - the model's raw margin| for the predicted class (all arrays (n,))."""
    return np.abs(np.asarray(shap_row_sum) + np.asarray(expected_value) - np.asarray(raw_margin))
