"""Task 4.5 runner (pipelines/run_openset_boost.py): every idea end to end on small synthetic data, plus the invariants that make the comparison fair."""
import numpy as np
import pandas as pd
import pytest

from pipelines import run_openset_boost as rob
from pipelines.run_open_set_study import OpenSetRun
from pipelines.run_tier_study import prepare
from src.utils.config_loader import load_config, load_feature_sets

SPEC = [("Worms + Shellcode", ["Worms", "Shellcode"])]


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg["paths"].update(unsw_train=str(tmp_path / "missing_train.csv"), unsw_test=str(tmp_path / "missing_test.csv"), cic_file=str(tmp_path / "missing_cic.csv"),
                        models_dir=str(tmp_path / "models"), results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["data"]["synthetic_fallback_rows"] = 3000
    cfg["model"]["params"] = {"n_estimators": 8, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["tier_study"].update(block_size=100, buffer=20)
    cfg["feature_selection"]["pool"] = "base"
    return cfg


@pytest.fixture
def run(config):
    cfg, sets, splits = prepare(config, load_feature_sets(), "base", "xgboost", 42)
    return OpenSetRun(cfg, splits.train, splits.val, splits.test, splits.unknown, list(sets["feature_pool"]), 42), cfg, splits


def test_calibration_adds_two_scores_and_reports_ece(run):
    r, _, _ = run
    out = rob.add_calibration(r)
    assert 0.25 <= out["temperature"] <= 5 and 0 <= out["ece_before"] <= 1 and 0 <= out["ece_after"] <= 1
    for part in rob.PARTS:
        assert {"msp_cal", "entropy_cal"} <= set(r.parts[part]["scores"])


def test_per_class_rule_flags_about_the_target_share_inside_every_predicted_class(run):
    r, _, _ = run
    rob.add_per_class(r)
    flagged = r.flags("msp_pc", "thr")                                                     # the half the thresholds were fitted on
    assert flagged.mean() == pytest.approx(0.05, abs=0.02)
    assert "msp_pc" in r.flaggers and (r.parts["thr"]["scores"]["msp_pc"] > 0).tolist() == flagged.tolist()    # the shifted score is above 0 exactly when flagged
    assert r.flags("msp_pc", "test", 0.30).mean() >= r.flags("msp_pc", "test", 0.05).mean()  # a larger target flags more


def test_ensemble_and_distance_scores_cover_every_part(run):
    r, _, _ = run
    rob.add_ensemble(r, 42)
    rob.add_distance(r, 42)
    for part in rob.PARTS:
        n = len(r.parts[part]["p"])
        for name in ("ens_mi", "ens_var", "ens_msp", "knn", "maha"):
            assert len(r.parts[part]["scores"][name]) == n and np.isfinite(r.parts[part]["scores"][name]).all()
    assert (r.parts["test"]["scores"]["ens_mi"] >= -1e-9).all()                            # mutual information is non-negative


def test_outlier_exposure_run_removes_the_pseudo_unknown_classes_from_the_known_sets(config):
    cfg, sets, splits = prepare({**config, "data": {**config["data"], "unknown_attack_categories": ["Worms", "Shellcode"]}}, load_feature_sets(), "base", "xgboost", 42)
    run, diag = rob.build_oe_run(cfg, splits, list(sets["feature_pool"]), 42, ["Worms", "Shellcode"])
    assert diag["pseudo_unknown_classes"] == "Reconnaissance+Generic"
    for part in ("cal", "thr", "test"):
        assert not run.frames[part]["attack_cat"].isin(["Reconnaissance", "Generic"]).any()
    assert "Reconnaissance" not in run.classes and "Generic" not in run.classes and "Unknown" not in run.classes          # the baseline model never saw them
    assert 0 <= diag["known_macro_recall_oe"] <= 1 and 0 <= diag["known_macro_recall_noP"] <= 1
    assert {"oe_pu", "oe_msp"} <= set(run.parts["unknown"]["scores"])
    held_generic = rob.pseudo_unknown_classes(["Generic"])
    assert "Generic" not in held_generic                                                   # the evaluation's held-out class is never a pseudo-unknown class


def test_composition_counts_and_precision_by_hand(run):
    r, _, _ = run
    rows = rob.composition_rows(r, "40f", 42, "Worms + Shellcode", ["msp"])
    table = pd.DataFrame(rows)
    flagged_known = int(table[table["kind"] == "known"]["n_flagged"].sum())
    flagged_zero = int(table[table["kind"] == "zero-day"]["n_flagged"].sum())
    assert flagged_known == int(r.flags("msp", "test").sum()) and flagged_zero == int(r.flags("msp", "unknown").sum())
    assert table["unknown_precision"].iloc[0] == pytest.approx(flagged_zero / max(flagged_zero + flagged_known, 1))
    assert set(table[table["kind"] == "zero-day"]["bucket"]) == {"Worms", "Shellcode"}


def test_iforest_check_reports_the_sign_and_percentiles(run):
    r, _, _ = run
    rob.add_distance(r, 42)
    rows = rob.iforest_rows(r, "40f", 42)
    assert {x["score"] for x in rows} == {"iforest", "knn", "maha"}
    for x in rows:
        assert 0 <= x["attack_vs_normal_auroc"] <= 1 and 0 <= x["percentile_Worms"] <= 1 and 0 <= x["percentile_Shellcode"] <= 1


def test_top_two_and_combination_use_the_selection_table_and_the_calibration_half(run):
    selection = pd.DataFrame({"score": ["msp", "entropy", "ens_mi", "knn", "iforest"] * 2, "pseudo_auroc": [0.7, 0.8, 0.9, 0.6, 0.99] * 2})
    assert rob.top_two(selection) == ["ens_mi", "entropy"]                                  # iforest is not eligible
    r, _, _ = run
    rob.add_calibration(r)
    rob.add_combination(r, ["msp", "entropy_cal"])
    combo = r.parts["test"]["scores"]["combo"]
    assert ((combo >= 0) & (combo <= 1)).all()                       # a mean of two ranks in [0, 1] (a score below every calibration score has rank 0)
    from src.openset_scores import RankNormalizer
    expected = (RankNormalizer().fit(r.parts["cal"]["scores"]["msp"]).transform(r.parts["test"]["scores"]["msp"])
                + RankNormalizer().fit(r.parts["cal"]["scores"]["entropy_cal"]).transform(r.parts["test"]["scores"]["entropy_cal"])) / 2
    assert np.allclose(combo, expected)                              # by hand: the mean of the two calibration-half ranks


def test_every_idea_runs_end_to_end(config):
    feature_sets = load_feature_sets()
    for idea in ("calibration", "perclass", "ensemble", "distance", "oe", "iforest"):
        tables = rob.run_idea(config, feature_sets, "base", idea, (42,), SPEC)
        runs = tables["runs"]
        assert set(runs["held_out"]) == {"Worms + Shellcode"} and set(runs["zero_day"]) == {"Shellcode+Worms", "Shellcode", "Worms"}
        special = {"iforest": {"msp"}, "oe": {"noP_msp", "noP_entropy", "oe_pu", "oe_msp"}}
        expected = special[idea] if idea in special else {"msp", "entropy", *rob.SCORE_NAMES[idea]}
        assert set(runs["score"]) == expected, idea
        assert runs["detection_matched_to_msp"].between(0, 1).all() if idea != "oe" else True
        assert len(tables["curve"]) > 0 and len(tables["composition"]) > 0
    selection = rob.run_selection(config, feature_sets, "base", (42,))
    assert set(selection["inner_class"]) == {"Reconnaissance", "Generic"} and set(rob.ELIGIBLE) <= set(selection["score"])
    combo = rob.run_combo(config, feature_sets, "base", (42,), SPEC, selection)
    assert "combo" in set(combo["runs"]["score"]) and combo["runs"]["combo_of"].nunique() == 1


def _runs(score_effects: dict[str, tuple[float, float]], seeds=(42, 43, 44, 45, 46), ws_shift: float = 0.0) -> pd.DataFrame:
    """Rows for the nine rotation classes and Worms + Shellcode: detection / AUROC of each score are the given constants (detection, AUROC)."""
    from scripts.open_set_boost_summary import ROTATION, WS, WS_SET
    rows = []
    for score, (det, auc) in score_effects.items():
        for seed in seeds:
            for held in ROTATION:
                rows.append({"seed": seed, "score": score, "held_out": held, "zero_day": held, "detection": det, "unknown_auroc": auc, "false_unknown_thr_half": 0.05, "false_unknown_cal_half": 0.05,
                             "false_unknown_test": 0.06, "flagged_or_attack": 0.9, "detection_matched_to_msp": det})
            rows.append({"seed": seed, "score": score, "held_out": WS, "zero_day": WS_SET, "detection": det + ws_shift, "unknown_auroc": auc, "false_unknown_thr_half": 0.05,
                         "false_unknown_cal_half": 0.05, "false_unknown_test": 0.06, "flagged_or_attack": 0.9, "detection_matched_to_msp": det})
    return pd.DataFrame(rows)


def test_verdict_applies_the_declared_rule():
    from scripts.open_set_boost_summary import verdict
    runs = _runs({"msp": (0.20, 0.75), "good": (0.28, 0.78), "small": (0.23, 0.78), "lower_auroc": (0.30, 0.70)})
    assert verdict(runs, "good")["clearly_beats"] is True and verdict(runs, "good")["seeds_better"] == 5
    assert verdict(runs, "small")["clearly_beats"] is False                                  # +0.03 is below the declared +0.05
    assert verdict(runs, "lower_auroc")["clearly_beats"] is False                            # detection gain but a lower AUROC
    worse_ws = pd.concat([_runs({"msp": (0.20, 0.75)}), _runs({"good": (0.28, 0.78)}, ws_shift=-0.20)])   # rotation gain, but Worms + Shellcode detection 0.12 below msp's 0.20 -> 0.08
    assert verdict(worse_ws, "good")["clearly_beats"] is False


def test_summary_per_class_composition_and_queue_tables_render():
    from scripts.open_set_boost_summary import composition_table, per_class_table, queue_table, summary_table
    runs = _runs({"msp": (0.20, 0.75), "ens_mi": (0.28, 0.78)})
    assert "yes" in summary_table(runs, ["msp", "ens_mi"])[-1] and "no" in summary_table(runs, ["msp", "ens_mi"])[-2]
    assert any("Worms + Shellcode" in line for line in per_class_table(runs, ["msp"]))
    comp = pd.DataFrame([{"score": "msp", "bucket": b, "kind": k, "n_total": n, "n_flagged": f, "unknown_precision": 0.1}
                         for b, k, n, f in [("Shellcode", "zero-day", 100, 25), ("Worms", "zero-day", 10, 1), ("Normal", "known", 1000, 60)]])
    assert "25 of 100" in composition_table(comp, ["msp"])[-1] and "0.100" in composition_table(comp, ["msp"])[-1]
    curve = pd.DataFrame([{"score": "msp", "target": 0.05, "alert_fpr_off": 0.29, "alert_fpr_on": 0.31, "confident_alert_fpr": 0.25, "review_rate_normal": 0.06,
                           "share_of_false_alerts_that_skip_review": 0.88, "zero_day_catch": 0.95, "zero_day_flagged": 0.22}])
    assert "0.250" in queue_table(curve, ["msp"])[-1]


def test_one_pass_gives_every_idea_its_own_tables_with_the_shared_baselines(config):
    selection = pd.DataFrame({"score": ["msp", "entropy", "ens_mi", "knn", "oe_pu"], "pseudo_auroc": [0.7, 0.8, 0.9, 0.85, 0.5]})      # top two: ens_mi, knn (no Unknown-class model)
    tables = rob.run_pass(config, load_feature_sets(), "base", (42,), SPEC, selection)
    assert set(tables) == {"calibration", "perclass", "ensemble", "distance", "combo", "iforest"}
    for idea in rob.PASS_IDEAS:
        assert set(tables[idea]["runs"]["score"]) == {"msp", "entropy", *rob.SCORE_NAMES[idea]}
        assert len(tables[idea]["curve"]) > 0 and len(tables[idea]["composition"]) > 0
    assert set(tables["combo"]["runs"]["score"]) == {"msp", "entropy", "ens_mi", "knn", "combo"} and tables["combo"]["runs"]["combo_of"].iloc[0] == "ens_mi+knn"
    assert {"temperature", "ece_before", "ece_after"} <= set(tables["calibration"]["diagnostics"].columns)
    assert set(tables["iforest"]["checks"]["score"]) == {"iforest", "knn", "maha"}
    # the same baseline rows appear in every idea (one base model per run)
    base = [t["runs"][t["runs"]["score"] == "msp"][["seed", "zero_day", "detection"]].reset_index(drop=True) for t in (tables["calibration"], tables["ensemble"])]
    assert base[0].equals(base[1])
    with_oe = pd.DataFrame({"score": ["oe_pu", "ens_mi", "msp"], "pseudo_auroc": [0.9, 0.8, 0.7]})                                      # top two need the Unknown-class model: no combo here
    assert "combo" not in rob.run_pass(config, load_feature_sets(), "base", (42,), SPEC, with_oe)


def test_one_outlier_exposure_pass_serves_the_oe_and_combo_ideas(config):
    selection = pd.DataFrame({"score": ["oe_pu", "ens_mi", "msp"], "pseudo_auroc": [0.9, 0.8, 0.7]})                                   # top two: oe_pu, ens_mi
    tables = rob.run_combo(config, load_feature_sets(), "base", (42,), SPEC, selection)
    assert set(tables["runs"]["score"]) == {"noP_msp", "noP_entropy", "oe_pu", "oe_msp", "ens_mi", "combo"}
    split = rob.split_ideas(tables, ["noP_msp", "noP_entropy"], True, rob.top_two(selection))
    assert set(split) == {"combo", "oe"}
    assert set(split["combo"]["runs"]["score"]) == {"noP_msp", "noP_entropy", "oe_pu", "ens_mi", "combo"}
    assert set(split["oe"]["runs"]["score"]) == {"noP_msp", "noP_entropy", "oe_pu", "oe_msp"}
    assert "known_macro_recall_oe" in tables["diagnostics"].columns                                                                  # the cost to known-class recall is recorded
    no_oe = rob.split_ideas(tables, ["msp", "entropy"], False, ["ens_mi", "knn"])
    assert set(no_oe) == {"combo"}


def test_iforest_table_reports_sign_and_percentiles():
    from scripts.open_set_boost_summary import WS, render_iforest
    checks = pd.DataFrame([{"seed": s, "score": "iforest", "held_out": WS, "attack_vs_normal_auroc": 0.67, "percentile_Worms": 0.68, "percentile_Shellcode": 0.41} for s in (42, 43)]
                          + [{"seed": 42, "score": "iforest", "held_out": "Fuzzers", "attack_vs_normal_auroc": 0.60, "percentile_Worms": 0.5, "percentile_Shellcode": 0.5}])
    text = render_iforest("40f", checks)
    assert "| iforest | 0.670 +/- 0.000 | 0.680 +/- 0.000 | 0.410 +/- 0.000 |" in text and "iforest AUROC 0.600" in text
