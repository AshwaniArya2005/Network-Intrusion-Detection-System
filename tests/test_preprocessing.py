import numpy as np
import pandas as pd
import pytest

from src.data_loader import make_synthetic_unsw
from src.preprocessing import UNDEFINED_RATIO, Preprocessor, engineer_features, split_known_unknown

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


def test_zero_denominator_ratios_use_a_distinct_sentinel():
    """No reply (dbytes=0) must not look like no data sent (sbytes=0): both used to be 0."""
    df = pd.DataFrame({"sbytes": [100.0, 0.0, 0.0], "dbytes": [0.0, 50.0, 0.0],
                       "spkts": [4.0, 0.0, 0.0], "dpkts": [0.0, 3.0, 0.0], "dur": [1.0, 1.0, 1.0]})
    out = engineer_features(df)
    assert out["byte_ratio"].tolist() == [UNDEFINED_RATIO, 0.0, UNDEFINED_RATIO]
    assert out["avg_pkt_size"].tolist() == [25.0, 50 / 3, UNDEFINED_RATIO]


def test_transform_raises_on_unseen_target_label(df):
    pre = Preprocessor(feature_list=FEATURES).fit(df)
    novel = df.copy()
    novel.loc[0, "attack_cat"] = "NeverSeen"
    with pytest.raises(ValueError, match="NeverSeen"):
        pre.transform(novel)
    assert pre.transform_features(novel).shape[0] == len(novel)  # feature-only path still works


def test_missing_categoricals_are_encoded_as_unknown_not_nan_string(df):
    df = df.copy()
    df.loc[:5, "proto"] = None
    pre = Preprocessor(feature_list=FEATURES).fit(df)
    classes = list(pre.label_encoders["proto"].classes_)
    assert "unknown" in classes and "nan" not in classes


def test_required_columns_exclude_engineered_features():
    pre = Preprocessor(feature_list=["rate", "proto", "total_bytes", "byte_ratio"])
    assert pre.required_columns == ["rate", "proto", "sbytes", "dbytes"]


def test_required_columns_include_base_inputs_of_engineered_features():
    """pkt_ratio needs spkts/dpkts even when neither is itself a feature."""
    pre = Preprocessor(feature_list=["rate", "pkt_ratio"])
    assert set(pre.required_columns) == {"rate", "spkts", "dpkts"}


def test_missing_base_column_raises_instead_of_silently_becoming_zero(df):
    with pytest.raises(ValueError, match="spkts"):
        engineer_features(df.drop(columns=["spkts"]))
    pre = Preprocessor(feature_list=["rate", "pkt_ratio"]).fit(df)
    with pytest.raises(ValueError, match="spkts"):
        pre.transform_features(df.drop(columns=["spkts"]))
