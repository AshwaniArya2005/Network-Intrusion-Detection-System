"""Open-set / zero-day detection layer (novelty #1).

Wraps any BaseModel: if the model's max class probability falls below a
confidence threshold, the prediction is relabeled "Unknown" instead of forced
into one of the known training classes. This lets the system flag genuinely
novel (zero-day) attack traffic instead of confidently mislabeling it.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.models.base_model import BaseModel
from src.utils.logger import get_logger

logger = get_logger(__name__)


def select_threshold(known_val_confidence: np.ndarray, target_false_unknown_rate: float) -> float:
    """Confidence threshold that flags at most `target_false_unknown_rate` of KNOWN
    validation flows as Unknown. Uses known data only — the reported zero-day
    classes must never influence this choice."""
    return float(np.quantile(known_val_confidence, target_false_unknown_rate))


@dataclass
class OpenSetPrediction:
    closed_set_label: np.ndarray    # original argmax prediction (encoded class index)
    open_set_label: np.ndarray      # closed_set_label, or -1 where flagged "Unknown"
    confidence: np.ndarray          # max class probability per sample
    is_unknown: np.ndarray          # boolean mask


class OpenSetWrapper:
    """Confidence-threshold open-set wrapper around any BaseModel."""

    UNKNOWN_INDEX = -1

    def __init__(self, model: BaseModel, confidence_threshold: float = 0.6):
        self.model = model
        self.confidence_threshold = confidence_threshold

    def fit(self, X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray | None = None) -> "OpenSetWrapper":
        self.model.fit(X, y, sample_weight=sample_weight)
        return self

    def predict(self, X: np.ndarray) -> OpenSetPrediction:
        """Return both the original (closed-set) prediction and the open-set prediction."""
        proba = self.model.predict_proba(X)
        closed_set_label = np.argmax(proba, axis=1)
        confidence = np.max(proba, axis=1)
        is_unknown = confidence < self.confidence_threshold

        open_set_label = closed_set_label.copy()
        open_set_label[is_unknown] = self.UNKNOWN_INDEX

        logger.info(f"Open-set prediction: {is_unknown.sum()}/{len(X)} flagged Unknown "
                    f"(threshold={self.confidence_threshold})")
        return OpenSetPrediction(
            closed_set_label=closed_set_label,
            open_set_label=open_set_label,
            confidence=confidence,
            is_unknown=is_unknown,
        )
