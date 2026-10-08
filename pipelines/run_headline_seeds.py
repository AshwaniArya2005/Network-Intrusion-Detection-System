"""Headline metrics over several seeds, for both feature pools and both split protocols:

    python pipelines/run_headline_seeds.py [--pools full base]   (default: the primary pool 48 only) [--seeds 42 43 44 45 46]
                                           [--tuned f1|auc] [--protocols official pooled_random]

For every (pool, split protocol, seed) it trains the configured model on the whole pool (40 or 48
features, scheme `current`) and evaluates it with the shared evaluate_model, so every metric
(accuracy, macro F1, detection / false-positive rate, per-class and macro ROC-AUC / PR-AUC, ECE, Brier,
open-set detection and AUROC, ...) is reported. A seed changes the model's random_state and the
train/validation split (and, for the pooled random protocol, the train/test split); the official
test file is fixed. Writes under results/metrics/<model.type>/:

  headline_seeds.csv        one row per (pool, split, seed), plus `normal_to_<class>` shares of Normal test flows
  headline_summary.csv      per (pool, split, metric): mean, std (ddof=1), min, max over seeds
  headline_summary.md       the key metrics as "mean +/- std", pools and protocols side by side

`--tuned f1|auc` uses the hyperparameters selected on validation by pipelines/tune_xgboost.py (tuned_params_<N>f.json)
instead of config.yaml's defaults; any non-default selection of tuned / protocols writes under its own file names
(headline_tuned_f1_official_seeds.csv, headline_full_no_ttl_seeds.csv, ...), so earlier results are never overwritten.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.train_pipeline import load_split_data, train_and_evaluate
from pipelines.tune_xgboost import load_tuned
from src.utils.config_loader import apply_pool_variant, choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

PROTOCOLS = (("official", True), ("pooled_random", False))
KEY_METRICS = ["accuracy", "f1", "detection_rate", "false_positive_rate", "recall_Normal", "normal_to_Fuzzers",
               "roc_auc_macro", "pr_auc_macro", "roc_auc_attack_vs_normal", "ece", "brier",
               "fpr_at_95_detection", "unknown_detection_rate", "false_unknown_alarm_rate", "unknown_auroc"]
NOT_AGGREGATED = {"seed", "n_features", "n_train", "n_val", "n_test"}


DEFAULT_POOLS = ("base", "full")


def output_stem(tuned: str | None, protocols: tuple[str, ...], pools: tuple[str, ...] = DEFAULT_POOLS) -> str:
    """File-name stem of a run's outputs: plain `headline` for the default run (both pools, both protocols, default
    hyperparameters), else tagged by what differs, so a different run never overwrites an earlier result."""
    parts = (["headline"] + ([f"tuned_{tuned}"] if tuned else []) + (list(protocols) if len(protocols) < len(PROTOCOLS) else [])
             + (list(pools) if tuple(pools) != DEFAULT_POOLS else []))
    return "_".join(parts)


def run_headline_seeds(config: dict, feature_sets: dict, pools=DEFAULT_POOLS, seeds=None, tuned: str | None = None,
                       protocols: tuple[str, ...] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    seeds = list(seeds or config["experiments"]["headline_seeds"])
    protocols = tuple(protocols or [name for name, _ in PROTOCOLS])
    normal = config["data"]["normal_category"]
    rows = []
    for pool in pools:
        for protocol, official in [p for p in PROTOCOLS if p[0] in protocols]:
            for seed in seeds:
                cfg = apply_pool_variant(config, pool)
                cfg["project"]["seed"] = seed
                cfg["model"]["params"]["random_state"] = seed
                splits = load_split_data(cfg, use_official_split=official)
                cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
                if tuned:  # hyperparameters selected on validation (pipelines/tune_xgboost.py)
                    params, power = load_tuned(cfg, pool_label(sets), tuned)
                    cfg["model"]["params"].update(params)
                    cfg["model"]["class_weight_power"] = power
                predictions = {}
                features = list(sets["feature_pool"])  # the whole pool: no ranking needed, nothing written to results/
                result = train_and_evaluate(cfg, sets, str(len(features)), True, splits, save_artifacts=False,
                                            predictions_out=predictions, features=features)
                called = pd.Series(predictions["y_pred_labels"])[pd.Series(predictions["fine_grained_true"]) == normal]
                shares = called.value_counts(normalize=True).round(4)
                rows.append({"pool": pool, "split": protocol, "seed": seed, **result,
                             **{f"normal_to_{c}": float(shares.get(c, 0.0)) for c in predictions["class_names"]}})
                logger.info(f"[headline] pool={pool} split={protocol} seed={seed}: acc={result['accuracy']} f1={result['f1']}")
    seeds_df = pd.DataFrame(rows)

    numeric = [c for c in seeds_df.select_dtypes("number").columns if c not in NOT_AGGREGATED]
    long = seeds_df.melt(id_vars=["pool", "split", "seed"], value_vars=numeric, var_name="metric")
    summary = (long.groupby(["pool", "split", "metric"], sort=False)["value"]
               .agg(mean="mean", std=lambda v: v.std(ddof=1) if v.notna().sum() > 1 else float("nan"), min="min", max="max",
                    n_seeds="count").round(4).reset_index())

    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    stem = output_stem(tuned, protocols, tuple(pools))
    seeds_df.to_csv(metrics_dir / f"{stem}_seeds.csv", index=False)
    summary.to_csv(metrics_dir / f"{stem}_summary.csv", index=False)
    (metrics_dir / f"{stem}_summary.md").write_text(render_summary(summary, seeds), encoding="utf-8")
    return seeds_df, summary


def render_summary(summary: pd.DataFrame, seeds: list[int]) -> str:
    """Key metrics as "mean +/- std" with one column per (pool, split), as a markdown table."""
    cell = summary.assign(text=lambda d: d["mean"].map("{:.4f}".format) + " +/- " + d["std"].map("{:.4f}".format))
    cell["column"] = cell["pool"].map({"base": "40 features", "full": "48 features"}).fillna(cell["pool"]) + ", " + cell["split"]
    table = (cell[cell["metric"].isin(KEY_METRICS)].pivot(index="metric", columns="column", values="text")
             .reindex([m for m in KEY_METRICS if m in set(cell["metric"])]))
    lines = ["| metric | " + " | ".join(table.columns) + " |", "|---|" + "---|" * len(table.columns)]
    lines += [f"| {metric} | " + " | ".join(row.fillna("n/a")) + " |" for metric, row in table.iterrows()]
    return (f"# Headline metrics, mean +/- std over seeds {seeds} (ddof=1)\n\n"
            "A seed changes the model seed and the train/validation split (and the train/test split on the pooled random "
            "protocol); the official test file is fixed. Scheme `current`, whole-pool tier.\n\n" + "\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["full"], help="default: the primary pool 48 (full); add base (40), full_no_ttl (45) or an experiments.pool_variants name for the comparison pools")
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--tuned", choices=["f1", "auc"], help="use the validation-selected hyperparameters of this objective")
    parser.add_argument("--protocols", nargs="*", choices=[name for name, _ in PROTOCOLS])
    args = parser.parse_args()
    config = load_config()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    run_headline_seeds(config, load_feature_sets(), args.pools, args.seeds, args.tuned, args.protocols)
    stem = output_stem(args.tuned, tuple(args.protocols or [n for n, _ in PROTOCOLS]), tuple(args.pools))
    print((get_metrics_dir(config) / f"{stem}_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
