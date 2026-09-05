"""Human-Centered Actionable Explanations (novelty #2).

Turns SHAP values + a prediction into an analyst-readable narrative: which
features drove the decision, described in plain language with a magnitude cue
(e.g. "extremely high"), plus a suggested remediation action per attack type.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Plain-English descriptions for the raw/engineered feature names. Falls back to
# the raw column name (with underscores replaced) if a feature isn't listed.
FEATURE_DESCRIPTIONS = {
    "dur": "flow duration",
    "sbytes": "bytes sent by the source",
    "dbytes": "bytes sent by the destination",
    "sttl": "source time-to-live",
    "dttl": "destination time-to-live",
    "rate": "packet rate",
    "spkts": "number of packets sent by the source",
    "dpkts": "number of packets sent by the destination",
    "sload": "source data load",
    "dload": "destination data load",
    "smean": "mean packet size from source",
    "dmean": "mean packet size from destination",
    "tcprtt": "TCP round-trip time",
    "synack": "SYN-ACK handshake time",
    "ackdat": "ACK data time",
    "sjit": "source jitter",
    "djit": "destination jitter",
    "ct_srv_src": "connections to the same service from this source",
    "ct_srv_dst": "connections to the same service and destination",
    "ct_state_ttl": "connections with the same state and TTL",
    "total_bytes": "total bytes transferred",
    "total_pkts": "total packets transferred",
    "byte_ratio": "source-to-destination byte ratio",
    "pkt_ratio": "source-to-destination packet ratio",
    "avg_pkt_size": "average packet size",
    "duration_log": "log-scaled flow duration",
    "ttl_diff": "TTL difference between source and destination",
    "proto": "network protocol",
    "service": "network service",
    "state": "connection state",
}


def _describe_feature(name: str) -> str:
    return FEATURE_DESCRIPTIONS.get(name, name.replace("_", " "))


def _magnitude_phrase(z_score: float) -> str:
    """Translate a z-score (feature value vs. training mean/std) into a plain-English
    magnitude cue used in the narrative sentence."""
    if z_score >= 2.5:
        return "extremely high"
    if z_score >= 1.0:
        return "unusually high"
    if z_score >= 0.3:
        return "elevated"
    if z_score <= -2.5:
        return "extremely low"
    if z_score <= -1.0:
        return "unusually low"
    if z_score <= -0.3:
        return "reduced"
    return "typical"


class NarrativeGenerator:
    """Generates human-readable, actionable explanations from SHAP output."""

    def __init__(self, suggested_actions: dict[str, str] | None = None):
        self.suggested_actions = suggested_actions or {}

    def _categorical_phrase(self, feat: str, desc: str, feature_values: pd.Series | None,
                             category_decoders: dict[str, object] | None) -> str:
        """Categorical features (proto/service/state) are label-encoded integers, not
        magnitudes — "extremely high protocol" is meaningless. Name the actual category
        instead, decoding back from the encoder if one was provided."""
        if feature_values is None or feat not in feature_values.index:
            return f"notable {desc}"
        raw_value = feature_values[feat]
        decoded = None
        if category_decoders and feat in category_decoders:
            try:
                decoded = category_decoders[feat].inverse_transform([int(round(raw_value))])[0]
            except Exception:
                decoded = None
        value_str = decoded if decoded is not None else str(raw_value)
        return f"{desc}={value_str}"

    def _reason_phrases(self, shap_row: pd.Series, feature_values: pd.Series | None,
                         feature_means: pd.Series | None, feature_stds: pd.Series | None,
                         categorical_features: frozenset[str], category_decoders: dict[str, object] | None,
                         top_k: int) -> list[str]:
        top_features = shap_row.reindex(shap_row.abs().sort_values(ascending=False).index[:top_k])
        phrases = []
        for feat, contribution in top_features.items():
            if contribution <= 0:
                continue  # only cite features that pushed toward this prediction
            desc = _describe_feature(feat)
            if feat in categorical_features:
                phrases.append(self._categorical_phrase(feat, desc, feature_values, category_decoders))
            elif feature_values is not None and feature_means is not None and feature_stds is not None and feat in feature_values.index:
                std = feature_stds.get(feat, 0.0) or 1e-9
                z = (feature_values[feat] - feature_means.get(feat, 0.0)) / std
                phrases.append(f"{_magnitude_phrase(z)} {desc}")
            else:
                phrases.append(f"notable {desc}")
        return phrases

    def generate(
        self,
        predicted_label: str,
        confidence: float,
        shap_row: pd.Series,
        feature_values: pd.Series | None = None,
        feature_means: pd.Series | None = None,
        feature_stds: pd.Series | None = None,
        categorical_features: frozenset[str] | set[str] = frozenset(),
        category_decoders: dict[str, object] | None = None,
        top_k: int = 3,
        is_unknown: bool = False,
    ) -> str:
        """Build a narrative string like:
        "This flow was flagged as DoS with 97.8% confidence. Main reasons: extremely
        high packet rate, unusually high number of packets sent by the source.
        Suggested action: Consider rate-limiting this source IP."

        `categorical_features` names which features are label-encoded (e.g. proto/
        service/state) rather than continuous — those get named by category
        ("protocol=tcp") instead of a magnitude cue, which is meaningless for a
        categorical value. `category_decoders` (feature name -> fitted LabelEncoder,
        e.g. Preprocessor.label_encoders) decodes the integer back to the original
        string; without it, the raw encoded value is shown instead.
        """
        label_for_sentence = "an unrecognized (potential zero-day) pattern" if is_unknown else predicted_label
        reasons = self._reason_phrases(shap_row, feature_values, feature_means, feature_stds,
                                        frozenset(categorical_features), category_decoders, top_k)

        sentence = f"This flow was flagged as {label_for_sentence} with {confidence * 100:.1f}% confidence."
        if reasons:
            sentence += " Main reasons: " + ", ".join(reasons) + "."
        else:
            sentence += " No single feature dominated the decision; the pattern was diffuse across many features."

        action_key = "Unknown" if is_unknown else predicted_label
        action = self.suggested_actions.get(action_key)
        if action:
            sentence += f" Suggested action: {action}"

        return sentence

    def generate_batch(
        self,
        predicted_labels: list[str],
        confidences: np.ndarray,
        shap_matrix: pd.DataFrame,
        feature_values_df: pd.DataFrame | None = None,
        feature_means: pd.Series | None = None,
        feature_stds: pd.Series | None = None,
        categorical_features: frozenset[str] | set[str] = frozenset(),
        category_decoders: dict[str, object] | None = None,
        unknown_mask: np.ndarray | None = None,
        top_k: int = 3,
    ) -> list[str]:
        """Vectorized convenience wrapper over generate() for a batch of predictions."""
        narratives = []
        for i, label in enumerate(predicted_labels):
            fv = feature_values_df.iloc[i] if feature_values_df is not None else None
            is_unknown = bool(unknown_mask[i]) if unknown_mask is not None else False
            narratives.append(self.generate(
                predicted_label=label,
                confidence=float(confidences[i]),
                shap_row=shap_matrix.iloc[i],
                feature_values=fv,
                feature_means=feature_means,
                feature_stds=feature_stds,
                categorical_features=categorical_features,
                category_decoders=category_decoders,
                top_k=top_k,
                is_unknown=is_unknown,
            ))
        return narratives
