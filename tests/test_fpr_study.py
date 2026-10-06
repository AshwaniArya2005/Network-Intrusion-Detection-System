"""FPR-reduction study runner (pipelines/run_fpr_study.py): metrics by hand, label hygiene of the self-training rows, and a small end-to-end run of every step."""
import numpy as np
import pandas as pd
import pytest

from pipelines import run_fpr_study as rfs
from src.utils.config_loader import load_config, load_feature_sets


@pytest.fixture
def config(tmp_path):
    cfg = load_config()
    cfg["paths"].update(unsw_train=str(tmp_path / "missing_train.csv"), unsw_test=str(tmp_path / "missing_test.csv"), cic_file=str(tmp_path / "missing_cic.csv"),
                        models_dir=str(tmp_path / "models"), results_dir=str(tmp_path / "results"), feature_ranking=str(tmp_path / "ranking_{source}.csv"))
    cfg["data"]["synthetic_fallback_rows"] = 2500
    cfg["model"]["params"] = {"n_estimators": 8, "max_depth": 3, "random_state": 0, "n_jobs": 1}
    cfg["tier_study"].update(block_size=100, buffer=20)
    cfg["feature_selection"]["pool"] = "base"
    return cfg


def test_evaluate_probabilities_by_hand():
    # classes: 0 = Normal, 1 = attack. Validation: 2 Normal, 2 attacks; test: 3 Normal, 2 attacks.
    pv = np.array([[0.9, 0.1], [0.6, 0.4], [0.3, 0.7], [0.1, 0.9]])
    yv = np.array([0, 0, 1, 1])
    pt = np.array([[0.8, 0.2], [0.55, 0.45], [0.2, 0.8], [0.35, 0.65], [0.1, 0.9]])
    yt = np.array([0, 0, 0, 1, 1])
    m = rfs.evaluate_probabilities(pv, yv, pt, yt, 0, 15)
    # 95% detection on validation needs both attacks: the threshold on 1 - P(Normal) is 0.7 (the lower attack score)
    assert m["det95_threshold"] == pytest.approx(0.7)
    assert m["det95_test_detection"] == pytest.approx(0.5)            # attack scores 0.65 and 0.9: only 0.9 reaches 0.7
    assert m["det95_test_fpr"] == pytest.approx(1 / 3)                # Normal scores 0.2, 0.45, 0.8: one reaches 0.7
    assert m["argmax_fpr"] == pytest.approx(1 / 3) and m["argmax_detection"] == pytest.approx(1.0)
    assert m["accuracy"] == pytest.approx(4 / 5)
    assert m["fpr_at_95_threshold_free"] == pytest.approx(1 / 3)      # ranked 0.9 A, 0.8 N, 0.65 A: both attacks are found after one of the three Normal flows
    explicit = rfs.evaluate_probabilities(pv, yv, pt, yt, 0, 15, threshold=0.4)       # Normal scores 0.2 / 0.45 / 0.8: two reach 0.4; both attacks do
    assert explicit["det95_threshold"] == 0.4 and explicit["det95_test_detection"] == pytest.approx(1.0) and explicit["det95_test_fpr"] == pytest.approx(2 / 3)


def test_open_set_columns_use_the_validation_quantile_only():
    pv = np.tile([[0.9, 0.1]], (100, 1)) * 1.0
    pv[:5] = [0.55, 0.45]                                              # the 5% least confident validation rows
    pt = np.tile([[0.9, 0.1]], (10, 1))
    pu = np.array([[0.5, 0.5], [0.95, 0.05]])
    m = rfs.evaluate_probabilities(pv, np.zeros(100, dtype=int), pt, np.zeros(10, dtype=int), 0, 15, proba_unknown=pu)
    assert m["open_set_detection"] == pytest.approx(0.5) and m["open_set_false_unknown_test"] == 0.0


def test_pseudo_rows_carry_the_predicted_label_and_not_the_true_one():
    frame = pd.DataFrame({"x": [1, 2, 3, 4], "label_merged": ["Normal", "Exploits", "Normal", "Fuzzers"], "attack_cat": ["Normal", "Exploits", "Normal", "Fuzzers"]})
    out = rfs.pseudo_rows(frame, np.array([0, 3]), np.array([1, 0]), ["Normal", "Fuzzers"], "label_merged", "attack_cat")
    assert out["label_merged"].tolist() == ["Fuzzers", "Normal"] and out["attack_cat"].tolist() == ["Fuzzers", "Normal"] and out["x"].tolist() == [1, 4]
    assert frame["label_merged"].tolist() == ["Normal", "Exploits", "Normal", "Fuzzers"]      # the source frame is untouched


def test_reinforcement_diagnostics_by_hand():
    proba = np.array([[0.95, 0.05], [0.05, 0.95], [0.04, 0.96], [0.6, 0.4], [0.02, 0.98]])
    truth = np.array([0, 0, 1, 0, 0])                                  # row 1 and row 4 are Normal flows with a confident attack label
    r = rfs.reinforcement(np.arange(5), proba, truth, 0, 0.9)
    assert r["pseudo_labelled"] == 4                                   # row 3 (0.6) is below tau
    assert r["pseudo_wrong_share"] == pytest.approx(2 / 4)             # rows 1 and 4 are labelled attack but are Normal
    assert r["true_normal_given_attack_pseudo_label"] == pytest.approx(2 / 4)   # four true Normal rows (0, 1, 3, 4); rows 1 and 4 get a confident attack label
    assert r["attack_pseudo_labels_that_are_normal"] == pytest.approx(2 / 3)    # attack pseudo-labels: rows 1, 2, 4; Normal among them: rows 1 and 4


def test_choose_rows_dispatches_every_strategy():
    rng = np.random.default_rng(0)
    proba, X = rng.dirichlet([1, 1, 1], size=60), rng.normal(size=(60, 4))
    for strategy in rfs.STRATEGIES:
        pick = rfs.choose_rows(strategy, proba, X, 12, 7)
        assert len(set(pick.tolist())) == 12 and pick.max() < 60
    with pytest.raises(ValueError):
        rfs.choose_rows("bogus", proba, X, 5, 0)


def test_tuned_overrides_skips_missing_searches(config):
    assert list(rfs.tuned_overrides(config, "40f")) == ["default"]    # no tuned_params files exist in the temporary results directory


def test_every_step_runs_end_to_end_on_small_data(config, monkeypatch):
    feature_sets = load_feature_sets()
    monkeypatch.setattr(rfs, "BLOCK", 100)
    monkeypatch.setattr(rfs, "BUFFER", 20)
    tuned = rfs.run_tuned(config, feature_sets, "base", seeds=(42,))
    assert set(tuned["method"]) == {"default"} and tuned["access"].eq("zero-shot").all()
    prior = rfs.run_prior(config, feature_sets, "base", seeds=(42,))
    assert list(prior["method"]) == ["default", "calibrated", "calibrated_valprior", "calibrated_em"]
    assert prior.set_index("method").loc["calibrated_em", "access"] == "transductive" and prior.set_index("method").loc["calibrated_valprior", "access"] == "zero-shot"
    em = prior[prior["method"] == "calibrated_em"].iloc[0]
    assert 0 <= em["em_l1_to_true_shares"] <= 2 and em["temperature"] > 0
    assert sum(em[c] for c in em.index if c.startswith("est_share_")) == pytest.approx(1.0)       # the diagnostic shares are never used for fitting
    selfs = rfs.run_self(config, feature_sets, "base", seeds=(42,))
    assert set(selfs["source"]) == {"validation", "test"} and sorted(selfs["round"].unique()) == [0, 1, 2]
    assert selfs[selfs["round"] == 0]["access"].eq("zero-shot").all()
    fewshot = rfs.run_fewshot(config, feature_sets, "base", runs=1, ks=(20,), strategies=("random", "entropy"))
    assert set(fewshot["method"]) == {"zero_shot", "random_k20", "entropy_k20"}
    few = fewshot[fewshot["k"] == 20]
    assert few["access"].eq("few-shot").all() and (few["n_labelled"] == 20).all()
    assert fewshot[fewshot["method"] == "zero_shot"]["n_eval"].iloc[0] == few["n_eval"].iloc[0]      # same evaluation rows for the baseline and every strategy


def test_paired_verdict_applies_the_declared_rule():
    from scripts.fpr_summary import paired_verdict, smallest_k
    seeds = [42, 43, 44, 45, 46]
    base = pd.DataFrame({"method": "default", "seed": seeds, "det95_test_fpr": [0.25] * 5, "det95_test_detection": [0.95] * 5})
    good = pd.DataFrame({"method": "good", "seed": seeds, "det95_test_fpr": [0.22, 0.23, 0.22, 0.21, 0.24], "det95_test_detection": [0.95] * 5})   # -0.028 on average, better in 5 of 5
    small = pd.DataFrame({"method": "small", "seed": seeds, "det95_test_fpr": [0.24] * 5, "det95_test_detection": [0.95] * 5})                      # -0.01: below the declared 0.02
    costly = pd.DataFrame({"method": "costly", "seed": seeds, "det95_test_fpr": [0.20] * 5, "det95_test_detection": [0.90] * 5})                      # detection 0.05 lower
    unstable = pd.DataFrame({"method": "unstable", "seed": seeds, "det95_test_fpr": [0.10, 0.10, 0.10, 0.26, 0.26], "det95_test_detection": [0.95] * 5})  # mean -0.07 but better in 3 of 5
    df = pd.concat([base, good, small, costly, unstable])
    assert paired_verdict(df, "good", "default")["clearly_beats"] is True and paired_verdict(df, "good", "default")["n_better"] == 5
    assert paired_verdict(df, "small", "default")["clearly_beats"] is False
    assert paired_verdict(df, "costly", "default")["clearly_beats"] is False
    assert paired_verdict(df, "unstable", "default")["clearly_beats"] is False and paired_verdict(df, "unstable", "default")["n_better"] == 3
    few = pd.DataFrame({"strategy": ["random"] * 4 + ["entropy"] * 2, "k": [100, 100, 500, 500, 100, 500], "det95_test_fpr": [0.3, 0.2, 0.12, 0.16, 0.3, 0.2]})
    assert smallest_k(few, "random") == 500 and smallest_k(few, "entropy") is None        # random: mean 0.25 at k=100, 0.14 at k=500; entropy never reaches 0.15


def test_combined_recipe_records_what_it_chose_and_its_access_level(config, monkeypatch):
    feature_sets = load_feature_sets()
    monkeypatch.setattr(rfs, "BLOCK", 100)
    monkeypatch.setattr(rfs, "BUFFER", 20)
    out = rfs.run_combined(config, feature_sets, "base", seeds=(42,))
    combined = out[out["method"] == "combined"].iloc[0]
    assert set(out["method"]) == {"combined", "default"}
    assert not combined["used_tuned"]                                  # no tuned_params file in the temporary directory: the default is used
    assert combined["access"] == ("transductive" if combined["used_em"] else "zero-shot")
    assert combined["temperature"] > 0


def test_block_validation_frames_can_be_concatenated_with_other_rows(config):
    from dataclasses import replace
    from pipelines.run_tier_study import prepare
    cfg, sets, splits = prepare(config, load_feature_sets(), "base", "xgboost", 42)
    marked = replace(splits, train=splits.train.copy(), val=splits.val.copy())
    for part in (marked.train, marked.val):
        part.attrs["counts_before_dedup"] = pd.DataFrame({"x": [1]})          # what load_unsw attaches to the frame it returns
    from pipelines.train_pipeline import block_validation_splits
    rebuilt = block_validation_splits(cfg, marked, 42, 100, 20)
    assert rebuilt.train.attrs == {} and rebuilt.val.attrs == {}
    pd.concat([rebuilt.train, rebuilt.val], ignore_index=True)                  # raised "truth value of a DataFrame is ambiguous" before the fix
