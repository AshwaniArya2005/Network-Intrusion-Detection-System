"""Automatic audit of generated narratives (Task 5; protocol: results/task_5_protocol.md).

A narrative reads "This flow was flagged as <label> with <p>% confidence. Main reasons: <cue> <feature>, ... Suggested action: <text>". `parse_narrative` takes it apart again and the
`check_*` functions compare each claim with an independent computation (SHAP from a separate explainer, z-scores from the raw training frame, the configured actions).
"""
from __future__ import annotations

import re

from src.xai.narrative_generator import FEATURE_DESCRIPTIONS, _magnitude_phrase

CUES = ["extremely high", "unusually high", "elevated", "extremely low", "unusually low", "reduced", "typical", "notable"]
HIGH, LOW = {"extremely high", "unusually high", "elevated"}, {"extremely low", "unusually low", "reduced"}
Z_BOUNDARIES = (-2.5, -1.0, -0.3, 0.3, 1.0, 2.5)
UNRECOGNIZED = "an unrecognized (potential zero-day) pattern"
CLASS_NAMES = ("Normal", "Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic", "Reconnaissance", "Worms", "Shellcode", "Overlap-Group-1", "Overlap-Group-2")


def description_of(feature: str) -> str:
    return FEATURE_DESCRIPTIONS.get(feature, feature.replace("_", " "))


def parse_narrative(text: str, features: list[str]) -> dict:
    """{"label": the text after "flagged as" (up to " with"), "confidence_pct": float, "reasons": [(feature, cue or None, category value or None)], "action": text or None, "diffuse": bool}.
    A reason is matched to the feature with the LONGEST description that ends the phrase (categorical reasons read "<description>=<value>")."""
    m = re.match(r"This flow was flagged as (?P<label>.+?) with (?P<pct>[0-9.]+)% confidence\.", text)
    out = {"label": m.group("label") if m else None, "confidence_pct": float(m.group("pct")) if m else None, "reasons": [], "action": None,
           "diffuse": "No single feature dominated" in text}
    if " Suggested action: " in text:
        out["action"] = text.split(" Suggested action: ", 1)[1]
        text = text.split(" Suggested action: ", 1)[0]
    if " Main reasons: " in text:
        body = text.split(" Main reasons: ", 1)[1].rstrip(".")
        by_length = sorted(features, key=lambda f: -len(description_of(f)))
        for phrase in body.split(", "):
            feature, cue, category = None, None, None
            for f in by_length:
                d = description_of(f)
                if phrase.endswith(d):
                    feature, prefix = f, phrase[: -len(d)].strip()
                    cue = prefix if prefix in CUES else (None if not prefix else prefix)
                    break
                if phrase.startswith(d + "="):
                    feature, category = f, phrase[len(d) + 1:]
                    break
            out["reasons"].append((feature, cue, category))
    return out


def cue_direction(cue: str | None) -> str:
    """high / low / typical for a magnitude cue; none for `notable` or no cue."""
    if cue in HIGH:
        return "high"
    if cue in LOW:
        return "low"
    return "typical" if cue == "typical" else "none"


def check_cited_in_top(cited: list[str], shap_row, k: int) -> bool:
    """(a) every cited feature is among the positive-SHAP features of the top `k` by absolute SHAP value of the predicted class."""
    top = shap_row.reindex(shap_row.abs().sort_values(ascending=False).index[:k])
    allowed = set(top[top > 0].index)
    return all(f in allowed for f in cited)


def check_cue(cue: str | None, z: float, tol: float = 1e-6) -> dict:
    """(b) the cue against the z-score of the flow's value relative to the TRAINING mean / std. `exact`: the cue is the one `_magnitude_phrase(z)` gives (a z within `tol` of a boundary
    accepts either neighbouring cue); `direction`: high / low / typical agree."""
    accepted = {_magnitude_phrase(z), _magnitude_phrase(z - tol), _magnitude_phrase(z + tol)}
    return {"exact": cue in accepted, "direction": cue_direction(cue) in {cue_direction(a) for a in accepted}, "expected": _magnitude_phrase(z)}


def check_categorical(feature: str, cue: str | None, category: str | None, raw_value: str, seen_in_training: bool) -> tuple[bool, str]:
    """(c) a categorical feature is named by the flow's actual category and carries no magnitude cue. Returns (ok, reason)."""
    if cue is not None:
        return False, f"{feature}: magnitude cue {cue!r} on a categorical feature"
    if category is None:
        return False, f"{feature}: no category named"
    if not seen_in_training:
        return False, f"{feature}: category {raw_value!r} was never seen in training and is shown as {category!r}"
    return (category == str(raw_value)), (f"{feature}: names {category!r} but the flow has {raw_value!r}" if category != str(raw_value) else "")


def check_action(action: str | None, label: str, actions: dict[str, str]) -> bool:
    """(d) the suggested action equals the configured action of the label ("Unknown" when the flow is flagged); a label without a configured action has no action text."""
    expected = actions.get(label)
    return (action is None) if not expected else (action == str(expected).strip() or action == expected)


def check_label_statement(parsed: dict, predicted_label: str, is_unknown: bool, text: str) -> tuple[bool, str]:
    """(e) the narrative says nothing false about the label: the first sentence names the predicted label (the unrecognized-pattern wording exactly when the flow is flagged Unknown)
    and no other class name. Class names inside the configured action text are not part of this check (check (d) compares that text)."""
    first = text.split(" Main reasons:")[0].split(" No single feature")[0].split(" Suggested action:")[0]
    expected = UNRECOGNIZED if is_unknown else predicted_label
    if parsed["label"] != expected:
        return False, f"names {parsed['label']!r} but the prediction is {expected!r}"
    others = [c for c in CLASS_NAMES if c != predicted_label and re.search(rf"(?<![\w-]){re.escape(c)}(?![\w-])", first)]
    if is_unknown:
        others = [c for c in CLASS_NAMES if re.search(rf"(?<![\w-]){re.escape(c)}(?![\w-])", first)]
    return (not others), (f"mentions {others}" if others else "")


def directional_consistency(cue: str | None, rho: float, min_abs: float = 0.10) -> str:
    """(f) consistent / inconsistent / "no monotone relation" (|rho| below `min_abs`) / "no direction claimed" (a typical or no cue). `rho` is the Spearman correlation between the
    feature value and its SHAP value for the predicted class on training rows: a high cue should come with a positive rho, a low cue with a negative one."""
    direction = cue_direction(cue)
    if direction in ("none", "typical"):
        return "no direction claimed"
    if abs(rho) < min_abs:
        return "no monotone relation"
    return "consistent" if (direction == "high") == (rho > 0) else "inconsistent"
