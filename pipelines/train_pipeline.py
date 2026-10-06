"""Main training pipeline — fully config-driven. Run from the project root:

    python pipelines/train_pipeline.py

Trains the model configured in configs/config.yaml (`model.type`, `feature_selection.active_set`,
`open_set.enabled`), evaluates it, and saves the model + preprocessor to models_saved/.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.data_loader import _class_split_counts, load_unsw
from src.evaluation.metrics import (
    binary_detection_metrics, build_overlap_diagnostics, compute_metrics, confusion_matrix_tables, fpr_at_detection,
    group_recall_from_diagnostics, per_class_metrics, probabilistic_metrics, threshold_sweep, unknown_auroc, unknown_detection_rate,
)
from src.adaptation import adaptation_weights
from src.evaluation.plots import plot_confusion_matrix_for_scheme, plot_roc_curve
from src.fpr_methods import fit_temperature
from src.xai.class_reference import ClassReference
from src.feature_selection import compute_feature_ranking, data_signature, ranking_is_current, write_feature_ranking
from src.models.model_factory import create_scheme_model
from src.models.open_set_wrapper import OpenSetWrapper, select_threshold
from src.preprocessing import Preprocessor, add_merged_label, balanced_sample_weight, split_known_unknown
from src.utils.config_loader import (
    artifact_suffix, choose_pool, get_active_features, get_label_scheme, get_metrics_dir, load_config, load_feature_sets,
    ranking_path, resolve_path, scheme_tag, tagged,
)
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

SWEEP_THRESHOLDS = [round(float(t), 2) for t in np.arange(0.05, 1.0, 0.05)]


@dataclass
class Splits:
    """train: fits the model. val: KNOWN classes only, used solely to choose the open-set
    threshold. test: KNOWN classes only, reported. unknown: held-out zero-day classes,
    reported only (never used to choose anything)."""
    train: pd.DataFrame
    val: pd.DataFrame
    test: pd.DataFrame
    unknown: pd.DataFrame
    summary: pd.DataFrame | None = None   # per-class counts before/after dedup and per split
    name: str = "official"                # "official" or "pooled_random": which protocol made the test split
    # few-shot adaptation (src/adaptation.py): train rows flagged in `adapt_flag` are labelled rows drawn from the TARGET
    # distribution and together carry this fraction of the total training sample weight (None: no adaptation)
    adapt_fraction: float | None = None
    # TRANSDUCTIVE reweighting (src/adaptation.domain_importance_weights): one multiplier per training row, applied to the sample weights
    weight_multiplier: np.ndarray | None = None


def _split_summary(raw: pd.DataFrame, before: pd.DataFrame, parts: dict[str, pd.DataFrame], fine: str) -> pd.DataFrame:
    """Per fine-grained class: rows in each official file before/after dedup, then in each final split."""
    after = _class_split_counts(raw)
    out = pd.DataFrame({
        "raw_train_file": before["train"], "raw_test_file": before["test"],
        "dedup_train_file": after["train"], "dedup_test_file": after["test"],
    })
    for name, part in parts.items():
        out[f"n_{name}"] = part[fine].value_counts()
    out = out.fillna(0).astype(int)
    out.index.name = "attack_cat"
    return out


def load_split_data(config: dict, use_official_split: bool | None = None) -> Splits:
    """Load UNSW-NB15 (exact duplicates dropped), hold out zero-day categories, and split
    the known traffic into train/val/test. With `data.use_official_split` (and both official
    files present) test is unsw_nb15_test.csv and train/val come from unsw_nb15_train.csv;
    otherwise known rows are split randomly. `use_official_split` overrides the config value."""
    data_cfg = config["data"]
    seed = config["project"]["seed"]
    target = data_cfg["target_column"]
    df = load_unsw(
        resolve_path(config["paths"]["unsw_train"]),
        resolve_path(config["paths"]["unsw_test"]),
        seed=seed,
        synthetic_rows=data_cfg["synthetic_fallback_rows"],
    )
    before_dedup = df.attrs.get("counts_before_dedup")
    raw_df = df
    # Label-level only: adds `label_merged` (the primary training target) without touching
    # `attack_cat` (the fine-grained column, preserved for the overlap diagnostic table).
    # Categories not named in any group (Worms/Shellcode included) pass through unchanged,
    # so the zero-day split below is unaffected by the merge.
    df = add_merged_label(df, get_label_scheme(config)[1],
                           source_column=data_cfg["fine_grained_target_column"], target_column=target)
    # The held-out (zero-day) classes are named by their ORIGINAL class, so a member of a merged group (Analysis, Backdoor, DoS) can be held out while its siblings stay known
    # and still form the merged group; for unmerged classes (Worms, Shellcode, ...) the original and the merged label are the same.
    known_df, unknown_df = split_known_unknown(df, data_cfg["unknown_attack_categories"], data_cfg["fine_grained_target_column"])

    official = (data_cfg.get("use_official_split", True) if use_official_split is None else use_official_split)         and {"train", "test"} <= set(known_df["split"])
    if official:
        train_full = known_df[known_df["split"] == "train"]
        test_df = known_df[known_df["split"] == "test"]
        logger.info("Using the official UNSW-NB15 train/test split")
    else:
        train_full, test_df = train_test_split(known_df, test_size=data_cfg["test_size"], random_state=seed,
                                               stratify=known_df[target])
        logger.info("Using a random train/test split of the pooled UNSW-NB15 rows")
    train_df, val_df = train_test_split(train_full, test_size=data_cfg["val_size"], random_state=seed,
                                        stratify=train_full[target])
    train_df, val_df, test_df = (d.reset_index(drop=True) for d in (train_df, val_df, test_df))
    for part in (train_df, val_df, test_df, unknown_df):
        part.attrs = {}  # the loader's DataFrame-valued dedup counts must not travel with the splits (they break pd.concat)
    summary = None
    if before_dedup is not None:
        summary = _split_summary(raw_df, before_dedup, {"train": train_df, "val": val_df, "test": test_df,
                                                        "unknown": unknown_df}, data_cfg["fine_grained_target_column"])
    return Splits(train_df, val_df, test_df, unknown_df, summary, "official" if official else "pooled_random")


def ordered_training_rows(config: dict) -> pd.DataFrame:
    """The known training-file rows in FILE order (load_split_data shuffles them when it splits train / validation). The official
    files are not shuffled: neighbouring rows share sliding-window (ct_*) values and often a class."""
    data = config["data"]
    df = load_unsw(resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]), seed=config["project"]["seed"],
                   synthetic_rows=data["synthetic_fallback_rows"])
    df = add_merged_label(df, get_label_scheme(config)[1], source_column=data["fine_grained_target_column"], target_column=data["target_column"])
    known, _ = split_known_unknown(df, data["unknown_attack_categories"], data["fine_grained_target_column"])
    return known[known["split"] == "train"].reset_index(drop=True)


def block_validation_splits(config: dict, splits: Splits, seed: int, block_size: int = 1000, buffer: int = 200) -> Splits:
    """`splits` with the training / validation parts rebuilt from contiguous blocks of the training file (in file order): `data.val_size` of
    the blocks, drawn with `seed`, form the validation set and `buffer` rows on each side of every block boundary are dropped from both, so no
    validation row has a neighbour (a row within the sliding window) in training. The official test and zero-day parts are unchanged. A random
    validation split shares neighbours with the training rows and is optimistic (Task 2.6)."""
    from dataclasses import replace
    from src.neighbours import block_split
    ordered = ordered_training_rows(config)
    val_pos, train_pos = block_split(len(ordered), block_size, buffer, config["data"]["val_size"], seed)
    train, val = ordered.iloc[train_pos].reset_index(drop=True), ordered.iloc[val_pos].reset_index(drop=True)
    for part in (train, val):
        part.attrs = {}  # the loader's DataFrame-valued dedup counts must not travel with the splits (they break pd.concat when rows are added to the training set)
    return replace(splits, train=train, val=val)


def generate_feature_ranking(config: dict, feature_sets: dict, train_df: pd.DataFrame) -> pd.Series:
    """Write the ranking for `feature_selection.ranking_source` to its own file
    (results/rankings/feature_ranking_<source>.csv): mutual information on the training split, or the
    curated order. get_active_features builds the 30/20/15 sets from it."""
    fs_cfg = config["feature_selection"]
    if fs_cfg["ranking_source"] == "curated":
        order = feature_sets["feature_curated_rank"]
        ranking = pd.Series(range(len(order), 0, -1), index=order, dtype=float)
    else:
        ranking = compute_feature_ranking(
            train_df, feature_sets["feature_pool"], config["data"]["target_column"],
            max_rows=fs_cfg["ranking_max_rows"], seed=config["project"]["seed"],
            redundancy_threshold=fs_cfg.get("redundancy_threshold"),
        )
    write_feature_ranking(ranking, ranking_path(config), ranking_signature(config, feature_sets, train_df))
    return ranking


def ranking_signature(config: dict, feature_sets: dict, train_df: pd.DataFrame) -> str:
    fs_cfg = config["feature_selection"]
    extra = (f"{feature_sets.get('pool_name', 'base')}|{fs_cfg['ranking_source']}|{fs_cfg.get('redundancy_threshold')}|"
             f"{config['data']['target_column']}|{fs_cfg['ranking_max_rows']}")
    return data_signature(train_df, config["project"]["seed"], extra)


def ensure_feature_ranking(config: dict, feature_sets: dict, train_df: pd.DataFrame) -> bool:
    """(Re)generate the ranking unless its file matches this training data (see data_signature);
    returns True if it was regenerated."""
    if ranking_is_current(ranking_path(config), ranking_signature(config, feature_sets, train_df)):
        return False
    generate_feature_ranking(config, feature_sets, train_df)
    return True


def write_tier_diagnostics(config: dict, feature_set_name: str) -> bool:
    """Whether this tier gets its own open-set sweep / overlap-diagnostic CSVs: always the active
    tier, the others only with `experiments.save_per_tier_diagnostics`."""
    return (config["experiments"]["save_per_tier_diagnostics"]
            or str(feature_set_name) == str(config["feature_selection"]["active_set"]))


def evaluate_model(model, preprocessor: Preprocessor, test_df: pd.DataFrame, config: dict) -> tuple[dict, dict]:
    """The one evaluation used for every reported test metric (training pipeline, experiment
    grid and evaluate_pipeline.py). Returns (metrics, predictions): macro metrics on the scheme's
    target, per-class precision/recall/F1, attack-vs-normal detection / false-positive rate, the
    FPR at 90/95/99% detection, per-class and macro ROC-AUC / PR-AUC, ECE and Brier, `fine_recall_<class>` (+ macro) of the ORIGINAL classes under the
    active scheme, and `group_size_share` (share of attack rows inside a merged group)."""
    data_cfg = config["data"]
    _, merge_groups, _ = get_label_scheme(config)
    X_test, y_test = preprocessor.transform(test_df)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    y_pred_labels = preprocessor.decode_target(y_pred)
    true_labels = preprocessor.decode_target(y_test)
    classes = list(preprocessor.target_encoder.classes_)
    fine = test_df[data_cfg["fine_grained_target_column"]].values
    normal = data_cfg["normal_category"]

    metrics = compute_metrics(y_test, y_pred)
    # Headline multiclass numbers are on the merged class, so also report per-class scores,
    # the attack-vs-normal view, and the fine-grained recall of the merged categories.
    metrics.update(per_class_metrics(y_test, y_pred, classes))
    metrics.update(binary_detection_metrics(true_labels, y_pred_labels, normal))
    metrics.update(fpr_at_detection(true_labels, y_proba, classes, normal))
    metrics.update(probabilistic_metrics(y_test, y_proba, classes, normal, config["evaluation"]["ece_bins"]))
    metrics.update(group_recall_from_diagnostics(build_overlap_diagnostics(fine, y_pred_labels, merge_groups)))
    # Recall of the ORIGINAL classes under the active scheme (their true class's label, which
    # for a merged class is the group name), so a merge cannot hide them.
    label_of = {c: g for g, cats in merge_groups.items() for c in cats}
    recalls = []
    for c in data_cfg["report_fine_recall"]:
        rows = fine == c
        recall = float((y_pred_labels[rows] == label_of.get(c, c)).mean()) if rows.any() else float("nan")
        metrics[f"fine_recall_{c}"] = round(recall, 4)
        recalls.append(recall)
    metrics["fine_recall_macro"] = round(float(np.nanmean(recalls)), 4)
    attack_rows = fine != normal
    metrics["group_size_share"] = round(float(np.isin(fine[attack_rows], list(label_of)).mean()), 4)
    predictions = dict(X_test=X_test, y_test=y_test, y_pred=y_pred, y_proba=y_proba, class_names=preprocessor.target_encoder.classes_,
                       y_pred_labels=y_pred_labels, true_labels=true_labels, fine_grained_true=fine)
    return metrics, predictions


def write_confusion_csvs(config: dict, feature_set_name: str, split_name: str, predictions: dict) -> None:
    """results/metrics/<model.type>/confusion_matrix_<tier>_<split>[_rownorm]<tags>.csv from evaluate_model's predictions."""
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    counts, rownorm = confusion_matrix_tables(predictions["true_labels"], predictions["y_pred_labels"], predictions["class_names"])
    counts.to_csv(metrics_dir / tagged(config, f"confusion_matrix_{feature_set_name}_{split_name}.csv"))
    rownorm.to_csv(metrics_dir / tagged(config, f"confusion_matrix_{feature_set_name}_{split_name}_rownorm.csv"))


def train_and_evaluate(
    config: dict,
    feature_sets: dict,
    feature_set_name: str,
    open_set_enabled: bool,
    splits: Splits,
    save_artifacts: bool = True,
    predictions_out: dict | None = None,
    features: list[str] | None = None,
    write_confusion: bool = False,
) -> dict:
    """Train one model configuration and return its metrics dict. Optionally save the
    fitted model + preprocessor to models_saved/ for later evaluation/dashboard use.

    `features` overrides the feature list (e.g. the random-ranking baseline); by default
    it's the top-N of the generated ranking for `feature_set_name`. If `predictions_out`
    is passed, it's populated with y_test/y_pred/y_proba/class_names so a caller can
    render a confusion matrix or ROC curve without retraining. `write_confusion` writes the test
    confusion matrix (counts + row-normalised) as CSVs, named by tier and split protocol."""
    data_cfg = config["data"]
    model_cfg = config["model"]
    features = features or get_active_features(config, feature_sets, feature_set_name)
    scheme_name, merge_groups, hierarchical = get_label_scheme(config)

    preprocessor = Preprocessor(feature_list=features, target_column=data_cfg["target_column"]).fit(splits.train)
    preprocessor.metadata = {  # traceability: which feature list / ranking produced this artifact
        "feature_set": feature_set_name, "features": list(features),
        "ranking_source": config["feature_selection"]["ranking_source"], "model_type": model_cfg["type"],
        "feature_pool": feature_sets.get("pool_name", "base"), "label_scheme": scheme_name,
    }
    X_train, y_train = preprocessor.transform(splits.train)
    X_val, y_val = preprocessor.transform(splits.val)

    normal_index = list(preprocessor.target_encoder.classes_).index(data_cfg["normal_category"])
    model = create_scheme_model(model_cfg["type"], model_cfg["params"], hierarchical, normal_index,
                                model_cfg.get("stage1_params"), model_cfg.get("stage1_class_weight_power", 0.5))
    # A hierarchical model balances each stage itself (binary stage 1, family stage 2).
    weights = None if hierarchical else balanced_sample_weight(y_train, model_cfg.get("class_weight_power", 0.5))
    if splits.adapt_fraction is not None and weights is not None:
        weights = adaptation_weights(weights, splits.train["adapt_flag"].to_numpy(dtype=bool), splits.adapt_fraction)
    if splits.weight_multiplier is not None and weights is not None:
        weights = weights * splits.weight_multiplier
    model.fit(X_train, y_train, sample_weight=weights)
    metrics, predictions = evaluate_model(model, preprocessor, splits.test, config)
    if predictions_out is not None:
        predictions_out.update(model=model, preprocessor=preprocessor)  # for callers that score further rows
        predictions_out.update({k: predictions[k] for k in
                                ("y_test", "y_pred", "y_proba", "class_names", "y_pred_labels", "fine_grained_true")})
    y_proba = predictions["y_proba"]
    if write_confusion:
        write_confusion_csvs(config, feature_set_name, splits.name, predictions)

    result = {
        "model_type": model_cfg["type"],
        "feature_set": feature_set_name,
        "feature_pool": feature_sets.get("pool_name", "base"),
        "label_scheme": scheme_name,
        "n_features": len(features),
        "open_set": open_set_enabled,
        "n_train": len(splits.train),
        "n_val": len(splits.val),
        "n_test": len(splits.test),
        **metrics,
    }

    tag = "open" if open_set_enabled else "closed"
    model_name = f"{model_cfg['type']}_{feature_set_name}_{tag}{scheme_tag(config)}"
    metrics_dir = get_metrics_dir(config)

    # Open-set threshold: chosen on KNOWN validation data only (target false-"Unknown" rate),
    # then frozen. The zero-day classes are only ever scored at this threshold.
    proba_val = model.predict_proba(X_val)
    conf_val = proba_val.max(axis=1)
    if predictions_out is not None:  # validation scores, for operating points chosen on validation only
        predictions_out.update(y_proba_val=proba_val, val_labels=preprocessor.decode_target(y_val))
    threshold = select_threshold(conf_val, config["open_set"]["target_false_unknown_rate"])

    if open_set_enabled and len(splits.unknown) > 0:
        X_test = predictions["X_test"]
        X_unknown = preprocessor.transform_features(splits.unknown)
        osp = OpenSetWrapper(model, threshold).predict(np.vstack([X_test, X_unknown]))
        is_true_unknown = np.arange(len(osp.confidence)) >= len(X_test)
        if predictions_out is not None:
            predictions_out.update(open_set_is_unknown=osp.is_unknown, is_true_unknown=is_true_unknown)
        result.update(
            open_set_threshold=round(threshold, 4),
            target_false_unknown_rate=config["open_set"]["target_false_unknown_rate"],
            false_unknown_alarm_rate_val=round(float((conf_val < threshold).mean()), 4),
            **unknown_detection_rate(is_true_unknown, osp.is_unknown),
            unknown_auroc=unknown_auroc(osp.confidence[~is_true_unknown], osp.confidence[is_true_unknown]),
        )
        if save_artifacts and write_tier_diagnostics(config, feature_set_name):
            metrics_dir.mkdir(parents=True, exist_ok=True)
            threshold_sweep(osp.confidence[~is_true_unknown], osp.confidence[is_true_unknown],
                            sorted({*SWEEP_THRESHOLDS, round(threshold, 4)})
                            ).to_csv(metrics_dir / tagged(config, f"open_set_sweep_{feature_set_name}.csv"), index=False)

    if save_artifacts:
        # Grouped by model type (models_saved/xgboost/, models_saved/random_forest/, ...)
        # so every artifact for a given model — all feature sets, closed/open-set,
        # preprocessors — lives together instead of a flat, hard-to-scan directory.
        # XGBoost artifacts are .json (native format), everything else .pkl.
        model_dir = resolve_path(config["paths"]["models_dir"]) / model_cfg["type"]
        model_dir.mkdir(parents=True, exist_ok=True)
        model.save(str(model_dir / f"{model_name}{artifact_suffix(model_cfg['type'])}"))
        joblib.dump(preprocessor, model_dir / f"preprocessor_{feature_set_name}{scheme_tag(config)}.pkl")
        # Task 5.5: where flows sit among the training flows of each class, and a temperature fitted on the validation split, for the class-relative narrative and its calibrated confidence
        ClassReference.fit(X_train, y_train, list(preprocessor.target_encoder.classes_), list(features), list(preprocessor.categorical_features)
                           ).save(model_dir / f"class_reference_{feature_set_name}{scheme_tag(config)}.npz")
        (model_dir / f"calibration_{feature_set_name}{scheme_tag(config)}.json").write_text(json.dumps({"temperature": fit_temperature(proba_val, y_val)}))
        (model_dir / f"open_set_{feature_set_name}{scheme_tag(config)}.json").write_text(json.dumps(
            {"confidence_threshold": threshold,
             "target_false_unknown_rate": config["open_set"]["target_false_unknown_rate"]}))

    logger.info(f"[{model_name}] metrics: {metrics}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-ranking", action="store_true",
                        help="(re)generate the feature ranking file; otherwise an existing one is required")
    args = parser.parse_args()
    config = load_config()
    feature_sets = load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    splits = load_split_data(config)
    config, feature_sets = choose_pool(config, feature_sets, splits.train.columns)
    if args.write_ranking:
        generate_feature_ranking(config, feature_sets, splits.train)

    feature_set_name = config["feature_selection"]["active_set"]
    predictions_out = {}
    result = train_and_evaluate(
        config, feature_sets,
        feature_set_name=feature_set_name,
        open_set_enabled=config["open_set"]["enabled"],
        splits=splits,
        predictions_out=predictions_out,
    )
    logger.info(f"Training complete: {result}")

    results_dir = resolve_path(config["paths"]["results_dir"])
    plots_dir = results_dir / "plots" / config["model"]["type"]
    scheme_name, merge_groups, _ = get_label_scheme(config)
    plot_confusion_matrix_for_scheme(predictions_out["y_test"], predictions_out["y_pred"], predictions_out["class_names"],
                                      plots_dir / tagged(config, f"confusion_matrix_{feature_set_name}.png"),
                                      scheme_name, merge_groups)
    plot_roc_curve(predictions_out["y_test"], predictions_out["y_proba"],
                    predictions_out["class_names"], plots_dir / tagged(config, f"roc_curve_{feature_set_name}.png"))

    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = build_overlap_diagnostics(predictions_out["fine_grained_true"], predictions_out["y_pred_labels"],
                                             merge_groups)
    for group_name, table in diagnostics.items():
        out_csv = metrics_dir / tagged(config, f"overlap_diagnostic_{feature_set_name}.csv")
        table.to_csv(out_csv)
        logger.info(f"Saved {group_name} overlap diagnostic to {out_csv}:\n{table}")


if __name__ == "__main__":
    main()
