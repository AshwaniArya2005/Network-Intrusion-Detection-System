"""Accuracy as three numbers together, per feature pool:

    python scripts/accuracy_table.py [--pools base full] [--tuned f1 auc]

  official split   mean +/- std over seeds (results/metrics/<model.type>/headline_*_summary.csv)
  pooled split     same, pooled random split
  ceiling          best-possible accuracy of ANY classifier on the pool's raw columns (duplicates kept, known classes,
                   scheme `current`; src/evaluation/overlap.py): rows sharing a feature vector can only get one label

Tuned rows (hyperparameters chosen on validation, see pipelines/tune_xgboost.py) exist for the official split only.
Needs the headline runs (pipelines/run_headline_seeds.py) for the requested pools. Writes
accuracy_three_numbers_<pools>[_tuned_<objectives>].csv / .md next to them (pool sizes in the name, e.g. _40f_48f).
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.run_headline_seeds import DEFAULT_POOLS, PROTOCOLS, output_stem
from scripts.overlap_analysis import build_label_columns
from src.data_loader import UNSW_RAW_COLUMNS, load_unsw
from src.evaluation.overlap import best_possible_accuracy
from src.utils.config_loader import choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path

ALL_PROTOCOLS = tuple(name for name, _ in PROTOCOLS)


def ceiling(config: dict, feature_sets: dict, pool: str, raw: pd.DataFrame, label_col: str) -> tuple[str, float, int]:
    """(pool label, best-possible accuracy, number of raw columns) of a pool on the known-class rows `raw`."""
    cfg = copy.deepcopy(config)
    cfg["feature_selection"]["pool"] = pool
    cfg, sets = choose_pool(cfg, feature_sets, raw.columns)
    raw_features = [c for c in UNSW_RAW_COLUMNS if c in raw.columns and c in sets["feature_pool"]]
    return pool_label(sets), round(best_possible_accuracy(raw, raw_features, label_col), 4), len(raw_features)


def accuracy_rows(config: dict, feature_sets: dict, pools: list[str], tuned: list[str]) -> pd.DataFrame:
    metrics_dir = get_metrics_dir(config)
    data = config["data"]
    raw = load_unsw(resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]),
                    seed=config["project"]["seed"], synthetic_rows=data["synthetic_fallback_rows"], drop_duplicates=False)
    raw = raw[~raw[data["fine_grained_target_column"]].isin(data["unknown_attack_categories"])].copy()
    label_col = build_label_columns(raw, config, [data["label_scheme"]])[data["label_scheme"]]

    def accuracy(stem: str, pool: str, split: str):
        path = metrics_dir / f"{stem}_summary.csv"
        if not path.exists():
            return None
        s = pd.read_csv(path)
        s = s[(s["pool"] == pool) & (s["split"] == split) & (s["metric"] == "accuracy")]
        return None if s.empty else (float(s["mean"].iloc[0]), float(s["std"].iloc[0]))

    rows = []
    for pool in pools:
        label, bound, n_raw = ceiling(config, feature_sets, pool, raw, label_col)
        for variant in [None, *tuned]:
            row = {"pool": label, "hyperparameters": "default" if variant is None else f"tuned_{variant}", "raw_columns": n_raw,
                   "ceiling": bound}
            for split in ALL_PROTOCOLS:
                if variant is None:  # the default run is stored under its own pool list; fall back to the single-pool file
                    found = accuracy(output_stem(None, ALL_PROTOCOLS, DEFAULT_POOLS), pool, split) \
                        or accuracy(output_stem(None, ALL_PROTOCOLS, (pool,)), pool, split)
                else:
                    found = accuracy(output_stem(variant, ("official",), DEFAULT_POOLS), pool, split) if split == "official" else None
                row[f"{split}_mean"], row[f"{split}_std"] = found if found else (float("nan"), float("nan"))
            if not pd.isna(row["official_mean"]):
                row["official_minus_ceiling"] = round(row["official_mean"] - bound, 4)
                row["pooled_minus_ceiling"] = round(row["pooled_random_mean"] - bound, 4) if not pd.isna(row["pooled_random_mean"]) else float("nan")
                rows.append(row)
    return pd.DataFrame(rows).round(4)


def render(df: pd.DataFrame) -> str:
    fmt = lambda m, s: "n/a" if pd.isna(m) else f"{m:.4f} +/- {s:.4f}"  # noqa: E731
    lines = ["# Accuracy: official split, pooled split and the best-possible ceiling", "",
             "Scheme `current`, whole-pool tier; mean +/- std over seeds. The ceiling is what ANY classifier could reach on the pool's raw "
             "columns (rows with identical feature vectors can only get one label); it is not a target for the model.", "",
             "| pool | hyperparameters | official split | pooled random split | ceiling | official - ceiling | pooled - ceiling |",
             "|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        lines.append(f"| {r.pool} | {r.hyperparameters} | {fmt(r.official_mean, r.official_std)} | {fmt(r.pooled_random_mean, r.pooled_random_std)} | "
                     f"{r.ceiling:.4f} | {r.official_minus_ceiling:+.4f} | " + ("n/a" if pd.isna(r.pooled_minus_ceiling) else f"{r.pooled_minus_ceiling:+.4f}") + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["base", "full"])
    parser.add_argument("--tuned", nargs="*", choices=["f1", "auc"], default=[])
    args = parser.parse_args()
    config = load_config()
    df = accuracy_rows(config, load_feature_sets(), args.pools, args.tuned)
    metrics_dir = get_metrics_dir(config)
    tag = "_".join(df["pool"].drop_duplicates()) + (f"_tuned_{'_'.join(args.tuned)}" if args.tuned else "")
    df.to_csv(metrics_dir / f"accuracy_three_numbers_{tag}.csv", index=False)
    (metrics_dir / f"accuracy_three_numbers_{tag}.md").write_text(render(df), encoding="utf-8")
    print(render(df))


if __name__ == "__main__":
    main()
