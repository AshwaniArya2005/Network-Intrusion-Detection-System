"""Task 5: are the explanations faithful and are the narratives correct? (protocol: results/03_novelty2_explanations.md, section `Source: explanations_protocol.md`). XGBoost, official split, `current` scheme, ZERO-SHOT.

    python pipelines/run_xai_study.py --part faithfulness [--pools base full_no_ttl full] [--seeds 42 43 44 45 46]
    python pipelines/run_xai_study.py --part audit        [--pools base full]

faithfulness  Steps 1 (SHAP additivity) and 2 (deletion / insertion) for every pool and its 30- and 15-feature tiers, on a stratified sample of official-test flows and of block-grouped
              validation flows (the shift check). Writes xai_faithfulness_<N>f_runs.csv and xai_additivity_<N>f.csv.
audit         Steps 1 (quoted confidence) and 3 (narrative audit): a model is trained and SAVED to a scratch directory, the dashboard's PredictionService loads it exactly as the dashboard does and
              produces the narratives, which are checked (a)-(f) against independent computations. Writes xai_audit_<N>f_{narratives,failures,summary}.csv.
Files go under results/metrics/xgboost/ (pool size in the name).
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import shap
from scipy.stats import spearmanr

from pipelines.run_tier_study import ensure_pool_ranking, prepare
from pipelines.train_pipeline import train_and_evaluate
from src.fpr_methods import apply_temperature
from src.models.open_set_wrapper import select_threshold
from src.preprocessing import _clean_numeric, engineer_features
from src.utils.config_loader import get_active_features, get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger
from src.xai.faithfulness import (
    KS, METHODS, additivity_error, bootstrap_mean_interval, faithfulness_curves, stratified_sample,
)
from src.xai.narrative_audit import (
    check_action, check_categorical, check_category_clause, check_cited_in_top, check_cue, check_label_statement, check_numeric_clause, cue_direction, directional_consistency,
    parse_narrative, shap_trend_phrase,
)
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)

SEEDS = (42, 43, 44, 45, 46)
PER_CLASS, UNKNOWN_N = 300, 200                 # Step 2 sample
AUDIT_PER_CLASS, AUDIT_UNKNOWN = 25, 50         # Step 3 sample
TOLERANCE = 1e-3                                # SHAP additivity tolerance on the raw margin
TRAIN_SHAP_ROWS = 3000                          # rows for the directional-consistency correlations
LABEL_COLUMNS = ["attack_cat", "label", "label_merged", "split"]


def flag_unknown(model, proba_val: np.ndarray, proba: np.ndarray) -> np.ndarray:
    """Open-set flag as the dashboard has it: max-softmax below the 5%-false-Unknown threshold of the block-grouped validation flows."""
    threshold = select_threshold(proba_val.max(axis=1), 0.05)
    return proba.max(axis=1) < threshold


def strata_of(proba: np.ndarray, flagged: np.ndarray, classes: list[str]) -> np.ndarray:
    return np.where(flagged, "Unknown", np.asarray(classes)[proba.argmax(axis=1)])


# ---------------------------------------------------------------- Steps 1-2: additivity and faithfulness
def summarise_curves(curves: dict, strata: np.ndarray, meta: dict, n_boot: int = 1000) -> list[dict]:
    rows = []
    groups = {"all": np.ones(len(strata), bool), **{s: strata == s for s in sorted(set(strata))}}
    for name, mask in groups.items():
        for (method, baseline, k), drop in curves["drop"].items():
            rows.append({**meta, "stratum": name, "method": method, "baseline": baseline, "k": k, "n": int(mask.sum()), "mean_drop": float(drop[mask].mean()),
                         "flip_rate": float(curves["flip"][(method, baseline, k)][mask].mean()), "mean_insertion": float(curves["insertion"][(method, baseline, k)][mask].mean()),
                         "mean_p0": float(curves["p0"][mask].mean())})
        for baseline in ("median", "random_row"):
            for k in KS:
                diff = (curves["drop"][("top", baseline, k)] - curves["drop"][("random", baseline, k)])[mask]
                mean, lo, hi = bootstrap_mean_interval(diff, n_boot, seed=k)
                rows.append({**meta, "stratum": name, "method": "top_minus_random", "baseline": baseline, "k": k, "n": int(mask.sum()), "mean_drop": mean, "ci_low": lo, "ci_high": hi})
    return rows


def run_faithfulness(config: dict, feature_sets: dict, pool: str, seeds=SEEDS, n_boot: int = 1000, per_class: int = PER_CLASS, unknown_n: int = UNKNOWN_N) -> dict[str, pd.DataFrame]:
    runs, additivity, flow_diffs = [], [], []
    ensure_pool_ranking(config, feature_sets, pool)
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label, whole = pool_label(sets), str(len(sets["feature_pool"]))
        for tier in dict.fromkeys([whole, "30", "15"]):
            features = list(sets["feature_pool"]) if tier == whole else get_active_features(cfg, sets, tier)
            pred = {}
            train_and_evaluate(cfg, sets, tier, False, splits, False, pred, features=features)
            model, pre = pred["model"], pred["preprocessor"]
            classes = list(pre.target_encoder.classes_)
            X_train = pre.transform(splits.train)[0]
            cat_cols = [features.index(f) for f in pre.categorical_features]
            explainer = SHAPExplainer(model, features, background_samples=100)
            for source, frame in (("test", pd.concat([splits.test, splits.unknown], ignore_index=True)), ("validation", splits.val)):
                X = pre.transform_features(frame)
                proba = model.predict_proba(X)
                strata = strata_of(proba, flag_unknown(model, pred["y_proba_val"], proba), classes)
                rng = np.random.default_rng(seed * 100 + (0 if source == "test" else 1))
                pick = stratified_sample(strata, per_class, "Unknown", unknown_n, rng)
                Xs, ps, ss = X[pick], proba[pick].argmax(axis=1), strata[pick]
                shap_values = explainer.local_explanations(Xs, ps).to_numpy()
                margin = model.underlying_model.predict(Xs, output_margin=True)[np.arange(len(Xs)), ps]
                err = additivity_error(shap_values.sum(axis=1), explainer.expected_values(Xs)[ps], margin)
                meta = {"pool_label": label, "tier": tier, "n_features": len(features), "seed": seed, "source": source}
                additivity.append({**meta, "n": int(len(err)), "max_abs_error": float(err.max()), "mean_abs_error": float(err.mean()), "n_over_tolerance": int((err > TOLERANCE).sum())})
                curves = faithfulness_curves(model, Xs, ps, shap_values, X_train, cat_cols, np.random.default_rng(seed * 100 + 7))
                runs += summarise_curves(curves, ss, meta, n_boot)
                primary = curves["drop"][("top", "median", 5)] - curves["drop"][("random", "median", 5)]         # per-flow primary-metric differences, for the shift bootstrap
                flow_diffs.append(pd.DataFrame({**meta, "stratum": ss, "diff_top_minus_random_k5": primary}))
            logger.info(f"[xai faithfulness {label}] seed={seed} tier={tier} done")
    return {"runs": pd.DataFrame(runs), "additivity": pd.DataFrame(additivity), "flowdiffs": pd.concat(flow_diffs, ignore_index=True)}


# ---------------------------------------------------------------- Steps 1 and 3: the audit through the dashboard path
def train_and_save(cfg: dict, sets: dict, splits, features: list[str], models_dir: Path):
    """Train the closed-set model and save it where the dashboard's PredictionService looks for it (a scratch directory); returns (the in-memory model, the in-memory preprocessor, the config
    the service needs)."""
    cfg = copy.deepcopy(cfg)
    cfg["paths"]["models_dir"] = str(models_dir)
    tier = str(len(features))
    cfg["dashboard"]["feature_set"] = tier
    pred = {}
    train_and_evaluate(cfg, sets, tier, False, splits, True, pred, features=features)
    return pred["model"], pred["preprocessor"], cfg


def training_statistics(train_df: pd.DataFrame, numeric_features: list[str]) -> tuple[pd.Series, pd.Series]:
    """Mean and standard deviation (ddof 0) of the engineered numeric features of the raw TRAINING frame, computed without the preprocessor's scaler."""
    numeric = _clean_numeric(engineer_features(train_df, allow_missing=True), numeric_features)
    return numeric.mean(), numeric.std(ddof=0)


def correlation_matrix(model, pre, train_df: pd.DataFrame, features: list[str], n_rows: int, seed: int) -> np.ndarray:
    """(n_classes, n_features) Spearman correlation between a feature's value and its SHAP value for each class, on a seeded sample of training rows (independent TreeExplainer)."""
    X = pre.transform_features(train_df)
    X = X[np.random.default_rng(seed).choice(len(X), min(n_rows, len(X)), replace=False)]
    values = shap.TreeExplainer(model.underlying_model).shap_values(X)
    per_class = [values[:, :, c] for c in range(values.shape[2])] if np.ndim(values) == 3 else list(values)
    rho = np.zeros((len(per_class), len(features)))
    for c, sv in enumerate(per_class):
        for j in range(len(features)):
            rho[c, j] = 0.0 if np.std(X[:, j]) == 0 or np.std(sv[:, j]) == 0 else spearmanr(X[:, j], sv[:, j])[0]
    return rho


def audit_flows(frame: pd.DataFrame, results: list[dict], model, pre, cfg: dict, train_df: pd.DataFrame, rho: np.ndarray, features: list[str], seed: int, label: str,
                strata: np.ndarray, flow_index: np.ndarray, relative_temperature: float | None = None) -> tuple[list[dict], list[dict]]:
    """Check every narrative of `results` (the dashboard's output for the rows of `frame`) against independent computations. Returns (one row per narrative, one row per failure).
    With `relative_temperature` (the class-relative style of Task 5.5) check (g) is added: every clause against the raw training frame, and the calibrated number against the temperature."""
    classes = list(pre.target_encoder.classes_)
    X = pre.transform_features(frame)
    proba = model.predict_proba(X)
    pred_idx = proba.argmax(axis=1)
    explainer = shap.TreeExplainer(model.underlying_model)
    raw = explainer.shap_values(X)
    per_class = np.stack([raw[:, :, c] for c in range(raw.shape[2])], axis=0) if np.ndim(raw) == 3 else np.stack(raw, axis=0)
    shap_rows = per_class[pred_idx, np.arange(len(X))]
    means, stds = training_statistics(train_df, pre.numeric_features)
    engineered = _clean_numeric(engineer_features(frame, allow_missing=True), pre.numeric_features)
    actions, top_k = cfg["narrative"]["suggested_actions"], cfg["xai"]["top_k_features"]
    rows, failures = [], []
    for i, res in enumerate(results):
        text, parsed = res["narrative"], parse_narrative(res["narrative"], features)
        predicted, unknown = classes[pred_idx[i]], bool(res["is_unknown"])
        shap_row = pd.Series(shap_rows[i], index=features)
        fail = []
        quoted_ok = parsed["confidence_pct"] is not None and f"{proba[i, pred_idx[i]] * 100:.1f}" == f"{parsed['confidence_pct']:.1f}"
        json_ok = res["confidence"] == round(float(proba[i, pred_idx[i]]), 4)
        if not quoted_ok:
            fail.append(("confidence", f"narrative says {parsed['confidence_pct']}% but the model's probability is {proba[i, pred_idx[i]] * 100:.1f}%"))
        if not json_ok:
            fail.append(("confidence", f"JSON confidence {res['confidence']} != {round(float(proba[i, pred_idx[i]]), 4)}"))
        cited = [f for f, _, _ in parsed["reasons"] if f is not None]
        unparsed = [r for r in parsed["reasons"] if r[0] is None]
        a_ok = (not unparsed) and check_cited_in_top(cited, shap_row, top_k)
        if not a_ok:
            fail.append(("a_cited_in_top_k", f"cited {cited}, positive top-{top_k}: {sorted(shap_row.reindex(shap_row.abs().sort_values(ascending=False).index[:top_k]).loc[lambda s: s > 0].index)}"
                         + (f"; unparsed {unparsed}" if unparsed else "")))
        b_exact = b_dir = n_num = c_ok_n = n_cat = f_cons = f_incons = f_nomono = f_nodir = 0
        g_ok_n = g_n = n_outside = 0
        class_rows = (train_df[cfg["data"]["target_column"]] == predicted).to_numpy() if relative_temperature is not None else None
        for idx, (feature, cue, category) in enumerate(parsed["reasons"]):
            if feature is None:
                continue
            clause = parsed["clauses"][idx]
            if feature in pre.categorical_features:
                n_cat += 1
                raw_value = str(frame.iloc[i][feature]) if pd.notna(frame.iloc[i][feature]) else "unknown"
                ok, reason = check_categorical(feature, cue, category, raw_value, raw_value in set(pre.label_encoders[feature].classes_))
                c_ok_n += int(ok)
                if not ok:
                    fail.append(("c_categorical", reason))
                if relative_temperature is not None:
                    train_cat = train_df[feature].fillna("unknown").astype(str).to_numpy()
                    g_ok, g_reason = check_category_clause(clause, raw_value, train_cat, train_cat[class_rows], predicted, unknown)
                    g_n, g_ok_n = g_n + 1, g_ok_n + int(g_ok)
                    if not g_ok:
                        fail.append(("g_clause", f"{feature}: {g_reason}"))
                continue
            n_num += 1
            if relative_temperature is not None:
                column = _clean_numeric(engineer_features(train_df, allow_missing=True), [feature])[feature].to_numpy()
                g_ok, outside, g_reason = check_numeric_clause(clause, cue, float(engineered.iloc[i][feature]), column, column[class_rows], predicted, unknown)
                g_n, g_ok_n, n_outside = g_n + 1, g_ok_n + int(g_ok), n_outside + int(outside)
                if not g_ok:
                    fail.append(("g_clause", f"{feature}: {g_reason}"))
            z = float((engineered.iloc[i][feature] - means[feature]) / (stds[feature] or 1e-9))
            c = check_cue(cue, z)
            b_exact, b_dir = b_exact + int(c["exact"]), b_dir + int(c["direction"])
            if not c["exact"]:
                fail.append(("b_cue", f"{feature}: cue {cue!r}, z-score vs the training mean/std is {z:.2f} (expected {c['expected']!r})"))
            verdict = directional_consistency(cue, rho[pred_idx[i], features.index(feature)])
            f_cons, f_incons = f_cons + int(verdict == "consistent"), f_incons + int(verdict == "inconsistent")
            f_nomono, f_nodir = f_nomono + int(verdict == "no monotone relation"), f_nodir + int(verdict == "no direction claimed")
            if verdict == "inconsistent":
                rho_value = rho[pred_idx[i], features.index(feature)]
                fail.append(("f_direction", f"{feature}: cue {cue!r} but SHAP for {predicted} {shap_trend_phrase(rho_value)} as the value rises (rho {rho_value:.2f} on training rows)"))
        d_ok = check_action(parsed["action"], "Unknown" if unknown else predicted, actions)
        if not d_ok:
            fail.append(("d_action", f"action {parsed['action']!r} for label {'Unknown' if unknown else predicted!r}"))
        e_ok, e_reason = check_label_statement(parsed, predicted, unknown, text)
        if not e_ok:
            fail.append(("e_label", e_reason))
        calibrated_ok = True
        if relative_temperature is not None:
            expected_cal = 100 * float(apply_temperature(proba[i:i + 1], relative_temperature)[0, pred_idx[i]])
            calibrated_ok = parsed["calibrated_pct"] is not None and abs(parsed["calibrated_pct"] - expected_cal) <= 1.0 and res.get("calibrated_confidence") is not None \
                and abs(100 * res["calibrated_confidence"] - expected_cal) <= 0.01
            if not calibrated_ok:
                fail.append(("g_calibrated", f"narrative says {parsed['calibrated_pct']}% but the temperature-scaled probability is {expected_cal:.1f}%"))
        rows.append({"pool_label": label, "seed": seed, "flow": int(flow_index[i]), "stratum": strata[i], "predicted": predicted, "is_unknown": unknown, "narrative": text,
                     "confidence_text_ok": quoted_ok, "confidence_json_ok": json_ok, "a_ok": a_ok, "n_cited_numeric": n_num, "b_exact": b_exact, "b_direction": b_dir,
                     "n_cited_categorical": n_cat, "c_ok": c_ok_n, "d_ok": d_ok, "e_ok": e_ok, "f_consistent": f_cons, "f_inconsistent": f_incons, "f_no_monotone_relation": f_nomono,
                     "f_no_direction_claimed": f_nodir, "n_failures": len(fail), "diffuse": parsed["diffuse"], "g_clauses": g_n, "g_ok": g_ok_n, "calibrated_ok": calibrated_ok,
                     "n_outside_class_iqr": n_outside, "confidence": float(proba[i, pred_idx[i]])})
        failures += [{"pool_label": label, "seed": seed, "flow": int(flow_index[i]), "stratum": strata[i], "predicted": predicted, "check": c, "reason": r, "narrative": text} for c, r in fail]
    return rows, failures


def run_audit(config: dict, feature_sets: dict, pool: str, seeds=SEEDS, scratch: Path | None = None, per_class: int = AUDIT_PER_CLASS, unknown_n: int = AUDIT_UNKNOWN,
              source: str = "test") -> dict[str, pd.DataFrame]:
    from dashboard.backend.prediction_service import PredictionService
    scratch = scratch or resolve_path(config["paths"]["results_dir"]) / "_local_scratch" / "xai_models"
    rows, failures = [], []
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label, features = pool_label(sets), list(sets["feature_pool"])
        model, pre, service_cfg = train_and_save(cfg, sets, splits, features, scratch / f"{label}_{seed}")
        service = PredictionService(service_cfg)
        candidates = pd.concat([splits.test, splits.unknown], ignore_index=True) if source == "test" else splits.val.reset_index(drop=True)   # `validation`: block-grouped validation flows, no shift
        raw = candidates.drop(columns=[c for c in LABEL_COLUMNS if c in candidates.columns])           # the dashboard receives flows without labels
        proba_c = service.model.predict_proba(service.preprocessor.transform_features(raw))
        flagged = service.wrapper.predict(service.preprocessor.transform_features(raw)).is_unknown
        strata = strata_of(proba_c, flagged, list(service.preprocessor.target_encoder.classes_))
        pick = stratified_sample(strata, per_class, "Unknown", unknown_n, np.random.default_rng(seed))
        sample = raw.iloc[pick].reset_index(drop=True)
        results = service.predict(sample)
        rho = correlation_matrix(model, pre, splits.train, features, TRAIN_SHAP_ROWS, seed)
        r, f = audit_flows(sample, results, model, pre, service_cfg, splits.train, rho, features, seed, label, strata[pick], pick)
        rows += r
        failures += f
        logger.info(f"[xai audit {label}] seed={seed}: {len(r)} narratives, {len(f)} failures")
    narratives = pd.DataFrame(rows)
    return {"narratives": narratives, "failures": pd.DataFrame(failures), "summary": audit_summary(narratives)}


def audit_summary(n: pd.DataFrame) -> pd.DataFrame:
    """Correctness rates per check, overall and per predicted stratum, per seed (flow level: all cited features pass; cite level for b, c, f)."""
    def rates(g: pd.DataFrame) -> dict:
        cites, cats = g["n_cited_numeric"].sum(), g["n_cited_categorical"].sum()
        determined = g["f_consistent"].sum() + g["f_inconsistent"].sum()
        return {"n": len(g), "confidence_text": g["confidence_text_ok"].mean(), "confidence_json": g["confidence_json_ok"].mean(), "a_cited_in_top_k": g["a_ok"].mean(),
                "b_cue_exact_cite": g["b_exact"].sum() / cites if cites else np.nan, "b_cue_direction_cite": g["b_direction"].sum() / cites if cites else np.nan,
                "b_cue_exact_flow": ((g["b_exact"] == g["n_cited_numeric"])).mean(), "c_categorical_cite": g["c_ok"].sum() / cats if cats else np.nan,
                "d_action": g["d_ok"].mean(), "e_label": g["e_ok"].mean(), "f_consistent_of_determined": g["f_consistent"].sum() / determined if determined else np.nan,
                "f_share_no_monotone_relation": g["f_no_monotone_relation"].sum() / max(cites, 1), "f_share_typical_cue": g["f_no_direction_claimed"].sum() / max(cites, 1),
                "share_diffuse_narratives": g["diffuse"].mean(), "mean_failures_per_narrative": g["n_failures"].mean()}
    out = []
    for (label, seed), g in n.groupby(["pool_label", "seed"]):
        out.append({"pool_label": label, "seed": seed, "stratum": "all", **rates(g)})
        out += [{"pool_label": label, "seed": seed, "stratum": s, **rates(gs)} for s, gs in g.groupby("stratum")]
    return pd.DataFrame(out)


def save(config: dict, name: str, label: str, tables: dict[str, pd.DataFrame]) -> None:
    d = get_metrics_dir(config)
    d.mkdir(parents=True, exist_ok=True)
    for kind, df in tables.items():
        if len(df):
            df.to_csv(d / (f"xai_{name}_{label}_{kind}.csv" if kind != "additivity" else f"xai_additivity_{label}.csv"), index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--part", required=True, choices=["faithfulness", "audit"])
    parser.add_argument("--pools", nargs="*")
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--source", choices=["test", "validation"], default="test", help="audit: flows from the official test file (default) or from block-grouped validation (the shift check)")
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    seeds = tuple(args.seeds) if args.seeds else SEEDS
    for pool in args.pools or (["base", "full_no_ttl", "full"] if args.part == "faithfulness" else ["base", "full"]):
        label = pool_label(prepare(config, feature_sets, pool, "xgboost", 42)[1])
        if args.part == "faithfulness":
            save(config, "faithfulness", label, run_faithfulness(config, feature_sets, pool, seeds))
        else:
            save(config, "audit" if args.source == "test" else "audit_validation", label, run_audit(config, feature_sets, pool, seeds, source=args.source))


if __name__ == "__main__":
    main()
