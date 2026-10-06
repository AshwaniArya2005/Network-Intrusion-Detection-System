"""Optional 48-feature pool when the 8 extra official columns are present; downloader check."""
from scripts.download_datasets import missing_extra_columns
from src.data_loader import EXTRA_OFFICIAL_COLUMNS, load_unsw, make_synthetic_unsw
from src.utils.config_loader import choose_pool, load_config, load_feature_sets
from src.xai.narrative_generator import FEATURE_DESCRIPTIONS


def _write(path, df):
    df.to_csv(path, index=False)
    return path


def test_loader_and_pool_choice_with_and_without_the_8_extra_columns(tmp_path):
    full = make_synthetic_unsw(n_rows=300, seed=1)
    trimmed = full.drop(columns=EXTRA_OFFICIAL_COLUMNS)
    config, fsets = load_config(), load_feature_sets()

    with_cols = load_unsw(_write(tmp_path / "full.csv", full))
    without = load_unsw(_write(tmp_path / "trim.csv", trimmed))
    assert set(EXTRA_OFFICIAL_COLUMNS) <= set(with_cols.columns)
    assert not set(EXTRA_OFFICIAL_COLUMNS) & set(without.columns)

    cfg_full, fs_full = choose_pool(config, fsets, with_cols.columns)
    assert fs_full["pool_name"] == "full" and len(fs_full["feature_pool"]) == 48
    assert cfg_full["experiments"]["feature_sets"] == config["experiments"]["feature_sets_full"]

    cfg_base, fs_base = choose_pool(config, fsets, without.columns)
    assert fs_base["pool_name"] == "base" and len(fs_base["feature_pool"]) == 40
    assert cfg_base["experiments"]["feature_sets"] == config["experiments"]["feature_sets"] == ["40", "30", "20", "15"]

    partial = with_cols.drop(columns=["sttl"])  # all 8 are needed, not just some
    assert choose_pool(config, fsets, partial.columns)[1]["pool_name"] == "base"


def test_pool_option_forces_base_or_full_and_tags_only_the_full_pool(tmp_path):
    import pytest
    from src.utils.config_loader import ranking_path, scheme_tag, tagged
    config, fsets = load_config(), load_feature_sets()
    full_cols = load_unsw(_write(tmp_path / "f.csv", make_synthetic_unsw(n_rows=300, seed=1))).columns
    trimmed_cols = [c for c in full_cols if c not in EXTRA_OFFICIAL_COLUMNS]

    cfg_auto, fs_auto = choose_pool(config, fsets, full_cols)
    assert fs_auto["pool_name"] == "full" and scheme_tag(cfg_auto) == "_48f"
    assert tagged(cfg_auto, "experiment_results.csv") == "experiment_results_48f.csv"

    forced = dict(config, feature_selection=dict(config["feature_selection"], pool="base"))
    cfg_base, fs_base = choose_pool(forced, fsets, full_cols)  # data HAS the columns, base is forced
    assert fs_base["pool_name"] == "base" and len(fs_base["feature_pool"]) == 40 and scheme_tag(cfg_base) == ""
    assert cfg_base["experiments"]["feature_sets"] == ["40", "30", "20", "15"]
    # the two pools get different ranking files
    assert ranking_path(cfg_base).name == "feature_ranking_mutual_info.csv"
    assert ranking_path(cfg_auto).name == "feature_ranking_mutual_info_48f.csv"

    need_full = dict(config, feature_selection=dict(config["feature_selection"], pool="full"))
    with pytest.raises(ValueError, match="lacks official columns"):
        choose_pool(need_full, fsets, trimmed_cols)
    with pytest.raises(ValueError, match="auto, base or full"):
        choose_pool(dict(config, feature_selection=dict(config["feature_selection"], pool="x")), fsets, full_cols)


def test_tier_names_match_pool_sizes():
    fsets = load_feature_sets()
    assert fsets["feature_sets"]["48"] == len(fsets["feature_pool_full"]) == 48
    assert fsets["feature_sets"]["40"] == len(fsets["feature_pool"]) == 40


def test_downloader_reports_missing_columns(tmp_path):
    full = make_synthetic_unsw(n_rows=20, seed=2)
    _write(tmp_path / "unsw_nb15_train.csv", full)
    _write(tmp_path / "unsw_nb15_test.csv", full.drop(columns=["sttl", "dttl"]))
    assert missing_extra_columns(tmp_path) == {"unsw_nb15_train.csv": [], "unsw_nb15_test.csv": ["sttl", "dttl"]}


def test_narrative_describes_every_connection_count_feature():
    for name in ["ct_src_ltm", "ct_dst_ltm", "ct_dst_src_ltm", "ct_src_dport_ltm", "ct_dst_sport_ltm"]:
        assert name in FEATURE_DESCRIPTIONS
