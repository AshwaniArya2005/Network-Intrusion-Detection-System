"""Data loading utilities for UNSW-NB15 and CICIDS2017.

Both real loaders expect the raw CSVs described in configs/config.yaml under
`paths.unsw_train` / `paths.unsw_test` / `paths.cic_file`. Since those datasets
require a manual download (see scripts/download_datasets.py), synthetic
fallback generators are provided so the rest of the pipeline (training, XAI,
dashboard) is runnable end-to-end without the real data for development/testing.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

ATTACK_CATEGORIES = [
    "Normal", "Generic", "Exploits", "Fuzzers", "DoS",
    "Reconnaissance", "Analysis", "Backdoor", "Shellcode", "Worms",
]

# Raw UNSW-NB15 numeric/categorical columns used by this project (id, ip, port,
# and timestamp columns are dropped as they are per-flow identifiers, not
# generalizable features). The official training/testing set has all of these; this
# project's data/raw copy lacks 8 (see EXTRA_OFFICIAL_COLUMNS) and loads with the rest.
UNSW_RAW_COLUMNS = [
    "dur", "proto", "service", "state", "spkts", "dpkts", "sbytes", "dbytes", "rate",
    "sttl", "dttl", "sload", "dload", "sloss", "dloss", "sinpkt", "dinpkt", "sjit", "djit",
    "swin", "dwin", "stcpb", "dtcpb", "tcprtt", "synack", "ackdat", "smean", "dmean",
    "trans_depth", "response_body_len", "ct_srv_src", "ct_state_ttl", "ct_dst_ltm",
    "ct_src_dport_ltm", "ct_dst_sport_ltm", "ct_dst_src_ltm", "is_ftp_login", "ct_ftp_cmd",
    "ct_flw_http_mthd", "ct_src_ltm", "ct_srv_dst", "is_sm_ips_ports",
]

# Official columns missing from the local data/raw copy; when all are present the 48-feature
# `feature_pool_full` is used (configs/feature_sets.yaml).
EXTRA_OFFICIAL_COLUMNS = ["sttl", "dttl", "ct_state_ttl", "ct_srv_src", "ct_dst_ltm", "ct_src_ltm", "ct_srv_dst", "ct_dst_src_ltm"]

PROTOCOLS = ["tcp", "udp", "arp", "ospf", "icmp"]
SERVICES = ["-", "http", "ftp", "smtp", "ssh", "dns", "ftp-data", "pop3", "dhcp"]
STATES = ["FIN", "CON", "INT", "REQ", "RST"]


def _rng(seed: int = 42) -> np.random.Generator:
    return np.random.default_rng(seed)


def make_synthetic_unsw(n_rows: int = 4000, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic UNSW-NB15-shaped dataset for offline dev/testing.

    Not real traffic — used only when the real dataset files are absent, so the
    pipeline can be exercised end-to-end (train, explain, evaluate, dashboard).
    """
    rng = _rng(seed)
    n_classes = len(ATTACK_CATEGORIES)
    labels = rng.choice(ATTACK_CATEGORIES, size=n_rows, p=[0.55] + [0.05] * (n_classes - 1))

    df = pd.DataFrame({
        "dur": rng.exponential(1.0, n_rows),
        "proto": rng.choice(PROTOCOLS, n_rows),
        "service": rng.choice(SERVICES, n_rows),
        "state": rng.choice(STATES, n_rows),
        "spkts": rng.poisson(10, n_rows).astype(float),
        "dpkts": rng.poisson(8, n_rows).astype(float),
        "sbytes": rng.exponential(500, n_rows),
        "dbytes": rng.exponential(400, n_rows),
        "rate": rng.exponential(50, n_rows),
        "sttl": rng.integers(1, 255, n_rows).astype(float),
        "dttl": rng.integers(1, 255, n_rows).astype(float),
        "sload": rng.exponential(1000, n_rows),
        "dload": rng.exponential(800, n_rows),
        "sloss": rng.poisson(1, n_rows).astype(float),
        "dloss": rng.poisson(1, n_rows).astype(float),
        "sinpkt": rng.exponential(10, n_rows),
        "dinpkt": rng.exponential(10, n_rows),
        "sjit": rng.exponential(5, n_rows),
        "djit": rng.exponential(5, n_rows),
        "swin": rng.integers(0, 65535, n_rows).astype(float),
        "dwin": rng.integers(0, 65535, n_rows).astype(float),
        "stcpb": rng.integers(0, 2**31, n_rows).astype(float),
        "dtcpb": rng.integers(0, 2**31, n_rows).astype(float),
        "tcprtt": rng.exponential(0.1, n_rows),
        "synack": rng.exponential(0.05, n_rows),
        "ackdat": rng.exponential(0.05, n_rows),
        "smean": rng.exponential(200, n_rows),
        "dmean": rng.exponential(200, n_rows),
        "trans_depth": rng.integers(0, 5, n_rows).astype(float),
        "response_body_len": rng.exponential(300, n_rows),
        "ct_srv_src": rng.integers(0, 20, n_rows).astype(float),
        "ct_state_ttl": rng.integers(0, 10, n_rows).astype(float),
        "ct_dst_ltm": rng.integers(0, 20, n_rows).astype(float),
        "ct_src_dport_ltm": rng.integers(0, 20, n_rows).astype(float),
        "ct_dst_sport_ltm": rng.integers(0, 20, n_rows).astype(float),
        "ct_dst_src_ltm": rng.integers(0, 20, n_rows).astype(float),
        "is_ftp_login": rng.integers(0, 2, n_rows).astype(float),
        "ct_ftp_cmd": rng.integers(0, 5, n_rows).astype(float),
        "ct_flw_http_mthd": rng.integers(0, 5, n_rows).astype(float),
        "ct_src_ltm": rng.integers(0, 20, n_rows).astype(float),
        "ct_srv_dst": rng.integers(0, 20, n_rows).astype(float),
        "is_sm_ips_ports": rng.integers(0, 2, n_rows).astype(float),
        "attack_cat": labels,
    })

    # Make DoS/Generic rows look distinct (high rate/packet count) so models
    # and SHAP explanations have real signal to pick up on, not pure noise.
    dos_mask = df["attack_cat"] == "DoS"
    df.loc[dos_mask, "rate"] *= 20
    df.loc[dos_mask, "spkts"] *= 15
    df.loc[dos_mask, "sttl"] = rng.integers(1, 30, dos_mask.sum()).astype(float)

    df["label"] = (df["attack_cat"] != "Normal").astype(int)
    logger.info(f"Generated synthetic UNSW-NB15-like dataset: {n_rows} rows")
    return df


def make_synthetic_cic(n_rows: int = 3000, seed: int = 7) -> pd.DataFrame:
    """Generate a synthetic CICIDS2017-shaped dataset (raw CIC column names)."""
    rng = _rng(seed)
    categories = ["BENIGN", "DoS", "PortScan", "Bot", "Infiltration"]
    labels = rng.choice(categories, size=n_rows, p=[0.6, 0.15, 0.15, 0.05, 0.05])

    df = pd.DataFrame({
        "Flow Duration": rng.exponential(1_000_000, n_rows),
        "Total Fwd Packets": rng.poisson(12, n_rows).astype(float),
        "Total Backward Packets": rng.poisson(9, n_rows).astype(float),
        "Total Length of Fwd Packets": rng.exponential(600, n_rows),
        "Total Length of Bwd Packets": rng.exponential(500, n_rows),
        "Flow Bytes/s": rng.exponential(2000, n_rows),
        "Flow Packets/s": rng.exponential(60, n_rows),
        "Fwd Packet Length Mean": rng.exponential(150, n_rows),
        "Bwd Packet Length Mean": rng.exponential(150, n_rows),
        "Label": labels,
    })
    dos_mask = df["Label"] == "DoS"
    df.loc[dos_mask, "Flow Packets/s"] *= 25
    df.loc[dos_mask, "Total Fwd Packets"] *= 15
    logger.info(f"Generated synthetic CICIDS2017-like dataset: {n_rows} rows")
    return df


def _class_split_counts(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["attack_cat", "split"]).size().unstack(fill_value=0).reindex(columns=["train", "test"], fill_value=0)


def load_unsw(train_path: str | Path, test_path: str | Path | None = None, seed: int = 42, synthetic_rows: int = 4000,
              drop_duplicates: bool = True) -> pd.DataFrame:
    """Load UNSW-NB15 train (+ optional test) CSVs. Falls back to synthetic data if missing.

    Adds a `split` column ("train" / "test" = which official file a row came from;
    synthetic rows are all "train"). Exact duplicate rows are dropped (logged; `drop_duplicates=False` keeps them), keeping
    the first occurrence so a row present in both files stays in train and cannot leak
    into the official test split.
    """
    train_path = Path(train_path)
    if train_path.exists():
        logger.info(f"Loading UNSW-NB15 training data from {train_path}")
        frames = [pd.read_csv(train_path).assign(split="train")]
        if test_path is not None and Path(test_path).exists():
            logger.info(f"Loading UNSW-NB15 test data from {test_path}")
            frames.append(pd.read_csv(test_path).assign(split="test"))
        df = pd.concat(frames, ignore_index=True)
    else:
        logger.warning(f"SYNTHETIC DATA: UNSW-NB15 file not found at {train_path}; using generated fallback data. Numbers from this run are not results; fetch the real files with python scripts/download_datasets.py.")
        df = make_synthetic_unsw(n_rows=synthetic_rows, seed=seed).assign(split="train")

    df.columns = [c.strip().lower() for c in df.columns]
    keep = [c for c in UNSW_RAW_COLUMNS if c in df.columns] + ["attack_cat", "label", "split"]
    df = df[[c for c in keep if c in df.columns]].copy()
    df["attack_cat"] = df["attack_cat"].fillna("Normal").astype(str).str.strip()
    df.loc[df["attack_cat"].str.lower() == "normal", "attack_cat"] = "Normal"
    if "label" not in df.columns:
        df["label"] = (df["attack_cat"] != "Normal").astype(int)

    n_before = len(df)
    counts_before = _class_split_counts(df)
    if drop_duplicates:
        df = df.drop_duplicates(subset=[c for c in df.columns if c != "split"], keep="first").reset_index(drop=True)
    logger.info(f"Dropped {n_before - len(df)} exact duplicate UNSW-NB15 rows ({n_before} -> {len(df)})")
    df.attrs["counts_before_dedup"] = counts_before  # per attack_cat x official file, for split_summary.csv
    return df


# Renames CIC's raw column names into the same semantic namespace UNSW uses, so
# cross_dataset.py can compare feature importance on genuinely common features.
CIC_TO_COMMON = {
    "flow duration": "dur",
    "total fwd packets": "spkts",
    "total backward packets": "dpkts",
    "total length of fwd packets": "sbytes",
    "total length of bwd packets": "dbytes",
    "flow packets/s": "rate",
    "fwd packet length mean": "smean",
    "bwd packet length mean": "dmean",
    "label": "attack_cat",
}


def stratified_subsample(df: pd.DataFrame, max_rows: int, column: str = "attack_cat", seed: int = 7) -> pd.DataFrame:
    """Fixed-seed subsample to ~max_rows keeping each `column` class's share (at least one
    row per class); logs the reduction. No-op when df is already small enough."""
    if len(df) <= max_rows:
        return df
    frac = max_rows / len(df)
    out = pd.concat([g.sample(n=max(1, round(len(g) * frac)), random_state=seed) for _, g in df.groupby(column)])
    logger.info(f"Stratified subsample on '{column}': {len(df)} -> {len(out)} rows (seed={seed})")
    return out.reset_index(drop=True)


CIC_DAY_FILES = [("Friday-DDoS", 225745), ("Friday-PortScan", 286467), ("Friday-Morning", 191033), ("Monday", 529918), ("Thursday-Afternoon", 288602),
                 ("Thursday-Morning", 170366), ("Tuesday", 445909), ("Wednesday", 692703)]   # the original day files in the order of cicids2017_combined.csv (alphabetical); sums to CIC_TOTAL_ROWS
CIC_TOTAL_ROWS = sum(n for _, n in CIC_DAY_FILES)


def _normalise_cic(df: pd.DataFrame) -> pd.DataFrame:
    """Remap raw CIC columns onto the common namespace and clean the label (shared by load_cic and load_cic_common)."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns=CIC_TO_COMMON)
    df["attack_cat"] = df["attack_cat"].astype(str).str.strip()
    # CIC's Flow Duration is in microseconds; UNSW's dur is in seconds. Convert so the
    # shared `dur` feature (and duration_log) has the same unit in both datasets.
    df["dur"] = pd.to_numeric(df["dur"], errors="coerce") / 1e6
    # The publicly distributed CICIDS2017 CSVs have a known encoding defect: the en-dash
    # in labels like "Web Attack – Brute Force" was corrupted to U+FFFD before release.
    # Normalize it to a plain hyphen so it doesn't render as a replacement-character glyph.
    df["attack_cat"] = df["attack_cat"].str.replace("�", "-", regex=False)
    df.loc[df["attack_cat"].str.upper() == "BENIGN", "attack_cat"] = "Normal"
    df["label"] = (df["attack_cat"] != "Normal").astype(int)
    common_cols = [c for c in CIC_TO_COMMON.values() if c in df.columns and c != "attack_cat"]
    return df[common_cols + ["attack_cat", "label"]].reset_index(drop=True)


def load_cic(cic_path: str | Path, seed: int = 7, synthetic_rows: int = 3000) -> pd.DataFrame:
    """Load a CICIDS2017 CSV and remap it onto the common feature namespace shared with UNSW."""
    cic_path = Path(cic_path)
    if cic_path.exists():
        logger.info(f"Loading CICIDS2017 data from {cic_path}")
        df = pd.read_csv(cic_path)
    else:
        logger.warning(f"SYNTHETIC DATA: CICIDS2017 file not found at {cic_path}; using generated fallback data. Numbers from this run are not results; fetch the real file with python scripts/download_datasets.py.")
        df = make_synthetic_cic(n_rows=synthetic_rows, seed=seed)
    return _normalise_cic(df)


def load_cic_common(cic_path: str | Path, cache_path: str | Path | None = None, chunk_rows: int = 500_000, seed: int = 7, synthetic_rows: int = 3000) -> pd.DataFrame:
    """The same frame as `load_cic` (common columns, attack_cat, label), in FILE ORDER, read in chunks with only the needed columns (the 1 GB file never sits in memory whole) and cached
    as parquet. When the file has the known size of the combined CICIDS2017 file a `day` column names the original day file of every row (CIC_DAY_FILES). Falls back to synthetic data."""
    cic_path = Path(cic_path)
    if not cic_path.exists():
        return load_cic(cic_path, seed, synthetic_rows)
    cache = Path(cache_path) if cache_path else None
    if cache is not None and cache.exists() and cache.stat().st_mtime >= cic_path.stat().st_mtime:
        logger.info(f"Loading cached common-column CICIDS2017 frame {cache}")
        return pd.read_parquet(cache)
    header = pd.read_csv(cic_path, nrows=0, encoding_errors="replace").columns
    wanted = [c for c in header if c.strip().lower() in CIC_TO_COMMON]
    logger.info(f"Streaming CICIDS2017 from {cic_path}: {len(wanted)} of {len(header)} columns, {chunk_rows} rows per chunk")
    df = pd.concat([_normalise_cic(chunk) for chunk in pd.read_csv(cic_path, usecols=wanted, chunksize=chunk_rows, encoding_errors="replace")], ignore_index=True)
    if len(df) == CIC_TOTAL_ROWS:
        df["day"] = np.repeat([name for name, _ in CIC_DAY_FILES], [n for _, n in CIC_DAY_FILES])
    if cache is not None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache, index=False)
        logger.info(f"Cached {len(df)} rows to {cache}")
    return df
