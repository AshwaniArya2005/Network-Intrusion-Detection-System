"""One confusion matrix and one ROC figure per (pool, tier) of every model type, in results/plots/<model.type>/."""
import numpy as np
import pytest

import pipelines.run_tier_study as rts
from pipelines.run_tier_study import plots_dir_for, run_tier_plots, run_tiers
from src.evaluation import plots as P
from src.utils.config_loader import load_config, load_feature_sets


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg["paths"].update(unsw_train=str(tmp_path / "missing_train.csv"), unsw_test=str(tmp_path / "missing_test.csv"), cic_file=str(tmp_path / "missing_cic.csv"),
                        models_dir=str(tmp_path / "models"), results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["data"]["synthetic_fallback_rows"] = 1500
    cfg["model"]["params"] = {"n_estimators": 10, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["tier_study"]["model_params"]["random_forest"] = {"n_estimators": 10, "max_depth": 3, "n_jobs": 1}
    cfg["tier_study"].update(block_size=50, buffer=5, shap_rows=60, bootstrap=3, seeds=[1, 2])
    cfg["xai"].update(shap_background_samples=30, importance_samples=60)
    return cfg


def _predictions(n=300, seed=0):
    rng = np.random.default_rng(seed)
    names = ["Normal", "Exploits", "Overlap-Group-1"]
    y = rng.integers(0, 3, n)
    proba = rng.dirichlet(np.ones(3), n) * 0.4
    proba[np.arange(n), y] += 0.6
    return {"y_test": y, "y_pred": proba.argmax(axis=1), "y_proba": proba / proba.sum(axis=1, keepdims=True), "class_names": names}


def test_plot_file_names_carry_the_pool_the_tier_and_a_non_default_scheme(tmp_path):
    cm, roc = P.tier_plot_paths(tmp_path, 48, "30")
    assert (cm.name, roc.name) == ("confusion_matrix_pool48_tier30.png", "roc_curve_pool48_tier30.png")
    assert P.tier_plot_paths(tmp_path, 40, "30")[0].name != cm.name          # the same tier number in another pool is another feature set
    assert P.tier_plot_paths(tmp_path, 48, "30", "wide")[1].name == "roc_curve_pool48_tier30_wide.png"


def test_the_roc_figure_says_what_each_curve_is_and_gives_both_aucs(monkeypatch, tmp_path):
    seen = {}
    monkeypatch.setattr(P, "_save", lambda fig, path: seen.update(title=fig.axes[0].get_title(), labels=[t.get_text() for t in fig.axes[0].get_legend().get_texts()], path=path))
    pred = _predictions()
    P.plot_roc_curve(pred["y_test"], pred["y_proba"], pred["class_names"], tmp_path / "r.png", title_prefix="demo, 40-feature pool, tier 15: ")
    assert "attack vs Normal" in seen["title"] and "1 - P(Normal)" in seen["title"] and "one-vs-rest" in seen["title"] and "demo, 40-feature pool, tier 15" in seen["title"]
    assert any(l.startswith("Attack vs Normal") and "AUC=" in l for l in seen["labels"]) and sum("AUC=" in l for l in seen["labels"]) == 4   # attack-vs-normal + 3 classes
    from sklearn.metrics import roc_auc_score
    expected = roc_auc_score((pred["y_test"] != 0).astype(int), 1 - pred["y_proba"][:, 0])
    assert f"AUC={expected:.3f}" in seen["title"]
    P.plot_roc_curve(pred["y_test"], pred["y_proba"], ["a", "b", "c"], tmp_path / "r2.png")      # no Normal class: only the one-vs-rest curves
    assert "attack vs" not in seen["title"] and "one-vs-rest" in seen["title"]


def test_write_tier_plots_writes_both_files(tmp_path):
    cm, roc = P.write_tier_plots(_predictions(), tmp_path / "plots" / "m", 40, "15", "current", {"Overlap-Group-1": ["Analysis"]}, model_type="m")
    assert cm.exists() and roc.exists() and cm.parent == tmp_path / "plots" / "m" and cm.stat().st_size > 1000


@pytest.mark.parametrize("model_type", ["xgboost", "random_forest"])
def test_a_small_tier_grid_writes_its_plots_into_the_model_named_folder_and_reuses_saved_models(config, model_type, monkeypatch, tmp_path):
    fs = load_feature_sets()
    folder = plots_dir_for(config, model_type)
    assert folder == tmp_path / "results" / "plots" / model_type
    written = run_tier_plots(config, fs, "base", model_type, tiers=["40", "15"])
    names = sorted(p.name for p in written)
    assert names == ["confusion_matrix_pool40_tier15.png", "confusion_matrix_pool40_tier40.png", "roc_curve_pool40_tier15.png", "roc_curve_pool40_tier40.png"]
    assert all(p.parent == folder and p.exists() for p in written)
    assert not (tmp_path / "results" / "plots" / ("random_forest" if model_type == "xgboost" else "xgboost")).exists()      # nothing in another model's folder
    saved = sorted(f.name for f in (tmp_path / "models" / model_type).iterdir())
    assert any(f.startswith(f"{model_type}_15_closed_blockval_40f") for f in saved) and "preprocessor_40_blockval_40f.pkl" in saved
    trained = []
    real = rts.train_and_evaluate
    monkeypatch.setattr(rts, "train_and_evaluate", lambda *a, **k: trained.append(a[2]) or real(*a, **k))
    again = run_tier_plots(config, fs, "base", model_type, tiers=["40", "15"])
    assert not trained and len(again) == 4                                       # the second run loaded the saved models, nothing was trained
    run_tier_plots(config, fs, "base", model_type, tiers=["30"])
    assert trained == ["30"]                                                      # only the missing tier was trained


def test_the_tiers_part_plots_only_the_declared_seed(config, monkeypatch, tmp_path):
    fs = load_feature_sets()
    calls = []
    real = rts.write_tier_plots
    monkeypatch.setattr(rts, "write_tier_plots", lambda pred, d, n, tier, *a, **k: calls.append((n, tier)) or real(pred, d, n, tier, *a, **k))
    run_tiers(config, fs, "base", "xgboost", tiers=["15"], with_shap=False, plots_dir=plots_dir_for(config, "xgboost"))
    assert calls == [(40, "15")]                                                  # seeds [1, 2]: only the first (the declared seed) is plotted
    assert (plots_dir_for(config, "xgboost") / "roc_curve_pool40_tier15.png").exists()
