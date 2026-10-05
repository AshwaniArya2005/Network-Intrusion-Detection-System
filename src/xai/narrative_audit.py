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
    cal = re.search(r"Calibrated estimate: about (\d+)%", text)
    out = {"label": m.group("label") if m else None, "confidence_pct": float(m.group("pct")) if m else None, "reasons": [], "clauses": [], "action": None,
           "calibrated_pct": float(cal.group(1)) if cal else None, "diffuse": "No single feature dominated" in text}
    if " Suggested action: " in text:
        out["action"] = text.split(" Suggested action: ", 1)[1]
        text = text.split(" Suggested action: ", 1)[0]
    if " Main reasons: " in text:
        body = text.split(" Main reasons: ", 1)[1].rstrip(".")
        by_length = sorted(features, key=lambda f: -len(description_of(f)))
        for phrase in body.split(", "):
            clause = None
            parenthetical = re.match(r"^(?P<main>.*?) \((?P<clause>[^()]*)\)$", phrase)
            if parenthetical:                                                      # the class-relative style adds "(<overall clause>; <class clause>)"
                phrase, clause = parenthetical.group("main"), parenthetical.group("clause")
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
            out["clauses"].append(clause)
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


def _strictly(values, v: float, direction: str) -> float:
    """100 x the share of `values` strictly smaller (direction "higher") or strictly larger ("lower") than v."""
    import numpy as np
    values = np.asarray(values, dtype=float)
    return 100.0 * float((values < v).mean() if direction == "higher" else (values > v).mean())


def check_numeric_clause(clause: str | None, cue: str | None, value: float, all_values, class_values, label: str, is_unknown: bool, tol_pct: float = 1.0) -> tuple[bool, bool, str]:
    """(g) for a numeric reason of the class-relative style: the overall clause ("higher / lower than P% of all flows") and the class clause ("typical of <label> flows" or "higher / lower than Q% of <label>
    flows") must equal an independent computation from the raw TRAINING values (`all_values`, `class_values`, the flow's raw `value`): the direction word agrees with the cue, P and Q within `tol_pct`
    percentage points, "typical" exactly when the value lies in the class's interquartile range (a value within 1e-9 of a quartile accepts either statement), and no class clause for a flagged-Unknown flow.
    Returns (ok, outside_class_iqr, reason)."""
    import numpy as np
    if clause is None:
        return False, False, "no clause"
    parts = clause.split("; ")
    m = re.fullmatch(r"(higher|lower) than (\d+)% of all flows", parts[0])
    if not m:
        return False, False, f"unreadable overall clause {parts[0]!r}"
    if m.group(1) != ("higher" if cue_direction(cue) == "high" else "lower"):
        return False, False, f"overall clause says {m.group(1)!r} but the cue is {cue!r}"
    expected = _strictly(all_values, value, m.group(1))
    if abs(expected - float(m.group(2))) > tol_pct + 0.5:
        return False, False, f"overall clause {m.group(2)}% but the training flows give {expected:.1f}%"
    if is_unknown:
        return (len(parts) == 1), False, ("" if len(parts) == 1 else "class clause on a flow flagged Unknown")
    if len(parts) != 2:
        return False, False, "no class clause"
    class_values = np.asarray(class_values, dtype=float)
    q25, q75 = float(np.quantile(class_values, 0.25)), float(np.quantile(class_values, 0.75))
    near = min(abs(value - q25), abs(value - q75)) <= 1e-9 * max(1.0, abs(q25), abs(q75))
    inside = q25 <= value <= q75
    if parts[1] == f"typical of {label} flows":
        return (inside or near), False, ("" if (inside or near) else f"says typical of {label} flows but the value {value:g} is outside [{q25:g}, {q75:g}]")
    m2 = re.fullmatch(rf"(higher|lower) than (\d+)% of {re.escape(label)} flows", parts[1])
    if not m2:
        return False, True, f"unreadable class clause {parts[1]!r}"
    expected_class = _strictly(class_values, value, m2.group(1))
    side_ok = (value > q75) if m2.group(1) == "higher" else (value < q25)
    ok = abs(expected_class - float(m2.group(2))) <= tol_pct + 0.5 and (side_ok or near) and not (inside and not near)
    return ok, True, ("" if ok else f"class clause {parts[1]!r} but the class's flows give {expected_class:.1f}% and the interquartile range is [{q25:g}, {q75:g}] for {value:g}")


def check_category_clause(clause: str | None, raw_value: str, all_values, class_values, label: str, is_unknown: bool, tol_pct: float = 1.0) -> tuple[bool, str]:
    """(g) for a categorical reason: "seen in A% of all flows[; seen in B% of <label> flows]" against the shares among the raw TRAINING categories."""
    import numpy as np
    if clause is None:
        return False, "no clause"
    parts = clause.split("; ")
    m = re.fullmatch(r"seen in (\d+)% of all flows", parts[0])
    if not m:
        return False, f"unreadable clause {parts[0]!r}"
    expected = 100.0 * float((np.asarray(all_values, dtype=str) == str(raw_value)).mean())
    if abs(expected - float(m.group(1))) > tol_pct + 0.5:
        return False, f"overall share {m.group(1)}% but the training flows give {expected:.1f}%"
    if is_unknown:
        return (len(parts) == 1), ("" if len(parts) == 1 else "class clause on a flow flagged Unknown")
    m2 = re.fullmatch(rf"seen in (\d+)% of {re.escape(label)} flows", parts[1]) if len(parts) == 2 else None
    if not m2:
        return False, "no readable class clause"
    expected_class = 100.0 * float((np.asarray(class_values, dtype=str) == str(raw_value)).mean())
    ok = abs(expected_class - float(m2.group(1))) <= tol_pct + 0.5
    return ok, ("" if ok else f"class share {m2.group(1)}% but the class's training flows give {expected_class:.1f}%")
