"""Task 6 runner on small synthetic data: every step, and the leak-free properties of the splits."""
import numpy as np
import pandas as pd
import pytest

from pipelines import run_cross_dataset_study as rcs
from src.data_loader import load_cic, load_unsw
from src.evaluation import cross_dataset_protocol as cdp

SMALL = rcs.Settings(block=100, buffer=20, source_cap=1200, pool_cap=300, ks=(20, 60), eval_thin=0.5, thin_above=10**9, top_k=6, n_random=2, draws=2, seeds=(42,), min_type_rows=5)


@pytest.fixture(scope="module")
def domains(tmp_path_factory):
    d = tmp_path_factory.mktemp("data")
    unsw = load_unsw(d / "no_train.csv", d / "no_test.csv", synthetic_rows=4000)
    cic = load_cic(d / "no_cic.csv", synthetic_rows=4000)
    return {"UNSW": rcs.make_domain("UNSW", unsw), "CIC": rcs.make_domain("CIC", cic)}


def test_domains_have_the_common_features_labels_and_attack_types(domains):
    for dom in domains.values():
        assert dom.X.shape[1] == 14 and set(np.unique(dom.y)) == {0, 1} and len(dom.attack) == len(dom.y) and np.isfinite(dom.X).all()
    assert "Normal" in set(domains["UNSW"].attack) and "Normal" in set(domains["CIC"].attack)


def test_bundle_splits_are_block_disjoint_and_the_threshold_comes_from_the_validation_blocks(domains):
    b = rcs.build_bundle(domains["UNSW"], 42, SMALL)
    sets = [set(b.fit_pos.tolist()), set(b.val_pos.tolist()), set(b.eval_pos.tolist())]
    assert not sets[0] & sets[1] and not sets[0] & sets[2] and not sets[1] & sets[2]
    assert set(b.fit_pos.tolist()) | set(b.val_pos.tolist()) <= set(b.train_pos.tolist())
    assert min(np.abs(x - b.eval_pos).min() for x in b.train_pos[::7]) > SMALL.buffer             # no train row within 200 positions of an evaluation row
    assert b.threshold is not None and 0 < b.threshold < 1 and set(b.importance.index) == set(cdp.COMMON_FEATURES)


def test_zero_shot_step_reports_every_method_and_the_stable_versus_random_sets(domains):
    t = rcs.run_zero_shot(domains, SMALL)
    runs = t["runs"]
    assert set(runs["method"]) == {"within_dataset_reference", "common_all", "source_only", "stable", "random"} and set(runs["direction"]) == {"UNSW_to_CIC", "CIC_to_UNSW"}
    assert runs[runs["method"] == "random"].groupby("direction").size().eq(SMALL.n_random).all()
    stable = runs[runs["method"] == "stable"]
    assert stable["access"].str.contains("not zero-shot").all() and runs[runs["method"] == "common_all"]["access"].eq("zero-shot").all()
    for sub, g in runs[runs["method"] == "random"].groupby(["direction", "seed"]):
        assert g["n_features"].nunique() == 1                                                       # the random subsets have one size per seed and direction
    assert {"auroc", "balanced_accuracy", "fpr_at_threshold", "detection_at_threshold", "fpr_at_95_threshold_free", "predicted_attack_share", "degenerate"} <= set(runs.columns)
    assert len(t["types"]) > 0 and set(t["block_mix"]["dataset"]) == {"UNSW", "CIC"} and (t["block_mix"]["rows"] <= SMALL.block).all()
    assert (t["eval_mix"]["evaluation_rows"] > 0).all()


def test_diagnostic_step_counts_flipped_and_absent_features_and_importance_agreement(domains):
    t = rcs.run_diagnostic(domains, SMALL)
    u = t["univariate"]
    assert len(u) == 14 and {"UNSW", "CIC", "agree", "absent_in_either", "flipped"} <= set(u.columns)
    assert not (u["flipped"] & u["absent_in_either"]).any() and not (u["flipped"] & u["agree"]).any()
    assert -1 <= t["importance_agreement"]["spearman_importance"].iloc[0] <= 1


def test_align_step_runs_every_transductive_variant(domains):
    runs = rcs.run_align(domains, SMALL)["runs"]
    assert set(runs["method"]) == {"per_dataset_standardisation", "quantile_mapping", "drop_top3_shifted", "drop_top5_shifted", "quantile_mapping_drop_top3"}
    assert runs["access"].eq("transductive").all() and runs[runs["method"] == "drop_top5_shifted"]["n_features"].eq(9).all()


@pytest.mark.parametrize("direction", ["UNSW_to_CIC", "CIC_to_UNSW"])
def test_fewshot_step_has_baseline_reference_and_target_only_control_next_to_every_adapted_row(domains, direction):
    runs = rcs.run_fewshot(domains, direction, SMALL)["runs"]
    assert {"zero_shot", "within_dataset_reference", "source+target", "target_only"} <= set(runs["method"])
    adapted = runs[runs["method"].isin(["source+target", "target_only"])]
    assert set(adapted["k"]) == set(SMALL.ks) and set(adapted["strategy"]) == {"random", "diverse"} and adapted["access"].str.contains("few-shot").all()
    for (draw, strategy, k), g in adapted.groupby(["draw", "strategy", "k"]):
        assert set(g["method"]) == {"source+target", "target_only"} and g["n_eval"].nunique() == 1          # both models are scored on the same rows
        assert (runs[(runs["draw"] == draw) & (runs["method"] == "zero_shot")]["n_eval"] == g["n_eval"].iloc[0]).all()      # and so is the zero-shot baseline
    assert runs[runs["method"] == "zero_shot"]["access"].eq("zero-shot").all()
    assert adapted["n_fit"].add(adapted["n_threshold"]).eq(adapted["k"]).all()                              # half the labelled rows fit, the other half choose the threshold


def test_adaptation_rows_are_never_evaluated(domains):
    """Re-derive one draw's split: the candidate blocks and the evaluation blocks are disjoint with a gap, so no labelled row can be an evaluation row."""
    tgt = domains["CIC"]
    cand, ev = cdp.split_positions(np.arange(len(tgt.y)), SMALL.adapt_share, 100 * 42 + 0, SMALL.block, SMALL.buffer)
    assert not set(cand.tolist()) & set(ev.tolist()) and min(np.abs(c - ev).min() for c in cand[::11]) > SMALL.buffer
    assert rcs.select_pool("random", np.random.rand(50, 3), 10, 0).shape == (10,) and rcs.select_pool("diverse", np.random.rand(50, 3), 10, 0).shape == (10,)
    with pytest.raises(ValueError):
        rcs.select_pool("bogus", np.random.rand(5, 2), 2, 0)


def test_summary_readings_by_hand():
    from scripts.cross_dataset_summary import paired_interval, source_helps, stable_vs_random, success_k
    rows = []
    for seed in (42, 43, 44, 45, 46):
        rows.append({"direction": "d", "seed": seed, "method": "stable", "auroc": 0.60 + 0.01 * (seed - 42)})
        rows += [{"direction": "d", "seed": seed, "method": "random", "auroc": a} for a in (0.50, 0.52, 0.54)]
    r = stable_vs_random(pd.DataFrame(rows), "d")
    assert r["better_in"] == 5 and r["stable_beats_random"] is True and r["mean_difference"] == pytest.approx(0.60 + 0.02 - 0.52)
    worse = pd.DataFrame(rows).assign(auroc=lambda d: np.where(d["method"] == "stable", 0.51, d["auroc"]))
    assert stable_vs_random(worse, "d")["stable_beats_random"] is False                              # 0.51 against a random mean of 0.52
    mean, lo, hi = paired_interval(pd.Series([0.1, 0.2, 0.3]))
    assert mean == pytest.approx(0.2) and lo < 0.2 < hi
    curve = pd.DataFrame({"k": [100] * 2 + [500] * 2, "fpr_at_threshold": [0.4, 0.5, 0.10, 0.12], "detection_at_threshold": [0.95, 0.95, 0.93, 0.92], "balanced_accuracy_unranked": [0.6, 0.6, 0.7, 0.7]})
    assert success_k(curve, reference_balanced=0.95) == {"fpr_detection": 500, "balanced_accuracy": None}                   # 0.70 is not within 0.05 of 0.95
    assert success_k(curve.assign(fpr_at_threshold=0.5), reference_balanced=0.95) == {"fpr_detection": None, "balanced_accuracy": None}
    assert success_k(curve.assign(fpr_at_threshold=0.5, balanced_accuracy_unranked=[0.6, 0.6, 0.92, 0.92]), reference_balanced=0.95) == {"fpr_detection": None, "balanced_accuracy": 500}
    runs = pd.DataFrame([{"seed": s, "draw": 0, "method": m, "fpr_at_threshold": f} for s, (a, b) in enumerate([(0.1, 0.3), (0.12, 0.35), (0.11, 0.28), (0.13, 0.31)]) for m, f in (("source+target", a), ("target_only", b))])
    h = source_helps(runs)
    assert h["pairs"] == 4 and h["share_favouring_source"] == 1.0 and h["source_helps"] is True and h["mean_difference"] < 0
