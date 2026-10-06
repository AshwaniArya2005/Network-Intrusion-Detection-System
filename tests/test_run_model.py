"""The shared one-command workflow: model-named folders, run names, the config override, the tier-study parameter fallback, the pre-flight messages, and
two model types run end to end on synthetic data without touching another model's folders."""
import logging
import sys

import pandas as pd
import pytest
import yaml

import pipelines.run_model as rm
from pipelines.run_tier_study import model_config
from src.utils.config_loader import (
    CONFIG_ENV, get_metrics_dir, get_models_dir, get_plots_dir, load_config, load_feature_sets, model_folder, require_xgboost,
)


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg["paths"].update(unsw_train=str(tmp_path / "missing_train.csv"), unsw_test=str(tmp_path / "missing_test.csv"), cic_file=str(tmp_path / "missing_cic.csv"),
                        models_dir=str(tmp_path / "models_saved"), results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["logging"]["log_file"] = str(tmp_path / "pipeline.log")
    cfg["data"]["synthetic_fallback_rows"] = 1500
    cfg["model"]["params"] = {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["experiments"].update(headline_seeds=[1, 2], feature_sets=["40", "15"], feature_sets_full=["40", "15"])
    cfg["tier_study"].update(block_size=50, buffer=5, shap_rows=60, bootstrap=3, seeds=[1, 2])
    cfg["xai"].update(shap_background_samples=30, importance_samples=60)
    return cfg


def _write(cfg, path):
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return path


def test_every_output_folder_is_named_by_the_model_and_an_optional_run_name(config):
    assert model_folder(config) == "xgboost"
    for helper, parent in ((get_metrics_dir, "metrics"), (get_plots_dir, "plots")):
        assert helper(config).parent.name == parent and helper(config).name == "xgboost" and helper(config, "random_forest").name == "random_forest"
    assert get_models_dir(config).name == "xgboost"
    config.setdefault("project", {})["run_name"] = "deep"
    assert model_folder(config) == "xgboost__deep" and model_folder(config, "random_forest") == "random_forest__deep"
    assert get_metrics_dir(config).name == get_plots_dir(config).name == get_models_dir(config).name == "xgboost__deep"


def test_the_config_can_be_replaced_by_an_environment_variable_and_the_file_loaded_is_logged(config, tmp_path, monkeypatch, caplog):
    config["model"]["type"] = "random_forest"
    path = _write(config, tmp_path / "mine.yaml")
    monkeypatch.setenv(CONFIG_ENV, str(path))
    with caplog.at_level(logging.INFO):
        assert load_config()["model"]["type"] == "random_forest"
    assert any(str(path) in r.getMessage() for r in caplog.records)
    monkeypatch.delenv(CONFIG_ENV)
    assert load_config()["model"]["type"] == "xgboost"


def test_the_tier_study_takes_model_params_for_the_configured_type_and_declared_params_for_other_families(config):
    config["model"].update(type="random_forest", params={"n_estimators": 7, "max_depth": 2})
    config["tier_study"]["model_params"] = {"random_forest": {"n_estimators": 150}, "logistic_regression": {"max_iter": 33}}
    cfg = model_config(load_copy(config), "random_forest", 5)
    assert cfg["model"]["params"] == {"n_estimators": 7, "max_depth": 2, "random_state": 5}      # model.params wins for the configured type
    assert model_config(load_copy(config), "logistic_regression", 5)["model"]["params"] == {"max_iter": 33, "random_state": 5}
    del config["tier_study"]["model_params"]                                                        # no declaration needed for the configured type
    assert model_config(load_copy(config), "random_forest", 5)["model"]["params"]["n_estimators"] == 7
    with pytest.raises(ValueError, match="No parameters declared"):
        model_config(load_copy(config), "logistic_regression", 5)


def load_copy(cfg):
    import copy
    return copy.deepcopy(cfg)


def test_xgboost_only_studies_refuse_another_model_type(config):
    require_xgboost(config, "the open-set study")
    config["model"]["type"] = "random_forest"
    with pytest.raises(SystemExit, match="XGBoost-only"):
        require_xgboost(config, "the open-set study")


def test_preflight_names_the_missing_files_the_synthetic_flag_and_the_pools_a_download_supports(config, tmp_path):
    fs = load_feature_sets()
    with pytest.raises(SystemExit, match="download_datasets.py"):
        rm.preflight(config, fs, "48")
    assert "SYNTHETIC" in rm.preflight(config, fs, "48", allow_synthetic=True)[0]
    narrow = [c for c in fs["feature_pool"] if c not in set(fs["feature_pool_full"]) - set(fs["feature_pool"])]
    pd.DataFrame(columns=narrow).to_csv(tmp_path / "missing_train.csv", index=False)           # a download without the extra official columns
    pd.DataFrame(columns=narrow).to_csv(tmp_path / "missing_test.csv", index=False)
    with pytest.raises(SystemExit, match="36-column download only supports pool 40"):
        rm.preflight(config, fs, "48")
    assert "40 only" in rm.preflight(config, fs, "40")[0]
    config["model"]["type"] = "no_such_model"
    with pytest.raises(SystemExit, match="Register a new model"):
        rm.preflight(config, fs, "40", allow_synthetic=True)


def test_existing_results_are_refused_unless_overwrite_or_a_run_name_gives_new_folders(config):
    rm.check_output_free(config, overwrite=False)                                                  # nothing there yet
    metrics = get_metrics_dir(config)
    metrics.mkdir(parents=True)
    (metrics / "old.csv").write_text("x", encoding="utf-8")
    with pytest.raises(SystemExit, match="--run-name"):
        rm.check_output_free(config, overwrite=False)
    rm.check_output_free(config, overwrite=True)
    rm.check_output_free(rm.apply_overrides(config, "second", None), overwrite=False)              # <type>__second is a different folder
    with pytest.raises(SystemExit, match="letters, digits"):
        rm.apply_overrides(config, "bad name!", None)


def _run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["run_model.py", *argv])
    rm.main()


@pytest.mark.parametrize("model_type, steps", [("random_forest", ["A", "B", "C"]), ("logistic_regression", ["A", "B"])])
def test_changing_model_type_and_params_in_the_config_creates_that_models_folders_and_leaves_another_models_untouched(config, tmp_path, monkeypatch, model_type, steps):
    config["model"].update(type=model_type, params={"n_estimators": 10, "max_depth": 3, "n_jobs": 1} if model_type == "random_forest" else {"max_iter": 100})
    other = tmp_path / "results" / "metrics" / "xgboost"                                           # a teammate's finished results
    other.mkdir(parents=True)
    (other / "headline_full_summary.csv").write_text("keep me", encoding="utf-8")
    before = (other / "headline_full_summary.csv").stat().st_mtime_ns
    path = _write(config, tmp_path / "mine.yaml")
    _run(monkeypatch, "--config", str(path), "--pool", "40", "--allow-synthetic", "--steps", *steps)
    metrics = tmp_path / "results" / "metrics" / model_type
    assert (metrics / "headline_base_summary.csv").exists() and (metrics / "run_config.yaml").exists()
    assert any(metrics.glob("tier_study_*_runs.csv")) and any(metrics.glob("tier_summary_*.csv"))
    assert any((tmp_path / "results" / "plots" / model_type).glob("confusion_matrix_*f.png")) and any((tmp_path / "models_saved" / model_type).glob(f"{model_type}_*"))
    filled = pd.read_csv(metrics / f"model_results_{model_type}.csv")
    assert set(filled["model"]) == {model_type} and filled["accuracy_mean"].astype(str).ne("not computed").any()
    assert ("C" in steps) == (metrics / f"stability_{model_type}.md").exists()
    assert (other / "headline_full_summary.csv").read_text(encoding="utf-8") == "keep me" and (other / "headline_full_summary.csv").stat().st_mtime_ns == before
    assert not (tmp_path / "results" / "plots" / "xgboost").exists() and not (tmp_path / "models_saved" / "xgboost").exists()
    with pytest.raises(SystemExit, match="already contain results"):                              # a second run does not overwrite silently
        _run(monkeypatch, "--config", str(path), "--pool", "40", "--allow-synthetic", "--steps", "A")


def test_a_run_name_writes_side_by_side_folders(config, tmp_path, monkeypatch):
    config["model"].update(type="logistic_regression", params={"max_iter": 100})
    path = _write(config, tmp_path / "mine.yaml")
    _run(monkeypatch, "--config", str(path), "--pool", "40", "--allow-synthetic", "--steps", "A", "--run-name", "short")
    _run(monkeypatch, "--config", str(path), "--pool", "40", "--allow-synthetic", "--steps", "A", "--run-name", "long")
    base = tmp_path / "results" / "metrics"
    assert (base / "logistic_regression__short" / "headline_base_summary.csv").exists() and (base / "logistic_regression__long" / "headline_base_summary.csv").exists()
    assert not (base / "logistic_regression").exists()
