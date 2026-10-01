"""Reproducible class-overlap analysis for the UNSW-NB15 files named in configs/config.yaml.

    python scripts/overlap_analysis.py                              # pooled train+test, all loaded features
    python scripts/overlap_analysis.py --partition train            # official training partition only
    python scripts/overlap_analysis.py --features base34            # drop the 8 extra official columns
    python scripts/overlap_analysis.py --schemes current wide --no-near

Known classes only (the zero-day categories are excluded), duplicates kept. For each label set
(the original classes, every non-hierarchical entry of `data.label_schemes`, and binary
attack-vs-normal) it writes, under results/metrics/overlap/<partition>_<n>f/:
exact-twin matrices (% of rows and % of distinct vectors), near-twin rates, best-possible
accuracy (duplicates kept and (vector, label) pairs deduplicated), and summary.md.
Methods are documented in src/evaluation/overlap.py.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_loader import EXTRA_OFFICIAL_COLUMNS, UNSW_RAW_COLUMNS, load_unsw
from src.evaluation.overlap import analyse, render_markdown
from src.preprocessing import add_merged_label
from src.utils.config_loader import load_config, resolve_path
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_label_columns(df, config: dict, scheme_names: list[str] | None = None):
    """Add one label column per requested scheme (+ binary) and return {name: column}."""
    data_cfg = config["data"]
    fine = data_cfg["fine_grained_target_column"]
    cols = {"original": fine}
    for name in scheme_names or list(data_cfg["label_schemes"]):
        scheme = data_cfg["label_schemes"][name]
        if scheme.get("hierarchical"):
            continue  # a hierarchy ends in the fine-grained classes: same ceiling as "original"
        col = f"scheme_{name}"
        df[col] = add_merged_label(df, scheme.get("merge_groups") or {}, source_column=fine, target_column=col)[col]
        cols[name] = col
    df["scheme_binary"] = (df[fine] != data_cfg["normal_category"]).astype(int)
    cols["binary"] = "scheme_binary"
    return cols


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--partition", choices=["pooled", "train", "test"], default="pooled")
    parser.add_argument("--features", choices=["all", "base34"], default="all",
                        help="all: every UNSW_RAW_COLUMNS column present; base34: without the 8 extra official columns")
    parser.add_argument("--schemes", nargs="*", help="label_schemes entries (default: all)")
    parser.add_argument("--no-near", action="store_true", help="skip the (slower) near-twin computation")
    args = parser.parse_args()

    config = load_config()
    df = load_unsw(resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]),
                   seed=config["project"]["seed"], synthetic_rows=config["data"]["synthetic_fallback_rows"],
                   drop_duplicates=False)
    df = df[~df[config["data"]["fine_grained_target_column"]].isin(config["data"]["unknown_attack_categories"])].copy()
    if args.partition != "pooled":
        df = df[df["split"] == args.partition].copy()

    features = [c for c in UNSW_RAW_COLUMNS if c in df.columns and not (args.features == "base34" and c in EXTRA_OFFICIAL_COLUMNS)]
    label_cols = build_label_columns(df, config, args.schemes)
    result = analyse(df, features, label_cols, near=not args.no_near)

    out_dir = resolve_path(config["paths"]["results_dir"]) / "metrics" / "overlap" / f"{args.partition}_{len(features)}f"
    out_dir.mkdir(parents=True, exist_ok=True)
    result["ceilings"].to_csv(out_dir / "best_possible_accuracy.csv", index=False)
    for name in result["twin_rows"]:
        result["twin_rows"][name].to_csv(out_dir / f"twin_rows_pct_{name}.csv")
        result["twin_vectors"][name].to_csv(out_dir / f"twin_vectors_pct_{name}.csv")
        if name in result["near"]:
            result["near"][name].to_csv(out_dir / f"near_twin_{name}.csv")
    header = (f"Partition: {args.partition}; {len(df)} known-class rows (duplicates kept); {len(features)} features "
              f"({'base 34' if args.features == 'base34' else 'all loaded'}): {', '.join(features)}.")
    (out_dir / "summary.md").write_text(render_markdown(result, header), encoding="utf-8")
    print(result["ceilings"].to_string(index=False))
    logger.info(f"Wrote overlap analysis to {out_dir}")


if __name__ == "__main__":
    main()
