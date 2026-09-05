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

from pipelines.train_pipeline import load_split_data
from src.evaluation.metrics import compute_metrics
from src.models.model_factory import create_model
from src.utils.config_loader import get_dashboard_paths, load_config, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)


def evaluate(config: dict, model_path: Path, preprocessor_path: Path, test_df: pd.DataFrame) -> dict:
    # joblib.load executes arbitrary code on untrusted input; only ever load
    # artifacts this project trained and wrote to models_saved/ itself.
    preprocessor = joblib.load(preprocessor_path)
    model = create_model(config["model"]["type"], config["model"]["params"])
    model.load(str(model_path))

    X_test, y_test = preprocessor.transform(test_df)
    y_pred = model.predict(X_test)
    metrics = compute_metrics(y_test, y_pred)
    logger.info(f"Evaluation of {model_path.name}: {metrics}")
    return metrics


def main() -> None:
    config = load_config()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    _, test_df, _ = load_split_data(config)

    model_path, preprocessor_path = get_dashboard_paths(config)
    if not model_path.exists() or not preprocessor_path.exists():
        raise FileNotFoundError(
            f"Model/preprocessor not found at {model_path} / {preprocessor_path}. "
            f"Run pipelines/train_pipeline.py or pipelines/run_all_experiments.py first."
        )

    metrics = evaluate(config, model_path, preprocessor_path, test_df)

    results_dir = resolve_path(config["paths"]["results_dir"])
    results_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(results_dir / "evaluation_results.csv", index=False)
    logger.info(f"Saved evaluation results to {results_dir / 'evaluation_results.csv'}")


if __name__ == "__main__":
    main()
