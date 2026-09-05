"""CLI: load raw UNSW-NB15 / CICIDS2017 data (or synthesize it) and cache as CSV
under data/processed/. Run from the project root:

    python data/scripts/load_data.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.data_loader import load_cic, load_unsw
from src.utils.config_loader import load_config, resolve_path
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    config = load_config()
    paths = config["paths"]
    processed_dir = resolve_path(paths["processed_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)

    unsw_df = load_unsw(
        resolve_path(paths["unsw_train"]),
        resolve_path(paths["unsw_test"]),
        seed=config["project"]["seed"],
        synthetic_rows=config["data"]["synthetic_fallback_rows"],
    )
    unsw_out = processed_dir / "unsw_combined.csv"
    unsw_df.to_csv(unsw_out, index=False)
    logger.info(f"Saved {len(unsw_df)} UNSW-NB15 rows to {unsw_out}")

    cic_df = load_cic(
        resolve_path(paths["cic_file"]),
        seed=config["project"]["seed"],
        synthetic_rows=config["data"]["synthetic_fallback_rows"],
    )
    cic_out = processed_dir / "cic_combined.csv"
    cic_df.to_csv(cic_out, index=False)
    logger.info(f"Saved {len(cic_df)} CICIDS2017 rows to {cic_out}")


if __name__ == "__main__":
    main()
