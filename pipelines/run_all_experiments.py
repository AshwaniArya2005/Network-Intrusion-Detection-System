"""Run the full experiment suite in one command:

    python pipelines/run_all_experiments.py

- Trains XGBoost (or whatever model.type is configured) on all 4 feature sets
  (49/30/20/15), each in closed-set and open-set mode -> 8 models saved to
  models_saved/<model.type>/, metrics collected into
  results/metrics/<model.type>/experiment_results.csv.
- Computes SHAP global importance per feature-set model and runs the
  explanation-stability study -> results/metrics/<model.type>/explanation_stability.csv.
- Runs the cross-dataset (UNSW <-> CICIDS2017) generalization study ->
  results/metrics/<model.type>/cross_dataset_results.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.train_pipeline import load_split_data, train_and_evaluate
from src.data_loader import load_cic, load_unsw
from src.evaluation.cross_dataset import run_cross_dataset_study
from src.evaluation.metrics import build_overlap_diagnostics
from src.evaluation.plots import generate_all_plots, plot_confusion_matrix_grouped, plot_roc_curve
from src.models.model_factory import create_model
from src.preprocessing import Preprocessor
from src.utils.config_loader import get_active_features, get_metrics_dir, load_config, load_feature_sets, resolve_path
from src.utils.logger import add_file_logging, get_logger
from src.xai.explanation_stability import run_stability_study
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)

# Common feature namespace shared by UNSW-NB15 and CICIDS2017 after src.data_loader's
# column remapping (see CIC_TO_COMMON) — used only by the cross-dataset study.
CROSS_DATASET_COMMON_FEATURES = [
    "dur", "spkts", "dpkts", "sbytes", "dbytes", "rate", "smean", "dmean",
    "total_bytes", "total_pkts", "byte_ratio", "pkt_ratio", "avg_pkt_size", "duration_log",
]


def run_experiment_grid(config: dict, feature_sets: dict) -> pd.DataFrame:
    train_df, test_df, unknown_df = load_split_data(config)
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = resolve_path(config["paths"]["results_dir"]) / "plots" / config["model"]["type"]
    rows = []
    for feature_set_name in config["experiments"]["feature_sets"]:
        for open_set_enabled in config["experiments"]["open_set_modes"]:
            logger.info(f"=== Training feature_set={feature_set_name} open_set={open_set_enabled} ===")
            # Closed/open-set share the same underlying classifier predictions (the
            # wrapper only relabels low-confidence rows), so only capture predictions
            # once per feature set — on the closed-set run — for the confusion
            # matrix / ROC curve, rather than duplicating them for both variants.
            predictions_out = {} if not open_set_enabled else None
            result = train_and_evaluate(
                config, feature_sets, feature_set_name, open_set_enabled,
                train_df, test_df, unknown_df, save_artifacts=True, predictions_out=predictions_out,
            )
            rows.append(result)

            if predictions_out:
                plot_confusion_matrix_grouped(predictions_out["y_test"], predictions_out["y_pred"],
                                               predictions_out["class_names"],
                                               plots_dir / f"confusion_matrix_{feature_set_name}.png")
                plot_roc_curve(predictions_out["y_test"], predictions_out["y_proba"],
                                predictions_out["class_names"],
                                plots_dir / f"roc_curve_{feature_set_name}.png")

                diagnostics = build_overlap_diagnostics(predictions_out["fine_grained_true"],
                                                         predictions_out["y_pred_labels"],
                                                         config["data"]["label_merge_groups"])
                for table in diagnostics.values():
                    table.to_csv(metrics_dir / f"overlap_diagnostic_{feature_set_name}.csv")

    results_df = pd.DataFrame(rows)
    out_path = metrics_dir / config["experiments"]["output_csv"]
    results_df.to_csv(out_path, index=False)
    logger.info(f"Saved experiment grid results ({len(results_df)} rows) to {out_path}")
    return results_df


def run_explanation_stability(config: dict, feature_sets: dict) -> pd.DataFrame:
    """Train one closed-set model per feature-set size and compare their SHAP
    global-importance rankings pairwise (novelty #3)."""
    train_df, test_df, _ = load_split_data(config)
    model_cfg = config["model"]
    importances = {}

    for feature_set_name in config["experiments"]["feature_sets"]:
        features = get_active_features(config, feature_sets, feature_set_name)
        preprocessor = Preprocessor(feature_list=features, target_column=config["data"]["target_column"]).fit(train_df)
        X_train, y_train = preprocessor.transform(train_df)

        model = create_model(model_cfg["type"], model_cfg["params"])
        model.fit(X_train, y_train)

        explainer = SHAPExplainer(model, features, background_samples=config["xai"]["shap_background_samples"])
        importances[f"{model_cfg['type']}_{feature_set_name}"] = explainer.global_importance(X_train)

    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    stability_df = run_stability_study(importances, output_csv=str(metrics_dir / config["experiments"]["stability_csv"]))
    logger.info(f"Explanation stability study complete:\n{stability_df}")
    return stability_df


def run_cross_dataset(config: dict) -> pd.DataFrame:
    unsw_df = load_unsw(
        resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]),
        seed=config["project"]["seed"], synthetic_rows=config["data"]["synthetic_fallback_rows"],
    )
    cic_df = load_cic(
        resolve_path(config["paths"]["cic_file"]),
        seed=config["project"]["seed"], synthetic_rows=config["data"]["synthetic_fallback_rows"],
    )
    cross_df = run_cross_dataset_study(
        unsw_df, cic_df, CROSS_DATASET_COMMON_FEATURES,
        config["model"]["type"], config["model"]["params"],
    )
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    out_path = metrics_dir / config["experiments"]["cross_dataset_csv"]
    cross_df.to_csv(out_path, index=False)
    logger.info(f"Saved cross-dataset results to {out_path}")
    return cross_df


def main() -> None:
    config = load_config()
    feature_sets = load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))

    logger.info("Step 1/3: training 8-model experiment grid (4 feature sets x closed/open-set)")
    experiment_df = run_experiment_grid(config, feature_sets)

    logger.info("Step 2/3: explanation stability study")
    stability_df = run_explanation_stability(config, feature_sets)

    logger.info("Step 3/3: cross-dataset generalization study")
    cross_dataset_df = run_cross_dataset(config)

    plots_dir = generate_all_plots(
        config["model"]["type"], resolve_path(config["paths"]["results_dir"]),
        experiment_df=experiment_df, stability_df=stability_df, cross_dataset_df=cross_dataset_df,
    )

    logger.info(f"All experiments complete. See {get_metrics_dir(config)} for CSV outputs, "
                f"{plots_dir} for charts, and models_saved/ for artifacts.")


if __name__ == "__main__":
    main()
