"""Tables for Task 5 from results/metrics/xgboost/xai_*.csv (protocol: results/03_novelty2_explanations.md, section `Source: explanations_protocol.md`).

    python scripts/xai_summary.py --pools 40f 45f 48f

Writes xai_faithfulness_<pools>.md (Steps 1-2: additivity, primary metric, deletion / insertion curves, per class, shift) and xai_audit_<pools>.md (Steps 1 and 3: quoted confidence and the
narrative checks a-f, failures). Declared readings: faithful = the top-minus-random probability drop at k = 5 is at least 0.05 with a bootstrap interval excluding 0 in all 5 seeds; faithfulness is
lost under the shift = a test-minus-validation difference below -0.05 whose two-sample bootstrap interval excludes 0.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config
from src.xai.faithfulness import bootstrap_difference_interval

MIN_EFFECT, SHIFT_EFFECT = 0.05, -0.05


def ms(values: pd.Series, digits: int = 3) -> str:
    v = pd.Series(values).dropna()
    return "n/a" if v.empty else (f"{v.mean():.{digits}f} +/- {v.std(ddof=1):.{digits}f}" if len(v) > 1 else f"{v.mean():.{digits}f}")


def primary_rows(runs: pd.DataFrame, source: str = "test", stratum: str = "all") -> pd.DataFrame:
    """One row per (configuration, seed): the primary metric (top-SHAP minus random-removal probability drop at k = 5, median baseline) with its bootstrap interval."""
    g = runs[(runs["method"] == "top_minus_random") & (runs["baseline"] == "median") & (runs["k"] == 5) & (runs["stratum"] == stratum) & (runs["source"] == source)]
    return g[["pool_label", "tier", "n_features", "seed", "n", "mean_drop", "ci_low", "ci_high"]].reset_index(drop=True)


def is_faithful(rows: pd.DataFrame) -> bool:
    """The declared reading for one configuration's seeds: every seed has a difference of at least MIN_EFFECT with an interval above 0."""
    return bool(len(rows) and ((rows["mean_drop"] >= MIN_EFFECT) & (rows["ci_low"] > 0)).all())


def shift_row(test_diffs: np.ndarray, val_diffs: np.ndarray, seed: int = 0) -> dict:
    """Test-minus-validation difference of the per-flow primary metric with a two-sample bootstrap interval, and the declared reading."""
    mean, lo, hi = bootstrap_difference_interval(test_diffs, val_diffs, 1000, seed)
    return {"test_mean": float(np.mean(test_diffs)), "validation_mean": float(np.mean(val_diffs)), "difference": mean, "ci_low": lo, "ci_high": hi, "lost_under_shift": bool(mean < SHIFT_EFFECT and hi < 0)}


def render_faithfulness(labels: list[str], runs: pd.DataFrame, additivity: pd.DataFrame, flowdiffs: pd.DataFrame) -> str:
    out = ["# Task 5 Steps 1-2: SHAP additivity and faithfulness (XGBoost, official split, 5 seeds)", "",
           "Sample: 300 flows per predicted class + 200 flagged-Unknown flows per model and source (official test = known + zero-day flows; validation = block-grouped validation flows).", ""]
    out += ["## Step 1: SHAP additivity (sum of SHAP values + expected value against the raw margin of the predicted class)", "",
            "| pool | tier | flows checked | maximum error | flows over 1e-3 |", "|---|---|---|---|---|"]
    for (label, tier), g in additivity.groupby(["pool_label", "tier"], sort=False):
        out.append(f"| {label} | {tier} | {int(g['n'].sum())} | {g['max_abs_error'].max():.2e} | {int(g['n_over_tolerance'].sum())} |")
    out += ["", "## Primary metric: probability drop at k = 5, top-SHAP removal minus random removal (median baseline), official-test flows", "",
            "| pool | tier | features | difference (mean +/- std over seeds) | seeds with interval above 0 and difference >= 0.05 | faithful (declared reading) |", "|---|---|---|---|---|---|"]
    prim = primary_rows(runs)
    for (label, tier, nf), g in prim.groupby(["pool_label", "tier", "n_features"], sort=False):
        ok = int(((g["mean_drop"] >= MIN_EFFECT) & (g["ci_low"] > 0)).sum())
        out.append(f"| {label} | {tier} | {nf} | {ms(g['mean_drop'])} | {ok} of {len(g)} | {'yes' if is_faithful(g) else 'no'} |")
    whole = runs[runs["tier"].astype(str) == runs["n_features"].astype(str)]
    for baseline in ("median", "random_row"):
        out += ["", f"## Deletion curve, whole pools, official-test flows, baseline = {'training median' if baseline == 'median' else 'a random training row'} (probability drop; flip rate)", "",
                "| pool | k | top SHAP | random | least important | top: class flips | random: class flips | least: class flips |", "|---|---|---|---|---|---|---|---|"]
        g = whole[(whole["source"] == "test") & (whole["stratum"] == "all") & (whole["baseline"] == baseline) & whole["method"].isin(["top", "random", "least"])]
        for (label, k), gk in g.groupby(["pool_label", "k"], sort=False):
            cells = {m: gk[gk["method"] == m] for m in ("top", "random", "least")}
            out.append(f"| {label} | {k} | " + " | ".join(ms(cells[m]["mean_drop"]) for m in ("top", "random", "least")) + " | " + " | ".join(ms(cells[m]["flip_rate"]) for m in ("top", "random", "least")) + " |")
    out += ["", "## Insertion and sufficiency at k = 5, whole pools, official-test flows, median baseline", "",
            "Comprehensiveness = the deletion drop; sufficiency = the original probability minus the probability with ONLY the chosen features on the baseline vector (lower = the chosen features alone nearly reproduce the prediction).", "",
            "| pool | comprehensiveness: top / random | sufficiency: top / random |", "|---|---|---|"]
    g = whole[(whole["source"] == "test") & (whole["stratum"] == "all") & (whole["baseline"] == "median") & (whole["k"] == 5)]
    for label, gl in g.groupby("pool_label", sort=False):
        top, rnd = gl[gl["method"] == "top"], gl[gl["method"] == "random"]
        out.append(f"| {label} | {ms(top['mean_drop'])} / {ms(rnd['mean_drop'])} | {ms(top['mean_p0'] - top['mean_insertion'])} / {ms(rnd['mean_p0'] - rnd['mean_insertion'])} |")
    out += ["", "## Primary metric per predicted class (whole pools, official-test flows; mean +/- std over seeds)", "", "| pool | stratum | flows per seed | difference | interval above 0 in |", "|---|---|---|---|---|"]
    for label in labels:
        for stratum in sorted(set(runs[runs["pool_label"] == label]["stratum"]) - {"all"}):
            g = primary_rows(runs[(runs["pool_label"] == label) & (runs["tier"].astype(str) == runs["n_features"].astype(str))], "test", stratum)
            if len(g):
                out.append(f"| {label} | {stratum} | {g['n'].mean():.0f} | {ms(g['mean_drop'])} | {int((g['ci_low'] > 0).sum())} of {len(g)} |")
    out += ["", "## Shift check: the primary metric on official-test flows against block-grouped validation flows (flows pooled over the 5 seeds; two-sample bootstrap)", "",
            "| pool | tier | official test | validation | test minus validation (95% interval) | faithfulness lost under the shift (declared reading) |", "|---|---|---|---|---|---|"]
    fd = flowdiffs[flowdiffs["stratum"] != "xx"]
    for (label, tier), g in fd.groupby(["pool_label", "tier"], sort=False):
        t, v = g[g["source"] == "test"]["diff_top_minus_random_k5"].to_numpy(), g[g["source"] == "validation"]["diff_top_minus_random_k5"].to_numpy()
        r = shift_row(t, v)
        out.append(f"| {label} | {tier} | {r['test_mean']:.3f} | {r['validation_mean']:.3f} | {r['difference']:+.3f} ({r['ci_low']:+.3f}, {r['ci_high']:+.3f}) | {'yes' if r['lost_under_shift'] else 'no'} |")
    return "\n".join(out) + "\n"


def render_audit(summary: pd.DataFrame, failures: pd.DataFrame, narratives: pd.DataFrame) -> str:
    checks = [("confidence_text", "quoted confidence = model probability"), ("confidence_json", "JSON confidence = model probability"), ("a_cited_in_top_k", "(a) cited features are positive top-5 SHAP features"),
              ("b_cue_exact_cite", "(b) cue exact vs training z-score (per cited feature)"), ("b_cue_direction_cite", "(b) cue direction (per cited feature)"),
              ("c_categorical_cite", "(c) categorical named by category (per cited feature)"), ("d_action", "(d) action matches the label"), ("e_label", "(e) no false statement about the label"),
              ("f_consistent_of_determined", "(f) cue direction agrees with the SHAP-vs-value relation (determined cases)")]
    out = ["# Task 5 Steps 1 and 3: narrative audit through the dashboard path (XGBoost, official split, 5 seeds x 200 flows per pool)", "",
           "| check | " + " | ".join(sorted(summary["pool_label"].unique())) + " |", "|---|" + "---|" * summary["pool_label"].nunique()]
    allrows = summary[summary["stratum"] == "all"]
    for col, name in checks:
        out.append(f"| {name} | " + " | ".join(ms(allrows[allrows["pool_label"] == p][col]) for p in sorted(summary["pool_label"].unique())) + " |")
    for p in sorted(summary["pool_label"].unique()):
        g = narratives[narratives["pool_label"] == p]
        no_dir = (g["f_no_direction_claimed"] == g["n_cited_numeric"]) & (g["n_cited_numeric"] > 0)
        cites = g["n_cited_numeric"].sum()
        out += ["", f"{p}: of the cited numeric features {g['f_no_direction_claimed'].sum() / max(cites, 1):.1%} carry the cue \"typical\" (no direction claimed), {g['f_no_monotone_relation'].sum() / max(cites, 1):.1%} have no monotone SHAP-vs-value relation, "
                f"and in {no_dir.mean():.1%} of the narratives no cited numeric feature carries a direction at all; {g['diffuse'].mean():.1%} of narratives say the decision was diffuse."]
    out += ["", "## Per predicted class (mean over seeds; all deterministic checks a-e must be 1.000)", "", "| pool | stratum | narratives | (a) | (b) exact | (d) | (e) | (f) consistent |", "|---|---|---|---|---|---|---|---|"]
    for (label, stratum), g in summary[summary["stratum"] != "all"].groupby(["pool_label", "stratum"], sort=False):
        out.append(f"| {label} | {stratum} | {g['n'].sum()} | {g['a_cited_in_top_k'].mean():.3f} | {g['b_cue_exact_cite'].mean():.3f} | {g['d_action'].mean():.3f} | {g['e_label'].mean():.3f} | {g['f_consistent_of_determined'].mean():.3f} |")
    out += ["", "## Failures", ""]
    if failures is None or not len(failures):
        out.append("No narrative failed any check.")
    else:
        counts = failures.groupby(["pool_label", "check"]).size().unstack(fill_value=0)
        out += ["| pool | " + " | ".join(counts.columns) + " |", "|---|" + "---|" * len(counts.columns), *[f"| {p} | " + " | ".join(str(counts.loc[p, c]) for c in counts.columns) + " |" for p in counts.index], ""]
        out += ["Most frequent reasons:", ""]
        top = failures.groupby(["check", "reason"]).size().sort_values(ascending=False).head(8)
        out += [f"- {c}: {r} ({n})" for (c, r), n in top.items()]
    return "\n".join(out) + "\n"


def render_audit_shift(test: pd.DataFrame, validation: pd.DataFrame) -> str:
    """The audit rates on official-test flows against block-grouped validation flows (the same models, 5 seeds), to see whether the narratives are less trustworthy under the shift."""
    cols = [("a_cited_in_top_k", "(a) cited features in the SHAP top 5"), ("b_cue_exact_cite", "(b) cue exact"), ("c_categorical_cite", "(c) categorical named"), ("d_action", "(d) action"),
            ("e_label", "(e) label statement"), ("f_consistent_of_determined", "(f) directional consistency"), ("f_share_typical_cue", "share of cited features read \"typical\""),
            ("f_share_no_monotone_relation", "share with no monotone SHAP-vs-value relation")]
    out = ["## Audit rates on official-test flows against validation flows (the shift check)", "", "| check | pool | official test | validation | test minus validation |", "|---|---|---|---|---|"]
    for col, name in cols:
        for pool in sorted(test["pool_label"].unique()):
            t = test[(test["stratum"] == "all") & (test["pool_label"] == pool)].sort_values("seed")[col].to_numpy()
            v = validation[(validation["stratum"] == "all") & (validation["pool_label"] == pool)].sort_values("seed")[col].to_numpy()
            if len(t) and len(v):
                out.append(f"| {name} | {pool} | {ms(pd.Series(t))} | {ms(pd.Series(v))} | {np.nanmean(t) - np.nanmean(v):+.3f} |")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="+", required=True)
    args = parser.parse_args()
    d = get_metrics_dir(load_config())
    tag = "_".join(args.pools)
    cat = lambda name, kind: pd.concat([pd.read_csv(d / name.format(p=p, kind=kind)) for p in args.pools], ignore_index=True)   # noqa: E731
    if all((d / f"xai_faithfulness_{p}_runs.csv").exists() for p in args.pools):
        text = render_faithfulness(args.pools, cat("xai_faithfulness_{p}_{kind}.csv", "runs"), pd.concat([pd.read_csv(d / f"xai_additivity_{p}.csv") for p in args.pools], ignore_index=True),
                                   cat("xai_faithfulness_{p}_{kind}.csv", "flowdiffs"))
        (d / f"xai_faithfulness_{tag}.md").write_text(text, encoding="utf-8")
        print(text)
    if all((d / f"xai_audit_{p}_summary.csv").exists() for p in args.pools):
        failures = pd.concat([pd.read_csv(d / f"xai_audit_{p}_failures.csv") for p in args.pools if (d / f"xai_audit_{p}_failures.csv").exists()], ignore_index=True)
        text = render_audit(cat("xai_audit_{p}_{kind}.csv", "summary"), failures, cat("xai_audit_{p}_{kind}.csv", "narratives"))
        if all((d / f"xai_audit_validation_{p}_summary.csv").exists() for p in args.pools):
            text += "\n" + render_audit_shift(cat("xai_audit_{p}_{kind}.csv", "summary"), cat("xai_audit_validation_{p}_{kind}.csv", "summary"))
        (d / f"xai_audit_{tag}.md").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
