"""Pipelines end-to-end on small synthetic data: splits, feature ranking, open-set threshold
selection, experiment grid, stability study. Nothing here touches data/raw, models_saved or results."""
from __future__ import annotations

import copy
import io

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


def test_select_attack_threshold_and_rates_by_hand():
    from src.evaluation.metrics import attack_rates, select_attack_threshold
    is_attack = np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=bool)
    score = np.array([0.9, 0.8, 0.6, 0.3, 0.7, 0.4, 0.2, 0.1])
    # 75% detection needs the third attack (0.6); the 0.7 normal outranks it -> FPR 1/4
    t = select_attack_threshold(is_attack, score, target_detection=0.75)
    assert t == 0.6 and attack_rates(is_attack, score, t) == (0.75, 0.25)
    # 50% detection is reached at 0.8, where no normal flow scores that high: FPR 0
    t = select_attack_threshold(is_attack, score, target_detection=0.5)
    assert t == 0.8 and attack_rates(is_attack, score, t) == (0.5, 0.0)
    # FPR budget 25% (one of four normals): the 0.7 normal is allowed and the next one enters only at 0.4,
    # so the lowest admissible threshold is 0.6 (detection .75); a 50% budget also admits the 0.4 normal -> 0.3 (detection 1)
    t = select_attack_threshold(is_attack, score, target_fpr=0.25)
    assert t == 0.6 and attack_rates(is_attack, score, t) == (0.75, 0.25)
    t = select_attack_threshold(is_attack, score, target_fpr=0.5)
    assert t == 0.3 and attack_rates(is_attack, score, t) == (1.0, 0.5)
    with pytest.raises(ValueError):
        select_attack_threshold(is_attack, score)
    with pytest.raises(ValueError):
        select_attack_threshold(is_attack, score, target_detection=0.9, target_fpr=0.1)


def test_operating_points_are_chosen_on_validation_and_reported_on_both(config, feature_sets, splits):
    from pipelines.run_operating_point import operating_points
    pred = {}
    train_and_evaluate(config, feature_sets, "15", False, splits, save_artifacts=False, predictions_out=pred)
    rows = {r["rule"]: r for r in operating_points(pred, "Normal")}
    assert set(rows) == {"argmax", "det95", "fpr10"}
    assert rows["det95"]["val_detection"] >= 0.95 and rows["fpr10"]["val_fpr"] <= 0.10  # the targets hold on validation
    for r in rows.values():
        assert abs(r["fpr_gap"] - (r["test_fpr"] - r["val_fpr"])) < 1e-3


def test_sample_params_is_seeded_and_stays_inside_the_space(config):
    from pipelines.tune_xgboost import sample_params
    space = config["tuning"]["space"]
    a = [sample_params(space, np.random.default_rng(7)) for _ in range(2)]
    assert a[0] == a[1]  # same seed, same draw
    rng = np.random.default_rng(0)
    for _ in range(200):
        p = sample_params(space, rng)
        assert 3 <= p["max_depth"] <= 10 and 0.03 <= p["learning_rate"] <= 0.3 and 0.0 <= p["class_weight_power"] <= 1.0
        assert p["min_child_weight"] in space["min_child_weight"]["choice"] and p["reg_alpha"] in space["reg_alpha"]["choice"]
        assert 0.6 <= p["subsample"] <= 1.0 and 0.5 <= p["colsample_bytree"] <= 1.0 and 0.5 <= p["reg_lambda"] <= 20.0


def test_class_weight_power_changes_the_weights():
    from src.preprocessing import balanced_sample_weight
    y = np.array([0] * 90 + [1] * 10)
    assert np.allclose(balanced_sample_weight(y, 0.0), 1.0)                       # unweighted
    w1, w05 = balanced_sample_weight(y, 1.0), balanced_sample_weight(y)           # default power is 0.5
    assert np.allclose(w05, w1 ** 0.5) and w1[-1] / w1[0] == 9.0                  # fully balanced: 90/10


def test_tune_pool_uses_validation_only_and_writes_search_and_selection(config, feature_sets):
    import json
    from pipelines.tune_xgboost import OBJECTIVES, load_tuned, tune_pool
    config["tuning"].update(n_trials=3, max_estimators=30, early_stopping_rounds=5)
    config["feature_selection"]["pool"] = "base"
    trials = tune_pool(config, feature_sets, "base")
    d = rae.get_metrics_dir(config)
    assert len(trials) == 4 and trials["is_default"].sum() == 1  # 3 budgeted trials + the default reference
    assert (d / "hyperparameter_search_40f.csv").exists()
    saved = json.loads((d / "tuned_params_40f.json").read_text())
    search = trials[~trials["is_default"]]
    for obj, col in OBJECTIVES.items():
        assert saved[obj]["trial"] == int(search.loc[search[col].idxmax(), "trial"])      # best by that validation metric
        params, power = load_tuned(config, "40f", obj)
        assert params["n_estimators"] == int(search.loc[search[col].idxmax(), "best_iteration"]) + 1
        assert 0.0 <= power <= 1.0
    assert saved["n_trials"] == 3 and "validation mlogloss" in saved["early_stopping"]


def test_headline_runner_can_use_tuned_parameters_and_tags_its_files(config, feature_sets):
    from pipelines.run_headline_seeds import output_stem, run_headline_seeds
    from pipelines.tune_xgboost import tune_pool
    config["tuning"].update(n_trials=2, max_estimators=20, early_stopping_rounds=5)
    config["experiments"]["headline_seeds"] = [1]
    tune_pool(config, feature_sets, "base")
    seeds_df, _ = run_headline_seeds(config, feature_sets, pools=("base",), tuned="f1", protocols=("official",))
    assert len(seeds_df) == 1 and output_stem("f1", ("official",)) == "headline_tuned_f1_official"  # both pools: no pool tag
    assert output_stem(None, ("official", "pooled_random")) == "headline" and output_stem(None, ("official", "pooled_random"), ("full_no_ttl",)) == "headline_full_no_ttl"
    d = rae.get_metrics_dir(config)
    assert (d / "headline_tuned_f1_official_base_seeds.csv").exists() and not (d / "headline_seeds.csv").exists()


def test_tuned_vs_default_table_reports_the_difference_to_the_default(config, feature_sets):
    from pipelines.run_headline_seeds import run_headline_seeds
    from pipelines.tune_xgboost import tune_pool
    from scripts.compare_tuned import render, tuned_vs_default
    config["tuning"].update(n_trials=2, max_estimators=20, early_stopping_rounds=5)
    config["experiments"]["headline_seeds"] = [1, 2]
    for pool in ("base", "full"):
        tune_pool(config, feature_sets, pool)
    run_headline_seeds(config, feature_sets)                                                  # default, both pools
    for objective in ("f1", "auc"):
        run_headline_seeds(config, feature_sets, tuned=objective, protocols=("official",))   # tuned, both pools
    df = tuned_vs_default(rae.get_metrics_dir(config), ["base", "full"], ["f1", "auc"])
    assert list(df["hyperparameters"]) == ["default", "tuned_f1", "tuned_auc"] * 2
    base = df[df["pool"] == "base"].set_index("hyperparameters")
    assert abs(base.loc["tuned_f1", "accuracy_vs_default"] - round(base.loc["tuned_f1", "accuracy_mean"] - base.loc["default", "accuracy_mean"], 4)) < 1e-9
    assert "tuned_f1" in render(df) and "(" in render(df)


def test_confusion_metrics_match_sklearn_and_hand_values():
    from sklearn.metrics import accuracy_score, f1_score
    from src.evaluation.bootstrap import confusion_metrics
    rng = np.random.default_rng(3)
    y = rng.integers(0, 4, 500)
    pred = np.where(rng.random(500) < 0.7, y, rng.integers(0, 4, 500))
    cm = np.bincount(y * 4 + pred, minlength=16).reshape(4, 4)
    m = confusion_metrics(cm, normal=1, fuzzers=2)
    assert abs(m["accuracy"] - accuracy_score(y, pred)) < 1e-12 and abs(m["f1"] - f1_score(y, pred, average="macro")) < 1e-12
    normal = y == 1
    assert abs(m["false_positive_rate"] - (pred[normal] != 1).mean()) < 1e-12
    assert abs(m["detection_rate"] - (pred[~normal] != 1).mean()) < 1e-12
    assert abs(m["normal_to_Fuzzers"] - (pred[normal] == 2).mean()) < 1e-12


def test_bootstrap_is_paired_seeded_and_brackets_the_estimate():
    from src.evaluation.bootstrap import bootstrap, intervals, paired_differences
    rng = np.random.default_rng(1)
    y = rng.integers(0, 3, 400)
    good = np.where(rng.random(400) < 0.9, y, rng.integers(0, 3, 400))
    bad = np.where(rng.random(400) < 0.5, y, rng.integers(0, 3, 400))
    flags = rng.random(60) < 0.4
    models = {"a": dict(y_true=y, y_pred=good, unknown_flags=flags), "b": dict(y_true=y, y_pred=bad, unknown_flags=flags),
              "a2": dict(y_true=y, y_pred=good, unknown_flags=flags)}
    point, draws = bootstrap(models, 3, normal=0, fuzzers=1, n_boot=300, seed=5)
    again = bootstrap(models, 3, normal=0, fuzzers=1, n_boot=300, seed=5)[1]
    assert draws["a"].equals(again["a"])                                  # fixed seed -> identical draws
    ci = intervals(point, draws).query("model == 'a' and metric == 'accuracy'").iloc[0]
    assert ci["ci_low"] <= ci["estimate"] <= ci["ci_high"] and ci["ci_high"] - ci["ci_low"] < 0.08
    diff = paired_differences(point, draws, [("a", "b"), ("a", "a2")])
    acc = diff[diff["metric"] == "accuracy"].set_index("comparison")
    assert acc.loc["b - a", "difference"] < 0 and bool(acc.loc["b - a", "excludes_zero"])    # clearly worse, interval excludes 0
    assert acc.loc["a2 - a", "difference"] == 0 and acc.loc["a2 - a", "ci_low"] == acc.loc["a2 - a", "ci_high"] == 0  # identical models: paired diff is exactly 0
    with pytest.raises(ValueError):
        bootstrap({"a": models["a"], "c": dict(y_true=y[::-1], y_pred=good, unknown_flags=flags)}, 3, 0, 1, n_boot=2)


def test_run_bootstrap_writes_ci_and_paired_difference_files(config, feature_sets):
    from pipelines.run_bootstrap import run_bootstrap
    cis, diffs = run_bootstrap(config, feature_sets, pools=("base", "full"), n_boot=20, seed=1)
    d = rae.get_metrics_dir(config)
    assert (d / "bootstrap_ci_40f_48f.csv").exists() and (d / "bootstrap_paired_diff_40f_48f.csv").exists()
    assert set(cis["model"]) == {"40f", "48f"} and set(diffs["comparison"]) == {"48f - 40f"}


def test_exclude_removes_features_from_pool_ranking_model_and_shap(config, feature_sets):
    from src.utils.config_loader import apply_pool_variant, choose_pool, ranking_path, scheme_tag
    ttl = ["sttl", "dttl", "ct_state_ttl"]
    config["experiments"]["pool_variants"] = {"no_ttl": {"pool": "full", "exclude": ttl}}
    cfg = apply_pool_variant(config, "no_ttl")
    splits = load_split_data(cfg)
    cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
    # the pool: 48 - 3, tagged, with its own tier list
    assert len(sets["feature_pool"]) == 45 and not set(ttl) & set(sets["feature_pool"])
    assert scheme_tag(cfg) == "_45f" and cfg["experiments"]["feature_sets"][0] == "45"
    # the ranking never contains them
    generate_feature_ranking(cfg, sets, splits.train)
    ranking = pd.read_csv(ranking_path(cfg))["feature"].tolist()
    assert len(ranking) == 45 and not set(ttl) & set(ranking) and ranking_path(cfg).name.endswith("_45f.csv")
    # nor the model's feature list or saved preprocessor
    pre_cols = rae.Preprocessor(feature_list=get_active_features(cfg, sets, "45"), target_column=cfg["data"]["target_column"]).fit(splits.train).feature_list
    assert len(pre_cols) == 45 and not set(ttl) & set(pre_cols)
    result = train_and_evaluate(cfg, sets, "45", False, splits, save_artifacts=True)
    saved = joblib.load(rae.resolve_path(cfg["paths"]["models_dir"]) / "xgboost" / "preprocessor_45_45f.pkl")
    assert result["n_features"] == 45 and not set(ttl) & set(saved.metadata["features"])
    # nor the SHAP output
    importance = rae._fit_importance(cfg, get_active_features(cfg, sets, "45"), splits.train)
    assert len(importance) == 45 and not set(ttl) & set(importance.index)
    # the 48-pool and plain 40-pool are unaffected
    assert len(choose_pool(apply_pool_variant(config, "full"), feature_sets, splits.train.columns)[1]["feature_pool"]) == 48
    assert len(choose_pool(apply_pool_variant(config, "base"), feature_sets, splits.train.columns)[1]["feature_pool"]) == 40


def test_exclude_rejects_names_outside_the_pool_and_unknown_variants(config, feature_sets):
    from src.utils.config_loader import apply_pool_variant, choose_pool
    splits = load_split_data(config)
    bad = apply_pool_variant(config, "full")
    bad["feature_selection"]["exclude"] = ["not_a_feature"]
    with pytest.raises(ValueError, match="not in the full pool"):
        choose_pool(bad, feature_sets, splits.train.columns)
    base_with_ttl = apply_pool_variant(config, "base")
    base_with_ttl["feature_selection"]["exclude"] = ["sttl"]  # sttl exists only in the full pool
    with pytest.raises(ValueError, match="not in the base pool"):
        choose_pool(base_with_ttl, feature_sets, splits.train.columns)
    with pytest.raises(KeyError, match="Unknown pool"):
        apply_pool_variant(config, "nope")


def test_accuracy_three_numbers_combines_headline_runs_and_the_ceiling(config, feature_sets):
    from pipelines.run_headline_seeds import run_headline_seeds
    from scripts.accuracy_table import accuracy_rows, render
    config["experiments"]["headline_seeds"] = [1, 2]
    seeds_df, _ = run_headline_seeds(config, feature_sets)
    df = accuracy_rows(config, feature_sets, ["base", "full"], tuned=[])
    assert list(df["pool"]) == ["40f", "48f"] and set(df["hyperparameters"]) == {"default"}
    by = df.set_index("pool")
    assert by.loc["48f", "ceiling"] >= by.loc["40f", "ceiling"]                  # more columns can only split more vectors apart
    for label, pool in (("40f", "base"), ("48f", "full")):
        official = seeds_df[(seeds_df["pool"] == pool) & (seeds_df["split"] == "official")]["accuracy"]
        assert abs(by.loc[label, "official_mean"] - round(official.mean(), 4)) < 1e-9
        assert by.loc[label, "ceiling"] >= by.loc[label, "official_mean"] - 1e-9  # no classifier beats the ceiling (in expectation)
        assert abs(by.loc[label, "official_minus_ceiling"] - round(by.loc[label, "official_mean"] - by.loc[label, "ceiling"], 4)) < 1e-4
    assert "ceiling" in render(df) and "+/-" in render(df)


def test_pool_variant_runs_never_overwrite_the_default_headline_files_and_compare_side_by_side(config, feature_sets):
    from pipelines.run_headline_seeds import run_headline_seeds
    from scripts.compare_pools import compare
    config["experiments"]["headline_seeds"] = [1]
    config["experiments"]["pool_variants"] = {"no_ttl": {"pool": "full", "exclude": ["sttl", "dttl", "ct_state_ttl"]}}
    run_headline_seeds(config, feature_sets)                                    # base + full: headline_*.csv
    variant, _ = run_headline_seeds(config, feature_sets, pools=("no_ttl",))   # headline_no_ttl_*.csv
    d = rae.get_metrics_dir(config)
    assert set(pd.read_csv(d / "headline_seeds.csv")["pool"]) == {"base", "full"}      # untouched by the variant run
    assert set(variant["pool"]) == {"no_ttl"} and variant["n_features"].eq(45).all()
    table = compare(d, {"base": "40f", "full": "48f", "no_ttl": "45f"}, "official")
    assert list(table.columns) == ["40f", "48f", "45f"] and "accuracy" in table.index and table.notna().all().all()


def test_shift_feature_groups_partition_the_48_feature_pool():
    cfg, fsets = load_config(), load_feature_sets()
    names = [f for fs in cfg["shift"]["feature_groups"].values() for f in fs]
    assert len(names) == len(set(names)) and set(names) == set(fsets["feature_pool_full"])


def test_shift_classifier_finds_a_shifted_feature_and_is_chance_without_one():
    from scripts.characterize_shift import rank_stability, shift_classifier
    rng = np.random.default_rng(0)
    make = lambda shift: pd.DataFrame({"a": rng.normal(shift, 1, 700), "b": rng.normal(0, 1, 700), "c": rng.normal(0, 1, 700)})  # noqa: E731
    auc, importance = shift_classifier(make(0), make(2.5), ["a", "b", "c"], seed=1, shap_rows=200)
    assert auc > 0.9 and importance.idxmax() == "a" and importance["a"] > 5 * importance["b"]
    assert abs(shift_classifier(make(0), make(0), ["a", "b", "c"], seed=1)[0] - 0.5) < 0.08
    # rank agreement by hand
    v = pd.Series({"x": 4.0, "y": 3.0, "z": 2.0, "w": 1.0})
    out = rank_stability({"p": v, "q": v * 2, "r": v[::-1].set_axis(v.index)}, top=2)
    pq, pr = out[(out.a == "p") & (out.b == "q")].iloc[0], out[(out.a == "p") & (out.b == "r")].iloc[0]
    assert pq["spearman"] == 1.0 and pq["top2_jaccard"] == 1.0
    assert pr["spearman"] == -1.0 and pr["top2_jaccard"] == 0.0


def test_shift_steps_run_end_to_end_and_report_every_group(config, feature_sets):
    from scripts.characterize_shift import run_a1, run_a2, run_a3
    config["shift"].update(seeds=[1, 2, 3], shap_rows=100)
    table, summary = run_a1(config, feature_sets, "full")
    assert len(table) == 48 and set(table["group"]) == set(config["shift"]["feature_groups"]) and 0.3 < summary["auc_mean"] < 0.7
    assert summary["n_seeds"] == 3 and -1 <= summary["shap_rank_spearman_across_seeds"] <= 1
    groups = run_a2(config, feature_sets, "base", top_features=list(table["feature"].head(5)))
    assert "all_features" in set(groups["feature_set"]) and "top5_shift_ranked" in set(groups["feature_set"])
    assert "ttl" not in set(groups["feature_set"])                                  # the 40-feature pool has no TTL columns
    ablation = run_a3(config, feature_sets, "base")
    assert ablation["removed_group"].iloc[0] == "none_removed" and ablation["shift_auc_vs_all"].iloc[0] == 0
    assert set(ablation["removed_group"]) == {"none_removed", "volume_size", "rate_load", "timing", "tcp_window_loss",
                                              "protocol_state", "connection_counts"}
    removed = ablation.set_index("removed_group")
    assert (removed["n_kept"] + removed["n_removed"] == 40).all()
    d = rae.get_metrics_dir(config)
    assert (d / "shift_normal_features_48f.csv").exists() and (d / "shift_nf_groups_40f.csv").exists() and (d / "shift_group_ablation_40f.csv").exists()


def test_hierarchical_stage1_can_have_its_own_params_and_weight_exponent(tmp_path):
    from src.models.hierarchical_model import HierarchicalModel
    from src.models.model_factory import create_model, create_scheme_model
    rng = np.random.default_rng(0)
    y = rng.integers(0, 4, 800)
    X = rng.normal(size=(800, 6)) + y[:, None] * 0.7
    base = {"n_estimators": 5, "max_depth": 2, "random_state": 0, "n_jobs": 1}
    plain = create_scheme_model("xgboost", base, True, normal_index=0).fit(X, y)
    own = create_scheme_model("xgboost", base, True, normal_index=0, stage1_params={"n_estimators": 40, "max_depth": 4}, stage1_power=1.0).fit(X, y)
    assert plain.stage1.underlying_model.get_params()["n_estimators"] == 5 == plain.stage2.underlying_model.get_params()["n_estimators"]
    assert own.stage1.underlying_model.get_params()["n_estimators"] == 40 and own.stage2.underlying_model.get_params()["n_estimators"] == 5
    assert not np.allclose(plain.predict_proba(X), own.predict_proba(X))
    assert np.allclose(own.predict_proba(X).sum(axis=1), 1.0, atol=1e-5)
    own.save(str(tmp_path / "hier.json"))
    loaded = HierarchicalModel(lambda: create_model("xgboost", base), 0, make_stage1=lambda: create_model("xgboost", dict(base, n_estimators=40, max_depth=4))).load(str(tmp_path / "hier.json"))
    assert np.allclose(loaded.predict_proba(X), own.predict_proba(X), atol=1e-6)


def test_stage1_search_scores_the_binary_task_and_run_methods_labels_access(config, feature_sets):
    import json
    from pipelines.run_methods import run_methods
    from pipelines.tune_xgboost import load_tuned, tune_pool
    config["tuning"].update(n_trials=2, max_estimators=20, early_stopping_rounds=5)
    config["experiments"]["headline_seeds"] = [1, 2]
    trials = tune_pool(config, feature_sets, "base", stage1=True)
    d = rae.get_metrics_dir(config)
    assert (d / "hyperparameter_search_stage1_40f.csv").exists() and not (d / "hyperparameter_search_40f.csv").exists()
    saved = json.loads((d / "tuned_params_stage1_40f.json").read_text())
    search = trials[~trials["is_default"]]
    assert saved["f1"]["trial"] == int(search.loc[search["val_macro_f1"].idxmax(), "trial"])      # declared objective: validation macro F1
    assert load_tuned(config, "40f", "f1", stage1=True)[0]["n_estimators"] >= 1
    out = run_methods(config, feature_sets, "unit", ["flat_default", "hier_default", "hier_stage1_tuned"], pools=("base",))["40f"]
    assert set(out["method"]) == {"flat_default", "hier_default", "hier_stage1_tuned"}
    assert set(out.loc[out["method"] == "hier_default", "access"]) == {"zero-shot"}
    acc = out[(out["method"] == "flat_default") & (out["metric"] == "accuracy")].iloc[0]
    assert acc["n_seeds"] == 2 and {"det95_test_fpr", "det95_fpr_gap"} <= set(out["metric"])
    seeds_df = pd.read_csv(d / "methods_unit_40f_seeds.csv")
    assert (d / "methods_unit_40f_summary.csv").exists() and len(seeds_df) == 6
    assert "recall_Analysis" in seeds_df.columns and "recall_Overlap-Group-1" in seeds_df.columns  # 8 classes (hierarchical) and 6 (flat) side by side


def test_draw_adaptation_sample_is_stratified_reproducible_and_disjoint():
    from src.adaptation import draw_adaptation_sample
    df = pd.DataFrame({"cls": ["a"] * 600 + ["b"] * 300 + ["c"] * 90 + ["d"] * 10, "x": np.arange(1000)})
    adapt, rest = draw_adaptation_sample(df, 100, "cls", seed=3)
    assert len(adapt) == 100 and len(rest) == 900 and not set(adapt.index) & set(rest.index)
    counts = adapt["cls"].value_counts()
    assert counts["a"] == 60 and counts["b"] == 30 and counts["c"] == 9 and counts["d"] == 1       # proportional, every class present
    again, _ = draw_adaptation_sample(df, 100, "cls", seed=3)
    assert adapt.index.equals(again.index)                                                           # reproducible
    assert not adapt.index.equals(draw_adaptation_sample(df, 100, "cls", seed=4)[0].index)           # another draw differs
    tiny, _ = draw_adaptation_sample(df, 8, "cls", seed=0)
    assert len(tiny) == 8 and set(tiny["cls"]) == {"a", "b", "c", "d"}                               # the one-per-class floor, still k rows
    with pytest.raises(ValueError):
        draw_adaptation_sample(df, 0, "cls", seed=0)
    with pytest.raises(ValueError):
        draw_adaptation_sample(df, 1000, "cls", seed=0)


def test_adaptation_weights_give_the_adaptation_rows_the_requested_share():
    from src.adaptation import adaptation_weights
    w = np.array([1.0, 1.0, 2.0, 4.0, 3.0, 1.0])
    flag = np.array([False, False, False, False, True, True])
    out = adaptation_weights(w, flag, 0.5)
    assert np.allclose(out[:4], w[:4]) and abs(out[flag].sum() - out[~flag].sum()) < 1e-12           # half of the total weight
    assert abs(out[4] / out[5] - 3.0) < 1e-12                                                          # their relative weights are kept
    assert abs(adaptation_weights(w, flag, 0.2)[flag].sum() / adaptation_weights(w, flag, 0.2).sum() - 0.2) < 1e-12
    assert np.array_equal(adaptation_weights(w, np.zeros(6, bool), 0.3), w)
    with pytest.raises(ValueError):
        adaptation_weights(w, flag, 1.0)


def test_adaptation_rows_leave_the_evaluation_set_and_enter_training(config, feature_sets, splits):
    from src.adaptation import draw_adaptation_sample, with_adaptation
    adapt, remaining = draw_adaptation_sample(splits.test, 60, config["data"]["target_column"], seed=1)
    adapted = with_adaptation(splits, adapt, remaining, 0.3)
    assert len(adapted.test) == len(splits.test) - 60 and len(adapted.train) == len(splits.train) + 60
    assert int(adapted.train["adapt_flag"].sum()) == 60 and adapted.adapt_fraction == 0.3 and splits.adapt_fraction is None
    result = train_and_evaluate(config, feature_sets, "15", False, adapted, save_artifacts=False)
    assert result["n_test"] == len(splits.test) - 60 and result["n_train"] == len(splits.train) + 60


def test_run_adaptation_pool_scores_zero_shot_and_adapted_methods_on_the_same_remaining_rows(config, feature_sets):
    from pipelines.run_adaptation import run_adaptation_pool, summarise
    runs = run_adaptation_pool(config, feature_sets, "base", ks=(40,), fractions=(0.3,), runs=2)
    assert set(runs["method"]) == {"zero_shot", "thr_adapt", "retrain_f0.3"} and len(runs) == 6
    assert set(runs.loc[runs["method"] == "zero_shot", "access"]) == {"zero-shot"} and set(runs.loc[runs["method"] != "zero_shot", "access"]) == {"few-shot"}
    for _, g in runs.groupby("run"):
        assert g["n_eval"].nunique() == 1 and (g["n_adapt"] == 40).all()                              # the same remaining rows for every method
    zero, thr = (runs[runs["method"] == m].sort_values("run") for m in ("zero_shot", "thr_adapt"))
    assert np.allclose(zero["accuracy"], thr["accuracy"])                                              # threshold adaptation leaves the argmax model unchanged
    assert summarise(runs).query("method == 'zero_shot' and metric == 'accuracy'")["n_runs"].iloc[0] == 2


def test_domain_weights_favour_target_like_rows_and_never_read_labels():
    from src.adaptation import domain_importance_weights, unlabelled_shift_ranking
    rng = np.random.default_rng(0)
    frame = lambda mu, n: pd.DataFrame({"dur": np.abs(rng.normal(mu, 1, n)), "sbytes": np.abs(rng.normal(0, 1, n)), "dbytes": rng.random(n),  # noqa: E731
                                        "spkts": rng.integers(1, 9, n).astype(float), "dpkts": rng.integers(1, 9, n).astype(float),
                                        "attack_cat": rng.choice(["Normal", "Fuzzers"], n), "label": rng.integers(0, 2, n)})
    source, target = frame(0, 1500), frame(2.0, 1500)
    feats = ["dur", "sbytes", "dbytes"]
    w = domain_importance_weights(source, target, feats, clip=5, seed=1)
    assert len(w) == len(source) and abs(w.mean() - 1) < 1e-9 and w.min() >= 0
    assert np.corrcoef(w, source["dur"])[0, 1] > 0.3                      # rows that look like the target (large dur) weigh more
    shuffled = target.assign(attack_cat=rng.permutation(target["attack_cat"].to_numpy()), label=rng.permutation(target["label"].to_numpy()))
    assert np.allclose(w, domain_importance_weights(source, shuffled, feats, clip=5, seed=1))   # target labels play no part
    unclipped_max = domain_importance_weights(source, target, feats, clip=1000, seed=1).max()
    assert w.max() < unclipped_max                                         # clipping bites
    ranking = unlabelled_shift_ranking(source, target, feats)
    assert ranking.index[0] == "dur" and ranking["dur"] > 0.5 and ranking["sbytes"] < 0.1
    assert unlabelled_shift_ranking(source, shuffled, feats).equals(ranking)


def test_transductive_methods_run_with_their_access_label(config, feature_sets):
    from pipelines.run_methods import METHODS, run_methods
    config["experiments"]["headline_seeds"] = [1]
    out = run_methods(config, feature_sets, "unit_tx", ["flat_default", "domain_weights_clip5", "drop_top5_shifted"], pools=("base",))["40f"]
    access = out.drop_duplicates("method").set_index("method")["access"]
    assert access["flat_default"] == "zero-shot" and access["domain_weights_clip5"] == "transductive" == access["drop_top5_shifted"]
    used = out[out["metric"] == "n_features_used"].set_index("method")["mean"]
    assert used["flat_default"] == 40 and used["drop_top5_shifted"] == 35 and used["domain_weights_clip5"] == 40
    assert "val_macro_f1" in set(out["metric"]) and all(METHODS[m]["access"] in ("zero-shot", "transductive") for m in METHODS)


def test_final_table_assembles_every_method_with_its_access_level(tmp_path):
    from scripts.final_table import COLUMNS, render, rows_for
    def summary(rows, extra):
        return pd.DataFrame([{**extra, "metric": m, "mean": mean, "std": 0.01} for m, mean in rows])
    metrics = [(m, 0.5) for m in COLUMNS]
    pd.concat([summary(metrics, {"pool": "base", "method": m, "access": "zero-shot"}) for m in ("flat_default", "hier_default", "hier_stage1_tuned")]).to_csv(
        tmp_path / "methods_zero_shot_b1_40f_summary.csv", index=False)
    for obj in ("f1", "auc"):
        summary(metrics, {"pool": "base", "split": "official"}).to_csv(tmp_path / f"headline_tuned_{obj}_official_summary.csv", index=False)
    pd.concat([summary(metrics, {"pool": "base", "k": k, "method": m, "access": "few-shot"}) for k in (100, 500, 1000, 5000)
               for m in ("zero_shot", "thr_adapt", "retrain_f0.3", "retrain_f0.5")]).to_csv(tmp_path / "adaptation_40f_summary.csv", index=False)
    pd.concat([summary(metrics, {"pool": "base", "method": m, "access": "transductive"}) for m in ("domain_weights_clip5", "drop_top5_shifted")]).to_csv(
        tmp_path / "methods_transductive_b3_40f_summary.csv", index=False)
    pd.concat([summary(metrics, {"pool": "base", "k": k, "method": "retrain_split_f0.5", "access": "few-shot"}) for k in (1000, 5000)]).to_csv(
        tmp_path / "adaptation_40f_split_summary.csv", index=False)
    pd.concat([summary(metrics, {"pool": "base", "k": 5000, "method": "retrain_f0.5_domain5", "access": "few-shot+transductive"})]).to_csv(
        tmp_path / "adaptation_40f_domain5_summary.csv", index=False)
    df = pd.DataFrame(rows_for(tmp_path, "40f", "base"))
    assert set(df["access"]) == {"zero-shot", "few-shot", "transductive", "few-shot+transductive"}
    few = df[df["access"] == "few-shot"]
    assert set(few["k_labelled"]) == {100, 500, 1000, 5000} and "zero_shot" not in set(few["method"])   # the baseline is a row of its own
    assert len(df) == 3 + 2 + 4 * 3 + 2 + 2 + 1 and (df["accuracy_mean"] == 0.5).all()
    text = render(df)
    assert "| retrain_f0.3 |" in text and "| retrain_f0.1 |" not in text and "| domain_weights_clip5 |" in text   # the .md omits the f=0.1 rows


def test_adaptation_with_domain_weights_labels_the_combined_access_level(config, feature_sets):
    from pipelines.run_adaptation import run_adaptation_pool
    runs = run_adaptation_pool(config, feature_sets, "base", ks=(40,), fractions=(0.3,), runs=2, domain_clip=5)
    assert set(runs["method"]) == {"retrain_f0.3_domain5"} and set(runs["access"]) == {"few-shot+transductive"} and len(runs) == 2
    assert (runs["n_adapt"] == 40).all() and runs["accuracy"].between(0, 1).all()


def test_split_threshold_never_scores_the_threshold_rows_in_training(config, feature_sets):
    from pipelines.run_adaptation import run_adaptation_pool
    runs = run_adaptation_pool(config, feature_sets, "base", ks=(60,), fractions=(0.3,), runs=2, split_threshold=True)
    assert set(runs["method"]) == {"retrain_split_f0.3"} and set(runs["access"]) == {"few-shot"} and len(runs) == 2
    assert (runs["n_adapt"] == 60).all() and runs["det95_test_fpr"].between(0, 1).all() and runs["det95_test_detection"].between(0, 1).all()
    assert set(runs["threshold_source"]) == {"held-out half of the adaptation sample"}


def test_block_split_leaves_a_gap_between_adaptation_and_evaluation_rows():
    from src.neighbours import block_split
    adapt, evaluation = block_split(200, block_size=20, buffer=3, adapt_share=0.4, seed=1)
    assert not set(adapt) & set(evaluation) and len(adapt) > 0 and len(evaluation) > 0
    gaps = np.abs(adapt[:, None] - evaluation[None, :])
    assert gaps.min() >= 2 * 3 + 1                                        # buffer rows dropped on each side of every boundary
    assert 20 * 3 <= len(adapt) <= 20 * 5                                  # about 40% of the 10 blocks (minus the dropped edges)
    again = block_split(200, 20, 3, 0.4, 1)
    assert np.array_equal(adapt, again[0]) and np.array_equal(evaluation, again[1])   # reproducible
    assert not np.array_equal(block_split(200, 20, 3, 0.4, 2)[0], adapt)               # another seed, another blocks
    # an adaptation block is contiguous apart from its dropped edges
    runs = np.split(adapt, np.flatnonzero(np.diff(adapt) > 1) + 1)
    assert all(len(r) == r[-1] - r[0] + 1 for r in runs)


def test_embedding_distance_uses_the_training_scale_and_exact_categoricals():
    from src.neighbours import Embedder, exact_twin_mask, nearest_distance, twin_shares
    train = pd.DataFrame({"dur": [0.0, 1.0, 3.0, 7.0], "sbytes": [10.0, 20.0, 40.0, 80.0], "dbytes": [1.0, 1.0, 2.0, 2.0],
                          "spkts": [1.0, 2.0, 3.0, 4.0], "dpkts": [1.0, 1.0, 1.0, 1.0], "proto": ["tcp", "tcp", "udp", "udp"]})
    feats = ["dur", "proto"]
    emb = Embedder(feats).fit(train)
    sd = np.log1p(train["dur"]).std(ddof=0)
    query = pd.DataFrame({"dur": [3.0, 3.5, 3.0, 100.0], "sbytes": [40.0] * 4, "dbytes": [2.0] * 4, "spkts": [3.0] * 4, "dpkts": [1.0] * 4,
                          "proto": ["udp", "udp", "tcp", "udp"]})
    d = nearest_distance(emb.transform(query), emb.transform(train), cutoff=0.5)
    assert d[0] == 0.0                                                    # identical row
    assert abs(d[1] - (np.log1p(3.5) - np.log1p(3.0)) / sd) < 1e-9         # distance in the TRAINING standard deviations
    assert d[2] == np.inf and d[3] == np.inf                               # another protocol never matches; a far value exceeds the cutoff
    exact = exact_twin_mask(query, train, ["dur", "proto"])
    assert exact.tolist() == [True, False, False, False]
    shares = twin_shares(d, exact, thresholds=(0.1, 0.25))
    assert shares["exact_twin"] == 0.25 and shares["near_twin_0.1"] >= 0.25


def test_composition_counts_rows_by_source_file_and_share():
    from scripts.pooled_reference_composition import composition
    frame = lambda a, b: pd.DataFrame({"split": ["train"] * a + ["test"] * b})  # noqa: E731
    table = composition({"pooled": {"train": frame(60, 30), "val": frame(10, 5), "test": frame(30, 15)}, "official": {"train": frame(100, 0), "test": frame(0, 50)}})
    pooled = table[table["protocol"] == "pooled"].set_index(["part", "source_file"])
    assert pooled.loc[("train", "test"), "rows"] == 30 and pooled.loc[("train", "test"), "share_of_source_file"] == 0.6      # 30 of the 50 test-file rows
    assert pooled.loc[("train", "test"), "share_of_part"] == round(30 / 90, 4)
    off = table[table["protocol"] == "official"].set_index(["part", "source_file"])
    assert off.loc[("train", "test"), "rows"] == 0 and off.loc[("test", "test"), "share_of_source_file"] == 1.0


def test_subset_metrics_by_hand():
    from pipelines.run_leakage_checks import subset_metrics
    # classes: 0 = Normal, 1 = attack. Rows: two Normal (scores .1, .6), two attacks (scores .9, .4)
    proba = np.array([[0.9, 0.1], [0.4, 0.6], [0.1, 0.9], [0.6, 0.4]])
    y = np.array([0, 0, 1, 1])
    full = subset_metrics(proba, y, normal_index=0, threshold=0.5, mask=np.ones(4, bool), ece_bins=10)
    assert full["det95_test_fpr"] == 0.5 and full["det95_test_detection"] == 0.5 and full["accuracy"] == 0.5 and full["n_eval"] == 4
    only_first_three = subset_metrics(proba, y, 0, 0.5, np.array([True, True, True, False]), 10)
    assert only_first_three["det95_test_fpr"] == 0.5 and only_first_three["det95_test_detection"] == 1.0 and only_first_three["n_eval"] == 3
    assert np.isnan(subset_metrics(proba, y, 0, 0.5, np.array([True, True, False, False]), 10)["det95_test_fpr"])   # no attacks in the subset


def test_leakage_runs_report_twin_shares_subsets_and_block_conditions(config, feature_sets):
    from pipelines.run_leakage_checks import run_runs, summarise
    runs = run_runs(config, feature_sets, "base", ks=(40,), runs=2, block_size=60, buffer=5, adapt_share=0.4)
    cond = set(runs["condition"])
    assert {"twin_share_vs_adaptation_rows", "twin_share_vs_random_training_subset", "twin_share_vs_whole_training_set", "all_eval",
            "no_near_twin_0.1", "has_near_twin_0.1", "zero_shot_E", "within_E", "block_disjoint"} <= cond
    for _, g in runs[runs["check"] == "twins"].groupby("run"):
        sub = g[(g["method"] == "retrain_split_f0.5")].set_index("condition")["n_eval"]
        assert sub["no_near_twin_0.1"] + sub["has_near_twin_0.1"] == sub["all_eval"]            # the two subsets partition the evaluation rows
    shares = runs[runs["condition"] == "twin_share_vs_adaptation_rows"]
    assert shares["twin_exact_twin"].between(0, 1).all() and (shares["twin_near_twin_0.25"] >= shares["twin_near_twin_0.1"]).all()
    assert set(runs.loc[runs["method"] == "zero_shot", "access"]) == {"zero-shot"} and set(runs.loc[runs["method"] == "retrain_split_f0.5", "access"]) == {"few-shot"}
    assert summarise(runs).query("condition == 'block_disjoint' and metric == 'accuracy'")["n_runs"].iloc[0] == 2


def test_validation_blocks_compare_random_and_block_validation(config, feature_sets):
    from pipelines.run_leakage_checks import ordered_training_rows, run_validation_blocks
    config["data"]["val_size"] = 0.2
    assert len(ordered_training_rows(config)) > 0
    val = run_validation_blocks(config, feature_sets, "base", seeds=(1,), block_size=50, buffer=5)
    assert set(val["validation"]) == {"random_validation", "block_validation"}
    assert (val["fpr_gap"] == (val["test_fpr"] - val["val_fpr"]).round(4)).all() and (val["n_val"] > 0).all()
    blocks = val.set_index("validation")
    assert blocks.loc["block_validation", "n_train"] < len(ordered_training_rows(config))   # the gap rows leave training as well


def test_validation_file_names_never_collide_across_block_sizes():
    from pipelines.run_leakage_checks import validation_filename
    assert validation_filename("48f", 1000) == "leakage_48f_validation_blocks.csv"
    assert validation_filename("48f", 200) == "leakage_48f_validation_blocks_b200.csv"


def test_leakage_table_reads_the_original_and_the_check_files_without_inventing_rows(tmp_path):
    from scripts.leakage_table import METRICS, build, render
    def summary(rows):
        return pd.DataFrame([{**keys, "metric": m, "mean": v, "std": 0.01, "n_runs": 5} for keys, vals in rows for m, v in vals.items()])
    vals = lambda fpr: {"det95_test_fpr": fpr, "det95_test_detection": 0.95, "accuracy": 0.8, "ece": 0.05, "n_eval": 100.0}  # noqa: E731
    pd.concat([summary([({"k": k, "method": "retrain_split_f0.5"}, vals(0.09))]) for k in (1000, 5000)]).to_csv(tmp_path / "adaptation_48f_split_summary.csv", index=False)
    leak = []
    for k in (1000, 5000):
        for cond, fpr in (("all_eval", 0.09), ("no_near_twin_0.1", 0.2), ("has_near_twin_0.1", 0.05), ("within_E", 0.08), ("block_disjoint", 0.22)):
            leak.append(({"k": k, "check": "x", "condition": cond, "method": "retrain_split_f0.5", "access": "few-shot"}, vals(fpr)))
        for cond in ("all_eval", "no_near_twin_0.1", "has_near_twin_0.1", "zero_shot_E"):
            leak.append(({"k": k, "check": "x", "condition": cond, "method": "zero_shot", "access": "zero-shot"}, vals(0.25)))
    summary(leak).to_csv(tmp_path / "leakage_48f_summary.csv", index=False)
    df = build(tmp_path, {"48f": "48 features", "40f": "40 features"}, {"45f": "no ttl"}, ks=(1000, 5000))
    assert set(df["pool"]) == {"48f"}                                          # 40f and 45f files do not exist: no rows are made up
    by = df.set_index(["k_labelled", "row"])
    assert by.loc[(5000, "original Task 2.5 result (retrain_split_f0.5, random adaptation rows)"), "det95_test_fpr_mean"] == 0.09
    assert by.loc[(5000, "twins: rows with NO near twin (<= 0.1) in the adaptation set"), "det95_test_fpr_mean"] == 0.2
    assert by.loc[(5000, "blocks: adaptation rows from other blocks (neighbourhood-disjoint)"), "det95_test_fpr_mean"] == 0.22
    assert {"few-shot", "zero-shot"} <= set(df["access"]) and all(f"{m}_mean" in df.columns for m in METRICS)
    assert "0.2200 +/- 0.0100" in render(df)


def test_ct_ablation_pools_exclude_exactly_the_declared_columns():
    from src.utils.config_loader import apply_pool_variant, choose_pool
    cfg, fsets = load_config(), load_feature_sets()
    cols = fsets["feature_pool_full"]
    window = {"ct_src_dport_ltm", "ct_dst_sport_ltm", "ct_srv_src", "ct_dst_ltm", "ct_src_ltm", "ct_srv_dst", "ct_dst_src_ltm"}
    a = choose_pool(apply_pool_variant(cfg, "full_no_ct_window"), fsets, cols)[1]["feature_pool"]
    b = choose_pool(apply_pool_variant(cfg, "full_no_ct_any"), fsets, cols)[1]["feature_pool"]
    assert len(a) == 41 and set(fsets["feature_pool_full"]) - set(a) == window
    assert len(b) == 38 and {f for f in fsets["feature_pool_full"] if f.startswith("ct_")} == set(fsets["feature_pool_full"]) - set(b)
    assert "ct_state_ttl" not in b and "ct_flw_http_mthd" not in b and "ct_ftp_cmd" not in b and "sttl" in b   # every ct_* column goes, the TTL columns stay


def test_shift_auc_by_cv_reports_random_and_block_grouped_auc(config, feature_sets):
    from pipelines.run_leakage_checks import shift_auc_by_cv
    out = shift_auc_by_cv(config, feature_sets, "base", seed=1, block_size=50)
    assert 0 <= out["auc_random_cv"] <= 1 and 0 <= out["auc_block_cv"] <= 1 and out["n_train_normal"] > 0 and out["n_test_normal"] > 0


def test_block_validation_splits_leave_a_gap_and_keep_the_test_part(config, feature_sets, splits):
    from pipelines.train_pipeline import block_validation_splits, ordered_training_rows
    config["data"]["val_size"] = 0.2
    out = block_validation_splits(config, splits, seed=3, block_size=50, buffer=5)
    ordered = ordered_training_rows(config)
    assert out.test is splits.test and out.unknown is splits.unknown                                  # only train / val are rebuilt
    from src.neighbours import block_split
    val_pos, train_pos = block_split(len(ordered), 50, 5, 0.2, 3)                                    # the same positions the helper used
    assert len(out.val) == len(val_pos) and len(out.train) == len(train_pos)
    assert len(out.train) + len(out.val) < len(ordered)                                              # the gap rows leave both parts
    assert out.val["attack_cat"].tolist() == ordered.iloc[val_pos]["attack_cat"].tolist()           # validation = those file rows, in file order
    assert np.abs(val_pos[:, None] - train_pos[None, :]).min() >= 2 * 5 + 1                          # no training row within the gap of a validation row


def test_family_counts_reports_which_extra_columns_survive():
    from pipelines.run_tier_study import family_counts
    groups = load_config()["shift"]["feature_groups"]
    out = family_counts(["rate", "sttl", "ct_state_ttl", "ct_srv_src", "ct_dst_ltm", "ct_flw_http_mthd", "dur"], groups)
    assert out["n_ct_window"] == 2 and out["n_ttl"] == 2 and out["n_ct_other"] == 1                 # ct_state_ttl counts as TTL, not as "other ct_"
    assert out["ct_window_cols"] == "ct_srv_src;ct_dst_ltm" and out["ttl_cols"] == "sttl;ct_state_ttl" and out["ct_other_cols"] == "ct_flw_http_mthd"
    assert family_counts(["rate", "dur"], groups)["n_ct_window"] == 0


def test_model_config_sets_the_declared_parameters_per_model_family():
    from pipelines.run_tier_study import model_config
    base = load_config()
    xgb = model_config(copy.deepcopy(base), "xgboost", 44)
    assert xgb["model"]["type"] == "xgboost" and xgb["model"]["params"]["random_state"] == 44 and xgb["model"]["params"]["max_depth"] == 8
    rf = model_config(copy.deepcopy(base), "random_forest", 45)
    assert rf["model"]["params"] == {"n_estimators": 150, "max_depth": 10, "min_samples_leaf": 5, "n_jobs": -1, "random_state": 45}
    lr = model_config(copy.deepcopy(base), "logistic_regression", 46)
    assert lr["model"]["params"] == {"max_iter": 300, "random_state": 46} and lr["project"]["seed"] == 46
    assert base["model"]["type"] == "xgboost"                                                        # the input config is not modified


def test_shap_with_bootstrap_is_paired_deterministic_and_centred_on_the_importance():
    from pipelines.run_tier_study import shap_with_bootstrap
    from src.models.model_factory import create_model
    from src.preprocessing import Preprocessor
    df = make_synthetic_unsw(n_rows=900, seed=2)
    feats = ["rate", "sbytes", "dbytes", "dur", "spkts", "proto"]
    pre = Preprocessor(feature_list=feats, target_column="attack_cat").fit(df)
    X, y = pre.transform(df)
    out = {}
    for name in ("xgboost", "random_forest"):
        m = create_model(name, {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}).fit(X, y)
        out[name] = shap_with_bootstrap(m, pre, df, feats, n_rows=200, n_boot=30, seed=7)
    imp, boot = out["xgboost"]
    assert list(imp.index) == feats and (imp >= 0).all() and boot.shape == (30, 6)
    assert np.allclose(boot.mean(axis=0), imp.to_numpy(), rtol=0.25, atol=0.02)                      # resamples centre on the point estimate
    again = shap_with_bootstrap(create_model("xgboost", {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}).fit(X, y), pre, df, feats, 200, 30, 7)
    assert np.allclose(again[1], boot)                                                               # deterministic
    assert not np.allclose(shap_with_bootstrap(create_model("xgboost", {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}).fit(X, y), pre, df, feats, 200, 30, 8)[1], boot)
    # a second model family goes through the same path (same row count, hence the same resample indices for a given seed)
    assert out["random_forest"][1].shape == boot.shape and (out["random_forest"][0] >= 0).all()


def test_run_tiers_trains_once_per_run_and_writes_metrics_and_shap(config, feature_sets):
    from pipelines.run_tier_study import run_tiers, save
    config["tier_study"].update(block_size=50, buffer=5, shap_rows=60, bootstrap=5, seeds=[1, 2])
    runs, imps, boots = run_tiers(config, feature_sets, "base", "xgboost", tiers=["40", "15"])
    assert len(runs) == 4 and set(runs["tier"]) == {"40", "15"} and set(runs["seed"]) == {1, 2}
    assert {"det95_test_fpr", "det95_val_fpr", "n_ct_window", "n_ttl", "roc_auc_attack_vs_normal", "ece"} <= set(runs.columns)
    assert runs["pool_label"].eq("40f").all() and (runs["n_features"].isin([40, 15])).all()
    assert len(imps) == 2 * (40 + 15) and set(imps["tier"]) == {"40", "15"} and boots["15__1"].shape == (5, 15)
    assert list(boots["15__features"]) == list(imps[(imps.tier == "15") & (imps.seed == 1)]["feature"])      # bootstrap columns follow the stored feature order
    from src.utils.config_loader import resolve_path
    save(config, "xgboost", "40f", runs, imps, boots)
    d = rae.get_metrics_dir(config)
    assert (d / "tier_study_xgboost_40f_runs.csv").exists() and (d / "shap_importance_xgboost_40f.csv").exists() and (d / "shap_boot_xgboost_40f.npz").exists()
    import glob
    assert any("blockval_40f" in f for f in glob.glob(str(resolve_path(config["paths"]["feature_ranking"]).parent / "*")))  # its own ranking file


def test_tier_baselines_and_pooled_runs(config, feature_sets):
    from pipelines.run_tier_study import run_baselines, run_tiers
    config["tier_study"].update(block_size=50, buffer=5, shap_rows=60, bootstrap=3, seeds=[1, 2])
    runs, _, _ = run_tiers(config, feature_sets, "base", "xgboost", tiers=["15"], with_shap=False)
    csv_runs = pd.read_csv(io.StringIO(runs.to_csv(index=False)))                                       # as main() reads it: tier names come back as integers
    df, summary, summary_acc = run_baselines(config, feature_sets, "base", csv_runs, draws=3, tiers=["15"])
    assert set(df["ranking"]) == {"ranked", "random", "worst"} and (df["ranking"] == "random").sum() == 3
    assert {"ranked_f1", "worst_f1", "random_f1_mean", "ranked_z_vs_random", "ranked_percentile_in_random"} <= set(summary.columns) and len(summary) == 1
    assert df.loc[df["ranking"] == "ranked", "f1"].iloc[0] == round(float(runs["f1"].mean()), 4)       # the ranked row is the seed mean
    pooled, imps, _ = run_tiers(config, feature_sets, "base", "xgboost", tiers=["15"], with_shap=True, pooled=True)
    assert set(pooled["split"]) == {"pooled_random"} and "det95_test_fpr" not in pooled.columns and imps.empty


def test_tier_table_computes_the_drop_welch_z_and_the_declared_criteria():
    from scripts.tier_summary import tier_table
    rows = []
    for tier, n, f1s in (("48", 48, [0.72, 0.721, 0.719, 0.72, 0.72]), ("30", 30, [0.715, 0.716, 0.714, 0.715, 0.715]), ("15", 15, [0.68, 0.681, 0.679, 0.68, 0.68])):
        for seed, f1 in zip(range(42, 47), f1s):
            rows.append({"tier": tier, "n_features": n, "seed": seed, "f1": f1, "accuracy": f1 + 0.03, "n_ct_window": 7 if n == 48 else 0, "n_ct_other": 0, "n_ttl": 3 if n == 48 else 0})
    t = tier_table(pd.DataFrame(rows)).set_index("tier")
    assert abs(t.loc["30", "drop_f1"] - 0.005) < 1e-9 and abs(t.loc["15", "drop_f1"] - 0.04) < 1e-9 and t.loc["48", "drop_f1"] == 0
    full_std = np.std([0.72, 0.721, 0.719, 0.72, 0.72], ddof=1)
    assert bool(t.loc["30", "meets_noise"]) == (0.005 <= 2 * full_std)                                    # compared with 2 x the full pool's std
    assert t.loc["30", "meets_practical"] and not t.loc["15", "meets_practical"]                          # 0.005 <= 0.02 < 0.04
    se = np.sqrt(full_std ** 2 / 5 + np.std([0.715, 0.716, 0.714, 0.715, 0.715], ddof=1) ** 2 / 5)
    assert abs(t.loc["30", "welch_z_f1"] - round(0.005 / se, 4)) < 1e-3 and t.loc["48", "n_ct_window"] == 7


def test_operating_point_summary_for_other_pools_does_not_overwrite_the_40f_48f_table(config, feature_sets):
    from pipelines.run_operating_point import run_operating_point
    d = rae.get_metrics_dir(config)
    d.mkdir(parents=True, exist_ok=True)
    (d / "operating_point_summary.md").write_text("original table")
    config["experiments"]["pool_variants"] = {"no_ttl": {"pool": "full", "exclude": ["sttl", "dttl", "ct_state_ttl"]}}
    run_operating_point(config, feature_sets, pools=("no_ttl",), seeds=[1])
    assert (d / "operating_point_summary.md").read_text() == "original table" and (d / "operating_point_summary_45f.md").exists()


def test_stability_table_compares_tiers_per_seed_and_seeds_per_tier():
    from scripts.explanation_stability_tiers import stability_table
    feats = [f"f{i}" for i in range(12)]
    rng = np.random.default_rng(0)
    base = np.linspace(1, 0.05, 12)
    rows = []
    for tier, keep in (("12", feats), ("8", feats[:8])):
        for seed in (1, 2, 3):
            noise = rng.normal(0, 0.001, 12)
            for f, v in zip(keep, (base + noise)[: len(keep)]):
                rows.append({"tier": tier, "seed": seed, "feature": f, "importance": v})
    t = stability_table(pd.DataFrame(rows)).set_index(["comparison", "a", "b"])
    assert t.loc[("tier_pair", "12", "8"), "n_common_features"] == 8 and t.loc[("tier_pair", "12", "8"), "n"] == 3
    assert t.loc[("tier_pair", "12", "8"), "rank_correlation_mean"] > 0.99                                    # same ordering up to tiny noise
    assert t.loc[("same_tier_seeds", "12", "12"), "n"] == 3 and t.loc[("same_tier_seeds", "12", "12"), "cosine_similarity_mean"] > 0.999   # 3 seeds -> 3 pairs
