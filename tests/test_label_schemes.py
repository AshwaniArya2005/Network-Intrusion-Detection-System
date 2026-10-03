"""Configurable label schemes: merging, end-to-end pipeline per scheme, comparison CSV, file naming."""
import numpy as np
import pytest

from pipelines.run_label_scheme_comparison import run_label_scheme_comparison
from pipelines.train_pipeline import generate_feature_ranking, load_split_data, train_and_evaluate
from src.data_loader import make_synthetic_unsw
from src.models.hierarchical_model import HierarchicalModel
from src.models.model_factory import create_model
from src.preprocessing import add_merged_label
from src.utils.config_loader import (
    choose_pool, get_label_scheme, get_metrics_dir, load_config, load_feature_sets, resolve_path, scheme_tag, tagged,
)

SCHEMES = ["current", "none", "wide", "hierarchical"]


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg["paths"].update(
        unsw_train=str(tmp_path / "missing.csv"), unsw_test=str(tmp_path / "missing2.csv"),
        models_dir=str(tmp_path / "models"), results_dir=str(tmp_path / "results"),
        feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["data"]["synthetic_fallback_rows"] = 1500
    cfg["model"]["params"] = {"n_estimators": 8, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["experiments"].update(feature_sets_full=["15"], feature_sets=["15"])
    cfg["feature_selection"]["active_set"] = "15"
    return cfg


def test_default_scheme_is_the_original_merge(config):
    assert config["data"]["label_scheme"] == "current"
    assert get_label_scheme(config) == ("current", {"Overlap-Group-1": ["Analysis", "Backdoor", "DoS"]}, False)
    assert scheme_tag(config) == "" and tagged(config, "experiment_results.csv") == "experiment_results.csv"


@pytest.mark.parametrize("name,expected", [
    ("current", {"Analysis": "Overlap-Group-1", "DoS": "Overlap-Group-1", "Exploits": "Exploits"}),
    ("none", {"Analysis": "Analysis", "DoS": "DoS", "Exploits": "Exploits"}),
    ("wide", {"Analysis": "Overlap-Group-2", "DoS": "Overlap-Group-2", "Exploits": "Overlap-Group-2", "Fuzzers": "Fuzzers"}),
    ("hierarchical", {"Analysis": "Analysis", "Exploits": "Exploits"}),
])
def test_add_merged_label_per_scheme(config, name, expected):
    config["data"]["label_scheme"] = name
    df = make_synthetic_unsw(n_rows=800, seed=1)
    merged = add_merged_label(df, get_label_scheme(config)[1])
    for cat, label in expected.items():
        assert set(merged.loc[df["attack_cat"] == cat, "label_merged"]) == {label}


def test_hierarchical_model_composes_valid_probabilities():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 4, 600)
    X = rng.normal(size=(600, 5)) + y[:, None]
    model = HierarchicalModel(lambda: create_model("xgboost", {"n_estimators": 8, "max_depth": 3}), normal_index=2).fit(X, y)
    proba = model.predict_proba(X)
    assert proba.shape == (600, 4) and np.allclose(proba.sum(axis=1), 1.0, atol=1e-5)
    assert (model.predict(X) == y).mean() > 0.5


@pytest.mark.parametrize("name", SCHEMES)
def test_pipeline_runs_end_to_end_for_each_scheme(config, name):
    config["data"]["label_scheme"] = name
    splits = load_split_data(config)
    config, fsets = choose_pool(config, load_feature_sets(), splits.train.columns)
    generate_feature_ranking(config, fsets, splits.train)
    result = train_and_evaluate(config, fsets, "15", True, splits)

    assert result["label_scheme"] == name and result["feature_pool"] == "full"
    assert {"fine_recall_Analysis", "fine_recall_Exploits", "unknown_auroc"} <= set(result)
    model_dir = resolve_path(config["paths"]["models_dir"]) / "xgboost"
    tag = scheme_tag(config)
    assert (model_dir / f"preprocessor_15{tag}.pkl").exists() and (model_dir / f"open_set_15{tag}.json").exists()


def test_scheme_outputs_never_overwrite_the_defaults(config):
    other = dict(config, data=dict(config["data"], label_scheme="wide"))
    assert tagged(other, "experiment_results.csv") == "experiment_results_wide.csv"
    assert tagged(config, "experiment_results.csv") == "experiment_results.csv"


def test_label_scheme_comparison_is_comparable_and_writes_both_splits(config):
    from pipelines.run_label_scheme_comparison import write_label_scheme_summary
    fsets = load_feature_sets()
    config["data"]["report_fine_recall"] = ["Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic",
                                            "Reconnaissance", "Normal"]
    out = run_label_scheme_comparison(config, fsets, SCHEMES)
    pooled = run_label_scheme_comparison(config, fsets, SCHEMES, use_official_split=False,
                                         output_name="label_scheme_comparison_pooled.csv")
    assert list(out["label_scheme"]) == SCHEMES == list(pooled["label_scheme"])
    assert "f1" not in out.columns and "macro_f1_not_comparable_across_schemes" in out.columns
    assert {"detection_rate", "false_positive_rate", "fine_recall_macro", "group_size_share", "rank_fine_recall_macro",
            "rank_false_positive_rate", "fine_recall_Fuzzers", "fine_recall_Normal",
            "best_possible_accuracy_dups_kept"} <= set(out.columns)
    by = out.set_index("label_scheme")
    assert by.loc["none", "group_size_share"] == 0 and by.loc["current", "group_size_share"] > 0
    assert by.loc["wide", "group_size_share"] > by.loc["current", "group_size_share"]  # wide lumps more attack traffic
    recalls = [c for c in out.columns if c.startswith("fine_recall_") and c != "fine_recall_macro"]
    np.testing.assert_allclose(by["fine_recall_macro"], by[recalls].mean(axis=1), atol=1e-3)
    assert sorted(by["rank_fine_recall_macro"])[0] == 1
    # coarser labels can only raise the ceiling; a hierarchy ends in the fine-grained classes
    c = by["best_possible_accuracy_dups_kept"]
    assert c["wide"] >= c["current"] >= c["none"] and c["hierarchical"] == c["none"]

    results = resolve_path(config["paths"]["results_dir"])
    assert not list(results.glob("feature_ranking_*none*")) and not list(results.glob("feature_ranking_*pooled*"))  # scratch only
    assert list((results / "diagnostics").glob("feature_ranking_*"))
    metrics_dir = get_metrics_dir(config)
    # synthetic data carries the 8 extra columns -> full pool -> "_48f"-tagged outputs; the confusion matrices are written too
    assert (metrics_dir / "label_scheme_comparison_48f.csv").exists() and (metrics_dir / "label_scheme_comparison_pooled_48f.csv").exists()
    assert (metrics_dir / "confusion_matrix_48_pooled_random_none_48f.csv").exists()
    text = write_label_scheme_summary(out, pooled, metrics_dir / "label_scheme_summary.md")
    assert "the choice of scheme is the team's" in text and "NOT comparable" in text
