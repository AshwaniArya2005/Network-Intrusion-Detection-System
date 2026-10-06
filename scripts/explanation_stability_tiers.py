"""Task 3 Step 2: stability of global SHAP importance across feature tiers, with the same-tier / different-seed noise floor.

    python scripts/explanation_stability_tiers.py [--model xgboost] [--pools 40f 45f 48f]

Reads results/metrics/<model>/shap_importance_<model>_<N>f.csv (written by pipelines/run_tier_study.py) and writes stability_<model>_<N>f.csv and
stability_<model>.md. Definitions are those of src/xai/explanation_stability.py (Spearman rank correlation, cosine similarity and top-10 Jaccard
overlap over the common features). `tier_pair`: two tiers of the same seed (nested feature sets), averaged over the seeds. `same_tier_seeds`: the
same tier under two different seeds, over all pairs of seeds (the noise floor). Protocol change from the earlier study: a seed here also changes
the block-grouped train / validation split, so the floor includes training-subset variation, not only model-seed variation.
"""
from __future__ import annotations

import argparse
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config
from src.xai.explanation_stability import compare_importances

SCORES = ["rank_correlation", "cosine_similarity", "topk_overlap"]


def importance_vectors(importances: pd.DataFrame) -> dict[tuple[str, int], pd.Series]:
    """{(tier, seed): Series feature -> importance} from the long importance table."""
    return {(t, int(s)): g.set_index("feature")["importance"] for (t, s), g in importances.groupby(["tier", "seed"])}


def stability_table(importances: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
    vec = importance_vectors(importances)
    tiers = list(dict.fromkeys(importances["tier"]))
    seeds = sorted({s for _, s in vec})
    rows = []
    for a, b in combinations(tiers, 2):
        per_seed = pd.DataFrame([compare_importances(vec[(a, s)], vec[(b, s)], top_k) for s in seeds if (a, s) in vec and (b, s) in vec])
        rows.append({"comparison": "tier_pair", "a": a, "b": b, "n": len(per_seed), "n_common_features": int(per_seed["n_common_features"].iloc[0]),
                     **{f"{m}_mean": per_seed[m].mean() for m in SCORES}, **{f"{m}_std": per_seed[m].std(ddof=1) for m in SCORES}})
    for t in tiers:
        pairs = pd.DataFrame([compare_importances(vec[(t, s1)], vec[(t, s2)], top_k) for s1, s2 in combinations(seeds, 2) if (t, s1) in vec and (t, s2) in vec])
        rows.append({"comparison": "same_tier_seeds", "a": t, "b": t, "n": len(pairs), "n_common_features": int(pairs["n_common_features"].iloc[0]),
                     **{f"{m}_mean": pairs[m].mean() for m in SCORES}, **{f"{m}_std": pairs[m].std(ddof=1) for m in SCORES}})
    return pd.DataFrame(rows).round(4)


def render(model: str, tables: dict[str, pd.DataFrame]) -> str:
    lines = [f"# Task 3 Step 2: explanation stability, {model} (mean over seeds 42-46; zero-shot)", "",
             "Tier agreement = SHAP importance of two tiers of the same seed; noise floor = the same tier under two seeds. Spearman rank correlation / cosine / top-10 Jaccard. "
             "Stability is evidence about the explanations, not about the cause of the official-split shift.", ""]
    for label, t in tables.items():
        tp, floor = t[t["comparison"] == "tier_pair"], t[t["comparison"] == "same_tier_seeds"]
        lines += [f"## {label}", "", f"Tier agreement: Spearman {tp['rank_correlation_mean'].min():.3f}-{tp['rank_correlation_mean'].max():.3f} (mean {tp['rank_correlation_mean'].mean():.3f}), "
                  f"cosine {tp['cosine_similarity_mean'].min():.3f}-{tp['cosine_similarity_mean'].max():.3f}, top-10 Jaccard {tp['topk_overlap_mean'].min():.3f}-{tp['topk_overlap_mean'].max():.3f}. "
                  f"Noise floor (same tier, different seeds): Spearman {floor['rank_correlation_mean'].min():.3f}-{floor['rank_correlation_mean'].max():.3f}, "
                  f"cosine {floor['cosine_similarity_mean'].min():.3f}-{floor['cosine_similarity_mean'].max():.3f}, top-10 Jaccard {floor['topk_overlap_mean'].min():.3f}-{floor['topk_overlap_mean'].max():.3f}.", "",
                  "| comparison | a | b | common features | Spearman | cosine | top-10 Jaccard |", "|---|---|---|---|---|---|---|"]
        for r in t.itertuples(index=False):
            lines.append(f"| {r.comparison} | {r.a} | {r.b} | {r.n_common_features} | {r.rank_correlation_mean:.3f} +/- {r.rank_correlation_std:.3f} | "
                         f"{r.cosine_similarity_mean:.3f} +/- {r.cosine_similarity_std:.3f} | {r.topk_overlap_mean:.3f} +/- {r.topk_overlap_std:.3f} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="xgboost")
    parser.add_argument("--pools", nargs="*", default=["48f"], help="pool sizes, default the primary pool 48f; add 40f 45f for the comparison pools")
    parser.add_argument("--in-dir", help="read and write under <in-dir>/<model>/ instead of results/metrics/<model>/")
    args = parser.parse_args()
    d = Path(args.in_dir) / args.model if args.in_dir else get_metrics_dir(dict(load_config(), model={"type": args.model}))
    tables = {}
    for label in args.pools:
        path = d / f"shap_importance_{args.model}_{label}.csv"
        if path.exists():
            tables[label] = stability_table(pd.read_csv(path))
            tables[label].to_csv(d / f"stability_{args.model}_{label}.csv", index=False)
    text = render(args.model, tables)
    (d / f"stability_{args.model}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
