"""Task 5.5 Step 3: a blank A/B sheet for teammates (protocol: results/task_5_5_protocol.md).

    python scripts/make_ab_sheet.py

30 flows from the held-out official-test sample of the 40-feature pool (model seed 42), 5 from each of six strata (Normal, Overlap-Group-1, Fuzzers, flagged Unknown, false-positive Normal and one
group of the other attack classes), each with the classic and the class-relative narrative side by side as A and B in a seeded random order. The columns for the rater are BLANK; which column is
which style is only in the key file. Nothing is rated here and no rating is reported. Writes results/rating/task_5_5_ab_sheet.csv and results/rating/task_5_5_ab_key.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from pipelines.train_pipeline import load_split_data
from src.utils.config_loader import get_metrics_dir, load_config, rating_dir

GROUPS = {"Normal": ["Normal"], "Overlap-Group-1": ["Overlap-Group-1"], "Fuzzers": ["Fuzzers"], "Unknown": ["Unknown"], "FP-Normal": ["FP-Normal"],
          "other attack classes": ["Exploits", "Generic", "Reconnaissance"]}
PER_GROUP = 5
FLOW_COLUMNS = ["dur", "proto", "service", "state", "spkts", "dpkts", "sbytes", "dbytes", "rate"]
RATING_COLUMNS = ["clearer_A_B_same", "more_actionable_A_B_same", "comments", "rater"]


def pair_narratives(narratives: pd.DataFrame) -> pd.DataFrame:
    """One row per flow with the classic and the class-relative narrative (the same flows in both styles)."""
    wide = narratives.pivot_table(index=["seed", "flow", "stratum"], columns="style", values="narrative", aggfunc="first").reset_index()
    return wide.dropna(subset=["classic", "class_relative"]).reset_index(drop=True)


def pick_flows(pairs: pd.DataFrame, groups: dict[str, list[str]], per_group: int, seed: int = 0) -> pd.DataFrame:
    """`per_group` flows per group (all of them when fewer), without replacement, then shuffled; seeded."""
    rng = np.random.default_rng(seed)
    parts = []
    for name, strata in groups.items():
        rows = pairs[pairs["stratum"].isin(strata)]
        parts.append(rows.iloc[rng.choice(len(rows), size=min(per_group, len(rows)), replace=False)].assign(group=name))
    chosen = pd.concat(parts)
    return chosen.iloc[rng.permutation(len(chosen))].reset_index(drop=True)


def assign_ab(chosen: pd.DataFrame, seed: int = 1) -> pd.DataFrame:
    """Columns narrative_A / narrative_B in a seeded random order per flow, and `classic_is` ("A" or "B") for the key."""
    classic_is_a = np.random.default_rng(seed).random(len(chosen)) < 0.5
    out = chosen.copy()
    out["narrative_A"] = np.where(classic_is_a, chosen["classic"], chosen["class_relative"])
    out["narrative_B"] = np.where(classic_is_a, chosen["class_relative"], chosen["classic"])
    out["classic_is"] = np.where(classic_is_a, "A", "B")
    return out


def write_sheet(sheet: pd.DataFrame, key: pd.DataFrame, out) -> Path:
    """Write the blank sheet and its key into `out` (results/rating/); returns the sheet's path."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    sheet.to_csv(out / "task_5_5_ab_sheet.csv", index=False)
    key.to_csv(out / "task_5_5_ab_key.csv", index=False)
    return out / "task_5_5_ab_sheet.csv"


def main() -> None:
    config = load_config()
    narratives = pd.read_csv(get_metrics_dir(config) / "narrative_test_40f_narratives.csv")
    pairs = pair_narratives(narratives[narratives["seed"] == 42])
    chosen = assign_ab(pick_flows(pairs, GROUPS, PER_GROUP))
    splits = load_split_data(config)
    candidates = pd.concat([splits.test, splits.unknown], ignore_index=True)       # the flow numbers index this frame, as in the Task 5 sheet
    flows = candidates.loc[chosen["flow"], FLOW_COLUMNS].reset_index(drop=True)
    sheet = pd.concat([pd.DataFrame({"sheet_id": range(1, len(chosen) + 1)}), flows, chosen[["narrative_A", "narrative_B"]]], axis=1)
    for col in RATING_COLUMNS:
        sheet[col] = ""
    key = pd.DataFrame({"sheet_id": range(1, len(chosen) + 1), "flow": chosen["flow"], "seed": chosen["seed"], "stratum": chosen["stratum"], "group": chosen["group"], "classic_is": chosen["classic_is"]})
    print(f"wrote {len(sheet)} flows to {write_sheet(sheet, key, rating_dir(config))} (rating columns blank)")


if __name__ == "__main__":
    main()
