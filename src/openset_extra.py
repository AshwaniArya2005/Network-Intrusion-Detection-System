"""Extra open-set scores of Task 4.5 (protocol: results/task_4_5_protocol.md). Every score is "higher = more likely Unknown" and is fitted on known training / validation
flows only; nothing here sees a zero-day flow or an official-test label.

  per_class_thresholds / shift_by_class   one threshold per predicted class (the same false-Unknown rate inside every predicted class)
  predictive_mutual_information, member_variance, ensemble_msp   disagreement of an ensemble of models
  KnnScorer, MahalanobisScorer            distance to the training data in the scaled feature matrix
  pseudo_unknown_classes, relabel_unknown outlier exposure: known classes held out inside the training split become an "Unknown" class
  zero_day_percentile, matched_detection  diagnostics
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

EPS = 1e-12
PSEUDO_ORDER = ("Reconnaissance", "Generic", "Fuzzers", "Exploits")


def per_class_thresholds(scores: np.ndarray, predicted: np.ndarray, n_classes: int, target: float, min_rows: int = 30) -> np.ndarray:
    """Threshold per predicted class: the (1 - target) quantile of the known `scores` of the flows predicted as that class; a class with fewer than `min_rows` flows uses the
    global quantile. The flagged share inside every class (and so overall) is `target` on the rows the thresholds were fitted on."""
    scores, predicted = np.asarray(scores), np.asarray(predicted)
    global_threshold = float(np.quantile(scores, 1.0 - target))
    out = np.full(n_classes, global_threshold)
    for c in range(n_classes):
        rows = predicted == c
        if rows.sum() >= min_rows:
            out[c] = float(np.quantile(scores[rows], 1.0 - target))
    return out


def shift_by_class(scores: np.ndarray, predicted: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    """Score minus the threshold of the flow's predicted class: above 0 exactly when the per-class rule flags the flow."""
    return np.asarray(scores) - np.asarray(thresholds)[np.asarray(predicted)]


def _entropy(p: np.ndarray) -> np.ndarray:
    q = np.clip(p, EPS, 1.0)
    return -(q * np.log(q)).sum(axis=-1)


def predictive_mutual_information(member_proba: np.ndarray) -> np.ndarray:
    """(M, n, K) member probabilities -> entropy of the mean probability minus the mean member entropy (the epistemic part of the uncertainty)."""
    return _entropy(member_proba.mean(axis=0)) - _entropy(member_proba).mean(axis=0)


def member_variance(member_proba: np.ndarray) -> np.ndarray:
    """Variance of each class probability across the members, averaged over the classes."""
    return member_proba.var(axis=0).mean(axis=1)


def ensemble_msp(member_proba: np.ndarray) -> np.ndarray:
    """1 - the largest class probability of the mean member probability."""
    return 1.0 - member_proba.mean(axis=0).max(axis=1)


class KnnScorer:
    """Mean distance to the k nearest neighbours among a seeded uniform sample of the training rows (brute force, Euclidean)."""

    def __init__(self, k: int = 10, reference_size: int = 20000, seed: int = 0):
        self.k, self.reference_size, self.seed = k, reference_size, seed

    def fit(self, X_train: np.ndarray) -> "KnnScorer":
        rows = np.random.default_rng(self.seed).permutation(len(X_train))[: self.reference_size]
        self.index_ = NearestNeighbors(n_neighbors=self.k, algorithm="brute", n_jobs=-1).fit(np.asarray(X_train, dtype=float)[rows])
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        return self.index_.kneighbors(np.asarray(X, dtype=float), return_distance=True)[0].mean(axis=1)


class MahalanobisScorer:
    """Minimum over the training classes of the Mahalanobis distance to the class (class mean, class covariance + a ridge of `ridge` x the mean variance)."""

    def __init__(self, ridge: float = 0.01):
        self.ridge = ridge

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MahalanobisScorer":
        X, y = np.asarray(X, dtype=float), np.asarray(y)
        self.means_, self.precisions_ = [], []
        for c in np.unique(y):
            rows = X[y == c]
            cov = np.cov(rows, rowvar=False) if len(rows) > 1 else np.eye(X.shape[1])
            cov = np.atleast_2d(cov) + self.ridge * np.mean(np.diag(np.atleast_2d(cov))) * np.eye(X.shape[1])
            self.means_.append(rows.mean(axis=0))
            self.precisions_.append(np.linalg.pinv(cov))
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        distances = []
        for mean, precision in zip(self.means_, self.precisions_):
            d = X - mean
            distances.append(np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", d, precision, d), 0.0)))
        return np.min(distances, axis=0)


def pseudo_unknown_classes(held_out: list[str] | set[str], n: int = 2, order: tuple[str, ...] = PSEUDO_ORDER) -> list[str]:
    """The first `n` classes of `order` that are not among the evaluation's held-out classes: the known classes turned into the "Unknown" training class."""
    return [c for c in order if c not in set(held_out)][:n]


def relabel_unknown(frame: pd.DataFrame, classes: list[str], target_column: str, fine_column: str, label: str = "Unknown") -> pd.DataFrame:
    """A copy of `frame` in which every row of a class in `classes` carries the training label `label` (the fine-grained column is kept for reporting)."""
    out = frame.copy()
    out.loc[out[fine_column].isin(classes), target_column] = label
    return out


def zero_day_percentile(known_scores: np.ndarray, unknown_scores: np.ndarray) -> float:
    """Mean percentile of the zero-day scores among the known scores (0.5 = they look like a typical known flow; above 0.5 = more anomalous)."""
    known = np.sort(np.asarray(known_scores))
    return float((np.searchsorted(known, np.asarray(unknown_scores), side="left") / len(known)).mean())


def matched_detection(known_scores: np.ndarray, unknown_scores: np.ndarray, false_unknown_rate: float) -> float:
    """Diagnostic: share of zero-day flows above the threshold at which exactly `false_unknown_rate` of the known flows (the official-test flows) is flagged. Never used for selection."""
    return float((np.asarray(unknown_scores) > np.quantile(known_scores, 1.0 - false_unknown_rate)).mean())
