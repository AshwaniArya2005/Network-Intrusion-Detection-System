"""Task 5.5: a more informative narrative, and the explanations of false positives (protocol: results/03_novelty2_explanations.md, section `Source: narratives_protocol.md`). XGBoost, official split, `current` scheme, ZERO-SHOT.

    python pipelines/run_narrative_study.py --part narrative --source validation --seeds 42 --pools base   # development on block-grouped validation flows only
    python pipelines/run_narrative_study.py --part narrative                                              # the one evaluation on a fresh official-test sample
    python pipelines/run_narrative_study.py --part falsepos

narrative  per model: the narratives of the classic and the class-relative style for the same flows, both through the dashboard's PredictionService on the same saved artifacts, audited with
           checks a-f of Task 5 and the new check g (clauses and calibrated number against independent computations). Writes narrative_<source>_<N>f_{narratives,failures,summary,calibration}.csv.
falsepos   official-test groups (false-positive Normal flows, true Normal flows predicted Normal, true Fuzzers): deletion faithfulness, cited features, raw and calibrated confidence and what
           separates a false positive from a correct flow. Writes narrative_falsepos_<N>f_{faithfulness,groups,features,separation}.csv.
"""
from __future__ import annotations

import argparse
import copy
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from dashboard.backend.prediction_service import PredictionService
from pipelines.run_tier_study import prepare
from pipelines.run_xai_study import LABEL_COLUMNS, audit_flows, audit_summary, correlation_matrix, strata_of, train_and_save
from src.fpr_methods import apply_temperature, fit_temperature
from src.utils.config_loader import get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger
from src.xai.faithfulness import bootstrap_mean_interval, faithfulness_curves
from src.xai.narrative_audit import parse_narrative
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)

SEEDS = (42, 43, 44, 45, 46)
ALLOCATION = {"class": 25, "Unknown": 50, "FP-Normal": 30}      # per predicted class, flagged Unknown, false-positive Normal (protocol)
TRAIN_SHAP_ROWS = 3000
GROUP_SIZE = 300
EVAL_SAMPLE_OFFSET, FALSEPOS_SAMPLE_OFFSET, DEV_SAMPLE_OFFSET = 5000, 7000, 3000


def allocation_sample(strata: np.ndarray, allocation: dict, rng: np.random.Generator) -> np.ndarray:
    """Sorted positions: `allocation["class"]` from every stratum that is not named in `allocation`, and the named strata (Unknown, FP-Normal) with their own sizes; without replacement."""
    chosen = []
    for s in sorted(set(strata.tolist())):
        rows = np.flatnonzero(strata == s)
        chosen.append(rng.choice(rows, size=min(allocation.get(s, allocation["class"]), len(rows)), replace=False))
    return np.sort(np.concatenate(chosen))


def two_services(service_cfg: dict) -> tuple[PredictionService, PredictionService]:
    """The dashboard service with each narrative style, loading the same saved artifacts."""
    classic = copy.deepcopy(service_cfg)
    classic["narrative"]["style"] = "classic"
    relative = copy.deepcopy(service_cfg)
    relative["narrative"]["style"] = "class_relative"
    return PredictionService(classic), PredictionService(relative)


def label_strata(service: PredictionService, raw: pd.DataFrame, true_labels: np.ndarray | None, normal: str) -> np.ndarray:
    """Predicted class, "Unknown" for flows the open-set rule flags, and "FP-Normal" for true Normal flows predicted as an attack and not flagged Unknown."""
    X = service.preprocessor.transform_features(raw)
    proba = service.model.predict_proba(X)
    classes = list(service.preprocessor.target_encoder.classes_)
    strata = strata_of(proba, service.wrapper.predict(X).is_unknown, classes)
    if true_labels is not None:
        strata = np.where((true_labels == normal) & (strata != normal) & (strata != "Unknown"), "FP-Normal", strata)
    return strata


def extra_rates(g: pd.DataFrame) -> dict:
    """Informativeness and (g) rates of one set of narratives."""
    cited_numeric, cited = g["n_cited_numeric"].sum(), g["n_cited_numeric"].sum() + g["n_cited_categorical"].sum()
    return {"typical_share_of_cited_numeric": g["f_no_direction_claimed"].sum() / cited_numeric if cited_numeric else np.nan,
            "cited_features_per_narrative": (g["n_cited_numeric"] + g["n_cited_categorical"]).mean(), "cited_numeric_per_narrative": g["n_cited_numeric"].mean(),
            "share_narratives_without_numeric_feature": (g["n_cited_numeric"] == 0).mean(),
            "g_clauses_correct": g["g_ok"].sum() / g["g_clauses"].sum() if g["g_clauses"].sum() else np.nan, "calibrated_number_correct": g["calibrated_ok"].mean() if "calibrated_ok" in g else np.nan}


def style_summary(narratives: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for style, g in narratives.groupby("style"):
        base = audit_summary(g)
        extra = []
        for (label, seed), gs in g.groupby(["pool_label", "seed"]):
            extra.append({"pool_label": label, "seed": seed, "stratum": "all", **extra_rates(gs)})
            extra += [{"pool_label": label, "seed": seed, "stratum": s, **extra_rates(gss)} for s, gss in gs.groupby("stratum")]
        merged = base.merge(pd.DataFrame(extra), on=["pool_label", "seed", "stratum"]).assign(style=style)
        if style == "classic":
            merged["g_clauses_correct"], merged["calibrated_number_correct"] = np.nan, np.nan          # the classic style has no clauses and no calibrated number
        parts.append(merged)
    return pd.concat(parts, ignore_index=True)


def run_narrative(config: dict, feature_sets: dict, pool: str, seeds=SEEDS, source: str = "test", scratch: Path | None = None, allocation: dict = ALLOCATION,
                  sample_offset: int | None = None) -> dict[str, pd.DataFrame]:
    scratch = scratch or resolve_path(config["paths"]["results_dir"]) / "_local_scratch" / "narrative_models"
    offset = (EVAL_SAMPLE_OFFSET if source == "test" else DEV_SAMPLE_OFFSET) if sample_offset is None else sample_offset
    rows, failures, calibration = [], [], []
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label, features = pool_label(sets), list(sets["feature_pool"])
        model, pre, service_cfg = train_and_save(cfg, sets, splits, features, scratch / f"{label}_{seed}")
        classic, relative = two_services(service_cfg)
        target, normal = cfg["data"]["target_column"], cfg["data"]["normal_category"]
        candidates = (pd.concat([splits.test, splits.unknown], ignore_index=True) if source == "test" else splits.val.reset_index(drop=True))
        true = candidates[target].to_numpy() if target in candidates else None
        raw = candidates.drop(columns=[c for c in LABEL_COLUMNS if c in candidates.columns])
        strata = label_strata(relative, raw, true, normal)
        pick = allocation_sample(strata, allocation, np.random.default_rng(offset + seed))
        sample = raw.iloc[pick].reset_index(drop=True)
        rho = correlation_matrix(model, pre, splits.train, features, TRAIN_SHAP_ROWS, seed)
        proba_val = model.predict_proba(pre.transform_features(splits.val))
        y_val = pre.target_encoder.transform(splits.val[target].astype(str))
        temperature = fit_temperature(proba_val, y_val)                                           # fitted independently of the saved file
        X_test, y_test = pre.transform(splits.test)
        from src.evaluation.metrics import expected_calibration_error
        p_test = model.predict_proba(X_test)
        calibration.append({"pool_label": label, "seed": seed, "temperature": temperature, "ece_raw": expected_calibration_error(y_test, p_test, cfg["evaluation"]["ece_bins"]),
                            "ece_calibrated": expected_calibration_error(y_test, apply_temperature(p_test, temperature), cfg["evaluation"]["ece_bins"])})
        for style, service in (("classic", classic), ("class_relative", relative)):
            results = service.predict(sample)
            r, f = audit_flows(sample, results, model, pre, service.config, splits.train, rho, features, seed, label, strata[pick], pick,
                               relative_temperature=temperature if style == "class_relative" else None)
            rows += [{**x, "style": style} for x in r]
            failures += [{**x, "style": style} for x in f]
        logger.info(f"[narrative {source} {label}] seed={seed}: {len(pick)} flows per style")
    narratives = pd.DataFrame(rows)
    return {"narratives": narratives, "failures": pd.DataFrame(failures), "summary": style_summary(narratives), "calibration": pd.DataFrame(calibration)}


# ---------------------------------------------------------------- Step 2: false-positive explanations
def group_masks(true_labels: np.ndarray, fine: np.ndarray, pred_labels: np.ndarray, normal: str) -> dict[str, np.ndarray]:
    """FP-attack (true Normal predicted as an attack), FP-Fuzzers (predicted Fuzzers), TN (true Normal predicted Normal) and TP-Fuzzers (true Fuzzers predicted Fuzzers)."""
    true_normal = true_labels == normal
    return {"FP-attack": true_normal & (pred_labels != normal), "FP-Fuzzers": true_normal & (pred_labels == "Fuzzers"), "TN": true_normal & (pred_labels == normal),
            "TP-Fuzzers": (fine == "Fuzzers") & (pred_labels == "Fuzzers")}


def atypicality(parsed: dict) -> float:
    """Share of a narrative's numeric reasons whose class clause says the value lies OUTSIDE the predicted class's interquartile range (NaN when no numeric reason has a class clause)."""
    clauses = [c for (f, cue, cat), c in zip(parsed["reasons"], parsed["clauses"]) if f is not None and cat is None and c is not None and ";" in c]
    if not clauses:
        return float("nan")
    return float(np.mean([not c.split("; ")[1].startswith("typical of") for c in clauses]))


def auroc(positive: np.ndarray, negative: np.ndarray) -> float:
    """AUROC of a score (higher = more likely a false positive), NaN scores dropped; NaN when either side is empty."""
    p, n = positive[~np.isnan(positive)], negative[~np.isnan(negative)]
    if len(p) == 0 or len(n) == 0:
        return float("nan")
    return float(roc_auc_score(np.r_[np.ones(len(p)), np.zeros(len(n))], np.r_[p, n]))


def run_falsepos(config: dict, feature_sets: dict, pool: str, seeds=SEEDS, group_size: int = GROUP_SIZE, scratch: Path | None = None, n_boot: int = 1000) -> dict[str, pd.DataFrame]:
    scratch = scratch or resolve_path(config["paths"]["results_dir"]) / "_local_scratch" / "narrative_models"
    faith, groups, features_rows, separation = [], [], [], []
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label, features = pool_label(sets), list(sets["feature_pool"])
        model, pre, service_cfg = train_and_save(cfg, sets, splits, features, scratch / f"{label}_{seed}")
        _, relative = two_services(service_cfg)
        target, normal = cfg["data"]["target_column"], cfg["data"]["normal_category"]
        classes = list(pre.target_encoder.classes_)
        test = splits.test.reset_index(drop=True)
        raw = test.drop(columns=[c for c in LABEL_COLUMNS if c in test.columns])
        X = pre.transform_features(raw)
        proba = model.predict_proba(X)
        pred = proba.argmax(axis=1)
        pred_labels = np.asarray(classes)[pred]
        flagged = relative.wrapper.predict(X).is_unknown
        temperature = fit_temperature(model.predict_proba(pre.transform_features(splits.val)), pre.target_encoder.transform(splits.val[target].astype(str)))
        calibrated = apply_temperature(proba, temperature)[np.arange(len(X)), pred]
        masks = group_masks(test[target].to_numpy(), test["attack_cat"].to_numpy(), pred_labels, normal)
        rng = np.random.default_rng(FALSEPOS_SAMPLE_OFFSET + seed)
        X_train = pre.transform(splits.train)[0]
        cat_cols = [features.index(f) for f in pre.categorical_features]
        explainer = SHAPExplainer(model, features, background_samples=100)
        scores = {}
        for name, mask in masks.items():
            idx = np.flatnonzero(mask)
            if len(idx) == 0:
                continue
            pick = np.sort(rng.choice(idx, size=min(group_size, len(idx)), replace=False))
            Xs, ps = X[pick], pred[pick]
            shap_values = explainer.local_explanations(Xs, ps).to_numpy()
            curves = faithfulness_curves(model, Xs, ps, shap_values, X_train, cat_cols, np.random.default_rng(seed))
            meta = {"pool_label": label, "seed": seed, "group": name, "n": int(len(pick)), "n_in_test": int(mask.sum())}
            for baseline in ("median", "random_row"):
                diff = curves["drop"][("top", baseline, 5)] - curves["drop"][("random", baseline, 5)]
                mean, lo, hi = bootstrap_mean_interval(diff, n_boot, seed=5)
                faith.append({**meta, "baseline": baseline, "top_drop_k5": float(curves["drop"][("top", baseline, 5)].mean()), "random_drop_k5": float(curves["drop"][("random", baseline, 5)].mean()),
                              "top_flip_k5": float(curves["flip"][("top", baseline, 5)].mean()), "random_flip_k5": float(curves["flip"][("random", baseline, 5)].mean()),
                              "difference": mean, "ci_low": lo, "ci_high": hi})
            narratives = relative.predict(raw.iloc[pick].reset_index(drop=True))
            parsed = [parse_narrative(r["narrative"], features) for r in narratives]
            atyp = np.array([atypicality(p) for p in parsed])
            shap_top = pd.DataFrame(shap_values, columns=features)
            classic_cited = Counter(f for _, row in shap_top.iterrows() for f in row.reindex(row.abs().sort_values(ascending=False).index[:cfg["xai"]["top_k_features"]]).loc[lambda s: s > 0].index)
            relative_cited = Counter(f for p in parsed for f, _, _ in p["reasons"] if f is not None)
            for style, counter in (("classic", classic_cited), ("class_relative", relative_cited)):
                features_rows += [{**meta, "style": style, "feature": f, "narratives_citing": c, "share": c / len(pick)} for f, c in counter.most_common(8)]
            groups.append({**meta, "raw_confidence_mean": float(proba[pick].max(axis=1).mean()), "calibrated_confidence_mean": float(calibrated[pick].mean()),
                           "raw_share_ge_0.90": float((proba[pick].max(axis=1) >= 0.90).mean()), "calibrated_share_ge_0.90": float((calibrated[pick] >= 0.90).mean()),
                           "share_flagged_unknown": float(flagged[pick].mean()), "mean_cited_features_class_relative": float(np.mean([len([r for r in p["reasons"] if r[0]]) for p in parsed])),
                           "atypicality_mean": float(np.nanmean(atyp)) if (~np.isnan(atyp)).any() else float("nan"), "atypicality_defined": int((~np.isnan(atyp)).sum())})
            scores[name] = {"raw": 1 - proba[pick].max(axis=1), "calibrated": 1 - calibrated[pick], "atypicality": atyp}
        for pos, neg in (("FP-Fuzzers", "TP-Fuzzers"), ("FP-attack", "TN")):
            if pos not in scores or neg not in scores:
                continue
            for score in ("raw", "calibrated", "atypicality"):
                separation.append({"pool_label": label, "seed": seed, "false_positive_group": pos, "compared_with": neg, "score": {"raw": "1 - raw confidence", "calibrated": "1 - calibrated confidence",
                                   "atypicality": "class-atypicality of the cited features"}[score], "auroc": auroc(scores[pos][score], scores[neg][score])})
        logger.info(f"[falsepos {label}] seed={seed} done")
    return {"faithfulness": pd.DataFrame(faith), "groups": pd.DataFrame(groups), "features": pd.DataFrame(features_rows), "separation": pd.DataFrame(separation)}


def save(config: dict, name: str, label: str, tables: dict[str, pd.DataFrame]) -> None:
    d = get_metrics_dir(config)
    d.mkdir(parents=True, exist_ok=True)
    for kind, df in tables.items():
        if len(df):
            df.to_csv(d / f"narrative_{name}_{label}_{kind}.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--part", required=True, choices=["narrative", "falsepos"])
    parser.add_argument("--pools", nargs="*", default=["full"], help="default: the primary pool 48 (full); add base (40) or full_no_ttl (45) for the comparison pools")
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--source", choices=["test", "validation"], default="test")
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    seeds = tuple(args.seeds) if args.seeds else SEEDS
    for pool in args.pools:
        label = pool_label(prepare(config, feature_sets, pool, "xgboost", 42)[1])
        if args.part == "narrative":
            save(config, args.source, label, run_narrative(config, feature_sets, pool, seeds, args.source))
        else:
            save(config, "falsepos", label, run_falsepos(config, feature_sets, pool, seeds))


if __name__ == "__main__":
    main()
