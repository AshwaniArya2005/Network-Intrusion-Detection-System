"""How much of the Normal-flow false-positive rate is forced by exact feature-vector overlap?

    python scripts/normal_fpr_floor.py

Official train / test files with exact duplicates removed (as the pipelines do), raw columns of each pool (engineered columns are functions of the raw ones, so they add no
information to an exact-twin count). Writes results/metrics/xgboost/normal_fpr_floor_<pools>.csv. Method: `normal_overlap_floor` in src/evaluation/overlap.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.data_loader import UNSW_RAW_COLUMNS, load_unsw
from src.evaluation.overlap import normal_overlap_floor
from src.utils.config_loader import apply_pool_variant, choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path

POOLS = ("full",)   # the primary pool 48; add "base" for the 40-feature comparison pool


def main() -> None:
    config = load_config()
    feature_sets = load_feature_sets()
    data = config["data"]
    raw = load_unsw(resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]), seed=config["project"]["seed"],
                    synthetic_rows=data["synthetic_fallback_rows"])
    rows = []
    for pool in POOLS:
        _, sets = choose_pool(apply_pool_variant(config, pool), feature_sets, raw.columns)
        features = [c for c in UNSW_RAW_COLUMNS if c in raw.columns and c in sets["feature_pool"]]
        result = normal_overlap_floor(raw[raw["split"] == "train"], raw[raw["split"] == "test"], features)
        rows.append({"pool": pool_label(sets), "raw_columns": len(features), **result})
    table = pd.DataFrame(rows)
    stem = "_".join(r["pool"] for r in rows)
    out = get_metrics_dir(config) / f"normal_fpr_floor_{stem}.csv"
    table.round(4).to_csv(out, index=False)
    print(table.round(4).T.to_string())
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
