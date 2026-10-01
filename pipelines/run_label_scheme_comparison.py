"""Train the active-set model once per label scheme and compare them side by side:

    python pipelines/run_label_scheme_comparison.py [--schemes current none wide hierarchical]

Writes, under results/metrics/<model.type>/ (the default scheme's other outputs are untouched):
  label_scheme_comparison.csv         official train/test split
  label_scheme_comparison_pooled.csv  pooled random split
  label_scheme_summary.md             the numbers in words; the choice of scheme is the team's

Compare schemes on the scheme-independent columns: attack-vs-normal detection / false-positive
rate, `fine_recall_<class>` (share of an ORIGINAL class's rows predicted as the label that contains
it) and `fine_recall_macro` (their mean), `group_size_share` (share of attack rows inside a merged
group). Macro F1 is kept as `macro_f1_not_comparable_across_schemes`: it averages over a different
number of classes per scheme. `best_possible_accuracy_*` (src/evaluation/overlap.py) rises
mechanically with coarser labels. Models are not saved.
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.train_pipeline import ensure_feature_ranking, load_split_data, train_and_evaluate
from scripts.overlap_analysis import build_label_columns
from src.data_loader import UNSW_RAW_COLUMNS, load_unsw
from src.evaluation.overlap import best_possible_accuracy
from src.utils.config_loader import choose_pool, get_metrics_dir, load_config, load_feature_sets, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

KEEP = ("label_scheme", "feature_set", "feature_pool", "n_features", "accuracy", "detection_rate", "false_positive_rate",
        "fine_recall_macro", "group_size_share")
F1_COLUMN = "macro_f1_not_comparable_across_schemes"


def run_label_scheme_comparison(config: dict, feature_sets: dict, schemes: list[str] | None = None,
                                use_official_split: bool | None = None, output_name: str = "label_scheme_comparison.csv") -> pd.DataFrame:
    schemes = schemes or list(config["data"]["label_schemes"])
    feature_set_name = config["feature_selection"]["active_set"]
    pooled = use_official_split is False

    # Known-class rows with duplicates kept, for the best-possible accuracy of each scheme.
    raw = load_unsw(resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]),
                    seed=config["project"]["seed"], synthetic_rows=config["data"]["synthetic_fallback_rows"],
                    drop_duplicates=False)
    raw = raw[~raw[config["data"]["fine_grained_target_column"]].isin(config["data"]["unknown_attack_categories"])].copy()
    raw_features = [c for c in UNSW_RAW_COLUMNS if c in raw.columns]
    label_cols = build_label_columns(raw, config, schemes)

    rows = []
    for name in schemes:
        scheme_config = copy.deepcopy(config)
        scheme_config["data"]["label_scheme"] = name
        if pooled:  # the pooled split has other training rows, hence its own ranking file
            scheme_config["feature_selection"]["variant_tag"] = "_pooled"
        if pooled or name != "current":  # scratch rankings stay out of results/ (gitignored folder)
            scheme_config["paths"]["feature_ranking"] = f"{config['paths']['results_dir']}/diagnostics/feature_ranking_{{source}}.csv"
        splits = load_split_data(scheme_config, use_official_split=use_official_split)
        scheme_config, scheme_sets = choose_pool(scheme_config, feature_sets, splits.train.columns)
        # Per-scheme ranking, regenerated whenever its training data changed (not only when missing).
        if ensure_feature_ranking(scheme_config, scheme_sets, splits.train):
            logger.info(f"Regenerated the '{name}' feature ranking (missing or training data changed)")
        result = train_and_evaluate(scheme_config, scheme_sets, feature_set_name, False, splits, save_artifacts=False)

        ceiling_col = label_cols.get(name, label_cols["original"])  # a hierarchy ends in the fine-grained classes
        rows.append({
            **{k: result[k] for k in KEEP},
            **{k: v for k, v in result.items() if k.startswith("fine_recall_") and k not in KEEP},
            F1_COLUMN: result["f1"],
            **{k: v for k, v in result.items() if k.startswith("recall_") and "_as_" not in k},
            "n_classes": raw[ceiling_col].nunique(),
            "best_possible_accuracy_dups_kept": round(best_possible_accuracy(raw, raw_features, ceiling_col), 4),
            "best_possible_accuracy_pairs_deduped": round(best_possible_accuracy(raw, raw_features, ceiling_col, True), 4),
        })
    comparison = pd.DataFrame(rows)
    comparison.insert(comparison.columns.get_loc("false_positive_rate") + 1, "rank_false_positive_rate",
                      comparison["false_positive_rate"].rank(method="min").astype(int))
    comparison.insert(comparison.columns.get_loc("fine_recall_macro") + 1, "rank_fine_recall_macro",
                      comparison["fine_recall_macro"].rank(method="min", ascending=False).astype(int))
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(metrics_dir / output_name, index=False)
    logger.info(f"Saved label-scheme comparison to {metrics_dir / output_name}")
    return comparison


def write_label_scheme_summary(official: pd.DataFrame, pooled: pd.DataFrame, path: Path) -> str:
    """Markdown summary of both comparisons. It reports; it does not choose a scheme."""
    def table(df):
        cols = ["label_scheme", "n_classes", "detection_rate", "false_positive_rate", "fine_recall_macro", "group_size_share",
                "rank_fine_recall_macro", "rank_false_positive_rate", "best_possible_accuracy_dups_kept"]
        return "```\n" + df[cols].to_string(index=False) + "\n```"

    def fine(df):
        cols = ["label_scheme"] + [c for c in df.columns if c.startswith("fine_recall_") and c != "fine_recall_macro"]
        return "```\n" + df[cols].to_string(index=False) + "\n```"

    text = f"""# Label scheme comparison (report only; the choice of scheme is the team's)

Compare schemes on the scheme-independent columns below. Macro F1 is NOT comparable across schemes
(it averages over {', '.join(str(int(n)) for n in official['n_classes'])} classes for {', '.join(official['label_scheme'])}), and
`best_possible_accuracy` rises mechanically with coarser labels: it measures what a merge discards,
not which merge is right. `group_size_share` is the share of attack rows inside a merged group, so a
high value means the scheme lumps most attack traffic together. Ranks: 1 = best.

## Official train/test split
{table(official)}

Recall of each ORIGINAL class under each scheme (share of its rows predicted as the label that contains it):
{fine(official)}

## Pooled random split
{table(pooled)}

{fine(pooled)}
"""
    Path(path).write_text(text, encoding="utf-8")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schemes", nargs="*", help="label_schemes entries to compare (default: all)")
    args = parser.parse_args()
    config = load_config()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    feature_sets = load_feature_sets()
    official = run_label_scheme_comparison(config, feature_sets, args.schemes)
    pooled = run_label_scheme_comparison(config, feature_sets, args.schemes, use_official_split=False,
                                         output_name="label_scheme_comparison_pooled.csv")
    write_label_scheme_summary(official, pooled, get_metrics_dir(config) / "label_scheme_summary.md")
    print(official.T.to_string())


if __name__ == "__main__":
    main()
