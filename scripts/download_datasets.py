"""Dataset acquisition helper.

UNSW-NB15 and CICIDS2017 require a manual download from their official portals
(no direct-download API exists), so this script:
  1. Prints the official download links + where to place the files.
  2. Generates synthetic demo data in their place, so the rest of the pipeline
     (training, XAI, dashboard) is runnable immediately without waiting on a
     multi-GB manual download. Replace the generated CSVs with the real
     datasets for actual research results.

Run from the project root:
    python scripts/download_datasets.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.model_selection import train_test_split

from src.data_loader import EXTRA_OFFICIAL_COLUMNS, make_synthetic_cic, make_synthetic_unsw
from src.utils.config_loader import load_config, resolve_path
from src.utils.logger import get_logger

logger = get_logger(__name__)

INSTRUCTIONS = """
=====================================================================
 Manual dataset download (required for real research results)
=====================================================================
UNSW-NB15:
  https://research.unsw.edu.au/projects/unsw-nb15-dataset
  -> the page links an interactive OneDrive folder ("a part of this dataset is
     configured as a training set and testing set"); download from it
       UNSW_NB15_training-set.csv   (175,341 rows)
       UNSW_NB15_testing-set.csv    (82,332 rows)
     and save them as:
       data/raw/unsw_nb15_train.csv
       data/raw/unsw_nb15_test.csv
  The official files have all 42 feature columns. Some mirrors (and the copy this
  project was first developed on) omit 8: sttl, dttl, ct_state_ttl, ct_srv_src,
  ct_dst_ltm, ct_src_ltm, ct_srv_dst, ct_dst_src_ltm. With all 8 present the loader
  switches to the 48-feature pool automatically. This script reports which are missing.

CICIDS2017:
  https://www.unb.ca/cic/datasets/ids-2017.html
  -> download the 8 day CSVs (MachineLearningCSV.zip) and concatenate them
     (matching header, e.g. `pd.concat` or `csvstack`) into a single file:
       data/raw/cicids2017_combined.csv

Until those files are in place, this script writes small SYNTHETIC
stand-ins to the same paths so the pipeline is runnable end-to-end.
=====================================================================
"""


def missing_extra_columns(raw_dir: Path | str, files: tuple[str, ...] = ("unsw_nb15_train.csv", "unsw_nb15_test.csv")) -> dict[str, list[str]]:
    """For each UNSW CSV under `raw_dir`, which of the 8 extra official columns its header lacks
    ({} for files that don't exist). Reads only the header row."""
    out = {}
    for name in files:
        path = Path(raw_dir) / name
        if path.exists():
            header = {c.strip().lower() for c in pd.read_csv(path, nrows=0).columns}
            out[name] = [c for c in EXTRA_OFFICIAL_COLUMNS if c not in header]
    return out


def main() -> None:
    print(INSTRUCTIONS)
    config = load_config()
    raw_dir = resolve_path(config["paths"]["raw_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)

    for name, missing in missing_extra_columns(raw_dir).items():
        logger.info(f"{name}: " + (f"missing official columns {missing}" if missing else "has all 8 extra official columns"))

    unsw_train_path = resolve_path(config["paths"]["unsw_train"])
    unsw_test_path = resolve_path(config["paths"]["unsw_test"])
    cic_path = resolve_path(config["paths"]["cic_file"])

    if unsw_train_path.exists() and unsw_test_path.exists():
        logger.info("UNSW-NB15 files already present, skipping synthetic generation.")
    else:
        df = make_synthetic_unsw(n_rows=config["data"]["synthetic_fallback_rows"], seed=config["project"]["seed"])
        train_df, test_df = train_test_split(df, test_size=0.3, random_state=config["project"]["seed"])
        train_df.to_csv(unsw_train_path, index=False)
        test_df.to_csv(unsw_test_path, index=False)
        logger.info(f"Wrote synthetic UNSW-NB15 stand-in data to {unsw_train_path} / {unsw_test_path}")

    if cic_path.exists():
        logger.info("CICIDS2017 file already present, skipping synthetic generation.")
    else:
        cic_df = make_synthetic_cic(n_rows=config["data"]["synthetic_fallback_rows"], seed=config["project"]["seed"])
        cic_df.to_csv(cic_path, index=False)
        logger.info(f"Wrote synthetic CICIDS2017 stand-in data to {cic_path}")


if __name__ == "__main__":
    main()
