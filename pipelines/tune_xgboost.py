"""Capped hyperparameter search for XGBoost, tuned on VALIDATION only (xgboost model type):

    python pipelines/tune_xgboost.py [--pools full base]   (default: the primary pool 48 only)

Per feature pool it draws `tuning.n_trials` random configurations from `tuning.space` (seeded), fits each on the
training split with early stopping on the validation split's mlogloss, and scores it on validation: macro F1 and the
attack-vs-normal AUC (score 1 - P(Normal)). The default configuration of config.yaml is scored the same way as a
reference (not part of the budget). Two configurations are kept, one per objective. The official test file and the
held-out zero-day rows are never read here. Writes under results/metrics/<model.type>/:

  hyperparameter_search_<N>f.csv   every trial: parameters, best_iteration, validation metrics
  tuned_params_<N>f.json           the two selected configurations (n_estimators = best_iteration + 1) and the budget

Evaluate a selection on the official split over seeds with
`python pipelines/run_headline_seeds.py --tuned f1|auc --protocols official`.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import f1_score, roc_auc_score

from pipelines.train_pipeline import block_validation_splits, load_split_data
from src.preprocessing import Preprocessor, balanced_sample_weight
from src.utils.config_loader import apply_pool_variant, choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

OBJECTIVES = {"f1": "val_macro_f1", "auc": "val_attack_auc"}


def sample_params(space: dict, rng: np.random.Generator) -> dict:
    """One configuration drawn from `tuning.space` (entries: int [lo, hi], uniform / loguniform [lo, hi], choice [...])."""
    out = {}
    for name, spec in space.items():
        (kind, arg), = spec.items()
        if kind == "int":
            out[name] = int(rng.integers(arg[0], arg[1] + 1))
        elif kind == "uniform":
            out[name] = round(float(rng.uniform(*arg)), 4)
        elif kind == "loguniform":
            out[name] = round(float(np.exp(rng.uniform(np.log(arg[0]), np.log(arg[1])))), 5)
        elif kind == "choice":
            out[name] = arg[int(rng.integers(len(arg)))]
        else:
            raise ValueError(f"unknown tuning.space kind {kind!r} for {name}")
    return out


def score_validation(proba: np.ndarray, y_val: np.ndarray, normal_index: int) -> dict:
    return {"val_macro_f1": round(float(f1_score(y_val, proba.argmax(axis=1), average="macro", zero_division=0)), 4),
            "val_attack_auc": round(float(roc_auc_score(y_val != normal_index, 1 - proba[:, normal_index])), 4)}


def run_trial(params: dict, base_params: dict, tuning: dict, data: tuple, seed: int) -> dict:
    """Fit one configuration with early stopping on validation mlogloss; returns its validation scores."""
    X_train, y_train, X_val, y_val, normal_index = data
    power = params.get("class_weight_power", 0.5)
    fit_params = {k: v for k, v in dict(base_params, **params).items() if k != "class_weight_power"}
    fit_params.update(n_estimators=tuning["max_estimators"], early_stopping_rounds=tuning["early_stopping_rounds"],
                      eval_metric="mlogloss" if len(np.unique(y_train)) > 2 else "logloss", random_state=seed)
    start = time.time()
    model = xgb.XGBClassifier(**fit_params)
    model.fit(X_train, y_train, sample_weight=balanced_sample_weight(y_train, power), eval_set=[(X_val, y_val)], verbose=False)
    return {**params, "class_weight_power": power, "best_iteration": int(model.best_iteration),
            **score_validation(model.predict_proba(X_val), y_val, normal_index), "seconds": round(time.time() - start, 1)}


def select_best(trials: pd.DataFrame) -> dict[str, pd.Series]:
    """The best non-reference trial per objective (highest validation score; ties -> the earlier trial)."""
    search = trials[~trials["is_default"]].reset_index(drop=True)
    return {obj: search.loc[search[col].idxmax()] for obj, col in OBJECTIVES.items()}


def tune_pool(config: dict, feature_sets: dict, pool: str, stage1: bool = False, block_validation: bool = False) -> pd.DataFrame:
    """Random search for `pool`. With `stage1` the labels are attack (1) vs Normal (0): the search for the binary first
    stage of the hierarchical model (same space and budget; the 2-class macro F1 and attack AUC are scored on validation);
    its files are named hyperparameter_search_stage1_<N>f.csv / tuned_params_stage1_<N>f.json.
    With `block_validation` (Task 2.7) the validation split is built from contiguous blocks of the training file (no neighbours shared with training) and the
    search uses `tuning.space_regularised`; the files are named hyperparameter_search_blockval_<N>f.csv / tuned_params_blockval_<N>f.json."""
    cfg = apply_pool_variant(config, pool)
    tuning, seed = dict(cfg["tuning"]), cfg["tuning"]["seed"]
    if block_validation:
        tuning["space"] = tuning["space_regularised"]
    splits = load_split_data(cfg, use_official_split=True)
    if block_validation:
        splits = block_validation_splits(cfg, splits, seed, cfg["tier_study"]["block_size"], cfg["tier_study"]["buffer"])
    cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
    features = list(sets["feature_pool"])
    pre = Preprocessor(feature_list=features, target_column=cfg["data"]["target_column"]).fit(splits.train)
    (X_train, y_train), (X_val, y_val) = pre.transform(splits.train), pre.transform(splits.val)
    normal_index = list(pre.target_encoder.classes_).index(cfg["data"]["normal_category"])
    if stage1:  # attack = 1, Normal = 0, so score_validation's Normal index is 0
        y_train, y_val, normal_index = (y_train != normal_index).astype(int), (y_val != normal_index).astype(int), 0
    data = (X_train, y_train, X_val, y_val, normal_index)
    base = {k: v for k, v in cfg["model"]["params"].items() if k not in ("n_estimators", "random_state", "eval_metric")}

    rng = np.random.default_rng(seed)
    rows = [{"trial": 0, "is_default": True, **run_trial(
        {k: v for k, v in cfg["model"]["params"].items() if k in tuning["space"]}, base, tuning, data, seed)}]
    # the default reference keeps its configured depth/learning rate etc. but early-stops like every trial, so the
    # comparison on validation is like for like; it is not one of the n_trials
    for i in range(1, tuning["n_trials"] + 1):
        rows.append({"trial": i, "is_default": False, **run_trial(sample_params(tuning["space"], rng), base, tuning, data, seed)})
        logger.info(f"[tune {pool_label(sets)}] trial {i}/{tuning['n_trials']}: f1={rows[-1]['val_macro_f1']} auc={rows[-1]['val_attack_auc']} "
                    f"it={rows[-1]['best_iteration']} {rows[-1]['seconds']}s")
    trials = pd.DataFrame(rows)

    metrics_dir = get_metrics_dir(cfg)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    label = pool_label(sets)
    prefix = ("stage1_" if stage1 else "") + ("blockval_" if block_validation else "")
    trials.to_csv(metrics_dir / f"hyperparameter_search_{prefix}{label}.csv", index=False)
    keys = [k for k in tuning["space"] if k != "class_weight_power"]
    best = select_best(trials)
    out = {"pool": pool, "n_features": len(features), "n_trials": tuning["n_trials"], "seed": seed,
           "early_stopping": f"{tuning['early_stopping_rounds']} rounds on validation mlogloss, max {tuning['max_estimators']} trees",
           "default_reference": trials[trials["is_default"]].iloc[0][["best_iteration", *OBJECTIVES.values()]].to_dict()}
    for obj, row in best.items():
        out[obj] = {"params": {**{k: row[k] for k in keys}, "n_estimators": int(row["best_iteration"]) + 1},
                    "class_weight_power": float(row["class_weight_power"]),
                    "val_macro_f1": float(row["val_macro_f1"]), "val_attack_auc": float(row["val_attack_auc"]), "trial": int(row["trial"])}
    (metrics_dir / f"tuned_params_{prefix}{label}.json").write_text(json.dumps(out, indent=2, default=lambda o: o.item()), encoding="utf-8")
    return trials


def load_tuned(config: dict, label: str, objective: str, stage1: bool = False, block_validation: bool = False) -> tuple[dict, float]:
    """(model params to merge into config model.params, class_weight_power) of the tuned selection for `objective`
    (the stage-1 search with `stage1`, the block-grouped-validation search with `block_validation`)."""
    path = get_metrics_dir(config) / f"tuned_params_{'stage1_' if stage1 else ''}{'blockval_' if block_validation else ''}{label}.json"
    chosen = json.loads(path.read_text(encoding="utf-8"))[objective]
    return chosen["params"], chosen["class_weight_power"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["full"], help="default: the primary pool 48 (full); add base (40) or an experiments.pool_variants name")
    parser.add_argument("--stage1", action="store_true", help="search the binary attack-vs-normal first stage of the hierarchical model")
    parser.add_argument("--block-validation", action="store_true", help="select on block-grouped validation with the regularised space (Task 2.7)")
    args = parser.parse_args()
    config = load_config()
    if config["model"]["type"] != "xgboost":
        raise SystemExit("tune_xgboost.py tunes XGBoost only (model.type: xgboost)")
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    for pool in args.pools:
        trials = tune_pool(config, load_feature_sets(), pool, args.stage1, args.block_validation)
        print(trials.sort_values("val_macro_f1", ascending=False).head(5).to_string(index=False))


if __name__ == "__main__":
    main()
