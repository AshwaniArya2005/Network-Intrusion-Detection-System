"""FEW-SHOT adaptation on the official split: how many labelled test-distribution rows does it take to close the gap?

    python pipelines/run_adaptation.py [--pools base full] [--ks 100 500 1000 5000] [--runs 5]

Per run i (model seed 42 + i, adaptation draw seed 1000 + i) and per pool it trains the zero-shot model once, then for each k
draws k labelled rows from the official test file (stratified by the training target classes, src/adaptation.py), REMOVES
them from the evaluation set and scores, on the same remaining rows:

  zero_shot      access zero-shot       the model as trained; det95 threshold chosen on validation
  thr_adapt      access few-shot (ii)   the same model, det95 threshold re-chosen on the k adaptation rows
  retrain_f<f>   access few-shot (i)    retrained on train + the k rows carrying a fraction f of the sample weight
                                        (f = 0.1 / 0.3 / 0.5; the primary f = 0.3 was declared in results/06_fpr_and_adaptation.md, section `Source: shift_and_fewshot_protocol.md`);
                                        det95 threshold chosen on validation
  retrain_split_f<f>   few-shot (i)+(ii) (--split-threshold)   the k rows are split in two halves: the model is retrained on one half
                                        (weight fraction f) and the det95 threshold is chosen on the OTHER half, which the model never saw
  retrain_f<f>_domain<c>  few-shot + transductive (B4)   the same, with the training rows also importance-weighted towards the
                                        unlabelled official-test features (src.adaptation.domain_importance_weights, clip c)

(No threshold is re-chosen on adaptation rows for a retrained model: they are training rows, so it would be optimistic.)
Writes under results/metrics/<model.type>/ (pool size in the names): adaptation_<N>f_runs.csv, adaptation_<N>f_summary.csv
(mean / std over runs per k and method) and results/plots/<model.type>/adaptation_curve_<N>f.png.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from dataclasses import replace

from pipelines.run_operating_point import operating_points
from pipelines.train_pipeline import evaluate_model, load_split_data, train_and_evaluate
from src.adaptation import domain_importance_weights, draw_adaptation_sample, with_adaptation
from src.evaluation.metrics import attack_rates, select_attack_threshold
from src.utils.config_loader import apply_pool_variant, choose_pool, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

PRIMARY_FRACTION = 0.3
KEEP = ["accuracy", "f1", "detection_rate", "false_positive_rate", "recall_Normal", "fpr_at_90_detection", "fpr_at_95_detection",
        "fpr_at_99_detection", "roc_auc_attack_vs_normal", "ece", "brier", "unknown_detection_rate", "false_unknown_alarm_rate", "unknown_auroc"]
OPEN_SET = ["unknown_detection_rate", "false_unknown_alarm_rate", "unknown_auroc"]


def score_rows(model, preprocessor, frame: pd.DataFrame, normal_index: int) -> np.ndarray:
    """1 - P(Normal) of arbitrary rows under a trained model."""
    return 1 - model.predict_proba(preprocessor.transform_features(frame))[:, normal_index]


def fewshot_rows(metrics: dict, pred: dict, normal: str, base: dict) -> dict:
    """The recorded columns of one evaluation: argmax metrics, normal_to_<class> shares and the open-set metrics
    (`base` supplies them for methods that reuse the zero-shot model, whose open-set scores do not depend on the test rows)."""
    row = {m: metrics.get(m, base.get(m)) for m in KEEP}
    fine, called = np.asarray(pred["fine_grained_true"]), np.asarray(pred["y_pred_labels"])
    row["normal_to_Fuzzers"] = round(float((called[fine == normal] == "Fuzzers").mean()), 4)
    return row


def run_adaptation_pool(config: dict, feature_sets: dict, pool: str, ks=(100, 500, 1000, 5000), fractions=(0.1, 0.3, 0.5), runs: int = 5,
                        domain_clip: float | None = None, split_threshold: bool = False) -> pd.DataFrame:
    """Rows per (run, k, method). With `domain_clip` only the combined few-shot + transductive retraining rows are produced, with
    `split_threshold` only the retrain-on-half / threshold-on-the-other-half rows (the zero-shot and few-shot-only rows come from the
    plain run)."""
    rows = []
    for i in range(runs):
        seed, draw_seed = 42 + i, 1000 + i
        cfg = apply_pool_variant(config, pool)
        cfg["project"]["seed"], cfg["model"]["params"]["random_state"] = seed, seed
        splits = load_split_data(cfg, use_official_split=True)
        cfg, sets = choose_pool(cfg, feature_sets, splits.train.columns)
        features, tier, label = list(sets["feature_pool"]), None, pool_label(sets)
        tier = str(len(features))
        normal, target = cfg["data"]["normal_category"], cfg["data"]["target_column"]
        multiplier = domain_importance_weights(splits.train, splits.test, features, domain_clip, seed) if domain_clip else None
        base_pred = {}
        base = train_and_evaluate(cfg, sets, tier, True, splits, False, base_pred, features=features)  # the zero-shot model (also gives the encoders)
        model, pre = base_pred["model"], base_pred["preprocessor"]
        classes = list(pre.target_encoder.classes_)
        normal_index = classes.index(normal)
        val_attack = np.asarray(base_pred["val_labels"]) != normal
        val_score = 1 - base_pred["y_proba_val"][:, normal_index]
        val_threshold = select_attack_threshold(val_attack, val_score, target_detection=0.95)
        for k in ks:
            adapt, remaining = draw_adaptation_sample(splits.test, k, target, draw_seed)
            remaining = remaining.reset_index(drop=True)
            common = {"pool": pool, "pool_label": label, "run": i, "seed": seed, "draw_seed": draw_seed, "k": k,
                      "n_eval": len(remaining), "n_adapt": len(adapt)}
            if split_threshold:  # retrain on one half of the k rows, choose the det95 threshold on the other half
                fit_half, threshold_half = draw_adaptation_sample(adapt, k // 2, target, draw_seed)
                for f in fractions:
                    adapted = with_adaptation(splits, fit_half, remaining, f)
                    pred = {}
                    result = train_and_evaluate(cfg, sets, tier, True, adapted, False, pred, features=features)
                    scores = score_rows(pred["model"], pred["preprocessor"], threshold_half, normal_index)
                    threshold = select_attack_threshold(np.asarray(threshold_half["attack_cat"]) != normal, scores, target_detection=0.95)
                    attack = np.asarray(pred["fine_grained_true"]) != normal
                    det, fpr = attack_rates(attack, 1 - pred["y_proba"][:, normal_index], threshold)
                    rows.append({**common, "method": f"retrain_split_f{f}", "access": "few-shot", "threshold_source": "held-out half of the adaptation sample",
                                 **fewshot_rows(result, pred, normal, base), "det95_test_fpr": round(fpr, 4), "det95_test_detection": round(det, 4)})
                logger.info(f"[adaptation {label} split] run={i} k={k} done")
                continue
            if domain_clip:  # combined rows only
                for f in fractions:
                    adapted = replace(with_adaptation(splits, adapt, remaining, f), weight_multiplier=np.r_[multiplier, np.ones(len(adapt))])
                    pred = {}
                    result = train_and_evaluate(cfg, sets, tier, True, adapted, False, pred, features=features)
                    op = {r["rule"]: r for r in operating_points(pred, normal)}["det95"]
                    rows.append({**common, "method": f"retrain_f{f}_domain{domain_clip:g}", "access": "few-shot+transductive",
                                 "threshold_source": "validation", **fewshot_rows(result, pred, normal, base),
                                 "det95_test_fpr": op["test_fpr"], "det95_test_detection": op["test_detection"]})
                logger.info(f"[adaptation {label} domain{domain_clip:g}] run={i} k={k} done")
                continue
            metrics, remaining_pred = evaluate_model(model, pre, remaining, cfg)
            test_attack = np.asarray(remaining_pred["fine_grained_true"]) != normal
            test_score = 1 - remaining_pred["y_proba"][:, normal_index]
            zero = fewshot_rows(metrics, remaining_pred, normal, base)
            det, fpr = attack_rates(test_attack, test_score, val_threshold)
            rows.append({**common, "method": "zero_shot", "access": "zero-shot", "threshold_source": "validation", **zero,
                         "det95_test_fpr": round(fpr, 4), "det95_test_detection": round(det, 4)})
            adapt_threshold = select_attack_threshold(np.asarray(adapt["attack_cat"]) != normal, score_rows(model, pre, adapt, normal_index),
                                                      target_detection=0.95)
            det, fpr = attack_rates(test_attack, test_score, adapt_threshold)
            rows.append({**common, "method": "thr_adapt", "access": "few-shot", "threshold_source": "adaptation sample", **zero,
                         "det95_test_fpr": round(fpr, 4), "det95_test_detection": round(det, 4)})
            for f in fractions:
                adapted = with_adaptation(splits, adapt, remaining, f)
                pred = {}
                result = train_and_evaluate(cfg, sets, tier, True, adapted, False, pred, features=features)
                op = {r["rule"]: r for r in operating_points(pred, normal)}["det95"]
                rows.append({**common, "method": f"retrain_f{f}", "access": "few-shot", "threshold_source": "validation",
                             **fewshot_rows(result, pred, normal, base), "det95_test_fpr": op["test_fpr"], "det95_test_detection": op["test_detection"]})
            logger.info(f"[adaptation {label}] run={i} k={k} done")
    return pd.DataFrame(rows)


def summarise(runs_df: pd.DataFrame) -> pd.DataFrame:
    numeric = [c for c in runs_df.select_dtypes("number").columns if c not in {"run", "seed", "draw_seed", "k", "n_eval", "n_adapt"}]
    long = runs_df.melt(id_vars=["pool", "k", "method", "access", "run"], value_vars=numeric, var_name="metric")
    return (long.groupby(["pool", "k", "method", "access", "metric"], sort=False)["value"]
            .agg(mean="mean", std=lambda v: v.std(ddof=1) if v.notna().sum() > 1 else float("nan"), n_runs="count").round(4).reset_index())


def plot_curve(summary: pd.DataFrame, path: Path, pooled_reference: dict[str, float] | None = None) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, metric, title in zip(axes, ["det95_test_fpr", "det95_test_detection"], ["FPR at the det95 operating point", "Detection at the det95 operating point"]):
        for method, style in [("zero_shot", "k--"), ("thr_adapt", "b-o"), (f"retrain_f{PRIMARY_FRACTION}", "r-o")]:
            g = summary[(summary["method"] == method) & (summary["metric"] == metric)].sort_values("k")
            if method == "zero_shot":
                ax.axhline(g["mean"].mean(), color="k", ls="--", label="zero-shot")
            else:
                ax.errorbar(g["k"], g["mean"], yerr=g["std"], fmt=style, capsize=3, label=f"{method} (few-shot)")
        if pooled_reference and metric in pooled_reference:
            ax.axhline(pooled_reference[metric], color="g", ls=":", label="pooled-split FPR (argmax)")
        ax.set_xscale("log"); ax.set_xlabel("labelled adaptation rows k"); ax.set_title(title); ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["base", "full"])
    parser.add_argument("--ks", nargs="*", type=int, default=[100, 500, 1000, 5000])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--fractions", nargs="*", type=float, default=[0.1, 0.3, 0.5])
    parser.add_argument("--domain-clip", type=float, help="few-shot + transductive: also importance-weight the training rows (clip)")
    parser.add_argument("--split-threshold", action="store_true", help="retrain on half of the k rows, choose the det95 threshold on the other half")
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    for pool in args.pools:
        runs_df = run_adaptation_pool(config, feature_sets, pool, tuple(args.ks), tuple(args.fractions), args.runs, args.domain_clip, args.split_threshold)
        label = runs_df["pool_label"].iloc[0]
        summary = summarise(runs_df)
        tag = f"_domain{args.domain_clip:g}" if args.domain_clip else ("_split" if args.split_threshold else "")
        runs_df.to_csv(metrics_dir / f"adaptation_{label}{tag}_runs.csv", index=False)
        summary.to_csv(metrics_dir / f"adaptation_{label}{tag}_summary.csv", index=False)
        if args.domain_clip or args.split_threshold:
            print(label, summary[summary["metric"].isin(["false_positive_rate", "det95_test_fpr", "fpr_at_95_detection", "detection_rate", "accuracy"])]
                  .pivot_table(index=["k", "method"], columns="metric", values="mean").round(4).to_string())
            continue
        reference = None
        headline = metrics_dir / "headline_summary.csv"
        if headline.exists():  # pooled-random FPR of the same pool as a reference (argmax, so shown on the FPR panel only)
            h = pd.read_csv(headline)
            h = h[(h["pool"] == pool) & (h["split"] == "pooled_random") & (h["metric"] == "false_positive_rate")]
            reference = {"det95_test_fpr": float(h["mean"].iloc[0])} if len(h) else None
        plot_curve(summary, resolve_path(config["paths"]["results_dir"]) / "plots" / config["model"]["type"] / f"adaptation_curve_{label}.png", reference)
        print(label, "\n", summary[summary["metric"].isin(["det95_test_fpr", "det95_test_detection", "false_positive_rate", "accuracy"])]
              .pivot_table(index=["k", "method"], columns="metric", values="mean").round(4).to_string())


if __name__ == "__main__":
    main()
