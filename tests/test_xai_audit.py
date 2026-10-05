"""Task 5 narrative audit helpers, checked by hand on narratives from the real generator."""
import pandas as pd
import pytest

from src.xai.narrative_audit import (
    UNRECOGNIZED, check_action, check_categorical, check_cited_in_top, check_cue, check_label_statement, cue_direction, directional_consistency, parse_narrative,
)
from src.xai.narrative_generator import NarrativeGenerator

FEATURES = ["rate", "dur", "total_bytes", "duration_log", "proto", "ct_srv_src"]
ACTIONS = {"DoS": "Consider rate-limiting.", "Unknown": "Escalate.", "Overlap-Group-1": "Flagged as DoS, Backdoor, or Analysis-type behavior. Escalate."}


def narrative(label="DoS", conf=0.978, shap=None, values=None, unknown=False, top_k=3):
    shap = pd.Series(shap or {"rate": 2.0, "dur": 1.5, "proto": 1.0}, index=FEATURES).fillna(0.0)
    values = pd.Series(values or {"rate": 3.0, "dur": -1.5, "proto": 0.0}, index=FEATURES).fillna(0.0)
    return NarrativeGenerator(ACTIONS).generate(label, conf, shap, values, pd.Series(0.0, index=FEATURES), pd.Series(1.0, index=FEATURES),
                                                categorical_features=frozenset({"proto"}), top_k=top_k, is_unknown=unknown)


def test_parse_recovers_label_confidence_reasons_and_action():
    text = narrative()
    p = parse_narrative(text, FEATURES)
    assert p["label"] == "DoS" and p["confidence_pct"] == 97.8 and p["action"] == "Consider rate-limiting."
    assert p["reasons"] == [("rate", "extremely high", None), ("dur", "unusually low", None), ("proto", None, "0.0")]


def test_parse_prefers_the_longest_description_and_handles_diffuse_and_unknown():
    text = NarrativeGenerator(ACTIONS).generate("DoS", 0.5, pd.Series({"duration_log": 3.0, "dur": 0.0, "rate": 0.0}),
                                                pd.Series({"duration_log": 2.0, "dur": 0.0, "rate": 0.0}), pd.Series(0.0, index=["duration_log", "dur", "rate"]),
                                                pd.Series(1.0, index=["duration_log", "dur", "rate"]), top_k=1)
    assert parse_narrative(text, ["dur", "duration_log", "rate"])["reasons"] == [("duration_log", "unusually high", None)]      # "log-scaled flow duration" beats "flow duration"
    diffuse = parse_narrative(NarrativeGenerator(ACTIONS).generate("DoS", 0.5, pd.Series({"rate": -1.0})), ["rate"])
    assert diffuse["diffuse"] and diffuse["reasons"] == []
    unknown = parse_narrative(narrative(unknown=True), FEATURES)
    assert unknown["label"] == UNRECOGNIZED and unknown["action"] == "Escalate."


def test_cue_check_exact_direction_and_boundaries():
    assert check_cue("extremely high", 3.0) == {"exact": True, "direction": True, "expected": "extremely high"}
    assert check_cue("unusually high", 3.0)["exact"] is False and check_cue("unusually high", 3.0)["direction"] is True      # right direction, wrong strength
    assert check_cue("typical", 0.2)["exact"] is True and check_cue("reduced", 0.2)["direction"] is False
    assert check_cue("elevated", 1.0 - 1e-9)["exact"] is True                                                           # within tolerance of the 1.0 boundary: either neighbour
    assert check_cue("extremely high", -3.0)["direction"] is False                                                      # the double-standardisation failure mode: a low value read as high
    assert cue_direction("notable") == "none" and cue_direction(None) == "none"


def test_cited_features_must_be_positive_and_in_the_top_k():
    shap = pd.Series({"rate": 2.0, "dur": -3.0, "total_bytes": 1.0, "ct_srv_src": 0.1})
    assert check_cited_in_top(["rate", "total_bytes"], shap, 3) is True            # top 3 by |SHAP|: dur (negative), rate, total_bytes
    assert check_cited_in_top(["dur"], shap, 3) is False                           # negative SHAP is never a reason
    assert check_cited_in_top(["ct_srv_src"], shap, 3) is False                    # fourth by magnitude


def test_categorical_check_names_the_real_category_and_flags_unseen_values():
    assert check_categorical("proto", None, "tcp", "tcp", True) == (True, "")
    assert check_categorical("proto", "extremely high", None, "tcp", True)[0] is False
    ok, reason = check_categorical("proto", None, "udp", "tcp", True)
    assert ok is False and "udp" in reason and "tcp" in reason
    ok, reason = check_categorical("service", None, "__unseen__", "weird", False)
    assert ok is False and "never seen in training" in reason


def test_action_and_label_checks():
    assert check_action("Consider rate-limiting.", "DoS", ACTIONS) is True
    assert check_action("Escalate.", "DoS", ACTIONS) is False
    assert check_action(None, "Normal", ACTIONS) is True                           # no configured action: none expected
    text = narrative(label="Overlap-Group-1")
    assert check_label_statement(parse_narrative(text, FEATURES), "Overlap-Group-1", False, text) == (True, "")
    wrong = narrative(label="DoS")
    ok, reason = check_label_statement(parse_narrative(wrong, FEATURES), "Overlap-Group-1", False, wrong)
    assert ok is False and "DoS" in reason                                          # says "flagged as DoS" when the prediction is the group
    unk = narrative(unknown=True)
    assert check_label_statement(parse_narrative(unk, FEATURES), "DoS", True, unk) == (True, "")
    ok, _ = check_label_statement(parse_narrative(narrative(label="DoS"), FEATURES), "DoS", True, narrative(label="DoS"))
    assert ok is False                                                              # flagged Unknown but the narrative names the class


def test_directional_consistency_rule():
    assert directional_consistency("unusually high", 0.5) == "consistent"
    assert directional_consistency("unusually high", -0.5) == "inconsistent"
    assert directional_consistency("reduced", -0.4) == "consistent" and directional_consistency("reduced", 0.4) == "inconsistent"
    assert directional_consistency("unusually high", 0.05) == "no monotone relation"
    assert directional_consistency("typical", 0.9) == "no direction claimed" and directional_consistency("notable", 0.9) == "no direction claimed"


def test_standardised_values_need_mean_zero_std_one_and_the_check_script_uses_them():
    """Regression test: feature values from Preprocessor.transform are already z-scores. Passing the scaler's raw mean / scale standardised them twice, so a flow 3 standard deviations above
    the training mean of a feature whose raw mean is 1000 read as 'extremely low'. scripts/check_explainability.py had that defect; it must use the shared helper."""
    import inspect
    from src.xai.narrative_generator import standardised_value_statistics
    means, stds = standardised_value_statistics(["rate", "dur"])
    assert means.tolist() == [0.0, 0.0] and stds.tolist() == [1.0, 1.0]
    gen = NarrativeGenerator({})
    z_values = pd.Series({"rate": 3.0})
    ok = gen.generate("DoS", 0.9, pd.Series({"rate": 1.0}), z_values, means, stds, top_k=1)
    assert "extremely high packet rate" in ok
    twice = gen.generate("DoS", 0.9, pd.Series({"rate": 1.0}), z_values, pd.Series({"rate": 1000.0}), pd.Series({"rate": 50.0}), top_k=1)
    assert "extremely low packet rate" in twice                                    # what the second standardisation did
    import scripts.check_explainability as script
    source = inspect.getsource(script.main)
    assert "standardised_value_statistics" in source and "scaler.mean_" not in source and "scaler.scale_" not in source


def test_summary_readings_by_hand():
    import numpy as np
    from scripts.xai_summary import is_faithful, primary_rows, shift_row
    runs = pd.DataFrame([{"pool_label": "40f", "tier": "40", "n_features": 40, "seed": s, "source": "test", "stratum": "all", "method": "top_minus_random", "baseline": "median",
                          "k": 5, "n": 100, "mean_drop": d, "ci_low": lo, "ci_high": hi} for s, d, lo, hi in [(42, 0.20, 0.15, 0.25), (43, 0.10, 0.04, 0.16)]])
    rows = primary_rows(runs)
    assert len(rows) == 2 and is_faithful(rows)
    assert not is_faithful(rows.assign(ci_low=[0.15, -0.01]))                       # an interval reaching zero in one seed
    assert not is_faithful(rows.assign(mean_drop=[0.20, 0.03]))                     # an effect below 0.05
    rng = np.random.default_rng(0)
    lost = shift_row(rng.normal(0.05, 0.2, 3000), rng.normal(0.20, 0.2, 3000))
    assert lost["lost_under_shift"] is True and lost["difference"] < -0.05
    kept = shift_row(rng.normal(0.19, 0.2, 3000), rng.normal(0.20, 0.2, 3000))
    assert kept["lost_under_shift"] is False


def test_human_audit_sheet_allocation_is_stratified_seeded_and_unlabelled():
    from scripts.make_human_audit_sheet import ALLOCATION, RATING_COLUMNS, pick_rows
    rows = pd.DataFrame([{"stratum": s, "flow": i, "seed": 42, "narrative": f"n{i}"} for i, s in enumerate(["Normal"] * 10 + ["Overlap-Group-1"] * 10 + ["Exploits"] * 10 + ["Fuzzers"] * 10 +
                                                                                                ["Generic"] * 10 + ["Reconnaissance"] * 10 + ["Unknown"] * 3)])
    chosen = pick_rows(rows, ALLOCATION)
    counts = chosen["stratum"].value_counts().to_dict()
    assert len(chosen) == 28 and counts["Unknown"] == 3 and counts["Overlap-Group-1"] == 5 and counts["Normal"] == 4             # Unknown has only 3 narratives here
    assert chosen["flow"].is_unique and chosen.equals(pick_rows(rows, ALLOCATION))
    assert sum(ALLOCATION.values()) == 30 and not any(c in ("attack_cat", "true_label") for c in RATING_COLUMNS)
