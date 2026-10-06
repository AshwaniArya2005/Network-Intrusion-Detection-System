"""Fill the columns of results/TEMPLATE_model_results.csv from one model's own outputs, so it can be compared with results/REFERENCE_XGBOOST.csv:

    python scripts/fill_model_template.py [--model xgboost] [--pool 48]

Reads, from results/metrics/<model folder>/, the headline summary (run_headline_seeds.py), tier_summary_<model>_<N>f.csv and tier_study_<model>_<N>f_runs_pooled.csv
(run_tier_study.py, tier_summary.py) and stability_<model>_<N>f.csv (explanation_stability_tiers.py), and writes model_results_<model folder>.csv next to them
with the template's columns and the rows of the chosen pool. A value the model's outputs do not contain stays "not computed".
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.run_headline_seeds import output_stem
from src.utils.config_loader import get_metrics_dir, load_config, model_folder, resolve_path

NC = "not computed"
POOLS = {"48": ("full", "48f"), "40": ("base", "40f"), "45": ("full_no_ttl", "45f")}
HEADLINE = {"accuracy": "accuracy", "f1": "macro_f1", "detection_rate": "detection_rate", "false_positive_rate": "fpr_argmax", "fpr_at_95_detection": "fpr_at_95_detection",
            "roc_auc_attack_vs_normal": "roc_auc_attack_vs_normal", "ece": "ece"}
TIER = {"accuracy": "accuracy", "f1": "macro_f1", "detection_rate": "detection_rate", "false_positive_rate": "fpr_argmax", "det95_test_fpr": "det95_fpr",
        "roc_auc_attack_vs_normal": "roc_auc_attack_vs_normal", "ece": "ece"}
STAB_PAIR = {"rank_correlation": "shap_rank_corr_vs_full_tier", "cosine_similarity": "shap_cosine_vs_full_tier", "topk_overlap": "shap_top10_jaccard_vs_full_tier"}
STAB_FLOOR = {"rank_correlation": "shap_noise_floor_rank_corr", "cosine_similarity": "shap_noise_floor_cosine", "topk_overlap": "shap_noise_floor_top10_jaccard"}


def read(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


def put(row: dict, name: str, mean, std) -> None:
    row[f"{name}_mean"] = f"{mean:.4f}"
    row[f"{name}_std"] = NC if pd.isna(std) else f"{std:.4f}"


def fill(config: dict, model: str, pool: str, template: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """(filled table, names of the files that were read)."""
    name, label = POOLS[pool]
    d = get_metrics_dir(config, model)
    folder = model_folder(config, model)
    used = []
    headline = read(d / f"{output_stem(None, ('official', 'pooled_random'), (name,))}_summary.csv")
    tiers = read(d / f"tier_summary_{model}_{label}.csv")
    pooled = read(d / f"tier_study_{model}_{label}_runs_pooled.csv")
    stability = read(d / f"stability_{model}_{label}.csv")
    rows = template[template["pool"] == label].astype(object).copy()
    out = []
    for r in rows.to_dict("records"):
        r["model"] = folder
        tier, split = str(r["tier"]), r["split"]
        if r["protocol"].startswith("headline"):
            if headline is None:
                out.append(r); continue
            g = headline[(headline["pool"] == name) & (headline["split"] == split)]
            for metric, col in HEADLINE.items():
                m = g[g["metric"] == metric]
                if len(m):
                    put(r, col, float(m["mean"].iloc[0]), float(m["std"].iloc[0])); r["n_seeds"] = int(m["n_seeds"].iloc[0])
        elif split == "official" and tiers is not None:
            g = tiers[tiers["tier"].astype(str) == tier]
            if len(g):
                g = g.iloc[0]; r["n_seeds"] = int(g["n_seeds"])
                for metric, col in TIER.items():
                    if f"{metric}_mean" in g and not pd.isna(g[f"{metric}_mean"]):
                        put(r, col, float(g[f"{metric}_mean"]), float(g[f"{metric}_std"]))
        elif split == "pooled_random" and pooled is not None:
            g = pooled[pooled["tier"].astype(str) == tier]["f1"]
            if len(g):
                put(r, "macro_f1", float(g.mean()), float(g.std(ddof=1)) if len(g) > 1 else float("nan")); r["n_seeds"] = len(g)
        if split == "official" and stability is not None and not r["protocol"].startswith("headline"):
            full = str(max(rows["tier"].astype(int)))
            pair = stability[(stability["comparison"] == "tier_pair") & (stability["a"].astype(str) == full) & (stability["b"].astype(str) == tier)]
            floor = stability[(stability["comparison"] == "same_tier_seeds") & (stability["a"].astype(str) == tier)]
            for table, mapping in ((pair, STAB_PAIR), (floor, STAB_FLOOR)):
                if len(table):
                    for metric, col in mapping.items():
                        put(r, col, float(table[f"{metric}_mean"].iloc[0]), float(table[f"{metric}_std"].iloc[0]))
            if tier == full:
                for col in STAB_PAIR.values():
                    r[f"{col}_mean"] = r[f"{col}_std"] = "not applicable"
        out.append(r)
    names = [n for n, t in (("headline summary", headline), ("tier_summary", tiers), ("pooled tier runs", pooled), ("stability", stability)) if t is not None]
    for r in out:
        for k, v in list(r.items()):
            if pd.isna(v) or v == "":
                r[k] = NC if k != "notes" else ""
        r["notes"] = "filled by scripts/fill_model_template.py from: " + ", ".join(names)
    return pd.DataFrame(out, columns=list(template.columns)), names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", help="model type (default: model.type of the config)")
    parser.add_argument("--pool", choices=list(POOLS), default="48")
    args = parser.parse_args()
    config = load_config()
    model = args.model or config["model"]["type"]
    template = pd.read_csv(resolve_path("results/TEMPLATE_model_results.csv"), dtype=str, keep_default_na=False)
    table, names = fill(config, model, args.pool, template)
    path = get_metrics_dir(config, model) / f"model_results_{model_folder(config, model)}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, index=False)
    filled = int((table.drop(columns=["model", "pool", "tier", "split", "protocol", "role", "n_seeds", "notes"]) != NC).to_numpy().sum())
    print(f"wrote {path} ({len(table)} rows, {filled} values filled from: {', '.join(names) or 'nothing found'})")


if __name__ == "__main__":
    main()
