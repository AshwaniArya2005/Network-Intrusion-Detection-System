"""Task 5 runner on small synthetic data: faithfulness, additivity and the audit through the dashboard's PredictionService."""
import numpy as np
import pandas as pd
import pytest

from pipelines import run_xai_study as rxs
from src.utils.config_loader import load_config, load_feature_sets


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg["paths"].update(unsw_train=str(tmp_path / "missing_train.csv"), unsw_test=str(tmp_path / "missing_test.csv"), cic_file=str(tmp_path / "missing_cic.csv"),
                        models_dir=str(tmp_path / "models"), results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["data"]["synthetic_fallback_rows"] = 3000
    cfg["model"]["params"] = {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["tier_study"].update(block_size=100, buffer=20)
    cfg["feature_selection"]["pool"] = "base"
    return cfg


def test_faithfulness_and_additivity_run_for_every_tier(config):
    tables = rxs.run_faithfulness(config, load_feature_sets(), "base", seeds=(42,), n_boot=50, per_class=15, unknown_n=10)
    add, runs = tables["additivity"], tables["runs"]
    assert set(add["tier"]) == {"40", "30", "15"} and set(add["source"]) == {"test", "validation"}
    assert (add["max_abs_error"] < rxs.TOLERANCE).all() and (add["n_over_tolerance"] == 0).all()               # SHAP values + expected value reproduce the raw margin
    prim = runs[(runs["method"] == "top_minus_random") & (runs["k"] == 5) & (runs["baseline"] == "median") & (runs["stratum"] == "all")]
    assert len(prim) == 6 and (prim["ci_low"] <= prim["mean_drop"]).all() and (prim["mean_drop"] <= prim["ci_high"]).all()   # 3 tiers x 2 sources
    one = runs[(runs["method"] == "top") & (runs["k"] == 1) & (runs["baseline"] == "median") & (runs["stratum"] == "all") & (runs["tier"] == "40") & (runs["source"] == "test")].iloc[0]
    assert 0 <= one["flip_rate"] <= 1 and one["n"] <= 6 * 15 + 10
    assert set(runs["method"]) == {"top", "least", "random", "top_minus_random"}


def test_audit_runs_through_the_dashboard_service_and_reports_every_check(config, tmp_path):
    tables = rxs.run_audit(config, load_feature_sets(), "base", seeds=(42,), scratch=tmp_path / "scratch", per_class=4, unknown_n=6)
    n, summary = tables["narratives"], tables["summary"]
    assert len(n) > 10 and set(n["stratum"]) >= {"Normal"} and n["narrative"].str.startswith("This flow was flagged as").all()
    assert n["confidence_text_ok"].all() and n["confidence_json_ok"].all()                                       # Step 1: the quoted confidence is the model's probability
    assert n[n["is_unknown"]]["narrative"].str.contains("unrecognized").all()
    assert set(summary["stratum"]) >= {"all", "Normal"} and summary[summary["stratum"] == "all"]["n"].iloc[0] == len(n)
    assert {"a_cited_in_top_k", "b_cue_exact_cite", "c_categorical_cite", "d_action", "e_label", "f_consistent_of_determined"} <= set(summary.columns)
    f = tables["failures"]
    assert set(f["check"]) <= {"confidence", "a_cited_in_top_k", "b_cue", "c_categorical", "d_action", "e_label", "f_direction"} if len(f) else True


def test_audit_catches_a_wrong_narrative(config, tmp_path):
    """A narrative whose label, action, confidence and cue are corrupted must fail the matching checks."""
    from src.xai.narrative_generator import NarrativeGenerator
    features = ["rate", "dur", "proto"]
    cfg = load_config()
    shap_row, values = pd.Series({"rate": 2.0, "dur": 1.0, "proto": 0.5}), pd.Series({"rate": -3.0, "dur": 0.0, "proto": 0.0})
    text = NarrativeGenerator(cfg["narrative"]["suggested_actions"]).generate("DoS", 0.5, shap_row, values, pd.Series(0.0, index=features), pd.Series(1.0, index=features),
                                                                              categorical_features=frozenset({"proto"}), top_k=3)
    from src.xai.narrative_audit import check_action, check_cue, check_label_statement, parse_narrative
    parsed = parse_narrative(text, features)
    assert check_cue(parsed["reasons"][0][1], -3.0)["exact"] is True
    assert check_cue("extremely high", -3.0)["direction"] is False                                              # a low value described as high is caught
    assert check_label_statement(parsed, "Exploits", False, text)[0] is False
    assert check_action(parsed["action"], "Exploits", cfg["narrative"]["suggested_actions"]) is False


def test_audit_can_use_validation_flows(config, tmp_path):
    tables = rxs.run_audit(config, load_feature_sets(), "base", seeds=(42,), scratch=tmp_path / "scratch", per_class=3, unknown_n=3, source="validation")
    n = tables["narratives"]
    assert len(n) > 5 and n["confidence_text_ok"].all() and (n["flow"] < 100000).all()
