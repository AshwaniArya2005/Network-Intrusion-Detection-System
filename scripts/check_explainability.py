"""Sanity-check SHAP explanations + narratives on the real saved model against real
UNSW-NB15 test data (not synthetic fixtures). Run from the project root:

    python scripts/check_explainability.py

For each known class, prints one correctly-classified real example: its top SHAP
features, the generated narrative, and its true original attack category. Use this
after retraining or after changing anything in src/xai/ to eyeball whether the
explanations still make domain sense — pytest's tests/test_xai.py only checks that
the SHAP/narrative *code* behaves correctly on tiny synthetic data (shapes, string
formatting); it can't tell you whether an explanation is actually meaningful.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd

from pipelines.train_pipeline import load_split_data
from src.models.model_factory import create_model
from src.utils.config_loader import get_active_features, get_dashboard_paths, load_config, load_feature_sets
from src.utils.logger import get_logger
from src.xai.narrative_generator import NarrativeGenerator
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)


def main() -> None:
    config = load_config()
    feature_sets = load_feature_sets()
    train_df, test_df, unknown_df = load_split_data(config)

    feature_set_name = config["dashboard"]["feature_set"]
    features = get_active_features(config, feature_sets, feature_set_name)

    model_path, preprocessor_path = get_dashboard_paths(config)
    if not model_path.exists() or not preprocessor_path.exists():
        raise FileNotFoundError(
            f"No trained model at {model_path} / {preprocessor_path}. "
            f"Run pipelines/train_pipeline.py or pipelines/run_all_experiments.py first."
        )

    # This project's own previously-trained artifact (models_saved/) -- not an
    # untrusted source; joblib.load executes arbitrary code, so only ever point
    # this at files this project trained and saved itself.
    preprocessor = joblib.load(preprocessor_path)
    model = create_model(config["model"]["type"], config["model"]["params"])
    model.load(str(model_path))

    X_test, y_test = preprocessor.transform(test_df)
    y_pred = model.predict(X_test)
    proba = model.predict_proba(X_test)
    pred_labels = preprocessor.decode_target(y_pred)
    true_labels = preprocessor.decode_target(y_test)

    explainer = SHAPExplainer(model, features, background_samples=config["xai"]["shap_background_samples"])
    generator = NarrativeGenerator(config["narrative"]["suggested_actions"])
    feature_means = pd.Series(preprocessor.scaler.mean_, index=preprocessor.numeric_features)
    feature_stds = pd.Series(preprocessor.scaler.scale_, index=preprocessor.numeric_features)

    test_df = test_df.reset_index(drop=True)
    for cls in preprocessor.target_encoder.classes_:
        idx = np.where((true_labels == cls) & (pred_labels == cls))[0]
        if len(idx) == 0:
            logger.warning(f"No correctly-classified test rows for class '{cls}' — skipping.")
            continue
        i = idx[0]
        conf = proba[i, y_pred[i]]
        shap_row = explainer.local_explanation(X_test[i:i + 1], int(y_pred[i]))
        feature_values = pd.Series(X_test[i], index=features)
        narrative = generator.generate(
            pred_labels[i], conf, shap_row, feature_values, feature_means, feature_stds,
            categorical_features=frozenset(preprocessor.categorical_features),
            category_decoders=preprocessor.label_encoders,
            top_k=config["xai"]["top_k_features"],
        )
        top_features = SHAPExplainer.top_k(shap_row, k=config["xai"]["top_k_features"])

        print(f"\n=== {cls} (real test row {i}, confidence={conf:.3f}) ===")
        print(f"Original fine-grained attack_cat: {test_df.loc[i, 'attack_cat']}")
        print(f"Top SHAP features:\n{top_features.to_string()}")
        print(f"Narrative: {narrative}")


if __name__ == "__main__":
    main()
