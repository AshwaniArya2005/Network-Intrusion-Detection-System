"""Main training pipeline — fully config-driven. Run from the project root:

    python pipelines/train_pipeline.py

Trains the model configured in configs/config.yaml (`model.type`, `feature_selection.active_set`,
`open_set.enabled`), evaluates it, and saves the model + preprocessor to models_saved/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_sample_weight

from src.data_loader import load_unsw
from src.evaluation.metrics import build_overlap_diagnostics, compute_metrics, unknown_detection_rate
from src.evaluation.plots import plot_confusion_matrix_grouped, plot_roc_curve
from src.models.model_factory import create_model
from src.models.open_set_wrapper import OpenSetWrapper
from src.preprocessing import Preprocessor, add_merged_label, split_known_unknown
from src.utils.config_loader import get_active_features, get_metrics_dir, load_config, load_feature_sets, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)


def load_split_data(config: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load UNSW-NB15, hold out zero-day categories, and split the remaining known
    traffic into train/test sets. Returns (train_df, test_df, unknown_df)."""
    data_cfg = config["data"]
    df = load_unsw(
        resolve_path(config["paths"]["unsw_train"]),
        resolve_path(config["paths"]["unsw_test"]),
        seed=config["project"]["seed"],
        synthetic_rows=data_cfg["synthetic_fallback_rows"],
    )
    # Label-level only: adds `label_merged` (the primary training target) without touching
    # `attack_cat` (the fine-grained column, preserved for the overlap diagnostic table).
    # Categories not named in any group (Worms/Shellcode included) pass through unchanged,
    # so the zero-day split below is unaffected by the merge.
    df = add_merged_label(df, data_cfg["label_merge_groups"],
                           source_column=data_cfg["fine_grained_target_column"], target_column=data_cfg["target_column"])
    known_df, unknown_df = split_known_unknown(df, data_cfg["unknown_attack_categories"], data_cfg["target_column"])
    train_df, test_df = train_test_split(
        known_df, test_size=data_cfg["test_size"], random_state=config["project"]["seed"],
        stratify=known_df[data_cfg["target_column"]],
    )
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True), unknown_df


def train_and_evaluate(
    config: dict,
    feature_sets: dict,
    feature_set_name: str,
    open_set_enabled: bool,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    unknown_df: pd.DataFrame,
    save_artifacts: bool = True,
    predictions_out: dict | None = None,
) -> dict:
    """Train one model configuration and return its metrics dict. Optionally save the
    fitted model + preprocessor to models_saved/ for later evaluation/dashboard use.

    If `predictions_out` is passed, it's populated with y_test/y_pred/y_proba/class_names
    so a caller can render a confusion matrix or ROC curve without retraining."""
    data_cfg = config["data"]
    model_cfg = config["model"]
    features = get_active_features(config, feature_sets, feature_set_name)

    preprocessor = Preprocessor(feature_list=features, target_column=data_cfg["target_column"]).fit(train_df)
    X_train, y_train = preprocessor.transform(train_df)
    X_test, y_test = preprocessor.transform(test_df)

    # UNSW-NB15's attack categories are heavily imbalanced (e.g. Normal=56k rows vs.
    # Analysis=2k). Full inverse-frequency weighting (Analysis at ~28x Normal) proved
    # too aggressive in practice — it pushed recall up but tanked precision by leaking
    # majority-class traffic into minority predictions. A hard cap on the ratio was
    # tried too and scored worse on every metric (F1 0.60 vs 0.61, weaker zero-day
    # detection) — square-rooting the weights was the best of the three in practice.
    sample_weight = compute_sample_weight("balanced", y_train) ** 0.5

    model = create_model(model_cfg["type"], model_cfg["params"])
    model.fit(X_train, y_train, sample_weight=sample_weight)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    metrics = compute_metrics(y_test, y_pred)

    if predictions_out is not None:
        predictions_out.update(
            y_test=y_test, y_pred=y_pred, y_proba=y_proba,
            class_names=preprocessor.target_encoder.classes_,
            y_pred_labels=preprocessor.decode_target(y_pred),
            fine_grained_true=test_df[data_cfg["fine_grained_target_column"]].values,
        )

    result = {
        "model_type": model_cfg["type"],
        "feature_set": feature_set_name,
        "n_features": len(features),
        "open_set": open_set_enabled,
        "n_train": len(train_df),
        "n_test": len(test_df),
        **metrics,
    }

    tag = "open" if open_set_enabled else "closed"
    model_name = f"{model_cfg['type']}_{feature_set_name}_{tag}"

    if open_set_enabled and len(unknown_df) > 0:
        wrapper = OpenSetWrapper(model, config["open_set"]["confidence_threshold"])
        X_unknown, _ = preprocessor.transform(unknown_df)
        X_combined = np.vstack([X_test, X_unknown])
        is_true_unknown = np.concatenate([np.zeros(len(X_test), dtype=bool), np.ones(len(X_unknown), dtype=bool)])
        osp = wrapper.predict(X_combined)
        result.update(unknown_detection_rate(is_true_unknown, osp.is_unknown))

    if save_artifacts:
        # Grouped by model type (models_saved/xgboost/, models_saved/random_forest/, ...)
        # so every artifact for a given model — all feature sets, closed/open-set,
        # preprocessors — lives together instead of a flat, hard-to-scan directory.
        model_dir = resolve_path(config["paths"]["models_dir"]) / model_cfg["type"]
        model_dir.mkdir(parents=True, exist_ok=True)
        model.save(str(model_dir / f"{model_name}.pkl"))
        joblib.dump(preprocessor, model_dir / f"preprocessor_{feature_set_name}.pkl")

    logger.info(f"[{model_name}] metrics: {metrics}")
    return result


def main() -> None:
    config = load_config()
    feature_sets = load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    train_df, test_df, unknown_df = load_split_data(config)

    feature_set_name = config["feature_selection"]["active_set"]
    predictions_out = {}
    result = train_and_evaluate(
        config, feature_sets,
        feature_set_name=feature_set_name,
        open_set_enabled=config["open_set"]["enabled"],
        train_df=train_df, test_df=test_df, unknown_df=unknown_df,
        predictions_out=predictions_out,
    )
    logger.info(f"Training complete: {result}")

    results_dir = resolve_path(config["paths"]["results_dir"])
    plots_dir = results_dir / "plots" / config["model"]["type"]
    plot_confusion_matrix_grouped(predictions_out["y_test"], predictions_out["y_pred"],
                                   predictions_out["class_names"], plots_dir / f"confusion_matrix_{feature_set_name}.png")
    plot_roc_curve(predictions_out["y_test"], predictions_out["y_proba"],
                    predictions_out["class_names"], plots_dir / f"roc_curve_{feature_set_name}.png")

    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = build_overlap_diagnostics(predictions_out["fine_grained_true"], predictions_out["y_pred_labels"],
                                             config["data"]["label_merge_groups"])
    for group_name, table in diagnostics.items():
        out_csv = metrics_dir / f"overlap_diagnostic_{feature_set_name}.csv"
        table.to_csv(out_csv)
        logger.info(f"Saved {group_name} overlap diagnostic to {out_csv}:\n{table}")


if __name__ == "__main__":
    main()
