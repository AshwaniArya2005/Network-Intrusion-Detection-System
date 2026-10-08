"""Feature-tier study, step 1 summary: the tier study as one table per pool (mean +/- std over the 5 seeds), the shrinking-claim test and the random-subset comparison.

    python scripts/tier_summary.py [--model xgboost] [--pools 40f 45f 48f]

Reads results/metrics/<model>/tier_study_<model>_<N>f_runs.csv (and, when present, *_pooled.csv, tier_baselines_summary_*.csv and the earlier
random-validation operating-point file for the full tier) and writes tier_summary_<model>_<N>f.csv and tier_summary_<model>.md.
Claim tested (declared in results/04_novelty3_feature_tiers.md, section `Source: feature_tiers_protocol.md`): shrinking the feature set costs no more than retraining noise. For every tier
`drop_f1` = full-pool mean macro F1 - tier mean, `meets_noise` = drop <= 2 x the full pool's seed-to-seed std, `meets_practical` = drop <= 0.02,
`welch_z_f1` = drop / sqrt(var_full / n + var_tier / n).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config

METRICS = ["accuracy", "f1", "detection_rate", "false_positive_rate", "det95_test_fpr", "det95_test_detection", "roc_auc_attack_vs_normal", "ece",
           "unknown_detection_rate", "unknown_auroc"]


def tier_table(runs: pd.DataFrame, full_tier: str | None = None, noise_multiple: float = 2.0, practical: float = 0.02) -> pd.DataFrame:
    """One row per tier of a (model, pool): mean / std over seeds of every metric, the surviving extra columns and the shrinking-claim test
    against the largest tier (`full_tier`, default the tier with the most features)."""
    g = runs.groupby("tier", sort=False)
    rows = []
    for tier, r in g:
        row = {"tier": tier, "n_features": int(r["n_features"].iloc[0]), "n_seeds": len(r)}
        for m in METRICS:
            if m in r:
                row[f"{m}_mean"], row[f"{m}_std"] = float(r[m].mean()), float(r[m].std(ddof=1)) if len(r) > 1 else float("nan")
        for c in ("n_ct_window", "n_ct_other", "n_ttl", "ct_window_cols", "ct_other_cols", "ttl_cols"):
            if c in r:
                row[c] = r[c].iloc[0]
        rows.append(row)
    table = pd.DataFrame(rows)
    full = table.loc[table["n_features"].idxmax()] if full_tier is None else table[table["tier"] == full_tier].iloc[0]
    n = float(full["n_seeds"])
    table["drop_f1"] = full["f1_mean"] - table["f1_mean"]
    se = np.sqrt(full["f1_std"] ** 2 / n + table["f1_std"] ** 2 / table["n_seeds"])
    table["welch_z_f1"] = np.where(se > 0, table["drop_f1"] / se, np.nan)
    table["meets_noise"] = table["drop_f1"] <= noise_multiple * full["f1_std"]
    table["meets_practical"] = table["drop_f1"] <= practical
    table["drop_accuracy"] = full["accuracy_mean"] - table["accuracy_mean"]
    return table.round(4)


def render(model: str, tables: dict[str, pd.DataFrame], baselines: dict[str, pd.DataFrame], pooled: dict[str, pd.DataFrame]) -> str:
    fmt = lambda m, s: "n/a" if pd.isna(m) else f"{m:.4f} +/- {s:.4f}"  # noqa: E731
    lines = [f"# Feature-tier study Step 1: tier study, {model} (official split, block-grouped validation, mean +/- std over 5 seeds)", "",
             "Ranked top-N tiers (mutual information on the training split). `det95 FPR` is the 95%-detection operating point chosen on the BLOCK-GROUPED "
             "validation split. The pooled random split is a best case: it shares neighbouring flows with its training rows and is optimistic. "
             "`noise` / `practical`: macro F1 drop from the full pool within 2 x seed std / within 0.02.", ""]
    for label, t in tables.items():
        lines += [f"## {label}", "", "| tier | features | macro F1 | accuracy | FPR | det95 FPR | det95 detection | ROC-AUC | ECE | open-set det. | open-set AUROC | pooled macro F1 (best case) | drop F1 | z | noise | practical | ct window / other / TTL cols |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        p = pooled.get(label)
        for r in t.itertuples(index=False):
            d = r._asdict()
            pooled_f1 = "n/a"
            if p is not None and (p["tier"] == d["tier"]).any():
                q = p[p["tier"] == d["tier"]].iloc[0]
                pooled_f1 = fmt(q["f1_mean"], q["f1_std"])
            lines.append(f"| {d['tier']} | {d['n_features']} | {fmt(d['f1_mean'], d['f1_std'])} | {fmt(d['accuracy_mean'], d['accuracy_std'])} | "
                         f"{fmt(d['false_positive_rate_mean'], d['false_positive_rate_std'])} | {fmt(d['det95_test_fpr_mean'], d['det95_test_fpr_std'])} | "
                         f"{fmt(d['det95_test_detection_mean'], d['det95_test_detection_std'])} | {fmt(d['roc_auc_attack_vs_normal_mean'], d['roc_auc_attack_vs_normal_std'])} | "
                         f"{fmt(d['ece_mean'], d['ece_std'])} | {fmt(d['unknown_detection_rate_mean'], d['unknown_detection_rate_std'])} | "
                         f"{fmt(d['unknown_auroc_mean'], d['unknown_auroc_std'])} | {pooled_f1} | {d['drop_f1']:+.4f} | {d['welch_z_f1']:.1f} | "
                         f"{'yes' if d['meets_noise'] else 'NO'} | {'yes' if d['meets_practical'] else 'NO'} | {d['n_ct_window']} / {d['n_ct_other']} / {d['n_ttl']} |")
        b = baselines.get(label)
        if b is not None and len(b):
            lines += ["", f"Ranked vs 10 random subsets vs worst-N ({label}, macro F1):", "", "| tier | ranked | random mean +/- std (min-max) | worst | ranked percentile | z |", "|---|---|---|---|---|---|"]
            for r in b.itertuples(index=False):
                lines.append(f"| {r.feature_set} | {r.ranked_f1:.4f} | {r.random_f1_mean:.4f} +/- {r.random_f1_std:.4f} ({r.random_f1_min:.4f}-{r.random_f1_max:.4f}) | "
                             f"{r.worst_f1:.4f} | {r.ranked_percentile_in_random:.0f} | {r.ranked_z_vs_random:.2f} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="xgboost")
    parser.add_argument("--pools", nargs="*", default=["48f"], help="pool sizes, default the primary pool 48f; add 40f 45f for the comparison pools")
    parser.add_argument("--in-dir", help="read and write under <in-dir>/<model>/ instead of results/metrics/<model>/")
    args = parser.parse_args()
    config = load_config()
    d = Path(args.in_dir) / args.model if args.in_dir else get_metrics_dir(config, args.model)
    tables, baselines, pooled = {}, {}, {}
    for label in args.pools:
        path = d / f"tier_study_{args.model}_{label}_runs.csv"
        if not path.exists():
            continue
        tables[label] = tier_table(pd.read_csv(path))
        tables[label].to_csv(d / f"tier_summary_{args.model}_{label}.csv", index=False)
        pooled_path = d / f"tier_study_{args.model}_{label}_runs_pooled.csv"
        if pooled_path.exists():
            pooled[label] = tier_table(pd.read_csv(pooled_path))
        base_path = d / f"tier_baselines_summary_{args.model}_{label}.csv"
        if base_path.exists():
            baselines[label] = pd.read_csv(base_path)
    text = render(args.model, tables, baselines, pooled)
    (d / f"tier_summary_{args.model}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
