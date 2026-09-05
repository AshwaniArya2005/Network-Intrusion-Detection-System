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
# generalizable features).
UNSW_RAW_COLUMNS = [
    "dur", "proto", "service", "state", "spkts", "dpkts", "sbytes", "dbytes", "rate",
    "sttl", "dttl", "sload", "dload", "sloss", "dloss", "sinpkt", "dinpkt", "sjit", "djit",
    "swin", "dwin", "stcpb", "dtcpb", "tcprtt", "synack", "ackdat", "smean", "dmean",
    "trans_depth", "response_body_len", "ct_srv_src", "ct_state_ttl", "ct_dst_ltm",
    "ct_src_dport_ltm", "ct_dst_sport_ltm", "ct_dst_src_ltm", "is_ftp_login", "ct_ftp_cmd",
    "ct_flw_http_mthd", "ct_src_ltm", "ct_srv_dst", "is_sm_ips_ports",
]

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


def load_unsw(train_path: str | Path, test_path: str | Path | None = None, seed: int = 42, synthetic_rows: int = 4000) -> pd.DataFrame:
    """Load UNSW-NB15 train (+ optional test) CSVs. Falls back to synthetic data if missing."""
    train_path = Path(train_path)
    frames = []
    if train_path.exists():
        logger.info(f"Loading UNSW-NB15 training data from {train_path}")
        frames.append(pd.read_csv(train_path))
        if test_path is not None and Path(test_path).exists():
            logger.info(f"Loading UNSW-NB15 test data from {test_path}")
            frames.append(pd.read_csv(test_path))
        df = pd.concat(frames, ignore_index=True)
    else:
        logger.warning(f"UNSW-NB15 file not found at {train_path}; using synthetic fallback data.")
        df = make_synthetic_unsw(n_rows=synthetic_rows, seed=seed)

    df.columns = [c.strip().lower() for c in df.columns]
    keep = [c for c in UNSW_RAW_COLUMNS if c in df.columns] + ["attack_cat", "label"]
    df = df[[c for c in keep if c in df.columns]].copy()
    df["attack_cat"] = df["attack_cat"].fillna("Normal").astype(str).str.strip()
    df.loc[df["attack_cat"].str.lower() == "normal", "attack_cat"] = "Normal"
    if "label" not in df.columns:
        df["label"] = (df["attack_cat"] != "Normal").astype(int)
    return df.reset_index(drop=True)


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


def load_cic(cic_path: str | Path, seed: int = 7, synthetic_rows: int = 3000) -> pd.DataFrame:
    """Load a CICIDS2017 CSV and remap it onto the common feature namespace shared with UNSW."""
    cic_path = Path(cic_path)
    if cic_path.exists():
        logger.info(f"Loading CICIDS2017 data from {cic_path}")
        df = pd.read_csv(cic_path)
    else:
        logger.warning(f"CICIDS2017 file not found at {cic_path}; using synthetic fallback data.")
        df = make_synthetic_cic(n_rows=synthetic_rows, seed=seed)

    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns=CIC_TO_COMMON)
    df["attack_cat"] = df["attack_cat"].astype(str).str.strip()
    # The publicly distributed CICIDS2017 CSVs have a known encoding defect: the en-dash
    # in labels like "Web Attack – Brute Force" was corrupted to U+FFFD before release.
    # Normalize it to a plain hyphen so it doesn't render as a replacement-character glyph.
    df["attack_cat"] = df["attack_cat"].str.replace("�", "-", regex=False)
    df.loc[df["attack_cat"].str.upper() == "BENIGN", "attack_cat"] = "Normal"
    df["label"] = (df["attack_cat"] != "Normal").astype(int)

    common_cols = [c for c in CIC_TO_COMMON.values() if c in df.columns and c != "attack_cat"]
    return df[common_cols + ["attack_cat", "label"]].reset_index(drop=True)
