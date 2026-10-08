"""Test-row bootstrap for the headline metrics, with paired differences between models.

Test rows are resampled with replacement; the SAME resampled rows are scored for every model, so a difference
between two models (e.g. 48 vs 40 features) is a paired difference whose interval excludes the row-sampling noise
both models share. Zero-day rows (open-set detection) are resampled independently of the known test rows.
Metrics come from the confusion matrix of the resample (no per-resample sklearn call), so 1,000 resamples are fast.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

METRICS = ["accuracy", "f1", "detection_rate", "false_positive_rate", "normal_to_Fuzzers", "unknown_detection_rate"]


def confusion_metrics(cm: np.ndarray, normal: int, fuzzers: int) -> dict[str, float]:
    """accuracy, macro F1 (over every class), attack-vs-normal detection / false-positive rate and the share of
    Normal flows predicted Fuzzers from one confusion matrix (rows = true, columns = predicted)."""
    tp = np.diag(cm).astype(float)
    denominator = 2 * tp + (cm.sum(axis=0) - tp) + (cm.sum(axis=1) - tp)
    attack = np.arange(len(cm)) != normal
    normal_total = max(cm[normal].sum(), 1)
    return {"accuracy": tp.sum() / max(cm.sum(), 1),
            "f1": float(np.mean(np.where(denominator > 0, 2 * tp / np.maximum(denominator, 1), 0.0))),
            "detection_rate": cm[np.ix_(attack, attack)].sum() / max(cm[attack].sum(), 1),
            "false_positive_rate": cm[normal, attack].sum() / normal_total,
            "normal_to_Fuzzers": cm[normal, fuzzers] / normal_total}


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int, normal: int, fuzzers: int, flags: np.ndarray) -> dict[str, float]:
    cm = np.bincount(y_true * n_classes + y_pred, minlength=n_classes ** 2).reshape(n_classes, n_classes)
    return {**confusion_metrics(cm, normal, fuzzers), "unknown_detection_rate": float(flags.mean())}


def bootstrap(models: dict[str, dict], n_classes: int, normal: int, fuzzers: int, n_boot: int = 1000, seed: int = 0
              ) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """`models`: name -> {"y_true", "y_pred" (encoded known test rows, identical rows for every model), "unknown_flags"
    (bool per zero-day row: flagged Unknown)}. Returns (point estimates indexed by model, {model: draws}) with one row
    per resample and a column per metric."""
    names = list(models)
    first = models[names[0]]
    for name in names[1:]:
        if not (np.array_equal(models[name]["y_true"], first["y_true"]) and len(models[name]["unknown_flags"]) == len(first["unknown_flags"])):
            raise ValueError(f"{name} was not evaluated on the same test rows as {names[0]}: a paired bootstrap needs identical rows")
    n, n_unknown = len(first["y_true"]), len(first["unknown_flags"])
    rng = np.random.default_rng(seed)
    draws = {name: [] for name in names}
    for _ in range(n_boot):
        idx, idx_unknown = rng.integers(0, n, n), rng.integers(0, n_unknown, n_unknown)
        for name, m in models.items():
            draws[name].append(_metrics(m["y_true"][idx], m["y_pred"][idx], n_classes, normal, fuzzers, m["unknown_flags"][idx_unknown]))
    point = pd.DataFrame({name: _metrics(m["y_true"], m["y_pred"], n_classes, normal, fuzzers, m["unknown_flags"])
                          for name, m in models.items()}).T[METRICS]
    return point, {name: pd.DataFrame(rows)[METRICS] for name, rows in draws.items()}


def intervals(point: pd.DataFrame, draws: dict[str, pd.DataFrame], level: float = 0.95) -> pd.DataFrame:
    """Percentile interval of each model's metrics: columns model, metric, estimate, ci_low, ci_high."""
    lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
    return pd.DataFrame([{"model": name, "metric": m, "estimate": round(float(point.loc[name, m]), 4),
                          "ci_low": round(float(d[m].quantile(lo)), 4), "ci_high": round(float(d[m].quantile(hi)), 4)}
                         for name, d in draws.items() for m in METRICS])


def paired_differences(point: pd.DataFrame, draws: dict[str, pd.DataFrame], pairs: list[tuple[str, str]], level: float = 0.95) -> pd.DataFrame:
    """(b - a) for each (a, b): the point difference, its percentile interval over the SHARED resamples and whether the
    interval excludes zero."""
    lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
    rows = []
    for a, b in pairs:
        for m in METRICS:
            diff = draws[b][m] - draws[a][m]
            low, high = float(diff.quantile(lo)), float(diff.quantile(hi))
            rows.append({"comparison": f"{b} - {a}", "metric": m, "difference": round(float(point.loc[b, m] - point.loc[a, m]), 4),
                         "ci_low": round(low, 4), "ci_high": round(high, 4), "excludes_zero": bool(low > 0 or high < 0)})
    return pd.DataFrame(rows)
