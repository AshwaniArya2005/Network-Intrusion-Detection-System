"""Explanation study, step 4: the dashboard service and an independent computation from the same saved artifact must agree exactly."""
import pandas as pd
import pytest

from pipelines.run_xai_study import LABEL_COLUMNS, train_and_save
from pipelines.run_tier_study import prepare
from scripts.dashboard_end_to_end import compare, pipeline_predictions
from src.utils.config_loader import load_config, load_feature_sets


@pytest.fixture
def saved(tmp_path):
    cfg = load_config()
    cfg["paths"].update(unsw_train=str(tmp_path / "missing_train.csv"), unsw_test=str(tmp_path / "missing_test.csv"), cic_file=str(tmp_path / "missing_cic.csv"),
                        models_dir=str(tmp_path / "models"), results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["data"]["synthetic_fallback_rows"] = 3000
    cfg["model"]["params"] = {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["tier_study"].update(block_size=100, buffer=20)
    cfg["feature_selection"]["pool"] = "base"
    cfg, sets, splits = prepare(cfg, load_feature_sets(), "base", "xgboost", 42)
    _, _, service_cfg = train_and_save(cfg, sets, splits, list(sets["feature_pool"]), tmp_path / "scratch")
    rows = pd.concat([splits.test, splits.unknown], ignore_index=True).sample(40, random_state=0)
    return service_cfg, rows.drop(columns=[c for c in LABEL_COLUMNS if c in rows.columns]).reset_index(drop=True)


def test_service_and_independent_pipeline_agree_on_every_field(saved):
    from dashboard.backend.prediction_service import PredictionService
    cfg, df = saved
    api = PredictionService(cfg).predict(df)
    own = pipeline_predictions(cfg, df)
    table = compare(api, own)
    assert len(table) == 40
    assert table[["prediction_match", "confidence_match", "unknown_match", "narrative_match", "top_features_match"]].all().all()
    assert set(table["prediction"]) >= {"Normal"} and table["api_narrative"].str.contains("confidence").all()


def test_compare_flags_a_difference():
    a = [{"prediction": "DoS", "confidence": 0.9, "is_unknown": False, "narrative": "x", "shap_top_features": [{"feature": "rate", "value": 1.0}]}]
    b = [{**a[0], "narrative": "y", "confidence": 0.8}]
    row = compare(a, b).iloc[0]
    assert row["prediction_match"] and not row["narrative_match"] and not row["confidence_match"] and row["top_features_match"]
