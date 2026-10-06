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
    "ct_src_ltm": "recent connections from this source",
    "ct_dst_ltm": "recent connections to this destination",
    "ct_dst_src_ltm": "recent connections between this source and destination",
    "ct_src_dport_ltm": "recent connections from this source to the same destination port",
    "ct_dst_sport_ltm": "recent connections to this destination from the same source port",
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


def standardised_value_statistics(numeric_features: list[str]) -> tuple[pd.Series, pd.Series]:
    """(means, stds) to pass to `NarrativeGenerator` together with feature values taken from `Preprocessor.transform`: those values are ALREADY standardised (training mean 0, std 1), so
    they are the z-scores. Passing the scaler's raw mean / scale here would standardise a second time and make most flows read "typical" (the dashboard and scripts/check_explainability.py
    both had this defect)."""
    return pd.Series(0.0, index=numeric_features), pd.Series(1.0, index=numeric_features)


HIGH_CUES = ("elevated", "unusually high", "extremely high")
CALIBRATION_NOTE = "(the model's raw probability tends to be too high on new traffic; treat both numbers as estimates, not guarantees)"


class NarrativeGenerator:
    """Generates human-readable, actionable explanations from SHAP output.

    `style="classic"` (default): every cited feature gets a magnitude cue against the overall training mean / std, "typical" included.
    `style="class_relative"` (Task 5.5, protocol results/task_5_5_protocol.md): features whose cue would read "typical" are omitted and the others say where the value sits among
    ALL training flows and among the flows of the PREDICTED class, using a `ClassReference` (src/xai/class_reference.py); a calibrated confidence can be shown next to the raw one."""

    def __init__(self, suggested_actions: dict[str, str] | None = None, style: str = "classic", reference=None):
        if style not in ("classic", "class_relative"):
            raise ValueError(f"unknown narrative style {style!r} (classic or class_relative)")
        if style == "class_relative" and reference is None:
            raise ValueError("narrative style 'class_relative' needs a ClassReference (saved with the model as class_reference_<set>.npz)")
        self.suggested_actions = suggested_actions or {}
        self.style, self.reference = style, reference

    def _class_clause(self, feat: str, value: float, label: str) -> str:
        """`typical of <label> flows` inside the class's interquartile range, else how far above / below the class's flows the value lies."""
        q25, q75 = self.reference.quartiles(feat, label)
        if q25 <= value <= q75:
            return f"typical of {label} flows"
        if value > q75:
            return f"higher than {100 * self.reference.share_below(feat, value, label):.0f}% of {label} flows"
        return f"lower than {100 * self.reference.share_above(feat, value, label):.0f}% of {label} flows"

    def _class_relative_phrases(self, shap_row: pd.Series, feature_values: pd.Series | None, feature_means: pd.Series | None, feature_stds: pd.Series | None,
                                categorical_features: frozenset[str], category_decoders: dict[str, object] | None, top_k: int, label: str, is_unknown: bool) -> list[str]:
        top_features = shap_row.reindex(shap_row.abs().sort_values(ascending=False).index[:top_k])
        phrases = []
        for feat, contribution in top_features.items():
            if contribution <= 0:
                continue
            desc = _describe_feature(feat)
            if feat in categorical_features:
                base = self._categorical_phrase(feat, desc, feature_values, category_decoders)
                if feature_values is None or feat not in feature_values.index:
                    phrases.append(base)
                    continue
                code = int(round(feature_values[feat]))
                clause = f"seen in {100 * self.reference.category_share(feat, code):.0f}% of all flows"
                if not is_unknown:
                    clause += f"; seen in {100 * self.reference.category_share(feat, code, label):.0f}% of {label} flows"
                phrases.append(f"{base} ({clause})")
            elif feature_values is not None and feature_means is not None and feature_stds is not None and feat in feature_values.index:
                std = feature_stds.get(feat, 0.0) or 1e-9
                value = float(feature_values[feat])
                cue = _magnitude_phrase((value - feature_means.get(feat, 0.0)) / std)
                if cue == "typical":
                    continue                                                           # an uninformative feature is not cited
                if cue in HIGH_CUES:
                    clause = f"higher than {100 * self.reference.share_below(feat, value):.0f}% of all flows"
                else:
                    clause = f"lower than {100 * self.reference.share_above(feat, value):.0f}% of all flows"
                if not is_unknown:
                    clause += "; " + self._class_clause(feat, value, label)
                phrases.append(f"{cue} {desc} ({clause})")
            else:
                phrases.append(f"notable {desc}")
        return phrases

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
        calibrated_confidence: float | None = None,
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
        if self.style == "class_relative":
            reasons = self._class_relative_phrases(shap_row, feature_values, feature_means, feature_stds, frozenset(categorical_features), category_decoders, top_k,
                                                   predicted_label, is_unknown)
        else:
            reasons = self._reason_phrases(shap_row, feature_values, feature_means, feature_stds,
                                           frozenset(categorical_features), category_decoders, top_k)

        sentence = f"This flow was flagged as {label_for_sentence} with {confidence * 100:.1f}% confidence."
        if self.style == "class_relative" and calibrated_confidence is not None:
            sentence += f" Calibrated estimate: about {calibrated_confidence * 100:.0f}% {CALIBRATION_NOTE}."
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
