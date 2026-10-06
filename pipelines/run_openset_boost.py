"""Task 4.5: try to improve zero-day (open-set) detection (protocol: results/task_4_5_protocol.md). XGBoost, flat model, official split, ZERO-SHOT.

    python pipelines/run_openset_boost.py --idea calibration|perclass|ensemble|distance|oe [--pools base full] [--seeds 42 43 44 45 46] [--specs ...]
    python pipelines/run_openset_boost.py --idea selection   # pseudo-unknown validation of every individual score (inner models without Reconnaissance / Generic)
    python pipelines/run_openset_boost.py --idea combo       # rank-average of the two best individual scores by that selection
    python pipelines/run_openset_boost.py --idea iforest     # the isolation-forest sign check

Each idea is evaluated on the same held-out sets as Task 4: Worms + Shellcode, the nine leave-one-class-out classes and the Overlap-Group-1 trio, thresholds fixed at 5% false-Unknown on the
known threshold half of block-grouped validation. Files go under results/metrics/xgboost/ with the pool size in the name (open_set_boost_<idea>_<N>f_<kind>.csv).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from pipelines.run_open_set_study import (
    CANDIDATES, INNER_CLASSES, TARGET, OpenSetRun, curve_rows, rotation_specs, source_rows, zero_day_rows, zero_sets_of,
)
from pipelines.run_tier_study import prepare
from src.fpr_methods import apply_temperature, fit_temperature
from src.models.model_factory import create_model
from src.neighbours import exact_twin_mask
from src.openset_extra import (
    KnnScorer, MahalanobisScorer, ensemble_msp, member_variance, per_class_thresholds, predictive_mutual_information, pseudo_unknown_classes,
    relabel_unknown, shift_by_class, zero_day_percentile,
)
from src.openset_scores import RankNormalizer, combine, unknown_auroc
from src.preprocessing import Preprocessor, balanced_sample_weight
from src.utils.config_loader import get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

PARTS = ("cal", "thr", "test", "unknown")


def parts_of(run: OpenSetRun) -> list[str]:
    """The parts this run has (the inner pseudo-unknown runs have no official-test part)."""
    return [p for p in PARTS if p in run.parts]
SCORE_NAMES = {"calibration": ["msp_cal", "entropy_cal"], "perclass": ["msp_pc", "entropy_pc"], "ensemble": ["ens_mi", "ens_var", "ens_msp"],
               "distance": ["knn", "maha"], "oe": ["oe_pu", "oe_msp"]}
BASELINES = ["msp", "entropy"]
ELIGIBLE = ["msp", "entropy", "msp_cal", "entropy_cal", "ens_mi", "ens_var", "ens_msp", "knn", "maha", "oe_pu"]    # the individual scores the combination may use
MEMBER = {"subsample": 0.7, "colsample_bytree": 0.7, "n_estimators": 150, "learning_rate": 0.2}
ENSEMBLE_SIZE, KNN_K, KNN_REFERENCE = 5, 10, 20000
WORMS_SHELLCODE = ("Worms + Shellcode", ["Worms", "Shellcode"])


def specs_for(names: list[str] | None = None) -> list[tuple[str, list[str]]]:
    """The held-out sets: Worms + Shellcode, the nine rotation classes and the trio (or the subset named in `names`)."""
    every = [WORMS_SHELLCODE, *rotation_specs()]
    return every if not names else [s for s in every if s[0] in names]


# ---------------------------------------------------------------- the scores
def add_calibration(run: OpenSetRun) -> dict:
    """msp / entropy of the temperature-scaled probabilities (T fitted on the CALIBRATION half). Returns T and the ECE of the known test flows before and after."""
    from src.evaluation.metrics import expected_calibration_error
    from src.openset_scores import entropy_score, msp_score
    cal = run.parts["cal"]
    temperature = fit_temperature(cal["p"], cal["y"])
    for part in parts_of(run):
        p = apply_temperature(run.parts[part]["p"], temperature)
        run.parts[part]["p_cal"] = p
        run.parts[part]["scores"]["msp_cal"], run.parts[part]["scores"]["entropy_cal"] = msp_score(p), entropy_score(p)
    if "test" not in run.parts:
        return {"temperature": temperature}
    test = run.parts["test"]
    bins = run.cfg["evaluation"]["ece_bins"]
    return {"temperature": temperature, "ece_before": expected_calibration_error(test["y"], test["p"], bins), "ece_after": expected_calibration_error(test["y"], test["p_cal"], bins)}


def add_per_class(run: OpenSetRun, bases=("msp", "entropy")) -> None:
    """Per-predicted-class thresholds on the base scores: the score `<base>_pc` is the base score minus its predicted class's 5% threshold (above 0 = flagged); the flag rule
    for any target is the per-class (1 - target) quantile of the known threshold half."""
    K = len(run.classes)
    thr_part = run.parts["thr"]
    for base in bases:
        name = f"{base}_pc"
        at_target = per_class_thresholds(thr_part["scores"][base], thr_part["pred"], K, TARGET)
        for part in parts_of(run):
            run.parts[part]["scores"][name] = shift_by_class(run.parts[part]["scores"][base], run.parts[part]["pred"], at_target)

        def flagger(part, target, base=base):
            thresholds = per_class_thresholds(thr_part["scores"][base], thr_part["pred"], K, target)
            return run.parts[part]["scores"][base] > thresholds[run.parts[part]["pred"]]
        run.flaggers[name] = flagger


def add_ensemble(run: OpenSetRun, seed: int) -> None:
    """Ensemble disagreement: the main model plus ENSEMBLE_SIZE - 1 members (other seeds, row / column subsampling, smaller and faster), same classes, weights and preprocessing."""
    cfg = run.cfg
    power = cfg["model"].get("class_weight_power", 0.5)
    weights = balanced_sample_weight(run.y_train, power)
    members = []
    for j in range(1, ENSEMBLE_SIZE):
        params = {**cfg["model"]["params"], **MEMBER, "random_state": seed + 100 * j}
        members.append(create_model(cfg["model"]["type"], params).fit(run.X_train, run.y_train, sample_weight=weights))
    for part in parts_of(run):
        stack = np.stack([run.parts[part]["p"], *[m.predict_proba(run.parts[part]["X"]) for m in members]])
        run.parts[part]["scores"].update(ens_mi=predictive_mutual_information(stack), ens_var=member_variance(stack), ens_msp=ensemble_msp(stack))


def add_distance(run: OpenSetRun, seed: int) -> None:
    knn = KnnScorer(KNN_K, KNN_REFERENCE, seed).fit(run.X_train)
    maha = MahalanobisScorer().fit(run.X_train, run.y_train)
    for part in parts_of(run):
        run.parts[part]["scores"]["knn"] = knn.score(run.parts[part]["X"])
        run.parts[part]["scores"]["maha"] = maha.score(run.parts[part]["X"])


def known_macro_recall(predicted_labels: np.ndarray, true_labels: np.ndarray, classes: list[str]) -> float:
    """Macro recall over `classes` (a flow predicted as a label outside `classes`, e.g. Unknown, counts as missed); classes without rows are skipped."""
    recalls = [float((predicted_labels[true_labels == c] == c).mean()) for c in classes if (true_labels == c).any()]
    return float(np.mean(recalls))


def build_oe_run(cfg: dict, splits, features: list[str], seed: int, held_out: list[str]) -> tuple[OpenSetRun, dict]:
    """The outlier-exposure comparison. P = the pseudo-unknown classes (two known classes, never a held-out one) are removed from the known train / validation / test sets of the
    baseline run (`noP`, a closed-set model trained without them) and, in the Unknown-class model, relabelled as the training class "Unknown". Scores `oe_pu` = P(Unknown) and
    `oe_msp` = 1 - max probability of the Unknown-class model are added to the noP run, so every score is evaluated on the same known flows. Returns (run, diagnostics)."""
    target, fine = cfg["data"]["target_column"], cfg["data"]["fine_grained_target_column"]
    pseudo = pseudo_unknown_classes(held_out)
    drop = lambda df: df[~df[fine].isin(pseudo)].reset_index(drop=True)   # noqa: E731
    run = OpenSetRun(cfg, drop(splits.train), drop(splits.val), drop(splits.test), splits.unknown, features, seed)
    train_oe = relabel_unknown(splits.train, pseudo, target, fine)
    pre = Preprocessor(feature_list=features, target_column=target).fit(train_oe)
    X, y = pre.transform(train_oe)
    model = create_model(cfg["model"]["type"], cfg["model"]["params"]).fit(X, y, sample_weight=balanced_sample_weight(y, cfg["model"].get("class_weight_power", 0.5)))
    classes = list(pre.target_encoder.classes_)
    unknown_index = classes.index("Unknown")
    frames = {**run.frames, "unknown": run.unknown_df}
    probas = {part: model.predict_proba(pre.transform_features(frame)) for part, frame in frames.items()}
    for part in parts_of(run):
        run.parts[part]["scores"]["oe_pu"] = probas[part][:, unknown_index]
        run.parts[part]["scores"]["oe_msp"] = 1.0 - probas[part].max(axis=1)
    test_true = run.frames["test"][target].to_numpy()
    known = list(run.classes)
    diagnostics = {"pseudo_unknown_classes": "+".join(pseudo),
                   "known_macro_recall_noP": known_macro_recall(np.asarray(run.classes)[run.parts["test"]["pred"]], test_true, known),
                   "known_macro_recall_oe": known_macro_recall(np.asarray(classes)[probas["test"].argmax(axis=1)], test_true, known),
                   "oe_predicts_unknown_on_known_test": float((probas["test"].argmax(axis=1) == unknown_index).mean())}
    return run, diagnostics


# ---------------------------------------------------------------- rows
def composition_rows(run: OpenSetRun, pool: str, seed: int, held_name: str, names: list[str]) -> list[dict]:
    """Composition of the flagged-Unknown bucket on the official test at the 5% target: for each score, how many flows of each known class (and Normal) and of each zero-day class
    are flagged, out of how many there are, and the precision of Unknown (zero-day share of the flagged flows)."""
    rows = []
    fine_known, fine_unknown = run.frames["test"]["attack_cat"].to_numpy(), run.unknown_df["attack_cat"].to_numpy()
    for name in names:
        flag_known, flag_unknown = run.flags(name, "test"), run.flags(name, "unknown")
        precision = float(flag_unknown.sum() / max(flag_unknown.sum() + flag_known.sum(), 1))
        for bucket, labels, flags, kind in [(c, fine_known, flag_known, "known") for c in sorted(set(fine_known))] + [(c, fine_unknown, flag_unknown, "zero-day") for c in sorted(set(fine_unknown))]:
            rows.append({"pool": pool, "seed": seed, "held_out": held_name, "score": name, "bucket": bucket, "kind": kind, "n_total": int((labels == bucket).sum()),
                         "n_flagged": int(flags[labels == bucket].sum()), "unknown_precision": precision})
    return rows


def iforest_rows(run: OpenSetRun, pool: str, seed: int) -> list[dict]:
    """Sign check of the isolation-forest score (and of the distance scores): AUROC of the score for known attacks against known Normal flows on the official test (above 0.5 =
    the score ranks attacks as more anomalous than Normal), and the mean percentile of each zero-day class among the known test scores (above 0.5 = more anomalous than a typical flow)."""
    fine = run.frames["test"]["attack_cat"].to_numpy()
    is_attack = fine != run.normal
    rows = []
    for name in [n for n in ("iforest", "knn", "maha") if n in run.parts["test"]["scores"]]:
        known, unknown = run.parts["test"]["scores"][name], run.parts["unknown"]["scores"][name]
        row = {"pool": pool, "seed": seed, "score": name, "attack_vs_normal_auroc": float(roc_auc_score(is_attack, known)), "known_median": float(np.median(known))}
        for cls in sorted(set(run.unknown_df["attack_cat"])):
            row[f"percentile_{cls}"] = zero_day_percentile(known, unknown[(run.unknown_df["attack_cat"] == cls).to_numpy()])
        rows.append(row)
    return rows


# ---------------------------------------------------------------- the runner
def prepare_run(config: dict, feature_sets: dict, pool: str, seed: int, held: list[str]):
    cfg = {**config, "data": {**config["data"], "unknown_attack_categories": held}}
    cfg, sets, splits = prepare(cfg, feature_sets, pool, "xgboost", seed)
    return cfg, sets, splits, list(sets["feature_pool"])


def run_idea(config: dict, feature_sets: dict, pool: str, idea: str, seeds, specs, save=None) -> dict[str, pd.DataFrame]:
    """One idea over every held-out set and seed. Rows: `runs` (per score and zero-day set), `diagnostics` (per run: temperature / ECE, ensemble-free, outlier-exposure recall cost),
    and for Worms + Shellcode the review-queue `curve` and the flagged-bucket `composition`."""
    runs, curve, composition, diagnostics, checks = [], [], [], [], []
    names = [*BASELINES, *SCORE_NAMES.get(idea, [])] if idea != "iforest" else ["msp"]
    for held_name, held in specs:
        for seed in seeds:
            cfg, sets, splits, features = prepare_run(config, feature_sets, pool, seed, held)
            label = pool_label(sets)
            extra = {}
            if idea == "oe":
                run, extra = build_oe_run(cfg, splits, features, seed, held)
                run_names = [*BASELINES, *SCORE_NAMES["oe"]]
            else:
                run = OpenSetRun(cfg, splits.train, splits.val, splits.test, splits.unknown, features, seed)
                run_names = names
                if idea == "calibration":
                    extra = add_calibration(run)
                elif idea == "perclass":
                    add_per_class(run)
                elif idea == "ensemble":
                    add_ensemble(run, seed)
                elif idea == "distance":
                    add_distance(run, seed)
                elif idea == "iforest":
                    add_distance(run, seed)
                    checks += [{**r, "held_out": held_name} for r in iforest_rows(run, label, seed)]
            sets_of_zero = zero_sets_of(splits.unknown) if held_name == WORMS_SHELLCODE[0] else {held_name: np.ones(len(splits.unknown), bool)}
            twin = float(exact_twin_mask(splits.unknown, pd.concat([splits.train, splits.val, splits.test], ignore_index=True), features).mean())
            rows = zero_day_rows(run, label, seed, sets_of_zero, run_names)
            rename = {"msp": "noP_msp", "entropy": "noP_entropy"} if idea == "oe" else {}
            runs += [{**r, "score": rename.get(r["score"], r["score"]), "held_out": held_name, "exact_twin_share_in_known": twin} for r in rows]
            if extra:
                diagnostics.append({"pool": label, "seed": seed, "held_out": held_name, **extra})
            if held_name == WORMS_SHELLCODE[0]:
                curve += [{**r, "score": rename.get(r["score"], r["score"])} for r in curve_rows(run, label, seed, run_names)]
                composition += [{**r, "score": rename.get(r["score"], r["score"])} for r in composition_rows(run, label, seed, held_name, run_names)]
            logger.info(f"[boost {idea} {label}] held out {held_name} seed={seed} done")
        if save:
            save(pd.DataFrame(runs), pd.DataFrame(curve), pd.DataFrame(composition), pd.DataFrame(diagnostics), pd.DataFrame(checks))   # partial results after every held-out set
    return {"runs": pd.DataFrame(runs), "curve": pd.DataFrame(curve), "composition": pd.DataFrame(composition), "diagnostics": pd.DataFrame(diagnostics),
            "checks": pd.DataFrame(checks)}


# ---------------------------------------------------------------- one pass over several ideas
PASS_IDEAS = ("calibration", "perclass", "ensemble", "distance")


def run_pass(config: dict, feature_sets: dict, pool: str, seeds, specs, selection: pd.DataFrame | None = None, save=None) -> dict[str, dict[str, pd.DataFrame]]:
    """Ideas 1-4 (and the combination when `selection` is given and its two scores need no Unknown-class model) from ONE base model per held-out set and seed: the closed-set
    classifier and its Task 4 score suite are fitted once, every extra score is added to it, and the rows are split into one table set per idea (each idea's table also carries
    the `msp` and `entropy` baselines of the same runs). Returns {idea: {"runs", "curve", "composition", "diagnostics", "checks"}}; `iforest` holds the sign check."""
    chosen = top_two(selection) if selection is not None else None
    combo_here = chosen is not None and not any(n.startswith("oe_") for n in chosen)
    wanted = {i: list(dict.fromkeys([*BASELINES, *SCORE_NAMES[i]])) for i in PASS_IDEAS}
    if combo_here:
        wanted["combo"] = list(dict.fromkeys([*BASELINES, *chosen, "combo"]))
    every = list(dict.fromkeys(n for names in wanted.values() for n in names))
    kinds = ("runs", "curve", "composition", "diagnostics", "checks")
    out = {i: {k: [] for k in kinds} for i in (*wanted, "iforest")}
    for held_name, held in specs:
        for seed in seeds:
            cfg, sets, splits, features = prepare_run(config, feature_sets, pool, seed, held)
            label = pool_label(sets)
            run = OpenSetRun(cfg, splits.train, splits.val, splits.test, splits.unknown, features, seed)
            calibration = add_calibration(run)
            add_per_class(run)
            add_ensemble(run, seed)
            add_distance(run, seed)
            if combo_here:
                add_combination(run, chosen)
            is_ws = held_name == WORMS_SHELLCODE[0]
            zero = zero_sets_of(splits.unknown) if is_ws else {held_name: np.ones(len(splits.unknown), bool)}
            twin = float(exact_twin_mask(splits.unknown, pd.concat([splits.train, splits.val, splits.test], ignore_index=True), features).mean())
            rows = [{**r, "held_out": held_name, "exact_twin_share_in_known": twin, **({"combo_of": "+".join(chosen)} if combo_here else {})} for r in zero_day_rows(run, label, seed, zero, every)]
            curve = curve_rows(run, label, seed, every) if is_ws else []
            composition = composition_rows(run, label, seed, held_name, every) if is_ws else []
            for idea, names in wanted.items():
                out[idea]["runs"] += [r for r in rows if r["score"] in names]
                out[idea]["curve"] += [r for r in curve if r["score"] in names]
                out[idea]["composition"] += [r for r in composition if r["score"] in names]
            out["calibration"]["diagnostics"].append({"pool": label, "seed": seed, "held_out": held_name, **calibration})
            out["iforest"]["checks"] += [{**r, "held_out": held_name} for r in iforest_rows(run, label, seed)]
            logger.info(f"[boost pass {label}] held out {held_name} seed={seed} done")
        if save:
            save({idea: {k: pd.DataFrame(v) for k, v in t.items()} for idea, t in out.items()})   # partial results after every held-out set
    return {idea: {k: pd.DataFrame(v) for k, v in t.items()} for idea, t in out.items()}


# ---------------------------------------------------------------- selection and combination
def inner_scores(config: dict, feature_sets: dict, pool: str, seed: int, x_class: str) -> tuple[str, dict[str, tuple[np.ndarray, np.ndarray]]]:
    """Every eligible score on an inner model trained without `x_class`: {score: (known threshold-half scores, pseudo-unknown scores)} (pseudo-unknowns = the validation flows of x_class)."""
    cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
    features, fine = list(sets["feature_pool"]), cfg["data"]["fine_grained_target_column"]
    train, val = splits.train[splits.train[fine] != x_class], splits.val
    known_val, pseudo = val[val[fine] != x_class].reset_index(drop=True), val[val[fine] == x_class].reset_index(drop=True)
    run = OpenSetRun(cfg, train, known_val, None, pseudo, features, seed)
    add_calibration(run)
    add_ensemble(run, seed)
    add_distance(run, seed)
    out = {n: (run.parts["thr"]["scores"][n], run.parts["unknown"]["scores"][n]) for n in ELIGIBLE if n in run.parts["thr"]["scores"]}
    # the Unknown-class model: P excludes the inner held-out class by the same rule (its known sets are the inner known validation flows; the test part is not used here)
    inner_splits = SimpleNamespace(train=train, val=known_val, test=known_val, unknown=pseudo)
    oe_run, _ = build_oe_run({**cfg, "data": {**cfg["data"], "unknown_attack_categories": [x_class]}}, inner_splits, features, seed, [x_class])
    out["oe_pu"] = (oe_run.parts["thr"]["scores"]["oe_pu"], oe_run.parts["unknown"]["scores"]["oe_pu"])
    return pool_label(sets), out


def run_selection(config: dict, feature_sets: dict, pool: str, seeds) -> pd.DataFrame:
    rows = []
    for seed in seeds:
        for x_class in INNER_CLASSES:
            label, scores = inner_scores(config, feature_sets, pool, seed, x_class)
            rows += [{"pool": label, "seed": seed, "inner_class": x_class, "score": n, "pseudo_auroc": unknown_auroc(k, u), "n_pseudo": int(len(u))} for n, (k, u) in scores.items()]
            logger.info(f"[boost selection {label}] seed={seed} inner={x_class} done")
    return pd.DataFrame(rows)


def top_two(selection: pd.DataFrame) -> list[str]:
    """The two eligible scores with the highest mean pseudo-unknown AUROC over seeds and inner classes (ties: the order of ELIGIBLE)."""
    mean = selection[selection["score"].isin(ELIGIBLE)].groupby("score")["pseudo_auroc"].mean()
    return sorted(mean.index, key=lambda n: (-mean[n], ELIGIBLE.index(n)))[:2]


def add_combination(run: OpenSetRun, names: list[str]) -> None:
    """`combo` = the mean of the empirical-CDF ranks (fitted on the CALIBRATION half) of the two scores in `names`."""
    rankers = {n: RankNormalizer().fit(run.parts["cal"]["scores"][n]) for n in names}
    for part in parts_of(run):
        ranks = [rankers[n].transform(run.parts[part]["scores"][n]) for n in names]
        run.parts[part]["scores"]["combo"] = combine(ranks[0], ranks[1], "mean")


def run_combo(config: dict, feature_sets: dict, pool: str, seeds, specs, selection: pd.DataFrame, save=None) -> dict[str, pd.DataFrame]:
    """The declared combination on every held-out set. Every score it may use is computed; if it uses the Unknown-class model the known sets lose the pseudo-unknown classes P and the
    comparison is against the closed-set model trained without them (`noP_*`)."""
    chosen = top_two(selection)
    uses_oe = any(n.startswith("oe_") for n in chosen)
    runs, curve, composition, diagnostics = [], [], [], []
    for held_name, held in specs:
        for seed in seeds:
            cfg, sets, splits, features = prepare_run(config, feature_sets, pool, seed, held)
            label = pool_label(sets)
            extra = {}
            if uses_oe:
                run, extra = build_oe_run(cfg, splits, features, seed, held)
            else:
                run = OpenSetRun(cfg, splits.train, splits.val, splits.test, splits.unknown, features, seed)
            add_calibration(run)
            add_ensemble(run, seed)
            add_distance(run, seed)
            add_combination(run, chosen)
            names = list(dict.fromkeys([*BASELINES, *chosen, "combo", *(SCORE_NAMES["oe"] if uses_oe else [])]))   # the Unknown-class scores are recorded too: one pass serves `oe` and `combo`
            sets_of_zero = zero_sets_of(splits.unknown) if held_name == WORMS_SHELLCODE[0] else {held_name: np.ones(len(splits.unknown), bool)}
            rename = {"msp": "noP_msp", "entropy": "noP_entropy"} if uses_oe else {}
            rows = zero_day_rows(run, label, seed, sets_of_zero, names)
            twin = float(exact_twin_mask(splits.unknown, pd.concat([splits.train, splits.val, splits.test], ignore_index=True), features).mean())
            runs += [{**r, "score": rename.get(r["score"], r["score"]), "held_out": held_name, "exact_twin_share_in_known": twin, "combo_of": "+".join(chosen)} for r in rows]
            diagnostics.append({"pool": label, "seed": seed, "held_out": held_name, "combo_of": "+".join(chosen), **extra})
            if held_name == WORMS_SHELLCODE[0]:
                curve += [{**r, "score": rename.get(r["score"], r["score"])} for r in curve_rows(run, label, seed, names)]
                composition += [{**r, "score": rename.get(r["score"], r["score"])} for r in composition_rows(run, label, seed, held_name, names)]
            logger.info(f"[boost combo {label}] held out {held_name} seed={seed} done")
        if save:
            save(pd.DataFrame(runs), pd.DataFrame(curve), pd.DataFrame(composition), pd.DataFrame(diagnostics), pd.DataFrame())
    return {"runs": pd.DataFrame(runs), "curve": pd.DataFrame(curve), "composition": pd.DataFrame(composition), "diagnostics": pd.DataFrame(diagnostics), "checks": pd.DataFrame()}


def split_ideas(tables: dict[str, pd.DataFrame], baselines: list[str], uses_oe: bool, chosen: list[str]) -> dict[str, dict[str, pd.DataFrame]]:
    """From one combination pass the table sets of the two ideas it serves: `combo` (baselines, the two chosen scores and `combo`) and, when the Unknown-class model was used, `oe`
    (baselines, `oe_pu`, `oe_msp`)."""
    keep = {"combo": [*baselines, *chosen, "combo"]}
    if uses_oe:
        keep["oe"] = [*baselines, *SCORE_NAMES["oe"]]
    return {idea: {kind: (df[df["score"].isin(names)] if len(df) and "score" in df else df) for kind, df in tables.items()} for idea, names in keep.items()}


def save_tables(config: dict, idea: str, label: str, tables: dict[str, pd.DataFrame]) -> None:
    d = get_metrics_dir(config)
    d.mkdir(parents=True, exist_ok=True)
    for kind, df in tables.items():
        if len(df):
            df.to_csv(d / f"open_set_boost_{idea}_{label}_{kind}.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--idea", required=True, choices=[*SCORE_NAMES, "selection", "combo", "iforest", "pass"],
                        help="pass = ideas 1-4, the isolation-forest check and (when the selection file exists and needs no Unknown-class model) the combination, from one base model per run")
    parser.add_argument("--pools", nargs="*", default=["base", "full"])
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--specs", nargs="*", help="held-out sets by name (default: Worms + Shellcode, the nine classes and the trio)")
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    seeds = args.seeds or config["tier_study"]["seeds"]
    for pool in args.pools:
        label = pool_label(prepare(config, feature_sets, pool, "xgboost", 42)[1])
        if args.idea == "selection":
            df = run_selection(config, feature_sets, pool, seeds)
            save_tables(config, "selection", label, {"scores": df})
            print(label, "top two:", top_two(df))
            continue
        if args.idea == "pass":
            selection_path = get_metrics_dir(config) / f"open_set_boost_selection_{label}_scores.csv"
            selection = pd.read_csv(selection_path) if selection_path.exists() else None
            def save_all(tables_by_idea: dict, l: str = label) -> None:
                for name, t in tables_by_idea.items():
                    save_tables(config, name, l, t)
            save_all(run_pass(config, feature_sets, pool, seeds, specs_for(args.specs), selection, save_all))
            continue
        if args.idea == "combo":
            selection = pd.read_csv(get_metrics_dir(config) / f"open_set_boost_selection_{label}_scores.csv")
            chosen = top_two(selection)
            uses_oe = any(n.startswith("oe_") for n in chosen)
            baselines = ["noP_msp", "noP_entropy"] if uses_oe else BASELINES
            def save_combo(r, c, k, d, ch, l=label) -> None:
                for name, t in split_ideas({"runs": r, "curve": c, "composition": k, "diagnostics": d, "checks": ch}, baselines, uses_oe, chosen).items():
                    save_tables(config, name, l, t)
            save_combo(*[v for v in run_combo(config, feature_sets, pool, seeds, specs_for(args.specs), selection, save_combo).values()])
            continue
        save = lambda r, c, k, d, ch, i=args.idea, l=label: save_tables(config, i, l, {"runs": r, "curve": c, "composition": k, "diagnostics": d, "checks": ch})   # noqa: E731
        tables = run_idea(config, feature_sets, pool, args.idea, seeds, specs_for(args.specs), save)
        save_tables(config, args.idea, label, tables)


if __name__ == "__main__":
    main()
