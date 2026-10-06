"""Feature-tier study, step 4: do XGBoost, logistic regression and the random forest agree on which features matter?

    python scripts/cross_model_agreement.py [--pools 40f 45f 48f]

For every pool, tier and model pair, compares the global SHAP importance of the SAME seed (Spearman rank correlation, cosine similarity and
top-10 Jaccard overlap over the shared feature set) and averages over the seeds. 95% percentile intervals come from the paired bootstrap resamples
of the explained rows stored by pipelines/run_tier_study.py (the same 1,000 rows and the same resample indices for every model): replicate b is the
mean over seeds of the agreement computed from resample b of both models. Reads results/metrics/<model>/shap_importance_<model>_<N>f.csv and
shap_boot_<model>_<N>f.npz; writes results/metrics/cross_model/cross_model_agreement_<N>f.csv and cross_model_agreement.md.
"""
from __future__ import annotations

import argparse
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config, resolve_path
from src.xai.explanation_stability import compare_importances

MODELS = ("xgboost", "logistic_regression", "random_forest")
SCORES = ["rank_correlation", "cosine_similarity", "topk_overlap"]


def agreement_with_intervals(vectors: dict[str, dict[int, pd.Series]], boots: dict[str, dict[int, np.ndarray]], features: list[str],
                             model_a: str, model_b: str, top_k: int = 10, level: float = 0.95) -> dict:
    """Agreement of two models for one tier: the mean over seeds of the point agreement and the percentile interval of the seed-averaged agreement over
    the bootstrap replicates. `vectors[model][seed]`: Series; `boots[model][seed]`: (replicates, features) array in `features` order."""
    seeds = sorted(set(vectors[model_a]) & set(vectors[model_b]))
    point = pd.DataFrame([compare_importances(vectors[model_a][s], vectors[model_b][s], top_k) for s in seeds])
    n_boot = min(boots[model_a][seeds[0]].shape[0], boots[model_b][seeds[0]].shape[0])
    replicates = []
    for b in range(n_boot):
        per_seed = [compare_importances(pd.Series(boots[model_a][s][b], index=features), pd.Series(boots[model_b][s][b], index=features), top_k) for s in seeds]
        replicates.append(pd.DataFrame(per_seed)[SCORES].mean())
    reps = pd.DataFrame(replicates)
    lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
    out = {"n_seeds": len(seeds), "n_bootstrap": n_boot, "n_common_features": int(point["n_common_features"].iloc[0])}
    for m in SCORES:
        out.update({f"{m}_mean": point[m].mean(), f"{m}_ci_low": reps[m].quantile(lo), f"{m}_ci_high": reps[m].quantile(hi)})
    return out


def model_dir(config: dict, model: str, in_dir: str | None = None) -> Path:
    """<in-dir>/<model>/ when that folder exists (local runs of a model family), else results/metrics/<model>/."""
    if in_dir and (Path(in_dir) / model).exists():
        return Path(in_dir) / model
    return get_metrics_dir(dict(config, model={"type": model}))


def load_model(config: dict, model: str, label: str, in_dir: str | None = None):
    d = model_dir(config, model, in_dir)
    imp, boot_path = d / f"shap_importance_{model}_{label}.csv", d / f"shap_boot_{model}_{label}.npz"
    if not imp.exists() or not boot_path.exists():
        return None
    return pd.read_csv(imp), np.load(boot_path)


def cross_model_table(config: dict, label: str, models=MODELS, in_dir: str | None = None) -> pd.DataFrame:
    loaded = {m: load_model(config, m, label, in_dir) for m in models}
    loaded = {m: v for m, v in loaded.items() if v is not None}
    if len(loaded) < 2:
        return pd.DataFrame()
    tiers = list(dict.fromkeys(next(iter(loaded.values()))[0]["tier"]))
    rows = []
    for tier in tiers:
        vectors, boots, features = {}, {}, None
        for m, (imp, npz) in loaded.items():
            sub = imp[imp["tier"] == tier]
            vectors[m] = {int(s): g.set_index("feature")["importance"] for s, g in sub.groupby("seed")}
            boots[m] = {s: npz[f"{tier}__{s}"] for s in vectors[m]}
            features = [str(f) for f in npz[f"{tier}__features"]]
        for a, b in combinations(loaded, 2):
            rows.append({"pool_label": label, "tier": tier, "model_a": a, "model_b": b, **agreement_with_intervals(vectors, boots, features, a, b)})
    return pd.DataFrame(rows).round(4)


def render(tables: dict[str, pd.DataFrame]) -> str:
    lines = ["# Feature-tier study Step 4: cross-model agreement of global SHAP importance (zero-shot; mean over seeds 42-46, 95% bootstrap interval over the explained rows)", "",
             "Spearman rank correlation / cosine similarity / top-10 Jaccard between two models on the same tier and seed. Agreement of explanations says nothing about "
             "the cause of the official-split shift.", ""]
    for label, t in tables.items():
        lines += [f"## {label}", "", "| tier | models | Spearman [95% CI] | cosine [95% CI] | top-10 Jaccard [95% CI] |", "|---|---|---|---|---|"]
        for r in t.itertuples(index=False):
            lines.append(f"| {r.tier} | {r.model_a} vs {r.model_b} | {r.rank_correlation_mean:.3f} [{r.rank_correlation_ci_low:.3f}, {r.rank_correlation_ci_high:.3f}] | "
                         f"{r.cosine_similarity_mean:.3f} [{r.cosine_similarity_ci_low:.3f}, {r.cosine_similarity_ci_high:.3f}] | "
                         f"{r.topk_overlap_mean:.3f} [{r.topk_overlap_ci_low:.3f}, {r.topk_overlap_ci_high:.3f}] |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["48f"], help="pool sizes, default the primary pool 48f; add 40f 45f for the comparison pools")
    parser.add_argument("--models", nargs="*", default=list(MODELS), help="model types to compare (their SHAP files must exist)")
    parser.add_argument("--in-dir", help="look for <in-dir>/<model>/ first (local runs); XGBoost falls back to results/metrics/xgboost/")
    parser.add_argument("--out-dir", help="where to write the agreement tables (default results/metrics/cross_model, or <in-dir>/cross_model with --in-dir)")
    args = parser.parse_args()
    config = load_config()
    out_dir = Path(args.out_dir) if args.out_dir else (Path(args.in_dir) / "cross_model" if args.in_dir else resolve_path(config["paths"]["results_dir"]) / "metrics" / "cross_model")
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = {}
    for label in args.pools:
        t = cross_model_table(config, label, tuple(args.models), args.in_dir)
        if len(t):
            tables[label] = t
            t.to_csv(out_dir / f"cross_model_agreement_{label}.csv", index=False)
    text = render(tables)
    (out_dir / "cross_model_agreement.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
