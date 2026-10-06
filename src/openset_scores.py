"""Open-set / zero-day scoring functions (Task 4; protocol: results/02_novelty1_open_set.md, section `Source: open_set_protocol.md`).

Every score is "higher = more likely Unknown", so a flow is flagged Unknown when its score exceeds a threshold taken as a quantile of the scores of KNOWN
validation flows (`flag_threshold`). Nothing here sees a zero-day flow or an official-test label when a threshold, a calibration or a normalisation is fitted.

  msp, entropy, margin   functions of the class probabilities
  ConformalScorer        class-conditional split-conformal p-values; score = 1 - the largest p-value (a flow is Unknown exactly when its prediction set is empty)
  AnomalyScorer          isolation forest fitted on Normal TRAINING flows only
  RankNormalizer         empirical-CDF rank on a calibration set, so scores on different scales can be combined
  combine                `mean` or `max` of two ranks
"""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

EPS = 1e-12


def msp_score(proba: np.ndarray) -> np.ndarray:
    """1 - the maximum class probability (the current max-softmax confidence, as an uncertainty)."""
    return 1.0 - proba.max(axis=1)


def entropy_score(proba: np.ndarray) -> np.ndarray:
    """Shannon entropy of the class probabilities divided by ln K (0 = certain, 1 = uniform)."""
    q = np.clip(proba, EPS, 1.0)
    return -(q * np.log(q)).sum(axis=1) / np.log(proba.shape[1])


def margin_score(proba: np.ndarray) -> np.ndarray:
    """1 - (largest probability - second largest probability): near 1 when two classes compete."""
    top = np.sort(proba, axis=1)
    return 1.0 - (top[:, -1] - top[:, -2])


class ConformalScorer:
    """Class-conditional (Mondrian) split-conformal p-values from a calibration set of KNOWN flows.

    Nonconformity of a flow for class k is 1 - p_k(x). For each class the calibration flows of that class give a sorted nonconformity sample;
    p_k(x) = (number of those calibration scores >= 1 - p_k(x) + 1) / (n_k + 1). A class absent from the calibration set gets p-value 0 (it can never be in a set).
    score(x) = 1 - max_k p_k(x); the prediction set at level alpha is {k: p_k(x) > alpha}, so the set is empty exactly when score(x) >= 1 - alpha."""

    def fit(self, proba: np.ndarray, y: np.ndarray) -> "ConformalScorer":
        self.n_classes_ = proba.shape[1]
        self.sorted_ = [np.sort(1.0 - proba[y == k, k]) for k in range(self.n_classes_)]
        return self

    def pvalues(self, proba: np.ndarray) -> np.ndarray:
        out = np.zeros(proba.shape)
        for k, cal in enumerate(self.sorted_):
            if len(cal):
                greater_equal = len(cal) - np.searchsorted(cal, 1.0 - proba[:, k], side="left")
                out[:, k] = (greater_equal + 1) / (len(cal) + 1)
        return out

    def score(self, proba: np.ndarray) -> np.ndarray:
        return 1.0 - self.pvalues(proba).max(axis=1)

    def prediction_sets(self, proba: np.ndarray, alpha: float) -> np.ndarray:
        """Boolean (n, K) matrix: class k is in the set of a flow when its p-value exceeds alpha."""
        return self.pvalues(proba) > alpha


class AnomalyScorer:
    """Isolation forest fitted on Normal training flows only; score = -score_samples (higher = more anomalous)."""

    def __init__(self, seed: int = 0, n_estimators: int = 200):
        self.forest = IsolationForest(n_estimators=n_estimators, random_state=seed, n_jobs=-1)

    def fit(self, X_normal: np.ndarray) -> "AnomalyScorer":
        self.forest.fit(X_normal)
        return self

    def score(self, X: np.ndarray) -> np.ndarray:
        return -self.forest.score_samples(X)


class RankNormalizer:
    """Empirical-CDF rank of a score against a calibration sample of known flows, in (0, 1]."""

    def fit(self, calibration_scores: np.ndarray) -> "RankNormalizer":
        self.sorted_ = np.sort(calibration_scores)
        return self

    def transform(self, scores: np.ndarray) -> np.ndarray:
        return np.searchsorted(self.sorted_, scores, side="right") / len(self.sorted_)


def combine(rank_a: np.ndarray, rank_b: np.ndarray, rule: str) -> np.ndarray:
    """Combine two ranks: `mean` (average) or `max` (the larger one)."""
    if rule == "mean":
        return (rank_a + rank_b) / 2.0
    if rule == "max":
        return np.maximum(rank_a, rank_b)
    raise ValueError(f"unknown combination rule {rule!r} (mean or max)")


def flag_threshold(known_scores: np.ndarray, target_false_unknown_rate: float) -> float:
    """Threshold above which a flow is flagged Unknown: the (1 - target) quantile of the scores of KNOWN validation flows, so about `target` of them are flagged."""
    return float(np.quantile(known_scores, 1.0 - target_false_unknown_rate))


def unknown_auroc(known_scores: np.ndarray, unknown_scores: np.ndarray) -> float:
    """AUROC of a score for separating known flows (label 0) from unknown / zero-day flows (label 1); 0.5 = no separation."""
    scores = np.concatenate([known_scores, unknown_scores])
    labels = np.r_[np.zeros(len(known_scores)), np.ones(len(unknown_scores))]
    return float(roc_auc_score(labels, scores))


BASE_SCORES = ("msp", "entropy", "margin", "conformal")
RULES = ("mean", "max")


class ScoreSuite:
    """All candidate scores of one fitted model. `fit` takes the calibration half of the known validation flows (class probabilities, encoded labels, feature matrix)
    and the Normal training matrix; `scores(proba, X)` returns {name: score array} for the base scores, `iforest` and every `iforest+<base>:<rule>` combination."""

    def __init__(self, seed: int = 0):
        self.anomaly = AnomalyScorer(seed)
        self.conformal = ConformalScorer()

    def _base(self, proba: np.ndarray, X: np.ndarray) -> dict[str, np.ndarray]:
        return {"msp": msp_score(proba), "entropy": entropy_score(proba), "margin": margin_score(proba), "conformal": self.conformal.score(proba),
                "iforest": self.anomaly.score(X)}

    def fit(self, cal_proba: np.ndarray, cal_y: np.ndarray, cal_X: np.ndarray, normal_train_X: np.ndarray) -> "ScoreSuite":
        self.anomaly.fit(normal_train_X)
        self.conformal.fit(cal_proba, cal_y)
        base = self._base(cal_proba, cal_X)
        self.rankers = {name: RankNormalizer().fit(s) for name, s in base.items()}
        return self

    def scores(self, proba: np.ndarray, X: np.ndarray) -> dict[str, np.ndarray]:
        base = self._base(proba, X)
        out = dict(base)
        ranks = {name: self.rankers[name].transform(s) for name, s in base.items()}
        for name in BASE_SCORES:
            for rule in RULES:
                out[f"iforest+{name}:{rule}"] = combine(ranks["iforest"], ranks[name], rule)
        return out
