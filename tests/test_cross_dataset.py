"""Cross-dataset study: one train-fitted preprocessor per direction, CIC duration in seconds."""
from __future__ import annotations

import pandas as pd

import numpy as np

from src.data_loader import load_cic, make_synthetic_cic, make_synthetic_unsw, stratified_subsample
from src.evaluation import cross_dataset
from src.preprocessing import Preprocessor

FEATURES = ["dur", "spkts", "dpkts", "sbytes", "dbytes", "rate", "smean", "dmean"]


def test_load_cic_converts_duration_microseconds_to_seconds(tmp_path):
    path = tmp_path / "cic.csv"
    make_synthetic_cic(n_rows=50).assign(**{"Flow Duration": 2_000_000.0}).to_csv(path, index=False)
    assert (load_cic(path)["dur"] == 2.0).all()


def test_test_set_is_scaled_with_the_train_fitted_scaler(monkeypatch):
    """Each direction must fit ONE preprocessor on the train dataset and transform both
    datasets with it. The old code fit a separate preprocessor per dataset, so the test set
    was scaled with its own statistics."""
    unsw = make_synthetic_unsw(n_rows=400, seed=1)
    cic = load_cic("missing.csv", synthetic_rows=400)  # synthetic fallback, remapped + unit-converted
    calls = []

    class Recording(Preprocessor):
        def fit(self, df):
            self.fit_df = df
            return super().fit(df)

        def transform(self, df):
            calls.append((self.fit_df, df))
            return super().transform(df)

    monkeypatch.setattr(cross_dataset, "Preprocessor", Recording)
    result = cross_dataset.run_cross_dataset_study(unsw, cic, FEATURES, "xgboost",
                                                    {"n_estimators": 5, "max_depth": 2}, top_k=6, importance_samples=50)

    assert len(result) == 8  # 2 within-dataset references + 3 strategies x 2 directions
    assert any(fit is unsw and test is cic for fit, test in calls)
    assert any(fit is cic and test is unsw for fit, test in calls)


def test_scaled_test_data_keeps_the_unit_mismatch_visible():
    """Fit on UNSW-like seconds, transform data 1e6x larger: z-scores must be huge, not ~N(0,1)."""
    unsw = make_synthetic_unsw(n_rows=300, seed=2)
    pre = Preprocessor(feature_list=["dur", "rate"], target_column="label").fit(unsw)
    scaled = unsw.assign(dur=unsw["dur"] * 1e6)
    X, _ = pre.transform(scaled)
    assert pd.Series(X[:, 0]).abs().mean() > 1000


def test_imbalanced_training_data_does_not_yield_a_constant_predictor():
    """CIC is ~80% benign: without balanced weights the model predicted "benign" for everything
    (predicted attack share 0, accuracy = benign share). Rows now carry the share so that is visible."""
    rng = np.random.default_rng(0)
    n = 4000
    y = (rng.random(n) < 0.04).astype(int)
    df = pd.DataFrame({"dur": rng.normal(0, 1, n) + y * 0.8, "rate": rng.normal(0, 1, n) + y * 0.8, "label": y})
    out = cross_dataset._train_eval("xgboost", {"n_estimators": 20, "max_depth": 3}, ["dur", "rate"], df, df)
    assert 0 < out["predicted_attack_share"] < 1 and not out["degenerate"]
    assert out["balanced_accuracy"] > 0.6


def test_study_marks_constant_predictions_degenerate(monkeypatch):
    monkeypatch.setattr(cross_dataset, "_train_eval",
                        lambda *a, **k: {"accuracy": 0.5, "predicted_attack_share": 0.0, "degenerate": True})
    monkeypatch.setattr(cross_dataset, "_importance", lambda *a, **k: pd.Series({"dur": 2.0, "rate": 1.0}))
    tiny = pd.DataFrame({"dur": range(20), "rate": range(20), "label": [0, 1] * 10})
    out = cross_dataset.run_cross_dataset_study(tiny, tiny, ["dur", "rate"], "xgboost", {}, top_k=2)
    assert out["degenerate"].all()


def test_stratified_subsample_keeps_class_shares_and_is_seeded():
    df = pd.DataFrame({"attack_cat": ["a"] * 900 + ["b"] * 90 + ["c"] * 10, "x": range(1000)})
    sub = stratified_subsample(df, 100, seed=1)
    assert 95 <= len(sub) <= 105 and set(sub["attack_cat"]) == {"a", "b", "c"}
    assert sub.equals(stratified_subsample(df, 100, seed=1))


def test_near_constant_predictions_are_flagged_degenerate():
    rng = np.random.default_rng(0)
    train = pd.DataFrame({"dur": rng.normal(0, 1, 2000), "rate": rng.normal(0, 1, 2000)})
    train["label"] = (train["dur"] + train["rate"] > 0.5).astype(int)
    shifted = train.assign(dur=train["dur"] - 50, rate=train["rate"] - 50)  # everything looks benign
    out = cross_dataset._train_eval("xgboost", {"n_estimators": 10, "max_depth": 3}, ["dur", "rate"], train, shifted)
    assert out["predicted_attack_share"] < 0.01 and out["degenerate"]


def _shifted_pair(shift: float, n: int = 3000):
    rng = np.random.default_rng(0)

    def make(offset):
        y = (rng.random(n) < 0.3).astype(int)
        return pd.DataFrame({"dur": rng.normal(0, 1, n) + y * 1.5 + offset, "rate": rng.normal(0, 1, n) + y * 1.5 + offset,
                             "label": y})
    return make(0.0), make(shift)


def test_identical_distributions_transfer_above_chance_and_are_not_degenerate():
    a, b = _shifted_pair(0.0)
    out = cross_dataset.run_cross_dataset_study(a, b, ["dur", "rate"], "xgboost", {"n_estimators": 20, "max_depth": 3}, top_k=2,
                                                importance_samples=100)
    cross = out[out["strategy"] != "within_dataset"]
    assert not cross["degenerate"].any() and (cross["balanced_accuracy"] > 0.7).all()
    within = out[out["strategy"] == "within_dataset"]
    assert set(within["train"]) == set(within["test"]) == {"UNSW", "CIC"}  # reference rows, one per dataset


def test_degenerate_rows_get_nan_metrics_but_keep_their_flag_and_share(caplog):
    a, b = _shifted_pair(60.0)  # target dataset sits far outside the training range: all rows look benign
    out = cross_dataset.run_cross_dataset_study(a, b, ["dur", "rate"], "xgboost", {"n_estimators": 10, "max_depth": 3}, top_k=2,
                                                importance_samples=50)
    bad = out[out["degenerate"]]
    assert len(bad) > 0 and bad[["accuracy", "f1", "balanced_accuracy"]].isna().all().all()
    assert bad["predicted_attack_share"].notna().all()
    assert out[~out["degenerate"]]["f1"].notna().all()


def test_feature_shift_table_flags_the_shifted_feature():
    a, b = _shifted_pair(0.0)
    b["dur"] = b["dur"] + 100
    table = cross_dataset.feature_shift_table(a, b, ["dur", "rate"]).set_index("feature")
    assert table.loc["dur", "ks_statistic"] > 0.9 and table.loc["rate", "ks_statistic"] < 0.1
    assert {"unsw_median", "cic_iqr"} <= set(table.columns)
