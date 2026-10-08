"""Streaming, cached CICIDS2017 loader: same frame as load_cic, file order kept, header variants handled."""
import numpy as np
import pandas as pd
import pytest

from src import data_loader
from src.data_loader import load_cic, load_cic_common

RAW = ["Destination Port", "Flow Duration", "Total Fwd Packets", "Total Backward Packets", "Total Length of Fwd Packets", "Total Length of Bwd Packets", "Flow Bytes/s",
       "Flow Packets/s", "Fwd Packet Length Mean", "Bwd Packet Length Mean", "Label"]


def write_csv(path, n=2500, spaces=False):
    rng = np.random.default_rng(0)
    labels = np.where(np.arange(n) % 7 == 0, "DoS Hulk", "BENIGN").astype(object)
    labels[5] = "Web Attack \ufffd Brute Force"                                     # the encoding defect of the public files
    df = pd.DataFrame({"Destination Port": rng.integers(1, 9000, n), "Flow Duration": rng.integers(1, 10**7, n), "Total Fwd Packets": rng.integers(1, 50, n),
                       "Total Backward Packets": rng.integers(0, 50, n), "Total Length of Fwd Packets": rng.integers(0, 5000, n), "Total Length of Bwd Packets": rng.integers(0, 5000, n),
                       "Flow Bytes/s": rng.random(n) * 1e5, "Flow Packets/s": rng.random(n) * 1e3, "Fwd Packet Length Mean": rng.random(n) * 200, "Bwd Packet Length Mean": rng.random(n) * 200,
                       "Label": labels})
    df.loc[3, "Flow Packets/s"] = np.inf
    if spaces:
        df.columns = [f" {c}" for c in df.columns]
    df.to_csv(path, index=False, encoding="utf-8")


def test_streaming_loader_equals_load_cic_and_keeps_file_order(tmp_path):
    path = tmp_path / "cic.csv"
    write_csv(path)
    whole, streamed = load_cic(path), load_cic_common(path, chunk_rows=700)       # 4 chunks
    pd.testing.assert_frame_equal(whole, streamed)
    assert (streamed["attack_cat"].iloc[[0, 7, 14]] == "DoS Hulk").all() and streamed["attack_cat"].iloc[1] == "Normal"
    assert streamed["attack_cat"].iloc[5] == "Web Attack - Brute Force" and "day" not in streamed.columns       # a small file has no day structure
    assert "destination port" not in streamed.columns and streamed["label"].isin([0, 1]).all()
    assert streamed["dur"].max() <= 10.0                                           # microseconds converted to seconds


def test_header_with_leading_spaces_and_the_parquet_cache(tmp_path):
    path, cache = tmp_path / "cic.csv", tmp_path / "cache" / "cic.parquet"
    write_csv(path, spaces=True)
    first = load_cic_common(path, cache_path=cache, chunk_rows=1000)
    assert cache.exists() and set(first.columns) >= {"dur", "spkts", "dmean", "attack_cat", "label"}
    path.write_text("not a csv any more")                                          # the cache is used while it is newer than the source
    import os, time
    os.utime(cache, (time.time() + 10, time.time() + 10))
    pd.testing.assert_frame_equal(first, load_cic_common(path, cache_path=cache))


def test_day_column_is_added_only_for_the_known_file_size(tmp_path, monkeypatch):
    path = tmp_path / "cic.csv"
    write_csv(path, n=2500)
    monkeypatch.setattr(data_loader, "CIC_DAY_FILES", [("A", 1000), ("B", 1500)])
    monkeypatch.setattr(data_loader, "CIC_TOTAL_ROWS", 2500)
    df = load_cic_common(path, chunk_rows=900)
    assert df["day"].iloc[0] == "A" and df["day"].iloc[999] == "A" and df["day"].iloc[1000] == "B" and df["day"].iloc[-1] == "B"


def test_known_day_files_sum_to_the_combined_file():
    assert data_loader.CIC_TOTAL_ROWS == 2830743 and len(data_loader.CIC_DAY_FILES) == 8
