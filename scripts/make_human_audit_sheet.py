"""Explanation study, step 5: a blank rating sheet for teammates (protocol: results/03_novelty2_explanations.md, section `Source: explanations_protocol.md`).

    python scripts/make_human_audit_sheet.py

Takes 30 narratives from the Step 3 audit of the 40-feature pool (seed 42), stratified over the predicted classes and Unknown (4 per stratum, 5 for Overlap-Group-1 and Unknown), in a seeded
random order, with a few raw flow values so a rater can judge the flow. The sheet has BLANK rating columns and does not show the flow's true class; nothing is rated here and no rating is
reported. Writes results/rating/explanations_human_audit_sheet.csv and results/rating/explanations_human_audit_key.csv (sheet id -> flow, stratum; kept apart so the sheet shows no label).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from pipelines.train_pipeline import load_split_data
from src.utils.config_loader import get_metrics_dir, load_config, rating_dir

ALLOCATION = {"Normal": 4, "Overlap-Group-1": 5, "Exploits": 4, "Fuzzers": 4, "Generic": 4, "Reconnaissance": 4, "Unknown": 5}
FLOW_COLUMNS = ["dur", "proto", "service", "state", "spkts", "dpkts", "sbytes", "dbytes", "rate"]
RATING_COLUMNS = ["rating_understandable_1_to_5", "rating_actionable_1_to_5", "rating_agrees_with_my_judgement_yes_no_unsure", "comments", "rater"]


def pick_rows(narratives: pd.DataFrame, allocation: dict[str, int], seed: int = 0) -> pd.DataFrame:
    """`allocation[stratum]` narratives per stratum, drawn without replacement (all of them when a stratum has fewer), then shuffled; seeded."""
    rng = np.random.default_rng(seed)
    parts = []
    for stratum, n in allocation.items():
        rows = narratives[narratives["stratum"] == stratum]
        parts.append(rows.iloc[rng.choice(len(rows), size=min(n, len(rows)), replace=False)])
    chosen = pd.concat(parts)
    return chosen.iloc[rng.permutation(len(chosen))].reset_index(drop=True)


def write_sheet(sheet: pd.DataFrame, key: pd.DataFrame, out) -> Path:
    """Write the blank sheet and its key into `out` (results/rating/); returns the sheet's path."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    sheet.to_csv(out / "explanations_human_audit_sheet.csv", index=False)
    key.to_csv(out / "explanations_human_audit_key.csv", index=False)
    return out / "explanations_human_audit_sheet.csv"


def main() -> None:
    config = load_config()
    narratives = pd.read_csv(get_metrics_dir(config) / "xai_audit_40f_narratives.csv")
    narratives = narratives[narratives["seed"] == 42]
    chosen = pick_rows(narratives, ALLOCATION)
    splits = load_split_data(config)
    candidates = pd.concat([splits.test, splits.unknown], ignore_index=True)       # the audit's flow numbers index this frame (the same for every seed)
    flows = candidates.loc[chosen["flow"], FLOW_COLUMNS].reset_index(drop=True)
    sheet = pd.concat([pd.DataFrame({"sheet_id": range(1, len(chosen) + 1), "narrative": chosen["narrative"]}), flows], axis=1)
    for col in RATING_COLUMNS:
        sheet[col] = ""
    key = pd.DataFrame({"sheet_id": range(1, len(chosen) + 1), "flow": chosen["flow"], "seed": chosen["seed"], "stratum": chosen["stratum"]})
    print(f"wrote {len(sheet)} narratives to {write_sheet(sheet, key, rating_dir(config))} (rating columns blank)")


if __name__ == "__main__":
    main()
