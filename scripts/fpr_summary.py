"""Tables for Task 2.7 from results/metrics/xgboost/fpr_study_<step>_<N>f_runs.csv (protocol: results/task_2_7_protocol.md).

    python scripts/fpr_summary.py --step tuned|prior|self|fewshot --pools 40f 45f 48f

Writes fpr_study_<step>_<pools>.md next to the inputs. Verdicts apply the rule declared before any result: a method CLEARLY BEATS the baseline when the mean paired
(same seed) difference in det95_test_fpr is at most -0.02, it is better in at least 4 of the 5 seeds, and its detection at the operating point is not more than 0.02 below.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.utils.config_loader import get_metrics_dir, load_config

METRICS = ["accuracy", "macro_f1", "argmax_fpr", "det95_test_fpr", "fpr_at_95_threshold_free", "det95_test_detection", "ece", "open_set_detection"]
MIN_GAIN, MIN_SEEDS, MAX_DETECTION_LOSS = 0.02, 4, 0.02


def mean_std(values: pd.Series) -> str:
    return "n/a" if values.isna().all() else f"{values.mean():.3f} +/- {values.std(ddof=1):.3f}" if values.notna().sum() > 1 else f"{values.mean():.3f}"


def paired_verdict(df: pd.DataFrame, method: str, baseline: str, key: tuple[str, ...] = ("seed",), metric: str = "det95_test_fpr",
                   detection: str = "det95_test_detection") -> dict:
    """Paired comparison of `method` with `baseline` over the rows that share `key` (e.g. seed, or seed + run): mean difference in `metric` (negative = lower FPR), the number of
    pairs in which the method is better, the mean detection difference, and whether the declared rule is met."""
    a = df[df["method"] == method].set_index(list(key))
    b = df[df["method"] == baseline].set_index(list(key))
    common = a.index.intersection(b.index)
    if len(common) == 0:
        return {"n_pairs": 0, "mean_diff": float("nan"), "n_better": 0, "detection_diff": float("nan"), "clearly_beats": False}
    diff = (a.loc[common, metric] - b.loc[common, metric]).astype(float)
    det = (a.loc[common, detection] - b.loc[common, detection]).astype(float)
    wins = int((diff < 0).sum())
    required = int(np.ceil(MIN_SEEDS / 5 * len(common)))      # 4 of 5 seeds, scaled when fewer pairs are available
    return {"n_pairs": int(len(common)), "mean_diff": float(diff.mean()), "n_better": wins, "detection_diff": float(det.mean()),
            "clearly_beats": bool(diff.mean() <= -MIN_GAIN and wins >= required and det.mean() >= -MAX_DETECTION_LOSS)}


def smallest_k(df: pd.DataFrame, strategy: str, target: float = 0.15, metric: str = "det95_test_fpr") -> int | None:
    """The smallest budget k whose mean `metric` over the runs is at most `target` for `strategy` (None when no budget gets there)."""
    g = df[df["strategy"] == strategy].groupby("k")[metric].mean().sort_index()
    ok = g[g <= target]
    return int(ok.index[0]) if len(ok) else None


def table(rows: pd.DataFrame, first: list[str], metrics: list[str] = METRICS) -> list[str]:
    cols = [m for m in metrics if m in rows]
    lines = ["| " + " | ".join([*first, *cols]) + " |", "|" + "---|" * (len(first) + len(cols))]
    for keys, g in rows.groupby(first, sort=False):
        keys = keys if isinstance(keys, tuple) else (keys,)
        lines.append("| " + " | ".join([*map(str, keys), *(mean_std(g[c]) for c in cols)]) + " |")
    return lines


def render_tuned(runs: pd.DataFrame) -> str:
    out = ["# Task 2.7 Step 1 (ZERO-SHOT): re-tuning on block-grouped validation, official test, mean +/- std over seeds 42-46", "",
           "Primary metric `det95_test_fpr` (threshold at 95% detection chosen on block-grouped validation). `earlier_tuned_*` = the Task 2a search on random validation (40 and 48 features only); "
           "`blockval_tuned_*` = the 40-trial search on block-grouped validation with the regularised space. Verdict = the declared rule against `default` on the same seeds.", ""]
    for label, g in runs.groupby("pool_label", sort=False):
        out += [f"## {label}", "", *table(g, ["method"]), "", "| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |", "|---|---|---|---|---|"]
        for method in g["method"].unique():
            if method != "default":
                v = paired_verdict(g, method, "default")
                out.append(f"| {method} | {v['mean_diff']:+.4f} | {v['n_better']} of {v['n_pairs']} | {v['detection_diff']:+.4f} | {'yes' if v['clearly_beats'] else 'no'} |")
        out.append("")
    return "\n".join(out) + "\n"


def render_prior(runs: pd.DataFrame) -> str:
    out = ["# Task 2.7 Step 2: temperature scaling and class-prior correction, official test, mean +/- std over seeds 42-46", "",
           "`calibrated` and `calibrated_valprior` are ZERO-SHOT; `calibrated_em` is TRANSDUCTIVE (uses the unlabelled test features). The same transformation is applied to validation and test; "
           "the det95 threshold is chosen on the transformed validation scores.", ""]
    for label, g in runs.groupby("pool_label", sort=False):
        em = g[g["method"] == "calibrated_em"]
        out += [f"## {label}", "", *table(g, ["method", "access"]), "", "| method | mean paired diff in det95 FPR | better in | detection diff | clearly beats default |", "|---|---|---|---|---|"]
        for method in ("calibrated", "calibrated_valprior", "calibrated_em"):
            v = paired_verdict(g, method, "default")
            out.append(f"| {method} | {v['mean_diff']:+.4f} | {v['n_better']} of {v['n_pairs']} | {v['detection_diff']:+.4f} | {'yes' if v['clearly_beats'] else 'no'} |")
        shares = [c[len("est_share_"):] for c in em.columns if c.startswith("est_share_")]
        out += ["", f"Temperature (mean) {em['temperature'].mean():.2f}. Diagnostic only, the true shares never enter a fit: L1 distance to the true test shares: EM estimate "
                f"{mean_std(em['em_l1_to_true_shares'])}, model prior {mean_std(em['model_prior_l1_to_true_shares'])}, validation shares {mean_std(em['val_prior_l1_to_true_shares'])}. "
                f"EM validation gate (simulated shifts) passes in {int(em['em_gate_passes'].sum())} of {len(em)} seeds.", "",
                "| class | estimated share | true share |", "|---|---|---|",
                *[f"| {c} | {em['est_share_' + c].mean():.3f} | {em['true_share_' + c].mean():.3f} |" for c in shares], ""]
    return "\n".join(out) + "\n"


def render_self(runs: pd.DataFrame) -> str:
    out = ["# Task 2.7 Step 3 (TRANSDUCTIVE): self-training, mean +/- std over seeds 42-46", "",
           "Two rounds, tau = 0.90, pseudo-labelled rows carry 20% of the sample weight, rounds are not cumulative. Pseudo-labels come from the unlabelled blocks and every metric is on the other blocks (200-row gaps). "
           "`validation` rows are the check made before looking at the test file (half of the block-grouped validation blocks treated as unlabelled).", ""]
    for label, g in runs.groupby("pool_label", sort=False):
        out += [f"## {label}", ""]
        for source in ("validation", "test"):
            s = g[g["source"] == source]
            out += [f"### {source} blocks", "", *table(s, ["method", "access"], ["accuracy", "macro_f1", "argmax_fpr", "det95_test_fpr", "det95_test_detection", "ece"]), ""]
            base, last = s[s["method"] == "self_round0"], s[s["method"] == f"self_round{int(s['round'].max())}"]
            d = (last.set_index("seed")["argmax_fpr"] - base.set_index("seed")["argmax_fpr"]).dropna()
            f = (last.set_index("seed")["macro_f1"] - base.set_index("seed")["macro_f1"]).dropna()
            out += [f"Round {int(s['round'].max())} minus round 0: argmax FPR {d.mean():+.4f} (lower in {int((d < 0).sum())} of {len(d)} seeds), macro F1 {f.mean():+.4f}.", ""]
            if source == "validation":
                out += [f"Validation check (macro F1 not down more than 0.01 and argmax FPR not up more than 0.01): {'passes' if (f.mean() >= -0.01 and d.mean() <= 0.01) else 'fails'}.", ""]
        diag = g[(g["source"] == "test") & g["pseudo_labelled"].notna()]
        out += ["### Reinforcement diagnostics on the test blocks (true labels used to report only)", "",
                *table(diag, ["method"], ["pseudo_labelled", "pseudo_wrong_share", "true_normal_given_attack_pseudo_label", "attack_pseudo_labels_that_are_normal"]), ""]
    return "\n".join(out) + "\n"


def render_fewshot(runs: pd.DataFrame) -> str:
    out = ["# Task 2.7 Step 4 (FEW-SHOT): label budget and selection strategy, mean +/- std over 5 runs", "",
           "Half of the k labelled rows retrain the model (weight fraction 0.5), the other half chooses the 95%-detection threshold. Candidates and evaluation rows come from different time blocks "
           "(200-row gaps); every method is scored on the same evaluation rows as the zero-shot baseline. Smallest k with mean det95 FPR <= 0.15 is stated per strategy.", ""]
    for label, g in runs.groupby("pool_label", sort=False):
        zero = g[g["method"] == "zero_shot"]
        out += [f"## {label}", "", f"Zero-shot baseline on the same rows: det95 FPR {mean_std(zero['det95_test_fpr'])}, detection {mean_std(zero['det95_test_detection'])}, argmax FPR {mean_std(zero['argmax_fpr'])}.", "",
                "| strategy | k | det95 FPR | detection | argmax FPR | accuracy | macro F1 | ECE | held-out half FPR | labelled attack share |", "|---|---|---|---|---|---|---|---|---|---|"]
        few = g[g["k"] > 0]
        for (strategy, k), s in few.groupby(["strategy", "k"], sort=False):
            out.append(f"| {strategy} | {k} | {mean_std(s['det95_test_fpr'])} | {mean_std(s['det95_test_detection'])} | {mean_std(s['argmax_fpr'])} | {mean_std(s['accuracy'])} | "
                       f"{mean_std(s['macro_f1'])} | {mean_std(s['ece'])} | {mean_std(s['held_half_fpr'])} | {mean_std(s['labelled_attack_share'])} |")
        out += ["", "| strategy | smallest k with mean det95 FPR <= 0.15 |", "|---|---|", *[f"| {s} | {smallest_k(few, s) or 'none reached'} |" for s in few['strategy'].unique()], ""]
    return "\n".join(out) + "\n"


def best_strategy(fewshot: pd.DataFrame, k: int = 1000) -> str | None:
    """The declared few-shot choice that uses only the labelled sample: the strategy with the lowest mean held-out-half FPR at budget `k`."""
    g = fewshot[fewshot["k"] == k].groupby("strategy")["held_half_fpr"].mean().dropna()
    return None if g.empty else str(g.idxmin())


FINAL_COLUMNS = ["accuracy", "macro_f1", "argmax_fpr", "det95_test_fpr", "fpr_at_95_threshold_free", "det95_test_detection", "ece", "open_set_detection"]


def render_final(tuned: pd.DataFrame, prior: pd.DataFrame, combined: pd.DataFrame, selfs: pd.DataFrame, fewshot: pd.DataFrame, label: str) -> str:
    """Step 5 table of one pool. Block A: the whole official test file, threshold at ~95% detection chosen on block-grouped validation. Block B: rows from other time blocks
    (200-row gaps) than the unlabelled / labelled rows; every method there sits next to the zero-shot baseline scored on exactly the same rows."""
    out = [f"## {label}", "", "### A. Whole official test file (zero-shot and transductive methods)", "",
           "| method | access | " + " | ".join(FINAL_COLUMNS) + " |", "|---|---|" + "---|" * len(FINAL_COLUMNS)]
    def line(name: str, access: str, g: pd.DataFrame) -> str:
        return f"| {name} | {access} | " + " | ".join(mean_std(g[c]) if c in g else "n/a" for c in FINAL_COLUMNS) + " |"
    blocks = [("default (config.yaml)", "zero-shot", tuned[tuned["method"] == "default"]),
              ("earlier tuned, random validation (auc)", "zero-shot", tuned[tuned["method"] == "earlier_tuned_auc"]),
              ("tuned on block-grouped validation (auc)", "zero-shot", tuned[tuned["method"] == "blockval_tuned_auc"]),
              ("tuned on block-grouped validation (macro F1)", "zero-shot", tuned[tuned["method"] == "blockval_tuned_f1"]),
              ("temperature scaling", "zero-shot", prior[prior["method"] == "calibrated"]),
              ("temperature scaling + validation class prior (control)", "zero-shot", prior[prior["method"] == "calibrated_valprior"]),
              ("temperature scaling + EM prior correction", "transductive", prior[prior["method"] == "calibrated_em"]),
              ("declared combination (tuned if validation AUC >= default, temperature, EM if its gate passes)", "zero-shot / transductive", combined[combined["method"] == "combined"])]
    out += [line(n, a, g) for n, a, g in blocks if len(g)]
    out += ["", "### B. Rows from other time blocks than the unlabelled / labelled rows (each method next to its zero-shot baseline on the same rows)", "",
            "| method | access | " + " | ".join(FINAL_COLUMNS) + " |", "|---|---|" + "---|" * len(FINAL_COLUMNS)]
    test_rows = selfs[selfs["source"] == "test"]
    out += [line("zero-shot baseline (self-training evaluation rows)", "zero-shot", test_rows[test_rows["method"] == "self_round0"]),
            line("self-training, round 2", "transductive", test_rows[test_rows["method"] == "self_round2"])]
    choice = best_strategy(fewshot)
    out += [line("zero-shot baseline (few-shot evaluation rows)", "zero-shot", fewshot[fewshot["method"] == "zero_shot"])]
    if choice:
        for k in (1000, 5000):
            out.append(line(f"few-shot, {choice} selection, k = {k}", "few-shot", fewshot[fewshot["method"] == f"{choice}_k{k}"]))
        out += ["", f"Few-shot strategy chosen by the declared rule (lowest held-out-half FPR at k = 1,000): **{choice}**."]
    return "\n".join(out) + "\n"


RENDER = {"tuned": render_tuned, "prior": render_prior, "self": render_self, "fewshot": render_fewshot}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--step", required=True, choices=[*RENDER, "final"])
    parser.add_argument("--pools", nargs="+", required=True, help="pool labels such as 40f 45f 48f 41f")
    args = parser.parse_args()
    d = get_metrics_dir(load_config())
    if args.step == "final":
        parts = []
        for p in args.pools:
            read = lambda step, p=p: pd.read_csv(d / f"fpr_study_{step}_{p}_runs.csv")   # noqa: E731
            parts.append(render_final(read("tuned"), read("prior"), read("combined"), read("self"), read("fewshot"), p))
        text = "# Task 2.7 Step 5: final table (official split, mean +/- std over seeds 42-46)\n\n" + "\n".join(parts)
        out = d / f"fpr_study_final_{'_'.join(args.pools)}.md"
        out.write_text(text, encoding="utf-8")
        print(text)
        return
    runs = pd.concat([pd.read_csv(d / f"fpr_study_{args.step}_{p}_runs.csv") for p in args.pools], ignore_index=True)
    text = RENDER[args.step](runs)
    out = d / f"fpr_study_{args.step}_{'_'.join(args.pools)}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
