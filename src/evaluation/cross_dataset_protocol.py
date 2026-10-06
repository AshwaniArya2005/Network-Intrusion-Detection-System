"""Leak-free cross-dataset protocol (Task 6; protocol: results/task_6_protocol.md).

Everything here works on feature MATRICES of the 14 common features (engineered exactly as the models see them), so every split, metric and transform is a small pure function:
  split_positions / cap_blocks / thin_blocks   block-disjoint splits of row positions in file order, with a gap between groups, for ANY subset of rows
  block_mix                                    per-block class mix (attack share and dominant attack type)
  fit_binary / score / evaluate_scores         the binary XGBoost model, the primary and secondary metrics and the degenerate-row rule
  shap_importance / univariate_auroc           importance and the per-feature attack-vs-normal relation
  QuantileMapper / standardise / ks_ranking    label-free alignment of the target to the source
  fit_adapted                                  source rows plus labelled target rows carrying a fixed share of the sample weight
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from scipy.special import ndtri
from sklearn.metrics import roc_auc_score, roc_curve

from src.adaptation import adaptation_weights
from src.evaluation.metrics import attack_rates, select_attack_threshold
from src.models.model_factory import create_model
from src.preprocessing import _clean_numeric, balanced_sample_weight, engineer_features

COMMON_FEATURES = ["dur", "spkts", "dpkts", "sbytes", "dbytes", "rate", "smean", "dmean", "total_bytes", "total_pkts", "byte_ratio", "pkt_ratio", "avg_pkt_size", "duration_log"]
MODEL_PARAMS = {"n_estimators": 200, "max_depth": 6, "learning_rate": 0.1, "subsample": 0.9, "colsample_bytree": 0.9, "min_child_weight": 3, "reg_lambda": 1.5, "n_jobs": 8,
                "eval_metric": "logloss", "random_state": 42}
BLOCK, BUFFER = 1000, 200
DEGENERATE_SHARE = 0.01
DETECTION = 0.95


# ---------------------------------------------------------------- features and splits
def feature_matrix(df: pd.DataFrame, features: list[str] = COMMON_FEATURES) -> np.ndarray:
    """(n, len(features)) float matrix: engineered features, non-finite values set to 0 (as the preprocessor does)."""
    return _clean_numeric(engineer_features(df, allow_missing=True), features).to_numpy(dtype=float)


def _nearest_distance(x: np.ndarray, ref: np.ndarray) -> np.ndarray:
    if len(ref) == 0:
        return np.full(len(x), np.inf)
    idx = np.searchsorted(ref, x)
    return np.minimum(np.abs(x - ref[np.clip(idx - 1, 0, len(ref) - 1)]), np.abs(x - ref[np.clip(idx, 0, len(ref) - 1)]))


def split_positions(positions: np.ndarray, share: float, seed: int, block_size: int = BLOCK, buffer: int = BUFFER) -> tuple[np.ndarray, np.ndarray]:
    """(A, B): the row positions (file order) cut into blocks of `block_size` consecutive file positions; a random `share` of the blocks goes to A, the rest to B, and every row
    within `buffer` file positions of a row of the other group is dropped from both, so no A row has a neighbour (a row within the sliding window) in B."""
    positions = np.sort(np.asarray(positions))
    groups = positions // block_size
    ids = np.unique(groups)
    a_ids = np.random.default_rng(seed).choice(ids, size=max(1, round(share * len(ids))), replace=False)
    in_a = np.isin(groups, a_ids)
    a, b = positions[in_a], positions[~in_a]
    return a[_nearest_distance(a, b) > buffer], b[_nearest_distance(b, a) > buffer]


def cap_blocks(positions: np.ndarray, max_rows: int, seed: int, block_size: int = BLOCK) -> np.ndarray:
    """Sorted positions of whole blocks drawn at random until `max_rows` rows are reached (all positions when there are fewer)."""
    positions = np.sort(np.asarray(positions))
    if len(positions) <= max_rows:
        return positions
    groups = positions // block_size
    chosen, total = [], 0
    for g in np.random.default_rng(seed).permutation(np.unique(groups)):
        n = int((groups == g).sum())
        chosen.append(g)
        total += n
        if total >= max_rows:
            break
    return positions[np.isin(groups, chosen)]


def thin_blocks(positions: np.ndarray, fraction: float, seed: int, block_size: int = BLOCK) -> np.ndarray:
    """Whole blocks kept at random: about `fraction` of the blocks (at least one)."""
    positions = np.sort(np.asarray(positions))
    groups = positions // block_size
    ids = np.unique(groups)
    keep = np.random.default_rng(seed).choice(ids, size=max(1, round(fraction * len(ids))), replace=False)
    return positions[np.isin(groups, keep)]


def block_mix(attack: np.ndarray, y: np.ndarray, block_size: int = BLOCK) -> pd.DataFrame:
    """One row per block: rows, attack share, and the dominant label among the block's attack rows ("Normal" when the block has none) with its share of the block."""
    frame = pd.DataFrame({"block": np.arange(len(y)) // block_size, "attack": np.asarray(attack, dtype=object), "y": np.asarray(y)})
    rows = []
    for block, g in frame.groupby("block"):
        attacks = g.loc[g["y"] == 1, "attack"]
        top = attacks.value_counts()
        rows.append({"block": int(block), "rows": len(g), "attack_share": float(g["y"].mean()), "dominant": top.index[0] if len(top) else "Normal", "dominant_share": float(top.iloc[0] / len(g)) if len(top) else 1.0})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- model and metrics
def fit_binary(X: np.ndarray, y: np.ndarray, seed: int, sample_weight: np.ndarray | None = None, columns: list[int] | None = None):
    """The binary XGBoost model (balanced ** 0.5 sample weights unless given) on the columns `columns` of X; None when y has one class only."""
    if len(np.unique(y)) < 2:
        return None
    Xs = X if columns is None else X[:, columns]
    w = balanced_sample_weight(np.asarray(y), 0.5) if sample_weight is None else sample_weight
    return create_model("xgboost", {**MODEL_PARAMS, "random_state": seed}).fit(Xs, y, sample_weight=w)


def score(model, X: np.ndarray, columns: list[int] | None = None) -> np.ndarray:
    """P(attack)."""
    return model.predict_proba(X if columns is None else X[:, columns])[:, 1]


def operating_threshold(y: np.ndarray, s: np.ndarray, detection: float = DETECTION) -> float | None:
    """Threshold on P(attack) reaching `detection` of the attacks of (y, s) at the lowest FPR; None when one class is missing."""
    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        return None
    return float(select_attack_threshold(y.astype(bool), s, target_detection=detection))


def evaluate_scores(y: np.ndarray, s: np.ndarray, threshold: float | None) -> dict:
    """Primary and secondary metrics of scores `s` on rows with labels `y`: at the argmax (P >= 0.5): balanced accuracy, FPR, detection, the predicted attack share and the degenerate flag
    (share below 1% or above 99%: the argmax metrics are then NaN, never ranked); at `threshold`: FPR and detection; AUROC; and the threshold-free FPR at exactly 95% detection."""
    y, s = np.asarray(y).astype(int), np.asarray(s)
    pred = s >= 0.5
    share = float(pred.mean())
    det_arg, fpr_arg = float(pred[y == 1].mean()), float(pred[y == 0].mean())
    degenerate = min(share, 1 - share) < DEGENERATE_SHARE
    both = len(np.unique(y)) == 2
    out = {"balanced_accuracy": np.nan if degenerate else (det_arg + 1 - fpr_arg) / 2, "fpr_argmax": np.nan if degenerate else fpr_arg, "detection_argmax": np.nan if degenerate else det_arg,
           "balanced_accuracy_unranked": (det_arg + 1 - fpr_arg) / 2, "predicted_attack_share": share, "degenerate": bool(degenerate), "auroc": float(roc_auc_score(y, s)) if both else np.nan,
           "n_eval": int(len(y)), "n_attack": int(y.sum())}
    if both and threshold is not None:
        det, fpr = attack_rates(y.astype(bool), s, threshold)
        out.update(fpr_at_threshold=float(fpr), detection_at_threshold=float(det))
    else:
        out.update(fpr_at_threshold=np.nan, detection_at_threshold=np.nan)
    if both:
        fpr_curve, tpr_curve, _ = roc_curve(y, s)
        out["fpr_at_95_threshold_free"] = float(fpr_curve[np.searchsorted(tpr_curve, DETECTION, side="left")])
    else:
        out["fpr_at_95_threshold_free"] = np.nan
    return out


def type_recall(attack: np.ndarray, y: np.ndarray, s: np.ndarray, threshold: float | None, min_rows: int = 100) -> pd.DataFrame:
    """Recall per attack type present with at least `min_rows` rows: at the argmax and at `threshold` (types below the minimum are left out: their recall is not reportable)."""
    attack, y, s = np.asarray(attack, dtype=object), np.asarray(y), np.asarray(s)
    rows = []
    for t in sorted(set(attack[y == 1].tolist())):
        m = (attack == t) & (y == 1)
        if m.sum() >= min_rows:
            rows.append({"attack_type": t, "n": int(m.sum()), "recall_argmax": float((s[m] >= 0.5).mean()), "recall_at_threshold": float((s[m] >= threshold).mean()) if threshold is not None else np.nan})
    return pd.DataFrame(rows, columns=["attack_type", "n", "recall_argmax", "recall_at_threshold"])


# ---------------------------------------------------------------- diagnostics
def shap_importance(model, X: np.ndarray, features: list[str], n: int = 2000, seed: int = 0) -> pd.Series:
    """Mean absolute SHAP value per feature of a binary tree model on a seeded sample of n rows."""
    import shap
    rows = X[np.random.default_rng(seed).choice(len(X), size=min(n, len(X)), replace=False)]
    values = shap.TreeExplainer(model.underlying_model).shap_values(rows)
    values = values[:, :, 1] if np.ndim(values) == 3 else values
    return pd.Series(np.abs(values).mean(axis=0), index=features)


def univariate_auroc(X: np.ndarray, y: np.ndarray, features: list[str]) -> pd.DataFrame:
    """AUROC of each feature alone for attack (1) against normal (0), the direction (above / below 0.5) and whether the feature is absent (|AUROC - 0.5| < 0.05)."""
    rows = []
    for j, f in enumerate(features):
        a = 0.5 if np.ptp(X[:, j]) == 0 else float(roc_auc_score(y, X[:, j]))
        rows.append({"feature": f, "auroc": a, "direction": "attack higher" if a > 0.5 else "attack lower", "absent": abs(a - 0.5) < 0.05})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- label-free alignment (TRANSDUCTIVE)
def standardise(X: np.ndarray, mean: np.ndarray | None = None, std: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(z, mean, std) with the given statistics, or the matrix's own."""
    mean = X.mean(axis=0) if mean is None else mean
    std = X.std(axis=0) if std is None else std
    return (X - mean) / np.where(std > 0, std, 1.0), mean, std


class QuantileMapper:
    """Each column through its own empirical CDF (mid-ranks, ties averaged) to a normal score; fitted on one dataset's unlabelled features."""

    def fit(self, X: np.ndarray) -> "QuantileMapper":
        self.sorted_ = np.sort(X, axis=0)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        out = np.empty_like(X, dtype=float)
        n = len(self.sorted_)
        for j in range(X.shape[1]):
            col = self.sorted_[:, j]
            rank = (np.searchsorted(col, X[:, j], side="left") + np.searchsorted(col, X[:, j], side="right")) / 2.0
            out[:, j] = ndtri((rank + 0.5) / (n + 1.0))
        return out


def ks_ranking(Xs: np.ndarray, Xt: np.ndarray, features: list[str], max_rows: int = 100_000, seed: int = 0) -> pd.Series:
    """Features ranked by the Kolmogorov-Smirnov statistic between source and unlabelled target (seeded samples of up to `max_rows`), largest first."""
    rng = np.random.default_rng(seed)
    s = Xs[rng.choice(len(Xs), min(max_rows, len(Xs)), replace=False)]
    t = Xt[rng.choice(len(Xt), min(max_rows, len(Xt)), replace=False)]
    return pd.Series({f: float(ks_2samp(s[:, j], t[:, j]).statistic) for j, f in enumerate(features)}).sort_values(ascending=False)


# ---------------------------------------------------------------- few-shot
def fit_adapted(Xs: np.ndarray, ys: np.ndarray, Xa: np.ndarray, ya: np.ndarray, seed: int, fraction: float = 0.5, columns: list[int] | None = None):
    """Source rows plus labelled target rows; the labelled rows keep their relative (class-balancing) weights and together carry `fraction` of the total sample weight."""
    X, y = np.vstack([Xs, Xa]), np.r_[ys, ya]
    w = np.r_[balanced_sample_weight(np.asarray(ys), 0.5), balanced_sample_weight(np.asarray(ya), 0.5) if len(np.unique(ya)) > 1 else np.ones(len(ya))]
    w = adaptation_weights(w, np.r_[np.zeros(len(ys), bool), np.ones(len(ya), bool)], fraction)
    return fit_binary(X, y, seed, w, columns)
