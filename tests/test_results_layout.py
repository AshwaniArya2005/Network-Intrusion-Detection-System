"""The tidy layout of results/: rankings in results/rankings/, blank rating sheets in results/rating/."""
import copy

import pandas as pd

from src.feature_selection import ranking_is_current, write_feature_ranking
from src.utils.config_loader import load_config, rating_dir, ranking_path, resolve_path

COMMITTED_RANKINGS = ["feature_ranking_mutual_info", "feature_ranking_mutual_info_48f", "feature_ranking_mutual_info_blockval_40f",
                      "feature_ranking_mutual_info_blockval_45f", "feature_ranking_mutual_info_blockval_48f"]


def test_default_ranking_path_is_the_rankings_folder_and_the_committed_files_are_there():
    config = load_config()
    path = ranking_path(config)
    assert path.parent == resolve_path("results/rankings") and path.name == "feature_ranking_mutual_info.csv"
    for stem in COMMITTED_RANKINGS:   # a fresh clone must find every committed ranking and the sidecar that stops it being regenerated
        assert (path.parent / f"{stem}.csv").exists() and (path.parent / f"{stem}.meta.json").exists(), stem
    assert not list(resolve_path("results").glob("feature_ranking_*"))   # nothing left in the root


def test_a_new_ranking_is_written_with_its_sidecar_into_a_missing_rankings_folder(tmp_path):
    config = copy.deepcopy(load_config())
    config["paths"]["feature_ranking"] = str(tmp_path / "results" / "rankings" / "feature_ranking_{source}.csv")
    path = ranking_path(config)
    assert not path.parent.exists()
    write_feature_ranking(pd.Series({"rate": 0.3, "dur": 0.1}), path, signature="abc")
    assert path.exists() and path.with_suffix(".meta.json").exists()
    assert ranking_is_current(path, "abc") and not ranking_is_current(path, "other")


def test_rating_dir_is_results_rating_and_is_created_on_demand(tmp_path):
    assert rating_dir(load_config()) == resolve_path("results/rating")
    config = copy.deepcopy(load_config())
    config["paths"]["rating_dir"] = str(tmp_path / "rating")
    out = rating_dir(config)
    assert out == tmp_path / "rating" and out.is_dir()


def test_both_sheet_scripts_write_into_the_given_rating_folder(tmp_path):
    from scripts.make_ab_sheet import write_sheet as write_ab
    from scripts.make_human_audit_sheet import write_sheet as write_audit
    sheet, key = pd.DataFrame({"sheet_id": [1]}), pd.DataFrame({"sheet_id": [1], "flow": [7]})
    out = tmp_path / "results" / "rating"
    assert write_ab(sheet, key, out) == out / "task_5_5_ab_sheet.csv"
    assert write_audit(sheet, key, out) == out / "task_5_human_audit_sheet.csv"
    assert sorted(p.name for p in out.iterdir()) == ["task_5_5_ab_key.csv", "task_5_5_ab_sheet.csv", "task_5_human_audit_key.csv", "task_5_human_audit_sheet.csv"]
    assert pd.read_csv(out / "task_5_5_ab_key.csv")["flow"].tolist() == [7]
