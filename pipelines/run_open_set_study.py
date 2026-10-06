"""Open-set / zero-day detection under an honest protocol (protocol: results/02_novelty1_open_set.md, section `Source: open_set_protocol.md`). XGBoost, flat model, official split, ZERO-SHOT.

    python pipelines/run_open_set_study.py --step scores   [--pools full base full_no_ttl]   (default: full) [--seeds 42 43 44 45 46]
    python pipelines/run_open_set_study.py --step rotation [--pools full base]   (default: the primary pool 48 only)
    python pipelines/run_open_set_study.py --step ablation

scores    Step 1 (+ the data for Steps 3 and 4): every candidate score (msp, entropy, margin, conformal, iforest and the iforest combinations) with the threshold fixed on the
          THRESHOLD half of the block-grouped known validation flows at 5% false-Unknown; unknown AUROC / detection on the zero-day flows (Worms + Shellcode, and each separately),
          the realised false-Unknown rate on both validation halves and on the official test, the review-queue curve and the known classes the false alarms come from. The combination
          rule and the best score are chosen on PSEUDO-UNKNOWNS (validation flows of Reconnaissance and Generic, with an inner model trained without that class), never on the zero-day flows.
rotation  Step 2: each attack class (and the Overlap-Group-1 trio as a unit) is held out in turn, the model retrained without it, the threshold fixed on known validation at 5%.
ablation  Step 4: the Step 1 protocol on 48 features without the window-count ct_* columns, without any ct_* column, and the 30- and 15-feature tiers of the 48 pool.

Files go under results/metrics/xgboost/ with the pool size in the name (open_set_<kind>_<N>f[...].csv).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from pipelines.run_tier_study import prepare
from src.models.model_factory import create_model
from src.neighbours import exact_twin_mask
from src.openset_extra import matched_detection
from src.openset_scores import BASE_SCORES, RULES, ScoreSuite, flag_threshold, unknown_auroc
from src.preprocessing import Preprocessor, balanced_sample_weight
from src.utils.config_loader import get_active_features, get_metrics_dir, load_config, load_feature_sets, pool_label, require_xgboost, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

TARGET = 0.05
CURVE_TARGETS = (0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30)
INNER_CLASSES = ("Reconnaissance", "Generic")
ROTATION_CLASSES = ["Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic", "Reconnaissance", "Worms", "Shellcode"]
GROUP = ["Analysis", "Backdoor", "DoS"]
CANDIDATES = [*BASE_SCORES, "iforest", *(f"iforest+{b}:{r}" for b in BASE_SCORES for r in RULES)]


def fit_closed_set(cfg: dict, train_df: pd.DataFrame, features: list[str]):
    """(preprocessor, model, X_train, y_train): the closed-set classifier exactly as train_and_evaluate builds it (class weights balanced ** class_weight_power)."""
    pre = Preprocessor(feature_list=features, target_column=cfg["data"]["target_column"]).fit(train_df)
    X, y = pre.transform(train_df)
    model = create_model(cfg["model"]["type"], cfg["model"]["params"]).fit(X, y, sample_weight=balanced_sample_weight(y, cfg["model"].get("class_weight_power", 0.5)))
    return pre, model, X, y


def validation_halves(val_df: pd.DataFrame, block_size: int, seed: int) -> np.ndarray:
    """Boolean mask of the CALIBRATION half of the validation rows: whole blocks (row index // block_size) are assigned at random, half to calibration and half to the
    threshold, so the two halves are disjoint."""
    groups = np.arange(len(val_df)) // block_size
    ids = np.unique(groups)
    cal_groups = np.random.default_rng(seed).permutation(ids)[: len(ids) // 2]
    return np.isin(groups, cal_groups)


class OpenSetRun:
    """One fitted configuration: the classifier, the score suite and every candidate score on the validation halves, the known test flows (when given) and the unknown flows.
    Thresholds and calibration only ever see the known validation halves and the Normal training flows."""

    def __init__(self, cfg: dict, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame | None, unknown_df: pd.DataFrame, features: list[str], seed: int):
        self.cfg, self.seed = cfg, seed
        self.normal = cfg["data"]["normal_category"]
        self.pre, self.model, X_train, y_train = fit_closed_set(cfg, train_df, features)
        self.X_train, self.y_train, self.train_df, self.features = X_train, y_train, train_df, features   # kept for the open-set boost study scores (distance, ensemble, outlier exposure)
        self.flaggers = {}   # name -> f(part, target) -> boolean flags, for rules that are not one threshold on one score (per-class thresholds)
        self.classes = list(self.pre.target_encoder.classes_)
        self.normal_index = self.classes.index(self.normal)
        cal_mask = validation_halves(val_df, cfg["tier_study"]["block_size"], seed)
        frames = {"cal": val_df[cal_mask].reset_index(drop=True), "thr": val_df[~cal_mask].reset_index(drop=True)}
        if test_df is not None:
            frames["test"] = test_df
        self.frames, self.parts = frames, {}
        for name, df in frames.items():
            X, y = self.pre.transform(df)
            self.parts[name] = {"X": X, "y": y, "p": self.model.predict_proba(X)}
        Xu = self.pre.transform_features(unknown_df)
        self.parts["unknown"] = {"X": Xu, "y": None, "p": self.model.predict_proba(Xu)}
        self.unknown_df = unknown_df
        self.suite = ScoreSuite(seed).fit(self.parts["cal"]["p"], self.parts["cal"]["y"], self.parts["cal"]["X"], X_train[y_train == self.normal_index])
        for part in self.parts.values():
            part["scores"] = self.suite.scores(part["p"], part["X"])
            part["pred"] = part["p"].argmax(axis=1)

    def threshold(self, name: str, target: float = TARGET) -> float:
        return flag_threshold(self.parts["thr"]["scores"][name], target)

    def flags(self, name: str, part: str, target: float = TARGET) -> np.ndarray:
        """Boolean "flagged Unknown" of every flow of `part`: one threshold on the score fixed on the known threshold half, or the registered per-name rule."""
        if name in self.flaggers:
            return self.flaggers[name](part, target)
        return self.parts[part]["scores"][name] > self.threshold(name, target)


def zero_day_rows(run: OpenSetRun, pool: str, seed: int, zero_sets: dict[str, np.ndarray], names=CANDIDATES) -> list[dict]:
    """Step 1 / 2 rows: per candidate score and zero-day set, unknown AUROC, detection at the 5% threshold, share flagged OR predicted as an attack class, and the realised
    false-Unknown rate on the two validation halves and on the official test."""
    rows = []
    msp_test_rate = float(run.flags("msp", "test").mean()) if "msp" in run.parts["test"]["scores"] else float("nan")
    for name in names:
        thr = float("nan") if name in run.flaggers else run.threshold(name)
        known_test = run.parts["test"]["scores"][name]
        flagged_unknown = run.flags(name, "unknown")
        for zero_name, mask in zero_sets.items():
            s = run.parts["unknown"]["scores"][name][mask]
            attack_pred = run.parts["unknown"]["pred"][mask] != run.normal_index
            rows.append({"pool": pool, "seed": seed, "score": name, "zero_day": zero_name, "n_zero_day": int(mask.sum()), "threshold": thr,
                         "unknown_auroc": unknown_auroc(known_test, s), "detection": float(flagged_unknown[mask].mean()),
                         "flagged_or_attack": float((flagged_unknown[mask] | attack_pred).mean()),
                         "false_unknown_thr_half": float(run.flags(name, "thr").mean()), "false_unknown_cal_half": float(run.flags(name, "cal").mean()),
                         "false_unknown_test": float(run.flags(name, "test").mean()),
                         "msp_false_unknown_test": msp_test_rate,   # diagnostic: detection at the threshold that flags the same share of known test flows as max-softmax did
                         "detection_matched_to_msp": matched_detection(known_test, s, msp_test_rate) if msp_test_rate == msp_test_rate else float("nan")})
    return rows


def source_rows(run: OpenSetRun, pool: str, seed: int, names) -> list[dict]:
    """Which known classes the false-Unknown alarms come from: per score, validation half or test, original class: flows, the share of that class flagged, and its share
    of all false alarms."""
    rows = []
    for name in names:
        for part in ("thr", "cal", "test"):
            flagged = run.flags(name, part)
            fine = run.frames[part]["attack_cat"].to_numpy()
            for cls in sorted(set(fine)):
                m = fine == cls
                rows.append({"pool": pool, "seed": seed, "score": name, "part": part, "known_class": cls, "n": int(m.sum()), "flagged_share": float(flagged[m].mean()),
                             "share_of_false_alarms": float(flagged[m].sum() / max(flagged.sum(), 1))})
    return rows


def curve_rows(run: OpenSetRun, pool: str, seed: int, names=CANDIDATES) -> list[dict]:
    """Review-queue curve (Step 3): for each false-Unknown target the threshold comes from the known threshold half; on the official test Normal flows we report the alert FPR with
    the open-set wrapper OFF (any attack class) and ON (attack class or Unknown), the confident-alert FPR (called an attack and NOT sent to review), the review rate and what
    it removes; for zero-day flows the catch rate (flagged or called an attack); for known attacks the alert / confident detection."""
    test, unk, normal = run.parts["test"], run.parts["unknown"], run.normal_index
    is_normal = test["y"] == normal
    called = test["pred"] != normal
    rows = []
    for name in names:
        for target in CURVE_TARGETS:
            thr = float("nan") if name in run.flaggers else run.threshold(name, target)
            flag, flag_u = run.flags(name, "test", target), run.flags(name, "unknown", target)
            off = float(called[is_normal].mean())
            conf = float((called & ~flag)[is_normal].mean())
            rows.append({"pool": pool, "seed": seed, "score": name, "target": target, "threshold": thr,
                         "alert_fpr_off": off, "alert_fpr_on": float((called | flag)[is_normal].mean()), "confident_alert_fpr": conf,
                         "review_rate_normal": float(flag[is_normal].mean()), "normal_called_normal_but_reviewed": float((~called & flag)[is_normal].mean()),
                         "share_of_false_alerts_that_skip_review": conf / off if off else float("nan"),
                         "zero_day_catch": float((flag_u | (unk["pred"] != normal)).mean()), "zero_day_flagged": float(flag_u.mean()),
                         "known_attack_alert_rate": float((called | flag)[~is_normal].mean()), "known_attack_confident_detection": float((called & ~flag)[~is_normal].mean())})
    return rows


def pseudo_unknown_rows(cfg: dict, train_df: pd.DataFrame, val_df: pd.DataFrame, features: list[str], seed: int, pool: str) -> list[dict]:
    """Choose the combination rule and the best score on VALIDATION: for each inner class X an inner model is trained without X; the validation flows of X are the pseudo-unknowns
    and the other known validation flows (threshold half) the knowns; the AUROC of each candidate is the selection criterion. No zero-day flow and no test label is used."""
    rows = []
    for x_class in INNER_CLASSES:
        known_val, pseudo = val_df[val_df["attack_cat"] != x_class], val_df[val_df["attack_cat"] == x_class]
        inner = OpenSetRun(cfg, train_df[train_df["attack_cat"] != x_class], known_val.reset_index(drop=True), None, pseudo.reset_index(drop=True), features, seed)
        known_scores, pseudo_scores = inner.parts["thr"]["scores"], inner.parts["unknown"]["scores"]
        rows += [{"pool": pool, "seed": seed, "inner_class": x_class, "score": name, "pseudo_auroc": unknown_auroc(known_scores[name], pseudo_scores[name]),
                  "n_pseudo": len(pseudo)} for name in CANDIDATES]
    return rows


def pool_selection(selection: pd.DataFrame) -> dict:
    """From the pseudo-unknown table of ONE pool/label: the rule per base score (the rule whose combination has the higher mean pseudo-unknown AUROC over seeds and inner
    classes) and the best score among {base scores, iforest, the combinations with their chosen rule} by the same criterion."""
    mean = selection.groupby("score")["pseudo_auroc"].mean()
    rules = {b: max(RULES, key=lambda r: mean[f"iforest+{b}:{r}"]) for b in BASE_SCORES}
    chosen = [*BASE_SCORES, "iforest", *(f"iforest+{b}:{rules[b]}" for b in BASE_SCORES)]
    return {"rules": rules, "candidates": chosen, "best": max(chosen, key=lambda n: mean[n]), "mean_pseudo_auroc": {n: float(mean[n]) for n in chosen}}


def zero_sets_of(unknown_df: pd.DataFrame) -> dict[str, np.ndarray]:
    sets = {"+".join(sorted(set(unknown_df["attack_cat"]))): np.ones(len(unknown_df), bool)}
    for cls in sorted(set(unknown_df["attack_cat"])):
        if len(set(unknown_df["attack_cat"])) > 1:
            sets[cls] = (unknown_df["attack_cat"] == cls).to_numpy()
    return sets


def run_scores(config: dict, feature_sets: dict, pool: str, seeds, features_fn=None, label: str | None = None, inner: bool = True) -> dict[str, pd.DataFrame]:
    """Step 1 for one pool (or a feature variant via `features_fn(cfg, sets) -> features`)."""
    scores, selection, curve, sources = [], [], [], []
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        features = features_fn(cfg, sets) if features_fn else list(sets["feature_pool"])
        label = label or pool_label(sets)
        if inner:
            selection += pseudo_unknown_rows(cfg, splits.train, splits.val, features, seed, label)
        run = OpenSetRun(cfg, splits.train, splits.val, splits.test, splits.unknown, features, seed)
        scores += zero_day_rows(run, label, seed, zero_sets_of(splits.unknown))
        curve += curve_rows(run, label, seed)
        sources += source_rows(run, label, seed, CANDIDATES)
        logger.info(f"[open-set scores {label}] seed={seed} done")
    return {"runs": pd.DataFrame(scores), "selection": pd.DataFrame(selection), "curve": pd.DataFrame(curve), "sources": pd.DataFrame(sources)}


def rotation_specs(classes=None) -> list[tuple[str, list[str]]]:
    specs = [(c, [c]) for c in (classes or ROTATION_CLASSES)]
    if classes is None:
        specs.append(("Overlap-Group-1 (all three)", list(GROUP)))
    return specs


def run_rotation(config: dict, feature_sets: dict, pool: str, seeds, names=CANDIDATES, classes=None) -> dict[str, pd.DataFrame]:
    """Step 2: for each held-out class (or the trio) retrain without it, threshold on known validation at 5%, score it as the zero-day set. Every candidate score is recorded
    (`names`); the summary shows the pool's validation-selected score, max-softmax and any other score of interest."""
    rows, sources = [], []
    for held_name, held in rotation_specs(classes):
        for seed in seeds:
            cfg = {**config, "data": {**config["data"], "unknown_attack_categories": held}}
            cfg, sets, splits = prepare(cfg, feature_sets, pool, "xgboost", seed)
            features = list(sets["feature_pool"])
            run = OpenSetRun(cfg, splits.train, splits.val, splits.test, splits.unknown, features, seed)
            known = pd.concat([splits.train, splits.val, splits.test], ignore_index=True)
            twin = float(exact_twin_mask(splits.unknown, known, features).mean())
            for r in zero_day_rows(run, pool_label(sets), seed, {held_name: np.ones(len(splits.unknown), bool)}, names):
                rows.append({**r, "held_out": held_name, "exact_twin_share_in_known": twin})
            sources += [{**r, "held_out": held_name} for r in source_rows(run, pool_label(sets), seed, names)]
            logger.info(f"[open-set rotation {pool_label(sets)}] held out {held_name} seed={seed} done")
    return {"runs": pd.DataFrame(rows), "sources": pd.DataFrame(sources)}


def save_tables(config: dict, kind: str, label: str, tables: dict[str, pd.DataFrame]) -> None:
    d = get_metrics_dir(config)
    d.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        if len(df):
            df.to_csv(d / f"open_set_{kind}_{label}_{name}.csv" if kind != "scores" else d / f"open_set_{name}_{label}.csv", index=False)


def selection_for(config: dict, label: str) -> dict:
    """The declared per-pool choice (rules and best score) from the saved pseudo-unknown table of Step 1."""
    return pool_selection(pd.read_csv(get_metrics_dir(config) / f"open_set_selection_{label}.csv"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--step", choices=["scores", "rotation", "ablation"], required=True)
    parser.add_argument("--pools", nargs="*")
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--classes", nargs="*", help="rotation: held-out classes (default: all nine plus the trio)")
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    require_xgboost(config, "the open-set study")
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    seeds = args.seeds or config["tier_study"]["seeds"]
    if args.step == "scores":
        for pool in args.pools or config["tier_study"]["pools"]:
            tables = run_scores(config, feature_sets, pool, seeds)
            save_tables(config, "scores", tables["runs"]["pool"].iloc[0], tables)
    elif args.step == "rotation":
        for pool in args.pools or ["full"]:
            label = pool_label(prepare(config, feature_sets, pool, "xgboost", 42)[1])
            tables = run_rotation(config, feature_sets, pool, seeds, CANDIDATES, args.classes)
            save_tables(config, "rotation", label, tables)
    else:  # ablation: 48 features without ct_* columns, and the 30 / 15 tiers
        variants = [("full_no_ct_window", None, None), ("full_no_ct_any", None, None), ("full", "30", "48f_t30"), ("full", "15", "48f_t15")]
        for pool, tier, label in variants:
            fn = (lambda cfg, sets, t=tier: get_active_features(cfg, sets, t)) if tier else None
            tables = run_scores(config, feature_sets, pool, seeds, features_fn=fn, label=label)
            save_tables(config, "scores", tables["runs"]["pool"].iloc[0], tables)


if __name__ == "__main__":
    main()
