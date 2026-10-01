"""Cross-Dataset Generalization study (novelty #4).

Trains on UNSW-NB15, tests on CICIDS2017 (and vice versa) using only the
feature namespace the two datasets share (see CIC_TO_COMMON in
src/data_loader.py), and compares three feature-selection strategies:

  - "common_all":  every feature common to both datasets
  - "source_only": top-k common features ranked by SHAP importance on the TRAIN dataset
  - "stable":      common features that rank in the top-k on BOTH datasets
                    (src/feature_selection.get_stable_features)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.evaluation.metrics import compute_metrics
from src.feature_selection import get_stable_features
from src.models.model_factory import create_model
from sklearn.metrics import balanced_accuracy_score

from scipy.stats import ks_2samp
from sklearn.model_selection import train_test_split

from src.preprocessing import Preprocessor, balanced_sample_weight, engineer_features
from src.utils.logger import get_logger
from src.xai.shap_explainer import SHAPExplainer

logger = get_logger(__name__)

# A model that flags fewer than 1% (or more than 99%) of test rows as attack is treated as constant.
DEGENERATE_SHARE = 0.01
METRIC_COLUMNS = ["accuracy", "precision", "recall", "f1", "balanced_accuracy"]


def _fit_on_train(features: list[str], train_df: pd.DataFrame, test_df: pd.DataFrame | None = None):
    """Fit ONE preprocessor on the training dataset only and transform both datasets with
    it, so the test set is scaled with the train set's statistics (no test-statistics leak,
    and unit mismatches between datasets stay visible instead of being scaled away)."""
    pre = Preprocessor(feature_list=features, target_column="label").fit(train_df)
    X_train, y_train = pre.transform(train_df)
    if test_df is None:
        return X_train, y_train
    X_test, y_test = pre.transform(test_df)
    return X_train, y_train, X_test, y_test


def _train_eval(model_type: str, model_params: dict, features: list[str], train_df, test_df) -> dict:
    X_train, y_train, X_test, y_test = _fit_on_train(features, train_df, test_df)
    model = create_model(model_type, model_params)
    # Balanced weights: CIC is ~80% benign, and an unweighted model collapses to "always benign".
    model.fit(X_train, y_train, sample_weight=balanced_sample_weight(y_train))
    y_pred = model.predict(X_test)
    attack_share = float(np.mean(y_pred == 1))
    return {
        **compute_metrics(y_test, y_pred),
        "balanced_accuracy": round(float(balanced_accuracy_score(y_test, y_pred)), 4),
        "predicted_attack_share": round(attack_share, 4),
        # A (near-)constant predictor says nothing about the strategy: never rank these rows.
        "degenerate": min(attack_share, 1 - attack_share) < DEGENERATE_SHARE,
    }


def feature_shift_table(unsw_df: pd.DataFrame, cic_df: pd.DataFrame, features: list[str],
                        max_rows: int = 50000, seed: int = 42) -> pd.DataFrame:
    """Per common feature: median and IQR in each dataset and the Kolmogorov-Smirnov statistic
    between them (0 = same distribution, 1 = disjoint) on a seeded sample, to document WHY transfer
    fails. Engineered features are derived first, exactly as the models see them."""
    def prepared(df):
        df = df.sample(min(len(df), max_rows), random_state=seed)
        out = engineer_features(df, allow_missing=True)
        return {f: pd.to_numeric(out[f], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna() for f in features}

    u, c = prepared(unsw_df), prepared(cic_df)
    rows = []
    for f in features:
        q = lambda s: (float(s.median()), float(s.quantile(0.75) - s.quantile(0.25)))  # noqa: E731
        (um, ui), (cm, ci) = q(u[f]), q(c[f])
        rows.append({"feature": f, "unsw_median": um, "unsw_iqr": ui, "cic_median": cm, "cic_iqr": ci,
                     "ks_statistic": float(ks_2samp(u[f], c[f]).statistic)})
    return pd.DataFrame(rows).sort_values("ks_statistic", ascending=False).round(4).reset_index(drop=True)


def _importance(model_type: str, model_params: dict, features: list[str], df: pd.DataFrame,
                importance_samples: int) -> pd.Series:
    """SHAP importance of a model trained on `df` alone (preprocessor also fit on `df` alone)."""
    X, y = _fit_on_train(features, df)
    model = create_model(model_type, model_params).fit(X, y, sample_weight=balanced_sample_weight(y))
    return SHAPExplainer(model, features).global_importance(X, max_samples=importance_samples)


def run_cross_dataset_study(
    unsw_df: pd.DataFrame,
    cic_df: pd.DataFrame,
    common_features: list[str],
    model_type: str,
    model_params: dict,
    top_k: int = 10,
    importance_samples: int = 2000,
    seed: int = 42,
) -> pd.DataFrame:
    """Run the full cross-dataset generalization comparison and return a results dataframe
    with one row per (strategy, train_dataset -> test_dataset) combination.

    Strategies: "common_all" (every shared feature), "source_only" (top-k by SHAP on the
    TRAIN dataset of each direction), "stable" (top-k on BOTH datasets — note this looks at
    the test dataset's importances, so it is not a strict zero-shot transfer)."""

    # attack_cat taxonomies differ between UNSW and CIC (e.g. "Generic" vs "PortScan"),
    # so cross-dataset transfer is evaluated on the shared binary label (normal/attack)
    # rather than the multiclass target, which wouldn't align across datasets.
    imp = {
        "UNSW": _importance(model_type, model_params, common_features, unsw_df, importance_samples),
        "CIC": _importance(model_type, model_params, common_features, cic_df, importance_samples),
    }
    stable = get_stable_features(imp["UNSW"].to_dict(), imp["CIC"].to_dict(), top_k=top_k)
    datasets = {"UNSW": unsw_df, "CIC": cic_df}

    rows = []
    # Within-dataset reference (same features, train and test from the SAME dataset's own split):
    # the upper bound a cross-dataset drop is compared against.
    for name, df in datasets.items():
        train_df, test_df = train_test_split(df, test_size=0.3, stratify=df["label"], random_state=seed)
        rows.append({"strategy": "within_dataset", "n_features": len(common_features), "train": name, "test": name,
                     **_train_eval(model_type, model_params, common_features, train_df, test_df)})
    for train_name, test_name in [("UNSW", "CIC"), ("CIC", "UNSW")]:
        strategies = {
            "common_all": common_features,
            "source_only": list(imp[train_name].head(top_k).index),
            "stable": stable,
        }
        for strategy_name, features in strategies.items():
            if len(features) < 2:
                logger.warning(f"Strategy '{strategy_name}' has too few features ({len(features)}); skipping.")
                continue
            metrics = _train_eval(model_type, model_params, features, datasets[train_name], datasets[test_name])
            rows.append({"strategy": strategy_name, "n_features": len(features),
                         "train": train_name, "test": test_name, **metrics})

    result = pd.DataFrame(rows)
    degenerate = result["degenerate"].astype(bool)
    if degenerate.any():
        names = ", ".join(f"{r.strategy} {r.train}->{r.test} (attack share {r.predicted_attack_share})"
                          for r in result[degenerate].itertuples())
        logger.warning(f"Degenerate (constant-prediction) rows, metrics set to NaN and not rankable: {names}")
        cols = [c for c in METRIC_COLUMNS if c in result]
        result[cols] = result[cols].astype(float)
        result.loc[degenerate, cols] = np.nan
    return result
