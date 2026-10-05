"""Loads the configured model + preprocessor once, and turns an uploaded flow CSV
into predictions + SHAP explanations + human-readable narratives."""
from __future__ import annotations

import json
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from src.models.model_factory import create_scheme_model
from src.models.open_set_wrapper import OpenSetWrapper
from src.utils.config_loader import get_dashboard_paths, get_label_scheme, load_config, scheme_tag
from src.fpr_methods import apply_temperature
from src.utils.logger import get_logger
from src.xai.class_reference import ClassReference
from src.xai.narrative_generator import NarrativeGenerator, standardised_value_statistics
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)


class PredictionService:
    """Loads the best/configured model (config.yaml `dashboard.*`) and serves
    predictions + explanations for uploaded flow records."""

    def __init__(self, config: dict | None = None):
        self.config = config or load_config()
        self.feature_set_name = self.config["dashboard"]["feature_set"]

        model_path, preprocessor_path = get_dashboard_paths(self.config)
        hierarchical = get_label_scheme(self.config)[2]
        # A hierarchical model is saved as a directory (the model path without its suffix).
        artifact = model_path.with_suffix("") if hierarchical else model_path
        if not preprocessor_path.exists() or not artifact.exists():
            raise FileNotFoundError(
                f"Dashboard model/preprocessor not found ({model_path}, {preprocessor_path}). "
                f"Run `python pipelines/run_all_experiments.py` (or train_pipeline.py) first."
            )

        # joblib.load executes arbitrary code on untrusted input; only ever load
        # artifacts this project trained and wrote to models_saved/ itself.
        self.preprocessor = joblib.load(preprocessor_path)
        normal_index = list(self.preprocessor.target_encoder.classes_).index(self.config["data"]["normal_category"])
        self.model = create_scheme_model(self.config["model"]["type"], self.config["model"]["params"],
                                         hierarchical, normal_index)
        self.model.load(str(model_path))
        # The exact features the model was trained on (not a re-derived list that could drift).
        self.features = self.preprocessor.feature_list

        self.open_set_enabled = self.config["open_set"]["enabled"]
        # Use the threshold chosen on validation data at training time; the config value
        # is only a fallback for models trained before thresholds were saved.
        threshold_path = model_path.parent / f"open_set_{self.feature_set_name}{scheme_tag(self.config)}.json"
        threshold = (json.loads(threshold_path.read_text())["confidence_threshold"] if threshold_path.exists()
                     else self.config["open_set"]["confidence_threshold"])
        self.wrapper = OpenSetWrapper(self.model, threshold) if self.open_set_enabled else None

        self.explainer = SHAPExplainer(self.model, self.features, background_samples=self.config["xai"]["shap_background_samples"])
        # narrative.style: "classic" (default) or "class_relative" (Task 5.5: needs class_reference_<set>.npz and calibration_<set>.json saved with the model)
        self.narrative_style = self.config["narrative"].get("style", "classic")
        reference, self.temperature = None, None
        if self.narrative_style == "class_relative":
            suffix = f"{self.feature_set_name}{scheme_tag(self.config)}"
            reference_path, calibration_path = model_path.parent / f"class_reference_{suffix}.npz", model_path.parent / f"calibration_{suffix}.json"
            if not reference_path.exists() or not calibration_path.exists():
                raise FileNotFoundError(f"narrative.style is class_relative but {reference_path.name} / {calibration_path.name} are missing next to the model; retrain to create them.")
            reference = ClassReference.load(reference_path)
            self.temperature = float(json.loads(calibration_path.read_text())["temperature"])
        self.narrative_gen = NarrativeGenerator(self.config["narrative"]["suggested_actions"], self.narrative_style, reference)

        # Preprocessor.transform already standardises numeric features, so the values the
        # narrative sees ARE z-scores: mean 0 / std 1. (Passing the raw training mean/std
        # here would z-score twice.)
        self.feature_means, self.feature_stds = standardised_value_statistics(self.preprocessor.numeric_features)
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
        calibrated = apply_temperature(proba, self.temperature)[np.arange(len(X)), pred_idx] if self.temperature is not None else None

        is_unknown = np.zeros(len(X), dtype=bool)
        if self.wrapper is not None:
            is_unknown = self.wrapper.predict(X).is_unknown

        shap_matrix = self.explainer.local_explanations(X, pred_idx)  # one batched call

        results = []
        for i in range(len(X)):
            shap_row = shap_matrix.iloc[i]
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
                calibrated_confidence=float(calibrated[i]) if calibrated is not None else None,
            )
            top_shap = SHAPExplainer.top_k(shap_row, k=top_k)

            result = {
                "flow_id": i,
                "prediction": label,
                "confidence": round(float(confidence[i]), 4),
                "is_unknown": bool(is_unknown[i]),
                "narrative": narrative,
                "shap_top_features": [{"feature": f, "value": round(float(v), 4)} for f, v in top_shap.items()],
            }
            if calibrated is not None:
                result["calibrated_confidence"] = round(float(calibrated[i]), 4)
            results.append(result)
        return results


@lru_cache(maxsize=1)
def get_prediction_service() -> PredictionService:
    """Singleton accessor so the model is loaded once per process, not per request."""
    return PredictionService()
