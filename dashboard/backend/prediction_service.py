"""Loads the configured model + preprocessor once, and turns an uploaded flow CSV
into predictions + SHAP explanations + human-readable narratives."""
from __future__ import annotations

from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from src.models.model_factory import create_model
from src.models.open_set_wrapper import OpenSetWrapper
from src.utils.config_loader import get_active_features, get_dashboard_paths, load_config, load_feature_sets
from src.utils.logger import get_logger
from src.xai.narrative_generator import NarrativeGenerator
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)


class PredictionService:
    """Loads the best/configured model (config.yaml `dashboard.*`) and serves
    predictions + explanations for uploaded flow records."""

    def __init__(self, config: dict | None = None):
        self.config = config or load_config()
        feature_sets = load_feature_sets()
        self.feature_set_name = self.config["dashboard"]["feature_set"]
        self.features = get_active_features(self.config, feature_sets, self.feature_set_name)

        model_path, preprocessor_path = get_dashboard_paths(self.config)
        if not preprocessor_path.exists() or not model_path.exists():
            raise FileNotFoundError(
                f"Dashboard model/preprocessor not found ({model_path}, {preprocessor_path}). "
                f"Run `python pipelines/run_all_experiments.py` (or train_pipeline.py) first."
            )

        # joblib.load executes arbitrary code on untrusted input; only ever load
        # artifacts this project trained and wrote to models_saved/ itself.
        self.preprocessor = joblib.load(preprocessor_path)
        self.model = create_model(self.config["model"]["type"], self.config["model"]["params"])
        self.model.load(str(model_path))

        self.open_set_enabled = self.config["open_set"]["enabled"]
        self.wrapper = OpenSetWrapper(self.model, self.config["open_set"]["confidence_threshold"]) if self.open_set_enabled else None

        self.explainer = SHAPExplainer(self.model, self.features, background_samples=self.config["xai"]["shap_background_samples"])
        self.narrative_gen = NarrativeGenerator(self.config["narrative"]["suggested_actions"])

        numeric_features = self.preprocessor.numeric_features
        self.feature_means = pd.Series(self.preprocessor.scaler.mean_, index=numeric_features)
        self.feature_stds = pd.Series(self.preprocessor.scaler.scale_, index=numeric_features)
        logger.info(f"PredictionService ready: model={self.config['model']['type']} "
                    f"feature_set={self.feature_set_name} open_set={self.open_set_enabled}")

    def predict(self, df: pd.DataFrame, top_k: int | None = None) -> list[dict]:
        """Run predictions + SHAP explanations + narratives for every row in df."""
        top_k = top_k or self.config["xai"]["top_k_features"]
        X, _ = self.preprocessor.transform(df)
        proba = self.model.predict_proba(X)
        pred_idx = np.argmax(proba, axis=1)
        confidence = np.max(proba, axis=1)
        pred_labels = self.preprocessor.decode_target(pred_idx)

        is_unknown = np.zeros(len(X), dtype=bool)
        if self.wrapper is not None:
            is_unknown = self.wrapper.predict(X).is_unknown

        results = []
        for i in range(len(X)):
            shap_row = self.explainer.local_explanation(X[i:i + 1], int(pred_idx[i]))
            feature_values = pd.Series(X[i], index=self.features)
            label = "Unknown" if is_unknown[i] else str(pred_labels[i])

            narrative = self.narrative_gen.generate(
                predicted_label=str(pred_labels[i]),
                confidence=float(confidence[i]),
                shap_row=shap_row,
                feature_values=feature_values,
                feature_means=self.feature_means,
                feature_stds=self.feature_stds,
                categorical_features=frozenset(self.preprocessor.categorical_features),
                category_decoders=self.preprocessor.label_encoders,
                top_k=top_k,
                is_unknown=bool(is_unknown[i]),
            )
            top_shap = SHAPExplainer.top_k(shap_row, k=top_k)

            results.append({
                "flow_id": i,
                "prediction": label,
                "confidence": round(float(confidence[i]), 4),
                "is_unknown": bool(is_unknown[i]),
                "narrative": narrative,
                "shap_top_features": [{"feature": f, "value": round(float(v), 4)} for f, v in top_shap.items()],
            })
        return results


@lru_cache(maxsize=1)
def get_prediction_service() -> PredictionService:
    """Singleton accessor so the model is loaded once per process, not per request."""
    return PredictionService()
