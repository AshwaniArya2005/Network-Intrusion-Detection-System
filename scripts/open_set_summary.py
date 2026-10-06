"""Open-set study summaries: turn the raw open-set runs into one table per step (mean +/- std over seeds 42-46).

    python scripts/open_set_summary.py [--pools 40f 45f 48f] [--rotation-pools 40f 48f] [--variants 41f 38f 48f_t30 48f_t15]

Reads results/metrics/xgboost/open_set_{runs,selection,curve,sources}_<label>.csv and open_set_rotation_<label>_{runs,sources}.csv (pipelines/run_open_set_study.py) and writes
open_set_step{1,2,3,4}_<labels>.md / .csv. The per-pool choice of combination rule and best score comes from the PSEUDO-UNKNOWN validation table only
(pipelines.run_open_set_study.pool_selection); the score that happens to be best on the real zero-day flows is shown but never used for a choice.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipelines.run_open_set_study import CANDIDATES, pool_selection
from src.utils.config_loader import get_metrics_dir, load_config

MAIN_ZERO_DAY = "Shellcode+Worms"
STEP1_METRICS = ["unknown_auroc", "detection", "flagged_or_attack", "false_unknown_thr_half", "false_unknown_cal_half", "false_unknown_test"]


def mean_std(df: pd.DataFrame, by: list[str], cols: list[str]) -> pd.DataFrame:
    """Per group: <col>_mean and <col>_std (ddof=1) over seeds."""
    g = df.groupby(by, sort=False)[cols]
    out = g.mean().add_suffix("_mean").join(g.std(ddof=1).add_suffix("_std"))
    out["n_seeds"] = df.groupby(by, sort=False)["seed"].nunique()
    return out.reset_index()


def fmt(m, s) -> str:
    return "n/a" if pd.isna(m) else (f"{m:.3f} +/- {s:.3f}" if not pd.isna(s) else f"{m:.3f}")


def step1_table(runs: pd.DataFrame, selection: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Per candidate score: zero-day metrics (Worms + Shellcode), the realised false-Unknown rates, the per-class detection and the pseudo-unknown validation AUROC; flags for the
    validation-selected rule / best score and for the score that is best on the real zero-day flows (reported, not used)."""
    sel = pool_selection(selection)
    main = mean_std(runs[runs["zero_day"] == MAIN_ZERO_DAY], ["score"], STEP1_METRICS)
    for cls in ("Shellcode", "Worms"):
        part = runs[runs["zero_day"] == cls].groupby("score")["detection"].mean().rename(f"detection_{cls}")
        main = main.join(part, on="score")
    main = main.join(selection.groupby("score")["pseudo_auroc"].mean().rename("pseudo_unknown_auroc"), on="score")
    main["chosen_candidate"] = main["score"].isin(sel["candidates"])
    main["best_on_validation"] = main["score"] == sel["best"]
    chosen = main[main["chosen_candidate"]]
    main["best_on_zero_day_auroc"] = main["score"] == chosen.loc[chosen["unknown_auroc_mean"].idxmax(), "score"]
    return main, sel


def render_step1(tables: dict[str, tuple[pd.DataFrame, dict]]) -> str:
    lines = ["# Open-set study Step 1: open-set scoring functions (XGBoost, official split, block-grouped validation, threshold at 5% false-Unknown, mean +/- std over 5 seeds)", "",
             "Zero-day = Worms + Shellcode (Shellcode is 89.5% of the 1,627 flows). Threshold fixed on the known THRESHOLD half of the validation flows; `false-Unknown cal half` is the held-out validation half, "
             "`false-Unknown test` the official test known flows (the gap to 5% is the cost of the shift). `chosen` = candidates after the rule choice; `*` = best on pseudo-unknown validation "
             "(used downstream), `+` = best on the real zero-day AUROC (reported only). Pseudo-unknown AUROC = validation flows of Reconnaissance / Generic held out of an inner model.", ""]
    for label, (t, sel) in tables.items():
        lines += [f"## {label}  (rules chosen on validation: {sel['rules']}; best: **{sel['best']}**)", "",
                  "| score | chosen | unknown AUROC | detection @5% | flagged or called attack | det. Shellcode | det. Worms | false-Unknown thr half | cal half | test | pseudo-unknown AUROC |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in t.itertuples(index=False):
            d = r._asdict()
            mark = ("*" if d["best_on_validation"] else "") + ("+" if d["best_on_zero_day_auroc"] else "")
            lines.append(f"| {d['score']}{mark} | {'yes' if d['chosen_candidate'] else 'no'} | {fmt(d['unknown_auroc_mean'], d['unknown_auroc_std'])} | {fmt(d['detection_mean'], d['detection_std'])} | "
                         f"{fmt(d['flagged_or_attack_mean'], d['flagged_or_attack_std'])} | {d['detection_Shellcode']:.3f} | {d['detection_Worms']:.3f} | "
                         f"{fmt(d['false_unknown_thr_half_mean'], d['false_unknown_thr_half_std'])} | {fmt(d['false_unknown_cal_half_mean'], d['false_unknown_cal_half_std'])} | "
                         f"{fmt(d['false_unknown_test_mean'], d['false_unknown_test_std'])} | {d['pseudo_unknown_auroc']:.3f} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def rotation_table(runs: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    """Per held-out class and score: mean / std over seeds of AUROC, detection and flagged-or-attack, plus the exact-twin share of the class in the known data."""
    t = mean_std(runs[runs["score"].isin(names)], ["held_out", "score"], ["unknown_auroc", "detection", "flagged_or_attack", "false_unknown_cal_half", "false_unknown_test"])
    twin = runs.groupby("held_out")["exact_twin_share_in_known"].mean().rename("exact_twin_share")
    n = runs.groupby("held_out")["n_zero_day"].first().rename("n_flows")
    return t.join(twin, on="held_out").join(n, on="held_out")


def render_step2(tables: dict[str, tuple[pd.DataFrame, str]]) -> str:
    lines = ["# Open-set study Step 2: leave-one-attack-class-out (XGBoost, official split, threshold at 5% false-Unknown on block-grouped known validation, mean +/- std over 5 seeds)", "",
             "Each class is held out in turn (never trained on); `best` = the pool's pseudo-unknown-selected score, compared with `msp`. Overlap-Group-1 members are held out one at a time "
             "(siblings stay known and still form the merged group); the trio is also held out as a unit. `exact twin share` = share of the class's flows with an identical feature vector among the known flows.", ""]
    for label, (t, best) in tables.items():
        lines += [f"## {label}  (best score: {best})", "", "| held-out class | flows | exact twin share | score | AUROC | detection @5% | flagged or called attack | false-Unknown test |", "|---|---|---|---|---|---|---|---|"]
        for r in t.itertuples(index=False):
            d = r._asdict()
            lines.append(f"| {d['held_out']} | {int(d['n_flows'])} | {d['exact_twin_share']:.2f} | {d['score']} | {fmt(d['unknown_auroc_mean'], d['unknown_auroc_std'])} | {fmt(d['detection_mean'], d['detection_std'])} | "
                         f"{fmt(d['flagged_or_attack_mean'], d['flagged_or_attack_std'])} | {fmt(d['false_unknown_test_mean'], d['false_unknown_test_std'])} |")
        single = t[~t["held_out"].str.startswith("Overlap-Group")]
        for score, g in single.groupby("score"):
            worst = g.loc[g["unknown_auroc_mean"].idxmin()]
            lines.append(f"| **mean over the nine classes** | | | {score} | {g['unknown_auroc_mean'].mean():.3f} | {g['detection_mean'].mean():.3f} | {g['flagged_or_attack_mean'].mean():.3f} | {g['false_unknown_test_mean'].mean():.3f} |")
            lines.append(f"| **worst class by AUROC ({worst['held_out']})** | | | {score} | {worst['unknown_auroc_mean']:.3f} | {worst['detection_mean']:.3f} | {worst['flagged_or_attack_mean']:.3f} | {worst['false_unknown_test_mean']:.3f} |")
        lines.append("")
    return "\n".join(lines) + "\n"


CURVE_COLS = ["alert_fpr_off", "alert_fpr_on", "confident_alert_fpr", "review_rate_normal", "share_of_false_alerts_that_skip_review", "zero_day_catch", "zero_day_flagged",
              "known_attack_alert_rate", "known_attack_confident_detection"]


def render_step3(tables: dict[str, tuple[pd.DataFrame, str]]) -> str:
    lines = ["# Open-set study Step 3: alert-level FPR and the review queue (XGBoost, official split, mean +/- std over 5 seeds)", "",
             "Alert FPR OFF = Normal flows predicted as any attack class. Alert FPR ON = Normal flows predicted as an attack class OR sent to review as Unknown (it can only be higher). "
             "Confident-alert FPR = Normal flows called an attack and NOT sent to review (the alerts that skip the queue). Review rate = Normal flows sent to Unknown (the cost). "
             "Zero-day catch = zero-day flows flagged Unknown or called an attack. The declared operating point is the 5% target, chosen on validation only.", ""]
    for label, (c, best) in tables.items():
        for score in dict.fromkeys([best, "msp"]):
            g = c[c["score"] == score]
            lines += [f"## {label}: {score}{' (best)' if score == best else ''}", "", "| false-Unknown target | alert FPR OFF | alert FPR ON | confident-alert FPR | review rate on Normal | false alerts that skip review | zero-day catch | zero-day flagged Unknown | known-attack alert rate | known attacks detected confidently |",
                      "|---|---|---|---|---|---|---|---|---|---|"]
            for r in g.itertuples(index=False):
                d = r._asdict()
                lines.append(f"| {d['target']:.1%} | " + " | ".join(fmt(d[f"{col}_mean"], d[f"{col}_std"]) for col in CURVE_COLS) + " |")
            lines.append("")
    return "\n".join(lines) + "\n"


def render_step4(rows: pd.DataFrame, gap_note: str) -> str:
    lines = ["# Open-set study Step 4: does ct_* carry the open-set gain? (XGBoost, official split, threshold at 5% false-Unknown, mean +/- std over 5 seeds)", "", gap_note, "",
             "| variant | score | unknown AUROC | detection @5% | false-Unknown test |", "|---|---|---|---|---|"]
    for r in rows.itertuples(index=False):
        d = r._asdict()
        lines.append(f"| {d['label']} | {d['score']} | {fmt(d['unknown_auroc_mean'], d['unknown_auroc_std'])} | {fmt(d['detection_mean'], d['detection_std'])} | {fmt(d['false_unknown_test_mean'], d['false_unknown_test_std'])} |")
    return "\n".join(lines) + "\n"


def sources_table(sources: pd.DataFrame, scores: list[str]) -> pd.DataFrame:
    """Which known classes the false-Unknown alarms come from: per score, split (thr = validation threshold half, cal = held-out validation half, test = official test) and original
    class, the mean over seeds of the share of that class's flows flagged and of its share of all false alarms."""
    g = sources[sources["score"].isin(scores)].groupby(["score", "part", "known_class"], sort=False)
    out = g[["flagged_share", "share_of_false_alarms"]].mean()
    out["n"] = g["n"].mean()
    return out.reset_index()


def render_sources(label: str, best: str, t: pd.DataFrame) -> str:
    lines = [f"## {label}: where the false-Unknown alarms come from (Worms + Shellcode held out, threshold at 5%, mean over 5 seeds)", "",
             "`flagged` = share of the class's known flows flagged Unknown; `of alarms` = the class's share of all false alarms. thr / cal = the two validation halves, test = official test.", ""]
    for score in dict.fromkeys([best, "msp"]):
        g = t[t["score"] == score].pivot(index="known_class", columns="part", values=["flagged_share", "share_of_false_alarms", "n"])
        lines += [f"**{score}**", "", "| known class | flows (test) | flagged: thr | cal | test | of alarms: thr | cal | test |", "|---|---|---|---|---|---|---|---|"]
        for cls in g.index:
            lines.append(f"| {cls} | {g.loc[cls, ('n', 'test')]:.0f} | " + " | ".join(f"{g.loc[cls, ('flagged_share', p)]:.3f}" for p in ("thr", "cal", "test")) + " | "
                         + " | ".join(f"{g.loc[cls, ('share_of_false_alarms', p)]:.3f}" for p in ("thr", "cal", "test")) + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def ct_verdict(det_by_label: dict[str, float]) -> tuple[str, float, float]:
    """Declared reading (results/02_novelty1_open_set.md, section `Source: open_set_protocol.md`): with gap = detection(48f) - detection(40f) for msp, the ct_* window counts carry the gain if removing them lowers the detection by at
    least half the gap (confirm), by less than a quarter (reject), otherwise partial. Returns (verdict, drop, gap)."""
    gap = det_by_label["48f"] - det_by_label["40f"]
    drop = det_by_label["48f"] - det_by_label["41f"]
    if gap <= 0:
        return "no gap to explain", drop, gap
    return ("confirmed" if drop >= 0.5 * gap else "rejected" if drop < 0.25 * gap else "partial"), drop, gap


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pools", nargs="*", default=["40f", "45f", "48f"])
    parser.add_argument("--rotation-pools", nargs="*", default=["40f", "48f"])
    parser.add_argument("--variants", nargs="*", default=["41f", "38f", "48f_t30", "48f_t15"])
    args = parser.parse_args()
    d = get_metrics_dir(load_config())
    step1, step3 = {}, {}
    for label in args.pools:
        if (d / f"open_set_runs_{label}.csv").exists():
            runs, selection, curve = (pd.read_csv(d / f"open_set_{n}_{label}.csv") for n in ("runs", "selection", "curve"))
            t, sel = step1_table(runs, selection)
            step1[label] = (t, sel)
            t.to_csv(d / f"open_set_step1_{label}.csv", index=False)
            step3[label] = (mean_std(curve[curve["score"].isin([sel["best"], "msp"])], ["score", "target"], CURVE_COLS), sel["best"])
    tag = "_".join(step1)
    if step1:
        src_text = "# Open-set study Step 2 (continued): known classes behind the false-Unknown alarms\n\n"
        for label, (t, sel) in step1.items():
            src = pd.read_csv(d / f"open_set_sources_{label}.csv")
            src_text += render_sources(label, sel["best"], sources_table(src, list(dict.fromkeys([sel["best"], "msp"]))))
        (d / f"open_set_step2_sources_{tag}.md").write_text(src_text, encoding="utf-8")
        (d / f"open_set_step1_{tag}.md").write_text(render_step1(step1), encoding="utf-8")
        (d / f"open_set_step3_{tag}.md").write_text(render_step3(step3), encoding="utf-8")
    step2 = {}
    for label in args.rotation_pools:
        path = d / f"open_set_rotation_{label}_runs.csv"
        if path.exists() and label in step1:
            best = step1[label][1]["best"]
            step2[label] = (rotation_table(pd.read_csv(path), list(dict.fromkeys([best, "msp"]))), best)
            step2[label][0].to_csv(d / f"open_set_step2_{label}.csv", index=False)
    if step2:
        (d / f"open_set_step2_{'_'.join(step2)}.md").write_text(render_step2(step2), encoding="utf-8")
    rows = []
    for label in ["40f", "48f", *args.variants]:
        if (d / f"open_set_runs_{label}.csv").exists():
            runs = pd.read_csv(d / f"open_set_runs_{label}.csv")
            sel = pool_selection(pd.read_csv(d / f"open_set_selection_{label}.csv"))
            t = mean_std(runs[(runs["zero_day"] == MAIN_ZERO_DAY) & runs["score"].isin(list(dict.fromkeys(["msp", sel["best"]])))], ["score"], ["unknown_auroc", "detection", "false_unknown_test"])
            rows += [{"label": label, **r} for r in t.to_dict("records")]
    if rows:
        df = pd.DataFrame(rows)
        msp = df[df["score"] == "msp"].set_index("label")["detection_mean"].to_dict()
        note = "No verdict (the 40f, 48f and 41f runs are needed)."
        if {"40f", "48f", "41f"} <= set(msp):
            verdict, drop, gap = ct_verdict(msp)
            note = f"msp detection: 40f {msp['40f']:.3f}, 48f {msp['48f']:.3f} (gap {gap:.3f}); without the 7 window-count ct_* columns {msp['41f']:.3f} (drop {drop:.3f}). Declared reading: **{verdict}**."
        tag4 = "_".join(["40f", "48f", *args.variants])
        df.to_csv(d / f"open_set_step4_{tag4}.csv", index=False)
        (d / f"open_set_step4_{tag4}.md").write_text(render_step4(df, note), encoding="utf-8")
        print(note)


if __name__ == "__main__":
    main()
