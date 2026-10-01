"""Evaluate a previously trained model from models_saved/ against a fresh test split.
Run from the project root:

    python pipelines/evaluate_pipeline.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd

from pipelines.train_pipeline import evaluate_model, load_split_data
from src.models.model_factory import create_scheme_model
from src.utils.config_loader import (
    get_dashboard_paths, get_label_scheme, get_metrics_dir, load_config, resolve_path, tagged,
)
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)


def evaluate(config: dict, model_path: Path, preprocessor_path: Path, test_df: pd.DataFrame) -> dict:
    # joblib.load executes arbitrary code on untrusted input; only ever load
    # artifacts this project trained and wrote to models_saved/ itself.
    preprocessor = joblib.load(preprocessor_path)
    normal_index = list(preprocessor.target_encoder.classes_).index(config["data"]["normal_category"])
    model = create_scheme_model(config["model"]["type"], config["model"]["params"], get_label_scheme(config)[2], normal_index)
    model.load(str(model_path))

    # Same evaluation as the experiment grid, so a saved model gets the same numbers as its grid row.
    metrics, _ = evaluate_model(model, preprocessor, test_df, config)
    logger.info(f"Evaluation of {model_path.name}: {metrics}")
    return metrics


def main() -> None:
    config = load_config()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    test_df = load_split_data(config).test

    model_path, preprocessor_path = get_dashboard_paths(config)
    artifact = model_path.with_suffix("") if get_label_scheme(config)[2] else model_path  # hierarchical: a directory
    if not artifact.exists() or not preprocessor_path.exists():
        raise FileNotFoundError(
            f"Model/preprocessor not found at {model_path} / {preprocessor_path}. "
            f"Run pipelines/train_pipeline.py or pipelines/run_all_experiments.py first."
        )

    metrics = evaluate(config, model_path, preprocessor_path, test_df)
    out_name = tagged(config, "evaluation_results.csv")

    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(metrics_dir / out_name, index=False)
    logger.info(f"Saved evaluation results to {metrics_dir / out_name}")


if __name__ == "__main__":
    main()
