"""Classification metrics, including the open-set "unknown detection rate"."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, average: str = "macro") -> dict[str, float]:
    """Standard multiclass classification metrics."""
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, average=average, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, average=average, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, average=average, zero_division=0)), 4),
    }


def unknown_detection_rate(is_true_unknown: np.ndarray, is_predicted_unknown: np.ndarray) -> dict[str, float]:
    """How well the open-set wrapper flags genuinely novel (zero-day) samples as
    "Unknown", and how often it wrongly flags known samples as Unknown.

    `is_true_unknown`: boolean mask, True for samples from a withheld zero-day category.
    `is_predicted_unknown`: boolean mask, True where OpenSetWrapper predicted "Unknown".
    """
    is_true_unknown = np.asarray(is_true_unknown, dtype=bool)
    is_predicted_unknown = np.asarray(is_predicted_unknown, dtype=bool)

    n_unknown = is_true_unknown.sum()
    n_known = (~is_true_unknown).sum()

    detection_rate = float((is_predicted_unknown & is_true_unknown).sum() / n_unknown) if n_unknown else float("nan")
    false_alarm_rate = float((is_predicted_unknown & ~is_true_unknown).sum() / n_known) if n_known else float("nan")

    return {
        "unknown_detection_rate": round(detection_rate, 4),
        "false_unknown_alarm_rate": round(false_alarm_rate, 4),
        "n_zero_day_samples": int(n_unknown),
    }


def build_overlap_diagnostics(fine_grained_true: np.ndarray, y_pred_labels: np.ndarray,
                               label_merge_groups: dict[str, list[str]]) -> dict[str, pd.DataFrame]:
    """For each label-merge group (see configs/config.yaml `data.label_merge_groups`),
    build a row-normalized crosstab of the ORIGINAL fine-grained label vs. the merged-
    target model's prediction, restricted to rows whose true fine-grained label belongs
    to that group. This is a diagnostic, not a headline metric: it confirms the merge
    didn't just hide the confusion — rows that were truly Analysis/Backdoor/DoS should
    now be routed into the merged group at a high rate, rather than scattered elsewhere.
    """
    tables = {}
    for group_name, source_categories in label_merge_groups.items():
        df = pd.DataFrame({"true_fine_grained": fine_grained_true, "predicted": y_pred_labels})
        subset = df[df["true_fine_grained"].isin(source_categories)]
        if subset.empty:
            continue
        tables[group_name] = pd.crosstab(subset["true_fine_grained"], subset["predicted"], normalize="index").round(4)
    return tables
