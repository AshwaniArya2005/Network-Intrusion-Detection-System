"""Pipelines end-to-end on small synthetic data: splits, feature ranking, open-set threshold
selection, experiment grid, stability study. Nothing here touches data/raw, models_saved or results."""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
import pytest

from pipelines import run_all_experiments as rae
from pipelines.train_pipeline import generate_feature_ranking, load_split_data, train_and_evaluate
from src.data_loader import load_unsw, make_synthetic_unsw
from src.models.open_set_wrapper import select_threshold
from src.utils.config_loader import (
    get_active_features, get_random_features, get_worst_features, load_config, load_feature_sets, ranking_path,
)


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg["paths"].update(
        unsw_train=str(tmp_path / "missing_train.csv"), unsw_test=str(tmp_path / "missing_test.csv"),
        cic_file=str(tmp_path / "missing_cic.csv"), models_dir=str(tmp_path / "models"),
        results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"),
    )
    cfg["data"]["synthetic_fallback_rows"] = 1500
    cfg["model"]["params"] = {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["xai"].update(shap_background_samples=30, importance_samples=60)
    cfg["experiments"].update(run_nonredundant=True, feature_sets=["40", "15"], feature_sets_full=["40", "15"], stability_seeds=[43], random_baseline_draws=2)
    cfg["data"]["cic_max_rows"] = 800
    return cfg


@pytest.fixture
def feature_sets():
    return load_feature_sets()


@pytest.fixture
def splits(config, feature_sets):
    s = load_split_data(config)
    generate_feature_ranking(config, feature_sets, s.train)
    return s


def test_split_holds_out_zero_day_classes(config, splits):
    zero_day = set(config["data"]["unknown_attack_categories"])
    assert set(splits.unknown["attack_cat"]) <= zero_day and len(splits.unknown) > 0
    for part in (splits.train, splits.val, splits.test):
        assert not part["attack_cat"].isin(zero_day).any()
    assert len(splits.val) > 0


def _write_unsw(path, df):
    df.drop(columns=["split"], errors="ignore").to_csv(path, index=False)


def test_unsw_duplicates_dropped_and_official_split_used(config, tmp_path):
    train = make_synthetic_unsw(n_rows=800, seed=1)
    test = make_synthetic_unsw(n_rows=400, seed=2)
    train = pd.concat([train, train.head(10)], ignore_index=True)  # 10 exact duplicates inside train
    test = pd.concat([test, train.iloc[100:105]], ignore_index=True)  # 5 rows already in train
    _write_unsw(tmp_path / "train.csv", train)
    _write_unsw(tmp_path / "test.csv", test)

    df = load_unsw(tmp_path / "train.csv", tmp_path / "test.csv")
    assert (df["split"] == "train").sum() == 800 and (df["split"] == "test").sum() == 400

    config["paths"].update(unsw_train=str(tmp_path / "train.csv"), unsw_test=str(tmp_path / "test.csv"))
    config["data"]["use_official_split"] = True
    official = load_split_data(config)
    known = ~df["attack_cat"].isin(["Worms", "Shellcode"])
    assert len(official.test) == (known & (df["split"] == "test")).sum()
    assert len(official.train) + len(official.val) == (known & (df["split"] == "train")).sum()

    config["data"]["use_official_split"] = False
    pooled = load_split_data(config)
    assert abs(len(pooled.test) / (len(pooled.train) + len(pooled.val) + len(pooled.test)) - 0.2) < 0.02


def test_feature_ranking_is_generated_and_drives_feature_sets(config, feature_sets, splits):
    ranking = pd.read_csv(ranking_path(config))["feature"].tolist()
    assert sorted(ranking) == sorted(feature_sets["feature_pool"])
    assert get_active_features(config, feature_sets, "15") == ranking[:15]
    assert get_active_features(config, feature_sets, "40") == ranking

    random_15 = get_random_features(config, feature_sets, "15")
    assert len(set(random_15)) == 15 and set(random_15) <= set(ranking)
    assert random_15 == get_random_features(config, feature_sets, "15")  # deterministic
    assert random_15 != ranking[:15]
    assert random_15 != get_random_features(config, feature_sets, "15", draw=1)  # draws are independent
    assert get_worst_features(config, feature_sets, "15") == ranking[::-1][:15]


def test_ranking_source_and_missing_ranking_are_explicit(config, feature_sets, splits):
    config["feature_selection"]["ranking_source"] = "curated"
    assert get_active_features(config, feature_sets, "15") == feature_sets["feature_curated_rank"][:15]
    assert not ranking_path(config).exists()  # the curated ranking is not the mutual-info file

    config["feature_selection"]["ranking_source"] = "mutual_info"
    assert ranking_path(config).exists()
    ranking_path(config).unlink()
    with pytest.raises(FileNotFoundError):
        get_active_features(config, feature_sets, "15")  # no silent fallback to the static order

    ranking_path(config).write_text("feature,score\nrate,1\n")
    with pytest.raises(ValueError, match="does not match"):
        get_active_features(config, feature_sets, "15")


def test_select_threshold_uses_only_known_confidence():
    conf = np.linspace(0, 1, 1001)
    t = select_threshold(conf, 0.05)
    assert (conf < t).mean() <= 0.05 + 1e-9 and t == pytest.approx(0.05)


def test_open_set_threshold_is_chosen_without_the_zero_day_samples(config, feature_sets, splits):
    """The reported zero-day samples must not influence the threshold: the old code used a
    fixed 0.65 swept against them; the threshold now comes from known validation data only."""
    with_unknown = train_and_evaluate(config, feature_sets, "15", True, splits, save_artifacts=False)
    splits.unknown = splits.unknown.iloc[: len(splits.unknown) // 2]
    other_unknown = train_and_evaluate(config, feature_sets, "15", True, splits, save_artifacts=False)

    assert with_unknown["open_set_threshold"] == other_unknown["open_set_threshold"]
    assert with_unknown["open_set_threshold"] != config["open_set"]["confidence_threshold"]
    assert 0.0 <= with_unknown["unknown_auroc"] <= 1.0
    assert with_unknown["n_zero_day_samples"] != other_unknown["n_zero_day_samples"]


def test_stability_models_match_evaluated_models(config, feature_sets, splits, monkeypatch):
    """Stability-study models must be fit with the shared sample weights and explained on
    xai.importance_samples rows, not the 100-row SHAP background size."""
    seen = {}

    class SpyModel:
        def __init__(self, inner):
            self.inner = inner

        def fit(self, X, y, sample_weight=None):
            seen["sample_weight"] = sample_weight
            self.inner.fit(X, y, sample_weight=sample_weight)
            return self

        def __getattr__(self, name):
            return getattr(self.inner, name)

    class SpyExplainer:
        def __init__(self, *args, **kwargs):
            pass

        def global_importance(self, X, max_samples=None):
            seen["max_samples"] = max_samples
            return pd.Series(1.0, index=["a", "b"])

    real_create = rae.create_model
    monkeypatch.setattr(rae, "create_model", lambda *a, **k: SpyModel(real_create(*a, **k)))
    monkeypatch.setattr(rae, "SHAPExplainer", SpyExplainer)

    rae._fit_importance(config, get_active_features(config, feature_sets, "15"), splits.train)
    assert seen["sample_weight"] is not None and len(np.unique(seen["sample_weight"])) > 1
    assert seen["max_samples"] == config["xai"]["importance_samples"]


def test_run_all_writes_every_output(config, feature_sets):
    config["feature_selection"]["pool"] = "base"  # synthetic data has the 8 extra columns; base keeps the untagged file names
    out = rae.run_all(config, feature_sets)
    metrics_dir = rae.get_metrics_dir(config)

    exp = out["experiments"]
    assert len(exp) == 4  # 2 feature sets x closed/open
    assert {"recall_Normal", "f1_Normal", "detection_rate", "false_positive_rate",
            "recall_Analysis_as_Overlap-Group-1", "unknown_auroc", "open_set_threshold"} <= set(exp.columns)
    # per-tier diagnostics only for the active tier (40) unless experiments.save_per_tier_diagnostics
    assert (metrics_dir / "open_set_sweep_40.csv").exists() and (metrics_dir / "overlap_diagnostic_40.csv").exists()
    assert not (metrics_dir / "open_set_sweep_15.csv").exists() and not (metrics_dir / "overlap_diagnostic_15.csv").exists()
    sweep = pd.read_csv(metrics_dir / "open_set_sweep_40.csv")
    assert list(sweep.columns) == ["threshold", "detection_rate", "false_alarm_rate"]

    assert set(out["baselines"]["ranking"]) == {"ranked", "random", "worst"}
    summary = pd.read_csv(metrics_dir / "feature_selection_baselines_summary.csv")
    assert summary.loc[0, "n_random_draws"] == 2 and {"random_f1_mean", "random_f1_std", "worst_f1"} <= set(summary.columns)
    assert (metrics_dir / "split_summary.csv").exists()
    assert (metrics_dir / "confusion_matrix_15_pooled_random.csv").exists()  # synthetic data always splits randomly
    assert set(out["pooled_split"]["split"]) == {"pooled_random"}
    comparison = pd.read_csv(metrics_dir / "split_comparison.csv")
    assert set(comparison["split"]) == {"official", "pooled_random"} and set(comparison["feature_set"].astype(str)) == {"40", "15"}
    assert {"false_positive_rate", "recall_Normal", "fpr_at_95_detection", "train_rows_Generic", "test_rows_Generic"} <= set(comparison.columns)
    # redundancy-aware variant: separate files, default outputs untouched
    assert (metrics_dir / "experiment_results_nonredundant.csv").exists() and (metrics_dir / "experiment_results.csv").exists()
    assert len(out["nonredundant"]) == 4
    assert (rae.resolve_path(config["paths"]["models_dir"]) / "xgboost" / "preprocessor_15_nonredundant.pkl").exists()
    assert set(out["stability"]["comparison"]) == {"nested_feature_sets", "same_set_different_seed"}
    assert len(out["cross_dataset"]) == 8  # 2 within-dataset references + 3 strategies x 2 directions

    model_dir = rae.resolve_path(config["paths"]["models_dir"]) / "xgboost"
    meta = joblib.load(model_dir / "preprocessor_15.pkl").metadata
    assert meta["ranking_source"] == "mutual_info" and len(meta["features"]) == 15
    assert (model_dir / "xgboost_15_closed.json").exists() and (model_dir / "open_set_15.json").exists()


def test_fpr_at_detection_by_hand():
    from src.evaluation.metrics import fpr_at_detection

    classes = ["Fuzzers", "Normal"]
    true = np.array(["Normal"] * 4 + ["Fuzzers"] * 4)
    # attack scores 1-P(Normal): normals .1 .2 .3 .6 ; attacks .5 .7 .8 .9
    p_normal = 1 - np.array([0.1, 0.2, 0.3, 0.6, 0.5, 0.7, 0.8, 0.9])
    proba = np.column_stack([1 - p_normal, p_normal])
    out = fpr_at_detection(true, proba, classes, "Normal", targets=(0.5, 1.0))
    # 50% detection needs only the top two attacks (score >= .8): no normal flow is that high;
    # 100% needs the .5 attack, and the .6 normal outranks it -> 1 of 4 normals.
    assert out == {"fpr_at_50_detection": 0.0, "fpr_at_100_detection": 0.25}


def test_new_reporting_columns_and_val_false_unknown_gap(config, feature_sets, splits):
    config["open_set"]["target_false_unknown_rate"] = 0.05
    r = train_and_evaluate(config, feature_sets, "15", True, splits, save_artifacts=False)
    assert {"fpr_at_90_detection", "fpr_at_95_detection", "fpr_at_99_detection", "false_unknown_alarm_rate_val",
            "fine_recall_macro", "group_size_share"} <= set(r)
    assert r["fpr_at_90_detection"] <= r["fpr_at_95_detection"] <= r["fpr_at_99_detection"]
    assert r["false_unknown_alarm_rate_val"] <= 0.06  # the threshold was chosen on exactly this split


def test_evaluate_pipeline_reports_the_same_metrics_as_the_grid(config, feature_sets, splits):
    from pipelines.evaluate_pipeline import evaluate
    from src.utils.config_loader import get_dashboard_paths

    config["dashboard"]["feature_set"] = "15"
    grid_row = train_and_evaluate(config, feature_sets, "15", False, splits)
    model_path, pre_path = get_dashboard_paths(config)
    metrics = evaluate(config, model_path, pre_path, splits.test)
    for key, value in metrics.items():
        assert grid_row[key] == pytest.approx(value, nan_ok=True), key
    assert "fpr_at_95_detection" in metrics and "recall_Normal" in metrics  # the full report, not just 4 numbers


def test_summarize_baselines_significance_by_hand():
    from pipelines.run_all_experiments import summarize_baselines

    def rows(ranked, draws):
        base = {"feature_set": "20", "n_features": 20}
        return ([dict(base, ranking="ranked", f1=ranked), dict(base, ranking="worst", f1=0.5)]
                + [dict(base, ranking="random", f1=f) for f in draws])
    draws = [0.60, 0.62, 0.64]  # mean .62, std .02
    win = summarize_baselines(pd.DataFrame(rows(0.70, draws))).iloc[0]
    assert win["ranked_percentile_in_random"] == 100 and win["ranked_rank_among_draws"] == 1
    assert win["ranked_z_vs_random"] == 4.0 and win["ranked_beats_random_mean_plus_2std"]
    tie = summarize_baselines(pd.DataFrame(rows(0.63, draws))).iloc[0]
    assert tie["ranked_percentile_in_random"] == pytest.approx(66.7) and not tie["ranked_beats_random_mean_plus_2std"]


def test_ensure_feature_ranking_regenerates_only_when_training_data_changed(config, feature_sets, splits):
    from pipelines.train_pipeline import ensure_feature_ranking

    assert ensure_feature_ranking(config, feature_sets, splits.train) is False  # fixture already wrote it for this data
    assert ensure_feature_ranking(config, feature_sets, splits.train.iloc[: len(splits.train) // 2]) is True
    assert ensure_feature_ranking(config, feature_sets, splits.train.iloc[: len(splits.train) // 2]) is False
    ranking_path(config).unlink()
    assert ensure_feature_ranking(config, feature_sets, splits.train.iloc[: len(splits.train) // 2]) is True  # missing


def test_feature_set_metrics_plot_draws_numeric_tiers(tmp_path):
    """Tiers read back from a CSV are ints; the plot must still put the points on screen."""
    import matplotlib
    matplotlib.use("Agg")
    import pandas as pd
    from src.evaluation import plots

    df = pd.DataFrame({"feature_set": [15, 20, 30, 40], "n_features": [15, 20, 30, 40], "open_set": False,
                       "accuracy": [.7, .71, .72, .73], "precision": .6, "recall": .6, "f1": .6})
    seen = {}
    real_save = plots._save
    plots._save = lambda fig, path: (seen.update(x=fig.axes[0].lines[0].get_xdata().tolist(), xlim=fig.axes[0].get_xlim()),
                                     real_save(fig, path))
    try:
        plots.plot_feature_set_metrics(df, tmp_path)
    finally:
        plots._save = real_save
    # categorical (str) x-values sit at positions 0..3, inside the forced xlim; ints would sit at 15..40, off-screen
    assert all(isinstance(v, str) for v in seen["x"])


def test_confusion_matrix_tables_counts_and_row_shares():
    import numpy as np
    from src.evaluation.metrics import confusion_matrix_tables
    true = np.array(["Normal"] * 4 + ["DoS"] * 2)
    pred = np.array(["Normal", "Normal", "Fuzzers", "Fuzzers", "DoS", "Normal"])
    counts, share = confusion_matrix_tables(true, pred, ["DoS", "Fuzzers", "Normal", "Worms"])
    assert counts.loc["Normal", "Fuzzers"] == 2 and counts.loc["DoS", "Normal"] == 1
    assert counts.to_numpy().sum() == 6 and list(counts.columns) == ["DoS", "Fuzzers", "Normal", "Worms"]  # empty class kept
    assert share.loc["Normal", "Fuzzers"] == 0.5 and share.loc["Worms"].sum() == 0 and abs(share.loc["DoS"].sum() - 1) < 1e-9


def test_train_and_evaluate_writes_the_confusion_csvs(config, feature_sets, splits):
    import pandas as pd
    from src.utils.config_loader import get_metrics_dir
    train_and_evaluate(config, feature_sets, "15", False, splits, save_artifacts=False, write_confusion=True)
    d = get_metrics_dir(config)
    counts = pd.read_csv(d / f"confusion_matrix_15_{splits.name}.csv", index_col=0)
    share = pd.read_csv(d / f"confusion_matrix_15_{splits.name}_rownorm.csv", index_col=0)
    assert counts.to_numpy().sum() == len(splits.test) and list(counts.index) == list(counts.columns)
    assert abs(share.loc["Normal"].sum() - 1) < 1e-3


def test_probabilistic_metrics_by_hand():
    from src.evaluation.metrics import brier_score, expected_calibration_error, probabilistic_metrics
    classes = ["Fuzzers", "Normal", "Worms"]  # Worms has no test rows
    y = np.array([0, 0, 1, 1])
    proba = np.array([[0.9, 0.1, 0.0], [0.2, 0.8, 0.0], [0.1, 0.9, 0.0], [0.6, 0.4, 0.0]])
    out = probabilistic_metrics(y, proba, classes, ece_bins=10)
    # Fuzzers vs rest: scores .9 .2 .1 .6, positives are rows 0,1 -> 3 of 4 (pos, neg) pairs ranked right
    assert out["roc_auc_Fuzzers"] == 0.75 and out["roc_auc_Normal"] == 0.75
    assert np.isnan(out["roc_auc_Worms"]) and np.isnan(out["pr_auc_Worms"])
    assert out["roc_auc_macro"] == 0.75  # NaN class skipped
    # AP of Fuzzers: ranking by score = rows 0 (pos), 3 (neg), 1 (pos), 2 (neg) -> (1/1 + 2/3) / 2
    assert out["pr_auc_Fuzzers"] == round((1 + 2 / 3) / 2, 4)
    # attack-vs-normal: "attack" = class != Normal(=1): rows 0,1 attack; score 1-P(Normal) = .9,.2 vs .1,.6 -> AUC .75
    assert out["roc_auc_attack_vs_normal"] == 0.75
    # Brier per row (squared distance to the one-hot label): .02, 1.28, .02, .72 -> mean .51
    assert abs(brier_score(y, proba) - 0.51) < 1e-9 and out["brier"] == 0.51
    # one bin: predictions are 0,1,1,0 -> 2 of 4 correct; mean confidence (.9+.8+.9+.6)/4 = .8 -> |.5 - .8| = .3
    assert abs(expected_calibration_error(y, proba, n_bins=1) - 0.3) < 1e-9
    perfect = np.eye(3)[[0, 1, 1]]
    assert expected_calibration_error(np.array([0, 1, 1]), perfect) == 0.0 and brier_score(np.array([0, 1, 1]), perfect) == 0.0


def test_ece_matches_a_hand_computed_value():
    from src.evaluation.metrics import expected_calibration_error
    # two bins: confidences .6,.6 (1 of 2 correct: gap .1) and .9,.9 (both correct: gap .1) -> ECE = .5*.1 + .5*.1
    proba = np.array([[0.6, 0.4], [0.6, 0.4], [0.1, 0.9], [0.1, 0.9]])
    y = np.array([0, 1, 1, 1])
    assert abs(expected_calibration_error(y, proba, n_bins=10) - 0.1) < 1e-9


def test_run_headline_seeds_reports_mean_and_std_per_pool_and_protocol(config, feature_sets):
    from pipelines.run_headline_seeds import run_headline_seeds
    config["experiments"]["headline_seeds"] = [1, 2]
    seeds_df, summary = run_headline_seeds(config, feature_sets, pools=("base", "full"))
    assert len(seeds_df) == 2 * 2 * 2  # pools x protocols x seeds
    assert set(seeds_df["pool"]) == {"base", "full"} and set(seeds_df["split"]) == {"official", "pooled_random"}
    assert {"roc_auc_macro", "pr_auc_macro", "ece", "brier", "normal_to_Fuzzers"} <= set(seeds_df.columns)
    acc = summary[(summary["metric"] == "accuracy") & (summary["pool"] == "base")].iloc[0]
    vals = seeds_df.loc[(seeds_df["pool"] == "base") & (seeds_df["split"] == acc["split"]), "accuracy"]
    assert abs(acc["mean"] - round(vals.mean(), 4)) < 1e-9 and acc["n_seeds"] == 2
    d = rae.get_metrics_dir(config)
    assert (d / "headline_seeds.csv").exists() and "mean +/-" not in (d / "headline_summary.csv").read_text()
    assert "+/-" in (d / "headline_summary.md").read_text()
