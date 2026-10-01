"""CLI: fit the preprocessing pipeline on data/processed/unsw_combined.csv (produced by
load_data.py) using the active feature set from config, and cache the transformed
arrays + fitted preprocessor. Run from the project root:

    python data/scripts/preprocess.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.preprocessing import Preprocessor, add_merged_label, split_known_unknown
from src.utils.config_loader import get_active_features, get_label_scheme, load_config, load_feature_sets, resolve_path
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    config = load_config()
    feature_sets = load_feature_sets()
    processed_dir = resolve_path(config["paths"]["processed_dir"])

    unsw_csv = processed_dir / "unsw_combined.csv"
    if not unsw_csv.exists():
        raise FileNotFoundError(f"{unsw_csv} not found — run data/scripts/load_data.py first.")

    df = pd.read_csv(unsw_csv)
    df = add_merged_label(df, get_label_scheme(config)[1],
                           source_column=config["data"]["fine_grained_target_column"], target_column=config["data"]["target_column"])
    known_df, unknown_df = split_known_unknown(df, config["data"]["unknown_attack_categories"], config["data"]["target_column"])

    features = get_active_features(config, feature_sets)
    preprocessor = Preprocessor(feature_list=features, target_column=config["data"]["target_column"]).fit(known_df)
    X, y = preprocessor.transform(known_df)

    out_dir = processed_dir
    np.save(out_dir / "X.npy", X)
    np.save(out_dir / "y.npy", y)
    unknown_df.to_csv(out_dir / "unknown_holdout.csv", index=False)
    joblib.dump(preprocessor, out_dir / "preprocessor.pkl")

    logger.info(f"Preprocessed {X.shape[0]} rows x {X.shape[1]} features -> {out_dir}")


if __name__ == "__main__":
    main()
