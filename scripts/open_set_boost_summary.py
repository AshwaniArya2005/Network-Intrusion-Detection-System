"""Tables for the open-set boost study from results/metrics/xgboost/open_set_boost_<idea>_<N>f_<kind>.csv (protocol: results/02_novelty1_open_set.md, section `Source: open_set_boost_protocol.md`).

    python scripts/open_set_boost_summary.py --idea calibration|perclass|ensemble|distance|oe|combo --pools 40f 48f

Writes open_set_boost_<idea>_<pools>.md (one table per kind with a plain-language caption). The verdict applies the rule declared before any result: a score CLEARLY BEATS
max-softmax when the rotation-mean detection (nine classes) is at least 0.05 higher, the rotation-mean AUROC is not lower, the rotation-mean detection is higher in at least
4 of 5 seeds, and the Worms + Shellcode detection is not more than 0.02 below max-softmax's.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config

ROTATION = ["Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic", "Reconnaissance", "Worms", "Shellcode"]
TRIO, WS, WS_SET = "Overlap-Group-1 (all three)", "Worms + Shellcode", "Shellcode+Worms"
MIN_GAIN, MIN_SEEDS, MAX_WS_LOSS = 0.05, 4, 0.02


def mean_std(values: pd.Series) -> str:
    v = values.dropna()
    return "n/a" if v.empty else f"{v.mean():.3f} +/- {v.std(ddof=1):.3f}" if len(v) > 1 else f"{v.mean():.3f}"


def rotation_by_seed(runs: pd.DataFrame, score: str, metric: str) -> pd.Series:
    """Per seed, the mean of `metric` over the nine rotation classes (the trio and Worms + Shellcode are not part of the mean)."""
    g = runs[(runs["score"] == score) & runs["held_out"].isin(ROTATION)]
    return g.groupby(["seed", "held_out"])[metric].mean().groupby("seed").mean()


def verdict(runs: pd.DataFrame, score: str, baseline: str = "msp") -> dict:
    """The declared rule for `score` against `baseline` (the rows of both must come from the same runs)."""
    det, base_det = rotation_by_seed(runs, score, "detection"), rotation_by_seed(runs, baseline, "detection")
    auc, base_auc = rotation_by_seed(runs, score, "unknown_auroc"), rotation_by_seed(runs, baseline, "unknown_auroc")
    ws = runs[(runs["held_out"] == WS) & (runs["zero_day"] == WS_SET)]
    ws_det, ws_base = ws[ws["score"] == score]["detection"].mean(), ws[ws["score"] == baseline]["detection"].mean()
    paired = (det - base_det).dropna()
    need = int(np.ceil(MIN_SEEDS / 5 * len(paired))) if len(paired) else 0
    return {"rotation_detection": float(det.mean()), "rotation_detection_gain": float(paired.mean()) if len(paired) else float("nan"),
            "rotation_auroc": float(auc.mean()), "rotation_auroc_gain": float((auc - base_auc).mean()), "seeds_better": int((paired > 0).sum()), "n_seeds": int(len(paired)),
            "ws_detection": float(ws_det), "ws_detection_gain": float(ws_det - ws_base),
            "clearly_beats": bool(len(paired) and paired.mean() >= MIN_GAIN and (auc - base_auc).mean() >= 0 and (paired > 0).sum() >= need and ws_det - ws_base >= -MAX_WS_LOSS)}


def summary_table(runs: pd.DataFrame, scores: list[str], baseline: str = "msp") -> list[str]:
    lines = ["| score | rotation mean AUROC | rotation mean detection | detection gain vs " + baseline + " | better in | worst class (AUROC) | Worms + Shellcode AUROC | Worms + Shellcode detection | "
             "detection at msp's realised test false-Unknown (diagnostic) | clearly beats |", "|" + "---|" * 10]
    for score in scores:
        if not (runs["score"] == score).any():
            continue
        v = verdict(runs, score, baseline) if (runs["score"] == baseline).any() else {}
        rot = runs[(runs["score"] == score) & runs["held_out"].isin(ROTATION)].groupby("held_out")[["unknown_auroc", "detection"]].mean()
        worst = rot["unknown_auroc"].idxmin() if len(rot) else "n/a"
        ws = runs[(runs["score"] == score) & (runs["held_out"] == WS) & (runs["zero_day"] == WS_SET)]
        lines.append(f"| {score} | {v.get('rotation_auroc', float('nan')):.3f} | {v.get('rotation_detection', float('nan')):.3f} | {v.get('rotation_detection_gain', float('nan')):+.3f} | "
                     f"{v.get('seeds_better', 0)} of {v.get('n_seeds', 0)} | {worst} ({rot['unknown_auroc'].min() if len(rot) else float('nan'):.3f}) | {mean_std(ws['unknown_auroc'])} | "
                     f"{mean_std(ws['detection'])} | {mean_std(ws['detection_matched_to_msp']) if 'detection_matched_to_msp' in ws else 'n/a'} | {'yes' if v.get('clearly_beats') else 'no'} |")
    return lines


def per_class_table(runs: pd.DataFrame, scores: list[str]) -> list[str]:
    lines = ["| held-out set | score | AUROC | detection @5% | false-Unknown (threshold half / calibration half / test) | flagged or called attack | detection at msp's test false-Unknown (diagnostic) |", "|" + "---|" * 7]
    order = [WS, *ROTATION, TRIO]
    for held in order:
        for score in scores:
            g = runs[(runs["held_out"] == held) & (runs["score"] == score) & (runs["zero_day"] == (WS_SET if held == WS else held))]
            if g.empty:
                continue
            lines.append(f"| {held} | {score} | {mean_std(g['unknown_auroc'])} | {mean_std(g['detection'])} | {g['false_unknown_thr_half'].mean():.3f} / {g['false_unknown_cal_half'].mean():.3f} / "
                         f"{g['false_unknown_test'].mean():.3f} | {mean_std(g['flagged_or_attack'])} | {mean_std(g['detection_matched_to_msp']) if 'detection_matched_to_msp' in g else 'n/a'} |")
    return lines


def composition_table(composition: pd.DataFrame, scores: list[str]) -> list[str]:
    """Mean flagged counts per bucket on the official test (Worms + Shellcode held out, 5% threshold) and the precision of Unknown."""
    buckets = [b for b in ["Shellcode", "Worms", "Exploits", "Fuzzers", "Generic", "Reconnaissance", "DoS", "Analysis", "Backdoor", "Normal"] if b in set(composition["bucket"])]
    lines = ["| score | " + " | ".join(buckets) + " | precision of Unknown (zero-day share of flagged flows) |", "|" + "---|" * (len(buckets) + 2)]
    for score in scores:
        g = composition[composition["score"] == score]
        if g.empty:
            continue
        counts = g.groupby("bucket")["n_flagged"].mean()
        totals = g.groupby("bucket")["n_total"].mean()
        lines.append(f"| {score} | " + " | ".join(f"{counts.get(b, 0):.0f} of {totals.get(b, 0):.0f}" for b in buckets) + f" | {g['unknown_precision'].mean():.3f} |")
    return lines


def queue_table(curve: pd.DataFrame, scores: list[str], target: float = 0.05) -> list[str]:
    lines = ["| score | alert FPR off | alert FPR on | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown |", "|" + "---|" * 8]
    for score in scores:
        g = curve[(curve["score"] == score) & np.isclose(curve["target"], target)]
        if g.empty:
            continue
        cols = ["alert_fpr_off", "alert_fpr_on", "confident_alert_fpr", "review_rate_normal", "share_of_false_alerts_that_skip_review", "zero_day_catch", "zero_day_flagged"]
        lines.append(f"| {score} | " + " | ".join(mean_std(g[c]) for c in cols) + " |")
    return lines


def render(idea: str, label: str, tables: dict[str, pd.DataFrame]) -> str:
    runs = tables["runs"]
    names = [n for n in runs["score"].unique()]
    baseline = "noP_msp" if "noP_msp" in names else "msp"
    out = [f"## {idea} ({label}, mean over seeds 42-46)", "", f"Baseline for the verdict: `{baseline}`. Thresholds at 5% false-Unknown on the known threshold half of block-grouped validation; ZERO-SHOT.", "",
           "### Summary and verdict against the declared rule", "", *summary_table(runs, names, baseline), "", "### Per held-out set", "", *per_class_table(runs, names), ""]
    if len(tables.get("composition", [])):
        out += ["### Composition of the flagged-Unknown bucket on the official test (Worms + Shellcode held out)", "", *composition_table(tables["composition"], names), ""]
    if len(tables.get("curve", [])):
        out += ["### Alert FPR and the review queue at the 5% target (the open-set study Step 3 measures; Worms + Shellcode held out)", "", *queue_table(tables["curve"], names), ""]
    diag = tables.get("diagnostics")
    if diag is not None and len(diag):
        numeric = diag.select_dtypes("number").drop(columns=["seed"], errors="ignore")
        out += ["### Diagnostics (mean over seeds, per held-out set)", "", "| held-out set | " + " | ".join(numeric.columns) + " |", "|" + "---|" * (len(numeric.columns) + 1)]
        for held, g in diag.groupby("held_out", sort=False):
            out.append(f"| {held} | " + " | ".join(f"{g[c].mean():.3f}" for c in numeric.columns) + " |")
        out.append("")
    return "\n".join(out) + "\n"


def render_iforest(label: str, checks: pd.DataFrame) -> str:
    """Sign check of the anomaly scores: AUROC of the score for known attacks against known Normal flows on the official test (above 0.5 = attacks rank as more anomalous than Normal), and the
    mean percentile of each zero-day class among the known test scores (above 0.5 = more anomalous than a typical known flow), with Worms + Shellcode held out; the nine rotation runs are summarised
    in one line."""
    ws = checks[checks["held_out"] == WS]
    out = [f"## isolation-forest sign check ({label}, mean over seeds 42-46)", "", "Worms + Shellcode held out.", "",
           "| score | known attacks vs Normal (AUROC) | Worms: mean percentile among known test flows | Shellcode: mean percentile |", "|---|---|---|---|"]
    for score, g in ws.groupby("score", sort=False):
        out.append(f"| {score} | {mean_std(g['attack_vs_normal_auroc'])} | {mean_std(g['percentile_Worms'])} | {mean_std(g['percentile_Shellcode'])} |")
    rotation = checks[checks["held_out"].isin(ROTATION)]
    out += ["", "Known attacks vs Normal, averaged over the nine rotation runs: " + "; ".join(f"{score} AUROC {g['attack_vs_normal_auroc'].mean():.3f}" for score, g in rotation.groupby("score", sort=False)) + ".", ""]
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--idea", required=True)
    parser.add_argument("--pools", nargs="+", required=True)
    args = parser.parse_args()
    d = get_metrics_dir(load_config())
    text = f"# Open-set boost study: {args.idea}\n\n"
    if args.idea == "iforest":
        for pool in args.pools:
            text += render_iforest(pool, pd.read_csv(d / f"open_set_boost_iforest_{pool}_checks.csv"))
        out = d / f"open_set_boost_iforest_{'_'.join(args.pools)}.md"
        out.write_text(text, encoding="utf-8")
        print(text)
        return
    for pool in args.pools:
        tables = {kind: pd.read_csv(d / f"open_set_boost_{args.idea}_{pool}_{kind}.csv") for kind in ("runs", "curve", "composition", "diagnostics")
                  if (d / f"open_set_boost_{args.idea}_{pool}_{kind}.csv").exists()}
        text += render(args.idea, pool, tables)
    out = d / f"open_set_boost_{args.idea}_{'_'.join(args.pools)}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
