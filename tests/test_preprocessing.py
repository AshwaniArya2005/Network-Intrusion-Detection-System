import numpy as np
import pytest

from src.data_loader import make_synthetic_unsw
from src.preprocessing import Preprocessor, engineer_features, split_known_unknown

FEATURES = ["sttl", "dttl", "rate", "sbytes", "dbytes", "proto", "service", "state", "total_bytes", "byte_ratio"]


@pytest.fixture
def df():
    return make_synthetic_unsw(n_rows=200, seed=1)


def test_engineer_features_adds_derived_columns(df):
    out = engineer_features(df)
    for col in ["total_bytes", "total_pkts", "byte_ratio", "pkt_ratio", "avg_pkt_size", "duration_log"]:
        assert col in out.columns
    assert not out["byte_ratio"].isna().any()
    assert np.isfinite(out["byte_ratio"]).all()


def test_split_known_unknown(df):
    known, unknown = split_known_unknown(df, unknown_categories=["Worms", "Shellcode"])
    assert len(known) + len(unknown) == len(df)
    assert not unknown.empty or (df["attack_cat"].isin(["Worms", "Shellcode"]).sum() == 0)
    assert not known["attack_cat"].isin(["Worms", "Shellcode"]).any()


def test_preprocessor_fit_transform_shapes(df):
    pre = Preprocessor(feature_list=FEATURES)
    pre.fit(df)
    X, y = pre.transform(df)
    assert X.shape == (len(df), len(FEATURES))
    assert y.shape == (len(df),)
    assert not np.isnan(X).any()


def test_preprocessor_handles_unseen_categorical(df):
    pre = Preprocessor(feature_list=FEATURES).fit(df)
    novel = df.copy()
    novel.loc[0, "proto"] = "totally-new-protocol"
    X, _ = pre.transform(novel)
    assert X.shape[0] == len(novel)


def test_preprocessor_decode_target_roundtrip(df):
    pre = Preprocessor(feature_list=FEATURES).fit(df)
    _, y = pre.transform(df)
    decoded = pre.decode_target(y[:5])
    assert set(decoded).issubset(set(df["attack_cat"].unique()))
