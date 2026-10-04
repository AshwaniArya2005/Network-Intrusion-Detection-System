"""Methods for lowering the official-split Normal false-positive rate (Task 2.7; protocol: results/task_2_7_protocol.md).

TRANSDUCTIVE helpers read the unlabelled FEATURES (through the model's probabilities) of the target rows and nothing else:
  fit_temperature / apply_temperature   temperature scaling fitted on known validation rows (ZERO-SHOT)
  weighted_prior                        class prior a model trained with sample weights implies
  em_prior                              EM estimate of the class shares of unlabelled rows (Saerens, Latinne, Decaestecker 2002)
  prior_correct                         re-weight probabilities by pi_hat / pi_model
  em_gate                               validation-only check that EM recovers a simulated prior shift
  pseudo_labels                         confident predictions as labels (self-training)
FEW-SHOT row selection (labels are revealed only for the chosen rows; selection uses features and the zero-shot probabilities only):
  random_selection, entropy_selection, diverse_selection, mix_selection
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.spatial import cKDTree
from sklearn.cluster import MiniBatchKMeans

EPS = 1e-12


def apply_temperature(proba: np.ndarray, temperature: float) -> np.ndarray:
    """Probabilities proportional to p ** (1 / T): T > 1 flattens them, T < 1 sharpens them (the softmax of the logits divided by T)."""
    logits = np.log(np.clip(proba, EPS, 1.0)) / temperature
    logits -= logits.max(axis=1, keepdims=True)
    q = np.exp(logits)
    return q / q.sum(axis=1, keepdims=True)


def fit_temperature(proba: np.ndarray, y: np.ndarray, bounds: tuple[float, float] = (0.25, 5.0)) -> float:
    """The temperature in `bounds` that minimises the negative log-likelihood of the labels `y` (encoded class indices) of known validation rows."""
    y = np.asarray(y)
    def nll(t: float) -> float:
        return float(-np.log(np.clip(apply_temperature(proba, t)[np.arange(len(y)), y], EPS, 1.0)).mean())
    return float(minimize_scalar(nll, bounds=bounds, method="bounded").x)


def weighted_prior(y: np.ndarray, weights: np.ndarray, n_classes: int) -> np.ndarray:
    """Class shares of the training rows weighted by the sample weights actually used (the prior a model fitted with those weights implies)."""
    shares = np.bincount(np.asarray(y), weights=np.asarray(weights, dtype=float), minlength=n_classes)
    return shares / shares.sum()


def prior_correct(proba: np.ndarray, pi_new: np.ndarray, pi_model: np.ndarray) -> np.ndarray:
    """p'(y|x) proportional to p(y|x) * pi_new(y) / pi_model(y), renormalised."""
    q = proba * (np.asarray(pi_new) / np.clip(np.asarray(pi_model), EPS, None))
    return q / q.sum(axis=1, keepdims=True)


def em_prior(proba: np.ndarray, pi_model: np.ndarray, max_iter: int = 100, tol: float = 1e-6) -> np.ndarray:
    """EM estimate of the class shares of the rows `proba` came from, given that the model's posteriors assume the prior `pi_model`
    (Saerens et al. 2002): start at pi_model; E-step: correct the posteriors with the current shares; M-step: the shares are their mean."""
    pi = np.asarray(pi_model, dtype=float).copy()
    for _ in range(max_iter):
        new = prior_correct(proba, pi, pi_model).mean(axis=0)
        done = np.abs(new - pi).max() < tol
        pi = new
        if done:
            break
    return pi


def em_gate(proba: np.ndarray, y: np.ndarray, pi_model: np.ndarray, seeds=(42, 43, 44, 45, 46), sigma: float = 1.0) -> dict:
    """Validation-only check of the EM estimator: resample the known validation rows (probabilities `proba`, labels `y`) to class shares proportional to
    (validation share) * exp(sigma * z), z ~ N(0, 1), once per seed. Returns the mean L1 error of the EM estimate against the simulated shares, the mean L1 distance
    between `pi_model` and the simulated shares, and `passes` = EM error below half of that distance."""
    y = np.asarray(y)
    n_classes = proba.shape[1]
    val_share = np.bincount(y, minlength=n_classes) / len(y)
    present = np.flatnonzero(val_share > 0)
    em_err, base_err = [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        share = np.zeros(n_classes)
        share[present] = val_share[present] * np.exp(sigma * rng.standard_normal(len(present)))
        share /= share.sum()
        row_weight = (share / np.clip(val_share, EPS, None))[y]      # a row of class c is drawn with weight share_c / val_share_c
        idx = rng.choice(len(y), size=len(y), replace=True, p=row_weight / row_weight.sum())
        simulated = np.bincount(y[idx], minlength=n_classes) / len(idx)
        em_err.append(np.abs(em_prior(proba[idx], pi_model) - simulated).sum())
        base_err.append(np.abs(np.asarray(pi_model) - simulated).sum())
    return {"em_l1_error": float(np.mean(em_err)), "model_prior_l1_distance": float(np.mean(base_err)), "passes": bool(np.mean(em_err) < 0.5 * np.mean(base_err))}


def pseudo_labels(proba: np.ndarray, tau: float) -> tuple[np.ndarray, np.ndarray]:
    """(mask of rows whose largest probability is at least `tau`, predicted class index of every row)."""
    return proba.max(axis=1) >= tau, proba.argmax(axis=1)


def entropy(proba: np.ndarray) -> np.ndarray:
    q = np.clip(proba, EPS, 1.0)
    return -(q * np.log(q)).sum(axis=1)


def random_selection(n_rows: int, k: int, seed: int) -> np.ndarray:
    """k distinct row positions drawn uniformly (labels are not used)."""
    return np.sort(np.random.default_rng(seed).choice(n_rows, size=k, replace=False))


def entropy_selection(proba: np.ndarray, k: int) -> np.ndarray:
    """The k rows with the largest predictive entropy (ties broken by position)."""
    return np.sort(np.argsort(-entropy(proba), kind="stable")[:k])


def diverse_selection(X: np.ndarray, k: int, seed: int = 0) -> np.ndarray:
    """k distinct rows, each the nearest row to one centroid of a k-means with k clusters (MiniBatchKMeans) on the scaled feature matrix `X`;
    if two centroids share a nearest row the remaining slots are filled with random unused rows (seeded)."""
    if k >= len(X):
        return np.arange(len(X))
    centres = MiniBatchKMeans(n_clusters=k, n_init=1, batch_size=4096, random_state=seed).fit(X).cluster_centers_
    chosen = list(dict.fromkeys(cKDTree(X).query(centres)[1].tolist()))
    if len(chosen) < k:
        rest = np.setdiff1d(np.arange(len(X)), chosen)
        chosen += np.random.default_rng(seed).choice(rest, size=k - len(chosen), replace=False).tolist()
    return np.sort(np.array(chosen))


def mix_selection(proba: np.ndarray, X: np.ndarray, k: int, seed: int = 0) -> np.ndarray:
    """Half the budget (rounded up) from `entropy_selection`, the rest from `diverse_selection` on the rows not already chosen."""
    first = entropy_selection(proba, (k + 1) // 2)
    rest = np.setdiff1d(np.arange(len(X)), first)
    second = rest[diverse_selection(X[rest], k - len(first), seed)] if k - len(first) > 0 else np.array([], dtype=int)
    return np.sort(np.concatenate([first, second]))
