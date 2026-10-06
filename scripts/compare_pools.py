"""The headline metrics of several feature pools side by side (mean +/- std over seeds), from the headline runs:

    python scripts/compare_pools.py [--pools base full full_no_ttl] [--protocol official]   (a comparison tool: needs the headline runs of each pool,
    e.g. run_headline_seeds.py --pools full base; the other scripts default to pool 48 only)

Reads results/metrics/<model.type>/headline_summary.csv (base + full) and headline_<pool>_summary.csv for any other
pool (pipelines/run_headline_seeds.py --pools <pool>), and writes pool_comparison_<sizes>_<protocol>.csv / .md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.run_headline_seeds import DEFAULT_POOLS, KEY_METRICS, PROTOCOLS, output_stem
from src.utils.config_loader import apply_pool_variant, get_metrics_dir, load_config, load_feature_sets, pool_label, choose_pool


def load_summary(metrics_dir: Path, pool: str) -> pd.DataFrame:
    """The summary rows of `pool` from whichever headline run holds them."""
    protocols = tuple(name for name, _ in PROTOCOLS)
    for stem in (output_stem(None, protocols, DEFAULT_POOLS), output_stem(None, protocols, (pool,))):
        path = metrics_dir / f"{stem}_summary.csv"
        if path.exists():
            s = pd.read_csv(path)
            if (s["pool"] == pool).any():
                return s[s["pool"] == pool]
    raise FileNotFoundError(f"no headline summary for pool {pool!r} in {metrics_dir}; run pipelines/run_headline_seeds.py --pools {pool}")


def compare(metrics_dir: Path, labels: dict[str, str], protocol: str) -> pd.DataFrame:
    """metric x pool table of "mean +/- std" strings for `protocol`; `labels` maps pool name -> column label."""
    cols = {}
    for pool, label in labels.items():
        s = load_summary(metrics_dir, pool)
        s = s[(s["split"] == protocol) & (s["metric"].isin(KEY_METRICS))].set_index("metric")
        cols[label] = s["mean"].map("{:.4f}".format) + " +/- " + s["std"].map("{:.4f}".format)
    return pd.DataFrame(cols).reindex([m for m in KEY_METRICS if m in set.intersection(*(set(c.index) for c in cols.values()))])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["base", "full", "full_no_ttl"])
    parser.add_argument("--protocol", choices=[name for name, _ in PROTOCOLS], default="official")
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    labels = {}
    for pool in args.pools:  # pool size labels from the real pool definitions (data columns are not needed to count features)
        _, sets = choose_pool(apply_pool_variant(config, pool), feature_sets, feature_sets["feature_pool_full"])
        labels[pool] = pool_label(sets)
    table = compare(get_metrics_dir(config), labels, args.protocol)
    tag = "_".join(labels.values()) + f"_{args.protocol}"
    table.to_csv(get_metrics_dir(config) / f"pool_comparison_{tag}.csv")
    lines = [f"# Pools side by side, {args.protocol} split (mean +/- std over seeds)", "",
             "| metric | " + " | ".join(table.columns) + " |", "|---|" + "---|" * len(table.columns)]
    lines += [f"| {m} | " + " | ".join(row.fillna("n/a")) + " |" for m, row in table.iterrows()]
    (get_metrics_dir(config) / f"pool_comparison_{tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
