"""Run the full experiment suite in one command:

    python pipelines/run_all_experiments.py

- Ranks the feature pool by mutual information on the training split (written to
  results/feature_ranking.csv); the 30/20/15 feature sets are the top-N of that ranking.
- Trains XGBoost (or whatever model.type is configured) on all 4 feature sets
  (40/30/20/15), each in closed-set and open-set mode -> 8 models saved to
  models_saved/<model.type>/, metrics collected into
  results/metrics/<model.type>/experiment_results.csv.
- Trains closed-set models on random feature subsets of the same sizes as a baseline
  -> feature_selection_baselines.csv.
- Computes SHAP global importance per feature-set model and runs the explanation-
  stability study (nested sets + a same-set/different-seed reference)
  -> results/metrics/<model.type>/explanation_stability.csv.
- Runs the cross-dataset (UNSW <-> CICIDS2017) generalization study ->
  results/metrics/<model.type>/cross_dataset_results.csv.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.train_pipeline import (
    Splits, generate_feature_ranking, load_split_data, train_and_evaluate, write_tier_diagnostics,
)
from src.data_loader import load_cic, load_unsw, stratified_subsample
from src.evaluation.cross_dataset import feature_shift_table, run_cross_dataset_study
from src.evaluation.metrics import build_overlap_diagnostics
from src.evaluation.plots import generate_all_plots, plot_confusion_matrix_for_scheme, plot_roc_curve
from src.models.model_factory import create_model
from src.preprocessing import Preprocessor, balanced_sample_weight
from src.utils.config_loader import (
    choose_pool, get_active_features, get_label_scheme, get_metrics_dir, get_random_features, get_worst_features,
    load_config, load_feature_sets, resolve_path, tagged,
)
from src.utils.logger import add_file_logging, get_logger
from src.xai.explanation_stability import compare_importances, run_stability_study
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)

# Common feature namespace shared by UNSW-NB15 and CICIDS2017 after src.data_loader's
# column remapping (see CIC_TO_COMMON) — used only by the cross-dataset study.
CROSS_DATASET_COMMON_FEATURES = [
    "dur", "spkts", "dpkts", "sbytes", "dbytes", "rate", "smean", "dmean",
    "total_bytes", "total_pkts", "byte_ratio", "pkt_ratio", "avg_pkt_size", "duration_log",
]


def run_experiment_grid(config: dict, feature_sets: dict, splits: Splits) -> pd.DataFrame:
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = resolve_path(config["paths"]["results_dir"]) / "plots" / config["model"]["type"]
    scheme_name, merge_groups, _ = get_label_scheme(config)
    rows = []
    for feature_set_name in config["experiments"]["feature_sets"]:
        for open_set_enabled in config["experiments"]["open_set_modes"]:
            logger.info(f"=== Training feature_set={feature_set_name} open_set={open_set_enabled} ===")
            # Closed/open-set share the same underlying classifier predictions (the
            # wrapper only relabels low-confidence rows), so only capture predictions
            # once per feature set — on the closed-set run — for the confusion
            # matrix / ROC curve, rather than duplicating them for both variants.
            predictions_out = {} if not open_set_enabled else None
            result = train_and_evaluate(
                config, feature_sets, feature_set_name, open_set_enabled,
                splits, save_artifacts=True, predictions_out=predictions_out,
                write_confusion=not open_set_enabled,
            )
            rows.append(result)

            if predictions_out:
                plot_confusion_matrix_for_scheme(predictions_out["y_test"], predictions_out["y_pred"],
                                                  predictions_out["class_names"],
                                                  plots_dir / tagged(config, f"confusion_matrix_{feature_set_name}.png"),
                                                  scheme_name, merge_groups)
                plot_roc_curve(predictions_out["y_test"], predictions_out["y_proba"],
                                predictions_out["class_names"],
                                plots_dir / tagged(config, f"roc_curve_{feature_set_name}.png"))

                diagnostics = build_overlap_diagnostics(predictions_out["fine_grained_true"],
                                                         predictions_out["y_pred_labels"],
                                                         merge_groups)
                for table in diagnostics.values() if write_tier_diagnostics(config, feature_set_name) else []:
                    table.to_csv(metrics_dir / tagged(config, f"overlap_diagnostic_{feature_set_name}.csv"))

    results_df = pd.DataFrame(rows)
    out_path = metrics_dir / tagged(config, config["experiments"]["output_csv"])
    results_df.to_csv(out_path, index=False)
    logger.info(f"Saved experiment grid results ({len(results_df)} rows) to {out_path}")
    return results_df


def summarize_baselines(baseline_df: pd.DataFrame) -> pd.DataFrame:
    """Per tier: ranked / worst macro F1, the random draws' mean/std/min/max, and how the ranked
    tier compares with them: its percentile and z-score among the draws, its rank among the draws
    (1 = best) and whether it beats random mean + 2 std."""
    rows = []
    for name, g in baseline_df.groupby("feature_set", sort=False):
        random_f1 = g.loc[g["ranking"] == "random", "f1"]
        if random_f1.empty:
            continue
        ranked = float(g.loc[g["ranking"] == "ranked", "f1"].iloc[0])
        mean, std = float(random_f1.mean()), float(random_f1.std())
        rows.append({
            "feature_set": name, "n_features": int(g["n_features"].iloc[0]),
            "ranked_f1": ranked, "worst_f1": float(g.loc[g["ranking"] == "worst", "f1"].iloc[0]),
            "random_f1_mean": round(mean, 4), "random_f1_std": round(std, 4),
            "random_f1_min": float(random_f1.min()), "random_f1_max": float(random_f1.max()),
            "n_random_draws": len(random_f1),
            "ranked_percentile_in_random": round(100 * float((random_f1 <= ranked).mean()), 1),
            "ranked_rank_among_draws": 1 + int((random_f1 > ranked).sum()),
            "ranked_z_vs_random": round((ranked - mean) / std, 2) if std > 0 else float("nan"),
            "ranked_beats_random_mean_plus_2std": bool(ranked > mean + 2 * std),
        })
    return pd.DataFrame(rows)


def run_random_baseline(config: dict, feature_sets: dict, splits: Splits, experiment_df: pd.DataFrame) -> pd.DataFrame:
    """Closed-set metrics per tier for: the ranked top-N, `random_baseline_draws` independent
    random subsets, and the worst-N by the ranking. A ranking only counts if its tier beats the
    random draws' spread (see the summary CSV: mean/std/min/max macro F1 of the draws)."""
    pool_size = len(feature_sets["feature_pool"])
    rows = [dict(r, ranking="ranked", draw=0) for r in experiment_df[~experiment_df["open_set"]].to_dict("records")]
    for name in config["experiments"]["feature_sets"]:
        if feature_sets["feature_sets"][name] >= pool_size:
            continue  # the full pool has no random/worst counterpart
        subsets = [("worst", 0, get_worst_features(config, feature_sets, name))] + [
            ("random", d, get_random_features(config, feature_sets, name, draw=d))
            for d in range(config["experiments"]["random_baseline_draws"])]
        for kind, draw, features in subsets:
            result = train_and_evaluate(config, feature_sets, name, False, splits, save_artifacts=False, features=features)
            rows.append(dict(result, ranking=kind, draw=draw))
    baseline_df = pd.DataFrame(rows)

    summary_df = summarize_baselines(baseline_df)
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    baseline_df.to_csv(metrics_dir / tagged(config, config["experiments"]["baselines_csv"]), index=False)
    summary_df.to_csv(metrics_dir / tagged(config, config["experiments"]["baselines_summary_csv"]), index=False)
    return baseline_df


def run_nonredundant_grid(config: dict, feature_sets: dict, splits: Splits) -> pd.DataFrame:
    """The experiment grid again with the redundancy-aware ranking (correlated features pushed
    down, `experiments.nonredundant_threshold`), into separate `_nonredundant` files; the default
    ranking and its outputs are untouched."""
    variant = copy.deepcopy(config)
    variant["feature_selection"].update(redundancy_threshold=config["experiments"]["nonredundant_threshold"],
                                        variant_tag="_nonredundant")
    generate_feature_ranking(variant, feature_sets, splits.train)
    return run_experiment_grid(variant, feature_sets, splits)


SPLIT_COMPARISON_COLUMNS = ["accuracy", "precision", "recall", "f1", "detection_rate", "false_positive_rate", "fpr_at_90_detection",
                            "fpr_at_95_detection", "fpr_at_99_detection"]


def build_split_comparison(official_df: pd.DataFrame, official: Splits, pooled_df: pd.DataFrame | None,
                           pooled: Splits | None, fine_column: str) -> pd.DataFrame:
    """One table: per feature tier, the official train/test split next to the pooled random split
    (accuracy, macro F1, attack-vs-normal detection / false-positive rate, Normal recall, per-class
    precision/recall) plus the per-class row counts of each split's train and test parts (after
    dedup), the cause of the gap: dedup removes the recurring, easy rows and reshapes the class mix."""
    parts = [("official", official_df[~official_df["open_set"]], official)]
    if pooled_df is not None:
        parts.append(("pooled_random", pooled_df, pooled))
    rows = []
    for name, df, splits in parts:
        counts = {f"{part}_rows_{c}": n for part, frame in (("train", splits.train), ("test", splits.test))
                  for c, n in frame[fine_column].value_counts().items()}
        for r in df.to_dict("records"):
            keep = {k: v for k, v in r.items() if k in SPLIT_COMPARISON_COLUMNS or k.startswith(("precision_", "recall_"))
                    and "_as_" not in k}
            rows.append({"feature_set": r["feature_set"], "split": name, "n_train": r["n_train"], "n_test": r["n_test"],
                         **keep, **counts})
    return pd.DataFrame(rows).sort_values(["feature_set", "split"], ascending=[False, True], kind="stable").reset_index(drop=True)


def run_pooled_split_report(config: dict, feature_sets: dict) -> tuple[pd.DataFrame, Splits]:
    """Same models evaluated on a pooled random split (use_official_split=False), so both
    the official-split and pooled numbers can be shown side by side."""
    splits = load_split_data(config, use_official_split=False)
    rows = [dict(train_and_evaluate(config, feature_sets, name, True, splits, save_artifacts=False,
                                         write_confusion=True), split="pooled_random")
            for name in config["experiments"]["feature_sets"]]
    df = pd.DataFrame(rows)
    df.to_csv(get_metrics_dir(config) / tagged(config, config["experiments"]["pooled_split_csv"]), index=False)
    return df, splits


def _fit_importance(config: dict, features: list[str], train_df: pd.DataFrame, seed: int | None = None) -> pd.Series:
    """Fit a model exactly like train_and_evaluate does (same sample weights) and return its
    global SHAP importance on `xai.importance_samples` training rows."""
    model_cfg = config["model"]
    preprocessor = Preprocessor(feature_list=features, target_column=config["data"]["target_column"]).fit(train_df)
    X_train, y_train = preprocessor.transform(train_df)
    params = dict(model_cfg["params"], **({"random_state": seed} if seed is not None else {}))
    model = create_model(model_cfg["type"], params)
    model.fit(X_train, y_train, sample_weight=balanced_sample_weight(y_train))
    explainer = SHAPExplainer(model, features, background_samples=config["xai"]["shap_background_samples"])
    return explainer.global_importance(X_train, max_samples=config["xai"]["importance_samples"])


def run_explanation_stability(config: dict, feature_sets: dict, splits: Splits) -> pd.DataFrame:
    """Train one closed-set model per feature-set size and compare their SHAP
    global-importance rankings pairwise (novelty #3). Also compares each model with the
    SAME feature set retrained under other seeds: the reference for how much agreement
    the nested-set comparisons show from retraining noise alone."""
    model_type = config["model"]["type"]
    importances = {}
    for feature_set_name in config["experiments"]["feature_sets"]:
        features = get_active_features(config, feature_sets, feature_set_name)
        importances[f"{model_type}_{feature_set_name}"] = _fit_importance(config, features, splits.train)

    nested = run_stability_study(importances)
    nested.insert(0, "comparison", "nested_feature_sets")

    seed_rows = []
    for feature_set_name in config["experiments"]["feature_sets"]:
        features = get_active_features(config, feature_sets, feature_set_name)
        name = f"{model_type}_{feature_set_name}"
        for seed in config["experiments"]["stability_seeds"]:
            other = _fit_importance(config, features, splits.train, seed=seed)
            seed_rows.append({"comparison": "same_set_different_seed", "config_a": name,
                              "config_b": f"{name}_seed{seed}", **compare_importances(importances[name], other)})

    stability_df = pd.concat([nested, pd.DataFrame(seed_rows)], ignore_index=True)
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    stability_df.to_csv(metrics_dir / tagged(config, config["experiments"]["stability_csv"]), index=False)
    logger.info(f"Explanation stability study complete:\n{stability_df}")
    return stability_df


def run_cross_dataset(config: dict) -> pd.DataFrame:
    unsw_df = load_unsw(
        resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]),
        seed=config["project"]["seed"], synthetic_rows=config["data"]["synthetic_fallback_rows"],
    )
    cic_df = load_cic(
        resolve_path(config["paths"]["cic_file"]),
        seed=config["project"]["seed"], synthetic_rows=config["data"]["synthetic_fallback_rows"],
    )
    cic_df = stratified_subsample(cic_df, config["data"]["cic_max_rows"], seed=config["project"]["seed"])
    cross_df = run_cross_dataset_study(
        unsw_df, cic_df, CROSS_DATASET_COMMON_FEATURES,
        config["model"]["type"], config["model"]["params"], importance_samples=config["xai"]["importance_samples"],
        seed=config["project"]["seed"],
    )
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    out_path = metrics_dir / config["experiments"]["cross_dataset_csv"]
    cross_df.to_csv(out_path, index=False)
    feature_shift_table(unsw_df, cic_df, CROSS_DATASET_COMMON_FEATURES, seed=config["project"]["seed"]).to_csv(
        metrics_dir / "cross_dataset_feature_shift.csv", index=False)
    logger.info(f"Saved cross-dataset results to {out_path} (+ cross_dataset_feature_shift.csv)")
    return cross_df


def run_all(config: dict, feature_sets: dict) -> dict[str, pd.DataFrame]:
    splits = load_split_data(config)
    config, feature_sets = choose_pool(config, feature_sets, splits.train.columns)
    generate_feature_ranking(config, feature_sets, splits.train)
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    if splits.summary is not None:
        splits.summary.to_csv(metrics_dir / tagged(config, config["experiments"]["split_summary_csv"]))

    logger.info("Step 1/4: training the experiment grid (feature sets x closed/open-set)")
    experiment_df = run_experiment_grid(config, feature_sets, splits)

    logger.info("Step 2/4: random-feature-set baseline")
    baseline_df = run_random_baseline(config, feature_sets, splits, experiment_df)

    logger.info("Step 3/4: explanation stability study")
    stability_df = run_explanation_stability(config, feature_sets, splits)

    logger.info("Step 4/4: cross-dataset generalization study")
    cross_dataset_df = run_cross_dataset(config)
    results = {"experiments": experiment_df, "baselines": baseline_df,
               "stability": stability_df, "cross_dataset": cross_dataset_df}
    if config["experiments"]["run_nonredundant"]:
        logger.info("Extra: experiment grid with the redundancy-aware ranking")
        results["nonredundant"] = run_nonredundant_grid(config, feature_sets, splits)
    pooled_df = pooled_splits = None
    if config["experiments"]["report_pooled_split"]:
        logger.info("Extra: metrics on a pooled random split")
        pooled_df, pooled_splits = run_pooled_split_report(config, feature_sets)
        results["pooled_split"] = pooled_df
    results["split_comparison"] = build_split_comparison(experiment_df, splits, pooled_df, pooled_splits,
                                                         config["data"]["fine_grained_target_column"])
    results["split_comparison"].to_csv(metrics_dir / tagged(config, "split_comparison.csv"), index=False)
    return results


def main() -> None:
    config = load_config()
    feature_sets = load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))

    results = run_all(config, feature_sets)
    plots_dir = generate_all_plots(
        config["model"]["type"], resolve_path(config["paths"]["results_dir"]), scheme=get_label_scheme(config)[0],
        experiment_df=results["experiments"], stability_df=results["stability"],
        cross_dataset_df=results["cross_dataset"],
    )

    logger.info(f"All experiments complete. See {get_metrics_dir(config)} for CSV outputs, "
                f"{plots_dir} for charts, and models_saved/ for artifacts.")


if __name__ == "__main__":
    main()
