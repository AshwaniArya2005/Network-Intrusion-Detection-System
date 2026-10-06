"""Feature-tier study: accuracy and SHAP explanations as the feature set shrinks (protocol: results/04_novelty3_feature_tiers.md, section `Source: feature_tiers_protocol.md`).

    python pipelines/run_tier_study.py --model xgboost [--pools full base full_no_ttl] [--parts tiers baselines pooled plots] [--no-plots]   (default pool: full = 48 features, the primary pool;
    base = 40 and full_no_ttl = 45 features are the comparison pools)

For every pool (40 / 45 / 48 features) and tier (the top-N of a mutual-information ranking of the pool, computed once on the seed-42
block-grouped training split and shared by every model type and seed) and seed 42..46 it trains the model ONCE and records the official-split
metrics and the global SHAP importance of that same model (mean |SHAP| over classes on `tier_study.shap_rows` training rows, plus
`tier_study.bootstrap` paired bootstrap resamples of those rows). Training / validation come from contiguous blocks of the training file
(block_validation_splits); the validation-chosen 95%-detection operating point (`det95`) is chosen on that block-grouped validation split.
All methods here are ZERO-SHOT. Parts:

  tiers      ranked tiers with SHAP                  -> tier_study_<model>_<N>f_runs.csv, shap_importance_<model>_<N>f.csv, shap_boot_<model>_<N>f.npz
  baselines  random subsets and worst-N (xgboost)    -> tier_baselines_<model>_<N>f.csv, tier_baselines_summary_<model>_<N>f.csv
  pooled     ranked tiers on the pooled random split (best case; neighbour-leaking) -> tier_study_<model>_<N>f_pooled.csv
  plots      one confusion-matrix PNG and one ROC PNG per (pool, tier) -> results/plots/<model.type>/confusion_matrix_<T>f.png and
             roc_curve_<T>f.png (pool 48; a comparison pool N adds `pool<N>_`, e.g. confusion_matrix_pool40_30f.png); seed 42 (tier_study.seeds[0]), block-grouped protocol; a model already saved in models_saved/<model.type>/ for
             that (pool, tier) is reused, a missing one is trained (closed set) and saved. The `tiers` part writes the same plots by itself for seed 42
             from the model it trains anyway (no extra training); `--no-plots` turns that off.

Files are written under results/metrics/<model.type>/ (<N>f = size of the pool: 40f, 45f, 48f).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd

from pipelines.run_all_experiments import summarize_baselines
from pipelines.run_operating_point import operating_points
from pipelines.train_pipeline import block_validation_splits, ensure_feature_ranking, evaluate_model, load_split_data, train_and_evaluate
from src.evaluation.plots import write_tier_plots
from src.models.model_factory import create_scheme_model
from src.utils.config_loader import (
    apply_pool_variant, artifact_suffix, choose_pool, get_active_features, get_label_scheme, get_metrics_dir, get_random_features, get_worst_features,
    load_config, load_feature_sets, pool_label, resolve_path, scheme_tag,
)
from src.utils.logger import add_file_logging, get_logger
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)

KEEP = ["accuracy", "f1", "detection_rate", "false_positive_rate", "recall_Normal", "roc_auc_attack_vs_normal", "roc_auc_macro", "pr_auc_macro", "ece", "brier",
        "fpr_at_90_detection", "fpr_at_95_detection", "unknown_detection_rate", "false_unknown_alarm_rate", "unknown_auroc", "fine_recall_macro"]


def model_config(cfg: dict, model_type: str, seed: int) -> dict:
    """`cfg` for `model_type` and `seed`: XGBoost keeps config.yaml's parameters, the other families the declared `tier_study.model_params`."""
    cfg["model"]["type"] = model_type
    if model_type != "xgboost":
        declared = cfg["tier_study"]["model_params"]
        if model_type not in declared:
            raise ValueError(f"No parameters declared for model type {model_type!r}: add tier_study.model_params.{model_type} to configs/config.yaml "
                             f"(and register the model in src/models/model_factory.py)")
        cfg["model"]["params"] = dict(declared[model_type])
    cfg["model"]["params"]["random_state"] = seed
    cfg["project"]["seed"] = seed
    return cfg


def prepare(config: dict, feature_sets: dict, pool: str, model_type: str, seed: int, pooled: bool = False):
    """(config, feature_sets, splits) of one run: block-grouped train / validation on the official split (or the pooled random split), and the
    ranking file name set so the feature-tier study rankings never overwrite the earlier ones."""
    cfg = model_config(apply_pool_variant(config, pool), model_type, seed)
    splits = load_split_data(cfg, use_official_split=not pooled)
    if not pooled:
        splits = block_validation_splits(cfg, splits, seed, cfg["tier_study"]["block_size"], cfg["tier_study"]["buffer"])
    cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
    cfg["feature_selection"]["variant_tag"] = "_blockval" + ("" if cfg["feature_selection"]["pool_tag"] else "_40f")
    return cfg, sets, splits


def ensure_pool_ranking(config: dict, feature_sets: dict, pool: str) -> list[str]:
    """The pool's mutual-information ranking on the seed-42 block-grouped training split (written once, shared by every model and seed)."""
    seed = config["tier_study"]["seeds"][0]
    cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
    ensure_feature_ranking(cfg, sets, splits.train)
    return get_active_features(cfg, sets, str(len(sets["feature_pool"])))


def family_counts(features: list[str], groups: dict[str, list[str]]) -> dict:
    """Which extra official columns a feature list contains: the seven window-count ct_* columns, the other ct_* columns and the TTL columns."""
    window, ttl = set(groups["connection_counts"]), set(groups["ttl"])
    other_ct = [f for f in features if f.startswith("ct_") and f not in window and f not in ttl]
    return {"n_ct_window": sum(f in window for f in features), "n_ct_other": len(other_ct), "n_ttl": sum(f in ttl for f in features),
            "ct_window_cols": ";".join(f for f in features if f in window), "ct_other_cols": ";".join(other_ct),
            "ttl_cols": ";".join(f for f in features if f in ttl)}


def shap_with_bootstrap(model, preprocessor, train_df: pd.DataFrame, features: list[str], n_rows: int, n_boot: int, seed: int,
                        background: int = 100) -> tuple[pd.Series, np.ndarray]:
    """Global SHAP importance (mean over classes of the mean |SHAP| of `n_rows` random training rows) and `n_boot` bootstrap resamples of
    those rows, as an (n_boot, n_features) array. The rows are drawn by SHAPExplainer with a fixed generator and the resample indices depend
    only on (seed, resample number), so models trained on the same data are explained on the same rows and resampled identically (paired)."""
    X = preprocessor.transform_features(train_df)
    per_class = SHAPExplainer(model, features, background_samples=background).compute_shap_values(X, n_rows)
    row_importance = np.mean([np.abs(c) for c in per_class], axis=0)                       # (rows, features)
    n = len(row_importance)
    boot = np.stack([row_importance[np.random.default_rng(seed * 1000 + b).integers(0, n, n)].mean(axis=0) for b in range(n_boot)])
    return pd.Series(row_importance.mean(axis=0), index=features), boot


def run_one(cfg: dict, sets: dict, splits, features: list[str], tier: str, seed: int, model_type: str, pool: str, with_shap: bool, pooled: bool = False,
            plots_dir: Path | None = None):
    """Train once; return (metrics row, SHAP importance Series or None, bootstrap array or None). With `plots_dir`, also write the tier's confusion matrix and ROC figure."""
    pred = {}
    result = train_and_evaluate(cfg, sets, tier, True, splits, False, pred, features=features)
    if plots_dir is not None and not pooled:
        write_tier_plots(pred, plots_dir, len(sets["feature_pool"]), tier, *get_label_scheme(cfg)[:2], normal_label=cfg["data"]["normal_category"], model_type=model_type)
    normal = cfg["data"]["normal_category"]
    row = {"pool": pool, "pool_label": pool_label(sets), "model": model_type, "tier": tier, "n_features": len(features), "seed": seed,
           "split": "pooled_random" if pooled else "official", **{m: result.get(m) for m in KEY_METRICS(result)},
           **family_counts(features, cfg["shift"]["feature_groups"])}
    if not pooled:
        det95 = {r["rule"]: r for r in operating_points(pred, normal)}["det95"]
        row.update(det95_threshold=det95["threshold"], det95_val_fpr=det95["val_fpr"], det95_test_fpr=det95["test_fpr"],
                   det95_test_detection=det95["test_detection"], det95_fpr_gap=det95["fpr_gap"])
    if not with_shap:
        return row, None, None
    importance, boot = shap_with_bootstrap(pred["model"], pred["preprocessor"], splits.train, features, cfg["tier_study"]["shap_rows"],
                                           cfg["tier_study"]["bootstrap"], seed)
    return row, importance, boot


def KEY_METRICS(result: dict) -> list[str]:
    return [m for m in KEEP if m in result]


def run_tiers(config: dict, feature_sets: dict, pool: str, model_type: str, seeds=None, tiers=None, with_shap: bool = True, pooled: bool = False,
              plots_dir: Path | None = None):
    """All ranked tiers x seeds for one pool and model. Returns (runs DataFrame, SHAP importance DataFrame, {key: bootstrap array}).
    With `plots_dir`, the seed-42 (`tier_study.seeds[0]`) model of every tier also gets its confusion matrix and ROC figure."""
    seeds = list(seeds or config["tier_study"]["seeds"])
    ensure_pool_ranking(config, feature_sets, pool)
    rows, importances, boots = [], [], {}
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, model_type, seed, pooled)
        for tier in tiers or list(cfg["experiments"]["feature_sets"]):
            features = get_active_features(cfg, sets, tier)
            row, importance, boot = run_one(cfg, sets, splits, features, tier, seed, model_type, pool, with_shap and not pooled, pooled,
                                            plots_dir if seed == config["tier_study"]["seeds"][0] else None)
            rows.append(row)
            if importance is not None:
                importances.append(pd.DataFrame({"pool": pool, "pool_label": row["pool_label"], "model": model_type, "tier": tier, "seed": seed,
                                                 "feature": importance.index, "importance": importance.to_numpy()}))
                boots[f"{tier}__{seed}"] = boot
                boots[f"{tier}__features"] = np.array(features)
            logger.info(f"[tiers {model_type} {row['pool_label']}{' pooled' if pooled else ''}] seed={seed} tier={tier}: f1={row['f1']} fpr={row['false_positive_rate']}")
    return pd.DataFrame(rows), (pd.concat(importances, ignore_index=True) if importances else pd.DataFrame()), boots


def run_baselines(config: dict, feature_sets: dict, pool: str, ranked_runs: pd.DataFrame, draws: int | None = None, tiers=None, seeds=None):
    """Ranked (mean over seeds of `ranked_runs`) vs `random_draws` random subsets vs worst-N for the `random_tiers` of one pool (XGBoost).
    Random draw d: model seed 42, split seed 42, subset seed 42 + d; worst-N: all seeds."""
    draws = draws or config["tier_study"]["random_draws"]
    tiers = tiers or config["tier_study"]["random_tiers"]
    seeds = list(seeds or config["tier_study"]["seeds"])
    base_seed = seeds[0]
    cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", base_seed)
    ranked_runs = ranked_runs.assign(tier=ranked_runs["tier"].astype(str))   # a CSV round trip turns the tier names into integers
    rows = []
    for tier in tiers:
        ranked = ranked_runs[ranked_runs["tier"] == tier]
        rows.append({"feature_set": tier, "n_features": int(ranked["n_features"].iloc[0]), "ranking": "ranked", "draw": 0,
                     "f1": round(float(ranked["f1"].mean()), 4), "accuracy": round(float(ranked["accuracy"].mean()), 4)})
        for d in range(draws):
            features = get_random_features(cfg, sets, tier, draw=d)
            r, _, _ = run_one(cfg, sets, splits, features, tier, base_seed, "xgboost", pool, False)
            rows.append({"feature_set": tier, "n_features": len(features), "ranking": "random", "draw": d, "f1": r["f1"], "accuracy": r["accuracy"]})
        worst = []
        for seed in seeds:
            c, s, sp = prepare(config, feature_sets, pool, "xgboost", seed)
            r, _, _ = run_one(c, s, sp, get_worst_features(c, s, tier), tier, seed, "xgboost", pool, False)
            worst.append(r)
        rows.append({"feature_set": tier, "n_features": worst[0]["n_features"], "ranking": "worst", "draw": 0,
                     "f1": round(float(np.mean([w["f1"] for w in worst])), 4), "accuracy": round(float(np.mean([w["accuracy"] for w in worst])), 4)})
    df = pd.DataFrame(rows)
    return df, summarize_baselines(df), summarize_baselines(df.assign(f1=df["accuracy"]))


def plots_dir_for(config: dict, model_type: str, out_dir: str | None = None) -> Path:
    """results/plots/<model_type>/, or <out_dir>/plots/<model_type>/ when `--out-dir` is given."""
    return Path(out_dir) / "plots" / model_type if out_dir else resolve_path(config["paths"]["results_dir"]) / "plots" / model_type


def tier_predictions(cfg: dict, sets: dict, splits, features: list[str], tier: str, model_type: str) -> tuple[dict, bool]:
    """Test-split predictions of one tier's model: loaded from models_saved/<model_type>/ when a model AND its preprocessor were saved for exactly this
    (pool, protocol, tier, feature list), otherwise trained (closed set, the config's seed) and saved there for the next run. -> (predictions, reused)."""
    model_dir = resolve_path(cfg["paths"]["models_dir"]) / model_type
    tag = scheme_tag(cfg)                                   # label scheme + "_blockval" + pool tag: the pool and the protocol are in the file name
    model_path = model_dir / f"{model_type}_{tier}_closed{tag}{artifact_suffix(model_type)}"
    pre_path = model_dir / f"preprocessor_{tier}{tag}.pkl"
    if model_path.exists() and pre_path.exists():
        preprocessor = joblib.load(pre_path)               # only artifacts this project wrote itself are ever loaded
        if list(preprocessor.metadata.get("features", [])) == list(features):
            normal_index = list(preprocessor.target_encoder.classes_).index(cfg["data"]["normal_category"])
            model = create_scheme_model(model_type, cfg["model"]["params"], get_label_scheme(cfg)[2], normal_index)
            model.load(str(model_path))
            _, predictions = evaluate_model(model, preprocessor, splits.test, cfg)
            return predictions, True
    pred: dict = {}
    train_and_evaluate(cfg, sets, tier, False, splits, True, pred, features=features)
    return pred, False


def run_tier_plots(config: dict, feature_sets: dict, pool: str, model_type: str, tiers=None, plots_dir: Path | None = None) -> list[Path]:
    """Confusion matrix and ROC figure of every tier of one pool for one model (seed `tier_study.seeds[0]`, block-grouped protocol); saved models are reused."""
    seed = config["tier_study"]["seeds"][0]
    ensure_pool_ranking(config, feature_sets, pool)
    cfg, sets, splits = prepare(config, feature_sets, pool, model_type, seed)
    out = plots_dir or plots_dir_for(config, model_type)
    scheme, merge_groups, _ = get_label_scheme(cfg)
    written = []
    for tier in tiers or list(cfg["experiments"]["feature_sets"]):
        features = get_active_features(cfg, sets, tier)
        pred, reused = tier_predictions(cfg, sets, splits, features, tier, model_type)
        written += write_tier_plots(pred, out, len(sets["feature_pool"]), tier, scheme, merge_groups, cfg["data"]["normal_category"], model_type)
        logger.info(f"[plots {model_type} {pool_label(sets)}] tier={tier}: {'reused the saved model' if reused else 'trained and saved a model'}")
    return written


def output_dir(config: dict, model_type: str, out_dir: str | None = None) -> Path:
    """results/metrics/<model_type>/, or <out_dir>/<model_type>/ when `--out-dir` is given (e.g. the gitignored results/_local_scratch)."""
    return Path(out_dir) / model_type if out_dir else get_metrics_dir(dict(config, model=dict(config["model"], type=model_type)))


def save(config: dict, model_type: str, label: str, runs: pd.DataFrame | None = None, importances: pd.DataFrame | None = None, boots: dict | None = None,
         suffix: str = "", out_dir: str | None = None) -> None:
    d = output_dir(config, model_type, out_dir)
    d.mkdir(parents=True, exist_ok=True)
    if runs is not None:
        runs.to_csv(d / f"tier_study_{model_type}_{label}_runs{suffix}.csv", index=False)
    if importances is not None and len(importances):
        importances.to_csv(d / f"shap_importance_{model_type}_{label}.csv", index=False)
    if boots:
        np.savez_compressed(d / f"shap_boot_{model_type}_{label}.npz", **boots)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="xgboost", help="a model.type registered in src/models/model_factory.py (non-XGBoost types need tier_study.model_params.<type>)")
    parser.add_argument("--pools", nargs="*")
    parser.add_argument("--parts", nargs="*", choices=["tiers", "baselines", "pooled", "plots"], default=["tiers"])
    parser.add_argument("--no-plots", action="store_true", help="the tiers part writes confusion-matrix and ROC plots of the seed-42 models by default; skip them")
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--out-dir", help="write the outputs under <out-dir>/<model>/ instead of results/metrics/<model>/ (e.g. results/_local_scratch, which is gitignored)")
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    for pool in args.pools or config["tier_study"]["pools"]:
        label = pool_label(prepare(config, feature_sets, pool, args.model, 42)[1])
        if "tiers" in args.parts:
            runs, imps, boots = run_tiers(config, feature_sets, pool, args.model, args.seeds, plots_dir=None if args.no_plots else plots_dir_for(config, args.model, args.out_dir))
            save(config, args.model, label, runs, imps, boots, out_dir=args.out_dir)
            print(label, "\n", runs.groupby("tier")[["accuracy", "f1", "false_positive_rate", "det95_test_fpr"]].mean().round(4).to_string())
        if "baselines" in args.parts:
            d = output_dir(config, args.model, args.out_dir)
            ranked = pd.read_csv(d / f"tier_study_{args.model}_{label}_runs.csv")
            df, summary_f1, summary_acc = run_baselines(config, feature_sets, pool, ranked, seeds=args.seeds)
            df.to_csv(d / f"tier_baselines_{args.model}_{label}.csv", index=False)
            summary_f1.to_csv(d / f"tier_baselines_summary_{args.model}_{label}.csv", index=False)
            summary_acc.to_csv(d / f"tier_baselines_summary_accuracy_{args.model}_{label}.csv", index=False)
            print(summary_f1.to_string(index=False))
        if "pooled" in args.parts:
            runs, _, _ = run_tiers(config, feature_sets, pool, args.model, args.seeds, with_shap=False, pooled=True)
            save(config, args.model, label, runs, suffix="_pooled", out_dir=args.out_dir)
        if "plots" in args.parts:
            for path in run_tier_plots(config, feature_sets, pool, args.model, plots_dir=plots_dir_for(config, args.model, args.out_dir)):
                print(path)


if __name__ == "__main__":
    main()
