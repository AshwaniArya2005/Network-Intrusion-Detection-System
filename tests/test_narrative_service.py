"""Task 5.5: training saves the class reference and the temperature; the dashboard service serves both narrative styles from the same saved model."""
import copy

import pandas as pd
import pytest

from dashboard.backend.prediction_service import PredictionService
from pipelines.run_tier_study import prepare
from pipelines.run_xai_study import LABEL_COLUMNS, train_and_save
from src.utils.config_loader import load_config, load_feature_sets


def test_service_serves_both_styles_from_the_same_saved_model(tmp_path):
    cfg = load_config()
    cfg["paths"].update(unsw_train=str(tmp_path / "m1.csv"), unsw_test=str(tmp_path / "m2.csv"), cic_file=str(tmp_path / "m3.csv"), models_dir=str(tmp_path / "models"),
                        results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["data"]["synthetic_fallback_rows"] = 3000
    cfg["model"]["params"] = {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["tier_study"].update(block_size=100, buffer=20)
    cfg["feature_selection"]["pool"] = "base"
    cfg, sets, splits = prepare(cfg, load_feature_sets(), "base", "xgboost", 42)
    _, _, service_cfg = train_and_save(cfg, sets, splits, list(sets["feature_pool"]), tmp_path / "scratch")
    model_dir = tmp_path / "scratch" / "xgboost"
    reference_files, calibration_files = list(model_dir.glob("class_reference_40*.npz")), list(model_dir.glob("calibration_40*.json"))
    assert len(reference_files) == 1 and len(calibration_files) == 1                       # named like the model files (the scheme / variant tag is part of the name)
    rows = pd.concat([splits.test, splits.unknown], ignore_index=True).sample(30, random_state=0)
    df = rows.drop(columns=[c for c in LABEL_COLUMNS if c in rows.columns]).reset_index(drop=True)

    assert service_cfg["narrative"]["style"] == "classic"                                  # the default does not change
    classic = PredictionService(service_cfg).predict(df)
    relative_cfg = copy.deepcopy(service_cfg)
    relative_cfg["narrative"]["style"] = "class_relative"
    relative = PredictionService(relative_cfg).predict(df)
    assert all("calibrated_confidence" not in r for r in classic) and all(0 <= r["calibrated_confidence"] <= 1 for r in relative)
    assert [r["prediction"] for r in classic] == [r["prediction"] for r in relative] and [r["confidence"] for r in classic] == [r["confidence"] for r in relative]
    assert all("Calibrated estimate" in r["narrative"] for r in relative) and not any("Calibrated" in r["narrative"] for r in classic)
    assert any("of all flows" in r["narrative"] for r in relative)

    reference_files[0].unlink()
    with pytest.raises(FileNotFoundError):
        PredictionService(relative_cfg)                                                      # an explicit error, not a silent fall back to classic
