"""What each split protocol trains on, by official source file (leakage check 4):

    python scripts/pooled_reference_composition.py

The official protocol trains on (part of) the official training file and tests on the official test file. The pooled random
protocol pools the known rows of BOTH files and splits them at random, so its training split contains rows of the official test
file, interleaved with the very rows it is tested on. Writes pooled_reference_composition.csv under results/metrics/<model.type>/:
rows per (protocol, part, source file) and the share of each source file's known rows that lies in that part.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.train_pipeline import load_split_data
from src.utils.config_loader import get_metrics_dir, load_config


def composition(protocols: dict[str, dict[str, pd.DataFrame]]) -> pd.DataFrame:
    """`protocols`: name -> {part: frame with a `split` column holding the source file ("train" / "test")}. One row per
    (protocol, part, source file): rows, share of the source file's known rows in this part, share of the part from this file."""
    rows = []
    for name, parts in protocols.items():
        totals = pd.concat(parts.values())["split"].value_counts()
        for part, frame in parts.items():
            counts = frame["split"].value_counts()
            for source in ("train", "test"):
                n = int(counts.get(source, 0))
                rows.append({"protocol": name, "part": part, "source_file": source, "rows": n,
                             "share_of_source_file": round(n / totals[source], 4) if source in totals else float("nan"),
                             "share_of_part": round(n / max(len(frame), 1), 4)})
    return pd.DataFrame(rows)


def main() -> None:
    config = load_config()
    protocols = {}
    for name, official in (("official", True), ("pooled_random", False)):
        s = load_split_data(config, use_official_split=official)
        protocols[name] = {"train": s.train, "val": s.val, "test": s.test}
    table = composition(protocols)
    out = get_metrics_dir(config) / "pooled_reference_composition.csv"
    table.to_csv(out, index=False)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
