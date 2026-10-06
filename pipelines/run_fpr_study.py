"""Task 2.7: lower the official-split false-positive rate (protocol: results/06_fpr_and_adaptation.md, section `Source: fpr_reduction_protocol.md`).

    python pipelines/run_fpr_study.py --step tuned    [--pools full base full_no_ttl]   (default: full) [--seeds 42 43 44 45 46]
    python pipelines/run_fpr_study.py --step prior    ...   TRANSDUCTIVE class-prior correction (+ ZERO-SHOT temperature scaling and a zero-shot control)
    python pipelines/run_fpr_study.py --step self     ...   TRANSDUCTIVE self-training
    python pipelines/run_fpr_study.py --step fewshot  [--pools full full_no_ttl full_no_ct_window]   FEW-SHOT label budget x selection strategy

Every run uses the block-grouped validation split of the seed (run_tier_study.prepare) for training / validation, scores the official test file, and chooses its
95%-detection threshold on validation (few-shot: on the held-out half of the labelled sample). One row per (pool, seed, method) with the same columns
(`evaluate_probabilities`), written to results/metrics/xgboost/fpr_study_<step>_<N>f_runs.csv.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score, roc_curve

from pipelines.run_tier_study import prepare
from pipelines.train_pipeline import train_and_evaluate
from pipelines.tune_xgboost import load_tuned
from src.adaptation import adaptation_weights, with_adaptation
from src.evaluation.metrics import attack_rates, expected_calibration_error, select_attack_threshold
from src.fpr_methods import (
    apply_temperature, diverse_selection, em_gate, em_prior, entropy_selection, fit_temperature, mix_selection, prior_correct, pseudo_labels,
    random_selection, weighted_prior,
)
from src.models.open_set_wrapper import select_threshold
from src.neighbours import block_split
from src.preprocessing import balanced_sample_weight
from src.utils.config_loader import get_metrics_dir, load_config, load_feature_sets, pool_label, resolve_path
from src.utils.logger import add_file_logging, get_logger

logger = get_logger(__name__)

SEEDS = (42, 43, 44, 45, 46)
TAU, SELF_FRACTION, SELF_ROUNDS = 0.90, 0.2, 2          # declared in results/06_fpr_and_adaptation.md, section `Source: fpr_reduction_protocol.md`
KS = (100, 250, 500, 1000, 2500, 5000)
STRATEGIES = ("random", "entropy", "diverse", "mix")
FEWSHOT_FRACTION, BLOCK, BUFFER = 0.5, 1000, 200
UNLABELLED_SHARE, ADAPT_SHARE = 0.5, 0.4


def evaluate_probabilities(proba_val: np.ndarray, y_val: np.ndarray, proba_test: np.ndarray, y_test: np.ndarray, normal_index: int, ece_bins: int,
                           proba_unknown: np.ndarray | None = None, threshold: float | None = None) -> dict:
    """The metrics of one set of class probabilities: argmax accuracy / macro F1 / FPR / detection, the 95%-detection operating point (threshold on
    1 - P(Normal) chosen on the validation rows unless `threshold` is given) with its test FPR and detection, the threshold-free FPR at 95% detection, ECE,
    and open-set detection (max-softmax flagged Unknown below the 5%-false-Unknown quantile of the validation confidences; Worms + Shellcode)."""
    y_val, y_test = np.asarray(y_val), np.asarray(y_test)
    val_attack, test_attack = y_val != normal_index, y_test != normal_index
    val_score, test_score = 1 - proba_val[:, normal_index], 1 - proba_test[:, normal_index]
    if threshold is None:
        threshold = select_attack_threshold(val_attack, val_score, target_detection=0.95)
    det, fpr = attack_rates(test_attack, test_score, threshold)
    _, val_fpr = attack_rates(val_attack, val_score, threshold)
    pred = proba_test.argmax(axis=1)
    called = pred != normal_index
    fpr_curve, tpr_curve, _ = roc_curve(test_attack, test_score)
    row = {"accuracy": float((pred == y_test).mean()), "macro_f1": float(f1_score(y_test, pred, average="macro", zero_division=0)),
           "argmax_fpr": float(called[~test_attack].mean()), "argmax_detection": float(called[test_attack].mean()),
           "det95_threshold": float(threshold), "det95_val_fpr": float(val_fpr), "det95_test_fpr": float(fpr), "det95_test_detection": float(det),
           "fpr_at_95_threshold_free": float(fpr_curve[np.searchsorted(tpr_curve, 0.95, side="left")]),
           "ece": expected_calibration_error(y_test, proba_test, ece_bins), "n_eval": int(len(y_test))}
    if proba_unknown is not None and len(proba_unknown):
        cut = select_threshold(proba_val.max(axis=1), 0.05)
        row.update(open_set_detection=float((proba_unknown.max(axis=1) < cut).mean()), open_set_false_unknown_test=float((proba_test.max(axis=1) < cut).mean()))
    return row


def fit_model(cfg: dict, sets: dict, splits, features: list[str], override: dict | None = None) -> SimpleNamespace:
    """Train once (zero-shot unless `splits` carries adaptation rows) and return what every method needs: the model, its probabilities on the validation,
    test and zero-day rows, the encoded labels and the class prior the sample weights imply."""
    cfg = {**cfg, "model": {**cfg["model"], "params": dict(cfg["model"]["params"])}}
    if override:
        cfg["model"]["params"].update(override["params"])
        cfg["model"]["class_weight_power"] = override["class_weight_power"]
    pred = {}
    train_and_evaluate(cfg, sets, str(len(features)), False, splits, False, pred, features=features)
    pre, model = pred["preprocessor"], pred["model"]
    classes = list(pred["class_names"])
    index = {c: i for i, c in enumerate(classes)}
    y_train = pre.transform(splits.train)[1]
    weights = balanced_sample_weight(y_train, cfg["model"].get("class_weight_power", 0.5))
    if splits.adapt_fraction is not None:
        weights = adaptation_weights(weights, splits.train["adapt_flag"].to_numpy(dtype=bool), splits.adapt_fraction)
    return SimpleNamespace(cfg=cfg, sets=sets, splits=splits, features=features, model=model, pre=pre, classes=classes, normal_index=index[cfg["data"]["normal_category"]],
                           proba_val=pred["y_proba_val"], y_val=np.array([index[c] for c in pred["val_labels"]]), proba_test=pred["y_proba"], y_test=pred["y_test"],
                           proba_unknown=model.predict_proba(pre.transform_features(splits.unknown)) if len(splits.unknown) else None,
                           pi_model=weighted_prior(y_train, weights, len(classes)))


def evaluate_fit(fit: SimpleNamespace, rows: np.ndarray | None = None, **kwargs) -> dict:
    rows = np.arange(len(fit.y_test)) if rows is None else rows
    return evaluate_probabilities(fit.proba_val, fit.y_val, fit.proba_test[rows], fit.y_test[rows], fit.normal_index, fit.cfg["evaluation"]["ece_bins"],
                                  fit.proba_unknown, **kwargs)


def base_row(pool_label_: str, seed: int, method: str, access: str, **extra) -> dict:
    return {"pool_label": pool_label_, "seed": seed, "method": method, "access": access, **extra}


# ---------------------------------------------------------------- Step 1: tuned (ZERO-SHOT)
def tuned_overrides(config: dict, label: str) -> dict[str, dict | None]:
    out = {"default": None}
    for tag, kwargs in (("earlier_tuned", {}), ("blockval_tuned", {"block_validation": True})):
        for objective in ("auc", "f1"):
            try:
                params, power = load_tuned(config, label, objective, **kwargs)
            except FileNotFoundError:
                continue      # the earlier (random-validation) search exists for 40 and 48 features only
            out[f"{tag}_{objective}"] = {"params": params, "class_weight_power": power}
    return out


def run_tuned(config: dict, feature_sets: dict, pool: str, seeds=SEEDS) -> pd.DataFrame:
    rows = []
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label = pool_label(sets)
        for method, override in tuned_overrides(config, label).items():
            fit = fit_model(cfg, sets, splits, list(sets["feature_pool"]), override)
            rows.append(base_row(label, seed, method, "zero-shot", **evaluate_fit(fit)))
            logger.info(f"[fpr tuned {label}] seed={seed} {method}: det95_fpr={rows[-1]['det95_test_fpr']:.4f} argmax_fpr={rows[-1]['argmax_fpr']:.4f}")
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Step 2: prior correction
def run_prior(config: dict, feature_sets: dict, pool: str, seeds=SEEDS) -> pd.DataFrame:
    rows = []
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label = pool_label(sets)
        fit = fit_model(cfg, sets, splits, list(sets["feature_pool"]))
        K = len(fit.classes)
        temperature = fit_temperature(fit.proba_val, fit.y_val)
        cal_val, cal_test = apply_temperature(fit.proba_val, temperature), apply_temperature(fit.proba_test, temperature)
        cal_unknown = apply_temperature(fit.proba_unknown, temperature) if fit.proba_unknown is not None else None
        val_prior = np.bincount(fit.y_val, minlength=K) / len(fit.y_val)
        pi_hat = em_prior(cal_test, fit.pi_model)
        true_share = np.bincount(fit.y_test, minlength=K) / len(fit.y_test)
        gate = em_gate(cal_val, fit.y_val, fit.pi_model, seeds=SEEDS)
        diagnostics = {"temperature": temperature, "em_l1_to_true_shares": float(np.abs(pi_hat - true_share).sum()),
                       "model_prior_l1_to_true_shares": float(np.abs(fit.pi_model - true_share).sum()),
                       "val_prior_l1_to_true_shares": float(np.abs(val_prior - true_share).sum()), "em_gate_passes": gate["passes"],
                       "em_gate_l1_error": gate["em_l1_error"], "em_gate_model_prior_distance": gate["model_prior_l1_distance"],
                       **{f"est_share_{c}": float(pi_hat[i]) for i, c in enumerate(fit.classes)}, **{f"true_share_{c}": float(true_share[i]) for i, c in enumerate(fit.classes)}}
        variants = {"default": (fit.proba_val, fit.proba_test, fit.proba_unknown, "zero-shot"),
                    "calibrated": (cal_val, cal_test, cal_unknown, "zero-shot")}
        for name, pi_new, access in (("calibrated_valprior", val_prior, "zero-shot"), ("calibrated_em", pi_hat, "transductive")):
            variants[name] = (prior_correct(cal_val, pi_new, fit.pi_model), prior_correct(cal_test, pi_new, fit.pi_model),
                              prior_correct(cal_unknown, pi_new, fit.pi_model) if cal_unknown is not None else None, access)
        for method, (pv, pt, pu, access) in variants.items():
            metrics = evaluate_probabilities(pv, fit.y_val, pt, fit.y_test, fit.normal_index, cfg["evaluation"]["ece_bins"], pu)
            rows.append(base_row(label, seed, method, access, **metrics, **(diagnostics if method == "calibrated_em" else {})))
        logger.info(f"[fpr prior {label}] seed={seed} T={temperature:.2f} em_l1={diagnostics['em_l1_to_true_shares']:.3f} gate={gate['passes']}")
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Step 3: self-training
def pseudo_rows(frame: pd.DataFrame, positions: np.ndarray, labels: np.ndarray, classes: list[str], target: str, fine: str) -> pd.DataFrame:
    """The rows of `frame` at `positions` labelled with the model's predicted class (both label columns); the true labels are not carried over."""
    out = frame.iloc[positions].copy()
    out[target] = np.asarray(classes)[labels]
    out[fine] = out[target]
    return out


def self_train(cfg: dict, sets: dict, splits, features: list[str], unlabelled_positions: np.ndarray, evaluate_on: str, rounds: int = SELF_ROUNDS,
               tau: float = TAU, fraction: float = SELF_FRACTION) -> list[SimpleNamespace]:
    """Round 0 = the zero-shot model; each next round re-labels the unlabelled rows (`splits.test` or `splits.val` rows at `unlabelled_positions`) with the previous
    model's confident predictions and retrains on train + those rows (weight fraction `fraction`). Not cumulative. Returns the fitted models in order."""
    target, fine = cfg["data"]["target_column"], cfg["data"]["fine_grained_target_column"]
    frame_name = "test" if evaluate_on == "test" else "val"
    fits = [fit_model(cfg, sets, splits, features)]
    for _ in range(rounds):
        previous = fits[-1]
        proba = previous.proba_test if frame_name == "test" else previous.proba_val
        mask, labels = pseudo_labels(proba[unlabelled_positions], tau)
        keep = unlabelled_positions[mask]
        rows = pseudo_rows(getattr(splits, frame_name), keep, labels[mask], previous.classes, target, fine)
        if not len(rows):
            adapted = splits
        else:
            adapted = with_adaptation(splits, rows, splits.test, fraction) if frame_name == "test" else with_val_rows(splits, rows, fraction)
        fits.append(fit_model(cfg, sets, adapted, features))
    return fits


def with_val_rows(splits, rows: pd.DataFrame, fraction: float):
    """`splits` with pseudo-labelled VALIDATION rows added to the training rows (the validation-blocks check of self-training); validation and test are unchanged."""
    from dataclasses import replace
    train = pd.concat([splits.train.assign(adapt_flag=False), rows.assign(adapt_flag=True)], ignore_index=True)
    return replace(splits, train=train, adapt_fraction=fraction)


def reinforcement(positions: np.ndarray, proba: np.ndarray, truth: np.ndarray, normal_index: int, tau: float) -> dict:
    """Diagnostics of one round's pseudo-labels (true labels used to REPORT only): share of pseudo-labelled rows that are wrong, share of true Normal rows that get a
    confident attack pseudo-label, and the share of confident attack pseudo-labels that are truly Normal."""
    mask, labels = pseudo_labels(proba[positions], tau)
    t = truth[positions]
    confident_attack = mask & (labels != normal_index)
    return {"pseudo_labelled": int(mask.sum()), "pseudo_wrong_share": float((labels[mask] != t[mask]).mean()) if mask.any() else float("nan"),
            "true_normal_given_attack_pseudo_label": float(confident_attack[t == normal_index].mean()) if (t == normal_index).any() else float("nan"),
            "attack_pseudo_labels_that_are_normal": float((t[confident_attack] == normal_index).mean()) if confident_attack.any() else float("nan")}


def run_self(config: dict, feature_sets: dict, pool: str, seeds=SEEDS) -> pd.DataFrame:
    rows = []
    for i, seed in enumerate(seeds):
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label, features = pool_label(sets), list(sets["feature_pool"])
        draw = 1000 + i
        for source, n_rows in (("validation", len(splits.val)), ("test", len(splits.test))):
            unlabelled, evaluation = block_split(n_rows, BLOCK, BUFFER, UNLABELLED_SHARE, draw)
            fits = self_train(cfg, sets, splits, features, unlabelled, "val" if source == "validation" else "test")
            for r, fit in enumerate(fits):
                if source == "test":
                    metrics = evaluate_fit(fit, evaluation)
                else:  # validation check: macro F1 / argmax FPR on the held-out validation blocks (no threshold)
                    pv, yv = fit.proba_val[evaluation], fit.y_val[evaluation]
                    called = pv.argmax(axis=1) != fit.normal_index
                    metrics = {"accuracy": float((pv.argmax(axis=1) == yv).mean()), "macro_f1": float(f1_score(yv, pv.argmax(axis=1), average="macro", zero_division=0)),
                               "argmax_fpr": float(called[yv == fit.normal_index].mean()), "n_eval": int(len(yv))}
                extra = {}
                if r < len(fits) - 1:   # the pseudo-labels this round PRODUCES (from this model's probabilities)
                    proba, truth = (fit.proba_test, fit.y_test) if source == "test" else (fit.proba_val, fit.y_val)
                    extra = reinforcement(unlabelled, proba, truth, fit.normal_index, TAU)
                rows.append(base_row(label, seed, f"self_round{r}", "zero-shot" if r == 0 else "transductive", source=source, round=r, n_unlabelled=int(len(unlabelled)),
                                     **metrics, **extra))
            logger.info(f"[fpr self {label}] seed={seed} {source}: argmax_fpr by round {[round(x['argmax_fpr'], 4) for x in rows[-len(fits):]]}")
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Step 4: few-shot label budget x selection
def choose_rows(strategy: str, proba: np.ndarray, X: np.ndarray, k: int, draw_seed: int) -> np.ndarray:
    """Positions (within the candidate rows) of the k rows to label; uses only the unlabelled features and the zero-shot probabilities."""
    if strategy == "random":
        return random_selection(len(proba), k, draw_seed)
    if strategy == "entropy":
        return entropy_selection(proba, k)
    if strategy == "diverse":
        return diverse_selection(X, k, 0)
    if strategy == "mix":
        return mix_selection(proba, X, k, 0)
    raise ValueError(f"unknown strategy {strategy!r}")


def run_fewshot(config: dict, feature_sets: dict, pool: str, runs: int = 5, ks=KS, strategies=STRATEGIES) -> pd.DataFrame:
    rows = []
    for i in range(runs):
        seed, draw = 42 + i, 1000 + i
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label, features = pool_label(sets), list(sets["feature_pool"])
        target, normal = cfg["data"]["target_column"], cfg["data"]["normal_category"]
        candidates, evaluation = block_split(len(splits.test), BLOCK, BUFFER, ADAPT_SHARE, draw)
        base = fit_model(cfg, sets, splits, features)
        eval_frame = splits.test.iloc[evaluation].reset_index(drop=True)
        zero = evaluate_fit(base, evaluation)
        rows.append(base_row(label, seed, "zero_shot", "zero-shot", k=0, strategy="none", run=i, n_candidates=int(len(candidates)), **zero))
        cand_frame = splits.test.iloc[candidates].reset_index(drop=True)
        proba_c, X_c = base.proba_test[candidates], np.asarray(base.pre.transform_features(cand_frame), dtype=float)
        for k in ks:
            for strategy in strategies:
                chosen = choose_rows(strategy, proba_c, X_c, k, draw + k)
                labelled = cand_frame.iloc[chosen]
                order = np.random.default_rng(draw + k).permutation(len(labelled))
                fit_half, threshold_half = labelled.iloc[order[: (len(order) + 1) // 2]], labelled.iloc[order[(len(order) + 1) // 2:]]
                adapted = with_adaptation(splits, fit_half, eval_frame, FEWSHOT_FRACTION)
                fit = fit_model(cfg, sets, adapted, features)
                scores = 1 - fit.model.predict_proba(fit.pre.transform_features(threshold_half))[:, fit.normal_index]
                attack = (threshold_half[target] != normal).to_numpy()
                usable = attack.any() and (~attack).any()
                threshold = select_attack_threshold(attack, scores, target_detection=0.95) if usable else None
                metrics = evaluate_fit(fit, None, threshold=threshold)
                held_fpr = attack_rates(attack, scores, threshold)[1] if usable else float("nan")
                rows.append(base_row(label, seed, f"{strategy}_k{k}", "few-shot", k=k, strategy=strategy, run=i, n_candidates=int(len(candidates)), n_labelled=int(len(labelled)),
                                     labelled_attack_share=float(((labelled[target] != normal).mean())), held_half_fpr=float(held_fpr),
                                     threshold_source="held-out half" if usable else "validation", **metrics))
            logger.info(f"[fpr fewshot {label}] run={i} k={k} done")
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Step 5: the declared zero-shot combination
def validation_auc(fit: SimpleNamespace) -> float:
    return float(roc_auc_score(fit.y_val != fit.normal_index, 1 - fit.proba_val[:, fit.normal_index]))


def run_combined(config: dict, feature_sets: dict, pool: str, seeds=SEEDS) -> pd.DataFrame:
    """The recipe declared in results/06_fpr_and_adaptation.md, section `Source: fpr_reduction_protocol.md`, per seed and chosen on that seed's validation rows only: the block-grouped-validation tuned configuration (objective: validation
    attack AUC) if its validation AUC is at least the default's, else the default; temperature scaling always; the EM prior correction only if its validation gate passes (then the recipe is
    TRANSDUCTIVE, otherwise ZERO-SHOT). Evaluated on the whole official test file."""
    rows = []
    for seed in seeds:
        cfg, sets, splits = prepare(config, feature_sets, pool, "xgboost", seed)
        label, features = pool_label(sets), list(sets["feature_pool"])
        default = fit_model(cfg, sets, splits, features)
        chosen, used_tuned = default, False
        override = tuned_overrides(config, label).get("blockval_tuned_auc")
        if override is not None:
            tuned = fit_model(cfg, sets, splits, features, override)
            if validation_auc(tuned) >= validation_auc(default):
                chosen, used_tuned = tuned, True
        temperature = fit_temperature(chosen.proba_val, chosen.y_val)
        pv, pt = apply_temperature(chosen.proba_val, temperature), apply_temperature(chosen.proba_test, temperature)
        pu = apply_temperature(chosen.proba_unknown, temperature) if chosen.proba_unknown is not None else None
        gate = em_gate(pv, chosen.y_val, chosen.pi_model, seeds=SEEDS)
        if gate["passes"]:
            pi_hat = em_prior(pt, chosen.pi_model)
            pv, pt = prior_correct(pv, pi_hat, chosen.pi_model), prior_correct(pt, pi_hat, chosen.pi_model)
            pu = prior_correct(pu, pi_hat, chosen.pi_model) if pu is not None else None
        metrics = evaluate_probabilities(pv, chosen.y_val, pt, chosen.y_test, chosen.normal_index, cfg["evaluation"]["ece_bins"], pu)
        rows.append(base_row(label, seed, "combined", "transductive" if gate["passes"] else "zero-shot", used_tuned=used_tuned, used_em=gate["passes"], temperature=temperature,
                             val_auc_default=validation_auc(default), **metrics))
        rows.append(base_row(label, seed, "default", "zero-shot", **evaluate_fit(default)))
        logger.info(f"[fpr combined {label}] seed={seed} tuned={used_tuned} em={gate['passes']} det95_fpr={rows[-2]['det95_test_fpr']:.4f}")
    return pd.DataFrame(rows)


RUNNERS = {"tuned": run_tuned, "prior": run_prior, "self": run_self, "combined": run_combined}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--step", required=True, choices=[*RUNNERS, "fewshot"])
    parser.add_argument("--pools", nargs="*", default=None)
    parser.add_argument("--seeds", nargs="*", type=int)
    parser.add_argument("--ks", nargs="*", type=int)
    args = parser.parse_args()
    config, feature_sets = load_config(), load_feature_sets()
    add_file_logging(str(resolve_path(config["logging"]["log_file"])))
    metrics_dir = get_metrics_dir(config)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    pools = args.pools or ["full"]   # the primary pool 48; --pools base full_no_ttl (or full_no_ct_window for fewshot) adds comparison pools
    for pool in pools:
        if args.step == "fewshot":
            df = run_fewshot(config, feature_sets, pool, len(args.seeds) if args.seeds else 5, tuple(args.ks) if args.ks else KS)
        else:
            df = RUNNERS[args.step](config, feature_sets, pool, tuple(args.seeds) if args.seeds else SEEDS)
        out = metrics_dir / f"fpr_study_{args.step}_{df['pool_label'].iloc[0]}_runs.csv"
        df.to_csv(out, index=False)
        print(df.groupby("method")[["argmax_fpr", "det95_test_fpr", "det95_test_detection", "accuracy", "macro_f1", "ece"]].mean().round(4).to_string()
              if "det95_test_fpr" in df else df.groupby("method")[["argmax_fpr", "macro_f1"]].mean().round(4).to_string())
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
