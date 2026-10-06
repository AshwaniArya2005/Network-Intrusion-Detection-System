"""Renders the experiment CSVs (results/*.csv) as static PNG charts under
results/plots/<model.type>/, so the numbers in experiment_results.csv,
explanation_stability.csv, and cross_dataset_results.csv are readable at a glance
without opening a spreadsheet.

Palette and chart-chrome values follow the project's validated categorical palette
(fixed hue order, never cycled) — see the dataviz skill's references/palette.md.
"""
from __future__ import annotations

import logging
import re
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # this module only writes PNG files: never open a GUI backend (headless runs, background jobs, tests)
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from src.utils.logger import get_logger

logger = get_logger(__name__)
logging.getLogger("matplotlib").setLevel(logging.WARNING)  # quiet its noisy category-axis INFO logs

# Fixed categorical hue order — reused across every chart so a given series
# (e.g. "accuracy") always gets the same color if it appears in multiple plots.
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, GREEN, VIOLET, RED = "#e87ba4", "#008300", "#4a3aa7", "#e34948"
CATEGORICAL_8 = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
# Sequential single-hue (blue) ramp, light -> dark, for magnitude encoding (confusion matrix).
SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281", "#0d366b"]
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
AXIS = "#c3c2b7"


def _new_axes(figsize: tuple[float, float] = (8, 5)) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRIDLINE, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(AXIS)
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    ax.title.set_color(INK_PRIMARY)
    return fig, ax


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)
    logger.info(f"Saved plot to {path}")


def plot_feature_set_metrics(df: pd.DataFrame, out_dir: Path) -> None:
    """Accuracy/precision/recall/f1 vs. feature-set size (closed-set rows — these
    4 metrics are identical between closed/open-set since the wrapper only relabels
    low-confidence predictions, it doesn't change the underlying classifier)."""
    closed = df[df["open_set"] == False].sort_values("n_features")  # noqa: E712
    order = closed["feature_set"].astype(str).tolist()  # str: numeric tiers read back from CSV would plot off-screen

    fig, ax = _new_axes()
    for metric, color in zip(["accuracy", "precision", "recall", "f1"], [BLUE, ORANGE, AQUA, YELLOW]):
        ax.plot(order, closed[metric], marker="o", markersize=8, linewidth=2, color=color, label=metric)

    # No direct end-labels here: accuracy/precision and recall/f1 sit almost on top of
    # each other at every feature-set size, so per-line labels would collide — the
    # legend (4 series, distinct colors) is the only identity cue this chart needs.
    ax.set_xlabel("Feature set (tier)", color=INK_SECONDARY)
    ax.set_ylabel("Score", color=INK_SECONDARY)
    ax.set_ylim(0, 1)
    ax.set_xlim(-0.3, len(order) - 0.7)
    ax.set_title("Model performance vs. feature-set size", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, labelcolor=INK_SECONDARY)
    _save(fig, out_dir / "feature_set_metrics.png")


def plot_open_set_detection(df: pd.DataFrame, out_dir: Path) -> None:
    """Zero-day unknown-detection rate vs. false "Unknown" alarm rate, by feature-set size."""
    open_rows = df[df["open_set"] == True].sort_values("n_features")  # noqa: E712
    if open_rows.empty or "unknown_detection_rate" not in open_rows:
        return
    order = open_rows["feature_set"].tolist()

    fig, ax = _new_axes()
    x = range(len(order))
    width = 0.35
    ax.bar([i - width / 2 for i in x], open_rows["unknown_detection_rate"], width, color=BLUE, label="Zero-day detection rate")
    ax.bar([i + width / 2 for i in x], open_rows["false_unknown_alarm_rate"], width, color=ORANGE, label="False \"Unknown\" alarm rate")
    ax.set_xticks(list(x))
    ax.set_xticklabels(order)
    ax.set_xlabel("Feature set (tier)", color=INK_SECONDARY)
    ax.set_ylabel("Rate", color=INK_SECONDARY)
    ax.set_ylim(0, 1)
    ax.set_title("Open-set zero-day detection vs. false alarms", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, labelcolor=INK_SECONDARY)
    _save(fig, out_dir / "open_set_detection.png")


def plot_open_set_sweep(metrics_dir: Path, experiment_df: pd.DataFrame, out_dir: Path, legacy_threshold: float = 0.65,
                        tag: str = "") -> None:
    """Zero-day detection rate vs. false-"Unknown" rate across thresholds (one curve per
    feature set, from open_set_sweep_<set>.csv), with each set's chosen operating point
    (validation-selected threshold) and the old fixed `legacy_threshold` point marked."""
    open_rows = experiment_df[experiment_df["open_set"] == True]  # noqa: E712
    if open_rows.empty or "open_set_threshold" not in open_rows:
        return
    fig, ax = _new_axes(figsize=(7, 6))
    ax.grid(axis="x", color=GRIDLINE, linewidth=1, zorder=0)
    for i, (_, row) in enumerate(open_rows.iterrows()):
        path = Path(metrics_dir) / f"open_set_sweep_{row['feature_set']}{tag}.csv"
        if not path.exists():
            continue
        sweep = pd.read_csv(path)
        color = CATEGORICAL_8[i % len(CATEGORICAL_8)]
        ax.plot(sweep["false_alarm_rate"], sweep["detection_rate"], color=color, linewidth=2, label=f"{row['feature_set']} features")
        chosen = sweep.loc[(sweep["threshold"] - row["open_set_threshold"]).abs().idxmin()]
        ax.scatter([chosen["false_alarm_rate"]], [chosen["detection_rate"]], color=color, s=60, zorder=3, marker="o")
        legacy = sweep[sweep["threshold"].round(2) == round(legacy_threshold, 2)]
        if not legacy.empty:
            ax.scatter(legacy["false_alarm_rate"], legacy["detection_rate"], color=color, s=60, zorder=3, marker="s", facecolors="none")
    ax.set_xlabel("False \"Unknown\" rate on known test traffic", color=INK_SECONDARY)
    ax.set_ylabel("Zero-day detection rate", color=INK_SECONDARY)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_title(f"Open-set operating curve (dot: chosen threshold, square: {legacy_threshold})", fontsize=11, fontweight="bold")
    ax.legend(frameon=False, labelcolor=INK_SECONDARY)
    _save(fig, out_dir / f"open_set_sweep{tag}.png")


def plot_explanation_stability(df: pd.DataFrame, out_dir: Path) -> None:
    """rank_correlation / cosine_similarity / topk_overlap for each feature-set-pair comparison."""
    # Same-set/different-seed reference rows (comparison column) live in the CSV, not this chart.
    if "comparison" in df:
        df = df[df["comparison"] == "nested_feature_sets"]
    if df.empty:
        return
    # config_a/config_b are always "<model.type>_<feature_set>" (see run_all_experiments.py's
    # run_explanation_stability) — strip whatever the model-type prefix is, generically,
    # so this isn't a list of hardcoded model names that goes stale as new ones are added.
    strip_prefix = re.compile(r"^[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*_(?=\d+$)")
    labels = [f"{strip_prefix.sub('', a)}\nvs {strip_prefix.sub('', b)}"
              for a, b in zip(df["config_a"], df["config_b"])]

    fig, ax = _new_axes(figsize=(9, 5))
    x = range(len(labels))
    width = 0.25
    metrics = [("rank_correlation", BLUE), ("cosine_similarity", ORANGE), ("topk_overlap", AQUA)]
    for i, (metric, color) in enumerate(metrics):
        offset = (i - 1) * width
        ax.bar([xi + offset for xi in x], df[metric], width, color=color, label=metric.replace("_", " "))
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Score", color=INK_SECONDARY)
    ax.set_ylim(0, 1.05)
    ax.set_title("Explanation stability across feature-set sizes", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, labelcolor=INK_SECONDARY)
    _save(fig, out_dir / "explanation_stability.png")


def plot_cross_dataset(df: pd.DataFrame, out_dir: Path) -> None:
    """Accuracy/F1 for each (strategy, train->test direction) combination. Degenerate
    (constant-prediction) rows are left out: they don't rank anything."""
    if "degenerate" in df:
        df = df[~df["degenerate"]]
    if df.empty:
        return
    labels = [f"{s}\n{t}→{te}" for s, t, te in zip(df["strategy"], df["train"], df["test"])]

    fig, ax = _new_axes(figsize=(9, 5))
    x = range(len(labels))
    width = 0.35
    ax.bar([i - width / 2 for i in x], df["accuracy"], width, color=BLUE, label="accuracy")
    ax.bar([i + width / 2 for i in x], df["f1"], width, color=ORANGE, label="f1")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Score", color=INK_SECONDARY)
    ax.set_ylim(0, 1)
    ax.set_title("Cross-dataset generalization by feature-selection strategy", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, labelcolor=INK_SECONDARY)
    _save(fig, out_dir / "cross_dataset_generalization.png")


def _render_confusion_matrix(cm_norm: "np.ndarray", labels: list[str], title: str, out_path: Path,
                              block_boundaries: list[int] | None = None) -> None:
    """Shared renderer for a row-normalized confusion matrix heatmap. `block_boundaries`
    (row/col indices) get a heavier divider line, for the grouped variant below."""
    from matplotlib.colors import LinearSegmentedColormap

    n = len(labels)
    cmap = LinearSegmentedColormap.from_list("seq_blue", SEQUENTIAL_BLUE)
    fig, ax = plt.subplots(figsize=(1.1 * n + 2, 1.1 * n + 1.5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    im = ax.imshow(cm_norm, cmap=cmap, vmin=0, vmax=1)

    ax.set_xticks(range(n))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9, color=INK_SECONDARY)
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, fontsize=9, color=INK_SECONDARY)
    ax.set_xlabel("Predicted", color=INK_SECONDARY)
    ax.set_ylabel("True", color=INK_SECONDARY)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i in range(n):
        for j in range(n):
            value = cm_norm[i, j]
            text_color = SURFACE if value > 0.6 else INK_PRIMARY
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", color=text_color, fontsize=8)

    for boundary in (block_boundaries or []):
        if 0 < boundary < n:
            ax.axhline(boundary - 0.5, color=INK_PRIMARY, linewidth=2)
            ax.axvline(boundary - 0.5, color=INK_PRIMARY, linewidth=2)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=INK_MUTED, labelsize=8)
    cbar.set_label("Recall (row-normalized)", color=INK_SECONDARY)
    ax.set_title(textwrap.fill(title, 58, replace_whitespace=False), fontsize=10, fontweight="bold", color=INK_PRIMARY)   # wrapped: long titles are clipped by the figure edge
    _save(fig, out_path)


def plot_confusion_matrix(y_test, y_pred, class_names, out_path: Path, title: str = "Confusion matrix") -> None:
    """Row-normalized (recall-per-class) confusion matrix — a sequential blue heatmap,
    since this encodes one magnitude (fraction of each true class), not identity."""
    from sklearn.metrics import confusion_matrix as _confusion_matrix

    n = len(class_names)
    cm = _confusion_matrix(y_test, y_pred, labels=range(n))
    cm_norm = (cm / cm.sum(axis=1, keepdims=True).clip(min=1)).astype(float)
    _render_confusion_matrix(cm_norm, list(class_names), title, out_path)


def plot_confusion_matrix_grouped(y_test, y_pred, class_names, out_path: Path,
                                   normal_label: str = "Normal", front_groups: tuple[str, ...] = ("Overlap-Group-1",),
                                   title: str | None = None) -> None:
    """Confusion matrix reordered into visual blocks — Normal | merged overlap group(s) |
    the remaining separable attack classes — with a heavy divider between blocks. Use this
    instead of plot_confusion_matrix whenever the target includes a label-merge group, so
    the chart reads as the model's real granularity rather than implying every class is
    equally distinguishable in a flat NxN grid."""
    import numpy as np
    from sklearn.metrics import confusion_matrix as _confusion_matrix

    class_names = list(class_names)
    front = [c for c in (normal_label, *front_groups) if c in class_names]
    rest = sorted(c for c in class_names if c not in front)
    order = front + rest
    order_idx = [class_names.index(c) for c in order]

    n = len(class_names)
    cm = _confusion_matrix(y_test, y_pred, labels=range(n))
    cm = cm[np.ix_(order_idx, order_idx)]
    cm_norm = (cm / cm.sum(axis=1, keepdims=True).clip(min=1)).astype(float)

    # One divider after each singleton front block (Normal, then each merge group) —
    # the remaining classes stay ungrouped since they're already individually separable.
    boundaries = list(range(1, len(front) + 1))
    title = title or f"Confusion matrix (grouped: {' | '.join(front)} | other attacks)"
    _render_confusion_matrix(cm_norm, order, title, out_path, block_boundaries=boundaries)


def plot_confusion_matrix_for_scheme(y_test, y_pred, class_names, out_path: Path, scheme_name: str,
                                     merge_groups: dict, normal_label: str = "Normal", title_prefix: str = "") -> None:
    """Confusion matrix laid out for the active label scheme: blocks Normal | each merged group |
    other attacks when the scheme merges classes, the plain matrix when it merges none.
    `title_prefix` (for example "xgboost, 48 features, tier 30: ") says which model and feature set it is."""
    if merge_groups:
        plot_confusion_matrix_grouped(y_test, y_pred, class_names, out_path, normal_label, tuple(merge_groups),
                                      title=f"{title_prefix}Confusion matrix, scheme '{scheme_name}' (Normal | {' | '.join(merge_groups)} | other attacks)")
    else:
        plot_confusion_matrix(y_test, y_pred, class_names, out_path, title=f"{title_prefix}Confusion matrix, scheme '{scheme_name}'")


def plot_roc_curve(y_test, y_proba, class_names, out_path: Path, normal_label: str | None = "Normal", title_prefix: str = "") -> None:
    """ROC figure with two kinds of curve: one thin one-vs-rest curve per class (their mean AUC is the
    macro AUC), and, when `normal_label` is one of the classes, one bold attack-versus-normal curve whose
    score is 1 - P(Normal) (the attack-vs-normal AUC of the reports). Up to 8 classes fit the
    project's validated 8-hue categorical order (adjacent-pair CVD gates hold for
    line/bar forms across the full set, unlike scatter/small-multiples). The title states both AUCs."""
    import numpy as np
    from sklearn.metrics import auc as _auc
    from sklearn.metrics import roc_curve as _roc_curve
    from sklearn.preprocessing import label_binarize

    n = len(class_names)
    y_bin = label_binarize(y_test, classes=range(n))
    if n == 2:  # label_binarize collapses binary targets to a single column
        y_bin = pd.DataFrame({0: 1 - y_bin.ravel(), 1: y_bin.ravel()}).values

    fig, ax = _new_axes(figsize=(7, 7))
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, color=AXIS, label="Chance")

    all_fpr = pd.Series(dtype=float)
    tprs = []
    for i, name in enumerate(class_names):
        fpr, tpr, _ = _roc_curve(y_bin[:, i], y_proba[:, i])
        roc_auc = _auc(fpr, tpr)
        color = CATEGORICAL_8[i % len(CATEGORICAL_8)]
        ax.plot(fpr, tpr, linewidth=2, color=color, label=f"{name} (AUC={roc_auc:.2f})")
        tprs.append((fpr, tpr))

    macro_auc = sum(_auc(fpr, tpr) for fpr, tpr in tprs) / len(tprs)
    if normal_label is not None and normal_label in list(class_names):
        normal_idx = list(class_names).index(normal_label)
        y_attack = (np.asarray(y_test) != normal_idx).astype(int)
        a_fpr, a_tpr, _ = _roc_curve(y_attack, 1.0 - np.asarray(y_proba)[:, normal_idx])
        attack_auc = _auc(a_fpr, a_tpr)
        ax.plot(a_fpr, a_tpr, linewidth=3.5, color=INK_PRIMARY, label=f"Attack vs {normal_label}, score 1 - P({normal_label}) (AUC={attack_auc:.3f})", zorder=5)
        title = (f"{title_prefix}ROC curves\nbold: attack vs {normal_label} (score 1 - P({normal_label})), AUC={attack_auc:.3f}\n"
                 f"thin: each class one-vs-rest, macro AUC={macro_auc:.3f}")
    else:
        title = f"{title_prefix}ROC curves, each class one-vs-rest (macro AUC={macro_auc:.3f})"
    ax.set_xlabel("False positive rate", color=INK_SECONDARY)
    ax.set_ylabel("True positive rate", color=INK_SECONDARY)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_title("\n".join(textwrap.fill(line, 64) for line in title.split("\n")), fontsize=10, fontweight="bold")
    ax.legend(frameon=False, labelcolor=INK_SECONDARY, fontsize=8, loc="lower right")
    _save(fig, out_path)


PRIMARY_POOL = 48   # the primary feature pool; its plots carry no pool prefix


def tier_plot_paths(plots_dir: Path, pool_size: int, tier: str, label_scheme: str = "current") -> tuple[Path, Path]:
    """(confusion-matrix path, ROC path) of one tier of one pool: `confusion_matrix_<T>f.png` for the primary pool (48), and
    `confusion_matrix_pool<N>_<T>f.png` for a comparison pool, because the same tier number in another pool is another feature set;
    a non-default label scheme adds its name."""
    suffix = "" if label_scheme == "current" else f"_{label_scheme}"
    stem = f"{tier}f{suffix}" if pool_size == PRIMARY_POOL else f"pool{pool_size}_{tier}f{suffix}"
    d = Path(plots_dir)
    return d / f"confusion_matrix_{stem}.png", d / f"roc_curve_{stem}.png"


def write_tier_plots(predictions: dict, plots_dir: Path, pool_size: int, tier: str, scheme_name: str, merge_groups: dict,
                     normal_label: str = "Normal", model_type: str = "") -> tuple[Path, Path]:
    """Write the confusion matrix and the ROC figure of one (pool, tier) from a `predictions_out` dict
    (y_test, y_pred, y_proba, class_names); returns the two paths (see `tier_plot_paths`)."""
    cm_path, roc_path = tier_plot_paths(plots_dir, pool_size, tier, scheme_name)
    prefix = f"{model_type + ', ' if model_type else ''}{pool_size}-feature pool, tier {tier}: "
    plot_confusion_matrix_for_scheme(predictions["y_test"], predictions["y_pred"], predictions["class_names"], cm_path, scheme_name, merge_groups,
                                     normal_label, title_prefix=prefix)
    plot_roc_curve(predictions["y_test"], predictions["y_proba"], predictions["class_names"], roc_path, normal_label, title_prefix=prefix)
    return cm_path, roc_path


def generate_all_plots(model_type: str, results_dir: Path,
                        experiment_df: pd.DataFrame | None = None,
                        stability_df: pd.DataFrame | None = None,
                        cross_dataset_df: pd.DataFrame | None = None, scheme: str = "current") -> Path:
    """Render every available result CSV to results/plots/<model_type>/*.png. Any
    dataframe left as None is skipped (e.g. when only a single model was trained)."""
    out_dir = Path(results_dir) / "plots" / model_type / ("" if scheme == "current" else scheme)  # per-scheme subdir
    tag = "" if scheme == "current" else f"_{scheme}"
    if experiment_df is not None and not experiment_df.empty:
        plot_feature_set_metrics(experiment_df, out_dir)
        plot_open_set_detection(experiment_df, out_dir)
        plot_open_set_sweep(Path(results_dir) / "metrics" / model_type, experiment_df, out_dir, tag=tag)
    if stability_df is not None and not stability_df.empty:
        plot_explanation_stability(stability_df, out_dir)
    if cross_dataset_df is not None and not cross_dataset_df.empty:
        plot_cross_dataset(cross_dataset_df, out_dir)
    return out_dir
