"""Tables for Task 5.5 from results/metrics/xgboost/narrative_*.csv (protocol: results/task_5_5_protocol.md).

    python scripts/narrative_summary.py --pools 40f 48f [--source test]

Writes narrative_<source>_<pools>.md (Step 1: classic against class-relative on the held-out sample, per predicted class, calibration) and narrative_falsepos_<pools>.md (Step 2).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config

METRICS = [("n", "narratives"), ("typical_share_of_cited_numeric", "cited numeric features read \"typical\""), ("cited_features_per_narrative", "features cited per narrative"),
           ("cited_numeric_per_narrative", "numeric features cited per narrative"), ("share_narratives_without_numeric_feature", "narratives citing no numeric feature"),
           ("a_cited_in_top_k", "(a) cited features are positive top-5 SHAP features"), ("b_cue_exact_cite", "(b) cue exact vs training z-score"), ("c_categorical_cite", "(c) categorical named"),
           ("d_action", "(d) action matches the label"), ("e_label", "(e) no false statement about the label"), ("f_consistent_of_determined", "(f) cue direction agrees with the SHAP trend"),
           ("g_clauses_correct", "(g) clauses equal an independent computation"), ("calibrated_number_correct", "calibrated number = temperature-scaled probability")]
STYLES = ("classic", "class_relative")


def ms(values, digits: int = 3) -> str:
    v = pd.Series(values).dropna()
    return "n/a" if v.empty else (f"{v.mean():.{digits}f} +/- {v.std(ddof=1):.{digits}f}" if len(v) > 1 else f"{v.mean():.{digits}f}")


def side_by_side(summary: pd.DataFrame, pool: str, stratum: str = "all") -> list[str]:
    """One row per metric, classic and class-relative columns (mean +/- std over seeds)."""
    g = summary[(summary["pool_label"] == pool) & (summary["stratum"] == stratum)]
    lines = ["| metric | classic | class-relative |", "|---|---|---|"]
    for col, name in METRICS:
        cells = [ms(g[g["style"] == s][col], 0 if col == "n" else 3) for s in STYLES]
        lines.append(f"| {name} | {cells[0]} | {cells[1]} |")
    return lines


def per_class(summary: pd.DataFrame, pool: str) -> list[str]:
    lines = ["| predicted class (stratum) | flows per seed | \"typical\" share: classic -> class-relative | features cited: classic -> class-relative | (f): classic -> class-relative |", "|---|---|---|---|---|"]
    g = summary[(summary["pool_label"] == pool) & (summary["stratum"] != "all")]
    for stratum in sorted(g["stratum"].unique()):
        c, r = (g[(g["stratum"] == stratum) & (g["style"] == s)] for s in STYLES)
        lines.append(f"| {stratum} | {c['n'].mean():.0f} | {ms(c['typical_share_of_cited_numeric'])} -> {ms(r['typical_share_of_cited_numeric'])} | "
                     f"{ms(c['cited_features_per_narrative'])} -> {ms(r['cited_features_per_narrative'])} | {ms(c['f_consistent_of_determined'])} -> {ms(r['f_consistent_of_determined'])} |")
    return lines


def render_narrative(summary: pd.DataFrame, calibration: pd.DataFrame, failures: pd.DataFrame, source: str) -> str:
    out = [f"# Task 5.5 Step 1: classic against class-relative narratives ({source} flows, 5 seeds, mean +/- std)", ""]
    for pool in sorted(summary["pool_label"].unique()):
        out += [f"## {pool}", "", *side_by_side(summary, pool), "", f"### {pool} per predicted class", "", *per_class(summary, pool), ""]
    out += ["## Calibration (temperature fitted on block-grouped validation; ECE of the known official-test flows, 15 bins)", "", "| pool | temperature | ECE raw | ECE calibrated |", "|---|---|---|---|"]
    for pool, g in calibration.groupby("pool_label"):
        out.append(f"| {pool} | {ms(g['temperature'], 2)} | {ms(g['ece_raw'])} | {ms(g['ece_calibrated'])} |")
    out += ["", "## Failures", ""]
    if failures is None or not len(failures):
        out.append("No narrative failed any check.")
    else:
        counts = failures.groupby(["style", "check"]).size().unstack(fill_value=0)
        out += ["| style | " + " | ".join(counts.columns) + " |", "|---|" + "---|" * len(counts.columns), *[f"| {s} | " + " | ".join(str(counts.loc[s, c]) for c in counts.columns) + " |" for s in counts.index], ""]
        non_f = failures[failures["check"] != "f_direction"]
        out.append(f"Failures other than the cue-direction check (f): {len(non_f)}.")
    return "\n".join(out) + "\n"


def faithful_reading(g: pd.DataFrame) -> bool:
    return bool(len(g) and ((g["difference"] >= 0.05) & (g["ci_low"] > 0)).all())


def render_falsepos(tables: dict[str, pd.DataFrame]) -> str:
    out = ["# Task 5.5 Step 2: explanations of false-positive flows (official test, 5 seeds, 300 flows per group and model, mean +/- std)", "",
           "FP-attack = true Normal predicted as an attack; FP-Fuzzers = true Normal predicted as Fuzzers; TN = true Normal predicted Normal; TP-Fuzzers = true Fuzzers predicted Fuzzers.", ""]
    faith, groups, feats, sep = tables["faithfulness"], tables["groups"], tables["features"], tables["separation"]
    for pool in sorted(faith["pool_label"].unique()):
        out += [f"## {pool}", "", "### (a) Deletion faithfulness: probability drop at k = 5, top SHAP minus random removal (median baseline; random-row baseline in brackets)", "",
                "| group | flows in test | top SHAP drop | random drop | difference (std over seeds) | seeds with interval above 0 and difference >= 0.05 | top: class flips |", "|---|---|---|---|---|---|---|"]
        for group in ["TN", "FP-attack", "FP-Fuzzers", "TP-Fuzzers"]:
            m = faith[(faith["pool_label"] == pool) & (faith["group"] == group) & (faith["baseline"] == "median")]
            r = faith[(faith["pool_label"] == pool) & (faith["group"] == group) & (faith["baseline"] == "random_row")]
            if m.empty:
                continue
            ok = int(((m["difference"] >= 0.05) & (m["ci_low"] > 0)).sum())
            out.append(f"| {group} | {m['n_in_test'].mean():.0f} | {ms(m['top_drop_k5'])} | {ms(m['random_drop_k5'])} | {ms(m['difference'])} ({ms(r['difference'])}) | {ok} of {len(m)} | {ms(m['top_flip_k5'])} |")
        g = groups[groups["pool_label"] == pool]
        out += ["", "### (c) Confidence on these flows", "", "| group | raw confidence | calibrated confidence | raw >= 0.90 | calibrated >= 0.90 | flagged Unknown | features cited (class-relative) | class-atypicality of cited features |",
                "|---|---|---|---|---|---|---|---|"]
        for group in ["TN", "FP-attack", "FP-Fuzzers", "TP-Fuzzers"]:
            x = g[g["group"] == group]
            if len(x):
                out.append(f"| {group} | {ms(x['raw_confidence_mean'])} | {ms(x['calibrated_confidence_mean'])} | {ms(x['raw_share_ge_0.90'])} | {ms(x['calibrated_share_ge_0.90'])} | "
                           f"{ms(x['share_flagged_unknown'])} | {ms(x['mean_cited_features_class_relative'], 2)} | {ms(x['atypicality_mean'])} |")
        s = sep[sep["pool_label"] == pool]
        out += ["", "### (c) Does anything separate a false positive from a correct flow? (AUROC; 0.5 = nothing; positive = the false-positive group)", "", "| false positives | compared with | score | AUROC |", "|---|---|---|---|"]
        for (pos, neg, score), x in s.groupby(["false_positive_group", "compared_with", "score"], sort=False):
            out.append(f"| {pos} | {neg} | {score} | {ms(x['auroc'])} |")
        f = feats[(feats["pool_label"] == pool) & (feats["style"] == "classic")]
        out += ["", "### (b) Features the classic narrative cites most often (share of narratives, mean over seeds)", "", "| group | top cited features |", "|---|---|"]
        for group in ["TN", "FP-attack", "FP-Fuzzers", "TP-Fuzzers"]:
            x = f[f["group"] == group].groupby("feature")["share"].mean().sort_values(ascending=False).head(5)
            if len(x):
                out.append(f"| {group} | " + ", ".join(f"{k} ({v:.0%})" for k, v in x.items()) + " |")
        out.append("")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="+", required=True)
    parser.add_argument("--source", default="test")
    args = parser.parse_args()
    d = get_metrics_dir(load_config())
    tag = "_".join(args.pools)
    def cat(name: str, kind: str) -> pd.DataFrame:
        paths = [d / f"narrative_{name}_{p}_{kind}.csv" for p in args.pools]
        return pd.concat([pd.read_csv(p) for p in paths if p.exists()], ignore_index=True) if any(p.exists() for p in paths) else pd.DataFrame()
    if len(cat(args.source, "summary")):
        text = render_narrative(cat(args.source, "summary"), cat(args.source, "calibration"), cat(args.source, "failures"), args.source)
        (d / f"narrative_{args.source}_{tag}.md").write_text(text, encoding="utf-8")
        print(text)
    if len(cat("falsepos", "faithfulness")):
        text = render_falsepos({k: cat("falsepos", k) for k in ("faithfulness", "groups", "features", "separation")})
        (d / f"narrative_falsepos_{tag}.md").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
