"""Characterise the official-split shift (diagnostic only: no model, threshold or protocol changes).

    python scripts/characterize_shift.py [--steps a1 a2 a3] [--pools full base full_no_ttl]   (default: full)

a1  Normal flows only: a classifier telling train-Normal (train + validation) from official-test-Normal. Reports its
    cross-validated AUC over `shift.seeds`, ranks the features by SHAP importance and by per-feature KS (TVD for
    categoricals), and checks the stability of those rankings across seeds and across the pools.
a2  The Normal flows the default model calls Fuzzers (NF) vs correctly predicted Normal (NN) vs true Fuzzers (TF):
    for each feature group (`shift.feature_groups`), how well a classifier using ONLY that group separates NF from NN
    and NF from TF; `resemblance` = AUC(NF vs NN) - AUC(NF vs TF), positive when NF looks more like Fuzzers.
a3  Group ablation: remove one feature group at a time and report the train-vs-test Normal AUC and the retrained
    model's Normal -> Fuzzers rate / FPR (first 3 `shift.seeds`) against the all-features reference. Groups that do
    not matter are reported too.

Writes under results/metrics/<model.type>/ (pool size in every name, e.g. _48f):
  shift_normal_features_<N>f.csv   shift_normal_summary_<N>f.csv   shift_ranking_stability_<sizes>.csv
  shift_nf_groups_<N>f.csv         shift_group_ablation_<N>f.csv
"""
from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import shap
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from xgboost import XGBClassifier

from pipelines.train_pipeline import train_and_evaluate
from scripts.diagnose_normal_fuzzers import CV_PARAMS, FUZZERS, NORMAL, codes, distance, load_splits
from src.preprocessing import CATEGORICAL_FEATURES, engineer_features
from src.utils.config_loader import (
    apply_pool_variant, choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path,
)
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)


def group_of(config: dict) -> dict[str, str]:
    """feature -> group name, from `shift.feature_groups`."""
    return {f: g for g, fs in config["shift"]["feature_groups"].items() for f in fs}


def shift_classifier(a: pd.DataFrame, b: pd.DataFrame, features: list[str], seed: int, shap_rows: int = 0
                     ) -> tuple[float, pd.Series | None]:
    """5-fold cross-validated AUC of an XGBoost classifier separating frame `a` (label 0) from `b` (label 1) on
    `features` (0.5 = indistinguishable); with `shap_rows`, also the mean |SHAP| per feature of a model fitted on all
    rows, computed on that many random rows."""
    both = pd.concat([a, b], ignore_index=True)
    X, y = codes(both, features), np.r_[np.zeros(len(a)), np.ones(len(b))]
    proba = cross_val_predict(XGBClassifier(random_state=seed, **CV_PARAMS), X, y,
                              cv=StratifiedKFold(5, shuffle=True, random_state=seed), method="predict_proba")[:, 1]
    auc = float(roc_auc_score(y, proba))
    if not shap_rows:
        return auc, None
    model = XGBClassifier(random_state=seed, **CV_PARAMS).fit(X, y)
    rows = np.random.default_rng(seed).choice(len(X), min(shap_rows, len(X)), replace=False)
    values = shap.TreeExplainer(model).shap_values(X.iloc[rows])
    return auc, pd.Series(np.abs(values).mean(axis=0), index=features)


def normal_frames(splits) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Engineered Normal rows of train + validation and of the official test split."""
    pick = lambda df: engineer_features(df[df["attack_cat"] == NORMAL], allow_missing=True).reset_index(drop=True)  # noqa: E731
    return pick(pd.concat([splits.train, splits.val], ignore_index=True)), pick(splits.test)


def rank_stability(vectors: dict[str, pd.Series], top: int = 10) -> pd.DataFrame:
    """Pairwise agreement of importance vectors on their shared features: Spearman correlation and the Jaccard
    overlap of their top-`top` features."""
    rows = []
    for (na, a), (nb, b) in itertools.combinations(vectors.items(), 2):
        shared = a.index.intersection(b.index)
        a, b = a[shared], b[shared]
        k = min(top, len(shared))
        ta, tb = set(a.nlargest(k).index), set(b.nlargest(k).index)
        rows.append({"a": na, "b": nb, "n_shared_features": len(shared), "spearman": round(float(spearmanr(a, b)[0]), 4),
                     f"top{top}_jaccard": round(len(ta & tb) / len(ta | tb), 4)})
    return pd.DataFrame(rows)


def prepare(config: dict, feature_sets: dict, pool: str, seed: int | None = None, official: bool = True):
    """(config, feature_sets, splits) of a pool variant (and seed) on the official or pooled split."""
    cfg = apply_pool_variant(config, pool)
    if seed is not None:
        cfg["project"]["seed"] = seed
        cfg["model"]["params"]["random_state"] = seed
    splits = load_splits(cfg, official)
    cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
    return cfg, sets, splits


def label_of(config: dict, feature_sets: dict, pool: str) -> str:
    """Pool-size label ("40f", "45f", "48f") of a pool name without loading any data."""
    return pool_label(choose_pool(apply_pool_variant(config, pool), feature_sets, feature_sets["feature_pool_full"])[1])


def run_a1(config: dict, feature_sets: dict, pool: str) -> tuple[pd.DataFrame, dict]:
    cfg, sets, splits = prepare(config, feature_sets, pool)
    features, label = list(sets["feature_pool"]), pool_label(sets)
    train_n, test_n = normal_frames(splits)
    groups = group_of(cfg)
    aucs, shaps = [], []
    for seed in cfg["shift"]["seeds"]:
        auc, importance = shift_classifier(train_n, test_n, features, seed, cfg["shift"]["shap_rows"])
        aucs.append(auc)
        shaps.append(importance)
        logger.info(f"[shift a1 {label}] seed={seed} AUC={auc:.4f}")
    shap_df = pd.concat(shaps, axis=1)
    ks = pd.Series({f: distance(train_n[f], test_n[f], f in CATEGORICAL_FEATURES) for f in features})
    table = pd.DataFrame({"feature": features, "group": [groups[f] for f in features], "ks_or_tvd": ks.round(4).to_numpy(),
                          "shap_mean": shap_df.mean(axis=1).round(5).to_numpy(), "shap_std": shap_df.std(axis=1, ddof=1).round(5).to_numpy()})
    table["rank_shap"] = table["shap_mean"].rank(ascending=False, method="min").astype(int)
    table["rank_ks"] = table["ks_or_tvd"].rank(ascending=False, method="min").astype(int)
    table = table.sort_values("rank_shap")
    seed_stab = rank_stability({f"seed{s}": shap_df[i] for i, s in enumerate(cfg["shift"]["seeds"])})
    summary = {"pool": label, "n_features": len(features), "n_seeds": len(aucs), "auc_mean": round(float(np.mean(aucs)), 4),
               "auc_std": round(float(np.std(aucs, ddof=1)), 4), "shap_rank_spearman_across_seeds": round(float(seed_stab["spearman"].mean()), 4),
               "shap_top10_jaccard_across_seeds": round(float(seed_stab["top10_jaccard"].mean()), 4),
               "shap_vs_ks_rank_spearman": round(float(spearmanr(table["shap_mean"], table["ks_or_tvd"])[0]), 4),
               "top5_shap_features": ", ".join(table["feature"].head(5)), "top5_ks_features": ", ".join(table.sort_values("rank_ks")["feature"].head(5))}
    metrics_dir = get_metrics_dir(cfg)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(metrics_dir / f"shift_normal_features_{label}.csv", index=False)
    pd.Series(summary).rename("value").rename_axis("metric").to_csv(metrics_dir / f"shift_normal_summary_{label}.csv")
    return table, summary


def run_a2(config: dict, feature_sets: dict, pool: str, top_features: list[str] | None = None) -> pd.DataFrame:
    cfg, sets, splits = prepare(config, feature_sets, pool)
    features, label = list(sets["feature_pool"]), pool_label(sets)
    pred = {}
    train_and_evaluate(cfg, sets, str(len(features)), False, splits, save_artifacts=False, predictions_out=pred, features=features)
    fine, called = np.asarray(pred["fine_grained_true"]), np.asarray(pred["y_pred_labels"])
    feat = engineer_features(splits.test.reset_index(drop=True), allow_missing=True)
    nf, nn, tf = (fine == NORMAL) & (called == FUZZERS), (fine == NORMAL) & (called == NORMAL), fine == FUZZERS
    seed = cfg["shift"]["seeds"][0]
    sets_of = {g: [f for f in fs if f in features] for g, fs in cfg["shift"]["feature_groups"].items()}
    sets_of = {g: fs for g, fs in sets_of.items() if fs}
    sets_of["all_features"] = features
    if top_features:
        sets_of[f"top{len(top_features)}_shift_ranked"] = list(top_features)
    rows = []
    for name, fs in sets_of.items():
        enough = min(nf.sum(), nn.sum(), tf.sum()) >= 20  # too few flows of a kind: the AUC would be meaningless
        auc_nn = shift_classifier(feat[nf], feat[nn], fs, seed)[0] if enough else float("nan")
        auc_tf = shift_classifier(feat[nf], feat[tf], fs, seed)[0] if enough else float("nan")
        ks = lambda m: float(np.mean([distance(feat.loc[nf, f], feat.loc[m, f], f in CATEGORICAL_FEATURES) for f in fs]))  # noqa: E731
        rows.append({"feature_set": name, "n_features": len(fs), "auc_NF_vs_NN": round(auc_nn, 4), "auc_NF_vs_TF": round(auc_tf, 4),
                     "resemblance": round(auc_nn - auc_tf, 4), "mean_ks_NF_vs_NN": round(ks(nn), 4), "mean_ks_NF_vs_TF": round(ks(tf), 4),
                     "n_NF": int(nf.sum()), "n_NN": int(nn.sum()), "n_TF": int(tf.sum())})
        logger.info(f"[shift a2 {label}] {name}: NF-vs-NN {auc_nn:.3f} NF-vs-TF {auc_tf:.3f}")
    out = pd.DataFrame(rows)
    out.to_csv(get_metrics_dir(cfg) / f"shift_nf_groups_{label}.csv", index=False)
    return out


def run_a3(config: dict, feature_sets: dict, pool: str) -> pd.DataFrame:
    cfg0, sets0, _ = prepare(config, feature_sets, pool)
    features, label = list(sets0["feature_pool"]), pool_label(sets0)
    groups = {g: [f for f in fs if f in features] for g, fs in cfg0["shift"]["feature_groups"].items()}
    variants = {"none_removed": []} | {g: fs for g, fs in groups.items() if fs}
    seeds = cfg0["shift"]["seeds"][:3]
    rows = []
    for name, removed in variants.items():
        kept = [f for f in features if f not in removed]
        rates = []
        for seed in seeds:
            cfg, sets, splits = prepare(config, feature_sets, pool, seed)
            pred = {}
            res = train_and_evaluate(cfg, sets, str(len(kept)), False, splits, save_artifacts=False, predictions_out=pred, features=kept)
            fine, called = np.asarray(pred["fine_grained_true"]), np.asarray(pred["y_pred_labels"])
            rates.append({"normal_to_Fuzzers": float((called[fine == NORMAL] == FUZZERS).mean()), "fpr": res["false_positive_rate"],
                          "accuracy": res["accuracy"], "f1": res["f1"], "detection": res["detection_rate"]})
            if seed == seeds[0]:
                train_n, test_n = normal_frames(splits)
        auc, _ = shift_classifier(train_n, test_n, kept, seeds[0])
        r = pd.DataFrame(rates)
        rows.append({"removed_group": name, "n_removed": len(removed), "n_kept": len(kept), "shift_auc": round(auc, 4),
                     **{f"{m}_mean": round(float(r[m].mean()), 4) for m in r}, **{f"{m}_std": round(float(r[m].std(ddof=1)), 4) for m in r}})
        logger.info(f"[shift a3 {label}] removed={name}: AUC={auc:.4f} Normal->Fuzzers={r['normal_to_Fuzzers'].mean():.4f}")
    out = pd.DataFrame(rows)
    base = out[out["removed_group"] == "none_removed"].iloc[0]
    out["shift_auc_vs_all"] = (out["shift_auc"] - base["shift_auc"]).round(4)
    out["normal_to_Fuzzers_vs_all"] = (out["normal_to_Fuzzers_mean"] - base["normal_to_Fuzzers_mean"]).round(4)
    out.to_csv(get_metrics_dir(cfg0) / f"shift_group_ablation_{label}.csv", index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--steps", nargs="*", choices=["a1", "a2", "a3"], default=["a1", "a2", "a3"])
    parser.add_argument("--pools", nargs="*", default=["full"], help="default: the primary pool 48; add base full_no_ttl for the comparison pools")
    parser.add_argument("--ablation-pools", nargs="*", default=["full"], help="pools for a3 (it retrains many models)")
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    metrics_dir = get_metrics_dir(config)
    tables = {}
    if "a1" in args.steps:
        for pool in args.pools:
            tables[pool], summary = run_a1(config, feature_sets, pool)
            print(pd.Series(summary).to_string())
        labels = "_".join(label_of(config, feature_sets, p) for p in args.pools)
        shap_vectors = {label_of(config, feature_sets, p): t.set_index("feature")["shap_mean"] for p, t in tables.items()}
        ks_vectors = {k: t.set_index("feature")["ks_or_tvd"] for k, t in zip(shap_vectors, tables.values())}
        stab = pd.concat([rank_stability(shap_vectors).assign(importance="shap"), rank_stability(ks_vectors).assign(importance="ks")])
        stab.to_csv(metrics_dir / f"shift_ranking_stability_{labels}.csv", index=False)
        print(stab.to_string(index=False))
    if "a2" in args.steps:
        for pool in args.pools:
            top = None
            label = label_of(config, feature_sets, pool)
            path = metrics_dir / f"shift_normal_features_{label}.csv"
            if path.exists():
                top = list(pd.read_csv(path).sort_values("rank_shap")["feature"].head(10))
            print(run_a2(config, feature_sets, pool, top).to_string(index=False))
    if "a3" in args.steps:
        for pool in args.ablation_pools:
            print(run_a3(config, feature_sets, pool).to_string(index=False))


if __name__ == "__main__":
    main()
