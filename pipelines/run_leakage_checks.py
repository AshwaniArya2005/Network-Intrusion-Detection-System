"""Task 2.6: is the few-shot result adaptation or neighbour leakage? (protocol: results/task_2_6_protocol.md)

    python pipelines/run_leakage_checks.py [--pools base full] [--ks 1000 5000] [--runs 5] [--checks twins blocks validation]

Method of record: `retrain_split_f0.5` (FEW-SHOT): k labelled rows from the official test file, half used to retrain with weight fraction
0.5, the 95%-detection threshold chosen on the other half; reported as det95_test_fpr / det95_test_detection with accuracy and ECE.
Runs i = 0..4 use model seed 42 + i and adaptation draw seed 1000 + i (the draws of pipelines/run_adaptation.py).

twins      check 1: share of evaluation rows with an exact / near (L-inf <= 0.1, 0.25) twin in the adaptation set, vs in an equally sized random
           subset of the TRAINING rows and in the whole training set; the metrics on all evaluation rows, on the rows with NO near twin
           (<= 0.1) in the adaptation set and on the rows that have one. The zero-shot model is scored on the same subsets.
blocks     check 2: the ordered known official-test rows are cut into contiguous blocks; adaptation rows from some blocks, evaluation rows from
           the others, with a gap dropped at every boundary (src/neighbours.block_split). Conditions on the SAME evaluation rows: zero-shot,
           `within_E` (adaptation rows drawn at random from the evaluation blocks) and `block_disjoint` (adaptation rows from the other blocks).
shift_auc  check 6: the train-vs-test Normal AUC of Task 2.5 Step A with random vs block-grouped cross-validation.
validation check 5: validation built from contiguous blocks of the training file vs the standard random validation: FPR of the model on its
           validation rows and on the official test (the validation-vs-test gap of Task 2a).

Writes under results/metrics/<model.type>/ (pool size in the names): leakage_<N>f_runs.csv, leakage_<N>f_summary.csv,
leakage_<N>f_validation_blocks.csv.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from dataclasses import replace

from pipelines.run_adaptation import score_rows
from pipelines.train_pipeline import load_split_data, train_and_evaluate
from src.adaptation import draw_adaptation_sample, with_adaptation
from src.data_loader import load_unsw
from src.evaluation.metrics import attack_rates, expected_calibration_error, select_attack_threshold
from src.neighbours import Embedder, block_split, exact_twin_mask, nearest_distance, twin_shares
from src.preprocessing import add_merged_label, split_known_unknown
from src.utils.config_loader import (
    apply_pool_variant, choose_pool, get_label_scheme, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path,
)
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

FRACTION = 0.5
BLOCK_SIZE, BUFFER, ADAPT_SHARE = 1000, 200, 0.4
NEAR = (0.1, 0.25)


def subset_metrics(proba: np.ndarray, y_true: np.ndarray, normal_index: int, threshold: float, mask: np.ndarray, ece_bins: int) -> dict:
    """det95-operating-point FPR / detection, accuracy and ECE of the rows selected by `mask`."""
    y, p = np.asarray(y_true)[mask], proba[mask]
    attack = y != normal_index
    if mask.sum() == 0 or attack.all() or not attack.any():
        return {"n_eval": int(mask.sum()), "det95_test_fpr": float("nan"), "det95_test_detection": float("nan"), "accuracy": float("nan"), "ece": float("nan")}
    det, fpr = attack_rates(attack, 1 - p[:, normal_index], threshold)
    return {"n_eval": int(mask.sum()), "det95_test_fpr": round(fpr, 4), "det95_test_detection": round(det, 4),
            "accuracy": round(float((p.argmax(axis=1) == y).mean()), 4), "ece": round(expected_calibration_error(y, p, ece_bins), 4)}


class Context:
    """One run's trained zero-shot model, encoders and the pieces every check needs."""

    def __init__(self, config: dict, feature_sets: dict, pool: str, run: int):
        self.run, self.seed, self.draw_seed = run, 42 + run, 1000 + run
        cfg = apply_pool_variant(config, pool)
        cfg["project"]["seed"], cfg["model"]["params"]["random_state"] = self.seed, self.seed
        splits = load_split_data(cfg, use_official_split=True)
        self.cfg, self.sets = choose_pool(cfg, feature_sets, splits.train.columns)
        self.splits, self.pool = splits, pool
        self.features = list(self.sets["feature_pool"])
        self.tier, self.label = str(len(self.features)), pool_label(self.sets)
        self.target, self.normal = self.cfg["data"]["target_column"], self.cfg["data"]["normal_category"]
        self.bins = self.cfg["evaluation"]["ece_bins"]
        pred = {}
        train_and_evaluate(self.cfg, self.sets, self.tier, False, splits, False, pred, features=self.features)
        self.model, self.pre = pred["model"], pred["preprocessor"]
        self.normal_index = list(self.pre.target_encoder.classes_).index(self.normal)
        val_attack = np.asarray(pred["val_labels"]) != self.normal
        self.val_threshold = select_attack_threshold(val_attack, 1 - pred["y_proba_val"][:, self.normal_index], target_detection=0.95)
        self.embedder = Embedder(self.features).fit(splits.train)
        self.test_emb = self.embedder.transform(splits.test)
        self.train_emb = self.embedder.transform(splits.train)
        self.y_all = self.pre.transform(splits.test)[1]

    def zero_shot(self, rows: pd.DataFrame, mask: np.ndarray | None = None) -> dict:
        proba = self.model.predict_proba(self.pre.transform_features(rows))
        y = self.pre.transform(rows)[1]
        return subset_metrics(proba, y, self.normal_index, self.val_threshold, np.ones(len(rows), bool) if mask is None else mask, self.bins)

    def adapted(self, adapt: pd.DataFrame, evaluation: pd.DataFrame, draw_seed: int):
        """Retrain on half of `adapt` (weight fraction 0.5), choose the det95 threshold on the other half; return (proba, y_true, threshold)
        for `evaluation` (rows in their given order)."""
        fit_half, threshold_half = draw_adaptation_sample(adapt, len(adapt) // 2, self.target, draw_seed)
        adapted = with_adaptation(self.splits, fit_half, evaluation, FRACTION)
        pred = {}
        train_and_evaluate(self.cfg, self.sets, self.tier, False, adapted, False, pred, features=self.features)
        threshold = select_attack_threshold(np.asarray(threshold_half["attack_cat"]) != self.normal,
                                            score_rows(pred["model"], pred["preprocessor"], threshold_half, self.normal_index), target_detection=0.95)
        return pred["y_proba"], np.asarray(pred["y_test"]), threshold

    def twin_distance(self, evaluation_emb: np.ndarray, adapt_emb: np.ndarray) -> np.ndarray:
        return nearest_distance(evaluation_emb, adapt_emb, cutoff=max(NEAR))


def row(ctx: Context, k: int, check: str, condition: str, method: str, access: str, metrics: dict, shares: dict | None = None) -> dict:
    shares = shares or {}
    return {"pool": ctx.pool, "pool_label": ctx.label, "run": ctx.run, "seed": ctx.seed, "draw_seed": ctx.draw_seed, "k": k, "check": check,
            "condition": condition, "method": method, "access": access, **metrics,
            **{f"twin_{name}": round(v, 4) for name, v in shares.items()}}


def run_runs(config: dict, feature_sets: dict, pool: str, ks=(1000, 5000), runs: int = 5, checks=("twins", "blocks"),
             block_size: int = BLOCK_SIZE, buffer: int = BUFFER, adapt_share: float = ADAPT_SHARE) -> pd.DataFrame:
    rows = []
    for i in range(runs):
        ctx = Context(config, feature_sets, pool, i)
        test = ctx.splits.test
        train_dist_all = nearest_distance(ctx.test_emb, ctx.train_emb, cutoff=max(NEAR)) if "twins" in checks else None
        train_exact_all = exact_twin_mask(test, ctx.splits.train, ctx.features) if "twins" in checks else None
        for k in ks:
            if "twins" in checks:
                adapt, remaining = draw_adaptation_sample(test, k, ctx.target, ctx.draw_seed)
                pos = remaining.index.to_numpy()
                remaining = remaining.reset_index(drop=True)
                dist = ctx.twin_distance(ctx.test_emb[pos], ctx.test_emb[adapt.index.to_numpy()])
                exact = exact_twin_mask(remaining, adapt, ctx.features)
                sub = ctx.splits.train.sample(k, random_state=ctx.draw_seed)
                sub_dist = ctx.twin_distance(ctx.test_emb[pos], ctx.embedder.transform(sub))
                sub_exact = exact_twin_mask(remaining, sub, ctx.features)
                rows.append(row(ctx, k, "twins", "twin_share_vs_adaptation_rows", "n/a", "n/a", {}, twin_shares(dist, exact, NEAR)))
                rows.append(row(ctx, k, "twins", "twin_share_vs_random_training_subset", "n/a", "n/a", {}, twin_shares(sub_dist, sub_exact, NEAR)))
                rows.append(row(ctx, k, "twins", "twin_share_vs_whole_training_set", "n/a", "n/a", {}, twin_shares(train_dist_all[pos], train_exact_all[pos], NEAR)))
                proba, y, threshold = ctx.adapted(adapt, remaining, ctx.draw_seed)
                near = dist <= NEAR[0] + 1e-12
                for name, mask in (("all_eval", np.ones(len(remaining), bool)), ("no_near_twin_0.1", ~near), ("has_near_twin_0.1", near)):
                    rows.append(row(ctx, k, "twins", name, "retrain_split_f0.5", "few-shot", subset_metrics(proba, y, ctx.normal_index, threshold, mask, ctx.bins)))
                    rows.append(row(ctx, k, "twins", name, "zero_shot", "zero-shot", ctx.zero_shot(remaining, mask)))
            if "blocks" in checks:
                adapt_pos, eval_pos = block_split(len(test), block_size, buffer, adapt_share, ctx.draw_seed)
                evaluation = test.iloc[eval_pos].reset_index(drop=True)
                eval_emb = ctx.test_emb[eval_pos]
                rows.append(row(ctx, k, "blocks", "zero_shot_E", "zero_shot", "zero-shot", ctx.zero_shot(evaluation)))
                # adaptation rows drawn at random from the evaluation blocks themselves (neighbours of the evaluation rows)
                within, rest = draw_adaptation_sample(test.iloc[eval_pos], k, ctx.target, ctx.draw_seed)
                rest_pos = np.setdiff1d(eval_pos, within.index.to_numpy())
                proba, y, threshold = ctx.adapted(within, rest.reset_index(drop=True), ctx.draw_seed)
                shares = twin_shares(ctx.twin_distance(ctx.test_emb[rest_pos], ctx.test_emb[within.index.to_numpy()]),
                                     exact_twin_mask(rest, within, ctx.features), NEAR)
                rows.append(row(ctx, k, "blocks", "within_E", "retrain_split_f0.5", "few-shot",
                                subset_metrics(proba, y, ctx.normal_index, threshold, np.ones(len(rest), bool), ctx.bins), shares))
                # adaptation rows from the other blocks (a gap of `buffer` rows on each side of every boundary is dropped from both)
                disjoint, _ = draw_adaptation_sample(test.iloc[adapt_pos], min(k, len(adapt_pos) - 1), ctx.target, ctx.draw_seed)
                proba, y, threshold = ctx.adapted(disjoint, evaluation, ctx.draw_seed)
                shares = twin_shares(ctx.twin_distance(eval_emb, ctx.test_emb[disjoint.index.to_numpy()]), exact_twin_mask(evaluation, disjoint, ctx.features), NEAR)
                rows.append(row(ctx, k, "blocks", "block_disjoint", "retrain_split_f0.5", "few-shot",
                                subset_metrics(proba, y, ctx.normal_index, threshold, np.ones(len(evaluation), bool), ctx.bins), shares))
            logger.info(f"[leakage {ctx.label}] run={i} k={k} done")
    return pd.DataFrame(rows)


def summarise(runs_df: pd.DataFrame) -> pd.DataFrame:
    keys = ["pool", "pool_label", "k", "check", "condition", "method", "access"]
    numeric = [c for c in runs_df.select_dtypes("number").columns if c not in {"run", "seed", "draw_seed", "k"}]
    long = runs_df.melt(id_vars=keys + ["run"], value_vars=numeric, var_name="metric").dropna(subset=["value"])
    return (long.groupby(keys + ["metric"], sort=False)["value"].agg(mean="mean", std=lambda v: v.std(ddof=1) if len(v) > 1 else float("nan"), n_runs="count")
            .round(4).reset_index())


def ordered_training_rows(config: dict) -> pd.DataFrame:
    """The known training-file rows in FILE order (load_split_data shuffles them when it splits train / validation)."""
    data = config["data"]
    df = load_unsw(resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]), seed=config["project"]["seed"],
                   synthetic_rows=data["synthetic_fallback_rows"])
    df = add_merged_label(df, get_label_scheme(config)[1], source_column=data["fine_grained_target_column"], target_column=data["target_column"])
    known, _ = split_known_unknown(df, data["unknown_attack_categories"], data["target_column"])
    return known[known["split"] == "train"].reset_index(drop=True)


def run_validation_blocks(config: dict, feature_sets: dict, pool: str, seeds=(42, 43, 44, 45, 46), block_size: int = BLOCK_SIZE,
                          buffer: int = BUFFER) -> pd.DataFrame:
    """Check 5: argmax FPR / detection of a model on (a) the standard random validation rows and (b) a model trained without a block-built
    validation set, on those block-validation rows; both models are also scored on the official test."""
    rows = []
    for seed in seeds:
        cfg = apply_pool_variant(config, pool)
        cfg["project"]["seed"], cfg["model"]["params"]["random_state"] = seed, seed
        splits = load_split_data(cfg, use_official_split=True)
        cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
        features, tier, normal = list(sets["feature_pool"]), None, cfg["data"]["normal_category"]
        tier = str(len(features))
        ordered = ordered_training_rows(cfg)
        val_pos, train_pos = block_split(len(ordered), block_size, buffer, cfg["data"]["val_size"], seed)
        block_splits = replace(splits, train=ordered.iloc[train_pos].reset_index(drop=True), val=ordered.iloc[val_pos].reset_index(drop=True))
        for name, sp in (("random_validation", splits), ("block_validation", block_splits)):
            pred = {}
            train_and_evaluate(cfg, sets, tier, False, sp, False, pred, features=features)
            labels = np.asarray(pred["preprocessor"].decode_target(pred["model"].predict(pred["preprocessor"].transform_features(sp.val))))
            truth = sp.val["attack_cat"].to_numpy()
            test_called = np.asarray(pred["y_pred_labels"]) != normal
            test_attack = np.asarray(pred["fine_grained_true"]) != normal
            val_called, val_attack = labels != normal, truth != normal
            rows.append({"pool": pool, "pool_label": pool_label(sets), "seed": seed, "validation": name, "n_train": len(sp.train), "n_val": len(sp.val),
                         "val_fpr": round(float(val_called[~val_attack].mean()), 4), "val_detection": round(float(val_called[val_attack].mean()), 4),
                         "test_fpr": round(float(test_called[~test_attack].mean()), 4), "test_detection": round(float(test_called[test_attack].mean()), 4)})
            rows[-1]["fpr_gap"] = round(rows[-1]["test_fpr"] - rows[-1]["val_fpr"], 4)
    return pd.DataFrame(rows)


def shift_auc_by_cv(config: dict, feature_sets: dict, pool: str, seed: int = 42, block_size: int = BLOCK_SIZE) -> dict:
    """Check 6: the train-Normal vs test-Normal classifier of Task 2.5 Step A with random 5-fold CV and with CV grouped by contiguous
    blocks of file rows (every block, hence every neighbourhood, sits in a single fold). If neighbouring flows leak between folds the
    random-CV AUC is the inflated one."""
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import GroupKFold, cross_val_predict
    from xgboost import XGBClassifier
    from scripts.characterize_shift import shift_classifier
    from scripts.diagnose_normal_fuzzers import CV_PARAMS, codes
    from src.preprocessing import engineer_features
    cfg = apply_pool_variant(config, pool)
    cfg["project"]["seed"] = seed
    splits = load_split_data(cfg, use_official_split=True)
    cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
    features, normal = list(sets["feature_pool"]), cfg["data"]["normal_category"]
    train_rows, test_rows = ordered_training_rows(cfg), splits.test
    keep = lambda df: df["attack_cat"].to_numpy() == normal  # noqa: E731
    train_n, test_n = engineer_features(train_rows[keep(train_rows)], allow_missing=True), engineer_features(test_rows[keep(test_rows)], allow_missing=True)
    random_auc, _ = shift_classifier(train_n.reset_index(drop=True), test_n.reset_index(drop=True), features, seed)
    groups = np.r_[train_rows.index[keep(train_rows)].to_numpy() // block_size, 100000 + test_rows.index[keep(test_rows)].to_numpy() // block_size]
    X, y = codes(pd.concat([train_n, test_n], ignore_index=True), features), np.r_[np.zeros(len(train_n)), np.ones(len(test_n))]
    proba = cross_val_predict(XGBClassifier(random_state=seed, **CV_PARAMS), X, y, cv=GroupKFold(5), groups=groups, method="predict_proba")[:, 1]
    return {"pool": pool, "pool_label": pool_label(sets), "seed": seed, "block_size": block_size, "n_train_normal": len(train_n), "n_test_normal": len(test_n),
            "auc_random_cv": round(float(random_auc), 4), "auc_block_cv": round(float(roc_auc_score(y, proba)), 4)}


def validation_filename(label: str, block_size: int) -> str:
    """leakage_<N>f_validation_blocks.csv for the declared 1,000-row blocks; other block sizes get their own file (never overwritten)."""
    return f"leakage_{label}_validation_blocks{'' if block_size == BLOCK_SIZE else f'_b{block_size}'}.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["base", "full"])
    parser.add_argument("--ks", nargs="*", type=int, default=[1000, 5000])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--checks", nargs="*", choices=["twins", "blocks", "validation", "shift_auc"], default=["twins", "blocks", "validation"])
    parser.add_argument("--val-block-size", type=int, default=BLOCK_SIZE, help="block size of check 5 (the declared protocol uses 1,000; other sizes are exploratory)")
    parser.add_argument("--val-buffer", type=int, default=BUFFER)
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    for pool in args.pools:
        if set(args.checks) & {"twins", "blocks"}:
            runs_df = run_runs(config, feature_sets, pool, tuple(args.ks), args.runs, tuple(c for c in args.checks if c != "validation"))
            label = runs_df["pool_label"].iloc[0]
            runs_df.to_csv(metrics_dir / f"leakage_{label}_runs.csv", index=False)
            summary = summarise(runs_df)
            summary.to_csv(metrics_dir / f"leakage_{label}_summary.csv", index=False)
            print(label, "\n", summary[summary["metric"].isin(["det95_test_fpr", "det95_test_detection", "twin_near_twin_0.1"])]
                  .pivot_table(index=["k", "check", "condition", "method"], columns="metric", values="mean").round(4).to_string())
        if "shift_auc" in args.checks:
            row_ = shift_auc_by_cv(config, feature_sets, pool)
            pd.DataFrame([row_]).to_csv(metrics_dir / f"leakage_{row_['pool_label']}_shift_auc.csv", index=False)
            print(row_)
        if "validation" in args.checks:
            val = run_validation_blocks(config, feature_sets, pool, tuple(range(42, 42 + args.runs)), args.val_block_size, args.val_buffer)
            val.to_csv(metrics_dir / validation_filename(val["pool_label"].iloc[0], args.val_block_size), index=False)
            print(val.groupby("validation")[["val_fpr", "val_detection", "test_fpr", "test_detection", "fpr_gap"]].mean().round(4).to_string())


if __name__ == "__main__":
    main()
