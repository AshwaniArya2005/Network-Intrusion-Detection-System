"""Bootstrap intervals over the official test rows, and paired differences between feature pools:

    python pipelines/run_bootstrap.py [--pools base full] [--resamples 1000] [--seed 42]

Trains the configured model once per pool (official split, scheme `current`, whole pool, default hyperparameters,
`--seed` for the model and the train/validation split) and resamples the official test rows (and, independently, the
held-out zero-day rows) with replacement, scoring every pool on the SAME resampled rows (src/evaluation/bootstrap.py).
Writes under results/metrics/<model.type>/ (names carry the pools, e.g. _40f_48f):

  bootstrap_ci_<pools>.csv            per pool and metric: estimate and 95% interval
  bootstrap_paired_diff_<pools>.csv   for every pair, later pool minus earlier (e.g. 48f - 40f): difference, 95% interval, excludes_zero
"""
from __future__ import annotations

import argparse
import copy
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from pipelines.train_pipeline import load_split_data, train_and_evaluate
from src.evaluation.bootstrap import bootstrap, intervals, paired_differences
from src.utils.config_loader import choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)


def run_bootstrap(config: dict, feature_sets: dict, pools=("base", "full"), n_boot: int = 1000, seed: int = 42):
    models, labels, classes = {}, [], None
    for pool in pools:
        cfg = copy.deepcopy(config)
        cfg["feature_selection"]["pool"] = pool
        cfg["project"]["seed"] = seed
        cfg["model"]["params"]["random_state"] = seed
        splits = load_split_data(cfg, use_official_split=True)
        cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
        features, pred = list(sets["feature_pool"]), {}
        train_and_evaluate(cfg, sets, str(len(features)), True, splits, save_artifacts=False, predictions_out=pred, features=features)
        label = pool_label(sets)
        labels.append(label)
        classes = list(pred["class_names"])
        models[label] = {"y_true": np.asarray(pred["y_test"]), "y_pred": np.asarray(pred["y_pred"]),
                         "unknown_flags": np.asarray(pred["open_set_is_unknown"])[np.asarray(pred["is_true_unknown"])]}
    normal, fuzzers = classes.index(config["data"]["normal_category"]), classes.index("Fuzzers")
    point, draws = bootstrap(models, len(classes), normal, fuzzers, n_boot, seed)
    cis = intervals(point, draws)
    diffs = paired_differences(point, draws, list(itertools.combinations(labels, 2)))
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    tag = "_".join(labels)
    cis.to_csv(metrics_dir / f"bootstrap_ci_{tag}.csv", index=False)
    diffs.to_csv(metrics_dir / f"bootstrap_paired_diff_{tag}.csv", index=False)
    return cis, diffs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["base", "full"], help="base, full, or an experiments.pool_variants name")
    parser.add_argument("--resamples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    config = load_config()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    cis, diffs = run_bootstrap(config, load_feature_sets(), args.pools, args.resamples, args.seed)
    print(cis.to_string(index=False), "\n", diffs.to_string(index=False))


if __name__ == "__main__":
    main()
