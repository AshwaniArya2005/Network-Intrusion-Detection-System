"""Tables for Task 6 from results/metrics/xgboost/cross_dataset_*.csv (protocol: results/05_novelty4_cross_dataset.md, section `Source: cross_dataset_protocol.md`).

    python scripts/cross_dataset_summary.py

Writes cross_dataset_step1_zero_shot.md, cross_dataset_step2_diagnostic.md, cross_dataset_step3_align.md and cross_dataset_step4_fewshot.md. The declared readings are applied here:
"stable beats random" only when it holds in a majority of seeds with an interval over seeds that excludes 0; the few-shot success level is FPR at the held-out-half threshold at or below 0.15 with detection
at least 0.90, or balanced accuracy within 0.05 of the leak-free reference; "the source data helps" only where source+target beats target-only in a majority of paired runs with an interval excluding 0.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy import stats

from src.utils.config_loader import get_metrics_dir, load_config

METRICS = [("balanced_accuracy", "balanced accuracy (argmax)"), ("auroc", "AUROC"), ("fpr_at_threshold", "FPR at the 95%-detection threshold"), ("detection_at_threshold", "detection at that threshold"),
           ("fpr_at_95_threshold_free", "FPR at exactly 95% detection"), ("predicted_attack_share", "predicted attack share")]
SUCCESS_FPR, SUCCESS_DETECTION, SUCCESS_BALANCED = 0.15, 0.90, 0.05


def ms(values, digits: int = 3) -> str:
    v = pd.Series(values).dropna()
    return "n/a" if v.empty else (f"{v.mean():.{digits}f} +/- {v.std(ddof=1):.{digits}f}" if len(v) > 1 else f"{v.mean():.{digits}f}")


def metric_table(runs: pd.DataFrame, keys: list[str]) -> list[str]:
    cols = [c for c, _ in METRICS]
    lines = ["| " + " | ".join([*keys, *[n for _, n in METRICS], "degenerate runs"]) + " |", "|" + "---|" * (len(keys) + len(METRICS) + 1)]
    for k, g in runs.groupby(keys, sort=False):
        k = k if isinstance(k, tuple) else (k,)
        lines.append("| " + " | ".join([*map(str, k), *(ms(g[c]) for c in cols), f"{int(g['degenerate'].sum())} of {len(g)}"]) + " |")
    return lines


def paired_interval(diff: pd.Series, level: float = 0.95) -> tuple[float, float, float]:
    """(mean, lower, upper) of a paired difference over its observations (t interval)."""
    d = pd.Series(diff).dropna().to_numpy(dtype=float)
    if len(d) < 2:
        return (float(d.mean()) if len(d) else np.nan, np.nan, np.nan)
    half = stats.t.ppf((1 + level) / 2, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return float(d.mean()), float(d.mean() - half), float(d.mean() + half)


def stable_vs_random(runs: pd.DataFrame, direction: str, metric: str = "auroc") -> dict:
    """Per seed: stable minus the mean of the random subsets of the same size; the number of seeds in which stable is better and the t interval over the seeds. `stable beats random`
    is declared true only if it is better in a majority of seeds and the interval excludes 0."""
    g = runs[runs["direction"] == direction]
    stable = g[g["method"] == "stable"].set_index("seed")[metric]
    random_mean = g[g["method"] == "random"].groupby("seed")[metric].mean()
    diff = (stable - random_mean).dropna()
    mean, lo, hi = paired_interval(diff)
    better = int((diff > 0).sum()) if metric == "auroc" else int((diff < 0).sum())
    return {"seeds": int(len(diff)), "better_in": better, "mean_difference": mean, "ci_low": lo, "ci_high": hi, "random_std_over_subsets": float(g[g["method"] == "random"][metric].std(ddof=1)),
            "stable_beats_random": bool(len(diff) and better > len(diff) / 2 and ((lo > 0) if metric == "auroc" else (hi < 0)))}


def success_k(curve: pd.DataFrame, reference_balanced: float) -> dict:
    """Smallest k at which the mean over the runs reaches each declared success criterion: `fpr_detection` (FPR at the held-out-half threshold <= 0.15 with detection >= 0.90) and
    `balanced_accuracy` (within 0.05 of the leak-free reference); None where a criterion is never reached."""
    out = {"fpr_detection": None, "balanced_accuracy": None}
    for k, g in sorted(curve.groupby("k"), key=lambda kv: kv[0]):
        if out["fpr_detection"] is None and g["fpr_at_threshold"].mean() <= SUCCESS_FPR and g["detection_at_threshold"].mean() >= SUCCESS_DETECTION:
            out["fpr_detection"] = int(k)
        if out["balanced_accuracy"] is None and g["balanced_accuracy_unranked"].mean() >= reference_balanced - SUCCESS_BALANCED:
            out["balanced_accuracy"] = int(k)
    return out


def source_helps(runs: pd.DataFrame, metric: str = "fpr_at_threshold") -> dict:
    """Paired (seed, draw) difference source+target minus target-only at the same selection and k: mean, share of runs in which source+target has the lower FPR (or higher AUROC), t interval."""
    a = runs[runs["method"] == "source+target"].set_index(["seed", "draw"])[metric]
    b = runs[runs["method"] == "target_only"].set_index(["seed", "draw"])[metric]
    d = (a - b).dropna()
    mean, lo, hi = paired_interval(d)
    favours = float((d < 0).mean()) if metric != "auroc" else float((d > 0).mean())
    helps = len(d) > 1 and favours > 0.5 and ((hi < 0) if metric != "auroc" else (lo > 0))
    return {"pairs": int(len(d)), "mean_difference": mean, "ci_low": lo, "ci_high": hi, "share_favouring_source": favours, "source_helps": bool(helps)}


# ---------------------------------------------------------------- rendering
def render_step1(runs: pd.DataFrame, types: pd.DataFrame, block_mix: pd.DataFrame, eval_mix: pd.DataFrame) -> str:
    out = ["# Task 6 Step 1: leak-free zero-shot baseline (5 seeds, mean +/- std; target = the evaluation blocks, 200-row gaps)", ""]
    for direction in ("UNSW_to_CIC", "CIC_to_UNSW"):
        g = runs[runs["direction"] == direction]
        out += [f"## {direction.replace('_to_', ' -> ')}", "", *metric_table(g.assign(method=g["method"].replace({"random": "random (10 subsets x 5 seeds)"})), ["method"]), ""]
        for metric, name in (("auroc", "AUROC"), ("fpr_at_95_threshold_free", "FPR at exactly 95% detection")):
            r = stable_vs_random(runs, direction, metric)
            out.append(f"Stable against random subsets of the same size ({name}): better in {r['better_in']} of {r['seeds']} seeds, mean difference {r['mean_difference']:+.3f} (95% interval {r['ci_low']:+.3f}, {r['ci_high']:+.3f}); "
                       f"spread of the random subsets {r['random_std_over_subsets']:.3f}; **stable beats random: {'yes' if r['stable_beats_random'] else 'no'}**.")
        out.append("")
    out += ["## Recall per attack type at the argmax (mean over seeds; types with at least 100 evaluation rows)", ""]
    for direction in ("UNSW_to_CIC", "CIC_to_UNSW"):
        t = types[(types["direction"] == direction) & types["method"].isin(["common_all", "within_dataset_reference"])]
        if t.empty:
            continue
        piv = t.pivot_table(index="attack_type", columns="method", values="recall_argmax", aggfunc="mean").round(3)
        n = t.groupby("attack_type")["n"].mean().round(0)
        out += [f"### {direction.replace('_to_', ' -> ')}", "", "| attack type | evaluation rows | zero-shot (common_all) | leak-free reference |", "|---|---|---|---|",
                *[f"| {a} | {int(n[a])} | {piv.loc[a].get('common_all', np.nan):.3f} | {piv.loc[a].get('within_dataset_reference', np.nan):.3f} |" for a in piv.index], ""]
    out += ["## Block class mix (1,000-row blocks in file order)", "", "| dataset | blocks | pure normal | mixed | pure attack | most frequent dominant attack types (blocks) |", "|---|---|---|---|---|---|"]
    for name, g in block_mix.groupby("dataset"):
        dom = g[g["attack_share"] > 0]["dominant"].value_counts().head(5)
        out.append(f"| {name} | {len(g)} | {int((g['attack_share'] == 0).sum())} | {int(((g['attack_share'] > 0) & (g['attack_share'] < 1)).sum())} | {int((g['attack_share'] == 1).sum())} | "
                   + ", ".join(f"{k} ({v})" for k, v in dom.items()) + " |")
    mix = eval_mix.groupby(["dataset", "attack_type"])["evaluation_rows"].agg(["mean", "min"]).round(0)
    small = mix[mix["min"] < 100]
    out += ["", "Evaluation rows per attack type (mean over seeds, minimum over seeds): types with fewer than 100 rows in some seed are not reported per type: " + (", ".join(f"{d} {t} (min {int(r['min'])})" for (d, t), r in small.iterrows()) or "none") + ".", ""]
    return "\n".join(out) + "\n"


def render_step2(univariate: pd.DataFrame, agreement: pd.DataFrame, zero: pd.DataFrame) -> str:
    u = univariate.copy()
    out = ["# Task 6 Step 2: why zero-shot fails (diagnostic)", "", "AUROC of each common feature alone for attack against normal (all rows of each dataset; above 0.5 = attack flows have higher values). `absent` = |AUROC - 0.5| < 0.05 in at least one dataset.", "",
           "| feature | UNSW | CIC | same direction | absent in either dataset | flipped (clear and opposite) |", "|---|---|---|---|---|---|"]
    out += [f"| {r.feature} | {r.UNSW:.3f} | {r.CIC:.3f} | {'yes' if r.agree else 'no'} | {'yes' if r.absent_in_either else 'no'} | {'yes' if r.flipped else 'no'} |" for r in u.sort_values("feature").itertuples()]
    out += ["", f"Of {len(u)} features: {int(u['agree'].sum())} point the same way, {int((~u['agree']).sum())} do not, {int(u['absent_in_either'].sum())} are absent (near 0.5) in at least one dataset and {int(u['flipped'].sum())} are clearly flipped. "
            f"SHAP importance rank agreement between a UNSW-trained and a CIC-trained model on the common features: Spearman {ms(agreement['spearman_importance'], 2)} over {len(agreement)} seeds.", ""]
    z = zero[zero["method"] == "common_all"].groupby("direction")["auroc"].agg(["mean", "std"])
    out += ["Zero-shot AUROC of the common_all model: " + "; ".join(f"{d.replace('_to_', ' -> ')} {r['mean']:.3f} +/- {r['std']:.3f}" for d, r in z.iterrows()) + ".", ""]
    return "\n".join(out) + "\n"


def render_step3(align: pd.DataFrame, zero: pd.DataFrame) -> str:
    base = zero[zero["method"] == "common_all"].assign(method="baseline: common_all (ZERO-SHOT, Step 1)")
    runs = pd.concat([base, align], ignore_index=True)
    out = ["# Task 6 Step 3: label-free alignment (TRANSDUCTIVE) against the zero-shot baseline (5 seeds, mean +/- std)", ""]
    for direction in ("UNSW_to_CIC", "CIC_to_UNSW"):
        out += [f"## {direction.replace('_to_', ' -> ')}", "", *metric_table(runs[runs["direction"] == direction], ["method"]), ""]
    return "\n".join(out) + "\n"


def render_step4(curves: dict[str, pd.DataFrame]) -> str:
    out = ["# Task 6 Step 4: few-shot curve, both directions (25 runs per cell = 5 seeds x 5 draws; mean +/- std)", "",
           "k labelled target rows: half retrain the model (together with the source data for source+target), half choose the threshold; evaluation on target rows from other blocks. Success level: FPR at the held-out-half threshold <= 0.15 with detection >= 0.90, or balanced accuracy within 0.05 of the leak-free reference.", ""]
    for direction, runs in curves.items():
        ref = runs[runs["method"] == "within_dataset_reference"]
        ref_bal = float(ref["balanced_accuracy_unranked"].mean())
        zero = runs[runs["method"] == "zero_shot"]
        out += [f"## {direction.replace('_to_', ' -> ')}", "", f"Zero-shot baseline on the same evaluation rows (k = 0): FPR {ms(zero['fpr_at_threshold'])}, detection {ms(zero['detection_at_threshold'])}, AUROC {ms(zero['auroc'])}, balanced accuracy {ms(zero['balanced_accuracy_unranked'])}. "
                f"Leak-free reference (trained on all candidate blocks): FPR {ms(ref['fpr_at_threshold'])}, detection {ms(ref['detection_at_threshold'])}, AUROC {ms(ref['auroc'])}, balanced accuracy {ms(ref['balanced_accuracy_unranked'])}.", "",
                "| strategy | k | model | FPR at threshold | detection | balanced accuracy | AUROC | FPR at exactly 95% detection | degenerate runs |", "|---|---|---|---|---|---|---|---|---|"]
        few = runs[runs["method"].isin(["source+target", "target_only"])]
        for (strategy, k, method), g in few.groupby(["strategy", "k", "method"], sort=False):
            out.append(f"| {strategy} | {k} | {method} | {ms(g['fpr_at_threshold'])} | {ms(g['detection_at_threshold'])} | {ms(g['balanced_accuracy_unranked'])} | {ms(g['auroc'])} | {ms(g['fpr_at_95_threshold_free'])} | "
                       f"{int(g['degenerate'].fillna(False).sum())} of {len(g)} |")
        out += ["", "| strategy | model | smallest k: FPR <= 0.15 with detection >= 0.90 | smallest k: balanced accuracy within 0.05 of the reference | source data helps? (source+target minus target-only, FPR, by k) |", "|---|---|---|---|---|"]
        for strategy in sorted(few["strategy"].unique()):
            for method in ("source+target", "target_only"):
                k = success_k(few[(few["strategy"] == strategy) & (few["method"] == method)], ref_bal)
                fmt = lambda v: str(v) if v is not None else "not reached"   # noqa: E731
                helps = []
                for kk in sorted(few["k"].unique()):
                    r = source_helps(few[(few["strategy"] == strategy) & (few["k"] == kk)])
                    helps.append(f"k={kk}: {r['mean_difference']:+.3f} ({'yes' if r['source_helps'] else 'no'})")
                out.append(f"| {strategy} | {method} | {fmt(k['fpr_detection'])} | {fmt(k['balanced_accuracy'])} | " + ("; ".join(helps) if method == "source+target" else "") + " |")
        out.append("")
    return "\n".join(out) + "\n"


def main() -> None:
    d = get_metrics_dir(load_config())
    read = lambda name: pd.read_csv(d / f"cross_dataset_{name}.csv")   # noqa: E731
    zero = read("zero_shot_runs")
    (d / "cross_dataset_step1_zero_shot.md").write_text(render_step1(zero, read("zero_shot_types"), read("zero_shot_block_mix"), read("zero_shot_eval_mix")), encoding="utf-8")
    (d / "cross_dataset_step2_diagnostic.md").write_text(render_step2(read("diagnostic_univariate"), read("diagnostic_importance_agreement"), zero), encoding="utf-8")
    if (d / "cross_dataset_align_runs.csv").exists():
        (d / "cross_dataset_step3_align.md").write_text(render_step3(read("align_runs"), zero), encoding="utf-8")
    curves = {dr: pd.read_csv(d / f"cross_dataset_fewshot_{dr}_runs.csv") for dr in ("UNSW_to_CIC", "CIC_to_UNSW") if (d / f"cross_dataset_fewshot_{dr}_runs.csv").exists()}
    if curves:
        (d / "cross_dataset_step4_fewshot.md").write_text(render_step4(curves), encoding="utf-8")
    print("wrote", sorted(p.name for p in d.glob("cross_dataset_step*.md")))


if __name__ == "__main__":
    main()
