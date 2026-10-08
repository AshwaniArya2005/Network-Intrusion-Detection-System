"""Diagnostic (no model or protocol changes): why are Normal flows called Fuzzers on the official split?

    python scripts/diagnose_normal_fuzzers.py [--pools full base]   (default: the primary pool 48 only)

For each feature pool it trains the configured model once (scheme `current`, closed-set, whole pool
as the tier, exactly like pipelines/run_label_scheme_comparison.py) and writes, under
results/metrics/<model.type>/normal_fuzzers_diagnostic/ (suffix `_48f` for the full pool):

  feature_distributions<tag>.csv   official test split: Normal-called-Fuzzers (NF) vs correctly
                                   predicted Normal (NN) vs true Fuzzers (TF): per-feature median/IQR
                                   (or top category), KS (total-variation distance for categoricals)
                                   of NF vs NN and NF vs TF, and which group NF is closer to
  split_shift_ks<tag>.csv          train-Normal vs test-Normal, per feature (KS / TVD), official split
  summary<tag>.csv                 scalar results: group sizes, NF-vs-NN / NF-vs-TF classifier AUCs,
                                   train-vs-test Normal AUC (official, pooled-random control, within-train
                                   control), exact / near twins of NF flows in true Fuzzers, NF confidence,
                                   attack-vs-normal AUROC and FPR at fixed detection

Everything is measured on rows and predictions that already exist; nothing here chooses a
threshold, a hyperparameter or a feature set.
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import ks_2samp
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from xgboost import XGBClassifier

from pipelines.train_pipeline import ensure_feature_ranking, load_split_data, train_and_evaluate
from src.data_loader import UNSW_RAW_COLUMNS
from src.evaluation.metrics import fpr_at_detection
from src.evaluation.overlap import NEAR_THRESHOLDS, _embedding, vector_ids
from src.preprocessing import CATEGORICAL_FEATURES, engineer_features
from src.utils.config_loader import choose_pool, get_metrics_dir, load_config, load_feature_sets
from src.utils.logger import get_logger

logger = get_logger(__name__)
NORMAL, FUZZERS = "Normal", "Fuzzers"
CV_PARAMS = dict(n_estimators=200, max_depth=6, learning_rate=0.1, subsample=0.9, n_jobs=-1, eval_metric="logloss")


def distance(a: pd.Series, b: pd.Series, categorical: bool) -> float:
    """KS statistic (numeric) or total-variation distance (categorical) between two samples."""
    if categorical:
        pa, pb = a.value_counts(normalize=True), b.value_counts(normalize=True)
        return float(pa.sub(pb, fill_value=0).abs().sum() / 2)
    return float(ks_2samp(a, b).statistic)


def codes(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Numeric matrix for a tree classifier: numerics as is, categoricals as integer codes."""
    return pd.DataFrame({f: pd.factorize(df[f])[0] if f in CATEGORICAL_FEATURES else pd.to_numeric(df[f], errors="coerce")
                         for f in features}).replace([np.inf, -np.inf], np.nan)


def cv_auc(a: pd.DataFrame, b: pd.DataFrame, features: list[str], seed: int = 42) -> tuple[float, pd.Series]:
    """5-fold cross-validated AUC of a classifier telling frame `a` (label 0) from `b` (label 1), and the
    gain importances of a model fitted on all of it. 0.5 = indistinguishable, 1.0 = perfectly separable."""
    both = pd.concat([a, b], ignore_index=True)
    X, y = codes(both, features), np.r_[np.zeros(len(a)), np.ones(len(b))]
    proba = cross_val_predict(XGBClassifier(random_state=seed, **CV_PARAMS), X, y,
                              cv=StratifiedKFold(5, shuffle=True, random_state=seed), method="predict_proba")[:, 1]
    model = XGBClassifier(random_state=seed, importance_type="gain", **CV_PARAMS).fit(X, y)
    return float(roc_auc_score(y, proba)), pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)


def twin_shares(test_normal: pd.DataFrame, fuzzers: pd.DataFrame, nf_mask: np.ndarray, raw_features: list[str],
                features: list[str]) -> dict:
    """Share of NF / NN flows (and of all Normal test flows) with an exact twin (identical raw feature vector)
    or a near twin (L-inf <= t in the embedding of src.evaluation.overlap, categoricals exact) among `fuzzers`."""
    out = {}
    fuzz_ids = set(vector_ids(fuzzers, raw_features))
    exact = np.isin(vector_ids(test_normal, raw_features), list(fuzz_ids))
    emb = _embedding(pd.concat([test_normal, fuzzers], ignore_index=True)[features], features)
    tree = cKDTree(emb[len(test_normal):])
    dist, _ = tree.query(emb[:len(test_normal)], p=np.inf, distance_upper_bound=max(NEAR_THRESHOLDS) + 1e-9, workers=-1)
    for name, mask in (("NF", nf_mask), ("NN", ~nf_mask), ("all_normal", np.ones(len(nf_mask), bool))):
        out[f"exact_twin_in_fuzzers_{name}_pct"] = round(100 * float(exact[mask].mean()), 2)
        for t in NEAR_THRESHOLDS:
            out[f"near_twin_{t}_in_fuzzers_{name}_pct"] = round(100 * float((dist[mask] <= t + 1e-12).mean()), 2)
    return out


def load_splits(config: dict, official: bool | None = None):
    """load_split_data with the (DataFrame-valued) dedup-count attrs stripped, which break pd.concat."""
    splits = load_split_data(config, use_official_split=official)
    for part in (splits.train, splits.val, splits.test, splits.unknown):
        part.attrs = {}
    return splits


def run_pool(config: dict, feature_sets: dict, pool: str) -> None:
    config = copy.deepcopy(config)
    config["feature_selection"]["pool"] = pool
    splits = load_splits(config)
    config, feature_sets = choose_pool(config, feature_sets, splits.train.columns)
    ensure_feature_ranking(config, feature_sets, splits.train)
    tier = str(len(feature_sets["feature_pool"]))
    features = feature_sets["feature_pool"]
    raw_features = [c for c in UNSW_RAW_COLUMNS if c in features]
    tag = config["feature_selection"]["pool_tag"]
    out_dir = get_metrics_dir(config) / "normal_fuzzers_diagnostic"
    out_dir.mkdir(parents=True, exist_ok=True)

    pred = {}
    train_and_evaluate(config, feature_sets, tier, False, splits, save_artifacts=False, predictions_out=pred)
    fine, labels = np.asarray(pred["fine_grained_true"]), np.asarray(pred["y_pred_labels"])
    test = splits.test.reset_index(drop=True)
    feat = engineer_features(test, allow_missing=True)
    nf, nn, tf = (fine == NORMAL) & (labels == FUZZERS), (fine == NORMAL) & (labels == NORMAL), fine == FUZZERS
    summary = {"pool": pool, "n_features": len(features), "n_test_normal": int((fine == NORMAL).sum()),
               "n_normal_called_fuzzers": int(nf.sum()), "n_normal_correct": int(nn.sum()), "n_true_fuzzers": int(tf.sum()),
               "normal_called_fuzzers_share": round(float(nf.sum() / (fine == NORMAL).sum()), 4)}

    # 1. NF vs NN vs TF on the official test split
    rows = []
    for f in features:
        cat = f in CATEGORICAL_FEATURES
        g = {k: feat.loc[m, f] for k, m in (("NF", nf), ("NN", nn), ("TF", tf))}
        ks_nn, ks_tf = distance(g["NF"], g["NN"], cat), distance(g["NF"], g["TF"], cat)
        row = {"feature": f, "type": "categorical" if cat else "numeric", "ks_NF_vs_NN": round(ks_nn, 4),
               "ks_NF_vs_TF": round(ks_tf, 4), "closer_to": "Fuzzers" if ks_tf < ks_nn else "Normal"}
        for k, s in g.items():
            if cat:
                row[f"{k}_top"] = ", ".join(f"{v}:{p:.2f}" for v, p in s.value_counts(normalize=True).head(3).items())
            else:
                q = pd.to_numeric(s, errors="coerce").quantile([0.25, 0.5, 0.75])
                row.update({f"{k}_median": round(float(q[0.5]), 4), f"{k}_iqr": round(float(q[0.75] - q[0.25]), 4)})
        rows.append(row)
    dist_df = pd.DataFrame(rows).sort_values("ks_NF_vs_NN", ascending=False)
    dist_df.to_csv(out_dir / f"feature_distributions{tag}.csv", index=False)
    summary.update(features_closer_to_Fuzzers=int((dist_df["closer_to"] == "Fuzzers").sum()),
                   features_closer_to_Normal=int((dist_df["closer_to"] == "Normal").sum()),
                   median_ks_NF_vs_NN=round(float(dist_df["ks_NF_vs_NN"].median()), 4),
                   median_ks_NF_vs_TF=round(float(dist_df["ks_NF_vs_TF"].median()), 4))
    summary["auc_NF_vs_NN"] = round(cv_auc(feat[nf], feat[nn], features)[0], 4)
    summary["auc_NF_vs_TF"] = round(cv_auc(feat[nf], feat[tf], features)[0], 4)

    # 2. train-Normal vs test-Normal (split shift)
    normal = lambda df: engineer_features(df[df["attack_cat"] == NORMAL], allow_missing=True)  # noqa: E731
    train_n = normal(pd.concat([splits.train, splits.val], ignore_index=True))
    test_n = normal(test)
    auc, importance = cv_auc(train_n, test_n, features)
    summary["auc_train_normal_vs_test_normal_official"] = round(auc, 4)
    summary["shift_top5_features_by_gain"] = ", ".join(importance.head(5).index)
    shift = pd.DataFrame({"feature": features,
                          "ks_or_tvd_train_vs_test_normal": [round(distance(train_n[f], test_n[f], f in CATEGORICAL_FEATURES), 4)
                                                             for f in features],
                          "shift_classifier_gain": importance.reindex(features).round(4).to_numpy()}
                         ).sort_values("ks_or_tvd_train_vs_test_normal", ascending=False)
    shift.to_csv(out_dir / f"split_shift_ks{tag}.csv", index=False)
    summary["median_ks_train_vs_test_normal"] = round(float(shift["ks_or_tvd_train_vs_test_normal"].median()), 4)
    half = train_n.sample(frac=0.5, random_state=0)
    summary["auc_control_within_train_normal"] = round(cv_auc(half, train_n.drop(half.index), features)[0], 4)
    pooled = load_splits(config, official=False)
    summary["auc_train_normal_vs_test_normal_pooled_random"] = round(cv_auc(
        normal(pd.concat([pooled.train, pooled.val], ignore_index=True)), normal(pooled.test), features)[0], 4)

    # 3. twins of NF flows in true Fuzzers (train+val Fuzzers = what the model saw; all Fuzzers = every known row)
    known = pd.concat([splits.train, splits.val, test], ignore_index=True)
    test_normal = test[fine == NORMAL].reset_index(drop=True)
    nf_in_normal = (labels[fine == NORMAL] == FUZZERS)
    for scope, frame in (("train_fuzzers", pd.concat([splits.train, splits.val])), ("all_known_fuzzers", known)):
        fz = frame[frame["attack_cat"] == FUZZERS].reset_index(drop=True)
        shares = twin_shares(engineer_features(test_normal, allow_missing=True), engineer_features(fz, allow_missing=True),
                             nf_in_normal, raw_features, features)
        summary.update({f"{scope}__{k}": v for k, v in shares.items()})

    # NF confidence and the attack-vs-normal view of the same scores
    classes = list(pred["class_names"])
    proba = pred["y_proba"]
    p_norm_nf = proba[nf, classes.index(NORMAL)]
    summary.update(NF_median_p_normal=round(float(np.median(p_norm_nf)), 4),
                   NF_median_p_fuzzers=round(float(np.median(proba[nf, classes.index(FUZZERS)])), 4),
                   NF_share_p_normal_ge_0_25=round(float((p_norm_nf >= 0.25).mean()), 4),
                   NF_share_p_normal_ge_0_40=round(float((p_norm_nf >= 0.40).mean()), 4))
    is_attack = fine != NORMAL
    summary["binary_auroc_attack_vs_normal"] = round(float(roc_auc_score(is_attack, 1 - proba[:, classes.index(NORMAL)])), 4)
    summary.update(fpr_at_detection(fine, proba, classes, NORMAL))  # fine labels: anything but Normal is an attack
    # 4. the TTL signature NF flows share with Fuzzers (sttl 254 / dttl 252; the columns are in the data for either pool)
    trainval = pd.concat([splits.train, splits.val], ignore_index=True)
    sig_rows = []
    for split_name, frame in (("train+val", trainval), ("official_test", test)):
        has = (frame["sttl"] == 254) & (frame["dttl"] == 252)
        for cls, g in frame.groupby("attack_cat"):
            sig_rows.append({"split": split_name, "class": cls, "rows": len(g), "rows_with_signature": int(has[g.index].sum()),
                             "share_of_class_with_signature": round(float(has[g.index].mean()), 4),
                             "share_of_signature_rows": round(float(has[g.index].sum() / max(has.sum(), 1)), 4)})
    sig = pd.DataFrame(sig_rows)
    sig.to_csv(out_dir / f"ttl_signature{tag}.csv", index=False)
    for split_name, key in (("train+val", "train"), ("official_test", "test")):
        pick = sig[(sig["split"] == split_name) & (sig["class"] == NORMAL)].iloc[0]
        summary[f"normal_share_with_ttl_signature_{key}"] = pick["share_of_class_with_signature"]
    summary["nf_share_with_ttl_signature"] = round(float(((test.loc[nf, "sttl"] == 254) & (test.loc[nf, "dttl"] == 252)).mean()), 4)
    pd.Series(summary).rename("value").rename_axis("metric").to_csv(out_dir / f"summary{tag}.csv")
    logger.info(f"[{pool}] wrote {out_dir}")
    print(f"--- pool={pool}\n{pd.Series(summary).to_string()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", choices=["base", "full"], default=["full"])
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    for pool in args.pools:
        run_pool(config, feature_sets, pool)


if __name__ == "__main__":
    main()
