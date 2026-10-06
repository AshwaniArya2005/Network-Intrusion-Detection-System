"""Cross-dataset generalisation UNSW-NB15 <-> CICIDS2017 under a leak-free protocol (protocol: results/05_novelty4_cross_dataset.md, section `Source: cross_dataset_protocol.md`). XGBoost, binary, 14 common features.

    python pipelines/run_cross_dataset_study.py --step zero_shot      # Step 1 (+ the block mix tables)
    python pipelines/run_cross_dataset_study.py --step diagnostic    # Step 2
    python pipelines/run_cross_dataset_study.py --step align         # Step 3 (TRANSDUCTIVE)
    python pipelines/run_cross_dataset_study.py --step fewshot --direction UNSW_to_CIC   # Step 4 (FEW-SHOT), one direction per job

All splits are block-disjoint with a gap, for both datasets (src/evaluation/cross_dataset_protocol.py). Outputs go to results/metrics/xgboost/cross_dataset_<step>_*.csv.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.data_loader import load_cic_common, load_unsw
from src.evaluation import cross_dataset_protocol as cdp
from src.fpr_methods import diverse_selection, random_selection
from src.utils.config_loader import get_metrics_dir, load_config, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)
DIRECTIONS = {"UNSW_to_CIC": ("UNSW", "CIC"), "CIC_to_UNSW": ("CIC", "UNSW")}


@dataclass
class Settings:
    """The declared sizes (results/05_novelty4_cross_dataset.md, section `Source: cross_dataset_protocol.md`); tests pass smaller ones."""
    block: int = cdp.BLOCK
    buffer: int = cdp.BUFFER
    train_share: float = 0.6          # Steps 1-3: share of the target blocks that are "train blocks" (the rest are the evaluation blocks)
    fit_share: float = 0.85           # of a dataset's train blocks: the model is fitted on this share, the rest is the validation set that fixes the threshold
    source_cap: int = 200_000
    adapt_share: float = 0.4          # Step 4: share of the target blocks that are adaptation candidates
    pool_cap: int = 100_000
    ks: tuple = (100, 500, 1000, 5000, 10000)
    eval_thin: float = 0.25           # Step 4: share of the evaluation blocks scored when the target is larger than `thin_above` rows
    thin_above: int = 500_000
    top_k: int = 10
    n_random: int = 10
    draws: int = 5
    seeds: tuple = (42, 43, 44, 45, 46)
    strategies: tuple = ("random", "diverse")
    min_type_rows: int = 100


@dataclass
class Domain:
    name: str
    X: np.ndarray
    y: np.ndarray
    attack: np.ndarray
    day: np.ndarray | None = None
    features: list = field(default_factory=lambda: list(cdp.COMMON_FEATURES))


def make_domain(name: str, df: pd.DataFrame) -> Domain:
    return Domain(name, cdp.feature_matrix(df), df["label"].to_numpy().astype(int), df["attack_cat"].to_numpy(dtype=object), df["day"].to_numpy(dtype=object) if "day" in df else None)


def load_domains(config: dict) -> dict[str, Domain]:
    """UNSW-NB15 (official files, duplicates removed, file order) and CICIDS2017 (streamed once, cached as parquet, file order)."""
    unsw = load_unsw(resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"]), seed=config["project"]["seed"], synthetic_rows=config["data"]["synthetic_fallback_rows"])
    cic = load_cic_common(resolve_path(config["paths"]["cic_file"]), cache_path=resolve_path("data/processed/cic_common.parquet"), synthetic_rows=config["data"]["synthetic_fallback_rows"])
    return {"UNSW": make_domain("UNSW", unsw), "CIC": make_domain("CIC", cic)}


@dataclass
class Bundle:
    """A model trained on one dataset's own train blocks (fit part) with its threshold from the validation part, usable as a SOURCE model or as the leak-free within-dataset reference."""
    model: object
    threshold: float | None
    fit_pos: np.ndarray
    val_pos: np.ndarray
    train_pos: np.ndarray
    eval_pos: np.ndarray
    importance: pd.Series
    x_mean: np.ndarray
    x_std: np.ndarray


def build_bundle(dom: Domain, seed: int, st: Settings) -> Bundle:
    train_pos, eval_pos = cdp.split_positions(np.arange(len(dom.y)), st.train_share, seed, st.block, st.buffer)
    capped = cdp.cap_blocks(train_pos, st.source_cap, seed, st.block)
    fit_pos, val_pos = cdp.split_positions(capped, st.fit_share, seed + 1, st.block, st.buffer)
    model = cdp.fit_binary(dom.X[fit_pos], dom.y[fit_pos], seed)
    threshold = cdp.operating_threshold(dom.y[val_pos], cdp.score(model, dom.X[val_pos]))
    return Bundle(model, threshold, fit_pos, val_pos, train_pos, eval_pos, cdp.shap_importance(model, dom.X[fit_pos], dom.features, seed=seed),
                  dom.X[fit_pos].mean(axis=0), dom.X[fit_pos].std(axis=0))


def meta(direction: str, seed: int, method: str, access: str, **extra) -> dict:
    return {"direction": direction, "seed": seed, "method": method, "access": access, **extra}


def eval_row(base: dict, dom: Domain, pos: np.ndarray, s: np.ndarray, threshold: float | None, **extra) -> dict:
    return {**base, **cdp.evaluate_scores(dom.y[pos], s, threshold), **extra}


def type_rows(base: dict, dom: Domain, pos: np.ndarray, s: np.ndarray, threshold: float | None, st: Settings) -> list[dict]:
    t = cdp.type_recall(dom.attack[pos], dom.y[pos], s, threshold, st.min_type_rows)
    return [{**base, **r} for r in t.to_dict("records")]


# ---------------------------------------------------------------- Step 1: leak-free zero-shot
def run_zero_shot(domains: dict[str, Domain], st: Settings) -> dict[str, pd.DataFrame]:
    rows, types, mixes = [], [], []
    features = domains["UNSW"].features
    for seed in st.seeds:
        bundles = {name: build_bundle(dom, seed, st) for name, dom in domains.items()}
        for direction, (src_name, tgt_name) in DIRECTIONS.items():
            src, tgt, bs, bt = domains[src_name], domains[tgt_name], bundles[src_name], bundles[tgt_name]
            ev = bt.eval_pos
            s_ref = cdp.score(bt.model, tgt.X[ev])
            rows.append(eval_row(meta(direction, seed, "within_dataset_reference", "reference (target labels, leak-free)", n_features=len(features), subset=0), tgt, ev, s_ref, bt.threshold))
            types += type_rows(meta(direction, seed, "within_dataset_reference", "reference"), tgt, ev, s_ref, bt.threshold, st)
            s_common = cdp.score(bs.model, tgt.X[ev])
            rows.append(eval_row(meta(direction, seed, "common_all", "zero-shot", n_features=len(features), subset=0), tgt, ev, s_common, bs.threshold))
            types += type_rows(meta(direction, seed, "common_all", "zero-shot"), tgt, ev, s_common, bs.threshold, st)
            top_src = list(bs.importance.sort_values(ascending=False).index[: st.top_k])
            top_tgt = list(bt.importance.sort_values(ascending=False).index[: st.top_k])
            stable = [f for f in features if f in top_src and f in top_tgt]
            subsets = {"source_only": (top_src, "zero-shot"), "stable": (stable, "uses target labels (target model importance); not zero-shot")}
            for name, (names, access) in subsets.items():
                cols = [features.index(f) for f in names]
                model = cdp.fit_binary(src.X[bs.fit_pos], src.y[bs.fit_pos], seed, columns=cols)
                thr = cdp.operating_threshold(src.y[bs.val_pos], cdp.score(model, src.X[bs.val_pos], cols))
                s = cdp.score(model, tgt.X[ev], cols)
                rows.append(eval_row(meta(direction, seed, name, access, n_features=len(cols), subset=0, features=";".join(names)), tgt, ev, s, thr))
                types += type_rows(meta(direction, seed, name, access), tgt, ev, s, thr, st)
            size = max(2, len(stable))
            for j in range(st.n_random):
                cols = sorted(np.random.default_rng(100 * seed + j).choice(len(features), size=size, replace=False).tolist())
                model = cdp.fit_binary(src.X[bs.fit_pos], src.y[bs.fit_pos], seed, columns=cols)
                thr = cdp.operating_threshold(src.y[bs.val_pos], cdp.score(model, src.X[bs.val_pos], cols))
                rows.append(eval_row(meta(direction, seed, "random", "zero-shot", n_features=size, subset=j, features=";".join(features[c] for c in cols)), tgt, ev,
                                     cdp.score(model, tgt.X[ev], cols), thr))
            logger.info(f"[cross zero-shot {direction}] seed={seed} done (stable size {len(stable)})")
        for name, dom in domains.items():
            ev = bundles[name].eval_pos
            mix = cdp.block_mix(dom.attack, dom.y, st.block)
            counts = pd.Series(dom.attack[ev][dom.y[ev] == 1]).value_counts()
            mixes.append(pd.DataFrame({"dataset": name, "seed": seed, "attack_type": counts.index, "evaluation_rows": counts.values, "attack_blocks_in_dataset": int((mix["attack_share"] > 0).sum())}))
    blocks = pd.concat([pd.DataFrame({"dataset": name, **cdp.block_mix(dom.attack, dom.y, st.block).to_dict("list")}) for name, dom in domains.items()], ignore_index=True)
    return {"runs": pd.DataFrame(rows), "types": pd.DataFrame(types), "eval_mix": pd.concat(mixes, ignore_index=True), "block_mix": blocks}


# ---------------------------------------------------------------- Step 2: why zero-shot fails
def run_diagnostic(domains: dict[str, Domain], st: Settings) -> dict[str, pd.DataFrame]:
    uni = []
    for name, dom in domains.items():
        uni.append(cdp.univariate_auroc(dom.X, dom.y, dom.features).assign(dataset=name))
    uni = pd.concat(uni, ignore_index=True)
    wide = uni.pivot(index="feature", columns="dataset", values="auroc")
    wide["agree"] = (wide["UNSW"] - 0.5) * (wide["CIC"] - 0.5) > 0
    absent = uni.pivot(index="feature", columns="dataset", values="absent")
    wide["absent_in_either"] = absent["UNSW"] | absent["CIC"]
    wide["flipped"] = ~wide["agree"] & ~wide["absent_in_either"]
    spear = []
    for seed in st.seeds:
        b = {name: build_bundle(dom, seed, st) for name, dom in domains.items()}
        rho = spearmanr(b["UNSW"].importance.reindex(domains["UNSW"].features), b["CIC"].importance.reindex(domains["UNSW"].features))[0]
        spear.append({"seed": seed, "spearman_importance": float(rho), **{f"importance_rank_{n}_{f}": int(b[n].importance.rank(ascending=False)[f]) for n in b for f in domains["UNSW"].features}})
    return {"univariate": wide.reset_index(), "importance_agreement": pd.DataFrame(spear)}


# ---------------------------------------------------------------- Step 3: label-free alignment (TRANSDUCTIVE)
def run_align(domains: dict[str, Domain], st: Settings) -> dict[str, pd.DataFrame]:
    rows = []
    features = domains["UNSW"].features
    for seed in st.seeds:
        bundles = {name: build_bundle(dom, seed, st) for name, dom in domains.items()}
        for direction, (src_name, tgt_name) in DIRECTIONS.items():
            src, tgt, bs, bt = domains[src_name], domains[tgt_name], bundles[src_name], bundles[tgt_name]
            ev = bt.eval_pos
            Xs_fit, Xs_val, Xt_all = src.X[bs.fit_pos], src.X[bs.val_pos], tgt.X                          # Xt_all: the unlabelled target features (labels are never read here)
            ks = cdp.ks_ranking(Xs_fit, Xt_all, features, seed=seed)
            def evaluate(name: str, cols: list[int], zs_fit, zs_val, zt_eval, **extra):
                model = cdp.fit_binary(zs_fit, src.y[bs.fit_pos], seed, columns=cols)
                thr = cdp.operating_threshold(src.y[bs.val_pos], cdp.score(model, zs_val, cols))
                rows.append(eval_row(meta(direction, seed, name, "transductive", n_features=len(cols), **extra), tgt, ev, cdp.score(model, zt_eval, cols), thr))
            all_cols = list(range(len(features)))
            zs_fit, m_s, s_s = cdp.standardise(Xs_fit)
            evaluate("per_dataset_standardisation", all_cols, zs_fit, (Xs_val - m_s) / np.where(s_s > 0, s_s, 1.0), cdp.standardise(Xt_all)[0][ev])
            qs, qt = cdp.QuantileMapper().fit(Xs_fit), cdp.QuantileMapper().fit(Xt_all)
            evaluate("quantile_mapping", all_cols, qs.transform(Xs_fit), qs.transform(Xs_val), qt.transform(tgt.X[ev]))
            for m in (3, 5):
                drop = list(ks.index[:m])
                cols = [i for i, f in enumerate(features) if f not in drop]
                evaluate(f"drop_top{m}_shifted", cols, Xs_fit, Xs_val, tgt.X[ev], dropped=";".join(drop))
            drop3 = list(ks.index[:3])
            cols3 = [i for i, f in enumerate(features) if f not in drop3]
            evaluate("quantile_mapping_drop_top3", cols3, qs.transform(Xs_fit), qs.transform(Xs_val), qt.transform(tgt.X[ev]), dropped=";".join(drop3))
            logger.info(f"[cross align {direction}] seed={seed} done")
    return {"runs": pd.DataFrame(rows)}


# ---------------------------------------------------------------- Step 4: few-shot curve
def select_pool(strategy: str, Z: np.ndarray, k: int, seed: int) -> np.ndarray:
    if strategy == "random":
        return random_selection(len(Z), min(k, len(Z)), seed)
    if strategy == "diverse":
        return diverse_selection(Z, min(k, len(Z)), seed)
    raise ValueError(f"unknown strategy {strategy!r} (random or diverse)")


def run_fewshot(domains: dict[str, Domain], direction: str, st: Settings, save=None) -> dict[str, pd.DataFrame]:
    src_name, tgt_name = DIRECTIONS[direction]
    src, tgt = domains[src_name], domains[tgt_name]
    rows = []
    for seed in st.seeds:
        bs = build_bundle(src, seed, st)
        Xs, ys = src.X[bs.fit_pos], src.y[bs.fit_pos]
        for draw in range(st.draws):
            draw_seed = 100 * seed + draw
            cand, ev = cdp.split_positions(np.arange(len(tgt.y)), st.adapt_share, draw_seed, st.block, st.buffer)
            if len(tgt.y) > st.thin_above:
                ev = cdp.thin_blocks(ev, st.eval_thin, draw_seed, st.block)
            pool = np.sort(np.random.default_rng(draw_seed).choice(cand, size=min(st.pool_cap, len(cand)), replace=False))
            Zp = (tgt.X[pool] - bs.x_mean) / np.where(bs.x_std > 0, bs.x_std, 1.0)
            common = {"pool_rows": int(len(pool)), "candidate_rows": int(len(cand))}
            base = lambda method, access, strategy, k, **e: meta(direction, seed, method, access, draw=draw, strategy=strategy, k=k, **common, **e)   # noqa: E731
            s0 = cdp.score(bs.model, tgt.X[ev])
            rows.append(eval_row(base("zero_shot", "zero-shot", "none", 0), tgt, ev, s0, bs.threshold, threshold_source="source validation"))
            ref_pos = cdp.cap_blocks(cand, st.source_cap, draw_seed, st.block)
            rf, rv = cdp.split_positions(ref_pos, st.fit_share, draw_seed + 1, st.block, st.buffer)
            ref = cdp.fit_binary(tgt.X[rf], tgt.y[rf], seed)
            if ref is not None:
                rows.append(eval_row(base("within_dataset_reference", "reference (target labels, leak-free)", "none", len(ref_pos)), tgt, ev, cdp.score(ref, tgt.X[ev]),
                                     cdp.operating_threshold(tgt.y[rv], cdp.score(ref, tgt.X[rv])), threshold_source="reference validation blocks"))
            for strategy in st.strategies:
                for k in st.ks:
                    chosen = pool[select_pool(strategy, Zp, k, draw_seed + k)]
                    order = np.random.default_rng(draw_seed + k).permutation(len(chosen))
                    fit_half, thr_half = chosen[order[: (len(order) + 1) // 2]], chosen[order[(len(order) + 1) // 2:]]
                    info = {"n_fit": int(len(fit_half)), "n_threshold": int(len(thr_half)), "attack_share_fit": float(tgt.y[fit_half].mean())}
                    adapted = cdp.fit_adapted(Xs, ys, tgt.X[fit_half], tgt.y[fit_half], seed)
                    only = cdp.fit_binary(tgt.X[fit_half], tgt.y[fit_half], seed)
                    for method, access, model in (("source+target", "few-shot", adapted), ("target_only", "few-shot (no source data)", only)):
                        if model is None:
                            rows.append({**base(method, access, strategy, k, **info), "degenerate": True, "threshold_source": "single-class labelled rows"})
                            continue
                        thr = cdp.operating_threshold(tgt.y[thr_half], cdp.score(model, tgt.X[thr_half]))
                        source = "held-out labelled half"
                        if thr is None:
                            thr, source = bs.threshold, "source validation (labelled half had one class)"
                        rows.append(eval_row(base(method, access, strategy, k, **info), tgt, ev, cdp.score(model, tgt.X[ev]), thr, threshold_source=source))
            logger.info(f"[cross fewshot {direction}] seed={seed} draw={draw} done")
        if save:
            save({"runs": pd.DataFrame(rows)})
    return {"runs": pd.DataFrame(rows)}


def save_tables(config: dict, step: str, tables: dict[str, pd.DataFrame], suffix: str = "") -> None:
    d = get_metrics_dir(config)
    d.mkdir(parents=True, exist_ok=True)
    for kind, df in tables.items():
        if len(df):
            df.to_csv(d / f"cross_dataset_{step}{suffix}_{kind}.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--step", required=True, choices=["zero_shot", "diagnostic", "align", "fewshot"])
    parser.add_argument("--direction", choices=list(DIRECTIONS), help="few-shot: one direction per job")
    parser.add_argument("--seeds", nargs="*", type=int)
    args = parser.parse_args()
    config = load_config()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    st = Settings(seeds=tuple(args.seeds)) if args.seeds else Settings()
    domains = load_domains(config)
    if args.step == "fewshot":
        if not args.direction:
            raise SystemExit("--direction UNSW_to_CIC or CIC_to_UNSW is required for the few-shot step")
        save_tables(config, "fewshot", run_fewshot(domains, args.direction, st, lambda t: save_tables(config, "fewshot", t, f"_{args.direction}")), f"_{args.direction}")
    else:
        save_tables(config, args.step, {"zero_shot": run_zero_shot, "diagnostic": run_diagnostic, "align": run_align}[args.step](domains, st))


if __name__ == "__main__":
    main()
