"""Classification metrics, including the open-set "unknown detection rate"."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, precision_score, recall_score, roc_auc_score


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, average: str = "macro") -> dict[str, float]:
    """Standard multiclass classification metrics."""
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, average=average, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, average=average, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, average=average, zero_division=0)), 4),
    }


def per_class_metrics(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]) -> dict[str, float]:
    """Flat per-class precision/recall/F1 (keys like `recall_Normal`) for one CSV row."""
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, labels=range(len(class_names)), zero_division=0)
    out = {}
    for name, pi, ri, fi in zip(class_names, p, r, f):
        out.update({f"precision_{name}": round(float(pi), 4), f"recall_{name}": round(float(ri), 4),
                    f"f1_{name}": round(float(fi), 4)})
    return out


def binary_detection_metrics(true_labels: np.ndarray, pred_labels: np.ndarray, normal_label: str = "Normal") -> dict[str, float]:
    """Attack-vs-normal view of a multiclass prediction: `detection_rate` is the share of
    true attacks predicted as ANY attack class (so a DoS called Exploits still counts),
    `false_positive_rate` the share of normal flows predicted as any attack."""
    true_attack = np.asarray(true_labels) != normal_label
    pred_attack = np.asarray(pred_labels) != normal_label
    return {
        "detection_rate": round(float((pred_attack & true_attack).sum() / max(true_attack.sum(), 1)), 4),
        "false_positive_rate": round(float((pred_attack & ~true_attack).sum() / max((~true_attack).sum(), 1)), 4),
    }


def fpr_at_detection(true_labels: np.ndarray, proba: np.ndarray, class_names: list[str], normal_label: str = "Normal",
                     targets: tuple[float, ...] = (0.90, 0.95, 0.99)) -> dict[str, float]:
    """Second operating point of the attack-vs-normal view: the false-positive rate needed to
    reach each detection rate, scoring a flow by 1 - P(Normal) (so the FPR is not only reported at
    the argmax decision). Keys like `fpr_at_95_detection`."""
    is_attack = np.asarray(true_labels) != normal_label
    score = 1.0 - proba[:, list(class_names).index(normal_label)]
    fpr, tpr, _ = roc_curve(is_attack, score)
    return {f"fpr_at_{round(t * 100)}_detection": round(float(fpr[np.searchsorted(tpr, t, side="left")]), 4) for t in targets}


def confusion_matrix_tables(true_labels: np.ndarray, pred_labels: np.ndarray, class_names: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Confusion matrix as DataFrames, rows = true class, columns = predicted class (every class
    present even with zero rows): (counts, row-normalised shares). The row for a class answers
    "where do this class's flows go?", e.g. the Normal row gives each class's share of Normal flows."""
    names = list(class_names)
    counts = pd.crosstab(pd.Categorical(np.asarray(true_labels), categories=names),
                         pd.Categorical(np.asarray(pred_labels), categories=names), dropna=False)
    counts.index.name, counts.columns.name = "true", "predicted"
    return counts, counts.div(counts.sum(axis=1).replace(0, 1), axis=0).round(4)


def group_recall_from_diagnostics(diagnostics: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Fine-grained recall of each original category routed into its merged group, read off
    the overlap diagnostic tables (keys like `recall_Analysis_as_Overlap-Group-1`)."""
    out = {}
    for group, table in diagnostics.items():
        for category in table.index:
            out[f"recall_{category}_as_{group}"] = float(table.loc[category, group]) if group in table.columns else 0.0
    return out


def unknown_auroc(known_confidence: np.ndarray, unknown_confidence: np.ndarray) -> float:
    """AUROC of max-softmax confidence for separating known (high) from zero-day (low) flows."""
    scores = np.concatenate([known_confidence, unknown_confidence])
    is_known = np.concatenate([np.ones(len(known_confidence)), np.zeros(len(unknown_confidence))])
    return round(float(roc_auc_score(is_known, scores)), 4)


def threshold_sweep(known_confidence: np.ndarray, unknown_confidence: np.ndarray, thresholds) -> pd.DataFrame:
    """(threshold, detection_rate, false_alarm_rate): share of zero-day / known flows whose
    max-softmax confidence falls below each threshold (i.e. would be flagged Unknown)."""
    return pd.DataFrame({
        "threshold": list(thresholds),
        "detection_rate": [float((unknown_confidence < t).mean()) for t in thresholds],
        "false_alarm_rate": [float((known_confidence < t).mean()) for t in thresholds],
    }).round(4)


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
    """For each label-merge group (the active `data.label_schemes` entry in configs/config.yaml),
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
