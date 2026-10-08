from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score

from pipelines.run_tier_study import prepare
from pipelines.train_pipeline import train_and_evaluate
from src.preprocessing import balanced_sample_weight
from src.utils.config_loader import load_config, load_feature_sets, get_active_features, pool_label

CONFIG = "configs/config_lr.yaml"
SEED = 42
POOL = "full"
TIER = "40"

C_VALUES = [0.01, 0.1, 1.0, 10.0, 100.0]
POWER_VALUES = [0.0, 0.25, 0.5, 0.75, 1.0]

config = load_config(CONFIG)
feature_sets = load_feature_sets()

cfg, sets, splits = prepare(config, feature_sets, POOL, "logistic_regression", SEED)
features = get_active_features(cfg, sets, TIER)

rows = []

CANDIDATES = [
    (0.1, 0.5),
    (1.0, 0.5),
    (10.0, 0.5),
]
SEEDS = [42, 43, 44, 45, 46]

for C, power in CANDIDATES:
    for seed in SEEDS:
        cfg_seed, sets_seed, splits_seed = prepare(
            config, feature_sets, POOL, "logistic_regression", seed
        )
        features_seed = get_active_features(cfg_seed, sets_seed, TIER)

        cfg_run = {
            **cfg_seed,
            "model": {
                **cfg_seed["model"],
                "params": dict(cfg_seed["model"]["params"]),
            },
        }
        cfg_run["model"]["params"].update({
            "C": C,
            "solver": "lbfgs",
            "max_iter": 1000,
        })
        cfg_run["model"]["class_weight_power"] = power

        pred = {}
        train_and_evaluate(
            cfg_run,
            sets_seed,
            TIER,
            False,
            splits_seed,
            False,
            pred,
            features=features_seed,
        )

        classes = list(pred["class_names"])
        label_to_index = {c: i for i, c in enumerate(classes)}
        y_true = np.asarray([label_to_index[c] for c in pred["val_labels"]])
        proba = np.asarray(pred["y_proba_val"])
        y_pred = proba.argmax(axis=1)

        f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

        try:
            auc = roc_auc_score(
                y_true, proba, multi_class="ovr", average="macro"
            )
        except ValueError:
            auc = np.nan

        rows.append({
            "C": C,
            "class_weight_power": power,
            "seed": seed,
            "val_macro_f1": f1,
            "val_roc_auc": auc,
        })

        print(
            f"C={C:<5} power={power:<3} seed={seed} "
            f"F1={f1:.4f} AUC={auc:.4f}"
        )

out = pd.DataFrame(rows)
summary = (
    out.groupby(["C", "class_weight_power"])
    .agg(
        macro_f1_mean=("val_macro_f1", "mean"),
        macro_f1_std=("val_macro_f1", "std"),
        roc_auc_mean=("val_roc_auc", "mean"),
        roc_auc_std=("val_roc_auc", "std"),
    )
    .reset_index()
    .sort_values(["macro_f1_mean", "roc_auc_mean"], ascending=False)
)

Path("results/metrics/logistic_regression__LR").mkdir(
    parents=True, exist_ok=True
)

out.to_csv(
    "results/metrics/logistic_regression__LR/lr_multiseed_validation_40f.csv",
    index=False,
)
summary.to_csv(
    "results/metrics/logistic_regression__LR/lr_multiseed_summary_40f.csv",
    index=False,
)

print("\nMULTI-SEED SUMMARY:")
print(summary.to_string(index=False))
print("\nSaved:")
print("results/metrics/logistic_regression__LR/lr_multiseed_validation_40f.csv")
print("results/metrics/logistic_regression__LR/lr_multiseed_summary_40f.csv")
Path("results/metrics/logistic_regression__LR").mkdir(
    parents=True, exist_ok=True
)

out.to_csv(
    "results/metrics/logistic_regression__LR/lr_tuning_40f_seed42.csv",
    index=False,
)

print("\nTOP CONFIGURATIONS:")
print(out.head(10).to_string(index=False))
print("\nSaved:")
print("results/metrics/logistic_regression__LR/lr_tuning_40f_seed42.csv")
