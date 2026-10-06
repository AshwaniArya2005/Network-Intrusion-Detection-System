"""Compare methods for the official-split false-positive problem, over seeds, per feature pool:

    python pipelines/run_methods.py --tag <name> --methods flat_default hier_default hier_stage1_tuned [--pools full base]   (default: the primary pool 48 only)

Every method carries an ACCESS level: zero-shot (training data only), transductive (also the unlabelled official-test
features) or few-shot (see pipelines/run_adaptation.py). For each (pool, method, seed) it trains on the official split,
evaluates with the shared evaluate_model (accuracy, macro F1, FPR, detection, FPR at 95% detection, ECE, open-set
detection / AUROC, per-class and fine-grained recall, ...) and adds the validation-chosen det95 operating point
(src.evaluation.metrics.select_attack_threshold on 1 - P(Normal), validation only): `det95_test_fpr`, `det95_test_detection`,
`det95_val_fpr`, `det95_fpr_gap`, plus `normal_to_<class>` shares at argmax. Writes under results/metrics/<model.type>/
(pool size and tag in the names):

  methods_<tag>_<N>f_seeds.csv     one row per (method, seed)
  methods_<tag>_<N>f_summary.csv   per (method, metric): mean, std (ddof=1), min, max over seeds
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from dataclasses import replace

from pipelines.run_operating_point import operating_points
from pipelines.train_pipeline import load_split_data, train_and_evaluate
from pipelines.tune_xgboost import load_tuned
from sklearn.metrics import f1_score

from src.adaptation import domain_importance_weights, unlabelled_shift_ranking
from src.utils.config_loader import apply_pool_variant, choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

# name -> access level and what differs from the flat default model
METHODS = {
    "flat_default": {"access": "zero-shot", "scheme": "current"},
    "hier_default": {"access": "zero-shot", "scheme": "hierarchical"},
    "hier_stage1_tuned": {"access": "zero-shot", "scheme": "hierarchical", "stage1_tuned": True},
    # TRANSDUCTIVE: use the unlabelled FEATURES of the official test file (no labels)
    "domain_weights_clip5": {"access": "transductive", "scheme": "current", "domain_clip": 5},
    "domain_weights_clip20": {"access": "transductive", "scheme": "current", "domain_clip": 20},
    "drop_top5_shifted": {"access": "transductive", "scheme": "current", "drop_top_shifted": 5},
    "drop_top10_shifted": {"access": "transductive", "scheme": "current", "drop_top_shifted": 10},
}
NOT_AGGREGATED = {"seed", "n_features", "n_train", "n_val", "n_test"}


def apply_method(cfg: dict, sets: dict, spec: dict) -> dict:
    """The config for one method after the pool is chosen: stage-1 hyperparameters selected on validation
    (tuned_params_stage1_<N>f.json, objective = validation macro F1 as declared in results/06_fpr_and_adaptation.md, section `Source: shift_and_fewshot_protocol.md`)."""
    if spec.get("stage1_tuned"):
        params, power = load_tuned(cfg, pool_label(sets), "f1", stage1=True)
        cfg["model"]["stage1_params"] = params
        cfg["model"]["stage1_class_weight_power"] = power
    return cfg


def run_method(config: dict, feature_sets: dict, pool: str, method: str, seed: int) -> dict:
    spec = METHODS[method]
    cfg = apply_pool_variant(config, pool)
    cfg["project"]["seed"] = seed
    cfg["model"]["params"]["random_state"] = seed
    cfg["data"]["label_scheme"] = spec["scheme"]
    splits = load_split_data(cfg, use_official_split=True)
    cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
    cfg = apply_method(cfg, sets, spec)
    features, pred = list(sets["feature_pool"]), {}
    if spec.get("domain_clip"):      # TRANSDUCTIVE: reweight the training rows towards the unlabelled test features
        splits = replace(splits, weight_multiplier=domain_importance_weights(splits.train, splits.test, features, spec["domain_clip"], seed))
    if spec.get("drop_top_shifted"):  # TRANSDUCTIVE: drop the features whose all-row distribution differs most train vs test
        ranking = unlabelled_shift_ranking(splits.train, splits.test, features)
        features = [f for f in features if f not in set(ranking.index[: spec["drop_top_shifted"]])]
    result = train_and_evaluate(cfg, sets, str(len(features)), True, splits, save_artifacts=False, predictions_out=pred, features=features)
    normal = cfg["data"]["normal_category"]
    det95 = {r["rule"]: r for r in operating_points(pred, normal)}["det95"]
    called = pd.Series(pred["y_pred_labels"])[pd.Series(pred["fine_grained_true"]) == normal]
    shares = called.value_counts(normalize=True)
    classes = np.asarray(pred["class_names"])
    val_macro_f1 = round(float(f1_score(pred["val_labels"], classes[pred["y_proba_val"].argmax(axis=1)], average="macro", zero_division=0)), 4)
    return {"pool": pool, "pool_label": pool_label(sets), "method": method, "access": spec["access"], "seed": seed, **result, "val_macro_f1": val_macro_f1,
            "n_features_used": len(features), "det95_threshold": det95["threshold"], "det95_val_fpr": det95["val_fpr"], "det95_val_detection": det95["val_detection"],
            "det95_test_fpr": det95["test_fpr"], "det95_test_detection": det95["test_detection"], "det95_fpr_gap": det95["fpr_gap"],
            **{f"normal_to_{c}": round(float(shares.get(c, 0.0)), 4) for c in pred["class_names"]}}


def summarise(seeds_df: pd.DataFrame) -> pd.DataFrame:
    numeric = [c for c in seeds_df.select_dtypes("number").columns if c not in NOT_AGGREGATED]
    long = seeds_df.melt(id_vars=["pool", "method", "access", "seed"], value_vars=numeric, var_name="metric")
    return (long.groupby(["pool", "method", "access", "metric"], sort=False)["value"]
            .agg(mean="mean", std=lambda v: v.std(ddof=1) if v.notna().sum() > 1 else float("nan"), min="min", max="max", n_seeds="count")
            .round(4).reset_index())


def run_methods(config: dict, feature_sets: dict, tag: str, methods: list[str], pools=("full",), seeds=None) -> dict[str, pd.DataFrame]:
    seeds = list(seeds or config["experiments"]["headline_seeds"])
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    out = {}
    for pool in pools:
        rows = []
        for method in methods:
            for seed in seeds:
                rows.append(run_method(config, feature_sets, pool, method, seed))
                logger.info(f"[methods {tag}] pool={pool} method={method} seed={seed}: fpr={rows[-1]['false_positive_rate']} "
                            f"det95_fpr={rows[-1]['det95_test_fpr']}")
        seeds_df = pd.DataFrame(rows)
        label = seeds_df["pool_label"].iloc[0]
        seeds_df.to_csv(metrics_dir / f"methods_{tag}_{label}_seeds.csv", index=False)
        out[label] = summarise(seeds_df)
        out[label].to_csv(metrics_dir / f"methods_{tag}_{label}_summary.csv", index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tag", required=True, help="name of this comparison, used in the file names")
    parser.add_argument("--methods", nargs="*", required=True, choices=list(METHODS))
    parser.add_argument("--pools", nargs="*", default=["full"], help="default: the primary pool 48 (full); add base (40) or full_no_ttl (45) for the comparison pools")
    parser.add_argument("--seeds", nargs="*", type=int)
    args = parser.parse_args()
    config = load_config()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    for label, summary in run_methods(config, load_feature_sets(), args.tag, args.methods, args.pools, args.seeds).items():
        key = summary[summary["metric"].isin(["accuracy", "f1", "false_positive_rate", "detection_rate", "fpr_at_95_detection",
                                              "det95_test_fpr", "det95_test_detection", "ece", "unknown_detection_rate", "unknown_auroc"])]
        print(label, "\n", key.pivot(index="metric", columns="method", values="mean").to_string())


if __name__ == "__main__":
    main()
