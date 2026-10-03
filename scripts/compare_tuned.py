"""Tuned vs default hyperparameters on the official split (mean +/- std over seeds), per feature pool:

    python scripts/compare_tuned.py [--pools base full] [--objectives f1 auc]

Reads the default run (results/metrics/<model.type>/headline_summary.csv) and the tuned runs
(headline_tuned_<objective>_official_summary.csv, from `pipelines/run_headline_seeds.py --tuned <objective> --protocols official`),
and writes tuned_vs_default.csv / .md with one row per pool and variant, plus the difference to the default in the last rows.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.run_headline_seeds import DEFAULT_POOLS, KEY_METRICS, PROTOCOLS, output_stem
from src.utils.config_loader import get_metrics_dir, load_config

COLUMNS = ["accuracy", "f1", "detection_rate", "false_positive_rate", "normal_to_Fuzzers", "roc_auc_attack_vs_normal", "ece",
           "unknown_detection_rate", "unknown_auroc"]


def tuned_vs_default(metrics_dir: Path, pools: list[str], objectives: list[str]) -> pd.DataFrame:
    """Rows (pool, hyperparameters) with the official-split mean / std of each COLUMNS metric and `<metric>_vs_default`."""
    protocols = tuple(name for name, _ in PROTOCOLS)
    sources = {"default": metrics_dir / f"{output_stem(None, protocols, DEFAULT_POOLS)}_summary.csv",
               **{f"tuned_{o}": metrics_dir / f"{output_stem(o, ('official',), DEFAULT_POOLS)}_summary.csv" for o in objectives}}
    rows = []
    for pool in pools:
        default_means = {}
        for variant, path in sources.items():
            s = pd.read_csv(path)
            s = s[(s["pool"] == pool) & (s["split"] == "official") & (s["metric"].isin(COLUMNS))].set_index("metric")
            row = {"pool": pool, "hyperparameters": variant}
            for m in COLUMNS:
                row[f"{m}_mean"], row[f"{m}_std"] = s.loc[m, "mean"], s.loc[m, "std"]
                if variant == "default":
                    default_means[m] = s.loc[m, "mean"]
                else:
                    row[f"{m}_vs_default"] = round(s.loc[m, "mean"] - default_means[m], 4)
            rows.append(row)
    return pd.DataFrame(rows)


def render(df: pd.DataFrame) -> str:
    lines = ["# Tuned vs default hyperparameters, official split (mean +/- std over seeds)", "",
             "Hyperparameters and the class-weight exponent were chosen on the validation split only (pipelines/tune_xgboost.py). "
             "`vs default` is the tuned mean minus the default mean.", "",
             "| pool | hyperparameters | " + " | ".join(COLUMNS) + " |", "|---|---|" + "---|" * len(COLUMNS)]
    for r in df.to_dict("records"):
        cells = []
        for m in COLUMNS:
            cell = f"{r[f'{m}_mean']:.4f} +/- {r[f'{m}_std']:.4f}"
            cells.append(cell + (f" ({r[f'{m}_vs_default']:+.4f})" if f"{m}_vs_default" in r and not pd.isna(r[f"{m}_vs_default"]) else ""))
        lines.append(f"| {r['pool']} | {r['hyperparameters']} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["base", "full"])
    parser.add_argument("--objectives", nargs="*", choices=["f1", "auc"], default=["f1", "auc"])
    args = parser.parse_args()
    metrics_dir = get_metrics_dir(load_config())
    df = tuned_vs_default(metrics_dir, args.pools, args.objectives)
    df.to_csv(metrics_dir / "tuned_vs_default.csv", index=False)
    (metrics_dir / "tuned_vs_default.md").write_text(render(df), encoding="utf-8")
    print(render(df))


if __name__ == "__main__":
    main()
