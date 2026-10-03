"""Attack-vs-normal operating point chosen on VALIDATION, and what it costs on the official test split:

    python pipelines/run_operating_point.py [--pools base full] [--seeds 42 43 44 45 46]

For every (pool, seed) it trains the configured model on the official split (scheme `current`, whole pool) and
compares three decision rules on the validation split (drawn from the training file, so it carries no split
shift) and on the official test split:

  argmax   a flow is an attack when the predicted class is not Normal
  det95    threshold on 1 - P(Normal) chosen on validation to reach 95% detection at the lowest FPR
  fpr10    threshold on 1 - P(Normal) chosen on validation to keep FPR <= 10% at the highest detection

The thresholds are fixed on validation and never adjusted afterwards. `fpr_gap` = test FPR - validation FPR is the
quantified cost of the train/test shift (also `detection_gap`). Writes under results/metrics/<model.type>/:

  operating_point_seeds_<N>f.csv     one row per (seed, rule)
  operating_point_summary_<N>f.csv   mean / std / min / max over seeds per rule
  operating_point_summary.md         the pools side by side
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from pipelines.train_pipeline import load_split_data, train_and_evaluate
from src.evaluation.metrics import attack_rates, select_attack_threshold
from src.utils.config_loader import choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

RULES = {"argmax": None, "det95": {"target_detection": 0.95}, "fpr10": {"target_fpr": 0.10}}
VALUE_COLUMNS = ["threshold", "val_detection", "val_fpr", "test_detection", "test_fpr", "detection_gap", "fpr_gap"]


def operating_points(pred: dict, normal: str, rules: dict = RULES) -> list[dict]:
    """The rows for one trained model: each rule's validation-chosen threshold and its validation / test rates.
    `pred` is train_and_evaluate's predictions_out (needs the validation outputs)."""
    classes = list(pred["class_names"])
    k = classes.index(normal)
    val_attack, test_attack = np.asarray(pred["val_labels"]) != normal, np.asarray(pred["fine_grained_true"]) != normal
    score_val, score_test = 1 - pred["y_proba_val"][:, k], 1 - pred["y_proba"][:, k]
    rows = []
    for name, target in rules.items():
        if target is None:  # argmax: an attack iff Normal is not the most probable class
            called_val, called_test = pred["y_proba_val"].argmax(axis=1) != k, pred["y_proba"].argmax(axis=1) != k
            val_det, val_fpr = called_val[val_attack].mean(), called_val[~val_attack].mean()
            test_det, test_fpr = called_test[test_attack].mean(), called_test[~test_attack].mean()
            threshold = float("nan")
        else:
            threshold = select_attack_threshold(val_attack, score_val, **target)
            val_det, val_fpr = attack_rates(val_attack, score_val, threshold)
            test_det, test_fpr = attack_rates(test_attack, score_test, threshold)
        rows.append({"rule": name, "threshold": round(threshold, 4), "val_detection": round(float(val_det), 4),
                     "val_fpr": round(float(val_fpr), 4), "test_detection": round(float(test_det), 4),
                     "test_fpr": round(float(test_fpr), 4), "detection_gap": round(float(test_det - val_det), 4),
                     "fpr_gap": round(float(test_fpr - val_fpr), 4)})
    return rows


def run_operating_point(config: dict, feature_sets: dict, pools=("base", "full"), seeds=None) -> dict[str, pd.DataFrame]:
    seeds = list(seeds or config["experiments"]["headline_seeds"])
    normal = config["data"]["normal_category"]
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    summaries = {}
    for pool in pools:
        rows = []
        for seed in seeds:
            cfg = copy.deepcopy(config)
            cfg["feature_selection"]["pool"] = pool
            cfg["project"]["seed"] = seed
            cfg["model"]["params"]["random_state"] = seed
            splits = load_split_data(cfg, use_official_split=True)
            cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
            pred = {}
            features = list(sets["feature_pool"])
            train_and_evaluate(cfg, sets, str(len(features)), False, splits, save_artifacts=False, predictions_out=pred,
                               features=features)
            rows += [{"pool": pool, "seed": seed, **r} for r in operating_points(pred, normal)]
            logger.info(f"[operating point] pool={pool} seed={seed} done")
        label = pool_label(sets)
        seeds_df = pd.DataFrame(rows)
        summary = (seeds_df.melt(id_vars=["pool", "seed", "rule"], value_vars=VALUE_COLUMNS, var_name="metric")
                   .groupby(["rule", "metric"], sort=False)["value"]
                   .agg(mean="mean", std=lambda v: v.std(ddof=1) if v.notna().sum() > 1 else float("nan"), min="min", max="max")
                   .round(4).reset_index())
        seeds_df.to_csv(metrics_dir / f"operating_point_seeds_{label}.csv", index=False)
        summary.to_csv(metrics_dir / f"operating_point_summary_{label}.csv", index=False)
        summaries[label] = summary
    (metrics_dir / "operating_point_summary.md").write_text(render_summary(summaries, seeds), encoding="utf-8")
    return summaries


def render_summary(summaries: dict[str, pd.DataFrame], seeds: list[int]) -> str:
    lines = [f"# Attack-vs-normal operating points chosen on validation, official test split (mean +/- std over seeds {seeds})", "",
             "Thresholds on 1 - P(Normal) are fixed on the validation split (drawn from the training file) and never adjusted; "
             "`fpr_gap` = test FPR - validation FPR is the cost of the train/test shift.", "",
             "| pool | rule | threshold | val detection | val FPR | test detection | test FPR | FPR gap (test - val) |",
             "|---|---|---|---|---|---|---|---|"]
    for label, s in summaries.items():
        for rule in s["rule"].unique():
            g = s[s["rule"] == rule].set_index("metric")
            cell = lambda m: ("n/a" if np.isnan(g.loc[m, "mean"]) else f"{g.loc[m, 'mean']:.4f} +/- {g.loc[m, 'std']:.4f}")  # noqa: E731
            lines.append(f"| {label} | {rule} | " + " | ".join(cell(m) for m in
                         ["threshold", "val_detection", "val_fpr", "test_detection", "test_fpr", "fpr_gap"]) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["base", "full"], help="base, full, or an experiments.pool_variants name")
    parser.add_argument("--seeds", nargs="*", type=int)
    args = parser.parse_args()
    config = load_config()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    run_operating_point(config, load_feature_sets(), args.pools, args.seeds)
    print((get_metrics_dir(config) / "operating_point_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
