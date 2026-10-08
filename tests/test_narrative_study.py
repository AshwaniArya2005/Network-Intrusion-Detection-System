"""Narrative study runner on small synthetic data, and the pieces of it that can be checked by hand."""
import numpy as np
import pandas as pd
import pytest

from pipelines import run_narrative_study as rns
from src.utils.config_loader import load_config, load_feature_sets


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg["paths"].update(unsw_train=str(tmp_path / "m1.csv"), unsw_test=str(tmp_path / "m2.csv"), cic_file=str(tmp_path / "m3.csv"), models_dir=str(tmp_path / "models"),
                        results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["data"]["synthetic_fallback_rows"] = 4000
    cfg["model"]["params"] = {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["tier_study"].update(block_size=100, buffer=20)
    cfg["feature_selection"]["pool"] = "base"
    return cfg


def test_allocation_sample_uses_the_named_sizes_and_the_class_default():
    strata = np.array(["A"] * 40 + ["B"] * 5 + ["Unknown"] * 30 + ["FP-Normal"] * 10)
    pick = rns.allocation_sample(strata, {"class": 8, "Unknown": 12, "FP-Normal": 20}, np.random.default_rng(0))
    counts = pd.Series(strata[pick]).value_counts().to_dict()
    assert counts == {"A": 8, "B": 5, "Unknown": 12, "FP-Normal": 10}                         # B has 5 flows, FP-Normal only 10
    assert np.array_equal(pick, rns.allocation_sample(strata, {"class": 8, "Unknown": 12, "FP-Normal": 20}, np.random.default_rng(0)))


def test_group_masks_by_hand():
    true = np.array(["Normal", "Normal", "Normal", "Normal", "Attack", "Attack"])
    fine = np.array(["Normal", "Normal", "Normal", "Normal", "Fuzzers", "Exploits"])
    pred = np.array(["Normal", "Fuzzers", "Exploits", "Normal", "Fuzzers", "Fuzzers"])
    m = rns.group_masks(true, fine, pred, "Normal")
    assert m["TN"].tolist() == [True, False, False, True, False, False] and m["FP-attack"].tolist() == [False, True, True, False, False, False]
    assert m["FP-Fuzzers"].tolist() == [False, True, False, False, False, False] and m["TP-Fuzzers"].tolist() == [False, False, False, False, True, False]


def test_atypicality_and_auroc_by_hand():
    parsed = {"reasons": [("rate", "high", None), ("dur", "low", None), ("proto", None, "tcp"), ("sbytes", "high", None)],
              "clauses": ["higher than 90% of all flows; typical of DoS flows", "lower than 80% of all flows; lower than 95% of DoS flows", "seen in 50% of all flows; seen in 60% of DoS flows",
                          "higher than 70% of all flows"]}                                   # the last has no class clause (a flow flagged Unknown): not counted
    assert rns.atypicality(parsed) == 0.5                                                       # one of two numeric class clauses is outside the interquartile range
    assert np.isnan(rns.atypicality({"reasons": [("proto", None, "tcp")], "clauses": ["seen in 50% of all flows; seen in 60% of DoS flows"]}))
    assert rns.auroc(np.array([0.9, 0.8]), np.array([0.1, 0.2])) == 1.0 and rns.auroc(np.array([0.5]), np.array([0.5])) == 0.5
    assert np.isnan(rns.auroc(np.array([np.nan]), np.array([0.1])))


def test_narrative_part_audits_both_styles_and_reports_calibration(config, tmp_path):
    tables = rns.run_narrative(config, load_feature_sets(), "base", seeds=(42,), source="test", scratch=tmp_path / "s", allocation={"class": 4, "Unknown": 5, "FP-Normal": 4})
    n, summary, cal = tables["narratives"], tables["summary"], tables["calibration"]
    assert set(n["style"]) == {"classic", "class_relative"} and n.groupby("style").size().nunique() == 1          # the same flows in both styles
    rel, cls = n[n["style"] == "class_relative"], n[n["style"] == "classic"]
    assert rel["confidence_text_ok"].all() and rel["a_ok"].all() and rel["b_exact"].eq(rel["n_cited_numeric"]).all() and rel["d_ok"].all() and rel["e_ok"].all()
    assert rel["g_ok"].eq(rel["g_clauses"]).all() and rel["calibrated_ok"].all()                                  # check g: every clause and the calibrated number are right
    assert rel["f_no_direction_claimed"].sum() == 0 and cls["f_no_direction_claimed"].sum() >= 0                  # by construction no cited numeric feature reads "typical"
    assert {"ece_raw", "ece_calibrated", "temperature"} <= set(cal.columns) and (cal["temperature"] > 0).all()
    assert set(summary["style"]) == {"classic", "class_relative"} and summary[summary["style"] == "classic"]["g_clauses_correct"].isna().all()


def test_falsepos_part_reports_groups_faithfulness_and_separation(config, tmp_path):
    tables = rns.run_falsepos(config, load_feature_sets(), "base", seeds=(42,), group_size=20, scratch=tmp_path / "s", n_boot=50)
    f, g = tables["faithfulness"], tables["groups"]
    assert {"TN"} <= set(g["group"]) and set(f["baseline"]) == {"median", "random_row"}
    assert (f["ci_low"] <= f["difference"]).all() and (f["difference"] <= f["ci_high"]).all()
    assert g["raw_confidence_mean"].between(0, 1).all() and g["calibrated_confidence_mean"].between(0, 1).all()
    assert set(tables["features"]["style"]) <= {"classic", "class_relative"}


def test_summary_side_by_side_and_reading_by_hand():
    from scripts.narrative_summary import faithful_reading, side_by_side
    rows = []
    for style, typical in (("classic", 0.5), ("class_relative", 0.0)):
        for seed in (42, 43):
            rows.append({"pool_label": "40f", "seed": seed, "stratum": "all", "style": style, "n": 230, "typical_share_of_cited_numeric": typical, "cited_features_per_narrative": 4.0 if style == "classic" else 2.5,
                         "cited_numeric_per_narrative": 3.0, "share_narratives_without_numeric_feature": 0.0, "a_cited_in_top_k": 1.0, "b_cue_exact_cite": 1.0, "c_categorical_cite": 1.0, "d_action": 1.0,
                         "e_label": 1.0, "f_consistent_of_determined": 0.75, "g_clauses_correct": np.nan if style == "classic" else 1.0, "calibrated_number_correct": np.nan if style == "classic" else 1.0})
    lines = side_by_side(pd.DataFrame(rows), "40f")
    assert any(l.startswith("| cited numeric features read") and l.endswith("| 0.500 +/- 0.000 | 0.000 +/- 0.000 |") for l in lines)
    assert any("(g) clauses" in l and "| n/a | 1.000 +/- 0.000 |" in l for l in lines)
    ci = pd.DataFrame({"difference": [0.4, 0.3], "ci_low": [0.3, 0.2]})
    assert faithful_reading(ci) and not faithful_reading(ci.assign(ci_low=[0.3, -0.1])) and not faithful_reading(ci.assign(difference=[0.4, 0.02]))


def test_ab_sheet_pairs_flows_hides_the_style_and_keeps_it_in_the_key():
    from scripts.make_ab_sheet import GROUPS, assign_ab, pair_narratives, pick_flows
    rows = []
    for flow, stratum in enumerate(["Normal"] * 8 + ["Overlap-Group-1"] * 8 + ["Fuzzers"] * 8 + ["Unknown"] * 3 + ["FP-Normal"] * 8 + ["Exploits"] * 4 + ["Generic"] * 4):
        for style in ("classic", "class_relative"):
            rows.append({"seed": 42, "flow": flow, "stratum": stratum, "style": style, "narrative": f"{style} {flow}"})
    pairs = pair_narratives(pd.DataFrame(rows))
    assert len(pairs) == 43 and set(pairs.columns) >= {"classic", "class_relative"}
    chosen = assign_ab(pick_flows(pairs, GROUPS, 5))
    counts = chosen["group"].value_counts().to_dict()
    assert counts["Unknown"] == 3 and counts["Normal"] == 5 and counts["other attack classes"] == 5                 # Unknown has only 3 flows here
    assert chosen["flow"].is_unique
    for _, r in chosen.iterrows():                                                                                  # the key says which column is classic
        assert (r["narrative_A"].startswith("classic") if r["classic_is"] == "A" else r["narrative_B"].startswith("classic"))
    assert set(chosen["classic_is"]) == {"A", "B"}
