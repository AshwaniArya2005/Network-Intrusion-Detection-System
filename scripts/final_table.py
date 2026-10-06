"""The final table of the shift and few-shot study: every method with its access level on the official split (mean +/- std over 5 seeds / runs), next to
the 40- and 48-feature defaults.

    python scripts/final_table.py

Reads the default and tuned headline runs, the zero-shot comparison (methods_zero_shot_b1_*), the few-shot adaptation
(adaptation_*) and the transductive methods (methods_transductive_b3_*), and writes shift_and_fewshot_final_table_<sizes>.csv / .md under
results/metrics/<model.type>/. Columns: accuracy, macro F1, argmax FPR / detection, FPR / detection at the validation-chosen (or, for
thr_adapt, adaptation-sample) 95%-detection operating point, FPR at 95% detection (threshold-free), ECE, open-set detection and AUROC,
Normal -> Fuzzers share. Few-shot rows are scored on the official test rows that were NOT used for adaptation. Macro F1 is not
comparable between the hierarchical scheme (8 classes) and the flat scheme (6 classes).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config

COLUMNS = ["accuracy", "f1", "false_positive_rate", "detection_rate", "det95_test_fpr", "det95_test_detection", "fpr_at_95_detection",
           "ece", "unknown_detection_rate", "unknown_auroc", "normal_to_Fuzzers"]
POOLS = {"40f": "base", "48f": "full"}
FEWSHOT_KS = (100, 500, 1000, 5000)
SHOWN_KS = (1000, 5000)   # the markdown shows these k; the CSV holds every k


def cell(g: pd.DataFrame, metric: str) -> tuple[float, float]:
    r = g[g["metric"] == metric]
    return (float(r["mean"].iloc[0]), float(r["std"].iloc[0])) if len(r) else (float("nan"), float("nan"))


def rows_for(metrics_dir: Path, label: str, pool: str) -> list[dict]:
    out = []

    def add(method, access, k, g):
        row = {"pool": label, "method": method, "access": access, "k_labelled": k}
        for m in COLUMNS:
            row[f"{m}_mean"], row[f"{m}_std"] = cell(g, m)
        out.append(row)

    zero = pd.read_csv(metrics_dir / f"methods_zero_shot_b1_{label}_summary.csv")
    for method in ("flat_default", "hier_default", "hier_stage1_tuned"):
        add(method, "zero-shot", 0, zero[zero["method"] == method])
    for name, stem in (("flat_tuned_f1", "headline_tuned_f1_official_summary.csv"), ("flat_tuned_auc", "headline_tuned_auc_official_summary.csv")):
        s = pd.read_csv(metrics_dir / stem)
        s = s[(s["pool"] == pool) & (s["split"] == "official")]
        add(name, "zero-shot", 0, s)  # det95 columns are not part of the headline runs: left empty
    adaptation = metrics_dir / f"adaptation_{label}_summary.csv"
    if adaptation.exists():
        a = pd.read_csv(adaptation)
        for k in FEWSHOT_KS:
            for method in sorted(a["method"].unique()):
                if method == "zero_shot":
                    continue
                add(method, "few-shot", k, a[(a["k"] == k) & (a["method"] == method)])
    for extra in sorted(metrics_dir.glob(f"adaptation_{label}_*_summary.csv")):  # split-threshold and few-shot + transductive runs
        a = pd.read_csv(extra)
        for k in FEWSHOT_KS:
            for method in sorted(a["method"].unique()):
                g = a[(a["k"] == k) & (a["method"] == method)]
                if len(g):
                    add(method, g["access"].iloc[0], k, g)
    tx = metrics_dir / f"methods_transductive_b3_{label}_summary.csv"
    if tx.exists():
        t = pd.read_csv(tx)
        chosen = t[t["metric"] == "val_macro_f1"].set_index("method")["mean"].idxmax() if (t["metric"] == "val_macro_f1").any() else None
        for method in t["method"].unique():
            add(method + (" (declared choice: best validation macro F1)" if method == chosen else ""), "transductive", 0, t[t["method"] == method])
    return out


def render(df: pd.DataFrame, primary_only: bool = True) -> str:
    fmt = lambda m, s: "n/a" if pd.isna(m) else f"{m:.4f} +/- {s:.4f}"  # noqa: E731
    lines = ["# Shift and few-shot study final table (official split; mean +/- std over 5 seeds or runs)", "",
             "Access: zero-shot = training data only; transductive = also the unlabelled test features; few-shot = also k labelled test rows "
             "(excluded from evaluation). `det95` columns are the validation-chosen 95%-detection operating point (thr_adapt: chosen on the k rows). "
             "Macro F1 is not comparable between hierarchical (8 classes) and flat (6 classes) models.", ""]
    for pool, g in df.groupby("pool", sort=False):
        lines += [f"## {pool}", "", "| method | access | k | " + " | ".join(COLUMNS) + " |", "|---|---|---|" + "---|" * len(COLUMNS)]
        for r in g.itertuples():
            if r.access.startswith("few-shot") and r.k_labelled not in SHOWN_KS:
                continue
            if primary_only and r.access == "few-shot" and r.method in ("retrain_f0.1",):
                continue
            lines.append(f"| {r.method} | {r.access} | {r.k_labelled} | " + " | ".join(fmt(getattr(r, f"{m}_mean"), getattr(r, f"{m}_std")) for m in COLUMNS) + " |")
        lines.append("")
    lines.append("The markdown shows k = 1,000 and 5,000 and omits retrain_f0.1; the CSV holds every k and method (k = 100 / 500 too).")
    return "\n".join(lines) + "\n"


def main() -> None:
    metrics_dir = get_metrics_dir(load_config())
    frames = [pd.DataFrame(rows_for(metrics_dir, label, pool)) for label, pool in POOLS.items()]
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(metrics_dir / "shift_and_fewshot_final_table_40f_48f.csv", index=False)
    (metrics_dir / "shift_and_fewshot_final_table_40f_48f.md").write_text(render(df), encoding="utf-8")
    print(render(df))


if __name__ == "__main__":
    main()
