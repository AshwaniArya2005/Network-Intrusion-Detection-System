"""Task 2.6 table: the original few-shot result next to the leakage checks (mean +/- std over 5 runs).

    python scripts/leakage_table.py

Columns: FPR at about 95% detection (threshold chosen on held-out labelled adaptation rows, `det95_test_fpr`), detection at that threshold,
accuracy, ECE. Rows per pool and k: the original result (`retrain_split_f0.5` of pipelines/run_adaptation.py, read only), the same model on
all evaluation rows of the leakage run (a reproduction), on the evaluation rows with NO near twin (<= 0.1) in the adaptation set, on the rows
with one, and the neighbourhood-disjoint block conditions; plus the 41-, 38- and 45-feature ablations. Zero-shot rows are on the same
evaluation rows. Writes task_2_6_table_<pools>.csv / .md under results/metrics/<model.type>/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config

METRICS = ["det95_test_fpr", "det95_test_detection", "accuracy", "ece"]
LEAK_CONDITIONS = [("all_eval", "twins: all evaluation rows (reproduction)"), ("no_near_twin_0.1", "twins: rows with NO near twin (<= 0.1) in the adaptation set"),
                   ("has_near_twin_0.1", "twins: rows WITH a near twin (<= 0.1)"), ("within_E", "blocks: adaptation rows from the evaluation blocks (within-file)"),
                   ("block_disjoint", "blocks: adaptation rows from other blocks (neighbourhood-disjoint)")]


def cell(summary: pd.DataFrame, **where) -> dict:
    g = summary
    for column, value in where.items():
        g = g[g[column] == value]
    out = {}
    for m in METRICS:
        r = g[g["metric"] == m]
        out[f"{m}_mean"], out[f"{m}_std"] = (float(r["mean"].iloc[0]), float(r["std"].iloc[0])) if len(r) else (float("nan"), float("nan"))
    return out


def build(metrics_dir: Path, main_pools: dict[str, str], ablation_pools: dict[str, str], ks=(1000, 5000)) -> pd.DataFrame:
    """`main_pools` / `ablation_pools`: pool-size label -> description. Missing files are skipped, never invented."""
    rows = []

    def add(label, desc, k, source, access, values):
        rows.append({"pool": label, "k_labelled": k, "row": source, "access": access, "pool_description": desc, **values})

    for label, desc in main_pools.items():
        original = metrics_dir / f"adaptation_{label}_split_summary.csv"       # the Task 2.5 result files, read only
        leak = metrics_dir / f"leakage_{label}_summary.csv"
        for k in ks:
            if original.exists():
                o = pd.read_csv(original)
                add(label, desc, k, "original Task 2.5 result (retrain_split_f0.5, random adaptation rows)", "few-shot",
                    cell(o[o["k"] == k], method="retrain_split_f0.5"))
            if leak.exists():
                s = pd.read_csv(leak)
                s = s[s["k"] == k]
                for cond, text in LEAK_CONDITIONS:
                    add(label, desc, k, text, "few-shot", cell(s, condition=cond, method="retrain_split_f0.5"))
                    zero_cond = {"within_E": "zero_shot_E", "block_disjoint": "zero_shot_E"}.get(cond, cond)
                    if cond != "within_E":
                        add(label, desc, k, text.replace("adaptation rows from other blocks (neighbourhood-disjoint)", "same rows") + " - zero-shot", "zero-shot",
                            cell(s, condition=zero_cond, method="zero_shot"))
    for label, desc in ablation_pools.items():
        split = metrics_dir / f"adaptation_{label}_split_summary.csv"
        zero = metrics_dir / f"methods_leak_zero_{label}_summary.csv"
        for k in ks:
            if split.exists():
                o = pd.read_csv(split)
                add(label, desc, k, "ablation: retrain_split_f0.5, random adaptation rows", "few-shot", cell(o[o["k"] == k], method="retrain_split_f0.5"))
        if zero.exists():
            z = pd.read_csv(zero)
            z = z[z["method"] == "flat_default"].rename(columns={"metric": "metric"})
            v = {}
            for m, src in (("det95_test_fpr", "det95_test_fpr"), ("det95_test_detection", "det95_test_detection"), ("accuracy", "accuracy"), ("ece", "ece")):
                r = z[z["metric"] == src]
                v[f"{m}_mean"], v[f"{m}_std"] = (float(r["mean"].iloc[0]), float(r["std"].iloc[0])) if len(r) else (float("nan"), float("nan"))
            add(label, desc, 0, "ablation: zero-shot (validation-chosen det95)", "zero-shot", v)
    return pd.DataFrame(rows)


def render(df: pd.DataFrame) -> str:
    fmt = lambda m, s: "n/a" if pd.isna(m) else f"{m:.4f} +/- {s:.4f}"  # noqa: E731
    lines = ["# Task 2.6: is the few-shot result adaptation or neighbour leakage? (official split, mean +/- std over 5 runs)", "",
             "Few-shot = k labelled test rows (half retrain, half choose the 95%-detection threshold), evaluated on rows not used for adaptation. "
             "Zero-shot rows use the validation-chosen threshold.", "",
             "| pool | k | row | access | FPR at ~95% detection | detection | accuracy | ECE |", "|---|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        lines.append(f"| {r.pool} | {r.k_labelled} | {r.row} | {r.access} | " + " | ".join(
            fmt(getattr(r, f"{m}_mean"), getattr(r, f"{m}_std")) for m in METRICS) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    metrics_dir = get_metrics_dir(load_config())
    main_pools = {"40f": "40 features", "48f": "48 features"}
    ablation = {"45f": "48 minus sttl, dttl, ct_state_ttl", "41f": "48 minus the 7 window-count ct_* columns", "38f": "48 minus every ct_* column"}
    df = build(metrics_dir, main_pools, ablation)
    tag = "_".join([*main_pools, *ablation])
    df.to_csv(metrics_dir / f"task_2_6_table_{tag}.csv", index=False)
    (metrics_dir / f"task_2_6_table_{tag}.md").write_text(render(df), encoding="utf-8")
    print(render(df))


if __name__ == "__main__":
    main()
